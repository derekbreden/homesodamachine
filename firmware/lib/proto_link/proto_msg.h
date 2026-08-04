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
