#!/usr/bin/env python3
"""Live regression checks through the enclosure display's native USB port.

The default check is observational: version, touch/display health, and J9 link.
It never opens the main board's CH340 port, whose DTR/RTS lines reset it.

Optional checks are explicit and non-actuating unless ``--prime`` is named:

    ~/.platformio/penv/bin/python tools/firmware_live_check.py --animation
    ~/.platformio/penv/bin/python tools/firmware_live_check.py --wake-cycles 20
    ~/.platformio/penv/bin/python tools/firmware_live_check.py --toggle
    ~/.platformio/penv/bin/python tools/firmware_live_check.py --prime b

--animation opens the reusable operation lock, measures its logo animation, then
restores the page/idle/lock state it found. --wake-cycles repeatedly takes the
actual dark-to-lit path and checks its frame/reset telemetry. --toggle selects the
other flavor, proves main board synchronization and persistence, then restores it.
--prime runs the selected flavor pump for one second through the display's real
hold handlers and always posts PRIME:STOP and PRIME:EXIT in a finally block. It
proves the run belongs to a newly opened session, checks the measured elapsed
interval, and waits for authoritative OFF cleanup. The main board's own stale-tick
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
PRIME_OWNER_ENCLOSURE = 1
PRIME_OUTCOME_STOPPED = 1


def display_port(explicit: str | None) -> str:
    if explicit:
        return explicit
    ports = [p.device for p in list_ports.comports() if (p.vid, p.pid) == ESP32_S3]
    if len(ports) == 1:
        return ports[0]
    if not ports:
        raise RuntimeError("enclosure display not found (expected native USB 303a:1001)")
    raise RuntimeError("more than one S3 is connected; name it with --display-port")


def fields(line: str, prefix: str) -> dict[str, str]:
    if not line.startswith(prefix):
        raise RuntimeError(f"expected {prefix}, got {line!r}")
    out: dict[str, str] = {}
    for item in line[len(prefix):].split(","):
        if "=" in item:
            key, value = item.split("=", 1)
            out[key] = value
    return out


class EnclosureDisplay:
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


def snapshot(display: EnclosureDisplay) -> tuple[str, dict[str, str], dict[str, str], str]:
    version = display.query_prefix("GET_VERSION", "VERSION:ENCLOSURE=")
    state = fields(display.query_prefix("GET_STATE", "STATE:"), "STATE:")
    diag_line = display.query_prefix("GET_DIAG", "DIAG:")
    link = display.query_prefix("LINK", "LINK:")
    return version, state, fields(diag_line, "DIAG:"), link


def read_panel_diag(display: EnclosureDisplay) -> dict[str, str]:
    return fields(display.query_prefix("GET_PANEL", "PANEL:"), "PANEL:")


def wake_once(display: EnclosureDisplay, timeout: float = 1.5) -> tuple[dict[str, str], float]:
    """Exercise a real dark wake and wait for the staged panel recovery."""
    before = read_panel_diag(display)
    require(before.get("kickStage") == "0", f"panel kick already active: {before}")
    display.query_prefix("IDLE:1", "OK:IDLE=1")
    time.sleep(0.05)
    dark = read_panel_diag(display)
    require(dark.get("bl") == "0", f"panel did not go dark: {dark}")
    for key in ("drawErr", "frameTimeout", "kickTimeout", "phaseErr", "scanRecover", "exioErr"):
        require(int(dark[key]) == int(before[key]),
                f"panel {key} changed while going dark: {before[key]} -> {dark[key]}")
    started = time.monotonic()
    display.query_prefix("IDLE:0", "OK:IDLE=0")

    deadline = time.monotonic() + timeout
    after: dict[str, str] = {}
    while time.monotonic() < deadline:
        after = read_panel_diag(display)
        if (int(after["kickStart"]) > int(before["kickStart"]) and
                int(after["kickDone"]) > int(before["kickDone"]) and
                after.get("kickStage") == "0" and after.get("bl") == "1"):
            break
        time.sleep(0.02)
    else:
        raise RuntimeError(f"panel wake did not complete: {after}")

    for key in ("drawErr", "frameTimeout", "kickTimeout", "phaseErr", "scanRecover", "exioErr"):
        require(int(after[key]) == int(before[key]),
                f"panel {key} changed during wake: {before[key]} -> {after[key]}")
    require(int(after["phaseDone"]) - int(before["phaseDone"]) >= 2,
            f"wake did not phase reset and DISP at VSYNC: {before} -> {after}")
    for key in ("vsync", "frameDone"):
        require(int(after[key]) - int(before[key]) >= WAKE_REQUIRED_FRAMES,
                f"wake crossed too few {key} events: {before} -> {after}")
    return after, (time.monotonic() - started) * 1000.0


def fresh_main_board_diag(display: EnclosureDisplay) -> dict[str, str]:
    """Read status twice so the second snapshot includes the first turn's audit."""
    diag = fields(display.query_prefix("GET_DIAG", "DIAG:"), "DIAG:")
    main_board_rx = int(diag.get("ctrlRx", "0"))
    for _ in range(2):
        deadline = time.monotonic() + 2.0
        next_request = 0.0
        while time.monotonic() < deadline:
            now = time.monotonic()
            # A main-board-owned prime transition or queued announcement can
            # legitimately consume this J9 turn. Re-request at a restrained
            # cadence until an actual StatusPayload lands instead of treating
            # that deferred response as a failed link audit.
            if now >= next_request:
                display.query_prefix("STATUS", "OK:STATUS requested")
                next_request = now + 0.15
            diag = fields(display.query_prefix("GET_DIAG", "DIAG:"), "DIAG:")
            updated_rx = int(diag.get("ctrlRx", "0"))
            if updated_rx != main_board_rx:
                main_board_rx = updated_rx
                break
            time.sleep(0.02)
        else:
            raise RuntimeError(f"main board status did not refresh: {diag}")
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
            f"enclosure display send error after check: {after.get('sendErr')}")
    for field, label in (("reinits", "link reinitializations"),
                         ("outDrop", "outbound queue drops")):
        require(int(after.get(field, "0")) == int(before.get(field, "0")),
                f"enclosure display {label} changed during check: "
                f"{before.get(field, '0')} -> {after.get(field, '0')}")
    require(
        int(prime_after.get("staleReinits", "0")) ==
        int(prime_before.get("staleReinits", "0")),
        "prime session required a J9 stale-link reinitialization during check: "
        f"{prime_before.get('staleReinits', '0')} -> "
        f"{prime_after.get('staleReinits', '0')}",
    )
    require(int(after.get("ctrlTurnMax", "255")) <= 1,
            f"main board emitted {after.get('ctrlTurnMax')} replies in one J9 turn")
    require(int(after.get("ctrlTurnOver", "0")) ==
            int(before.get("ctrlTurnOver", "0")),
            "main board J9 multi-reply turns changed during check: "
            f"{before.get('ctrlTurnOver', '0')} -> {after.get('ctrlTurnOver', '0')}")


