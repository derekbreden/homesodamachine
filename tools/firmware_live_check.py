#!/usr/bin/env python3
"""Live regression checks through the front display's native USB port.

The default check is observational: version, touch/display health, and J9 link.
It never opens the controller's CH340 port, whose DTR/RTS lines reset the PCBA.

Optional checks are explicit and non-actuating unless ``--prime`` is named:

    ~/.platformio/penv/bin/python tools/firmware_live_check.py --animation
    ~/.platformio/penv/bin/python tools/firmware_live_check.py --wake-cycles 20
    ~/.platformio/penv/bin/python tools/firmware_live_check.py --toggle
    ~/.platformio/penv/bin/python tools/firmware_live_check.py --prime b

--animation opens the reusable operation lock, measures its logo animation, then
restores the page/idle/lock state it found. --wake-cycles repeatedly takes the
actual dark-to-lit path and checks its frame/reset telemetry. --toggle selects the
other flavor, proves controller synchronization and persistence, then restores it.
--prime runs the selected flavor pump for one second through the display's real
hold handlers and always posts PRIME:STOP and PRIME:EXIT in a finally block. It
proves the run belongs to a newly opened session, checks the measured elapsed
interval, and waits for authoritative OFF cleanup. The controller's own stale-tick
and 60-second ceilings remain the last line of defence if the host disappears
during that check.
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
WAKE_REQUIRED_FRAMES = 4

# firmware/lib/proto_link/proto_msg.h wire values used by GET_STATE/GET_DIAG.
PRIME_SESSION_READY = 1
PRIME_SESSION_RUNNING = 2
PRIME_SESSION_OFF = 0
PRIME_OWNER_NONE = 0
PRIME_OWNER_FRONT = 1
PRIME_OUTCOME_STOPPED = 1


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


def read_panel_diag(front: Front) -> dict[str, str]:
    return fields(front.query_prefix("GET_PANEL", "PANEL:"), "PANEL:")


def wake_once(front: Front, timeout: float = 1.5) -> tuple[dict[str, str], float]:
    """Exercise a real dark wake and wait for the staged panel recovery."""
    before = read_panel_diag(front)
    require(before.get("kickStage") == "0", f"panel kick already active: {before}")
    front.query_prefix("IDLE:1", "OK:IDLE=1")
    time.sleep(0.05)
    dark = read_panel_diag(front)
    require(dark.get("bl") == "0", f"panel did not go dark: {dark}")
    for key in ("drawErr", "frameTimeout", "kickTimeout", "exioErr"):
        require(int(dark[key]) == int(before[key]),
                f"panel {key} changed while going dark: {before[key]} -> {dark[key]}")
    started = time.monotonic()
    front.query_prefix("IDLE:0", "OK:IDLE=0")

    deadline = time.monotonic() + timeout
    after: dict[str, str] = {}
    while time.monotonic() < deadline:
        after = read_panel_diag(front)
        if (int(after["kickStart"]) > int(before["kickStart"]) and
                int(after["kickDone"]) > int(before["kickDone"]) and
                after.get("kickStage") == "0" and after.get("bl") == "1"):
            break
        time.sleep(0.02)
    else:
        raise RuntimeError(f"panel wake did not complete: {after}")

    for key in ("drawErr", "frameTimeout", "kickTimeout", "exioErr"):
        require(int(after[key]) == int(before[key]),
                f"panel {key} changed during wake: {before[key]} -> {after[key]}")
    for key in ("vsync", "frameDone"):
        require(int(after[key]) - int(before[key]) >= WAKE_REQUIRED_FRAMES,
                f"wake crossed too few {key} events: {before} -> {after}")
    return after, (time.monotonic() - started) * 1000.0


def fresh_controller_diag(front: Front) -> dict[str, str]:
    """Read status twice so the second snapshot includes the first turn's audit."""
    diag = fields(front.query_prefix("GET_DIAG", "DIAG:"), "DIAG:")
    controller_rx = int(diag.get("ctrlRx", "0"))
    for _ in range(2):
        deadline = time.monotonic() + 2.0
        next_request = 0.0
        while time.monotonic() < deadline:
            now = time.monotonic()
            # A controller-owned prime transition or queued announcement can
            # legitimately consume this J9 turn. Re-request at a restrained
            # cadence until an actual StatusPayload lands instead of treating
            # that deferred response as a failed link audit.
            if now >= next_request:
                front.query_prefix("STATUS", "OK:STATUS requested")
                next_request = now + 0.15
            diag = fields(front.query_prefix("GET_DIAG", "DIAG:"), "DIAG:")
            updated_rx = int(diag.get("ctrlRx", "0"))
            if updated_rx != controller_rx:
                controller_rx = updated_rx
                break
            time.sleep(0.02)
        else:
            raise RuntimeError(f"controller status did not refresh: {diag}")
    return diag


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def require_transport_health_unchanged(
    before: dict[str, str],
    after: dict[str, str],
    prime_before: dict[str, str],
    prime_after: dict[str, str],
) -> None:
    require(after.get("sendErr") == "0",
            f"front send error after check: {after.get('sendErr')}")
    for field, label in (("reinits", "link reinitializations"),
                         ("outDrop", "outbound queue drops")):
        require(int(after.get(field, "0")) == int(before.get(field, "0")),
                f"front {label} changed during check: "
                f"{before.get(field, '0')} -> {after.get(field, '0')}")
    require(
        int(prime_after.get("staleReinits", "0")) ==
        int(prime_before.get("staleReinits", "0")),
        "prime session required a J9 stale-link reinitialization during check: "
        f"{prime_before.get('staleReinits', '0')} -> "
        f"{prime_after.get('staleReinits', '0')}",
    )
    require(int(after.get("ctrlTurnMax", "255")) <= 1,
            f"controller emitted {after.get('ctrlTurnMax')} replies in one J9 turn")
    require(int(after.get("ctrlTurnOver", "0")) ==
            int(before.get("ctrlTurnOver", "0")),
            "controller J9 multi-reply turns changed during check: "
            f"{before.get('ctrlTurnOver', '0')} -> {after.get('ctrlTurnOver', '0')}")


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


