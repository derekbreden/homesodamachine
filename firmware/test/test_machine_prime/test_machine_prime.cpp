#include <string.h>
#include <vector>

#include <unity.h>
#include "fakes/Arduino.h"
#include "../../src_appliance/pins.h"
#include "../../src_appliance/pcba_expanders.cpp"
#include "sound_policy.h"
#include "sound.h"

namespace host {

constexpr uint8_t kGpioB = 0x13;
constexpr uint8_t kOlatA = 0x14;

enum class EventKind { Register, Duty, Mode, Attach };
struct Event {
    EventKind kind;
    int address;
    int reg;
    uint32_t before;
    uint32_t value;
};

std::vector<Event> events;
uint32_t now = 1000;
uint32_t gasMv = 0;
uint32_t duties[40] = {};
int modes[40] = {};
bool attachSucceeds = true;
bool pumpClosedAgainstDrive = false;
SoundId sounding = SND_NONE;

class RegisterBus : public pcba::Transport {
public:
    void reset() {
        memset(registers, 0, sizeof(registers));
        registers[0][kGpioB] = registers[1][kGpioB] = 0xff;
        failedReadAddress = failedWriteAddress = 0;
        readFailures = writeFailures = 0;
    }

    bool begin() override { return true; }

    bool writeRegister(uint8_t address, uint8_t reg, uint8_t value) override {
        uint8_t &previous = at(address, reg);
        events.push_back({EventKind::Register, address, reg, previous, value});
        if (writeFailures && address == failedWriteAddress &&
            reg == failedWriteRegister && value == failedWriteValue) {
            --writeFailures;
            return false;
        }
        if (reg == kOlatA) {
            // The real PCB map puts E/G at 0x20 bits 3/1 and H/J at
            // 0x20 bit 0 / 0x21 bit 6. A fault park must stop GPIO PWM
            // before removing any valve of the running pump's wet path.
            const uint8_t removed = previous & static_cast<uint8_t>(~value);
            if ((duties[PIN_PUMP_A] && address == 0x20 && (removed & 0x0a)) ||
                (duties[PIN_PUMP_B] && ((address == 0x20 && (removed & 0x01)) ||
                                       (address == 0x21 && (removed & 0x40)))))
                pumpClosedAgainstDrive = true;
        }
        previous = value;
        return true;
    }

    bool readRegister(uint8_t address, uint8_t reg, uint8_t &value) override {
        if (readFailures && address == failedReadAddress && reg == failedReadRegister) {
            --readFailures;
            return false;
        }
        value = at(address, reg);
        return true;
    }

    uint8_t &at(uint8_t address, uint8_t reg) {
        return registers[address == pcba::MCP_RESERVOIR_A ? 0 : 1][reg];
    }

    void failRead(uint8_t address, uint8_t reg) {
        failedReadAddress = address;
        failedReadRegister = reg;
        readFailures = 1;
    }

    void failWrite(uint8_t address, uint8_t reg, uint8_t value) {
        failedWriteAddress = address;
        failedWriteRegister = reg;
        failedWriteValue = value;
        writeFailures = 1;
    }

private:
    uint8_t registers[2][256] = {};
    uint8_t failedReadAddress = 0, failedReadRegister = 0, readFailures = 0;
    uint8_t failedWriteAddress = 0, failedWriteRegister = 0;
    uint8_t failedWriteValue = 0, writeFailures = 0;
};

RegisterBus bus;

}  // namespace host

HostSerial Serial;
unsigned long millis() { return host::now; }
void pinMode(int pin, int mode) {
    host::events.push_back({host::EventKind::Mode, pin, 0,
                           static_cast<uint32_t>(host::modes[pin]),
                           static_cast<uint32_t>(mode)});
    host::modes[pin] = mode;
}
void digitalWrite(int, int) {}
uint32_t analogReadMilliVolts(int) { return host::gasMv; }
bool ledcAttach(int pin, uint32_t, uint8_t) {
    host::events.push_back({host::EventKind::Attach, pin, 0, 0, 0});
    return host::attachSucceeds;
}
bool ledcWrite(int pin, uint32_t duty) {
    host::events.push_back({host::EventKind::Duty, pin, 0, host::duties[pin], duty});
    host::duties[pin] = duty;
    return true;
}
bool ledcDetach(int) { return true; }
void noInterrupts() {}
void interrupts() {}
int digitalPinToInterrupt(int pin) { return pin; }
void attachInterrupt(int, void (*)(), int) {}

void soundBegin(int) { host::sounding = SND_NONE; }
bool soundPlay(SoundId id) {
    if (host::sounding != SND_ALARM) host::sounding = id;
    return true;
}
void soundStop() { host::sounding = SND_NONE; }
SoundId soundPlaying() { return host::sounding; }
bool soundPlayNote(uint16_t, uint16_t, uint8_t) { return true; }

