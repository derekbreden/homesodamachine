#include "ota_receiver.h"

#include <esp_ota_ops.h>
#include <esp_partition.h>

bool OtaReceiver::slotAvailable() {
  return esp_ota_get_next_update_partition(nullptr) != nullptr;
}

void OtaReceiver::failWith(uint8_t e) {
  if (handle_) {
    esp_ota_abort((esp_ota_handle_t)(uintptr_t)handle_);
    handle_ = nullptr;
  }
  part_ = nullptr;
  state = OTA_STATE_FAILED;
  err = e;
}

bool OtaReceiver::begin(uint32_t size, uint32_t crc32, uint8_t k) {
  abort();
  kind = k;

  const esp_partition_t *target =
      (k == OTA_KIND_ART)
          ? esp_partition_find_first(ESP_PARTITION_TYPE_DATA,
                                     (esp_partition_subtype_t)0x40, "art")
          : esp_ota_get_next_update_partition(nullptr);
  if (!target) {
    state = OTA_STATE_FAILED;
    err = OTA_ERR_NO_SLOT;
    return false;
  }
  if (size == 0 || size > target->size) {
    state = OTA_STATE_FAILED;
    err = OTA_ERR_TOO_BIG;
    return false;
  }

  if (k == OTA_KIND_ART) {
    handle_ = nullptr;
    erasedTo_ = 0;
  } else {
    esp_ota_handle_t h = 0;
    // Sequential writes, not a sized begin. Passing the size makes esp_ota_begin
    // erase the whole extent in one call, which holds interrupts off for well
    // past the interrupt watchdog's window and resets the board (TG1WDT_SYS_RST)
    // before a byte has arrived. This erases a sector at a time, as each write
    // reaches it.
    if (esp_ota_begin(target, OTA_WITH_SEQUENTIAL_WRITES, &h) != ESP_OK) {
      state = OTA_STATE_FAILED;
      err = OTA_ERR_WRITE;
      return false;
    }
    handle_ = (void *)(uintptr_t)h;
  }
  part_ = target;
  expected = size;
  wantCrc = crc32;
  received = 0;
  runCrc = 0;
  state = OTA_STATE_READY;
  err = OTA_ERR_NONE;
  return true;
}

bool OtaReceiver::write(uint32_t offset, const uint8_t *data, uint16_t len) {
  if (!active()) return false;
  if (len == 0) return true;

  // A retry of something already written. The sender did not hear the request
  // that followed it; saying yes and writing nothing is what lets it move on.
  if (offset < received) return true;
  if (offset != received) {
    failWith(OTA_ERR_SEQUENCE);
    return false;
  }
  if (received + len > expected) {
    failWith(OTA_ERR_SEQUENCE);
    return false;
  }

  if (kind == OTA_KIND_ART) {
    // Erase forward only as far as this write reaches. The partition is 4 MB
    // and erasing it in one call would stall the board for seconds before a
    // single byte had arrived.
    const esp_partition_t *part = (const esp_partition_t *)part_;
    const uint32_t needTo = offset + len;
    if (needTo > erasedTo_) {
      const uint32_t blk = 4096;   // one sector: a block erase outlasts the watchdog
      const uint32_t upto = ((needTo + blk - 1) / blk) * blk;
      const uint32_t end = (upto > part->size) ? part->size : upto;
      if (esp_partition_erase_range(part, erasedTo_, end - erasedTo_) != ESP_OK) {
        failWith(OTA_ERR_WRITE);
        return false;
      }
      erasedTo_ = end;
    }
    if (esp_partition_write(part, offset, data, len) != ESP_OK) {
      failWith(OTA_ERR_WRITE);
      return false;
    }
  } else if (esp_ota_write((esp_ota_handle_t)(uintptr_t)handle_, data, len) != ESP_OK) {
    failWith(OTA_ERR_WRITE);
    return false;
  }

  runCrc = uartCrc32Update(runCrc, data, len);
  received += len;
  state = OTA_STATE_WRITING;
  return true;
}

bool OtaReceiver::finish() {
  if (!active()) return false;
  if (received != expected) {
    failWith(OTA_ERR_SEQUENCE);
    return false;
  }
  // The CRC is checked before esp_ota_end, so a bad image is refused without
  // ever having been a candidate to boot.
  if (runCrc != wantCrc) {
    failWith(OTA_ERR_CRC);
    return false;
  }

  // A data partition is written in place; there is no handle to close and no
  // boot partition to move. The CRC above is the whole of its acceptance.
  if (kind == OTA_KIND_ART) {
    part_ = nullptr;
    state = OTA_STATE_DONE;
    err = OTA_ERR_NONE;
    return true;
  }

  esp_ota_handle_t h = (esp_ota_handle_t)(uintptr_t)handle_;
  handle_ = nullptr;
  if (esp_ota_end(h) != ESP_OK) {
    part_ = nullptr;
    state = OTA_STATE_FAILED;
    err = OTA_ERR_VERIFY;
    return false;
  }
  if (esp_ota_set_boot_partition((const esp_partition_t *)part_) != ESP_OK) {
    part_ = nullptr;
    state = OTA_STATE_FAILED;
    err = OTA_ERR_VERIFY;
    return false;
  }

  part_ = nullptr;
  state = OTA_STATE_DONE;
  err = OTA_ERR_NONE;
  return true;
}

void OtaReceiver::abort() {
  if (handle_) {
    esp_ota_abort((esp_ota_handle_t)(uintptr_t)handle_);
    handle_ = nullptr;
  }
  part_ = nullptr;
  state = OTA_STATE_IDLE;
  err = OTA_ERR_NONE;
  expected = received = wantCrc = runCrc = 0;
  erasedTo_ = 0;
  kind = OTA_KIND_APP;
}

void OtaReceiver::fill(OtaStatePayload &out) const {
  out.state = state;
  out.err = err;
  out.received = received;
}
