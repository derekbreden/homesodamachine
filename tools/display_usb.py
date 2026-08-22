#!/usr/bin/env python3
"""Make the externally-powered 4.3B display reattach to this computer's USB.

The command goes through the controller PCBA's CH340C and J9. A running
front-display application briefly deep-sleeps the S3 USB PHY; neither the
appliance's 12 V rail nor any load is switched.

Run with any Python that has pyserial; PlatformIO's always does:

    ~/.platformio/penv/bin/python tools/display_usb.py
"""

from __future__ import annotations

import argparse
import sys
import time

try:
    import serial
    from serial.tools import list_ports
except ImportError:
    sys.exit("pyserial not found - try ~/.platformio/penv/bin/python tools/display_usb.py")


CH340 = (0x1A86, 0x7523)
ESP32_S3 = (0x303A, 0x1001)
RESULTS = (b"DISPLAY_USB:APP", b"DISPLAY_USB:UNREACHABLE")


def ports_with_id(hwid: tuple[int, int]):
    return [p for p in list_ports.comports() if (p.vid, p.pid) == hwid]


def open_without_modem_reset(port: str, timeout: float = 0.05):
    # Set the lines before open so pyserial does not pulse the PCBA's Q2/Q3
    # auto-reset lattice merely to ask its already-running console for a command.
    ser = serial.Serial()
    ser.port = port
    ser.baudrate = 115200
    ser.timeout = timeout
    ser.write_timeout = 1
    ser.dtr = False
    ser.rts = False
    ser.open()
    return ser


def ask_controller(port: str) -> tuple[bytes | None, str]:
    with open_without_modem_reset(port) as ser:
        ser.reset_input_buffer()
        seen = bytearray()

        # A driver can still reset a CH340 when the port first opens. Retrying the
        # line also covers the controller finishing setup after that reset.
        for _ in range(3):
            ser.write(b"\ndisplay usb\n")
            ser.flush()
            until = time.monotonic() + 4.0
            while time.monotonic() < until:
                chunk = ser.read(ser.in_waiting or 1)
                if chunk:
                    seen.extend(chunk)
                    for marker in RESULTS:
                        if marker in seen:
                            # Finish the status line so diagnostics do not end at the
                            # marker merely because the UART read split the packet.
                            seen.extend(ser.readline())
                            text = seen.decode("utf-8", errors="replace")
                            return marker, text
                else:
                    time.sleep(0.02)
        return None, seen.decode("utf-8", errors="replace")


def front_version(timeout_s: float = 18.0) -> tuple[str, str] | None:
    until = time.monotonic() + timeout_s
    while time.monotonic() < until:
        for port in ports_with_id(ESP32_S3):
            try:
                with open_without_modem_reset(port.device, timeout=0.1) as ser:
                    ser.reset_input_buffer()
                    for _ in range(3):
                        ser.write(b"GET_VERSION\n")
                        ser.flush()
                        wait = time.monotonic() + 0.8
                        reply = bytearray()
                        while time.monotonic() < wait:
                            reply.extend(ser.read(ser.in_waiting or 1))
                            if b"VERSION:FRONT=" in reply:
                                for line in reply.decode("utf-8", errors="replace").splitlines():
                                    if line.startswith("VERSION:FRONT="):
                                        return port.device, line
                            time.sleep(0.02)
            except (OSError, serial.SerialException):
                pass
        time.sleep(0.5)
    return None


def wait_for_front(timeout_s: float = 12.0):
    until = time.monotonic() + timeout_s
    while time.monotonic() < until:
        found = ports_with_id(ESP32_S3)
        if found:
            return found[0]
        time.sleep(0.25)
    return None


def wait_until_absent(paths: set[str], timeout_s: float = 4.0) -> bool:
    """Observe the old USB attachment leave before accepting its replacement."""
    until = time.monotonic() + timeout_s
    while time.monotonic() < until:
        live = {p.device for p in ports_with_id(ESP32_S3)}
        if not paths.intersection(live):
            return True
        time.sleep(0.05)
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--controller-port", help="PCBA CH340C port (auto-detected by default)")
    args = parser.parse_args()

    if args.controller_port:
        controller = args.controller_port
    else:
        pcba = ports_with_id(CH340)
        if not pcba:
            print("controller PCBA not found (expected CH340C 1a86:7523)", file=sys.stderr)
            return 2
        if len(pcba) > 1:
            choices = ", ".join(p.device for p in pcba)
            print(f"more than one controller PCBA found: {choices}; use --controller-port", file=sys.stderr)
            return 2
        controller = pcba[0].device

    old_fronts = {p.device for p in ports_with_id(ESP32_S3)}
    print(f"controller  {controller}")
    result, transcript = ask_controller(controller)
    for line in transcript.splitlines():
        if "DISPLAY_USB:" in line:
            print(line.strip())
    if result in (None, RESULTS[-1]):
        if "DISPLAY_USB:UNREACHABLE" not in transcript:
            print("controller did not recognize or finish 'display usb'; flash env appliance first",
                  file=sys.stderr)
        return 1

    if result == RESULTS[0] and old_fronts and not wait_until_absent(old_fronts):
        print("display accepted the command, but its previous USB attachment never detached",
              file=sys.stderr)
        return 1

    if not wait_for_front():
        print("display command succeeded, but no 303a:1001 USB device enumerated", file=sys.stderr)
        return 1

    identified = front_version()
    if not identified:
        print("USB enumerated, but the front application did not answer GET_VERSION", file=sys.stderr)
        return 1
    port, version = identified
    print(f"display     {port}")
    print(version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
