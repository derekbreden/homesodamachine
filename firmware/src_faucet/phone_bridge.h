#pragma once

#include <stdint.h>

#include "proto_msg.h"

// ════════════════════════════════════════════════════════════
//  What a phone asks of the machine, carried to the main board
// ════════════════════════════════════════════════════════════
//
// A phone writes BLE_FRAME_MACHINE_REQ — a BridgeHeader, then the request's own
// payload — and this board puts it on J3 as MSG_BRIDGE_REQ under an id of its
// own, so two phones' ids never meet on the wire. The main board's answer comes
// back under that id and goes to the phone that asked, under the phone's id.
// What may be asked is the main board's list (faucet_link.cpp), not this
// board's: anything else comes back BRIDGE_ERR_REFUSED.
//
// State that moved reaches every phone on the air under id 0: what the main
// board volunteers inside MSG_BRIDGE_RESP, and the selection and Prime's
// session, which J3 already brings this board for its own glass.
//
// NOTHING IS REPLAYED. A request the main board does not answer in time is
// answered BRIDGE_ERR_NO_ANSWER, and the phone reads the truth with a query
// rather than asking for the action twice.
//
// The other frame types this board speaks are in ble_ota.h and ble_image.h.
constexpr uint8_t BLE_FRAME_MACHINE_REQ = 0x23;  // phone → board: BridgeHeader, then the request
constexpr uint8_t BLE_FRAME_MACHINE     = 0x24;  // board → phone: BridgeHeader, then the answer
constexpr uint8_t BLE_FRAME_BRIDGE      = 0x25;  // board → phone: BRIDGE_VERSION, sent with IDENTITY

// A phone's frame, from the link (and that link's generation) it arrived on.
void phoneBridgeRequest(uint16_t link, uint32_t gen, const uint8_t *frame, uint16_t len);

// MSG_BRIDGE_RESP off J3.
void phoneBridgeOnAnswer(const uint8_t *payload, uint16_t len);

// State this board hears on J3 for its own glass, passed on when it moves.
void phoneBridgeOnState(uint8_t type, const void *data, uint16_t len);

// The main board answered MSG_BRIDGE_REQ with MSG_ERR_UNSUPPORTED: its firmware
// predates the bridge, and nothing asked of it will be answered.
void phoneBridgeOnNoBridge();

void phoneBridgeService();
