#include <Arduino.h>

#include "flavor.h"
#include "machine.h"
#include "machine_policy.h"
#include "pcba_expanders.h"
#include "pins.h"
#include "pour_policy.h"
#include "proto_msg.h"
#include "sound.h"

void (*machineOnPrimeState)(uint8_t, uint8_t, uint32_t) = nullptr;
void (*machineOnPumpDone)(uint8_t) = nullptr;
void (*machineOnFillState)(const MachineFillState &) = nullptr;
void (*machineOnCleanState)(const MachineCleanState &) = nullptr;
void (*machineOnAirState)(const MachineAirState &) = nullptr;

static_assert(PRIME_TICK_MS == machine_policy::kPrimeTickPeriodMs,
              "prime tick period must match machine policy");
static_assert(PRIME_TICK_GRACE_MS == machine_policy::kPrimeTickGraceMs,
              "prime tick grace must match machine policy");
static_assert(PRIME_MAX_MS == machine_policy::kPumpRunCeilingMs,
              "pump ceiling must match machine policy");
static_assert(PRIME_SESSION_OFF == static_cast<uint8_t>(machine_policy::PrimeSessionPhase::Off),
              "prime session phase drift: off");
static_assert(PRIME_SESSION_READY == static_cast<uint8_t>(machine_policy::PrimeSessionPhase::Ready),
              "prime session phase drift: ready");
static_assert(PRIME_SESSION_RUNNING == static_cast<uint8_t>(machine_policy::PrimeSessionPhase::Running),
              "prime session phase drift: running");
static_assert(PRIME_OWNER_NONE == static_cast<uint8_t>(machine_policy::PrimeSessionOwner::None),
              "prime session owner drift: none");
static_assert(PRIME_OWNER_ENCLOSURE ==
                  static_cast<uint8_t>(machine_policy::PrimeSessionOwner::Enclosure),
              "prime session owner drift: enclosure");
static_assert(PRIME_OWNER_FAUCET == static_cast<uint8_t>(machine_policy::PrimeSessionOwner::Faucet),
              "prime session owner drift: faucet");
static_assert(PRIME_OUTCOME_CANCELED ==
                  static_cast<uint8_t>(machine_policy::PrimeSessionOutcome::Canceled),
              "prime session outcome drift: canceled");
static_assert(PRIME_OUTCOME_LEASE_EXPIRED ==
                  static_cast<uint8_t>(machine_policy::PrimeSessionOutcome::LeaseExpired),
              "prime session outcome drift: lease expired");

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
static machine_policy::PumpTimer pumpTimer;
static machine_policy::PrimeSession primeSession;
static bool primeRunUsesSession = false;
static bool primeEventUsesSession = false;

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

// ── The reeds, and the level they say ─────────────────────────────────────
// One read of both expanders serves everything that wants a reed: the fill,
// the clean and air cycles read through here every quarter second while they
// run, and the idle machine reads once a second so the glasses' gauges are
// never older than that. Each reading feeds the two level trackers with what
// the machine is doing to that reservoir at the time.
static const uint32_t kIdleReedPeriodMs = 1000;
static const uint32_t kReedFreshMs      = 5000;
static pcba::ReedSnapshot reedCache;
static bool     reedCacheValid = false;
static uint32_t reedCacheMs    = 0;
static uint32_t reedIdleMs     = 0;
static machine_policy::ReservoirLevel reservoirLevel[2];

static machine_policy::LevelMotion levelMotionFor(uint8_t channel);

static bool readReeds() {
    pcba::ReedSnapshot reeds;
    if (!pcba::expanders().readReeds(reeds)) {
        reedCacheValid = false;
        return false;
    }
    reedCache      = reeds;
    reedCacheValid = true;
    reedCacheMs    = millis();
    reservoirLevel[0].observe(reeds.reservoirAClosedMask, levelMotionFor(0));
    reservoirLevel[1].observe(reeds.reservoirBClosedMask, levelMotionFor(1));
    return true;
}

static uint8_t reedMaskFor(uint8_t channel) {
    return channel == PUMP_CHANNEL_A ? reedCache.reservoirAClosedMask : reedCache.reservoirBClosedMask;
}

static void reedIdleService(uint32_t now) {
    if (state != ST_IDLE || !pcba::expanders().initialized()) return;
    if (now - reedIdleMs < kIdleReedPeriodMs) return;
    reedIdleMs = now;
    readReeds();
}

