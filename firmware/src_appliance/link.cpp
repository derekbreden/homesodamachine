#include <Arduino.h>

#include "link.h"
#include "machine.h"
#include "pins.h"
#include "rtc.h"
#include "proto_link.h"
#include "rs485_echo.h"
#include "sound.h"
#include "fw_version.h"

// The wire ids in proto_msg.h and the SoundId enum in lib/sound are two halves of
// one contract, and this is the seam that translates between them. Asserting the
// pairs here means a sound added to the vocabulary without a wire number — or
// renumbered on one side only — fails the build rather than playing the wrong
// sound on a customer's machine.
static_assert(SND_WIRE_TICK   == SND_TICK,   "sound wire id drift: tick");
static_assert(SND_WIRE_ACK    == SND_ACK,    "sound wire id drift: ack");
static_assert(SND_WIRE_CHIME  == SND_CHIME,  "sound wire id drift: chime");
static_assert(SND_WIRE_REFUSE == SND_REFUSE, "sound wire id drift: refuse");
static_assert(SND_WIRE_WELCOME == SND_WELCOME, "sound wire id drift: welcome");
static_assert(SND_WIRE_FAULT  == SND_FAULT,  "sound wire id drift: fault");
static_assert(SND_WIRE_ALARM  == SND_ALARM,  "sound wire id drift: alarm");

static EchoCancel j9Stream(Serial1);
static HdlcLink   j9;
static bool displayUsbReattachAck = false;

// What the controller currently holds, as the glass reads it.
static void fillSoundCfg(SoundCfgPayload &c) {
    c.volume      = soundVolume();
    c.quietOn     = soundQuietOn() ? 1 : 0;
    c.quietStart  = soundQuietStart();
    c.quietEnd    = soundQuietEnd();
    c.quietVolume = soundQuietVolume();
    c.flags       = (rtcValid()          ? SOUND_CFG_F_CLOCK_OK  : 0)
                  | (soundInQuietHours() ? SOUND_CFG_F_QUIET_NOW : 0);
}

// ── What the machine announces, going out on the pair ─────────────────────
// This board answers; it does not interrupt. A prime that timed out and a bounded
// run that finished both come from machineService(), on a clock of their own, and
// putting them straight on the wire means driving it while the glass may already
// be mid-frame — which collides, destroys this board's own echo, and costs
// whichever frame the glass was sending (rs485_echo.h).
//
// So an announcement waits for a turn. It is held here and goes out inside the
// window right after a frame arrives, when the glass is known to be listening
// rather than talking. The glass polls on an interval for exactly this reason,
// so the wait is bounded by that poll and not by whether anyone touches anything.
struct Announce { uint8_t type; uint8_t len; uint8_t data[8]; };
static const uint8_t ANN_DEPTH = 4;
static Announce annQ[ANN_DEPTH];
static uint8_t  annHead = 0, annTail = 0, annCount = 0;
static uint32_t annDropped = 0;

static void announceQueue(uint8_t type, const void *data, uint8_t len) {
    if (len > sizeof(annQ[0].data)) len = sizeof(annQ[0].data);
    if (annCount >= ANN_DEPTH) {
        annTail = (uint8_t)((annTail + 1) % ANN_DEPTH);
        annCount--;
        annDropped++;
    }
    Announce &a = annQ[annHead];
    a.type = type;
    a.len  = len;
    if (len && data) memcpy(a.data, data, len);
    annHead = (uint8_t)((annHead + 1) % ANN_DEPTH);
    annCount++;
}

// Drained only from inside onMessage, which is the one moment the far end is
// certainly not driving the pair.
static void announceFlush() {
    while (annCount) {
        Announce &a = annQ[annTail];
        j9.send(a.type, a.len ? a.data : nullptr, a.len);
        annTail = (uint8_t)((annTail + 1) % ANN_DEPTH);
        annCount--;
    }
}

static void onPrimeState(uint8_t state, uint8_t channel, uint32_t ms) {
    PrimeStatePayload st{state, channel, ms};
    announceQueue(MSG_RESP_PRIME, &st, sizeof(st));
}

