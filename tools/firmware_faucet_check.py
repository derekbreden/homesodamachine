#!/usr/bin/env python3
"""Prove the faucet display's J3 link without driving any actuator.

The default check is observational: it identifies the 1.47-inch display over
native USB, waits for controller-owned flavor state to converge and persist,
then measures USB query and firmware-loop latency. It never opens the PCBA's
CH340C port and never runs a pump, valve, relay, fan, or compressor.

The explicit ``--toggle`` check selects the other flavor through the faucet's
normal local-first path, waits for both controller persistence and faucet-cache
persistence, and restores the original selection in a finally block. Two UI
ticks from the controller are expected: one for the test selection and one for
the restoration.

    ~/.platformio/penv/bin/python tools/firmware_faucet_check.py
    ~/.platformio/penv/bin/python tools/firmware_faucet_check.py --toggle
"""

from __future__ import annotations

import argparse
import math
import statistics
import sys
import time

try:
    import serial
    from serial.tools import list_ports
except ImportError:
    sys.exit("pyserial not found — run with ~/.platformio/penv/bin/python")


ESP32_S3 = (0x303A, 0x1001)
DEFAULT_LOOP_LIMIT_MS = 50
DEFAULT_QUERY_P95_MS = 15.0
DEFAULT_ACK_LIMIT_MS = 250
DEFAULT_LINK_SERVICE_LIMIT_US = 5000


def faucet_port(explicit: str | None) -> str:
    if explicit:
        return explicit
    ports = [p.device for p in list_ports.comports() if (p.vid, p.pid) == ESP32_S3]
    if len(ports) == 1:
        return ports[0]
    if not ports:
        raise RuntimeError("faucet display not found (expected native USB 303a:1001)")
    raise RuntimeError("more than one S3 is connected; name the faucet with --faucet-port")


def fields(line: str, prefix: str) -> dict[str, str]:
    if not line.startswith(prefix):
        raise RuntimeError(f"expected {prefix}, got {line!r}")
    values: dict[str, str] = {}
    for item in line[len(prefix):].split(","):
        if "=" in item:
            key, value = item.split("=", 1)
            values[key] = value
    return values


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


class Faucet:
    def __init__(self, port: str):
        # Set modem lines before opening. Some USB stacks still restart a native
        # S3 attachment; identification below tolerates the normal boot interval.
        self.serial = serial.Serial()
        self.serial.port = port
        self.serial.baudrate = 115200
        self.serial.timeout = 0.05
        self.serial.write_timeout = 1
        self.serial.dtr = False
        self.serial.rts = False
        self.serial.open()
        self.pending = bytearray()

    def close(self) -> None:
        self.serial.close()

    def _line(self, prefix: str, timeout: float) -> str:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            chunk = self.serial.read(self.serial.in_waiting or 1)
            if chunk:
                self.pending.extend(chunk)
            while b"\n" in self.pending:
                raw, _, rest = self.pending.partition(b"\n")
                self.pending = bytearray(rest)
                line = raw.decode("utf-8", "replace").strip()
                if line.startswith(prefix):
                    return line
        raise RuntimeError(f"timed out waiting for {prefix}")

    def send(self, command: str) -> float:
        started = time.monotonic()
        self.serial.write((command + "\n").encode("ascii"))
        self.serial.flush()
        return started

    def query(self, command: str, prefix: str, timeout: float = 1.5) -> tuple[str, float]:
        started = self.send(command)
        return self._line(prefix, timeout), (time.monotonic() - started) * 1000.0

    def identify(self, timeout: float = 7.0) -> str:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            self.send("GET_VERSION")
            try:
                return self._line("VERSION:FAUCET=", 0.5)
            except RuntimeError:
                pass
        raise RuntimeError("native USB board did not identify as the faucet display")

    def state(self) -> dict[str, str]:
        line, _ = self.query("GET_STATE", "STATE:")
        return fields(line, "STATE:")

    def diag(self) -> dict[str, str]:
        line, _ = self.query("GET_DIAG", "DIAG:")
        return fields(line, "DIAG:")


def state_ready(state: dict[str, str], flavor: int | None = None) -> bool:
    return (
        (flavor is None or state.get("FLAVOR") == str(flavor))
        and state.get("SYNC") == "1"
        and state.get("BASE") == state.get("FLAVOR")
        and state.get("PERSISTED") == "1"
        and state.get("PENDING") == "0"
        and state.get("DURABILITYPENDING") == "0"
        and state.get("CACHEPENDING") == "0"
    )


def wait_ready(faucet: Faucet, flavor: int | None = None, timeout: float = 6.0) -> dict[str, str]:
    deadline = time.monotonic() + timeout
    last: dict[str, str] = {}
    while time.monotonic() < deadline:
        last = faucet.state()
        if state_ready(last, flavor):
            return last
        time.sleep(0.1)
    raise RuntimeError(f"flavor state did not converge and persist: {last}")


