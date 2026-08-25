#pragma once

#include <stdint.h>

// ════════════════════════════════════════════════════════════
//  J9 — the pair to the enclosure display
// ════════════════════════════════════════════════════════════
//
// A finger on the display's glass arrives here as a message. Every frame this
// file understands becomes a call in machine.h, and every answer it sends is
// something the machine announced.

void linkBegin();

// Publish the shared idle state to the enclosure at its next turn.
void linkPublishIdle();
void linkService();       // call every loop
void linkReport();        // one console block: frames, bytes, echo, last rx

// Put a frame on the pair and read the echo back. /RE is tied to GND, so the
// echo returning through U7 to IO34 walks IO32 -> U7 -> the A/B pair and R6's
// termination -> U7 -> IO34 without the far end taking any part.
void linkPing();

// Volunteer an OTA frame to the enclosure. Queued like any announcement and
// flushed inside a turn, because the main board does not interrupt the pair.
void linkQueueOta(uint8_t type, const void *data, uint8_t len);

// Answer an OTA request from inside its own dispatch, spending that turn's one
// reply. Illegal anywhere else.
bool linkReplyOta(uint8_t type, const void *data, uint16_t len);

// Make an externally-powered enclosure display present a fresh USB attach. An application
// that knows MSG_DISPLAY_USB_REATTACH briefly deep-sleeps its USB PHY.
bool linkDisplayUsbReattach();
