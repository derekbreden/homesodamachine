#pragma once

#include <stdint.h>

#include "proto_msg.h"   // the wire payloads a caller reads a result out of

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
bool faucetLinkImagesQuery(uint8_t verbose);

// Have the faucet make itself a picture, so the store and everything reading
// it can be exercised with no phone in the room.
bool faucetLinkImageSynth(uint8_t slot);

// Tell the faucet the enclosure's radio is standing and it may send.
bool faucetLinkImageRelayGo(uint8_t slot);

// A slot the faucet has asked to have carried to the enclosure, or 0xFF for
// none. Taking it clears it, so the loop runs one hop per request.
uint8_t faucetLinkTakeRelayRequest();

// A slot the phone removed, or 0xFF for none. Taking it clears it.
uint8_t faucetLinkTakeEraseRequest();

// The outcome of the last radio push, once. A relay waits on this rather than
// on a clock: the transfer takes a second or two and the fixed minute it used
// to wait was a minute of dark glass on the enclosure. False until one lands.
bool faucetLinkTakePushResult(WifiPushResultPayload &out);

// Drop any result still standing, so a wait cannot be satisfied by the last run.
void faucetLinkForgetPushResult();

// What a WIFI_BENCH_ERR_* means, in words.
const char *faucetLinkPushError(uint8_t err);

// Take a picture back off the faucet.
bool faucetLinkImageErase(uint8_t slot);

void faucetLinkReport();
void faucetLinkReadStatus(FaucetLinkStatus &status);
