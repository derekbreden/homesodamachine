#include <unity.h>

#include "reed_rig_policy.h"

using namespace reed_rig;

namespace {

// ── Units and limits ──────────────────────────────────────────────────────

void test_a_millimetre_is_a_whole_number_of_steps() {
    TEST_ASSERT_EQUAL_INT32(kStepsPerMm, stepsFromMm(1.0f));
    TEST_ASSERT_EQUAL_INT32(-kStepsPerMm / 2, stepsFromMm(-0.5f));
    TEST_ASSERT_FLOAT_WITHIN(1e-6f, 1.0f, mmFromSteps(kStepsPerMm));
}

void test_a_sled_position_is_named_from_the_tab() {
    const int32_t tab = stepsFromMm(1.0f);
    TEST_ASSERT_EQUAL_INT32(0, homeStepsFromSledMm(1.0f, tab));
    TEST_ASSERT_EQUAL_INT32(stepsFromMm(29.0f), homeStepsFromSledMm(30.0f, tab));
    TEST_ASSERT_FLOAT_WITHIN(1e-4f, 30.0f, sledMmFromHomeSteps(stepsFromMm(29.0f), tab));
}

void test_the_sled_may_go_from_home_to_its_deepest_and_no_further() {
    const int32_t tab = reed_sweep_datums::kHomeFromTabSteps;
    const int32_t deepest = deepestFromHome(tab);
    TEST_ASSERT_EQUAL_INT32(reed_sweep_datums::kDeepestFromTabSteps - tab, deepest);
    TEST_ASSERT_TRUE(reachable(0, tab));
    TEST_ASSERT_TRUE(reachable(deepest, tab));
    TEST_ASSERT_FALSE(reachable(-1, tab));
    TEST_ASSERT_FALSE(reachable(deepest + 1, tab));
}

void test_the_tab_is_believed_only_a_little_behind_home() {
    TEST_ASSERT_TRUE(validTabSteps(reed_sweep_datums::kHomeFromTabSteps));
    TEST_ASSERT_FALSE(validTabSteps(0));
    TEST_ASSERT_FALSE(validTabSteps(-5));
    TEST_ASSERT_FALSE(validTabSteps(stepsFromMm(kMostTabMm) + 1));
}

void test_a_sweep_speed_stays_within_what_the_motor_takes_at_once() {
    TEST_ASSERT_TRUE(validSweepSpeed(kDefaultSweepMmPerS));
    TEST_ASSERT_TRUE(validSweepSpeed(kSlowestSweepMmPerS));
    TEST_ASSERT_TRUE(validSweepSpeed(kFastestSweepMmPerS));
    TEST_ASSERT_FALSE(validSweepSpeed(kFastestSweepMmPerS + 0.01f));
    TEST_ASSERT_FALSE(validSweepSpeed(0.0f));
}

// ── A move ────────────────────────────────────────────────────────────────

// Runs a move to its end and reports the steps taken and the fastest and the last speed.
struct Ran {
    int32_t steps;
    float fastest;
    float first;
    float last;
};

Ran run(Move &move) {
    Ran ran{0, 0.0f, move.stepsPerS(), 0.0f};
    while (move.active()) {
        const float speed = move.stepsPerS();
        if (speed > ran.fastest) ran.fastest = speed;
        ran.last = speed;
        ++ran.steps;
        move.step();
    }
    return ran;
}

void test_a_long_move_climbs_to_its_cruise_and_comes_down_again() {
    Move move;
    const int32_t steps = stepsFromMm(60.0f);
    move.begin(steps, stepsPerSecond(kTravelMmPerS));
    TEST_ASSERT_EQUAL_INT8(1, move.direction());
    const Ran ran = run(move);
    TEST_ASSERT_EQUAL_INT32(steps, ran.steps);
    TEST_ASSERT_FLOAT_WITHIN(1.0f, stepsPerSecond(kInstantMmPerS), ran.first);
    TEST_ASSERT_FLOAT_WITHIN(1.0f, stepsPerSecond(kTravelMmPerS), ran.fastest);
    // It ends no faster than the motor stops from at once, give or take the last step's ramp.
    TEST_ASSERT_TRUE(ran.last <= stepsPerSecond(kInstantMmPerS) * 1.05f);
    TEST_ASSERT_FALSE(move.active());
    TEST_ASSERT_EQUAL_UINT32(0, move.step());
}

void test_a_short_move_never_reaches_its_cruise() {
    Move move;
    move.begin(stepsFromMm(1.0f), stepsPerSecond(kTravelMmPerS));
    const Ran ran = run(move);
    TEST_ASSERT_EQUAL_INT32(stepsFromMm(1.0f), ran.steps);
    TEST_ASSERT_TRUE(ran.fastest < stepsPerSecond(kTravelMmPerS));
    TEST_ASSERT_TRUE(ran.last <= stepsPerSecond(kInstantMmPerS) * 1.05f);
}

void test_a_sweep_leg_holds_one_speed() {
    Move move;
    const float speed = stepsPerSecond(kDefaultSweepMmPerS);
    move.begin(-stepsFromMm(40.0f), speed);
    TEST_ASSERT_EQUAL_INT8(-1, move.direction());
    TEST_ASSERT_FALSE(move.aboveInstant());
    const uint32_t pause = move.pauseUs();
    int32_t steps = 0;
    while (move.active()) {
        const uint32_t next = move.step();
        ++steps;
        if (move.active()) TEST_ASSERT_EQUAL_UINT32(pause, next);
    }
    TEST_ASSERT_EQUAL_INT32(stepsFromMm(40.0f), steps);
    TEST_ASSERT_UINT32_WITHIN(1, static_cast<uint32_t>(1000000.0f / speed), pause);
}

void test_a_move_of_no_steps_is_over_before_it_starts() {
    Move move;
    move.begin(0, stepsPerSecond(kTravelMmPerS));
    TEST_ASSERT_FALSE(move.active());
    TEST_ASSERT_EQUAL_INT8(0, move.direction());
}

void test_a_halted_move_takes_no_more_steps() {
    Move move;
    move.begin(stepsFromMm(60.0f), stepsPerSecond(kTravelMmPerS));
    for (int i = 0; i < 2000; ++i) move.step();
    TEST_ASSERT_TRUE(move.aboveInstant());
    move.halt();
    TEST_ASSERT_FALSE(move.active());
    TEST_ASSERT_EQUAL_UINT32(0, move.step());
}

// ── An input that has to hold ─────────────────────────────────────────────

void test_a_level_counts_once_it_has_held() {
    Debounced input(1000);
    input.reset(false);
    TEST_ASSERT_FALSE(input.sample(true, 100));
    TEST_ASSERT_FALSE(input.sample(true, 600));
    TEST_ASSERT_FALSE(input.state());
    TEST_ASSERT_TRUE(input.sample(true, 1100));
    TEST_ASSERT_TRUE(input.state());
    TEST_ASSERT_FALSE(input.sample(true, 1200));
}

void test_a_bounce_starts_the_hold_again() {
    Debounced input(1000);
    input.reset(false);
    TEST_ASSERT_FALSE(input.sample(true, 100));
    TEST_ASSERT_FALSE(input.sample(false, 500));
    TEST_ASSERT_FALSE(input.sample(true, 900));
    TEST_ASSERT_FALSE(input.sample(true, 1500));
    TEST_ASSERT_TRUE(input.sample(true, 1900));
}

void test_the_hold_survives_the_clock_wrapping() {
    Debounced input(1000);
    input.reset(false);
    const uint32_t late = 0xFFFFFE00u;
    TEST_ASSERT_FALSE(input.sample(true, late));
    TEST_ASSERT_FALSE(input.sample(true, late + 500u));
    TEST_ASSERT_TRUE(input.sample(true, late + 1000u));
}

// ── The reeds ─────────────────────────────────────────────────────────────

void test_a_reed_change_is_logged_where_it_first_read_differently() {
    Reeds reeds;
    reeds.reset(0);
    reeds.sample(0x02, 1000, 10);
    reeds.sample(0x02, 1001, 600);
    ReedEvent event{};
    TEST_ASSERT_FALSE(reeds.pop(event));
    reeds.sample(0x02, 1002, 1200);
    TEST_ASSERT_TRUE(reeds.pop(event));
    TEST_ASSERT_EQUAL_UINT8(1, event.reed);
    TEST_ASSERT_TRUE(event.closed);
    TEST_ASSERT_EQUAL_INT32(1000, event.step);
    TEST_ASSERT_EQUAL_UINT32(10, event.at_us);
    TEST_ASSERT_EQUAL_UINT8(0x02, reeds.closed());
    TEST_ASSERT_FALSE(reeds.pop(event));
}

void test_a_reed_bounce_logs_nothing() {
    Reeds reeds;
    reeds.reset(0x01);
    reeds.sample(0x00, 50, 0);
    reeds.sample(0x01, 51, 400);
    reeds.sample(0x01, 52, 2000);
    ReedEvent event{};
    TEST_ASSERT_FALSE(reeds.pop(event));
    TEST_ASSERT_EQUAL_UINT8(0x01, reeds.closed());
}

void test_reeds_change_apart_and_queue_in_order() {
    Reeds reeds;
    reeds.reset(0);
    reeds.sample(0x01, 10, 0);
    reeds.sample(0x05, 20, 500);
    reeds.sample(0x05, 30, 1000);   // reed 0 has held
    reeds.sample(0x05, 40, 1500);   // reed 2 has held
    ReedEvent event{};
    TEST_ASSERT_TRUE(reeds.pop(event));
    TEST_ASSERT_EQUAL_UINT8(0, event.reed);
    TEST_ASSERT_EQUAL_INT32(10, event.step);
    TEST_ASSERT_TRUE(reeds.pop(event));
    TEST_ASSERT_EQUAL_UINT8(2, event.reed);
    TEST_ASSERT_EQUAL_INT32(20, event.step);
    TEST_ASSERT_FALSE(reeds.pop(event));
}

void test_a_full_queue_says_it_dropped_a_change() {
    Reeds reeds;
    reeds.reset(0);
    uint32_t now = 0;
    uint8_t level = 0;
    for (int change = 0; change < kReedQueue + 3; ++change) {
        level ^= 1u;
        reeds.sample(level, change, now);
        now += kReedHoldUs;
        reeds.sample(level, change, now);
        now += 10;
    }
    TEST_ASSERT_TRUE(reeds.overflowed());
    int popped = 0;
    ReedEvent event{};
    while (reeds.pop(event)) ++popped;
    TEST_ASSERT_EQUAL_INT(kReedQueue, popped);
    reeds.clearOverflow();
    TEST_ASSERT_FALSE(reeds.overflowed());
}

// ── Homing ────────────────────────────────────────────────────────────────

// A bench with a switch that trips where the sled comes down to `trip` and lets go once it is
// `slack` steps back out. `position` is where the sled really stands.
struct Bench {
    int32_t position;
    int32_t trip;
    int32_t slack;
    bool pressed;
    bool connected;

