#include <Arduino.h>
#include <NimBLEDevice.h>
#include <esp_mac.h>

#include "ble_link.h"
#include "base_link.h"
#include "ble_ota.h"
#include "ble_image.h"
#include "fw_version.h"

// ESP's connection reattempt restarts advertising from a field set this code
// never fills, and leaves an empty advertisement on air. platformio.ini
// compiles it out; a build that has it back does not build.
#if !defined(MYNEWT_VAL_BLE_ENABLE_CONN_REATTEMPT) || MYNEWT_VAL_BLE_ENABLE_CONN_REATTEMPT
#error "esp32s3_faucet needs -DMYNEWT_VAL_BLE_ENABLE_CONN_REATTEMPT=0 (platformio.ini)"
#endif

// Nordic UART Service — the same three UUIDs the iOS app already knows.
static const char *NUS_SERVICE = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E";
static const char *NUS_RX      = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E";
static const char *NUS_TX      = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E";

// 0xFFFF is the company id reserved for a device that has none.
static const uint16_t MFG_ID = 0xFFFF;

static const uint8_t BLE_TEXT = 0x01;

static NimBLEServer         *server = nullptr;
static NimBLECharacteristic *txChar = nullptr;
/// Any phone on. loop()'s, from the links below.
static bool                  connected = false;
/// What `adv->start()` last said, which is not the same as the stack existing.
static bool                  advertising = false;
/// A radio-bench run has BLE off the air, and nothing here puts it back.
static bool                  quiet = false;
/// A phone let go. Set on the NimBLE task, acted on in loop().
static volatile bool         restartOwed = false;
/// When advertising was first found stopped with no phone on, or 0.
static uint32_t              offAirSinceMs = 0;
static uint32_t              offAirRestarts = 0;
static const uint32_t        OFF_AIR_GRACE_MS = 1000;

// How often the controller is told again what this board advertises.
static const uint32_t PAYLOAD_REASSERT_MS = 10000;
static uint32_t       payloadPushedAtMs = 0;
static uint32_t       payloadRefusals = 0;

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
  uint16_t conn;   // the link it arrived on
  uint8_t  data[RX_FRAME];
};
static RxFrame ring[RX_RING];
static volatile uint8_t rxHead = 0;   // the radio task writes here
static volatile uint8_t rxTail = 0;   // loop() reads from here
static uint32_t stageDrops = 0;

// ── The links, and the one that is the session ───────────────────────────
//
// NimBLE takes three at once, and this board advertises while there is room
// for another, so a second phone — or a laptop — can be on while the first is
// mid-transfer. The frame protocol has one phone in it at a time: one OTA
// session, one picture in flight. So one link is the session: a transfer's
// frames are sized to its MTU and go to it alone, and only its leaving ends
// what was in flight. A frame from another link makes that link the session
// when nothing is in flight. A reply goes back down the link that asked, a
// picture read back to the phone reading it, and what the machine holds to
// every link that can carry it — see notify.
//
// The NimBLE task only writes down which links exist and what each negotiated.
// loop() decides the session and tells the OTA and picture paths, which reach
// flash, J3 and the glass.
struct Link {
  uint16_t handle;   // BLE_HS_CONN_HANDLE_NONE when the row is empty
  uint16_t mtu;
  uint32_t gen;      // which connection, since a handle is used again
};
static portMUX_TYPE linksMux = portMUX_INITIALIZER_UNLOCKED;
static Link         links[CONFIG_BT_NIMBLE_MAX_CONNECTIONS];
static uint32_t     linkGen = 0;

static uint8_t  linkCount = 0;   // loop()'s, from settleLinks
static uint16_t session = BLE_HS_CONN_HANDLE_NONE;
static uint32_t sessionGen = 0;
/// The link whose frame is being handled, while dispatchFrame runs.
static uint16_t replyTo = BLE_HS_CONN_HANDLE_NONE;

// What the session's link has actually negotiated. A notification larger than
// that is truncated by the host stack rather than split — the phone gets a frame
// header promising more bytes than arrived, and nothing later can put that right.
static uint16_t linkMtu = 23;

static void linkUp(uint16_t handle) {
  portENTER_CRITICAL(&linksMux);
  for (Link &l : links) {
    if (l.handle != BLE_HS_CONN_HANDLE_NONE) continue;
    l = {handle, 23, ++linkGen};
    break;
  }
  portEXIT_CRITICAL(&linksMux);
}

