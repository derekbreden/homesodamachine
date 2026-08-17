#!/usr/bin/env python3
"""Manage images on the RP2040 display and ESP32-S3 config display via ESP32 USB serial.

The ESP32 is the authoritative image store. Images are stored on ESP32's
LittleFS (both resolutions + compressed PNG), then pushed to display devices
via TinyProto HDLC over inter-MCU UART.

Usage:
    python3 upload_image.py --sync-factory [--port PORT]
    python3 upload_image.py --sync-user [--port PORT]
    python3 upload_image.py --push [--port PORT]
    python3 upload_image.py --list-store [--port PORT]
    python3 upload_image.py --build-data
    python3 upload_image.py <image.png> [--slot N] [--port PORT]
    python3 upload_image.py --list [--target TARGET] [--port PORT]
    python3 upload_image.py --delete N [--target TARGET] [--port PORT]
    python3 upload_image.py --swap A B [--target TARGET] [--port PORT]
    python3 upload_image.py --label N NAME [--target TARGET] [--port PORT]
    python3 upload_image.py --query [--target TARGET] [--port PORT]

Target devices (for device-level queries):
    rp2040  - RP2040 round display (128x115, external)
    s3      - ESP32-S3 config display (240x240, rotary)
    both    - Both devices (default)

Dependencies:
    pip install pyserial Pillow
"""

import argparse
import binascii
import glob
import json
import struct
import sys
import time
from pathlib import Path

import serial

# ── Device dimensions ──
RP2040_W = 128
RP2040_H = 115
RP2040_IMAGE_BYTES = RP2040_W * RP2040_H * 2  # 29440

S3_W = 240
S3_H = 240
S3_IMAGE_BYTES = S3_W * S3_H * 2  # 115200

CHUNK_SIZE = 128
BAUD_USB = 115200

# USB binary protocol constants (ESP32 store mode — unchanged)
STX = 0x02
CMD_UPLOAD_START = 0x01
CMD_CHUNK_DATA = 0x02
CMD_UPLOAD_DONE = 0x03

RESP_READY = 0x10
RESP_CHUNK_OK = 0x11
RESP_UPLOAD_OK = 0x12


def crc16(data: bytes) -> int:
    crc = 0xFFFF
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021 if crc & 0x8000 else crc << 1) & 0xFFFF
    return crc


def crc32(data: bytes) -> int:
    return binascii.crc32(data) & 0xFFFFFFFF


def png_to_rgb565(path: str, width: int, height: int) -> bytes:
    from PIL import Image

    img = Image.open(path).convert("RGB")
    img = img.resize((width, height), Image.LANCZOS)
    pixels = list(img.getdata())
    result = bytearray()
    for r, g, b in pixels:
        rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
        result += struct.pack("<H", rgb565)
    return bytes(result)


def find_port():
    for pattern in [
        "/dev/cu.usbserial-*",
        "/dev/cu.SLAB_*",
        "/dev/ttyUSB*",
        "/dev/ttyACM*",
    ]:
        matches = sorted(glob.glob(pattern))
        if matches:
            return matches[0]
    return None


def send_text_cmd(ser, cmd: str) -> str:
    ser.reset_input_buffer()
    ser.write((cmd + "\n").encode())
    time.sleep(0.3)
    resp = ser.read(ser.in_waiting or 512).decode("utf-8", errors="replace").strip()
    return resp


def read_text_lines(ser, end_marker="END", timeout=3.0):
    """Read text lines from serial until end_marker or timeout."""
    lines = []
    start = time.time()
    buf = ""
    while time.time() - start < timeout:
        if ser.in_waiting:
            buf += ser.read(ser.in_waiting).decode("utf-8", errors="replace")
            while "\n" in buf:
                line, buf = buf.split("\n", 1)
                line = line.strip()
                if line == end_marker:
                    return lines
                if line:
                    lines.append(line)
                start = time.time()  # reset timeout on activity
        time.sleep(0.01)
    return lines