static void onPumpDone(uint8_t channel) {
    ResponsePayload r{channel};
    announceQueue(MSG_RESP_PUMP_DONE, &r, sizeof(r));
}

// A frame that only a finger could have produced. The glass sends no separate
// click for these — one press is one frame on J9 — so the tick is made here, off
// the command itself. A prime TICK is the same finger still held rather than a
// new press, and a status poll is nobody's finger at all; neither sounds.
// MSG_PRIME_START is deliberately not here. A hold is answered by the machine
// itself with SND_ENGAGE when the pad takes, or SND_REFUSE when it does not —
// both of which say more than a tick, and a tick underneath them would only be a
// click getting cut off by the sweep that follows it.
static bool isUserAction(uint8_t type) {
    return type == MSG_PUMP_RUN || type == MSG_CLEAN_START || type == MSG_SOUND_CFG_SET;
}

static void dispatch(HdlcLink *link, const uint8_t *frame, uint16_t len);

// The turn. A frame has landed, so the glass is listening rather than driving:
// this is the only window in which this board puts anything on the pair. The
// reply goes out from inside dispatch(), and anything the machine wanted to
// volunteer since the last frame follows it here.
static void onMessage(HdlcLink *link, const uint8_t *frame, uint16_t len) {
    dispatch(link, frame, len);
    announceFlush();
}

