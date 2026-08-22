#pragma once

#include <stdint.h>
#include "proto_msg.h"

struct BaseLinkStatus {
  bool connected;
  bool synchronized;
  bool controllerPersisted;
  bool controllerPersistError;
  bool durabilityPending;
  uint8_t controllerFlavor;
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

void baseLinkReadStatus(BaseLinkStatus &status);
