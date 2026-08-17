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
// or bounded from the console. Nothing touches the two MCP23017s, so the eleven
// valves and the condenser fan stay high-Z, and neither relay is ever driven.

enum MachineState : uint8_t {
    ST_IDLE,     // nothing driven
    ST_PUMPING,  // one flavor pump turning
};

// Why the pump is turning, which is the same as what will stop it.
enum PumpHold : uint8_t {
    HOLD_PRIME,  // a finger on the glass — a stale tick or the ceiling ends it
    HOLD_TIMED,  // a bounded run — its own deadline ends it
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
bool machinePumpRun(uint8_t channel, uint32_t ms);
void machineStop();      // whatever is running, end it and park

MachineState machineState();
const char  *machineStateName();
bool         machineIsPriming();
uint8_t      machinePumpChannel();
uint32_t     machinePumpElapsedMs();
const char  *machinePumpName(uint8_t channel);
