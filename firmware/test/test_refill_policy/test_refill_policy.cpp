#include <unity.h>

#include "refill_policy.h"

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

static RefillContext ctx(bool dispenseOpen, bool machineIdle = true) {
    RefillContext c;
    c.dispenseOpen = dispenseOpen;
    c.machineIdle  = machineIdle;
    return c;
}

static RefillAction step(Refill &r, uint32_t now, const RefillReading &rd, const RefillContext &c) {
    r.reading(rd, now);
    return r.service(now, c);
}

// Carry the loop forward, feeding the same reeds and context.
static RefillAction carry(Refill &r, uint32_t from, uint32_t until,
                          const RefillReading &rd, const RefillContext &c, uint32_t dt = 1000) {
    RefillAction last = RefillAction::None;
    for (uint32_t t = from; t < until; t += dt) {
        const RefillAction a = step(r, t, rd, c);
        if (a != RefillAction::None) last = a;
    }
    return last;
}

void test_an_idle_carbonator_asks_for_nothing() {
    Refill r;
    TEST_ASSERT_EQUAL(RefillState::Idle, r.state());
    TEST_ASSERT_EQUAL(RefillAction::None, step(r, 1000, reeds(false, false), ctx(false)));
    TEST_ASSERT_EQUAL(RefillState::Idle, r.state());
    TEST_ASSERT_FALSE(r.pumpOn());
}

void test_the_low_reed_is_believed_only_after_the_debounce() {
    Refill r;
    const RefillReading low = reeds(true, false);
    TEST_ASSERT_EQUAL(RefillAction::None, step(r, 1000, low, ctx(false)));
    TEST_ASSERT_EQUAL(RefillState::Idle, r.state());

    TEST_ASSERT_EQUAL(RefillAction::None, step(r, 1000 + kRefillDebounceMs - 1, low, ctx(false)));
    TEST_ASSERT_EQUAL(RefillState::Idle, r.state());

    // Debounce met, nothing else holds the actuators: queued and running in one pass.
    TEST_ASSERT_EQUAL(RefillAction::Start, step(r, 1000 + kRefillDebounceMs, low, ctx(false)));
    TEST_ASSERT_EQUAL(RefillState::Filling, r.state());
    TEST_ASSERT_TRUE(r.pumpOn());
}

void test_a_surface_that_settles_back_resets_the_debounce() {
    Refill r;
    step(r, 1000, reeds(true, false), ctx(false));
    step(r, 1500, reeds(false, false), ctx(false));   // the donut lifted again
    TEST_ASSERT_EQUAL(RefillAction::None, step(r, 2000, reeds(true, false), ctx(false)));
    TEST_ASSERT_EQUAL(RefillState::Idle, r.state());
    TEST_ASSERT_EQUAL(RefillAction::Start, step(r, 2000 + kRefillDebounceMs, reeds(true, false), ctx(false)));
}

void test_the_ask_that_arrives_mid_pour_waits_for_the_window_to_close() {
    Refill r;
    const RefillReading low = reeds(true, false);
    // CLO closes while the glass is filling. The window refuses relay #2.
    step(r, 1000, low, ctx(true));
    TEST_ASSERT_EQUAL(RefillAction::None, step(r, 1000 + kRefillDebounceMs, low, ctx(true)));
    TEST_ASSERT_EQUAL(RefillState::Queued, r.state());
    TEST_ASSERT_FALSE(r.pumpOn());

    TEST_ASSERT_EQUAL(RefillAction::None, carry(r, 1000 + kRefillDebounceMs, 20000, low, ctx(true)));
    TEST_ASSERT_EQUAL(RefillState::Queued, r.state());

    // The pour ends.
    TEST_ASSERT_EQUAL(RefillAction::Start, step(r, 20000, low, ctx(false)));
    TEST_ASSERT_EQUAL(RefillState::Filling, r.state());
}

void test_a_dispense_opening_mid_refill_takes_the_relay_down() {
    Refill r;
    const RefillReading low = reeds(true, false);
    step(r, 1000, low, ctx(false));
    step(r, 1000 + kRefillDebounceMs, low, ctx(false));
    TEST_ASSERT_EQUAL(RefillState::Filling, r.state());

    TEST_ASSERT_EQUAL(RefillAction::Stop, step(r, 10000, low, ctx(true)));
    TEST_ASSERT_EQUAL(RefillState::Queued, r.state());
    TEST_ASSERT_FALSE(r.pumpOn());

    TEST_ASSERT_EQUAL(RefillAction::Start, step(r, 15000, low, ctx(false)));
    TEST_ASSERT_EQUAL(RefillState::Filling, r.state());
}

