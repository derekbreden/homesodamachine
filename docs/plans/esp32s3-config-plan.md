---
name: ESP32-S3 config display implementation
description: DONE — Meshnology ESP32-S3 round rotary display for config editing (LVGL, rotary encoder, bidirectional UART)
type: project
---

# ESP32-S3 Config Display — DONE

All phases complete. Meshnology ESP32-S3 board (Amazon B0G5Q4LXVJ, $47.76) — 240x240 1.28" IPS with GC9A01A controller and rotary encoder bezel.

## Architecture

ESP32-S3 is a UI frontend. ESP32 is source of truth. S3 sends text commands (`GET_CONFIG`, `SET:`, `SAVE`) over UART; ESP32 responds with `CONFIG:`, `OK:`, `ERR:`.

## What was built

1. **ESP32 config system** — runtime variables backed by persistent storage, `processConfigCommand()` parser
2. **Bidirectional UART** — ESP32-S3 ↔ ESP32 via TinyProto HDLC at 115200 baud
3. **240x240 RGB565 images** — converted from PNG, stored in LittleFS
4. **LVGL UI** — dot-page carousel (2 image pages, 2 ratio pages, settings page), rotary encoder navigation
5. **Boot sync** — S3 polls `GET_CONFIG` until ESP32 responds

## Current state

- Config storage: LittleFS (see roadmap item 1c)
- UART: TinyProto HDLC at 115200 baud via ProtoLink wrapper
- S3 serves as BLE bridge to iOS app (see `ble-plan.md`)