def check_wake_cycles(front: Front, initial: dict[str, str], cycles: int) -> None:
    if cycles < 1:
        return
    durations: list[float] = []
    try:
        for _ in range(cycles):
            _, elapsed_ms = wake_once(front)
            durations.append(elapsed_ms)
            time.sleep(0.05)
        print(f"wake        {cycles} cycles, {min(durations):.1f}–{max(durations):.1f} ms, "
              "no panel/expander errors")
    finally:
        restore_view(front, initial)


def check_animation(front: Front, initial: dict[str, str], min_fps: float, loop_limit: int) -> None:
    try:
        _, wake_ms = wake_once(front)
        front.query_prefix("LOCK:SHOW", "OK:LOCK=1")
        time.sleep(0.3)  # finish the post-wake animation quiet window

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
        print(f"animation  {fps:.2f} flushes/s, loop high-water {max_loop} ms, "
              f"wake {wake_ms:.1f} ms")
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


def wait_prime_state(
    front: Front,
    phase: int,
    owner: int,
    timeout: float = 2.5,
) -> tuple[dict[str, str], float]:
    deadline = time.monotonic() + timeout
    last: dict[str, str] = {}
    while time.monotonic() < deadline:
        line = front.query_prefix("GET_STATE", "STATE:", timeout=0.5)
        last = fields(line, "STATE:")
        if last.get("PRIME") == str(phase) and last.get("OWNER") == str(owner):
            return last, time.monotonic()
        time.sleep(0.01)
    raise RuntimeError(
        f"prime did not reach phase={phase}, owner={owner}: {last}"
    )


def read_prime_diag(front: Front) -> dict[str, str]:
    return fields(
        front.query_prefix("GET_DIAG", "DIAG_PRIME:"), "DIAG_PRIME:"
    )