def restore_view(display: EnclosureDisplay, initial: dict[str, str]) -> None:
    page = int(initial.get("page", "0"))
    stage = int(initial.get("stage", "0"))
    display.query_prefix(f"PAGE:{page}", "OK:PAGE=")
    if initial.get("idle") == "1" or stage > 0:
        display.query_prefix(f"IDLE:{max(1, min(stage, 3))}", "OK:IDLE=")
    if initial.get("lock") == "1":
        display.query_prefix("LOCK:SHOW", "OK:LOCK=1")
    else:
        display.query_prefix("LOCK:HIDE", "OK:LOCK=0")


def check_wake_cycles(display: EnclosureDisplay, initial: dict[str, str], cycles: int) -> None:
    if cycles < 1:
        return
    durations: list[float] = []
    try:
        for _ in range(cycles):
            _, elapsed_ms = wake_once(display)
            durations.append(elapsed_ms)
            time.sleep(0.05)
        print(f"wake        {cycles} cycles, {min(durations):.1f}–{max(durations):.1f} ms, "
              "no panel/expander errors")
    finally:
        restore_view(display, initial)


def check_animation(display: EnclosureDisplay, initial: dict[str, str], min_fps: float, loop_limit: int) -> None:
    try:
        _, wake_ms = wake_once(display)
        display.query_prefix("LOCK:SHOW", "OK:LOCK=1")
        time.sleep(0.3)  # finish the post-wake animation quiet window

        first = fields(display.query_prefix("GET_DIAG", "DIAG:"), "DIAG:")
        flush0 = int(first["flushes"])
        started = time.monotonic()
        time.sleep(2.0)
        second = fields(display.query_prefix("GET_DIAG", "DIAG:"), "DIAG:")
        elapsed = time.monotonic() - started
        fps = (int(second["flushes"]) - flush0) / elapsed
        max_loop = int(second["maxLoopMs"])

        require(fps >= min_fps, f"lock-screen animation only advanced at {fps:.2f} fps")
        require(max_loop <= loop_limit,
                f"display loop high-water {max_loop} ms exceeds {loop_limit} ms")
        print(f"animation  {fps:.2f} flushes/s, loop high-water {max_loop} ms, "
              f"wake {wake_ms:.1f} ms")
    finally:
        display.query_prefix("LOCK:HIDE", "OK:LOCK=0")
        restore_view(display, initial)
        # LOCK:HIDE invalidates the whole 800x480 surface. Let that one-time
        # restoration render before a following latency check starts its clock.
        time.sleep(0.35)


