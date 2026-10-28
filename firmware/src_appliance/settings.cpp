#include <Arduino.h>
#include <Preferences.h>
#include <limits.h>
#include <string.h>

#include "settings.h"
#include "settings_core.h"
#include "faucet_link.h"
#include "flavor.h"
#include "identity.h"
#include "link.h"
#include "machine.h"
#include "sound.h"

namespace {
Preferences prefs;
stamped_settings::Authority authority;
bool started = false;
bool storeOpen = false;
bool identityPending = false;
uint8_t pending = 0;
uint8_t nextPublication = 0;
uint32_t persistDueMs = 0;
constexpr uint32_t kPersistDelayMs = 500;
constexpr uint32_t kPersistRetryMs = 5000;

void apply() {
    const auto &v = authority.image().values;
    flavorApplySettings(v[4].bytes[0], v[0].bytes[0], v[1].bytes[0],
                         v[5].bytes[0], v[6].bytes[0]);
    sound_policy::Settings s;
    s.volume = v[2].bytes[0]; s.quietOn = v[2].bytes[1] != 0;
    s.quietStart = v[2].bytes[2]; s.quietEnd = v[2].bytes[3];
    s.quietVolume = v[2].bytes[4];
    soundApplySettings(s);
    identityApplySettings(v[3].bytes, v[3].length);
}

void accepted(uint8_t mask) {
    apply();
    pending |= mask;
    persistDueMs = millis() + kPersistDelayMs;
    // Legacy telemetry keeps its layout; stamped STATE is the write/readback
    // authority. The direct identity frame also updates the radio's advert.
    if (mask & (1 << 3)) {
        identityPending = true;
        IdentityPayload id;
        machineIdentity(id);
        linkRelay(MSG_RESP_IDENTITY, &id, sizeof(id));
    }
}

bool soundWrite(const sound_policy::Settings &s) {
    const uint8_t value[6] = {s.volume, s.quietOn ? uint8_t(1) : uint8_t(0),
                              s.quietStart, s.quietEnd, s.quietVolume, 0};
    return settingsWrite(SETTING_SOUND, SETTING_GLOBAL, value, sizeof(value));
}

bool persist(const stamped_settings::Image &image, void *) {
    return storeOpen && prefs.putBytes("state", &image, sizeof(image)) == sizeof(image);
}

bool persistEpoch(uint32_t epoch, void *) {
    return prefs.putUInt("epoch", epoch) == sizeof(epoch);
}

stamped_settings::Image legacy() {
    auto image = stamped_settings::defaults();
    image.values[0].bytes[0] = flavorRatio(0);
    image.values[1].bytes[0] = flavorRatio(1);
    image.values[4].bytes[0] = flavorSelected();
    image.values[5].bytes[0] = flavorArt(0);
    image.values[6].bytes[0] = flavorArt(1);
    auto &s = image.values[2];
    s.bytes[0] = soundVolume(); s.bytes[1] = soundQuietOn() ? 1 : 0;
    s.bytes[2] = soundQuietStart(); s.bytes[3] = soundQuietEnd(); s.bytes[4] = soundQuietVolume();
    IdentityPayload id;
    machineIdentity(id);
    auto &name = image.values[3];
    name.length = strnlen(id.name, MACHINE_NAME_MAX);
    memcpy(name.bytes, id.name, name.length);
    // A legacy name cut through a UTF-8 character is clipped at its last
    // complete character. New stamped requests reject malformed UTF-8.
    while (name.length && !stamped_settings::validValue(SETTING_NAME, name.bytes, name.length)) --name.length;
    return image;
}
}  // namespace

void settingsBegin() {
    auto image = legacy();
    uint32_t bootEpoch = 0;
    storeOpen = prefs.begin("hsmsettings", false);
    if (storeOpen) {
        const bool hasState = prefs.isKey("state");
        const bool hasEpoch = prefs.isKey("epoch");
        bool valid = !hasState;
        if (hasState && prefs.getBytesLength("state") == sizeof(image)) {
            valid = prefs.getBytes("state", &image, sizeof(image)) == sizeof(image)
                 && stamped_settings::validImage(image);
        }
        // A state without its monotonic epoch is a damaged store, not a new
        // machine. Never restart its sequence at one and reuse old stamps.
        if (valid && (!hasState || hasEpoch) && (!hasEpoch || prefs.getType("epoch") == PT_U32)) {
            const uint32_t previous = prefs.getUInt("epoch", 0);
            if (!hasState || image.epoch <= previous)
                bootEpoch = stamped_settings::reserveBootEpoch(previous, persistEpoch, nullptr);
        }
    }
    authority.begin(image, bootEpoch);
    started = true;
    soundSetSettingsWriter(soundWrite);
    apply();
    pending = (1 << stamped_settings::kFields) - 1;
    identityPending = true;
    persistDueMs = millis() + kPersistDelayMs;
    Serial.printf("\n[settings] authority %s, boot epoch %lu\n",
                  authority.ready() ? "ready" : "storage unavailable; writes refused",
                  (unsigned long)bootEpoch);
}

