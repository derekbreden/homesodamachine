#include <unity.h>

#include "sweep_policy.h"

using namespace machine_policy;

void setUp() {}
void tearDown() {}

// Feed the same reading `samples` times and report the last thing that changed.
static SweepAction carry(Sweep &s, uint32_t samples, uint32_t pulses) {
    SweepAction last = SweepAction::None;
    for (uint32_t i = 0; i < samples; i++) {
        const SweepAction a = s.sample(pulses);
        if (a != SweepAction::None) last = a;
    }
    return last;
}

void test_a_sweep_that_is_not_owed_counts_nothing() {
    Sweep s;
    TEST_ASSERT_EQUAL(SweepState::Clear, s.state());
    TEST_ASSERT_FALSE(s.owed());
    TEST_ASSERT_EQUAL(SweepAction::None, carry(s, 200, 40));
    TEST_ASSERT_EQUAL_UINT32(0, s.pulses());
    TEST_ASSERT_EQUAL_UINT8(0, s.percent());
}

void test_gas_on_the_meter_begins_the_count() {
    Sweep s;
    s.owe();
    TEST_ASSERT_TRUE(s.owed());
    TEST_ASSERT_FALSE(s.flowing());
    TEST_ASSERT_EQUAL(SweepAction::None, s.sample(0));

    TEST_ASSERT_EQUAL(SweepAction::Began, s.sample(30));
    TEST_ASSERT_TRUE(s.flowing());
    TEST_ASSERT_EQUAL(SweepAction::None, s.sample(30));
    TEST_ASSERT_EQUAL_UINT32(60, s.pulses());
}

void test_the_lever_let_go_pauses_the_count_and_keeps_it() {
    Sweep s;
    s.owe();
    carry(s, 20, 30);
    const uint32_t counted = s.pulses();
    TEST_ASSERT_EQUAL_UINT32(600, counted);

    TEST_ASSERT_EQUAL(SweepAction::None, carry(s, kSweepQuietSamples - 1, 0));
    TEST_ASSERT_TRUE(s.flowing());
    TEST_ASSERT_EQUAL(SweepAction::Paused, s.sample(0));
    TEST_ASSERT_FALSE(s.flowing());
    TEST_ASSERT_TRUE(s.owed());
    TEST_ASSERT_EQUAL_UINT32(counted, s.pulses());

    TEST_ASSERT_EQUAL(SweepAction::Began, s.sample(30));
    TEST_ASSERT_EQUAL_UINT32(counted + 30, s.pulses());
}

void test_one_empty_reading_inside_the_flow_does_not_pause_it() {
    Sweep s;
    s.owe();
    carry(s, 10, 30);
    TEST_ASSERT_EQUAL(SweepAction::None, s.sample(0));
    TEST_ASSERT_EQUAL(SweepAction::None, s.sample(30));
    TEST_ASSERT_TRUE(s.flowing());
}

// Carry a sweep that is owed up to one reading short of its target.
static const uint32_t kPerSample = 40;
static void nearlyDone(Sweep &s) {
    s.owe();
    carry(s, (kSweepTargetPulses - 1) / kPerSample, kPerSample);
}

void test_the_target_is_said_once_and_the_sweep_stays_owed_while_the_lever_is_down() {
    Sweep s;
    nearlyDone(s);
    TEST_ASSERT_TRUE(s.flowing());
    TEST_ASSERT_TRUE(s.percent() < 100);

    TEST_ASSERT_EQUAL(SweepAction::Done, s.sample(kPerSample));
    TEST_ASSERT_TRUE(s.owed());
    TEST_ASSERT_TRUE(s.done());
    TEST_ASSERT_FALSE(s.flowing());
    TEST_ASSERT_EQUAL_UINT32(kSweepTargetPulses, s.pulses());
    TEST_ASSERT_EQUAL_UINT8(100, s.percent());

    // Gas still on the meter is a hand still on the lever, however long it stays.
    TEST_ASSERT_EQUAL(SweepAction::None, carry(s, 400, kPerSample));
    TEST_ASSERT_TRUE(s.owed());
    TEST_ASSERT_EQUAL_UINT32(kSweepTargetPulses, s.pulses());
}