static void linkMtuIs(uint16_t handle, uint16_t mtu) {
  portENTER_CRITICAL(&linksMux);
  for (Link &l : links)
    if (l.handle == handle) l.mtu = mtu;
  portEXIT_CRITICAL(&linksMux);
}

static void linkDown(uint16_t handle) {
  portENTER_CRITICAL(&linksMux);
  for (Link &l : links)
    if (l.handle == handle) l.handle = BLE_HS_CONN_HANDLE_NONE;
  portEXIT_CRITICAL(&linksMux);
}

static bool linkFind(uint16_t handle, Link &out) {
  bool found = false;
  portENTER_CRITICAL(&linksMux);
  for (const Link &l : links) {
    if (l.handle == BLE_HS_CONN_HANDLE_NONE || l.handle != handle) continue;
    out = l;
    found = true;
  }
  portEXIT_CRITICAL(&linksMux);
  return found;
}

static void useMtu(uint16_t mtu) {
  if (mtu == linkMtu) return;
  linkMtu = mtu;
  bleOtaSetMtu(mtu);
  Serial.printf("BLE: MTU %u\n", mtu);
}

static void adopt(const Link &l) {
  session = l.handle;
  sessionGen = l.gen;
  useMtu(l.mtu);
}

// Once a pass, before anything is sent: which links are up, whether the
// session is still one of them, and the MTU frames are sized to.
static void settleLinks() {
  Link now[CONFIG_BT_NIMBLE_MAX_CONNECTIONS];
  portENTER_CRITICAL(&linksMux);
  memcpy(now, links, sizeof(now));
  portEXIT_CRITICAL(&linksMux);

  const Link *first = nullptr;
  const Link *held = nullptr;
  linkCount = 0;
  for (const Link &l : now) {
    if (l.handle == BLE_HS_CONN_HANDLE_NONE) continue;
    ++linkCount;
    if (!first) first = &l;
    if (l.handle == session && l.gen == sessionGen) held = &l;
  }
  connected = first != nullptr;

  if (session != BLE_HS_CONN_HANDLE_NONE && !held) {
    // What was in flight was the phone's that left, and no one else's.
    session = BLE_HS_CONN_HANDLE_NONE;
    bleOtaDisconnected();
    bleImageDisconnected();
  }
  if (held) useMtu(held->mtu);
  else if (first) adopt(*first);
  else useMtu(23);   // the next phone negotiates its own
}

// A frame from a link that is not the session makes it the session, unless the
// session has something in flight. Whether the link is the session once heard.
static bool heardFrom(uint16_t handle) {
  if (handle == session) return true;
  if (bleOtaTarget() != OTA_TGT_NONE || bleImageBusy()) return false;
  Link l;
  if (!linkFind(handle, l)) return false;
  adopt(l);
  return true;
}

// A TRANSFER BELONGS TO THE SESSION. The OTA and picture paths each hold one
// transfer's state, so a second phone's frames would write into the first
// one's: its picture into the middle of another slot, its BEGIN ending an
// update it never started. While the session has one in flight, another
// link's BEGIN is told the board is busy and the rest of what it sends toward
// a transfer is not heard.
static bool transferFrame(uint8_t type) {
  return type == BLE_FRAME_OTA_BEGIN || type == BLE_FRAME_OTA_DATA ||
         type == BLE_FRAME_IMG_BEGIN || type == BLE_FRAME_IMG_DATA ||
         type == BLE_FRAME_IMG_END || type == BLE_FRAME_IMG_ABORT ||
         type == BLE_FRAME_IMG_ERASE;
}

// What the transfer in flight says, which only the phone running it is asking
// for: the OTA's asks and its end, a picture's acks and its read-back.
static bool sessionFrame(uint8_t type) {
  return type == BLE_FRAME_OTA_NEED || type == BLE_FRAME_OTA_END || type == BLE_FRAME_IMG_ACK;
}

// What the machine holds is every phone's news, whoever's frame changed it: a
// phone that did not hear a slot fill would offer it as free.
static bool everyoneFrame(uint8_t type) {
  return type == BLE_FRAME_IMG_STATE || type == BLE_FRAME_ART_STATE ||
         type == BLE_FRAME_VERSIONS;
}

