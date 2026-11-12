#include "../machine_host/machine_host.h"

// A move, and the starts that find a tank emptied, as the production machine runs them:
// machine.cpp whole, with the meter, the reeds, the relays and the flash replaced by the
// host's.
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

machine_policy::RefillState refillStateNow() {
    MachineThermal thermal;
    machineThermal(thermal);
    return static_cast<machine_policy::RefillState>(thermal.refillState);
}

MachineSweep sweepNow() {
    MachineSweep s;
    machineSweep(s);
    return s;
}

MachineMove moveNow() {
    MachineMove m;
    machineMove(m);
    return m;
}

MachineLevels levelsNow() {
    MachineLevels l;
    machineLevels(l);
    return l;
}

std::vector<machine_log::Entry> notedOf(machine_log::Kind kind) {
    std::vector<machine_log::Entry> out;
    for (const machine_log::Entry &entry : host::noted)
        if (entry.kind == kind) out.push_back(entry);
    return out;
}

// A first fill, as a machine that has been in service has had: asked for, and ended by the
// high reed.
void fillTheTank() {
    machineRefillRequest();
    sampleFor(1500);
    TEST_ASSERT_EQUAL(ST_REFILLING, machineState());
    carbonatorReeds(false, true);
    sampleFor(2000);
    TEST_ASSERT_EQUAL(ST_IDLE, machineState());
    TEST_ASSERT_TRUE(host::refillFilledInFlash);
}

// The float falls through the low reed's window and out of its foot, as a tank being emptied
// carries it.
void theFloatFallsThroughTheLowReed() {
    carbonatorReeds(false, false);
    sampleFor(2500);
    carbonatorReeds(true, false);
    sampleFor(3000);
    carbonatorReeds(false, false);
    sampleFor(2500);
}

// ── The move ──────────────────────────────────────────────────────────────

void test_a_machine_that_is_moving_starts_no_refill_and_opens_no_pour() {
    fillTheTank();
    TEST_ASSERT_TRUE(machineMoveBegin());
    TEST_ASSERT_TRUE(moveNow().moving);
    TEST_ASSERT_TRUE(host::sweepMovingInFlash);
    TEST_ASSERT_EQUAL_UINT8(NOTICE_MOVE, machineNotice());

    // The lever is down and the tank is emptying: no flavor follows what leaves.
    machineFlowSimulate(6, 600000);
    for (uint32_t t = kStep; t <= 2000; t += kStep) {
        runAt(host::now + kStep);
        TEST_ASSERT_FALSE(machineIsPouring());
        TEST_ASSERT_EQUAL_UINT16(0, machineValvesOpen());
    }
    TEST_ASSERT_TRUE(moveNow().flowing);
    TEST_ASSERT_TRUE(moveNow().pulses > 0);

    // The float asks for water on its way down, and the pump stays off a supply that is shut.
    theFloatFallsThroughTheLowReed();
    TEST_ASSERT_EQUAL(machine_policy::RefillState::Queued, refillStateNow());
    TEST_ASSERT_FALSE(refillRelayClosed());
    TEST_ASSERT_EQUAL(ST_IDLE, machineState());
    TEST_ASSERT_EQUAL_UINT8(NOTICE_MOVE, machineNotice());
    TEST_ASSERT_EQUAL_UINT32(0, notedOf(machine_log::Kind::Pour).size());

    machineFlowSimulate(0, 0);
    sampleFor(500);
    TEST_ASSERT_FALSE(moveNow().flowing);
}

