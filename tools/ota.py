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
# What each target's tree stamps into its own fw_version.h. A flash is checked
# against this afterwards, because the failure worth catching is not a transfer
# that breaks — that reports itself — but one that carries a stale image: a
# build that did not run, whose previous firmware.bin is still on disk and gets
# sent anyway. That flashes cleanly, verifies cleanly, and leaves the board
# running code the source no longer describes, which is invisible until someone
# spends an afternoon testing fixes that were never on the board.
VERSION_HEADERS = {
    "self":      "firmware/src_appliance/fw_version.h",
    "faucet":    "firmware/src_faucet/fw_version.h",
    "enclosure": "firmware/src_front/fw_version.h",
}

TARGETS = {
    "self":      ("appliance",      "the main board's own spare slot"),
    "faucet":    ("esp32s3_faucet", "the faucet display, over J3"),
    "enclosure": ("esp32s3_front",  "the enclosure display, over J9"),
    "art":       ("esp32s3_front",  "the enclosure display's art partition, over J9"),
}

# The art partition is not a firmware image and is not built by pio; it is laid
# out from the same frame headers the firmware used to compile in.
ART_IMAGE = os.path.join(REPO, ".pio", "build", "esp32s3_front", "art.bin")


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
    # Small: every chunk costs one of these waits, and at 1 KB a chunk a 200 ms
    # blocking read is most of the transfer. 5 ms keeps the pipe wire-bound.
    ser.timeout = 0.005
    ser.write_timeout = 5
    ser.dtr = False
    ser.rts = False
    ser.open()

    # Opening reset the board. Let it boot, throw away the banner, then ask for
    # a prompt and wait for that one — a `>` already sitting in the port buffer
    # is the previous session's, and taking it means writing the command into a
    # console that is still coming up, where it is simply lost.
    # Let the boot banner run out, then ask something harmless and wait for the
    # answer. A bare newline draws no reply at all — the console only acts on a
    # non-empty line — and a `>` already in the buffer is the previous session's,
    # so neither is proof that anyone is listening yet.
    quiet_since = time.time()
    while time.time() - quiet_since < 0.4:
        if ser.read(max(1, ser.in_waiting)):
            quiet_since = time.time()
        if time.time() - quiet_since > 12:
            break
    ser.reset_input_buffer()

    deadline = time.time() + 10
    ser.write(b"ota\n")
    ser.flush()
    seen = b""
    while time.time() < deadline:
        seen += ser.read(max(1, ser.in_waiting))
        if seen.rstrip().endswith(b">"):
            break
        time.sleep(0.02)
    else:
        sys.exit("the main board never answered — is it powered at J10?")
    if b"SINGLE SLOT" in seen:
        sys.exit("the main board still has a single-slot partition table")
    ser.reset_input_buffer()
    return ser


def expected_version(target: str) -> str | None:
    """What the tree this target is built from currently stamps."""
    rel = VERSION_HEADERS.get(target)
    if not rel:
        return None
    try:
        with open(os.path.join(REPO, rel)) as f:
            for line in f:
                if "FW_VERSION" in line and '"' in line:
                    return line.split('"')[1]
    except OSError:
        return None
    return None


def confirm_version(port: str, target: str) -> int:
    """Ask the machine what it is running and hold the flash to it.

    Non-zero when the board comes back reporting something other than the image
    just sent, which is what a stale binary looks like from the outside.
    """
    want = expected_version(target)
    if not want:
        return 0

    # A fresh console rather than the one the transfer ran on: that one is still
    # at the session's baud, and reopening the port is also what gives a main
    # board that has just been talked at 500000 a clean 115200 to answer on.
    time.sleep(8)          # the board reboots into what was just written
    ser = open_console(port)

    # A display answers through the main board, so its link has to come back
    # before it can be asked at all — and the answer arrives whenever it
    # arrives. So this asks repeatedly rather than once and waits.
    deadline = time.time() + 75
    asked = 0.0
    seen, buf = None, b""
    label = {"faucet": "faucet", "enclosure": "enclosure"}.get(target)
    while time.time() < deadline and seen is None:
        if time.time() - asked > 5:
            asked = time.time()
            ser.reset_input_buffer()
            buf = b""
            ser.write(b"versions\n")
            ser.flush()
        buf += ser.read(max(1, ser.in_waiting))
        text = buf.decode(errors="replace")
        # Only ever a completed line. A console answer arrives in pieces, and
        # half of one parses perfectly well into the wrong answer — which is a
        # worse failure here than none, because this is the check that is
        # supposed to be trusted.
        if target == "self":
            for line in text.split("\n")[:-1]:
                if line.startswith("main board") and len(line.split()) >= 3:
                    seen = line.split(None, 2)[2].strip()
        elif label:
            marker = f"VERSION {label} = "
            if marker in text:
                rest = text.split(marker, 1)[1]
                if "\n" in rest:
                    candidate = rest.split("\n", 1)[0].strip()
                    if candidate and "unanswered" not in candidate:
                        seen = candidate
        time.sleep(0.1)

    ser.close()
    if seen is None:
        print(f"could not confirm what {target} is running — it did not answer")
        return 1
    if seen != want:
        print(f"WRONG IMAGE: {target} reports {seen!r}, sent {want!r}")
        print("the build did not run and a stale firmware.bin was flashed")
        return 1
    print(f"confirmed: {target} is running {seen}")
    return 0


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

    idle_since = time.time()
    while True:
        chunk = ser.read(max(1, ser.in_waiting))
        if chunk:
            buf += chunk
            idle_since = time.time()
        elif time.time() - idle_since > 30:
            print("\ntimed out — nothing from the main board for 30s")
            ser.close()
            return 1

        while b"\n" in buf:
            line, buf = buf.split(b"\n", 1)
            line = line.decode(errors="replace").strip()
            if not line:
                continue
            if line.startswith("OTA:BAUD"):
                # The board has already switched; follow it. It drops back when
                # the session ends, and a reset restores the idle rate anyway.
                rate = int(line.split()[1])
                time.sleep(0.05)
                ser.baudrate = rate
                # Bytes straddling the switch are framed at the old rate and
                # arrive as noise. Drop them rather than parse them.
                time.sleep(0.05)
                ser.reset_input_buffer()
                buf = b""
                print(f"console at {rate:,} baud")
                continue

            if line.startswith("OTA:STALL"):
                print(f"\n  {line}")
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
                return confirm_version(port, target)

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

    if a.image:
        img = a.image
    elif a.target == "art":
        img = ART_IMAGE
    else:
        img = os.path.join(REPO, ".pio", "build", TARGETS[a.target][0], "firmware.bin")
    if not os.path.exists(img):
        how = ("~/.platformio/penv/bin/python tools/make_art.py enclosure"
               if a.target == "art" else f"pio run -e {TARGETS[a.target][0]}")
        sys.exit(f"no image at {img} — build it first: {how}")
    sys.exit(run(a.target, img, a.verbose))
