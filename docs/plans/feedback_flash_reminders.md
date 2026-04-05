---
name: Remind user when firmware flashing is needed
description: After making firmware changes, always tell the user which boards need flashing and in what order
type: feedback
---

When firmware changes are made to any target (ESP32, S3, RP2040), always explicitly tell the user which boards need to be flashed before testing. Don't assume they'll figure it out — say something like "This change requires flashing the S3. Can you connect it in bootloader mode?"

**Why:** The user had to figure out on their own that the S3 needed flashing after a `src_config/main.cpp` change. That's friction that should be avoided.

**How to apply:** After committing firmware changes, list which boards need flashing. Reference the flash order from memory if multiple boards changed (peripherals first, then ESP32). Prompt the user to connect the right board.