void test_another_operation_holding_the_manifold_holds_the_refill() {
    Refill r;
    const RefillReading low = reeds(true, false);
    step(r, 1000, low, ctx(false, false));   // a clean cycle owns the machine
    TEST_ASSERT_EQUAL(RefillAction::None, step(r, 1000 + kRefillDebounceMs, low, ctx(false, false)));
    TEST_ASSERT_EQUAL(RefillState::Queued, r.state());
    TEST_ASSERT_EQUAL(RefillAction::Start, step(r, 20000, low, ctx(false, true)));
}

void test_the_high_reed_ends_the_draw() {
    Refill r;
    step(r, 1000, reeds(true, false), ctx(false));
    step(r, 1000 + kRefillDebounceMs, reeds(true, false), ctx(false));
    TEST_ASSERT_EQUAL(RefillState::Filling, r.state());

    // Between the stations both reeds are open and the latch holds.
    TEST_ASSERT_EQUAL(RefillAction::None, carry(r, 5000, 20000, reeds(false, false), ctx(false)));
    TEST_ASSERT_EQUAL(RefillState::Filling, r.state());

    TEST_ASSERT_EQUAL(RefillAction::Stop, step(r, 20000, reeds(false, true), ctx(false)));
    TEST_ASSERT_EQUAL(RefillState::Idle, r.state());
    TEST_ASSERT_FALSE(r.pumpOn());
}

void test_pumping_time_accumulates_only_while_the_relay_is_closed() {
    Refill r;
    const RefillReading low = reeds(true, false);
    step(r, 0, low, ctx(false));
    step(r, kRefillDebounceMs, low, ctx(false));
    TEST_ASSERT_EQUAL(RefillState::Filling, r.state());
    TEST_ASSERT_EQUAL_UINT32(0, r.pumpedMs(kRefillDebounceMs));

    step(r, kRefillDebounceMs + 10000, low, ctx(false));
    TEST_ASSERT_EQUAL_UINT32(10000, r.pumpedMs(kRefillDebounceMs + 10000));

    // Held for a pour: the clock stops.
    step(r, kRefillDebounceMs + 12000, low, ctx(true));
    TEST_ASSERT_EQUAL_UINT32(12000, r.pumpedMs(kRefillDebounceMs + 12000));
    step(r, kRefillDebounceMs + 60000, low, ctx(true));
    TEST_ASSERT_EQUAL_UINT32(12000, r.pumpedMs(kRefillDebounceMs + 60000));

    // Running again: it resumes where it stopped.
    step(r, kRefillDebounceMs + 60000, low, ctx(false));
    step(r, kRefillDebounceMs + 65000, low, ctx(false));
    TEST_ASSERT_EQUAL_UINT32(17000, r.pumpedMs(kRefillDebounceMs + 65000));
}

void test_a_draw_that_never_reaches_the_high_reed_times_out_and_latches() {
    Refill r;
    const RefillReading low = reeds(true, false);
    step(r, 0, low, ctx(false));
    step(r, kRefillDebounceMs, low, ctx(false));
    TEST_ASSERT_EQUAL(RefillState::Filling, r.state());

    const uint32_t started = kRefillDebounceMs;
    TEST_ASSERT_EQUAL(RefillAction::Stop,
                      carry(r, started, started + kRefillCeilingMs + 5000, low, ctx(false), 5000));
    TEST_ASSERT_EQUAL(RefillState::Timeout, r.state());
    TEST_ASSERT_FALSE(r.pumpOn());

    // Latched: the low reed still asking does not restart it.
    TEST_ASSERT_EQUAL(RefillAction::None,
                      carry(r, started + kRefillCeilingMs + 5000, started + kRefillCeilingMs + 60000, low, ctx(false), 5000));
    TEST_ASSERT_EQUAL(RefillState::Timeout, r.state());

    // Clearing it is trying again: the refill is still owed.
    r.clear(started + kRefillCeilingMs + 60000);
    TEST_ASSERT_EQUAL(RefillState::Queued, r.state());
    TEST_ASSERT_TRUE(r.owed());
}

