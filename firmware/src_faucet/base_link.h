#pragma once

#include <stdint.h>

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
  uint32_t lastAckMs;
  uint32_t maxAckMs;
  uint32_t maxServiceUs;
};

typedef void (*BaseFlavorHandler)(uint8_t flavor);

void baseLinkBegin(uint8_t cachedFlavor, BaseFlavorHandler handler);
void baseLinkService();

// Non-blocking touch-path call. The absolute selection enters a fixed queue;
// TinyProto and any Preferences write happen later from baseLinkService().
void baseLinkSelect(uint8_t flavor, bool audible);

void baseLinkReadStatus(BaseLinkStatus &status);
