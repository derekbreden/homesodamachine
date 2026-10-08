#!/usr/bin/env python3
"""Send one command line to the X1 Pro rear-port console and capture the reply.

The rear RS232 port is the laser controller's RT-Thread ``msh`` shell. This tool
writes a single operator-supplied command line, then records what the machine
returns for a fixed listen window. The receive path matches ``capture.py``.

Discovery uses read commands only (``status``, ``iostate``, ``error``,
``cur_pro``, ``getall``, ``worktime``, ``sn``, ``ver`` …). Do not script the
live actuators (``onkey``, ``power``, ``pilot``, ``gas``, ``pulse``, ``feeder``,
a ``dflt*``/``fac*`` restore, ``reboot``): the hardware interlocks gate laser
emission, not this tool, and a bounded write test belongs in the staged plan in
README.md with the key off and both E-stops engaged.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time

try:
    import serial
    from serial.tools import list_ports
except ImportError:
    sys.exit("pyserial is required; try ~/.platformio/penv/bin/python tools/x1_control/console.py")

EOL = {"cr": "\r", "lf": "\n", "crlf": "\r\n"}


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="list serial ports without opening them")
    parser.add_argument("--port", help="explicit serial device; never auto-selected")
    parser.add_argument("--baud", type=int, default=115200, help="115200 8N1 is the observed console rate")
    parser.add_argument("--cmd", help="one command line to send to the msh shell")
    parser.add_argument("--eol", choices=tuple(EOL), default="cr", help="line terminator the shell runs on")
    parser.add_argument("--seconds", type=float, default=4.0, help="listen window after the command is sent")
    parser.add_argument("--output", type=Path, help="new capture directory; existing paths are refused")
    parser.add_argument("--label", default="", help="description of the command's purpose")
    return parser


def run(args: argparse.Namespace) -> int:
    console = serial.Serial()
    console.port = args.port
    console.baudrate = args.baud
    console.bytesize = 8
    console.parity = "N"
    console.stopbits = 1
    console.timeout = 0.05
    console.xonxoff = False
    console.rtscts = False
    console.dsrdtr = False

    args.output.mkdir(parents=True, exist_ok=False)
    console.open()
    time.sleep(0.25)
    console.reset_input_buffer()

    sent = (args.cmd + EOL[args.eol]).encode("latin-1")
    console.write(sent)
    console.flush()

    buffer = bytearray()
    deadline = time.monotonic() + args.seconds
    while time.monotonic() < deadline:
        chunk = console.read(4096)
        if chunk:
            buffer += chunk
    console.close()

    (args.output / "raw.bin").write_bytes(buffer)
    (args.output / "console.json").write_text(json.dumps({
        "utc": datetime.now(timezone.utc).isoformat(),
        "port": args.port,
        "baud": args.baud,
        "command": args.cmd,
        "eol": args.eol,
        "listen_seconds": args.seconds,
        "label": args.label,
        "bytes_received": len(buffer),
    }, indent=2) + "\n")

    sys.stdout.write(buffer.decode("latin-1"))
    sys.stdout.write(f"\n---\n[{len(buffer)} bytes captured]\n")
    return 0


def main() -> int:
    parser = make_parser()
    args = parser.parse_args()
    if args.list:
        for port in sorted(list_ports.comports(), key=lambda item: item.device):
            usb_id = f"{port.vid:04x}:{port.pid:04x}" if port.vid is not None and port.pid is not None else "no USB ID"
            print(f"{port.device}\t{port.description}\t{usb_id}")
        return 0
    if not args.port or not args.cmd or not args.output:
        parser.error("console requires --port, --cmd and --output")
    try:
        return run(args)
    except (OSError, ValueError, serial.SerialException) as exc:
        print(f"Cannot run console command: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
