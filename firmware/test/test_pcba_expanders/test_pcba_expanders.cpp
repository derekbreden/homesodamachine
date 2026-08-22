#include <string.h>

#include <unity.h>

// The production adapter lives in src_appliance rather than a reusable
// library. Include its host-safe implementation so this native test exercises
// the exact code compiled into the appliance; the Arduino Wire adapter itself
// is excluded by its ARDUINO guard.
#include "../../src_appliance/pcba_expanders.cpp"

using namespace pcba;

namespace {

constexpr uint8_t kIodirA = 0x00;
constexpr uint8_t kIodirB = 0x01;
constexpr uint8_t kGppuA  = 0x0c;
constexpr uint8_t kGppuB  = 0x0d;
constexpr uint8_t kGpioB  = 0x13;
constexpr uint8_t kOlatA  = 0x14;

struct RegisterWrite {
    uint8_t address;
    uint8_t reg;
    uint8_t value;
};

class FakeTransport : public Transport {
public:
    FakeTransport()
        : began(false),
          writeCount(0),
          failAddress(0),
          failRegister(0),
          failValue(0),
          writeFailuresRemaining(0),
          readFailureAddress(0),
          readFailureRegister(0),
          readFailuresRemaining(0) {
        memset(registers, 0, sizeof(registers));
        bankOne[0] = bankOne[1] = false;
        registers[0][kIodirA] = registers[0][kIodirB] = 0xff;
        registers[1][kIodirA] = registers[1][kIodirB] = 0xff;
    }

    bool begin() override {
        began = true;
        return true;
    }

    bool writeRegister(uint8_t address, uint8_t reg, uint8_t value) override {
        TEST_ASSERT_TRUE(writeCount < kMaxWrites);
        writes[writeCount++] = {address, reg, value};
        if (writeFailuresRemaining != 0 && address == failAddress &&
            reg == failRegister && value == failValue) {
            --writeFailuresRemaining;
            return false;
        }
        const uint8_t device = index(address);
        const uint8_t mapped = mappedRegister(device, reg);
        registers[device][mapped] = value;
        if (bankOne[device] && reg == 0x05 && (value & 0x80) == 0)
            bankOne[device] = false;
        return true;
    }

    bool readRegister(uint8_t address, uint8_t reg, uint8_t &value) override {
        if (readFailuresRemaining != 0 && address == readFailureAddress &&
            reg == readFailureRegister) {
            --readFailuresRemaining;
            return false;
        }
        const uint8_t device = index(address);
        value = registers[device][mappedRegister(device, reg)];
        return true;
    }

    void clearWrites() { writeCount = 0; }

    size_t firstWrite(uint8_t address, uint8_t reg, uint8_t value) const {
        for (size_t i = 0; i < writeCount; ++i) {
            if (writes[i].address == address && writes[i].reg == reg &&
                writes[i].value == value) return i;
        }
        return writeCount;
    }

    uint8_t &at(uint8_t address, uint8_t reg) {
        return registers[index(address)][reg];
    }

    void setBankOne(uint8_t address) {
        const uint8_t device = index(address);
        bankOne[device] = true;
        registers[device][0x0a] = 0x80;
    }

    bool began;
    static constexpr size_t kMaxWrites = 192;
    RegisterWrite writes[kMaxWrites];
    size_t writeCount;
    uint8_t failAddress;
    uint8_t failRegister;
    uint8_t failValue;
    uint8_t writeFailuresRemaining;
    uint8_t readFailureAddress;
    uint8_t readFailureRegister;
    uint8_t readFailuresRemaining;

private:
    uint8_t registers[2][256];
    bool bankOne[2];

    static uint8_t index(uint8_t address) {
        TEST_ASSERT_TRUE(address == MCP_RESERVOIR_A || address == MCP_RESERVOIR_B);
        return address == MCP_RESERVOIR_A ? 0 : 1;
    }