// ── What arrives on the pair, becoming an intent ──────────────────────────
static void dispatch(HdlcLink *link, const uint8_t *frame, uint16_t len) {
    uint8_t        type    = msgType(frame);
    const uint8_t *payload = msgPayload(frame);
    uint16_t       plen    = msgPayloadLen(len);

    // Ahead of the dispatch, so the click lands under the finger rather than
    // after whatever the command sets in motion. Anything the machine decides
    // next — a refusal, a chime — outranks PRIO_UI and pre-empts it.
    if (isUserAction(type)) soundPlay(SND_TICK);

    if (type == MSG_RESP_DISPLAY_USB_REATTACH) {
        displayUsbReattachAck = true;
        return;
    }

    // A hold: START on finger down, TICK every PRIME_TICK_MS while it stays down,
    // STOP on lift. The machine announces all three, and a refusal.
    if (type == MSG_PRIME_START && plen >= sizeof(ChannelPayload)) {
        machinePrimeBegin(payload[0]);
        return;
    }
    if (type == MSG_PRIME_TICK && plen >= sizeof(ChannelPayload)) {
        machinePrimeTick(payload[0]);
        return;
    }
    if (type == MSG_PRIME_STOP && plen >= sizeof(ChannelPayload)) {
        machinePrimeEnd();
        return;
    }

    // A bounded run. MSG_RESP_PUMP_DONE goes out from onPumpDone(), with the head
    // already stopped.
    if (type == MSG_PUMP_RUN && plen >= sizeof(PumpRunPayload)) {
        PumpRunPayload req;
        memcpy(&req, payload, sizeof(req));
        Serial.printf("\n[J9] MSG_PUMP_RUN ch=%u ms=%u\n", req.channel, req.ms);
        if (!machinePumpRun(req.channel, req.ms))
            link->sendResponse(machineState() == ST_IDLE ? MSG_ERR_SLOT_INVALID : MSG_ERR_BUSY,
                               req.channel);
        return;
    }

    // A click from the glass. Neither display carries a sounder, so this frame is
    // the entire path from a finger on the panel to a sound in the room — which is
    // why the glass sends it on touch-down rather than on the click, and why
    // nothing is sent back: an ack would double the traffic to acknowledge a tick.
    if (type == MSG_SOUND_PLAY && plen >= sizeof(SoundPlayPayload)) {
        soundPlay((SoundId)payload[0]);
        return;
    }

    if (type == MSG_SOUND_CFG_GET) {
        SoundCfgPayload c;
        fillSoundCfg(c);
        link->send(MSG_RESP_SOUND_CFG, &c, sizeof(c));
        return;
    }

    // The controller owns these and persists them; the answer is what it now
    // holds, not an echo of what was asked for, so a value it clamped comes back
    // clamped and the glass shows the truth.
    if (type == MSG_SOUND_CFG_SET && plen >= sizeof(SoundCfgPayload)) {
        SoundCfgPayload req;
        memcpy(&req, payload, sizeof(req));
        soundSetVolume(req.volume);
        soundSetQuiet(req.quietOn != 0, req.quietStart, req.quietEnd, req.quietVolume);
        Serial.printf("\n[J9] sound cfg: volume %u, quiet %s %02u:00-%02u:00 at %u\n",
                      req.volume, req.quietOn ? "on" : "off",
                      req.quietStart, req.quietEnd, req.quietVolume);
        SoundCfgPayload c;
        fillSoundCfg(c);
        link->send(MSG_RESP_SOUND_CFG, &c, sizeof(c));
        return;
    }

    if (type == MSG_STATUS_REQ) {
        StatusPayload s{};
        s.uptimeS      = millis() / 1000;
        s.freeHeap     = ESP.getFreeHeap();
        s.framesRx     = j9.framesRx;
        s.framesTx     = j9.framesTx;
        s.gasMv        = (uint16_t)analogReadMilliVolts(PIN_GAS_AOUT);
        s.flags        = (machineGasTripped()  ? STATUS_F_GAS_TRIP : 0)
                       | (machineIsPriming()   ? STATUS_F_PRIMING  : 0);
        s.primeChannel = machinePumpChannel();
        strncpy(s.version, FW_VERSION, sizeof(s.version) - 1);
        link->send(MSG_RESP_STATUS, &s, sizeof(s));
        return;
    }

    // The clean cycle runs the manifold, which hangs off the two MCP23017s this
    // image leaves untouched.
    if (type == MSG_CLEAN_START) {
        link->sendResponse(MSG_ERR_UNSUPPORTED, plen ? payload[0] : 0);
        Serial.println("\n[J9] MSG_CLEAN_START -> unsupported (no valve drive in this build)");
        return;
    }

    if (type == MSG_TEXT) {
        char text[96];
        uint16_t n = plen < sizeof(text) - 1 ? plen : sizeof(text) - 1;
        memcpy(text, payload, n);
        text[n] = '\0';
        Serial.printf("\n[J9] text: %s\n", text);
        return;
    }

    Serial.printf("\n[J9] type 0x%02X, %u byte(s), raw", type, plen);
    for (uint16_t i = 0; i < len && i < 16; i++) Serial.printf(" %02X", frame[i]);
    Serial.println();
}

void linkBegin() {
    machineOnPrimeState = onPrimeState;
    machineOnPumpDone   = onPumpDone;

    Serial1.begin(RS485_BAUD, SERIAL_8N1, PIN_485_RO, PIN_485_DI);
    j9.onMessage = onMessage;
    j9.begin(j9Stream, "J9");
}

void linkService() { j9.service(); }

// ── Development USB recovery ─────────────────────────────────────────────
//
// The Waveshare puts RS485 on GPIO43/44. In the application those pads are UART1;
// in the ESP32-S3 ROM download loader they are UART0. A USB upload aimed at the wrong
// board can leave that ROM loader running, so the same J9 pair that normally carries
// HDLC can safely ask it to run the existing flash image. The sequence is esptool's
// ROM "soft reset": SYNC, zero-length FLASH_BEGIN, FLASH_END(run). A zero-length begin
// erases and writes nothing.

