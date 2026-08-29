#pragma once

#include <stdint.h>
#include "proto_msg.h"

struct BaseLinkStatus {
  bool connected;
  bool synchronized;
  bool mainBoardPersisted;
  bool mainBoardPersistError;
  bool durabilityPending;
  uint8_t mainBoardFlavor;
  uint8_t pending;
  uint32_t framesRx;
  uint32_t framesTx;
  uint32_t retries;
  uint32_t queueDrops;
  uint32_t staleResponses;
  uint32_t authoritativeReconciliations;
  uint32_t lastAckMs;
  uint32_t maxAckMs;
  uint32_t maxServiceUs;
  uint8_t primePending;
  uint32_t primeQueueDrops;
  uint32_t connectionGeneration;
};

typedef void (*BaseFlavorHandler)(uint8_t flavor);
typedef void (*BasePrimeHandler)(const PrimeSessionStatePayload &state,
                                 uint32_t connectionGeneration);

void baseLinkBegin(uint8_t cachedFlavor, BaseFlavorHandler flavorHandler,
                   BasePrimeHandler primeHandler);
void baseLinkService();

// Which logo each channel wears, as the main board now holds it. Defined in
// main.cpp, where the artwork and the image object live.
void faucetApplyFlavorArt(const uint8_t art[2]);

// The pair as this board last heard it, and a request to change one of them.
// The main board owns the answer; this only asks.
void faucetReadFlavorArt(uint8_t out[2]);
void faucetSetFlavorArt(uint8_t channel, uint8_t art);

// A picture landed here whole; ask for it to be carried the last hop.
void faucetRequestRelay(uint8_t slot);

// The identity of the enclosure's copy of a slot, as that board's store keeps
// it — so the main board can hold the two stores against each other. Zero where
// the slot is empty. Cached; faucetForgetEnclosureCrc() drops it.
uint32_t faucetEnclosureCrc(uint8_t slot);
void     faucetForgetEnclosureCrc();

// A picture was removed here; remove it from the rest of the machine too.
void faucetRequestErase(uint8_t slot);

// A phone asked for a picture and got it.
void faucetSayRead(uint8_t slot, uint32_t bytes);

// A phone asked for one, and with how much room per frame.
void faucetSayReadAsked(uint8_t slot, uint16_t mtu);

// Whether the appliance considers anyone present. Defined in main.cpp, where
// the backlight lives.
void faucetApplyIdle(bool asleep);

// What the glass shows while an image is arriving. Defined in main.cpp, where
// the display lives. Flash writes stall this board for whole seconds at a
// time, so the panel says what is happening rather than appearing to hang.
void faucetApplyOta(bool active, uint8_t percent);

// What the glass shows while a picture is arriving, and the rebind a written
// or erased slot forces: writing the store remaps the partition every logo
// descriptor points into. Both defined in main.cpp, where the display lives.
void faucetApplyImage(bool active, uint8_t percent);
void faucetRebindLogos();

// A press this display did not otherwise report.
void baseLinkTouched();

// Non-blocking touch-path call. The absolute selection enters a fixed queue;
// TinyProto and any Preferences write happen later from baseLinkService().
void baseLinkSelect(uint8_t flavor, bool audible);

// Fixed-memory, non-blocking prime-session controls. The enclosure owns
// session activation; the faucet may cancel it or own one physical hold.
void baseLinkPrimeCancel(uint8_t channel, uint32_t sessionToken);
void baseLinkPrimeHoldStart(uint8_t channel, uint32_t sessionToken, uint32_t holdToken);
void baseLinkPrimeHoldTick(uint8_t channel, uint32_t sessionToken, uint32_t holdToken);
void baseLinkPrimeHoldStop(uint8_t channel, uint32_t sessionToken, uint32_t holdToken);
void baseLinkPrimeDiscard();

// Put one frame on J3 for the OTA path — the source half, where this board is
// upstream of the relay rather than a target of it. False when the link is busy
// or down, which the pull answers by re-asking.
bool baseLinkSendOtaSrc(uint8_t type, const void *data, uint16_t len);

// One line to the main board's console, which is the only console this board
// has once it is in a machine.
void baseLinkSay(const char *text);

// The same, held and repeated on every J3 connection. What a board with no
// console wants said at boot is exactly what the link is too young to carry.
void baseLinkSayOnConnect(const char *text);

void baseLinkReadStatus(BaseLinkStatus &status);
