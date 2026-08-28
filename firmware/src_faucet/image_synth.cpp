#include "image_synth.h"

#include <Arduino.h>

#include "image_store.h"
#include "proto_msg.h"

namespace {

// Widest rendition in the bundle, in bytes. One row is the working buffer.
constexpr uint16_t ROW_MAX = 240 * 2;

// Deterministic, and different per rendition so a mix-up between them shows as
// a colour rather than as a plausible picture.
void makeRow(uint8_t rendition, uint16_t w, uint16_t h, uint16_t y, uint8_t *out) {
  for (uint16_t x = 0; x < w; x++) {
    const uint16_t r = (uint16_t)((uint32_t)x * 31 / (w ? w : 1));
    const uint16_t g = (uint16_t)((uint32_t)y * 63 / (h ? h : 1));
    const uint16_t b = (uint16_t)((rendition * 7u) & 31u);
    const uint16_t v = (uint16_t)((r << 11) | (g << 5) | b);
    out[x * 2]     = (uint8_t)(v & 0xFF);
    out[x * 2 + 1] = (uint8_t)(v >> 8);
  }
}

}  // namespace

bool imageSynthWrite(uint8_t slot) {
  static uint8_t row[ROW_MAX];

  // Pass one: what the store will be told to hold this to.
  uint32_t crc = 0;
  for (uint8_t i = 0; i < IMAGE_BUNDLE_COUNT; i++) {
    const uint16_t w = IMAGE_BUNDLE[i].w, h = IMAGE_BUNDLE[i].h;
    for (uint16_t y = 0; y < h; y++) {
      makeRow(i, w, h, y, row);
      crc = uartCrc32Update(crc, row, (size_t)w * 2);
    }
  }

  if (!imageStoreWriteBegin(slot, crc)) return false;

  // Pass two: the same bytes, through the path a phone's would take.
  uint32_t at = 0;
  for (uint8_t i = 0; i < IMAGE_BUNDLE_COUNT; i++) {
    const uint16_t w = IMAGE_BUNDLE[i].w, h = IMAGE_BUNDLE[i].h;
    for (uint16_t y = 0; y < h; y++) {
      makeRow(i, w, h, y, row);
      if (!imageStoreWriteChunk(at, row, (uint16_t)(w * 2))) {
        imageStoreWriteAbort();
        return false;
      }
      at += (uint32_t)w * 2;
    }
  }

  return imageStoreWriteFinish();
}