    uint8_t mappedRegister(uint8_t device, uint8_t reg) const {
        if (!bankOne[device]) return reg;
        if (reg == 0x05) return 0x0a;  // IOCONA
        if (reg == 0x0a) return kOlatA;
        if (reg == 0x14) return 0xfe;  // INTCONB; harmless scratch in this fake
        return reg;
    }
};

uint8_t countBits(uint16_t value) {
    uint8_t count = 0;
    while (value != 0) {
        count += static_cast<uint8_t>(value & 1u);
        value >>= 1;
    }
    return count;
}

void expectEncoding(Valve valve, uint8_t expected20, uint8_t expected21) {
    uint8_t actual20 = 0;
    uint8_t actual21 = 0;
    TEST_ASSERT_TRUE(Expanders::encodeOutputs(
        ExpanderOutputs(valveBit(valve), false), actual20, actual21));
    TEST_ASSERT_EQUAL_HEX8(expected20, actual20);
    TEST_ASSERT_EQUAL_HEX8(expected21, actual21);
}

void test_logical_outputs_follow_the_reversed_pcba_port_a_map() {
    const uint8_t expected20[] = {0x80, 0x40, 0x20, 0x10,
                                  0x08, 0x04, 0x02, 0x01};
    for (uint8_t i = 0; i < 8; ++i)
        expectEncoding(static_cast<Valve>(i), expected20[i], 0);

    expectEncoding(Valve::I, 0, 0x80);
    expectEncoding(Valve::J, 0, 0x40);
    expectEncoding(Valve::K, 0, 0x20);

    uint8_t port20 = 0;
    uint8_t port21 = 0;
    TEST_ASSERT_TRUE(Expanders::encodeOutputs(
        ExpanderOutputs(0, true), port20, port21));
    TEST_ASSERT_EQUAL_HEX8(0, port20);
    TEST_ASSERT_EQUAL_HEX8(0x08, port21);
}

void test_encoder_rejects_unknown_or_over_budget_solenoids() {
    uint8_t port20 = 0xff;
    uint8_t port21 = 0xff;
    TEST_ASSERT_FALSE(Expanders::encodeOutputs(
        ExpanderOutputs(0x000f, false), port20, port21));
    TEST_ASSERT_EQUAL_HEX8(0, port20);
    TEST_ASSERT_EQUAL_HEX8(0, port21);

    TEST_ASSERT_FALSE(Expanders::encodeOutputs(
        ExpanderOutputs(0x0800, false), port20, port21));
}

void test_begin_clears_latches_before_outputs_and_verifies_pullups() {
    FakeTransport bus;
    Expanders expanders(bus);
    TEST_ASSERT_TRUE(expanders.begin());
    TEST_ASSERT_TRUE(bus.began);
    TEST_ASSERT_TRUE(expanders.initialized());
    TEST_ASSERT_TRUE(expanders.outputsKnownParked());

    for (uint8_t address = MCP_RESERVOIR_A; address <= MCP_RESERVOIR_B; ++address) {
        TEST_ASSERT_EQUAL_HEX8(0x00, bus.at(address, kIodirA));
        TEST_ASSERT_EQUAL_HEX8(0xff, bus.at(address, kIodirB));
        TEST_ASSERT_EQUAL_HEX8(0x00, bus.at(address, kGppuA));
        TEST_ASSERT_EQUAL_HEX8(0xff, bus.at(address, kGppuB));
        TEST_ASSERT_EQUAL_HEX8(0x00, bus.at(address, kOlatA));

        const size_t latchCleared = bus.firstWrite(address, kOlatA, 0);
        const size_t madeOutput = bus.firstWrite(address, kIodirA, 0);
        TEST_ASSERT_TRUE(latchCleared < madeOutput);
    }

    Health health;
    TEST_ASSERT_TRUE(expanders.readHealth(health));
    TEST_ASSERT_TRUE(health.configurationVerified);
    TEST_ASSERT_TRUE(health.outputsMatchPlan);
}

void test_begin_recovers_bank_one_and_clears_live_latches_before_normalizing() {
    FakeTransport bus;
    for (uint8_t address = MCP_RESERVOIR_A; address <= MCP_RESERVOIR_B; ++address) {
        bus.setBankOne(address);
        bus.at(address, kIodirA) = 0;
        bus.at(address, kGppuA) = 0xff;
        bus.at(address, kOlatA) = 0xff;
    }

    Expanders expanders(bus);
    TEST_ASSERT_TRUE(expanders.begin());
    TEST_ASSERT_TRUE(expanders.outputsKnownParked());

    for (uint8_t address = MCP_RESERVOIR_A; address <= MCP_RESERVOIR_B; ++address) {
        const size_t bankOneLatchClear = bus.firstWrite(address, 0x0a, 0);
        const size_t bankNormalize = bus.firstWrite(address, 0x05, 0);
        TEST_ASSERT_TRUE(bankOneLatchClear < bankNormalize);
        TEST_ASSERT_EQUAL_HEX8(0, bus.at(address, kOlatA));
        TEST_ASSERT_EQUAL_HEX8(0, bus.at(address, kGppuA));
        TEST_ASSERT_EQUAL_HEX8(0, bus.at(address, kIodirA));
    }
}

void test_park_proves_low_output_pins_not_only_low_latches() {
    FakeTransport bus;
    Expanders expanders(bus);
    TEST_ASSERT_TRUE(expanders.begin());

    // This is the dangerous corrupt state: an input pin with its internal
    // pull-up enabled can source a TBD62083 input despite OLATA already zero.
    for (uint8_t address = MCP_RESERVOIR_A; address <= MCP_RESERVOIR_B; ++address) {
        bus.at(address, kIodirA) = 0xff;
        bus.at(address, kGppuA) = 0xff;
        bus.at(address, kOlatA) = 0;
    }

    TEST_ASSERT_TRUE(expanders.parkAll());
    TEST_ASSERT_TRUE(expanders.outputsKnownParked());
    for (uint8_t address = MCP_RESERVOIR_A; address <= MCP_RESERVOIR_B; ++address) {
        TEST_ASSERT_EQUAL_HEX8(0, bus.at(address, kGppuA));
        TEST_ASSERT_EQUAL_HEX8(0, bus.at(address, kOlatA));
        TEST_ASSERT_EQUAL_HEX8(0, bus.at(address, kIodirA));
    }
}

void test_cross_expander_transition_finishes_global_off_phase_first() {
    FakeTransport bus;
    Expanders expanders(bus);
    TEST_ASSERT_TRUE(expanders.begin());
    TEST_ASSERT_TRUE(expanders.apply(ExpanderOutputs(
        valveBit(Valve::A) | valveBit(Valve::B) | valveBit(Valve::C), false)));

    bus.clearWrites();
    TEST_ASSERT_TRUE(expanders.apply(ExpanderOutputs(
        valveBit(Valve::I) | valveBit(Valve::J) | valveBit(Valve::K), false)));

    const size_t outgoingOff = bus.firstWrite(MCP_RESERVOIR_A, kOlatA, 0x00);
    const size_t incomingOn = bus.firstWrite(MCP_RESERVOIR_B, kOlatA, 0xe0);
    TEST_ASSERT_TRUE(outgoingOff < incomingOn);
}

void test_every_valid_source_target_transition_is_off_before_on_and_in_budget() {
    ValveMask validMasks[232];
    size_t validCount = 0;
    for (ValveMask mask = 0; mask <= machine_policy::kAllValves; ++mask) {
        if (countBits(mask) <= machine_policy::kMaxOpenValves)
            validMasks[validCount++] = mask;
    }
    TEST_ASSERT_EQUAL_UINT32(232, validCount);

    FakeTransport bus;
    Expanders expanders(bus);
    TEST_ASSERT_TRUE(expanders.begin());

    for (size_t sourceIndex = 0; sourceIndex < validCount; ++sourceIndex) {
        for (size_t targetIndex = 0; targetIndex < validCount; ++targetIndex) {
            const ValveMask source = validMasks[sourceIndex];
            const ValveMask target = validMasks[targetIndex];
            TEST_ASSERT_TRUE(expanders.apply(ExpanderOutputs(source, false)));

            uint8_t source20 = 0;
            uint8_t source21 = 0;
            uint8_t target20 = 0;
            uint8_t target21 = 0;
            TEST_ASSERT_TRUE(Expanders::encodeOutputs(
                ExpanderOutputs(source, false), source20, source21));
            TEST_ASSERT_TRUE(Expanders::encodeOutputs(
                ExpanderOutputs(target, false), target20, target21));

            const uint8_t outgoing20 = source20 & static_cast<uint8_t>(~target20);
            const uint8_t outgoing21 = source21 & static_cast<uint8_t>(~target21);
            const uint8_t incoming20 = target20 & static_cast<uint8_t>(~source20);
            const uint8_t incoming21 = target21 & static_cast<uint8_t>(~source21);
            uint8_t live20 = source20;
            uint8_t live21 = source21;

            bus.clearWrites();
            TEST_ASSERT_TRUE(expanders.apply(ExpanderOutputs(target, false)));
            for (size_t i = 0; i < bus.writeCount; ++i) {
                const RegisterWrite &write = bus.writes[i];
                if (write.reg != kOlatA) continue;

                const bool addsIncoming =
                    (write.address == MCP_RESERVOIR_A &&
                     (write.value & incoming20 & static_cast<uint8_t>(~live20)) != 0) ||
                    (write.address == MCP_RESERVOIR_B &&
                     (write.value & incoming21 & static_cast<uint8_t>(~live21)) != 0);
                if (addsIncoming) {
                    TEST_ASSERT_EQUAL_HEX8(0, live20 & outgoing20);
                    TEST_ASSERT_EQUAL_HEX8(0, live21 & outgoing21);
                }

                if (write.address == MCP_RESERVOIR_A) live20 = write.value;
                else                                  live21 = write.value;
                TEST_ASSERT_TRUE(countBits(live20) + countBits(live21 & 0xe0) <=
                                 machine_policy::kMaxOpenValves);
            }

            TEST_ASSERT_EQUAL_HEX8(target20, live20);
            TEST_ASSERT_EQUAL_HEX8(target21, live21);
        }
    }
}

void test_failed_output_write_parks_both_devices_and_requires_rebegin() {
    FakeTransport bus;
    Expanders expanders(bus);
    TEST_ASSERT_TRUE(expanders.begin());
    TEST_ASSERT_TRUE(expanders.apply(ExpanderOutputs(
        valveBit(Valve::A) | valveBit(Valve::B) | valveBit(Valve::C), false)));

    bus.failAddress = MCP_RESERVOIR_B;
    bus.failRegister = kOlatA;
    bus.failValue = 0xe0;
    bus.writeFailuresRemaining = 1;
    TEST_ASSERT_FALSE(expanders.apply(ExpanderOutputs(
        valveBit(Valve::I) | valveBit(Valve::J) | valveBit(Valve::K), false)));

    TEST_ASSERT_FALSE(expanders.initialized());
    TEST_ASSERT_TRUE(expanders.outputsKnownParked());
    TEST_ASSERT_EQUAL_HEX8(0, bus.at(MCP_RESERVOIR_A, kOlatA));
    TEST_ASSERT_EQUAL_HEX8(0, bus.at(MCP_RESERVOIR_B, kOlatA));
}

void test_invalid_plan_fails_parked_without_damaging_configuration() {
    FakeTransport bus;
    Expanders expanders(bus);
    TEST_ASSERT_TRUE(expanders.begin());
    TEST_ASSERT_TRUE(expanders.apply(ExpanderOutputs(valveBit(Valve::A), true)));

    TEST_ASSERT_FALSE(expanders.apply(ExpanderOutputs(0x000f, false)));
    TEST_ASSERT_TRUE(expanders.initialized());
    TEST_ASSERT_TRUE(expanders.outputsKnownParked());
    TEST_ASSERT_EQUAL(Fault::InvalidOutputPlan, expanders.lastFault());
}

void test_failed_park_on_first_device_still_attempts_second_device() {
    FakeTransport bus;
    Expanders expanders(bus);
    TEST_ASSERT_TRUE(expanders.begin());
    bus.at(MCP_RESERVOIR_A, kGppuA) = 0xff;
    bus.clearWrites();
    bus.failAddress = MCP_RESERVOIR_A;
    bus.failRegister = kGppuA;
    bus.failValue = 0;
    bus.writeFailuresRemaining = 1;

    TEST_ASSERT_FALSE(expanders.parkAll());
    TEST_ASSERT_FALSE(expanders.initialized());
    TEST_ASSERT_FALSE(expanders.outputsKnownParked());
    TEST_ASSERT_TRUE(bus.firstWrite(MCP_RESERVOIR_B, kIodirA, 0) < bus.writeCount);
    TEST_ASSERT_EQUAL_HEX8(0, bus.at(MCP_RESERVOIR_B, kGppuA));
    TEST_ASSERT_EQUAL_HEX8(0, bus.at(MCP_RESERVOIR_B, kOlatA));
    TEST_ASSERT_EQUAL_HEX8(0, bus.at(MCP_RESERVOIR_B, kIodirA));
}

void test_reed_snapshot_inverts_active_low_inputs_and_preserves_raw_ports() {
    FakeTransport bus;
    Expanders expanders(bus);
    TEST_ASSERT_TRUE(expanders.begin());
    bus.at(MCP_RESERVOIR_A, kGpioB) = 0xfa;  // A reeds 1 and 3 closed.
    bus.at(MCP_RESERVOIR_B, kGpioB) = 0xce;  // B reed 1 + both carbonator reeds closed.

    ReedSnapshot snapshot;
    TEST_ASSERT_TRUE(expanders.readReeds(snapshot));
    TEST_ASSERT_EQUAL_HEX8(0xfa, snapshot.rawReservoirAPortB);
    TEST_ASSERT_EQUAL_HEX8(0xce, snapshot.rawReservoirBPortB);
    TEST_ASSERT_EQUAL_HEX8(0x05, snapshot.reservoirAClosedMask);
    TEST_ASSERT_EQUAL_HEX8(0x01, snapshot.reservoirBClosedMask);
    TEST_ASSERT_TRUE(snapshot.carbonatorLowClosed);
    TEST_ASSERT_TRUE(snapshot.carbonatorHighClosed);
}

void test_failed_reed_read_parks_outputs_and_requires_rebegin() {
    FakeTransport bus;
    Expanders expanders(bus);
    TEST_ASSERT_TRUE(expanders.begin());
    TEST_ASSERT_TRUE(expanders.apply(ExpanderOutputs(valveBit(Valve::K), false)));
    bus.readFailureAddress = MCP_RESERVOIR_B;
    bus.readFailureRegister = kGpioB;
    bus.readFailuresRemaining = 1;

    ReedSnapshot snapshot;
    TEST_ASSERT_FALSE(expanders.readReeds(snapshot));
    TEST_ASSERT_FALSE(expanders.initialized());
    TEST_ASSERT_TRUE(expanders.outputsKnownParked());
    TEST_ASSERT_EQUAL(Fault::BusReadFailed, expanders.lastFault());
    TEST_ASSERT_EQUAL_HEX8(MCP_RESERVOIR_B, expanders.lastFaultAddress());
    TEST_ASSERT_EQUAL_HEX8(kGpioB, expanders.lastFaultRegister());
    TEST_ASSERT_EQUAL_HEX8(0, bus.at(MCP_RESERVOIR_B, kOlatA));
}

void test_health_configuration_mismatch_fails_parked() {
    FakeTransport bus;
    Expanders expanders(bus);
    TEST_ASSERT_TRUE(expanders.begin());
    TEST_ASSERT_TRUE(expanders.apply(ExpanderOutputs(valveBit(Valve::A), false)));
    bus.at(MCP_RESERVOIR_B, kGppuB) = 0;

    Health health;
    TEST_ASSERT_FALSE(expanders.readHealth(health));
    TEST_ASSERT_FALSE(expanders.initialized());
    TEST_ASSERT_TRUE(expanders.outputsKnownParked());
    TEST_ASSERT_EQUAL(Fault::RegisterMismatch, expanders.lastFault());
    TEST_ASSERT_EQUAL_HEX8(0, bus.at(MCP_RESERVOIR_A, kOlatA));
}

}  // namespace

