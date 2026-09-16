#include <unity.h>

#include "cold_policy.h"

using namespace machine_policy;

void setUp() {}
void tearDown() {}

// One pass of the bus and one pass of the loop, at the same instant.
static ColdAction step(Cold &c, uint32_t now, float tank, float coil) {
    ColdReading r;
    r.tankC = tank;
    r.tankValid = true;
    r.coilC = coil;
    r.coilValid = true;
    c.reading(r, now);
    return c.service(now);
}

// Carry the loop to `until` inclusive, feeding a reading often enough to stay
// fresh. The last step lands on `until` itself, so a deadline that falls
// between two strides is still met.
static ColdAction carry(Cold &c, uint32_t from, uint32_t until, float tank, float coil) {
    ColdAction last = ColdAction::None;
    for (uint32_t t = from; t < until; t += kReadingStaleMs / 3) {
        const ColdAction a = step(c, t, tank, coil);
        if (a != ColdAction::None) last = a;
    }
    const ColdAction a = step(c, until, tank, coil);
    if (a != ColdAction::None) last = a;
    return last;
}

void test_setpoints_are_the_commissioned_figures() {
    TEST_ASSERT_EQUAL_FLOAT(2.0f, kTankTargetC);
    TEST_ASSERT_EQUAL_FLOAT(2.0f, kHysteresisC);
    TEST_ASSERT_EQUAL_FLOAT(4.0f, kCompOnC);
    TEST_ASSERT_EQUAL_FLOAT(2.0f, kCompOffC);
    TEST_ASSERT_EQUAL_FLOAT(-8.0f, kFreezeCutoffC);
    TEST_ASSERT_EQUAL_UINT32(180000, kMinOffMs);
}

void test_a_loop_with_no_reading_is_parked_and_says_so() {
    Cold c;
    TEST_ASSERT_EQUAL(ColdState::Fault, c.state());
    TEST_ASSERT_EQUAL(ColdAction::None, c.service(0));
    TEST_ASSERT_FALSE(c.compressorOn());
    TEST_ASSERT_EQUAL(ColdAction::None, c.service(500000));
    TEST_ASSERT_EQUAL(ColdState::Fault, c.state());
    TEST_ASSERT_FALSE(c.compressorOn());
}

void test_one_probe_missing_is_as_good_as_none() {
    Cold c;
    ColdReading r;
    r.tankC = 9.0f;  r.tankValid = true;
    r.coilC = 5.0f;  r.coilValid = false;   // the DS18S20 did not answer
    c.reading(r, 1000);
    TEST_ASSERT_EQUAL(ColdAction::None, c.service(1000));
    TEST_ASSERT_EQUAL(ColdState::Fault, c.state());
    TEST_ASSERT_FALSE(c.compressorOn());
}

void test_a_boot_holds_the_minimum_off_time_before_its_first_start() {
    Cold c;
    // Warm tank the instant the probes read: the loop wants to run and waits.
    TEST_ASSERT_EQUAL(ColdAction::None, step(c, 0, 8.0f, 5.0f));
    TEST_ASSERT_EQUAL(ColdState::Holding, c.state());
    TEST_ASSERT_EQUAL_UINT32(kMinOffMs, c.holdRemainingMs(0));

    TEST_ASSERT_EQUAL(ColdAction::None, carry(c, 1, kMinOffMs - 1, 8.0f, 5.0f));
    TEST_ASSERT_EQUAL(ColdState::Holding, c.state());

    TEST_ASSERT_EQUAL(ColdAction::CompressorOn, step(c, kMinOffMs, 8.0f, 5.0f));
    TEST_ASSERT_EQUAL(ColdState::On, c.state());
    TEST_ASSERT_TRUE(c.compressorOn());
    TEST_ASSERT_EQUAL_UINT32(0, c.holdRemainingMs(kMinOffMs));
}