static size_t slipPacket(uint8_t *out, size_t cap, uint8_t op,
                         const uint8_t *data, uint16_t len) {
    uint8_t packet[64];
    if ((size_t)len + 8 > sizeof(packet)) return 0;
    packet[0] = 0x00;       // host -> ROM
    packet[1] = op;
    packet[2] = (uint8_t)(len & 0xff);
    packet[3] = (uint8_t)(len >> 8);
    memset(packet + 4, 0, 4);   // checksum; these commands use zero
    if (len) memcpy(packet + 8, data, len);

    size_t n = 0;
    if (n < cap) out[n++] = 0xc0;
    for (size_t i = 0; i < (size_t)len + 8; i++) {
        uint8_t b = packet[i];
        if (b == 0xc0 || b == 0xdb) {
            if (n + 2 > cap) return 0;
            out[n++] = 0xdb;
            out[n++] = b == 0xc0 ? 0xdc : 0xdd;
        } else {
            if (n + 1 > cap) return 0;
            out[n++] = b;
        }
    }
    if (n + 1 > cap) return 0;
    out[n++] = 0xc0;
    return n;
}

static bool rawWrite(const uint8_t *bytes, size_t len) {
    while (Serial1.available()) Serial1.read();
    Serial1.write(bytes, len);
    Serial1.flush();

    // U7 receives while it drives, so its own packet comes back before the far end
    // can answer. Remove only an exact echo; a mismatch is a collision, not a reply.
    size_t echoed = 0;
    unsigned long until = millis() + 100;
    while (echoed < len && (long)(millis() - until) < 0) {
        if (!Serial1.available()) { delay(1); continue; }
        if ((uint8_t)Serial1.read() != bytes[echoed++]) return false;
    }
    return echoed == len;
}

static bool rawResponse(uint8_t wantedOp, unsigned long timeoutMs) {
    uint8_t packet[64];
    size_t n = 0;
    bool inFrame = false, escaped = false;
    unsigned long until = millis() + timeoutMs;

    while ((long)(millis() - until) < 0) {
        if (!Serial1.available()) { delay(1); continue; }
        uint8_t b = (uint8_t)Serial1.read();
        if (b == 0xc0) {
            if (inFrame && n >= 10) {
                // response, operation, payload length, value, then status. ESP32-S3
                // ROM responses carry a zero status byte at packet[8]. Extra SYNC
                // replies are expected and skipped while waiting for the next op.
                uint16_t plen = (uint16_t)packet[2] | ((uint16_t)packet[3] << 8);
                if (packet[0] == 0x01 && packet[1] == wantedOp &&
                    plen <= n - 8 && plen >= 2 && packet[8] == 0) return true;
            }
            inFrame = true; escaped = false; n = 0;
            continue;
        }
        if (!inFrame) continue;
        if (escaped) {
            if (b == 0xdc) b = 0xc0;
            else if (b == 0xdd) b = 0xdb;
            else { inFrame = false; n = 0; }
            escaped = false;
        } else if (b == 0xdb) {
            escaped = true;
            continue;
        }
        if (n < sizeof(packet)) packet[n++] = b;
        else { inFrame = false; n = 0; }
    }
    return false;
}

static bool romCommand(uint8_t op, const uint8_t *data, uint16_t len,
                       unsigned long timeoutMs) {
    uint8_t framed[96];
    size_t n = slipPacket(framed, sizeof(framed), op, data, len);
    return n && rawWrite(framed, n) && rawResponse(op, timeoutMs);
}

static bool displayRomRun() {
    // esptool loader.py: sync payload, then ESP32-S3's five-word FLASH_BEGIN.
    uint8_t sync[36] = {0x07, 0x07, 0x12, 0x20};
    memset(sync + 4, 0x55, 32);
    const uint8_t flashBegin[20] = {
        0,0,0,0,  0,0,0,0,  0x00,0x04,0,0,  0,0,0,0,  0,0,0,0
    };
    const uint8_t flashEnd[4] = {1, 0, 0, 0};   // run user code, do not reboot to loader

    j9.end();
    Serial1.end();
    Serial1.begin(RS485_BAUD, SERIAL_8N1, PIN_485_RO, PIN_485_DI);
    while (Serial1.available()) Serial1.read();

    bool synced = romCommand(0x08, sync, sizeof(sync), 500);
    bool began = synced && romCommand(0x02, flashBegin, sizeof(flashBegin), 500);

    bool finishSent = false;
    if (began) {
        uint8_t framed[32];
        size_t n = slipPacket(framed, sizeof(framed), 0x04, flashEnd, sizeof(flashEnd));
        // The ROM can jump before finishing its reply. Exact local echo proves the
        // command reached U7 and the pair; SYNC + FLASH_BEGIN proved who was listening.
        finishSent = n && rawWrite(framed, n);
        delay(750);
    }

    Serial1.end();
    Serial1.begin(RS485_BAUD, SERIAL_8N1, PIN_485_RO, PIN_485_DI);
    j9.onMessage = onMessage;
    j9.begin(j9Stream, "J9");
    return began && finishSent;
}