    bool read() {
        if (!connected) return false;
        if (position <= trip) pressed = true;
        if (position >= trip + slack) pressed = false;
        return pressed;
    }
};

// Runs a homing to its end on the bench. Returns the steps it took.
int32_t home(Homing &homing, Bench &bench, bool proven) {
    homing.begin(bench.read(), proven);
    int32_t steps = 0;
    for (;;) {
        const Homing::Order order = homing.next(bench.read());
        if (order.direction == 0) return steps;
        bench.position += order.direction;
        homing.stepped();
        ++steps;
        TEST_ASSERT_TRUE_MESSAGE(steps < 200000, "homing ran away");
    }
}

void test_homing_finds_the_trip_and_how_far_back_the_switch_lets_go() {
    Homing homing;
    Bench bench{stepsFromMm(42.0f), 0, 96, false, true};
    home(homing, bench, true);
    TEST_ASSERT_TRUE(homing.done());
    TEST_ASSERT_EQUAL(HomeFault::None, homing.fault());
    // The sled stands where the switch let go, that many steps from the trip.
    TEST_ASSERT_EQUAL_INT32(96, homing.releaseSteps());
    TEST_ASSERT_EQUAL_INT32(96, bench.position);
}

void test_homing_from_a_pressed_switch_backs_off_first() {
    Homing homing;
    Bench bench{-40, 0, 96, true, true};
    // The switch being seen to let go is its proof, so none is asked for.
    home(homing, bench, false);
    TEST_ASSERT_TRUE(homing.done());
    TEST_ASSERT_EQUAL_INT32(96, homing.releaseSteps());
    TEST_ASSERT_EQUAL_INT32(96, bench.position);
}

void test_homing_never_goes_far_past_the_trip() {
    Homing homing;
    Bench bench{stepsFromMm(42.0f), 0, 96, false, true};
    homing.begin(bench.read(), true);
    int32_t lowest = bench.position;
    for (;;) {
        const Homing::Order order = homing.next(bench.read());
        if (order.direction == 0) break;
        bench.position += order.direction;
        homing.stepped();
        if (bench.position < lowest) lowest = bench.position;
    }
    // The model switch answers at once, so the sled turns back on the step that trips it.
    TEST_ASSERT_EQUAL_INT32(0, lowest);
}

void test_homing_creeps_onto_the_switch_and_seeks_it_faster() {
    Homing homing;
    Bench bench{stepsFromMm(10.0f), 0, 96, false, true};
    homing.begin(bench.read(), true);
    const Homing::Order seeking = homing.next(bench.read());
    TEST_ASSERT_EQUAL_INT8(-1, seeking.direction);
    TEST_ASSERT_FLOAT_WITHIN(0.5f, stepsPerSecond(kHomeSeekMmPerS), seeking.steps_per_s);
    float slowest_toward = seeking.steps_per_s;
    for (;;) {
        const Homing::Order order = homing.next(bench.read());
        if (order.direction == 0) break;
        if (order.direction < 0 && order.steps_per_s < slowest_toward) slowest_toward = order.steps_per_s;
        bench.position += order.direction;
        homing.stepped();
    }
    TEST_ASSERT_FLOAT_WITHIN(0.5f, stepsPerSecond(kHomeCreepMmPerS), slowest_toward);
}

void test_a_switch_never_seen_to_change_is_not_sought() {
    Homing homing;
    Bench bench{stepsFromMm(42.0f), 0, 96, false, true};
    const int32_t steps = home(homing, bench, false);
    TEST_ASSERT_EQUAL_INT32(0, steps);
    TEST_ASSERT_TRUE(homing.failed());
    TEST_ASSERT_EQUAL(HomeFault::Unproven, homing.fault());
}

void test_a_switch_that_never_trips_ends_the_seek() {
    Homing homing;
    Bench bench{stepsFromMm(42.0f), 0, 96, false, false};
    const int32_t steps = home(homing, bench, true);
    TEST_ASSERT_TRUE(homing.failed());
    TEST_ASSERT_EQUAL(HomeFault::NotFound, homing.fault());
    TEST_ASSERT_EQUAL_INT32(reed_sweep_datums::kDeepestFromTabSteps + stepsFromMm(kHomeSeekSlackMm), steps);
}

void test_a_switch_that_never_lets_go_ends_the_escape() {
    Homing homing;
    // The switch reads pressed wherever the sled stands, as a wrong level setting makes it.
    Bench bench{0, 1000000, 96, true, true};
    const int32_t steps = home(homing, bench, true);
    TEST_ASSERT_TRUE(homing.failed());
    TEST_ASSERT_EQUAL(HomeFault::StuckPressed, homing.fault());
    TEST_ASSERT_EQUAL_INT32(stepsFromMm(kHomeEscapeMm), steps);
    // It only ever moved away from the tab.
    TEST_ASSERT_EQUAL_INT32(stepsFromMm(kHomeEscapeMm), bench.position);
}

// ── A sweep ───────────────────────────────────────────────────────────────

void test_a_sweep_runs_in_then_reads_out_and_back() {
    SweepPlan plan;
    const int32_t from = stepsFromMm(5.0f);
    const int32_t to = stepsFromMm(100.0f);
    const float speed = stepsPerSecond(kDefaultSweepMmPerS);
    plan.begin(from, to, speed, 2);
    TEST_ASSERT_EQUAL_UINT16(4, plan.traverses());

    Leg leg{};
    TEST_ASSERT_TRUE(plan.next(leg));
    TEST_ASSERT_EQUAL_INT32(from + stepsFromMm(kRunInMm), leg.target);
    TEST_ASSERT_FALSE(leg.logged);
    TEST_ASSERT_TRUE(plan.next(leg));
    TEST_ASSERT_EQUAL_INT32(from, leg.target);
    TEST_ASSERT_FALSE(leg.logged);

    const int32_t targets[4] = {to, from, to, from};
    for (uint16_t traverse = 1; traverse <= 4; ++traverse) {
        TEST_ASSERT_TRUE(plan.next(leg));
        TEST_ASSERT_TRUE(leg.logged);
        TEST_ASSERT_EQUAL_UINT16(traverse, leg.traverse);
        TEST_ASSERT_EQUAL_INT32(targets[traverse - 1], leg.target);
        TEST_ASSERT_FLOAT_WITHIN(0.01f, speed, leg.steps_per_s);
    }
    TEST_ASSERT_FALSE(plan.next(leg));
}

void test_a_short_sweep_runs_in_no_further_than_its_far_end() {
    SweepPlan plan;
    const int32_t from = stepsFromMm(5.0f);
    const int32_t to = from + stepsFromMm(kRunInMm) / 2;
    plan.begin(from, to, stepsPerSecond(kDefaultSweepMmPerS), 1);
    Leg leg{};
    TEST_ASSERT_TRUE(plan.next(leg));
    TEST_ASSERT_EQUAL_INT32(to, leg.target);
}

}  // namespace

