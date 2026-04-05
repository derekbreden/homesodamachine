---
name: BLE + iOS app plan
description: DONE (Phases 1-3) — NimBLE on S3 as BLE bridge, iOS app (SwiftUI + CoreBluetooth), config/image/upload flows
type: project
---

# BLE Mobile App — DONE (Phases 1-3)

Phase 4 (stats) was completed as roadmap item 5 (not part of this plan).

## Architecture

```
iOS App (SwiftUI + CoreBluetooth)
    │ BLE 5.0 (NUS service, framed protocol)
    ▼
ESP32-S3 (config display + BLE bridge, LittleFS images)
    │ TinyProto HDLC UART (115200 baud)
    ▼
ESP32 (main controller, source of truth, LittleFS config + images)
    │ TinyProto HDLC UARTs
    ▼
RP2040 display + ESP32-S3
```

## Hard architectural rules (learned the painful way)

1. **PNG lifecycle** — every slot operation must handle both PNG and RGB565 (delete, swap, push, upload)
2. **S3 memory constraints** — ~4-10KB free heap after LVGL + BLE. PNG downloads stream from LittleFS via `bleFile` into `bleSendChunkBuf[240]`. Never malloc buffers for BLE image transfer.
3. **Cross-task safety** — BLE callbacks run on NimBLE task, `loop()` on main task. BLE callback sets flags (`BleRequest` enum + volatile vars), `loop()` does all file I/O.
4. **Config push model** — ESP32 pushes `CONFIG:` to S3 after every SAVE. iOS sends one `GET_CONFIG` on connect, then listens reactively. No polling.
5. **RP2040 is frozen** — only receives RGB565 via SerialTransfer, no BLE awareness.

## What was built

### Phase 1 (BLE Foundation)
- NimBLE BLE server on S3 with NUS service (TX notify, RX write)
- BLE commands handled locally (`LIST`, `GETPNG:N`, `GETIMG:N`) or forwarded to ESP32 via SerialTransfer

### Phase 2 (Config + Image Download)
- iOS app: scan, connect, auto-reconnect, push-based config, sequential PNG downloads
- ConfigView: 5-page TabView carousel (2 images, 2 ratios, settings)

### Phase 3 (Image Upload — Option C implemented)
- Phone generates PNG + 2x RGB565, sends all three via BLE → S3 → ESP32
- S3 stores locally AND forwards to ESP32 via SerialTransfer
- ESP32 pushes RP2040 RGB565 via SerialTransfer
- ~150KB BLE transfer per image — acceptable for infrequent uploads

## Deferred items

- **Boot sync scalability:** Pushing all PNGs every boot works at 3 images. At 10+ images, boot will take minutes. Future option: per-slot existence check.
- **BLE connection indicator on S3 display:** Nice to have.
- **WiFi/Matter:** Can add C6/C3 later if needed.
