#include <unity.h>
#include <initializer_list>
#include "../../src_front/front_cooling.h"
#include "../../src_front/front_ui_policy.h"
using namespace front_ui;
using machine_policy::ColdState;

void setUp() {}
void tearDown() {}

static void queued_and_running_operations_allow_only_stop() {
    // The input shield is raised when START is queued, and remains raised while
    // the operation is running or its authoritative answer is unavailable.
    for (bool held : {false, true}) {
        TEST_ASSERT_FALSE(allows(Action::SelectFlavor, true, held));
        TEST_ASSERT_FALSE(allows(Action::Dismiss, true, held));
        TEST_ASSERT_FALSE(allows(Action::Task, true, held));
        TEST_ASSERT_FALSE(allows(Action::Settings, true, held));
        TEST_ASSERT_FALSE(allows(Action::Edit, true, held));
        TEST_ASSERT_TRUE(allows(Action::Stop, true, held));
        TEST_ASSERT_FALSE(showBack(true, held));
    }
}

static void prime_keeps_cancellation_exits_available() {
    TEST_ASSERT_TRUE(allows(Action::Dismiss, false, true));
    TEST_ASSERT_TRUE(allows(Action::SelectFlavor, false, true));
    TEST_ASSERT_TRUE(allows(Action::Stop, false, true));
    TEST_ASSERT_FALSE(allows(Action::Task, false, true));
    TEST_ASSERT_FALSE(allows(Action::Settings, false, true));
    TEST_ASSERT_FALSE(allows(Action::Edit, false, true));
    // The held pad is the pane's one control; the rail and the portrait are the exits.
    TEST_ASSERT_FALSE(showBack(false, true));
    TEST_ASSERT_TRUE(showBack(false, false));
}

static void faucet_selection_dismisses_only_flavor_tasks() {
    TEST_ASSERT_TRUE(dismissForFaucetChange(false, true, false));
    TEST_ASSERT_FALSE(dismissForFaucetChange(true, true, false));
    TEST_ASSERT_FALSE(dismissForFaucetChange(false, false, false));
    TEST_ASSERT_FALSE(dismissForFaucetChange(false, true, true));
}

static void stale_sensor_readings_clear_at_deadline_and_across_clock_wrap() {
    TEST_ASSERT_FALSE(readingFresh(0, 1, 1500));
    TEST_ASSERT_TRUE(readingFresh(1000, 2499, 1500));
    TEST_ASSERT_FALSE(readingFresh(1000, 2500, 1500));
    TEST_ASSERT_TRUE(readingFresh(UINT32_MAX - 99, 100, 1500));
    TEST_ASSERT_FALSE(readingFresh(UINT32_MAX - 99, 1500, 1500));
}

static void available_uploads_precede_defaults_without_empty_pages() {
    uint8_t order[8];
    const uint8_t none[] = {0, 1, 2, 3};
    TEST_ASSERT_EQUAL_UINT8(4, imageOrder(0, order));
    TEST_ASSERT_EQUAL_UINT8_ARRAY(none, order, 4);
    TEST_ASSERT_EQUAL_UINT8(1, imagePages(4));

    const uint8_t sparse[] = {5, 0, 1, 2, 3};
    TEST_ASSERT_EQUAL_UINT8(5, imageOrder(0x20, order));
    TEST_ASSERT_EQUAL_UINT8_ARRAY(sparse, order, 5);
    TEST_ASSERT_EQUAL_UINT8(2, imagePages(5));

    const uint8_t two[] = {4, 6, 0, 1, 2, 3};
    TEST_ASSERT_EQUAL_UINT8(6, imageOrder(0x50, order));
    TEST_ASSERT_EQUAL_UINT8_ARRAY(two, order, 6);

    const uint8_t three[] = {4, 5, 7, 0, 1, 2, 3};
    TEST_ASSERT_EQUAL_UINT8(7, imageOrder(0xb0, order));
    TEST_ASSERT_EQUAL_UINT8_ARRAY(three, order, 7);

    const uint8_t all[] = {4, 5, 6, 7, 0, 1, 2, 3};
    TEST_ASSERT_EQUAL_UINT8(8, imageOrder(0xf0, order));
    TEST_ASSERT_EQUAL_UINT8_ARRAY(all, order, 8);
    TEST_ASSERT_EQUAL_UINT8(2, imagePages(8));
}

static StatusPayload thermalStatus(ColdState cold) {
    StatusPayload status{};
    status.coldState = static_cast<uint8_t>(cold);
    status.tankCx10 = 37;
    status.coilCx10 = -18;
    return status;
}

static void cooling_distinguishes_a_startup_countdown_from_a_later_restart_hold() {
    StatusPayload s = thermalStatus(ColdState::Holding);
    s.startupCoolingS = 75;
    TEST_ASSERT_EQUAL(CoolingState::StartupWait, coolingState(true, s));
    s.startupCoolingS = 1;
    TEST_ASSERT_EQUAL(CoolingState::StartupWait, coolingState(true, s));
    s.startupCoolingS = 0;
    TEST_ASSERT_EQUAL(CoolingState::RestartHold, coolingState(true, s));
    s.startupCoolingS = STARTUP_COOLING_RUNNING;
    TEST_ASSERT_EQUAL(CoolingState::RestartHold, coolingState(true, s));
}

