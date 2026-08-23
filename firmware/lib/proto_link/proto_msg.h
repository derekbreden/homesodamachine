#pragma once

#include <stdint.h>
#include <string.h>

// ════════════════════════════════════════════════════════════
//  Message type constants for inter-MCU protocol over TinyProto
// ════════════════════════════════════════════════════════════
//
// Each message is sent as a TinyProto I-frame with the message
// type in payload[0] and application data in payload[1..N].
//
// Image uploads use a state-based protocol: after MSG_UPLOAD_START,
// all subsequent frames are raw image data (no type byte) until
// expectedSize bytes are received, followed by MSG_UPLOAD_DONE.
// TinyProto handles fragmentation, acking, and retransmission
// internally — no per-chunk acks or sequence numbers needed.

// Commands (ESP32 → device)
constexpr uint8_t MSG_UPLOAD_START     = 0x01;
// 0x02 reserved
constexpr uint8_t MSG_UPLOAD_DONE      = 0x03;
constexpr uint8_t MSG_QUERY_COUNT      = 0x04;
constexpr uint8_t MSG_DELETE_IMAGE     = 0x05;
constexpr uint8_t MSG_SWAP_IMAGES      = 0x06;
constexpr uint8_t MSG_UPLOAD_PNG_START = 0x07;
constexpr uint8_t MSG_UPLOAD_RP_START  = 0x08;
constexpr uint8_t MSG_DEVICE_READY     = 0x09;  // device → ESP32: "I'm ready" + image count
constexpr uint8_t MSG_PUMP_RUN         = 0x0A;  // display → ESP32: run one pump now
constexpr uint8_t MSG_PRIME_START      = 0x0B;  // ChannelPayload: begin priming, finger down
constexpr uint8_t MSG_PRIME_TICK       = 0x0C;  // ChannelPayload: still held (every PRIME_TICK_MS)
constexpr uint8_t MSG_PRIME_STOP       = 0x0D;  // ChannelPayload: finger up
constexpr uint8_t MSG_STATUS_REQ       = 0x0E;  // no payload: answer with StatusPayload
constexpr uint8_t MSG_CLEAN_START      = 0x0F;  // ChannelPayload: run the clean cycle

// Responses (device → ESP32)
constexpr uint8_t MSG_RESP_READY       = 0x10;
// 0x11 reserved
constexpr uint8_t MSG_RESP_UPLOAD_OK   = 0x12;
constexpr uint8_t MSG_RESP_DELETE_OK   = 0x13;
constexpr uint8_t MSG_RESP_COUNT       = 0x14;
constexpr uint8_t MSG_RESP_SWAP_OK     = 0x15;
constexpr uint8_t MSG_RESP_PUMP_DONE   = 0x16;  // ResponsePayload: the channel that ran
constexpr uint8_t MSG_RESP_PRIME       = 0x17;  // PrimeStatePayload: every prime state change
constexpr uint8_t MSG_RESP_STATUS      = 0x18;  // StatusPayload

// Error responses (device → ESP32)
constexpr uint8_t MSG_ERR_SLOT_INVALID   = 0xE1;
constexpr uint8_t MSG_ERR_NO_SPACE       = 0xE2;
constexpr uint8_t MSG_ERR_BUSY           = 0xE3;
// 0xE4, 0xE5 reserved
constexpr uint8_t MSG_ERR_WRITE          = 0xE6;
constexpr uint8_t MSG_ERR_SIZE_MISMATCH  = 0xE7;
constexpr uint8_t MSG_ERR_CRC32_MISMATCH = 0xE8;
constexpr uint8_t MSG_ERR_UNSUPPORTED    = 0xE9;  // this controller has no such subsystem

// ── Sound (0x20..) ────────────────────────────────────────────────────────
// The buzzer is U8 on the controller PCBA. Neither display carries a sounder of
// its own, so every click a finger makes on glass crosses this pair.
constexpr uint8_t MSG_SOUND_PLAY     = 0x20;  // SoundPlayPayload: make this sound now
constexpr uint8_t MSG_SOUND_CFG_GET  = 0x21;  // no payload: answer with SoundCfgPayload
constexpr uint8_t MSG_SOUND_CFG_SET  = 0x22;  // SoundCfgPayload: write volume / quiet hours
constexpr uint8_t MSG_RESP_SOUND_CFG = 0x23;  // SoundCfgPayload, after a GET or a SET