void test_overlapping_reed_windows_stop_refill_without_latching_a_fault() {
    Refill r;
    step(r, 1000, reeds(true, false), ctx(false));
    step(r, 1000 + kRefillDebounceMs, reeds(true, false), ctx(false));
    TEST_ASSERT_EQUAL(RefillState::Filling, r.state());

    TEST_ASSERT_EQUAL(RefillAction::Stop, step(r, 10000, reeds(true, true), ctx(false)));
    TEST_ASSERT_EQUAL(RefillState::Idle, r.state());
    TEST_ASSERT_FALSE(r.pumpOn());

    // Remaining in the overlap cannot start another refill.
    TEST_ASSERT_EQUAL(RefillAction::None, carry(r, 11000, 40000, reeds(true, true), ctx(false)));
    TEST_ASSERT_EQUAL(RefillState::Idle, r.state());
    TEST_ASSERT_EQUAL(RefillAction::None, step(r, 40000, reeds(false, false), ctx(false)));

    // On a later falling crossing, low-only still needs the full debounce.
    TEST_ASSERT_EQUAL(RefillAction::None, step(r, 41000, reeds(true, false), ctx(false)));
    TEST_ASSERT_EQUAL(RefillAction::Start,
                      step(r, 41000 + kRefillDebounceMs, reeds(true, false), ctx(false)));

}

void test_an_overlapping_high_signal_does_not_clear_a_refill_timeout() {
    Refill r;
    step(r, 0, reeds(true, false), ctx(false));
    step(r, kRefillDebounceMs, reeds(true, false), ctx(false));
    TEST_ASSERT_EQUAL(RefillAction::Stop,
                      step(r, kRefillDebounceMs + kRefillCeilingMs, reeds(false, false), ctx(false)));
    TEST_ASSERT_EQUAL(RefillState::Timeout, r.state());
    TEST_ASSERT_EQUAL(RefillAction::None,
                      step(r, kRefillDebounceMs + kRefillCeilingMs + 1000, reeds(true, true), ctx(false)));
    TEST_ASSERT_EQUAL(RefillState::Timeout, r.state());
    TEST_ASSERT_FALSE(r.pumpOn());
}

void test_reeds_that_cannot_be_read_are_not_reeds_that_read_open() {
    Refill r;
    const RefillReading low = reeds(true, false);
    step(r, 1000, low, ctx(false));
    step(r, 1000 + kRefillDebounceMs, low, ctx(false));
    TEST_ASSERT_EQUAL(RefillState::Filling, r.state());

    // The relay drops and the ask waits. The water fell through the low reed and nothing
    // has said it came back, so the refill is still owed; a reading nobody can make neither
    // pumps on it nor forgets it. By the time the expander reads again the water may stand
    // below the low reed's window, where no reed is closed to raise the ask a second time.
    TEST_ASSERT_EQUAL(RefillAction::Stop, step(r, 10000, reeds(false, false, false), ctx(false)));
    TEST_ASSERT_EQUAL(RefillState::Queued, r.state());
    TEST_ASSERT_TRUE(r.owed());
    TEST_ASSERT_FALSE(r.pumpOn());
    TEST_ASSERT_EQUAL(RefillAction::None, step(r, 60000, reeds(false, false, false), ctx(false)));
    TEST_ASSERT_EQUAL(RefillAction::Start, step(r, 61000, reeds(false, false), ctx(false)));
    TEST_ASSERT_EQUAL(RefillAction::Stop, step(r, 70000, reeds(false, true), ctx(false)));
    TEST_ASSERT_EQUAL(RefillState::Idle, r.state());
    TEST_ASSERT_FALSE(r.owed());

    // An unreadable expander never starts one either.
    Refill r2;
    TEST_ASSERT_EQUAL(RefillAction::None, step(r2, 1000, reeds(true, false, false), ctx(false)));
    TEST_ASSERT_EQUAL(RefillAction::None, step(r2, 1000 + kRefillDebounceMs, reeds(true, false, false), ctx(false)));
    TEST_ASSERT_EQUAL(RefillState::Idle, r2.state());
}