// A PICTURE READ BACK GOES TO THE PHONE THAT ASKED FOR IT, at that link's own
// MTU. Reading is no transfer in flight — any phone may ask while another
// updates — so it is not the session's.
static uint16_t reader = BLE_HS_CONN_HANDLE_NONE;
static uint32_t readerGen = 0;

static void readAskedOn(uint16_t handle) {
  Link l;
  if (!linkFind(handle, l)) return;
  reader = l.handle;
  readerGen = l.gen;
  bleImageSetMtu(l.mtu);
}

// A picture read back out of flash is the largest thing sent this way now, and
// it is sent a full MTU at a time — so this carries one, and says whether the
// stack took it. A reader that cannot tell has no way to pace itself, and this
// used to answer an oversized frame by silently dropping it.
//
// A FRAME THE LINK CANNOT CARRY IS NOT SENT AT ALL. Refusing it here is the
// difference between a caller that knows to ask again and a phone handed a
// header for bytes that were cut off in the radio.
//
// A reply goes down the link that asked, and what that link took is the
// answer. What a transfer says goes to the session alone, and a picture read
// back to the phone reading it. What the machine holds, and anything else,
// goes to every link that can carry it, and what the session took is the answer.
static bool fits(uint16_t len, uint16_t mtu) { return (uint32_t)len + 3 <= (uint32_t)mtu - 3; }

static bool notify(uint8_t type, const void *data, uint16_t len) {
  if (!txChar) return false;
  uint8_t frame[3 + 560];
  if (len > sizeof(frame) - 3) return false;
  frame[0] = type;
  frame[1] = (uint8_t)(len & 0xFF);
  frame[2] = (uint8_t)(len >> 8);
  if (len) memcpy(frame + 3, data, len);
  txChar->setValue(frame, 3 + len);

  if (replyTo != BLE_HS_CONN_HANDLE_NONE && !everyoneFrame(type)) {
    Link l;
    if (!linkFind(replyTo, l) || !fits(len, l.mtu)) return false;
    return txChar->notify(replyTo);
  }

  if (type == BLE_FRAME_IMG_PIX) {
    Link l;
    if (!linkFind(reader, l) || l.gen != readerGen || !fits(len, l.mtu)) return false;
    return txChar->notify(reader);
  }

  if (sessionFrame(type)) {
    if (session == BLE_HS_CONN_HANDLE_NONE || !fits(len, linkMtu)) return false;
    return txChar->notify(session);
  }

  Link now[CONFIG_BT_NIMBLE_MAX_CONNECTIONS];
  portENTER_CRITICAL(&linksMux);
  memcpy(now, links, sizeof(now));
  portEXIT_CRITICAL(&linksMux);
  bool took = false;
  for (const Link &l : now) {
    if (l.handle == BLE_HS_CONN_HANDLE_NONE || !fits(len, l.mtu)) continue;
    const bool sent = txChar->notify(l.handle);
    if (l.handle == session) took = sent;
  }
  return took;
}

// One line to the phone, in the text vocabulary it already reads.
static void sayToPhone(const char *text) { notify(BLE_TEXT, text, (uint16_t)strlen(text)); }

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
  size_t vlen = strlen(FW_VERSION);
  if (vlen > 31) vlen = 31;
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

