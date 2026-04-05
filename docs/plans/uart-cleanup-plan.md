---
name: UART Architecture Cleanup Plan (superseded)
description: SUPERSEDED — original hand-rolled unified framing plan, replaced by SerialTransfer, then by TinyProto HDLC. Kept for reference only.
type: project
---

# UART Architecture Cleanup Plan

> **SUPERSEDED** — This plan proposed building a custom unified framing protocol from scratch. The codebase now uses TinyProto HDLC via ProtoLink wrapper. This file is kept for reference only.

## Context

After 7 hours of debugging BLE image downloads, the root cause of nearly every bug is the same: text and binary protocols are multiplexed on the same UART lines with ad-hoc detection (scan for STX STX, otherwise accumulate text until newline). This creates an entire category of bugs:

- Stray text during binary transfers corrupts protocol responses
- Boot noise (GPIO 15 floating) corrupts the S3 parser (requires 150 zero-byte flush hack)
- BLE command forwarding can inject text during binary uploads
- GET_CONFIG polling can collide with binary uploads
- `waitBinaryResponse` does blind 6-byte reads — one stray byte permanently misaligns it
- Every new feature requires another guard/suppression check

This plan replaces those guards with a unified framing protocol that wraps ALL UART traffic in self-describing binary frames. It also fixes the BLE callback cross-task safety issue and eliminates the imageBuf/bleSendBuf aliasing.

**This plan supersedes the "Pre-Phase 3 Cleanup" section in `ble-plan.md`** (those 3 items are subsets of this work). The ble-plan.md items remain as fallback if this plan is abandoned.

---

## 1. Unified Frame Format

All inter-MCU UART traffic uses one frame format:

```
STX STX <type> <len_lo> <len_hi> <payload[len]> <crc_lo> <crc_hi>
```

- **STX STX**: 0x02 0x02 sync sentinel (unchanged)
- **TYPE**: 1 byte command/response code
- **LEN**: 2 bytes little-endian payload length
- **PAYLOAD**: LEN bytes (format depends on TYPE)
- **CRC-16**: CCITT over bytes [TYPE, LEN_LO, LEN_HI, PAYLOAD...] (excludes STX STX)

Minimum frame: 7 bytes (zero-payload). Parser is self-describing — no command-type switch needed to determine frame length.

### Type Codes

**Commands:**

| Code | Name | Payload | Notes |
|------|------|---------|-------|
| 0x01 | CMD_UPLOAD_START | slot(1) + size(4) | Begin RGB565 upload |
| 0x02 | CMD_CHUNK_DATA | seq(1) + data(N) | Upload chunk, seq wraps at 256 |
| 0x03 | CMD_UPLOAD_DONE | slot(1) + crc32(4) | Finalize upload |
| 0x04 | CMD_QUERY_COUNT | (none) | Query image count |
| 0x05 | CMD_DELETE_IMAGE | slot(1) | Delete image |
| 0x06 | CMD_SWAP_IMAGES | slotA(1) + slotB(1) | Swap two slots |
| 0x07 | CMD_UPLOAD_PNG_START | slot(1) + size(4) | **New.** Replaces slot >= 100 hack |
| 0xFE | CMD_TEXT | ASCII text (N bytes) | **New.** Wraps text commands |

**Responses:**

| Code | Name | Payload | Notes |
|------|------|---------|-------|
| 0x10 | RESP_READY | (none) | Ready for chunks |
| 0x11 | RESP_CHUNK_OK | nextSeq(1) | Chunk accepted |
| 0x12 | RESP_UPLOAD_OK | numImages(1) | Upload complete |
| 0x13 | RESP_DELETE_OK | numImages(1) | Delete complete |
| 0x14 | RESP_COUNT | count(1) | Image count |
| 0x15 | RESP_SWAP_OK | numImages(1) | Swap complete |
| 0xE1-E8 | ERR_* | 0 or 1 byte | Error codes (unchanged) |

Text responses (CONFIG:, OK:, ERR:, IMG:, END) are wrapped in CMD_TEXT (0xFE) frames.

### Parser State Machine (shared across all 3 MCUs)

```
States: SCAN_STX1 → SCAN_STX2 → READ_TYPE → READ_LEN_LO → READ_LEN_HI → READ_PAYLOAD → READ_CRC_LO → READ_CRC_HI
```

- Byte-at-a-time processing, works with any UART read pattern
- Automatic re-sync on corruption: non-STX bytes in SCAN_STX1 are skipped
- One stray byte never permanently misaligns the reader
- No text mode, no newline detection