// Display development control (0x24..)
//
// The enclosure display can remain powered from J9 while its USB cable is reconnected. A
// normal ESP.restart() does not guarantee that the host sees a detach, but a brief
// deep-sleep does: the S3 powers down its USB Serial/JTAG PHY and drops the D+ pull-up,
// then timer-wakes into the application. This is sent only by an explicit controller
// console command; no production boot path sends it.
constexpr uint8_t MSG_DISPLAY_USB_REATTACH      = 0x24;  // no payload: detach USB PHY, then timer-wake
constexpr uint8_t MSG_RESP_DISPLAY_USB_REATTACH = 0x25;  // ResponsePayload: accepted

// Controller-owned flavor selection (0x26..)
//
// A display sends an absolute selection, never a toggle. An application retry
// can therefore be handled idempotently instead of turning one tap into two
// flips. SYNC carries the faucet's saved choice as a migration candidate: a
// controller with no saved selection adopts it; an established controller
// answers with its own authoritative value.
constexpr uint8_t MSG_FLAVOR_SYNC        = 0x26;  // FlavorRequestPayload: boot/reconnect candidate
constexpr uint8_t MSG_FLAVOR_SELECT      = 0x27;  // FlavorRequestPayload: a new absolute selection
constexpr uint8_t MSG_RESP_FLAVOR_STATE  = 0x28;  // FlavorStatePayload: controller's resulting truth
constexpr uint8_t MSG_FLAVOR_QUERY       = 0x29;  // enclosure poll: request controller truth

// Controller-owned prime-ready session (0x2A..0x2F). The legacy 0x0B..0x0D
// ChannelPayload contract remains intact for commissioning and older images;
// session holds use distinct ids so their tokenized payload can never be
// mistaken for that one-byte shape.
constexpr uint8_t MSG_PRIME_SESSION_SET        = 0x2A;  // PrimeSessionRequestPayload
constexpr uint8_t MSG_PRIME_SESSION_QUERY      = 0x2B;  // PrimeSessionQueryPayload
constexpr uint8_t MSG_RESP_PRIME_SESSION       = 0x2C;  // PrimeSessionStatePayload
constexpr uint8_t MSG_PRIME_SESSION_HOLD_START = 0x2D;  // PrimeHoldPayload: finger down
constexpr uint8_t MSG_PRIME_SESSION_HOLD_TICK  = 0x2E;  // PrimeHoldPayload: still held
constexpr uint8_t MSG_PRIME_SESSION_HOLD_STOP  = 0x2F;  // PrimeHoldPayload: lift/lost press

// Funnel fill (0x30). Concentrate is poured into the funnel on the enclosure's
// top face; this draws it down the channel's own path into the chilled
// reservoir. Open-ended like the clean cycle, and sequenced by the controller.
constexpr uint8_t MSG_FILL_START       = 0x30;  // ChannelPayload: draw funnel → reservoir

// ── Which logo a channel wears ────────────────────────────────────────────
// The logo is a channel's identity on every glass: it fills the faucet head,
// the round display, and a Choose card. The controller owns the assignment and
// persists it beside the selection, so a channel that changes contents changes
// face everywhere rather than on the surface that happened to set it.
constexpr uint8_t MSG_FLAVOR_ART_SET   = 0x31;  // FlavorArtPayload: both channels
constexpr uint8_t MSG_FLAVOR_ART_QUERY = 0x32;  // no payload: answer with the pair
constexpr uint8_t MSG_RESP_FLAVOR_ART  = 0x33;  // FlavorArtPayload: resulting truth

// Fixed transport capacities are part of the replay contract. Keeping the
// values beside the shared wire protocol lets each actual queue assert that a
// future depth/window change still fits inside the controller's token ledger.
constexpr uint8_t PRIME_J9_APP_QUEUE_DEPTH       = 8;
constexpr uint8_t PRIME_J9_IN_FLIGHT_DEPTH       = 1;
constexpr uint8_t PRIME_J3_APP_QUEUE_DEPTH       = 8;
constexpr uint8_t PRIME_PROTO_LINK_WINDOW_DEPTH  = 4;
constexpr uint8_t PRIME_SESSION_REPLAY_HISTORY   = 16;
constexpr uint8_t PRIME_HOLD_REPLAY_HISTORY      = 16;