void test_a_refill_owed_at_a_power_cut_is_resumed_and_a_timed_out_one_stays_owed() {
    // A boot that is told a refill was owed queues it, whatever the reeds read: below the
    // low reed's window both are open.
    Refill r;
    TEST_ASSERT_FALSE(r.owed());
    r.resume(1000);
    TEST_ASSERT_EQUAL(RefillState::Queued, r.state());
    TEST_ASSERT_EQUAL(RefillAction::Start, step(r, 1100, reeds(false, false), ctx(false)));
    TEST_ASSERT_EQUAL(RefillAction::Stop, step(r, 9000, reeds(false, true), ctx(false)));
    TEST_ASSERT_FALSE(r.owed());

    // Resuming nothing changes nothing once a refill is under way.
    Refill busy;
    busy.resume(1000);
    step(busy, 1100, reeds(false, false), ctx(false));
    busy.resume(2000);
    TEST_ASSERT_EQUAL(RefillState::Filling, busy.state());

    // A draw that timed out stays owed and stays stopped, however long it is left and
    // whatever the low reed does: only being told to try again starts it.
    Refill dry;
    dry.resume(1000);
    step(dry, 1100, reeds(false, false), ctx(false));
    TEST_ASSERT_EQUAL(RefillAction::Stop, step(dry, 1100 + kRefillCeilingMs, reeds(false, false), ctx(false)));
    TEST_ASSERT_EQUAL(RefillState::Timeout, dry.state());
    TEST_ASSERT_TRUE(dry.owed());
    const uint32_t gaveUp = 1100 + kRefillCeilingMs;
    TEST_ASSERT_EQUAL(RefillAction::None, step(dry, gaveUp + 3600000, reeds(false, false), ctx(false)));
    TEST_ASSERT_EQUAL(RefillAction::None, step(dry, gaveUp + 3601000, reeds(true, false), ctx(false)));
    TEST_ASSERT_EQUAL(RefillAction::None, step(dry, gaveUp + 3610000, reeds(true, false), ctx(false)));
    TEST_ASSERT_EQUAL(RefillState::Timeout, dry.state());
    TEST_ASSERT_TRUE(dry.owed());
    dry.clear(gaveUp + 3620000);
    TEST_ASSERT_EQUAL(RefillAction::Start, step(dry, gaveUp + 3620100, reeds(false, false), ctx(false)));
    TEST_ASSERT_EQUAL(RefillAction::Stop, step(dry, gaveUp + 3640000, reeds(false, true), ctx(false)));
    TEST_ASSERT_FALSE(dry.owed());
}

void test_a_level_that_recovers_while_queued_stands_the_ask_down() {
    Refill r;
    const RefillReading low = reeds(true, false);
    step(r, 1000, low, ctx(true));
    step(r, 1000 + kRefillDebounceMs, low, ctx(true));
    TEST_ASSERT_EQUAL(RefillState::Queued, r.state());

    TEST_ASSERT_EQUAL(RefillAction::None, step(r, 5000, reeds(false, true), ctx(true)));
    TEST_ASSERT_EQUAL(RefillState::Idle, r.state());
}

int main(int, char **) {
    UNITY_BEGIN();
    RUN_TEST(test_an_idle_carbonator_asks_for_nothing);
    RUN_TEST(test_the_low_reed_is_believed_only_after_the_debounce);
    RUN_TEST(test_a_surface_that_settles_back_resets_the_debounce);
    RUN_TEST(test_the_ask_that_arrives_mid_pour_waits_for_the_window_to_close);
    RUN_TEST(test_a_dispense_opening_mid_refill_takes_the_relay_down);
    RUN_TEST(test_another_operation_holding_the_manifold_holds_the_refill);
    RUN_TEST(test_the_high_reed_ends_the_draw);
    RUN_TEST(test_pumping_time_accumulates_only_while_the_relay_is_closed);
    RUN_TEST(test_a_draw_that_never_reaches_the_high_reed_times_out_and_latches);
    RUN_TEST(test_overlapping_reed_windows_stop_refill_without_latching_a_fault);
    RUN_TEST(test_an_overlapping_high_signal_does_not_clear_a_refill_timeout);
    RUN_TEST(test_reeds_that_cannot_be_read_are_not_reeds_that_read_open);
    RUN_TEST(test_a_refill_owed_at_a_power_cut_is_resumed_and_a_timed_out_one_stays_owed);
    RUN_TEST(test_a_level_that_recovers_while_queued_stands_the_ask_down);
    return UNITY_END();
}