void test_the_loop_runs_to_the_setpoint_and_stops_there() {
    Cold c;
    step(c, 0, 8.0f, 5.0f);
    step(c, kMinOffMs, 8.0f, 5.0f);
    TEST_ASSERT_EQUAL(ColdState::On, c.state());

    // At the setpoint but inside the minimum on-time: still running.
    const uint32_t on_at = kMinOffMs;
    TEST_ASSERT_EQUAL(ColdAction::None, carry(c, on_at + 1, on_at + kMinOnMs - 1, 1.5f, -2.0f));
    TEST_ASSERT_EQUAL(ColdState::On, c.state());

    TEST_ASSERT_EQUAL(ColdAction::CompressorOff, step(c, on_at + kMinOnMs, 1.5f, -2.0f));
    TEST_ASSERT_EQUAL(ColdState::Off, c.state());
    TEST_ASSERT_FALSE(c.compressorOn());
}

void test_hysteresis_keeps_it_off_until_the_tank_reaches_the_on_temperature() {
    Cold c;
    step(c, 0, 8.0f, 5.0f);
    step(c, kMinOffMs, 8.0f, 5.0f);
    const uint32_t off_at = kMinOffMs + kMinOnMs;
    step(c, off_at, 1.5f, -2.0f);
    TEST_ASSERT_EQUAL(ColdState::Off, c.state());

    // Drifting up through the band, short of kCompOnC: no call.
    carry(c, off_at + 1, off_at + kMinOffMs - 1, 3.9f, 1.0f);
    TEST_ASSERT_EQUAL(ColdState::Off, c.state());

    // At kCompOnC it calls — and the minimum off-time is already spent.
    TEST_ASSERT_EQUAL(ColdAction::CompressorOn, step(c, off_at + kMinOffMs, 4.0f, 1.0f));
    TEST_ASSERT_EQUAL(ColdState::On, c.state());
}

void test_a_call_inside_the_minimum_off_time_waits_it_out() {
    Cold c;
    step(c, 0, 8.0f, 5.0f);
    step(c, kMinOffMs, 8.0f, 5.0f);
    const uint32_t off_at = kMinOffMs + kMinOnMs;
    step(c, off_at, 1.5f, -2.0f);
    TEST_ASSERT_EQUAL(ColdState::Off, c.state());

    // Warm again immediately: Holding, not On.
    TEST_ASSERT_EQUAL(ColdAction::None, step(c, off_at + 1000, 6.0f, 1.0f));
    TEST_ASSERT_EQUAL(ColdState::Holding, c.state());
    TEST_ASSERT_FALSE(c.compressorOn());
    TEST_ASSERT_EQUAL_UINT32(kMinOffMs - 1000, c.holdRemainingMs(off_at + 1000));

    TEST_ASSERT_EQUAL(ColdAction::CompressorOn, carry(c, off_at + 1001, off_at + kMinOffMs + 1, 6.0f, 1.0f));
    TEST_ASSERT_EQUAL(ColdState::On, c.state());
}

void test_a_tank_that_cools_while_holding_stands_down() {
    Cold c;
    step(c, 0, 8.0f, 5.0f);
    TEST_ASSERT_EQUAL(ColdState::Holding, c.state());
    step(c, 1000, 1.0f, 0.0f);
    TEST_ASSERT_EQUAL(ColdState::Off, c.state());
    TEST_ASSERT_EQUAL_UINT32(0, c.holdRemainingMs(1000));
}

void test_the_freeze_cutout_beats_the_minimum_on_time() {
    Cold c;
    step(c, 0, 8.0f, 5.0f);
    step(c, kMinOffMs, 8.0f, 5.0f);
    TEST_ASSERT_EQUAL(ColdState::On, c.state());

    // One second in — nowhere near kMinOnMs — the suction line hits the cutout.
    TEST_ASSERT_EQUAL(ColdAction::CompressorOff, step(c, kMinOffMs + 1000, 8.0f, kFreezeCutoffC));
    TEST_ASSERT_EQUAL(ColdState::Freeze, c.state());
    TEST_ASSERT_FALSE(c.compressorOn());
}