void machineLevels(MachineLevels &l) {
    l.valid    = reedCacheValid && (uint32_t)(millis() - reedCacheMs) < kReedFreshMs;
    l.reeds[0] = reedCache.reservoirAClosedMask;
    l.reeds[1] = reedCache.reservoirBClosedMask;
    l.level[0] = reservoirLevel[0].segments();
    l.level[1] = reservoirLevel[1].segments();
    l.carbLow  = reedCache.carbonatorLowClosed;
    l.carbHigh = reedCache.carbonatorHighClosed;
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

static machine_policy::PrimeSessionOwner primeOwner(MachinePrimeSource source) {
    return source == MACHINE_PRIME_FAUCET
        ? machine_policy::PrimeSessionOwner::Faucet
        : machine_policy::PrimeSessionOwner::Enclosure;
}

static machine_policy::PrimeSessionOutcome primeOutcome(uint8_t state) {
    switch (state) {
        case PRIME_STOPPED: return machine_policy::PrimeSessionOutcome::Stopped;
        case PRIME_TIMEOUT: return machine_policy::PrimeSessionOutcome::Timeout;
        case PRIME_LIMIT:   return machine_policy::PrimeSessionOutcome::Limit;
        default:            return machine_policy::PrimeSessionOutcome::Refused;
    }
}

static void announce(uint8_t primeState, uint8_t channel, uint32_t ms) {
    Serial.printf("\n[machine] pump %s %s after %lu ms\n",
                  kPump[channel & 1].who, primeStateName(primeState), (unsigned long)ms);
    if (machineOnPrimeState) machineOnPrimeState(primeState, channel, ms);
}

// Every exit from ST_PUMPING runs through here. A timer service consumes its
// terminal event, so that path supplies the elapsed time captured just before
// service; an explicit stop captures it here.
static void endPumping(uint8_t primeState, uint32_t ran) {
    if (state != ST_PUMPING) return;
    uint8_t  ch  = channelNow;
    PumpHold why = hold;
    const bool sessionRun = primeRunUsesSession;

    pumpTimer.stop();
    pumpPark(ch);
    led(PIN_LED_ACT, false);
    state = ST_IDLE;

    if (why == HOLD_PRIME) {
        primeSession.pumpStopped(primeOutcome(primeState), ran);
        // The mirror of the engage. A finger that MEANT to lift already knows, but
        // one that slid off the pad does not — PRESS_LOST ends a hold exactly as a
        // lift does, and a pump spinning down sounds the same either way. The two
        // endings below are the machine deciding rather than the finger, and they
        // get the fault pattern instead: the display stopped answering, or the
        // ceiling arrived under a finger that was still holding.
        if (primeState == PRIME_TIMEOUT || primeState == PRIME_LIMIT) soundPlay(SND_FAULT);
        else                                                          soundPlay(SND_RELEASE);
        primeEventUsesSession = sessionRun;
        announce(primeState, ch, ran);
        primeEventUsesSession = false;
        primeRunUsesSession = false;
    } else {
        Serial.printf("\n[machine] pump %s done after %lu ms\n", kPump[ch].who, (unsigned long)ran);
        soundPlay(SND_CHIME);
        if (machineOnPumpDone) machineOnPumpDone(ch);
    }
}

static void endPumping(uint8_t primeState) {
    endPumping(primeState, pumpTimer.elapsedMs(millis()));
}

// ── The funnel fill ───────────────────────────────────────────────────────
// Three valves and one pump: the channel's funnel path, held open while its
// head draws what was poured down into the reservoir. The plan is the
// topology's own (machine_policy::fillOperation), the clock and the reservoir's
// reeds decide the end (machine_policy::fillShouldEnd), and the pump stops a
// dwell before its valves close.
static uint8_t  fillChannel    = 0;
static uint8_t  fillOutcome    = FILL_OUTCOME_NONE;
static uint8_t  fillReeds      = 0xFF;
static uint32_t fillStartMs    = 0;
static uint32_t fillPlannedMs  = machine_policy::kFillPlannedMs;
static uint32_t fillElapsedMs  = 0;   // final, once the draw has ended
static uint32_t fillLastReedMs = 0;
static uint32_t fillParkAtMs   = 0;   // nonzero: the pump is off and the valves close then
static bool     fillDrawing    = false;

static uint32_t fillElapsedNow(uint32_t now) {
    return fillDrawing ? now - fillStartMs : fillElapsedMs;
}

static void fillAnnounce(uint32_t now) {
    MachineFillState st;
    st.phase     = state == ST_FILLING ? FILL_PHASE_RUNNING : FILL_PHASE_OFF;
    st.channel   = fillChannel;
    st.outcome   = state == ST_FILLING ? FILL_OUTCOME_NONE : fillOutcome;
    st.elapsedMs = fillElapsedNow(now);
    st.plannedMs = fillPlannedMs;
    st.reeds     = fillReeds;
    if (machineOnFillState) machineOnFillState(st);
}

static const char *fillOutcomeName(uint8_t outcome) {
    switch (outcome) {
        case FILL_OUTCOME_DONE:    return "drew its planned time";
        case FILL_OUTCOME_FULL:    return "the reservoir is full";
        case FILL_OUTCOME_STOPPED: return "stopped on request";
        case FILL_OUTCOME_BUSY:    return "refused — busy";
        case FILL_OUTCOME_NO_IO:   return "refused — expanders unverified";
        case FILL_OUTCOME_FAULT:   return "fault — everything parked";
        case FILL_OUTCOME_GAS:     return "gas alarm";
        default:                   return "none";
    }
}

// "B C F", off a logical mask.
static const char *valveNames(uint16_t mask, char *buf, size_t n) {
    size_t at = 0;
    for (uint8_t v = 0; v < machine_policy::kValveCount && at + 2 < n; v++) {
        if (!(mask & (1u << v))) continue;
        if (at) buf[at++] = ' ';
        buf[at++] = (char)('A' + v);
    }
    buf[at] = '\0';
    return at ? buf : "none";
}

static bool fillReadReeds() {
    if (!readReeds()) return false;
    fillReeds = reedMaskFor(fillChannel);
    return true;
}

// The pump stops now; the valves close after the dwell, from fillService().
static void fillEnd(uint8_t outcome, uint32_t now) {
    if (state != ST_FILLING || fillParkAtMs) return;
    fillElapsedMs = fillElapsedNow(now);
    if (fillDrawing) pumpPark(fillChannel);
    fillDrawing  = false;
    fillOutcome  = outcome;
    fillParkAtMs = now + machine_policy::kFillParkDwellMs;
    if (!fillParkAtMs) fillParkAtMs = 1;
}

// Everything off. The ending is announced from here, once nothing is energised.
static void fillParked() {
    // A fault has already parked the expanders and invalidated them; asking
    // again is harmless and keeps the one exit.
    if (!pcba::expanders().apply(pcba::ExpanderOutputs())) pcba::expanders().parkAll();
    fillParkAtMs = 0;
    led(PIN_LED_ACT, false);
    state = ST_IDLE;
    Serial.printf("\n[machine] fill %s: %s after %lu ms — valves closed\n",
                  kPump[fillChannel & 1].who, fillOutcomeName(fillOutcome),
                  (unsigned long)fillElapsedMs);
    switch (fillOutcome) {
        case FILL_OUTCOME_DONE:
        case FILL_OUTCOME_FULL:    soundPlay(SND_CHIME); break;
        case FILL_OUTCOME_STOPPED: soundPlay(SND_ACK);   break;
        default:                   soundPlay(SND_FAULT); break;
    }
    fillAnnounce(millis());
}

static void fillService(uint32_t now) {
    if (state != ST_FILLING) return;
    if (fillParkAtMs) {
        if ((int32_t)(now - fillParkAtMs) >= 0) fillParked();
        return;
    }
    if (machineGasTripped()) { fillEnd(FILL_OUTCOME_GAS, now); return; }
    if (now - fillLastReedMs >= machine_policy::kFillReedPeriodMs) {
        fillLastReedMs = now;
        if (!fillReadReeds()) { fillEnd(FILL_OUTCOME_FAULT, now); return; }
    }
    switch (machine_policy::fillShouldEnd(fillElapsedNow(now), fillPlannedMs, fillReeds)) {
        case machine_policy::FillEnd::Full:    fillEnd(FILL_OUTCOME_FULL, now); break;
        case machine_policy::FillEnd::Planned: fillEnd(FILL_OUTCOME_DONE, now); break;
        case machine_policy::FillEnd::None:    break;
    }
}

bool machineFillBegin(uint8_t channel, uint32_t plannedMs) {
    const uint32_t now = millis();
    // A fill already drawing answers with itself; its channel is the refusal.
    if (state == ST_FILLING) { soundPlay(SND_REFUSE); fillAnnounce(now); return false; }

    uint8_t refusal = FILL_OUTCOME_NONE;
    if (channel > 1 || state != ST_IDLE)       refusal = FILL_OUTCOME_BUSY;
    else if (machineGasTripped())              refusal = FILL_OUTCOME_GAS;
    else if (!pcba::expanders().initialized()) refusal = FILL_OUTCOME_NO_IO;
    fillChannel   = channel & 1;
    fillPlannedMs = plannedMs ? plannedMs : machine_policy::kFillPlannedMs;
    fillElapsedMs = 0;
    fillReeds     = 0xFF;
    fillDrawing   = false;
    fillParkAtMs  = 0;
    if (refusal == FILL_OUTCOME_NONE && !fillReadReeds()) refusal = FILL_OUTCOME_FAULT;
    if (refusal == FILL_OUTCOME_NONE && (fillReeds & machine_policy::kReservoirReedFull))
        refusal = FILL_OUTCOME_FULL;   // nothing to draw into
    if (refusal != FILL_OUTCOME_NONE) {
        fillOutcome = refusal;
        Serial.printf("\n[machine] fill %s: %s\n", kPump[fillChannel].who, fillOutcomeName(refusal));
        soundPlay(SND_REFUSE);
        fillAnnounce(now);
        return false;
    }

    const machine_policy::ActuatorPlan plan =
        machine_policy::canonicalPlan(machine_policy::fillOperation(fillChannel));
    if (!machine_policy::isPlanSafe(plan, machine_policy::SafetyContext{false}) ||
        !pcba::expanders().apply(pcba::ExpanderOutputs(plan.valves, false))) {
        fillOutcome = FILL_OUTCOME_FAULT;
        Serial.printf("\n[machine] fill %s: the valves could not be opened — parked\n",
                      kPump[fillChannel].who);
        soundPlay(SND_FAULT);
        fillAnnounce(now);
        return false;
    }
    if (!pumpDrive(fillChannel)) {
        pcba::expanders().apply(pcba::ExpanderOutputs());
        fillOutcome = FILL_OUTCOME_BUSY;   // no LEDC channel free
        soundPlay(SND_REFUSE);
        fillAnnounce(now);
        return false;
    }

    fillStartMs    = now;
    fillLastReedMs = now;
    fillDrawing    = true;
    fillOutcome    = FILL_OUTCOME_NONE;
    state          = ST_FILLING;
    led(PIN_LED_ACT, true);
    char names[24];
    Serial.printf("\n[machine] fill %s: valves %s open, pump %s drawing for %lu ms "
                  "(IO%d -> %s.IN1 -> J13.%s), reeds %02X\n",
                  kPump[fillChannel].who, valveNames(plan.valves, names, sizeof(names)),
                  kPump[fillChannel].who, (unsigned long)fillPlannedMs, kPump[fillChannel].pin,
                  kPump[fillChannel].driver, kPump[fillChannel].j13, fillReeds);
    soundPlay(SND_ACK);
    fillAnnounce(now);
    return true;
}

void machineFillStop() {
    if (state == ST_FILLING) fillEnd(FILL_OUTCOME_STOPPED, millis());
}

bool machineIsFilling() { return state == ST_FILLING; }

void machineReadFillState(MachineFillState &st) {
    const uint32_t now = millis();
    st.phase     = state == ST_FILLING ? FILL_PHASE_RUNNING : FILL_PHASE_OFF;
    st.channel   = fillChannel;
    st.outcome   = state == ST_FILLING ? FILL_OUTCOME_NONE : fillOutcome;
    st.elapsedMs = fillElapsedNow(now);
    st.plannedMs = fillPlannedMs;
    st.reeds     = fillReeds;
}

uint16_t machineValvesOpen() { return pcba::expanders().currentOutputs().valves; }

// ── The clean cycle ───────────────────────────────────────────────────────
// One topology state at a time, kCleanRounds times over: the channel's
// tap-water fill — V-A, its select and its return open, pump off — until the
// full reed closes, then its flush — its draw and its flavor tube open, pump
// on — until the empty reed has opened and the tail has drawn the line clear.
// Every step ends at its planned time as well (machine_policy::clean*ShouldEnd).
// Between steps the pump stops, every valve closes, and nothing is energised
// for kCleanSettleMs.
static uint8_t  cleanChannel        = 0;
static uint8_t  cleanOutcome        = CLEAN_OUTCOME_NONE;
static uint8_t  cleanRounds         = machine_policy::kCleanRounds;
static uint8_t  cleanStepIndex      = 0;      // 0..2*rounds-1: even a water fill, odd a flush
static uint8_t  cleanReeds          = 0xFF;
static uint32_t cleanWaterPlannedMs = machine_policy::kCleanWaterFillPlannedMs;
static uint32_t cleanFlushPlannedMs = machine_policy::kCleanFlushPlannedMs;
static uint32_t cleanStepStartMs    = 0;
static uint32_t cleanStepPlannedMs  = 0;
static uint32_t cleanStepElapsedMs  = 0;      // final, once the step has ended
static uint32_t cleanLastReedMs     = 0;
static uint32_t cleanSettleAtMs     = 0;      // nonzero: the step is over, the valves close then
static uint8_t  cleanEndAfterSettle = CLEAN_OUTCOME_NONE;   // NONE: the next step follows the settle
static bool     cleanStepRunning    = false;
static bool     cleanPumpOn         = false;
static uint32_t cleanEmptyClosedAtMs = UINT32_MAX;   // elapsed when the empty reed was first seen closed

static machine_policy::CleanStep cleanStepOf(uint8_t index) {
    return (index & 1) ? machine_policy::CleanStep::Flush : machine_policy::CleanStep::WaterFill;
}

static uint32_t cleanStepElapsedNow(uint32_t now) {
    return cleanStepRunning ? now - cleanStepStartMs : cleanStepElapsedMs;
}

static void cleanFill(MachineCleanState &st, uint32_t now) {
    const bool running = state == ST_CLEANING;
    st.phase         = running ? CLEAN_PHASE_RUNNING : CLEAN_PHASE_OFF;
    st.channel       = cleanChannel;
    st.outcome       = running ? CLEAN_OUTCOME_NONE : cleanOutcome;
    st.step          = static_cast<uint8_t>(cleanStepOf(cleanStepIndex));
    st.round         = (uint8_t)(cleanStepIndex / 2 + 1);
    st.rounds        = cleanRounds;
    st.stepElapsedMs = cleanStepElapsedNow(now);
    st.stepPlannedMs = cleanStepPlannedMs;
    st.cycleLeftMs   = running
        ? machine_policy::cleanCycleLeftMs(cleanStepIndex, cleanRounds, st.stepElapsedMs,
                                           cleanStepPlannedMs, cleanWaterPlannedMs,
                                           cleanFlushPlannedMs)
        : 0;
    st.reeds         = cleanReeds;
}

static void cleanAnnounce(uint32_t now) {
    MachineCleanState st;
    cleanFill(st, now);
    if (machineOnCleanState) machineOnCleanState(st);
}

static const char *cleanOutcomeName(uint8_t outcome) {
    switch (outcome) {
        case CLEAN_OUTCOME_DONE:    return "every round ran";
        case CLEAN_OUTCOME_STOPPED: return "stopped on request";
        case CLEAN_OUTCOME_BUSY:    return "refused — busy";
        case CLEAN_OUTCOME_NO_IO:   return "refused — expanders unverified";
        case CLEAN_OUTCOME_FAULT:   return "fault — everything parked";
        case CLEAN_OUTCOME_GAS:     return "gas alarm";
        default:                    return "none";
    }
}

static const char *cleanStepName(uint8_t index) {
    return (index & 1) ? "flush" : "water fill";
}

static bool cleanReadReeds() {
    if (!readReeds()) return false;
    cleanReeds = reedMaskFor(cleanChannel);
    return true;
}

// The pump stops now; the valves close after the settle, from cleanService().
// NONE ends only the step; anything else ends the cycle once the settle is over.
static void cleanStepEnd(uint8_t cycleOutcome, uint32_t now) {
    if (state != ST_CLEANING) return;
    if (cleanSettleAtMs) {
        // Already settling between steps: the cycle ends there instead of going on.
        if (cleanEndAfterSettle == CLEAN_OUTCOME_NONE) cleanEndAfterSettle = cycleOutcome;
        return;
    }
    cleanStepElapsedMs = cleanStepElapsedNow(now);
    if (cleanPumpOn) pumpPark(cleanChannel);
    cleanPumpOn        = false;
    cleanStepRunning   = false;
    cleanEndAfterSettle = cycleOutcome;
    cleanSettleAtMs    = now + machine_policy::kCleanSettleMs;
    if (!cleanSettleAtMs) cleanSettleAtMs = 1;
}

// Everything off. The ending is announced from here, once nothing is energised.
static void cleanParked(uint8_t outcome) {
    if (!pcba::expanders().apply(pcba::ExpanderOutputs())) pcba::expanders().parkAll();
    cleanSettleAtMs = 0;
    cleanOutcome    = outcome;
    led(PIN_LED_ACT, false);
    state = ST_IDLE;
    Serial.printf("\n[machine] clean %s: %s in round %u of %u, %s — valves closed\n",
                  kPump[cleanChannel & 1].who, cleanOutcomeName(outcome),
                  (unsigned)(cleanStepIndex / 2 + 1), (unsigned)cleanRounds,
                  cleanStepName(cleanStepIndex));
    switch (outcome) {
        case CLEAN_OUTCOME_DONE:    soundPlay(SND_CHIME); break;
        case CLEAN_OUTCOME_STOPPED: soundPlay(SND_ACK);   break;
        default:                    soundPlay(SND_FAULT); break;
    }
    cleanAnnounce(millis());
}

// The next step's valves open and, for a flush, its pump starts. False parks
// everything and ends the cycle as a fault.
static bool cleanStepBegin(uint32_t now) {
    const machine_policy::CleanStep step = cleanStepOf(cleanStepIndex);
    const machine_policy::ActuatorPlan plan =
        machine_policy::canonicalPlan(machine_policy::cleanOperation(cleanChannel, step));
    if (!machine_policy::isPlanSafe(plan, machine_policy::SafetyContext{false}) ||
        !pcba::expanders().apply(pcba::ExpanderOutputs(plan.valves, false))) {
        Serial.printf("\n[machine] clean %s: the %s valves could not be opened — parked\n",
                      kPump[cleanChannel].who, cleanStepName(cleanStepIndex));
        cleanParked(CLEAN_OUTCOME_FAULT);
        return false;
    }
    if (plan.flavor_pumps && !pumpDrive(cleanChannel)) {
        Serial.printf("\n[machine] clean %s: pump %s would not start — parked\n",
                      kPump[cleanChannel].who, kPump[cleanChannel].who);
        cleanParked(CLEAN_OUTCOME_FAULT);
        return false;
    }
    cleanPumpOn          = plan.flavor_pumps != 0;
    cleanStepPlannedMs   = step == machine_policy::CleanStep::Flush ? cleanFlushPlannedMs
                                                                     : cleanWaterPlannedMs;
    cleanStepStartMs     = now;
    cleanStepElapsedMs   = 0;
    cleanLastReedMs      = now;
    cleanStepRunning     = true;
    cleanEmptyClosedAtMs = (cleanReeds != 0xFF) && (cleanReeds & machine_policy::kReservoirReedEmpty)
                               ? 0 : UINT32_MAX;
    char names[24];
    Serial.printf("\n[machine] clean %s: round %u of %u, %s — valves %s open, pump %s, "
                  "for %lu ms, reeds %02X\n",
                  kPump[cleanChannel].who, (unsigned)(cleanStepIndex / 2 + 1),
                  (unsigned)cleanRounds, cleanStepName(cleanStepIndex),
                  valveNames(plan.valves, names, sizeof(names)),
                  cleanPumpOn ? "on" : "off", (unsigned long)cleanStepPlannedMs, cleanReeds);
    cleanAnnounce(now);
    return true;
}

// The settle is over: every valve closes, and the cycle ends or the next step
// begins.
static void cleanSettled(uint32_t now) {
    cleanSettleAtMs = 0;
    if (!pcba::expanders().apply(pcba::ExpanderOutputs())) {
        pcba::expanders().parkAll();
        cleanParked(CLEAN_OUTCOME_FAULT);
        return;
    }
    if (cleanEndAfterSettle != CLEAN_OUTCOME_NONE) { cleanParked(cleanEndAfterSettle); return; }
    Serial.printf("\n[machine] clean %s: %s ended after %lu ms — valves closed\n",
                  kPump[cleanChannel].who, cleanStepName(cleanStepIndex),
                  (unsigned long)cleanStepElapsedMs);
    if (cleanStepIndex + 1 >= cleanRounds * 2) { cleanParked(CLEAN_OUTCOME_DONE); return; }
    cleanStepIndex++;
    cleanStepBegin(now);
}

static void cleanService(uint32_t now) {
    if (state != ST_CLEANING) return;
    if (cleanSettleAtMs) {
        if ((int32_t)(now - cleanSettleAtMs) >= 0) cleanSettled(now);
        return;
    }
    if (!cleanStepRunning) return;
    if (machineGasTripped()) { cleanStepEnd(CLEAN_OUTCOME_GAS, now); return; }
    const uint32_t elapsed = cleanStepElapsedNow(now);
    if (now - cleanLastReedMs >= machine_policy::kCleanReedPeriodMs) {
        cleanLastReedMs = now;
        if (!cleanReadReeds()) { cleanStepEnd(CLEAN_OUTCOME_FAULT, now); return; }
        if ((cleanReeds & machine_policy::kReservoirReedEmpty) && cleanEmptyClosedAtMs == UINT32_MAX)
            cleanEmptyClosedAtMs = elapsed;
    }
    machine_policy::CleanEnd end = machine_policy::CleanEnd::None;
    if (cleanStepOf(cleanStepIndex) == machine_policy::CleanStep::Flush) {
        end = machine_policy::cleanFlushShouldEnd(elapsed, cleanStepPlannedMs, cleanEmptyClosedAtMs);
    } else {
        end = machine_policy::cleanWaterFillShouldEnd(elapsed, cleanStepPlannedMs, cleanReeds);
    }
    if (end != machine_policy::CleanEnd::None) {
        Serial.printf("\n[machine] clean %s: %s %s\n", kPump[cleanChannel].who,
                      cleanStepName(cleanStepIndex),
                      end == machine_policy::CleanEnd::Reed ? "ended on its reed"
                                                            : "ran its planned time");
        cleanStepEnd(CLEAN_OUTCOME_NONE, now);
    }
}

bool machineCleanBegin(uint8_t channel, uint8_t rounds, uint32_t stepPlannedMs) {
    const uint32_t now = millis();
    // A cycle already running answers with itself; its channel is the refusal.
    if (state == ST_CLEANING) { soundPlay(SND_REFUSE); cleanAnnounce(now); return false; }

    uint8_t refusal = CLEAN_OUTCOME_NONE;
    if (channel > 1 || state != ST_IDLE)       refusal = CLEAN_OUTCOME_BUSY;
    else if (machineGasTripped())              refusal = CLEAN_OUTCOME_GAS;
    else if (!pcba::expanders().initialized()) refusal = CLEAN_OUTCOME_NO_IO;
    cleanChannel        = channel & 1;
    cleanRounds         = rounds ? rounds : machine_policy::kCleanRounds;
    cleanWaterPlannedMs = stepPlannedMs ? stepPlannedMs : machine_policy::kCleanWaterFillPlannedMs;
    cleanFlushPlannedMs = stepPlannedMs ? stepPlannedMs : machine_policy::kCleanFlushPlannedMs;
    cleanStepIndex      = 0;
    cleanStepPlannedMs  = cleanWaterPlannedMs;
    cleanStepElapsedMs  = 0;
    cleanReeds          = 0xFF;
    cleanStepRunning    = false;
    cleanPumpOn         = false;
    cleanSettleAtMs     = 0;
    cleanEndAfterSettle = CLEAN_OUTCOME_NONE;
    if (refusal == CLEAN_OUTCOME_NONE && !cleanReadReeds()) refusal = CLEAN_OUTCOME_FAULT;
    if (refusal != CLEAN_OUTCOME_NONE) {
        cleanOutcome = refusal;
        Serial.printf("\n[machine] clean %s: %s\n", kPump[cleanChannel].who, cleanOutcomeName(refusal));
        soundPlay(SND_REFUSE);
        cleanAnnounce(now);
        return false;
    }

    state = ST_CLEANING;
    led(PIN_LED_ACT, true);
    cleanOutcome = CLEAN_OUTCOME_NONE;
    Serial.printf("\n[machine] clean %s: %u round%s, water fill %lu ms and flush %lu ms each\n",
                  kPump[cleanChannel].who, (unsigned)cleanRounds, cleanRounds == 1 ? "" : "s",
                  (unsigned long)cleanWaterPlannedMs, (unsigned long)cleanFlushPlannedMs);
    if (!cleanStepBegin(now)) return false;
    soundPlay(SND_ACK);
    return true;
}

void machineCleanStop() {
    if (state == ST_CLEANING) cleanStepEnd(CLEAN_OUTCOME_STOPPED, millis());
}

bool machineIsCleaning() { return state == ST_CLEANING; }

void machineReadCleanState(MachineCleanState &st) { cleanFill(st, millis()); }

// ── The air cycles ────────────────────────────────────────────────────────
// The funnel open to air and a pump carrying it along the path, one topology
// state at a time (machine_policy::airOperation): Dry is In then Through on
// each channel in turn; Purge is In then Out on one. Every step runs its
// planned time; Out also ends on the empty reed plus the tail, the way a
// clean flush does. Between steps the pump stops and every valve is closed
// for kCleanSettleMs.
static uint8_t  airMode          = AIR_MODE_DRY;
static uint8_t  airChannel       = 0;     // the channel named on the request
static uint8_t  airOutcome       = AIR_OUTCOME_NONE;
static uint8_t  airStepIndex     = 0;
static uint8_t  airReeds         = 0xFF;
static uint32_t airStepCapMs     = 0;     // nonzero: the console's cap on every step
static uint32_t airStepStartMs   = 0;
static uint32_t airStepPlannedMs = 0;
static uint32_t airStepElapsedMs = 0;
static uint32_t airLastReedMs    = 0;
static uint32_t airSettleAtMs    = 0;
static uint8_t  airEndAfterSettle = AIR_OUTCOME_NONE;
static bool     airStepRunning   = false;
static bool     airPumpOn        = false;
static uint32_t airEmptyClosedAtMs = UINT32_MAX;

static machine_policy::AirMode airModeOf(uint8_t mode) {
    return mode == AIR_MODE_PURGE ? machine_policy::AirMode::Purge : machine_policy::AirMode::Dry;
}

static uint8_t airStepKind(uint8_t mode, uint8_t index) {
    if ((index & 1) == 0) return AIR_STEP_IN;
    return mode == AIR_MODE_PURGE ? AIR_STEP_OUT : AIR_STEP_THROUGH;
}

static const char *airStepName(uint8_t kind) {
    switch (kind) {
        case AIR_STEP_IN:      return "air in";
        case AIR_STEP_THROUGH: return "air through";
        default:               return "air out";
    }
}

static uint8_t airStepChannelNow() {
    return machine_policy::airStepChannel(airModeOf(airMode), airChannel, airStepIndex);
}

static uint32_t airStepElapsedNow(uint32_t now) {
    return airStepRunning ? now - airStepStartMs : airStepElapsedMs;
}

static uint32_t airPlannedFor(uint8_t index) {
    const uint32_t planned = machine_policy::airStepPlannedMs(airModeOf(airMode), index);
    return airStepCapMs && airStepCapMs < planned ? airStepCapMs : planned;
}

static void airFill(MachineAirState &st, uint32_t now) {
    const bool running = state == ST_AIRING;
    const machine_policy::AirMode m = airModeOf(airMode);
    st.phase         = running ? AIR_PHASE_RUNNING : AIR_PHASE_OFF;
    st.mode          = airMode;
    st.channel       = airStepChannelNow();
    st.outcome       = running ? AIR_OUTCOME_NONE : airOutcome;
    st.step          = airStepKind(airMode, airStepIndex);
    st.stepIndex     = airStepIndex;
    st.steps         = machine_policy::airSteps(m);
    st.stepElapsedMs = airStepElapsedNow(now);
    st.stepPlannedMs = airStepPlannedMs;
    // What is left counts every later step at its own planned time — capped
    // the way the running one is when the console named a cap.
    uint32_t left = 0;
    if (running) {
        left = st.stepElapsedMs >= airStepPlannedMs ? 0 : airStepPlannedMs - st.stepElapsedMs;
        for (uint8_t i = (uint8_t)(airStepIndex + 1); i < st.steps; i++) left += airPlannedFor(i);
    }
    st.cycleLeftMs   = left;
    st.reeds         = airReeds;
}

static void airAnnounce(uint32_t now) {
    MachineAirState st;
    airFill(st, now);
    if (machineOnAirState) machineOnAirState(st);
}

static const char *airOutcomeName(uint8_t outcome) {
    switch (outcome) {
        case AIR_OUTCOME_DONE:    return "every step ran";
        case AIR_OUTCOME_STOPPED: return "stopped on request";
        case AIR_OUTCOME_BUSY:    return "refused — busy";
        case AIR_OUTCOME_NO_IO:   return "refused — expanders unverified";
        case AIR_OUTCOME_FAULT:   return "fault — everything parked";
        case AIR_OUTCOME_GAS:     return "gas alarm";
        default:                  return "none";
    }
}

static bool airReadReeds() {
    if (!readReeds()) return false;
    airReeds = reedMaskFor(airStepChannelNow());
    return true;
}

static void airStepEnd(uint8_t cycleOutcome, uint32_t now) {
    if (state != ST_AIRING) return;
    if (airSettleAtMs) {
        if (airEndAfterSettle == AIR_OUTCOME_NONE) airEndAfterSettle = cycleOutcome;
        return;
    }
    airStepElapsedMs = airStepElapsedNow(now);
    if (airPumpOn) pumpPark(airStepChannelNow());
    airPumpOn         = false;
    airStepRunning    = false;
    airEndAfterSettle = cycleOutcome;
    airSettleAtMs     = now + machine_policy::kCleanSettleMs;
    if (!airSettleAtMs) airSettleAtMs = 1;
}

static void airParked(uint8_t outcome) {
    if (!pcba::expanders().apply(pcba::ExpanderOutputs())) pcba::expanders().parkAll();
    airSettleAtMs = 0;
    airOutcome    = outcome;
    led(PIN_LED_ACT, false);
    state = ST_IDLE;
    Serial.printf("\n[machine] %s: %s at step %u of %u, %s — valves closed\n",
                  airMode == AIR_MODE_PURGE ? "purge" : "dry", airOutcomeName(outcome),
                  (unsigned)(airStepIndex + 1),
                  (unsigned)machine_policy::airSteps(airModeOf(airMode)),
                  airStepName(airStepKind(airMode, airStepIndex)));
    switch (outcome) {
        case AIR_OUTCOME_DONE:    soundPlay(SND_CHIME); break;
        case AIR_OUTCOME_STOPPED: soundPlay(SND_ACK);   break;
        default:                  soundPlay(SND_FAULT); break;
    }
    airAnnounce(millis());
}

static bool airStepBegin(uint32_t now) {
    const machine_policy::AirMode m = airModeOf(airMode);
    const uint8_t ch = airStepChannelNow();
    const machine_policy::ActuatorPlan plan =
        machine_policy::canonicalPlan(machine_policy::airOperation(m, airChannel, airStepIndex));
    if (!machine_policy::isPlanSafe(plan, machine_policy::SafetyContext{false}) ||
        !pcba::expanders().apply(pcba::ExpanderOutputs(plan.valves, false))) {
        Serial.printf("\n[machine] %s: the valves could not be opened — parked\n",
                      airMode == AIR_MODE_PURGE ? "purge" : "dry");
        airParked(AIR_OUTCOME_FAULT);
        return false;
    }
    if (!pumpDrive(ch)) {
        Serial.printf("\n[machine] %s: pump %s would not start — parked\n",
                      airMode == AIR_MODE_PURGE ? "purge" : "dry", kPump[ch].who);
        airParked(AIR_OUTCOME_FAULT);
        return false;
    }
    airPumpOn          = true;
    airStepPlannedMs   = airPlannedFor(airStepIndex);
    airStepStartMs     = now;
    airStepElapsedMs   = 0;
    airLastReedMs      = now;
    airStepRunning     = true;
    airEmptyClosedAtMs = (airReeds != 0xFF) && (airReeds & machine_policy::kReservoirReedEmpty)
                             ? 0 : UINT32_MAX;
    char names[24];
    Serial.printf("\n[machine] %s: step %u of %u, %s on %s — valves %s open, pump %s on, for %lu ms, reeds %02X\n",
                  airMode == AIR_MODE_PURGE ? "purge" : "dry", (unsigned)(airStepIndex + 1),
                  (unsigned)machine_policy::airSteps(m), airStepName(airStepKind(airMode, airStepIndex)),
                  kPump[ch].who, valveNames(plan.valves, names, sizeof(names)), kPump[ch].who,
                  (unsigned long)airStepPlannedMs, airReeds);
    airAnnounce(now);
    return true;
}

static void airSettled(uint32_t now) {
    airSettleAtMs = 0;
    if (!pcba::expanders().apply(pcba::ExpanderOutputs())) {
        pcba::expanders().parkAll();
        airParked(AIR_OUTCOME_FAULT);
        return;
    }
    if (airEndAfterSettle != AIR_OUTCOME_NONE) { airParked(airEndAfterSettle); return; }
    Serial.printf("\n[machine] %s: %s ended after %lu ms — valves closed\n",
                  airMode == AIR_MODE_PURGE ? "purge" : "dry",
                  airStepName(airStepKind(airMode, airStepIndex)), (unsigned long)airStepElapsedMs);
    if (airStepIndex + 1 >= machine_policy::airSteps(airModeOf(airMode))) {
        airParked(AIR_OUTCOME_DONE);
        return;
    }
    airStepIndex++;
    airReeds = 0xFF;   // the next step may be the other channel's reservoir
    if (!airReadReeds()) { airParked(AIR_OUTCOME_FAULT); return; }
    airStepBegin(now);
}

static void airService(uint32_t now) {
    if (state != ST_AIRING) return;
    if (airSettleAtMs) {
        if ((int32_t)(now - airSettleAtMs) >= 0) airSettled(now);
        return;
    }
    if (!airStepRunning) return;
    if (machineGasTripped()) { airStepEnd(AIR_OUTCOME_GAS, now); return; }
    const uint32_t elapsed = airStepElapsedNow(now);
    if (now - airLastReedMs >= machine_policy::kCleanReedPeriodMs) {
        airLastReedMs = now;
        if (!airReadReeds()) { airStepEnd(AIR_OUTCOME_FAULT, now); return; }
        if ((airReeds & machine_policy::kReservoirReedEmpty) && airEmptyClosedAtMs == UINT32_MAX)
            airEmptyClosedAtMs = elapsed;
    }
    machine_policy::CleanEnd end = machine_policy::CleanEnd::None;
    if (machine_policy::airStepDrawsReservoir(airModeOf(airMode), airStepIndex)) {
        end = machine_policy::cleanFlushShouldEnd(elapsed, airStepPlannedMs, airEmptyClosedAtMs);
    } else if (elapsed >= airStepPlannedMs) {
        end = machine_policy::CleanEnd::Planned;
    }
    if (end != machine_policy::CleanEnd::None) {
        Serial.printf("\n[machine] %s: %s %s\n", airMode == AIR_MODE_PURGE ? "purge" : "dry",
                      airStepName(airStepKind(airMode, airStepIndex)),
                      end == machine_policy::CleanEnd::Reed ? "ended on its reed"
                                                            : "ran its planned time");
        airStepEnd(AIR_OUTCOME_NONE, now);
    }
}

bool machineAirBegin(uint8_t mode, uint8_t channel, uint32_t stepPlannedMs) {
    const uint32_t now = millis();
    if (state == ST_AIRING) { soundPlay(SND_REFUSE); airAnnounce(now); return false; }

    uint8_t refusal = AIR_OUTCOME_NONE;
    if (mode > AIR_MODE_PURGE || channel > 1 || state != ST_IDLE) refusal = AIR_OUTCOME_BUSY;
    else if (machineGasTripped())                                  refusal = AIR_OUTCOME_GAS;
    else if (!pcba::expanders().initialized())                     refusal = AIR_OUTCOME_NO_IO;
    airMode           = mode > AIR_MODE_PURGE ? AIR_MODE_DRY : mode;
    airChannel        = channel & 1;
    airStepCapMs      = stepPlannedMs;
    airStepIndex      = 0;
    airStepPlannedMs  = airPlannedFor(0);
    airStepElapsedMs  = 0;
    airReeds          = 0xFF;
    airStepRunning    = false;
    airPumpOn         = false;
    airSettleAtMs     = 0;
    airEndAfterSettle = AIR_OUTCOME_NONE;
    if (refusal == AIR_OUTCOME_NONE && !airReadReeds()) refusal = AIR_OUTCOME_FAULT;
    if (refusal != AIR_OUTCOME_NONE) {
        airOutcome = refusal;
        Serial.printf("\n[machine] %s: %s\n", airMode == AIR_MODE_PURGE ? "purge" : "dry",
                      airOutcomeName(refusal));
        soundPlay(SND_REFUSE);
        airAnnounce(now);
        return false;
    }

    state = ST_AIRING;
    led(PIN_LED_ACT, true);
    airOutcome = AIR_OUTCOME_NONE;
    Serial.printf("\n[machine] %s: %u steps, the funnel dry and open to air\n",
                  airMode == AIR_MODE_PURGE ? "purge" : "dry",
                  (unsigned)machine_policy::airSteps(airModeOf(airMode)));
    if (!airStepBegin(now)) return false;
    soundPlay(SND_ACK);
    return true;
}

void machineAirStop() {
    if (state == ST_AIRING) airStepEnd(AIR_OUTCOME_STOPPED, millis());
}

bool machineIsAiring() { return state == ST_AIRING; }

void machineReadAirState(MachineAirState &st) { airFill(st, millis()); }

// ── The pour ──────────────────────────────────────────────────────────────
// The meter's falling edges are counted on IO25; every kFlowSampleMs the
// count is a flow reading for machine_policy::Pour, which says when the
// selected channel's dispense path opens, when its pump bursts, and when the
// path closes again. The bench can pretend a reading for a while.
static volatile uint32_t flowEdges = 0;
static uint32_t flowSampleMs   = 0;
static uint32_t flowTotal      = 0;
static uint32_t flowSimPulses  = 0;
static uint32_t flowSimUntilMs = 0;
static machine_policy::Pour pour;
static uint8_t  pourChannel = 0;
static uint32_t pourCycles  = 0;
static uint32_t pourStartMs = 0;

static void IRAM_ATTR flowIsr() { flowEdges++; }

static const char *pourActionName(machine_policy::PourAction a) {
    switch (a) {
        case machine_policy::PourAction::Start:   return "start";
        case machine_policy::PourAction::PumpOn:  return "burst";
        case machine_policy::PourAction::PumpOff: return "rest";
        case machine_policy::PourAction::Stop:    return "stop";
        case machine_policy::PourAction::Ceiling: return "ceiling";
        default:                                  return "none";
    }
}

static void pourClose(const char *how) {
    if (pour.pumpOn() || state == ST_POURING) pumpPark(pourChannel);
    if (!pcba::expanders().apply(pcba::ExpanderOutputs())) pcba::expanders().parkAll();
    led(PIN_LED_ACT, false);
    state = ST_IDLE;
    Serial.printf("\n[machine] pour %s: %s after %lu ms, %lu bursts — valves closed\n",
                  kPump[pourChannel].who, how, (unsigned long)(millis() - pourStartMs),
                  (unsigned long)pourCycles);
}

static void pourService(uint32_t now) {
    if (now - flowSampleMs >= machine_policy::kFlowSampleMs) {
        flowSampleMs = now;
        noInterrupts();
        uint32_t n = flowEdges;
        flowEdges = 0;
        interrupts();
        flowTotal += n;
        if (flowSimUntilMs) {
            if ((int32_t)(now - flowSimUntilMs) < 0) n = flowSimPulses;
            else flowSimUntilMs = 0;
        }
        pour.sample(n);
    }
    if (state != ST_IDLE && state != ST_POURING) { pour.reset(); return; }
    if (state == ST_IDLE && (machineGasTripped() || !pcba::expanders().initialized())) {
        pour.reset();
        return;
    }
    if (state == ST_POURING && machineGasTripped()) {
        pour.reset();
        pourClose("gas alarm");
        return;
    }
    const uint8_t ratio = flavorRatio(state == ST_POURING ? pourChannel : flavorSelected());
    const machine_policy::PourAction action = pour.service(now, ratio);
    switch (action) {
        case machine_policy::PourAction::Start: {
            pourChannel = flavorSelected() & 1;
            const machine_policy::ActuatorPlan plan = machine_policy::canonicalPlan(
                pourChannel == 0 ? machine_policy::Operation::DispenseA
                                 : machine_policy::Operation::DispenseB);
            if (!machine_policy::isPlanSafe(plan, machine_policy::SafetyContext{false}) ||
                !pcba::expanders().apply(pcba::ExpanderOutputs(plan.valves, false)) ||
                !pumpDrive(pourChannel)) {
                pcba::expanders().apply(pcba::ExpanderOutputs());
                pour.reset();
                Serial.printf("\n[machine] pour %s: the path could not be opened — parked\n",
                              kPump[pourChannel].who);
                soundPlay(SND_FAULT);
                return;
            }
            pourStartMs = now;
            pourCycles  = 1;
            state = ST_POURING;
            led(PIN_LED_ACT, true);
            char names[24];
            Serial.printf("\n[machine] pour %s at 1:%u: valves %s open, pump %s bursting %lu on / %lu off\n",
                          kPump[pourChannel].who, ratio, valveNames(plan.valves, names, sizeof(names)),
                          kPump[pourChannel].who, (unsigned long)pour.onMs(), (unsigned long)pour.offMs());
            break;
        }
        case machine_policy::PourAction::PumpOn:
            if (state != ST_POURING) { pour.reset(); return; }
            if (!pumpDrive(pourChannel)) { pour.reset(); pourClose("the pump would not start"); return; }
            pourCycles++;
            break;
        case machine_policy::PourAction::PumpOff:
            if (state == ST_POURING) pumpPark(pourChannel);
            break;
        case machine_policy::PourAction::Stop:
            if (state == ST_POURING) pourClose("flow stopped");
            break;
        case machine_policy::PourAction::Ceiling:
            if (state == ST_POURING) { pourClose("the meter never stopped"); soundPlay(SND_FAULT); }
            break;
        case machine_policy::PourAction::None:
            break;
    }
    (void)pourActionName;
}

bool machineIsPouring()          { return state == ST_POURING; }
bool machineDispenseWindowOpen() { return state == ST_POURING; }
uint32_t machinePourCycles()     { return pourCycles; }
uint32_t machineFlowPulsesTotal() { return flowTotal; }

void machineFlowSimulate(uint32_t pulses, uint32_t ms) {
    flowSimPulses  = pulses;
    flowSimUntilMs = ms ? millis() + ms : 0;
    if (ms && !flowSimUntilMs) flowSimUntilMs = 1;
}

// What the running operation is doing to a reservoir's level: a fill or a
// clean water fill raises it, a flush or a purge's Out step draws it down,
// and nothing else moves it.
static machine_policy::LevelMotion levelMotionFor(uint8_t channel) {
    using machine_policy::LevelMotion;
    switch (state) {
        case ST_FILLING:
            return fillChannel == channel ? LevelMotion::Rising : LevelMotion::Still;
        case ST_CLEANING:
            if (cleanChannel != channel || !cleanStepRunning) return LevelMotion::Still;
            return cleanStepOf(cleanStepIndex) == machine_policy::CleanStep::Flush
                       ? LevelMotion::Falling : LevelMotion::Rising;
        case ST_AIRING:
            if (!airStepRunning || airStepChannelNow() != channel) return LevelMotion::Still;
            return machine_policy::airStepDrawsReservoir(airModeOf(airMode), airStepIndex)
                       ? LevelMotion::Falling : LevelMotion::Still;
        case ST_POURING:
            return pourChannel == channel ? LevelMotion::Falling : LevelMotion::Still;
        default:
            return LevelMotion::Still;
    }
}

// ── The self-test ─────────────────────────────────────────────────────────
// One load at a time, each parked and read back before the next: V-A through
// V-K for a quarter second each, the condenser fan for a second, pump A and
// pump B for a second each. Fourteen steps, a quarter-second gap between them.
static const uint32_t kSelfTestValveMs = 250;
static const uint32_t kSelfTestGapMs   = 250;
static const uint32_t kSelfTestFanMs   = 1000;
static const uint32_t kSelfTestPumpMs  = 1000;
static const uint8_t  kSelfTestSteps   = machine_policy::kValveCount + 3;
static uint8_t  selfTestStep    = 0;
static uint32_t selfTestPhaseMs = 0;
static bool     selfTestStarted = false;   // the first step has been driven
static bool     selfTestOn      = false;   // the step's load is energised; else in its gap
static uint8_t  selfTestFailed  = 0;       // steps that did not take

static const char *selfTestStepName(uint8_t step, char *buf, size_t n) {
    if (step < machine_policy::kValveCount) snprintf(buf, n, "V-%c", 'A' + step);
    else if (step == machine_policy::kValveCount) snprintf(buf, n, "condenser fan");
    else snprintf(buf, n, "pump %s", kPump[(step - machine_policy::kValveCount - 1) & 1].who);
    return buf;
}

static uint32_t selfTestOnMs(uint8_t step) {
    if (step < machine_policy::kValveCount) return kSelfTestValveMs;
    if (step == machine_policy::kValveCount) return kSelfTestFanMs;
    return kSelfTestPumpMs;
}

// Drives step's load. False when the expanders would not take it or the pump
// would not start; the load is parked either way.
static bool selfTestDrive(uint8_t step) {
    if (step < machine_policy::kValveCount) {
        const machine_policy::ValveMask v = machine_policy::valveBit(static_cast<machine_policy::Valve>(step));
        return pcba::expanders().apply(pcba::ExpanderOutputs(v, false));
    }
    if (step == machine_policy::kValveCount)
        return pcba::expanders().apply(pcba::ExpanderOutputs(0, true));
    return pumpDrive((step - machine_policy::kValveCount - 1) & 1);
}

static void selfTestParkStep(uint8_t step) {
    if (step > machine_policy::kValveCount) pumpPark((step - machine_policy::kValveCount - 1) & 1);
    else if (!pcba::expanders().apply(pcba::ExpanderOutputs())) pcba::expanders().parkAll();
}

static void selfTestEnd(const char *how) {
    if (!pcba::expanders().apply(pcba::ExpanderOutputs())) pcba::expanders().parkAll();
    led(PIN_LED_ACT, false);
    state = ST_IDLE;
    Serial.printf("\n[machine] self-test %s: %u of %u steps took, %u did not — everything parked\n",
                  how, (unsigned)(kSelfTestSteps - selfTestFailed), (unsigned)kSelfTestSteps,
                  (unsigned)selfTestFailed);
    soundPlay(selfTestFailed ? SND_FAULT : SND_CHIME);
}

static void selfTestService(uint32_t now) {
    if (state != ST_SELFTEST) return;
    if (machineGasTripped()) {
        if (selfTestOn) selfTestParkStep(selfTestStep);
        selfTestEnd("stopped by the gas alarm");
        return;
    }
    char name[16];
    if (selfTestOn) {
        if (now - selfTestPhaseMs < selfTestOnMs(selfTestStep)) return;
        selfTestParkStep(selfTestStep);
        selfTestOn = false;
        selfTestPhaseMs = now;
        Serial.printf("[machine] self-test: %s released\n", selfTestStepName(selfTestStep, name, sizeof(name)));
        return;
    }
    // In the gap after a step, or at the very start.
    if (selfTestStarted) {
        if (now - selfTestPhaseMs < kSelfTestGapMs) return;
        if (selfTestStep + 1 >= kSelfTestSteps) { selfTestEnd("complete"); return; }
        selfTestStep++;
    }
    selfTestStarted = true;
    if (selfTestDrive(selfTestStep)) {
        selfTestOn = true;
        Serial.printf("[machine] self-test: %s driven for %lu ms\n",
                      selfTestStepName(selfTestStep, name, sizeof(name)),
                      (unsigned long)selfTestOnMs(selfTestStep));
    } else {
        selfTestFailed++;
        selfTestOn = false;
        Serial.printf("[machine] self-test: %s DID NOT TAKE (%s)\n",
                      selfTestStepName(selfTestStep, name, sizeof(name)),
                      machineIoFaultName(static_cast<uint8_t>(pcba::expanders().lastFault())));
        if (!pcba::expanders().initialized()) { selfTestEnd("stopped — the expanders fell out"); return; }
    }
    selfTestPhaseMs = now;
}

bool machineSelfTestBegin() {
    if (state != ST_IDLE || machineGasTripped() || !pcba::expanders().initialized()) {
        soundPlay(SND_REFUSE);
        return false;
    }
    selfTestStep    = 0;
    selfTestPhaseMs = 0;
    selfTestStarted = false;
    selfTestOn      = false;
    selfTestFailed  = 0;
    state = ST_SELFTEST;
    led(PIN_LED_ACT, true);
    Serial.printf("\n[machine] self-test: %u solenoids, the fan, both pumps — one at a time\n",
                  (unsigned)machine_policy::kValveCount);
    soundPlay(SND_ACK);
    selfTestService(millis());
    return true;
}

void machineSelfTestStop() {
    if (state != ST_SELFTEST) return;
    if (selfTestOn) selfTestParkStep(selfTestStep);
    selfTestEnd("stopped on request");
}

// ── Setup and service ─────────────────────────────────────────────────────
void machineBegin() {
    soundBegin(PIN_BUZZ);   // the coil is parked before anything else runs
    for (int pin : kActuators) pinMode(pin, INPUT);
    parkStraps();
    pinMode(PIN_LED_ACT, OUTPUT);
    led(PIN_LED_ACT, false);
    pumpTimer.stop();
    primeSession = machine_policy::PrimeSession();
    primeRunUsesSession = false;
    primeEventUsesSession = false;
    fillDrawing  = false;
    fillParkAtMs = 0;
    fillOutcome  = FILL_OUTCOME_NONE;
    fillReeds    = 0xFF;
    cleanStepRunning = false;
    cleanPumpOn      = false;
    cleanSettleAtMs  = 0;
    cleanOutcome     = CLEAN_OUTCOME_NONE;
    cleanReeds       = 0xFF;
    airStepRunning   = false;
    airPumpOn        = false;
    airSettleAtMs    = 0;
    airOutcome       = AIR_OUTCOME_NONE;
    airReeds         = 0xFF;
    state = ST_IDLE;

    // The MCPs keep their register state across an ESP-only reset because
    // their /RESET pins are tied high. Clear every latch and prove each output
    // pin low before enabling reed pull-ups or allowing setup to finish.
    if (!pcba::expanders().begin()) {
        pinMode(PIN_LED_ERR, OUTPUT);
        led(PIN_LED_ERR, true);
    }

    // The flow meter: open-collector into the internal pull-up, one falling
    // edge per impeller pulse.
    pour.reset();
    pinMode(PIN_FLOW, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(PIN_FLOW), flowIsr, FALLING);
    flowSampleMs = millis();
}

static void primeSessionLeaseService(uint32_t now) {
    if (!primeSession.leaseExpired(now)) return;

    const machine_policy::PrimeSessionSnapshot snapshot = primeSession.snapshot();
    const uint32_t elapsed = snapshot.phase == machine_policy::PrimeSessionPhase::Running
        ? pumpTimer.elapsedMs(now)
        : snapshot.elapsed_ms;
    if (!primeSession.cancel(snapshot.session_token,
                             machine_policy::PrimeSessionOutcome::LeaseExpired,
                             elapsed)) return;

    // A ready session expiring drives nothing. If a source was holding, park it
    // through the normal timeout path so the existing fault sound, response,
    // callbacks, and release ordering remain intact while session truth stays OFF.
    if (snapshot.phase == machine_policy::PrimeSessionPhase::Running &&
        state == ST_PUMPING && hold == HOLD_PRIME) {
        endPumping(PRIME_TIMEOUT, elapsed);
    }
}

void machineService() {
    heartbeat();
    gasService();
    const uint32_t now = millis();
    primeSessionLeaseService(now);
    fillService(now);
    cleanService(now);
    airService(now);
    selfTestService(now);
    pourService(now);
    reedIdleService(now);
    if (state != ST_PUMPING) return;

    const uint32_t elapsed = pumpTimer.elapsedMs(now);
    if (hold == HOLD_PRIME) {
        if (now - lastHoldNoteMs >= HOLD_NOTE_MS) {
            lastHoldNoteMs = now;
            holdNote(elapsed);
        }
    }

    // The hold is a heartbeat: a finger that lifts sends MSG_PRIME_STOP; a
    // display that crashes, unplugs, or loses the pair sends nothing. The head
    // stops either way. PumpTimer keeps these comparisons rollover-safe and
    // deliberately gives a stale tick priority over the hard ceiling.
    switch (pumpTimer.service(now)) {
        case machine_policy::PumpStopReason::TickTimeout:
            endPumping(PRIME_TIMEOUT, elapsed);
            break;
        case machine_policy::PumpStopReason::Ceiling:
            endPumping(PRIME_LIMIT, elapsed);
            break;
        case machine_policy::PumpStopReason::BoundedComplete:
            endPumping(PRIME_STOPPED, elapsed);
            break;
        case machine_policy::PumpStopReason::None:
        case machine_policy::PumpStopReason::Requested:
            break;
    }
}

// ── Intents ───────────────────────────────────────────────────────────────
static bool claimPump(uint8_t channel, PumpHold why, uint32_t requestedMs = 0,
                      uint32_t *acceptedMs = nullptr) {
    if (channel > 1)         return false;
    if (state != ST_IDLE)    return false;   // one operation at a time is the interlock
    if (!pumpDrive(channel)) return false;   // no LEDC channel free

    const uint32_t now = millis();
    if (why == HOLD_PRIME) {
        pumpTimer.beginPrime(now);
    } else {
        const uint32_t accepted = pumpTimer.beginBounded(now, requestedMs);
        if (acceptedMs) *acceptedMs = accepted;
    }
    hold       = why;
    channelNow = channel;
    state      = ST_PUMPING;
    led(PIN_LED_ACT, true);
    return true;
}

static bool beginPrimePump(
    uint8_t channel,
    machine_policy::PrimeSessionOwner owner = machine_policy::PrimeSessionOwner::None,
    uint32_t holdToken = 0) {
    if (!claimPump(channel, HOLD_PRIME)) {
        if (owner != machine_policy::PrimeSessionOwner::None)
            primeSession.pumpRefused(holdToken);
        soundPlay(SND_REFUSE);
        primeEventUsesSession = owner != machine_policy::PrimeSessionOwner::None;
        announce(PRIME_REFUSED, channel, 0);
        primeEventUsesSession = false;
        return false;
    }
    primeRunUsesSession = owner != machine_policy::PrimeSessionOwner::None;
    if (owner != machine_policy::PrimeSessionOwner::None)
        primeSession.pumpStarted(owner, holdToken);
    soundPlay(SND_ENGAGE);           // the pad took — richer than a tick, and specific to a hold
    lastHoldNoteMs = millis();       // the first reading is a second in, not immediately
    Serial.printf("\n[machine] prime %s at full (IO%d -> %s.IN1 -> J13.%s)\n",
                  kPump[channel].who, kPump[channel].pin, kPump[channel].driver, kPump[channel].j13);
    primeEventUsesSession = primeRunUsesSession;
    if (machineOnPrimeState) machineOnPrimeState(PRIME_RUNNING, channel, 0);
    primeEventUsesSession = false;
    return true;
}

bool machinePrimeBegin(uint8_t channel) {
    return beginPrimePump(channel);
}

void machinePrimeTick(uint8_t channel) {
    if (state == ST_PUMPING && hold == HOLD_PRIME && channel == channelNow) {
        pumpTimer.primeTick(millis());
    }
}

void machinePrimeEnd() {
    if (state == ST_PUMPING && hold == HOLD_PRIME) endPumping(PRIME_STOPPED);
}

bool machinePrimeSessionActivate(uint8_t channel, uint32_t sessionToken) {
    return primeSession.activate(channel, sessionToken, millis());
}

bool machinePrimeSessionQuery(uint32_t sessionToken) {
    return primeSession.query(sessionToken, millis());
}

bool machinePrimeSessionCancel(uint32_t sessionToken,
                               bool tombstonePendingActivation) {
    const machine_policy::PrimeSessionSnapshot snapshot = primeSession.snapshot();
    const uint32_t elapsed = snapshot.phase == machine_policy::PrimeSessionPhase::Running
        ? pumpTimer.elapsedMs(millis())
        : snapshot.elapsed_ms;
    if (!primeSession.cancel(sessionToken,
                             machine_policy::PrimeSessionOutcome::Canceled,
                             elapsed,
                             tombstonePendingActivation)) return false;

    if (snapshot.phase == machine_policy::PrimeSessionPhase::Running &&
        state == ST_PUMPING && hold == HOLD_PRIME) {
        endPumping(PRIME_STOPPED, elapsed);
    }
    return true;
}

bool machinePrimeSessionHoldBegin(MachinePrimeSource source,
                                  uint8_t channel,
                                  uint32_t sessionToken,
                                  uint32_t holdToken) {
    const machine_policy::PrimeSessionOwner owner = primeOwner(source);
    switch (primeSession.holdStart(owner, channel, sessionToken, holdToken, millis())) {
        case machine_policy::PrimeHoldDecision::StartPump:
            return beginPrimePump(channel, owner, holdToken);
        case machine_policy::PrimeHoldDecision::RefreshPump:
            machinePrimeTick(channel);
            return true;
        case machine_policy::PrimeHoldDecision::Ignore:
        case machine_policy::PrimeHoldDecision::StopPump:
        case machine_policy::PrimeHoldDecision::RecordStopped:
            return false;
    }
    return false;
}

bool machinePrimeSessionHoldTick(MachinePrimeSource source,
                                 uint8_t channel,
                                 uint32_t sessionToken,
                                 uint32_t holdToken) {
    if (primeSession.holdTick(primeOwner(source), channel, sessionToken,
                              holdToken, millis()) !=
        machine_policy::PrimeHoldDecision::RefreshPump) return false;
    machinePrimeTick(channel);
    return true;
}

bool machinePrimeSessionHoldEnd(MachinePrimeSource source,
                                uint8_t channel,
                                uint32_t sessionToken,
                                uint32_t holdToken) {
    const machine_policy::PrimeHoldDecision decision = primeSession.holdStop(
        primeOwner(source), channel, sessionToken, holdToken, millis());
    if (decision == machine_policy::PrimeHoldDecision::StopPump) {
        machinePrimeEnd();
        return true;
    }
    return decision == machine_policy::PrimeHoldDecision::RecordStopped;
}

void machinePrimeSessionSourceDisconnected(MachinePrimeSource source) {
    if (!primeSession.runningOwnedBy(primeOwner(source))) return;
    if (state == ST_PUMPING && hold == HOLD_PRIME) {
        endPumping(PRIME_TIMEOUT);
    } else {
        primeSession.pumpStopped(machine_policy::PrimeSessionOutcome::Timeout, 0);
    }
}

void machineReadPrimeSessionState(MachinePrimeSessionState &session) {
    const machine_policy::PrimeSessionSnapshot &snapshot = primeSession.snapshot();
    session.phase = static_cast<uint8_t>(snapshot.phase);
    session.channel = snapshot.channel;
    session.owner = static_cast<uint8_t>(snapshot.owner);
    session.outcome = static_cast<uint8_t>(snapshot.outcome);
    session.elapsedMs = snapshot.phase == machine_policy::PrimeSessionPhase::Running
        ? pumpTimer.elapsedMs(millis())
        : snapshot.elapsed_ms;
    session.revision = snapshot.revision;
    session.sessionToken = snapshot.session_token;
    session.holdToken = snapshot.hold_token;
}

bool machinePrimeEventIsSessionOwned() { return primeEventUsesSession; }

bool machinePumpRun(uint8_t channel, uint32_t ms) {
    uint32_t acceptedMs = 0;
    if (!claimPump(channel, HOLD_TIMED, ms, &acceptedMs)) {
        soundPlay(SND_REFUSE);
        return false;
    }
    Serial.printf("\n[machine] pump %s at full for %lu ms (IO%d -> %s.IN1 -> J13.%s)\n",
                  kPump[channel].who, (unsigned long)acceptedMs, kPump[channel].pin,
                  kPump[channel].driver, kPump[channel].j13);
    return true;
}

void machineStop() {
    if      (state == ST_FILLING)  machineFillStop();
    else if (state == ST_CLEANING) machineCleanStop();
    else if (state == ST_AIRING)   machineAirStop();
    else if (state == ST_SELFTEST) machineSelfTestStop();
    else if (state == ST_POURING)  { pour.reset(); flowSimUntilMs = 0; pourClose("stopped on request"); }
    else                           endPumping(PRIME_STOPPED);
}

MachineState machineState()     { return state; }
const char  *machineStateName() {
    switch (state) {
        case ST_PUMPING:  return "pumping";
        case ST_FILLING:  return "filling";
        case ST_CLEANING: return "cleaning";
        case ST_AIRING:   return airMode == AIR_MODE_PURGE ? "purging" : "drying";
        case ST_SELFTEST: return "self-test";
        case ST_POURING:  return "pouring";
        default:          return "idle";
    }
}
bool         machineIsPriming() { return state == ST_PUMPING && hold == HOLD_PRIME; }
uint8_t      machinePumpChannel()   {
    switch (state) {
        case ST_FILLING:  return fillChannel;
        case ST_CLEANING: return cleanChannel;
        case ST_AIRING:   return airStepChannelNow();
        case ST_POURING:  return pourChannel;
        default:          return channelNow;
    }
}
uint32_t     machinePumpElapsedMs() {
    return state == ST_PUMPING ? pumpTimer.elapsedMs(millis()) : 0;
}
const char  *machinePumpName(uint8_t channel) { return kPump[channel & 1].who; }
