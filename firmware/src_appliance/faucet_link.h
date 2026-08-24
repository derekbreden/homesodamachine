#pragma once

#include <stdint.h>

struct FaucetLinkStatus {
    bool connected;
    bool synchronized;
    uint32_t framesRx;
    uint32_t framesTx;
    uint32_t heartbeatPublications;
    uint32_t duplicateRequests;
    uint32_t invalidRequests;
    uint32_t lastRxAgoMs;
    uint32_t primeStatePublications;
    uint32_t primeHeartbeatPublications;
};

void faucetLinkBegin();
void faucetLinkService();

// Publish the shared idle state to the faucet.
void faucetLinkPublishIdle();
void faucetLinkReport();
void faucetLinkReadStatus(FaucetLinkStatus &status);
