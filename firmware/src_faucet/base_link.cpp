#include <Arduino.h>
#include <driver/gpio.h>
#include <esp_system.h>

#include "base_link.h"
#include "flavor_link_policy.h"
#include "proto_link.h"
#include "proto_msg.h"

namespace {

constexpr int kBaseRxPin = 44;  // P1 ESP_RXD, crossed from controller J3 IO33 TX
constexpr int kBaseTxPin = 43;  // P1 ESP_TXD, crossed to controller J3 IO35 RX
constexpr long kBaseBaud = 115200;
constexpr uint8_t kQueueDepth = 8;
constexpr uint32_t kResponseTimeoutMs = 750;
constexpr uint32_t kAudibleFreshMs = 300;

struct Intent {
  uint8_t type;
  FlavorRequestPayload request;
  uint32_t queuedAtMs;
  uint32_t firstSentAtMs;
  uint32_t lastSentAtMs;
  bool sent;
};

ProtoLink base;
BaseFlavorHandler flavorHandler = nullptr;
Intent queue[kQueueDepth];
uint8_t queueHead = 0;
uint8_t queueTail = 0;
uint8_t queueCount = 0;
uint8_t desiredFlavor = 0;
uint8_t controllerFlavor = 0;
bool synchronized = false;
bool offlineSelection = false;
bool awaitingPersistence = false;
bool controllerPersisted = false;
bool controllerPersistError = false;
uint32_t tokenState = 1;
uint32_t framesRx = 0;
uint32_t framesTx = 0;
uint32_t retries = 0;
uint32_t queueDrops = 0;
uint32_t staleResponses = 0;
uint32_t lastAckMs = 0;
uint32_t maxAckMs = 0;
uint32_t maxServiceUs = 0;
uint32_t connectionGeneration = 0;

uint32_t nextToken() {
  tokenState += 0x9E3779B9u;
  if (tokenState == 0) ++tokenState;
  return tokenState;
}

void clearQueue() {
  queueHead = queueTail = queueCount = 0;
}

void enqueue(uint8_t type, uint8_t flavor, bool audible) {
  if (queueCount >= kQueueDepth) {
    // Preserve the final absolute state. Only the newest intermediate event
    // (and therefore at most one delayed tick) is coalesced under abuse.
    const uint8_t newest = static_cast<uint8_t>((queueTail + kQueueDepth - 1) % kQueueDepth);
    Intent &intent = queue[newest];
    intent.type = type;
    intent.request = {flavor,
                      static_cast<uint8_t>(audible ? FLAVOR_REQ_F_AUDIBLE : 0),
                      nextToken()};
    intent.queuedAtMs = millis();
    intent.firstSentAtMs = intent.lastSentAtMs = 0;
    intent.sent = false;
    ++queueDrops;
    return;
  }

  Intent &intent = queue[queueTail];
  intent.type = type;
  intent.request = {flavor,
                    static_cast<uint8_t>(audible ? FLAVOR_REQ_F_AUDIBLE : 0),
                    nextToken()};
  intent.queuedAtMs = millis();
  intent.firstSentAtMs = intent.lastSentAtMs = 0;
  intent.sent = false;
  queueTail = static_cast<uint8_t>((queueTail + 1) % kQueueDepth);
  ++queueCount;
}

void popQueue() {
  if (queueCount == 0) return;
  queueHead = static_cast<uint8_t>((queueHead + 1) % kQueueDepth);
  --queueCount;
}

bool queueHasSelection() {
  for (uint8_t i = 0; i < queueCount; ++i) {
    const uint8_t slot = static_cast<uint8_t>((queueHead + i) % kQueueDepth);
    if (queue[slot].type == MSG_FLAVOR_SELECT) return true;
  }
  return false;
}

void sendHead() {
  if (queueCount == 0 || !base.isConnected()) return;
  Intent &intent = queue[queueHead];
  const uint32_t now = millis();
  if (intent.sent && static_cast<uint32_t>(now - intent.lastSentAtMs) < kResponseTimeoutMs)
    return;

  if ((intent.request.flags & FLAVOR_REQ_F_AUDIBLE) != 0 &&
      static_cast<uint32_t>(now - intent.queuedAtMs) > kAudibleFreshMs) {
    intent.request.flags &= static_cast<uint8_t>(~FLAVOR_REQ_F_AUDIBLE);
  }

  if (base.trySend(intent.type, &intent.request, sizeof(intent.request)) < 0) return;
  ++framesTx;
  if (intent.sent) ++retries;
  else             intent.firstSentAtMs = now;
  intent.lastSentAtMs = now;
  intent.sent = true;
}

void applyAuthoritative(uint8_t flavor) {
  controllerFlavor = flavor;
  desiredFlavor = flavor;
  if (flavorHandler) flavorHandler(flavor);
}

void onMessage(ProtoLink *link, const uint8_t *frame, uint16_t len) {
  (void)link;
  ++framesRx;
  const uint8_t type = msgType(frame);
  const uint8_t *payload = msgPayload(frame);
  const uint16_t plen = msgPayloadLen(len);

  if (type == MSG_RESP_FLAVOR_STATE && plen >= sizeof(FlavorStatePayload)) {
    FlavorStatePayload state;
    memcpy(&state, payload, sizeof(state));
    if (state.flavor > PUMP_CHANNEL_B) return;

    controllerFlavor = state.flavor;
    controllerPersisted = (state.flags & FLAVOR_STATE_F_PERSISTED) != 0;
    controllerPersistError = (state.flags & FLAVOR_STATE_F_PERSIST_ERROR) != 0;

    if (state.token == 0) {
      if (queueCount == 0 && !offlineSelection) {
        applyAuthoritative(state.flavor);
        synchronized = (state.flags & FLAVOR_STATE_F_ESTABLISHED) != 0;
        awaitingPersistence = !controllerPersisted;
      }
      return;
    }

    if (queueCount == 0 || queue[queueHead].request.token != state.token) {
      ++staleResponses;
      // A token can outlive its queue entry because TinyProto and the
      // application both retry. With no newer local intent, its payload is
      // still the controller's current truth and may be the only successful
      // publication of a persistence or console revision.
      if (queueCount == 0 && !offlineSelection) {
        applyAuthoritative(state.flavor);
        synchronized = (state.flags & FLAVOR_STATE_F_ESTABLISHED) != 0;
        awaitingPersistence = !controllerPersisted;
      }
      return;
    }

    const Intent answered = queue[queueHead];
    popQueue();
    lastAckMs = millis() - answered.firstSentAtMs;
    if (lastAckMs > maxAckMs) maxAckMs = lastAckMs;

    if (queueCount == 0 && !offlineSelection) {
      applyAuthoritative(state.flavor);
      synchronized = (state.flags & FLAVOR_STATE_F_ESTABLISHED) != 0;
      awaitingPersistence = !controllerPersisted;
    }
    return;
  }

  if (type >= MSG_ERR_SLOT_INVALID && type <= MSG_ERR_UNSUPPORTED) {
    if (queueCount) popQueue();
    synchronized = false;
    ++staleResponses;
  }
}

}  // namespace

