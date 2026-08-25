#include <Arduino.h>
#include <NimBLEDevice.h>
#include <esp_mac.h>

#include "ble_link.h"
#include "base_link.h"
#include "ota_receiver.h"
#include "fw_version.h"

// Nordic UART Service — the same three UUIDs the iOS app already knows.
static const char *NUS_SERVICE = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E";
static const char *NUS_RX      = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E";
static const char *NUS_TX      = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E";

// Anthropic's assigned company id is not ours to use and this is not a shipped
// product, so the manufacturer block opens with 0xFFFF — the id reserved for
// exactly this.
static const uint16_t MFG_ID = 0xFFFF;

// ── The framing the app speaks ────────────────────────────────────────────
// 0x01..0x04 are the vocabulary the prototype's rotary display already uses.
// Firmware starts at 0x10 so nothing here can be read as one of those.
static const uint8_t BLE_TEXT       = 0x01;
static const uint8_t BLE_OTA_BEGIN  = 0x10;  // phone → board: target, size, crc32, kind
static const uint8_t BLE_OTA_NEED   = 0x11;  // board → phone: offset, length
static const uint8_t BLE_OTA_DATA   = 0x12;  // phone → board: offset, then bytes
static const uint8_t BLE_OTA_END    = 0x13;  // board → phone: state, err, received
static const uint8_t BLE_IDENTITY   = 0x14;  // board → phone: model, unit, name, versions

struct __attribute__((packed)) BleOtaBegin {
  uint8_t  target;   // OTA_TGT_*
  uint8_t  kind;     // OTA_KIND_*
  uint32_t size;
  uint32_t crc32;
};

struct __attribute__((packed)) BleOtaNeed {
  uint32_t offset;
  uint16_t len;
};

static NimBLEServer         *server = nullptr;
static NimBLECharacteristic *txChar = nullptr;
static volatile bool         connected = false;

static IdentityPayload identity{};
static bool            haveIdentity = false;
static uint32_t        identityAskedAtMs = 0;

// ── The session, as this board sees it ────────────────────────────────────
// Either the bytes are going onto J3 for someone else, or into this board's own
// spare slot. Nothing else is held.
static uint8_t   sessionTarget = OTA_TGT_NONE;
static uint32_t  imgSize = 0;
static uint32_t  owedOffset = 0;   // what the phone was last asked for
static uint16_t  owed = 0;         // how much of that it still owes
// What the relay asked for, which is more than one BLE frame carries. This
// board walks it a frame at a time and the relay sees the pieces arrive.
static uint32_t  spanOffset = 0;
static uint32_t  spanRemain = 0;

static OtaReceiver localRx;
static uint32_t    localAskedAtMs = 0;
static bool        rebootPending = false;
static uint32_t    rebootAtMs = 0;

// A write arrives on the NimBLE task; anything that touches flash, LVGL or J3
// has to happen in loop(). One frame is in flight at a time because the pull
// only ever asks for one, so a single staging buffer is the whole queue.
static const uint16_t RX_STAGE = 640;
static volatile uint16_t stageLen = 0;
static uint8_t  stage[RX_STAGE];
static uint32_t dropped = 0;

static void notify(uint8_t type, const void *data, uint16_t len) {
  if (!txChar || !connected) return;
  uint8_t frame[3 + 64];
  if (len > sizeof(frame) - 3) return;
  frame[0] = type;
  frame[1] = (uint8_t)(len & 0xFF);
  frame[2] = (uint8_t)(len >> 8);
  if (len) memcpy(frame + 3, data, len);
  txChar->setValue(frame, 3 + len);
  txChar->notify();
}

static void sendIdentity() {
  // Everything a picker needs on one screen: which machine, which unit, what it
  // is called, and what this display is running.
  uint8_t body[1 + 3 + (MACHINE_NAME_MAX + 1) + 32];
  size_t n = 0;
  body[n++] = haveIdentity ? identity.model : 0;
  memcpy(body + n, haveIdentity ? identity.unit : (const uint8_t *)"\0\0\0", 3); n += 3;
  memset(body + n, 0, MACHINE_NAME_MAX + 1);
  if (haveIdentity) strncpy((char *)(body + n), identity.name, MACHINE_NAME_MAX);
  n += MACHINE_NAME_MAX + 1;
  const size_t vlen = strnlen(FW_VERSION, 31);
  memcpy(body + n, FW_VERSION, vlen); n += vlen;
  body[n++] = 0;
  notify(BLE_IDENTITY, body, (uint16_t)n);
}