bool linkDisplayUsbReattach() {
    displayUsbReattachAck = false;

    // The current application gets first refusal. Retry because this explicit
    // development request is the rare controller-originated frame and can meet a
    // status poll on the half-duplex pair.
    for (uint8_t attempt = 0; attempt < 3 && !displayUsbReattachAck; attempt++) {
        j9.send(MSG_DISPLAY_USB_REATTACH, nullptr, 0);
        unsigned long until = millis() + 200;
        while ((long)(millis() - until) < 0 && !displayUsbReattachAck) {
            j9.service();
            delay(2);
        }
    }
    if (displayUsbReattachAck) {
        Serial.println("\nDISPLAY_USB:APP accepted — USB PHY will detach and timer-wake");
        return true;
    }

    Serial.println("\nDISPLAY_USB: no application ack; probing the ROM loader on J9 UART0");
    if (displayRomRun()) {
        Serial.println("DISPLAY_USB:ROM run command sent — existing flash image is starting");
        return true;
    }
    Serial.println("DISPLAY_USB:UNREACHABLE — neither the application nor ROM loader answered");
    return false;
}

// The one thing here that speaks unprompted, and it is a bench command: it exists
// to prove this board's half of the pair carries, with nobody expected to answer.
void linkPing() {
    size_t before = j9Stream.echoSwallowed();
    uint32_t rxBefore = j9.framesRx;
    const char *msg = "ping";
    j9.send(MSG_TEXT, msg, strlen(msg));

    unsigned long t0 = millis();
    while (millis() - t0 < 1000) { j9.service(); delay(2); }

    size_t echoed = j9Stream.echoSwallowed() - before;
    Serial.printf("\nping — %u byte(s) went out and came back through U7\n", (unsigned)echoed);
    if (!echoed)
        Serial.println("  the frame did not return: IO32, U7, the pair, or R6");
    else if (j9.framesRx > rxBefore)
        Serial.println("  and the display answered");
    else
        Serial.println("  this board's half carries; nothing answered from the far end");
}

void linkReport() {
    Serial.printf("\nJ9  IO%d DI / IO%d RO @ %ld — frames rx %lu / tx %lu, bytes rx %lu / tx %lu\n",
                  PIN_485_DI, PIN_485_RO, RS485_BAUD,
                  (unsigned long)j9.framesRx, (unsigned long)j9.framesTx,
                  (unsigned long)j9.bytesRx, (unsigned long)j9.bytesTx);
    if (j9.lastRxMs)
        Serial.printf("    last frame %lu ms ago\n", millis() - j9.lastRxMs);
    else
        Serial.println("    nothing has arrived — the display is unpowered, unflashed, or A/B is swapped");
    Serial.printf("    announcements held %u, dropped %lu\n",
                  (unsigned)annCount, (unsigned long)annDropped);
    Serial.printf("    echo swallowed %u, outstanding %u, high-water %u, desyncs %u\n",
                  (unsigned)j9Stream.echoSwallowed(), (unsigned)j9Stream.echoOutstanding(),
                  (unsigned)j9Stream.echoHighWater(), (unsigned)j9Stream.echoDesyncs());
    if (j9Stream.echoDesyncs())
        Serial.println("    a desync is a frame both ends talked over — the count rising under load\n"
                       "    is the pair colliding, not the framer");
}
