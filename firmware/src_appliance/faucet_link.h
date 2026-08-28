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

// Ask the faucet to join the enclosure's bench AP and push this many bytes to
// it. The answer arrives asynchronously and prints itself; this only says
// whether J3 took the request.
bool faucetLinkWifiPush(uint32_t bytes, bool quietBle);

// Push this many bytes at J3 as fast as TinyProto's window will take them,
// writing nothing to flash. The wire's own ceiling, for the radio to be
// measured against. Blocks for the length of the run.
bool faucetLinkBenchPush(uint32_t bytes);

// What pictures the faucet is holding. The answer prints itself when it lands.
bool faucetLinkImagesQuery();

// Have the faucet make itself a picture, so the store and everything reading
// it can be exercised with no phone in the room.
bool faucetLinkImageSynth(uint8_t slot);

void faucetLinkReport();
void faucetLinkReadStatus(FaucetLinkStatus &status);
