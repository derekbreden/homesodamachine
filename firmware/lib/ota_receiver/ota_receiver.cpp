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

bool OtaReceiver::begin(uint32_t size, uint32_t crc32) {
  abort();

  const esp_partition_t *target = esp_ota_get_next_update_partition(nullptr);
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

  esp_ota_handle_t h = 0;
  // The size is known, so the slot is erased for exactly what is coming rather
  // than in full: on a 7 MB slot holding a 5.6 MB image that is a second and a
  // half of erase nobody waits through.
  if (esp_ota_begin(target, size, &h) != ESP_OK) {
    state = OTA_STATE_FAILED;
    err = OTA_ERR_WRITE;
    return false;
  }

  handle_ = (void *)(uintptr_t)h;
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

  if (esp_ota_write((esp_ota_handle_t)(uintptr_t)handle_, data, len) != ESP_OK) {
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
}

void OtaReceiver::fill(OtaStatePayload &out) const {
  out.state = state;
  out.err = err;
  out.received = received;
}
