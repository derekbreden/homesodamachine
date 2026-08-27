#include "image_store.h"

#include <Arduino.h>
#include <esp_partition.h>
#include <spi_flash_mmap.h>
#include <string.h>

namespace {

const esp_partition_t *part = nullptr;
const void            *mapped = nullptr;
esp_partition_mmap_handle_t mapHandle = 0;

uint16_t imgW = 0, imgH = 0;
uint32_t slotBytes = 0;    // header + pixels, rounded up to the erase size
uint32_t pixelBytes = 0;
uint8_t  slotCount = 0;

// The open write, if any.
bool     writing = false;
uint8_t  writeSlot = 0;
uint32_t writeAt = 0;
uint32_t writeCrc = 0;
uint32_t writeRunning = 0;

constexpr uint32_t ERASE = 4096;

uint32_t crc32Update(uint32_t prev, const uint8_t *data, size_t len) {
  uint32_t crc = ~prev;
  for (size_t i = 0; i < len; i++) {
    crc ^= data[i];
    for (uint8_t b = 0; b < 8; b++) crc = (crc & 1) ? (crc >> 1) ^ 0xEDB88320 : crc >> 1;
  }
  return ~crc;
}

// The map has to be dropped around a write and taken again after: what the MMU
// is showing is the flash that just changed underneath it.
bool remap() {
  if (mapped) {
    esp_partition_munmap(mapHandle);
    mapped = nullptr;
    mapHandle = 0;
  }
  if (!part) return false;
  return esp_partition_mmap(part, 0, part->size, ESP_PARTITION_MMAP_DATA,
                            &mapped, &mapHandle) == ESP_OK;
}

const ImageSlotHeader *headerAt(uint8_t slot) {
  if (!mapped || slot >= slotCount) return nullptr;
  const uint8_t *base = (const uint8_t *)mapped + (size_t)slot * slotBytes;
  const ImageSlotHeader *h = (const ImageSlotHeader *)base;
  if (h->magic != IMAGE_SLOT_MAGIC || h->format != IMAGE_SLOT_FORMAT) return nullptr;
  if (h->w != imgW || h->h != imgH || h->bytes != pixelBytes) return nullptr;
  return h;
}

}  // namespace

bool imageStoreBegin(const char *partitionLabel, uint16_t w, uint16_t h) {
  part = esp_partition_find_first(ESP_PARTITION_TYPE_DATA,
                                  ESP_PARTITION_SUBTYPE_ANY, partitionLabel);
  if (!part) {
    Serial.printf("[images] no partition '%s'\n", partitionLabel);
    return false;
  }

  imgW = w;
  imgH = h;
  pixelBytes = (uint32_t)w * h * 2;
  slotBytes = ((IMAGE_SLOT_HEADER + pixelBytes) + ERASE - 1) / ERASE * ERASE;
  slotCount = (uint8_t)((part->size / slotBytes) > 255 ? 255 : (part->size / slotBytes));

  if (!slotCount) {
    Serial.printf("[images] '%s' is %lu B, one %ux%u slot needs %lu\n",
                  partitionLabel, (unsigned long)part->size, w, h,
                  (unsigned long)slotBytes);
    part = nullptr;
    return false;
  }
  if (!remap()) {
    Serial.println("[images] partition would not map");
    part = nullptr;
    return false;
  }

  uint8_t held = 0;
  for (uint8_t i = 0; i < slotCount; i++) if (headerAt(i)) ++held;
  Serial.printf("[images] '%s': %u slots of %lu B for %ux%u, %u held\n",
                partitionLabel, slotCount, (unsigned long)slotBytes, w, h, held);
  return true;
}

uint8_t imageStoreCapacity() { return slotCount; }

bool imageStoreOccupied(uint8_t slot) { return headerAt(slot) != nullptr; }

const uint16_t *imageStorePixels(uint8_t slot) {
  const ImageSlotHeader *h = headerAt(slot);
  if (!h) return nullptr;
  return (const uint16_t *)((const uint8_t *)h + IMAGE_SLOT_HEADER);
}

bool imageStoreWriteBegin(uint8_t slot, uint16_t w, uint16_t h, uint32_t crc32) {
  if (!part || slot >= slotCount) return false;
  if (w != imgW || h != imgH) {
    Serial.printf("[images] %ux%u is not this board's %ux%u\n", w, h, imgW, imgH);
    return false;
  }
  // Erasing first is what makes an interrupted write cost only this picture:
  // the header goes on last, so until it does the slot reads as empty.
  if (esp_partition_erase_range(part, (size_t)slot * slotBytes, slotBytes) != ESP_OK) {
    Serial.printf("[images] slot %u would not erase\n", slot);
    return false;
  }
  writing = true;
  writeSlot = slot;
  writeAt = 0;
  writeCrc = crc32;
  writeRunning = 0;
  remap();
  return true;
}

bool imageStoreWriteChunk(uint32_t offset, const void *data, uint16_t len) {
  if (!writing || offset != writeAt) return false;
  if (writeAt + len > pixelBytes) return false;
  const size_t at = (size_t)writeSlot * slotBytes + IMAGE_SLOT_HEADER + writeAt;
  if (esp_partition_write(part, at, data, len) != ESP_OK) {
    imageStoreWriteAbort();
    return false;
  }
  writeRunning = crc32Update(writeRunning, (const uint8_t *)data, len);
  writeAt += len;
  return true;
}

bool imageStoreWriteFinish() {
  if (!writing) return false;
  if (writeAt != pixelBytes || writeRunning != writeCrc) {
    Serial.printf("[images] slot %u refused: %lu of %lu bytes, crc %08lX want %08lX\n",
                  writeSlot, (unsigned long)writeAt, (unsigned long)pixelBytes,
                  (unsigned long)writeRunning, (unsigned long)writeCrc);
    imageStoreWriteAbort();
    return false;
  }

  // The header last, and only now: it is what makes the slot readable, so a
  // picture is either wholly there or not there at all.
  ImageSlotHeader h{};
  h.magic = IMAGE_SLOT_MAGIC;
  h.format = IMAGE_SLOT_FORMAT;
  h.w = imgW;
  h.h = imgH;
  h.bytes = pixelBytes;
  h.crc32 = writeCrc;
  h.seq = 0;
  for (uint8_t i = 0; i < slotCount; i++) {
    const ImageSlotHeader *e = headerAt(i);
    if (e && e->seq >= h.seq) h.seq = e->seq + 1;
  }
  const bool ok = esp_partition_write(part, (size_t)writeSlot * slotBytes,
                                      &h, sizeof(h)) == ESP_OK;
  writing = false;
  remap();
  if (ok) Serial.printf("[images] slot %u written, %lu B\n",
                        writeSlot, (unsigned long)pixelBytes);
  return ok;
}

void imageStoreWriteAbort() {
  if (!writing) return;
  writing = false;
  // The slot stays erased. Nothing readable was ever there.
  remap();
}

uint32_t imageStoreWriteOffset() { return writing ? writeAt : 0; }
bool     imageStoreWriteActive() { return writing; }

bool imageStoreErase(uint8_t slot) {
  if (!part || slot >= slotCount || writing) return false;
  const bool ok = esp_partition_erase_range(part, (size_t)slot * slotBytes, slotBytes) == ESP_OK;
  remap();
  return ok;
}
