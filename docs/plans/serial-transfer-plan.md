---
name: SerialTransfer migration (superseded)
description: SUPERSEDED — SerialTransfer was later replaced by TinyProto HDLC. Kept for reference only.
type: project
---

# SerialTransfer Migration — SUPERSEDED

Originally replaced hand-rolled UART binary protocol with SerialTransfer library. Later replaced by TinyProto HDLC (ProtoLink wrapper) for reliable full-duplex communication with built-in ACKs, retransmission, and flow control.

## Why

After $50/7 hours debugging hand-rolled UART binary protocol bugs (byte misalignment, text/binary collision, boot noise corruption), replaced the custom STX STX framing on inter-MCU links with [SerialTransfer](https://github.com/PowerBroker2/SerialTransfer). COBS encoding makes false frame detection structurally impossible.

## What changed

- **USB protocol unchanged** — problems were on inter-MCU links only
- **No bridge mode** — images stored on ESP32, pushed to devices (`PUSH_IMG:slot:target`)
- **Text commands wrapped in PKT_TEXT (0xFE)** — eliminates text/binary multiplexing
- **Shared header `lib/uart_st/uart_st.h`** — all packet IDs, payload structs, CRC-32, helper functions
- **~2000 lines of custom framing/CRC/parser code removed**

## 9 commits

1. BLE callback cross-task safety fix (S3)
2. PNG file streaming to replace imageBuf/bleSendBuf aliasing (S3)
3. Add SerialTransfer lib + shared `uart_st.h` header
4. Migrate RP2040 receiver to SerialTransfer
5. Migrate ESP32 Serial2 (RP2040 link) sender
6. Migrate S3 receiver to SerialTransfer
7. Migrate ESP32 Serial1 (S3 link) sender + `processConfigCommand` refactor with `StStream` wrapper
8. Update `upload_image.py` (remove bridge mode, add `PUSH_IMG` support)
9. Dead code cleanup

## Key gotcha

SerialTransfer rejects zero-length payloads (`PAYLOAD_ERROR`) — always send ≥1 byte.

## Flash order matters

Peripherals first (RP2040, S3), then ESP32 — because the new protocol is incompatible with the old one.
