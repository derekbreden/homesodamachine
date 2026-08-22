#!/usr/bin/env python3
"""Live regression checks through the front display's native USB port.

The default check is observational: version, touch/display health, and J9 link.
It never opens the controller's CH340 port, whose DTR/RTS lines reset the PCBA.

Optional checks are explicit and non-actuating unless ``--prime`` is named:

    ~/.platformio/penv/bin/python tools/firmware_live_check.py --animation
    ~/.platformio/penv/bin/python tools/firmware_live_check.py --toggle
    ~/.platformio/penv/bin/python tools/firmware_live_check.py --prime b

--animation opens the reusable operation lock, measures its logo animation, then
restores the page/idle/lock state it found. --toggle selects the other flavor,
proves controller synchronization and persistence, then restores it. --prime runs
the selected flavor pump for one second through the display's real hold handlers
and always posts PRIME:STOP in a finally block. The controller's own stale-tick and
60-second ceilings remain the last line of defence if the host disappears during
that check.
"""

from __future__ import annotations

import argparse
import re
import sys
import time

try:
    import serial
    from serial.tools import list_ports
except ImportError:
    sys.exit("pyserial not found — run with ~/.platformio/penv/bin/python")


ESP32_S3 = (0x303A, 0x1001)
DEFAULT_ACK_LIMIT_MS = 250.0
DEFAULT_LOOP_LIMIT_MS = 140
DEFAULT_MIN_ANIMATION_FPS = 9.0


def display_port(explicit: str | None) -> str:
    if explicit:
        return explicit
    ports = [p.device for p in list_ports.comports() if (p.vid, p.pid) == ESP32_S3]
    if len(ports) == 1:
        return ports[0]
    if not ports:
        raise RuntimeError("front display not found (expected native USB 303a:1001)")
    raise RuntimeError("more than one S3 is connected; name the front with --display-port")


def fields(line: str, prefix: str) -> dict[str, str]:
    if not line.startswith(prefix):
        raise RuntimeError(f"expected {prefix}, got {line!r}")
    out: dict[str, str] = {}
    for item in line[len(prefix):].split(","):
        if "=" in item:
            key, value = item.split("=", 1)
            out[key] = value
    return out


class Front:
    def __init__(self, port: str):
        self.serial = serial.Serial()
        self.serial.port = port
        self.serial.baudrate = 115200
        self.serial.timeout = 0.05
        self.serial.write_timeout = 1
        # ESP32-S3 USB Serial/JTAG gates application TX on the host's DTR line.
        # Keep RTS deasserted so opening diagnostics does not request a reset.
        self.serial.dtr = True
        self.serial.rts = False
        self.serial.open()
        time.sleep(0.25)
        self.serial.reset_input_buffer()

    def close(self) -> None:
        self.serial.close()

    def send(self, command: str) -> float:
        started = time.monotonic()
        self.serial.write((command + "\n").encode("ascii"))
        self.serial.flush()
        return started

    def wait_line(self, predicate, timeout: float, what: str) -> tuple[str, float]:
        deadline = time.monotonic() + timeout
        pending = bytearray()
        while time.monotonic() < deadline:
            chunk = self.serial.read(self.serial.in_waiting or 1)
            if not chunk:
                continue
            pending.extend(chunk)
            while b"\n" in pending:
                raw, _, rest = pending.partition(b"\n")
                pending = bytearray(rest)
                line = raw.decode("utf-8", "replace").strip()
                if predicate(line):
                    return line, time.monotonic()
        raise RuntimeError(f"timed out waiting for {what}")

    def query_prefix(self, command: str, prefix: str, timeout: float = 1.5) -> str:
        self.send(command)
        line, _ = self.wait_line(lambda value: value.startswith(prefix), timeout, prefix)
        return line


def snapshot(front: Front) -> tuple[str, dict[str, str], dict[str, str], str]:
    version = front.query_prefix("GET_VERSION", "VERSION:FRONT=")
    state = fields(front.query_prefix("GET_STATE", "STATE:"), "STATE:")
    diag_line = front.query_prefix("GET_DIAG", "DIAG:")
    link = front.query_prefix("LINK", "LINK:")
    return version, state, fields(diag_line, "DIAG:"), link


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def restore_view(front: Front, initial: dict[str, str]) -> None:
    page = int(initial.get("page", "0"))
    stage = int(initial.get("stage", "0"))
    front.query_prefix(f"PAGE:{page}", "OK:PAGE=")
    if initial.get("idle") == "1" or stage > 0:
        front.query_prefix(f"IDLE:{max(1, min(stage, 3))}", "OK:IDLE=")
    if initial.get("lock") == "1":
        front.query_prefix("LOCK:SHOW", "OK:LOCK=1")
    else:
        front.query_prefix("LOCK:HIDE", "OK:LOCK=0")