void test_the_lever_let_go_after_the_target_ends_the_sweep() {
    Sweep s;
    nearlyDone(s);
    s.sample(kPerSample);

    TEST_ASSERT_EQUAL(SweepAction::None, carry(s, kSweepReleaseSamples - 1, 0));
    TEST_ASSERT_TRUE(s.owed());
    TEST_ASSERT_EQUAL(SweepAction::Released, s.sample(0));
    TEST_ASSERT_FALSE(s.owed());
    TEST_ASSERT_FALSE(s.done());
    TEST_ASSERT_EQUAL(SweepState::Clear, s.state());
    TEST_ASSERT_EQUAL_UINT8(100, s.percent());

    TEST_ASSERT_EQUAL(SweepAction::None, carry(s, 100, kPerSample));
}

void test_a_sputter_after_the_target_is_not_the_lever_let_go() {
    Sweep s;
    nearlyDone(s);
    s.sample(kPerSample);

    for (int round = 0; round < 6; round++) {
        TEST_ASSERT_EQUAL(SweepAction::None, carry(s, kSweepReleaseSamples - 1, 0));
        TEST_ASSERT_EQUAL(SweepAction::None, s.sample(kPerSample));
    }
    TEST_ASSERT_TRUE(s.done());
    TEST_ASSERT_EQUAL(SweepAction::Released, carry(s, kSweepReleaseSamples, 0));
}

void test_a_sweep_given_up_with_gas_moving_waits_for_the_meter_to_go_quiet() {
    Sweep s;
    s.owe();
    carry(s, 20, 30);
    TEST_ASSERT_TRUE(s.flowing());
    const uint32_t counted = s.pulses();

    TEST_ASSERT_TRUE(s.giveUpWhileFlowing());
    TEST_ASSERT_TRUE(s.owed());
    TEST_ASSERT_TRUE(s.done());
    TEST_ASSERT_FALSE(s.flowing());

    // The lever is still down: nothing more is counted, and no target is said.
    TEST_ASSERT_EQUAL(SweepAction::None, carry(s, 400, 30));
    TEST_ASSERT_EQUAL_UINT32(counted, s.pulses());
    TEST_ASSERT_TRUE(s.owed());

    TEST_ASSERT_EQUAL(SweepAction::None, carry(s, kSweepReleaseSamples - 1, 0));
    TEST_ASSERT_EQUAL(SweepAction::Released, s.sample(0));
    TEST_ASSERT_FALSE(s.owed());
}

void test_a_sweep_is_given_up_that_way_only_while_gas_is_moving() {
    Sweep s;
    TEST_ASSERT_FALSE(s.giveUpWhileFlowing());
    TEST_ASSERT_EQUAL(SweepState::Clear, s.state());

    s.owe();
    TEST_ASSERT_FALSE(s.giveUpWhileFlowing());
    TEST_ASSERT_EQUAL(SweepState::Owed, s.state());

    // Let go short of the target, the lever is up and the count is kept for the caller.
    carry(s, 20, 30);
    carry(s, kSweepQuietSamples, 0);
    TEST_ASSERT_FALSE(s.giveUpWhileFlowing());
    TEST_ASSERT_EQUAL(SweepState::Owed, s.state());
    TEST_ASSERT_EQUAL_UINT32(600, s.pulses());
}

void test_a_meter_that_turns_slowly_on_gas_costs_a_bounded_hold() {
    Sweep s;
    s.owe();
    // One pulse a reading would take far longer than the ceiling to reach the count.
    TEST_ASSERT_TRUE(kSweepTargetPulses > kSweepCeilingSamples);
    TEST_ASSERT_EQUAL(SweepAction::Began, carry(s, kSweepCeilingSamples - 1, 1));
    TEST_ASSERT_TRUE(s.flowing());
    TEST_ASSERT_TRUE(s.percent() >= 99);
    TEST_ASSERT_EQUAL(SweepAction::Done, s.sample(1));
    TEST_ASSERT_TRUE(s.done());
    TEST_ASSERT_EQUAL_UINT8(100, s.percent());
    TEST_ASSERT_EQUAL_UINT32(kSweepCeilingSamples, s.pulses());
    TEST_ASSERT_EQUAL_UINT32(kSweepCeilingMs, s.flowedMs());
    TEST_ASSERT_EQUAL(SweepAction::Released, carry(s, kSweepReleaseSamples, 0));
}

