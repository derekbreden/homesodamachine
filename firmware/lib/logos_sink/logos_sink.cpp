#include "logos_sink.h"

#include <string.h>

#include "image_store.h"

namespace {

uint32_t crc32Update(uint32_t prev, const uint8_t *data, size_t len) {
  uint32_t crc = ~prev;
  for (size_t i = 0; i < len; i++) {
    crc ^= data[i];
    for (uint8_t b = 0; b < 8; b++) crc = (crc & 1) ? (crc >> 1) ^ 0xEDB88320 : crc >> 1;
  }
  return ~crc;
}

uint32_t le32(const uint8_t *p) {
  return (uint32_t)p[0] | ((uint32_t)p[1] << 8) | ((uint32_t)p[2] << 16) |
         ((uint32_t)p[3] << 24);
}

}  // namespace

void LogosSink::failWith(uint8_t e) {
  closeOpen();
  state = OTA_STATE_FAILED;
  err = e;
}

bool LogosSink::begin(uint32_t size, uint32_t crc32) {
  abort();
  if (size <= HEADER_BYTES) { failWith(OTA_ERR_TOO_BIG); return false; }
  expected = size;
  wantCrc = crc32;
  received = 0;
  runCrc = 0;
  state = OTA_STATE_READY;
  err = OTA_ERR_NONE;
  return true;
}

bool LogosSink::readHeader() {
  if (le32(header_) != MAGIC || le32(header_ + 4) != FORMAT) return false;
  faces_ = le32(header_ + 8);
  bundleBytes_ = le32(header_ + 12);
  const uint32_t renditions = le32(header_ + 16);
  if (faces_ != FLAVOR_ART_FACTORY) return false;
  if (renditions != IMAGE_BUNDLE_COUNT) return false;
  if (bundleBytes_ != imageStoreBundleBytes()) return false;
  if (expected != HEADER_BYTES + faces_ * bundleBytes_) return false;
  if (imageStoreCapacity() < FLAVOR_ART_CUSTOM + faces_) return false;
  for (uint32_t i = 0; i < faces_; i++) crc_[i] = le32(header_ + 20 + i * 4);
  return true;
}

bool LogosSink::openFor(uint32_t face) {
  if (!closeOpen()) return false;
  const uint8_t slot = flavorArtFactorySlot((uint8_t)face);
  if (!imageStoreWriteBegin(slot, crc_[face])) return false;
  openSlot_ = (int16_t)slot;
  return true;
}

bool LogosSink::closeOpen() {
  if (openSlot_ < 0) return true;
  openSlot_ = -1;
  return imageStoreWriteFinish();
}

bool LogosSink::write(uint32_t offset, const uint8_t *data, uint16_t len) {
  if (!active()) return false;
  if (offset < received) return true;           // a retry that already landed
  if (offset != received) { failWith(OTA_ERR_SEQUENCE); return false; }
  if (received + len > expected) { failWith(OTA_ERR_TOO_BIG); return false; }
  state = OTA_STATE_WRITING;
  runCrc = crc32Update(runCrc, data, len);

  while (len) {
    if (received < HEADER_BYTES) {
      const uint16_t take = (uint16_t)((HEADER_BYTES - received) < len
                                           ? (HEADER_BYTES - received) : len);
      memcpy(header_ + received, data, take);
      received += take;
      data += take;
      len = (uint16_t)(len - take);
      if (received == HEADER_BYTES && !readHeader()) {
        failWith(OTA_ERR_WRITE);
        return false;
      }
      continue;
    }

    const uint32_t into = received - HEADER_BYTES;
    const uint32_t face = into / bundleBytes_;
    const uint32_t at = into % bundleBytes_;
    if (at == 0 && !openFor(face)) { failWith(OTA_ERR_WRITE); return false; }

    const uint32_t room = bundleBytes_ - at;
    const uint16_t take = (uint16_t)(room < len ? room : len);
    if (!imageStoreWriteChunk(at, data, take)) { failWith(OTA_ERR_WRITE); return false; }
    received += take;
    data += take;
    len = (uint16_t)(len - take);
    if (at + take == bundleBytes_ && !closeOpen()) { failWith(OTA_ERR_WRITE); return false; }
  }
  return true;
}

bool LogosSink::finish() {
  if (state == OTA_STATE_DONE) return true;
  if (!active()) return false;
  if (received != expected) { failWith(OTA_ERR_SEQUENCE); return false; }
  if (!closeOpen()) { failWith(OTA_ERR_WRITE); return false; }
  if (runCrc != wantCrc) { failWith(OTA_ERR_CRC); return false; }
  state = OTA_STATE_DONE;
  return true;
}

void LogosSink::abort() {
  if (openSlot_ >= 0) {
    openSlot_ = -1;
    imageStoreWriteAbort();
  }
  state = OTA_STATE_IDLE;
  err = OTA_ERR_NONE;
  expected = received = wantCrc = runCrc = 0;
  faces_ = bundleBytes_ = 0;
}

void LogosSink::fill(OtaStatePayload &out) const {
  out.state = state;
  out.err = err;
  out.received = received;
}
