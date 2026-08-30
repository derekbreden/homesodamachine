#include <unity.h>

#include "weld_rotator_policy.h"

using namespace weld_rotator_policy;

namespace {

void test_physical_ratio_and_default_lap_are_exact() {
    TEST_ASSERT_EQUAL_UINT16(3200, kMotorPulsesPerRev);
    TEST_ASSERT_EQUAL_UINT16(14400, kTablePulsesPerRev);
    TEST_ASSERT_EQUAL_UINT32(15200, lapPulses(kDefaultOverlapDegrees));
}

void test_speed_window_maps_to_expected_rotary_motion() {
    TEST_ASSERT_FLOAT_WITHIN(0.001f, 0.772f, tableRpm(5.0f));
    TEST_ASSERT_FLOAT_WITHIN(0.001f, 1.235f, tableRpm(8.0f));
    TEST_ASSERT_FLOAT_WITHIN(0.001f, 2.316f, tableRpm(15.0f));
    TEST_ASSERT_FLOAT_WITHIN(0.1f, 185.3f, pulseHz(5.0f));
    TEST_ASSERT_FLOAT_WITHIN(0.1f, 296.4f, pulseHz(8.0f));
    TEST_ASSERT_FLOAT_WITHIN(0.1f, 555.8f, pulseHz(15.0f));
}

void test_speed_and_overlap_bounds_are_closed_intervals() {
    TEST_ASSERT_TRUE(validTravelSpeed(5.0f));
    TEST_ASSERT_TRUE(validTravelSpeed(15.0f));
    TEST_ASSERT_FALSE(validTravelSpeed(4.999f));
    TEST_ASSERT_FALSE(validTravelSpeed(15.001f));

    TEST_ASSERT_TRUE(validOverlap(0.0f));
    TEST_ASSERT_TRUE(validOverlap(60.0f));
    TEST_ASSERT_FALSE(validOverlap(-0.001f));
    TEST_ASSERT_FALSE(validOverlap(60.001f));
}

void test_boot_with_pedal_down_cannot_start_motion() {
    MotionPolicy policy;
    TEST_ASSERT_FALSE(policy.armed());
    TEST_ASSERT_EQUAL(Event::None, policy.updatePedal(true));
    TEST_ASSERT_FALSE(policy.running());
    TEST_ASSERT_EQUAL(Event::Armed, policy.updatePedal(false));
    TEST_ASSERT_TRUE(policy.armed());
    TEST_ASSERT_EQUAL(Event::Started, policy.updatePedal(true));
    TEST_ASSERT_TRUE(policy.running());
}

void test_pedal_release_aborts_a_partial_lap() {
    MotionPolicy policy;
    policy.updatePedal(false);
    policy.updatePedal(true);
    for (uint32_t i = 0; i < 100; ++i) {
        TEST_ASSERT_EQUAL(Event::None, policy.pulseEmitted());
    }
    TEST_ASSERT_EQUAL(Event::Released, policy.updatePedal(false));
    TEST_ASSERT_FALSE(policy.running());
    TEST_ASSERT_EQUAL_UINT32(100, policy.emittedPulses());
}

void test_lap_stops_on_exact_target_and_requires_release_to_rearm() {
    MotionPolicy policy;
    policy.updatePedal(false);
    policy.updatePedal(true);
    const uint32_t target = policy.targetPulses();

    for (uint32_t i = 1; i < target; ++i) {
        TEST_ASSERT_EQUAL(Event::None, policy.pulseEmitted());
        TEST_ASSERT_TRUE(policy.running());
    }
    TEST_ASSERT_EQUAL(Event::LapComplete, policy.pulseEmitted());
    TEST_ASSERT_FALSE(policy.running());
    TEST_ASSERT_FALSE(policy.armed());
    TEST_ASSERT_EQUAL_UINT32(target, policy.emittedPulses());

    TEST_ASSERT_EQUAL(Event::None, policy.updatePedal(true));
    TEST_ASSERT_FALSE(policy.running());
    TEST_ASSERT_EQUAL(Event::Armed, policy.updatePedal(false));
    TEST_ASSERT_EQUAL(Event::Started, policy.updatePedal(true));
}

void test_jog_runs_until_the_pedal_is_released() {
    MotionPolicy policy;
    TEST_ASSERT_TRUE(policy.setMode(Mode::Jog));
    policy.updatePedal(false);
    policy.updatePedal(true);
    for (uint32_t i = 0; i < kTablePulsesPerRev * 2u; ++i) {
        TEST_ASSERT_EQUAL(Event::None, policy.pulseEmitted());
    }
    TEST_ASSERT_TRUE(policy.running());
    TEST_ASSERT_EQUAL(Event::Released, policy.updatePedal(false));
    TEST_ASSERT_FALSE(policy.running());
}

void test_running_configuration_cannot_change_under_the_part() {
    MotionPolicy policy;
    policy.updatePedal(false);
    policy.updatePedal(true);
    TEST_ASSERT_FALSE(policy.setMode(Mode::Jog));
    TEST_ASSERT_FALSE(policy.setLapTarget(16000));
    TEST_ASSERT_EQUAL(Event::Stopped, policy.stop());
    TEST_ASSERT_TRUE(policy.setMode(Mode::Jog));
    TEST_ASSERT_TRUE(policy.setLapTarget(16000));
}

}  // namespace

int main(int, char **) {
    UNITY_BEGIN();
    RUN_TEST(test_physical_ratio_and_default_lap_are_exact);
    RUN_TEST(test_speed_window_maps_to_expected_rotary_motion);
    RUN_TEST(test_speed_and_overlap_bounds_are_closed_intervals);
    RUN_TEST(test_boot_with_pedal_down_cannot_start_motion);
    RUN_TEST(test_pedal_release_aborts_a_partial_lap);
    RUN_TEST(test_lap_stops_on_exact_target_and_requires_release_to_rearm);
    RUN_TEST(test_jog_runs_until_the_pedal_is_released);
    RUN_TEST(test_running_configuration_cannot_change_under_the_part);
    return UNITY_END();
}
