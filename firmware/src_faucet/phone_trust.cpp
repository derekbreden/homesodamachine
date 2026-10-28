#include "phone_trust.h"

#include <Arduino.h>
#include <NimBLEDevice.h>
#include <Preferences.h>
#include <string.h>

#include "base_link.h"
#include "ble_link.h"
#include "trust_policy.h"

namespace {

Preferences store;
bool        storeOpen = false;

// A trusted phone and the pairing it was trusted under.
struct Trusted {
  PhoneId  id;
  uint32_t pairing;   // pairingOf() when it was trusted
};

Trusted  trusted[TRUST_MAX];   // oldest first
uint8_t  trustedCount = 0;
uint32_t generation = 1;

struct Ask {
  uint8_t  id;       // 0 while no ask is up
  uint16_t link;
  uint32_t gen;
  PhoneId  phone;
  uint8_t clientTag;
  uint8_t reason, channel, kind;
  uint32_t shownAtMs;
};
Ask     ask{};
uint8_t lastAskId = 0;
phone_trust_policy::RequestWindow requestWindow;
phone_trust_policy::RateLimit rateLimit;

uint64_t phoneKey(const PhoneId &id) {
  uint64_t key = id.type;
  for (uint8_t b : id.addr) key = (key << 8) | b;
  return key;
}

void showAsk() {
  TrustShowPayload show{ask.id, ask.reason, ask.channel, ask.kind};
  faucetTrustShow(show);
  baseLinkSendTrust(MSG_TRUST_SHOW, &show, sizeof(show));
  ask.shownAtMs = millis();
}

bool same(const PhoneId &a, const PhoneId &b) {
  return a.type == b.type && memcmp(a.addr, b.addr, sizeof(a.addr)) == 0;
}

void say(const char *what, const PhoneId &id) {
  char line[64];
  snprintf(line, sizeof(line), "trust: phone %02X%02X%02X%02X%02X%02X %s",
           id.addr[5], id.addr[4], id.addr[3], id.addr[2], id.addr[1], id.addr[0], what);
  baseLinkSay(line);
}

// The key of the phone's bond, digested. Each pairing makes a new key, so a
// phone that forgot the machine and paired again no longer matches.
uint32_t pairingOf(const PhoneId &id) {
  ble_store_key_sec key{};
  key.peer_addr.type = id.type;
  memcpy(key.peer_addr.val, id.addr, sizeof(id.addr));
  ble_store_value_sec bond;
  if (ble_store_read_peer_sec(&key, &bond) != 0 || !bond.ltk_present) return 0;
  uint32_t h = 2166136261u;   // FNV-1a
  for (uint8_t b : bond.ltk) h = (h ^ b) * 16777619u;
  return h;
}

void save() {
  if (!storeOpen) return;
  if (trustedCount) store.putBytes("phones", trusted, sizeof(Trusted) * trustedCount);
  else store.remove("phones");
}

void drop(uint8_t i) {
  memmove(trusted + i, trusted + i + 1, sizeof(Trusted) * (trustedCount - i - 1));
  --trustedCount;
}

void add(const PhoneId &id) {
  if (phoneTrustKnows(id)) return;
  if (trustedCount == TRUST_MAX) drop(0);   // the oldest goes first, as its bond does
  trusted[trustedCount++] = Trusted{id, pairingOf(id)};
  ++generation;
  save();
}

// Every ask ends here: both displays let go of it, and the phone, if it is
// still on, hears how.
void end(uint8_t outcome, bool tellPhone) {
  if (!ask.id) return;
  const Ask done = ask;
  ask = Ask{};
  requestWindow.close();
  const uint32_t now = millis();
  if (outcome == TRUST_OUTCOME_TRUSTED) rateLimit.approved(phoneKey(done.phone), now);
  else if (outcome == TRUST_OUTCOME_DECLINED) rateLimit.declined(phoneKey(done.phone), now);
  else rateLimit.unsuccessful(now);
  faucetTrustHide();
  TrustClosePayload close{done.id};
  baseLinkSendTrust(MSG_TRUST_CLOSE, &close, sizeof(close));
  if (tellPhone) bleLinkTrustEnded(done.link, done.gen, outcome);
  static const char *const kEnd[] = {"left", "trusted", "not trusted", "not answered",
                                     "busy", "not paired", "withdrawn"};
  say(outcome < sizeof(kEnd) / sizeof(kEnd[0]) ? kEnd[outcome] : "ended", done.phone);
}

}  // namespace

void phoneTrustBegin() {
  storeOpen = store.begin("trust");
  if (!storeOpen) return;
  const size_t n = store.getBytesLength("phones");
  if (n && n % sizeof(Trusted) == 0 && n <= sizeof(trusted)) {
    store.getBytes("phones", trusted, n);
    trustedCount = (uint8_t)(n / sizeof(Trusted));
  }
}