// Text wrapper
constexpr uint8_t MSG_TEXT = 0xFE;

// ════════════════════════════════════════════════════════════
//  Payload structs (packed, little-endian)
// ════════════════════════════════════════════════════════════

struct __attribute__((packed)) UploadStartPayload {
  uint8_t  slot;
  uint32_t size;
};

struct __attribute__((packed)) UploadDonePayload {
  uint8_t  slot;
  uint32_t crc32;
};

struct __attribute__((packed)) SlotPayload {
  uint8_t slot;
};

struct __attribute__((packed)) SwapPayload {
  uint8_t slotA;
  uint8_t slotB;
};

struct __attribute__((packed)) ResponsePayload {
  uint8_t value;
};

constexpr uint8_t PUMP_CHANNEL_A = 0;  // U11 -> J13.AM2/AM1, the two WEST pins
constexpr uint8_t PUMP_CHANNEL_B = 1;  // U12 -> J13.BM2/BM1, the two EAST pins

// Run one pump at full power for this long.
struct __attribute__((packed)) PumpRunPayload {
  uint8_t  channel;
  uint16_t ms;
};

// Which pump/flavor an open-ended operation acts on.
struct __attribute__((packed)) ChannelPayload {
  uint8_t channel;
};

// One logo index per channel, low channel first. A SET states both, so the
// controller never has to merge a partial view of the pair.
struct __attribute__((packed)) FlavorArtPayload {
  uint8_t art[2];
};

static_assert(sizeof(FlavorArtPayload) == 2, "flavor art wire layout drift");

// Logos every image carries artwork for. A value at or above this is refused
// rather than clamped, so a newer glass cannot silently show the wrong face.
constexpr uint8_t FLAVOR_ART_COUNT = 4;

// ── Faucet flavor selection ──────────────────────────────────────────────
// token is generated by the faucet and retained across an application-level
// retry. The controller echoes it and suppresses duplicate user feedback for
// an already-handled token. Token zero is reserved for an unsolicited state
// update after controller persistence completes or a console change.
struct __attribute__((packed)) FlavorRequestPayload {
  uint8_t  flavor;  // PUMP_CHANNEL_A / PUMP_CHANNEL_B
  uint8_t  flags;   // FLAVOR_REQ_F_*
  uint32_t token;
};

constexpr uint8_t FLAVOR_REQ_F_AUDIBLE = 1 << 0;  // fresh connected tap: make one UI tick

struct __attribute__((packed)) FlavorStatePayload {
  uint8_t  flavor;  // controller-authoritative selection
  uint8_t  flags;   // FLAVOR_STATE_F_*
  uint32_t token;   // request token, or zero for an unsolicited update
};

static_assert(sizeof(FlavorRequestPayload) == 6, "flavor request wire layout drift");
static_assert(sizeof(FlavorStatePayload) == 6, "flavor state wire layout drift");

constexpr uint8_t FLAVOR_STATE_F_ESTABLISHED   = 1 << 0;
constexpr uint8_t FLAVOR_STATE_F_PERSISTED     = 1 << 1;
constexpr uint8_t FLAVOR_STATE_F_PERSIST_ERROR = 1 << 2;

// ── Controller-owned prime-ready session ────────────────────────────────
// The enclosure creates a fresh nonzero sessionToken when it enters either
// flavor's prime hold screen. The controller snapshots that valid service
// channel as session truth. Either display may then own one physical hold;
// holdToken is fresh for each press and is retained across that press's START
// retry and ticks.
// Source identity is never trusted from a payload: the controller infers
// ENCLOSURE from J9 and FAUCET from J3.
struct __attribute__((packed)) PrimeSessionRequestPayload {
  uint8_t  action;        // PRIME_SESSION_ACTIVATE / PRIME_SESSION_CANCEL
  uint8_t  channel;       // selected channel; CANCEL is matched by sessionToken
  uint32_t sessionToken;
};

struct __attribute__((packed)) PrimeSessionQueryPayload {
  uint32_t sessionToken;  // only the current token renews the enclosure lease
};

struct __attribute__((packed)) PrimeHoldPayload {
  uint8_t  channel;
  uint32_t sessionToken;
  uint32_t holdToken;
};

constexpr uint8_t PRIME_SESSION_ACTIVATE = 0;
constexpr uint8_t PRIME_SESSION_CANCEL   = 1;

