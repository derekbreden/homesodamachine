#pragma once

#include <stdint.h>

#include "proto_msg.h"

// ════════════════════════════════════════════════════════════
//  The phone's end of the machine
// ════════════════════════════════════════════════════════════
//
// A GATT server on the Nordic UART Service, at the end of the gooseneck, above
// the counter, in open air. The iOS app writes framed messages to RX and takes
// them back as notifications on TX:
//
//     [type:1][len:2 LE][payload]
//
// THIS BOARD STORES NO IMAGE. It has 16 MB of flash and holds one BLE frame of
// whatever is passing through. The pull that runs from the enclosure display to
// the main board runs one link further out to here and then to the phone: the
// receiver asks the relay for an offset, the relay asks this board, this board
// asks the phone, and the bytes come back the same way. What crosses J3 is what
// arrived over BLE, unbuffered.
//
// An image for this display is the one case with no relay in it — the bytes go
// from the phone into a local OtaReceiver.
//
// WHAT THIS BOARD ADVERTISES IS THE MACHINE, NOT THE BOARD. The main board is
// the only one that knows which machine it is in and which unit; this asks at
// boot (MSG_IDENTITY_QUERY) and puts the answer in the local name and the
// manufacturer data, so a phone standing between two machines can tell them
// apart before it connects to either.

void bleLinkBegin();
void bleLinkService();

// The identity the main board answered with, which is what gets advertised.
void bleLinkOnIdentity(const IdentityPayload &id);

// What every board on this machine is running, as the main board assembled it.
void bleLinkOnVersions(const VersionsPayload &all);

// The relay asking for bytes, and telling this board how a session ended.
void bleLinkOnSrcNeed(uint32_t offset, uint16_t len);
void bleLinkOnSrcEnd(const OtaStatePayload &state);

// Stop and restart advertising around a radio-bench run. Both radios are one
// antenna and one PHY: what BLE costs WiFi is exactly the question, so it has
// to be possible to take BLE out of the way and measure without it.
void bleLinkQuiet(bool quiet);

bool bleLinkConnected();
void bleLinkFillStatus(BleStatusPayload &out);
void bleLinkReport();

// An answer from the main board, as BLE_FRAME_MACHINE: to the one link that
// asked — and only while it is still the same connection — or, to
// BLE_LINK_EVERY, to every phone on the air. False when the link is gone or
// could not carry it.
constexpr uint16_t BLE_LINK_EVERY = 0xFFFF;
bool bleLinkDeliver(uint16_t link, uint32_t gen, uint8_t reqId, uint8_t type,
                    const void *body, uint16_t len);

// Whether that connection is still the one on that link.
bool bleLinkUp(uint16_t link, uint32_t gen);

// A phone's trust ask ended: it hears how, and where it now stands.
void bleLinkTrustEnded(uint16_t link, uint32_t gen, uint8_t outcome);
