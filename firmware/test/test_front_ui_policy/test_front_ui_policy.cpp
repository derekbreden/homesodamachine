#include <unity.h>
#include <initializer_list>
#include "../../src_front/front_cooling.h"
#include "../../src_front/front_temperature_unit.h"
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

static void temperatures_round_once_in_the_selected_unit() {
    char out[16];
    const struct { int16_t cx10; const char *f, *c, *probeF, *probeC; } readings[] = {
        {168, "62°F", "17°C", "62.2°F", "16.8°C"},
        {-175, "1°F", "-18°C", "0.5°F", "-17.5°C"},
        {-225, "-9°F", "-23°C", "-8.5°F", "-22.5°C"},
        {-1, "32°F", "0°C", "31.8°F", "-0.1°C"},
        {-178, "0°F", "-18°C", "0.0°F", "-17.8°C"},
        {-550, "-67°F", "-55°C", "-67.0°F", "-55.0°C"},
        {1250, "257°F", "125°C", "257.0°F", "125.0°C"},
        {TEMP_UNREAD, "--", "--", "--", "--"},
    };
    for (const auto &r : readings) {
        formatTemperature(out, sizeof(out), r.cx10, true, TEMP_UNIT_FAHRENHEIT, Degrees::Whole);
        TEST_ASSERT_EQUAL_STRING(r.f, out);
        formatTemperature(out, sizeof(out), r.cx10, true, TEMP_UNIT_CELSIUS, Degrees::Whole);
        TEST_ASSERT_EQUAL_STRING(r.c, out);
        formatTemperature(out, sizeof(out), r.cx10, true, TEMP_UNIT_FAHRENHEIT, Degrees::Tenths);
        TEST_ASSERT_EQUAL_STRING(r.probeF, out);
        formatTemperature(out, sizeof(out), r.cx10, true, TEMP_UNIT_CELSIUS, Degrees::Tenths);
        TEST_ASSERT_EQUAL_STRING(r.probeC, out);
    }
    for (uint8_t unit : {TEMP_UNIT_CELSIUS, TEMP_UNIT_FAHRENHEIT}) {
        formatTemperature(out, sizeof(out), 168, false, unit, Degrees::Whole);
        TEST_ASSERT_EQUAL_STRING("--", out);
        formatTemperature(out, sizeof(out), 168, false, unit, Degrees::Tenths);
        TEST_ASSERT_EQUAL_STRING("--", out);
    }
}

static void unitReadback(TemperatureUnitSetting &s, uint8_t result, uint64_t revision,
                         uint8_t unit, uint32_t now) {
    uint8_t frame[SETTING_STATE_HEADER_SIZE + 1] = {SETTING_TEMPERATURE_UNIT, SETTING_GLOBAL, result};
    for (uint8_t i = 0; i < 8; ++i) frame[3 + i] = uint8_t(revision >> (i * 8));
    frame[11] = 1;
    frame[12] = unit;
    s.receive(frame, sizeof(frame), now);
}

static void unit_changes_need_a_fresh_machine_revision() {
    TemperatureUnitSetting s;
    uint8_t write[SETTING_SET_HEADER_SIZE + 1];
    TEST_ASSERT_EQUAL_UINT8(TEMP_UNIT_FAHRENHEIT, s.unit());
    TEST_ASSERT_FALSE(s.select(TEMP_UNIT_CELSIUS, 0, write));
    TEST_ASSERT_TRUE(s.queryDue(0));
    TEST_ASSERT_FALSE(s.queryDue(100));
    const uint8_t oldBoard[SETTING_STATE_HEADER_SIZE] = {SETTING_TEMPERATURE_UNIT, SETTING_GLOBAL, SETTING_INVALID};
    s.receive(oldBoard, sizeof(oldBoard), 120);
    TEST_ASSERT_EQUAL(TemperatureUnitSetting::State::Unsupported, s.state(150));
    TEST_ASSERT_FALSE(s.select(TEMP_UNIT_CELSIUS, 150, write));

    unitReadback(s, SETTING_OK, 0x123456789ABCDEF0ull, TEMP_UNIT_CELSIUS, UINT32_MAX - 100);
    TEST_ASSERT_TRUE(s.canChange(1));
    TEST_ASSERT_FALSE(s.select(TEMP_UNIT_CELSIUS, 1, write));
    TEST_ASSERT_FALSE(s.select(2, 1, write));
    TEST_ASSERT_TRUE(s.select(TEMP_UNIT_FAHRENHEIT, 20, write));
    const uint8_t expected[] = {SETTING_TEMPERATURE_UNIT, SETTING_GLOBAL, 0xF0, 0xDE, 0xBC,
                                 0x9A, 0x78, 0x56, 0x34, 0x12, 1, TEMP_UNIT_FAHRENHEIT};
    TEST_ASSERT_EQUAL_UINT8_ARRAY(expected, write, sizeof(expected));
    TEST_ASSERT_EQUAL_UINT8(TEMP_UNIT_CELSIUS, s.unit());
    TEST_ASSERT_FALSE(s.canChange(30));
    unitReadback(s, SETTING_OK, 43, TEMP_UNIT_FAHRENHEIT, 40);
    TEST_ASSERT_EQUAL_UINT8(TEMP_UNIT_FAHRENHEIT, s.unit());
    TEST_ASSERT_FALSE(s.select(TEMP_UNIT_CELSIUS, 6000, write));
    TEST_ASSERT_EQUAL(TemperatureUnitSetting::State::Waiting, s.state(6000));
    unitReadback(s, SETTING_OK, 45, TEMP_UNIT_CELSIUS, 6100);
    s.observeControllerUptime(100, 820, 720000);  // The glass slept while the controller kept running.
    TEST_ASSERT_EQUAL_UINT8(TEMP_UNIT_CELSIUS, s.unit());
    s.observeControllerUptime(820, 10, 15000);
    TEST_ASSERT_EQUAL_UINT8(TEMP_UNIT_FAHRENHEIT, s.unit());
    TEST_ASSERT_FALSE(s.canChange(6200));
    TEST_ASSERT_TRUE(s.queryDue(6200));
}

