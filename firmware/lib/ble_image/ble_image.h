#pragma once

#include <stdint.h>

#include "proto_msg.h"

// ════════════════════════════════════════════════════════════
//  A picture arriving from the phone
// ════════════════════════════════════════════════════════════
//
//     [type:1][len:2 LE][payload]
//
// on the same GATT server the firmware path uses, at 0x16 and up so nothing
// here reads as one of its frames.
//
// THIS PUSHES; THE FIRMWARE PATH PULLS. A pull costs a round trip per frame and
// the connection interval is then the transfer rate — which is what makes the
// existing path slow, not the radio. A picture is not firmware: it goes into a
// data partition rather than the slot the board is about to boot from, and a
// wrong byte costs a wrong pixel rather than a brick. So the phone streams
// without waiting and the board answers only to say where it has got to.
//
// EVERY FRAME CARRIES ITS OWN OFFSET, WHICH IS THE WHOLE RECOVERY STORY. The
// board takes a frame only at the offset it is expecting; anything else it
// ignores and answers with the offset it actually reached, and the phone winds
// back to there. So a frame dropped because the board was busy costs the
// distance between them and nothing else — no sequence numbers, no windows, no
// per-frame acknowledgement.

constexpr uint8_t BLE_FRAME_IMG_QUERY = 0x16;  // phone → board: no payload
constexpr uint8_t BLE_FRAME_IMG_STATE = 0x17;  // board → phone: BleImgState
constexpr uint8_t BLE_FRAME_IMG_BEGIN = 0x18;  // phone → board: BleImgBegin
constexpr uint8_t BLE_FRAME_IMG_DATA  = 0x19;  // phone → board: offset, then bytes
constexpr uint8_t BLE_FRAME_IMG_ACK   = 0x1A;  // board → phone: BleImgAck
constexpr uint8_t BLE_FRAME_IMG_END   = 0x1B;  // phone → board: no payload
constexpr uint8_t BLE_FRAME_IMG_ERASE = 0x1C;  // phone → board: BleImgSlot

// Which face each channel wears. The phone is choosing among the same eight
// the enclosure's own picker offers, so it asks for and sets the one thing the
// main board owns rather than keeping an idea of its own.
constexpr uint8_t BLE_FRAME_ART_QUERY = 0x1D;  // phone → board: no payload
constexpr uint8_t BLE_FRAME_ART_STATE = 0x1E;  // board → phone: BleArtState
constexpr uint8_t BLE_FRAME_ART_SET   = 0x1F;  // phone → board: BleArtSet

struct __attribute__((packed)) BleArtState {
  uint8_t art[2];      // art index each channel wears, low channel first
  uint8_t factory;     // how many of them are the ones that ship
  uint8_t custom;      // and how many are the owner's
};

struct __attribute__((packed)) BleArtSet {
  uint8_t channel;
  uint8_t art;
};

struct __attribute__((packed)) BleImgState {
  uint8_t  slots;        // custom slots this machine has
  uint8_t  held;         // how many hold a picture
  uint8_t  occupancy;    // bit per slot, low slot first
  uint8_t  renditions;   // IMAGE_BUNDLE_COUNT this build expects
  uint32_t bundleBytes;  // what one picture is, whole
  uint8_t  artFirst;     // art index the low custom slot answers to
};

struct __attribute__((packed)) BleImgBegin {
  uint8_t  slot;
  uint32_t bytes;
  uint32_t crc32;
};

struct __attribute__((packed)) BleImgSlot {
  uint8_t slot;
};

// `have` is the only thing the phone steers on: send from there. A running
// transfer answers with it every BLE_IMG_ACK_EVERY bytes and whenever a frame
// arrives out of step, so a rewind needs no separate request.
struct __attribute__((packed)) BleImgAck {
  uint8_t  slot;
  uint8_t  state;   // BLE_IMG_*
  uint8_t  err;     // BLE_IMG_ERR_*
  uint32_t have;    // bytes safely written; the offset to send from
};

constexpr uint8_t BLE_IMG_IDLE    = 0;
constexpr uint8_t BLE_IMG_TAKING  = 1;
constexpr uint8_t BLE_IMG_DONE    = 2;
constexpr uint8_t BLE_IMG_FAILED  = 3;

constexpr uint8_t BLE_IMG_ERR_NONE  = 0;
constexpr uint8_t BLE_IMG_ERR_SLOT  = 1;  // no such custom slot
constexpr uint8_t BLE_IMG_ERR_SIZE  = 2;  // not what one picture is on this build
constexpr uint8_t BLE_IMG_ERR_WRITE = 3;
constexpr uint8_t BLE_IMG_ERR_CRC   = 4;  // arrived whole and is not what was promised
constexpr uint8_t BLE_IMG_ERR_BUSY  = 5;

// How often a running transfer volunteers where it has got to. Often enough
// that a phone which stopped being listened to finds out quickly; rarely enough
// that the notifications do not themselves become the traffic.
constexpr uint32_t BLE_IMG_ACK_EVERY = 32768;

// What the owning board supplies.
struct BleImageSeams {
  void (*notify)(uint8_t type, const void *data, uint16_t len);
  // Ask the main board to give a channel a different face, and read back what
  // it currently holds. The main board owns this, not either display.
  void (*setArt)(uint8_t channel, uint8_t art);
  void (*readArt)(uint8_t out[2]);
  // Told at the start and end of a transfer, and every ack, so the glass can
  // say what is happening while its own flash is being written.
  void (*onProgress)(bool active, uint8_t percent);
  // A slot changed: rebind whatever points into the store, because writing it
  // remapped the partition.
  void (*onStoreMoved)();
};

void bleImageBegin(const BleImageSeams &seams);

// True when this type was one of ours.
bool bleImageHandleFrame(uint8_t type, const uint8_t *payload, uint16_t plen);

// A phone that walked away mid-transfer leaves a slot erased, not half-written.
void bleImageDisconnected();

bool bleImageBusy();

// Publish the pair whenever the main board revises it, so a phone watching the
// machine sees a change made on the glass as fast as one it made itself.
void bleImagePublishArt();