void test_the_float_passing_the_low_reed_is_what_the_move_can_say_of_the_tank() {
    fillTheTank();
    TEST_ASSERT_TRUE(machineMoveBegin());
    TEST_ASSERT_FALSE(moveNow().belowLow);

    carbonatorReeds(false, false);
    sampleFor(2500);
    TEST_ASSERT_TRUE(levelsNow().valid);
    TEST_ASSERT_FALSE(levelsNow().carbBelow);

    // In the reed's window the water is at the mark.
    carbonatorReeds(true, false);
    sampleFor(2500);
    TEST_ASSERT_TRUE(levelsNow().carbLow);
    TEST_ASSERT_FALSE(levelsNow().carbBelow);

    carbonatorReeds(false, false);
    sampleFor(2500);
    TEST_ASSERT_FALSE(levelsNow().carbLow);
    TEST_ASSERT_TRUE(levelsNow().carbBelow);
    TEST_ASSERT_TRUE(moveNow().belowLow);

    // It is said of a move, and of nothing else.
    TEST_ASSERT_TRUE(machineMoveCancel());
    TEST_ASSERT_FALSE(levelsNow().carbBelow);
}

void test_a_move_called_off_runs_the_refill_the_float_asked_for() {
    fillTheTank();
    TEST_ASSERT_TRUE(machineMoveBegin());
    theFloatFallsThroughTheLowReed();
    TEST_ASSERT_FALSE(refillRelayClosed());

    TEST_ASSERT_TRUE(machineMoveCancel());
    TEST_ASSERT_FALSE(moveNow().moving);
    TEST_ASSERT_FALSE(host::sweepMovingInFlash);
    TEST_ASSERT_FALSE(machineMoveCancel());
    sampleFor(1500);
    TEST_ASSERT_EQUAL(ST_REFILLING, machineState());
    TEST_ASSERT_TRUE(refillRelayClosed());
    TEST_ASSERT_EQUAL_UINT8(NOTICE_NONE, machineNotice());

    // And it pours again.
    carbonatorReeds(false, true);
    sampleFor(2000);
    machineFlowSimulate(6, 5000);
    sampleFor(200);
    TEST_ASSERT_TRUE(machineIsPouring());
}

void test_the_power_going_ends_the_move_and_the_next_start_is_a_first_start() {
    fillTheTank();
    TEST_ASSERT_TRUE(machineMoveBegin());
    theFloatFallsThroughTheLowReed();
    TEST_ASSERT_TRUE(host::refillOwedInFlash);

    restart();
    TEST_ASSERT_FALSE(moveNow().moving);
    TEST_ASSERT_FALSE(host::sweepMovingInFlash);
    TEST_ASSERT_TRUE(sweepNow().owed);
    TEST_ASSERT_TRUE(host::sweepOwedInFlash);
    TEST_ASSERT_EQUAL_UINT8(NOTICE_SWEEP, machineNotice());
    TEST_ASSERT_FALSE(host::refillOwedInFlash);

    // No water goes in ahead of the sweep, from the float's old ask or from the start's own.
    sampleFor(6000);
    TEST_ASSERT_EQUAL(ST_IDLE, machineState());
    TEST_ASSERT_FALSE(refillRelayClosed());

    // The lever held to its target and let go, as at a new machine's first start.
    machineFlowSimulate(40, 600000);
    for (uint32_t guard = 0; guard < 2000 && !sweepNow().done; guard++) runAt(host::now + kStep);
    TEST_ASSERT_TRUE(sweepNow().done);
    machineFlowSimulate(0, 0);
    sampleFor(machine_policy::kSweepReleaseMs + 2 * kStep + 1500);
    TEST_ASSERT_FALSE(sweepNow().owed);
    TEST_ASSERT_EQUAL(ST_REFILLING, machineState());
    carbonatorReeds(false, true);
    sampleFor(2000);
    TEST_ASSERT_EQUAL(ST_IDLE, machineState());

    // A start after that is an ordinary one.
    restart();
    TEST_ASSERT_FALSE(sweepNow().owed);
    TEST_ASSERT_EQUAL_UINT8(NOTICE_NONE, machineNotice());
}