### Overhead

Responses grow from 6 to 7+ bytes (+0.26ms at 38400 baud). Chunk frames same size. Negligible.

---

## 2. Implementation Commits

### Commit 1: Create shared `lib/uart_protocol/uart_protocol.h`

Contains:
- All CMD_*, RESP_*, ERR_*, STX constants
- CRC-16/CCITT function
- `FrameParser` struct + byte-at-a-time state machine
- `buildFrame(type, payload, len, outBuf)` → returns total frame length
- `buildTextFrame(text, outBuf)` → convenience for CMD_TEXT
- `buildResponse(code, extra, outBuf)` / `buildResponseNoPayload(code, outBuf)`

Remove duplicate constants and CRC-16 from all 3 source files. **No behavioral change.**

---

### Commit 2: Fix BLE callback cross-task safety (S3 only)

**File: `src_config/main.cpp`**

**Problem:** BLE RX callback runs on NimBLE FreeRTOS task, directly calls `loadPngFromFS()` and `loadImageFromFS()` which do LittleFS I/O. Cross-task LittleFS access crashes the ESP32-S3.

**Fix:** BLE callback sets flags only. `loop()` does all LittleFS and Serial0 work.

```cpp
enum BleRequest : uint8_t { BLE_NONE, BLE_LIST, BLE_GETPNG, BLE_GETIMG, BLE_FORWARD_TEXT };
static volatile BleRequest bleRequest = BLE_NONE;
static volatile uint8_t bleRequestSlot = 0;
static char bleForwardBuf[128];
```

BLE callback → sets `bleRequest` + parameters.
`loop()` → checks `bleRequest`, does file I/O, sends BLE responses.

**No protocol change.** Safe to flash S3 alone.

---

### Commit 3: Eliminate imageBuf/bleSendBuf aliasing (S3 only)

**File: `src_config/main.cpp`**

**Problem:** `static uint8_t *bleSendBuf = (uint8_t *)imageBuf;` — BLE PNG streaming and display rendering share the same 115KB buffer.

**Fix:** Stream PNGs from file in 240-byte chunks.

```cpp
// Remove: static uint8_t *bleSendBuf = (uint8_t *)imageBuf;
static File bleFile;                    // open during streaming
static uint8_t bleSendChunkBuf[240];    // small chunk buffer
```

`bleImageSendChunks()` reads 240 bytes from `bleFile` each iteration, sends via BLE notify.

**CRITICAL CAVEAT (previous attempt crashed):** A prior streaming attempt opened the file in the BLE callback (NimBLE task) and read from `loop()` (main task). Cross-task LittleFS access caused crashes. **This works now because Commit 2 moved all file operations to `loop()`.** File open, read, and close all happen in the same FreeRTOS task. Commit 2 is a prerequisite.

Remove `bleImageSending` guard from `renderCircularThumb()`. **No protocol change.** Safe to flash S3 alone.

---

### Commits 4-7: Unified frame protocol (flash ALL 3 devices together)

These commits are one atomic change. All 3 MCUs + upload tool must be updated together. Frame format is not backward-compatible.

**Flash order:** S3 first → RP2040 → ESP32 last (ESP32 initiates communication).

#### Commit 4: Unified protocol on RP2040

**File: `src_display/main.cpp`**

- Replace `checkUART()` with `FrameParser`
- CMD_TEXT (0xFE) → `processTextCommand()` (MAP, LABEL, LIST)
- Binary commands → existing handlers, adjusted payload indexing (payload[0] is slot, not msg[3])
- Replace `sendBinaryResponse()` with `buildResponse()`
- Wrap outgoing text (IMG:, END) in CMD_TEXT frames
- Keep bare-text fallback during development

#### Commit 5: Unified protocol on S3

**File: `src_config/main.cpp`**

- Replace `checkUart()` / `tryParseBinaryMessage()` with `FrameParser`
- CMD_TEXT (0xFE) → `processTextLine()`
- CMD_UPLOAD_PNG_START (0x07) → new handler (replaces slot >= 100 in handleUploadStart)
- Replace `sendBinaryResponse()` with `buildResponse()`
- Wrap outgoing text (CONFIG:, OK:, ERR:, IMG:, END, GET_CONFIG, SET:, SAVE) in CMD_TEXT frames

#### Commit 6: Unified protocol on ESP32

**File: `src/main.cpp`**

