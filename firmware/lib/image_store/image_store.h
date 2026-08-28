#pragma once

#include <stdint.h>
#include <stddef.h>

// ════════════════════════════════════════════════════════════
//  A user's own pictures, in a partition of their own
// ════════════════════════════════════════════════════════════
//
// The phone sends pixels a panel can already draw — cropped, resized and
// dithered on the device that has a real image pipeline — so nothing here
// decodes or scales anything. What arrives is written to flash once and mapped
// through the MMU from then on, exactly as `board_art` maps the loading
// animation: LVGL is handed a real pointer and renders straight out of flash,
// at no RAM cost and no load time. A picture chosen months ago is on the glass
// the instant the board boots.
//
// ONE PICTURE IS A BUNDLE, BECAUSE ONE PICTURE IS WORN AT SEVERAL SIZES. The
// enclosure shows a logo as a card, a mid, a thumb and a head; the faucet fills
// its whole glass with one. Every size is resampled on the phone rather than
// zoomed at draw time, so a custom face is as sharp as a factory one. A slot
// holds all the sizes its board needs, and either has all of them or none.
//
// WRITING IS THE RARE CASE AND IT IS WHAT COSTS. On the enclosure a flash write
// suspends the cache its scan-out reaches PSRAM through, so the panel comes down
// around one — the same conflict that keeps that board's logo choice on the main
// board rather than in local NVS. That is affordable because it happens when
// someone chooses a picture and never again. Reading costs nothing, which is why
// this is flash and not PSRAM: re-sending on every boot would trade a cost paid
// once for a cost paid always.
//
// EACH SLOT STANDS ON ITS OWN ERASE BOUNDARY AND CARRIES ITS OWN HEADER. There
// is no directory to keep consistent, so a slot is rewritten by erasing only its
// own sectors and a write cut short costs that one picture. The header goes on
// last: until it does the slot reads as empty rather than as half a face.

constexpr uint32_t IMAGE_SLOT_MAGIC  = 0x494D4753;  // 'IMGS'
constexpr uint32_t IMAGE_SLOT_FORMAT = 2;           // RGB565, row-major, no padding
constexpr uint8_t  IMAGE_MAX_SIZES   = 8;

// The pixel area begins at a fixed offset so the rendition table can grow to
// IMAGE_MAX_SIZES without moving a single stored byte.
constexpr uint32_t IMAGE_SLOT_PIXELS_AT = 128;

struct __attribute__((packed)) ImageSize {
  uint16_t w;
  uint16_t h;
  uint32_t offset;   // from the start of the pixel area
};

struct __attribute__((packed)) ImageSlotHeader {
  uint32_t  magic;
  uint32_t  format;
  uint32_t  bytes;    // pixel bytes across every rendition
  uint32_t  crc32;    // over those bytes, in rendition order
  uint32_t  seq;      // rises with each write, so the newest is identifiable
  uint8_t   count;    // renditions present
  uint8_t   reserved[7];
  ImageSize sizes[IMAGE_MAX_SIZES];
};
static_assert(sizeof(ImageSlotHeader) <= IMAGE_SLOT_PIXELS_AT, "header must fit before the pixels");

// Open the store over a named partition for bundles of exactly these sizes, in
// this order. Slot size is derived and rounded up to the flash erase size, so
// one slot is always rewritable without touching its neighbours. A stored slot
// whose sizes do not match this list is not this build's and reads as empty.
bool imageStoreBegin(const char *partitionLabel, const ImageSize *sizes, uint8_t count);

uint8_t imageStoreCapacity();
bool    imageStoreOccupied(uint8_t slot);
uint8_t imageStoreHeld();

// The crc32 over a slot's whole bundle, or 0 where the slot is empty. This is
// a picture's identity: a phone that has never seen this machine can tell
// which of its own cached faces is which, and a phone that cached one under a
// slot number can tell that the slot has changed hands since.
uint32_t imageStoreCrc(uint8_t slot);

// A mapped pointer to one rendition of one slot, or nullptr where the slot is
// empty. Valid until that slot is written again. Nothing is copied or allocated.
const uint16_t *imageStorePixels(uint8_t slot, uint8_t size);

// ── Taking a picture in ───────────────────────────────────────────────────
// One slot at a time, renditions concatenated in the order begin() was given.
// The crc32 covers the whole bundle, so a slot cannot end up holding one
// picture's card above another's thumb.
bool imageStoreWriteBegin(uint8_t slot, uint32_t crc32);
bool imageStoreWriteChunk(uint32_t offset, const void *data, uint16_t len);
bool imageStoreWriteFinish();
void imageStoreWriteAbort();

// Total pixel bytes one bundle carries — what a sender is told to send.
uint32_t imageStoreBundleBytes();

// Where the open write has got to, which is what a sender resumes from.
uint32_t imageStoreWriteOffset();
bool     imageStoreWriteActive();

// What the store sees when it looks at itself. For a board with no console:
// whether the partition is mapped at all, and what slot zero's header reads
// back as, which is what separates a write that did not happen from a write
// that cannot be seen.
void imageStoreDiag(char *out, unsigned n);

// Give a slot back. What the app calls "remove".
bool imageStoreErase(uint8_t slot);
