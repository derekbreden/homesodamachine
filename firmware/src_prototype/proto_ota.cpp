#include <Arduino.h>
#include <Preferences.h>
#include <esp_mac.h>

#include "proto_ota.h"
#include "ota_receiver.h"

static ProtoOtaSend sendToS3 = nullptr;

// ── The session ───────────────────────────────────────────────────────────
static OtaReceiver rx;
static uint32_t imgSize = 0;
static uint32_t askedAtMs = 0;
static uint32_t openedAtMs = 0;
static uint32_t reported = 0;

// The most bytes asked for at once. The rotary chops this into whatever its own
// BLE frames carry, and each piece arrives here naming where it starts.
static const uint16_t SPAN = 1024;
static uint32_t spanOffset = 0;
static uint16_t spanOwed = 0;
static uint16_t spanGot = 0;
static uint8_t  buf[SPAN];

static void ask(uint32_t offset) {
    const uint32_t remain = imgSize - offset;
    spanOffset = offset;
    spanOwed = (remain < SPAN) ? (uint16_t)remain : SPAN;
    spanGot = 0;
    askedAtMs = millis();
    OtaSrcNeedPayload need{offset, spanOwed};
    if (sendToS3) sendToS3(MSG_OTA_SRC_NEED, &need, sizeof(need));
}

static void finish(uint8_t state, uint8_t err) {
    OtaStatePayload st{state, err, rx.received};
    if (sendToS3) sendToS3(MSG_OTA_SRC_END, &st, sizeof(st));
    Serial.printf("OTA:%s state=%u err=%u recv=%lu exp=%lu run=%08lX want=%08lX\n",
                  state == OTA_STATE_DONE ? "DONE" : "FAIL", state, err,
                  (unsigned long)rx.received, (unsigned long)rx.expected,
                  (unsigned long)rx.runCrc, (unsigned long)rx.wantCrc);
    if (state != OTA_STATE_DONE) rx.abort();
    imgSize = 0;
    spanOwed = 0;
}

void protoOtaBegin(ProtoOtaSend send) { sendToS3 = send; }

void protoOtaOnSrcBegin(const uint8_t *payload, uint16_t plen) {
    if (plen < sizeof(OtaSrcBeginPayload)) return;
    OtaSrcBeginPayload b;
    memcpy(&b, payload, sizeof(b));

    if (imgSize) {
        // The source repeating BEGIN into the session it opened is a retry of a
        // frame this board answered.
        if (b.size == imgSize) return;
        finish(OTA_STATE_FAILED, OTA_ERR_NONE);
        return;
    }
    if (b.size == 0 || b.target != OTA_TGT_SELF) {
        OtaStatePayload no{OTA_STATE_FAILED, OTA_ERR_NONE, 0};
        if (sendToS3) sendToS3(MSG_OTA_SRC_END, &no, sizeof(no));
        return;
    }

    Serial.printf("OTA:BEGIN size=%lu crc=%08lX kind=%u\n",
                  (unsigned long)b.size, (unsigned long)b.crc32, b.kind);
    if (!rx.begin(b.size, b.crc32, b.kind)) {
        imgSize = b.size;      // so finish() reports against the right session
        finish(rx.state, rx.err);
        return;
    }
    imgSize = b.size;
    reported = 0;
    openedAtMs = millis();
    ask(0);
}

void protoOtaOnSrcData(const uint8_t *payload, uint16_t plen) {
    if (!imgSize || plen < 4 || spanOwed == 0) return;
    uint32_t offset;
    memcpy(&offset, payload, 4);
    const uint16_t len = (uint16_t)(plen - 4);
    if (offset != spanOffset + spanGot || len > spanOwed) return;

    memcpy(buf + spanGot, payload + 4, len);
    spanGot += len;
    spanOwed -= len;
    if (spanOwed) return;

    if (!rx.write(spanOffset, buf, spanGot)) { finish(rx.state, rx.err); return; }
    if (rx.nextOffset() < imgSize) {
        if (rx.received >= reported + 65536) {
            reported = rx.received;
            Serial.printf("OTA:AT %lu/%lu\n",
                          (unsigned long)rx.received, (unsigned long)imgSize);
        }
        ask(rx.nextOffset());
        return;
    }
    // Last byte is in. Nothing has moved yet — finish() verifies the whole image
    // and only then points the bootloader at it.
    const bool ok = rx.finish();
    finish(rx.state, rx.err);
    if (ok) { delay(200); ESP.restart(); }
}

void protoOtaService() {
    if (!imgSize) return;
    // A span whose request went missing is a deadlock: this board waits for
    // bytes and the source waits to be asked. Re-asking is only safe before any
    // of the span has arrived.
    if (spanOwed && spanGot == 0 && millis() - askedAtMs >= 400) ask(spanOffset);
    if (millis() - openedAtMs > 600000UL) finish(OTA_STATE_FAILED, OTA_ERR_NONE);
}

// ── Which machine this is ─────────────────────────────────────────────────
static Preferences prefs;
static char machineName[MACHINE_NAME_MAX + 1] = {0};
static uint8_t unitId[3] = {0};

void protoIdentityBegin() {
    uint8_t mac[6] = {0};
    esp_read_mac(mac, ESP_MAC_WIFI_STA);
    unitId[0] = mac[3];
    unitId[1] = mac[4];
    unitId[2] = mac[5];
    if (prefs.begin("machine", true)) {
        prefs.getString("name", machineName, sizeof(machineName));
        prefs.end();
    }
}

void protoMachineIdentity(IdentityPayload &out) {
    out.model = MACHINE_PROTOTYPE;
    memcpy(out.unit, unitId, sizeof(unitId));
    memset(out.name, 0, sizeof(out.name));
    strncpy(out.name, machineName, MACHINE_NAME_MAX);
}

void protoIdentityConsole(const String &line) {
    String rest = line.substring(8);
    rest.trim();
    if (rest.length()) {
        strncpy(machineName, rest.c_str(), MACHINE_NAME_MAX);
        machineName[MACHINE_NAME_MAX] = 0;
        if (prefs.begin("machine", false)) {
            prefs.putString("name", machineName);
            prefs.end();
        }
    }
    Serial.printf("IDENTITY model=prototype unit=%02X%02X%02X name=%s\n",
                  unitId[0], unitId[1], unitId[2],
                  machineName[0] ? machineName : "(unset)");
}