constexpr uint8_t PRIME_SESSION_OFF     = 0;
constexpr uint8_t PRIME_SESSION_READY   = 1;
constexpr uint8_t PRIME_SESSION_RUNNING = 2;

constexpr uint8_t PRIME_OWNER_NONE      = 0;
constexpr uint8_t PRIME_OWNER_ENCLOSURE = 1;
constexpr uint8_t PRIME_OWNER_FAUCET    = 2;

constexpr uint8_t PRIME_OUTCOME_NONE    = 0;
constexpr uint8_t PRIME_OUTCOME_STOPPED = 1;
constexpr uint8_t PRIME_OUTCOME_TIMEOUT = 2;
constexpr uint8_t PRIME_OUTCOME_LIMIT   = 3;
constexpr uint8_t PRIME_OUTCOME_REFUSED = 4;
constexpr uint8_t PRIME_OUTCOME_CANCELED = 5;
constexpr uint8_t PRIME_OUTCOME_LEASE_EXPIRED = 6;

// The controller's complete truth. READY retains the last hold's outcome,
// elapsed time, and holdToken for correlation. OFF retains the canceled
// sessionToken, which makes a missed cancellation harmless on the next
// absolute J3 heartbeat.
struct __attribute__((packed)) PrimeSessionStatePayload {
  uint8_t  phase;         // PRIME_SESSION_*
  uint8_t  channel;       // pump selected when the session was activated
  uint8_t  owner;         // PRIME_OWNER_*; NONE unless RUNNING
  uint8_t  outcome;       // PRIME_OUTCOME_*; terminal detail while READY/OFF
  uint32_t elapsedMs;
  uint32_t revision;
  uint32_t sessionToken;
  uint32_t holdToken;
};

// A display may miss READY/H1 after sending STOP/H1 and next observe H2. A
// newer revision in the same session proves H1 is terminal unless H1 itself is
// still the authoritative RUNNING hold. Signed subtraction preserves ordering
// across the controller's uint32_t revision wrap.
inline bool primeStateSupersedesPendingStop(
    const PrimeSessionStatePayload &state,
    uint32_t sessionToken,
    uint32_t holdToken,
    uint8_t owner,
    uint32_t revisionAtStop) {
  const bool sameRun = state.phase == PRIME_SESSION_RUNNING &&
                       state.owner == owner && state.holdToken == holdToken;
  return sessionToken != 0 && state.sessionToken == sessionToken &&
         static_cast<int32_t>(state.revision - revisionAtStop) > 0 &&
         !sameRun;
}

static_assert(sizeof(PrimeSessionRequestPayload) == 6, "prime session request wire layout drift");
static_assert(sizeof(PrimeSessionQueryPayload) == 4, "prime session query wire layout drift");
static_assert(sizeof(PrimeHoldPayload) == 9, "prime hold wire layout drift");
static_assert(sizeof(PrimeSessionStatePayload) == 20, "prime session state wire layout drift");

// ── Prime ─────────────────────────────────────────────────────────────────
// A hold is a heartbeat: MSG_PRIME_START on finger down, MSG_PRIME_TICK every
// PRIME_TICK_MS while it stays down, MSG_PRIME_STOP on lift. The controller stops the
// pump when a tick runs later than PRIME_TICK_GRACE_MS, and at PRIME_MAX_MS however well
// the hold is fed.
constexpr uint16_t PRIME_TICK_MS       = 500;
constexpr uint16_t PRIME_TICK_GRACE_MS = 2000;
constexpr uint32_t PRIME_MAX_MS        = 60000;

constexpr uint8_t PRIME_RUNNING = 0;  // pump is turning
constexpr uint8_t PRIME_STOPPED = 1;  // MSG_PRIME_STOP arrived
constexpr uint8_t PRIME_TIMEOUT = 2;  // ticks stopped coming
constexpr uint8_t PRIME_LIMIT   = 3;  // PRIME_MAX_MS reached
constexpr uint8_t PRIME_REFUSED = 4;  // bad channel, or something else was already running

static_assert(PRIME_OUTCOME_STOPPED == PRIME_STOPPED, "prime stopped outcome drift");
static_assert(PRIME_OUTCOME_TIMEOUT == PRIME_TIMEOUT, "prime timeout outcome drift");
static_assert(PRIME_OUTCOME_LIMIT == PRIME_LIMIT, "prime limit outcome drift");
static_assert(PRIME_OUTCOME_REFUSED == PRIME_REFUSED, "prime refused outcome drift");

