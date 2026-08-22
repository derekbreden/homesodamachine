#include "flavor_link_policy.h"

namespace flavor_link_policy {

bool needsReassert(bool offlineSelection,
                   bool durabilityPending,
                   bool queuedSelection,
                   uint8_t desiredFlavor,
                   uint8_t controllerFlavor) {
    return offlineSelection || durabilityPending || queuedSelection ||
           desiredFlavor != controllerFlavor;
}

EpochAction epochAction(bool connected,
                        bool offlineSelection,
                        bool durabilityPending,
                        bool queuedSelection,
                        uint8_t desiredFlavor,
                        uint8_t controllerFlavor) {
    if (!connected) return EpochAction::Disconnected;
    return needsReassert(offlineSelection, durabilityPending, queuedSelection,
                         desiredFlavor, controllerFlavor)
               ? EpochAction::Reassert
               : EpochAction::Synchronize;
}

void TokenLedger::reset() {
    have_ = false;
    token_ = 0;
}

bool TokenLedger::duplicateOrRemember(uint32_t token) {
    if (have_ && token_ == token) return true;
    have_ = true;
    token_ = token;
    return false;
}

}  // namespace flavor_link_policy
