#include <Arduino.h>

#include "faucet_link.h"
#include "flavor.h"
#include "flavor_link_policy.h"
#include "pins.h"
#include "proto_link.h"
#include "proto_msg.h"
#include "sound.h"

namespace {

ProtoLink faucet;
bool synchronized = false;
flavor_link_policy::TokenLedger handledTokens;
uint32_t lastSentRevision = 0;
uint32_t framesRx = 0;
uint32_t framesTx = 0;
uint32_t duplicateRequests = 0;
uint32_t invalidRequests = 0;
uint32_t lastRxMs = 0;
uint32_t connectionGeneration = 0;

uint8_t stateFlags() {
    return (flavorEstablished()       ? FLAVOR_STATE_F_ESTABLISHED   : 0)
         | (flavorPersisted()         ? FLAVOR_STATE_F_PERSISTED     : 0)
         | (flavorPersistenceError()  ? FLAVOR_STATE_F_PERSIST_ERROR : 0);
}

void sendState(uint32_t token) {
    FlavorStatePayload state{flavorSelected(), stateFlags(), token};
    if (faucet.trySend(MSG_RESP_FLAVOR_STATE, &state, sizeof(state)) >= 0) {
        ++framesTx;
        lastSentRevision = flavorRevision();
    }
}

void onMessage(ProtoLink *link, const uint8_t *frame, uint16_t len) {
    (void)link;
    ++framesRx;
    lastRxMs = millis();

    const uint8_t type = msgType(frame);
    const uint8_t *payload = msgPayload(frame);
    const uint16_t plen = msgPayloadLen(len);

    if ((type != MSG_FLAVOR_SYNC && type != MSG_FLAVOR_SELECT) ||
        plen < sizeof(FlavorRequestPayload)) {
        ++invalidRequests;
        if (faucet.trySendResponse(MSG_ERR_UNSUPPORTED, type) >= 0) ++framesTx;
        return;
    }

    FlavorRequestPayload request;
    memcpy(&request, payload, sizeof(request));
    if (request.flavor > PUMP_CHANNEL_B || request.token == 0) {
        ++invalidRequests;
        if (faucet.trySendResponse(MSG_ERR_SLOT_INVALID, request.flavor) >= 0) ++framesTx;
        return;
    }

    synchronized = true;
    const bool duplicate = handledTokens.duplicateOrRemember(request.token);
    if (duplicate) {
        ++duplicateRequests;
        sendState(request.token);
        return;
    }

    if (type == MSG_FLAVOR_SYNC) {
        flavorSynchronize(request.flavor);
    } else {
        flavorSelect(request.flavor);
        if ((request.flags & FLAVOR_REQ_F_AUDIBLE) != 0) soundPlay(SND_TICK);
        Serial.printf("\n[J3] faucet selected flavor %u%s\n",
                      flavorSelected() + 1,
                      flavorPersisted() ? "" : " — persistence pending");
    }
    sendState(request.token);
}

}  // namespace

void faucetLinkBegin() {
    Serial2.setRxBufferSize(1024);
    Serial2.begin(FAUCET_BAUD, SERIAL_8N1, PIN_FAUCET_RX, PIN_FAUCET_TX);
    faucet.onMessage = onMessage;
    faucet.begin(Serial2, "J3 faucet");
    connectionGeneration = faucet.connectionGeneration();
    lastSentRevision = flavorRevision();
}

void faucetLinkService() {
    faucet.service();

    const uint32_t generation = faucet.connectionGeneration();
    const bool connected = faucet.isConnected();
    if (generation != connectionGeneration) {
        connectionGeneration = generation;
        synchronized = false;
        handledTokens.reset();
        if (!connected) return;
    }

    // J3 is full duplex, so a controller-side console change or completion of
    // a deferred NVS write can be published without J9's turn-taking rule. A
    // new connection must send SYNC first so a first-ever controller can adopt
    // the faucet's cache rather than pushing an arbitrary default.
    if (connected && synchronized && flavorRevision() != lastSentRevision)
        sendState(0);

    faucet.service();
}

void faucetLinkReadStatus(FaucetLinkStatus &status) {
    status.connected = faucet.isConnected();
    status.synchronized = synchronized;
    status.framesRx = framesRx;
    status.framesTx = framesTx;
    status.duplicateRequests = duplicateRequests;
    status.invalidRequests = invalidRequests;
    status.lastRxAgoMs = lastRxMs ? millis() - lastRxMs : 0;
}

void faucetLinkReport() {
    FaucetLinkStatus status;
    faucetLinkReadStatus(status);
    Serial.printf("J3  IO%d TX / IO%d RX @ %ld — %s, %s, frames rx %lu / tx %lu\n",
                  PIN_FAUCET_TX, PIN_FAUCET_RX, FAUCET_BAUD,
                  status.connected ? "connected" : "disconnected",
                  status.synchronized ? "flavor synchronized" : "awaiting sync",
                  (unsigned long)status.framesRx, (unsigned long)status.framesTx);
    if (lastRxMs) Serial.printf("    last frame %lu ms ago\n", (unsigned long)status.lastRxAgoMs);
    else          Serial.println("    nothing has arrived from GPIO43 TX on the faucet");
    Serial.printf("    duplicate requests %lu, invalid requests %lu\n",
                  (unsigned long)status.duplicateRequests,
                  (unsigned long)status.invalidRequests);
}
