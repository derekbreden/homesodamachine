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

// ── A read-back in progress ───────────────────────────────────────────────
// Straight out of mapped flash, a frame at a time, paced by whether the stack
// will take another. Nothing is staged in RAM: what is sent is a pointer into
// the picture itself.
bool     reading = false;
uint8_t  readSlot = 0;
uint8_t  readRend = 0;
uint32_t readAt = 0;
uint32_t readTotal = 0;
uint32_t readSentThisBurst = 0;
uint8_t  readBudget = 0;
uint16_t mtu = 23;

// How many frames one request is answered with, and how many go out per loop
// pass. A notification is queued, not delivered — notify() returns true the
// moment the host stack takes it, and that stack has a handful of buffers
// against a link that carries a handful of packets per connection interval.
// Sending a whole picture as fast as it will be accepted therefore overruns it
// and most of the frames are simply dropped, with nothing anywhere saying so.
//
// So the phone's asking IS the flow control: a request is answered with one
// bounded burst and then silence, and the phone asks again from wherever it
// actually got to. That converges whatever the link loses, where blasting
// converged on nothing at all.
// One frame a pass, which is the only rate this link has been observed to
// carry without losing the front of a burst:
//
//     pix s=1/1 off=456 buf=0 n=228
//
// The first frame the phone ever saw was the third one. Four a pass overran
// the host stack at the start of every burst, the two that were dropped were
// the two the phone needed first, and everything after them was ahead of an
// empty buffer and refused. The loop is the pacing now — a pass is milliseconds
// and a connection interval is fifteen, so this cannot outrun the radio.
//
// A longer burst costs nothing once the rate is right; it is round trips, not
// frames, that the phone waits on.
constexpr uint8_t READ_BURST    = 64;
constexpr uint8_t READ_PER_PASS = 1;

// The most a notification carries, whatever the MTU says. An ATT MTU of 517
// permits 514, and a 514-byte notification is not reliably delivered — it
// leaves the board, notify() reports success, and it never reaches the phone.
// That is invisible from both ends at once, which is the worst shape a bug can
// have here. 244 is the size a BLE link carries without argument.
constexpr uint16_t NOTIFY_CAP = 244;

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
  for (uint8_t i = 0; i < FLAVOR_ART_CUSTOM; i++)
    st.crc[i] = (i < st.slots) ? imageStoreCrc(i) : 0;
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

void bleImageSetMtu(uint16_t m) { mtu = m; }

// One rendition's size, from the table both ends share.
static uint32_t renditionBytes(uint8_t r) {
  if (r >= IMAGE_BUNDLE_COUNT) return 0;
  return (uint32_t)IMAGE_BUNDLE[r].w * IMAGE_BUNDLE[r].h * 2;
}

void bleImageService() {
  if (!reading) return;

  // ATT header, then this protocol's, then the frame's own place in the
  // picture. What is left is pixels — and it is what the MTU actually allows
  // rather than a guess at it: a link that never exchanged one carries twenty
  // bytes, and a fixed fallback larger than that is a frame the phone never
  // sees and a read that never finishes.
  int32_t fits = (int32_t)mtu - 3 - 3 - (int32_t)sizeof(BleImgPix);
  const int32_t capped = (int32_t)NOTIFY_CAP - 3 - 3 - (int32_t)sizeof(BleImgPix);
  if (fits > capped) fits = capped;
  if (fits < 1) { reading = false; return; }
  const uint16_t room = (uint16_t)fits;

  for (uint8_t i = 0; i < READ_PER_PASS && reading; i++) {
    const uint8_t *px = (const uint8_t *)imageStorePixels(readSlot, readRend);
    if (!px) { reading = false; return; }

    uint32_t want = readTotal - readAt;
    if (want > room) want = room;

    uint8_t frame[3 + sizeof(BleImgPix) + 512];
    BleImgPix head{readSlot, readRend, readAt, readTotal};
    memcpy(frame, &head, sizeof(head));
    memcpy(frame + sizeof(head), px + readAt, want);

    // The stack would not take it; the rest keeps until the next pass.
    if (!seams.notify || !seams.notify(BLE_FRAME_IMG_PIX, frame,
                                       (uint16_t)(sizeof(head) + want))) return;

    readAt += want;
    readSentThisBurst += want;

    if (readAt >= readTotal) {
      reading = false;   // the last frame says so by its offset
      if (seams.onRead) seams.onRead(readSlot, readSentThisBurst);
      return;
    }
    if (--readBudget == 0) {
      // The burst is spent. Nothing more goes out until the phone says where
      // it got to, which is the only honest measure of what arrived.
      reading = false;
      if (seams.onRead) seams.onRead(readSlot, readSentThisBurst);
      return;
    }
  }
}

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

    case BLE_FRAME_IMG_READ: {
      if (plen < sizeof(BleImgRead)) return true;
      BleImgRead req;
      memcpy(&req, payload, sizeof(req));
      // Said before anything can refuse it, so "the phone never asked" and
      // "the board would not answer" stop looking identical from outside.
      if (seams.onReadAsked) seams.onReadAsked(req.slot, mtu);
      // A picture being written is not a picture yet.
      if (state == BLE_IMG_TAKING && req.slot == slot) {
        if (seams.onRead) seams.onRead(req.slot, 0);
        return true;
      }
      const uint32_t total = renditionBytes(req.rendition);
      if (!total || !imageStorePixels(req.slot, req.rendition)) {
        // Asked for something this board does not have. Said out loud, because
        // the phone's side of a refusal is silence.
        if (seams.onRead) seams.onRead(req.slot, 0);
        return true;
      }
      readSlot = req.slot;
      readRend = req.rendition;
      readAt = (req.offset < total) ? req.offset : 0;
      readTotal = total;
      readSentThisBurst = 0;
      readBudget = READ_BURST;
      reading = true;   // bleImageService carries it from here
      return true;
    }

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
      if (seams.onErased) seams.onErased(s.slot);
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
      // The phone is done and the faucet has it whole. The enclosure's copy is
      // the machine's own business from here — nobody waits on it.
      if (seams.onStored) seams.onStored(slot);
      return true;
    }

    default:
      return false;
  }
}
