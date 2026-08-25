#include <Arduino.h>
#include <NimBLEDevice.h>
#include <esp_mac.h>

#include "ble_link.h"
#include "base_link.h"
#include "ble_ota.h"
#include "fw_version.h"

// Nordic UART Service — the same three UUIDs the iOS app already knows.
static const char *NUS_SERVICE = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E";
static const char *NUS_RX      = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E";
static const char *NUS_TX      = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E";

// 0xFFFF is the company id reserved for a device that has none.
static const uint16_t MFG_ID = 0xFFFF;

static const uint8_t BLE_TEXT = 0x01;

static NimBLEServer         *server = nullptr;
static NimBLECharacteristic *txChar = nullptr;
static volatile bool         connected = false;

static IdentityPayload identity{};
static bool            haveIdentity = false;
static uint32_t        identityAskedAtMs = 0;

// A write arrives on the NimBLE task; anything that touches flash, LVGL or J3
// has to happen in loop(). One frame is in flight at a time because the pull
// only ever asks for one, so a single staging buffer is the whole queue.
static const uint16_t RX_STAGE = 640;
static volatile uint16_t stageLen = 0;
static uint8_t  stage[RX_STAGE];
static uint32_t stageDrops = 0;

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
  notify(BLE_FRAME_IDENTITY, body, (uint16_t)n);
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

void bleLinkOnSrcNeed(uint32_t offset, uint16_t len) { bleOtaOnSrcNeed(offset, len); }
void bleLinkOnSrcEnd(const OtaStatePayload &state)   { bleOtaOnSrcEnd(state); }

// ── NimBLE callbacks ──────────────────────────────────────────────────────
class RxCB : public NimBLECharacteristicCallbacks {
  void onWrite(NimBLECharacteristic *chr, NimBLEConnInfo &) override {
    NimBLEAttValue raw = chr->getValue();
    if (raw.length() > RX_STAGE || stageLen != 0) { ++stageDrops; return; }
    memcpy(stage, raw.data(), raw.length());
    stageLen = (uint16_t)raw.length();
  }
};

class ServerCB : public NimBLEServerCallbacks {
  void onConnect(NimBLEServer *, NimBLEConnInfo &info) override {
    connected = true;
    Serial.println("BLE: connected");
    // The pull costs one round trip per frame, so the connection interval is
    // the transfer rate. Ask for the shortest iOS grants.
    server->updateConnParams(info.getConnHandle(), 12, 24, 0, 200);
  }
  void onDisconnect(NimBLEServer *, NimBLEConnInfo &, int) override {
    connected = false;
    Serial.println("BLE: disconnected");
    bleOtaDisconnected();
    NimBLEDevice::startAdvertising();
  }
  void onMTUChange(uint16_t mtu, NimBLEConnInfo &) override {
    bleOtaSetMtu(mtu);
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

  BleOtaSeams seams{};
  seams.notify = notify;
  seams.sendSrc = baseLinkSendOtaSrc;
  seams.onLocalProgress = faucetApplyOta;
  seams.self = OTA_TGT_FAUCET;
  bleOtaBegin(seams);

  applyAdvertising();
  Serial.printf("BLE: advertising as '%s'\n", name);
}

void bleLinkService() {
  bleOtaService();

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

  if (bleOtaHandleFrame(type, payload, plen)) return;
  if (type == BLE_TEXT && plen >= 8 && !memcmp(payload, "IDENTITY", 8)) sendIdentity();
}

bool bleLinkConnected() { return connected; }

void bleLinkFillStatus(BleStatusPayload &out) {
  out.flags = (uint8_t)((server ? BLE_ST_UP : 0) |
                        (connected ? BLE_ST_CONNECTED : 0) |
                        (haveIdentity ? BLE_ST_IDENTITY : 0));
  out.target = bleOtaTarget();
  out.owed = bleOtaOwed();
  out.dropped = bleOtaDropped() + stageDrops;
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
                bleOtaTarget(), bleOtaOwed(), (unsigned long)(bleOtaDropped() + stageDrops));
}