void setUp() {}
void tearDown() {}

int main(int, char **) {
    UNITY_BEGIN();
    RUN_TEST(test_logical_outputs_follow_the_reversed_pcba_port_a_map);
    RUN_TEST(test_encoder_rejects_unknown_or_over_budget_solenoids);
    RUN_TEST(test_begin_clears_latches_before_outputs_and_verifies_pullups);
    RUN_TEST(test_begin_recovers_bank_one_and_clears_live_latches_before_normalizing);
    RUN_TEST(test_park_proves_low_output_pins_not_only_low_latches);
    RUN_TEST(test_cross_expander_transition_finishes_global_off_phase_first);
    RUN_TEST(test_every_valid_source_target_transition_is_off_before_on_and_in_budget);
    RUN_TEST(test_failed_output_write_parks_both_devices_and_requires_rebegin);
    RUN_TEST(test_invalid_plan_fails_parked_without_damaging_configuration);
    RUN_TEST(test_failed_park_on_first_device_still_attempts_second_device);
    RUN_TEST(test_reed_snapshot_inverts_active_low_inputs_and_preserves_raw_ports);
    RUN_TEST(test_failed_reed_read_parks_outputs_and_requires_rebegin);
    RUN_TEST(test_health_configuration_mismatch_fails_parked);
    return UNITY_END();
}
