#pragma once

#include <stdint.h>

#include "proto_msg.h"

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

// Raise or drop the radio bench's access point on the enclosure display, which
// is the sink for it. Retried, because this is a main-board-originated frame on
// a pair the main board otherwise only answers on.
bool linkWifiAp(bool on);

// 1 raises it with the panel taken down, 3 leaves the panel running.
// Which of those the radio actually survives is the question `wifi live`
// exists to answer.
bool linkWifiApMode(uint8_t mode);

// What the sink has counted. False if the display did not answer.
bool linkWifiApState(WifiApStatePayload &out);

// Make an externally-powered enclosure display present a fresh USB attach. An application
// that knows MSG_DISPLAY_USB_REATTACH briefly deep-sleeps its USB PHY.
bool linkDisplayUsbReattach();