bool settingsStarted() { return started; }
bool settingsReady() { return authority.ready(); }
bool settingsDirty() { return authority.dirty(); }
bool settingsStorageFailed() { return authority.storageFailed(); }

bool settingsWrite(uint8_t kind, uint8_t channel, const uint8_t *value, uint8_t length) {
    const stamped_settings::Mutation change{kind, channel, length, value};
    if (authority.set(&change, 1) != SETTING_OK) return false;
    accepted(1 << stamped_settings::index(kind, channel));
    return true;
}

bool settingsWritePair(uint8_t kind, uint8_t first, uint8_t second) {
    const stamped_settings::Mutation changes[2] = {{kind, 0, 1, &first}, {kind, 1, 1, &second}};
    if (authority.set(changes, 2) != SETTING_OK) return false;
    accepted((1 << stamped_settings::index(kind, 0)) | (1 << stamped_settings::index(kind, 1)));
    return true;
}

uint16_t settingsAnswer(uint8_t type, const uint8_t *body, uint16_t length,
                        uint8_t *answer, uint16_t capacity) {
    const uint8_t kind = length ? body[0] : 0xFF;
    const uint8_t channel = length > 1 ? body[1] : 0xFF;
    uint8_t result = SETTING_INVALID;
    if (type == MSG_SETTING_GET && length == 2) result = SETTING_OK;
    if (type == MSG_SETTING_SET_IF && length >= SETTING_SET_HEADER_SIZE &&
        body[10] <= SETTING_VALUE_MAX && length == SETTING_SET_HEADER_SIZE + body[10]) {
        result = authority.compareSet(kind, channel, stamped_settings::readLE64(body + 2),
                                      body + SETTING_SET_HEADER_SIZE, body[10]);
        if (result == SETTING_OK) accepted(1 << stamped_settings::index(kind, channel));
    }
    return stamped_settings::encode(authority.snapshot(kind, channel, result), answer, capacity);
}

void settingsService() {
    if (!started) return;
    if (authority.dirty() && machineState() == ST_IDLE && !soundBusy() &&
        int32_t(millis() - persistDueMs) >= 0) {
        const bool wasFailed = authority.storageFailed();
        const bool ok = authority.flush(persist, nullptr);
        persistDueMs = millis() + (ok ? kPersistDelayMs : kPersistRetryMs);
        flavorSettingsDurabilityChanged();
        if (wasFailed != authority.storageFailed()) pending = (1 << stamped_settings::kFields) - 1;
        Serial.printf("\n[settings] %s\n", ok ? "persisted" : "NVS write failed; live settings retained");
    }
    if (identityPending) {
        IdentityPayload id;
        machineIdentity(id);
        if (!faucetLinkSendOta(MSG_RESP_IDENTITY, &id, sizeof(id))) return;
        identityPending = false;
        return;
    }
    // A full TinyProto window keeps the field pending. Coalesce repeated live
    // changes to the newest absolute snapshot, and retry until J3 takes it.
    for (uint8_t offset = 0; offset < stamped_settings::kFields; ++offset) {
        const uint8_t i = (nextPublication + offset) % stamped_settings::kFields;
        if (!(pending & (1 << i))) continue;
        uint8_t kind, channel;
        stamped_settings::key(i, kind, channel);
        uint8_t frame[SETTING_STATE_HEADER_SIZE + SETTING_VALUE_MAX];
        const uint16_t len = stamped_settings::encode(authority.snapshot(kind, channel), frame, sizeof(frame));
        if (!faucetLinkTryPublish(MSG_SETTING_STATE, frame, len)) return;
        pending &= ~(1 << i);
        nextPublication = (i + 1) % stamped_settings::kFields;
        return;
    }
}