def wait_prime_diag(front: Front, predicate, what: str, timeout: float = 3.0) -> dict[str, str]:
    deadline = time.monotonic() + timeout
    last: dict[str, str] = {}
    while time.monotonic() < deadline:
        last = read_prime_diag(front)
        if predicate(last):
            return last
        time.sleep(0.02)
    raise RuntimeError(f"timed out waiting for {what}: {last}")


def prime_diag_is_authoritative_off(diag: dict[str, str]) -> bool:
    return (
        diag.get("known") == "1"
        and diag.get("phase") == str(PRIME_SESSION_OFF)
        and diag.get("owner") == str(PRIME_OWNER_NONE)
        and diag.get("desired") == "0"
        and diag.get("cancel") == "0"
        and diag.get("stop") == "0"
        and int(diag.get("session", "0"), 16) == 0
        and int(diag.get("hold", "0"), 16) == 0
    )


def wait_prime_off(front: Front, timeout: float = 3.0) -> dict[str, str]:
    return wait_prime_diag(
        front,
        prime_diag_is_authoritative_off,
        "authoritative prime OFF",
        timeout,
    )


def close_prime(front: Front) -> dict[str, str]:
    front.query_prefix("PRIME:STOP", "OK:PRIME:STOP")
    front.query_prefix("PRIME:EXIT", "OK:PRIME:EXIT")
    return wait_prime_off(front)


def best_effort_close_prime(front: Front) -> None:
    errors: list[str] = []
    for command, answer in (
        ("PRIME:STOP", "OK:PRIME:STOP"),
        ("PRIME:EXIT", "OK:PRIME:EXIT"),
    ):
        try:
            front.query_prefix(command, answer)
        except (OSError, serial.SerialException, RuntimeError, ValueError) as exc:
            errors.append(f"{command}: {exc}")
    try:
        wait_prime_off(front)
    except (OSError, serial.SerialException, RuntimeError, ValueError) as exc:
        errors.append(f"OFF: {exc}")
    if errors:
        raise RuntimeError("; ".join(errors))


