#include <Arduino.h>

#include "faucet_link.h"
#include "flavor.h"
#include "idle.h"
#include "flavor_link_policy.h"
#include "machine.h"
#include "pins.h"
#include "proto_link.h"
#include "proto_msg.h"
#include "sound.h"

namespace {

constexpr uint32_t kStateHeartbeatMs = 500;

ProtoLink faucet;
bool synchronized = false;
flavor_link_policy::TokenLedger handledTokens;
uint32_t lastSentRevision = 0;
uint32_t lastStatePublicationMs = 0;
uint32_t framesRx = 0;
uint32_t framesTx = 0;
uint32_t heartbeatPublications = 0;
uint32_t duplicateRequests = 0;
uint32_t invalidRequests = 0;
uint32_t lastRxMs = 0;
uint32_t connectionGeneration = 0;
bool connectionKnownUp = false;
uint32_t lastPrimeRevision = 0;
uint32_t lastPrimeStatePublicationMs = 0;
uint32_t primeStatePublications = 0;
uint32_t primeHeartbeatPublications = 0;
// A faucet display that just came up renders from artwork it has not been told
// yet, so the pair is published once per connection as well as on every change.
bool artPublished = false;
bool idlePublished = false;

void observeConnectionEpoch() {
    const uint32_t generation = faucet.connectionGeneration();
    if (!flavor_link_policy::consumeConnectionEpoch(
            generation, connectionGeneration)) return;
    if (connectionKnownUp)
        machinePrimeSessionSourceDisconnected(MACHINE_PRIME_FAUCET);
    connectionKnownUp = faucet.isConnected();
    synchronized = false;
    artPublished = false;
    handledTokens.reset();
}

uint8_t stateFlags() {
    return (flavorEstablished()       ? FLAVOR_STATE_F_ESTABLISHED   : 0)
         | (flavorPersisted()         ? FLAVOR_STATE_F_PERSISTED     : 0)
         | (flavorPersistenceError()  ? FLAVOR_STATE_F_PERSIST_ERROR : 0);
}

bool sendState(uint32_t token) {
    FlavorStatePayload state{flavorSelected(), stateFlags(), token};
    if (faucet.trySend(MSG_RESP_FLAVOR_STATE, &state, sizeof(state)) >= 0) {
        ++framesTx;
        lastSentRevision = flavorRevision();
        lastStatePublicationMs = millis();
        return true;
    }
    return false;
}

// The pair travels on its own message, so the six-byte flavor state keeps its
// wire layout and an older glass on either link is unaffected by it.
bool sendIdle() {
    IdlePayload idle{idleAsleep() ? (uint8_t)1 : (uint8_t)0, idleWindowMs()};
    if (faucet.trySend(MSG_RESP_IDLE, &idle, sizeof(idle)) >= 0) {
        ++framesTx;
        return true;
    }
    return false;
}

bool sendArt() {
    FlavorArtPayload art{{flavorArt(0), flavorArt(1)}};
    if (faucet.trySend(MSG_RESP_FLAVOR_ART, &art, sizeof(art)) >= 0) {
        ++framesTx;
        return true;
    }
    return false;
}

bool sendPrimeState() {
    MachinePrimeSessionState current;
    machineReadPrimeSessionState(current);
    PrimeSessionStatePayload state{
        current.phase,
        current.channel,
        current.owner,
        current.outcome,
        current.elapsedMs,
        current.revision,
        current.sessionToken,
        current.holdToken,
    };
    if (faucet.trySend(MSG_RESP_PRIME_SESSION, &state, sizeof(state)) >= 0) {
        ++framesTx;
        ++primeStatePublications;
        lastPrimeRevision = current.revision;
        lastPrimeStatePublicationMs = millis();
        return true;
    }
    return false;
}

void onMessage(ProtoLink *link, const uint8_t *frame, uint16_t len) {
    (void)link;
    // TinyProto reports CONNECTED before dispatching the first application
    // frame from that same RX buffer. Observe the epoch here so a valid SYNC
    // handled below cannot be erased by post-service epoch cleanup.
    observeConnectionEpoch();
    ++framesRx;
    lastRxMs = millis();

    const uint8_t type = msgType(frame);
    const uint8_t *payload = msgPayload(frame);
    const uint16_t plen = msgPayloadLen(len);

    if ((type == MSG_FLAVOR_SYNC || type == MSG_FLAVOR_SELECT) &&
        plen >= sizeof(FlavorRequestPayload)) {
        FlavorRequestPayload request;
        memcpy(&request, payload, sizeof(request));
        if (request.flavor > PUMP_CHANNEL_B || request.token == 0) {
            ++invalidRequests;
            if (faucet.trySendResponse(MSG_ERR_SLOT_INVALID, request.flavor) >= 0) ++framesTx;
            return;
        }

        synchronized = true;
        idleTouched();
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
        return;
    }

    if (type == MSG_TOUCH) {
        idleTouched();
        return;
    }

    if (type == MSG_IDLE_QUERY) {
        sendIdle();
        return;
    }

    if (type == MSG_FLAVOR_ART_QUERY) {
        sendArt();
        return;
    }

    if (type == MSG_FLAVOR_ART_SET && plen >= sizeof(FlavorArtPayload)) {
        FlavorArtPayload request;
        memcpy(&request, payload, sizeof(request));
        if (!flavorArtSet(request.art[0], request.art[1])) {
            ++invalidRequests;
            if (faucet.trySendResponse(MSG_ERR_SLOT_INVALID, request.art[0]) >= 0) ++framesTx;
            return;
        }
        sendArt();
        return;
    }

    if (type == MSG_PRIME_SESSION_QUERY &&
        plen >= sizeof(PrimeSessionQueryPayload)) {
        // J3 may ask for an immediate absolute snapshot, but only the enclosure
        // token on J9 can lease the prime-ready screen.
        sendPrimeState();
        return;
    }

    if (type == MSG_PRIME_SESSION_HOLD_START || type == MSG_PRIME_SESSION_SET) idleTouched();

    if (type == MSG_PRIME_SESSION_SET &&
        plen >= sizeof(PrimeSessionRequestPayload)) {
        PrimeSessionRequestPayload request;
        memcpy(&request, payload, sizeof(request));
        if (request.action != PRIME_SESSION_CANCEL ||
            request.channel > PUMP_CHANNEL_B || request.sessionToken == 0) {
            ++invalidRequests;
            if (faucet.trySendResponse(MSG_ERR_SLOT_INVALID, request.channel) >= 0) ++framesTx;
            return;
        }
        MachinePrimeSessionState before;
        machineReadPrimeSessionState(before);
        const bool accepted = machinePrimeSessionCancel(request.sessionToken);
        MachinePrimeSessionState after;
        machineReadPrimeSessionState(after);
        if (accepted && before.phase != PRIME_SESSION_OFF &&
            after.revision != before.revision) soundPlay(SND_TICK);
        sendPrimeState();
        return;
    }

    if ((type == MSG_PRIME_SESSION_HOLD_START ||
         type == MSG_PRIME_SESSION_HOLD_TICK ||
         type == MSG_PRIME_SESSION_HOLD_STOP) &&
        plen >= sizeof(PrimeHoldPayload)) {
        PrimeHoldPayload request;
        memcpy(&request, payload, sizeof(request));
        if (request.channel > PUMP_CHANNEL_B || request.sessionToken == 0 ||
            request.holdToken == 0) {
            ++invalidRequests;
            if (faucet.trySendResponse(MSG_ERR_SLOT_INVALID, request.channel) >= 0) ++framesTx;
            return;
        }

        if (type == MSG_PRIME_SESSION_HOLD_START) {
            machinePrimeSessionHoldBegin(MACHINE_PRIME_FAUCET,
                                         request.channel,
                                         request.sessionToken,
                                         request.holdToken);
        } else if (type == MSG_PRIME_SESSION_HOLD_TICK) {
            machinePrimeSessionHoldTick(MACHINE_PRIME_FAUCET,
                                        request.channel,
                                        request.sessionToken,
                                        request.holdToken);
        } else {
            machinePrimeSessionHoldEnd(MACHINE_PRIME_FAUCET,
                                       request.channel,
                                       request.sessionToken,
                                       request.holdToken);
        }
        sendPrimeState();
        return;
    }

    ++invalidRequests;
    if (faucet.trySendResponse(MSG_ERR_UNSUPPORTED, type) >= 0) ++framesTx;
}

}  // namespace

