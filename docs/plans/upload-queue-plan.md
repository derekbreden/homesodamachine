---
name: Upload Queue Plan
description: iOS upload queue — allow selecting and queuing multiple image uploads while one is in progress
type: project
---

# Upload Queue — Roadmap Item 7

**Status:** DONE — Implemented in commit e597d14

**Why:** Currently the iOS app only supports single-image uploads. The PhotosPicker is disabled during uploads, and `uploadImage()` drops any second call. Users need to be able to select and start uploading more images while the current one is in progress. This is a necessity even in the prototyping phase, not a nice-to-have.

**Scope:** iOS app only. No firmware changes expected — the BLE upload protocol already handles one upload at a time with busy guards (from BLE multi-client work). The queue lives entirely in the iOS app, draining one upload at a time.

**Current upload flow (single-image):**
- `ImageManagerView.swift`: PhotosPicker disabled while `ble.uploadProgress != nil`
- `UploadPreviewSheet.swift`: presents single image, calls `ble.uploadImage(image, toSlot: slot)`
- `BLEManager.swift`: `isUploading` bool, scalar upload state, `guard !isUploading` drops second calls
- Existing `imgDownloadQueue: [Int]` is a download queue pattern that could inform the upload queue design

**What needs to happen:**
1. Plan the upload queue architecture (data structure, UI changes, queue drain logic)
2. Implement the queue in BLEManager
3. Update iOS UI to allow selecting multiple images / queuing while upload is active
4. Test with concurrent BLE operations (downloads, config changes happening alongside queued uploads)