void test_time_without_gas_moving_is_not_counted() {
    Sweep s;
    s.owe();
    carry(s, kSweepCeilingSamples * 2, 0);
    TEST_ASSERT_TRUE(s.owed());
    TEST_ASSERT_EQUAL_UINT8(0, s.percent());
    // A hold in pieces adds up to the same ceiling.
    for (uint32_t piece = 0; piece < 3; piece++) {
        carry(s, kSweepCeilingSamples / 3 - 1, 1);
        carry(s, 100, 0);
    }
    TEST_ASSERT_FALSE(s.done());
    TEST_ASSERT_EQUAL(SweepAction::Done, carry(s, 4, 1));
}

void test_a_pause_does_not_lengthen_the_sweep() {
    Sweep whole, broken;
    whole.owe();
    broken.owe();
    uint32_t whole_flowing = 0, broken_flowing = 0;
    while (!whole.done()) {
        whole.sample(25);
        whole_flowing++;
    }
    for (uint32_t i = 0; !broken.done(); i++) {
        if (i % 40 < 30) {
            broken.sample(25);
            broken_flowing++;
        } else {
            broken.sample(0);
        }
    }
    TEST_ASSERT_EQUAL_UINT32(whole_flowing, broken_flowing);
}

void test_the_percent_follows_the_count() {
    Sweep s;
    s.owe();
    const uint32_t half           = (kSweepTargetPulses + 1) / 2;
    const uint32_t three_quarters = (kSweepTargetPulses * 3 + 3) / 4;
    s.sample(half);
    TEST_ASSERT_EQUAL_UINT8(50, s.percent());
    s.sample(three_quarters - half);
    TEST_ASSERT_EQUAL_UINT8(75, s.percent());
}

void test_owing_again_starts_the_count_from_nothing() {
    Sweep s;
    s.owe();
    carry(s, 10, 30);
    s.owe();
    TEST_ASSERT_EQUAL_UINT32(0, s.pulses());
    TEST_ASSERT_FALSE(s.flowing());

    carry(s, 10, 30);
    s.clear();
    TEST_ASSERT_FALSE(s.owed());
    TEST_ASSERT_EQUAL_UINT32(0, s.pulses());
    TEST_ASSERT_EQUAL(SweepAction::None, carry(s, 50, 30));
}

void test_the_target_is_the_tank_passed_through_the_meter() {
    const uint64_t pulses_a_tank =
        static_cast<uint64_t>(kSweepPulsesPerLitre) * kSweepTankMl / 1000;
    TEST_ASSERT_EQUAL_UINT32(pulses_a_tank * kSweepTankVolumesX10 / 10, kSweepTargetPulses);
    TEST_ASSERT_TRUE(kSweepTankVolumesX10 >= 10);
}

int main(int, char **) {
    UNITY_BEGIN();
    RUN_TEST(test_a_sweep_that_is_not_owed_counts_nothing);
    RUN_TEST(test_gas_on_the_meter_begins_the_count);
    RUN_TEST(test_the_lever_let_go_pauses_the_count_and_keeps_it);
    RUN_TEST(test_one_empty_reading_inside_the_flow_does_not_pause_it);
    RUN_TEST(test_the_target_is_said_once_and_the_sweep_stays_owed_while_the_lever_is_down);
    RUN_TEST(test_the_lever_let_go_after_the_target_ends_the_sweep);
    RUN_TEST(test_a_sputter_after_the_target_is_not_the_lever_let_go);
    RUN_TEST(test_a_sweep_given_up_with_gas_moving_waits_for_the_meter_to_go_quiet);
    RUN_TEST(test_a_sweep_is_given_up_that_way_only_while_gas_is_moving);
    RUN_TEST(test_a_meter_that_turns_slowly_on_gas_costs_a_bounded_hold);
    RUN_TEST(test_time_without_gas_moving_is_not_counted);
    RUN_TEST(test_a_pause_does_not_lengthen_the_sweep);
    RUN_TEST(test_the_percent_follows_the_count);
    RUN_TEST(test_owing_again_starts_the_count_from_nothing);
    RUN_TEST(test_the_target_is_the_tank_passed_through_the_meter);
    return UNITY_END();
}