def check_animation(front: Front, initial: dict[str, str], min_fps: float, loop_limit: int) -> None:
    try:
        front.query_prefix("IDLE:0", "OK:IDLE=0")
        front.query_prefix("LOCK:SHOW", "OK:LOCK=1")
        time.sleep(0.5)  # panel reset/recovery + the 200 ms animation quiet window

        first = fields(front.query_prefix("GET_DIAG", "DIAG:"), "DIAG:")
        flush0 = int(first["flushes"])
        started = time.monotonic()
        time.sleep(2.0)
        second = fields(front.query_prefix("GET_DIAG", "DIAG:"), "DIAG:")
        elapsed = time.monotonic() - started
        fps = (int(second["flushes"]) - flush0) / elapsed
        max_loop = int(second["maxLoopMs"])

        require(fps >= min_fps, f"lock-screen animation only advanced at {fps:.2f} fps")
        require(max_loop <= loop_limit,
                f"display loop high-water {max_loop} ms exceeds {loop_limit} ms")
        print(f"animation  {fps:.2f} flushes/s, loop high-water {max_loop} ms")
    finally:
        front.query_prefix("LOCK:HIDE", "OK:LOCK=0")
        restore_view(front, initial)
        # LOCK:HIDE invalidates the whole 800x480 surface. Let that one-time
        # restoration render before a following latency check starts its clock.
        time.sleep(0.35)


def wait_flavor(front: Front, flavor: int, durable: bool, timeout: float = 4.0) -> dict[str, str]:
    deadline = time.monotonic() + timeout
    last: dict[str, str] = {}
    while time.monotonic() < deadline:
        last = fields(front.query_prefix("GET_STATE", "STATE:"), "STATE:")
        ready = (
            last.get("FLAVOR") == str(flavor)
            and last.get("SYNC") == "1"
            and last.get("PENDING") == "0"
            and last.get("PERSISTERR") == "0"
        )
        if ready and (not durable or last.get("PERSISTED") == "1"):
            return last
        time.sleep(0.05)
    raise RuntimeError(f"flavor {flavor} did not {'persist' if durable else 'synchronize'}: {last}")


def check_toggle(front: Front, initial_flavor: int, ack_limit_ms: float, loop_limit: int) -> None:
    target = initial_flavor ^ 1
    restore_needed = False
    try:
        restore_needed = True
        started = front.send(f"FLAVOR:{target}")
        line, _ = front.wait_line(lambda value: value.startswith("OK:FLAVOR="),
                                  1.5, "OK:FLAVOR")
        require(line == f"OK:FLAVOR={target}", f"unexpected selection answer: {line}")
        wait_flavor(front, target, durable=False)
        ack_ms = (time.monotonic() - started) * 1000.0
        require(ack_ms <= ack_limit_ms,
                f"flavor synchronization {ack_ms:.1f} ms exceeds {ack_limit_ms:.1f} ms")
        wait_flavor(front, target, durable=True)
        diag = fields(front.query_prefix("GET_DIAG", "DIAG:"), "DIAG:")
        max_loop = int(diag["maxLoopMs"])
        require(max_loop <= loop_limit,
                f"flavor repaint loop high-water {max_loop} ms exceeds {loop_limit} ms")
        print(f"flavor     selected {target}, controller ack {ack_ms:.1f} ms, "
              f"repaint loop {max_loop} ms, durable")
    finally:
        if restore_needed:
            front.query_prefix(f"FLAVOR:{initial_flavor}", "OK:FLAVOR=")
            wait_flavor(front, initial_flavor, durable=True)
            print(f"restore    flavor {initial_flavor}, controller durable")


