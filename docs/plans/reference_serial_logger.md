---
name: Serial logger and flash wrapper tools
description: tools/serial_logger.py auto-logs ESP32+S3 serial output; tools/flash.sh wraps pio upload with logger pause/resume
type: reference
---

## Serial Logger (`tools/serial_logger.py`)

Auto-reconnecting serial logger that monitors ESP32 and S3 USB serial, writing timestamped output to `logs/esp32.log` and `logs/s3.log`.

**Usage:**
- `python3 tools/serial_logger.py` — log to files + stdout
- `python3 tools/serial_logger.py --quiet` — log to files only
- Ctrl+C to stop

**Device detection:** Uses pyserial VID/PID matching:
- ESP32: Silicon Labs CP210x (VID 0x10C4, PID 0xEA60) → `/dev/cu.usbserial-*`
- S3: Espressif USB JTAG (VID 0x303A, PID 0x1001) → `/dev/cu.usbmodem*`

**Pause/resume:** Watches for `/tmp/serial_logger_pause`. When present, releases all ports. When removed, reconnects. Used by `flash.sh`.

**Note:** Opening the S3 serial port causes a USB CDC reset (board reboots). This is ESP32-S3 hardware behavior with `ARDUINO_USB_CDC_ON_BOOT=1` and cannot be prevented.

## Flash Wrapper (`tools/flash.sh`)

Wraps `pio run -t upload` with serial logger pause/resume.

**Usage:**
- `./tools/flash.sh esp32dev` — build + flash ESP32
- `./tools/flash.sh esp32s3_config` — build + flash S3
- `./tools/flash.sh rp2040_display` — build + flash RP2040
- `./tools/flash.sh <env> build` — build only, no flash

**All agents should use `./tools/flash.sh` instead of raw `pio run -t upload`.**

## Log Files

- `logs/esp32.log` — ESP32 serial output (timestamped)
- `logs/s3.log` — S3 serial output (timestamped)
- Logs are gitignored (only `.gitkeep` is tracked)
- Logs persist across logger restarts (append mode)
- Reconnect events are marked with `── connected on <port> ──` separators
