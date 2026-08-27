#pragma once

#include <stdint.h>
#include <stddef.h>

// ════════════════════════════════════════════════════════════
//  A user's own pictures, in a partition of their own
// ════════════════════════════════════════════════════════════
//
// The phone sends pixels a panel can already draw — cropped, resized and
// dithered to this board's exact geometry in RGB565 — so nothing here decodes
// anything. What arrives is written to flash once and mapped through the MMU
// from then on, exactly as `board_art` maps the loading animation: LVGL is
// handed a real pointer and renders straight out of flash, at no RAM cost and
// no load time. A picture set months ago is on the glass the instant the board
// boots.
//
// WRITING IS THE RARE CASE AND IT IS WHAT COSTS. On the enclosure display a
// flash write suspends the cache its scan-out reaches PSRAM through, so the
// panel has to come down around one — the same conflict that keeps that
// board's logo choice on the main board rather than in local NVS. That is
// affordable because it happens when someone chooses a picture, and never
// again. Reading costs nothing, which is why storage is flash and not PSRAM.
//
// EACH SLOT CARRIES ITS OWN HEADER AND STANDS ON ITS OWN ERASE BOUNDARY.
// There is no directory to keep consistent: a slot is rewritten by erasing
// only its own sectors, so a write interrupted by a power cut costs that one
// picture and cannot corrupt another. An erased slot is 0xFF and matches no
// magic, which is how an empty one is told from a written one.

constexpr uint32_t IMAGE_SLOT_MAGIC  = 0x494D4753;  // 'IMGS'
constexpr uint32_t IMAGE_SLOT_FORMAT = 1;           // RGB565, row-major, no padding
constexpr uint32_t IMAGE_SLOT_HEADER = 32;

struct __attribute__((packed)) ImageSlotHeader {
  uint32_t magic;
  uint32_t format;
  uint16_t w;
  uint16_t h;
  uint32_t bytes;    // pixel bytes that follow, w * h * 2
  uint32_t crc32;    // over those bytes
  uint32_t seq;      // rises with every write, so the newest is identifiable
  uint8_t  reserved[8];
};
static_assert(sizeof(ImageSlotHeader) == IMAGE_SLOT_HEADER, "slot header is 32 bytes");

// Open the store over a named partition, for images of exactly this geometry.
// Slot size is derived from it and rounded up to the flash erase size, so one
// slot is always rewritable without touching its neighbours. False when the
// partition is absent or too small for a single slot.
bool imageStoreBegin(const char *partitionLabel, uint16_t w, uint16_t h);

// How many slots this partition holds, and how many currently hold a picture.
uint8_t imageStoreCapacity();
bool    imageStoreOccupied(uint8_t slot);

// A mapped pointer to one slot's pixels, or nullptr where the slot is empty or
// holds something this build does not recognise. Valid until that slot is
// written again. Nothing is copied and nothing is allocated.
const uint16_t *imageStorePixels(uint8_t slot);

// ── Taking a picture in ───────────────────────────────────────────────────
// One slot at a time. begin() erases it, write() takes the bytes in ascending
// order as they arrive, and finish() checks the whole thing against the crc32
// the sender promised before the header that makes the slot readable is
// written last. A transfer that stops partway leaves the slot empty rather
// than half-written, because the header is what makes it count.
bool imageStoreWriteBegin(uint8_t slot, uint16_t w, uint16_t h, uint32_t crc32);
bool imageStoreWriteChunk(uint32_t offset, const void *data, uint16_t len);
bool imageStoreWriteFinish();
void imageStoreWriteAbort();

// Where the open write has got to, which is what the sender is asked to resume
// from. Zero when no write is open.
uint32_t imageStoreWriteOffset();
bool     imageStoreWriteActive();

// Drop a picture, making the slot empty again.
bool imageStoreErase(uint8_t slot);
