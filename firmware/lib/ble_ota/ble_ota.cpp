#include <Arduino.h>
#include <string.h>

#include "ble_ota.h"
#include "ota_receiver.h"

static BleOtaSeams seam{};

// ── The session ───────────────────────────────────────────────────────────
static uint8_t   target = OTA_TGT_NONE;
static uint32_t  imgSize = 0;
static uint32_t  owedOffset = 0;   // what the phone was last asked for
static uint16_t  owed = 0;         // how much of that it still owes
// What the relay asked for, which is more than one BLE frame carries. This
// board walks it a frame at a time and the relay sees the pieces arrive.
static uint32_t  spanOffset = 0;
static uint32_t  spanRemain = 0;
static uint32_t  dropped = 0;

static OtaReceiver localRx;
static bool      rebootPending = false;
static uint32_t  rebootAtMs = 0;

// One BLE frame's worth, with room for the offset in front of it on the way to
// the link. Nothing larger is ever held.
static uint8_t   relay[4 + BLE_OTA_ASK];

static void askPhone(uint32_t offset, uint16_t len) {
  owedOffset = offset;
  owed = len;
  BleOtaNeed need{offset, len};
  if (seam.notify) seam.notify(BLE_FRAME_OTA_NEED, &need, sizeof(need));
}

static void endSession(uint8_t state, uint8_t err, uint32_t received) {
  OtaStatePayload st{state, err, received};
  if (seam.notify) seam.notify(BLE_FRAME_OTA_END, &st, sizeof(st));
  Serial.printf("BLE:OTA END target=%u state=%u err=%u recv=%lu\n",
                target, state, err, (unsigned long)received);
  target = OTA_TGT_NONE;
  imgSize = 0;
  owed = 0;
  spanRemain = 0;
}

void bleOtaBegin(const BleOtaSeams &seams) { seam = seams; }

void bleOtaOnSrcNeed(uint32_t offset, uint16_t len) {
  if (target == OTA_TGT_NONE || target == seam.self) return;
  spanOffset = offset;
  spanRemain = len;
  askPhone(spanOffset, (uint16_t)(spanRemain < BLE_OTA_ASK ? spanRemain : BLE_OTA_ASK));
}

void bleOtaOnSrcEnd(const OtaStatePayload &state) {
  if (target == OTA_TGT_NONE || target == seam.self) return;
  endSession(state.state, state.err, state.received);
}

static void handleBegin(const uint8_t *payload, uint16_t plen) {
  if (plen < sizeof(BleOtaBegin)) return;
  BleOtaBegin b;
  memcpy(&b, payload, sizeof(b));

  if (target != OTA_TGT_NONE) {
    // A repeat of the session already running is the phone's retry.
    if (b.target == target && b.size == imgSize) return;
    endSession(OTA_STATE_FAILED, OTA_ERR_NONE, 0);
    return;
  }
  if (b.size == 0 || b.target == OTA_TGT_NONE) return;

  target = b.target;
  imgSize = b.size;
  Serial.printf("BLE:OTA BEGIN target=%u size=%lu crc=%08lX kind=%u\n",
                b.target, (unsigned long)b.size, (unsigned long)b.crc32, b.kind);

  if (b.target == seam.self) {
    if (seam.onLocalProgress) seam.onLocalProgress(true, 0);
    if (!localRx.begin(b.size, b.crc32, b.kind)) {
      if (seam.onLocalProgress) seam.onLocalProgress(false, 0);
      endSession(localRx.state, localRx.err, 0);
      return;
    }
    askPhone(0, (uint16_t)(b.size < BLE_OTA_ASK ? b.size : BLE_OTA_ASK));
    return;
  }

  OtaSrcBeginPayload src{b.size, b.crc32,
                         (uint16_t)(b.target == OTA_TGT_ENCLOSURE ? OTA_CHUNK_J9 : OTA_CHUNK_J3),
                         b.kind, b.target};
  if (seam.sendSrc) seam.sendSrc(MSG_OTA_SRC_BEGIN, &src, sizeof(src));
}

static void handleData(const uint8_t *payload, uint16_t plen) {
  if (target == OTA_TGT_NONE || plen < 4 || owed == 0) return;
  uint32_t offset;
  memcpy(&offset, payload, 4);
  const uint16_t len = (uint16_t)(plen - 4);
  if (offset != owedOffset || len > owed) return;

  if (target == seam.self) {
    if (!localRx.write(offset, payload + 4, len)) {
      if (seam.onLocalProgress) seam.onLocalProgress(false, 0);
      endSession(localRx.state, localRx.err, localRx.received);
      return;
    }
    if (localRx.nextOffset() < localRx.expected) {
      const uint32_t remain = localRx.expected - localRx.nextOffset();
      if (seam.onLocalProgress)
        seam.onLocalProgress(true, (uint8_t)((uint64_t)localRx.nextOffset() * 100 / localRx.expected));
      askPhone(localRx.nextOffset(), (uint16_t)(remain < BLE_OTA_ASK ? remain : BLE_OTA_ASK));
      return;
    }
    const bool ok = localRx.finish();
    if (seam.onLocalProgress) seam.onLocalProgress(ok, ok ? 100 : 0);
    endSession(localRx.state, localRx.err, localRx.received);
    if (ok) { rebootPending = true; rebootAtMs = millis() + 600; }
    return;
  }

  // Straight onto the link, unbuffered. The relay accumulates it into the span
  // it asked for and forwards that.
  memcpy(relay, &offset, 4);
  memcpy(relay + 4, payload + 4, len);
  if (!seam.sendSrc || !seam.sendSrc(MSG_OTA_SRC_DATA, relay, (uint16_t)(4 + len))) {
    ++dropped;
    return;   // the relay re-asks for this offset
  }
  owed -= len;
  spanOffset += len;
  spanRemain -= len;
  // The relay only speaks again once its whole span is in, so the rest of it is
  // asked for from here.
  if (spanRemain)
    askPhone(spanOffset, (uint16_t)(spanRemain < BLE_OTA_ASK ? spanRemain : BLE_OTA_ASK));
  else owedOffset += len;
}

bool bleOtaHandleFrame(uint8_t type, const uint8_t *payload, uint16_t plen) {
  switch (type) {
    case BLE_FRAME_OTA_BEGIN: handleBegin(payload, plen); return true;
    case BLE_FRAME_OTA_DATA:  handleData(payload, plen);  return true;
    default: return false;
  }
}

void bleOtaDisconnected() {
  if (target == OTA_TGT_NONE) return;
  if (target == seam.self) {
    localRx.abort();
    if (seam.onLocalProgress) seam.onLocalProgress(false, 0);
  } else if (seam.sendSrc) {
    seam.sendSrc(MSG_OTA_ABORT, nullptr, 0);
  }
  target = OTA_TGT_NONE;
  owed = 0;
  spanRemain = 0;
}

void bleOtaService() {
  if (rebootPending && (int32_t)(millis() - rebootAtMs) >= 0) {
    Serial.println("BLE:OTA rebooting into the new image");
    delay(50);
    ESP.restart();
  }
}

uint8_t  bleOtaTarget()  { return target; }
uint16_t bleOtaOwed()    { return owed; }
uint32_t bleOtaDropped() { return dropped; }
