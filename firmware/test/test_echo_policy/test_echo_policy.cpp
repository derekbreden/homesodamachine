#include <string.h>
#include <unity.h>

#include "echo_policy.h"

using namespace echo_policy;

void setUp() {}
void tearDown() {}

// Hand the matcher a frame and read the wire back at it, byte for byte.
static void echoBack(EchoMatcher &m, const uint8_t *frame, size_t n) {
    m.sent(frame, n);
    for (size_t i = 0; i < n; i++) TEST_ASSERT_TRUE(m.consumeEcho(frame[i]));
}

void test_a_frame_this_end_sent_comes_back_and_is_swallowed_whole() {
    EchoMatcher m;
    const uint8_t frame[] = {0x7E, 0x16, 0x01, 0x8F, 0xDF, 0x7E};
    echoBack(m, frame, sizeof(frame));
    TEST_ASSERT_EQUAL_UINT32(0, m.outstanding());
    TEST_ASSERT_EQUAL_UINT32(sizeof(frame), m.swallowed());
    TEST_ASSERT_EQUAL_UINT32(0, m.desyncs());
    TEST_ASSERT_FALSE(m.expecting());
}

// Nothing sent, so nothing on the wire is ours.
void test_traffic_arriving_with_nothing_outstanding_is_the_far_end() {
    EchoMatcher m;
    TEST_ASSERT_FALSE(m.consumeEcho(0x7E));
    TEST_ASSERT_EQUAL_UINT32(0, m.desyncs());   // not a collision, just their turn
    TEST_ASSERT_EQUAL_UINT32(0, m.swallowed());
}

// THE FAILURE THE MATCHER EXISTS FOR. A count would stay in deficit from here
// and eat the far end's next frames as its own echo. Matching abandons the
// expectation on the first wrong byte and hands everything after it to the framer.
void test_a_collision_abandons_the_echo_instead_of_going_deaf() {
    EchoMatcher m;
    const uint8_t sent[] = {0x7E, 0x16, 0x01, 0x8F, 0xDF, 0x7E};
    m.sent(sent, sizeof(sent));

    TEST_ASSERT_TRUE(m.consumeEcho(0x7E));      // the first byte survived
    TEST_ASSERT_FALSE(m.consumeEcho(0x55));     // the rest was destroyed on the wire
    TEST_ASSERT_EQUAL_UINT32(1, m.desyncs());
    TEST_ASSERT_EQUAL_UINT32(0, m.outstanding());
    TEST_ASSERT_FALSE(m.expecting());

    // And the very next frame from the far end reaches the framer untouched,
    // which is what a byte-counting canceller could not do.
    const uint8_t theirs[] = {0x7E, 0x29, 0x11, 0x7E};
    for (size_t i = 0; i < sizeof(theirs); i++) TEST_ASSERT_FALSE(m.consumeEcho(theirs[i]));
    TEST_ASSERT_EQUAL_UINT32(1, m.desyncs());   // still the one collision
    TEST_ASSERT_EQUAL_UINT32(1, m.swallowed());
}

// A short echo — the tail eaten rather than a byte changed — is the same story.
void test_an_echo_that_stops_early_leaves_the_next_frame_readable() {
    EchoMatcher m;
    const uint8_t sent[] = {0xAA, 0xBB, 0xCC, 0xDD};
    m.sent(sent, sizeof(sent));
    TEST_ASSERT_TRUE(m.consumeEcho(0xAA));
    TEST_ASSERT_TRUE(m.consumeEcho(0xBB));
    TEST_ASSERT_FALSE(m.consumeEcho(0x7E));     // their flag, where our 0xCC should be
    TEST_ASSERT_EQUAL_UINT32(1, m.desyncs());
    TEST_ASSERT_FALSE(m.expecting());
}

// The main board sends several frames before draining; they come back in order.
void test_frames_queue_and_come_back_in_the_order_they_went_out() {
    EchoMatcher m;
    const uint8_t a[] = {0x01, 0x02};
    const uint8_t b[] = {0x03, 0x04, 0x05};
    m.sent(a, sizeof(a));
    m.sent(b, sizeof(b));
    TEST_ASSERT_EQUAL_UINT32(5, m.outstanding());
    for (uint8_t v = 0x01; v <= 0x05; v++) TEST_ASSERT_TRUE(m.consumeEcho(v));
    TEST_ASSERT_EQUAL_UINT32(0, m.outstanding());
    TEST_ASSERT_EQUAL_UINT32(0, m.desyncs());
}

// The ring wraps under sustained traffic and keeps matching.
void test_the_ring_wraps_without_losing_its_place() {
    EchoMatcher m;
    uint8_t frame[512];
    for (size_t i = 0; i < sizeof(frame); i++) frame[i] = (uint8_t)(i * 7 + 3);
    for (int pass = 0; pass < 40; pass++) {   // 20 KB through a 4 KB ring
        echoBack(m, frame, sizeof(frame));
        TEST_ASSERT_EQUAL_UINT32(0, m.outstanding());
    }
    TEST_ASSERT_EQUAL_UINT32(0, m.desyncs());
    TEST_ASSERT_EQUAL_UINT32(40 * sizeof(frame), m.swallowed());
}

// A whole J9 frame, stuffed at its worst, fits with room to spare.
void test_the_ring_holds_the_largest_frame_this_pair_carries() {
    EchoMatcher m;
    static uint8_t big[EchoMatcher::kCapacity];
    for (size_t i = 0; i < sizeof(big); i++) big[i] = (uint8_t)(i ^ 0x5A);
    m.sent(big, sizeof(big));
    TEST_ASSERT_EQUAL_UINT32(EchoMatcher::kCapacity, m.outstanding());
    TEST_ASSERT_EQUAL_UINT32(EchoMatcher::kCapacity, m.highWater());
    for (size_t i = 0; i < sizeof(big); i++) TEST_ASSERT_TRUE(m.consumeEcho(big[i]));
    TEST_ASSERT_EQUAL_UINT32(0, m.desyncs());
}

// High water is the deepest the ring ever stood, not where it stands now.
void test_high_water_is_the_deepest_it_ever_stood() {
    EchoMatcher m;
    const uint8_t frame[] = {1, 2, 3, 4, 5, 6, 7, 8};
    echoBack(m, frame, sizeof(frame));
    TEST_ASSERT_EQUAL_UINT32(0, m.outstanding());
    TEST_ASSERT_EQUAL_UINT32(sizeof(frame), m.highWater());
}

int main(int, char **) {
    UNITY_BEGIN();
    RUN_TEST(test_a_frame_this_end_sent_comes_back_and_is_swallowed_whole);
    RUN_TEST(test_traffic_arriving_with_nothing_outstanding_is_the_far_end);
    RUN_TEST(test_a_collision_abandons_the_echo_instead_of_going_deaf);
    RUN_TEST(test_an_echo_that_stops_early_leaves_the_next_frame_readable);
    RUN_TEST(test_frames_queue_and_come_back_in_the_order_they_went_out);
    RUN_TEST(test_the_ring_wraps_without_losing_its_place);
    RUN_TEST(test_the_ring_holds_the_largest_frame_this_pair_carries);
    RUN_TEST(test_high_water_is_the_deepest_it_ever_stood);
    return UNITY_END();
}