- Replace `waitBinaryResponse()` with `waitFrameResponse()` using FrameParser:
  - Scans for STX STX, reads type+len+payload+CRC
  - If unexpected CMD_TEXT frame during binary wait: log and skip
  - Automatic re-sync on CRC failure
- Replace `sendDisplayCommand()` / `sendS3DisplayCommand()` with frame-aware versions
- Update `pushImageToDevice()`, `pushPngToS3()` to build new-format frames
- `pushPngToS3()`: send CMD_UPLOAD_PNG_START (0x07) instead of slot+100
- Replace all Serial1/Serial2 text sends with `buildTextFrame()`
- Replace `checkConfigStream(Serial1, ...)` with FrameParser for Serial1
- Keep `checkConfigStream(Serial, ...)` for USB (no change to USB serial protocol)
- Update `enterStoreMode()` parser to accept new frame format
- Remove `resetS3Parser()` — new parser handles boot noise naturally

#### Commit 7: Update upload_image.py

**File: `tools/upload_image.py`**

- Add `build_frame(type_code, payload)` helper
- Update `make_upload_start()`, `make_chunk()`, `make_upload_done()` to new format
- Update `read_binary_response()` to parse new format
- Bridge modes (--target) work unchanged — ESP32 passes bytes through

---

### Commit 8: Remove bare-text fallback

Remove newline-based text accumulation from S3 and RP2040 parsers. Everything must come through CMD_TEXT frames.

### Commit 9: Remove GET_CONFIG polling suppression

The `upload.state != UPLOAD_RECEIVING` guard in S3 boot sync is no longer needed.

---

## 3. What Does NOT Change

- **USB serial protocol** (ESP32 ↔ computer): stays text + binary as-is
- **BLE protocol** (S3 ↔ iOS app): stays text-based NUS as-is
- **iOS app**: no changes
- **RP2040 display rendering**: no changes
- **Pump/valve/flow control**: no changes

---

## 4. Files Modified

| File | Changes |
|------|---------|
| `lib/uart_protocol/uart_protocol.h` | **New.** Shared constants, CRC, parser, builders |
| `src/main.cpp` (ESP32) | Replace wait/send, frame-wrap text, FrameParser for Serial1, update enterStoreMode, remove resetS3Parser |
| `src_config/main.cpp` (S3) | BLE callback restructuring, PNG file streaming, FrameParser, CMD_UPLOAD_PNG_START |
| `src_display/main.cpp` (RP2040) | FrameParser, new response format, frame-wrap text |
| `tools/upload_image.py` | New frame builders, new response parser |

---

## 5. Risk Assessment

**High:** All-devices-at-once flash for Commits 4-7. Mitigate: flash S3 → RP2040 → ESP32.

**High:** FrameParser bugs break all 3 devices. Mitigate: test parser on desktop (compile uart_protocol.h with g++, feed byte sequences).

**Medium:** BLE file streaming handle lifecycle — disconnect mid-stream must close file.

**Medium:** `enterStoreMode` parser change must match upload_image.py changes exactly.

**Low:** Response size increase (6→7+ bytes, ~0.26ms). Negligible.

---

## 6. Verification Checklist

**After Commits 1-3 (S3 only):**
- [ ] All 3 envs build
- [ ] iOS: LIST, GETPNG, SET/SAVE work
- [ ] S3 display renders during BLE download (no garbage)
- [ ] No crashes during BLE operations

**After Commits 4-7 (all 3 devices):**
- [ ] Boot sync: ESP32 queries counts from both devices
- [ ] Boot sync: image push on count mismatch
- [ ] Boot sync: PNG push to S3
- [ ] S3 rotary encoder config changes propagate to ESP32
- [ ] ESP32 CONFIG: push to S3 (BLE forwarding)
- [ ] RP2040 MAP/LABEL/LIST commands
- [ ] `upload_image.py --sync` works
- [ ] `upload_image.py --target rp2040` / `--target s3` bridge modes
- [ ] FACTORY_RESET works
- [ ] BLE GETPNG after protocol change
- [ ] GPIO 15 boot noise doesn't corrupt S3 parser
- [ ] Dispensing works during image upload

**Stress test:**
- [ ] BLE LIST request during pushAllToDevice — no corruption
- [ ] GET_CONFIG fires during binary upload without corruption

---

## 7. Deferred

- **File split** (src_config/main.cpp into multiple files): deferred until protocol is stable. Purely organizational, no behavioral change.
- **Boot sync optimization** (only push missing images instead of all): deferred to Phase 3 or later.
