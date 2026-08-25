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
// Put one OTA frame on J3. Full duplex, so this has none of J9's turn rule.
bool faucetLinkSendOta(uint8_t type, const void *data, uint16_t len);

// What the display at the far end is doing with its radio.
void faucetLinkBleReport();

void faucetLinkReport();
void faucetLinkReadStatus(FaucetLinkStatus &status);