void test_a_move_begun_during_a_pour_ends_the_pour() {
    fillTheTank();
    machineFlowSimulate(6, 600000);
    sampleFor(300);
    TEST_ASSERT_TRUE(machineIsPouring());

    TEST_ASSERT_TRUE(machineMoveBegin());
    TEST_ASSERT_FALSE(machineIsPouring());
    TEST_ASSERT_EQUAL_UINT16(0, machineValvesOpen());
    const std::vector<machine_log::Entry> pours = notedOf(machine_log::Kind::Pour);
    TEST_ASSERT_EQUAL_UINT32(1, pours.size());
    TEST_ASSERT_EQUAL_UINT8(static_cast<uint8_t>(machine_log::PourEnd::Stopped),
                            machine_log::detailHigh(pours[0].detail));

    // The flow that is still coming opens no other.
    sampleFor(2000);
    TEST_ASSERT_FALSE(machineIsPouring());
    TEST_ASSERT_EQUAL_UINT32(1, notedOf(machine_log::Kind::Pour).size());
}

void test_a_move_begun_during_a_refill_stands_the_pump_down() {
    fillTheTank();
    carbonatorReeds(true, false);
    sampleFor(3500);
    TEST_ASSERT_EQUAL(ST_REFILLING, machineState());
    TEST_ASSERT_TRUE(refillRelayClosed());

    TEST_ASSERT_TRUE(machineMoveBegin());
    sampleFor(500);
    TEST_ASSERT_FALSE(refillRelayClosed());
    TEST_ASSERT_EQUAL(ST_IDLE, machineState());
    TEST_ASSERT_EQUAL_UINT16(0, machineValvesOpen());
    TEST_ASSERT_EQUAL(machine_policy::RefillState::Queued, refillStateNow());

    // It stays down for as long as the machine is moving.
    sampleFor(10000);
    TEST_ASSERT_FALSE(refillRelayClosed());
}

void test_a_machine_that_is_moving_begins_nothing_else() {
    fillTheTank();
    TEST_ASSERT_TRUE(machineMoveBegin());
    TEST_ASSERT_FALSE(machineFillBegin(0));
    TEST_ASSERT_FALSE(machineCleanBegin(0));
    TEST_ASSERT_FALSE(machineAirBegin(AIR_MODE_DRY, 0));
    TEST_ASSERT_FALSE(machinePrimeBegin(0));
    TEST_ASSERT_FALSE(machinePumpRun(0, 200));
    TEST_ASSERT_FALSE(machineSelfTestBegin());
    sampleFor(500);
    TEST_ASSERT_EQUAL(ST_IDLE, machineState());
    TEST_ASSERT_EQUAL_UINT16(0, machineValvesOpen());

    TEST_ASSERT_TRUE(machineMoveCancel());
    TEST_ASSERT_TRUE(machinePumpRun(0, 200));
    sampleFor(1000);
    TEST_ASSERT_EQUAL(ST_IDLE, machineState());
}

void test_a_move_is_refused_while_something_has_the_manifold() {
    TEST_ASSERT_TRUE(machinePumpRun(0, 500));
    TEST_ASSERT_FALSE(machineMoveBegin());
    TEST_ASSERT_FALSE(moveNow().moving);
    TEST_ASSERT_FALSE(host::sweepMovingInFlash);
    TEST_ASSERT_EQUAL_UINT8(NOTICE_NONE, machineNotice());

    sampleFor(1500);
    TEST_ASSERT_EQUAL(ST_IDLE, machineState());
    TEST_ASSERT_TRUE(machineMoveBegin());
    // Asked again, it is still the one move.
    TEST_ASSERT_TRUE(machineMoveBegin());
    TEST_ASSERT_TRUE(moveNow().moving);
}