void faucetLinkBegin() {
    Serial2.setRxBufferSize(1024);
    Serial2.begin(FAUCET_BAUD, SERIAL_8N1, PIN_FAUCET_RX, PIN_FAUCET_TX);
    faucet.onMessage = onMessage;
    faucet.begin(Serial2, "J3 faucet");
    connectionGeneration = faucet.connectionGeneration();
    connectionKnownUp = faucet.isConnected();
    lastSentRevision = flavorRevision();
    // Make established persisted truth eligible as soon as the transport
    // connects. A factory-blank main board remains protected by the
    // mainBoardEstablished gate until it adopts the faucet cache.
    lastStatePublicationMs = millis() - kStateHeartbeatMs;
    MachinePrimeSessionState prime;
    machineReadPrimeSessionState(prime);
    lastPrimeRevision = prime.revision;
    lastPrimeStatePublicationMs = millis() - kStateHeartbeatMs;
}

void faucetLinkService() {
    faucet.service();

    // Covers a generation change that carried no application frame. If the
    // first frame arrived in the same service call, onMessage() already
    // observed the epoch before establishing synchronization.
    observeConnectionEpoch();
    const bool connected = faucet.isConnected();
    if (!connected) return;

    // Publish a revision immediately, then periodically repeat the complete
    // absolute state. trySend() only proves that TinyProto accepted a frame
    // into its local TX window; it does not prove that the sleeping faucet
    // applied it. The heartbeat closes that application-level gap and keeps
    // both UART directions exercised through TinyProto acknowledgements.
    // Same-state publications do not wake the faucet or reset its idle timer.
    const uint32_t now = millis();
    MachinePrimeSessionState prime;
    machineReadPrimeSessionState(prime);
    const bool primeRevisionPending = prime.revision != lastPrimeRevision;
    if (primeRevisionPending ||
        static_cast<uint32_t>(now - lastPrimeStatePublicationMs) >=
            kStateHeartbeatMs) {
        if (sendPrimeState() && !primeRevisionPending)
            ++primeHeartbeatPublications;
    }

    // Let TinyProto advance its one-frame window before the independent flavor
    // replica gets its turn. A RUNNING/OFF transition therefore is never held
    // behind a routine flavor heartbeat.
    faucet.service();

    const bool revisionPending = flavorRevision() != lastSentRevision;
    if (flavor_link_policy::mainBoardStatePublicationDue(
            connected, flavorEstablished(), revisionPending,
            now, lastStatePublicationMs, kStateHeartbeatMs)) {
        if (sendState(0) && !revisionPending) ++heartbeatPublications;
        // A revision moves for a selection or for the artwork; the faucet renders
        // from both, so a bump publishes both rather than guessing which moved.
        if (revisionPending || !artPublished) {
            if (sendArt()) artPublished = true;
        }
        if (!idlePublished && sendIdle()) idlePublished = true;
    }

    faucet.service();
}

void faucetLinkPublishIdle() {
    if (!sendIdle()) idlePublished = false;
}

void faucetLinkReadStatus(FaucetLinkStatus &status) {
    status.connected = faucet.isConnected();
    status.synchronized = synchronized;
    status.framesRx = framesRx;
    status.framesTx = framesTx;
    status.heartbeatPublications = heartbeatPublications;
    status.duplicateRequests = duplicateRequests;
    status.invalidRequests = invalidRequests;
    status.lastRxAgoMs = lastRxMs ? millis() - lastRxMs : 0;
    status.primeStatePublications = primeStatePublications;
    status.primeHeartbeatPublications = primeHeartbeatPublications;
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
    Serial.printf("    state heartbeats %lu, duplicate requests %lu, invalid requests %lu\n",
                  (unsigned long)status.heartbeatPublications,
                  (unsigned long)status.duplicateRequests,
                  (unsigned long)status.invalidRequests);
    Serial.printf("    prime states %lu (%lu heartbeats)\n",
                  (unsigned long)status.primeStatePublications,
                  (unsigned long)status.primeHeartbeatPublications);
}
