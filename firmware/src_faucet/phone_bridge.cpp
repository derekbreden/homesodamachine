#include <Arduino.h>
#include <string.h>

#include "phone_bridge.h"
#include "base_link.h"
#include "ble_link.h"
#include "j9_query_policy.h"

namespace {

// A conditional name write is the largest request: the stamped setting header
// and up to twenty UTF-8 bytes. The existing request/response prefixes stay put.
constexpr uint8_t  kBodyMax  = SETTING_SET_HEADER_SIZE + SETTING_VALUE_MAX;
constexpr uint8_t  kRequests = 6;
constexpr uint32_t kQueuedMs = 1000;   // J3 would not take it in this long
constexpr uint32_t kAnswerMs = 2000;   // the main board answers in milliseconds
// A Prime waits on the enclosure's next poll, and the main board gives up on
// that after kEnclosureReplyWaitMs. Its answer, either way, is owed after that.
constexpr uint32_t kPrimeOpenMs = j9_query_policy::kEnclosureReplyWaitMs + 1500;

struct Request {
  bool     used;
  bool     sent;       // on J3, waiting for its answer
  uint8_t  wireId;     // this board's id for it on J3
  uint8_t  phoneId;    // the phone's own
  uint16_t link;
  uint32_t gen;
  uint32_t atMs;       // when it arrived, then when J3 took it
  uint32_t order;
  uint8_t  len;        // the header and the body, as they go onto J3
  uint8_t  frame[sizeof(BridgeHeader) + kBodyMax];
};

Request  requests[kRequests];
uint8_t  nextWireId = 1;
uint32_t arrivals = 0;

// What was last passed on of the state this board hears for its own glass.
FlavorStatePayload lastFlavor{0xFF, 0, 0};
uint32_t lastPrimeRevision = 0;
uint8_t  lastPrimePhase = 0xFF;

bool linkUp() {
  BaseLinkStatus st;
  baseLinkReadStatus(st);
  return st.connected;
}

void refuse(const Request &r, uint8_t why) {
  bleLinkDeliver(r.link, r.gen, r.phoneId, why, nullptr, 0);
}

uint8_t freshWireId() {
  for (;;) {
    const uint8_t id = nextWireId++;
    if (nextWireId == 0) nextWireId = 1;
    bool taken = false;
    for (const Request &r : requests)
      if (r.used && r.wireId == id) taken = true;
    if (!taken) return id;
  }
}

// Oldest first, for as long as J3 takes them.
void sendQueued() {
  for (;;) {
    Request *next = nullptr;
    for (Request &r : requests)
      if (r.used && !r.sent && (!next || r.order < next->order)) next = &r;
    if (!next || !baseLinkSendBridge(next->frame, next->len)) return;
    next->sent = true;
    next->atMs = millis();
  }
}

}  // namespace

void phoneBridgeRequest(uint16_t link, uint32_t gen, const uint8_t *frame, uint16_t len) {
  if (len < sizeof(BridgeHeader)) return;
  const uint8_t phoneId = frame[0];
  if (len > sizeof(BridgeHeader) + kBodyMax) {
    bleLinkDeliver(link, gen, phoneId, BRIDGE_ERR_REFUSED, nullptr, 0);
    return;
  }
  if (!linkUp()) {
    bleLinkDeliver(link, gen, phoneId, BRIDGE_ERR_LINK_DOWN, nullptr, 0);
    return;
  }
  Request *slot = nullptr;
  for (Request &r : requests)
    if (!r.used) { slot = &r; break; }
  if (!slot) {
    bleLinkDeliver(link, gen, phoneId, BRIDGE_ERR_BUSY, nullptr, 0);
    return;
  }
  const uint8_t wireId = freshWireId();
  *slot = Request{true, false, wireId, phoneId, link, gen, millis(), ++arrivals, (uint8_t)len, {}};
  memcpy(slot->frame, frame, len);
  slot->frame[0] = wireId;
  sendQueued();
}

void phoneBridgeOnAnswer(const uint8_t *payload, uint16_t len) {
  if (len < sizeof(BridgeHeader)) return;
  const uint8_t wireId = payload[0];
  const uint8_t type = payload[1];
  const uint8_t *body = payload + sizeof(BridgeHeader);
  const uint16_t blen = len - sizeof(BridgeHeader);
  if (wireId == 0) {
    if (bleLinkConnected()) bleLinkDeliver(BLE_LINK_EVERY, 0, 0, type, body, blen);
    return;
  }
  // An answer that outlived its request has nobody waiting for it.
  for (Request &r : requests) {
    if (!r.used || !r.sent || r.wireId != wireId) continue;
    bleLinkDeliver(r.link, r.gen, r.phoneId, type, body, blen);
    r.used = false;
    return;
  }
}

void phoneBridgeOnState(uint8_t type, const void *data, uint16_t len) {
  // Taken in only while a phone is on.
  if (!bleLinkConnected()) return;

  if (type == MSG_SETTING_STATE) {
    bleLinkDeliver(BLE_LINK_EVERY, 0, 0, type, data, len);
    return;
  }

  if (type == MSG_RESP_FLAVOR_STATE && len >= sizeof(FlavorStatePayload)) {
    FlavorStatePayload st;
    memcpy(&st, data, sizeof(st));
    if (st.flavor == lastFlavor.flavor && st.flags == lastFlavor.flags) return;
    lastFlavor = st;
    st.token = 0;   // this board's own request's, not any phone's
    bleLinkDeliver(BLE_LINK_EVERY, 0, 0, type, &st, sizeof(st));
    return;
  }

  // The session's revision moves on every change to it; its heartbeats carry a
  // running hold's elapsed time, which a phone counts for itself.
  if (type == MSG_RESP_PRIME_SESSION && len >= sizeof(PrimeSessionStatePayload)) {
    PrimeSessionStatePayload st;
    memcpy(&st, data, sizeof(st));
    if (st.revision == lastPrimeRevision && st.phase == lastPrimePhase) return;
    lastPrimeRevision = st.revision;
    lastPrimePhase = st.phase;
    bleLinkDeliver(BLE_LINK_EVERY, 0, 0, type, &st, sizeof(st));
  }
}

void phoneBridgeOnNoBridge() {
  for (Request &r : requests) {
    if (!r.used || !r.sent) continue;
    refuse(r, BRIDGE_ERR_NO_BRIDGE);
    r.used = false;
  }
}

void phoneBridgeService() {
  const uint32_t now = millis();
  const bool up = linkUp();
  for (Request &r : requests) {
    if (!r.used) continue;
    if (!r.sent) {
      if (!up) {
        refuse(r, BRIDGE_ERR_LINK_DOWN);
        r.used = false;
      } else if (now - r.atMs >= kQueuedMs) {
        refuse(r, BRIDGE_ERR_BUSY);
        r.used = false;
      }
      continue;
    }
    // Asked and unanswered: whether the main board acted is unknown, so the
    // phone is told exactly that, and finds out with a query.
    const uint32_t wait = r.frame[1] == MSG_PRIME_OPEN ? kPrimeOpenMs : kAnswerMs;
    if (now - r.atMs >= wait) {
      refuse(r, BRIDGE_ERR_NO_ANSWER);
      r.used = false;
    }
  }
  if (up) sendQueued();
}
