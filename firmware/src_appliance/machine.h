#pragma once

#include <stdint.h>

// ════════════════════════════════════════════════════════════
//  The machine — every actuator on the main board, behind one door
// ════════════════════════════════════════════════════════════
//
// machine.cpp is the only file that drives a pin reaching a load. The glass,
// the serial console, and the faucet when it exists all ask for a thing here,
// and the three limits in main.cpp's header are held here.
//
// A hold from the glass draws from its reservoir through the dispense valves;
// a bounded console motor check drives only its pump. The funnel fill, clean
// cycle, two air cycles, flow-meter pour, and commissioning self-test run here
// too. The self-test walks every solenoid, the fan and both pumps one at a time.
// The two MCP23017s are initialized fail-closed: every output is parked low and
// the reed inputs have internal pull-ups. Both relays are driven from here:
// relay #1 by the cold loop against the two 1-wire probes, relay #2 by the
// refill against the carbonator's two reeds and the dispense window.

enum MachineState : uint8_t {
    ST_IDLE,      // nothing driven
    ST_PUMPING,   // a wet held prime or a bounded console motor check
    ST_FILLING,   // a funnel fill: three valves open, that channel's pump drawing
    ST_CLEANING,  // a clean cycle: one topology state at a time, the pump on for the funnel and the flushes
    ST_AIRING,    // an air cycle: the funnel open to air, a pump carrying it along the path
    ST_SELFTEST,  // the commissioning walk: one load at a time, briefly
    ST_POURING,   // carbonated water is flowing: the selected channel's dispense path open, its pump on a duty cycle
    ST_REFILLING, // the carbonator is drawing: V-K open, relay #2 closed on the G Ganen
};

// Why the pump is turning, which is the same as what will stop it.
enum PumpHold : uint8_t {
    HOLD_PRIME,  // a finger on the glass — a stale tick or the ceiling ends it
    HOLD_TIMED,  // a bounded run — its own deadline ends it
};

// Physical link identity is supplied by link.cpp / faucet_link.cpp and never
// accepted from a display payload.
enum MachinePrimeSource : uint8_t {
    MACHINE_PRIME_ENCLOSURE = 1,
    MACHINE_PRIME_FAUCET    = 2,
};

struct MachinePrimeSessionState {
    uint8_t phase;
    uint8_t channel;
    uint8_t owner;
    uint8_t outcome;
    uint32_t elapsedMs;
    uint32_t revision;
    uint32_t sessionToken;
    uint32_t holdToken;
};

// The funnel fill, in proto_msg.h's FILL_* vocabulary.
struct MachineFillState {
    uint8_t  phase;
    uint8_t  channel;
    uint8_t  outcome;
    uint32_t elapsedMs;
    uint32_t plannedMs;
    uint8_t  reeds;
};

// The clean cycle, in proto_msg.h's CLEAN_* vocabulary.
struct MachineCleanState {
    uint8_t  phase;
    uint8_t  channel;
    uint8_t  outcome;
    uint8_t  step;
    uint8_t  round;
    uint8_t  rounds;
    uint32_t stepElapsedMs;
    uint32_t stepPlannedMs;
    uint32_t cycleLeftMs;
    uint8_t  reeds;
};

// ── What the machine announces ────────────────────────────────────────────
// Every prime state change, in proto_msg.h's PRIME_* vocabulary. link.cpp turns
// these into MSG_RESP_PRIME. Set before machineBegin().
extern void (*machineOnPrimeState)(uint8_t state, uint8_t channel, uint32_t ms);

// Every fill state change — accepted, refused, ended and why. link.cpp turns
// these into MSG_RESP_FILL.
extern void (*machineOnFillState)(const MachineFillState &state);

// Every clean state change — accepted, refused, each step begun, ended and
// why. link.cpp turns these into MSG_RESP_CLEAN.
extern void (*machineOnCleanState)(const MachineCleanState &state);

// An air cycle, in proto_msg.h's AIR_* vocabulary.
struct MachineAirState {
    uint8_t  phase;
    uint8_t  mode;
    uint8_t  channel;
    uint8_t  outcome;
    uint8_t  step;
    uint8_t  stepIndex;
    uint8_t  steps;
    uint32_t stepElapsedMs;
    uint32_t stepPlannedMs;
    uint32_t cycleLeftMs;
    uint8_t  reeds;
};

