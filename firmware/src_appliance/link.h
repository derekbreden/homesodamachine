#pragma once

#include <stdint.h>

// ════════════════════════════════════════════════════════════
//  J9 — the pair to the front-face display
// ════════════════════════════════════════════════════════════
//
// A finger on the display's glass arrives here as a message. Every frame this
// file understands becomes a call in machine.h, and every answer it sends is
// something the machine announced.

void linkBegin();
void linkService();       // call every loop
void linkReport();        // one console block: frames, bytes, echo, last rx

// Put a frame on the pair and read the echo back. /RE is tied to GND, so the
// echo returning through U7 to IO34 walks IO32 -> U7 -> the A/B pair and R6's
// termination -> U7 -> IO34 without the far end taking any part.
void linkPing();

// Make an externally-powered front display present a fresh USB attach. An application
// that knows MSG_DISPLAY_USB_REATTACH briefly deep-sleeps its USB PHY.
bool linkDisplayUsbReattach();
