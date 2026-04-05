---
name: Upload Cancel & Disconnect Cleanup Plan
description: Full-stack upload cancel + disconnect cleanup + lazy slot assignment across iOS, S3, and ESP32
type: project
---

# Upload Cancel & Disconnect Cleanup — Roadmap Item 7b

**Status:** DONE — Implemented in commit a28c628

**Depends on:** Item 7 (Upload Queue) — DONE (implemented, in codebase)

**Why:** When an image upload is cancelled or BLE disconnects mid-upload, orphaned files are left on the S3 and ESP32 with no cleanup. The S3 writes image files to **final paths** during BLE reception (before FINALIZE_UPLOAD) and increments `numImages` for RGB565 uploads. No rollback exists. Additionally, slots assigned at queue time create gaps when items are cancelled or fail, breaking the sequential slot assumption on all devices.

**Scope:** Full stack — S3 firmware, ESP32 firmware, iOS app. RP2040 needs no changes (only receives images during FINALIZE_UPLOAD).

## What's Already Implemented (Item 7 — Upload Queue)

These are IN the codebase already — do NOT re-implement:
- `BLEManager.UploadQueueItem` struct (Identifiable, with `id: UUID`, `image: UIImage`, `slot: Int`)
- `queueUploads()` and `startNextUpload()` drain pattern in BLEManager
- `completeUpload()` and `failUpload()` with queue continuation
- `activeUploadImage`, `activeUploadSlot` observable properties
- `uploadQueue`, `uploadQueueTotal`, `uploadImageRef` state
- Multi-select PhotosPicker with `.ordered` in ImageManagerView
- `UploadQueueSheet` (formerly UploadPreviewSheet) showing grid + "Upload N Images" button
- Demo mode queue support via `uploadDemoImage()` calling `completeUpload()`
- Disconnect cleanup clearing queue in `didDisconnectPeripheral`

## Implementation details

### Current code state to be aware of:
- `UploadQueueItem` still has `slot: Int` field — needs removal for lazy assignment
- `ImageManagerView` active upload row still shows `"Slot \(ble.activeUploadSlot)"` — needs replacement
- `UploadPreviewSheet` still has `startSlot` computation and `"Slot \(startSlot + index)"` labels — needs removal
- No cancel button exists on active upload row
- No `ABORT_UPLOAD` or `ABORT_S3_UPLOAD` commands exist anywhere in firmware

## Files to modify

1. **`src_config/main.cpp`** — S3 firmware: abort flag, cleanup function, forwarding abort, disconnect cleanup
2. **`src/main.cpp`** — ESP32 firmware: ABORT_S3_UPLOAD command handler
3. **`ios/SodaMachine/SodaMachine/BLE/BLEManager.swift`** — cancelActiveUpload(), cancelQueuedUpload(), lazy slot assignment
4. **`ios/SodaMachine/SodaMachine/Views/ImageManagerView.swift`** — cancel buttons, remove slot labels
5. **`ios/SodaMachine/SodaMachine/Views/UploadPreviewSheet.swift`** — remove slot labels/computation

## Key design decisions

- **Volatile abort flag on S3**: BLE RX callback (NimBLE task) sets `bleUpload.abortRequested = true`. Forwarding functions check this between chunks and bail out. This works even when main loop is blocked in `stForwardToEsp()`.
- **ABORT_UPLOAD handled in BLE callback, not bleFwdQueue**: Recognized as a known command in the text handler so it executes immediately on NimBLE task, not queued for main loop (which may be blocked during forwarding).
- **S3 cleanup function**: `cleanupAbortedUpload(slot)` deletes `/s3_pngNN.png` and `/imgNN.bin`, calls `updateMeta()` to fix `numImages`.
- **ESP32 needs minimal changes**: It writes to `/tmp_s3.bin` (temp), renames on `PKT_UPLOAD_DONE`, increments `espNumImages` only on `FINALIZE_UPLOAD`. The 5-second inactivity timeout already cleans up. We add `ABORT_S3_UPLOAD` text command for faster cleanup.
- **RP2040 needs no changes**: Only receives images during `FINALIZE_UPLOAD` → `pushImageToDevice()`.
- **Lazy slot assignment**: Remove `slot` from `UploadQueueItem`. Assign `slot = numImages` in `startNextUpload()`. Eliminates all gap issues.

