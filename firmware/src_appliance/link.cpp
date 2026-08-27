#include <Arduino.h>

#include "link.h"
#include "ota.h"
#include "versions.h"
#include "flavor.h"
#include "idle.h"
#include "flavor_link_policy.h"
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
static bool wifiApAck = false;
static WifiApStatePayload wifiApState{};
static flavor_link_policy::TokenLedger enclosureFlavorTokens;
static uint32_t enclosureFlavorDuplicates = 0;
static uint32_t enclosureFlavorInvalid = 0;
static uint32_t enclosurePrimeSessionLastSentRevision = 0;
static bool enclosurePrimeSessionStateSent = false;
static uint8_t j9TurnReplyHighWater = 0;
static uint32_t j9TurnReplyOverruns = 0;

static uint8_t flavorStateFlags() {
    return (flavorEstablished()       ? FLAVOR_STATE_F_ESTABLISHED    : 0)
         | (flavorPersisted()         ? FLAVOR_STATE_F_PERSISTED      : 0)
         | (flavorPersistenceError()  ? FLAVOR_STATE_F_PERSIST_ERROR : 0);
}

static void sendFlavorState(HdlcLink *link, uint32_t token) {
    FlavorStatePayload state{flavorSelected(), flavorStateFlags(), token};
    link->send(MSG_RESP_FLAVOR_STATE, &state, sizeof(state));
}

static void sendPrimeSessionState(HdlcLink *link) {
    MachinePrimeSessionState current;
    machineReadPrimeSessionState(current);
    PrimeSessionStatePayload state{
        current.phase,
        current.channel,
        current.owner,
        current.outcome,
        current.elapsedMs,
        current.revision,
        current.sessionToken,
        current.holdToken,
    };
    link->send(MSG_RESP_PRIME_SESSION, &state, sizeof(state));
    enclosurePrimeSessionLastSentRevision = current.revision;
    enclosurePrimeSessionStateSent = true;
}

// J9 cannot be driven asynchronously. Revisions therefore coalesce here: when
// any enclosure display frame gives the main board a safe turn, only the newest
// absolute state is sent. A query/action response calls sendPrimeSessionState()
// directly and consumes the same revision, avoiding a duplicate snapshot.
static void sendChangedPrimeSessionState(HdlcLink *link) {
    MachinePrimeSessionState current;
    machineReadPrimeSessionState(current);
    // Revision zero is also the main board's authoritative OFF after boot. It
    // still has to cross J9 once so a display that survived this main board's
    // reset cannot retain an old READY/RUNNING snapshot indefinitely.
    if (enclosurePrimeSessionStateSent &&
        current.revision == enclosurePrimeSessionLastSentRevision) return;
    sendPrimeSessionState(link);
}

// What the main board currently holds, as the glass reads it.
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
// The main board answers; it does not interrupt. A prime that timed out and a bounded
// run that finished both come from machineService(), on a clock of their own, and
// putting them straight on the wire means driving it while the glass may already
// be mid-frame — which collides, destroys the main board's own echo, and costs
// whichever frame the glass was sending (rs485_echo.h).
//
// So an announcement waits for a turn. It is held here and goes out inside the
// window right after a frame arrives, when the glass is known to be listening
// rather than talking. The glass polls on an interval for exactly this reason,
// so the wait is bounded by that poll and not by whether anyone touches anything.
// 12 bytes because OtaBeginPayload is 10 and is queued here like anything
// else the main board volunteers; every other announcement fits in 8.
struct Announce { uint8_t type; uint8_t len; uint8_t data[12]; };
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
static void announceFlushOne() {
    if (!annCount) return;
    Announce &a = annQ[annTail];
    j9.send(a.type, a.len ? a.data : nullptr, a.len);
    annTail = (uint8_t)((annTail + 1) % ANN_DEPTH);
    annCount--;
}