static void lost_unit_acknowledgments_reconcile_without_overwriting_a_phone_change() {
    using State = TemperatureUnitSetting::State;
    TemperatureUnitSetting s;
    uint8_t write[SETTING_SET_HEADER_SIZE + 1];
    unitReadback(s, SETTING_OK, 41, TEMP_UNIT_FAHRENHEIT, 1000);
    TEST_ASSERT_TRUE(s.select(TEMP_UNIT_CELSIUS, 1010, write));
    unitReadback(s, SETTING_OK, 41, TEMP_UNIT_FAHRENHEIT, 1020);  // Earlier GET still in flight.
    TEST_ASSERT_EQUAL(State::Updating, s.state(1020));
    TEST_ASSERT_EQUAL_UINT8(TEMP_UNIT_FAHRENHEIT, s.unit());
    TEST_ASSERT_FALSE(s.queryDue(1200));
    TEST_ASSERT_TRUE(s.queryDue(1500));
    unitReadback(s, SETTING_OK, 42, TEMP_UNIT_CELSIUS, 1510);  // A later GET recovers the lost ACK.
    TEST_ASSERT_EQUAL(State::Ready, s.state(1510));
    TEST_ASSERT_EQUAL_UINT8(TEMP_UNIT_CELSIUS, s.unit());

    TEST_ASSERT_TRUE(s.select(TEMP_UNIT_FAHRENHEIT, 1600, write));
    unitReadback(s, SETTING_CONFLICT, 44, TEMP_UNIT_CELSIUS, 1620);
    TEST_ASSERT_EQUAL(State::ChangedElsewhere, s.state(1620));
    TEST_ASSERT_EQUAL_UINT8(TEMP_UNIT_CELSIUS, s.unit());
    TEST_ASSERT_TRUE(s.select(TEMP_UNIT_FAHRENHEIT, 2000, write));
    TEST_ASSERT_EQUAL_UINT8(44, write[2]);
    TEST_ASSERT_EQUAL(State::Unconfirmed, s.state(4500));
    unitReadback(s, SETTING_OK, 44, TEMP_UNIT_CELSIUS, 4600);
    TEST_ASSERT_EQUAL(State::Unconfirmed, s.state(4600));
    TEST_ASSERT_TRUE(s.canChange(4600));
    unitReadback(s, SETTING_STORAGE_FAILURE, 44, TEMP_UNIT_CELSIUS, 4700);
    TEST_ASSERT_EQUAL(State::StorageError, s.state(4700));
    TEST_ASSERT_FALSE(s.canChange(4700));
    unitReadback(s, SETTING_OK, 45, TEMP_UNIT_FAHRENHEIT, 4800);
    TEST_ASSERT_EQUAL(State::Ready, s.state(4800));
    TEST_ASSERT_EQUAL_UINT8(TEMP_UNIT_FAHRENHEIT, s.unit());
}

static void damaged_or_unrelated_setting_frames_do_not_change_the_unit() {
    TemperatureUnitSetting s;
    uint8_t bytes[SETTING_STATE_HEADER_SIZE + 1] = {SETTING_TEMPERATURE_UNIT, SETTING_GLOBAL, SETTING_OK, 91};
    bytes[11] = 1; bytes[12] = TEMP_UNIT_CELSIUS;
    s.receive(bytes, sizeof(bytes) - 1, 1000);
    bytes[0] = SETTING_SOUND;
    s.receive(bytes, sizeof(bytes), 1001);
    bytes[0] = SETTING_TEMPERATURE_UNIT; bytes[1] = 0;
    s.receive(bytes, sizeof(bytes), 1002);
    unitReadback(s, SETTING_OK, 0, TEMP_UNIT_CELSIUS, 1003);
    unitReadback(s, SETTING_OK, 1, 2, 1004);
    TEST_ASSERT_EQUAL_UINT8(TEMP_UNIT_FAHRENHEIT, s.unit());
    TEST_ASSERT_FALSE(s.canChange(1010));
    unitReadback(s, SETTING_STORAGE_FAILURE, 0, TEMP_UNIT_CELSIUS, 1020);
    TEST_ASSERT_EQUAL_UINT8(TEMP_UNIT_CELSIUS, s.unit());
    TEST_ASSERT_FALSE(s.canChange(1020));
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
    RUN_TEST(temperatures_round_once_in_the_selected_unit);
    RUN_TEST(unit_changes_need_a_fresh_machine_revision);
    RUN_TEST(lost_unit_acknowledgments_reconcile_without_overwriting_a_phone_change);
    RUN_TEST(damaged_or_unrelated_setting_frames_do_not_change_the_unit);
    return UNITY_END();
}
