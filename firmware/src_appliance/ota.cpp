#include "ota.h"

#include "proto_msg.h"
#include "ota_receiver.h"
#include "link.h"
#include "faucet_link.h"

// Each chunk plus its 4-byte offset has to fit what its link can carry, and
// the length that carries it has to be wide enough to say so.
static_assert(sizeof(OtaBeginPayload) <= 12,
              "OTA_BEGIN is queued in link.cpp's Announce.data");
static_assert(OTA_CHUNK_J9 + 4 <= J9_MAX_PAYLOAD,
              "a J9 chunk plus its offset has to fit one HDLC frame");
static_assert(OTA_CHUNK_J3 + 4 <= UINT16_MAX, "the send length is uint16_t");

// ── The session ───────────────────────────────────────────────────────────
static OtaTarget target = OTA_TGT_NONE;
static uint32_t  imgSize = 0;
static uint32_t  imgCrc = 0;
static uint16_t  chunk = 0;
static uint32_t  lastReported = 0;
static uint32_t  openedAtMs = 0;
static uint8_t   imgKind = OTA_KIND_APP;

// The console carries every image byte, so 115200 is a ceiling on the whole
// transfer no matter how fast the links get. A session raises it and drops back
// when it ends. Nothing can be stranded at the high rate: opening this port
// resets the board, and a reset always comes up at OTA_CONSOLE_BAUD_IDLE.
static const uint32_t OTA_CONSOLE_BAUD_IDLE = 115200;
static const uint32_t OTA_CONSOLE_BAUD_FAST = 921600;
static bool consoleFast = false;

static void consoleBaud(uint32_t rate) {
    Serial.flush();
    Serial.updateBaudRate(rate);
    consoleFast = (rate != OTA_CONSOLE_BAUD_IDLE);
}
// Until the far end says something, BEGIN may simply have been dropped —
// opening this board's console resets it, and a link takes seconds to come
// back up. So it is offered again until a receiver answers.
static bool      sawReceiver = false;
static uint32_t  beganAtMs = 0;

// One chunk, which is the whole of what this board holds of an image.
static uint8_t   buf[OTA_CHUNK_J3];
static uint16_t  bufLen = 0;
static uint32_t  bufOffset = 0;
static bool      bufFull = false;

// Raw-mode state: how many bytes of the current chunk the host still owes.
static uint16_t  hostOwes = 0;
static uint16_t  hostGot = 0;

// `ota self` writes into this board's own spare slot rather than onto a link.
static OtaReceiver selfRx;

static const char *targetName(OtaTarget t) {
    switch (t) {
        case OTA_TGT_SELF:      return "self";
        case OTA_TGT_FAUCET:    return "faucet";
        case OTA_TGT_ENCLOSURE: return "enclosure";
        default:                return "none";
    }
}

// Volunteering a frame. J3 is full duplex and takes it now; J9 is not, so the
// enclosure's copy waits in the announcement queue for its next turn.
static bool volunteer(OtaTarget t, uint8_t type, const void *data, uint8_t len) {
    if (t == OTA_TGT_FAUCET) return faucetLinkSendOta(type, data, len);
    if (t == OTA_TGT_ENCLOSURE) { linkQueueOta(type, data, len); return true; }
    return false;
}

// Answering a request, from inside its dispatch.
// uint16_t: a J3 chunk plus its offset is 1028 bytes, and a uint8_t length
// here silently became 4 — every frame carrying an offset and no image.
static bool reply(OtaTarget t, uint8_t type, const void *data, uint16_t len) {
    if (t == OTA_TGT_FAUCET)    return faucetLinkSendOta(type, data, len);
    if (t == OTA_TGT_ENCLOSURE) return linkReplyOta(type, data, len);
    return false;
}

static void endSession(const char *how, uint8_t state, uint8_t err) {
    if (target != OTA_TGT_NONE && target != OTA_TGT_SELF && state != OTA_STATE_DONE)
        volunteer(target, MSG_OTA_ABORT, nullptr, 0);
    if (target == OTA_TGT_SELF && state != OTA_STATE_DONE) selfRx.abort();
    Serial.printf("\nOTA:%s state=%u err=%u\n", how, state, err);
    if (consoleFast) { delay(20); consoleBaud(OTA_CONSOLE_BAUD_IDLE); }
    target = OTA_TGT_NONE;
    sawReceiver = false;
    hostOwes = hostGot = 0;
    bufFull = false;
    bufLen = 0;
}