// ── What this board advertises ────────────────────────────────────────────
static void advertisedName(char *out, size_t cap) {
  if (haveIdentity && identity.name[0]) {
    snprintf(out, cap, "%s", identity.name);
    return;
  }
  uint8_t unit[3];
  if (haveIdentity) {
    memcpy(unit, identity.unit, 3);
  } else {
    // Until the main board answers, this display's own MAC names the board.
    uint8_t mac[6] = {0};
    esp_read_mac(mac, ESP_MAC_WIFI_STA);
    unit[0] = mac[3]; unit[1] = mac[4]; unit[2] = mac[5];
  }
  snprintf(out, cap, "SodaMachine %02X-%02X", unit[1], unit[2]);
}

static void applyAdvertising() {
  NimBLEAdvertising *adv = NimBLEDevice::getAdvertising();
  adv->stop();

  char name[32];
  advertisedName(name, sizeof(name));
  NimBLEDevice::setDeviceName(name);

  // The 128-bit service UUID fills half of the 31-byte advertisement, so the
  // name and the manufacturer block ride the scan response.
  NimBLEAdvertisementData scan;
  scan.setName(name);
  uint8_t mfg[6];
  mfg[0] = (uint8_t)(MFG_ID & 0xFF);
  mfg[1] = (uint8_t)(MFG_ID >> 8);
  mfg[2] = haveIdentity ? identity.model : 0;
  memcpy(mfg + 3, haveIdentity ? identity.unit : (const uint8_t *)"\0\0\0", 3);
  scan.setManufacturerData(mfg, sizeof(mfg));
  adv->setScanResponseData(scan);

  NimBLEAdvertisementData primary;
  primary.setFlags(BLE_HS_ADV_F_DISC_GEN | BLE_HS_ADV_F_BREDR_UNSUP);
  primary.addServiceUUID(NimBLEUUID(NUS_SERVICE));
  adv->setAdvertisementData(primary);

  adv->start();
}

void bleLinkOnIdentity(const IdentityPayload &id) {
  const bool changed = !haveIdentity || memcmp(&identity, &id, sizeof(id)) != 0;
  identity = id;
  haveIdentity = true;
  if (changed) {
    Serial.printf("IDENTITY model=%u unit=%02X%02X%02X name=%s\n",
                  id.model, id.unit[0], id.unit[1], id.unit[2],
                  id.name[0] ? id.name : "(unset)");
    applyAdvertising();
    sendIdentity();
  }
}

// ── The session, driven from loop() ───────────────────────────────────────
// The most image bytes one BLE_OTA_DATA carries. A 517-byte MTU leaves 514 for
// the payload, less this board's 3-byte header and the 4-byte offset.
static const uint16_t BLE_ASK = 480;

static void askPhone(uint32_t offset, uint16_t len) {
  owedOffset = offset;
  owed = len;
  BleOtaNeed need{offset, len};
  notify(BLE_OTA_NEED, &need, sizeof(need));
}

static void endSession(uint8_t state, uint8_t err, uint32_t received) {
  OtaStatePayload st{state, err, received};
  notify(BLE_OTA_END, &st, sizeof(st));
  Serial.printf("BLE:OTA END target=%u state=%u err=%u recv=%lu\n",
                sessionTarget, state, err, (unsigned long)received);
  sessionTarget = OTA_TGT_NONE;
  imgSize = 0;
  owed = 0;
  spanRemain = 0;
}

void bleLinkOnSrcNeed(uint32_t offset, uint16_t len) {
  if (sessionTarget == OTA_TGT_NONE || sessionTarget == OTA_TGT_FAUCET) return;
  spanOffset = offset;
  spanRemain = len;
  askPhone(spanOffset, (uint16_t)(spanRemain < BLE_ASK ? spanRemain : BLE_ASK));
}

void bleLinkOnSrcEnd(const OtaStatePayload &state) {
  if (sessionTarget == OTA_TGT_NONE || sessionTarget == OTA_TGT_FAUCET) return;
  endSession(state.state, state.err, state.received);
}