def read_binary_response(ser, timeout: float = 5.0) -> bytes:
    """Read a 6-byte binary response (STX STX code extra crc16)."""
    start = time.time()
    buf = bytearray()
    while time.time() - start < timeout:
        if ser.in_waiting:
            buf += ser.read(ser.in_waiting)
            idx = buf.find(bytes([STX, STX]))
            if idx >= 0 and len(buf) >= idx + 6:
                return bytes(buf[idx : idx + 6])
        time.sleep(0.01)
    return b""


def make_upload_start(slot: int, size: int) -> bytes:
    msg = struct.pack("<BBBBI", STX, STX, CMD_UPLOAD_START, slot, size)
    crc = crc16(msg)
    return msg + struct.pack("<H", crc)


def make_chunk(seq: int, data: bytes) -> bytes:
    msg = struct.pack("<BBBBH", STX, STX, CMD_CHUNK_DATA, seq, len(data)) + data
    crc = crc16(msg)
    return msg + struct.pack("<H", crc)


def make_upload_done(slot: int, image_crc32: int) -> bytes:
    msg = bytes([STX, STX, CMD_UPLOAD_DONE, slot]) + struct.pack("<I", image_crc32)
    crc = crc16(msg)
    return msg + struct.pack("<H", crc)


def connect(port_name):
    port = port_name or find_port()
    if not port:
        print("ERROR: No serial port found. Use --port to specify.")
        sys.exit(1)
    print(f"Connecting to {port}...")
    ser = serial.Serial(port, BAUD_USB, timeout=2)
    time.sleep(2)
    ser.read(ser.in_waiting or 4096)  # drain boot messages
    return ser


# ════════════════════════════════════════════════════════════
#  Device-agnostic wrappers — dispatch by target prefix
# ════════════════════════════════════════════════════════════

def _cmd_prefix(target):
    """Return command prefix for a given target."""
    return "" if target == "rp2040" else "S3_"


def _device_label(target):
    return "RP2040" if target == "rp2040" else "S3"


def query_count(ser, target="rp2040") -> int:
    pfx = _cmd_prefix(target)
    cmd = f"QUERY_{pfx}IMAGES"
    resp = send_text_cmd(ser, cmd)
    key = f"NUM_{pfx}IMAGES="
    if key in resp:
        return int(resp.split(key)[1].split()[0])
    return -1


def list_images(ser, target="rp2040"):
    """Send LIST_IMAGES / LIST_S3_IMAGES and display all slots with labels."""
    pfx = _cmd_prefix(target)
    label = _device_label(target)
    cmd = f"LIST_{pfx}IMAGES"

    ser.reset_input_buffer()
    ser.write((cmd + "\n").encode())
    time.sleep(0.3)

    lines = read_text_lines(ser, end_marker="END", timeout=3.0)
    if not lines:
        print(f"No images found on {label} (or device not responding)")
        return []

    print(f"{label} images ({len(lines)} slots):")
    result = []
    for line in lines:
        # Format: IMG:slot:label
        if line.startswith("IMG:"):
            parts = line.split(":", 2)
            if len(parts) == 3:
                slot = int(parts[1])
                lbl = parts[2] if parts[2] else "(unlabeled)"
                print(f"  Slot {slot}: {lbl}")
                result.append((slot, parts[2]))
            else:
                print(f"  {line}")
    return result