// WHICH MACHINE THIS IS RIDES THE SAME PACKET AS THE SERVICE UUID.
//
// A phone scans for one service and iOS hands the app only the packets that
// carry it. The scan response arrives as its own report with no service UUID in
// it, so a filtered scan drops it whole and everything written there is unread.
//
// The primary advertisement holds all three: 3 bytes of flags, 18 for the
// 128-bit service UUID, 8 for the manufacturer block — 29 of the 31 there are.
// The name is what the scan response carries, and nothing the phone needs to
// find this machine depends on that report arriving.
//
// THE CONTROLLER IS TOLD AGAIN, EVERY TEN SECONDS, WHAT TO SAY. It keeps its own
// copy of both payloads and nothing on this side can read that copy back.
// Anything in the stack that writes the advertisement behind this code — ESP's
// connection reattempt is one, and platformio.ini compiles it out — leaves the
// controller advertising whatever it wrote: connectable, on air,
// ble_gap_adv_active() true. An empty one leaves the scan response alone on
// air: a name, no flags, no service, no unit. A phone filtering on the service
// never sees one of those packets, and every check on this board says
// advertising. Writing both payloads again is one HCI command each, legal while
// advertising runs, and it bounds that state to ten seconds whatever wrote it.
static bool pushPayloads() {
  char name[32];
  advertisedName(name, sizeof(name));

  uint8_t mfg[6];
  mfg[0] = (uint8_t)(MFG_ID & 0xFF);
  mfg[1] = (uint8_t)(MFG_ID >> 8);
  mfg[2] = haveIdentity ? identity.model : 0;
  memcpy(mfg + 3, haveIdentity ? identity.unit : (const uint8_t *)"\0\0\0", 3);

  NimBLEAdvertisementData primary;
  primary.setFlags(BLE_HS_ADV_F_DISC_GEN | BLE_HS_ADV_F_BREDR_UNSUP);
  primary.addServiceUUID(NimBLEUUID(NUS_SERVICE));
  primary.setManufacturerData(mfg, sizeof(mfg));

  NimBLEAdvertisementData scan;
  scan.setName(name);

  NimBLEAdvertising *adv = NimBLEDevice::getAdvertising();
  const bool primaryTaken = adv->setAdvertisementData(primary);
  const bool scanTaken = adv->setScanResponseData(scan);
  payloadPushedAtMs = millis();
  if (primaryTaken && scanTaken) return true;

  ++payloadRefusals;
  char line[80];
  snprintf(line, sizeof(line), "BLE: the controller refused the %s (%lu so far)",
           !primaryTaken ? "advertisement" : "scan response", (unsigned long)payloadRefusals);
  Serial.println(line);
  baseLinkSay(line);
  return false;
}

// Stopped, both payloads written, started. A payload the controller would not
// take is not advertised over: the start waits for the next service pass to
// write it again.
//
// At the stack's own pace with no phone on — 30 to 60 ms — and every 400 to
// 500 ms beside one, so a phone arriving still finds the machine in a second or
// so and the one already on keeps the air for its transfer.
static void applyAdvertising() {
  NimBLEAdvertising *adv = NimBLEDevice::getAdvertising();
  adv->stop();
  adv->setMinInterval(connected ? 640 : 0);   // 0.625 ms units; 0 is the stack's default
  adv->setMaxInterval(connected ? 800 : 0);

  char name[32];
  advertisedName(name, sizeof(name));
  NimBLEDevice::setDeviceName(name);

  advertising = pushPayloads() && adv->start();
  Serial.printf("BLE: %s as '%s'\n",
                advertising ? "advertising" : "ADVERTISING REFUSED", name);
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
  }
  // Every answer reaches the phone, not only a changed one: a name it just sent
  // is confirmed whether or not it differs from the one the machine had.
  sendIdentity();
}

void bleLinkOnSrcNeed(uint32_t offset, uint16_t len) { bleOtaOnSrcNeed(offset, len); }
void bleLinkOnSrcEnd(const OtaStatePayload &state)   { bleOtaOnSrcEnd(state); }

// ── NimBLE callbacks ──────────────────────────────────────────────────────
class RxCB : public NimBLECharacteristicCallbacks {
  void onWrite(NimBLECharacteristic *chr, NimBLEConnInfo &info) override {
    NimBLEAttValue raw = chr->getValue();
    const uint8_t next = (uint8_t)((rxHead + 1) % RX_RING);
    if (raw.length() > RX_FRAME || next == rxTail) { ++stageDrops; return; }
    memcpy(ring[rxHead].data, raw.data(), raw.length());
    ring[rxHead].len = (uint16_t)raw.length();
    ring[rxHead].conn = info.getConnHandle();
    rxHead = next;   // last, so a reader never sees a frame before its bytes
  }
};