def check_diag(diag: dict[str, str], loop_limit: int, link_limit: int) -> None:
    require(diag.get("base") == "up", "J3 link is down")
    require(diag.get("sync") == "1", "controller flavor is not synchronized")
    require(diag.get("basePersisted") == "1", "controller flavor is not persisted")
    require(diag.get("basePersistErr") == "0", "controller flavor persistence failed")
    require(diag.get("durabilityPending") == "0", "controller durability acknowledgement pending")
    require(diag.get("localPersistErr") == "0", "faucet flavor-cache persistence failed")
    require(diag.get("pending") == "0", f"{diag.get('pending')} flavor request(s) remain pending")
    require(diag.get("qDrop") == "0", f"faucet queue dropped {diag.get('qDrop')} request(s)")
    require(int(diag.get("maxLoopMs", "999999")) <= loop_limit,
            f"faucet loop high-water {diag.get('maxLoopMs')} ms exceeds {loop_limit} ms")
    require(int(diag.get("maxLinkUs", "999999")) <= link_limit,
            f"J3 service high-water {diag.get('maxLinkUs')} us exceeds {link_limit} us")


def measure_queries(faucet: Faucet, count: int, p95_limit: float) -> tuple[float, float]:
    samples = []
    for _ in range(count):
        line, elapsed = faucet.query("GET_STATE", "STATE:")
        require(state_ready(fields(line, "STATE:")), f"state changed during latency run: {line}")
        samples.append(elapsed)
    ordered = sorted(samples)
    p95 = ordered[max(0, math.ceil(len(ordered) * 0.95) - 1)]
    require(p95 <= p95_limit, f"USB query p95 {p95:.2f} ms exceeds {p95_limit:.2f} ms")
    return statistics.median(samples), p95


def toggle_and_restore(faucet: Faucet, initial_flavor: int, ack_limit: int) -> None:
    target = initial_flavor ^ 1
    restore_needed = False
    try:
        # Once the selection command leaves the host, it may reach the faucet
        # even if its USB response is lost. Always attempt the restoration from
        # that point onward rather than relying on receipt of the OK line.
        restore_needed = True
        line, _ = faucet.query(f"FLAVOR:{target}", "OK:FLAVOR=")
        require(line == f"OK:FLAVOR={target}", f"unexpected selection answer: {line}")
        wait_ready(faucet, target)
        diag = faucet.diag()
        require(int(diag.get("lastAckMs", "999999")) <= ack_limit,
                f"flavor acknowledgement {diag.get('lastAckMs')} ms exceeds {ack_limit} ms")
        print(f"toggle      flavor {target}, controller ack {diag['lastAckMs']} ms, both stores durable")
    finally:
        if restore_needed:
            line, _ = faucet.query(f"FLAVOR:{initial_flavor}", "OK:FLAVOR=")
            require(line == f"OK:FLAVOR={initial_flavor}", f"restore was not accepted: {line}")
            wait_ready(faucet, initial_flavor)
            print(f"restore     flavor {initial_flavor}, controller and faucet cache durable")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--faucet-port", help="faucet display native USB port")
    parser.add_argument("--toggle", action="store_true",
                        help="select the other flavor, prove both stores, then restore")
    parser.add_argument("--query-count", type=int, default=40)
    parser.add_argument("--query-p95-ms", type=float, default=DEFAULT_QUERY_P95_MS)
    parser.add_argument("--loop-limit-ms", type=int, default=DEFAULT_LOOP_LIMIT_MS)
    parser.add_argument("--ack-limit-ms", type=int, default=DEFAULT_ACK_LIMIT_MS)
    parser.add_argument("--link-service-limit-us", type=int,
                        default=DEFAULT_LINK_SERVICE_LIMIT_US)
    args = parser.parse_args()

    try:
        require(args.query_count > 0, "--query-count must be positive")
        port = faucet_port(args.faucet_port)
        faucet = Faucet(port)
        try:
            version = faucet.identify()
            initial = wait_ready(faucet)
            faucet.diag()  # reset the firmware loop high-water before measuring
            median, p95 = measure_queries(faucet, args.query_count, args.query_p95_ms)
            diag = faucet.diag()
            check_diag(diag, args.loop_limit_ms, args.link_service_limit_us)

            print(version)
            print(f"selection   flavor {initial['FLAVOR']}, controller persisted, faucet cache persisted")
            print(f"latency     USB median {median:.2f} ms, p95 {p95:.2f} ms; "
                  f"loop {diag['maxLoopMs']} ms, J3 service {diag['maxLinkUs']} us")
            print(f"link        rx {diag['linkRx']}, tx {diag['linkTx']}, retries {diag['retries']}")

            if args.toggle:
                toggle_and_restore(faucet, int(initial["FLAVOR"]), args.ack_limit_ms)
        finally:
            faucet.close()
    except (OSError, serial.SerialException, RuntimeError, ValueError) as exc:
        print(f"faucet firmware check: FAIL — {exc}", file=sys.stderr)
        return 1

    print("faucet firmware check: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
