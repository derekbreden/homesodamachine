#pragma once

#include <stdint.h>

// ════════════════════════════════════════════════════════════
//  The machine — every actuator on the board, behind one door
// ════════════════════════════════════════════════════════════
//
// machine.cpp is the only file that drives a pin reaching a load. The glass,
// the serial console, and the faucet when it exists all ask for a thing here,
// and the three limits in main.cpp's header are held here.
//
// What is implemented today is one flavor pump turning — held from the glass,
// or bounded from the console. The two MCP23017s are initialized fail-closed:
// every output is parked low and the reed inputs have internal pull-ups. No
// operation opens a valve or runs the fan, and neither relay is ever driven.

enum MachineState : uint8_t {
    ST_IDLE,     // nothing driven
    ST_PUMPING,  // one flavor pump turning
};

// Why the pump is turning, which is the same as what will stop it.
enum PumpHold : uint8_t {
    HOLD_PRIME,  // a finger on the glass — a stale tick or the ceiling ends it
    HOLD_TIMED,  // a bounded run — its own deadline ends it
};

// Physical link identity is supplied by link.cpp / faucet_link.cpp and never
// accepted from a display payload.
enum MachinePrimeSource : uint8_t {
    MACHINE_PRIME_FRONT  = 1,
    MACHINE_PRIME_FAUCET = 2,
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

// ── What the machine announces ────────────────────────────────────────────
// Every prime state change, in proto_msg.h's PRIME_* vocabulary. link.cpp turns
// these into MSG_RESP_PRIME. Set before machineBegin().
extern void (*machineOnPrimeState)(uint8_t state, uint8_t channel, uint32_t ms);

// A bounded run reaching its deadline, so MSG_RESP_PUMP_DONE goes out when the
// head has already stopped rather than when the run was asked for.
extern void (*machineOnPumpDone)(uint8_t channel);

void machineBegin();
void machineService();   // call every loop; the deadlines are read here

// ── Intents ───────────────────────────────────────────────────────────────
// Each answers whether the machine took it. A refusal is announced too, so a
// caller that only listens still learns what happened.
bool machinePrimeBegin(uint8_t channel);
void machinePrimeTick(uint8_t channel);
void machinePrimeEnd();

// Controller-owned prime-ready session. The enclosure activates and leases it;
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

// The MQ-6 comparator, debounced. U15 holds the compressor off it in hardware
// with no firmware in the path; what the firmware adds is the alarm.
bool machineGasTripped();

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