// Every air state change. link.cpp turns these into MSG_RESP_AIR.
extern void (*machineOnAirState)(const MachineAirState &state);

// A bounded run reaching its deadline, so MSG_RESP_PUMP_DONE goes out when the
// head has already stopped rather than when the run was asked for.
extern void (*machineOnPumpDone)(uint8_t channel);

void machineBegin();
void machineService();   // call every loop; the deadlines are read here

// ── Intents ───────────────────────────────────────────────────────────────
// Each answers whether the machine took it. A refusal is announced too, so a
// caller that only listens still learns what happened.
// Prime opens the selected reservoir's dispense pair before running its pump;
// every ending stops the pump before closing the valves. Unverified I/O, a
// gas alarm, or a busy machine refuse a hold; an I/O fault or gas trip ends it.
bool machinePrimeBegin(uint8_t channel);
void machinePrimeTick(uint8_t channel);
void machinePrimeEnd();

// Main-board-owned prime-ready session. The enclosure activates and leases it;
// either endpoint may own one tokenized hold, and either may cancel it. Every
// command is absolute and stale source/session/hold tokens are harmless.
bool machinePrimeSessionActivate(uint8_t channel, uint32_t sessionToken);
bool machinePrimeSessionQuery(uint32_t sessionToken);
// Only J9 may tombstone an activation token while OFF: the enclosure is the
// sole endpoint permitted to create a prime session. Faucet CANCEL is limited
// to the currently authoritative session.
bool machinePrimeSessionCancel(uint32_t sessionToken,
                               bool tombstonePendingActivation = false);
bool machinePrimeSessionHoldBegin(MachinePrimeSource source,
                                  uint8_t channel,
                                  uint32_t sessionToken,
                                  uint32_t holdToken);
bool machinePrimeSessionHoldTick(MachinePrimeSource source,
                                 uint8_t channel,
                                 uint32_t sessionToken,
                                 uint32_t holdToken);
bool machinePrimeSessionHoldEnd(MachinePrimeSource source,
                                uint8_t channel,
                                uint32_t sessionToken,
                                uint32_t holdToken);
void machinePrimeSessionSourceDisconnected(MachinePrimeSource source);
void machineReadPrimeSessionState(MachinePrimeSessionState &session);
// Valid only while machineOnPrimeState is being invoked; lets the transport
// retain legacy replies for legacy commands without double-answering a
// tokenized session action that carries its own authoritative state.
bool machinePrimeEventIsSessionOwned();

bool machinePumpRun(uint8_t channel, uint32_t ms);
void machineStop();      // whatever is running, end it and park

// ── The funnel fill ───────────────────────────────────────────────────────
// Opens the channel's funnel path and draws for machine_policy::kFillPlannedMs
// — or plannedMs, when the console names one — unless the reservoir's full
// reed closes first. Refused while anything else runs, while the expanders are
// unverified, and under the gas alarm; every answer, and every ending, goes
// out through machineOnFillState.
bool machineFillBegin(uint8_t channel, uint32_t plannedMs = 0);
void machineFillStop();   // ends a running fill on request; nothing otherwise
bool machineIsFilling();
void machineReadFillState(MachineFillState &state);
uint16_t machineValvesOpen();   // the logical valves the expanders hold open, bit 0 = V-A

// ── The clean cycle ───────────────────────────────────────────────────────
// Draws the funnel through the channel to the faucet for its planned time,
// then runs machine_policy::kCleanRounds rounds — or `rounds`, when the
// console names one — of the channel's tap-water fill and pumped flush, each
// step ending on its reed or at its planned time; `stepPlannedMs` shortens
// every step's planned time when the console names one. Refused while
// anything else runs, while the expanders are unverified, and under the gas
// alarm; every answer, every step, and every ending goes out through
// machineOnCleanState.
bool machineCleanBegin(uint8_t channel, uint8_t rounds = 0, uint32_t stepPlannedMs = 0);
void machineCleanStop();   // ends a running cycle on request; nothing otherwise
bool machineIsCleaning();
void machineReadCleanState(MachineCleanState &state);

