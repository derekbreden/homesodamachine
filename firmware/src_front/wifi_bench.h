#pragma once

#include <stdint.h>
#include "proto_msg.h"

// ════════════════════════════════════════════════════════════
//  The radio bench — this board is the sink
// ════════════════════════════════════════════════════════════
//
// The enclosure display raises a SoftAP and accepts one TCP connection on
// WIFI_BENCH_PORT, counting what arrives and timing first byte to last. The
// faucet is the sender. Nothing here is a product path: it exists so the
// wired links have something measured to be compared against, and it does
// nothing at all until the main board asks over J9.
//
// The accept-and-read loop runs in its own task on core 0, because the panel's
// scan-out and LVGL own core 1 and a socket read that blocks there would stop
// the glass.

// Raise or drop the access point. Idempotent.
void wifiBenchApSet(bool on, uint8_t channel);

// Fill the answer the main board asked for.
void wifiBenchFill(WifiApStatePayload &out);
