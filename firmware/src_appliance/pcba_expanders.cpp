#include "pcba_expanders.h"

#include <string.h>

#if defined(ARDUINO)
#include <Arduino.h>
#include <Wire.h>

#include "pins.h"
#endif

namespace pcba {
namespace {

// MCP23017 register addresses with IOCON.BANK=0.
static const uint8_t REG_IODIRA   = 0x00;
static const uint8_t REG_IODIRB   = 0x01;
static const uint8_t REG_IPOLA    = 0x02;
static const uint8_t REG_IPOLB    = 0x03;
static const uint8_t REG_GPINTENA = 0x04;
static const uint8_t REG_GPINTENB = 0x05;
static const uint8_t REG_IOCON    = 0x0A;
static const uint8_t REG_GPPUA    = 0x0C;
static const uint8_t REG_GPPUB    = 0x0D;
static const uint8_t REG_GPIOB    = 0x13;
static const uint8_t REG_OLATA    = 0x14;

// With IOCON.BANK=1, 0x05 is IOCONA and 0x0A is OLATA. Those aliases let the
// emergency park path recover safely after an ESP-only reset even if a prior
// image left the expander in the other register layout.
static const uint8_t REG_BANK1_IOCONA = 0x05;
static const uint8_t REG_BANK1_OLATA  = 0x0A;

static const uint8_t EXPECTED_IODIRA = 0x00;  // all Port-A pins held LOW outputs
static const uint8_t EXPECTED_IODIRB = 0xFF;  // all Port-B pins are reed/spare inputs
static const uint8_t EXPECTED_IPOL   = 0x00;  // raw GPIOB remains active-low
static const uint8_t EXPECTED_GPINTEN = 0x00; // INTA/INTB are not routed; firmware polls
static const uint8_t EXPECTED_IOCON  = 0x00;  // BANK=0, sequential register map
static const uint8_t EXPECTED_GPPUA  = 0x00;  // never pull a TBD62083 input high
static const uint8_t EXPECTED_GPPUB  = 0xFF;  // reeds and unused inputs must not float

static const uint8_t kAddresses[2] = {MCP_RESERVOIR_A, MCP_RESERVOIR_B};

static uint8_t bitCount16(ValveMask value) {
    uint8_t count = 0;
    while (value != 0) {
        count += static_cast<uint8_t>(value & 1u);
        value >>= 1;
    }
    return count;
}

static bool deviceConfigurationMatches(const DeviceHealth &health) {
    return health.registersRead &&
           health.iodirA == EXPECTED_IODIRA &&
           health.iodirB == EXPECTED_IODIRB &&
           health.ipolA == EXPECTED_IPOL &&
           health.ipolB == EXPECTED_IPOL &&
           health.gpintenA == EXPECTED_GPINTEN &&
           health.gpintenB == EXPECTED_GPINTEN &&
           health.iocon == EXPECTED_IOCON &&
           health.gppuA == EXPECTED_GPPUA &&
           health.gppuB == EXPECTED_GPPUB;
}

static uint8_t firstConfigurationMismatch(const DeviceHealth &health) {
    if (health.iodirA != EXPECTED_IODIRA) return REG_IODIRA;
    if (health.iodirB != EXPECTED_IODIRB) return REG_IODIRB;
    if (health.ipolA != EXPECTED_IPOL) return REG_IPOLA;
    if (health.ipolB != EXPECTED_IPOL) return REG_IPOLB;
    if (health.gpintenA != EXPECTED_GPINTEN) return REG_GPINTENA;
    if (health.gpintenB != EXPECTED_GPINTEN) return REG_GPINTENB;
    if (health.iocon != EXPECTED_IOCON) return REG_IOCON;
    if (health.gppuA != EXPECTED_GPPUA) return REG_GPPUA;
    if (health.gppuB != EXPECTED_GPPUB) return REG_GPPUB;
    return 0;
}

}  // namespace

Expanders::Expanders(Transport &transport)
    : transport_(transport),
      initialized_(false),
      outputsKnownParked_(false),
      currentOutputs_(),
      currentPortA20_(0),
      currentPortA21_(0),
      lastFault_(Fault::NotInitialized),
      faultAddress_(0),
      faultRegister_(0) {}

void Expanders::clearFault() {
    lastFault_ = Fault::None;
    faultAddress_ = 0;
    faultRegister_ = 0;
}

void Expanders::setFault(Fault fault, uint8_t address, uint8_t reg) {
    lastFault_ = fault;
    faultAddress_ = address;
    faultRegister_ = reg;
}

bool Expanders::encodeOutputs(const ExpanderOutputs &outputs,
                              uint8_t &portA20, uint8_t &portA21) {
    if ((outputs.valves & static_cast<ValveMask>(~machine_policy::kAllValves)) != 0 ||
        bitCount16(outputs.valves) > machine_policy::kMaxOpenValves) {
        portA20 = 0;
        portA21 = 0;
        return false;
    }

    portA20 = 0;
    portA21 = 0;

    // pcba.tsx routes GPA_k to TBD62083 channel 8-k. Consequently logical
    // V-A..V-H run from GPA7 down to GPA0, not from GPA0 upward.
    for (uint8_t valve = 0; valve < 8; ++valve) {
        if ((outputs.valves & static_cast<ValveMask>(1u << valve)) != 0)
            portA20 |= static_cast<uint8_t>(1u << (7u - valve));
    }

    if ((outputs.valves & valveBit(Valve::I)) != 0) portA21 |= (1u << 7);
    if ((outputs.valves & valveBit(Valve::J)) != 0) portA21 |= (1u << 6);
    if ((outputs.valves & valveBit(Valve::K)) != 0) portA21 |= (1u << 5);
    if (outputs.condenserFan)                        portA21 |= (1u << 3);
    return true;
}

bool Expanders::parkRaw() {
    bool parked = true;

    for (uint8_t i = 0; i < 2; ++i) {
        const uint8_t address = kAddresses[i];

        // Best-effort clears at both possible OLATA addresses. With BANK=0,
        // 0x0A is IOCON (zero is the desired value) and 0x14 is OLATA. With
        // BANK=1, 0x0A is OLATA and 0x14 is INTCONB (zero is harmless).
        transport_.writeRegister(address, REG_BANK1_OLATA, 0);
        transport_.writeRegister(address, REG_OLATA, 0);

        // 0x05 is GPINTENB under BANK=0 and IOCONA under BANK=1. Zero is safe
        // in either interpretation and guarantees BANK=0 after an ACK.
        const bool normalized =
            transport_.writeRegister(address, REG_BANK1_IOCONA, 0);
        const bool pullupsCleared =
            transport_.writeRegister(address, REG_GPPUA, 0);
        const bool cleared =
            transport_.writeRegister(address, REG_OLATA, 0);
        const bool directionsSet =
            transport_.writeRegister(address, REG_IODIRA, EXPECTED_IODIRA);

        uint8_t gppuA = 0xFF;
        uint8_t olatA = 0xFF;
        uint8_t iodirA = 0xFF;
        const bool verified =
            transport_.readRegister(address, REG_GPPUA, gppuA) && gppuA == 0 &&
            transport_.readRegister(address, REG_OLATA, olatA) && olatA == 0 &&
            transport_.readRegister(address, REG_IODIRA, iodirA) &&
                iodirA == EXPECTED_IODIRA;
        parked = parked && normalized && pullupsCleared && cleared &&
                 directionsSet && verified;
    }

    currentOutputs_ = ExpanderOutputs();
    currentPortA20_ = 0;
    currentPortA21_ = 0;
    outputsKnownParked_ = parked;
    return parked;
}

bool Expanders::failAndPark(Fault fault, uint8_t address, uint8_t reg,
                            bool requireReinitialize) {
    const bool parked = parkRaw();
    if (requireReinitialize || !parked) initialized_ = false;
    setFault(fault, address, reg);
    return false;
}

bool Expanders::configureDevice(uint8_t address) {
    // parkRaw() has already normalized BANK and cleared OLATA. GPPUA is
    // cleared again before IODIRA becomes output so no TBD62083 input can see
    // an internal pull-up during the direction transition.
    struct RegisterValue { uint8_t reg; uint8_t value; };
    const RegisterValue configuration[] = {
        {REG_GPPUA,    EXPECTED_GPPUA},
        {REG_OLATA,    0},
        {REG_IODIRA,   EXPECTED_IODIRA},
        {REG_IODIRB,   EXPECTED_IODIRB},
        {REG_IPOLA,    EXPECTED_IPOL},
        {REG_IPOLB,    EXPECTED_IPOL},
        {REG_GPINTENA, EXPECTED_GPINTEN},
        {REG_GPINTENB, EXPECTED_GPINTEN},
        {REG_IOCON,    EXPECTED_IOCON},
        {REG_GPPUB,    EXPECTED_GPPUB},
    };

    const uint8_t count = sizeof(configuration) / sizeof(configuration[0]);
    for (uint8_t i = 0; i < count; ++i) {
        if (!transport_.writeRegister(address, configuration[i].reg,
                                      configuration[i].value)) {
            setFault(Fault::BusWriteFailed, address, configuration[i].reg);
            return false;
        }
    }
    return true;
}

bool Expanders::begin() {
    initialized_ = false;
    outputsKnownParked_ = false;
    currentOutputs_ = ExpanderOutputs();
    currentPortA20_ = 0;
    currentPortA21_ = 0;

    if (!transport_.begin()) {
        setFault(Fault::BusBeginFailed, 0, 0);
        return false;
    }

    if (!parkRaw()) {
        setFault(Fault::BusWriteFailed, 0, REG_OLATA);
        return false;
    }

    for (uint8_t i = 0; i < 2; ++i) {
        if (!configureDevice(kAddresses[i]))
            return failAndPark(lastFault_, faultAddress_, faultRegister_, true);
    }

    // Mark initialized only long enough for readHealth() to enforce the exact
    // register contract and fail parked on any mismatch.
    initialized_ = true;
    Health health;
    if (!readHealth(health)) return false;

    clearFault();
    return true;
}

bool Expanders::parkAll() {
    const bool parked = parkRaw();
    if (!parked) {
        initialized_ = false;
        setFault(Fault::BusWriteFailed, 0, REG_OLATA);
        return false;
    }
    clearFault();
    return true;
}

bool Expanders::writeLatchVerified(uint8_t address, uint8_t value) {
    if (!transport_.writeRegister(address, REG_OLATA, value)) {
        setFault(Fault::BusWriteFailed, address, REG_OLATA);
        return false;
    }
    uint8_t readback = 0;
    if (!transport_.readRegister(address, REG_OLATA, readback)) {
        setFault(Fault::BusReadFailed, address, REG_OLATA);
        return false;
    }
    if (readback != value) {
        setFault(Fault::RegisterMismatch, address, REG_OLATA);
        return false;
    }
    return true;
}

bool Expanders::apply(const ExpanderOutputs &outputs) {
    uint8_t desired20 = 0;
    uint8_t desired21 = 0;
    if (!encodeOutputs(outputs, desired20, desired21))
        return failAndPark(Fault::InvalidOutputPlan, 0, 0, false);
    if (!initialized_)
        return failAndPark(Fault::NotInitialized, 0, 0, true);

    // Phase one removes every output that is not part of the new absolute
    // plan. Both expanders finish this phase before either can add an output.
    const uint8_t retained20 = currentPortA20_ & desired20;
    const uint8_t retained21 = currentPortA21_ & desired21;
    if (retained20 != currentPortA20_ &&
        !writeLatchVerified(MCP_RESERVOIR_A, retained20)) {
        return failAndPark(lastFault_, faultAddress_, faultRegister_, true);
    }
    if (retained21 != currentPortA21_ &&
        !writeLatchVerified(MCP_RESERVOIR_B, retained21)) {
        return failAndPark(lastFault_, faultAddress_, faultRegister_, true);
    }

    // Only after the global off phase succeeds may either expander add bits.
    if (desired20 != retained20 &&
        !writeLatchVerified(MCP_RESERVOIR_A, desired20)) {
        return failAndPark(lastFault_, faultAddress_, faultRegister_, true);
    }
    if (desired21 != retained21 &&
        !writeLatchVerified(MCP_RESERVOIR_B, desired21)) {
        return failAndPark(lastFault_, faultAddress_, faultRegister_, true);
    }

    currentOutputs_ = outputs;
    currentPortA20_ = desired20;
    currentPortA21_ = desired21;
    outputsKnownParked_ = desired20 == 0 && desired21 == 0;
    clearFault();
    return true;
}

bool Expanders::readReeds(ReedSnapshot &snapshot) {
    if (!initialized_)
        return failAndPark(Fault::NotInitialized, 0, 0, true);

    uint8_t raw20 = 0;
    uint8_t raw21 = 0;
    if (!transport_.readRegister(MCP_RESERVOIR_A, REG_GPIOB, raw20))
        return failAndPark(Fault::BusReadFailed, MCP_RESERVOIR_A, REG_GPIOB, true);
    if (!transport_.readRegister(MCP_RESERVOIR_B, REG_GPIOB, raw21))
        return failAndPark(Fault::BusReadFailed, MCP_RESERVOIR_B, REG_GPIOB, true);

    snapshot.rawReservoirAPortB = raw20;
    snapshot.rawReservoirBPortB = raw21;
    snapshot.reservoirAClosedMask = static_cast<uint8_t>((~raw20) & 0x0F);
    snapshot.reservoirBClosedMask = static_cast<uint8_t>((~raw21) & 0x0F);
    snapshot.carbonatorLowClosed = (raw21 & (1u << 4)) == 0;
    snapshot.carbonatorHighClosed = (raw21 & (1u << 5)) == 0;
    clearFault();
    return true;
}

bool Expanders::readDeviceHealth(uint8_t address, DeviceHealth &health,
                                 uint8_t &failedRegister) {
    memset(&health, 0, sizeof(health));
    health.address = address;
    failedRegister = 0;

    struct RegisterTarget {
        uint8_t reg;
        uint8_t *target;
    };
    RegisterTarget targets[] = {
        {REG_IODIRA,   &health.iodirA},
        {REG_IODIRB,   &health.iodirB},
        {REG_IPOLA,    &health.ipolA},
        {REG_IPOLB,    &health.ipolB},
        {REG_GPINTENA, &health.gpintenA},
        {REG_GPINTENB, &health.gpintenB},
        {REG_IOCON,    &health.iocon},
        {REG_GPPUA,    &health.gppuA},
        {REG_GPPUB,    &health.gppuB},
        {REG_OLATA,    &health.olatA},
    };

    const uint8_t targetCount = sizeof(targets) / sizeof(targets[0]);
    for (uint8_t i = 0; i < targetCount; ++i) {
        if (!transport_.readRegister(address, targets[i].reg, *targets[i].target)) {
            failedRegister = targets[i].reg;
            return false;
        }
        health.responding = true;
    }

    health.registersRead = true;
    health.configurationMatches = deviceConfigurationMatches(health);
    return true;
}

bool Expanders::readHealth(Health &health) {
    memset(&health, 0, sizeof(health));
    health.initialized = initialized_;
    health.outputsKnownParked = outputsKnownParked_;
    health.lastFault = lastFault_;
    health.faultAddress = faultAddress_;
    health.faultRegister = faultRegister_;

    uint8_t failedRegister = 0;
    for (uint8_t i = 0; i < 2; ++i) {
        if (!readDeviceHealth(kAddresses[i], health.devices[i], failedRegister)) {
            failAndPark(Fault::BusReadFailed, kAddresses[i], failedRegister, true);
            health.initialized = initialized_;
            health.outputsKnownParked = outputsKnownParked_;
            health.lastFault = lastFault_;
            health.faultAddress = faultAddress_;
            health.faultRegister = faultRegister_;
            return false;
        }
    }

    health.configurationVerified =
        health.devices[0].configurationMatches &&
        health.devices[1].configurationMatches;

    uint8_t expected20 = 0;
    uint8_t expected21 = 0;
    const bool planValid = encodeOutputs(currentOutputs_, expected20, expected21);
    health.outputsMatchPlan = planValid &&
        health.devices[0].olatA == expected20 &&
        health.devices[1].olatA == expected21;
    health.outputsKnownParked = health.devices[0].olatA == 0 &&
                                health.devices[1].olatA == 0;
    outputsKnownParked_ = health.outputsKnownParked;

    if (!health.configurationVerified) {
        uint8_t device = health.devices[0].configurationMatches ? 1 : 0;
        const uint8_t mismatch = firstConfigurationMismatch(health.devices[device]);
        failAndPark(Fault::RegisterMismatch, kAddresses[device], mismatch, true);
    } else if (!health.outputsMatchPlan) {
        const uint8_t device = health.devices[0].olatA == expected20 ? 1 : 0;
        failAndPark(Fault::RegisterMismatch, kAddresses[device], REG_OLATA, true);
    } else if (!initialized_) {
        setFault(Fault::NotInitialized, 0, 0);
    } else {
        clearFault();
    }

    health.initialized = initialized_;
    health.outputsKnownParked = outputsKnownParked_;
    health.lastFault = lastFault_;
    health.faultAddress = faultAddress_;
    health.faultRegister = faultRegister_;
    return initialized_ && health.configurationVerified && health.outputsMatchPlan;
}

#if defined(ARDUINO)
namespace {

class WireTransport : public Transport {
public:
    bool begin() override { return Wire.begin(PIN_SDA, PIN_SCL, 100000); }

    bool writeRegister(uint8_t address, uint8_t reg, uint8_t value) override {
        Wire.beginTransmission(address);
        Wire.write(reg);
        Wire.write(value);
        return Wire.endTransmission() == 0;
    }

    bool readRegister(uint8_t address, uint8_t reg, uint8_t &value) override {
        Wire.beginTransmission(address);
        Wire.write(reg);
        if (Wire.endTransmission(false) != 0) return false;
        if (Wire.requestFrom(static_cast<int>(address), 1, static_cast<int>(true)) != 1)
            return false;
        value = static_cast<uint8_t>(Wire.read());
        return true;
    }
};

}  // namespace

Expanders &expanders() {
    static WireTransport wireTransport;
    static Expanders controller(wireTransport);
    return controller;
}
#endif

}  // namespace pcba
