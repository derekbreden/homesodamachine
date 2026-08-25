#include "board_art.h"

#include <esp_partition.h>
#include <string.h>
#include "proto_msg.h"   // uartCrc32Update — the same CRC the link verifies with

static const esp_partition_t *artPart = nullptr;
static const void *artBase = nullptr;
static esp_partition_mmap_handle_t artMap = 0;
static bool artTried = false;

static bool mapOnce() {
  if (artBase) return true;
  if (artTried) return false;
  artTried = true;

  artPart = esp_partition_find_first(ESP_PARTITION_TYPE_DATA,
                                     (esp_partition_subtype_t)0x40, "art");
  if (!artPart) return false;

  // Mapped, not read: the MMU points the CPU at flash the same way it does for
  // const data in the app image, so nothing is copied and nothing is buffered.
  if (esp_partition_mmap(artPart, 0, artPart->size, ESP_PARTITION_MMAP_DATA,
                         &artBase, &artMap) != ESP_OK) {
    artBase = nullptr;
    return false;
  }
  return true;
}

bool boardArtHeader(BoardArtHeader &out) {
  if (!mapOnce()) return false;
  memcpy(&out, artBase, sizeof(out));
  return true;
}

const uint16_t *boardArtMap(uint32_t wantCount, uint16_t wantW, uint16_t wantH) {
  if (!mapOnce()) return nullptr;

  BoardArtHeader h;
  memcpy(&h, artBase, sizeof(h));
  if (h.magic != BOARD_ART_MAGIC) return nullptr;
  if (h.format != BOARD_ART_FORMAT) return nullptr;
  if (h.count != wantCount || h.w != wantW || h.h != wantH) return nullptr;

  const uint64_t need = (uint64_t)BOARD_ART_HEADER_SIZE +
                        (uint64_t)wantCount * wantW * wantH * 2u;
  if (need > artPart->size) return nullptr;

  return (const uint16_t *)((const uint8_t *)artBase + BOARD_ART_HEADER_SIZE);
}

bool boardArtVerify() {
  BoardArtHeader h;
  if (!boardArtHeader(h)) return false;
  if (h.magic != BOARD_ART_MAGIC) return false;

  const uint32_t bytes = h.count * (uint32_t)h.w * h.h * 2u;
  if ((uint64_t)BOARD_ART_HEADER_SIZE + bytes > artPart->size) return false;

  const uint8_t *p = (const uint8_t *)artBase + BOARD_ART_HEADER_SIZE;
  uint32_t crc = 0;
  for (uint32_t off = 0; off < bytes; off += 4096) {
    const uint32_t n = (bytes - off < 4096) ? (bytes - off) : 4096;
    crc = uartCrc32Update(crc, p + off, n);
  }
  return crc == h.crc32;
}
