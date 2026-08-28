#pragma once

#include <stdint.h>

#include "proto_msg.h"

// ════════════════════════════════════════════════════════════
//  A phone's end of an image, on whichever board holds the radio
// ════════════════════════════════════════════════════════════
//
// Two boards hold one: the appliance's faucet display and the prototype's
// rotary display. Each runs its own GATT server, and each answers the same
// four frames over it — so the session between the phone and the machine is
// here, once, and what differs stays with the server that owns it.
//
//     [type:1][len:2 LE][payload]
//
// 0x01..0x04 are the text and image-upload vocabulary the rotary display
// already spoke. Firmware starts at 0x10 so nothing here reads as one of those.
//
// THE BOARD HOLDING THE RADIO STORES NO IMAGE. The pull that runs from a
// receiver to the relay runs one link further out to the phone: the relay asks
// for an offset and a length, this asks the phone for as much of that as one
// BLE frame carries, and forwards each piece as it lands. An image for this
// board itself is the one case with no relay in it — the bytes go from the
// phone into a local OtaReceiver.

constexpr uint8_t BLE_FRAME_OTA_BEGIN = 0x10;  // phone → board: BleOtaBegin
constexpr uint8_t BLE_FRAME_OTA_NEED  = 0x11;  // board → phone: BleOtaNeed
constexpr uint8_t BLE_FRAME_OTA_DATA  = 0x12;  // phone → board: offset, then bytes
constexpr uint8_t BLE_FRAME_OTA_END   = 0x13;  // board → phone: OtaStatePayload
constexpr uint8_t BLE_FRAME_IDENTITY  = 0x14;  // board → phone: model, unit, name, version
constexpr uint8_t BLE_FRAME_VERSIONS  = 0x15;  // board → phone: VersionsPayload

struct __attribute__((packed)) BleOtaBegin {
  uint8_t  target;   // OTA_TGT_*
  uint8_t  kind;     // OTA_KIND_*
  uint32_t size;
  uint32_t crc32;
};

struct __attribute__((packed)) BleOtaNeed {
  uint32_t offset;
  uint16_t len;
};

// The most image bytes one BLE_FRAME_OTA_DATA carries, at the largest MTU worth
// asking for: 517 leaves 514 for the payload, less the 3-byte header and the
// 4-byte offset. What is actually asked for is bounded by the MTU the phone
// agreed to — a write longer than that is one the phone cannot make.
constexpr uint16_t BLE_OTA_ASK = 480;
constexpr uint16_t BLE_OTA_FRAME_OVERHEAD = 3 + 4;   // header, then the offset

// What the owning board supplies: its notify, its link to the main board, and
// what it does to its own screen while its own flash is being written.
struct BleOtaSeams {
  bool (*notify)(uint8_t type, const void *data, uint16_t len);
  bool (*sendSrc)(uint8_t type, const void *data, uint16_t len);
  void (*onLocalProgress)(bool active, uint8_t percent);
  // OTA_TGT_* this board is, so an image addressed to it is written here.
  uint8_t self;
};

void bleOtaBegin(const BleOtaSeams &seams);
void bleOtaService();

// The MTU the phone agreed to, from the server's onMTUChange.
void bleOtaSetMtu(uint16_t mtu);

// Frames off the radio. `handleFrame` returns true when it took the type.
bool bleOtaHandleFrame(uint8_t type, const uint8_t *payload, uint16_t plen);

// The relay's half, off the link to the main board.
void bleOtaOnSrcNeed(uint32_t offset, uint16_t len);
void bleOtaOnSrcEnd(const OtaStatePayload &state);

// A phone went away mid-session.
void bleOtaDisconnected();

uint8_t bleOtaTarget();
uint16_t bleOtaOwed();
uint32_t bleOtaDropped();