void test_a_machine_moved_before_its_first_sweep_still_owes_it() {
    TEST_ASSERT_TRUE(machineSweepOwe());
    TEST_ASSERT_TRUE(machineMoveBegin());
    TEST_ASSERT_EQUAL_UINT8(NOTICE_MOVE, machineNotice());

    // Gas let through now is the tank being emptied, and no part of the sweep.
    machineFlowSimulate(40, 3000);
    sampleFor(4000);
    TEST_ASSERT_EQUAL_UINT32(0, sweepNow().pulses);
    TEST_ASSERT_TRUE(sweepNow().owed);

    restart();
    TEST_ASSERT_TRUE(sweepNow().owed);
    TEST_ASSERT_EQUAL_UINT8(NOTICE_SWEEP, machineNotice());
    TEST_ASSERT_FALSE(host::sweepMovingInFlash);
}

void test_a_bench_can_hold_the_move_off_the_glasses() {
    TEST_ASSERT_TRUE(machineMoveBegin());
    machineNoticeHold(static_cast<uint8_t>(1u << NOTICE_MOVE));
    TEST_ASSERT_EQUAL_UINT8(NOTICE_MOVE, machineNoticeStanding());
    TEST_ASSERT_EQUAL_UINT8(NOTICE_NONE, machineNotice());
    machineFlowSimulate(6, 1000);
    sampleFor(1500);
    TEST_ASSERT_FALSE(machineIsPouring());
    machineNoticeHold(0);
    TEST_ASSERT_EQUAL_UINT8(NOTICE_MOVE, machineNotice());
}

void test_a_tank_that_was_never_emptied_drops_the_sweep_the_move_left() {
    fillTheTank();
    TEST_ASSERT_TRUE(machineMoveBegin());

    // The plug came out and went back with the water still at its high reed.
    restart();
    TEST_ASSERT_TRUE(sweepNow().owed);
    sampleFor(machine_policy::kSweepWetMs + 3000);
    TEST_ASSERT_FALSE(sweepNow().owed);
    TEST_ASSERT_FALSE(host::sweepOwedInFlash);
    TEST_ASSERT_EQUAL_UINT8(NOTICE_NONE, machineNotice());
    TEST_ASSERT_EQUAL(ST_IDLE, machineState());
}

// ── The water a start finds ───────────────────────────────────────────────

void test_a_tank_emptied_with_the_power_off_is_filled_at_the_next_start() {
    fillTheTank();

    // The plug is out, the lever lets everything go, and no reed is closed after it.
    carbonatorReeds(false, false);
    restart();
    TEST_ASSERT_EQUAL(ST_IDLE, machineState());
    sampleFor(3000);
    TEST_ASSERT_EQUAL(ST_REFILLING, machineState());
    TEST_ASSERT_TRUE(refillRelayClosed());
    TEST_ASSERT_TRUE(host::refillOwedInFlash);

    carbonatorReeds(false, true);
    sampleFor(2000);
    TEST_ASSERT_EQUAL(ST_IDLE, machineState());
    TEST_ASSERT_FALSE(host::refillOwedInFlash);
}

void test_a_start_that_finds_the_high_reed_closed_asks_for_nothing() {
    fillTheTank();
    restart();
    sampleFor(6000);
    TEST_ASSERT_EQUAL(ST_IDLE, machineState());
    TEST_ASSERT_FALSE(refillRelayClosed());
    TEST_ASSERT_FALSE(host::refillOwedInFlash);
}

void test_a_start_asks_once_and_not_again_when_the_water_falls() {
    fillTheTank();
    restart();
    sampleFor(3000);
    TEST_ASSERT_EQUAL(ST_IDLE, machineState());

    // A pour that leaves the float between its reeds is no reason to pump.
    carbonatorReeds(false, false);
    sampleFor(6000);
    TEST_ASSERT_EQUAL(ST_IDLE, machineState());
    TEST_ASSERT_FALSE(refillRelayClosed());
}

void test_a_board_that_never_filled_a_tank_asks_for_nothing_at_a_start() {
    carbonatorReeds(false, false);
    restart();
    sampleFor(6000);
    TEST_ASSERT_EQUAL(ST_IDLE, machineState());
    TEST_ASSERT_FALSE(refillRelayClosed());
    TEST_ASSERT_FALSE(host::refillOwedInFlash);
}