// Sent on every state change, not on a tick.
struct __attribute__((packed)) PrimeStatePayload {
  uint8_t  state;
  uint8_t  channel;
  uint32_t ms;       // how long the pump has been, or was, turning
};

// What a controller reads about itself without touching a bus or anything it drives.
struct __attribute__((packed)) StatusPayload {
  uint32_t uptimeS;
  uint32_t freeHeap;
  uint32_t framesRx;
  uint32_t framesTx;
  uint16_t gasMv;         // MQ-6 divider, 0 with no sensor fitted
  uint8_t  flags;         // see STATUS_F_* below
  uint8_t  primeChannel;  // valid while STATUS_F_PRIMING
  char     version[16];   // the controller build these readings came from
  uint8_t  j9ReplyHighWater;  // maximum replies emitted for one received J9 turn
  uint32_t j9ReplyOverruns;   // turns that emitted more than one reply
};

static_assert(sizeof(StatusPayload) == 41, "controller status wire layout drift");

constexpr uint8_t STATUS_F_GAS_TRIP = 1 << 0;  // the LM393 comparator has tripped
constexpr uint8_t STATUS_F_PRIMING  = 1 << 1;  // a prime hold is live

// ── Sound ─────────────────────────────────────────────────────────────────
// Wire-level sound ids. These mirror SoundId in lib/sound/sound.h, which is the
// definition; the controller static_asserts in link.cpp that the two still agree,
// so a sound added there without a number here does not compile.
constexpr uint8_t SND_WIRE_TICK   = 1;  // a touch was registered — not "it worked"
constexpr uint8_t SND_WIRE_ACK    = 2;  // something was committed
constexpr uint8_t SND_WIRE_CHIME  = 3;  // an operation finished
constexpr uint8_t SND_WIRE_REFUSE = 4;  // the machine said no
constexpr uint8_t SND_WIRE_WELCOME = 5;  // the machine waking up — the boot chime
constexpr uint8_t SND_WIRE_FAULT  = 6;  // needs attention
constexpr uint8_t SND_WIRE_ALARM  = 7;  // gas trip — cannot be silenced

struct __attribute__((packed)) SoundPlayPayload {
  uint8_t id;   // SND_WIRE_*
};

// Volume and quiet hours. The controller owns these and persists them in NVS;
// the glass reads them with a GET and writes them with a SET, and both are
// answered with the controller's resulting state rather than an echo.
//
// None of it reaches SND_WIRE_ALARM. A gas alarm a volume setting could mute
// would be a safety defect, so the controller exempts it before any of these
// fields are consulted.
struct __attribute__((packed)) SoundCfgPayload {
  uint8_t volume;       // 0..100; 0 mutes everything but the alarm
  uint8_t quietOn;      // 0 / 1
  uint8_t quietStart;   // hour, 0..23
  uint8_t quietEnd;     // hour, 0..23; start > end wraps midnight
  uint8_t quietVolume;  // 0..100, the ceiling while quiet hours are in force
  uint8_t flags;        // SOUND_CFG_F_*, controller → glass only
};

constexpr uint8_t SOUND_CFG_F_CLOCK_OK  = 1 << 0;  // U6 answers and its time is believed
constexpr uint8_t SOUND_CFG_F_QUIET_NOW = 1 << 1;  // quiet hours are in force right now

inline uint32_t uartCrc32Update(uint32_t prev, const uint8_t *data, size_t len) {
  uint32_t crc = ~prev;
  for (size_t i = 0; i < len; i++) {
    crc ^= data[i];
    for (uint8_t j = 0; j < 8; j++) {
      crc = (crc & 1) ? (crc >> 1) ^ 0xEDB88320 : crc >> 1;
    }
  }
  return ~crc;
}

// ════════════════════════════════════════════════════════════
//  Receive helpers — extract type and payload from frame
// ════════════════════════════════════════════════════════════

inline uint8_t msgType(const uint8_t *frame) { return frame[0]; }
inline const uint8_t *msgPayload(const uint8_t *frame) { return frame + 1; }
inline uint16_t msgPayloadLen(int frameLen) { return (frameLen > 1) ? frameLen - 1 : 0; }