// ── Asking the host for the bytes a receiver just asked us for ────────────
static void askHost(uint32_t offset) {
    uint32_t remain = imgSize - offset;
    uint16_t want = (remain < chunk) ? (uint16_t)remain : chunk;
    bufOffset = offset;
    bufLen = want;
    bufFull = false;
    hostOwes = want;
    hostGot = 0;
    Serial.printf("\nOTA:NEED %lu %u\n", (unsigned long)offset, want);
}

bool otaAwaitingHostBytes() { return hostOwes > 0; }

void otaFeedHostBytes() {
    while (hostOwes > 0 && Serial.available()) {
        int c = Serial.read();
        if (c < 0) break;
        buf[hostGot++] = (uint8_t)c;
        hostOwes--;
    }
    if (hostOwes > 0 || bufFull) return;

    bufFull = true;
    if (target == OTA_TGT_SELF) {
        if (!selfRx.write(bufOffset, buf, bufLen)) {
            endSession("FAIL", selfRx.state, selfRx.err);
            return;
        }
        if (selfRx.nextOffset() < imgSize) {
            askHost(selfRx.nextOffset());
        } else if (selfRx.finish()) {
            endSession("DONE", selfRx.state, selfRx.err);
        } else {
            endSession("FAIL", selfRx.state, selfRx.err);
        }
        return;
    }

    // The bytes are held now. On J3 they can go straight out, because both ends
    // may drive it at once. On J9 they cannot: the enclosure is polling, and the
    // frame leaves inside the turn its next request opens — otaOnRequest answers
    // it from this buffer without a further host round trip.
    if (target != OTA_TGT_FAUCET) return;

    uint8_t frame[4 + OTA_CHUNK_J3];
    memcpy(frame, &bufOffset, 4);
    memcpy(frame + 4, buf, bufLen);
    if (!faucetLinkSendOta(MSG_OTA_DATA, frame, (uint16_t)(4 + bufLen)))
        Serial.println("\nOTA:HOLD link busy");   // the receiver re-asks; bytes stay held
}

// ── What a receiver on either link asks for ───────────────────────────────
bool otaOnRequest(OtaTarget from, const uint8_t *payload, uint16_t plen) {
    if (target == OTA_TGT_NONE || from != target) return false;
    sawReceiver = true;
    if (plen < sizeof(OtaReqPayload)) return false;

    OtaReqPayload req;
    memcpy(&req, payload, sizeof(req));
    if (req.offset > imgSize) return false;

    // Already holding exactly what it wants: answer straight from the buffer.
    if (bufFull && req.offset == bufOffset) {
        uint8_t frame[4 + OTA_CHUNK_J3];
        memcpy(frame, &bufOffset, 4);
        memcpy(frame + 4, buf, bufLen);
        const uint32_t sent = bufOffset;
        const uint16_t sentLen = bufLen;
        const bool ok = reply(target, MSG_OTA_DATA, frame, (uint16_t)(4 + bufLen));

        // Prefetch. Without this every chunk costs a full host round trip that
        // J9 cannot overlap — the receiver asks, this board has nothing, the
        // turn is spent, and the bytes only leave on the request after that.
        // Asking now means the next request finds them already here.
        if (ok && hostOwes == 0 && (uint32_t)(sent + sentLen) < imgSize)
            askHost(sent + sentLen);
        return ok;
    }

    if (hostOwes == 0) askHost(req.offset);
    return false;   // the bytes go out when the host supplies them
}

void otaOnState(OtaTarget from, const uint8_t *payload, uint16_t plen) {
    if (target == OTA_TGT_NONE || from != target) return;
    sawReceiver = true;
    if (plen < sizeof(OtaStatePayload)) return;

    OtaStatePayload st;
    memcpy(&st, payload, sizeof(st));

    if (st.state == OTA_STATE_DONE)   { endSession("DONE", st.state, st.err); return; }
    if (st.state == OTA_STATE_FAILED) { endSession("FAIL", st.state, st.err); return; }

    if (st.received >= lastReported + 65536) {
        lastReported = st.received;
        Serial.printf("\nOTA:AT %lu/%lu\n",
                      (unsigned long)st.received, (unsigned long)imgSize);
    }
}