int main(int, char **) {
    UNITY_BEGIN();
    RUN_TEST(test_a_millimetre_is_a_whole_number_of_steps);
    RUN_TEST(test_a_sled_position_is_named_from_the_tab);
    RUN_TEST(test_the_sled_may_go_from_home_to_its_deepest_and_no_further);
    RUN_TEST(test_the_tab_is_believed_only_a_little_behind_home);
    RUN_TEST(test_a_sweep_speed_stays_within_what_the_motor_takes_at_once);
    RUN_TEST(test_a_long_move_climbs_to_its_cruise_and_comes_down_again);
    RUN_TEST(test_a_short_move_never_reaches_its_cruise);
    RUN_TEST(test_a_sweep_leg_holds_one_speed);
    RUN_TEST(test_a_move_of_no_steps_is_over_before_it_starts);
    RUN_TEST(test_a_halted_move_takes_no_more_steps);
    RUN_TEST(test_a_level_counts_once_it_has_held);
    RUN_TEST(test_a_bounce_starts_the_hold_again);
    RUN_TEST(test_the_hold_survives_the_clock_wrapping);
    RUN_TEST(test_a_reed_change_is_logged_where_it_first_read_differently);
    RUN_TEST(test_a_reed_bounce_logs_nothing);
    RUN_TEST(test_reeds_change_apart_and_queue_in_order);
    RUN_TEST(test_a_full_queue_says_it_dropped_a_change);
    RUN_TEST(test_homing_finds_the_trip_and_how_far_back_the_switch_lets_go);
    RUN_TEST(test_homing_from_a_pressed_switch_backs_off_first);
    RUN_TEST(test_homing_never_goes_far_past_the_trip);
    RUN_TEST(test_homing_creeps_onto_the_switch_and_seeks_it_faster);
    RUN_TEST(test_a_switch_never_seen_to_change_is_not_sought);
    RUN_TEST(test_a_switch_that_never_trips_ends_the_seek);
    RUN_TEST(test_a_switch_that_never_lets_go_ends_the_escape);
    RUN_TEST(test_a_sweep_runs_in_then_reads_out_and_back);
    RUN_TEST(test_a_short_sweep_runs_in_no_further_than_its_far_end);
    return UNITY_END();
}
