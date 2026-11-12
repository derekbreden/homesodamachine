#include <Preferences.h>

#include "refill_store.h"

namespace {
const char *const kNamespace = "refill";
const char *const kKey       = "owed";
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
