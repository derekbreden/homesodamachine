#include <Arduino.h>
#include <Preferences.h>

#include "flavor.h"
#include "flavor_selection.h"
#include "proto_msg.h"

namespace {

constexpr uint8_t kAbsentFlavor = 0xFF;
constexpr uint32_t kPersistDelayMs = 500;
constexpr uint32_t kPersistRetryMs = 5000;

Preferences prefs;
flavor_selection::Authority authority;
bool storeOpen = false;
uint32_t persistDueMs = 0;
uint32_t revision = 0;

// Which logo each channel wears. Held beside the selection because it is the
// same kind of state — main-board-authoritative, set from a glass, and read by
// every glass — and written under the same deferred, idle-only discipline.
uint8_t art[2] = {0, 1};
bool artDirty = false;
uint32_t artPersistDueMs = 0;

// What each channel pours at, held the same way.
uint8_t ratio[2] = {FLAVOR_RATIO_DEFAULT, FLAVOR_RATIO_DEFAULT};
bool ratioDirty = false;
uint32_t ratioPersistDueMs = 0;

bool due(uint32_t now, uint32_t deadline) {
    return static_cast<int32_t>(now - deadline) >= 0;
}

void changed(flavor_selection::Update update) {
    if (update != flavor_selection::Update::Changed) return;
    persistDueMs = millis() + kPersistDelayMs;
    ++revision;
}

}  // namespace

void flavorBegin() {
    storeOpen = prefs.begin("selection", false);
    if (storeOpen) {
        authority.loadPersisted(prefs.getUChar("flavor", kAbsentFlavor));
        for (uint8_t i = 0; i < 2; i++) {
            const uint8_t v = prefs.getUChar(i ? "art1" : "art0", art[i]);
            if (v < FLAVOR_ART_COUNT) art[i] = v;
            const uint8_t r = prefs.getUChar(i ? "ratio1" : "ratio0", ratio[i]);
            if (r >= FLAVOR_RATIO_MIN && r <= FLAVOR_RATIO_MAX) ratio[i] = r;
        }
    } else {
        // Storage failure is not a factory-blank namespace. Establish a
        // deterministic main board default and report the durability fault;
        // otherwise a faucet cache could silently become authority precisely
        // when the main board cannot preserve the adopted value.
        authority.select(0);
        authority.persistenceFinished(false);
    }
    revision = 1;
    persistDueMs = 0;
}

bool flavorService() {
    if (storeOpen && ratioDirty && due(millis(), ratioPersistDueMs)) {
        const bool ok = prefs.putUChar("ratio0", ratio[0]) == sizeof(uint8_t) &&
                        prefs.putUChar("ratio1", ratio[1]) == sizeof(uint8_t);
        ratioDirty = !ok;
        ratioPersistDueMs = millis() + (ok ? kPersistDelayMs : kPersistRetryMs);
        Serial.printf("\n[flavor] %s ratio 1:%u / 1:%u\n",
                      ok ? "persisted" : "NVS write failed for", ratio[0], ratio[1]);
        if (ok) return true;
    }

    if (storeOpen && artDirty && due(millis(), artPersistDueMs)) {
        const bool ok = prefs.putUChar("art0", art[0]) == sizeof(uint8_t) &&
                        prefs.putUChar("art1", art[1]) == sizeof(uint8_t);
        artDirty = !ok;
        artPersistDueMs = millis() + (ok ? kPersistDelayMs : kPersistRetryMs);
        Serial.printf("\n[flavor] %s artwork %u/%u\n",
                      ok ? "persisted" : "NVS write failed for", art[0], art[1]);
        if (ok) return true;
    }

    if (!storeOpen || !authority.needsPersistence()) return false;

    const uint32_t now = millis();
    if (!due(now, persistDueMs)) return false;

    const bool wasError = authority.persistenceError();
    const bool success = prefs.putUChar("flavor", authority.selected()) == sizeof(uint8_t);
    authority.persistenceFinished(success);
    persistDueMs = now + (success ? kPersistDelayMs : kPersistRetryMs);

    if (success) {
        Serial.printf("\n[flavor] persisted flavor %u\n", authority.selected() + 1);
    } else {
        Serial.println("\n[flavor] NVS write failed — selection remains active but not durable");
    }

    const bool statusChanged = success || wasError != authority.persistenceError();
    if (statusChanged) ++revision;
    return statusChanged;
}

bool flavorSynchronize(uint8_t candidate) {
    const flavor_selection::Update update = authority.synchronize(candidate);
    if (update == flavor_selection::Update::Rejected) return false;
    changed(update);
    if (update == flavor_selection::Update::Changed) {
        Serial.printf("\n[flavor] first main board sync adopted faucet flavor %u\n",
                      authority.selected() + 1);
    }
    return true;
}

bool flavorSelect(uint8_t flavor) {
    const flavor_selection::Update update = authority.select(flavor);
    if (update == flavor_selection::Update::Rejected) return false;
    changed(update);
    return true;
}

uint8_t flavorSelected() { return authority.selected(); }
bool flavorEstablished() { return authority.established(); }
bool flavorPersisted() { return storeOpen && authority.persisted(); }
bool flavorPersistenceError() {
    return !storeOpen || authority.persistenceError();
}
uint32_t flavorRevision() { return revision; }

uint8_t flavorArt(uint8_t channel) { return art[channel & 1]; }

bool flavorArtSet(uint8_t a0, uint8_t a1) {
    if (a0 >= FLAVOR_ART_COUNT || a1 >= FLAVOR_ART_COUNT) return false;
    if (art[0] == a0 && art[1] == a1) return true;
    art[0] = a0;
    art[1] = a1;
    artDirty = true;
    artPersistDueMs = millis() + kPersistDelayMs;
    ++revision;
    return true;
}

uint8_t flavorRatio(uint8_t channel) { return ratio[channel & 1]; }

bool flavorRatioSet(uint8_t r0, uint8_t r1) {
    if (r0 < FLAVOR_RATIO_MIN || r0 > FLAVOR_RATIO_MAX ||
        r1 < FLAVOR_RATIO_MIN || r1 > FLAVOR_RATIO_MAX) return false;
    if (ratio[0] == r0 && ratio[1] == r1) return true;
    ratio[0] = r0;
    ratio[1] = r1;
    ratioDirty = true;
    ratioPersistDueMs = millis() + kPersistDelayMs;
    ++revision;
    return true;
}
