---
name: Unified Image Picker Plan
description: Merge image management (add/delete/upload progress) into the flavor image picker sheet, eliminating separate ImageManagerView
type: project
---

# Unified Image Picker Plan

**Goal:** Merge all image management into the flavor `ImagePickerSheet` so users can select, add, and delete images from one place. Remove "Manage Images" from settings and delete `ImageManagerView.swift`.

## Current State

- `ImagePickerSheet` (ConfigView.swift lines 51-115): LazyVGrid of 120x120 circles, tap to select flavor image, "Done" to dismiss
- `ImageManagerView` (separate file): list-based view with add (PhotosPicker), delete (trash icon + alert), upload progress (linear bar + cancel), download progress, slot counter
- Settings page has "Manage Images" button that opens ImageManagerView as a sheet

## Design

### Grid Layout

Keep the existing `LazyVGrid` with `GridItem(.adaptive(minimum: 120), spacing: 20)` and 120x120 circles.

After all existing image circles, append:

1. **Active upload circle** (if `ble.uploadProgress != nil`):
   - Show `ble.activeUploadImage` as 120x120 circle
   - Dark overlay (Color.black.opacity(0.5)) on top of the image
   - Radial progress ring: `Circle().trim(from: 0, to: progress).stroke(style: StrokeStyle(lineWidth: 4, lineCap: .round)).rotationEffect(.degrees(-90))` in white
   - Not tappable for selection
   - Long-press context menu: "Cancel Upload" (destructive)

2. **Queued upload circles** (for each item in `ble.uploadQueue`):
   - Show `item.image` as 120x120 circle
   - Dark overlay (Color.black.opacity(0.5))
   - Small clock or pause SF Symbol centered (no progress ring)
   - Not tappable for selection
   - Long-press context menu: "Cancel Upload" (destructive)

3. **"+" add button** (if `totalPendingSlots < maxImages` and `ble.imageDownloadProgress == nil`):
   - 120x120 circle with `Theme.placeholder` fill
   - `plus` SF Symbol centered, `Theme.textSecondary`
   - Tap opens `PhotosPicker` (same config as ImageManagerView: `maxSelectionCount: remaining`, `.ordered`, `.images`)
   - Presented inline via `PhotosPicker` modifier on the circle, or via `@State` binding

### Context Menu (Long-Press on Existing Images)

```swift
.contextMenu {
    if canDelete {
        Button("Delete", role: .destructive) {
            deleteSlot = slot
            showDeleteConfirm = true
        }
    }
}
```

- `canDelete` logic (same as ImageManagerView): `numImages > 1 && imageDownloadProgress == nil && uploadQueue.isEmpty && uploadProgress == nil`
- Confirmation alert: "Delete Image?" / "This cannot be undone." / Delete (destructive) + Cancel
- Delete error alert: "Delete Failed" with `ble.deleteError` message
- Factory images (if factory image hiding is implemented later) would have "Hide" instead of "Delete"

### Selection Behavior

- Tap on an existing (completed) image: select it as the flavor image (same as current behavior — updates `selectedSlot`, calls `onSelect(slot)`)
- Tap on uploading/queued circle: no action (not selectable)
- Tap on "+": opens PhotosPicker

### Upload Integration

- `PhotosPicker` `onChange` handler: same async loading logic as ImageManagerView — load `Data` from each `PhotosPickerItem`, convert to `UIImage`, call `ble.queueUploads()`
- `selectedPhotos` state var moves into `ImagePickerSheet`
- Upload circles appear immediately in the grid after queuing

### Download Progress

- When `ble.imageDownloadProgress != nil`, images that aren't cached yet already show a placeholder circle with a spinner (existing behavior in ImagePickerSheet). No additional UI needed — the grid naturally shows loading state.

### What Gets Removed

1. **Settings page**: Remove "Manage Images" button and `showImageManager` binding
2. **ConfigView**: Remove `showImageManager` @State, remove `.sheet(isPresented: $showImageManager)` presenting `ImageManagerView`
3. **ImageManagerView.swift**: Delete the entire file
4. **SettingsPageView**: Remove `@Binding var showImageManager: Bool` parameter

## Implementation Steps

### Step 1: Expand ImagePickerSheet

- Add `import PhotosUI`
- Add state: `@State private var selectedPhotos: [PhotosPickerItem] = []`, `@State private var deleteSlot: Int?`, `@State private var showDeleteConfirm = false`
- Add computed properties: `maxImages = 10`, `totalPendingSlots`, `canDelete`
- Restructure the `ForEach` loop body into a helper that returns the circle with context menu
- After the ForEach, add: active upload circle, queued upload circles, "+" circle
- Add `.contextMenu` to each existing image circle with conditional "Delete" option
- Add delete confirmation alert and delete error alert
- Add PhotosPicker `.onChange` handler
- The "+" circle uses `PhotosPicker` as its label (PhotosPicker can wrap any view)

### Step 2: Radial Progress Circle

Create a small helper view `RadialProgressCircle`:
```swift
private struct RadialProgressCircle: View {
    let image: UIImage
    let progress: Double?  // nil = queued (no ring), 0-1 = uploading

    var body: some View {
        ZStack {
            Image(uiImage: image)
                .resizable()
                .scaledToFill()
                .frame(width: 120, height: 120)
                .clipShape(Circle())

            Circle()
                .fill(Color.black.opacity(0.5))
                .frame(width: 120, height: 120)

            if let progress {
                Circle()
                    .trim(from: 0, to: progress)
                    .stroke(Color.white, style: StrokeStyle(lineWidth: 4, lineCap: .round))
                    .frame(width: 100, height: 100)
                    .rotationEffect(.degrees(-90))
            } else {
                Image(systemName: "clock")
                    .font(.system(size: 24))
                    .foregroundStyle(.white.opacity(0.7))
            }
        }
    }
}
```

### Step 3: Remove ImageManagerView

- Delete `ImageManagerView.swift`
- Remove `showImageManager` from `SettingsPageView` (parameter + binding + button)
- Remove `showImageManager` from `ConfigView` (@State + .sheet)
- Clean up `SettingsPageView` init call in `ConfigView`

### Step 4: Slot Counter

- Add subtle slot counter text below the grid: `"N of 10"` in `Theme.textSecondary`, small font
- Only show when relevant (uploads pending or near capacity)
- Or: always show as a small label, keeping the user informed

## Edge Cases

- **User selects an uploading/queued image as flavor**: prevented — tap does nothing on upload circles
- **User deletes the currently-selected flavor image**: firmware handles reassignment (existing behavior)
- **Upload completes while picker is open**: new image appears as a normal selectable circle (uploadProgress clears, numImages increments, cachedImages updates — SwiftUI reactivity handles the transition)
- **At 10 images with uploads queued**: "+" button hidden (totalPendingSlots >= maxImages)
- **Download in progress**: "+" button hidden, images show placeholder spinners (existing)
- **Demo mode**: uploads are simulated, delete not applicable (demo images are generated) — context menu could be hidden entirely in demo mode, or shown but non-functional

## No Firmware Changes

This is purely an iOS UI refactor. No BLE protocol, ESP32, S3, or RP2040 changes needed. No boards need flashing.
