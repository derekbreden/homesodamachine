#include <unity.h>

#include "move_policy.h"

using namespace machine_policy;

void setUp() {}
void tearDown() {}

static RefillReading reeds(bool low, bool high, bool valid = true) {
    RefillReading r;
    r.lowClosed  = low;
    r.highClosed = high;
    r.valid      = valid;
    return r;
}

static const RefillReading kBetween = reeds(false, false);

static void carry(Move &m, uint32_t samples, uint32_t pulses, const RefillReading &rd = kBetween) {
    for (uint32_t i = 0; i < samples; i++) m.sample(pulses, rd);
}

void test_a_machine_that_is_not_moving_counts_nothing() {
    Move m;
    TEST_ASSERT_FALSE(m.moving());
    carry(m, 200, 40, reeds(true, false));
    TEST_ASSERT_FALSE(m.flowing());
    TEST_ASSERT_FALSE(m.belowLow());
    TEST_ASSERT_EQUAL_UINT32(0, m.pulses());
}

void test_the_meter_turning_says_something_is_leaving() {
    Move m;
    m.begin(false);
    TEST_ASSERT_TRUE(m.moving());
    TEST_ASSERT_FALSE(m.flowing());

    m.sample(30, kBetween);
    TEST_ASSERT_TRUE(m.flowing());
    carry(m, 9, 30);
    TEST_ASSERT_EQUAL_UINT32(300, m.pulses());

    // One empty reading inside the flow is not the lever let go.
    carry(m, kSweepQuietSamples - 1, 0);
    TEST_ASSERT_TRUE(m.flowing());
    m.sample(0, kBetween);
    TEST_ASSERT_FALSE(m.flowing());
    TEST_ASSERT_EQUAL_UINT32(300, m.pulses());

    m.sample(30, kBetween);
    TEST_ASSERT_TRUE(m.flowing());
    TEST_ASSERT_EQUAL_UINT32(330, m.pulses());
}

void test_the_float_passing_the_low_reed_says_the_water_is_below_it() {
    Move m;
    m.begin(false);
    carry(m, 40, 30, reeds(false, true));
    TEST_ASSERT_FALSE(m.belowLow());
    carry(m, 40, 30, kBetween);
    TEST_ASSERT_FALSE(m.belowLow());

    // In the low reed's window the water is at the mark, not yet below it.
    carry(m, 40, 30, reeds(true, false));
    TEST_ASSERT_FALSE(m.belowLow());
    carry(m, kSweepQuietSamples - 1, 30, kBetween);
    TEST_ASSERT_FALSE(m.belowLow());
    m.sample(30, kBetween);
    TEST_ASSERT_TRUE(m.belowLow());

    // Nothing reads closed from there down, and the answer stands.
    carry(m, 400, 0, kBetween);
    TEST_ASSERT_TRUE(m.belowLow());
}

void test_a_reed_that_blinks_open_in_its_window_is_not_the_water_below_it() {
    Move m;
    m.begin(false);
    carry(m, 10, 30, reeds(true, false));
    carry(m, kSweepQuietSamples - 1, 30, kBetween);
    carry(m, 10, 30, reeds(true, false));
    carry(m, kSweepQuietSamples - 1, 30, kBetween);
    TEST_ASSERT_FALSE(m.belowLow());
}

void test_reeds_that_cannot_be_read_say_nothing_of_the_water() {
    Move m;
    m.begin(false);
    carry(m, 10, 30, reeds(true, false));
    carry(m, 400, 30, reeds(false, false, false));
    TEST_ASSERT_FALSE(m.belowLow());
    TEST_ASSERT_TRUE(m.flowing());
}

void test_water_already_below_the_low_reed_is_known_from_the_start() {
    Move m;
    m.begin(true);
    TEST_ASSERT_TRUE(m.belowLow());
    carry(m, 40, 30, kBetween);
    TEST_ASSERT_TRUE(m.belowLow());

    // A float found at a reed is at that mark, whatever was said.
    m.sample(0, reeds(true, false));
    TEST_ASSERT_FALSE(m.belowLow());
    carry(m, kSweepQuietSamples, 0, kBetween);
    TEST_ASSERT_TRUE(m.belowLow());
    m.sample(0, reeds(false, true));
    TEST_ASSERT_FALSE(m.belowLow());
    carry(m, 40, 0, kBetween);
    TEST_ASSERT_FALSE(m.belowLow());
}

void test_a_move_called_off_forgets_what_it_saw() {
    Move m;
    m.begin(true);
    carry(m, 10, 30);
    m.end();
    TEST_ASSERT_FALSE(m.moving());
    TEST_ASSERT_FALSE(m.flowing());
    TEST_ASSERT_FALSE(m.belowLow());
    TEST_ASSERT_EQUAL_UINT32(0, m.pulses());

    m.begin(false);
    TEST_ASSERT_TRUE(m.moving());
    TEST_ASSERT_FALSE(m.belowLow());
    TEST_ASSERT_EQUAL_UINT32(0, m.pulses());
}

int main(int, char **) {
    UNITY_BEGIN();
    RUN_TEST(test_a_machine_that_is_not_moving_counts_nothing);
    RUN_TEST(test_the_meter_turning_says_something_is_leaving);
    RUN_TEST(test_the_float_passing_the_low_reed_says_the_water_is_below_it);
    RUN_TEST(test_a_reed_that_blinks_open_in_its_window_is_not_the_water_below_it);
    RUN_TEST(test_reeds_that_cannot_be_read_say_nothing_of_the_water);
    RUN_TEST(test_water_already_below_the_low_reed_is_known_from_the_start);
    RUN_TEST(test_a_move_called_off_forgets_what_it_saw);
    return UNITY_END();
}
