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
constexpr uint8_t MSG_ERR_UNSUPPORTED    = 0xE9;  // this main board has no such subsystem

// ── Sound (0x20..) ────────────────────────────────────────────────────────
// The buzzer is U8 on the main board. Neither display carries a sounder of
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

// Main-board-owned flavor selection (0x26..)
//
// A display sends an absolute selection, never a toggle. An application retry
// can therefore be handled idempotently instead of turning one tap into two
// flips. SYNC carries the faucet's saved choice as a migration candidate: a
// main board with no saved selection adopts it; an established main board
// answers with its own authoritative value.
constexpr uint8_t MSG_FLAVOR_SYNC        = 0x26;  // FlavorRequestPayload: boot/reconnect candidate
constexpr uint8_t MSG_FLAVOR_SELECT      = 0x27;  // FlavorRequestPayload: a new absolute selection
constexpr uint8_t MSG_RESP_FLAVOR_STATE  = 0x28;  // FlavorStatePayload: main board's resulting truth
constexpr uint8_t MSG_FLAVOR_QUERY       = 0x29;  // enclosure poll: request main board truth

// Main-board-owned prime-ready session (0x2A..0x2F). The legacy 0x0B..0x0D
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
// reservoir. Open-ended like the clean cycle, and sequenced by the main board.
constexpr uint8_t MSG_FILL_START       = 0x30;  // ChannelPayload: draw funnel → reservoir

// ── Which logo a channel wears ────────────────────────────────────────────
// The logo is a channel's identity on every glass: it fills the faucet display,
// the round display, and a Choose card. The main board owns the assignment and
// persists it beside the selection, so a channel that changes contents changes
// face everywhere rather than on the surface that happened to set it.
constexpr uint8_t MSG_FLAVOR_ART_SET   = 0x31;  // FlavorArtPayload: both channels
constexpr uint8_t MSG_FLAVOR_ART_QUERY = 0x32;  // no payload: answer with the pair
constexpr uint8_t MSG_RESP_FLAVOR_ART  = 0x33;  // FlavorArtPayload: resulting truth

// ── Idle, owned by the main board (0x34..) ───────────────────────────────
// Two glasses, one appliance, one clock. A finger on either is activity for
// both, so the pair sleeps and wakes together instead of each keeping its own
// idea of whether anyone is here. A display reports a touch that put no other
// frame on its link — a press that already sent a command is a touch the main
// board can see — and renders whatever state comes back. Nothing sleeps on a
// display's own timer: a pair left lit is a link that stopped talking, and is
// meant to be visible as such.
constexpr uint8_t MSG_TOUCH          = 0x34;  // no payload: a finger landed on this glass
constexpr uint8_t MSG_IDLE_QUERY     = 0x35;  // no payload: answer with the current state
constexpr uint8_t MSG_RESP_IDLE      = 0x36;  // IdlePayload: awake or asleep, and for how long

// ── Firmware over the link (0x37..) ──────────────────────────────────────
// A board takes its new image over the wire it already talks on, so a machine
// in a kitchen is updated from the phone rather than from a cable. The
// receiver pulls: it asks for the offset it is ready to write, and whoever
// holds the image answers with those bytes. That inverts cleanly onto J9,
// where the main board only ever speaks inside the turn after one arrives,
// and costs J3 nothing it cannot afford.
//
// The image lands in the OTA slot that is not running. Nothing is committed
// until the whole of it is written and its CRC32 matches what BEGIN promised;
// a receiver that never gets there keeps running what it booted.
constexpr uint8_t MSG_OTA_BEGIN = 0x37;  // OtaBeginPayload: size, crc32, chunk
constexpr uint8_t MSG_OTA_REQ   = 0x38;  // OtaReqPayload: receiver wants this offset
constexpr uint8_t MSG_OTA_DATA  = 0x39;  // OtaDataPayload: offset, then the bytes
constexpr uint8_t MSG_OTA_ABORT = 0x3A;  // no payload: drop the session
constexpr uint8_t MSG_RESP_OTA  = 0x3B;  // OtaStatePayload: where the receiver is

