#include <Arduino.h>

#include "machine.h"
#include "pins.h"
#include "proto_msg.h"
#include "sound.h"

void (*machineOnPrimeState)(uint8_t, uint8_t, uint32_t) = nullptr;
void (*machineOnPumpDone)(uint8_t) = nullptr;

// ── The two flavor pumps ──────────────────────────────────────────────────
struct PumpChannel { const char *who; int pin; const char *driver; const char *j13; };
static const PumpChannel kPump[2] = {
    {"A", PIN_PUMP_A, "U11", "AM1 + AM2 (the two WEST pins)"},
    {"B", PIN_PUMP_B, "U12", "BM1 + BM2 (the two EAST pins)"},
};

// ── State ─────────────────────────────────────────────────────────────────
static MachineState  state       = ST_IDLE;
static PumpHold      hold        = HOLD_PRIME;
static uint8_t       channelNow  = 0;
static unsigned long startedMs   = 0;
static unsigned long lastTickMs  = 0;
static unsigned long deadlineMs  = 0;

// Everything that reaches a load. Parked as inputs, which is dark: a DRV8870
// IN1 coasts on the driver's own pull-down and a Teyleten opto with no drive
// holds its relay open. The park survives a brownout reset, so a board that
// resets mid-pour comes back with nothing energized.
//
// IO13 is not in this list. It reaches a load too — U8's ~100 mA coil through
// Q1 — but a sound is a sequence in time rather than a level, so it needs a
// service loop of its own; lib/sound owns that pin end to end and is the only
// thing that writes it. soundBegin() below parks it before anything else runs.
static const int kActuators[] = {
    PIN_RELAY_COMPRESSOR, PIN_RELAY_REFILL, PIN_PUMP_A, PIN_PUMP_B,
};

// ── Indicators ────────────────────────────────────────────────────────────
// ERR hangs off 3V3, so LOW lights it; RUN and ACT run to GND and light HIGH.
static void led(int pin, bool on) { digitalWrite(pin, pin == PIN_LED_ERR ? !on : on); }

// RUN is a boot strap, so it lives parked on its internal pull-down and each
// beat is a brief excursion out and straight back — a reset landing between
// beats finds MTDI already where the 3.3 V flash setting wants it.
static const unsigned long BEAT_ON_MS     = 30;
static const unsigned long BEAT_PERIOD_MS = 2000;

static void parkStraps() {
    pinMode(PIN_LED_RUN, INPUT_PULLDOWN);
    pinMode(PIN_LED_ERR, INPUT_PULLUP);
}

static void heartbeat() {
    static unsigned long lastBeat = 0, beatEnds = 0;
    if (beatEnds) {
        if (millis() >= beatEnds) { pinMode(PIN_LED_RUN, INPUT_PULLDOWN); beatEnds = 0; }
    } else if (millis() - lastBeat >= BEAT_PERIOD_MS) {
        lastBeat = millis();
        pinMode(PIN_LED_RUN, OUTPUT);
        led(PIN_LED_RUN, true);
        beatEnds = lastBeat + BEAT_ON_MS;
    }
}

// ── The gas watch ─────────────────────────────────────────────────────────
// U15 already holds the compressor off a gas trip in hardware, with no firmware
// in the path — that interlock is the safety, and this is not it. This is the
// part a person needs: the trip made audible, so a leak in an empty kitchen is
// heard from another room.
//
// The MQ-6's LM393 output arrives divided to ~3.0 V through R3/R4. A trip has to
// hold GAS_SETTLE_MS to count, which keeps a comparator sitting on its threshold
// from chattering the alarm; clearing is held the same way. With no sensor fitted
// the divider reads near zero and nothing ever asserts.
static const int      GAS_TRIP_MV   = 1500;
static const uint32_t GAS_SETTLE_MS = 500;

static bool          gasTrip     = false;
static bool          gasRaw      = false;
static unsigned long gasChanged  = 0;

static void gasService() {
    bool raw = analogReadMilliVolts(PIN_GAS_DOUT) > GAS_TRIP_MV;
    if (raw != gasRaw) { gasRaw = raw; gasChanged = millis(); }
    if (raw != gasTrip && millis() - gasChanged >= GAS_SETTLE_MS) {
        gasTrip = raw;
        if (gasTrip) {
            Serial.println("\n[machine] GAS TRIP — MQ-6 comparator asserted, alarm sounding");
            soundPlay(SND_ALARM);
        } else {
            Serial.println("\n[machine] gas clear");
            if (soundPlaying() == SND_ALARM) soundStop();
        }
    }
    // The alarm loops forever, so re-asserting it costs nothing and covers a
    // soundStop() from anywhere else while the condition still stands.
    if (gasTrip) soundPlay(SND_ALARM);
}

bool machineGasTripped() { return gasTrip; }

// ── The pump, driven from nowhere but here ────────────────────────────────
static bool pumpDrive(uint8_t channel) {
    if (!ledcAttach(kPump[channel].pin, PUMP_PWM_HZ, PUMP_PWM_BITS)) {
        pinMode(kPump[channel].pin, INPUT);   // back to the park
        return false;
    }
    ledcWrite(kPump[channel].pin, 255);       // full duty
    return true;
}

static void pumpPark(uint8_t channel) {
    ledcWrite(kPump[channel].pin, 0);
    ledcDetach(kPump[channel].pin);
    pinMode(kPump[channel].pin, INPUT);       // back to the boot parking
}