def wait_flavor(display: EnclosureDisplay, flavor: int, durable: bool, timeout: float = 4.0) -> dict[str, str]:
    deadline = time.monotonic() + timeout
    last: dict[str, str] = {}
    while time.monotonic() < deadline:
        last = fields(display.query_prefix("GET_STATE", "STATE:"), "STATE:")
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


def check_toggle(display: EnclosureDisplay, initial_flavor: int, ack_limit_ms: float, loop_limit: int) -> None:
    target = initial_flavor ^ 1
    restore_needed = False
    try:
        restore_needed = True
        started = display.send(f"FLAVOR:{target}")
        line, _ = display.wait_line(lambda value: value.startswith("OK:FLAVOR="),
                                  1.5, "OK:FLAVOR")
        require(line == f"OK:FLAVOR={target}", f"unexpected selection answer: {line}")
        wait_flavor(display, target, durable=False)
        ack_ms = (time.monotonic() - started) * 1000.0
        require(ack_ms <= ack_limit_ms,
                f"flavor synchronization {ack_ms:.1f} ms exceeds {ack_limit_ms:.1f} ms")
        wait_flavor(display, target, durable=True)
        diag = fields(display.query_prefix("GET_DIAG", "DIAG:"), "DIAG:")
        max_loop = int(diag["maxLoopMs"])
        require(max_loop <= loop_limit,
                f"flavor repaint loop high-water {max_loop} ms exceeds {loop_limit} ms")
        print(f"flavor     selected {target}, main board ack {ack_ms:.1f} ms, "
              f"repaint loop {max_loop} ms, durable")
    finally:
        if restore_needed:
            display.query_prefix(f"FLAVOR:{initial_flavor}", "OK:FLAVOR=")
            wait_flavor(display, initial_flavor, durable=True)
            print(f"restore    flavor {initial_flavor}, main board durable")


def wait_prime_state(
    display: EnclosureDisplay,
    phase: int,
    owner: int,
    timeout: float = 2.5,
) -> tuple[dict[str, str], float]:
    deadline = time.monotonic() + timeout
    last: dict[str, str] = {}
    while time.monotonic() < deadline:
        line = display.query_prefix("GET_STATE", "STATE:", timeout=0.5)
        last = fields(line, "STATE:")
        if last.get("PRIME") == str(phase) and last.get("OWNER") == str(owner):
            return last, time.monotonic()
        time.sleep(0.01)
    raise RuntimeError(
        f"prime did not reach phase={phase}, owner={owner}: {last}"
    )