void oneWireBegin() {}
void oneWireService(uint32_t) {}
void oneWireRead(float &tank, bool &tankValid, float &coil, bool &coilValid) {
    tank = coil = 0;
    tankValid = coilValid = false;
}
uint8_t oneWireDeviceCount() { return 0; }
uint8_t flavorSelected() { return 0; }
uint8_t flavorRatio(uint8_t) { return 20; }

namespace pcba {
Expanders &expanders() {
    static Expanders instance(host::bus);
    return instance;
}
}  // namespace pcba

// Compile the production actuator arbiter and expander driver, with only
// their hardware endpoints replaced. This covers the actual entry/exit
// handlers rather than a separate test model of Prime.
#include "../../src_appliance/machine.cpp"

namespace {

constexpr uint32_t kSession = 0x1234;
constexpr uint32_t kHold = 0x5678;
uint8_t lastPrimeState = 0xff;
uint32_t lastPrimeElapsed = 0;
bool lastEventSessionOwned = false;
uint32_t primeEventCount = 0;
uint32_t pumpDoneCount = 0;

void onPrime(uint8_t phase, uint8_t, uint32_t elapsed) {
    if (phase != PRIME_RUNNING && machineState() == ST_IDLE) {
        TEST_ASSERT_EQUAL_HEX16(0, machineValvesOpen());
        TEST_ASSERT_EQUAL_UINT32(0, host::duties[PIN_PUMP_A]);
        TEST_ASSERT_EQUAL_UINT32(0, host::duties[PIN_PUMP_B]);
        TEST_ASSERT_FALSE(host::pumpClosedAgainstDrive);
    }
    lastPrimeState = phase;
    lastPrimeElapsed = elapsed;
    lastEventSessionOwned = machinePrimeEventIsSessionOwned();
    ++primeEventCount;
}
void onPumpDone(uint8_t) { ++pumpDoneCount; }

MachinePrimeSessionState session() {
    MachinePrimeSessionState value;
    machineReadPrimeSessionState(value);
    return value;
}

uint16_t dispensePair(uint8_t channel) {
    using machine_policy::Valve;
    using machine_policy::valveBit;
    return channel == 0 ? valveBit(Valve::E) | valveBit(Valve::G)
                        : valveBit(Valve::H) | valveBit(Valve::J);
}

int pumpPin(uint8_t channel) { return channel == 0 ? PIN_PUMP_A : PIN_PUMP_B; }

void runAt(uint32_t time) {
    host::now = time;
    machineService();
}

void start(uint8_t channel = 0, MachinePrimeSource source = MACHINE_PRIME_ENCLOSURE) {
    TEST_ASSERT_TRUE(machinePrimeSessionActivate(channel, kSession));
    TEST_ASSERT_TRUE(machinePrimeSessionHoldBegin(source, channel, kSession, kHold));
}

void expectWet(uint8_t channel) {
    TEST_ASSERT_TRUE(machineIsPriming());
    TEST_ASSERT_TRUE(machineDispenseWindowOpen());
    TEST_ASSERT_EQUAL_HEX16(dispensePair(channel), machineValvesOpen());
    TEST_ASSERT_EQUAL_UINT32(255, host::duties[pumpPin(channel)]);
    TEST_ASSERT_EQUAL_UINT32(0, host::duties[pumpPin(channel ^ 1)]);
    TEST_ASSERT_EQUAL_UINT8(PRIME_SESSION_RUNNING, session().phase);
    MachineThermal thermal;
    machineThermal(thermal);
    TEST_ASSERT_FALSE(thermal.refillRelay);
}

void expectParked() {
    TEST_ASSERT_FALSE(machineIsPriming());
    TEST_ASSERT_FALSE(machineDispenseWindowOpen());
    TEST_ASSERT_EQUAL_HEX16(0, machineValvesOpen());
    TEST_ASSERT_EQUAL_UINT32(0, host::duties[PIN_PUMP_A]);
    TEST_ASSERT_EQUAL_UINT32(0, host::duties[PIN_PUMP_B]);
    TEST_ASSERT_EQUAL(INPUT, host::modes[PIN_PUMP_A]);
    TEST_ASSERT_EQUAL(INPUT, host::modes[PIN_PUMP_B]);
    TEST_ASSERT_FALSE(host::pumpClosedAgainstDrive);
}

void expectOutcome(uint8_t phase, uint8_t outcome, uint32_t elapsed) {
    const MachinePrimeSessionState value = session();
    TEST_ASSERT_EQUAL_UINT8(phase, value.phase);
    TEST_ASSERT_EQUAL_UINT8(PRIME_OWNER_NONE, value.owner);
    TEST_ASSERT_EQUAL_UINT8(outcome, value.outcome);
    TEST_ASSERT_EQUAL_UINT32(elapsed, value.elapsedMs);
}

size_t firstDuty(uint32_t duty) {
    for (size_t i = 0; i < host::events.size(); ++i)
        if (host::events[i].kind == host::EventKind::Duty && host::events[i].value == duty)
            return i;
    return host::events.size();
}

void test_ready_and_cancel_ready_drive_nothing() {
    const size_t count = host::events.size();
    TEST_ASSERT_TRUE(machinePrimeSessionActivate(1, kSession));
    TEST_ASSERT_TRUE(machinePrimeSessionQuery(kSession));
    runAt(host::now + 500);
    TEST_ASSERT_EQUAL_UINT8(PRIME_SESSION_READY, session().phase);
    expectParked();
    TEST_ASSERT_TRUE(machinePrimeSessionCancel(kSession));
    expectOutcome(PRIME_SESSION_OFF, PRIME_OUTCOME_CANCELED, 0);
    TEST_ASSERT_EQUAL_UINT32(count, host::events.size());
}

void test_both_channels_open_the_complete_pair_before_forward_drive() {
    for (uint8_t channel = 0; channel < 2; ++channel) {
        host::events.clear();
        TEST_ASSERT_TRUE(machinePrimeSessionActivate(channel, kSession + channel));
        TEST_ASSERT_TRUE(machinePrimeSessionHoldBegin(
            MACHINE_PRIME_ENCLOSURE, channel, kSession + channel, kHold));
        expectWet(channel);
        const size_t driven = firstDuty(255);
        TEST_ASSERT_TRUE(driven > 0 && driven < host::events.size());
        for (size_t i = driven + 1; i < host::events.size(); ++i)
            TEST_ASSERT_TRUE(host::events[i].kind != host::EventKind::Register);
        host::now += 100;
        TEST_ASSERT_TRUE(machinePrimeSessionHoldEnd(
            MACHINE_PRIME_ENCLOSURE, channel, kSession + channel, kHold));
        expectParked();
        expectOutcome(PRIME_SESSION_READY, PRIME_OUTCOME_STOPPED, 100);
        TEST_ASSERT_EQUAL_UINT8(PRIME_STOPPED, lastPrimeState);
        TEST_ASSERT_TRUE(lastEventSessionOwned);
        TEST_ASSERT_TRUE(machinePrimeSessionCancel(kSession + channel));
    }
}

void test_duplicate_start_does_not_restart_the_clock_or_actuators() {
    start();
    const uint32_t revision = session().revision;
    const size_t count = host::events.size();
    host::now += 500;
    TEST_ASSERT_TRUE(machinePrimeSessionHoldBegin(MACHINE_PRIME_ENCLOSURE, 0, kSession, kHold));
    TEST_ASSERT_EQUAL_UINT32(revision, session().revision);
    TEST_ASSERT_EQUAL_UINT32(count, host::events.size());
    TEST_ASSERT_EQUAL_UINT32(500, machinePumpElapsedMs());
    TEST_ASSERT_TRUE(machinePrimeSessionHoldEnd(MACHINE_PRIME_ENCLOSURE, 0, kSession, kHold));
    expectParked();
    const size_t stopped = host::events.size();
    TEST_ASSERT_FALSE(machinePrimeSessionHoldBegin(MACHINE_PRIME_ENCLOSURE, 0, kSession, kHold));
    TEST_ASSERT_FALSE(machinePrimeSessionHoldTick(MACHINE_PRIME_ENCLOSURE, 0, kSession, kHold));
    TEST_ASSERT_FALSE(machinePrimeSessionHoldEnd(MACHINE_PRIME_ENCLOSURE, 0, kSession, kHold));
    TEST_ASSERT_EQUAL_UINT32(stopped, host::events.size());
    TEST_ASSERT_TRUE(machinePrimeSessionHoldBegin(MACHINE_PRIME_ENCLOSURE, 0, kSession, kHold + 1));
    expectWet(0);
    TEST_ASSERT_EQUAL_UINT32(0, machinePumpElapsedMs());
}

void test_competing_display_and_stale_tokens_do_not_change_a_wet_hold() {
    start(1, MACHINE_PRIME_FAUCET);
    const size_t count = host::events.size();
    TEST_ASSERT_FALSE(machinePrimeSessionHoldBegin(MACHINE_PRIME_ENCLOSURE, 1, kSession, kHold + 1));
    TEST_ASSERT_FALSE(machinePrimeSessionHoldEnd(MACHINE_PRIME_ENCLOSURE, 1, kSession, kHold));
    TEST_ASSERT_FALSE(machinePrimeSessionHoldTick(MACHINE_PRIME_FAUCET, 0, kSession, kHold));
    TEST_ASSERT_FALSE(machinePrimeSessionCancel(kSession + 1));
    TEST_ASSERT_FALSE(machinePrimeSessionActivate(0, kSession + 1));
    TEST_ASSERT_EQUAL_UINT32(count, host::events.size());
    expectWet(1);
    TEST_ASSERT_TRUE(machinePrimeSessionHoldEnd(MACHINE_PRIME_FAUCET, 1, kSession, kHold));
    expectParked();
    TEST_ASSERT_FALSE(machinePrimeSessionHoldBegin(MACHINE_PRIME_ENCLOSURE, 1, kSession, kHold + 1));
    TEST_ASSERT_TRUE(machinePrimeSessionHoldBegin(MACHINE_PRIME_ENCLOSURE, 1, kSession, kHold + 2));
    expectWet(1);
}

void test_stop_before_start_cannot_open_a_delayed_wet_path() {
    TEST_ASSERT_TRUE(machinePrimeSessionActivate(0, kSession));
    const size_t count = host::events.size();
    TEST_ASSERT_TRUE(machinePrimeSessionHoldEnd(MACHINE_PRIME_FAUCET, 0, kSession, kHold));
    TEST_ASSERT_FALSE(machinePrimeSessionHoldBegin(MACHINE_PRIME_FAUCET, 0, kSession, kHold));
    TEST_ASSERT_EQUAL_UINT32(count, host::events.size());
    expectParked();
}

void test_cancel_and_general_stop_park_before_terminal_publication() {
    start(1, MACHINE_PRIME_FAUCET);
    host::now += 300;
    TEST_ASSERT_TRUE(machinePrimeSessionCancel(kSession));
    expectParked();
    expectOutcome(PRIME_SESSION_OFF, PRIME_OUTCOME_CANCELED, 300);
    TEST_ASSERT_EQUAL_UINT32(300, lastPrimeElapsed);
    TEST_ASSERT_FALSE(machinePrimeSessionActivate(1, kSession));
    TEST_ASSERT_TRUE(machinePrimeSessionActivate(0, kSession + 1));
    TEST_ASSERT_TRUE(machinePrimeSessionHoldBegin(MACHINE_PRIME_ENCLOSURE, 0, kSession + 1, kHold));
    host::now += 50;
    machineStop();
    expectParked();
    expectOutcome(PRIME_SESSION_READY, PRIME_OUTCOME_STOPPED, 50);
}

void test_tick_timeout_closes_pair_at_exact_grace_plus_one() {
    start();
    const uint32_t began = host::now;
    runAt(began + PRIME_TICK_GRACE_MS);
    expectWet(0);
    runAt(began + PRIME_TICK_GRACE_MS + 1);
    expectParked();
    expectOutcome(PRIME_SESSION_READY, PRIME_OUTCOME_TIMEOUT, PRIME_TICK_GRACE_MS + 1);
    TEST_ASSERT_EQUAL_UINT8(PRIME_TIMEOUT, lastPrimeState);
    TEST_ASSERT_FALSE(machinePrimeSessionHoldTick(MACHINE_PRIME_ENCLOSURE, 0, kSession, kHold));
    expectParked();
}

void test_regular_ticks_stop_and_lock_at_the_hard_ceiling() {
    start(1, MACHINE_PRIME_FAUCET);
    const uint32_t began = host::now;
    for (uint32_t elapsed = PRIME_TICK_MS; elapsed <= PRIME_MAX_MS; elapsed += PRIME_TICK_MS) {
        host::now = began + elapsed;
        TEST_ASSERT_TRUE(machinePrimeSessionQuery(kSession));
        TEST_ASSERT_TRUE(machinePrimeSessionHoldTick(MACHINE_PRIME_FAUCET, 1, kSession, kHold));
        machineService();
        if (elapsed < PRIME_MAX_MS) expectWet(1);
    }
    expectParked();
    expectOutcome(PRIME_SESSION_READY, PRIME_OUTCOME_LIMIT, PRIME_MAX_MS);
    TEST_ASSERT_EQUAL_UINT8(PRIME_LIMIT, lastPrimeState);
}

void test_lease_expiry_stops_a_faucet_hold_with_live_ticks() {
    start(0, MACHINE_PRIME_FAUCET);
    const uint32_t began = host::now;
    for (uint32_t elapsed = 500; elapsed <= 5000; elapsed += 500) {
        host::now = began + elapsed;
        TEST_ASSERT_TRUE(machinePrimeSessionHoldTick(MACHINE_PRIME_FAUCET, 0, kSession, kHold));
        machineService();
    }
    expectWet(0);
    runAt(began + 5001);
    expectParked();
    expectOutcome(PRIME_SESSION_OFF, PRIME_OUTCOME_LEASE_EXPIRED, 5001);
    TEST_ASSERT_EQUAL_UINT8(PRIME_TIMEOUT, lastPrimeState);
}

void test_disconnect_stops_only_the_owning_display_hold() {
    start(1, MACHINE_PRIME_FAUCET);
    machinePrimeSessionSourceDisconnected(MACHINE_PRIME_ENCLOSURE);
    expectWet(1);
    host::now += 10;
    machinePrimeSessionSourceDisconnected(MACHINE_PRIME_FAUCET);
    expectParked();
    expectOutcome(PRIME_SESSION_READY, PRIME_OUTCOME_TIMEOUT, 10);
}

void test_prime_deadline_and_valve_park_survive_clock_wrap() {
    host::now = UINT32_MAX - 1000;
    start();
    runAt(999);
    expectWet(0);
    runAt(1000);
    expectParked();
    expectOutcome(PRIME_SESSION_READY, PRIME_OUTCOME_TIMEOUT, 2001);
}

void test_legacy_prime_uses_same_wet_sequence_and_stop() {
    TEST_ASSERT_TRUE(machinePrimeBegin(1));
    TEST_ASSERT_EQUAL_HEX16(dispensePair(1), machineValvesOpen());
    TEST_ASSERT_EQUAL_UINT32(255, host::duties[PIN_PUMP_B]);
    TEST_ASSERT_FALSE(lastEventSessionOwned);
    host::now += 100;
    machinePrimeEnd();
    expectParked();
    TEST_ASSERT_EQUAL_UINT8(PRIME_STOPPED, lastPrimeState);
    TEST_ASSERT_EQUAL_UINT32(100, lastPrimeElapsed);
    TEST_ASSERT_FALSE(lastEventSessionOwned);
}

void test_busy_and_invalid_admission_preserve_the_active_operation() {
    TEST_ASSERT_FALSE(machinePrimeBegin(2));
    TEST_ASSERT_TRUE(machineFillBegin(0));
    const uint16_t fillValves = machineValvesOpen();
    const size_t count = host::events.size();
    TEST_ASSERT_TRUE(machinePrimeSessionActivate(1, kSession));
    TEST_ASSERT_FALSE(machinePrimeSessionHoldBegin(MACHINE_PRIME_FAUCET, 1, kSession, kHold));
    TEST_ASSERT_TRUE(machineIsFilling());
    TEST_ASSERT_EQUAL_HEX16(fillValves, machineValvesOpen());
    TEST_ASSERT_EQUAL_UINT32(255, host::duties[PIN_PUMP_A]);
    TEST_ASSERT_EQUAL_UINT32(0, host::duties[PIN_PUMP_B]);
    TEST_ASSERT_EQUAL_UINT32(count, host::events.size());
    expectOutcome(PRIME_SESSION_READY, PRIME_OUTCOME_REFUSED, 0);
}

void test_unverified_io_refuses_both_prime_entry_points() {
    host::bus.failRead(pcba::MCP_RESERVOIR_A, 0x00);
    MachineIoStatus status;
    TEST_ASSERT_FALSE(machineReadIoStatus(status));
    host::events.clear();
    TEST_ASSERT_FALSE(machinePrimeBegin(0));
    TEST_ASSERT_TRUE(machinePrimeSessionActivate(1, kSession));
    TEST_ASSERT_FALSE(machinePrimeSessionHoldBegin(MACHINE_PRIME_FAUCET, 1, kSession, kHold));
    TEST_ASSERT_EQUAL_UINT32(0, host::events.size());
    expectParked();
    expectOutcome(PRIME_SESSION_READY, PRIME_OUTCOME_REFUSED, 0);
}

void test_valve_open_write_failure_never_starts_pump_and_parks_partial_pair() {
    host::bus.failWrite(pcba::MCP_RESERVOIR_B, host::kOlatA, 0x40);
    TEST_ASSERT_TRUE(machinePrimeSessionActivate(1, kSession));
    TEST_ASSERT_FALSE(machinePrimeSessionHoldBegin(MACHINE_PRIME_FAUCET, 1, kSession, kHold));
    expectParked();
    TEST_ASSERT_EQUAL_UINT32(host::events.size(), firstDuty(255));
    TEST_ASSERT_FALSE(machineIoReady());
    expectOutcome(PRIME_SESSION_READY, PRIME_OUTCOME_REFUSED, 0);
}

void test_valve_open_readback_failure_never_starts_pump() {
    host::bus.failRead(pcba::MCP_RESERVOIR_B, host::kOlatA);
    TEST_ASSERT_FALSE(machinePrimeBegin(1));
    expectParked();
    TEST_ASSERT_EQUAL_UINT32(host::events.size(), firstDuty(255));
    TEST_ASSERT_FALSE(machineIoReady());
}

void test_pwm_attachment_failure_closes_the_opened_pair() {
    host::attachSucceeds = false;
    TEST_ASSERT_TRUE(machinePrimeSessionActivate(0, kSession));
    TEST_ASSERT_FALSE(machinePrimeSessionHoldBegin(MACHINE_PRIME_ENCLOSURE, 0, kSession, kHold));
    expectParked();
    expectOutcome(PRIME_SESSION_READY, PRIME_OUTCOME_REFUSED, 0);
}

void test_reed_fault_parks_motor_before_expander_fault_cleanup() {
    start(1, MACHINE_PRIME_FAUCET);
    host::bus.failRead(pcba::MCP_RESERVOIR_A, host::kGpioB);
    runAt(host::now + 250);
    expectParked();
    TEST_ASSERT_FALSE(machineIoReady());
    TEST_ASSERT_EQUAL(pcba::Fault::BusReadFailed, pcba::expanders().lastFault());
    TEST_ASSERT_EQUAL_UINT8(PRIME_REFUSED, lastPrimeState);
    expectOutcome(PRIME_SESSION_READY, PRIME_OUTCOME_REFUSED, 250);
    TEST_ASSERT_FALSE(machinePrimeSessionHoldBegin(MACHINE_PRIME_FAUCET, 1, kSession, kHold + 1));
}

void test_initial_reed_failure_never_opens_a_path_or_starts_a_motor() {
    host::bus.failRead(pcba::MCP_RESERVOIR_B, host::kGpioB);
    TEST_ASSERT_TRUE(machinePrimeSessionActivate(1, kSession));
    TEST_ASSERT_FALSE(machinePrimeSessionHoldBegin(MACHINE_PRIME_FAUCET, 1, kSession, kHold));
    expectParked();
    TEST_ASSERT_EQUAL_UINT32(host::events.size(), firstDuty(255));
    expectOutcome(PRIME_SESSION_READY, PRIME_OUTCOME_REFUSED, 0);
}

void test_verified_fault_park_is_terminal_even_if_configuration_remains_ready() {
    start();
    TEST_ASSERT_FALSE(pcba::expanders().apply(pcba::ExpanderOutputs(0x000f, false)));
    TEST_ASSERT_TRUE(machineIoReady());
    TEST_ASSERT_EQUAL_UINT32(0, host::duties[PIN_PUMP_A]);
    TEST_ASSERT_EQUAL(pcba::Fault::InvalidOutputPlan, pcba::expanders().lastFault());
    runAt(host::now + 100);
    expectParked();
    expectOutcome(PRIME_SESSION_READY, PRIME_OUTCOME_REFUSED, 0);
    TEST_ASSERT_TRUE(machinePrimeSessionHoldBegin(MACHINE_PRIME_ENCLOSURE, 0, kSession, kHold + 1));
    expectWet(0);
}

void test_wet_prime_updates_only_selected_reservoir_as_falling() {
    host::bus.at(pcba::MCP_RESERVOIR_A, host::kGpioB) = 0xf7;
    host::bus.at(pcba::MCP_RESERVOIR_B, host::kGpioB) = 0xf7;
    start(1);
    MachineLevels levels;
    machineLevels(levels);
    TEST_ASSERT_EQUAL_UINT8(4, levels.level[0]);
    TEST_ASSERT_EQUAL_UINT8(4, levels.level[1]);
    host::bus.at(pcba::MCP_RESERVOIR_A, host::kGpioB) = 0xff;
    host::bus.at(pcba::MCP_RESERVOIR_B, host::kGpioB) = 0xff;
    runAt(host::now + 250);
    machineLevels(levels);
    TEST_ASSERT_TRUE(levels.valid);
    TEST_ASSERT_EQUAL_UINT8(4, levels.level[0]);
    TEST_ASSERT_EQUAL_UINT8(3, levels.level[1]);
    machineStop();
    TEST_ASSERT_TRUE(machinePumpRun(0, 500));
    TEST_ASSERT_EQUAL(machine_policy::LevelMotion::Still, levelMotionFor(0));
    TEST_ASSERT_EQUAL(machine_policy::LevelMotion::Still, levelMotionFor(1));
}

void test_refill_and_automatic_pour_cannot_join_a_wet_prime() {
    start(1);
    machineSimReeds(true, false);
    machineFlowSimulate(8, 5000);
    const uint32_t began = host::now;
    for (uint32_t elapsed = 500; elapsed <= 2000; elapsed += 500) {
        host::now = began + elapsed;
        TEST_ASSERT_TRUE(machinePrimeSessionHoldTick(MACHINE_PRIME_ENCLOSURE, 1, kSession, kHold));
        machineService();
        expectWet(1);
        TEST_ASSERT_FALSE(machineIsPouring());
    }
    MachineThermal thermal;
    machineThermal(thermal);
    TEST_ASSERT_EQUAL_UINT8(static_cast<uint8_t>(machine_policy::RefillState::Queued),
                          thermal.refillState);
    TEST_ASSERT_FALSE(thermal.refillRelay);
    machineFlowSimulate(0, 0);
    machineStop();
    expectParked();
}

void test_active_refill_refuses_prime_without_changing_its_outputs() {
    machineSimReeds(true, false);
    machineService();
    runAt(host::now + machine_policy::kRefillDebounceMs);
    TEST_ASSERT_EQUAL(ST_REFILLING, machineState());
    TEST_ASSERT_FALSE(machinePrimeBegin(0));
    TEST_ASSERT_EQUAL_HEX16(machine_policy::valveBit(machine_policy::Valve::K), machineValvesOpen());
    MachineThermal thermal;
    machineThermal(thermal);
    TEST_ASSERT_TRUE(thermal.refillRelay);
    TEST_ASSERT_EQUAL_UINT32(0, host::duties[PIN_PUMP_A]);
    machineStop();
    expectParked();
}

void test_cold_fan_is_preserved_on_prime_open_and_normal_close() {
    machineSimThermal(6.0f, true, 5.0f, true);
    runAt(host::now + machine_policy::kMinOffMs);
    MachineThermal thermal;
    machineThermal(thermal);
    TEST_ASSERT_TRUE(thermal.compressorRelay);
    TEST_ASSERT_TRUE(pcba::expanders().currentOutputs().condenserFan);
    start();
    expectWet(0);
    TEST_ASSERT_TRUE(pcba::expanders().currentOutputs().condenserFan);
    machineStop();
    expectParked();
    TEST_ASSERT_TRUE(pcba::expanders().currentOutputs().condenserFan);
}

void test_cold_loop_write_failure_stops_prime_in_the_same_service_pass() {
    machineSimThermal(6.0f, true, 5.0f, true);
    runAt(host::now + machine_policy::kMinOffMs - 1000);
    start();
    host::bus.failWrite(pcba::MCP_RESERVOIR_B, host::kOlatA, 0x08);
    runAt(host::now + 1000);
    expectParked();
    TEST_ASSERT_FALSE(machineIoReady());
    expectOutcome(PRIME_SESSION_READY, PRIME_OUTCOME_REFUSED, 1000);
    TEST_ASSERT_EQUAL(pcba::Fault::BusWriteFailed, pcba::expanders().lastFault());
}

void test_console_health_fault_stops_motor_synchronously_then_publishes() {
    start();
    host::now += 100;
    host::bus.at(pcba::MCP_RESERVOIR_A, 0x0d) = 0;
    MachineIoStatus status;
    TEST_ASSERT_FALSE(machineReadIoStatus(status));
    TEST_ASSERT_EQUAL_UINT32(0, host::duties[PIN_PUMP_A]);
    TEST_ASSERT_EQUAL_HEX16(0, machineValvesOpen());
    TEST_ASSERT_FALSE(host::pumpClosedAgainstDrive);
    TEST_ASSERT_EQUAL_UINT8(PRIME_SESSION_RUNNING, session().phase);
    machineService();
    expectParked();
    expectOutcome(PRIME_SESSION_READY, PRIME_OUTCOME_REFUSED, 100);
    TEST_ASSERT_EQUAL(SND_FAULT, host::sounding);
}

void test_cancel_after_immediate_io_stop_retains_actual_run_time() {
    start(1, MACHINE_PRIME_FAUCET);
    host::now += 100;
    host::bus.failRead(pcba::MCP_RESERVOIR_B, 0x00);
    MachineIoStatus status;
    TEST_ASSERT_FALSE(machineReadIoStatus(status));
    host::now += 500;
    TEST_ASSERT_EQUAL_UINT32(100, machinePumpElapsedMs());
    TEST_ASSERT_EQUAL_UINT32(100, session().elapsedMs);
    TEST_ASSERT_TRUE(machinePrimeSessionCancel(kSession));
    expectParked();
    expectOutcome(PRIME_SESSION_OFF, PRIME_OUTCOME_CANCELED, 100);
    TEST_ASSERT_EQUAL_UINT32(100, lastPrimeElapsed);
    TEST_ASSERT_EQUAL_UINT8(PRIME_REFUSED, lastPrimeState);
}

void test_valve_close_failure_cannot_leave_motor_running_or_report_success() {
    start(1, MACHINE_PRIME_FAUCET);
    host::bus.failWrite(pcba::MCP_RESERVOIR_A, host::kOlatA, 0);
    host::now += 100;
    TEST_ASSERT_TRUE(machinePrimeSessionHoldEnd(MACHINE_PRIME_FAUCET, 1, kSession, kHold));
    expectParked();
    TEST_ASSERT_FALSE(machineIoReady());
    TEST_ASSERT_EQUAL_UINT8(PRIME_REFUSED, lastPrimeState);
    expectOutcome(PRIME_SESSION_READY, PRIME_OUTCOME_REFUSED, 100);
}

void test_gas_trip_stops_wet_hold_and_refuses_new_admission() {
    start();
    const uint32_t began = host::now;
    host::gasMv = 2000;
    runAt(began + 1);
    expectWet(0);
    runAt(began + 501);
    expectParked();
    TEST_ASSERT_TRUE(machineGasTripped());
    TEST_ASSERT_EQUAL(SND_ALARM, host::sounding);
    expectOutcome(PRIME_SESSION_READY, PRIME_OUTCOME_REFUSED, 501);
    host::events.clear();
    TEST_ASSERT_FALSE(machinePrimeBegin(1));
    TEST_ASSERT_FALSE(machinePrimeSessionHoldBegin(MACHINE_PRIME_ENCLOSURE, 0, kSession, kHold + 1));
    TEST_ASSERT_EQUAL_UINT32(0, host::events.size());
}

void test_console_motor_check_stays_bounded_without_valves_or_prime_fault_hook() {
    TEST_ASSERT_TRUE(machinePumpRun(1, 500));
    TEST_ASSERT_EQUAL_HEX16(0, machineValvesOpen());
    TEST_ASSERT_FALSE(machineDispenseWindowOpen());
    host::bus.failRead(pcba::MCP_RESERVOIR_A, 0x00);
    MachineIoStatus status;
    TEST_ASSERT_FALSE(machineReadIoStatus(status));
    TEST_ASSERT_EQUAL_UINT32(255, host::duties[PIN_PUMP_B]);
    runAt(host::now + 500);
    expectParked();
    TEST_ASSERT_EQUAL_UINT32(1, pumpDoneCount);
    TEST_ASSERT_EQUAL_UINT32(0, primeEventCount);
}

void test_selftest_motor_step_remains_an_individual_load() {
    TEST_ASSERT_TRUE(machineSelfTestBegin());
    uint32_t time = host::now;
    // Eleven valves, their gaps, then the fan and its gap, lead to pump A.
    for (uint8_t step = 0; step < machine_policy::kValveCount + 1; ++step) {
        time += step < machine_policy::kValveCount ? 250 : 1000;
        runAt(time);
        time += 250;
        runAt(time);
    }
    TEST_ASSERT_EQUAL(ST_SELFTEST, machineState());
    TEST_ASSERT_EQUAL_HEX16(0, machineValvesOpen());
    TEST_ASSERT_EQUAL_UINT32(255, host::duties[PIN_PUMP_A]);
    TEST_ASSERT_EQUAL_UINT32(0, host::duties[PIN_PUMP_B]);
    machineSelfTestStop();
    expectParked();
}

}  // namespace