def check_prime(front: Front, initial: dict[str, str], channel: str, ack_limit_ms: float) -> None:
    flavor = 1 if channel == "a" else 2
    start_sent = False
    try:
        started = front.send(f"PRIME:START:{flavor}")
        start_sent = True
        line, answered = front.wait_line(
            lambda value: "MSG_RESP_PRIME state=" in value,
            2.5,
            "MSG_RESP_PRIME RUNNING",
        )
        require("state=0" in line, f"prime was not accepted: {line}")
        start_ms = (answered - started) * 1000.0
        require(start_ms <= ack_limit_ms,
                f"prime start acknowledgement {start_ms:.1f} ms exceeds {ack_limit_ms:.1f} ms")

        while time.monotonic() - started < 1.0:
            time.sleep(0.01)

        stopped = front.send("PRIME:STOP")
        line, answered = front.wait_line(
            lambda value: "MSG_RESP_PRIME state=" in value,
            2.5,
            "MSG_RESP_PRIME STOPPED",
        )
        require("state=1" in line, f"prime did not stop normally: {line}")
        start_sent = False
        stop_ms = (answered - stopped) * 1000.0
        require(stop_ms <= ack_limit_ms,
                f"prime stop acknowledgement {stop_ms:.1f} ms exceeds {ack_limit_ms:.1f} ms")
        print(f"prime {channel.upper()}     start ack {start_ms:.1f} ms, stop ack {stop_ms:.1f} ms")
    finally:
        # Safe and idempotent even when START was accepted but its answer was lost.
        if start_sent:
            front.send("PRIME:STOP")
            time.sleep(0.2)
        restore_view(front, initial)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--display-port", help="front display native USB port")
    parser.add_argument("--animation", action="store_true",
                        help="show the operation lock, measure animation/loop speed, and restore")
    parser.add_argument("--toggle", action="store_true",
                        help="select the other flavor, prove persistence, and restore")
    parser.add_argument("--prime", choices=("a", "b"),
                        help="ACTUATES the selected pump for about one second")
    parser.add_argument("--ack-limit-ms", type=float, default=DEFAULT_ACK_LIMIT_MS)
    parser.add_argument("--loop-limit-ms", type=int, default=DEFAULT_LOOP_LIMIT_MS)
    parser.add_argument("--min-animation-fps", type=float, default=DEFAULT_MIN_ANIMATION_FPS)
    args = parser.parse_args()

    try:
        port = display_port(args.display_port)
        front = Front(port)
        try:
            version, state, diag, link = snapshot(front)
            require(diag.get("gt911") not in (None, "0x00"), "GT911 touch controller absent")
            require(diag.get("reinits") == "0",
                    f"front link reinitialized {diag.get('reinits')} times")
            require(diag.get("sendErr") == "0", f"front send error {diag.get('sendErr')}")
            if "outDrop" in diag:
                require(diag["outDrop"] == "0",
                        f"front outbound queue dropped {diag['outDrop']} frames")
            require(diag.get("link") == "rx", "front has received no J9 frame")
            require(state.get("SYNC") == "1", "front flavor is not synchronized")
            require(state.get("PERSISTED") == "1", "controller flavor is not persisted")
            require(state.get("PERSISTERR") == "0", "controller flavor persistence failed")
            require(state.get("PENDING") == "0", "front flavor request remains pending")
            match = re.search(r"framesRx=(\d+),framesTx=(\d+)", link)
            require(match is not None and int(match.group(1)) > 0, f"unhealthy J9 report: {link}")

            print(version)
            print(f"display    GT911 {diag['gt911']}, heap {diag.get('heap')}, "
                  f"min {diag.get('minHeap')}, idle stage {diag.get('stage')}")
            print(f"link       rx {match.group(1)}, tx {match.group(2)}, reinits {diag.get('reinits')}")
            print(f"flavor     {state['FLAVOR']}, controller synchronized and durable")

            initial = dict(diag)
            if args.animation:
                check_animation(front, initial, args.min_animation_fps, args.loop_limit_ms)
            if args.toggle:
                check_toggle(front, int(state["FLAVOR"]), args.ack_limit_ms,
                             args.loop_limit_ms)
            if args.prime:
                check_prime(front, initial, args.prime, args.ack_limit_ms)
        finally:
            front.close()
    except (OSError, serial.SerialException, RuntimeError, ValueError) as exc:
        print(f"firmware live check: FAIL — {exc}", file=sys.stderr)
        return 1

    print("firmware live check: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