// ── The board holding the image, when it is not the relay (0x3C..) ───────
// The relay stores nothing. Where the image arrives from a phone rather than a
// cable, the board with the radio is upstream of the relay and the same pull
// runs one link further: the receiver asks the relay, the relay asks the
// source, the source asks the phone. One chunk is in flight anywhere on the
// path.
constexpr uint8_t MSG_OTA_SRC_BEGIN = 0x3C;  // OtaSrcBeginPayload: which target, and the image
constexpr uint8_t MSG_OTA_SRC_NEED  = 0x3D;  // OtaSrcNeedPayload: offset and how much
constexpr uint8_t MSG_OTA_SRC_DATA  = 0x3E;  // offset, then the bytes
constexpr uint8_t MSG_OTA_SRC_END   = 0x3F;  // OtaStatePayload: how the session finished

// ── What a machine is, asked of the board that knows (0x40..) ────────────
// The main board is the only one that knows which machine it is in. A display
// asks at boot and carries the answer into whatever it advertises.
constexpr uint8_t MSG_IDENTITY_QUERY = 0x40;  // no payload
constexpr uint8_t MSG_RESP_IDENTITY  = 0x41;  // IdentityPayload

// The radio is on a display, so the main board's console cannot see it
// directly. This is how it asks.
constexpr uint8_t MSG_BLE_STATUS_REQ  = 0x42;  // no payload
constexpr uint8_t MSG_RESP_BLE_STATUS = 0x43;  // BleStatusPayload

// ── What each board is running (0x44..) ──────────────────────────────────
// A phone asking whether a machine is current is asking about every board on
// it, not the one it happens to be talking to. The main board reaches them
// all, so it is where the answer is assembled: it knows its own and asks each
// display for theirs.
constexpr uint8_t MSG_VERSION_QUERY   = 0x44;  // no payload: a display's own
constexpr uint8_t MSG_RESP_VERSION    = 0x45;  // VersionPayload
constexpr uint8_t MSG_VERSIONS_QUERY  = 0x46;  // no payload: the whole machine
constexpr uint8_t MSG_RESP_VERSIONS   = 0x47;  // VersionsPayload

// ── The radio bench (0x48..) ─────────────────────────────────────────────
// Both displays carry a WiFi radio that no product path uses. These four
// frames stand a link up directly between them, push bytes across it, and
// report what it carried — so the wired links have a number to be compared
// against. The main board drives it from its console and is not on the path.
constexpr uint8_t MSG_WIFI_BENCH_AP   = 0x48;  // WifiApPayload: raise or drop the SoftAP
constexpr uint8_t MSG_RESP_WIFI_AP    = 0x49;  // WifiApStatePayload
constexpr uint8_t MSG_WIFI_BENCH_PUSH = 0x4A;  // WifiPushPayload: join it and send this much
constexpr uint8_t MSG_RESP_WIFI_PUSH  = 0x4B;  // WifiPushResultPayload

// The same question asked of the wire instead of the radio. The OTA path pulls
// one chunk at a time and pays a round trip per kilobyte, so what it measures
// is that discipline, not J3. These three frames push into TinyProto's window
// as fast as it will take them and write nothing to flash, which is the wire's
// own ceiling and the number the radio has to beat.
constexpr uint8_t MSG_BENCH_BEGIN     = 0x4C;  // BenchBeginPayload: this many bytes follow
constexpr uint8_t MSG_BENCH_DATA      = 0x4D;  // raw bytes, counted and dropped
constexpr uint8_t MSG_RESP_BENCH      = 0x4E;  // BenchResultPayload

