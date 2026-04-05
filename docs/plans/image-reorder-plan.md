---
name: Image Reorder + Factory Image Hiding Plan
description: Plan for item 8 — reordering images via order file + SET_ORDER command, and soft-hiding factory images
type: project
---

# Image Reorder + Factory Image Hiding

## UX Philosophy (learned from prior UI polish)

- **Remove unnecessary steps.** Reordering should be immediate, not require an edit mode toggle.
- **Content goes where it ends up.** The image visually moves to its new position, no jumping around.
- **Minimal chrome.** Reorder controls should be subtle (like the trash icon) not heavy (no drag handles, grippy bars, or edit mode toolbars).
- **Dark navy consistency.** Everything stays in Theme.background with Theme.textSecondary for controls.
- **Fun matters.** A quick tap-tap to rearrange images should feel snappy and satisfying, not tedious.

## Reorder UX: Up/Down Arrow Buttons

**Small up/down chevron buttons per row**, visible alongside the existing trash button.

Why this over drag-and-drop:
- We use `ScrollView` + `VStack` (not `List`), so `.onMove` isn't available and custom drag gestures fight with scroll.
- The image list is small (typically 3-8 images, max 23). Arrow taps are faster and more precise for short lists.
- Arrow buttons match the existing row layout. Discoverable without explanation.
- Haptic feedback on each swap (light impact) makes it feel responsive.

**Layout per row:**
```
[image circle]  ...spacer...  [F1] [F2]  [up] [down]  [trash]
```
- `up` hidden on first row, `down` hidden on last row
- Same 14pt system font as trash icon, Theme.textSecondary
- chevron.up / chevron.down SF Symbols

**No edit mode toggle.** The arrows and trash are always visible (when conditions allow — no uploads in progress, etc.).

## Factory Image Hiding UX

Factory images (slots 0 through factoryImageCount-1) are currently undeletable. The roadmap calls for "soft-delete" where factory images can be hidden from the flavor picker but remain on device.

- `HIDDEN_IMAGES=0,2,4` in user_config.txt (firmware-side, so S3 can respect it too)
- Hidden images don't appear in the ImagePickerSheet flavor selection grid
- Hidden images still appear in Manage Images but with reduced opacity and an "eye.slash" icon instead of trash
- Tapping the eye.slash icon un-hides; non-hidden factory images show the eye icon (tap to hide)
- User-uploaded images always show trash (they can be fully deleted)

## Ordering Architecture: `/img_order.txt`

### The Problem

Images are stored on ESP32 LittleFS as sequentially numbered files (`/rp_img00.bin`, `/s3_img00.bin`, etc.). Deletion shifts all higher slots down (compacting). There is no concept of display order separate from physical slot number. We need:
1. A single file that determines display order
2. A single message from iOS that sets an entirely new arbitrary order
3. Order persisted on ESP32, reflected in iOS LIST responses, optionally synced to S3

### Design: Order Is Metadata, Not File Layout

**File:** `/img_order.txt` on ESP32 LittleFS — a single line of comma-separated physical slot indices in display order.

Example with 4 images where user moved image 2 to the top:
```
2,0,1,3
```

If the file doesn't exist (first boot, migration), default to natural order `0,1,2,...,numEspImages-1`.

**Command:** `SET_ORDER:2,0,1,3` — the complete ordering in one message.
- Sent from iOS → S3 (BLE) → ESP32 (UART relay)
- ESP32 validates: correct count matches numEspImages, no duplicates, all slots 0..n-1 present
- ESP32 writes `/img_order.txt`, responds `OK`
- One file write = arbitrary reorder. No multi-device swap choreography.

### Who Needs Order

| Device | Needs order? | Why |
|--------|-------------|-----|
| **ESP32** | Yes (authoritative) | Writes `/img_order.txt`. Returns LIST results in order-file sequence. Translates logical→physical for all operations. |
| **iOS** | Yes (from LIST) | Receives ordered LIST from S3. Sends SET_ORDER when user reorders. Keeps local copy for instant optimistic UI. |
| **S3** | Defer | Rotary encoder with small list — natural order is fine for now. Could receive a copy later for settings menu image picker. |
| **RP2040** | No | Displays whichever single image ESP32 tells it. Doesn't browse. |

### Flavor References Stay Physical

**`flavor1Image` / `flavor2Image` remain physical slot references.** They do NOT change when order changes. If flavor1 points to physical slot 2, reordering the display list doesn't affect which image gets shown during dispensing. This completely decouples reorder from flavor assignment logic.

When iOS displays the flavor picker or badges, it maps physical slot → display position using the order array. But the SET config commands still send physical slot numbers.

### Interaction With Delete

Today, deletion shifts all higher physical slots down (compacting files on disk). The order file must be updated in lockstep:

**Example:** Order is `2,0,1,3`. Delete physical slot 1.
1. Remove `1` from the order list → `2,0,3`
2. Decrement any entry > 1 → `1,0,2`
3. Write updated `/img_order.txt`

This happens inside the existing ESP32 delete handler, after the file shift completes. Simple arithmetic, no multi-device coordination.

### Interaction With Add (Upload)

New images are always appended as the last physical slot (numEspImages before increment). The order file appends the new slot to the end:

**Example:** Order is `1,0,2`, new image uploaded → order becomes `1,0,2,3`.

### Interaction With Factory Reset

Factory reset rebuilds `/img_order.txt` as natural order `0,1,...,factoryImageCount-1`.

### LIST Response Change

Currently `LIST` returns images in physical slot order (`IMG:0:label0`, `IMG:1:label1`, ...). After this change, `LIST` returns images in order-file sequence:

If order is `2,0,1`:
```
IMG:2:label2
IMG:0:label0
IMG:1:label1
END
```

iOS parses these in the order received. The slot number in each `IMG:slot:label` line tells iOS which physical slot to reference for downloads, flavor assignment, etc.

### iOS Reorder Flow (Up Arrow Tap)

1. User taps up arrow on image at display position N
2. iOS swaps positions N and N-1 in its local order array (optimistic update with animation)
3. iOS sends `SET_ORDER:<full comma-separated order>` via BLE
4. ESP32 validates, writes file, responds OK
5. If ESP32 rejects (validation fail), iOS reverts the swap

### Migration

On firmware update (first boot with new code):
- `/img_order.txt` won't exist yet
- Any code reading the order file falls back to natural order `0,1,...,numEspImages-1`
- First reorder from iOS creates the file
- OR: boot code creates it with natural order if missing (cleaner)

## Implementation Order

1. **ESP32 firmware**: `/img_order.txt` read/write helpers, `SET_ORDER` command handler, update delete handler to adjust order file, update LIST to return in order-file sequence, boot migration (create file if missing)
2. **iOS BLEManager**: Parse slot numbers from ordered LIST (already has slot in `IMG:slot:label`), add `setOrder()` method, local order array for optimistic updates
3. **iOS ImageManagerView**: Add up/down chevron buttons, wire to BLEManager.setOrder()
4. **Factory image hiding** (can be separate PR):
   - ESP32: `HIDDEN_IMAGES` config key, `SET_HIDDEN`/`GET_HIDDEN` commands
   - iOS BLEManager: track hidden set
   - iOS ImageManagerView: eye/eye.slash toggle for factory images
   - iOS ImagePickerSheet: filter out hidden images

## Open Questions

- Should reorder be blocked during uploads (like delete currently is)? Probably yes for simplicity.
- Should the S3 rotary display respect order/hiding? Defer for now — can add later by syncing the order file.
- Edge case: what if iOS and S3 both send SET_ORDER simultaneously? Last-write-wins is fine given the use case (single user).
