#!/usr/bin/env python3
"""Push a firmware image to a board through the main board's USB console.

The main board holds no image — it holds one chunk. The receiving board asks
for the offset it is ready to write, the main board asks this script for those
bytes, and passes them on. So the transfer is paced from here and nothing is
buffered anywhere in between.

    ~/.platformio/penv/bin/python tools/ota.py faucet
    ~/.platformio/penv/bin/python tools/ota.py enclosure
    ~/.platformio/penv/bin/python tools/ota.py self

With no --image it uses the build that env just produced, so the usual shape is
`pio run -e esp32s3_faucet` and then this.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
import zlib

try:
    import serial
    from serial.tools import list_ports
except ImportError:
    sys.exit("pyserial not found - try ~/.platformio/penv/bin/python tools/ota.py")

CH340 = (0x1A86, 0x7523)
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Which build each target is flashed from, and the env that produces it.
TARGETS = {
    "self":      ("appliance",      "the main board's own spare slot"),
    "faucet":    ("esp32s3_faucet", "the faucet display, over J3"),
    "enclosure": ("esp32s3_front",  "the enclosure display, over J9"),
}


def main_board_port() -> str:
    ports = [p for p in list_ports.comports() if (p.vid, p.pid) == CH340]
    if not ports:
        sys.exit("no main board on USB (looking for the CH340C at J14)")
    if len(ports) > 1:
        sys.exit(f"more than one CH340 present: {', '.join(p.device for p in ports)}")
    return ports[0].device


def open_console(port: str) -> serial.Serial:
    # Opening this port drives the board's Q2/Q3 auto-reset lattice, so the
    # console that answers is always a freshly booted one. Wait for it rather
    # than talking over the boot banner.
    ser = serial.Serial()
    ser.port = port
    ser.baudrate = 115200
    ser.timeout = 0.2
    ser.write_timeout = 5
    ser.dtr = False
    ser.rts = False
    ser.open()
    time.sleep(2.5)
    ser.reset_input_buffer()
    return ser


def run(target: str, image: str, verbose: bool) -> int:
    data = open(image, "rb").read()
    crc = zlib.crc32(data) & 0xFFFFFFFF
    size = len(data)
    print(f"{os.path.relpath(image, REPO)}  {size:,} bytes  crc32 {crc:#010x}")
    print(f"target: {target} — {TARGETS[target][1]}")

    port = main_board_port()
    ser = open_console(port)
    print(f"main board on {port}")

    ser.write(f"ota {target} {size} {crc}\n".encode())
    ser.flush()

    started = time.time()
    sent = 0
    last_print = 0.0
    buf = b""

    while True:
        chunk = ser.read(256)
        if chunk:
            buf += chunk
        elif time.time() - started > 900:
            print("\ntimed out")
            ser.close()
            return 1

        while b"\n" in buf:
            line, buf = buf.split(b"\n", 1)
            line = line.decode(errors="replace").strip()
            if not line:
                continue
            if verbose and not line.startswith("OTA:NEED"):
                print(f"  [{line}]")

            if line.startswith("OTA:NEED"):
                _, off_s, len_s = line.split()
                off, want = int(off_s), int(len_s)
                ser.write(data[off:off + want])
                ser.flush()
                sent = off + want
                now = time.time()
                if now - last_print > 0.5:
                    last_print = now
                    pct = 100.0 * sent / size
                    rate = sent / max(now - started, 0.001) / 1024
                    print(f"\r  {pct:5.1f}%  {sent:,}/{size:,}  {rate:6.1f} KB/s", end="", flush=True)

            elif line.startswith("OTA:DONE"):
                el = time.time() - started
                print(f"\r  100.0%  {size:,}/{size:,}  in {el:.0f}s" + " " * 12)
                print("verified and set to boot — the board restarts itself")
                ser.close()
                return 0

            elif line.startswith("OTA:FAIL") or line.startswith("OTA:ABORT"):
                print(f"\n{line}")
                ser.close()
                return 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", choices=sorted(TARGETS))
    ap.add_argument("--image", help="path to a firmware.bin (default: this target's build)")
    ap.add_argument("-v", "--verbose", action="store_true", help="echo the console's own lines")
    a = ap.parse_args()

    img = a.image or os.path.join(REPO, ".pio", "build", TARGETS[a.target][0], "firmware.bin")
    if not os.path.exists(img):
        sys.exit(f"no image at {img} — build it first: pio run -e {TARGETS[a.target][0]}")
    sys.exit(run(a.target, img, a.verbose))
