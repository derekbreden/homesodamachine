#pragma once

#include <stdint.h>

#include "proto_msg.h"

// ════════════════════════════════════════════════════════════
//  Which phones may change the machine
// ════════════════════════════════════════════════════════════
//
// Every phone reads everything. Changing anything takes a phone this board
// trusts: a flavor on tap, a ratio, a picture, a cycle, the sound, the name,
// the software. A phone is trusted by a tap on either display, this board's or
// the enclosure's, which the main board carries the ask out to and the answer
// back from. A trusted phone is kept by its pairing, the identity address and
// the key of its bond, so it stays trusted through every later connection, a
// restart and an update. A phone that forgets the machine and pairs again is
// asked again, and the enclosure's settings forget every trusted phone at once.
//
// One ask is up at a time. Its first admission has an absolute one-minute
// ceiling. A leased ask also needs a heartbeat within fifteen seconds. A
// physical decline pauses that phone and, briefly, every new request; failed
// requests never extend that pause. Rate state is local to this boot.

constexpr uint8_t BLE_FRAME_TRUST     = 0x26;  // board → phone: BleTrustPayload
constexpr uint8_t BLE_FRAME_TRUST_ASK = 0x27;  // phone → board: BleTrustAskPayload

constexpr uint8_t TRUST_STATE_UNPAIRED = 0;  // no bond yet, so nothing to know the phone by
constexpr uint8_t TRUST_STATE_VIEWER   = 1;  // bonded, not trusted: reads only
constexpr uint8_t TRUST_STATE_TRUSTED  = 2;

constexpr uint8_t TRUST_OUTCOME_NONE      = 0;  // where the phone stands, not the end of an ask
constexpr uint8_t TRUST_OUTCOME_TRUSTED   = 1;
constexpr uint8_t TRUST_OUTCOME_DECLINED  = 2;  // Don't Trust, on either display
constexpr uint8_t TRUST_OUTCOME_TIMED_OUT = 3;
constexpr uint8_t TRUST_OUTCOME_BUSY      = 4;  // another phone's ask is up
constexpr uint8_t TRUST_OUTCOME_UNPAIRED  = 5;  // not bonded; the phone is asked to pair again
constexpr uint8_t TRUST_OUTCOME_CANCELED  = 6;  // the phone withdrew it

struct __attribute__((packed)) BleTrustPayload {
  uint8_t state;    // TRUST_STATE_*
  uint8_t asking;   // 1 while this phone's ask is on the displays
  uint8_t outcome;  // TRUST_OUTCOME_*
  uint16_t retryAfterSec;  // little-endian: a paused admission's remaining wait
  uint16_t remainingSec;   // this matching ask's absolute lifetime remaining
  uint8_t clientTag;       // 0 for a legacy request; otherwise its echoed attempt
};

constexpr uint8_t TRUST_CANCEL = 0xFF;  // as a reason: withdraw this phone's ask

struct __attribute__((packed)) BleTrustAskPayload {
  uint8_t reason;   // TRUST_FOR_*, or TRUST_CANCEL
  uint8_t channel;  // PUMP_CHANNEL_*, or UI_CHANNEL_NONE
  uint8_t kind;     // TRUST_KIND_*
  uint8_t flags;    // optional fourth byte: BLE_TRUST_ASK_LEASED
  uint8_t clientTag;  // optional fifth byte, nonzero for a new client attempt
};

constexpr uint32_t TRUST_ASK_MS = 60000;
constexpr uint8_t BLE_TRUST_ASK_PREFIX = 3;
constexpr uint8_t BLE_TRUST_ASK_LEASED = 1;
constexpr uint8_t  TRUST_MAX    = 16;   // as many as the radio keeps bonds for

struct PhoneId {
  uint8_t type;      // the identity address's type
  uint8_t addr[6];
};

void phoneTrustBegin();
bool phoneTrustKnows(const PhoneId &id);

// Moves whenever a phone is trusted or every one is forgotten, so a link's
// standing is worked out again only when it could have changed.
uint32_t phoneTrustGeneration();

// The ask, from the phone on `link` in connection `gen`, which is how its end
// finds the phone again. False while another attempt owns it or admission is
// paused; phoneTrustRefusal and phoneTrustRetryAfter describe that pause.
bool phoneTrustAsk(uint16_t link, uint32_t gen, const PhoneId &id, const BleTrustAskPayload &req);
bool phoneTrustAsking(uint16_t link, uint32_t gen);
uint8_t phoneTrustClientTag(uint16_t link, uint32_t gen);
uint8_t phoneTrustRefusal(const PhoneId &id);
uint16_t phoneTrustRetryAfter(uint16_t link, uint32_t gen, const PhoneId &id, uint8_t clientTag);
uint16_t phoneTrustRemaining(uint16_t link, uint32_t gen, uint8_t clientTag);
bool phoneTrustWithdraw(uint16_t link, uint32_t gen, uint8_t clientTag = 0);
void phoneTrustAnswer(uint8_t askId, bool trusted);   // a tap on either display; 0 is the console's
void phoneTrustService();                              // the minute, and a phone that left

uint8_t phoneTrustForget();   // every trusted phone; how many there were
void phoneTrustReport();      // one line on the main board's console

// The ask on this board's own glass. Defined in main.cpp, where the display lives.
void faucetTrustShow(const TrustShowPayload &ask);
void faucetTrustHide();
