---
name: ESP32 flash does NOT wipe LittleFS data
description: Flashing ESP32 does not wipe LittleFS — stats, config, images all survive across flashes
type: feedback
---

Flashing the ESP32 does NOT wipe stats, user config, or images. LittleFS persists across flashes.

**Why:** During earlier debugging, a reflash appeared to show empty data, leading to a wrong conclusion that data was wiped. The actual cause was a time sync issue (since resolved — time sync was removed entirely in commit b19183f).

**How to apply:**
- Don't panic about data loss from flashing — LittleFS survives.
- If data appears missing after a flash, investigate the specific symptom rather than assuming a wipe.