def store_on_esp32(ser, slot: int, image_data: bytes, is_s3: bool):
    """Store an image on ESP32's LittleFS via store mode binary protocol."""
    store_cmd = f"STORE_S3_IMG:{slot}" if is_s3 else f"STORE_RP_IMG:{slot}"
    res_label = "S3" if is_s3 else "RP2040"

    resp = send_text_cmd(ser, store_cmd)
    if "OK:STORE_MODE" not in resp:
        print(f"ERROR: ESP32 rejected store command: {resp}")
        sys.exit(1)
    time.sleep(0.2)

    expected_size = len(image_data)

    # Send UPLOAD_START
    ser.write(make_upload_start(slot, expected_size))
    resp = read_binary_response(ser, timeout=3.0)
    if len(resp) < 6 or resp[2] != RESP_READY:
        code = f"0x{resp[2]:02X}" if len(resp) >= 3 else "timeout"
        print(f"ERROR: ESP32 store not ready ({res_label}): {code}")
        sys.exit(1)

    # Send chunks
    seq = 0
    offset = 0
    total_chunks = (expected_size + CHUNK_SIZE - 1) // CHUNK_SIZE
    while offset < expected_size:
        chunk = image_data[offset : offset + CHUNK_SIZE]
        pkt = make_chunk(seq & 0xFF, chunk)

        for attempt in range(5):
            ser.write(pkt)
            resp = read_binary_response(ser, timeout=2.0)
            if len(resp) >= 6 and resp[2] == RESP_CHUNK_OK:
                break
            elif len(resp) >= 6:
                print(
                    f"\n  Error 0x{resp[2]:02X} on chunk {seq}, "
                    f"retrying ({attempt + 1}/5)"
                )
            else:
                print(f"\n  Timeout on chunk {seq}, retrying ({attempt + 1}/5)")
        else:
            print(f"\nFATAL: Failed to store chunk {seq} after 5 attempts")
            sys.exit(1)

        offset += CHUNK_SIZE
        seq += 1
        pct = min(100, int(seq * 100 / total_chunks))
        print(f"\r  [{pct:3d}%] Chunk {seq}/{total_chunks}", end="", flush=True)

    print()

    # Send UPLOAD_DONE with CRC-32
    img_crc = crc32(image_data)
    ser.write(make_upload_done(slot, img_crc))
    resp = read_binary_response(ser, timeout=5.0)
    if len(resp) >= 6 and resp[2] == RESP_UPLOAD_OK:
        new_count = resp[3]
        print(f"  Stored on ESP32 ({res_label} slot {slot}), store: {new_count} images")
    else:
        code = f"0x{resp[2]:02X}" if len(resp) >= 3 else "timeout"
        print(f"ERROR: Store verification failed ({code})")
        sys.exit(1)


