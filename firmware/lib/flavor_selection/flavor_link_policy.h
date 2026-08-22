#pragma once

#include <stdint.h>

namespace flavor_link_policy {

enum class EpochAction : uint8_t {
    Disconnected = 0,
    Synchronize,
    Reassert,
};

// Decide what the faucet replica must do whenever TinyProto reports any
// connection-generation change. queuedSelection is semantic: it stays true
// for B->A even when the final desired and last acknowledged values are both A.
bool needsReassert(bool offlineSelection,
                   bool durabilityPending,
                   bool queuedSelection,
                   uint8_t desiredFlavor,
                   uint8_t controllerFlavor);

EpochAction epochAction(bool connected,
                        bool offlineSelection,
                        bool durabilityPending,
                        bool queuedSelection,
                        uint8_t desiredFlavor,
                        uint8_t controllerFlavor);

// One controller session remembers the latest application token. The faucet
// sends only one application request at a time, so this is sufficient to make
// its retry idempotent without persisting protocol bookkeeping.
class TokenLedger {
public:
    TokenLedger() : have_(false), token_(0) {}

    void reset();
    bool duplicateOrRemember(uint32_t token);

private:
    bool have_;
    uint32_t token_;
};

}  // namespace flavor_link_policy