## Key architecture insight

The S3 main loop **blocks** during `stForwardToEsp()`/`stForwardFileToEsp()` (7-30 seconds per binary type at 38400 baud UART). Text commands in `bleFwdQueue` can't be processed during this time. The solution: handle `ABORT_UPLOAD` directly in the BLE RX callback (NimBLE task), which runs independently of the main loop. Set a volatile flag that the forwarding chunk loops check between iterations.

## Step 1: S3 firmware — abort flag and cleanup

### 1a. Add volatile abort flag to bleUpload struct (~line 155)
```c
volatile bool abortRequested = false;
```

### 1b. Add cleanupAbortedUpload() function (~after line 721)
```c
static void cleanupAbortedUpload(uint8_t slot) {
  char path[24];
  snprintf(path, sizeof(path), "/s3_png%02d.png", slot);
  if (LittleFS.exists(path)) LittleFS.remove(path);
  imagePath(path, slot);
  if (LittleFS.exists(path)) LittleFS.remove(path);
  updateMeta();
  Serial.printf("Abort cleanup: slot %d, numImages=%d\n", slot, numImages);
}
```

### 1c. Handle ABORT_UPLOAD in BLE RX callback (~line 284)
In the `BLE_FRAME_TEXT` handler, before the else-clause that queues into `bleFwdQueue`, recognize `"ABORT_UPLOAD"`:
- Set `bleUpload.abortRequested = true`
- If `phase == BLE_UP_WAIT_DATA`, set `phase = BLE_UP_IDLE` and call `cleanupAbortedUpload(bleUpload.slot)`
- Send `"OK:UPLOAD_ABORTED"` back to client

### 1d. Check abort flag in forwarding chunk loops
In `stForwardToEsp()` (~line 595) and `stForwardFileToEsp()` (~line 657), add at top of chunk loop:
```c
if (bleUpload.abortRequested) { /* close file if open, return false */ }
```

### 1e. Handle abort in processBleUpload() (~line 507)
After phase check, before CRC verification:
```c
if (bleUpload.abortRequested) {
  cleanupAbortedUpload(bleUpload.slot);
  bleUpload.phase = BLE_UP_IDLE;
  bleUpload.abortRequested = false;
  return;
}
```

### 1f. Handle abort result in processBleUploadForward() (~line 693)
After forwarding call returns, if `abortRequested` or forwarding failed due to abort:
- Call `cleanupAbortedUpload(bleUpload.slot)`
- Send `"ABORT_S3_UPLOAD"` to ESP32 via `stSendText(stLink, ...)`
- Send `"OK:UPLOAD_ABORTED"` to iOS via BLE (if still connected)
- Reset flag, set phase = IDLE

### 1g. Enhance disconnect handler (~line 185)
When disconnecting client owns upload:
- **FORWARDING phase**: set `abortRequested = true` (loop will exit, cleanup happens in processBleUploadForward)
- **WAIT_DATA/RECEIVED phase**: call `cleanupAbortedUpload(slot)`, set phase = IDLE
- Forward `"ABORT_S3_UPLOAD"` to ESP32

### 1h. Clear abort flag on new upload start (~line 329)
In `BLE_FRAME_BIN_START` handler: `bleUpload.abortRequested = false`

## Step 2: ESP32 firmware — ABORT_S3_UPLOAD command

### 2a. Add to processConfigCommand() (~line 1648)
```c
} else if (strcmp(cmd, "ABORT_S3_UPLOAD") == 0) {
  if (s3Upload.active) abortS3Upload();  // closes /tmp_s3.bin, removes it
}
```
No other ESP32 changes needed. `espNumImages` is never incremented for partial uploads (only FINALIZE_UPLOAD does that). The existing 5-second timeout is a safety net.

## Step 3: iOS — cancel methods and lazy slot assignment

### 3a. Remove slot from UploadQueueItem
```swift
struct UploadQueueItem: Identifiable {
    let id = UUID()
    let image: UIImage
}
```