static void handleBegin(const uint8_t *payload, uint16_t plen) {
  if (plen < sizeof(BleOtaBegin)) return;
  BleOtaBegin b;
  memcpy(&b, payload, sizeof(b));

  if (sessionTarget != OTA_TGT_NONE) {
    // A repeat of the session already running is the phone's retry.
    if (b.target == sessionTarget && b.size == imgSize) return;
    endSession(OTA_STATE_FAILED, OTA_ERR_NONE, 0);
    return;
  }
  if (b.size == 0 || b.target == OTA_TGT_NONE) return;

  sessionTarget = b.target;
  imgSize = b.size;
  Serial.printf("BLE:OTA BEGIN target=%u size=%lu crc=%08lX kind=%u\n",
                b.target, (unsigned long)b.size, (unsigned long)b.crc32, b.kind);

  if (b.target == OTA_TGT_FAUCET) {
    faucetApplyOta(true, 0);
    if (!localRx.begin(b.size, b.crc32, b.kind)) {
      faucetApplyOta(false, 0);
      endSession(localRx.state, localRx.err, 0);
      return;
    }
    localAskedAtMs = millis();
    askPhone(0, (uint16_t)(b.size < BLE_ASK ? b.size : BLE_ASK));
    return;
  }

  OtaSrcBeginPayload src{b.size, b.crc32,
                         (uint16_t)(b.target == OTA_TGT_ENCLOSURE ? OTA_CHUNK_J9 : OTA_CHUNK_J3),
                         b.kind, b.target};
  baseLinkSendOtaSrc(MSG_OTA_SRC_BEGIN, &src, sizeof(src));
}

static void handleData(const uint8_t *payload, uint16_t plen) {
  if (sessionTarget == OTA_TGT_NONE || plen < 4 || owed == 0) return;
  uint32_t offset;
  memcpy(&offset, payload, 4);
  const uint16_t len = (uint16_t)(plen - 4);
  if (offset != owedOffset || len > owed) return;

  if (sessionTarget == OTA_TGT_FAUCET) {
    if (!localRx.write(offset, payload + 4, len)) {
      faucetApplyOta(false, 0);
      endSession(localRx.state, localRx.err, localRx.received);
      return;
    }
    if (localRx.nextOffset() < localRx.expected) {
      const uint32_t remain = localRx.expected - localRx.nextOffset();
      faucetApplyOta(true, (uint8_t)((uint64_t)localRx.nextOffset() * 100 / localRx.expected));
      localAskedAtMs = millis();
      askPhone(localRx.nextOffset(), (uint16_t)(remain < BLE_ASK ? remain : BLE_ASK));
      return;
    }
    const bool ok = localRx.finish();
    faucetApplyOta(ok, ok ? 100 : 0);
    endSession(localRx.state, localRx.err, localRx.received);
    if (ok) { rebootPending = true; rebootAtMs = millis() + 600; }
    return;
  }

  // Straight onto J3, unbuffered. The relay accumulates it into the chunk it
  // asked for and forwards that.
  uint8_t frame[4 + RX_STAGE];
  memcpy(frame, &offset, 4);
  memcpy(frame + 4, payload + 4, len);
  if (!baseLinkSendOtaSrc(MSG_OTA_SRC_DATA, frame, (uint16_t)(4 + len))) {
    ++dropped;
    return;   // the relay re-asks for this offset
  }
  owed -= len;
  spanOffset += len;
  spanRemain -= len;
  // The relay only speaks again once its whole chunk is in, so the rest of this
  // span is asked for from here.
  if (spanRemain) askPhone(spanOffset, (uint16_t)(spanRemain < BLE_ASK ? spanRemain : BLE_ASK));
  else owedOffset += len;
}

// ── NimBLE callbacks ──────────────────────────────────────────────────────
class RxCB : public NimBLECharacteristicCallbacks {
  void onWrite(NimBLECharacteristic *chr, NimBLEConnInfo &) override {
    NimBLEAttValue raw = chr->getValue();
    if (raw.length() > RX_STAGE || stageLen != 0) { ++dropped; return; }
    memcpy(stage, raw.data(), raw.length());
    stageLen = (uint16_t)raw.length();
  }
};

