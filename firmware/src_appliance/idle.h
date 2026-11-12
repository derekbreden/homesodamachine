#pragma once

#include <stdint.h>

// Presence, as the appliance sees it across both glasses.
//
// A finger on either display is activity for both. The main board is the only
// place that sees both links, so it keeps the one clock and both displays
// render what it says. Neither display runs a timer of its own: a pair left lit
// is a link that stopped talking, and reads as exactly that.
void idleBegin();

// Something worth lighting both glasses for: a finger on either, a phone talking to the
// faucet, an operation someone started, the console's `wake`. It is not a person standing at
// the machine, so nothing that moves water or closes a relay hangs on it.
void idleTouched();

// Advances the clock. Returns true when awake/asleep changed on this call.
bool idleService();

bool     idleAsleep();
uint32_t idleWindowMs();
uint32_t idleQuietMs();
