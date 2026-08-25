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
  // Open the slot that is not running. False if there is no second slot (a
  // single-slot partition table) or the image will not fit the one there is.
  bool begin(uint32_t size, uint32_t crc32);

  // Write bytes at `offset`. They must start exactly at nextOffset(); anything
  // earlier is a retry and is ignored (returns true, writes nothing), anything
  // later fails the session.
  bool write(uint32_t offset, const uint8_t *data, uint16_t len);

  // Verify the whole image against the promised CRC32 and set it to boot.
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

private:
  void *handle_ = nullptr;         // esp_ota_handle_t, kept opaque
  const void *part_ = nullptr;     // const esp_partition_t *
  void failWith(uint8_t e);
};
