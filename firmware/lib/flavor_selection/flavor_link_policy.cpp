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

bool controllerStatePublicationDue(bool connected,
                                   bool controllerEstablished,
                                   bool revisionPending,
                                   uint32_t nowMs,
                                   uint32_t lastPublicationMs,
                                   uint32_t heartbeatMs) {
    if (!connected || !controllerEstablished) return false;
    return revisionPending ||
           static_cast<uint32_t>(nowMs - lastPublicationMs) >= heartbeatMs;
}

bool controllerHeartbeatSettlesPendingSelection(bool offlineSelection,
                                                 bool queuedSelection,
                                                 bool headSent,
                                                 uint8_t desiredFlavor,
                                                 uint8_t controllerFlavor,
                                                 uint32_t nowMs,
                                                 uint32_t firstSentAtMs,
                                                 uint32_t graceMs) {
    if (offlineSelection || !queuedSelection) return false;
    if (controllerFlavor == desiredFlavor) return true;
    return headSent &&
           static_cast<uint32_t>(nowMs - firstSentAtMs) >= graceMs;
}

bool consumeConnectionEpoch(uint32_t observedGeneration,
                            uint32_t &knownGeneration) {
    if (observedGeneration == knownGeneration) return false;
    knownGeneration = observedGeneration;
    return true;
}

void TokenLedger::reset() {
    count_ = 0;
    next_ = 0;
}

bool TokenLedger::duplicateOrRemember(uint32_t token) {
    for (uint8_t i = 0; i < count_; ++i) {
        if (tokens_[i] == token) return true;
    }

    tokens_[next_] = token;
    next_ = static_cast<uint8_t>((next_ + 1) % kRecentTokenCapacity);
    if (count_ < kRecentTokenCapacity) ++count_;
    return false;
}

}  // namespace flavor_link_policy
