#!/usr/bin/env python3
"""Receive-only serial capture for X1 Pro interface investigation.

Requires pyserial. The host TX and modem-control conductors must be physically
absent from the machine connection. This program implements no serial writes,
probing, trigger control, break generation, or automatic device selection.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import sys
import time

try:
    import serial
    from serial.tools import list_ports
except ImportError:
    sys.exit("pyserial is required; try ~/.platformio/penv/bin/python tools/x1_control/capture.py")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def positive_seconds(value: str) -> float:
    number = float(value)
    if not math.isfinite(number) or not 0 < number <= 3600:
        raise argparse.ArgumentTypeError("seconds must be finite and between 0 and 3600")
    return number


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="list serial ports without opening them")
    parser.add_argument("--port", help="explicit serial device; never auto-selected")
    parser.add_argument("--baud", type=int, help="receiver baud rate; not an assertion about X1 firmware")
    parser.add_argument("--parity", choices=("N", "E", "O"), default="N")
    parser.add_argument("--data-bits", type=int, choices=(7, 8), default=8)
    parser.add_argument("--stop-bits", type=int, choices=(1, 2), default=1)
    parser.add_argument("--seconds", type=positive_seconds, default=30)
    parser.add_argument("--output", type=Path, help="new capture directory; existing paths are refused")
    parser.add_argument("--label", default="", help="description of the observed operation")
    parser.add_argument(
        "--rx-only-wiring-confirmed", action="store_true",
        help="confirm the connection contains only machine TX to receiver RX, and signal ground",
    )
    return parser


def capture(args: argparse.Namespace) -> int:
    # A configured but unopened Serial object allows deasserting DTR/RTS before
    # opening. Drivers may still glitch these lines; physical disconnection is
    # the protection, rather than these software settings.
    receiver = serial.Serial()
    receiver.port = args.port
    receiver.baudrate = args.baud
    receiver.bytesize = args.data_bits
    receiver.parity = args.parity
    receiver.stopbits = args.stop_bits
    receiver.timeout = 0.05
    receiver.xonxoff = False
    receiver.rtscts = False
    receiver.dsrdtr = False
    receiver.dtr = False
    receiver.rts = False
    if os.name == "posix":
        receiver.exclusive = True

    args.output.mkdir(parents=True, exist_ok=False)
    metadata = {
        "started_utc": utc_now(),
        "port": args.port,
        "baud": args.baud,
        "data_bits": args.data_bits,
        "parity": args.parity,
        "stop_bits": args.stop_bits,
        "requested_seconds": args.seconds,
        "label": args.label,
        "rx_only_wiring_confirmed": True,
        "serial_transmit_operations": 0,
        "timing_scope": "host read batches, not individual UART edges",
    }
    metadata_path = args.output / "capture.json"
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n")
    offset = 0
    batches = 0
    started = time.monotonic()
    outcome = "complete"
    exit_code = 0
    try:
        with (args.output / "raw.bin").open("xb") as raw, (args.output / "events.jsonl").open("x") as events:
            receiver.open()
            started = time.monotonic()
            deadline = started + args.seconds
            print(f"Listening on {args.port} at {args.baud} {args.data_bits}{args.parity}{args.stop_bits}", flush=True)
            print(f"Capture directory: {args.output.resolve()}", flush=True)
            print("No commands are sent. Ctrl-C preserves the captured data.", flush=True)
            next_progress = started + 5
            while time.monotonic() < deadline:
                chunk = receiver.read(min(65536, max(1, receiver.in_waiting)))
                now = time.monotonic()
                if chunk:
                    raw.write(chunk)
                    raw.flush()
                    events.write(json.dumps({
                        "elapsed_s": round(now - started, 6),
                        "utc": utc_now(),
                        "offset": offset,
                        "length": len(chunk),
                        "hex": chunk.hex(),
                    }) + "\n")
                    events.flush()
                    offset += len(chunk)
                    batches += 1
                if now >= next_progress:
                    print(f"Received {offset} bytes in {batches} host read batches", flush=True)
                    next_progress = now + 5
    except KeyboardInterrupt:
        outcome = "interrupted"
        exit_code = 130
    except (OSError, serial.SerialException) as exc:
        outcome = "error"
        metadata["error"] = str(exc)
        print(f"Capture error: {exc}", file=sys.stderr)
        exit_code = 1
    finally:
        receiver.close()
        metadata.update({
            "ended_utc": utc_now(),
            "elapsed_s": round(time.monotonic() - started, 6),
            "bytes_received": offset,
            "read_batches": batches,
            "outcome": outcome,
        })
        metadata_path.write_text(json.dumps(metadata, indent=2) + "\n")

    print(f"{outcome}: {offset} bytes received; no serial transmit operations", flush=True)
    if not offset:
        print("Silence does not establish the baud rate, protocol, or absence of computer control.", flush=True)
    return exit_code


def main() -> int:
    parser = make_parser()
    args = parser.parse_args()
    if args.list:
        for port in sorted(list_ports.comports(), key=lambda item: item.device):
            usb_id = f"{port.vid:04x}:{port.pid:04x}" if port.vid is not None and port.pid is not None else "no USB ID"
            print(f"{port.device}\t{port.description}\t{usb_id}")
        return 0
    if not args.port or not args.baud or not args.output:
        parser.error("capture requires --port, --baud and --output")
    if args.baud <= 0:
        parser.error("baud must be positive")
    if not args.rx_only_wiring_confirmed:
        parser.error("verify physical receive-only wiring and pass --rx-only-wiring-confirmed")
    try:
        return capture(args)
    except (OSError, ValueError, serial.SerialException) as exc:
        print(f"Cannot start capture: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
