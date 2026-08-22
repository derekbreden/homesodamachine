#pragma once

#include <stdint.h>

struct FaucetLinkStatus {
    bool connected;
    bool synchronized;
    uint32_t framesRx;
    uint32_t framesTx;
    uint32_t duplicateRequests;
    uint32_t invalidRequests;
    uint32_t lastRxAgoMs;
};

void faucetLinkBegin();
void faucetLinkService();
void faucetLinkReport();
void faucetLinkReadStatus(FaucetLinkStatus &status);
