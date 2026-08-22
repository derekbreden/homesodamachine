#include <Arduino.h>

#include "machine.h"
#include "pcba_expanders.h"
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

// ── The sound of a hold ───────────────────────────────────────────────────
// A prime is the one thing in this machine a person does by holding still, and
// the pump is loud enough that "is it running" answers itself. What the noise
// does NOT answer is how long you have been holding — and the pad has a ceiling,
// so that is the thing worth hearing.
//
// So the pitch is the progress bar. Once a second the hold speaks a short note,
// low at the start and climbing toward SOUND_RESONANCE_HZ as the ceiling nears —
// which is also where this diaphragm is loudest, so it grows more present as well
// as higher without anything having to get faster or louder to say so. It stays a
// tick rather than a tone: a tone held under a running pump for a minute is a
// thing people learn to hate, and it would mask the pump's own note besides.
static const unsigned long HOLD_NOTE_MS     = 1000;   // one reading per second
static const int           HOLD_NOTE_LEN_MS = 18;
static const int           HOLD_NOTE_DUTY   = 12;     // ~9 dB under the alarm; under the pump too
static const int           HOLD_HZ_LO       = 2200;
static const int           HOLD_HZ_HI       = 4200;

static unsigned long lastHoldNoteMs = 0;

static void holdNote(unsigned long elapsedMs) {
    uint32_t span = PRIME_MAX_MS ? PRIME_MAX_MS : 1;
    if (elapsedMs > span) elapsedMs = span;
    int hz = HOLD_HZ_LO + (int)((int64_t)(HOLD_HZ_HI - HOLD_HZ_LO) * elapsedMs / span);
    soundPlayNote((uint16_t)hz, HOLD_NOTE_LEN_MS, HOLD_NOTE_DUTY);
}

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

bool machineIoReady() {
    return pcba::expanders().initialized();
}

const char *machineIoFaultName(uint8_t fault) {
    switch (static_cast<pcba::Fault>(fault)) {
        case pcba::Fault::None:              return "none";
        case pcba::Fault::NotInitialized:    return "not initialized";
        case pcba::Fault::InvalidOutputPlan: return "invalid output plan";
        case pcba::Fault::BusBeginFailed:    return "bus begin";
        case pcba::Fault::BusWriteFailed:    return "bus write";
        case pcba::Fault::BusReadFailed:     return "bus read";
        case pcba::Fault::RegisterMismatch:  return "register mismatch";
        default:                             return "unknown";
    }
}

bool machineReadIoStatus(MachineIoStatus &status) {
    status = {};

    pcba::Health health;
    const bool healthOk = pcba::expanders().readHealth(health);
    status.initialized = health.initialized;
    status.configurationVerified = health.configurationVerified;
    status.outputsMatchPlan = health.outputsMatchPlan;
    status.outputsKnownParked = health.outputsKnownParked;
    status.fault = static_cast<uint8_t>(health.lastFault);
    status.faultAddress = health.faultAddress;
    status.faultRegister = health.faultRegister;
    status.outputLatchA20 = health.devices[0].olatA;
    status.outputLatchA21 = health.devices[1].olatA;
    status.pullupsB20 = health.devices[0].gppuB;
    status.pullupsB21 = health.devices[1].gppuB;
    if (!healthOk) return false;

    pcba::ReedSnapshot reeds;
    if (!pcba::expanders().readReeds(reeds)) {
        status.initialized = pcba::expanders().initialized();
        status.outputsKnownParked = pcba::expanders().outputsKnownParked();
        status.fault = static_cast<uint8_t>(pcba::expanders().lastFault());
        status.faultAddress = pcba::expanders().lastFaultAddress();
        status.faultRegister = pcba::expanders().lastFaultRegister();
        return false;
    }

    status.reedsValid = true;
    status.rawReedsA = reeds.rawReservoirAPortB;
    status.rawReedsB = reeds.rawReservoirBPortB;
    status.reservoirAClosedMask = reeds.reservoirAClosedMask;
    status.reservoirBClosedMask = reeds.reservoirBClosedMask;
    status.carbonatorLowClosed = reeds.carbonatorLowClosed;
    status.carbonatorHighClosed = reeds.carbonatorHighClosed;
    return true;
}

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
        // The mirror of the engage. A finger that MEANT to lift already knows, but
        // one that slid off the pad does not — PRESS_LOST ends a hold exactly as a
        // lift does, and a pump spinning down sounds the same either way. The two
        // endings below are the machine deciding rather than the finger, and they
        // get the fault pattern instead: the display stopped answering, or the
        // ceiling arrived under a finger that was still holding.
        if (primeState == PRIME_TIMEOUT || primeState == PRIME_LIMIT) soundPlay(SND_FAULT);
        else                                                          soundPlay(SND_RELEASE);
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

    // The MCPs keep their register state across an ESP-only reset because
    // their /RESET pins are tied high. Clear every latch and prove each output
    // pin low before enabling reed pull-ups or allowing setup to finish.
    if (!pcba::expanders().begin()) {
        pinMode(PIN_LED_ERR, OUTPUT);
        led(PIN_LED_ERR, true);
    }
}

void machineService() {
    heartbeat();
    gasService();
    if (state != ST_PUMPING) return;

    unsigned long now = millis();
    if (hold == HOLD_PRIME) {
        if (now - lastHoldNoteMs >= HOLD_NOTE_MS) {
            lastHoldNoteMs = now;
            holdNote(now - startedMs);
        }
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
    soundPlay(SND_ENGAGE);           // the pad took — richer than a tick, and specific to a hold
    lastHoldNoteMs = millis();       // the first reading is a second in, not immediately
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
