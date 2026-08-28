#include <Arduino.h>
#include <NimBLEDevice.h>
#include <esp_mac.h>

#include "ble_link.h"
#include "base_link.h"
#include "ble_ota.h"
#include "ble_image.h"
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

static VersionsPayload versions{};
static bool            haveVersions = false;
static uint32_t        versionsAskedAtMs = 0;

// A write arrives on the NimBLE task; anything that touches flash, LVGL or J3
// has to happen in loop(). A ring rather than one slot, because one slot made
// the connection interval the transfer rate: the phone could not put a second
// frame on the air until this board had been round its whole loop once, so a
// picture crawled in at a frame per 15 ms no matter what the radio could do.
//
// Nothing is lost by dropping when it fills, either. Every frame carries its
// own offset, so a sender that overran this is told where the board actually
// got to and winds back — which is cheaper than making the phone wait for a
// board that is usually keeping up.
static const uint16_t RX_FRAME = 560;   // one full MTU's worth, and room over
static const uint8_t  RX_RING  = 12;
struct RxFrame {
  uint16_t len;
  uint8_t  data[RX_FRAME];
};
static RxFrame ring[RX_RING];
static volatile uint8_t rxHead = 0;   // the radio task writes here
static volatile uint8_t rxTail = 0;   // loop() reads from here
static uint32_t stageDrops = 0;

// A picture read back out of flash is the largest thing sent this way now, and
// it is sent a full MTU at a time — so this carries one, and says whether the
// stack took it. A reader that cannot tell has no way to pace itself, and this
// used to answer an oversized frame by silently dropping it.
static bool notify(uint8_t type, const void *data, uint16_t len) {
  if (!txChar || !connected) return false;
  uint8_t frame[3 + 560];
  if (len > sizeof(frame) - 3) return false;
  frame[0] = type;
  frame[1] = (uint8_t)(len & 0xFF);
  frame[2] = (uint8_t)(len >> 8);
  if (len) memcpy(frame + 3, data, len);
  txChar->setValue(frame, 3 + len);
  return txChar->notify();
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

// A phone asking whether a machine is current is asking about every board on
// it. An entry the main board has not been told about carries an empty string,
// which the phone reads as "has not said" rather than as current.
static void sendVersions() {
  if (!haveVersions) return;
  notify(BLE_FRAME_VERSIONS, &versions, sizeof(versions));
}

void bleLinkOnVersions(const VersionsPayload &all) {
  versions = all;
  haveVersions = true;
  // Sent on every answer rather than on a change. This frame is larger than the
  // default MTU carries, so the first one after a connection may not fit; the
  // poll behind it is what makes that heal instead of stranding the phone on a
  // machine whose versions it never learned.
  sendVersions();
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
    const uint8_t next = (uint8_t)((rxHead + 1) % RX_RING);
    if (raw.length() > RX_FRAME || next == rxTail) { ++stageDrops; return; }
    memcpy(ring[rxHead].data, raw.data(), raw.length());
    ring[rxHead].len = (uint16_t)raw.length();
    rxHead = next;   // last, so a reader never sees a frame before its bytes
  }
};

class ServerCB : public NimBLEServerCallbacks {
  void onConnect(NimBLEServer *, NimBLEConnInfo &info) override {
    connected = true;
    Serial.println("BLE: connected");
    versionsAskedAtMs = 0;
    // The pull costs one round trip per frame, so the connection interval is
    // the transfer rate. Ask for the shortest iOS grants.
    server->updateConnParams(info.getConnHandle(), 12, 24, 0, 200);
  }
  void onDisconnect(NimBLEServer *, NimBLEConnInfo &, int) override {
    connected = false;
    Serial.println("BLE: disconnected");
    bleOtaDisconnected();
    bleImageDisconnected();
    NimBLEDevice::startAdvertising();
  }
  void onMTUChange(uint16_t mtu, NimBLEConnInfo &) override {
    bleOtaSetMtu(mtu);
    bleImageSetMtu(mtu);
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

  BleImageSeams img{};
  img.notify = notify;
  img.onProgress = faucetApplyImage;
  img.onStoreMoved = faucetRebindLogos;
  img.setArt = faucetSetFlavorArt;
  img.readArt = faucetReadFlavorArt;
  img.onStored = faucetRequestRelay;
  img.onRead = faucetSayRead;
  img.onReadAsked = faucetSayReadAsked;
  img.onErased = faucetRequestErase;
  bleImageBegin(img);

  applyAdvertising();
  Serial.printf("BLE: advertising as '%s'\n", name);
}

static void dispatchFrame(const uint8_t *work, uint16_t len) {
  if (len < 3) return;
  const uint8_t type = work[0];
  const uint16_t plen = (uint16_t)(work[1] | (work[2] << 8));
  if (3 + plen > len) return;
  const uint8_t *payload = work + 3;

  if (bleOtaHandleFrame(type, payload, plen)) return;
  if (bleImageHandleFrame(type, payload, plen)) return;
  if (type == BLE_TEXT && plen >= 8 && !memcmp(payload, "IDENTITY", 8)) {
    sendIdentity();
    sendVersions();
    versionsAskedAtMs = 0;   // and ask the main board again, in case it has news
    return;
  }

  // Anything else the phone says goes to the main board's console. The phone is
  // the half of this machine with no wire on it, and its own log is not
  // reachable from a bench — so a decision it made silently, like declining to
  // ask for a picture, had no way of being seen at all.
  if (type == BLE_TEXT && plen) {
    char text[80];
    const uint16_t n = plen < sizeof(text) - 1 ? plen : (uint16_t)(sizeof(text) - 1);
    memcpy(text, payload, n);
    text[n] = '\0';
    char line[96];
    snprintf(line, sizeof(line), "[phone] %s", text);
    baseLinkSay(line);
  }
}

void bleLinkService() {
  bleOtaService();
  bleImageService();   // whatever a read-back still owes the phone

  // Until the main board answers, this board is advertising its own MAC rather
  // than the machine's. Ask again until it does.
  if (!haveIdentity && millis() - identityAskedAtMs >= 2000) {
    identityAskedAtMs = millis();
    baseLinkSendOtaSrc(MSG_IDENTITY_QUERY, nullptr, 0);
  }

  // Boards reboot into new images, so this is asked for again rather than once.
  if (millis() - versionsAskedAtMs >= (connected ? 5000UL : 30000UL)) {
    versionsAskedAtMs = millis();
    baseLinkSendOtaSrc(MSG_VERSIONS_QUERY, nullptr, 0);
  }

  // Everything the radio left, not one frame. Draining one per pass is what
  // made this board's own loop the ceiling on how fast a picture could arrive.
  while (rxTail != rxHead) {
    const RxFrame &f = ring[rxTail];
    dispatchFrame(f.data, f.len);
    rxTail = (uint8_t)((rxTail + 1) % RX_RING);
  }
}

void bleLinkQuiet(bool quiet) {
  if (quiet) NimBLEDevice::stopAdvertising();
  else       NimBLEDevice::startAdvertising();
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
