#include <unity.h>

#include "weld_rotator_policy.h"

using namespace weld_rotator_policy;

namespace {

void test_physical_ratio_is_exact() {
    TEST_ASSERT_EQUAL_UINT16(3200, kMotorPulsesPerRev);
    TEST_ASSERT_EQUAL_UINT16(14400, kTablePulsesPerRev);
    TEST_ASSERT_FLOAT_WITHIN(0.001f, 360.0f, degreesTurned(kTablePulsesPerRev));
    TEST_ASSERT_FLOAT_WITHIN(0.001f, 0.025f, degreesTurned(1));
}

void test_speed_window_maps_to_expected_rotary_motion() {
    TEST_ASSERT_FLOAT_WITHIN(0.001f, 0.772f, tableRpm(5.0f));
    TEST_ASSERT_FLOAT_WITHIN(0.001f, 1.235f, tableRpm(8.0f));
    TEST_ASSERT_FLOAT_WITHIN(0.001f, 2.316f, tableRpm(15.0f));
    TEST_ASSERT_FLOAT_WITHIN(0.1f, 185.3f, pulseHz(5.0f));
    TEST_ASSERT_FLOAT_WITHIN(0.1f, 296.4f, pulseHz(8.0f));
    TEST_ASSERT_FLOAT_WITHIN(0.1f, 555.8f, pulseHz(15.0f));
}

void test_speed_bounds_are_a_closed_interval() {
    TEST_ASSERT_TRUE(validTravelSpeed(5.0f));
    TEST_ASSERT_TRUE(validTravelSpeed(15.0f));
    TEST_ASSERT_FALSE(validTravelSpeed(4.999f));
    TEST_ASSERT_FALSE(validTravelSpeed(15.001f));
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

// The property Derek asked for: no count, no limit, no stop the operator did
// not command.  Ten revolutions is well past any lap the fixture ever ran.
void test_the_table_never_stops_itself() {
    MotionPolicy policy;
    policy.updatePedal(false);
    policy.updatePedal(true);
    for (uint32_t i = 0; i < kTablePulsesPerRev * 10u; ++i) {
        policy.recordPulse();
        TEST_ASSERT_TRUE(policy.running());
    }
    TEST_ASSERT_TRUE(policy.running());
    TEST_ASSERT_TRUE(policy.armed());
    TEST_ASSERT_EQUAL_UINT32(kTablePulsesPerRev * 10u, policy.emittedPulses());
    TEST_ASSERT_FLOAT_WITHIN(0.01f, 3600.0f,
                             degreesTurned(policy.emittedPulses()));
}

void test_release_stops_and_the_next_press_starts_again_immediately() {
    MotionPolicy policy;
    policy.updatePedal(false);
    policy.updatePedal(true);
    for (uint32_t i = 0; i < 100; ++i) policy.recordPulse();

    TEST_ASSERT_EQUAL(Event::Released, policy.updatePedal(false));
    TEST_ASSERT_FALSE(policy.running());
    TEST_ASSERT_EQUAL_UINT32(100, policy.emittedPulses());

    // Releasing never disarms, so the pedal is live again with no ceremony.
    TEST_ASSERT_TRUE(policy.armed());
    TEST_ASSERT_EQUAL(Event::Started, policy.updatePedal(true));
    TEST_ASSERT_TRUE(policy.running());
    TEST_ASSERT_EQUAL_UINT32(0, policy.emittedPulses());
}

void test_pulses_are_only_counted_while_running() {
    MotionPolicy policy;
    policy.recordPulse();
    TEST_ASSERT_EQUAL_UINT32(0, policy.emittedPulses());

    policy.updatePedal(false);
    policy.updatePedal(true);
    policy.recordPulse();
    TEST_ASSERT_EQUAL_UINT32(1, policy.emittedPulses());

    TEST_ASSERT_EQUAL(Event::Stopped, policy.stop());
    policy.recordPulse();
    TEST_ASSERT_EQUAL_UINT32(1, policy.emittedPulses());
    TEST_ASSERT_EQUAL(Event::None, policy.stop());
}

// The motor is held only while it has work.  At boot nothing has stopped, so
// nothing is held; a release starts the grace period; the wrap of millis()
// does not extend or cut it.
void test_driver_holds_only_while_it_has_work() {
    TEST_ASSERT_FALSE(driverHolds(false, 0, 5));
    TEST_ASSERT_TRUE(driverHolds(true, 0, 5));

    const uint32_t deadline = holdDeadline(1000);
    TEST_ASSERT_TRUE(driverHolds(false, deadline, 1000));
    TEST_ASSERT_TRUE(driverHolds(false, deadline, 1000 + kHoldAfterReleaseMs - 1));
    TEST_ASSERT_FALSE(driverHolds(false, deadline, 1000 + kHoldAfterReleaseMs));

    const uint32_t late = 0xFFFFFF00u;
    TEST_ASSERT_TRUE(driverHolds(false, holdDeadline(late), late + 5000u));
    TEST_ASSERT_FALSE(driverHolds(false, holdDeadline(late),
                                  late + kHoldAfterReleaseMs + 1u));
}

}  // namespace

int main(int, char **) {
    UNITY_BEGIN();
    RUN_TEST(test_physical_ratio_is_exact);
    RUN_TEST(test_speed_window_maps_to_expected_rotary_motion);
    RUN_TEST(test_speed_bounds_are_a_closed_interval);
    RUN_TEST(test_boot_with_pedal_down_cannot_start_motion);
    RUN_TEST(test_the_table_never_stops_itself);
    RUN_TEST(test_release_stops_and_the_next_press_starts_again_immediately);
    RUN_TEST(test_pulses_are_only_counted_while_running);
    RUN_TEST(test_driver_holds_only_while_it_has_work);
    return UNITY_END();
}