def store_s3_png(ser, slot: int, png_path: str):
    """Store a compressed PNG on ESP32's LittleFS for BLE serving."""
    from PIL import Image
    import subprocess, tempfile

    img = Image.open(png_path).convert("RGBA")
    img = img.resize((S3_W, S3_H), Image.LANCZOS)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        img.save(tmp.name)
        try:
            subprocess.run(
                ["pngquant", "--quality=40-70", "--speed=1", "--force",
                 "--output", tmp.name, tmp.name],
                check=True, capture_output=True
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass  # use unoptimized PNG if pngquant unavailable
        png_data = Path(tmp.name).read_bytes()
        Path(tmp.name).unlink()

    print(f"    PNG: {len(png_data)} bytes")

    resp = send_text_cmd(ser, f"STORE_S3_PNG:{slot}")
    if "OK:STORE_MODE" not in resp:
        print(f"ERROR: ESP32 rejected PNG store command: {resp}")
        sys.exit(1)
    time.sleep(0.2)

    # Send UPLOAD_START
    ser.write(make_upload_start(slot, len(png_data)))
    resp = read_binary_response(ser, timeout=3.0)
    if len(resp) < 6 or resp[2] != RESP_READY:
        code = f"0x{resp[2]:02X}" if len(resp) >= 3 else "timeout"
        print(f"ERROR: ESP32 PNG store not ready: {code}")
        sys.exit(1)

    # Send chunks
    seq = 0
    offset = 0
    while offset < len(png_data):
        chunk = png_data[offset : offset + CHUNK_SIZE]
        pkt = make_chunk(seq & 0xFF, chunk)
        for attempt in range(5):
            ser.write(pkt)
            resp = read_binary_response(ser, timeout=2.0)
            if len(resp) >= 6 and resp[2] == RESP_CHUNK_OK:
                break
        else:
            print(f"\nFATAL: Failed to store PNG chunk {seq}")
            sys.exit(1)
        offset += CHUNK_SIZE
        seq += 1

    # Send UPLOAD_DONE with CRC-32
    img_crc = crc32(png_data)
    ser.write(make_upload_done(slot, img_crc))
    resp = read_binary_response(ser, timeout=5.0)
    if len(resp) >= 6 and resp[2] == RESP_UPLOAD_OK:
        print(f"    Stored PNG on ESP32 (slot {slot})")
    else:
        code = f"0x{resp[2]:02X}" if len(resp) >= 3 else "timeout"
        print(f"ERROR: PNG store verification failed ({code})")
        sys.exit(1)


def set_label(ser, slot: int, label_text: str, target="rp2040"):
    """Set a label for a slot via text command through ESP32."""
    pfx = _cmd_prefix(target)
    cmd = f"SET_{pfx}LABEL:{slot}={label_text}"
    resp = send_text_cmd(ser, cmd)
    ok_key = f"OK:{pfx}LABEL=" if pfx else "OK:LABEL="
    if ok_key in resp:
        print(f"  [{_device_label(target)}] Label set: slot {slot} = {label_text}")
    else:
        print(f"  [{_device_label(target)}] Warning: could not set label ({resp})")


def delete_image(ser, slot: int, target="rp2040"):
    pfx = _cmd_prefix(target)
    cmd = f"DELETE_{pfx}IMG:{slot}"
    resp = send_text_cmd(ser, cmd)
    ok_key = f"OK:{pfx}DELETED=" if pfx else "OK:DELETED="
    if ok_key in resp:
        print(f"  [{_device_label(target)}] {resp}")
    else:
        print(f"ERROR: [{_device_label(target)}] {resp}")
        sys.exit(1)


def swap_images(ser, slot_a: int, slot_b: int, target="rp2040"):
    pfx = _cmd_prefix(target)
    cmd = f"SWAP_{pfx}IMG:{slot_a},{slot_b}"
    resp = send_text_cmd(ser, cmd)
    ok_key = f"OK:{pfx}SWAPPED=" if pfx else "OK:SWAPPED="
    if ok_key in resp:
        print(f"  [{_device_label(target)}] {resp}")
    else:
        print(f"ERROR: [{_device_label(target)}] {resp}")
        sys.exit(1)


def push_single_image(ser, slot: int, target="both"):
    """Push a single stored image from ESP32 to device(s) via PUSH_IMG command."""
    cmd = f"PUSH_IMG:{slot}:{target}"
    ser.reset_input_buffer()
    ser.write((cmd + "\n").encode())
    result = wait_for_push(ser, timeout=120.0)
    if not result:
        print("ERROR: Push timed out")
        sys.exit(1)


def wait_for_push(ser, timeout=600.0):
    """Read serial output during push/sync, print progress, return final status line."""
    start = time.time()
    buf = ""
    while time.time() - start < timeout:
        if ser.in_waiting:
            buf += ser.read(ser.in_waiting).decode("utf-8", errors="replace")
            while "\n" in buf:
                line, buf = buf.split("\n", 1)
                line = line.strip()
                if line:
                    print(f"  {line}")
                if (line.startswith("OK:PUSH_DONE") or
                    line.startswith("OK:SYNC_DONE") or
                    line.startswith("OK:PUSH_IMG=")):
                    return line
                start = time.time()  # reset timeout on activity
        time.sleep(0.1)
    return ""


# ════════════════════════════════════════════════════════════
#  Sync from manifest
# ════════════════════════════════════════════════════════════

def build_data(manifest):
    """Generate data/ directory for PlatformIO uploadfs (brand-new ESP32 setup).

    Creates binary image files + metadata that can be flashed directly to
    the ESP32's LittleFS partition via: pio run -e prototype -t uploadfs
    """
    import shutil

    slots = manifest["slots"]
    images_dir = Path(__file__).resolve().parent.parent / "images"
    data_dir = Path(__file__).resolve().parent.parent / "data"

    # Clean and recreate data directory
    if data_dir.exists():
        shutil.rmtree(data_dir)
    data_dir.mkdir()

    print(f"Building LittleFS data for {len(slots)} images...")

    for entry in slots:
        slot = entry["slot"]
        png_file = images_dir / entry["file"]
        if not png_file.exists():
            print(f"WARNING: {png_file} not found, skipping slot {slot}")
            continue

        print(f"  Slot {slot}: {entry['file']}")

        # RP2040 resolution (128x115)
        rp_data = png_to_rgb565(str(png_file), RP2040_W, RP2040_H)
        rp_path = data_dir / f"rp_img{slot:02d}.bin"
        rp_path.write_bytes(rp_data)
        print(f"    {rp_path.name}: {len(rp_data)} bytes")

        # S3 resolution (240x240)
        s3_data = png_to_rgb565(str(png_file), S3_W, S3_H)
        s3_path = data_dir / f"s3_img{slot:02d}.bin"
        s3_path.write_bytes(s3_data)
        print(f"    {s3_path.name}: {len(s3_data)} bytes")

        # S3 PNG for iOS BLE (240x240, pngquant-compressed)
        from PIL import Image
        import subprocess
        img = Image.open(str(png_file)).convert("RGBA")
        img = img.resize((S3_W, S3_H), Image.LANCZOS)
        png_out = data_dir / f"s3_png{slot:02d}.png"
        img.save(str(png_out))
        try:
            subprocess.run(
                ["pngquant", "--quality=40-70", "--speed=1", "--force",
                 "--output", str(png_out), str(png_out)],
                check=True, capture_output=True
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            # pngquant not available or failed, use unoptimized PNG
            pass
        print(f"    {png_out.name}: {png_out.stat().st_size} bytes")

    # Write meta.txt (image count)
    meta_path = data_dir / "meta.txt"
    meta_path.write_text(f"{len(slots)}\n")
    print(f"  meta.txt: {len(slots)} images")

    # Write labels.txt
    labels_path = data_dir / "labels.txt"
    labels = [entry.get("label", "") for entry in slots]
    labels_path.write_text("\n".join(labels) + "\n")
    print(f"  labels.txt: {len(labels)} labels")

    # Do NOT write fw_version.txt — its absence triggers first-boot detection

    total_bytes = sum(f.stat().st_size for f in data_dir.iterdir())
    print(f"\ndata/ ready: {len(list(data_dir.iterdir()))} files, {total_bytes:,} bytes")
    print(f"Flash with: ~/.platformio/penv/bin/pio run -e prototype -t uploadfs")


def sync_via_store(ser, manifest):
    """Store all images on ESP32, set labels, then push to both devices.

    This is the primary sync flow. The ESP32 becomes the authoritative store.
    """
    slots = manifest["slots"]
    images_dir = Path(__file__).resolve().parent.parent / "images"

    # Phase 1: Store both resolutions on ESP32
    print(f"\n{'='*60}")
    print(f"  Phase 1: Storing {len(slots)} images on ESP32")
    print(f"{'='*60}")

    for entry in slots:
        slot = entry["slot"]
        png_file = images_dir / entry["file"]
        if not png_file.exists():
            print(f"WARNING: {png_file} not found, skipping slot {slot}")
            continue

        print(f"\nSlot {slot}: {entry['file']}")

        # Store RP2040 version (128x115)
        print(f"  Converting to {RP2040_W}x{RP2040_H} RGB565 (RP2040)...")
        rp_data = png_to_rgb565(str(png_file), RP2040_W, RP2040_H)
        store_on_esp32(ser, slot, rp_data, is_s3=False)

        # Store S3 version (240x240)
        print(f"  Converting to {S3_W}x{S3_H} RGB565 (S3)...")
        s3_data = png_to_rgb565(str(png_file), S3_W, S3_H)
        store_on_esp32(ser, slot, s3_data, is_s3=True)

        # Store S3 PNG for iOS BLE
        print(f"  Creating compressed PNG for BLE...")
        store_s3_png(ser, slot, str(png_file))

    # Phase 2: Set labels
    print(f"\n{'='*60}")
    print(f"  Phase 2: Setting labels on ESP32")
    print(f"{'='*60}")
    for entry in slots:
        lbl = entry.get("label", "")
        if lbl:
            resp = send_text_cmd(ser, f"STORE_LABEL:{entry['slot']}={lbl}")
            if "OK:" in resp:
                print(f"  Slot {entry['slot']}: {lbl}")
            else:
                print(f"  Warning: slot {entry['slot']}: {resp}")

    # Phase 3: Push to both devices
    print(f"\n{'='*60}")
    print(f"  Phase 3: Pushing to both devices")
    print(f"{'='*60}")
    ser.reset_input_buffer()
    ser.write(b"PUSH_TO_DEVICES\n")
    result = wait_for_push(ser, timeout=600.0)
    if not result:
        print("ERROR: Push timed out")
        return False

    print(f"\nSync complete!")
    return True


# ════════════════════════════════════════════════════════════
#  CLI
# ════════════════════════════════════════════════════════════

def resolve_targets(target_str):
    """Return list of target strings to operate on."""
    if target_str == "both":
        return ["rp2040", "s3"]
    return [target_str]


def main():
    parser = argparse.ArgumentParser(
        description="Manage images on RP2040 and S3 displays via ESP32 serial"
    )
    parser.add_argument("image", nargs="?", default=None, help="PNG image to upload")
    parser.add_argument("--slot", type=int, default=None, help="Image slot (0-99)")
    parser.add_argument("--port", default=None, help="Serial port")
    parser.add_argument("--target", default="both",
                        choices=["rp2040", "s3", "both"],
                        help="Target device (default: both)")
    parser.add_argument("--list", action="store_true",
                        help="List all images with labels")
    parser.add_argument("--delete", type=int, default=None, metavar="N",
                        help="Delete image at slot N (shifts remaining down)")
    parser.add_argument("--swap", type=int, nargs=2, default=None, metavar=("A", "B"),
                        help="Swap images at slots A and B")
    parser.add_argument("--label", nargs=2, default=None, metavar=("N", "NAME"),
                        help="Set label for slot N")
    parser.add_argument("--query", action="store_true",
                        help="Query current image count")
    parser.add_argument("--sync-factory", action="store_true",
                        help="Sync factory images (factory_manifest.json) to ESP32 + push")
    parser.add_argument("--sync-user", action="store_true",
                        help="Sync all images (user_manifest.json) to ESP32 + push (dev/test)")
    parser.add_argument("--push", action="store_true",
                        help="Push stored images from ESP32 to both devices")
    parser.add_argument("--list-store", action="store_true",
                        help="List images stored on ESP32")
    parser.add_argument("--build-data", action="store_true",
                        help="Generate data/ directory for PlatformIO uploadfs")
    args = parser.parse_args()

    # Validate arguments
    actions = sum([args.image is not None, args.delete is not None,
                   args.swap is not None, args.query, args.list,
                   args.label is not None, args.sync_factory, args.sync_user,
                   args.push, args.list_store, args.build_data])
    if actions == 0:
        parser.print_help()
        sys.exit(1)
    if actions > 1:
        print("ERROR: specify only one action")
        sys.exit(1)

    # --build-data doesn't need serial connection
    if args.build_data:
        manifest_path = Path(__file__).resolve().parent.parent / "images" / "factory_manifest.json"
        if not manifest_path.exists():
            print(f"ERROR: {manifest_path} not found")
            sys.exit(1)
        with open(manifest_path) as f:
            manifest = json.load(f)
        build_data(manifest)
        return

    ser = connect(args.port)
    targets = resolve_targets(args.target)

    if args.sync_factory or args.sync_user:
        filename = "factory_manifest.json" if args.sync_factory else "user_manifest.json"
        manifest_path = Path(__file__).resolve().parent.parent / "images" / filename
        if not manifest_path.exists():
            print(f"ERROR: {manifest_path} not found")
            sys.exit(1)
        with open(manifest_path) as f:
            manifest = json.load(f)
        label = "factory" if args.sync_factory else "user"
        print(f"Syncing {label} manifest: {len(manifest['slots'])} images")
        sync_via_store(ser, manifest)
        ser.close()
        return

    if args.push:
        ser.reset_input_buffer()
        ser.write(b"PUSH_TO_DEVICES\n")
        result = wait_for_push(ser, timeout=600.0)
        if not result:
            print("ERROR: Push timed out")
        ser.close()
        return

    if args.list_store:
        ser.reset_input_buffer()
        ser.write(b"LIST_STORE\n")
        time.sleep(0.5)
        lines = read_text_lines(ser, end_marker="END", timeout=3.0)
        if not lines:
            print("ESP32 store is empty")
        else:
            print("ESP32 image store:")
            for line in lines:
                print(f"  {line}")
        ser.close()
        return

    if args.list:
        for target in targets:
            list_images(ser, target)
        ser.close()
        return

    if args.query:
        for target in targets:
            count = query_count(ser, target)
            label = _device_label(target)
            if count >= 0:
                print(f"{label} has {count} images (slots 0-{count - 1})")
            else:
                print(f"ERROR: could not query {label} image count")
        ser.close()
        return

    if args.label is not None:
        slot = int(args.label[0])
        name = args.label[1]
        for target in targets:
            set_label(ser, slot, name, target)
        ser.close()
        return

    if args.delete is not None:
        for target in targets:
            delete_image(ser, args.delete, target)
        ser.close()
        return

    if args.swap is not None:
        for target in targets:
            swap_images(ser, args.swap[0], args.swap[1], target)
        ser.close()
        return

    # Single-image upload: store on ESP32 (both resolutions + PNG) then push to devices
    if args.image:
        if args.slot is not None:
            slot = args.slot
        else:
            # Query ESP32 store count to find next available slot
            resp = send_text_cmd(ser, "LIST_STORE")
            # Parse STORE_COUNT:N from response
            count = 0
            for line in resp.split("\n"):
                if line.startswith("STORE_COUNT:"):
                    count = int(line.split(":")[1])
                    break
            slot = count
            print(f"  ESP32 store has {count} images, uploading to slot {slot}")

        print(f"\nStoring {args.image} on ESP32 (slot {slot})...")

        # Store RP2040 version (128x115)
        print(f"  Converting to {RP2040_W}x{RP2040_H} RGB565 (RP2040)...")
        rp_data = png_to_rgb565(args.image, RP2040_W, RP2040_H)
        store_on_esp32(ser, slot, rp_data, is_s3=False)

        # Store S3 version (240x240)
        print(f"  Converting to {S3_W}x{S3_H} RGB565 (S3)...")
        s3_data = png_to_rgb565(args.image, S3_W, S3_H)
        store_on_esp32(ser, slot, s3_data, is_s3=True)

        # Store S3 PNG for iOS BLE
        print(f"  Creating compressed PNG for BLE...")
        store_s3_png(ser, slot, args.image)

        # Set label from filename
        file_label = Path(args.image).stem
        resp = send_text_cmd(ser, f"STORE_LABEL:{slot}={file_label}")
        if "OK:" in resp:
            print(f"  Label: {file_label}")

        # Push to both devices
        print(f"\n  Pushing slot {slot} to devices...")
        push_single_image(ser, slot, "both")

        ser.close()
        return

    parser.print_help()
    ser.close()


if __name__ == "__main__":
    main()
