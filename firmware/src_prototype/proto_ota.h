#pragma once

#include <stdint.h>
#include <Arduino.h>

#include "proto_msg.h"

// ════════════════════════════════════════════════════════════
//  Taking an image from the rotary display
// ════════════════════════════════════════════════════════════
//
// The prototype's radio is on its rotary display, so this board is downstream
// of the phone rather than upstream of anything: an image arriving here is for
// this board's own spare slot. The rotary updates itself, and the RP2040 takes
// its image through BOOTSEL and a cable — its ROM offers USB and nothing else.
//
// So the relay the appliance's main board runs has no counterpart here. What is
// here is the receiving half and the same pull it answers to:
// MSG_OTA_SRC_BEGIN opens it, MSG_OTA_SRC_NEED asks for the next span,
// MSG_OTA_SRC_DATA carries it, MSG_OTA_SRC_END says how it finished.

typedef bool (*ProtoOtaSend)(uint8_t type, const void *data, uint16_t len);

void protoOtaBegin(ProtoOtaSend send);
void protoOtaService();

// Frames off the link to the rotary display.
void protoOtaOnSrcBegin(const uint8_t *payload, uint16_t plen);
void protoOtaOnSrcData(const uint8_t *payload, uint16_t plen);

// Which machine this is, for whatever the rotary advertises.
void protoIdentityBegin();
void protoMachineIdentity(IdentityPayload &out);
void protoIdentityConsole(const String &line);