// ── The air cycles ────────────────────────────────────────────────────────
// Dry sweeps both channels with air, in then through to the faucet, and dries
// the flavor lines at the bench or the factory; Purge airs one channel's
// reservoir and draws it out the faucet. Each step runs its planned time
// (machine_policy::airStepPlannedMs, or stepPlannedMs when the console names
// one); the Out step also ends on the empty reed the way a clean flush does.
// Refused on the same grounds as the fill; every answer, step and ending goes
// out through machineOnAirState.
bool machineAirBegin(uint8_t mode, uint8_t channel, uint32_t stepPlannedMs = 0);
void machineAirStop();
bool machineIsAiring();
void machineReadAirState(MachineAirState &state);

// ── The pour ──────────────────────────────────────────────────────────────
// The flow meter on the carbonated-water line is counted on an interrupt and
// read every 50 ms. Flow with the machine idle opens the selected channel's
// dispense path — its draw and its flavor tube — and runs its pump on the
// duty cycle machine_policy::Pour sets from the flow and the channel's ratio;
// a cooldown with nothing flowing closes it. Nothing is injected while
// another operation runs, while the expanders are unverified, or under the
// gas alarm; the water still pours. Relay #2 stays off while a pour or held
// prime has its dispense path open.
bool machineIsPouring();
bool machineDispenseWindowOpen();
uint32_t machinePourCycles();     // pump bursts in the running or last pour
// The bench has no meter: pretend it reads `pulses` per sample for `ms`.
void machineFlowSimulate(uint32_t pulses, uint32_t ms);
uint32_t machineFlowPulsesTotal();

// ── The self-test ─────────────────────────────────────────────────────────
// firmware-and-commissioning.md §7: every solenoid in turn, V-A through V-K,
// for a quarter second each; then the condenser fan for a second; then each
// pump for a second. Each load is parked and the outputs read back before the
// next is driven. Refused while anything else runs, while the expanders are
// unverified, and under the gas alarm. The console watches it step by step.
bool machineSelfTestBegin();
void machineSelfTestStop();

// ── Reservoir level ───────────────────────────────────────────────────────
// Both reed columns and the carbonator's two reeds, read once a second while
// the machine is idle and every quarter second while an operation moves a
// level, and each reservoir's gauge from them (machine_policy::ReservoirLevel).
struct MachineLevels {
    bool    valid;        // read within the last few seconds
    uint8_t reeds[2];     // closed masks, bit 0 empty .. bit 3 full
    uint8_t level[2];     // 0..LEVEL_SEGMENTS, or LEVEL_UNKNOWN
    bool    carbLow;
    bool    carbHigh;
};
void machineLevels(MachineLevels &levels);

// The MQ-6 comparator, debounced. U15 holds the compressor off it in hardware
// with no firmware in the path; what the firmware adds is the alarm, and
// relay #1 dropped as well.
bool machineGasTripped();

// ── The cold loop and the refill, as they read from outside ───────────────
// `coldState` and `refillState` are machine_policy::ColdState and
// ::RefillState; the two relay fields are the pins themselves, so a state
// that disagrees with its relay is visible rather than inferred.
struct MachineThermal {
    float   tankC;            // carbonator wall, DS18B20 family 0x28
    bool    tankValid;
    float   coilC;            // suction line, DS18S20 family 0x10
    bool    coilValid;
    uint8_t coldState;
    uint8_t refillState;
    bool    compressorRelay;
    bool    refillRelay;
    uint8_t probeCount;       // devices answering on the 1-wire bus
    uint32_t holdRemainingMs; // 0 unless the cold loop is inside its minimum off-time
    uint32_t refillPumpedMs;
    bool    simulated;        // a reading injected from the console, not a probe
};
void machineThermal(MachineThermal &thermal);

// The two state enums as words, for the console and the glass.
const char *machineColdStateName(uint8_t coldState);
const char *machineRefillStateName(uint8_t refillState);

