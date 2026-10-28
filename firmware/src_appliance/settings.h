#pragma once

#include <stdint.h>

// The main loop is the sole writer. Its dispatch calls compare/apply without
// yielding to another setting request; every source uses the same setters.
void settingsBegin();
void settingsService();
bool settingsStarted();
bool settingsReady();
bool settingsDirty();
bool settingsStorageFailed();

// Console and physical-display mutations are unconditional authoritative writes.
// Each explicitly supplied field advances, even when its value is unchanged.
bool settingsWrite(uint8_t kind, uint8_t channel, const uint8_t *value, uint8_t length);
bool settingsWritePair(uint8_t kind, uint8_t first, uint8_t second);

// GET / SET_IF, on either transport. Always produces a stamped current snapshot
// for a known key, including a rejected request. Returns encoded STATE length.
uint16_t settingsAnswer(uint8_t type, const uint8_t *body, uint16_t length,
                        uint8_t *answer, uint16_t capacity);