// Everything here runs on the NimBLE task. It writes down what happened to
// which link and leaves the rest to loop(): see settleLinks.
class ServerCB : public NimBLEServerCallbacks {
  void onConnect(NimBLEServer *, NimBLEConnInfo &info) override {
    linkUp(info.getConnHandle());
    Serial.println("BLE: connected");
    versionsAskedAtMs = 0;
    restartOwed = true;   // taking the connection stopped advertising
    // The pull costs one round trip per frame, so the connection interval is
    // the transfer rate. Ask for the shortest iOS grants.
    server->updateConnParams(info.getConnHandle(), 12, 24, 0, 200);
  }
  void onDisconnect(NimBLEServer *, NimBLEConnInfo &info, int reason) override {
    linkDown(info.getConnHandle());
    Serial.printf("BLE: disconnected, reason 0x%x\n", reason);
    // ADVERTISING IS loop()'S ALONE. This runs on the NimBLE task, and a start
    // from here races whatever loop() is doing to the same advertising object —
    // so this only says it is owed, and the next service pass writes both
    // payloads and starts.
    restartOwed = true;
  }
  void onMTUChange(uint16_t mtu, NimBLEConnInfo &info) override {
    linkMtuIs(info.getConnHandle(), mtu);
  }
};

void bleLinkBegin() {
  for (Link &l : links) l.handle = BLE_HS_CONN_HANDLE_NONE;

  char name[32];
  advertisedName(name, sizeof(name));
  NimBLEDevice::init(name);
  NimBLEDevice::setMTU(517);
  NimBLEDevice::setPower(ESP_PWR_LVL_P9);

  server = NimBLEDevice::createServer();
  server->setCallbacks(new ServerCB());
  server->advertiseOnDisconnect(false);   // loop() restarts it: see onDisconnect

  // On for good, so a start NimBLE makes on its own after a host reset writes
  // the scan response back along with the advertisement.
  NimBLEDevice::getAdvertising()->enableScanResponse(true);

  NimBLEService *svc = server->createService(NUS_SERVICE);
  txChar = svc->createCharacteristic(NUS_TX, NIMBLE_PROPERTY::NOTIFY);
  NimBLECharacteristic *rx =
      svc->createCharacteristic(NUS_RX, NIMBLE_PROPERTY::WRITE | NIMBLE_PROPERTY::WRITE_NR);
  rx->setCallbacks(new RxCB());

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

static uint32_t lastTouchTxMs = 0;

static void dispatchFrame(const uint8_t *work, uint16_t len) {
  if (len < 3) return;
  const uint8_t type = work[0];
  const uint16_t plen = (uint16_t)(work[1] | (work[2] << 8));
  if (3 + plen > len) return;
  const uint8_t *payload = work + 3;

  // THE PHONE IS A FINGER ON THIS MACHINE. Someone holding it is someone using
  // the machine, so anything it says holds both glasses lit exactly the way a
  // touch does. The main board owns the only sleep clock either display has,
  // and MSG_TOUCH is already what it reads as presence — so this needs no new
  // message and no phone change, only for the traffic to be counted.
  //
  // Once a second. An upload delivers hundreds of frames a second down this
  // same wire, and the window one touch holds open is sixty.
  const uint32_t now = millis();
  if (now - lastTouchTxMs >= 1000) {
    lastTouchTxMs = now;
    baseLinkTouched();
  }

  if (bleOtaHandleFrame(type, payload, plen)) return;
  if (bleImageHandleFrame(type, payload, plen)) return;
  if (type == BLE_TEXT && plen == 8 && !memcmp(payload, "IDENTITY", 8)) {
    sendIdentity();
    sendVersions();
    versionsAskedAtMs = 0;   // and ask the main board again, in case it has news
    return;
  }

  // `IDENTITY <name>`: the console's own verb, from the phone. The name is the
  // main board's to keep, so it crosses J3 as MSG_IDENTITY_SET and comes back
  // as the MSG_RESP_IDENTITY a query gets — which re-advertises and sends the
  // phone its identity frame. The bytes after the space are the name, as they
  // are, clipped to MACHINE_NAME_MAX; none of them clears it. A machine the
  // phone cannot name is told so, rather than left waiting for a frame.
  if (type == BLE_TEXT && plen >= 9 && !memcmp(payload, "IDENTITY ", 9)) {
    IdentityNamePayload req{};
    const uint16_t n = plen - 9 < MACHINE_NAME_MAX ? (uint16_t)(plen - 9) : MACHINE_NAME_MAX;
    memcpy(req.name, payload + 9, n);
    BaseLinkStatus st;
    baseLinkReadStatus(st);
    if (!st.connected) sayToPhone("ERR:IDENTITY:LINK_DOWN");
    else if (!baseLinkSendOtaSrc(MSG_IDENTITY_SET, &req, sizeof(req))) sayToPhone("ERR:IDENTITY:BUSY");
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
  settleLinks();
  bleOtaService();
  bleImageService();   // whatever a read-back still owes the phone

  // A RADIO THAT HAS STOPPED IS A MACHINE NO PHONE CAN FIND, and nothing else
  // on this board reads it. It advertises whenever there is room for another
  // phone: one already on — mid-update, or just open — does not hide the
  // machine from the next. Advertising goes back on the moment
  // a phone arrives or leaves, and a second after it is found stopped with room
  // — except through a bench run, whose whole point is BLE off the air.
  //
  // The second is what a phone whose connection broke while it was being set up
  // leaves behind: the controller stopped advertising to take the connection,
  // and the host told nobody about either the connection or its end.
  if (!quiet) {
    const bool room = linkCount < CONFIG_BT_NIMBLE_MAX_CONNECTIONS;
    const bool onAir = !room || NimBLEDevice::getAdvertising()->isAdvertising();
    if (onAir) offAirSinceMs = 0;
    else if (!offAirSinceMs) offAirSinceMs = millis() | 1;

    const bool stranded = offAirSinceMs && millis() - offAirSinceMs >= OFF_AIR_GRACE_MS;
    if (restartOwed || stranded) {
      restartOwed = false;
      offAirSinceMs = 0;
      // Through applyAdvertising even when already on air: a phone arriving or
      // leaving changes the pace it advertises at.
      if (room) applyAdvertising();
      if (room && stranded && !connected) {
        char line[64];
        snprintf(line, sizeof(line), "BLE: found off air with no phone, advertising again (%lu)",
                 (unsigned long)++offAirRestarts);
        baseLinkSay(line);
      }
    }
    if (millis() - payloadPushedAtMs >= PAYLOAD_REASSERT_MS) pushPayloads();
  }

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
    const bool owns = heardFrom(f.conn);
    replyTo = f.conn;
    if (owns || f.len < 3 || !transferFrame(f.data[0])) {
      // A read the board refused leaves the one already running where it was.
      const uint32_t readsBefore = bleImageReadsBegun();
      dispatchFrame(f.data, f.len);
      if (bleImageReadsBegun() != readsBefore) readAskedOn(f.conn);
    } else if (f.data[0] == BLE_FRAME_IMG_BEGIN && f.len >= 4) {
      // FAILED rather than TAKING: the phone reads TAKING as "send from here".
      BleImgAck ack{f.data[3], BLE_IMG_FAILED, BLE_IMG_ERR_BUSY, 0};
      notify(BLE_FRAME_IMG_ACK, &ack, sizeof(ack));
    } else if (f.data[0] == BLE_FRAME_OTA_BEGIN) {
      OtaStatePayload st{OTA_STATE_FAILED, OTA_ERR_BUSY, 0};
      notify(BLE_FRAME_OTA_END, &st, sizeof(st));
    }
    replyTo = BLE_HS_CONN_HANDLE_NONE;
    rxTail = (uint8_t)((rxTail + 1) % RX_RING);
  }
}

void bleLinkQuiet(bool off) {
  quiet = off;
  if (off) {
    NimBLEDevice::stopAdvertising();
    advertising = false;
  } else {
    // Through applyAdvertising: it puts the payloads on again and keeps what
    // start() said.
    applyAdvertising();
  }
}

bool bleLinkConnected() { return connected; }

void bleLinkFillStatus(BleStatusPayload &out) {
  // ON AIR, which is what a phone in the room can act on. A stack that exists
  // is not a radio that is advertising.
  const bool onAir = connected || (server && NimBLEDevice::getAdvertising()->isAdvertising());
  out.flags = (uint8_t)((onAir ? BLE_ST_UP : 0) |
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
                connected ? "connected"
                          : NimBLEDevice::getAdvertising()->isAdvertising() ? "advertising"
                                                                           : "OFF AIR", name,
                haveIdentity ? "known" : "unanswered",
                bleOtaTarget(), bleOtaOwed(), (unsigned long)(bleOtaDropped() + stageDrops));
  Serial.printf("     payloads written %lu ms ago, refused %lu times%s\n",
                (unsigned long)(millis() - payloadPushedAtMs), (unsigned long)payloadRefusals,
                quiet ? ", quiet for a bench run" : "");
}