void test_a_start_that_owes_a_sweep_leaves_the_asking_to_the_sweep() {
    fillTheTank();
    carbonatorReeds(false, false);
    sampleFor(1500);
    TEST_ASSERT_TRUE(machineSweepOwe());

    restart();
    sampleFor(6000);
    TEST_ASSERT_EQUAL(ST_IDLE, machineState());
    TEST_ASSERT_FALSE(refillRelayClosed());
    TEST_ASSERT_FALSE(host::refillOwedInFlash);
    TEST_ASSERT_EQUAL_UINT8(NOTICE_SWEEP, machineNotice());
}

void test_a_refill_already_owed_at_a_start_is_the_one_that_runs() {
    fillTheTank();
    carbonatorReeds(true, false);
    sampleFor(1700);
    TEST_ASSERT_TRUE(host::refillOwedInFlash);

    carbonatorReeds(false, false);
    restart();
    sampleFor(3000);
    TEST_ASSERT_EQUAL(ST_REFILLING, machineState());
    carbonatorReeds(false, true);
    sampleFor(2000);
    TEST_ASSERT_EQUAL(ST_IDLE, machineState());
    TEST_ASSERT_EQUAL_UINT32(2, notedOf(machine_log::Kind::Refill).size());
}

void test_a_reading_put_in_at_the_console_fills_no_tank() {
    machineSimReeds(false, false);
    machineRefillRequest();
    sampleFor(1500);
    TEST_ASSERT_EQUAL(ST_REFILLING, machineState());
    machineSimReeds(false, true);
    sampleFor(2000);
    TEST_ASSERT_EQUAL(ST_IDLE, machineState());
    TEST_ASSERT_FALSE(host::refillFilledInFlash);
    machineSimClear();
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
    host::refillSpentInFlash = 0;
    host::refillOwedWrites = 0;
    host::refillSpentWrites = 0;
    host::refillFilledInFlash = false;
    host::sweepOwedInFlash = false;
    host::sweepOwedWrites = 0;
    host::sweepMovingInFlash = false;
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
    RUN_TEST(test_a_machine_that_is_moving_starts_no_refill_and_opens_no_pour);
    RUN_TEST(test_the_float_passing_the_low_reed_is_what_the_move_can_say_of_the_tank);
    RUN_TEST(test_a_move_called_off_runs_the_refill_the_float_asked_for);
    RUN_TEST(test_the_power_going_ends_the_move_and_the_next_start_is_a_first_start);
    RUN_TEST(test_a_move_begun_during_a_pour_ends_the_pour);
    RUN_TEST(test_a_move_begun_during_a_refill_stands_the_pump_down);
    RUN_TEST(test_a_machine_that_is_moving_begins_nothing_else);
    RUN_TEST(test_a_move_is_refused_while_something_has_the_manifold);
    RUN_TEST(test_a_machine_moved_before_its_first_sweep_still_owes_it);
    RUN_TEST(test_a_bench_can_hold_the_move_off_the_glasses);
    RUN_TEST(test_a_tank_that_was_never_emptied_drops_the_sweep_the_move_left);
    RUN_TEST(test_a_tank_emptied_with_the_power_off_is_filled_at_the_next_start);
    RUN_TEST(test_a_start_that_finds_the_high_reed_closed_asks_for_nothing);
    RUN_TEST(test_a_start_asks_once_and_not_again_when_the_water_falls);
    RUN_TEST(test_a_board_that_never_filled_a_tank_asks_for_nothing_at_a_start);
    RUN_TEST(test_a_start_that_owes_a_sweep_leaves_the_asking_to_the_sweep);
    RUN_TEST(test_a_refill_already_owed_at_a_start_is_the_one_that_runs);
    RUN_TEST(test_a_reading_put_in_at_the_console_fills_no_tank);
    return UNITY_END();
}
