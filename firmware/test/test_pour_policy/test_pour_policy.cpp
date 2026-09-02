#include <unity.h>

#include "pour_policy.h"

using namespace machine_policy;

void setUp() {}
void tearDown() {}

void test_cycle_timing_at_one_to_twenty_is_the_documented_shape() {
    uint32_t on = 0, off = 0;
    pourCycleTiming(6, 20, on, off);   // full flow
    TEST_ASSERT_EQUAL_UINT32(200, on);
    TEST_ASSERT_EQUAL_UINT32(300, off);
    pourCycleTiming(1, 20, on, off);   // slow
    TEST_ASSERT_EQUAL_UINT32(50, on);
    TEST_ASSERT_EQUAL_UINT32(600, off);
}

void test_cycle_timing_clamps_the_reading_and_the_phases() {
    uint32_t on = 0, off = 0, on6 = 0, off6 = 0;
    pourCycleTiming(60, 20, on, off);
    pourCycleTiming(6, 20, on6, off6);
    TEST_ASSERT_EQUAL_UINT32(on6, on);
    TEST_ASSERT_EQUAL_UINT32(off6, off);
    uint32_t on0 = 0, off0 = 0, on1 = 0, off1 = 0;
    pourCycleTiming(0, 20, on0, off0);
    pourCycleTiming(1, 20, on1, off1);
    TEST_ASSERT_EQUAL_UINT32(on1, on0);
    TEST_ASSERT_TRUE(on >= kPourOnMinMs);
    TEST_ASSERT_TRUE(off <= kPourOffMaxMs);
}

void test_strong_pour_stays_on_at_full_flow_and_weak_pour_rests_longer() {
    uint32_t on = 0, off = 0;
    pourCycleTiming(6, 6, on, off);    // bag-in-box strength at full flow
    TEST_ASSERT_EQUAL_UINT32(500, on);
    TEST_ASSERT_EQUAL_UINT32(0, off);
    uint32_t on24 = 0, off24 = 0;
    pourCycleTiming(6, 24, on24, off24);
    TEST_ASSERT_TRUE(off24 > 300);
    TEST_ASSERT_TRUE(on24 < 200);
}

void test_pour_starts_on_flow_cycles_and_stops_after_a_cooldown() {
    Pour pour;
    TEST_ASSERT_EQUAL(PourPhase::Idle, pour.phase());
    TEST_ASSERT_EQUAL(PourAction::None, pour.service(0, 20));
    TEST_ASSERT_FALSE(pour.open());

    // Flow arrives: valves open, pump on, timing from the reading.
    pour.sample(6);
    TEST_ASSERT_EQUAL(PourAction::Start, pour.service(50, 20));
    TEST_ASSERT_TRUE(pour.open());
    TEST_ASSERT_TRUE(pour.pumpOn());
    TEST_ASSERT_EQUAL_UINT32(200, pour.onMs());
    TEST_ASSERT_EQUAL_UINT32(300, pour.offMs());

    // The on-phase runs its time, then the pump rests.
    TEST_ASSERT_EQUAL(PourAction::None, pour.service(249, 20));
    TEST_ASSERT_EQUAL(PourAction::PumpOff, pour.service(250, 20));
    TEST_ASSERT_FALSE(pour.pumpOn());
    TEST_ASSERT_TRUE(pour.open());

    // Flow holds through the cycle: the next cycle follows from its average.
    for (uint32_t t = 100; t <= 550; t += 50) pour.sample(6);
    TEST_ASSERT_EQUAL(PourAction::None, pour.service(549, 20));
    TEST_ASSERT_EQUAL(PourAction::PumpOn, pour.service(550, 20));
    TEST_ASSERT_EQUAL(PourPhase::On, pour.phase());

    // Flow stops inside this cycle: after the off-phase, a cooldown with the pump off.
    pour.sample(0);
    TEST_ASSERT_EQUAL(PourAction::PumpOff, pour.service(750, 20));
    TEST_ASSERT_EQUAL(PourAction::None, pour.service(1050, 20));
    TEST_ASSERT_EQUAL(PourPhase::Cooldown, pour.phase());
    TEST_ASSERT_TRUE(pour.open());
    TEST_ASSERT_FALSE(pour.pumpOn());

    // Still nothing flowing when the cooldown ends: the valves close.
    TEST_ASSERT_EQUAL(PourAction::None, pour.service(2049, 20));
    TEST_ASSERT_EQUAL(PourAction::Stop, pour.service(2050, 20));
    TEST_ASSERT_FALSE(pour.open());
    TEST_ASSERT_EQUAL(PourPhase::Idle, pour.phase());
}

void test_flow_returning_during_cooldown_keeps_the_valves_open() {
    Pour pour;
    pour.sample(3);
    TEST_ASSERT_EQUAL(PourAction::Start, pour.service(0, 20));
    uint32_t on = pour.onMs(), off = pour.offMs();
    TEST_ASSERT_EQUAL(PourAction::PumpOff, pour.service(on, 20));
    pour.sample(0);
    TEST_ASSERT_EQUAL(PourAction::None, pour.service(on + off, 20));
    TEST_ASSERT_EQUAL(PourPhase::Cooldown, pour.phase());
    // Flow is back before the cooldown ends: no Stop, and a new cycle from Idle.
    pour.sample(4);
    TEST_ASSERT_EQUAL(PourAction::None, pour.service(on + off + kPourCooldownMs, 20));
    TEST_ASSERT_TRUE(pour.open());
    TEST_ASSERT_EQUAL(PourAction::PumpOn, pour.service(on + off + kPourCooldownMs + 1, 20));
    TEST_ASSERT_TRUE(pour.pumpOn());
}

void test_pour_that_never_ends_hits_the_ceiling() {
    Pour pour;
    pour.sample(6);
    TEST_ASSERT_EQUAL(PourAction::Start, pour.service(0, 20));
    PourAction last = PourAction::None;
    for (uint32_t t = 50; t <= kPourCeilingMs + 50; t += 50) {
        pour.sample(6);
        last = pour.service(t, 20);
        if (last == PourAction::Ceiling) break;
    }
    TEST_ASSERT_EQUAL(PourAction::Ceiling, last);
    TEST_ASSERT_FALSE(pour.open());
    TEST_ASSERT_FALSE(pour.pumpOn());
}

void test_sample_period_and_readings_are_the_prototypes() {
    TEST_ASSERT_EQUAL_UINT32(50, kFlowSampleMs);
    TEST_ASSERT_EQUAL_UINT32(1, kFlowMinPulses);
    TEST_ASSERT_EQUAL_UINT32(6, kFlowFullPulses);
    TEST_ASSERT_EQUAL_UINT32(1000, kPourCooldownMs);
}

int main(int, char **) {
    UNITY_BEGIN();
    RUN_TEST(test_cycle_timing_at_one_to_twenty_is_the_documented_shape);
    RUN_TEST(test_cycle_timing_clamps_the_reading_and_the_phases);
    RUN_TEST(test_strong_pour_stays_on_at_full_flow_and_weak_pour_rests_longer);
    RUN_TEST(test_pour_starts_on_flow_cycles_and_stops_after_a_cooldown);
    RUN_TEST(test_flow_returning_during_cooldown_keeps_the_valves_open);
    RUN_TEST(test_pour_that_never_ends_hits_the_ceiling);
    RUN_TEST(test_sample_period_and_readings_are_the_prototypes);
    return UNITY_END();
}
