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

// Controller truth is normally published as soon as its revision changes.
// The periodic publication is the application-level backstop for a frame that
// TinyProto accepted into its TX window but the faucet never applied. An
// unestablished first-install controller must still wait for the faucet's
// cached candidate instead of publishing its arbitrary in-memory default.
bool controllerStatePublicationDue(bool connected,
                                   bool controllerEstablished,
                                   bool revisionPending,
                                   uint32_t nowMs,
                                   uint32_t lastPublicationMs,
                                   uint32_t heartbeatMs);

// Consume a transport generation exactly once. This lets a callback observe a
// new epoch before applying its first frame while a post-service check remains
// harmless when it sees that same generation.
bool consumeConnectionEpoch(uint32_t observedGeneration,
                            uint32_t &knownGeneration);

// Retain enough recent application tokens to cover more than one request.
// This keeps a delayed retry idempotent even after later maintenance traffic
// has used a newer token. The history is connection-local and needs no NVS.
constexpr uint8_t kRecentTokenCapacity = 16;

class TokenLedger {
public:
    TokenLedger() : tokens_{}, count_(0), next_(0) {}

    void reset();
    bool duplicateOrRemember(uint32_t token);

private:
    uint32_t tokens_[kRecentTokenCapacity];
    uint8_t count_;
    uint8_t next_;
};

}  // namespace flavor_link_policy
