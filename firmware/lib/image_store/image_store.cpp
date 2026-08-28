#include "image_store.h"

#include <Arduino.h>
#include <esp_partition.h>
#include <string.h>

namespace {

const esp_partition_t *part = nullptr;
const void            *mapped = nullptr;
esp_partition_mmap_handle_t mapHandle = 0;

ImageSize wantSizes[IMAGE_MAX_SIZES];
uint8_t   wantCount = 0;
uint32_t  bundleBytes = 0;
uint32_t  slotBytes = 0;
uint8_t   slotCount = 0;

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

// The map is showing flash that a write just changed underneath it, so it is
// dropped around one and taken again after.
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
  if (h->count != wantCount || h->bytes != bundleBytes) return nullptr;
  // A bundle laid out for a different board is not this board's picture.
  for (uint8_t i = 0; i < wantCount; i++)
    if (h->sizes[i].w != wantSizes[i].w || h->sizes[i].h != wantSizes[i].h) return nullptr;
  return h;
}

}  // namespace

bool imageStoreBegin(const char *partitionLabel, const ImageSize *sizes, uint8_t count) {
  if (!sizes || !count || count > IMAGE_MAX_SIZES) return false;

  part = esp_partition_find_first(ESP_PARTITION_TYPE_DATA,
                                  ESP_PARTITION_SUBTYPE_ANY, partitionLabel);
  if (!part) {
    Serial.printf("[images] no partition '%s'\n", partitionLabel);
    return false;
  }

  wantCount = count;
  bundleBytes = 0;
  for (uint8_t i = 0; i < count; i++) {
    wantSizes[i].w = sizes[i].w;
    wantSizes[i].h = sizes[i].h;
    wantSizes[i].offset = bundleBytes;
    bundleBytes += (uint32_t)sizes[i].w * sizes[i].h * 2;
  }

  slotBytes = ((IMAGE_SLOT_PIXELS_AT + bundleBytes) + ERASE - 1) / ERASE * ERASE;
  const uint32_t fits = part->size / slotBytes;
  slotCount = (uint8_t)(fits > 255 ? 255 : fits);

  if (!slotCount) {
    Serial.printf("[images] '%s' is %lu B, one bundle needs %lu\n",
                  partitionLabel, (unsigned long)part->size, (unsigned long)slotBytes);
    part = nullptr;
    return false;
  }
  if (!remap()) {
    Serial.println("[images] partition would not map");
    part = nullptr;
    return false;
  }

  Serial.printf("[images] '%s': %u slots of %lu B, bundle %lu B in %u sizes, %u held\n",
                partitionLabel, slotCount, (unsigned long)slotBytes,
                (unsigned long)bundleBytes, wantCount, imageStoreHeld());
  return true;
}

uint8_t imageStoreCapacity() { return slotCount; }
bool    imageStoreOccupied(uint8_t slot) { return headerAt(slot) != nullptr; }

uint8_t imageStoreHeld() {
  uint8_t n = 0;
  for (uint8_t i = 0; i < slotCount; i++) if (headerAt(i)) ++n;
  return n;
}

uint32_t imageStoreBundleBytes() { return bundleBytes; }

const uint16_t *imageStorePixels(uint8_t slot, uint8_t size) {
  const ImageSlotHeader *h = headerAt(slot);
  if (!h || size >= h->count) return nullptr;
  const uint8_t *pixels = (const uint8_t *)h + IMAGE_SLOT_PIXELS_AT;
  return (const uint16_t *)(pixels + h->sizes[size].offset);
}

bool imageStoreWriteBegin(uint8_t slot, uint32_t crc32) {
  if (!part || slot >= slotCount || writing) return false;
  // Erased first, so that until the header lands at the end this slot reads as
  // empty rather than as whatever it used to hold.
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
  if (!writing || offset != writeAt || writeAt + len > bundleBytes) return false;
  const size_t at = (size_t)writeSlot * slotBytes + IMAGE_SLOT_PIXELS_AT + writeAt;
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
  if (writeAt != bundleBytes || writeRunning != writeCrc) {
    Serial.printf("[images] slot %u refused: %lu of %lu B, crc %08lX want %08lX\n",
                  writeSlot, (unsigned long)writeAt, (unsigned long)bundleBytes,
                  (unsigned long)writeRunning, (unsigned long)writeCrc);
    imageStoreWriteAbort();
    return false;
  }

  ImageSlotHeader h{};
  h.magic = IMAGE_SLOT_MAGIC;
  h.format = IMAGE_SLOT_FORMAT;
  h.bytes = bundleBytes;
  h.crc32 = writeCrc;
  h.count = wantCount;
  for (uint8_t i = 0; i < wantCount; i++) h.sizes[i] = wantSizes[i];
  h.seq = 0;
  for (uint8_t i = 0; i < slotCount; i++) {
    const ImageSlotHeader *e = headerAt(i);
    if (e && e->seq >= h.seq) h.seq = e->seq + 1;
  }

  // Last, and only now: the header is what makes the slot count.
  const bool ok = esp_partition_write(part, (size_t)writeSlot * slotBytes,
                                      &h, sizeof(h)) == ESP_OK;
  writing = false;
  if (!remap()) Serial.println("[images] REMAP FAILED after write");
  if (ok) Serial.printf("[images] slot %u written, %lu B\n",
                        writeSlot, (unsigned long)bundleBytes);
  return ok;
}

void imageStoreWriteAbort() {
  if (!writing) return;
  writing = false;
  remap();   // the slot stays erased; nothing readable was ever there
}

uint32_t imageStoreWriteOffset() { return writing ? writeAt : 0; }
bool     imageStoreWriteActive() { return writing; }

void imageStoreDiag(char *out, unsigned n) {
  if (!part) { snprintf(out, n, "no partition"); return; }
  const ImageSlotHeader *raw =
      mapped ? (const ImageSlotHeader *)mapped : nullptr;
  snprintf(out, n, "map=%d n=%u m=%08lX f=%lu c=%u b=%lu",
           mapped ? 1 : 0, slotCount,
           raw ? (unsigned long)raw->magic : 0UL,
           raw ? (unsigned long)raw->format : 0UL,
           raw ? raw->count : 0,
           raw ? (unsigned long)raw->bytes : 0UL);
}

bool imageStoreErase(uint8_t slot) {
  if (!part || slot >= slotCount || writing) return false;
  const bool ok = esp_partition_erase_range(part, (size_t)slot * slotBytes, slotBytes) == ESP_OK;
  remap();
  return ok;
}
