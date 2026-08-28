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
void wifiBenchApSet(bool on, uint8_t channel, bool keepPanel);

// Fill the answer the main board asked for.
void wifiBenchFill(WifiApStatePayload &out);

// How far the radio got and what memory it had to do it with. This display has
// no console of its own in the appliance, so the account goes out on J9 as
// text. Keep it under 40 bytes: that is what one queued J9 frame carries.
void wifiBenchDiag(char *out, unsigned n);

// What the last arriving picture did. Survives the reboot that taking one ends
// in, because that reboot is where the account of it would otherwise be lost.
void wifiBenchPictureDiag(char *out, unsigned n);

// Taking the panel down before the radio comes up, and putting the board back
// afterwards. The scan-out DMA refills its bounce buffer out of PSRAM and the
// radio's bring-up writes flash, which suspends the cache PSRAM is reached
// through — the same conflict that makes an OTA blank this glass. Defined in
// main.cpp, where the panel lives.
void wifiBenchPanelStop();

// True once the bench is finished with a board whose panel it took down. The
// only way back is the reboot the loop then performs.
bool wifiBenchRebootWanted();
