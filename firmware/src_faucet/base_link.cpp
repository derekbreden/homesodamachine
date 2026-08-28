#include <Arduino.h>
#include <driver/gpio.h>
#include <esp_system.h>

#include "base_link.h"
#include "ble_link.h"
#include "fw_version.h"
#include "ota_receiver.h"
#include <esp_system.h>
#include "flavor_link_policy.h"
#include "proto_link.h"
#include "proto_msg.h"
#include "wifi_bench.h"
#include "image_store.h"
#include "image_synth.h"

namespace {

constexpr int kBaseRxPin = 44;  // P1 ESP_RXD, crossed from main board J3 IO33 TX
constexpr int kBaseTxPin = 43;  // P1 ESP_TXD, crossed to main board J3 IO35 RX
constexpr long kBaseBaud = 921600;
constexpr uint8_t kQueueDepth = 8;
constexpr uint8_t kPrimeQueueDepth = PRIME_J3_APP_QUEUE_DEPTH;
constexpr uint8_t kPrimePayloadMax = sizeof(PrimeHoldPayload);
constexpr uint32_t kResponseTimeoutMs = 750;
constexpr uint32_t kAudibleFreshMs = 300;
// A tokenized reply normally arrives in milliseconds. A repeated controller
// heartbeat with the requested value proves the same thing even when that one
// reply was lost; a conflicting heartbeat is allowed a few application retry
// windows before main board truth replaces an orphaned local intent.
constexpr uint32_t kMainBoardTruthGraceMs = kResponseTimeoutMs * 3;
static_assert(PROTOLINK_WINDOW == PRIME_PROTO_LINK_WINDOW_DEPTH,
              "prime replay contract must follow the TinyProto window");
static_assert(PRIME_HOLD_REPLAY_HISTORY >
                  kPrimeQueueDepth + PROTOLINK_WINDOW,
              "main board prime replay ledger must cover the complete J3 queue");

struct Intent {
  uint8_t type;
  FlavorRequestPayload request;
  uint32_t queuedAtMs;
  uint32_t firstSentAtMs;
  uint32_t lastSentAtMs;
  bool sent;
};

struct PrimeIntent {
  uint8_t type;
  uint8_t len;
  uint8_t data[kPrimePayloadMax];
};

ProtoLink base;
BaseFlavorHandler flavorHandler = nullptr;
BasePrimeHandler primeHandler = nullptr;
Intent queue[kQueueDepth];
uint8_t queueHead = 0;
uint8_t queueTail = 0;
uint8_t queueCount = 0;
PrimeIntent primeQueue[kPrimeQueueDepth];
uint8_t primeQueueHead = 0;
uint8_t primeQueueTail = 0;
uint8_t primeQueueCount = 0;
uint8_t desiredFlavor = 0;
uint8_t mainBoardFlavor = 0;
bool synchronized = false;
bool offlineSelection = false;
bool awaitingPersistence = false;
bool mainBoardPersisted = false;
bool mainBoardPersistError = false;
uint32_t tokenState = 1;
uint32_t framesRx = 0;
uint32_t framesTx = 0;
// What this board would have printed at boot if it had a console. J3 is not
// synchronised that early and the main board reboots often, so it is held and
// said again on every connection rather than once into a link nobody had yet.
char bootLine[96] = {0};
uint32_t benchWant = 0;
uint32_t benchGot = 0;
uint32_t benchFirstMs = 0;
uint32_t retries = 0;
uint32_t queueDrops = 0;
uint32_t staleResponses = 0;
uint32_t authoritativeReconciliations = 0;
uint32_t primeQueueDrops = 0;
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

void clearPrimeQueue() {
  primeQueueHead = primeQueueTail = primeQueueCount = 0;
}

void enqueuePrime(uint8_t type, const void *payload, uint8_t len, bool safetyCritical) {
  if (len > kPrimePayloadMax) return;

  // A STOP or session CANCEL is the safe final word. It supersedes every
  // queued START/TICK immediately, including across a release in the same UI
  // frame; no actuator-on intent may remain behind a physical lift.
  if (safetyCritical && primeQueueCount) clearPrimeQueue();

  if (primeQueueCount >= kPrimeQueueDepth) {
    ++primeQueueDrops;
    if (!safetyCritical) return;
    clearPrimeQueue();
  }

  PrimeIntent &intent = primeQueue[primeQueueTail];
  intent.type = type;
  intent.len = len;
  if (len && payload) memcpy(intent.data, payload, len);
  primeQueueTail = static_cast<uint8_t>((primeQueueTail + 1) % kPrimeQueueDepth);
  ++primeQueueCount;
}

bool sendPrimeHead() {
  if (primeQueueCount == 0 || !base.isConnected()) return false;
  PrimeIntent &intent = primeQueue[primeQueueHead];
  if (base.trySend(intent.type, intent.len ? intent.data : nullptr, intent.len) < 0)
    return true;  // retain priority while TinyProto's window is full
  primeQueueHead = static_cast<uint8_t>((primeQueueHead + 1) % kPrimeQueueDepth);
  --primeQueueCount;
  ++framesTx;
  return true;
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
  mainBoardFlavor = flavor;
  desiredFlavor = flavor;
  if (flavorHandler) flavorHandler(flavor);
}

void settleFromMainBoardHeartbeat(const FlavorStatePayload &state) {
  if (queueCount == 0 || offlineSelection) return;

  // A token-zero state is sent periodically by the main board. If it already
  // carries our final absolute choice, it is a valid acknowledgement even
  // when the original tokenized response was lost. If it disagrees for several
  // complete retry windows, retaining a local image indefinitely would leave
  // the faucet showing something the main board has rejected or never heard.
  const Intent &head = queue[queueHead];
  if (!flavor_link_policy::mainBoardHeartbeatSettlesPendingSelection(
          offlineSelection, queueCount != 0, head.sent, desiredFlavor,
          state.flavor, millis(), head.firstSentAtMs,
          kMainBoardTruthGraceMs)) return;

  clearQueue();
  applyAuthoritative(state.flavor);
  synchronized = (state.flags & FLAVOR_STATE_F_ESTABLISHED) != 0;
  awaitingPersistence = !mainBoardPersisted;
  ++authoritativeReconciliations;
}

// ── Firmware arriving over J3 ─────────────────────────────────────────────
// The receiver pulls: it asks for the offset it is ready to write and the main
// board answers that. A request that goes unanswered is simply re-asked, so a
// lost frame costs a retry interval rather than the transfer.
static OtaReceiver ota;
static uint32_t otaAskedAtMs = 0;
static uint32_t otaFrames = 0, otaDups = 0, otaGaps = 0, otaBytes = 0;
static bool     otaRebootPending = false;
static uint32_t otaRebootAtMs = 0;
static const uint32_t OTA_REASK_MS = 40;

static void otaAsk() {
  OtaReqPayload req{ota.nextOffset()};
  base.trySend(MSG_OTA_REQ, &req, sizeof(req));
  otaAskedAtMs = millis();
}

static void otaReport() {
  OtaStatePayload st;
  ota.fill(st);
  base.trySend(MSG_RESP_OTA, &st, sizeof(st));
}

static void otaHandle(uint8_t type, const uint8_t *payload, uint16_t plen) {
  if (type == MSG_OTA_ABORT) {
    ota.abort();
    faucetApplyOta(false, 0);
    return;
  }

  if (type == MSG_OTA_BEGIN && plen >= sizeof(OtaBeginPayload)) {
    OtaBeginPayload b;
    memcpy(&b, payload, sizeof(b));
    // Erasing a 3 MB slot takes long enough that the panel must say so first.
    faucetApplyOta(true, 0);
    otaFrames = otaDups = otaGaps = otaBytes = 0;
    Serial.printf("OTA:BEGIN size=%lu crc=%08lX chunk=%u kind=%u\n",
                  (unsigned long)b.size, (unsigned long)b.crc32, b.chunk, b.kind);
    ota.begin(b.size, b.crc32, b.kind);
    otaReport();
    if (ota.active()) otaAsk();
    else faucetApplyOta(false, 0);
    return;
  }

  if (type == MSG_OTA_DATA && plen >= 4 && ota.active()) {
    uint32_t offset;
    memcpy(&offset, payload, 4);
    ++otaFrames;
    otaBytes += (uint32_t)(plen - 4);
    if (offset < ota.nextOffset()) ++otaDups;
    else if (offset != ota.nextOffset()) ++otaGaps;
    if (!ota.write(offset, payload + 4, (uint16_t)(plen - 4))) {
      otaReport();
      faucetApplyOta(false, 0);
      return;
    }
    if (ota.nextOffset() < ota.expected) {
      faucetApplyOta(true, (uint8_t)((uint64_t)ota.nextOffset() * 100 / ota.expected));
      otaAsk();
      return;
    }
    // Last byte is in. Nothing has moved yet — finish() is what verifies the
    // whole image and only then points the bootloader at it.
    const bool ok = ota.finish();
    Serial.printf("OTA:END ok=%d state=%u err=%u recv=%lu exp=%lu run=%08lX want=%08lX "
                  "frames=%lu dup=%lu bytes=%lu\n",
                  (int)ok, ota.state, ota.err,
                  (unsigned long)ota.received, (unsigned long)ota.expected,
                  (unsigned long)ota.runCrc, (unsigned long)ota.wantCrc,
                  (unsigned long)otaFrames, (unsigned long)otaDups,
                  (unsigned long)otaBytes);
    otaReport();
    if (ota.done()) {
      faucetApplyOta(true, 100);
      otaRebootPending = true;
      otaRebootAtMs = millis() + 400;   // let the reply clear J3 first
    } else {
      faucetApplyOta(false, 0);
    }
    return;
  }
}

void onMessage(ProtoLink *link, const uint8_t *frame, uint16_t len) {
  (void)link;
  ++framesRx;
  const uint8_t type = msgType(frame);
  const uint8_t *payload = msgPayload(frame);
  const uint16_t plen = msgPayloadLen(len);

  if (type == MSG_OTA_BEGIN || type == MSG_OTA_DATA || type == MSG_OTA_ABORT) {
    otaHandle(type, payload, plen);
    return;
  }

  // The relay's half of a session this board opened for someone else.
  if (type == MSG_OTA_SRC_NEED && plen >= sizeof(OtaSrcNeedPayload)) {
    OtaSrcNeedPayload need;
    memcpy(&need, payload, sizeof(need));
    bleLinkOnSrcNeed(need.offset, need.len);
    return;
  }
  if (type == MSG_OTA_SRC_END && plen >= sizeof(OtaStatePayload)) {
    OtaStatePayload st;
    memcpy(&st, payload, sizeof(st));
    bleLinkOnSrcEnd(st);
    return;
  }
  if (type == MSG_VERSION_QUERY) {
    VersionPayload v{OTA_TGT_FAUCET, {0}, 0};
    strncpy(v.version, FW_VERSION, FW_VERSION_MAX);
    base.trySend(MSG_RESP_VERSION, &v, sizeof(v));
    return;
  }
  if (type == MSG_RESP_VERSIONS && plen >= sizeof(VersionsPayload)) {
    VersionsPayload all;
    memcpy(&all, payload, sizeof(all));
    bleLinkOnVersions(all);
    return;
  }
  // The wire's own ceiling, measured at the end that receives it. Nothing is
  // written to flash and nothing is answered per chunk: the point is what J3
  // and TinyProto's window carry when no one is taking a turn.
  if (type == MSG_BENCH_BEGIN && plen >= sizeof(BenchBeginPayload)) {
    BenchBeginPayload b;
    memcpy(&b, payload, sizeof(b));
    benchWant = b.bytes;
    benchGot = 0;
    benchFirstMs = 0;
    return;
  }

  if (type == MSG_BENCH_DATA) {
    if (!benchWant) return;
    if (!benchGot) benchFirstMs = millis();
    benchGot += plen;
    if (benchGot >= benchWant) {
      BenchResultPayload r{benchGot, (uint32_t)(millis() - benchFirstMs)};
      base.trySend(MSG_RESP_BENCH, &r, sizeof(r));
      benchWant = 0;
    }
    return;
  }

  // The radio bench. The run itself happens on a task of its own; this only
  // starts it, and its result goes out from baseLinkService() when it lands.
  if (type == MSG_WIFI_BENCH_PUSH && plen >= sizeof(WifiPushPayload)) {
    WifiPushPayload req;
    memcpy(&req, payload, sizeof(req));
    if (!wifiBenchPush(req.bytes, req.channel, req.flags)) {
      WifiPushResultPayload busy{};
      busy.err = WIFI_BENCH_ERR_BUSY;
      base.trySend(MSG_RESP_WIFI_PUSH, &busy, sizeof(busy));
    }
    return;
  }

  if (type == MSG_IMAGE_SYNTH && plen >= sizeof(ImageSlotPayload)) {
    ImageSlotPayload req;
    memcpy(&req, payload, sizeof(req));
    char line[64];
    const bool ok = imageSynthWrite(req.slot);
    if (ok) faucetRebindLogos();
    snprintf(line, sizeof(line), "synth slot %u %s, held %u", req.slot,
             ok ? "written" : "REFUSED", imageStoreHeld());
    base.trySend(MSG_TEXT, line, (uint16_t)strlen(line));
    char diag[80];
    imageStoreDiag(diag, sizeof(diag));
    base.trySend(MSG_TEXT, diag, (uint16_t)strlen(diag));
    return;
  }

  if (type == MSG_IMAGES_QUERY) {
    ImagesPayload im{};
    im.board = OTA_TGT_FAUCET;
    im.slots = imageStoreCapacity() < FLAVOR_ART_CUSTOM
                   ? imageStoreCapacity() : FLAVOR_ART_CUSTOM;
    im.bundleBytes = imageStoreBundleBytes();
    for (uint8_t i = 0; i < im.slots; i++)
      if (imageStoreOccupied(i)) { im.occupancy |= (uint8_t)(1u << i); ++im.held; }
    base.trySend(MSG_RESP_IMAGES, &im, sizeof(im));
    return;
  }

  if (type == MSG_BLE_STATUS_REQ) {
    BleStatusPayload st;
    bleLinkFillStatus(st);
    base.trySend(MSG_RESP_BLE_STATUS, &st, sizeof(st));
    return;
  }
  if (type == MSG_RESP_IDENTITY && plen >= sizeof(IdentityPayload)) {
    IdentityPayload id;
    memcpy(&id, payload, sizeof(id));
    bleLinkOnIdentity(id);
    return;
  }

  if (type == MSG_RESP_PRIME_SESSION && plen >= sizeof(PrimeSessionStatePayload)) {
    PrimeSessionStatePayload state;
    memcpy(&state, payload, sizeof(state));
    if (primeHandler) primeHandler(state, base.connectionGeneration());
    return;
  }

  if (type == MSG_RESP_IDLE && plen >= sizeof(IdlePayload)) {
    IdlePayload idle;
    memcpy(&idle, payload, sizeof(idle));
    faucetApplyIdle(idle.asleep != 0);
    return;
  }

  if (type == MSG_RESP_FLAVOR_ART && plen >= sizeof(FlavorArtPayload)) {
    FlavorArtPayload art;
    memcpy(&art, payload, sizeof(art));
    faucetApplyFlavorArt(art.art);
    return;
  }

  if (type == MSG_RESP_FLAVOR_STATE && plen >= sizeof(FlavorStatePayload)) {
    FlavorStatePayload state;
    memcpy(&state, payload, sizeof(state));
    if (state.flavor > PUMP_CHANNEL_B) return;

    mainBoardFlavor = state.flavor;
    mainBoardPersisted = (state.flags & FLAVOR_STATE_F_PERSISTED) != 0;
    mainBoardPersistError = (state.flags & FLAVOR_STATE_F_PERSIST_ERROR) != 0;

    if (state.token == 0) {
      if (queueCount == 0 && !offlineSelection) {
        applyAuthoritative(state.flavor);
        synchronized = (state.flags & FLAVOR_STATE_F_ESTABLISHED) != 0;
        awaitingPersistence = !mainBoardPersisted;
      } else {
        settleFromMainBoardHeartbeat(state);
      }
      return;
    }

    if (queueCount == 0 || queue[queueHead].request.token != state.token) {
      ++staleResponses;
      // A token can outlive its queue entry because TinyProto and the
      // application both retry. With no newer local intent, its payload is
      // still the main board's current truth and may be the only successful
      // publication of a persistence or console revision.
      if (queueCount == 0 && !offlineSelection) {
        applyAuthoritative(state.flavor);
        synchronized = (state.flags & FLAVOR_STATE_F_ESTABLISHED) != 0;
        awaitingPersistence = !mainBoardPersisted;
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
      awaitingPersistence = !mainBoardPersisted;
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

void baseLinkBegin(uint8_t cachedFlavor, BaseFlavorHandler handler,
                   BasePrimeHandler sessionHandler) {
  desiredFlavor = mainBoardFlavor = cachedFlavor <= PUMP_CHANNEL_B ? cachedFlavor : 0;
  flavorHandler = handler;
  primeHandler = sessionHandler;
  tokenState = esp_random();
  if (tokenState == 0) tokenState = 1;

  // GPIO43/44 are the ROM UART0 pads. Hand both back to the GPIO matrix before
  // mapping UART1, so the native-USB build never inherits a boot-ROM owner.
  gpio_reset_pin(static_cast<gpio_num_t>(kBaseTxPin));
  gpio_reset_pin(static_cast<gpio_num_t>(kBaseRxPin));
  Serial1.setRxBufferSize(8192);
  Serial1.begin(kBaseBaud, SERIAL_8N1, kBaseRxPin, kBaseTxPin);
  base.onMessage = onMessage;
  base.begin(Serial1, "J3 base");
  connectionGeneration = base.connectionGeneration();
}

// A press that put nothing else on the pair. The main board keeps one clock for
// both glasses and this is what it counts; a press that already sent a command
// is presence it can see without being told twice.
void baseLinkTouched() {
  if (!base.isConnected()) return;
  if (base.trySend(MSG_TOUCH, nullptr, 0) >= 0) ++framesTx;
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

void baseLinkPrimeCancel(uint8_t channel, uint32_t sessionToken) {
  if (channel > PUMP_CHANNEL_B || sessionToken == 0) return;
  PrimeSessionRequestPayload request{PRIME_SESSION_CANCEL, channel, sessionToken};
  enqueuePrime(MSG_PRIME_SESSION_SET, &request, sizeof(request), true);
}

void baseLinkPrimeHoldStart(uint8_t channel, uint32_t sessionToken, uint32_t holdToken) {
  if (channel > PUMP_CHANNEL_B || sessionToken == 0 || holdToken == 0) return;
  PrimeHoldPayload hold{channel, sessionToken, holdToken};
  enqueuePrime(MSG_PRIME_SESSION_HOLD_START, &hold, sizeof(hold), false);
}

void baseLinkPrimeHoldTick(uint8_t channel, uint32_t sessionToken, uint32_t holdToken) {
  if (channel > PUMP_CHANNEL_B || sessionToken == 0 || holdToken == 0) return;
  PrimeHoldPayload hold{channel, sessionToken, holdToken};
  enqueuePrime(MSG_PRIME_SESSION_HOLD_TICK, &hold, sizeof(hold), false);
}

void baseLinkPrimeHoldStop(uint8_t channel, uint32_t sessionToken, uint32_t holdToken) {
  if (channel > PUMP_CHANNEL_B || sessionToken == 0 || holdToken == 0) return;
  PrimeHoldPayload hold{channel, sessionToken, holdToken};
  enqueuePrime(MSG_PRIME_SESSION_HOLD_STOP, &hold, sizeof(hold), true);
}

void baseLinkPrimeDiscard() {
  clearPrimeQueue();
}

// Said over J3 because this board has no console of its own in the appliance.
void baseLinkSay(const char *text) { base.trySend(MSG_TEXT, text, (uint16_t)strlen(text)); }

void baseLinkSayOnConnect(const char *text) {
  snprintf(bootLine, sizeof(bootLine), "%s", text);
  baseLinkSay(text);
}

void baseLinkService() {
  const uint32_t startedUs = micros();
  base.service();

  if (otaRebootPending && (int32_t)(millis() - otaRebootAtMs) >= 0) esp_restart();
  if (ota.active() && millis() - otaAskedAtMs >= OTA_REASK_MS) otaAsk();

  const uint32_t generation = base.connectionGeneration();
  const bool connected = base.isConnected();
  if (generation != connectionGeneration) {
    connectionGeneration = generation;
    if (connected && bootLine[0]) base.trySend(MSG_TEXT, bootLine, (uint16_t)strlen(bootLine));
    synchronized = false;
    // A control accepted by the previous TinyProto epoch may or may not have
    // reached the main board. Drop it here; the UI fails closed and reasserts
    // any desired CANCEL/STOP with the same token after fresh truth.
    clearPrimeQueue();
    const bool mustReassert = flavor_link_policy::needsReassert(
        offlineSelection, awaitingPersistence, queueHasSelection(),
        desiredFlavor, mainBoardFlavor);
    const flavor_link_policy::EpochAction action = flavor_link_policy::epochAction(
        connected, offlineSelection, awaitingPersistence, queueHasSelection(),
        desiredFlavor, mainBoardFlavor);
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

  // A finished bench run, reported the moment it lands rather than waiting for
  // anyone to ask. The radio goes down with it: nothing on this board keeps a
  // WiFi association standing outside a run.
  if (wifiBenchResultReady()) {
    WifiPushResultPayload r;
    wifiBenchTakeResult(r);
    base.trySend(MSG_RESP_WIFI_PUSH, &r, sizeof(r));
    wifiBenchRelease();
  }

  if (connected && !sendPrimeHead()) sendHead();
  base.service();
  const uint32_t elapsedUs = micros() - startedUs;
  if (elapsedUs > maxServiceUs) maxServiceUs = elapsedUs;
}

bool baseLinkSendOtaSrc(uint8_t type, const void *data, uint16_t len) {
  return base.trySend(type, data, len) >= 0;
}

void baseLinkReadStatus(BaseLinkStatus &status) {
  status.connected = base.isConnected();
  status.synchronized = synchronized;
  status.mainBoardPersisted = mainBoardPersisted;
  status.mainBoardPersistError = mainBoardPersistError;
  status.durabilityPending = awaitingPersistence;
  status.mainBoardFlavor = mainBoardFlavor;
  status.pending = static_cast<uint8_t>(queueCount + (offlineSelection ? 1 : 0));
  status.framesRx = framesRx;
  status.framesTx = framesTx;
  status.retries = retries;
  status.queueDrops = queueDrops;
  status.staleResponses = staleResponses;
  status.authoritativeReconciliations = authoritativeReconciliations;
  status.lastAckMs = lastAckMs;
  status.maxAckMs = maxAckMs;
  status.maxServiceUs = maxServiceUs;
  status.primePending = primeQueueCount;
  status.primeQueueDrops = primeQueueDrops;
  status.connectionGeneration = connectionGeneration;
}