// ── What pictures a display is holding (0x4F..) ──────────────────────────
// Neither display has a console inside the appliance, and both hold a store
// the user can fill and empty from a phone. This is how the main board's
// console — and through it the factory and a service visit — sees what is
// actually on each board.
constexpr uint8_t MSG_IMAGES_QUERY    = 0x4F;  // no payload
constexpr uint8_t MSG_RESP_IMAGES     = 0x50;  // ImagesPayload

// A picture the machine makes for itself, so the store, the picker and the
// hop to the enclosure can be exercised with no phone in the room. It goes in
// through the same write path a real one does — erase, chunks, crc, header
// last — so what it proves is the path and not a shortcut around it.
constexpr uint8_t MSG_IMAGE_SYNTH     = 0x51;  // ImageSlotPayload

// Carrying one picture the last hop, to the display that cannot receive it
// itself. The faucet holds every rendition and has the radio; the enclosure
// has neither a phone nor a store it can fill on its own. The main board is
// not on the path — it only stands the enclosure's radio up, says go, and
// takes it down again, because it is the only board that can reach both.
constexpr uint8_t MSG_IMAGE_RELAY_REQ = 0x52;  // faucet -> main: ImageSlotPayload
constexpr uint8_t MSG_IMAGE_RELAY_GO  = 0x53;  // main -> faucet: ImageSlotPayload
constexpr uint8_t MSG_IMAGE_ERASE     = 0x54;  // main -> either: ImageSlotPayload

// ── The camera's test screen (0x55..) ────────────────────────────────────
// A bench camera reads the enclosure display, and reads it best when the
// panel shows a known picture: a frame on its outermost pixels and four
// fiducials at known pixel coordinates, so a photograph can be mapped back
// onto the panel's own grid. The main board's console asks for it; the
// enclosure shows it over whatever is up, for the seconds asked, then puts
// the page back. Nothing in a product path sends it.
constexpr uint8_t MSG_TEST_SCREEN      = 0x55;  // TestScreenPayload: seconds to hold it; 0 ends it
constexpr uint8_t MSG_RESP_TEST_SCREEN = 0x56;  // ResponsePayload: 1 showing, 0 not

// Fixed transport capacities are part of the replay contract. Keeping the
// values beside the shared wire protocol lets each actual queue assert that a
// future depth/window change still fits inside the main board's token ledger.
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