def check_prime(front: Front, initial: dict[str, str], channel: str, ack_limit_ms: float) -> None:
    flavor = 1 if channel == "a" else 2
    session_open = False
    try:
        # phase=OFF is also the diagnostic placeholder while known=0. Wait for
        # controller truth before deciding that it is safe to open a session.
        before = wait_prime_diag(
            front, lambda diag: diag.get("known") == "1",
            "authoritative prime discovery")
        if not prime_diag_is_authoritative_off(before):
            close_prime(front)
            before = read_prime_diag(front)
        require(
            prime_diag_is_authoritative_off(before),
            f"prime precondition is not authoritative OFF: {before}",
        )

        # Set the cleanup guard before writing. A short/failed host write can
        # still have delivered a complete command to native USB.
        session_open = True
        started = front.send(f"PRIME:START:{flavor}")
        running, answered = wait_prime_state(
            front, phase=PRIME_SESSION_RUNNING, owner=PRIME_OWNER_FRONT
        )
        require(
            running.get("PRIMECH") == str(flavor - 1),
            f"prime ran the wrong channel: {running}",
        )
        start_ms = (answered - started) * 1000.0
        require(start_ms <= ack_limit_ms,
                f"prime start acknowledgement {start_ms:.1f} ms exceeds {ack_limit_ms:.1f} ms")

        running_diag = read_prime_diag(front)
        session_token = int(running_diag.get("session", "0"), 16)
        hold_token = int(running_diag.get("hold", "0"), 16)
        require(session_token != 0 and hold_token != 0,
                f"prime did not establish fresh nonzero tokens: {running_diag}")

        # Measure the requested run only after authoritative RUNNING, not while
        # waiting for ACTIVATE/START to cross J9.
        while time.monotonic() - answered < 1.0:
            time.sleep(0.01)

        stopped = front.send("PRIME:STOP")
        _, answered = wait_prime_state(
            front, phase=PRIME_SESSION_READY, owner=PRIME_OWNER_NONE
        )
        prime_diag = read_prime_diag(front)
        require(
            prime_diag.get("outcome") == str(PRIME_OUTCOME_STOPPED),
            f"prime did not stop normally: {prime_diag}",
        )
        require(int(prime_diag.get("session", "0"), 16) == session_token and
                int(prime_diag.get("hold", "0"), 16) == hold_token,
                f"prime terminal state belongs to another run: {prime_diag}")
        elapsed_ms = int(prime_diag.get("elapsed", "0"))
        require(850 <= elapsed_ms <= 1750,
                f"prime elapsed {elapsed_ms} ms is outside the one-second run bound")
        stop_ms = (answered - stopped) * 1000.0
        require(stop_ms <= ack_limit_ms,
                f"prime stop acknowledgement {stop_ms:.1f} ms exceeds {ack_limit_ms:.1f} ms")
        off = close_prime(front)
        session_open = False
        require(prime_diag_is_authoritative_off(off),
                f"front retained local prime state after exit: {off}")
        print(f"prime {channel.upper()}     start ack {start_ms:.1f} ms, "
              f"stop ack {stop_ms:.1f} ms, elapsed {elapsed_ms} ms, OFF")
    finally:
        # Safe and idempotent even when START was accepted but its answer was
        # lost. EXIT closes the ready session on both displays after the pump
        # has been told to stop.
        active_failure = sys.exc_info()[0] is not None
        if session_open:
            try:
                best_effort_close_prime(front)
            except (OSError, serial.SerialException, RuntimeError, ValueError) as cleanup_error:
                if active_failure:
                    print(f"prime cleanup also failed — {cleanup_error}", file=sys.stderr)
                else:
                    raise
        try:
            restore_view(front, initial)
        except (OSError, serial.SerialException, RuntimeError, ValueError) as restore_error:
            if active_failure:
                print(f"view restoration also failed — {restore_error}", file=sys.stderr)
            else:
                raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--display-port", help="front display native USB port")
    parser.add_argument("--animation", action="store_true",
                        help="show the operation lock, measure animation/loop speed, and restore")
    parser.add_argument("--wake-cycles", type=int, default=0, metavar="N",
                        help="repeat the real dark-to-lit panel wake N times")
    parser.add_argument("--toggle", action="store_true",
                        help="select the other flavor, prove persistence, and restore")
    parser.add_argument("--prime", choices=("a", "b"),
                        help="ACTUATES the selected pump for about one second")
    parser.add_argument("--ack-limit-ms", type=float, default=DEFAULT_ACK_LIMIT_MS)
    parser.add_argument("--loop-limit-ms", type=int, default=DEFAULT_LOOP_LIMIT_MS)
    parser.add_argument("--min-animation-fps", type=float, default=DEFAULT_MIN_ANIMATION_FPS)
    args = parser.parse_args()

    try:
        require(args.wake_cycles >= 0, "--wake-cycles must be zero or greater")
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
            panel = read_panel_diag(front)
            for key in ("drawErr", "frameTimeout", "kickTimeout", "exioErr"):
                require(panel.get(key) == "0", f"panel reports {key}={panel.get(key)}")
            print(f"panel      {panel['frameDone']} complete frames, "
                  f"{panel['flushes']} completed submissions")
            initial_controller_health = fresh_controller_diag(front)
            initial_prime_health = read_prime_diag(front)
            if args.wake_cycles:
                check_wake_cycles(front, initial, args.wake_cycles)
            if args.animation:
                check_animation(front, initial, args.min_animation_fps, args.loop_limit_ms)
            if args.toggle:
                check_toggle(front, int(state["FLAVOR"]), args.ack_limit_ms,
                             args.loop_limit_ms)
            if args.prime:
                check_prime(front, initial, args.prime, args.ack_limit_ms)
            final_diag = fresh_controller_diag(front)
            final_prime_health = read_prime_diag(front)
            require_transport_health_unchanged(
                initial_controller_health, final_diag,
                initial_prime_health, final_prime_health)
        finally:
            front.close()
    except (OSError, serial.SerialException, RuntimeError, ValueError) as exc:
        print(f"firmware live check: FAIL — {exc}", file=sys.stderr)
        return 1

    print("firmware live check: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
