#include "../machine_host/machine_host.h"

// The sweep as the production machine runs it: machine.cpp whole, with the meter, the reeds,
// the relays and the flash replaced by the host's.
namespace {

const uint32_t kStep = machine_policy::kFlowSampleMs;

void runAt(uint32_t time) {
    host::now = time;
    machineService();
}

// Carry the loop forward a flow reading at a time.
void sampleFor(uint32_t ms) {
    for (uint32_t t = kStep; t <= ms; t += kStep) runAt(host::now + kStep);
}

// The carbonator's two reeds as the expander reads them: a closed reed pulls its pin low.
void carbonatorReeds(bool low, bool high) {
    uint8_t &pins = host::bus.at(pcba::MCP_RESERVOIR_B, host::kGpioB);
    pins |= 0x30;
    if (low) pins &= static_cast<uint8_t>(~0x10);
    if (high) pins &= static_cast<uint8_t>(~0x20);
}

// The power goes and comes back: every load dropped, nothing in RAM, the clock at zero.
void restart() {
    host::now = 0;
    memset(host::duties, 0, sizeof(host::duties));
    memset(host::modes, 0, sizeof(host::modes));
    reedCacheValid = false;
    reedIdleMs = 0;
    machineFlowSimulate(0, 0);
    machineBegin();
}

bool refillRelayClosed() {
    MachineThermal thermal;
    machineThermal(thermal);
    return thermal.refillRelay;
}

uint8_t refillStateNow() {
    MachineThermal thermal;
    machineThermal(thermal);
    return thermal.refillState;
}

MachineSweep sweepNow() {
    MachineSweep s;
    machineSweep(s);
    return s;
}

std::vector<machine_log::Entry> notedOf(machine_log::Kind kind) {
    std::vector<machine_log::Entry> out;
    for (const machine_log::Entry &entry : host::noted)
        if (entry.kind == kind) out.push_back(entry);
    return out;
}

// Gas on the meter at this many pulses a reading until the sweep's target is met.
const uint32_t kGas = 40;
void holdTheLeverUntilDone() {
    machineFlowSimulate(kGas, 600000);
    for (uint32_t guard = 0; guard < 2000 && !sweepNow().done; guard++) runAt(host::now + kStep);
    TEST_ASSERT_TRUE(sweepNow().done);
}

void letTheLeverGo() { machineFlowSimulate(0, 0); }

void test_a_machine_that_owes_no_sweep_pours_as_it_did() {
    TEST_ASSERT_FALSE(sweepNow().owed);
    TEST_ASSERT_EQUAL_UINT8(NOTICE_NONE, machineNotice());
    machineFlowSimulate(6, 5000);
    sampleFor(200);
    TEST_ASSERT_TRUE(machineIsPouring());
    TEST_ASSERT_EQUAL_UINT32(0, host::sweepOwedWrites);
}

void test_a_sweep_that_is_owed_holds_the_refill_and_opens_no_pour() {
    TEST_ASSERT_TRUE(machineSweepOwe());
    TEST_ASSERT_TRUE(host::sweepOwedInFlash);
    TEST_ASSERT_EQUAL_UINT8(NOTICE_SWEEP, machineNotice());

    // A fill asked for stays an ask: no water goes in over the air.
    machineRefillRequest();
    sampleFor(5000);
    TEST_ASSERT_EQUAL(ST_IDLE, machineState());
    TEST_ASSERT_FALSE(refillRelayClosed());
    TEST_ASSERT_EQUAL_UINT16(0, machineValvesOpen());

    // Pulses on the meter are gas: counted, and no flavor follows them.
    machineFlowSimulate(6, 2000);
    for (uint32_t t = kStep; t <= 3000; t += kStep) {
        runAt(host::now + kStep);
        TEST_ASSERT_FALSE(machineIsPouring());
        TEST_ASSERT_EQUAL_UINT16(0, machineValvesOpen());
    }
    TEST_ASSERT_TRUE(sweepNow().pulses > 0);
    TEST_ASSERT_EQUAL_UINT32(0, notedOf(machine_log::Kind::Pour).size());
    TEST_ASSERT_FALSE(refillRelayClosed());
}

void test_gas_through_the_tank_is_counted_and_the_lever_let_go_brings_the_first_fill() {
    TEST_ASSERT_TRUE(machineSweepOwe());
    machineFlowSimulate(kGas, 600000);
    sampleFor(1000);
    TEST_ASSERT_TRUE(sweepNow().flowing);
    TEST_ASSERT_EQUAL_UINT32(1, host::played[SND_ENGAGE]);
    TEST_ASSERT_EQUAL_UINT8(NOTICE_SWEEP, machineNotice());

    holdTheLeverUntilDone();
    TEST_ASSERT_EQUAL_UINT8(NOTICE_SWEEP_DONE, machineNotice());
    TEST_ASSERT_EQUAL_UINT32(1, host::played[SND_CHIME]);
    const std::vector<machine_log::Entry> sweeps = notedOf(machine_log::Kind::Sweep);
    TEST_ASSERT_EQUAL_UINT32(1, sweeps.size());
    TEST_ASSERT_EQUAL_UINT8(static_cast<uint8_t>(machine_log::SweepEnd::Done), sweeps[0].detail);
    TEST_ASSERT_EQUAL_UINT32(machine_policy::kSweepTargetPulses, sweeps[0].b);
    TEST_ASSERT_TRUE(sweeps[0].a > 0);

    // The lever is still down: gas still flows, and no water is sent out after it.
    sampleFor(4000);
    TEST_ASSERT_TRUE(sweepNow().owed);
    TEST_ASSERT_TRUE(host::sweepOwedInFlash);
    TEST_ASSERT_EQUAL(ST_IDLE, machineState());
    TEST_ASSERT_FALSE(refillRelayClosed());
    TEST_ASSERT_FALSE(machineIsPouring());

    letTheLeverGo();
    sampleFor(machine_policy::kSweepReleaseMs + 2 * kStep);
    TEST_ASSERT_FALSE(sweepNow().owed);
    TEST_ASSERT_FALSE(host::sweepOwedInFlash);
    sampleFor(1500);
    TEST_ASSERT_EQUAL(ST_REFILLING, machineState());
    TEST_ASSERT_TRUE(refillRelayClosed());
    TEST_ASSERT_TRUE(host::refillOwedInFlash);
    TEST_ASSERT_EQUAL_UINT32(1, notedOf(machine_log::Kind::Sweep).size());
    TEST_ASSERT_EQUAL_UINT32(0, notedOf(machine_log::Kind::Pour).size());

    // Both glasses go on saying Done for a while, and then say nothing.
    TEST_ASSERT_EQUAL_UINT8(NOTICE_SWEEP_DONE, machineNotice());
    sampleFor(kSweepDoneNoticeMs);
    TEST_ASSERT_EQUAL_UINT8(NOTICE_NONE, machineNotice());

    // The fill ends at the high reed like any other, and the machine pours after it.
    carbonatorReeds(false, true);
    sampleFor(2000);
    TEST_ASSERT_EQUAL(ST_IDLE, machineState());
    machineFlowSimulate(6, 5000);
    sampleFor(200);
    TEST_ASSERT_TRUE(machineIsPouring());
}

void test_the_lever_let_go_early_keeps_the_count() {
    TEST_ASSERT_TRUE(machineSweepOwe());
    machineFlowSimulate(kGas, 3000);
    sampleFor(3000);
    const uint32_t counted = sweepNow().pulses;
    TEST_ASSERT_TRUE(counted > 0);
    sampleFor(2000);
    TEST_ASSERT_TRUE(sweepNow().owed);
    TEST_ASSERT_FALSE(sweepNow().flowing);
    TEST_ASSERT_EQUAL_UINT32(counted, sweepNow().pulses);
    TEST_ASSERT_EQUAL_UINT32(1, host::played[SND_RELEASE]);
    TEST_ASSERT_EQUAL_UINT8(NOTICE_SWEEP, machineNotice());
    TEST_ASSERT_EQUAL_UINT32(0, notedOf(machine_log::Kind::Sweep).size());

    holdTheLeverUntilDone();
    TEST_ASSERT_EQUAL_UINT32(2, host::played[SND_ENGAGE]);
}

void test_a_tank_found_to_hold_water_drops_the_sweep() {
    TEST_ASSERT_TRUE(machineSweepOwe());
    carbonatorReeds(true, true);
    sampleFor(machine_policy::kSweepWetMs + 3000);
    TEST_ASSERT_FALSE(sweepNow().owed);
    TEST_ASSERT_FALSE(host::sweepOwedInFlash);
    TEST_ASSERT_EQUAL_UINT8(NOTICE_NONE, machineNotice());
    const std::vector<machine_log::Entry> sweeps = notedOf(machine_log::Kind::Sweep);
    TEST_ASSERT_EQUAL_UINT32(1, sweeps.size());
    TEST_ASSERT_EQUAL_UINT8(static_cast<uint8_t>(machine_log::SweepEnd::Moot), sweeps[0].detail);
    // A full tank is asked for no water.
    TEST_ASSERT_EQUAL(ST_IDLE, machineState());
    TEST_ASSERT_FALSE(host::refillOwedInFlash);
}

void test_a_sweep_cannot_be_owed_over_water() {
    carbonatorReeds(true, false);
    sampleFor(1500);
    TEST_ASSERT_FALSE(machineSweepOwe());
    TEST_ASSERT_FALSE(sweepNow().owed);
    TEST_ASSERT_FALSE(host::sweepOwedInFlash);
}

void test_owing_a_sweep_drops_the_refill_that_was_owed() {
    machineRefillLatch();
    sampleFor(500);
    TEST_ASSERT_EQUAL_UINT8(NOTICE_NO_WATER, machineNotice());
    TEST_ASSERT_TRUE(host::refillOwedInFlash);

    TEST_ASSERT_TRUE(machineSweepOwe());
    sampleFor(500);
    TEST_ASSERT_EQUAL_UINT8(NOTICE_SWEEP, machineNotice());
    TEST_ASSERT_EQUAL_UINT8(static_cast<uint8_t>(machine_policy::RefillState::Idle), refillStateNow());
    TEST_ASSERT_FALSE(host::refillOwedInFlash);
    TEST_ASSERT_EQUAL_UINT32(0, host::refillSpentInFlash);
}

void test_a_sweep_owed_when_the_power_went_is_owed_still() {
    TEST_ASSERT_TRUE(machineSweepOwe());
    machineFlowSimulate(kGas, 2000);
    sampleFor(2000);
    TEST_ASSERT_TRUE(sweepNow().pulses > 0);

    restart();
    TEST_ASSERT_TRUE(sweepNow().owed);
    TEST_ASSERT_EQUAL_UINT32(0, sweepNow().pulses);
    TEST_ASSERT_EQUAL_UINT8(NOTICE_SWEEP, machineNotice());
    sampleFor(5000);
    TEST_ASSERT_EQUAL(ST_IDLE, machineState());
    TEST_ASSERT_FALSE(refillRelayClosed());
}

void test_power_lost_between_the_target_and_the_lever_leaves_the_sweep_owed() {
    TEST_ASSERT_TRUE(machineSweepOwe());
    holdTheLeverUntilDone();
    TEST_ASSERT_TRUE(host::sweepOwedInFlash);

    restart();
    TEST_ASSERT_TRUE(sweepNow().owed);
    TEST_ASSERT_FALSE(sweepNow().done);
    TEST_ASSERT_EQUAL_UINT8(NOTICE_SWEEP, machineNotice());
    TEST_ASSERT_FALSE(host::refillOwedInFlash);
}

void test_a_sweep_given_up_at_the_machine_fills_without_it() {
    TEST_ASSERT_TRUE(machineSweepOwe());
    machineFlowSimulate(kGas, 1000);
    sampleFor(1500);
    TEST_ASSERT_TRUE(machineSweepSkip());
    TEST_ASSERT_FALSE(sweepNow().owed);
    TEST_ASSERT_FALSE(host::sweepOwedInFlash);
    TEST_ASSERT_EQUAL_UINT8(NOTICE_NONE, machineNotice());
    const std::vector<machine_log::Entry> sweeps = notedOf(machine_log::Kind::Sweep);
    TEST_ASSERT_EQUAL_UINT32(1, sweeps.size());
    TEST_ASSERT_EQUAL_UINT8(static_cast<uint8_t>(machine_log::SweepEnd::Skipped), sweeps[0].detail);
    TEST_ASSERT_TRUE(sweeps[0].b > 0);

    sampleFor(1500);
    TEST_ASSERT_EQUAL(ST_REFILLING, machineState());
    TEST_ASSERT_FALSE(machineSweepSkip());
}

void test_a_sweep_given_up_with_the_lever_down_waits_for_the_lever() {
    TEST_ASSERT_TRUE(machineSweepOwe());
    machineFlowSimulate(kGas, 600000);
    sampleFor(1000);
    TEST_ASSERT_TRUE(sweepNow().flowing);

    TEST_ASSERT_TRUE(machineSweepSkip());
    TEST_ASSERT_TRUE(sweepNow().owed);
    TEST_ASSERT_TRUE(sweepNow().done);
    TEST_ASSERT_TRUE(host::sweepOwedInFlash);
    TEST_ASSERT_EQUAL_UINT8(NOTICE_SWEEP_DONE, machineNotice());
    const std::vector<machine_log::Entry> sweeps = notedOf(machine_log::Kind::Sweep);
    TEST_ASSERT_EQUAL_UINT32(1, sweeps.size());
    TEST_ASSERT_EQUAL_UINT8(static_cast<uint8_t>(machine_log::SweepEnd::Skipped), sweeps[0].detail);
    TEST_ASSERT_TRUE(sweeps[0].b > 0);

    // The gas still moving opens no pour, and no water is sent out of the open faucet.
    for (uint32_t t = kStep; t <= 4000; t += kStep) {
        runAt(host::now + kStep);
        TEST_ASSERT_FALSE(machineIsPouring());
        TEST_ASSERT_EQUAL_UINT16(0, machineValvesOpen());
        TEST_ASSERT_FALSE(refillRelayClosed());
    }
    TEST_ASSERT_EQUAL_UINT32(0, host::played[SND_CHIME]);

    // Asked again while it waits, it is one sweep given up once.
    TEST_ASSERT_TRUE(machineSweepSkip());
    TEST_ASSERT_EQUAL_UINT32(1, notedOf(machine_log::Kind::Sweep).size());
    TEST_ASSERT_TRUE(sweepNow().owed);

    letTheLeverGo();
    sampleFor(machine_policy::kSweepReleaseMs + 2 * kStep);
    TEST_ASSERT_FALSE(sweepNow().owed);
    TEST_ASSERT_FALSE(host::sweepOwedInFlash);
    sampleFor(1500);
    TEST_ASSERT_EQUAL(ST_REFILLING, machineState());
    TEST_ASSERT_TRUE(refillRelayClosed());
    TEST_ASSERT_EQUAL_UINT32(0, notedOf(machine_log::Kind::Pour).size());
}

void test_a_sweep_given_up_after_its_target_still_waits_for_the_lever() {
    TEST_ASSERT_TRUE(machineSweepOwe());
    holdTheLeverUntilDone();

    TEST_ASSERT_TRUE(machineSweepSkip());
    TEST_ASSERT_TRUE(sweepNow().owed);
    sampleFor(4000);
    TEST_ASSERT_EQUAL(ST_IDLE, machineState());
    TEST_ASSERT_FALSE(refillRelayClosed());

    // The target was its end, and stays the one that is noted.
    const std::vector<machine_log::Entry> sweeps = notedOf(machine_log::Kind::Sweep);
    TEST_ASSERT_EQUAL_UINT32(1, sweeps.size());
    TEST_ASSERT_EQUAL_UINT8(static_cast<uint8_t>(machine_log::SweepEnd::Done), sweeps[0].detail);

    letTheLeverGo();
    sampleFor(machine_policy::kSweepReleaseMs + 2 * kStep + 1500);
    TEST_ASSERT_EQUAL(ST_REFILLING, machineState());
    TEST_ASSERT_EQUAL_UINT32(1, notedOf(machine_log::Kind::Sweep).size());
}

void test_a_bench_that_holds_the_notice_off_still_has_the_sweep() {
    TEST_ASSERT_TRUE(machineSweepOwe());
    machineNoticeHold(static_cast<uint8_t>((1u << NOTICE_SWEEP) | (1u << NOTICE_SWEEP_DONE)));
    TEST_ASSERT_EQUAL_UINT8(NOTICE_SWEEP, machineNoticeStanding());
    TEST_ASSERT_EQUAL_UINT8(NOTICE_NONE, machineNotice());

    // The glasses say nothing, and the sweep still holds the water and the flavor.
    machineRefillRequest();
    machineFlowSimulate(6, 2000);
    sampleFor(3000);
    TEST_ASSERT_EQUAL(ST_IDLE, machineState());
    TEST_ASSERT_FALSE(refillRelayClosed());
    TEST_ASSERT_EQUAL_UINT32(0, notedOf(machine_log::Kind::Pour).size());

    holdTheLeverUntilDone();
    TEST_ASSERT_EQUAL_UINT8(NOTICE_SWEEP_DONE, machineNoticeStanding());
    TEST_ASSERT_EQUAL_UINT8(NOTICE_NONE, machineNotice());
    machineNoticeHold(0);
    TEST_ASSERT_EQUAL_UINT8(NOTICE_SWEEP_DONE, machineNotice());
}

void test_a_sweep_forgotten_at_the_bench_asks_for_nothing() {
    TEST_ASSERT_TRUE(machineSweepOwe());
    TEST_ASSERT_TRUE(machineSweepForget());
    TEST_ASSERT_FALSE(host::sweepOwedInFlash);
    sampleFor(5000);
    TEST_ASSERT_EQUAL(ST_IDLE, machineState());
    TEST_ASSERT_FALSE(host::refillOwedInFlash);
    TEST_ASSERT_EQUAL_UINT32(0, notedOf(machine_log::Kind::Sweep).size());
    TEST_ASSERT_FALSE(machineSweepForget());
}

void test_a_sweep_forgotten_with_the_lever_down_opens_no_pour() {
    TEST_ASSERT_TRUE(machineSweepOwe());
    machineFlowSimulate(kGas, 600000);
    sampleFor(1000);
    TEST_ASSERT_TRUE(sweepNow().flowing);

    TEST_ASSERT_TRUE(machineSweepForget());
    TEST_ASSERT_FALSE(sweepNow().owed);
    TEST_ASSERT_FALSE(host::sweepOwedInFlash);
    TEST_ASSERT_EQUAL_UINT8(NOTICE_NONE, machineNoticeStanding());
    TEST_ASSERT_FALSE(machineSweepForget());
    TEST_ASSERT_FALSE(machineSweepSkip());

    // The gas that is still moving is not a pour.
    for (uint32_t t = kStep; t <= 4000; t += kStep) {
        runAt(host::now + kStep);
        TEST_ASSERT_FALSE(machineIsPouring());
        TEST_ASSERT_EQUAL_UINT16(0, machineValvesOpen());
        TEST_ASSERT_EQUAL_UINT8(NOTICE_NONE, machineNoticeStanding());
    }

    // The lever let go hands the meter back, and nothing is asked for.
    letTheLeverGo();
    sampleFor(machine_policy::kSweepReleaseMs + 2 * kStep + 1500);
    TEST_ASSERT_EQUAL(ST_IDLE, machineState());
    TEST_ASSERT_FALSE(refillRelayClosed());
    TEST_ASSERT_FALSE(host::refillOwedInFlash);
    TEST_ASSERT_EQUAL_UINT8(NOTICE_NONE, machineNoticeStanding());
    TEST_ASSERT_EQUAL_UINT32(0, notedOf(machine_log::Kind::Sweep).size());
    TEST_ASSERT_EQUAL_UINT32(0, notedOf(machine_log::Kind::Pour).size());
    machineFlowSimulate(6, 5000);
    sampleFor(200);
    TEST_ASSERT_TRUE(machineIsPouring());
}

void test_a_sweep_owed_again_after_one_forgotten_with_the_lever_down_is_a_whole_sweep() {
    TEST_ASSERT_TRUE(machineSweepOwe());
    machineFlowSimulate(kGas, 600000);
    sampleFor(1000);
    TEST_ASSERT_TRUE(machineSweepForget());

    TEST_ASSERT_TRUE(machineSweepOwe());
    TEST_ASSERT_TRUE(sweepNow().owed);
    TEST_ASSERT_TRUE(host::sweepOwedInFlash);
    TEST_ASSERT_EQUAL_UINT8(NOTICE_SWEEP, machineNoticeStanding());
    holdTheLeverUntilDone();
    letTheLeverGo();
    sampleFor(machine_policy::kSweepReleaseMs + 2 * kStep + 1500);
    TEST_ASSERT_EQUAL(ST_REFILLING, machineState());
}

}  // namespace

