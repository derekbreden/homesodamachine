---
name: Always flash after building firmware
description: After building firmware, always flash it using tools/flash.sh — never ask the user to do it themselves
type: feedback
---

ALWAYS use `./tools/flash.sh <env>` for flashing. Never use `pio run -t upload`, `esptool`, or any other manual flash method.

**Why:** `flash.sh` handles serial logger pausing, port selection, and cleanup. Manual approaches bypass this and cause connection failures. The user had to correct this — don't repeat the mistake.

**How to apply:** Use `./tools/flash.sh esp32dev`, `./tools/flash.sh esp32s3_config`, or `./tools/flash.sh rp2040_display`. For build-only (no flash): `./tools/flash.sh <env> build`. Never fall back to raw pio/esptool commands even if the first attempt fails.
