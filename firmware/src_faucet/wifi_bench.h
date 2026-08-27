#pragma once

#include <stdint.h>
#include "proto_msg.h"

// ════════════════════════════════════════════════════════════
//  The radio bench — this board is the sender
// ════════════════════════════════════════════════════════════
//
// The faucet is where a user's image lands: it carries the BLE radio the phone
// talks to. So it is also the board that would forward one, and the question
// this answers is how fast it can, over its own WiFi radio, to the enclosure
// display sinking on WIFI_BENCH_SSID.
//
// The run happens in its own task. The touch path and LVGL keep their loop,
// and J3 keeps being serviced, so a bench run that stalls costs a timeout
// rather than the glass.

// Start a run. False if one is already in flight.
bool wifiBenchPush(uint32_t bytes, uint8_t channel, uint8_t flags);

// True once between the end of a run and the collection of its result.
bool wifiBenchResultReady();

// Take the finished run's result. Clears the ready flag.
void wifiBenchTakeResult(WifiPushResultPayload &out);

// Drop the radio after a run. Called once the result has gone out on J3.
void wifiBenchRelease();
