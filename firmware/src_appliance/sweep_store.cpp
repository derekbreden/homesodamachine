#include <Preferences.h>

#include "sweep_store.h"

namespace {
const char *const kNamespace = "sweep";
const char *const kOwedKey   = "owed";
const char *const kMovingKey = "moving";

// Read-only: a board that has never kept either fact has no such namespace, and that reads
// as neither.
bool load(const char *key) {
    Preferences prefs;
    if (!prefs.begin(kNamespace, true)) return false;
    const bool kept = prefs.getBool(key, false);
    prefs.end();
    return kept;
}

void save(const char *key, bool value) {
    Preferences prefs;
    if (!prefs.begin(kNamespace, false)) return;
    prefs.putBool(key, value);
    prefs.end();
}
}  // namespace

bool sweepOwedLoad() { return load(kOwedKey); }
void sweepOwedSave(bool owed) { save(kOwedKey, owed); }
bool sweepMovingLoad() { return load(kMovingKey); }
void sweepMovingSave(bool moving) { save(kMovingKey, moving); }
