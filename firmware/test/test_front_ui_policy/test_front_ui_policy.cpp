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

int main() {
    UNITY_BEGIN();
    RUN_TEST(queued_and_running_operations_allow_only_stop);
    RUN_TEST(prime_keeps_cancellation_exits_available);
    RUN_TEST(faucet_selection_dismisses_only_flavor_tasks);
    RUN_TEST(stale_sensor_readings_clear_at_deadline_and_across_clock_wrap);
    RUN_TEST(available_uploads_precede_defaults_without_empty_pages);
    return UNITY_END();
}