static void cooling_follows_the_relay_on_start_and_during_normal_operation() {
    StatusPayload s = thermalStatus(ColdState::On);
    s.startupCoolingS = STARTUP_COOLING_RUNNING;
    TEST_ASSERT_EQUAL(CoolingState::Paused, coolingState(true, s));
    s.flags = STATUS_F_COMPRESSOR;
    TEST_ASSERT_EQUAL(CoolingState::Running, coolingState(true, s));
    s.startupCoolingS = 0;
    TEST_ASSERT_EQUAL(CoolingState::Running, coolingState(true, s));
    s.coldState = static_cast<uint8_t>(ColdState::Off);
    TEST_ASSERT_EQUAL(CoolingState::Running, coolingState(true, s));
    s.flags = 0;
    TEST_ASSERT_EQUAL(CoolingState::Idle, coolingState(true, s));
}

static void cooling_protections_keep_individual_readings_and_honor_the_gas_trip() {
    StatusPayload s = thermalStatus(ColdState::Freeze);
    TEST_ASSERT_EQUAL(CoolingState::FreezeProtection, coolingState(true, s));
    s.coldState = static_cast<uint8_t>(ColdState::Fault);
    TEST_ASSERT_EQUAL(CoolingState::ProbeFault, coolingState(true, s));
    s.coilCx10 = TEMP_UNREAD;
    TEST_ASSERT_TRUE(temperatureAvailable(true, s.tankCx10));
    TEST_ASSERT_FALSE(temperatureAvailable(true, s.coilCx10));
    s.coldState = static_cast<uint8_t>(ColdState::Off);
    TEST_ASSERT_EQUAL(CoolingState::ProbeFault, coolingState(true, s));
    s.coldState = static_cast<uint8_t>(ColdState::Fault);
    s.flags = STATUS_F_GAS_TRIP;
    TEST_ASSERT_EQUAL(CoolingState::Paused, coolingState(true, s));
}

static void cooling_requires_an_available_status_and_a_recognized_controller_state() {
    StatusPayload s = thermalStatus(ColdState::On);
    s.flags = STATUS_F_COMPRESSOR;
    TEST_ASSERT_EQUAL(CoolingState::Unavailable, coolingState(false, s));
    s.coldState = UINT8_MAX;
    TEST_ASSERT_EQUAL(CoolingState::Unavailable, coolingState(true, s));
}

static void temperatures_round_at_half_fahrenheit_and_preserve_negative_celsius_tenths() {
    char out[16];
    formatFahrenheit(out, sizeof(out), 20, true);
    TEST_ASSERT_EQUAL_STRING("36°F", out);
    formatFahrenheit(out, sizeof(out), -175, true);
    TEST_ASSERT_EQUAL_STRING("1°F", out);
    formatFahrenheit(out, sizeof(out), -225, true);
    TEST_ASSERT_EQUAL_STRING("-9°F", out);
    formatFahrenheit(out, sizeof(out), TEMP_UNREAD, true);
    TEST_ASSERT_EQUAL_STRING("--", out);
    formatFahrenheit(out, sizeof(out), 20, false);
    TEST_ASSERT_EQUAL_STRING("--", out);
    formatCelsius(out, sizeof(out), -1, true);
    TEST_ASSERT_EQUAL_STRING("-0.1°C", out);
    formatCelsius(out, sizeof(out), 0, true);
    TEST_ASSERT_EQUAL_STRING("0.0°C", out);
    formatCelsius(out, sizeof(out), TEMP_UNREAD, true);
    TEST_ASSERT_EQUAL_STRING("--", out);
    formatCelsius(out, sizeof(out), -1, false);
    TEST_ASSERT_EQUAL_STRING("--", out);
}

int main() {
    UNITY_BEGIN();
    RUN_TEST(queued_and_running_operations_allow_only_stop);
    RUN_TEST(prime_keeps_cancellation_exits_available);
    RUN_TEST(faucet_selection_dismisses_only_flavor_tasks);
    RUN_TEST(stale_sensor_readings_clear_at_deadline_and_across_clock_wrap);
    RUN_TEST(available_uploads_precede_defaults_without_empty_pages);
    RUN_TEST(cooling_distinguishes_a_startup_countdown_from_a_later_restart_hold);
    RUN_TEST(cooling_follows_the_relay_on_start_and_during_normal_operation);
    RUN_TEST(cooling_protections_keep_individual_readings_and_honor_the_gas_trip);
    RUN_TEST(cooling_requires_an_available_status_and_a_recognized_controller_state);
    RUN_TEST(temperatures_round_at_half_fahrenheit_and_preserve_negative_celsius_tenths);
    return UNITY_END();
}