static const char *primeStateName(uint8_t s) {
    switch (s) {
        case PRIME_RUNNING: return "running";
        case PRIME_STOPPED: return "stopped";
        case PRIME_TIMEOUT: return "tick timeout";
        case PRIME_LIMIT:   return "ceiling";
        default:            return "refused";
    }
}

static void announce(uint8_t primeState, uint8_t channel, uint32_t ms) {
    Serial.printf("\n[machine] pump %s %s after %lu ms\n",
                  kPump[channel & 1].who, primeStateName(primeState), (unsigned long)ms);
    if (machineOnPrimeState) machineOnPrimeState(primeState, channel, ms);
}

// Every exit from ST_PUMPING runs through here.
static void endPumping(uint8_t primeState) {
    if (state != ST_PUMPING) return;
    uint32_t ran = millis() - startedMs;
    uint8_t  ch  = channelNow;
    PumpHold why = hold;

    pumpPark(ch);
    led(PIN_LED_ACT, false);
    state = ST_IDLE;

    if (why == HOLD_PRIME) {
        // A finger lifting off the glass needs no sound — the user did it and is
        // watching. The other two endings are the machine deciding, so they are
        // the ones worth hearing: the display stopped answering, or the ceiling
        // arrived under a finger that was still holding.
        if (primeState == PRIME_TIMEOUT || primeState == PRIME_LIMIT) soundPlay(SND_FAULT);
        announce(primeState, ch, ran);
    } else {
        Serial.printf("\n[machine] pump %s done after %lu ms\n", kPump[ch].who, (unsigned long)ran);
        soundPlay(SND_CHIME);
        if (machineOnPumpDone) machineOnPumpDone(ch);
    }
}

// ── Setup and service ─────────────────────────────────────────────────────
void machineBegin() {
    soundBegin(PIN_BUZZ);   // the coil is parked before anything else runs
    for (int pin : kActuators) pinMode(pin, INPUT);
    parkStraps();
    pinMode(PIN_LED_ACT, OUTPUT);
    led(PIN_LED_ACT, false);
    state = ST_IDLE;
}

void machineService() {
    heartbeat();
    gasService();
    if (state != ST_PUMPING) return;

    unsigned long now = millis();
    if (hold == HOLD_PRIME) {
        // The hold is a heartbeat: a finger that lifts sends MSG_PRIME_STOP; a
        // display that crashes, unplugs, or loses the pair sends nothing. The head
        // stops either way.
        if (now - lastTickMs > PRIME_TICK_GRACE_MS)  endPumping(PRIME_TIMEOUT);
        else if (now - startedMs >= PRIME_MAX_MS)    endPumping(PRIME_LIMIT);
    } else if (now >= deadlineMs) {
        endPumping(PRIME_STOPPED);
    }
}

// ── Intents ───────────────────────────────────────────────────────────────
static bool claimPump(uint8_t channel, PumpHold why) {
    if (channel > 1)         return false;
    if (state != ST_IDLE)    return false;   // one operation at a time is the interlock
    if (!pumpDrive(channel)) return false;   // no LEDC channel free

    hold       = why;
    channelNow = channel;
    startedMs  = millis();
    lastTickMs = startedMs;
    state      = ST_PUMPING;
    led(PIN_LED_ACT, true);
    return true;
}

bool machinePrimeBegin(uint8_t channel) {
    if (!claimPump(channel, HOLD_PRIME)) {
        soundPlay(SND_REFUSE);
        announce(PRIME_REFUSED, channel, 0);
        return false;
    }
    Serial.printf("\n[machine] prime %s at full (IO%d -> %s.IN1 -> J13.%s)\n",
                  kPump[channel].who, kPump[channel].pin, kPump[channel].driver, kPump[channel].j13);
    if (machineOnPrimeState) machineOnPrimeState(PRIME_RUNNING, channel, 0);
    return true;
}

void machinePrimeTick(uint8_t channel) {
    if (state == ST_PUMPING && hold == HOLD_PRIME && channel == channelNow) lastTickMs = millis();
}

void machinePrimeEnd() {
    if (state == ST_PUMPING && hold == HOLD_PRIME) endPumping(PRIME_STOPPED);
}

bool machinePumpRun(uint8_t channel, uint32_t ms) {
    if (ms > PRIME_MAX_MS) ms = PRIME_MAX_MS;   // the same ceiling, whatever the caller asks for
    if (!claimPump(channel, HOLD_TIMED)) { soundPlay(SND_REFUSE); return false; }
    deadlineMs = startedMs + ms;
    Serial.printf("\n[machine] pump %s at full for %lu ms (IO%d -> %s.IN1 -> J13.%s)\n",
                  kPump[channel].who, (unsigned long)ms, kPump[channel].pin,
                  kPump[channel].driver, kPump[channel].j13);
    return true;
}

void machineStop() { endPumping(PRIME_STOPPED); }

MachineState machineState()     { return state; }
const char  *machineStateName() { return state == ST_PUMPING ? "pumping" : "idle"; }
bool         machineIsPriming() { return state == ST_PUMPING && hold == HOLD_PRIME; }
uint8_t      machinePumpChannel()   { return channelNow; }
uint32_t     machinePumpElapsedMs() { return state == ST_PUMPING ? millis() - startedMs : 0; }
const char  *machinePumpName(uint8_t channel) { return kPump[channel & 1].who; }
