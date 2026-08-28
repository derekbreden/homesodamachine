#include <Arduino.h>

#include "faucet_link.h"
#include "link.h"
#include "ota.h"
#include "flavor.h"
#include "identity.h"
#include "versions.h"
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

    if (type == MSG_OTA_REQ)  { otaOnRequest(OTA_TGT_FAUCET, payload, plen); return; }
    if (type == MSG_RESP_OTA) { otaOnState(OTA_TGT_FAUCET, payload, plen);   return; }

    // The faucet holds the radio, so it is also where an image arrives from.
    if (type == MSG_OTA_SRC_BEGIN) { otaOnSrcBegin(payload, plen); return; }
    if (type == MSG_OTA_SRC_DATA)  { otaOnSrcData(payload, plen);  return; }

    // The faucet has no console in the appliance. This is the one it borrows.
    if (type == MSG_TEXT) {
        char text[96];
        uint16_t n = plen < sizeof(text) - 1 ? plen : (uint16_t)(sizeof(text) - 1);
        memcpy(text, payload, n);
        text[n] = '\0';
        Serial.printf("\n[J3] text: %s\n", text);
        return;
    }

    if (type == MSG_RESP_IMAGES && plen >= sizeof(ImagesPayload)) {
        ImagesPayload im;
        memcpy(&im, payload, sizeof(im));
        char bits[FLAVOR_ART_CUSTOM + 1];
        for (uint8_t i = 0; i < FLAVOR_ART_CUSTOM; i++)
            bits[i] = (i < im.slots) ? ((im.occupancy & (1u << i)) ? 'X' : '.') : ' ';
        bits[FLAVOR_ART_CUSTOM] = '\0';
        Serial.printf("\n%-10s %u custom slots [%s], %u held, %lu B each\n",
                      im.board == OTA_TGT_FAUCET ? "faucet" : "enclosure",
                      im.slots, bits, im.held, (unsigned long)im.bundleBytes);
        return;
    }

    if (type == MSG_RESP_BENCH && plen >= sizeof(BenchResultPayload)) {
        BenchResultPayload r;
        memcpy(&r, payload, sizeof(r));
        const float secs = r.ms / 1000.0f;
        Serial.printf("\nJ3:BENCH %lu bytes in %lu ms — %.1f KB/s (%.0f%% of the %ld baud wire)\n",
                      (unsigned long)r.bytes, (unsigned long)r.ms,
                      secs > 0 ? (r.bytes / 1024.0f) / secs : 0.0f,
                      secs > 0 ? 100.0f * (r.bytes / secs) / (FAUCET_BAUD / 10.0f) : 0.0f,
                      FAUCET_BAUD);
        return;
    }

    // The bench run the console started, finished. Reported where it lands
    // rather than polled for: the run is seconds long and nothing waits on it.
    if (type == MSG_RESP_WIFI_PUSH && plen >= sizeof(WifiPushResultPayload)) {
        WifiPushResultPayload r;
        memcpy(&r, payload, sizeof(r));
        if (!r.ok) {
            static const char *why[] = {"", "never joined the AP", "the sink refused the socket",
                                        "the socket died mid-transfer", "a run is already in flight"};
            Serial.printf("\nWIFI:FAIL — %s\n",
                          r.err < 5 ? why[r.err] : "unknown");
            return;
        }
        const float kb = r.bytes / 1024.0f;
        const float secs = r.xferMs / 1000.0f;
        Serial.printf("\nWIFI:OK  %lu bytes in %lu ms — %.0f KB/s (%.1f Mbit/s)\n",
                      (unsigned long)r.bytes, (unsigned long)r.xferMs,
                      secs > 0 ? kb / secs : 0.0f,
                      secs > 0 ? (r.bytes * 8.0f / secs) / 1000000.0f : 0.0f);
        Serial.printf("     join %lu ms, socket %lu ms, RSSI %d dBm on channel %u\n",
                      (unsigned long)r.joinMs, (unsigned long)r.connectMs, r.rssi, r.channel);
        return;
    }

    if (type == MSG_RESP_BLE_STATUS && plen >= sizeof(BleStatusPayload)) {
        BleStatusPayload st;
        memcpy(&st, payload, sizeof(st));
        Serial.printf("\nBLE  %s%s%s as '%s'\n     session target=%u owed=%u dropped=%lu\n",
                      (st.flags & BLE_ST_UP) ? "up" : "DOWN",
                      (st.flags & BLE_ST_CONNECTED) ? ", a phone is connected" : ", advertising",
                      (st.flags & BLE_ST_IDENTITY) ? "" : ", identity unanswered",
                      st.advertised, st.target, st.owed, (unsigned long)st.dropped);
        return;
    }

    if (type == MSG_RESP_VERSION && plen >= sizeof(VersionPayload)) {
        VersionPayload v;
        memcpy(&v, payload, sizeof(v));
        v.version[FW_VERSION_MAX] = 0;
        versionsOnReport(OTA_TGT_FAUCET, v.version, v.artCrc32);
        return;
    }
    if (type == MSG_VERSIONS_QUERY) {
        VersionsPayload all;
        versionsFill(all);
        faucet.trySend(MSG_RESP_VERSIONS, &all, sizeof(all));
        return;
    }

    if (type == MSG_IDENTITY_QUERY) {
        IdentityPayload id;
        machineIdentity(id);
        faucet.trySend(MSG_RESP_IDENTITY, &id, sizeof(id));
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
    Serial2.setRxBufferSize(8192);
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

bool faucetLinkSendOta(uint8_t type, const void *data, uint16_t len) {
    return faucet.trySend(type, data, len) >= 0;
}

// Push into TinyProto's window as fast as it will take frames, servicing the
// link whenever it is full. No flash write and no per-chunk answer: what comes
// back is what J3 carries, which is the number the OTA pull is measured against.
bool faucetLinkImageSynth(uint8_t slot) {
    ImageSlotPayload req{slot};
    return faucet.trySend(MSG_IMAGE_SYNTH, &req, sizeof(req)) >= 0;
}

bool faucetLinkImagesQuery() {
    return faucet.trySend(MSG_IMAGES_QUERY, nullptr, 0) >= 0;
}

bool faucetLinkBenchPush(uint32_t bytes) {
    BenchBeginPayload begin{bytes};
    if (faucet.trySend(MSG_BENCH_BEGIN, &begin, sizeof(begin)) < 0) return false;

    static uint8_t chunk[BENCH_CHUNK];
    for (uint16_t i = 0; i < BENCH_CHUNK; i++) chunk[i] = (uint8_t)i;

    uint32_t sent = 0;
    const uint32_t started = millis();
    while (sent < bytes) {
        uint16_t want = (bytes - sent) > BENCH_CHUNK ? BENCH_CHUNK : (uint16_t)(bytes - sent);
        if (faucet.trySend(MSG_BENCH_DATA, chunk, want) >= 0) {
            sent += want;
        } else {
            faucet.service();   // window full: drain it and try the same chunk again
        }
        // The run is tens of seconds long and it owns the loop for all of them.
        // J9 is a half-duplex pair whose far end polls: leave it unanswered that
        // long and the enclosure gives up on the link and reinitialises it.
        linkService();
        if (millis() - started > 120000) return false;
    }
    // The last frames are still in the window; keep servicing so they land and
    // the far end's report can come back.
    const uint32_t drainUntil = millis() + 3000;
    while ((long)(millis() - drainUntil) < 0) { faucet.service(); linkService(); delay(1); }
    return true;
}

bool faucetLinkWifiPush(uint32_t bytes, bool quietBle) {
    WifiPushPayload req{bytes, WIFI_BENCH_CHANNEL,
                        (uint8_t)(quietBle ? WIFI_PUSH_F_QUIET_BLE : 0)};
    return faucet.trySend(MSG_WIFI_BENCH_PUSH, &req, sizeof(req)) >= 0;
}

void faucetLinkBleReport() {
    if (faucet.trySend(MSG_BLE_STATUS_REQ, nullptr, 0) < 0)
        Serial.println("\nJ3 would not take the request");
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