// ── Injected readings ─────────────────────────────────────────────────────
// Development control from the USB console. The loops run for real against
// these — the policy, the relays and the fan all move — and only the reading
// at the top is invented. Nothing production-facing calls them, a reboot
// clears them, and `simulated` stays true in MachineThermal while one stands.
void machineSimThermal(float tankC, bool tankValid, float coilC, bool coilValid);
void machineSimReeds(bool carbLow, bool carbHigh);
void machineSimClear();
void machineRefillRequest(); // fill now, whatever the reeds read: until the high reed or the ceiling
void machineRefillLatch();   // stand a refill latched as one that spent its ceiling does
void machineRefillForget();  // drop a refill that is owed, and the flash's note of it

// Someone at the machine, told what to check, asks for the water again: a refill that stands
// latched gets a whole pumping ceiling and tries. False when none stood latched. The
// machine's own display sends it, and the console's `refill clear`.
bool machineRefillRetry();

// True while a refill stands latched at its pumping ceiling.
bool machineRefillLatched();

// What stops the machine making soda, NOTICE_*: the one answer both links carry to the
// glasses. A kind a host on the console is holding reads as none.
uint8_t machineNotice();

// A machine on a bench has no water to find and nobody to tell so. A host on its console
// holds named notices off the glasses for a lease it renews while it stays connected; bit n
// of `kinds` holds NOTICE kind n, and none releases. Only what the glasses say is held:
// a refill that stands latched still stands. A restart or a lapsed lease ends the hold.
constexpr uint32_t kNoticeHoldLeaseMs = 900000;
void    machineNoticeHold(uint8_t kinds);
uint8_t machineNoticeHeld();          // the kinds held now
uint32_t machineNoticeHoldLeftMs();   // what is left of the lease
uint8_t machineNoticeStanding();      // the notice with nothing held

// ── The sweep ─────────────────────────────────────────────────────────────
// A carbonator that was drained and opened holds air, and a fill would squeeze it into the
// headspace to stay. While a sweep is owed the refill is held and the meter's pulses open
// no pour: with the tank dry and the cylinder open, the lever at the faucet lets CO2 carry
// the air out, and the meter counts it (machine_policy::Sweep). The lever let go after the
// target asks for the first fill. That a sweep is owed is kept in flash.
struct MachineSweep {
    bool     owed;
    bool     flowing;   // gas is moving and the count is short of its target
    bool     done;      // the target is met and the lever is still down
    uint8_t  percent;   // of the target
    uint32_t pulses;    // counted so far
};
void machineSweep(MachineSweep &sweep);

// The tank has been drained and opened: owe a sweep, and drop any refill that is owed.
// False while a carbonator reed reads closed, which is a tank that holds water.
bool machineSweepOwe();

// Give the sweep up and ask for the first fill without it. False when none is owed. The
// machine's own display sends it, and the console's `sweep skip`.
bool machineSweepSkip();

// Drop a sweep that is owed and ask for nothing, for a bench. False when none is owed.
bool machineSweepForget();

// Read-only commissioning snapshot of the two MCP23017s and all ten reeds.
// This is populated only when explicitly requested from the USB console; it is
// not polled in the interaction loop or placed on J9.
struct MachineIoStatus {
    bool initialized;
    bool configurationVerified;
    bool outputsMatchPlan;
    bool outputsKnownParked;
    bool reedsValid;
    uint8_t fault;
    uint8_t faultAddress;
    uint8_t faultRegister;
    uint8_t outputLatchA20;
    uint8_t outputLatchA21;
    uint8_t pullupsB20;
    uint8_t pullupsB21;
    uint8_t rawReedsA;
    uint8_t rawReedsB;
    uint8_t reservoirAClosedMask;
    uint8_t reservoirBClosedMask;
    bool carbonatorLowClosed;
    bool carbonatorHighClosed;
};

bool machineIoReady();
bool machineReadIoStatus(MachineIoStatus &status);
const char *machineIoFaultName(uint8_t fault);

MachineState machineState();
const char  *machineStateName();
bool         machineIsPriming();
uint8_t      machinePumpChannel();
uint32_t     machinePumpElapsedMs();
const char  *machinePumpName(uint8_t channel);
