#pragma once

#include <stdint.h>
#include <stddef.h>
#include "proto_msg.h"

// ════════════════════════════════════════════════════════════
//  Taking a new image over the link
// ════════════════════════════════════════════════════════════
//
// One receiver, the same on every board that can be updated: the main board's
// WROOM and both displays. What differs between them is only which link the
// bytes arrive on, so none of that is in here.
//
// The receiver pulls. `nextOffset()` is the only offset it will accept, and
// whoever holds the image answers that and nothing else. A duplicate that
// arrives after a retry is recognised by its offset and dropped rather than
// appended, which is the whole reason OTA_DATA carries one.
//
// Nothing is committed part-way. The image is written into the OTA slot that
// is not running; only when the last byte is in and the CRC32 over the whole
// of it matches what BEGIN promised does the boot partition move. A session
// that stalls, fails, or is abandoned leaves the board running what it booted.
struct OtaReceiver {
  // Open the destination. OTA_KIND_APP takes the slot that is not running —
  // false if there is no second slot, or the image will not fit it.
  // OTA_KIND_ART takes the named data partition, erased as the write crosses
  // into each block rather than all at once, so nothing waits on a 4 MB erase.
  bool begin(uint32_t size, uint32_t crc32, uint8_t kind = OTA_KIND_APP);

  // Write bytes at `offset`. They must start exactly at nextOffset(); anything
  // earlier is a retry and is ignored (returns true, writes nothing), anything
  // later fails the session.
  bool write(uint32_t offset, const uint8_t *data, uint16_t len);

  // Verify what arrived against the promised CRC32. For firmware that is what
  // sets it to boot; for a data partition the bytes are already in place and
  // this is the check that says they are the right ones.
  bool finish();

  void abort();

  uint32_t nextOffset() const { return received; }
  bool active() const { return state == OTA_STATE_READY || state == OTA_STATE_WRITING; }
  bool done() const { return state == OTA_STATE_DONE; }
  void fill(OtaStatePayload &out) const;

  // Whether this board's partition table can take an update at all. Cheap, and
  // worth asking before a table is trusted: a single-slot board answers false.
  static bool slotAvailable();

  uint8_t  state = OTA_STATE_IDLE;
  uint8_t  err = OTA_ERR_NONE;
  uint32_t expected = 0;   // image size BEGIN promised
  uint32_t received = 0;   // bytes written so far
  uint32_t wantCrc = 0;
  uint32_t runCrc = 0;     // CRC32 over what has been written
  uint8_t  kind = OTA_KIND_APP;

private:
  void *handle_ = nullptr;         // esp_ota_handle_t, kept opaque
  const void *part_ = nullptr;     // const esp_partition_t *
  uint32_t erasedTo_ = 0;          // ART: how far the erase has reached
  void failWith(uint8_t e);
};