void otaService() {
    if (target == OTA_TGT_NONE) return;

    // A session that stops moving says so. While the host owes bytes the
    // console reads raw and answers nothing, so without this a stall is
    // indistinguishable from a board that has stopped existing.
    static uint32_t lastMoveMs = 0;
    static uint32_t lastSeen = 0;
    if (lastReported != lastSeen) { lastSeen = lastReported; lastMoveMs = millis(); }
    if (lastMoveMs == 0) lastMoveMs = millis();
    if (millis() - lastMoveMs >= 4000) {
        lastMoveMs = millis();
        Serial.printf("\nOTA:STALL owes=%u got=%u bufOff=%lu bufLen=%u full=%d seen=%d\n",
                      hostOwes, hostGot, (unsigned long)bufOffset, bufLen,
                      (int)bufFull, (int)sawReceiver);
    }

    if (!sawReceiver && target != OTA_TGT_SELF && millis() - beganAtMs >= 500) {
        beganAtMs = millis();
        OtaBeginPayload begin{imgSize, imgCrc, chunk, imgKind};
        volunteer(target, MSG_OTA_BEGIN, &begin, sizeof(begin));
    }

    // A receiver that stops asking is a session nobody will finish. The board
    // keeps running what it booted either way; this just frees the console.
    if (millis() - openedAtMs > 600000UL) endSession("FAIL", OTA_STATE_FAILED, OTA_ERR_NONE);
}

// ── Console ───────────────────────────────────────────────────────────────
void otaConsole(const String &line) {
    String rest = line.substring(3);
    rest.trim();

    if (rest.length() == 0) {
        Serial.printf("\nthis board: %s\n",
                      OtaReceiver::slotAvailable()
                          ? "a spare OTA slot is present — it can take an update"
                          : "SINGLE SLOT — no ota_1, so it cannot take an update");
        Serial.println("  ota <self|faucet|enclosure|art> <size> <crc32>");
        if (target != OTA_TGT_NONE)
            Serial.printf("  a session to %s is open, %lu bytes\n",
                          targetName(target), (unsigned long)imgSize);
        return;
    }

    if (rest == "abort") { endSession("ABORT", OTA_STATE_IDLE, OTA_ERR_NONE); return; }

    char who[16] = {0};
    unsigned long size = 0, crc = 0;
    if (sscanf(rest.c_str(), "%15s %lu %lu", who, &size, &crc) != 3) {
        Serial.println("\nusage: ota <self|faucet|enclosure|art> <size> <crc32>");
        return;
    }

    OtaTarget t = OTA_TGT_NONE;
    imgKind = OTA_KIND_APP;
    if (!strcmp(who, "self"))           t = OTA_TGT_SELF;
    else if (!strcmp(who, "faucet"))    t = OTA_TGT_FAUCET;
    else if (!strcmp(who, "enclosure")) t = OTA_TGT_ENCLOSURE;
    // The enclosure's art partition rides the same session; only what the
    // receiver opens at the far end differs.
    else if (!strcmp(who, "art"))     { t = OTA_TGT_ENCLOSURE; imgKind = OTA_KIND_ART; }
    else { Serial.println("\nusage: ota <self|faucet|enclosure|art> <size> <crc32>"); return; }

    if (target != OTA_TGT_NONE) { Serial.println("\nOTA:FAIL a session is already open"); return; }
    if (size == 0) { Serial.println("\nOTA:FAIL size is zero"); return; }

    target = t;
    imgSize = size;
    imgCrc = crc;
    chunk = (t == OTA_TGT_ENCLOSURE) ? OTA_CHUNK_J9 : OTA_CHUNK_J3;
    lastReported = 0;
    openedAtMs = millis();
    beganAtMs = millis();
    sawReceiver = false;
    bufFull = false;
    bufLen = 0;

    Serial.printf("\nOTA:BAUD %lu\n", (unsigned long)OTA_CONSOLE_BAUD_FAST);
    delay(20);
    consoleBaud(OTA_CONSOLE_BAUD_FAST);

    if (t == OTA_TGT_SELF) {
        if (!selfRx.begin(imgSize, imgCrc, imgKind)) {
            Serial.printf("\nOTA:FAIL state=%u err=%u\n", selfRx.state, selfRx.err);
            target = OTA_TGT_NONE;
            return;
        }
        Serial.printf("\nOTA:BEGIN self size=%lu crc=%lu chunk=%u\n",
                      (unsigned long)imgSize, (unsigned long)imgCrc, chunk);
        askHost(0);
        return;
    }

    OtaBeginPayload begin{imgSize, imgCrc, chunk, imgKind};
    volunteer(t, MSG_OTA_BEGIN, &begin, sizeof(begin));
    Serial.printf("\nOTA:BEGIN %s size=%lu crc=%lu chunk=%u\n",
                  targetName(t), (unsigned long)imgSize, (unsigned long)imgCrc, chunk);
}