void test_the_freeze_lock_needs_recovery_not_merely_the_threshold() {
    Cold c;
    step(c, 0, 8.0f, 5.0f);
    step(c, kMinOffMs, 8.0f, 5.0f);
    step(c, kMinOffMs + 1000, 8.0f, -9.0f);
    TEST_ASSERT_EQUAL(ColdState::Freeze, c.state());

    const uint32_t froze_at = kMinOffMs + 1000;
    // Back above the cutout but short of recovery: still locked.
    carry(c, froze_at + 1, froze_at + 60000, 8.0f, -6.0f);
    TEST_ASSERT_EQUAL(ColdState::Freeze, c.state());

    // Recovered. The tank is still warm, so it calls — and waits out kMinOffMs
    // measured from the cutout, which is when the compressor stopped.
    step(c, froze_at + 60000, 8.0f, kFreezeRecoverC);
    TEST_ASSERT_EQUAL(ColdState::Holding, c.state());
    TEST_ASSERT_EQUAL(ColdAction::CompressorOn, carry(c, froze_at + 60001, froze_at + kMinOffMs + 1, 8.0f, -4.0f));
    TEST_ASSERT_EQUAL(ColdState::On, c.state());
}

void test_a_reading_that_stops_arriving_parks_a_running_compressor() {
    Cold c;
    step(c, 0, 8.0f, 5.0f);
    step(c, kMinOffMs, 8.0f, 5.0f);
    TEST_ASSERT_EQUAL(ColdState::On, c.state());

    // The bus goes quiet. One service inside the window changes nothing.
    TEST_ASSERT_EQUAL(ColdAction::None, c.service(kMinOffMs + kReadingStaleMs - 1));
    TEST_ASSERT_TRUE(c.compressorOn());

    TEST_ASSERT_EQUAL(ColdAction::CompressorOff, c.service(kMinOffMs + kReadingStaleMs));
    TEST_ASSERT_EQUAL(ColdState::Fault, c.state());
    TEST_ASSERT_FALSE(c.compressorOn());
}

void test_a_probe_going_bad_mid_run_parks_the_compressor() {
    Cold c;
    step(c, 0, 8.0f, 5.0f);
    step(c, kMinOffMs, 8.0f, 5.0f);
    TEST_ASSERT_EQUAL(ColdState::On, c.state());

    ColdReading r;
    r.tankC = 8.0f;  r.tankValid = false;   // CRC failed this pass
    r.coilC = -2.0f; r.coilValid = true;
    c.reading(r, kMinOffMs + 1000);
    TEST_ASSERT_EQUAL(ColdAction::CompressorOff, c.service(kMinOffMs + 1000));
    TEST_ASSERT_EQUAL(ColdState::Fault, c.state());
}

void test_reset_parks_and_restarts_the_minimum_off_time() {
    Cold c;
    step(c, 0, 8.0f, 5.0f);
    step(c, kMinOffMs, 8.0f, 5.0f);
    TEST_ASSERT_EQUAL(ColdState::On, c.state());

    c.reset(kMinOffMs + 5000);
    TEST_ASSERT_EQUAL(ColdState::Fault, c.state());
    TEST_ASSERT_FALSE(c.compressorOn());

    const uint32_t reset_at = kMinOffMs + 5000;
    step(c, reset_at + 1000, 8.0f, 5.0f);
    TEST_ASSERT_EQUAL(ColdState::Holding, c.state());
    TEST_ASSERT_EQUAL(ColdAction::CompressorOn, carry(c, reset_at + 1001, reset_at + kMinOffMs + 1, 8.0f, 5.0f));
}

int main(int, char **) {
    UNITY_BEGIN();
    RUN_TEST(test_setpoints_are_the_commissioned_figures);
    RUN_TEST(test_a_loop_with_no_reading_is_parked_and_says_so);
    RUN_TEST(test_one_probe_missing_is_as_good_as_none);
    RUN_TEST(test_a_boot_holds_the_minimum_off_time_before_its_first_start);
    RUN_TEST(test_the_loop_runs_to_the_setpoint_and_stops_there);
    RUN_TEST(test_hysteresis_keeps_it_off_until_the_tank_reaches_the_on_temperature);
    RUN_TEST(test_a_call_inside_the_minimum_off_time_waits_it_out);
    RUN_TEST(test_a_tank_that_cools_while_holding_stands_down);
    RUN_TEST(test_the_freeze_cutout_beats_the_minimum_on_time);
    RUN_TEST(test_the_freeze_lock_needs_recovery_not_merely_the_threshold);
    RUN_TEST(test_a_reading_that_stops_arriving_parks_a_running_compressor);
    RUN_TEST(test_a_probe_going_bad_mid_run_parks_the_compressor);
    RUN_TEST(test_reset_parks_and_restarts_the_minimum_off_time);
    return UNITY_END();
}
