#pragma once

#include <stdint.h>
#include <stddef.h>
#include "proto_msg.h"

// ════════════════════════════════════════════════════════════
//  The factory logos arriving over the link
// ════════════════════════════════════════════════════════════
//
// `OTA_KIND_LOGOS` streams the blob `tools/make_logos.py` writes: a 64-byte
// header, then one bundle per face in the rendition order `IMAGE_BUNDLE` names.
// Each bundle goes into its own store slot through `imageStoreWriteBegin` /
// `Chunk` / `Finish`, so one slot is erased at a time and the slots holding a
// user's own pictures are never touched.
//
// The bundle crc32s are in the header because a slot is told its crc before its
// bytes. A blob whose bundle size or face count is not what this board's store
// was opened for is refused at BEGIN.
//
// Bytes arrive in order and only at `nextOffset()`, the same contract
// `OtaReceiver` holds.
struct LogosSink {
  static constexpr uint32_t HEADER_BYTES = 64;
  static constexpr uint32_t MAGIC = 0x53474F4C;   // 'LOGS'
  static constexpr uint32_t FORMAT = 1;

  bool begin(uint32_t size, uint32_t crc32);
  bool write(uint32_t offset, const uint8_t *data, uint16_t len);
  bool finish();
  void abort();

  uint32_t nextOffset() const { return received; }
  bool active() const { return state == OTA_STATE_READY || state == OTA_STATE_WRITING; }
  bool done() const { return state == OTA_STATE_DONE; }
  void fill(OtaStatePayload &out) const;

  uint8_t  state = OTA_STATE_IDLE;
  uint8_t  err = OTA_ERR_NONE;
  uint32_t expected = 0;
  uint32_t received = 0;
  uint32_t wantCrc = 0;
  uint32_t runCrc = 0;

 private:
  uint8_t  header_[HEADER_BYTES];
  uint32_t faces_ = 0;
  uint32_t bundleBytes_ = 0;
  uint32_t crc_[FLAVOR_ART_FACTORY] = {};
  int16_t  openSlot_ = -1;          // the store slot a write is open on, or -1

  bool readHeader();
  bool openFor(uint32_t face);
  bool closeOpen();
  void failWith(uint8_t e);
};
