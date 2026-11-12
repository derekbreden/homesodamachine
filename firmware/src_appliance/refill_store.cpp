#include <Preferences.h>

#include "refill_store.h"

namespace {
const char *const kNamespace = "refill";
const char *const kKey       = "owed";
const char *const kSpentKey  = "spent";
const char *const kFilledKey = "filled";
}  // namespace

bool refillOwedLoad() {
    Preferences prefs;
    // Read-only: a board that has never owed a refill has no such namespace, and that
    // reads as nothing owed.
    if (!prefs.begin(kNamespace, true)) return false;
    const bool owed = prefs.getBool(kKey, false);
    prefs.end();
    return owed;
}

void refillOwedSave(bool owed) {
    Preferences prefs;
    if (!prefs.begin(kNamespace, false)) return;
    prefs.putBool(kKey, owed);
    prefs.end();
}

uint32_t refillSpentLoad() {
    Preferences prefs;
    if (!prefs.begin(kNamespace, true)) return 0;
    const uint32_t spent = prefs.getULong(kSpentKey, 0);
    prefs.end();
    return spent;
}

void refillSpentSave(uint32_t spentMs) {
    Preferences prefs;
    if (!prefs.begin(kNamespace, false)) return;
    prefs.putULong(kSpentKey, spentMs);
    prefs.end();
}

bool refillFilledLoad() {
    Preferences prefs;
    if (!prefs.begin(kNamespace, true)) return false;
    const bool filled = prefs.getBool(kFilledKey, false);
    prefs.end();
    return filled;
}

void refillFilledSave(bool filled) {
    Preferences prefs;
    if (!prefs.begin(kNamespace, false)) return;
    prefs.putBool(kFilledKey, filled);
    prefs.end();
}