### 3b. Lazy slot assignment in startNextUpload()
```swift
let slot = numImages  // assign at upload time, not queue time
```

### 3c. Add cancelActiveUpload()
```swift
func cancelActiveUpload() {
    guard isUploading else { return }
    isUploading = false
    uploadSteps = []
    uploadImageRef = nil
    if !demoMode { send("ABORT_UPLOAD") }

    if !uploadQueue.isEmpty {
        uploadStatus = "Cancelled, continuing..."
        uploadProgress = 0
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) { [weak self] in
            self?.startNextUpload()
        }
    } else {
        uploadProgress = nil
        uploadStatus = ""
        uploadQueueTotal = 0
        activeUploadImage = nil
        activeUploadSlot = -1
    }
}
```

### 3d. Re-add cancelQueuedUpload(id:) with total recalculation
```swift
func cancelQueuedUpload(id: UUID) {
    uploadQueue.removeAll { $0.id == id }
    uploadQueueTotal = uploadQueue.count + (isUploading ? 1 : 0)
}
```

### 3e. Handle OK:UPLOAD_ABORTED response
Add to text dispatch so it doesn't trigger error handling. No-op (state already cleared by cancelActiveUpload).

### 3f. Guard IMG_OK and OK:UPLOAD_DONE against cancelled state
```swift
guard isUploading else { return }  // ignore late responses after cancel
```

### 3g. Demo mode cancel: guard timer callback with isUploading check

## Step 4: iOS views — cancel buttons, remove slot labels

### 4a. ImageManagerView: cancel button on active upload row
Add xmark.circle.fill button calling `ble.cancelActiveUpload()`.

### 4b. ImageManagerView: cancel button on queued rows
Re-add xmark.circle.fill button calling `ble.cancelQueuedUpload(id:)`.

### 4c. ImageManagerView: replace "Slot N" with upload status text

### 4d. UploadPreviewSheet: remove slot labels and startSlot computation
Just show image thumbnails and "Upload N Images" button. No slot numbers anywhere.

### 4e. UploadPreviewSheet: update queue item construction
```swift
let items = images.map { BLEManager.UploadQueueItem(image: $0) }
```

## Edge cases

- **Cancel after FINALIZE sent but before OK:UPLOAD_DONE**: S3 is idle, abort is no-op. Guard `OK:UPLOAD_DONE` handler with `isUploading` check.
- **Disconnect during FORWARDING**: Abort flag set by disconnect handler. Forwarding loop exits between chunks. Cleanup runs in processBleUploadForward.
- **countImages() gap**: Impossible with lazy slot assignment (always fills next sequential slot).
- **Multiple rapid cancels**: `guard isUploading` prevents double-action.
- **Late IMG_OK after cancel**: `guard isUploading` in IMG_OK handler ignores it.

## Verification

1. **Build all**: S3 firmware, ESP32 firmware, iOS app
2. **Flash**: S3 first, then ESP32 (peripherals before controller)
3. **Cancel single upload**: Start upload, press cancel mid-progress. Verify: S3 files cleaned up, ESP32 /tmp_s3.bin removed, iOS shows no upload state, numImages unchanged on all devices.
4. **Cancel from queue**: Queue 3 images, cancel middle queued item. Verify: remaining uploads complete to correct sequential slots.
5. **Cancel active with queue**: Queue 3 images, cancel active upload. Verify: next image starts uploading to same slot (numImages unchanged).
6. **BLE disconnect mid-upload**: Pull BLE connection during transfer. Reconnect. Verify: S3 cleaned up, ESP32 cleaned up, no orphaned files.
7. **Demo mode cancel**: Test cancel in demo mode (no hardware needed).
8. **Normal upload still works**: Upload 1 image, upload 3 images. Verify all complete correctly.

## Known Issues to Also Investigate
- **Broken 2nd queued image**: ESP32 didn't save slot 4 despite OK:UPLOAD_DONE (from earlier testing). Likely related to 0.3s delay between queued uploads being too short.
- **RP2040 frozen 60-120s after uploads**: Likely ESP32 busy with UART pushes to devices, blocking periodic re-sync loop.
