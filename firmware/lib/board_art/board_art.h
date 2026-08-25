#pragma once

#include <stdint.h>
#include <stddef.h>

// ════════════════════════════════════════════════════════════
//  Images in a partition of their own
// ════════════════════════════════════════════════════════════
//
// Two displays carry pixels that dwarf their code. The enclosure's loading
// animation is 16 frames of 360x360 RGB565; the rotary display's animation and
// flavor faces are 19 of 240x240. Compiled in, every update of code that never
// touches a pixel carried them anyway.
//
// In the `art` partition they are mapped through the MMU exactly as const
// .rodata was — LVGL is handed a real pointer and renders straight out of
// flash — so this costs no RAM, no load time and no boot delay.
//
// The layout is written by `tools/make_art.py`, which reads the same
// `images/*.h` headers that used to be compiled in. Those headers stay the
// source; this is how they reach the board.
//
// The header is checked at boot, which is what distinguishes a flashed
// partition from an erased one (erased flash is 0xFF and matches no magic).
// The CRC32 over the pixels is not walked at boot — a half-written partition
// draws wrong frames, which is cosmetic — but it is what an arriving image is
// verified against before it is allowed to replace the one there.

constexpr uint32_t BOARD_ART_MAGIC       = 0x4D534148;
constexpr uint32_t BOARD_ART_FORMAT      = 1;
constexpr uint32_t BOARD_ART_HEADER_SIZE = 32;

struct __attribute__((packed)) BoardArtHeader {
  uint32_t magic;
  uint32_t format;
  uint32_t count;
  uint16_t w;
  uint16_t h;
  uint32_t crc32;      // over the pixels that follow
  uint8_t  reserved[12];
};
static_assert(sizeof(BoardArtHeader) == BOARD_ART_HEADER_SIZE, "art header is 32 bytes");

// Map the art partition. Returns a pointer to the first image's pixels, with
// images laid out back to back in the order `tools/make_art.py` wrote them, or
// nullptr if the partition is absent or holds something this build does not
// recognise. Safe to call more than once.
const uint16_t *boardArtMap(uint32_t wantCount, uint16_t wantW, uint16_t wantH);

// One image out of the mapped run.
inline const uint16_t *boardArtAt(const uint16_t *base, uint32_t index,
                                  uint16_t w, uint16_t h) {
  return base ? base + (size_t)index * w * h : nullptr;
}

// What the mapped partition says about itself, for the console.
bool boardArtHeader(BoardArtHeader &out);

// Walk the pixels and compare against the header's CRC32. Seconds of work, so
// this is asked for rather than done at boot.
bool boardArtVerify();
