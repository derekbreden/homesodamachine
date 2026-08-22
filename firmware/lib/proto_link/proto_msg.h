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
// The front board can remain powered from J9 while its USB cable is reconnected. A
// normal ESP.restart() does not guarantee that the host sees a detach, but a brief
// deep-sleep does: the S3 powers down its USB Serial/JTAG PHY and drops the D+ pull-up,
// then timer-wakes into the application. This is sent only by an explicit controller
// console command; no production boot path sends it.
constexpr uint8_t MSG_DISPLAY_USB_REATTACH      = 0x24;  // no payload: detach USB PHY, then timer-wake
constexpr uint8_t MSG_RESP_DISPLAY_USB_REATTACH = 0x25;  // ResponsePayload: accepted

// Faucet flavor selection (0x26..)
//
// The faucet sends an absolute selection, never a toggle. An application retry
// can therefore be handled idempotently instead of turning one tap into two
// flips. SYNC carries the faucet's saved choice as a migration candidate: a
// controller with no saved selection adopts it; an established controller
// answers with its own authoritative value.
constexpr uint8_t MSG_FLAVOR_SYNC        = 0x26;  // FlavorRequestPayload: boot/reconnect candidate
constexpr uint8_t MSG_FLAVOR_SELECT      = 0x27;  // FlavorRequestPayload: a new absolute selection
constexpr uint8_t MSG_RESP_FLAVOR_STATE  = 0x28;  // FlavorStatePayload: controller's resulting truth

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
};

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