struct __attribute__((packed)) TestScreenPayload {
  uint16_t seconds;
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

// Whether the appliance considers anyone present, and the window it is counting
// against — the window widens while an offered action is waiting to be taken.
struct __attribute__((packed)) IdlePayload {
  uint8_t  asleep;      // 0 awake, 1 asleep
  uint32_t windowMs;    // how long the current quiet stretch may run
};

static_assert(sizeof(IdlePayload) == 5, "idle wire layout drift");

// One logo index per channel, low channel first. A SET states both, so the
// main board never has to merge a partial view of the pair.
struct __attribute__((packed)) FlavorArtPayload {
  uint8_t art[2];
};

static_assert(sizeof(FlavorArtPayload) == 2, "flavor art wire layout drift");

// Logos a channel can be given. The low FLAVOR_ART_FACTORY are compiled into
// every image and cannot be removed; the rest are the user's own, held in each
// display's image store and empty until a phone puts one there. A value at or
// above the total is refused rather than clamped, so a newer glass cannot
// silently show the wrong face.
//
// A custom index whose slot is empty is a real state, not an error: a picture
// can be removed while a channel is wearing it. Each display falls back to the
// factory logo of the same channel rather than drawing nothing.
constexpr uint8_t FLAVOR_ART_FACTORY = 4;
constexpr uint8_t FLAVOR_ART_CUSTOM  = 4;
constexpr uint8_t FLAVOR_ART_COUNT   = FLAVOR_ART_FACTORY + FLAVOR_ART_CUSTOM;

// Which custom slot an art index names, or FLAVOR_ART_CUSTOM if it names a
// factory logo instead.
inline uint8_t flavorArtCustomSlot(uint8_t art) {
  return art >= FLAVOR_ART_FACTORY ? (uint8_t)(art - FLAVOR_ART_FACTORY) : FLAVOR_ART_CUSTOM;
}

// ── What one custom picture is ───────────────────────────────────────────
// Every size either glass draws it at, resampled on the phone, in this order.
// Nothing on either board scales anything at draw time, so a custom face is as
// sharp as a factory one.
//
// ONE SHAPE, AT THREE SIZES. Every rendition is 43:80 — the faucet's glass —
// so a photograph gives the machine one rectangle and every surface that shows
// it shows the same picture. A face composed for the tall glass is the face the
// enclosure's card wears and the face its picker previews, at three scales of
// one crop rather than three framings of one photograph.
//
// BOTH BOARDS KEEP ALL THREE. The faucet is the master copy — it has the radio,
// so an enclosure display can be replaced and re-provisioned from it without the
// phone ever being involved — and it now holds byte for byte what the enclosure
// holds, so one crc is both boards' answer for what a slot contains.

struct __attribute__((packed)) ImageRenditionSpec {
  uint16_t w;
  uint16_t h;
};

constexpr uint8_t IMAGE_BUNDLE_COUNT = 3;
constexpr uint8_t IMAGE_BUNDLE_ENCLOSURE_AT    = 0;
constexpr uint8_t IMAGE_BUNDLE_ENCLOSURE_COUNT = IMAGE_BUNDLE_COUNT;

// index 0: the faucet's whole glass, and the enclosure's detail anchor — the
//          picture at the size the faucet will wear it, standing under the back
//          button to say which flavor the page is about.
// index 1: the enclosure's Choose card, and the face on a prime/fill/clean pick.
// index 2: its picker tile.
constexpr ImageRenditionSpec IMAGE_BUNDLE[IMAGE_BUNDLE_COUNT] = {
    {172, 320},
    {129, 240},
    { 86, 160},
};

// 43:80 exactly, all of them — the glass at four, three and two. A rendition
// that is not the faucet's shape is a second crop of the photograph, and there
// is only one.
static_assert(IMAGE_BUNDLE[0].w == 43 * 4 && IMAGE_BUNDLE[0].h == 80 * 4, "43:80");
static_assert(IMAGE_BUNDLE[1].w == 43 * 3 && IMAGE_BUNDLE[1].h == 80 * 3, "43:80");
static_assert(IMAGE_BUNDLE[2].w == 43 * 2 && IMAGE_BUNDLE[2].h == 80 * 2, "43:80");

inline uint32_t imageBundleBytes() {
  uint32_t n = 0;
  for (uint8_t i = 0; i < IMAGE_BUNDLE_COUNT; i++)
    n += (uint32_t)IMAGE_BUNDLE[i].w * IMAGE_BUNDLE[i].h * 2;
  return n;
}

inline uint32_t imageEnclosureBytes() {
  uint32_t n = 0;
  for (uint8_t i = 0; i < IMAGE_BUNDLE_ENCLOSURE_COUNT; i++) {
    const ImageRenditionSpec &r = IMAGE_BUNDLE[IMAGE_BUNDLE_ENCLOSURE_AT + i];
    n += (uint32_t)r.w * r.h * 2;
  }
  return n;
}

// ── Faucet flavor selection ──────────────────────────────────────────────
// token is generated by the faucet and retained across an application-level
// retry. The main board echoes it and suppresses duplicate user feedback for
// an already-handled token. Token zero is reserved for an unsolicited state
// update after main board persistence completes or a console change.
struct __attribute__((packed)) FlavorRequestPayload {
  uint8_t  flavor;  // PUMP_CHANNEL_A / PUMP_CHANNEL_B
  uint8_t  flags;   // FLAVOR_REQ_F_*
  uint32_t token;
};

constexpr uint8_t FLAVOR_REQ_F_AUDIBLE = 1 << 0;  // fresh connected tap: make one UI tick

struct __attribute__((packed)) FlavorStatePayload {
  uint8_t  flavor;  // main-board-authoritative selection
  uint8_t  flags;   // FLAVOR_STATE_F_*
  uint32_t token;   // request token, or zero for an unsolicited update
};

static_assert(sizeof(FlavorRequestPayload) == 6, "flavor request wire layout drift");
static_assert(sizeof(FlavorStatePayload) == 6, "flavor state wire layout drift");

constexpr uint8_t FLAVOR_STATE_F_ESTABLISHED   = 1 << 0;
constexpr uint8_t FLAVOR_STATE_F_PERSISTED     = 1 << 1;
constexpr uint8_t FLAVOR_STATE_F_PERSIST_ERROR = 1 << 2;

// ── Main-board-owned prime-ready session ────────────────────────────────
// The enclosure creates a fresh nonzero sessionToken when it enters either
// flavor's prime hold screen. The main board snapshots that valid service
// channel as session truth. Either display may then own one physical hold;
// holdToken is fresh for each press and is retained across that press's START
// retry and ticks.
// Source identity is never trusted from a payload: the main board infers
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

// The main board's complete truth. READY retains the last hold's outcome,
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
// across the main board's uint32_t revision wrap.
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
// PRIME_TICK_MS while it stays down, MSG_PRIME_STOP on lift. The main board stops the
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

// What a main board reads about itself without touching a bus or anything it drives.
struct __attribute__((packed)) StatusPayload {
  uint32_t uptimeS;
  uint32_t freeHeap;
  uint32_t framesRx;
  uint32_t framesTx;
  uint16_t gasMv;         // MQ-6 divider, 0 with no sensor fitted
  uint8_t  flags;         // see STATUS_F_* below
  uint8_t  primeChannel;  // valid while STATUS_F_PRIMING
  char     version[16];   // the main board build these readings came from
  uint8_t  j9ReplyHighWater;  // maximum replies emitted for one received J9 turn
  uint32_t j9ReplyOverruns;   // turns that emitted more than one reply
};

static_assert(sizeof(StatusPayload) == 41, "main board status wire layout drift");

constexpr uint8_t STATUS_F_GAS_TRIP = 1 << 0;  // the LM393 comparator has tripped
constexpr uint8_t STATUS_F_PRIMING  = 1 << 1;  // a prime hold is live

// ── Sound ─────────────────────────────────────────────────────────────────
// Wire-level sound ids. These mirror SoundId in lib/sound/sound.h, which is the
// definition; the main board static_asserts in link.cpp that the two still agree,
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

// Volume and quiet hours. The main board owns these and persists them in NVS;
// the glass reads them with a GET and writes them with a SET, and both are
// answered with the main board's resulting state rather than an echo.
//
// None of it reaches SND_WIRE_ALARM. A gas alarm a volume setting could mute
// would be a safety defect, so the main board exempts it before any of these
// fields are consulted.
struct __attribute__((packed)) SoundCfgPayload {
  uint8_t volume;       // 0..100; 0 mutes everything but the alarm
  uint8_t quietOn;      // 0 / 1
  uint8_t quietStart;   // hour, 0..23
  uint8_t quietEnd;     // hour, 0..23; start > end wraps midnight
  uint8_t quietVolume;  // 0..100, the ceiling while quiet hours are in force
  uint8_t flags;        // SOUND_CFG_F_*, main board → glass only
};

constexpr uint8_t SOUND_CFG_F_CLOCK_OK  = 1 << 0;  // U6 answers and its time is believed
constexpr uint8_t SOUND_CFG_F_QUIET_NOW = 1 << 1;  // quiet hours are in force right now

// ── Firmware over the link ────────────────────────────────────────────────
// OTA_DATA carries a 4-byte offset then the bytes, so a reply that arrives
// after a retry is written where it belongs or discarded, never appended.
struct __attribute__((packed)) OtaBeginPayload {
  uint32_t size;    // bytes in the image
  uint32_t crc32;   // over the whole image
  uint16_t chunk;   // most bytes the sender will put in one OTA_DATA
  uint8_t  kind;    // OTA_KIND_*
};

// What is arriving. Firmware goes into the OTA slot that is not running and
// moves the boot partition; a named data partition is erased and rewritten in
// place. Both are verified against the promised CRC32 before anything counts.
constexpr uint8_t OTA_KIND_APP = 0;
constexpr uint8_t OTA_KIND_ART = 1;  // the enclosure display's `art` partition

struct __attribute__((packed)) OtaReqPayload {
  uint32_t offset;  // where the receiver is ready to write
};

struct __attribute__((packed)) OtaStatePayload {
  uint8_t  state;    // OTA_STATE_*
  uint8_t  err;      // OTA_ERR_*, meaningful when state is FAILED
  uint32_t received; // bytes written so far
};

constexpr uint8_t OTA_STATE_IDLE    = 0;
constexpr uint8_t OTA_STATE_READY   = 1;  // slot open, waiting on bytes
constexpr uint8_t OTA_STATE_WRITING = 2;
constexpr uint8_t OTA_STATE_DONE    = 3;  // verified and set to boot
constexpr uint8_t OTA_STATE_FAILED  = 4;

constexpr uint8_t OTA_ERR_NONE      = 0;
constexpr uint8_t OTA_ERR_NO_SLOT   = 1;  // single-slot table: nothing to write into
constexpr uint8_t OTA_ERR_TOO_BIG   = 2;  // image will not fit the slot
constexpr uint8_t OTA_ERR_WRITE     = 3;
constexpr uint8_t OTA_ERR_CRC       = 4;  // whole-image CRC32 did not match BEGIN
constexpr uint8_t OTA_ERR_VERIFY    = 5;  // esp_ota_end / set_boot_partition refused
constexpr uint8_t OTA_ERR_SEQUENCE  = 6;  // bytes arrived for the wrong offset

// Which board an image is for. The relay reaches every one of these; a source
// upstream of it names one here rather than knowing which link it lives on.
constexpr uint8_t OTA_TGT_NONE      = 0;
constexpr uint8_t OTA_TGT_SELF      = 1;  // the relay's own spare slot
constexpr uint8_t OTA_TGT_FAUCET    = 2;
constexpr uint8_t OTA_TGT_ENCLOSURE = 3;

// A phone's MTU is a few hundred bytes and a relay chunk is 1 KB, so the source
// answers one NEED with several DATA frames. The length is here because the
// source is what has to divide it.
struct __attribute__((packed)) OtaSrcNeedPayload {
  uint32_t offset;
  uint16_t len;
};

struct __attribute__((packed)) OtaSrcBeginPayload {
  uint32_t size;
  uint32_t crc32;
  uint16_t chunk;
  uint8_t  kind;    // OTA_KIND_*
  uint8_t  target;  // OTA_TGT_*
};

// Which machine this is and which unit of it. `model` decides what a phone
// shows; `unit` is the low three bytes of the main board's MAC, which is what
// distinguishes two machines standing next to each other.
constexpr uint8_t MACHINE_APPLIANCE = 1;
constexpr uint8_t MACHINE_PROTOTYPE = 2;

constexpr uint8_t MACHINE_NAME_MAX = 20;

struct __attribute__((packed)) IdentityPayload {
  uint8_t  model;                       // MACHINE_*
  uint8_t  unit[3];                     // low three bytes of the main board's MAC
  char     name[MACHINE_NAME_MAX + 1];  // NUL-terminated; empty until someone sets one
};

struct __attribute__((packed)) BleStatusPayload {
  uint8_t  flags;        // BLE_ST_*
  uint8_t  target;       // OTA_TGT_* of the session passing through, if any
  uint16_t owed;         // bytes of the current ask the phone still owes
  uint32_t dropped;      // frames this board could not take or forward
  char     advertised[MACHINE_NAME_MAX + 1];
};

constexpr uint8_t FW_VERSION_MAX = 23;

struct __attribute__((packed)) VersionPayload {
  uint8_t  board;                        // OTA_TGT_*
  char     version[FW_VERSION_MAX + 1];  // NUL-terminated; empty until asked
  // The art partition carries no version. It carries a crc32 over its pixels,
  // and the manifest carries the same one, so that is what says whether the
  // pictures on this board are the published pictures. Zero where the board has
  // no art partition, or has not mapped one.
  uint32_t artCrc32;
};

// Every board on this machine that can take an image. An entry whose version is
// empty is a board that has not answered — which is not the same as one running
// nothing, and the phone says so rather than calling the machine current.
constexpr uint8_t VERSIONS_MAX = 3;

struct __attribute__((packed)) VersionsPayload {
  uint8_t count;
  VersionPayload entries[VERSIONS_MAX];
};

constexpr uint8_t BLE_ST_UP        = 1 << 0;  // the stack came up and is advertising
constexpr uint8_t BLE_ST_CONNECTED = 1 << 1;
constexpr uint8_t BLE_ST_IDENTITY  = 1 << 2;  // the main board answered

// ── The radio bench ──────────────────────────────────────────────────────
// The enclosure display raises the access point and sinks the bytes; the
// faucet joins it and sends them. Both ends carry the same credentials rather
// than being told them, so a bench run is two independent commands and no
// handshake between them.
#define WIFI_BENCH_SSID "hsm-bench"
#define WIFI_BENCH_PSK  "carbonated"

// The SoftAP is always 192.168.4.1 and hands out .2 upward, so the sender
// needs no address from anyone.
constexpr uint16_t WIFI_BENCH_PORT    = 5001;
constexpr uint8_t  WIFI_BENCH_CHANNEL = 6;

struct __attribute__((packed)) WifiApPayload {
  uint8_t on;
  uint8_t channel;
};

struct __attribute__((packed)) WifiApStatePayload {
  uint8_t  up;
  uint8_t  clients;
  uint8_t  channel;
  uint32_t ip;       // the AP's own address, network order as WiFi reports it
  uint32_t bytes;    // what the sink took on the last connection
  uint32_t ms;       // first byte to last, on that connection
};

struct __attribute__((packed)) WifiPushPayload {
  uint32_t bytes;
  uint8_t  channel;
  uint8_t  flags;    // WIFI_PUSH_F_*
};

// Both radios on the faucet are one antenna. Advertising through a transfer is
// the honest case — the phone is what put the image there — but what it costs
// is only visible against a run with BLE out of the way.
constexpr uint8_t WIFI_PUSH_F_QUIET_BLE = 1 << 0;

// joinMs is association and DHCP; xferMs is first byte written to last ack.
// They are separate because only one of them is per-image: a machine that
// keeps the link up between images pays joinMs once.
struct __attribute__((packed)) WifiPushResultPayload {
  uint8_t  ok;
  uint8_t  err;      // WIFI_BENCH_ERR_*
  int8_t   rssi;
  uint8_t  channel;
  uint32_t bytes;
  uint32_t joinMs;
  uint32_t connectMs;
  uint32_t xferMs;
};

// What opens a picture on the enclosure's socket. The bench sends bytes with
// no header and is counted and dropped; this magic is what tells a real
// picture from that, on a link that carries both.
constexpr uint32_t IMAGE_WIRE_MAGIC = 0x57474D49;  // 'IMGW'

struct __attribute__((packed)) ImageWireHeader {
  uint32_t magic;
  uint8_t  slot;
  uint8_t  reserved[3];
  uint32_t bytes;    // the enclosure's four renditions, and only those
  uint32_t crc32;
};

// THE SINK ANSWERS, AND THAT ANSWER IS WHAT ENDS THE CONNECTION. A close is not
// a delivery: the sender's last kilobytes are still in flight when it calls
// stop(), and the receiver's loop ends the moment the socket says closed — so a
// picture arrives a couple of kilobytes short of itself and is refused, with the
// sender reporting every byte written and the machine holding nothing.
//
//     pic slot 0 SHORT 166844/169632
//
// One byte back closes that: the receiver has counted the whole picture and
// written its header before it sends, and the sender does not close until it
// arrives. So "sent" and "kept" become the same claim rather than two that can
// disagree.
constexpr uint8_t IMAGE_WIRE_KEPT    = 0xA1;  // whole, and its header is written
constexpr uint8_t IMAGE_WIRE_SHORT   = 0xA2;  // the bytes stopped coming
constexpr uint8_t IMAGE_WIRE_REFUSED = 0xA3;  // not a picture this board can hold

struct __attribute__((packed)) ImageSlotPayload {
  uint8_t slot;
};

// WHAT EACH BOARD SAYS IT IS HOLDING, IN TERMS THE OTHER CAN BE COMPARED WITH.
// The two stores keep different things — the faucet every rendition, the
// enclosure only the four it draws — so their own crcs are not the same number
// for the same picture and cannot be held against each other. `crc` is instead
// the identity of the ENCLOSURE'S copy, from both ends: what that board holds,
// and what the faucet would send it. Equal is in sync; anything else is a
// difference the machine can act on without a person noticing it first.
struct __attribute__((packed)) ImagesPayload {
  uint8_t  board;        // OTA_TGT_*
  uint8_t  slots;        // custom slots this display keeps
  uint8_t  held;
  uint8_t  occupancy;    // bit per slot, low slot first
  uint32_t bundleBytes;  // what one picture costs on this board
  uint32_t crc[FLAVOR_ART_CUSTOM];
};

// Asking costs a frame; saying it out loud costs a console someone is reading.
// The reconcile asks often and quietly; a person asking wants the account.
struct __attribute__((packed)) ImagesQueryPayload {
  uint8_t verbose;
};

struct __attribute__((packed)) BenchBeginPayload {
  uint32_t bytes;
};

struct __attribute__((packed)) BenchResultPayload {
  uint32_t bytes;
  uint32_t ms;    // first byte to last, measured at the receiving end
};

constexpr uint16_t BENCH_CHUNK = 1024;

constexpr uint8_t WIFI_BENCH_ERR_NONE    = 0;
constexpr uint8_t WIFI_BENCH_ERR_JOIN    = 1;  // never associated or never got an address
constexpr uint8_t WIFI_BENCH_ERR_CONNECT = 2;  // associated, but the sink refused the socket
constexpr uint8_t WIFI_BENCH_ERR_WRITE   = 3;  // the socket died mid-transfer
constexpr uint8_t WIFI_BENCH_ERR_BUSY    = 4;  // a run is already in flight
constexpr uint8_t WIFI_BENCH_ERR_REFUSED = 5;  // every byte arrived and the sink kept none
constexpr uint8_t WIFI_BENCH_ERR_SILENT  = 6;  // the sink never said whether it kept it

// The most image bytes one OTA_DATA carries on each link. Both are 1 KB: J9's
// HDLC frame buffers are sized for it, and J3's TinyProto Fd fragments
// internally. A chunk is a round trip, so this is most of what a transfer's
// speed is made of.
constexpr uint16_t OTA_CHUNK_J9 = 1024;

// What one J9 frame can carry: the HDLC tx buffer less the type byte. Declared
// here beside the chunk that has to fit it; proto_link.h asserts its buffer is
// at least this, so raising one without the other does not compile.
constexpr uint16_t J9_MAX_PAYLOAD = 1151;
constexpr uint16_t OTA_CHUNK_J3 = 1024;

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