void baseLinkBegin(uint8_t cachedFlavor, BaseFlavorHandler handler) {
  desiredFlavor = controllerFlavor = cachedFlavor <= PUMP_CHANNEL_B ? cachedFlavor : 0;
  flavorHandler = handler;
  tokenState = esp_random();
  if (tokenState == 0) tokenState = 1;

  // GPIO43/44 are the ROM UART0 pads. Hand both back to the GPIO matrix before
  // mapping UART1, so the native-USB build never inherits a boot-ROM owner.
  gpio_reset_pin(static_cast<gpio_num_t>(kBaseTxPin));
  gpio_reset_pin(static_cast<gpio_num_t>(kBaseRxPin));
  Serial1.setRxBufferSize(1024);
  Serial1.begin(kBaseBaud, SERIAL_8N1, kBaseRxPin, kBaseTxPin);
  base.onMessage = onMessage;
  base.begin(Serial1, "J3 base");
  connectionGeneration = base.connectionGeneration();
}

void baseLinkSelect(uint8_t flavor, bool audible) {
  if (flavor > PUMP_CHANNEL_B) return;
  desiredFlavor = flavor;
  synchronized = false;
  awaitingPersistence = true;

  if (!base.isConnected()) {
    clearQueue();
    offlineSelection = true;
    return;
  }

  enqueue(MSG_FLAVOR_SELECT, flavor, audible);
}

void baseLinkService() {
  const uint32_t startedUs = micros();
  base.service();

  const uint32_t generation = base.connectionGeneration();
  const bool connected = base.isConnected();
  if (generation != connectionGeneration) {
    connectionGeneration = generation;
    synchronized = false;
    const bool mustReassert = flavor_link_policy::needsReassert(
        offlineSelection, awaitingPersistence, queueHasSelection(),
        desiredFlavor, controllerFlavor);
    const flavor_link_policy::EpochAction action = flavor_link_policy::epochAction(
        connected, offlineSelection, awaitingPersistence, queueHasSelection(),
        desiredFlavor, controllerFlavor);
    clearQueue();
    if (action == flavor_link_policy::EpochAction::Disconnected) {
      // Any unacknowledged intent remains represented by desiredFlavor and is
      // sent once, without a stale delayed tick, after the new connection.
      offlineSelection = mustReassert;
      const uint32_t elapsedUs = micros() - startedUs;
      if (elapsedUs > maxServiceUs) maxServiceUs = elapsedUs;
      return;
    }

    if (action == flavor_link_policy::EpochAction::Reassert) {
      enqueue(MSG_FLAVOR_SELECT, desiredFlavor, false);
      offlineSelection = false;
    } else {
      enqueue(MSG_FLAVOR_SYNC, desiredFlavor, false);
    }
  }

  if (connected) sendHead();
  base.service();
  const uint32_t elapsedUs = micros() - startedUs;
  if (elapsedUs > maxServiceUs) maxServiceUs = elapsedUs;
}

void baseLinkReadStatus(BaseLinkStatus &status) {
  status.connected = base.isConnected();
  status.synchronized = synchronized;
  status.controllerPersisted = controllerPersisted;
  status.controllerPersistError = controllerPersistError;
  status.durabilityPending = awaitingPersistence;
  status.controllerFlavor = controllerFlavor;
  status.pending = static_cast<uint8_t>(queueCount + (offlineSelection ? 1 : 0));
  status.framesRx = framesRx;
  status.framesTx = framesTx;
  status.retries = retries;
  status.queueDrops = queueDrops;
  status.staleResponses = staleResponses;
  status.lastAckMs = lastAckMs;
  status.maxAckMs = maxAckMs;
  status.maxServiceUs = maxServiceUs;
}