void setUp() {
    static uint32_t bootMs = 1000;
    host::now = bootMs;
    bootMs += 1000000;
    host::gasMv = 0;
    host::attachSucceeds = true;
    host::pumpClosedAgainstDrive = false;
    memset(host::duties, 0, sizeof(host::duties));
    memset(host::modes, 0, sizeof(host::modes));
    host::bus.reset();
    // These file-local caches normally start fresh on each appliance boot.
    gasTrip = gasRaw = false;
    gasChanged = 0;
    reedCacheValid = false;
    reedIdleMs = 0;
    reservoirLevel[0] = reservoirLevel[1] = machine_policy::ReservoirLevel();
    machineSimClear();
    machineFlowSimulate(0, 0);
    machineOnPrimeState = onPrime;
    machineOnPumpDone = onPumpDone;
    machineBegin();
    TEST_ASSERT_TRUE(machineIoReady());
    host::events.clear();
    lastPrimeState = 0xff;
    lastPrimeElapsed = 0;
    lastEventSessionOwned = false;
    primeEventCount = pumpDoneCount = 0;
}

void tearDown() { TEST_ASSERT_FALSE(host::pumpClosedAgainstDrive); }

int main(int, char **) {
    UNITY_BEGIN();
    RUN_TEST(test_ready_and_cancel_ready_drive_nothing);
    RUN_TEST(test_both_channels_open_the_complete_pair_before_forward_drive);
    RUN_TEST(test_duplicate_start_does_not_restart_the_clock_or_actuators);
    RUN_TEST(test_competing_display_and_stale_tokens_do_not_change_a_wet_hold);
    RUN_TEST(test_stop_before_start_cannot_open_a_delayed_wet_path);
    RUN_TEST(test_cancel_and_general_stop_park_before_terminal_publication);
    RUN_TEST(test_tick_timeout_closes_pair_at_exact_grace_plus_one);
    RUN_TEST(test_regular_ticks_stop_and_lock_at_the_hard_ceiling);
    RUN_TEST(test_lease_expiry_stops_a_faucet_hold_with_live_ticks);
    RUN_TEST(test_disconnect_stops_only_the_owning_display_hold);
    RUN_TEST(test_prime_deadline_and_valve_park_survive_clock_wrap);
    RUN_TEST(test_legacy_prime_uses_same_wet_sequence_and_stop);
    RUN_TEST(test_busy_and_invalid_admission_preserve_the_active_operation);
    RUN_TEST(test_unverified_io_refuses_both_prime_entry_points);
    RUN_TEST(test_valve_open_write_failure_never_starts_pump_and_parks_partial_pair);
    RUN_TEST(test_valve_open_readback_failure_never_starts_pump);
    RUN_TEST(test_pwm_attachment_failure_closes_the_opened_pair);
    RUN_TEST(test_reed_fault_parks_motor_before_expander_fault_cleanup);
    RUN_TEST(test_initial_reed_failure_never_opens_a_path_or_starts_a_motor);
    RUN_TEST(test_verified_fault_park_is_terminal_even_if_configuration_remains_ready);
    RUN_TEST(test_wet_prime_updates_only_selected_reservoir_as_falling);
    RUN_TEST(test_refill_and_automatic_pour_cannot_join_a_wet_prime);
    RUN_TEST(test_active_refill_refuses_prime_without_changing_its_outputs);
    RUN_TEST(test_cold_fan_is_preserved_on_prime_open_and_normal_close);
    RUN_TEST(test_cold_loop_write_failure_stops_prime_in_the_same_service_pass);
    RUN_TEST(test_console_health_fault_stops_motor_synchronously_then_publishes);
    RUN_TEST(test_cancel_after_immediate_io_stop_retains_actual_run_time);
    RUN_TEST(test_valve_close_failure_cannot_leave_motor_running_or_report_success);
    RUN_TEST(test_gas_trip_stops_wet_hold_and_refuses_new_admission);
    RUN_TEST(test_console_motor_check_stays_bounded_without_valves_or_prime_fault_hook);
    RUN_TEST(test_selftest_motor_step_remains_an_individual_load);
    return UNITY_END();
}