class ServerCB : public NimBLEServerCallbacks {
  void onConnect(NimBLEServer *, NimBLEConnInfo &info) override {
    connected = true;
    Serial.println("BLE: connected");
    // The pull costs one round trip per chunk, so the interval is the transfer
    // rate. Ask for the shortest iOS grants.
    server->updateConnParams(info.getConnHandle(), 12, 24, 0, 200);
  }
  void onDisconnect(NimBLEServer *, NimBLEConnInfo &, int) override {
    connected = false;
    Serial.println("BLE: disconnected");
    if (sessionTarget != OTA_TGT_NONE) {
      if (sessionTarget == OTA_TGT_FAUCET) { localRx.abort(); faucetApplyOta(false, 0); }
      else baseLinkSendOtaSrc(MSG_OTA_ABORT, nullptr, 0);
      sessionTarget = OTA_TGT_NONE;
      owed = 0;
    }
    NimBLEDevice::startAdvertising();
  }
  void onMTUChange(uint16_t mtu, NimBLEConnInfo &) override {
    Serial.printf("BLE: MTU %u\n", mtu);
  }
};

void bleLinkBegin() {
  char name[32];
  advertisedName(name, sizeof(name));
  NimBLEDevice::init(name);
  NimBLEDevice::setMTU(517);
  NimBLEDevice::setPower(ESP_PWR_LVL_P9);

  server = NimBLEDevice::createServer();
  server->setCallbacks(new ServerCB());
  server->advertiseOnDisconnect(true);

  NimBLEService *svc = server->createService(NUS_SERVICE);
  txChar = svc->createCharacteristic(NUS_TX, NIMBLE_PROPERTY::NOTIFY);
  NimBLECharacteristic *rx =
      svc->createCharacteristic(NUS_RX, NIMBLE_PROPERTY::WRITE | NIMBLE_PROPERTY::WRITE_NR);
  rx->setCallbacks(new RxCB());
  svc->start();

  applyAdvertising();
  Serial.printf("BLE: advertising as '%s'\n", name);
}

void bleLinkService() {
  if (rebootPending && (int32_t)(millis() - rebootAtMs) >= 0) {
    Serial.println("BLE:OTA rebooting into the new image");
    delay(50);
    ESP.restart();
  }

  // Until the main board answers, this board is advertising its own MAC rather
  // than the machine's. Ask again until it does.
  if (!haveIdentity && millis() - identityAskedAtMs >= 2000) {
    identityAskedAtMs = millis();
    baseLinkSendOtaSrc(MSG_IDENTITY_QUERY, nullptr, 0);
  }

  if (stageLen == 0) return;
  const uint16_t len = stageLen;
  static uint8_t work[RX_STAGE];
  memcpy(work, stage, len);
  stageLen = 0;

  if (len < 3) return;
  const uint8_t type = work[0];
  const uint16_t plen = (uint16_t)(work[1] | (work[2] << 8));
  if (3 + plen > len) return;
  const uint8_t *payload = work + 3;

  switch (type) {
    case BLE_OTA_BEGIN: handleBegin(payload, plen); break;
    case BLE_OTA_DATA:  handleData(payload, plen);  break;
    case BLE_TEXT:
      if (plen >= 8 && !memcmp(payload, "IDENTITY", 8)) sendIdentity();
      break;
    default: break;
  }
}

bool bleLinkConnected() { return connected; }

void bleLinkFillStatus(BleStatusPayload &out) {
  out.flags = (uint8_t)((server ? BLE_ST_UP : 0) |
                        (connected ? BLE_ST_CONNECTED : 0) |
                        (haveIdentity ? BLE_ST_IDENTITY : 0));
  out.target = sessionTarget;
  out.owed = owed;
  out.dropped = dropped;
  memset(out.advertised, 0, sizeof(out.advertised));
  char name[32];
  advertisedName(name, sizeof(name));
  strncpy(out.advertised, name, MACHINE_NAME_MAX);
}

void bleLinkReport() {
  char name[32];
  advertisedName(name, sizeof(name));
  Serial.printf("BLE: %s as '%s', identity %s, session target=%u owed=%u dropped=%lu\n",
                connected ? "connected" : "advertising", name,
                haveIdentity ? "known" : "unanswered",
                sessionTarget, owed, (unsigned long)dropped);
}