def read_prime_diag(display: EnclosureDisplay) -> dict[str, str]:
    return fields(
        display.query_prefix("GET_DIAG", "DIAG_PRIME:"), "DIAG_PRIME:"
    )


def wait_prime_diag(display: EnclosureDisplay, predicate, what: str, timeout: float = 3.0) -> dict[str, str]:
    deadline = time.monotonic() + timeout
    last: dict[str, str] = {}
    while time.monotonic() < deadline:
        last = read_prime_diag(display)
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


def wait_prime_off(display: EnclosureDisplay, timeout: float = 3.0) -> dict[str, str]:
    return wait_prime_diag(
        display,
        prime_diag_is_authoritative_off,
        "authoritative prime OFF",
        timeout,
    )


def close_prime(display: EnclosureDisplay) -> dict[str, str]:
    display.query_prefix("PRIME:STOP", "OK:PRIME:STOP")
    display.query_prefix("PRIME:EXIT", "OK:PRIME:EXIT")
    return wait_prime_off(display)


def best_effort_close_prime(display: EnclosureDisplay) -> None:
    errors: list[str] = []
    for command, answer in (
        ("PRIME:STOP", "OK:PRIME:STOP"),
        ("PRIME:EXIT", "OK:PRIME:EXIT"),
    ):
        try:
            display.query_prefix(command, answer)
        except (OSError, serial.SerialException, RuntimeError, ValueError) as exc:
            errors.append(f"{command}: {exc}")
    try:
        wait_prime_off(display)
    except (OSError, serial.SerialException, RuntimeError, ValueError) as exc:
        errors.append(f"OFF: {exc}")
    if errors:
        raise RuntimeError("; ".join(errors))