static void onPrimeState(uint8_t state, uint8_t channel, uint32_t ms) {
    if (machinePrimeEventIsSessionOwned()) return;
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
    return type == MSG_PUMP_RUN || type == MSG_CLEAN_START || type == MSG_FILL_START ||
           type == MSG_SOUND_CFG_SET || type == MSG_FLAVOR_ART_SET ||
           type == MSG_PRIME_SESSION_SET;
}

static void dispatch(HdlcLink *link, const uint8_t *frame, uint16_t len);

// The turn. A frame has landed, so the glass is listening rather than driving:
// this is the only window in which the main board puts anything on the pair.
// Exactly one reply may leave in a turn. The enclosure releases its own
// transmit guard after the first complete frame, so following that frame with
// another would let its next request collide with our tail. Direct command
// replies win; otherwise the latest prime truth wins; otherwise one queued
// machine announcement gets the turn. Anything deferred remains eligible on
// the next enclosure poll.
static void onMessage(HdlcLink *link, const uint8_t *frame, uint16_t len) {
    const uint32_t framesBefore = link->framesTx;
    struct TurnReplyAudit {
        HdlcLink *link;
        uint32_t before;
        ~TurnReplyAudit() {
            const uint32_t replies = link->framesTx - before;
            if (replies > j9TurnReplyHighWater)
                j9TurnReplyHighWater = replies > UINT8_MAX
                    ? UINT8_MAX : static_cast<uint8_t>(replies);
            if (replies > 1) ++j9TurnReplyOverruns;
        }
    } audit{link, framesBefore};

    // Routine snapshots are also the glass's polling clock. If machine news is
    // waiting, use this turn for that news and let the routine query retry on
    // its normal cadence. Otherwise a status/flavor reply on every poll would
    // starve an asynchronous pump completion or a prime transition forever.
    const uint8_t type = msgType(frame);
    if (type == MSG_FLAVOR_QUERY || type == MSG_STATUS_REQ) {
        sendChangedPrimeSessionState(link);
        if (link->framesTx != framesBefore) return;
        announceFlushOne();
        if (link->framesTx != framesBefore) return;
    }

    dispatch(link, frame, len);
    if (link->framesTx != framesBefore) return;
    sendChangedPrimeSessionState(link);
    if (link->framesTx != framesBefore) return;
    announceFlushOne();
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
    // A press is presence whether or not it also asked for something.
    if (isUserAction(type) || type == MSG_SOUND_PLAY || type == MSG_TOUCH) idleTouched();

    if (type == MSG_RESP_WIFI_AP && plen >= sizeof(WifiApStatePayload)) {
        memcpy(&wifiApState, payload, sizeof(wifiApState));
        wifiApAck = true;
        return;
    }

    if (type == MSG_RESP_DISPLAY_USB_REATTACH) {
        displayUsbReattachAck = true;
        return;
    }

    // The enclosure display has no authoritative flavor cache. It asks for
    // main board truth at boot and on a short cadence, including while dark,
    // which gives the main board a collision-free turn to publish a faucet
    // selection. A selection is absolute and tokenized so an HDLC/application
    // retry cannot turn one press into two sounds or state changes.
    if (type == MSG_FLAVOR_QUERY) {
        sendFlavorState(link, 0);
        return;
    }

    // The logo a channel wears is main-board-owned like the selection, so the
    // enclosure states the pair and reads back what the main board now holds.
    // Firmware for this display. A request is answered from the held chunk if
    // the main board has it; otherwise this turn passes and the host is asked,
    // and the enclosure's next poll gets the bytes.
    if (type == MSG_RESP_VERSION && plen >= sizeof(VersionPayload)) {
        VersionPayload v;
        memcpy(&v, payload, sizeof(v));
        v.version[FW_VERSION_MAX] = 0;
        versionsOnReport(OTA_TGT_ENCLOSURE, v.version, v.artCrc32);
        return;
    }
    if (type == MSG_OTA_REQ)  { otaOnRequest(OTA_TGT_ENCLOSURE, payload, plen); return; }
    if (type == MSG_RESP_OTA) { otaOnState(OTA_TGT_ENCLOSURE, payload, plen);   return; }

    if (type == MSG_TOUCH) return;   // presence only; nothing to answer

    if (type == MSG_IDLE_QUERY) {
        IdlePayload idle{idleAsleep() ? (uint8_t)1 : (uint8_t)0, idleWindowMs()};
        link->send(MSG_RESP_IDLE, &idle, sizeof(idle));
        return;
    }

    if (type == MSG_FLAVOR_ART_QUERY) {
        FlavorArtPayload art{{flavorArt(0), flavorArt(1)}};
        link->send(MSG_RESP_FLAVOR_ART, &art, sizeof(art));
        return;
    }

    if (type == MSG_FLAVOR_ART_SET && plen >= sizeof(FlavorArtPayload)) {
        FlavorArtPayload request;
        memcpy(&request, payload, sizeof(request));
        if (!flavorArtSet(request.art[0], request.art[1])) {
            link->sendResponse(MSG_ERR_SLOT_INVALID, request.art[0]);
            return;
        }
        Serial.printf("\n[J9] artwork %u/%u\n", flavorArt(0), flavorArt(1));
        FlavorArtPayload art{{flavorArt(0), flavorArt(1)}};
        link->send(MSG_RESP_FLAVOR_ART, &art, sizeof(art));
        return;
    }

    if (type == MSG_FLAVOR_SELECT && plen >= sizeof(FlavorRequestPayload)) {
        FlavorRequestPayload request;
        memcpy(&request, payload, sizeof(request));
        if (request.flavor > PUMP_CHANNEL_B || request.token == 0) {
            enclosureFlavorInvalid++;
            link->sendResponse(MSG_ERR_SLOT_INVALID, request.flavor);
            return;
        }

        const bool duplicate = enclosureFlavorTokens.duplicateOrRemember(request.token);
        if (duplicate) {
            enclosureFlavorDuplicates++;
        } else {
            flavorSelect(request.flavor);
            if (request.flags & FLAVOR_REQ_F_AUDIBLE) soundPlay(SND_TICK);
            Serial.printf("\n[J9] enclosure selected flavor %u%s\n",
                          flavorSelected() + 1,
                          flavorPersisted() ? "" : " — persistence pending");
        }
        sendFlavorState(link, request.token);
        return;
    }

    if (type == MSG_PRIME_SESSION_QUERY &&
        plen >= sizeof(PrimeSessionQueryPayload)) {
        PrimeSessionQueryPayload query;
        memcpy(&query, payload, sizeof(query));
        machinePrimeSessionQuery(query.sessionToken);
        sendPrimeSessionState(link);
        return;
    }

    if (type == MSG_PRIME_SESSION_SET &&
        plen >= sizeof(PrimeSessionRequestPayload)) {
        PrimeSessionRequestPayload request;
        memcpy(&request, payload, sizeof(request));
        if (request.channel > PUMP_CHANNEL_B || request.sessionToken == 0 ||
            (request.action != PRIME_SESSION_ACTIVATE &&
             request.action != PRIME_SESSION_CANCEL)) {
            link->sendResponse(MSG_ERR_SLOT_INVALID, request.channel);
            return;
        }

        bool accepted = false;
        if (request.action == PRIME_SESSION_ACTIVATE) {
            MachinePrimeSessionState before;
            machineReadPrimeSessionState(before);
            accepted = machinePrimeSessionActivate(
                request.channel, request.sessionToken);
            MachinePrimeSessionState after;
            machineReadPrimeSessionState(after);
            if (accepted && after.revision != before.revision)
                soundPlay(SND_TICK);
        } else {
            MachinePrimeSessionState before;
            machineReadPrimeSessionState(before);
            accepted = machinePrimeSessionCancel(request.sessionToken, true);
            MachinePrimeSessionState after;
            machineReadPrimeSessionState(after);
            // Only a physical exit of a live session clicks. An idempotent
            // retry or an OFF-state tombstone used to retire an in-flight
            // ACTIVATE is silent.
            if (accepted && before.phase != PRIME_SESSION_OFF &&
                after.revision != before.revision) soundPlay(SND_TICK);
        }
        sendPrimeSessionState(link);
        return;
    }

    if ((type == MSG_PRIME_SESSION_HOLD_START ||
         type == MSG_PRIME_SESSION_HOLD_TICK ||
         type == MSG_PRIME_SESSION_HOLD_STOP) &&
        plen >= sizeof(PrimeHoldPayload)) {
        PrimeHoldPayload request;
        memcpy(&request, payload, sizeof(request));
        if (request.channel > PUMP_CHANNEL_B || request.sessionToken == 0 ||
            request.holdToken == 0) {
            link->sendResponse(MSG_ERR_SLOT_INVALID, request.channel);
            return;
        }

        if (type == MSG_PRIME_SESSION_HOLD_START) {
            machinePrimeSessionHoldBegin(MACHINE_PRIME_ENCLOSURE,
                                         request.channel,
                                         request.sessionToken,
                                         request.holdToken);
        } else if (type == MSG_PRIME_SESSION_HOLD_TICK) {
            machinePrimeSessionHoldTick(MACHINE_PRIME_ENCLOSURE,
                                        request.channel,
                                        request.sessionToken,
                                        request.holdToken);
        } else {
            machinePrimeSessionHoldEnd(MACHINE_PRIME_ENCLOSURE,
                                       request.channel,
                                       request.sessionToken,
                                       request.holdToken);
        }
        sendPrimeSessionState(link);
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

    // The main board owns these and persists them; the answer is what it now
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
        s.j9ReplyHighWater = j9TurnReplyHighWater;
        s.j9ReplyOverruns = j9TurnReplyOverruns;
        link->send(MSG_RESP_STATUS, &s, sizeof(s));
        return;
    }

    // The clean cycle and the funnel fill each need a sequenced manifold
    // operation. This image safely initializes the MCP23017s, but exposes no
    // runtime valve operation yet.
    if (type == MSG_CLEAN_START || type == MSG_FILL_START) {
        link->sendResponse(MSG_ERR_UNSUPPORTED, plen ? payload[0] : 0);
        Serial.printf("\n[J9] %s -> unsupported (no valve drive in this build)\n",
                      type == MSG_CLEAN_START ? "MSG_CLEAN_START" : "MSG_FILL_START");
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

// The enclosure cannot be driven asynchronously, so a change waits for the turn
// its next poll gives us.
void linkPublishIdle() {
    IdlePayload idle{idleAsleep() ? (uint8_t)1 : (uint8_t)0, idleWindowMs()};
    announceQueue(MSG_RESP_IDLE, &idle, sizeof(idle));
}

void linkBegin() {
    machineOnPrimeState = onPrimeState;
    machineOnPumpDone   = onPumpDone;

    // 8 KB, because the loop does not always come back quickly: a flash sector
    // erase inside esp_ota_write blocks for tens of milliseconds, and at these
    // rates that is thousands of bytes arriving with nobody draining them. The
    // default 256-byte ring overflows and the frame is simply lost — which
    // looks exactly like a link that has stopped talking.
    Serial1.setRxBufferSize(8192);
    Serial1.begin(RS485_BAUD, SERIAL_8N1, PIN_485_RO, PIN_485_DI);
    j9.onMessage = onMessage;
    j9.begin(j9Stream, "J9");
}

// Volunteered, so it waits for a turn exactly like every other announcement.
void linkQueueOta(uint8_t type, const void *data, uint8_t len) {
    announceQueue(type, data, len);
}

// A reply, sent from inside the dispatch of the request it answers. This is
// the one place OTA bytes may go straight onto the pair.
bool linkReplyOta(uint8_t type, const void *data, uint16_t len) {
    return j9.send(type, data, len) >= 0;
}

void linkService() { j9.service(); }

bool linkDisplayUsbReattach() {
    displayUsbReattachAck = false;

    // Retry because this explicit development request is the rare
    // main-board-originated frame and can meet a status poll on the half-duplex pair.
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

    Serial.println("\nDISPLAY_USB:UNREACHABLE — the display application did not answer");
    return false;
}

// The enclosure raises the bench AP, so this is a main-board-originated frame on
// a pair whose rule is that the main board answers. Same shape as the USB
// reattach above and for the same reason: it can meet a status poll, and the far
// end's transition takes long enough that the first answer may be late. Raising
// an AP that is already up is free at the other end, so a retry costs nothing.
// One main-board-originated frame on a pair whose rule is that the main board
// answers, so it retries: it can meet the enclosure's own poll. 0 drops the
// radio, 1 raises it, 2 only asks. All three are answered the same way.
static bool linkWifiAsk(uint8_t what) {
    wifiApAck = false;
    WifiApPayload req{what, WIFI_BENCH_CHANNEL};
    for (uint8_t attempt = 0; attempt < 4 && !wifiApAck; attempt++) {
        j9.send(MSG_WIFI_BENCH_AP, &req, sizeof(req));
        unsigned long until = millis() + 400;
        while ((long)(millis() - until) < 0 && !wifiApAck) {
            j9.service();
            delay(2);
        }
    }
    return wifiApAck;
}

bool linkWifiAp(bool on) { return linkWifiApMode(on ? 1 : 0); }

bool linkWifiApMode(uint8_t mode) {
    const bool on = (mode != 0);
    // The display raises its radio on a task of its own and answers this frame
    // at once, so the answer to the request is not the answer to the question.
    // Ask, then poll `up` until it moves. Asking twice is free at that end.
    if (!linkWifiAsk(mode)) {
        Serial.println("\nWIFI:AP UNREACHABLE — the enclosure display did not answer");
        return false;
    }

    const unsigned long deadline = millis() + (on ? 12000UL : 8000UL);
    while ((long)(millis() - deadline) < 0) {
        unsigned long until = millis() + 400;
        while ((long)(millis() - until) < 0) { j9.service(); delay(2); }
        if (!linkWifiAsk(2)) continue;
        if ((bool)wifiApState.up == on) {
            Serial.printf("\nWIFI:AP %s\n",
                          on ? "up as '" WIFI_BENCH_SSID "', channel 6, sinking on port 5001"
                             : "down");
            return true;
        }
    }

    Serial.printf("\nWIFI:AP did not come %s — the display answered but its radio did not move\n",
                  on ? "up" : "down");
    return false;
}

// What the sink counted, asked for after a run so the two ends can be compared.
bool linkWifiApState(WifiApStatePayload &out) {
    if (!linkWifiAsk(2)) return false;
    out = wifiApState;
    return true;
}

// The one thing here that speaks unprompted, and it is a bench command: it exists
// to prove the main board's half of the pair carries, with nobody expected to answer.
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
        Serial.println("  the main board's half carries; nothing answered from the far end");
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
    Serial.printf("    replies per received turn high-water %u, overruns %lu\n",
                  (unsigned)j9TurnReplyHighWater,
                  (unsigned long)j9TurnReplyOverruns);
    Serial.printf("    flavor duplicate requests %lu, invalid requests %lu\n",
                  (unsigned long)enclosureFlavorDuplicates,
                  (unsigned long)enclosureFlavorInvalid);
    Serial.printf("    echo swallowed %u, outstanding %u, high-water %u, desyncs %u\n",
                  (unsigned)j9Stream.echoSwallowed(), (unsigned)j9Stream.echoOutstanding(),
                  (unsigned)j9Stream.echoHighWater(), (unsigned)j9Stream.echoDesyncs());
    if (j9Stream.echoDesyncs())
        Serial.println("    a desync is a frame both ends talked over — the count rising under load\n"
                       "    is the pair colliding, not the framer");
}
