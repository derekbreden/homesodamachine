#include "phone_trust.h"

#include <Arduino.h>
#include <NimBLEDevice.h>
#include <Preferences.h>
#include <string.h>

#include "base_link.h"
#include "ble_link.h"

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
  uint32_t sinceMs;
};
Ask     ask{};
uint8_t lastAskId = 0;

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
  const bool mine = ask.id && ask.link == link && ask.gen == gen;
  if (ask.id && !mine) return false;
  if (!mine) {
    lastAskId = (uint8_t)(lastAskId + 1);
    if (!lastAskId) lastAskId = 1;
    ask = Ask{lastAskId, link, gen, id, 0};
    say("asked", id);
  }
  ask.sinceMs = millis();   // asking again is a fresh minute
  TrustShowPayload show{ask.id, req.reason, req.channel, req.kind};
  faucetTrustShow(show);
  baseLinkSendTrust(MSG_TRUST_SHOW, &show, sizeof(show));
  return true;
}

bool phoneTrustAsking(uint16_t link, uint32_t gen) {
  return ask.id && ask.link == link && ask.gen == gen;
}

void phoneTrustWithdraw(uint16_t link, uint32_t gen) {
  if (phoneTrustAsking(link, gen)) end(TRUST_OUTCOME_CANCELED, true);
}

void phoneTrustAnswer(uint8_t askId, bool trust) {
  if (!ask.id || (askId && askId != ask.id)) return;
  if (trust) add(ask.phone);
  end(trust ? TRUST_OUTCOME_TRUSTED : TRUST_OUTCOME_DECLINED, true);
}

void phoneTrustService() {
  if (!ask.id) return;
  if (millis() - ask.sinceMs >= TRUST_ASK_MS) end(TRUST_OUTCOME_TIMED_OUT, true);
  else if (!bleLinkUp(ask.link, ask.gen)) end(TRUST_OUTCOME_NONE, false);
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
