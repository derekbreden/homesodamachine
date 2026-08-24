#include <Arduino.h>

#include "idle.h"
#include "machine.h"
#include "proto_msg.h"

namespace {

// Quiet stretch before both glasses sleep. An open prime session widens it:
// the pad is offering something a hand may still be walking toward, and the
// walk is longer than the glance the short window is sized for.
constexpr uint32_t kQuietMs      = 60000;
constexpr uint32_t kQuietPrimeMs = 180000;

uint32_t lastTouchMs = 0;
bool asleep = false;

uint32_t window() {
    MachinePrimeSessionState prime;
    machineReadPrimeSessionState(prime);
    return prime.phase == PRIME_SESSION_OFF ? kQuietMs : kQuietPrimeMs;
}

}  // namespace

void idleBegin() {
    lastTouchMs = millis();
    asleep = false;
}

void idleTouched() {
    lastTouchMs = millis();
    asleep = false;
}

bool idleService() {
    const bool quiet = static_cast<uint32_t>(millis() - lastTouchMs) >= window();
    if (quiet == asleep) return false;
    asleep = quiet;
    return true;
}

bool     idleAsleep()   { return asleep; }
uint32_t idleWindowMs() { return window(); }
uint32_t idleQuietMs()  { return static_cast<uint32_t>(millis() - lastTouchMs); }
