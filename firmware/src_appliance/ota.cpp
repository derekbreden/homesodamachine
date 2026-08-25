#include "ota.h"

#include "proto_msg.h"
#include "ota_receiver.h"
#include "link.h"
#include "faucet_link.h"

// ── The session ───────────────────────────────────────────────────────────
static OtaTarget target = OTA_TGT_NONE;
static uint32_t  imgSize = 0;
static uint32_t  imgCrc = 0;
static uint16_t  chunk = 0;
static uint32_t  lastReported = 0;
static uint32_t  openedAtMs = 0;

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
static bool reply(OtaTarget t, uint8_t type, const void *data, uint8_t len) {
    if (t == OTA_TGT_FAUCET)    return faucetLinkSendOta(type, data, len);
    if (t == OTA_TGT_ENCLOSURE) return linkReplyOta(type, data, len);
    return false;
}

static void endSession(const char *how, uint8_t state, uint8_t err) {
    if (target != OTA_TGT_NONE && target != OTA_TGT_SELF && state != OTA_STATE_DONE)
        volunteer(target, MSG_OTA_ABORT, nullptr, 0);
    if (target == OTA_TGT_SELF && state != OTA_STATE_DONE) selfRx.abort();
    Serial.printf("\nOTA:%s state=%u err=%u\n", how, state, err);
    target = OTA_TGT_NONE;
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
    if (!faucetLinkSendOta(MSG_OTA_DATA, frame, (uint8_t)(4 + bufLen)))
        Serial.println("\nOTA:HOLD link busy");   // the receiver re-asks; bytes stay held
}

// ── What a receiver on either link asks for ───────────────────────────────
bool otaOnRequest(OtaTarget from, const uint8_t *payload, uint16_t plen) {
    if (target == OTA_TGT_NONE || from != target) return false;
    if (plen < sizeof(OtaReqPayload)) return false;

    OtaReqPayload req;
    memcpy(&req, payload, sizeof(req));
    if (req.offset > imgSize) return false;

    // Already holding exactly what it wants: answer straight from the buffer
    // without spending a host round trip. This is the retry path.
    if (bufFull && req.offset == bufOffset) {
        uint8_t frame[4 + OTA_CHUNK_J3];
        memcpy(frame, &bufOffset, 4);
        memcpy(frame + 4, buf, bufLen);
        return reply(target, MSG_OTA_DATA, frame, (uint8_t)(4 + bufLen));
    }

    if (hostOwes == 0) askHost(req.offset);
    return false;   // the bytes go out when the host supplies them
}

void otaOnState(OtaTarget from, const uint8_t *payload, uint16_t plen) {
    if (target == OTA_TGT_NONE || from != target) return;
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
        Serial.println("  ota <self|faucet|enclosure> <size> <crc32>");
        if (target != OTA_TGT_NONE)
            Serial.printf("  a session to %s is open, %lu bytes\n",
                          targetName(target), (unsigned long)imgSize);
        return;
    }

    if (rest == "abort") { endSession("ABORT", OTA_STATE_IDLE, OTA_ERR_NONE); return; }

    char who[16] = {0};
    unsigned long size = 0, crc = 0;
    if (sscanf(rest.c_str(), "%15s %lu %lu", who, &size, &crc) != 3) {
        Serial.println("\nusage: ota <self|faucet|enclosure> <size> <crc32>");
        return;
    }

    OtaTarget t = OTA_TGT_NONE;
    if (!strcmp(who, "self"))           t = OTA_TGT_SELF;
    else if (!strcmp(who, "faucet"))    t = OTA_TGT_FAUCET;
    else if (!strcmp(who, "enclosure")) t = OTA_TGT_ENCLOSURE;
    else { Serial.println("\nusage: ota <self|faucet|enclosure> <size> <crc32>"); return; }

    if (target != OTA_TGT_NONE) { Serial.println("\nOTA:FAIL a session is already open"); return; }
    if (size == 0) { Serial.println("\nOTA:FAIL size is zero"); return; }

    target = t;
    imgSize = size;
    imgCrc = crc;
    chunk = (t == OTA_TGT_ENCLOSURE) ? OTA_CHUNK_J9 : OTA_CHUNK_J3;
    lastReported = 0;
    openedAtMs = millis();
    bufFull = false;
    bufLen = 0;

    if (t == OTA_TGT_SELF) {
        if (!selfRx.begin(imgSize, imgCrc)) {
            Serial.printf("\nOTA:FAIL state=%u err=%u\n", selfRx.state, selfRx.err);
            target = OTA_TGT_NONE;
            return;
        }
        Serial.printf("\nOTA:BEGIN self size=%lu crc=%lu chunk=%u\n",
                      (unsigned long)imgSize, (unsigned long)imgCrc, chunk);
        askHost(0);
        return;
    }

    OtaBeginPayload begin{imgSize, imgCrc, chunk};
    volunteer(t, MSG_OTA_BEGIN, &begin, sizeof(begin));
    Serial.printf("\nOTA:BEGIN %s size=%lu crc=%lu chunk=%u\n",
                  targetName(t), (unsigned long)imgSize, (unsigned long)imgCrc, chunk);
}
