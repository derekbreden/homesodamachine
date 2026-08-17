#include <Arduino.h>

#include "link.h"
#include "machine.h"
#include "pins.h"
#include "proto_link.h"
#include "rs485_echo.h"
#include "fw_version.h"

static EchoCancel j9Stream(Serial1);
static HdlcLink   j9;

// ── What the machine announces, going out on the pair ─────────────────────
static void onPrimeState(uint8_t state, uint8_t channel, uint32_t ms) {
    PrimeStatePayload st{state, channel, ms};
    j9.send(MSG_RESP_PRIME, &st, sizeof(st));
}

static void onPumpDone(uint8_t channel) {
    j9.sendResponse(MSG_RESP_PUMP_DONE, channel);
}

// ── What arrives on the pair, becoming an intent ──────────────────────────
static void onMessage(HdlcLink *link, const uint8_t *frame, uint16_t len) {
    uint8_t        type    = msgType(frame);
    const uint8_t *payload = msgPayload(frame);
    uint16_t       plen    = msgPayloadLen(len);

    // A hold: START on finger down, TICK every PRIME_TICK_MS while it stays down,
    // STOP on lift. The machine announces all three, and a refusal.
    if (type == MSG_PRIME_START && plen >= sizeof(ChannelPayload)) {
        machinePrimeBegin(payload[0]);
        return;
    }
    if (type == MSG_PRIME_TICK && plen >= sizeof(ChannelPayload)) {
        machinePrimeTick(payload[0]);
        return;
    }
    if (type == MSG_PRIME_STOP && plen >= sizeof(ChannelPayload)) {
        machinePrimeEnd();
        return;
    }

    // A bounded run. MSG_RESP_PUMP_DONE goes out from onPumpDone(), with the head
    // already stopped.
    if (type == MSG_PUMP_RUN && plen >= sizeof(PumpRunPayload)) {
        PumpRunPayload req;
        memcpy(&req, payload, sizeof(req));
        Serial.printf("\n[J9] MSG_PUMP_RUN ch=%u ms=%u\n", req.channel, req.ms);
        if (!machinePumpRun(req.channel, req.ms))
            link->sendResponse(machineState() == ST_IDLE ? MSG_ERR_SLOT_INVALID : MSG_ERR_BUSY,
                               req.channel);
        return;
    }

    if (type == MSG_STATUS_REQ) {
        StatusPayload s{};
        s.uptimeS      = millis() / 1000;
        s.freeHeap     = ESP.getFreeHeap();
        s.framesRx     = j9.framesRx;
        s.framesTx     = j9.framesTx;
        s.gasMv        = (uint16_t)analogReadMilliVolts(PIN_GAS_AOUT);
        s.flags        = (analogReadMilliVolts(PIN_GAS_DOUT) > 1500 ? STATUS_F_GAS_TRIP : 0)
                       | (machineIsPriming() ? STATUS_F_PRIMING : 0);
        s.primeChannel = machinePumpChannel();
        strncpy(s.version, FW_VERSION, sizeof(s.version) - 1);
        link->send(MSG_RESP_STATUS, &s, sizeof(s));
        return;
    }

    // The clean cycle runs the manifold, which hangs off the two MCP23017s this
    // image leaves untouched.
    if (type == MSG_CLEAN_START) {
        link->sendResponse(MSG_ERR_UNSUPPORTED, plen ? payload[0] : 0);
        Serial.println("\n[J9] MSG_CLEAN_START -> unsupported (no valve drive in this build)");
        return;
    }

    if (type == MSG_TEXT) {
        char text[96];
        uint16_t n = plen < sizeof(text) - 1 ? plen : sizeof(text) - 1;
        memcpy(text, payload, n);
        text[n] = '\0';
        Serial.printf("\n[J9] text: %s\n", text);
        return;
    }

    Serial.printf("\n[J9] type 0x%02X, %u byte(s), raw", type, plen);
    for (uint16_t i = 0; i < len && i < 16; i++) Serial.printf(" %02X", frame[i]);
    Serial.println();
}

void linkBegin() {
    machineOnPrimeState = onPrimeState;
    machineOnPumpDone   = onPumpDone;

    Serial1.begin(RS485_BAUD, SERIAL_8N1, PIN_485_RO, PIN_485_DI);
    j9.onMessage = onMessage;
    j9.begin(j9Stream, "J9");
}

void linkService() { j9.service(); }

void linkReport() {
    Serial.printf("\nJ9  IO%d DI / IO%d RO @ %ld — frames rx %lu / tx %lu, bytes rx %lu / tx %lu\n",
                  PIN_485_DI, PIN_485_RO, RS485_BAUD,
                  (unsigned long)j9.framesRx, (unsigned long)j9.framesTx,
                  (unsigned long)j9.bytesRx, (unsigned long)j9.bytesTx);
    if (j9.lastRxMs)
        Serial.printf("    last frame %lu ms ago\n", millis() - j9.lastRxMs);
    else
        Serial.println("    nothing has arrived — the display is unpowered, unflashed, or A/B is swapped");
    Serial.printf("    echo swallowed %u, outstanding %u, high-water %u\n",
                  (unsigned)j9Stream.echoSwallowed(), (unsigned)j9Stream.echoOutstanding(),
                  (unsigned)j9Stream.echoHighWater());
}