def check_prime(display: EnclosureDisplay, initial: dict[str, str], channel: str, ack_limit_ms: float) -> None:
    flavor = 1 if channel == "a" else 2
    session_open = False
    try:
        # phase=OFF is also the diagnostic placeholder while known=0. Wait for
        # main board truth before deciding that it is safe to open a session.
        before = wait_prime_diag(
            display, lambda diag: diag.get("known") == "1",
            "authoritative prime discovery")
        if not prime_diag_is_authoritative_off(before):
            close_prime(display)
            before = read_prime_diag(display)
        require(
            prime_diag_is_authoritative_off(before),
            f"prime precondition is not authoritative OFF: {before}",
        )

        # Set the cleanup guard before writing. A short/failed host write can
        # still have delivered a complete command to native USB.
        session_open = True
        started = display.send(f"PRIME:START:{flavor}")
        running, answered = wait_prime_state(
            display, phase=PRIME_SESSION_RUNNING, owner=PRIME_OWNER_ENCLOSURE
        )
        require(
            running.get("PRIMECH") == str(flavor - 1),
            f"prime ran the wrong channel: {running}",
        )
        start_ms = (answered - started) * 1000.0
        require(start_ms <= ack_limit_ms,
                f"prime start acknowledgement {start_ms:.1f} ms exceeds {ack_limit_ms:.1f} ms")

        running_diag = read_prime_diag(display)
        session_token = int(running_diag.get("session", "0"), 16)
        hold_token = int(running_diag.get("hold", "0"), 16)
        require(session_token != 0 and hold_token != 0,
                f"prime did not establish fresh nonzero tokens: {running_diag}")

        # Measure the requested run only after authoritative RUNNING, not while
        # waiting for ACTIVATE/START to cross J9.
        while time.monotonic() - answered < 1.0:
            time.sleep(0.01)

        stopped = display.send("PRIME:STOP")
        _, answered = wait_prime_state(
            display, phase=PRIME_SESSION_READY, owner=PRIME_OWNER_NONE
        )
        prime_diag = read_prime_diag(display)
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
        off = close_prime(display)
        session_open = False
        require(prime_diag_is_authoritative_off(off),
                f"enclosure display retained local prime state after exit: {off}")
        print(f"prime {channel.upper()}     start ack {start_ms:.1f} ms, "
              f"stop ack {stop_ms:.1f} ms, elapsed {elapsed_ms} ms, OFF")
    finally:
        # Safe and idempotent even when START was accepted but its answer was
        # lost. EXIT closes the ready session on both displays after the pump
        # has been told to stop.
        active_failure = sys.exc_info()[0] is not None
        if session_open:
            try:
                best_effort_close_prime(display)
            except (OSError, serial.SerialException, RuntimeError, ValueError) as cleanup_error:
                if active_failure:
                    print(f"prime cleanup also failed — {cleanup_error}", file=sys.stderr)
                else:
                    raise
        try:
            restore_view(display, initial)
        except (OSError, serial.SerialException, RuntimeError, ValueError) as restore_error:
            if active_failure:
                print(f"view restoration also failed — {restore_error}", file=sys.stderr)
            else:
                raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--display-port", help="enclosure display native USB port")
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
        display = EnclosureDisplay(port)
        try:
            version, state, diag, link = snapshot(display)
            require(diag.get("gt911") not in (None, "0x00"), "GT911 touch controller absent")
            require(diag.get("reinits") == "0",
                    f"enclosure display link reinitialized {diag.get('reinits')} times")
            require(diag.get("sendErr") == "0", f"enclosure display send error {diag.get('sendErr')}")
            if "outDrop" in diag:
                require(diag["outDrop"] == "0",
                        f"enclosure display outbound queue dropped {diag['outDrop']} frames")
            require(diag.get("link") == "rx", "enclosure display has received no J9 frame")
            require(state.get("SYNC") == "1", "enclosure display flavor is not synchronized")
            require(state.get("PERSISTED") == "1", "main board flavor is not persisted")
            require(state.get("PERSISTERR") == "0", "main board flavor persistence failed")
            require(state.get("PENDING") == "0", "enclosure display flavor request remains pending")
            match = re.search(r"framesRx=(\d+),framesTx=(\d+)", link)
            require(match is not None and int(match.group(1)) > 0, f"unhealthy J9 report: {link}")

            print(version)
            print(f"display    GT911 {diag['gt911']}, heap {diag.get('heap')}, "
                  f"min {diag.get('minHeap')}, idle stage {diag.get('stage')}")
            print(f"link       rx {match.group(1)}, tx {match.group(2)}, reinits {diag.get('reinits')}")
            print(f"flavor     {state['FLAVOR']}, main board synchronized and durable")

            initial = dict(diag)
            panel = read_panel_diag(display)
            for key in ("drawErr", "frameTimeout", "kickTimeout", "exioErr"):
                require(panel.get(key) == "0", f"panel reports {key}={panel.get(key)}")
            print(f"panel      {panel['frameDone']} complete frames, "
                  f"{panel['flushes']} completed submissions")
            initial_main_board_health = fresh_main_board_diag(display)
            initial_prime_health = read_prime_diag(display)
            if args.wake_cycles:
                check_wake_cycles(display, initial, args.wake_cycles)
            if args.animation:
                check_animation(display, initial, args.min_animation_fps, args.loop_limit_ms)
            if args.toggle:
                check_toggle(display, int(state["FLAVOR"]), args.ack_limit_ms,
                             args.loop_limit_ms)
            if args.prime:
                check_prime(display, initial, args.prime, args.ack_limit_ms)
            final_diag = fresh_main_board_diag(display)
            final_prime_health = read_prime_diag(display)
            require_transport_health_unchanged(
                initial_main_board_health, final_diag,
                initial_prime_health, final_prime_health)
        finally:
            display.close()
    except (OSError, serial.SerialException, RuntimeError, ValueError) as exc:
        print(f"firmware live check: FAIL — {exc}", file=sys.stderr)
        return 1

    print("firmware live check: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
