#pragma once
#include <stdint.h>

namespace front_ui {
enum class Action : uint8_t { SelectFlavor, Dismiss, Task, Settings, Edit, Stop };

// A pending Start and an accepted operation both raise the input shield. Prime
// keeps its exits: navigation first queues the causal cancellation, then selects.
constexpr bool allows(Action action, bool operationLocked, bool primeHeld) {
  return operationLocked ? action == Action::Stop
      : !primeHeld || action == Action::Stop || action == Action::Dismiss || action == Action::SelectFlavor;
}
constexpr bool showDone(bool resting, bool operationLocked) {
  return !resting && !operationLocked;
}
constexpr bool dismissForFaucetChange(bool machinePage, bool changed, bool operationLocked) {
  return changed && !machinePage && !operationLocked;
}
constexpr bool readingFresh(uint32_t receivedAt, uint32_t now, uint32_t timeout) {
  return receivedAt != 0 && uint32_t(now - receivedAt) < timeout;
}

// Slots 0..3 are factory artwork, 4..7 are optional customer uploads. Empty
// upload slots never occupy a tile or a page ahead of the available artwork.
inline uint8_t imageOrder(uint8_t availableUploads, uint8_t (&order)[8]) {
  uint8_t count = 0;
  for (uint8_t slot = 4; slot < 8; ++slot)
    if (availableUploads & (1u << slot)) order[count++] = slot;
  for (uint8_t slot = 0; slot < 4; ++slot) order[count++] = slot;
  return count;
}
constexpr uint8_t imagePages(uint8_t count) { return (count + 3) / 4; }
}
