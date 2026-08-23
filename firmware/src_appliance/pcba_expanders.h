#pragma once

#include <stdint.h>

#include "machine_policy.h"

// Production board support for U2/U3, the two MCP23017s on the main
// board. This module owns the mapping between machine names (V-A..V-K) and
// expander pins; callers deal only in logical outputs and closed reeds.
//
// Nothing in this file is an operation sequencer. The machine state machine
// remains responsible for deciding which *valid* set of valves represents a
// dispense, clean, refill, or service operation. This layer enforces the
// board's absolute three-solenoid ceiling and makes every I2C failure converge
// on verified-low Port-A pins where the bus still permits it. It does not drive
// the separate refill relay, so the arbiter must still validate the complete
// machine_policy::ActuatorPlan and its refill/dispense interlock.
namespace pcba {

static const uint8_t MCP_RESERVOIR_A = 0x20;
static const uint8_t MCP_RESERVOIR_B = 0x21;

// Logical identity has one owner. machine_policy defines the topology-facing
// valve names and mask; this layer translates that mask into PCB pin bits.
using Valve = machine_policy::Valve;
using ValveMask = machine_policy::ValveMask;
using machine_policy::valveBit;

struct ExpanderOutputs {
    ValveMask valves;
    bool condenserFan;

    ExpanderOutputs() : valves(0), condenserFan(false) {}
    ExpanderOutputs(ValveMask valveMask, bool fan)
        : valves(valveMask), condenserFan(fan) {}

    bool valveOpen(Valve valve) const { return (valves & valveBit(valve)) != 0; }
    void setValve(Valve valve, bool open) {
        if (open) valves |= valveBit(valve);
        else      valves &= static_cast<ValveMask>(~valveBit(valve));
    }
};

// Raw GPIOB levels are retained for diagnostics. The named fields invert the
// MCP input because every reed uses INPUT_PULLUP: a closed reed reads LOW.
struct ReedSnapshot {
    uint8_t rawReservoirAPortB;
    uint8_t rawReservoirBPortB;
    uint8_t reservoirAClosedMask;  // bits 0..3: EMPTY through FULL
    uint8_t reservoirBClosedMask;  // bits 0..3: EMPTY through FULL
    bool carbonatorLowClosed;      // 0x21 PB4
    bool carbonatorHighClosed;     // 0x21 PB5
};

enum class Fault : uint8_t {
    None = 0,
    NotInitialized,
    InvalidOutputPlan,
    BusBeginFailed,
    BusWriteFailed,
    BusReadFailed,
    RegisterMismatch,
};

struct DeviceHealth {
    uint8_t address;
    bool responding;
    bool registersRead;
    bool configurationMatches;
    uint8_t iodirA;
    uint8_t iodirB;
    uint8_t ipolA;
    uint8_t ipolB;
    uint8_t gpintenA;
    uint8_t gpintenB;
    uint8_t iocon;
    uint8_t gppuA;
    uint8_t gppuB;
    uint8_t olatA;
};

struct Health {
    bool initialized;
    bool configurationVerified;
    bool outputsMatchPlan;
    bool outputsKnownParked;
    Fault lastFault;
    uint8_t faultAddress;
    uint8_t faultRegister;
    DeviceHealth devices[2];
};

// Kept deliberately smaller than TwoWire so the safety and mapping behavior
// can be exercised on a host with a register-file fake. begin() attaches or
// otherwise prepares the bus; it must not write an expander register itself.
class Transport {
public:
    virtual ~Transport() {}
    virtual bool begin() = 0;
    virtual bool writeRegister(uint8_t address, uint8_t reg, uint8_t value) = 0;
    virtual bool readRegister(uint8_t address, uint8_t reg, uint8_t &value) = 0;
};

class Expanders {
public:
    explicit Expanders(Transport &transport);

    // Establishes a known BANK=0 register map, clears both Port-A output
    // latches, and only then makes Port A outputs. Port B remains input with
    // every internal pull-up enabled, including unused pins. Every configured
    // register is read back before this returns true.
    bool begin();

    // Clears both output latches even when begin() has not completed. The park
    // path handles either MCP register-bank layout and attempts both devices
    // even after one stops answering.
    bool parkAll();

    // Applies an absolute logical output set. Removed outputs are written on
    // both expanders before any new output is added. Invalid masks, more than
    // three open solenoids, or any transfer/readback failure cause parkAll().
    // There is no intentional dwell between the global off phase and on phase.
    // If a physical sequence needs one, the state machine submits the retained
    // or parked stage, waits, and then submits the final output set.
    bool apply(const ExpanderOutputs &outputs);

    // Reads all ten active-low reed inputs in two I2C transactions. A failed
    // sensor read parks outputs and invalidates the initialized state.
    bool readReeds(ReedSnapshot &snapshot);

    // Reads the complete safety-relevant register set from both devices. A
    // mismatch after begin() parks outputs and requires begin() again.
    bool readHealth(Health &health);

    bool initialized() const { return initialized_; }
    bool outputsKnownParked() const { return outputsKnownParked_; }
    ExpanderOutputs currentOutputs() const { return currentOutputs_; }
    Fault lastFault() const { return lastFault_; }
    uint8_t lastFaultAddress() const { return faultAddress_; }
    uint8_t lastFaultRegister() const { return faultRegister_; }

    // Public so native tests can prove the PCB-canonical reversed Port-A map
    // without duplicating it. Returns false for an invalid/over-budget plan.
    static bool encodeOutputs(const ExpanderOutputs &outputs,
                              uint8_t &portA20, uint8_t &portA21);

private:
    Transport &transport_;
    bool initialized_;
    bool outputsKnownParked_;
    ExpanderOutputs currentOutputs_;
    uint8_t currentPortA20_;
    uint8_t currentPortA21_;
    Fault lastFault_;
    uint8_t faultAddress_;
    uint8_t faultRegister_;

    void clearFault();
    void setFault(Fault fault, uint8_t address, uint8_t reg);
    bool configureDevice(uint8_t address);
    bool writeLatchVerified(uint8_t address, uint8_t value);
    bool parkRaw();
    bool failAndPark(Fault fault, uint8_t address, uint8_t reg,
                     bool requireReinitialize);
    bool readDeviceHealth(uint8_t address, DeviceHealth &health,
                          uint8_t &failedRegister);
};

#if defined(ARDUINO)
// Singleton backed by Arduino Wire on PIN_SDA/PIN_SCL at 100 kHz. Merely
// obtaining the reference performs no bus transaction; Expanders::begin()
// attaches Wire and performs the fail-safe initialization.
Expanders &expanders();
#endif

}  // namespace pcba
