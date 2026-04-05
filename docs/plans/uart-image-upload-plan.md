---
name: Over-UART image upload
description: DONE — Chunked binary image upload from ESP32 to RP2040 and S3 over UART, replacing compiled PROGMEM arrays with LittleFS
type: project
---

# Over-UART Image Upload — DONE

All phases complete, including Phase 5 (S3 extension).

## What it does

Images uploaded via Python script → ESP32 USB serial → ESP32 UART → RP2040/S3 → LittleFS. Replaced compiled PROGMEM image arrays, eliminating the need to USB-flash peripheral boards for image changes.

## Key decisions

- **LittleFS on all devices** — images stored as raw RGB565 binary files (`/imgNN.bin`), metadata in `/meta.txt`
- **First-boot seeding** — PROGMEM arrays written to LittleFS on first boot, then dead weight but acceptable
- **115200 baud** — TinyProto HDLC handles fragmentation, ACKs, and retransmission internally
- **Push model** — images stored on ESP32 LittleFS, pushed to devices via `tiny_fd_send()` in 4KB chunks
- **CRC-32 verification** — whole-image CRC check on receiver, CRC-based boot sync skips matching slots
- **One new wire** — RP2040 GP27 (TX) → ESP32 GPIO 35 (RX) for bidirectional UART
