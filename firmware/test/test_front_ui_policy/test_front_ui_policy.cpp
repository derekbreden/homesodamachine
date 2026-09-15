#include <unity.h>
#include <initializer_list>
#include "../../src_front/front_ui_policy.h"
using namespace front_ui;

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
        TEST_ASSERT_FALSE(showDone(false, true));
    }
}

static void prime_keeps_cancellation_exits_available() {
    TEST_ASSERT_TRUE(allows(Action::Dismiss, false, true));
    TEST_ASSERT_TRUE(allows(Action::SelectFlavor, false, true));
    TEST_ASSERT_TRUE(allows(Action::Stop, false, true));
    TEST_ASSERT_FALSE(allows(Action::Task, false, true));
    TEST_ASSERT_FALSE(allows(Action::Settings, false, true));
    TEST_ASSERT_FALSE(allows(Action::Edit, false, true));
    TEST_ASSERT_TRUE(showDone(false, false));
}

static void faucet_selection_dismisses_only_flavor_tasks() {
    TEST_ASSERT_TRUE(dismissForFaucetChange(false, true, false));
    TEST_ASSERT_FALSE(dismissForFaucetChange(true, true, false));
    TEST_ASSERT_FALSE(dismissForFaucetChange(false, false, false));
    TEST_ASSERT_FALSE(dismissForFaucetChange(false, true, true));
    TEST_ASSERT_FALSE(showDone(true, false));
}

static void stale_sensor_readings_clear_at_deadline_and_across_clock_wrap() {
    TEST_ASSERT_FALSE(readingFresh(0, 1, 1500));
    TEST_ASSERT_TRUE(readingFresh(1000, 2499, 1500));
    TEST_ASSERT_FALSE(readingFresh(1000, 2500, 1500));
    TEST_ASSERT_TRUE(readingFresh(UINT32_MAX - 99, 100, 1500));
    TEST_ASSERT_FALSE(readingFresh(UINT32_MAX - 99, 1500, 1500));
}

int main() {
    UNITY_BEGIN();
    RUN_TEST(queued_and_running_operations_allow_only_stop);
    RUN_TEST(prime_keeps_cancellation_exits_available);
    RUN_TEST(faucet_selection_dismisses_only_flavor_tasks);
    RUN_TEST(stale_sensor_readings_clear_at_deadline_and_across_clock_wrap);
    return UNITY_END();
}