void setUp() {
    static uint32_t bootMs = 1000;
    host::now = bootMs;
    bootMs += 1000000;
    host::gasMv = 0;
    host::attachSucceeds = true;
    host::pumpClosedAgainstDrive = false;
    host::refillOwedInFlash = false;
    host::refillFilledInFlash = false;
    host::sweepMovingInFlash = false;
    host::refillSpentInFlash = 0;
    host::refillOwedWrites = 0;
    host::refillSpentWrites = 0;
    host::sweepOwedInFlash = false;
    host::sweepOwedWrites = 0;
    host::flashForgets = false;
    host::sounding = SND_NONE;
    memset(host::played, 0, sizeof(host::played));
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
    machineNoticeHold(0);
    machineBegin();
    TEST_ASSERT_TRUE(machineIoReady());
    host::events.clear();
    host::noted.clear();
}

void tearDown() { TEST_ASSERT_FALSE(host::pumpClosedAgainstDrive); }

int main(int, char **) {
    UNITY_BEGIN();
    RUN_TEST(test_a_machine_that_owes_no_sweep_pours_as_it_did);
    RUN_TEST(test_a_sweep_that_is_owed_holds_the_refill_and_opens_no_pour);
    RUN_TEST(test_gas_through_the_tank_is_counted_and_the_lever_let_go_brings_the_first_fill);
    RUN_TEST(test_the_lever_let_go_early_keeps_the_count);
    RUN_TEST(test_a_tank_found_to_hold_water_drops_the_sweep);
    RUN_TEST(test_a_sweep_cannot_be_owed_over_water);
    RUN_TEST(test_owing_a_sweep_drops_the_refill_that_was_owed);
    RUN_TEST(test_a_sweep_owed_when_the_power_went_is_owed_still);
    RUN_TEST(test_power_lost_between_the_target_and_the_lever_leaves_the_sweep_owed);
    RUN_TEST(test_a_sweep_given_up_at_the_machine_fills_without_it);
    RUN_TEST(test_a_sweep_given_up_with_the_lever_down_waits_for_the_lever);
    RUN_TEST(test_a_sweep_given_up_after_its_target_still_waits_for_the_lever);
    RUN_TEST(test_a_bench_that_holds_the_notice_off_still_has_the_sweep);
    RUN_TEST(test_a_sweep_forgotten_at_the_bench_asks_for_nothing);
    RUN_TEST(test_a_sweep_forgotten_with_the_lever_down_opens_no_pour);
    RUN_TEST(test_a_sweep_owed_again_after_one_forgotten_with_the_lever_down_is_a_whole_sweep);
    return UNITY_END();
}
