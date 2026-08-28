#include "ble_image.h"

#include <Arduino.h>
#include <string.h>

#include "image_store.h"

namespace {

BleImageSeams seams{};

uint8_t  state = BLE_IMG_IDLE;
uint8_t  err = BLE_IMG_ERR_NONE;
uint8_t  slot = 0;
uint32_t want = 0;
uint32_t nextAckAt = 0;

// Only the low FLAVOR_ART_CUSTOM slots are the user's. The partition holds far
// more, and the rest stay unused rather than becoming a capacity nobody asked
// for and the picker cannot show.
uint8_t customSlots() {
  const uint8_t held = imageStoreCapacity();
  return held < FLAVOR_ART_CUSTOM ? held : FLAVOR_ART_CUSTOM;
}

void sendAck() {
  BleImgAck ack{slot, state, err, imageStoreWriteActive() ? imageStoreWriteOffset() : 0};
  if (state == BLE_IMG_DONE) ack.have = want;
  if (seams.notify) seams.notify(BLE_FRAME_IMG_ACK, &ack, sizeof(ack));
}

void sendState() {
  BleImgState st{};
  st.slots = customSlots();
  st.renditions = IMAGE_BUNDLE_COUNT;
  st.bundleBytes = imageBundleBytes();
  st.artFirst = FLAVOR_ART_FACTORY;
  for (uint8_t i = 0; i < st.slots; i++) {
    if (imageStoreOccupied(i)) { st.occupancy |= (uint8_t)(1u << i); ++st.held; }
  }
  if (seams.notify) seams.notify(BLE_FRAME_IMG_STATE, &st, sizeof(st));
}

void fail(uint8_t why) {
  imageStoreWriteAbort();
  state = BLE_IMG_FAILED;
  err = why;
  if (seams.onProgress) seams.onProgress(false, 0);
  if (seams.onStoreMoved) seams.onStoreMoved();
  sendAck();
}

}  // namespace

void bleImageBegin(const BleImageSeams &s) { seams = s; }

void bleImagePublishArt() {
  if (!seams.notify || !seams.readArt) return;
  BleArtState st{};
  seams.readArt(st.art);
  st.factory = FLAVOR_ART_FACTORY;
  st.custom = FLAVOR_ART_CUSTOM;
  seams.notify(BLE_FRAME_ART_STATE, &st, sizeof(st));
}

bool bleImageBusy() { return state == BLE_IMG_TAKING; }

void bleImageDisconnected() {
  if (state != BLE_IMG_TAKING) return;
  // The slot was erased when the transfer opened and never got its header, so
  // it already reads as empty. Nothing to undo.
  imageStoreWriteAbort();
  state = BLE_IMG_IDLE;
  if (seams.onProgress) seams.onProgress(false, 0);
  if (seams.onStoreMoved) seams.onStoreMoved();
}

bool bleImageHandleFrame(uint8_t type, const uint8_t *payload, uint16_t plen) {
  switch (type) {
    case BLE_FRAME_IMG_QUERY:
      sendState();
      return true;

    case BLE_FRAME_ART_QUERY:
      bleImagePublishArt();
      return true;

    case BLE_FRAME_ART_SET: {
      if (plen < sizeof(BleArtSet)) return true;
      BleArtSet req;
      memcpy(&req, payload, sizeof(req));
      if (req.channel < 2 && req.art < FLAVOR_ART_COUNT && seams.setArt)
        seams.setArt(req.channel, req.art);
      // The answer is whatever the main board settles on, published when it
      // revises — not an echo of what was asked for.
      return true;
    }

    case BLE_FRAME_IMG_ERASE: {
      if (plen < sizeof(BleImgSlot)) return true;
      BleImgSlot s;
      memcpy(&s, payload, sizeof(s));
      if (state == BLE_IMG_TAKING) { err = BLE_IMG_ERR_BUSY; sendAck(); return true; }
      if (s.slot >= customSlots()) { slot = s.slot; err = BLE_IMG_ERR_SLOT; sendAck(); return true; }
      imageStoreErase(s.slot);
      if (seams.onStoreMoved) seams.onStoreMoved();
      sendState();
      return true;
    }

    case BLE_FRAME_IMG_BEGIN: {
      if (plen < sizeof(BleImgBegin)) return true;
      BleImgBegin b;
      memcpy(&b, payload, sizeof(b));
      slot = b.slot;
      err = BLE_IMG_ERR_NONE;

      if (state == BLE_IMG_TAKING) { err = BLE_IMG_ERR_BUSY; sendAck(); return true; }
      if (b.slot >= customSlots()) { err = BLE_IMG_ERR_SLOT; state = BLE_IMG_FAILED; sendAck(); return true; }
      if (b.bytes != imageStoreBundleBytes()) { err = BLE_IMG_ERR_SIZE; state = BLE_IMG_FAILED; sendAck(); return true; }

      if (!imageStoreWriteBegin(b.slot, b.crc32)) { err = BLE_IMG_ERR_WRITE; state = BLE_IMG_FAILED; sendAck(); return true; }
      want = b.bytes;
      nextAckAt = BLE_IMG_ACK_EVERY;
      state = BLE_IMG_TAKING;
      if (seams.onProgress) seams.onProgress(true, 0);
      if (seams.onStoreMoved) seams.onStoreMoved();
      sendAck();   // "sending from zero is right"
      return true;
    }

    case BLE_FRAME_IMG_DATA: {
      if (state != BLE_IMG_TAKING || plen < 4) return true;
      uint32_t offset;
      memcpy(&offset, payload, 4);
      const uint16_t bytes = (uint16_t)(plen - 4);

      // Anything but the offset being waited for is a frame that arrived while
      // this board was elsewhere. Saying where it actually is turns the whole
      // recovery into one number.
      if (offset != imageStoreWriteOffset()) { sendAck(); return true; }

      if (!imageStoreWriteChunk(offset, payload + 4, bytes)) { fail(BLE_IMG_ERR_WRITE); return true; }

      const uint32_t at = imageStoreWriteOffset();
      if (at >= nextAckAt || at >= want) {
        nextAckAt = at + BLE_IMG_ACK_EVERY;
        if (seams.onProgress) seams.onProgress(true, (uint8_t)((uint64_t)at * 100 / want));
        sendAck();
      }
      return true;
    }

    case BLE_FRAME_IMG_ABORT: {
      if (state != BLE_IMG_TAKING) return true;
      imageStoreWriteAbort();
      state = BLE_IMG_IDLE;
      err = BLE_IMG_ERR_NONE;
      if (seams.onProgress) seams.onProgress(false, 0);
      if (seams.onStoreMoved) seams.onStoreMoved();
      sendAck();
      sendState();
      return true;
    }

    case BLE_FRAME_IMG_END: {
      if (state != BLE_IMG_TAKING) return true;
      if (!imageStoreWriteFinish()) { fail(BLE_IMG_ERR_CRC); return true; }
      state = BLE_IMG_DONE;
      err = BLE_IMG_ERR_NONE;
      if (seams.onProgress) seams.onProgress(false, 100);
      if (seams.onStoreMoved) seams.onStoreMoved();
      sendAck();
      sendState();
      return true;
    }

    default:
      return false;
  }
}