bool phoneTrustKnows(const PhoneId &id) {
  for (uint8_t i = 0; i < trustedCount; i++) {
    if (!same(trusted[i].id, id)) continue;
    if (trusted[i].pairing == pairingOf(id)) return true;
    drop(i);   // trusted under a pairing the phone has since let go of
    save();
    return false;
  }
  return false;
}

uint32_t phoneTrustGeneration() { return generation; }

bool phoneTrustAsk(uint16_t link, uint32_t gen, const PhoneId &id, const BleTrustAskPayload &req) {
  phoneTrustService();
  const uint32_t now = millis();
  if (ask.id) {
    if (ask.link != link || ask.gen != gen || ask.clientTag != req.clientTag) return false;
    // A heartbeat preserves the same question, touch targets and first-show
    // deadline. Replaying its state lets an unavailable display catch up.
    if (!requestWindow.renew(now)) return false;
    if (now - ask.shownAtMs >= 1000) showAsk();
    return true;
  }
  if (!rateLimit.check(phoneKey(id), now).allowed()) return false;
  lastAskId = (uint8_t)(lastAskId + 1);
  if (!lastAskId) lastAskId = 1;
  ask = Ask{lastAskId, link, gen, id, req.clientTag,
            req.reason, req.channel, req.kind, now};
  requestWindow.open(now, (req.flags & BLE_TRUST_ASK_LEASED) && req.clientTag != 0);
  rateLimit.admitted(phoneKey(id), now);
  say("asked", id);
  showAsk();
  return true;
}

bool phoneTrustAsking(uint16_t link, uint32_t gen) {
  return ask.id && ask.link == link && ask.gen == gen;
}

uint8_t phoneTrustClientTag(uint16_t link, uint32_t gen) {
  return phoneTrustAsking(link, gen) ? ask.clientTag : 0;
}

uint8_t phoneTrustRefusal(const PhoneId &id) {
  return rateLimit.check(phoneKey(id), millis()).refusal == phone_trust_policy::Refusal::declined
             ? TRUST_OUTCOME_DECLINED : TRUST_OUTCOME_BUSY;
}

uint16_t phoneTrustRetryAfter(uint16_t link, uint32_t gen, const PhoneId &id, uint8_t clientTag) {
  const uint32_t now = millis();
  if (phoneTrustAsking(link, gen) && ask.clientTag == clientTag) return 0;
  uint32_t wait = rateLimit.check(phoneKey(id), now).retryMs;
  if (ask.id) {
    const uint32_t owner = requestWindow.remaining(now) + phone_trust_policy::kQuietMs;
    if (owner > wait) wait = owner;
  }
  return phone_trust_policy::seconds(wait);
}

uint16_t phoneTrustRemaining(uint16_t link, uint32_t gen, uint8_t clientTag) {
  return phoneTrustAsking(link, gen) && ask.clientTag == clientTag
             ? phone_trust_policy::seconds(requestWindow.remaining(millis())) : 0;
}

bool phoneTrustWithdraw(uint16_t link, uint32_t gen, uint8_t clientTag) {
  if (!phoneTrustAsking(link, gen) || ask.clientTag != clientTag) return false;
  end(TRUST_OUTCOME_CANCELED, true);
  return true;
}

void phoneTrustAnswer(uint8_t askId, bool trust) {
  phoneTrustService();
  if (!ask.id || (askId && askId != ask.id)) return;
  if (trust) add(ask.phone);
  end(trust ? TRUST_OUTCOME_TRUSTED : TRUST_OUTCOME_DECLINED, true);
}

void phoneTrustService() {
  const uint32_t now = millis();
  rateLimit.service(now);
  if (!ask.id) return;
  if (requestWindow.expired(now)) end(TRUST_OUTCOME_TIMED_OUT, true);
  else if (!bleLinkUp(ask.link, ask.gen)) end(TRUST_OUTCOME_NONE, false);
  else if (now - ask.shownAtMs >= 5000) showAsk();
}

uint8_t phoneTrustForget() {
  const uint8_t n = trustedCount;
  trustedCount = 0;
  ++generation;
  save();
  char line[48];
  snprintf(line, sizeof(line), "trust: forgot %u phone%s", n, n == 1 ? "" : "s");
  baseLinkSay(line);
  return n;
}

void phoneTrustReport() {
  char line[80];
  snprintf(line, sizeof(line), "trust: %u trusted phone%s, %d bonded%s", trustedCount,
           trustedCount == 1 ? "" : "s", NimBLEDevice::getNumBonds(), ask.id ? "; an ask is up" : "");
  baseLinkSay(line);
}
