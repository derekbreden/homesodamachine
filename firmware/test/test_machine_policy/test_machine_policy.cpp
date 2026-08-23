#include <unity.h>

#include "machine_policy.h"
#include "proto_msg.h"

using namespace machine_policy;

namespace {

constexpr ValveMask bit(Valve valve) {
    return valveBit(valve);
}

void expectPlan(Operation operation,
                ValveMask valves,
                uint8_t pumps,
                bool refill,
                bool dispense) {
    const ActuatorPlan plan = canonicalPlan(operation);
    TEST_ASSERT_EQUAL_UINT16(valves, plan.valves);
    TEST_ASSERT_EQUAL_UINT8(pumps, plan.flavor_pumps);
    TEST_ASSERT_EQUAL(refill, plan.refill_pump);
    TEST_ASSERT_EQUAL(dispense, plan.dispense_window);
    TEST_ASSERT_TRUE(isPlanSafe(plan, SafetyContext{false}));
}

void test_logical_valve_inventory_is_eleven_bits() {
    TEST_ASSERT_EQUAL_UINT8(11, kValveCount);
    TEST_ASSERT_EQUAL_HEX16(0x07ff, kAllValves);
    TEST_ASSERT_EQUAL_HEX16(0x0001, bit(Valve::A));
    TEST_ASSERT_EQUAL_HEX16(0x0400, bit(Valve::K));
}

void test_canonical_flavor_topology_plans_match_documented_states() {
    expectPlan(Operation::Parked, 0, kPumpNone, false, false);
    expectPlan(Operation::DispenseA, bit(Valve::E) | bit(Valve::G), kPumpA, false, true);
    expectPlan(Operation::DispenseB, bit(Valve::H) | bit(Valve::J), kPumpB, false, true);
    expectPlan(Operation::FunnelFillA,
               bit(Valve::B) | bit(Valve::C) | bit(Valve::F), kPumpA, false, false);
    expectPlan(Operation::FunnelFillB,
               bit(Valve::B) | bit(Valve::D) | bit(Valve::I), kPumpB, false, false);
    expectPlan(Operation::CleanWaterFillA,
               bit(Valve::A) | bit(Valve::C) | bit(Valve::F), kPumpNone, false, false);
    expectPlan(Operation::CleanWaterFillB,
               bit(Valve::A) | bit(Valve::D) | bit(Valve::I), kPumpNone, false, false);
    expectPlan(Operation::CleanFlushA,
               bit(Valve::E) | bit(Valve::G), kPumpA, false, false);
    expectPlan(Operation::CleanFlushB,
               bit(Valve::H) | bit(Valve::J), kPumpB, false, false);
    expectPlan(Operation::AirPurgeInA,
               bit(Valve::B) | bit(Valve::C) | bit(Valve::F), kPumpA, false, false);
    expectPlan(Operation::AirPurgeInB,
               bit(Valve::B) | bit(Valve::D) | bit(Valve::I), kPumpB, false, false);
    expectPlan(Operation::AirPurgeOutA,
               bit(Valve::E) | bit(Valve::G), kPumpA, false, false);
    expectPlan(Operation::AirPurgeOutB,
               bit(Valve::H) | bit(Valve::J), kPumpB, false, false);
    expectPlan(Operation::AirPurgeThroughA,
               bit(Valve::B) | bit(Valve::C) | bit(Valve::G), kPumpA, false, false);
    expectPlan(Operation::AirPurgeThroughB,
               bit(Valve::B) | bit(Valve::D) | bit(Valve::J), kPumpB, false, false);
}

void test_carbonator_refill_uses_only_v_k_and_the_refill_pump() {
    expectPlan(Operation::CarbonatorRefill, bit(Valve::K), kPumpNone, true, false);
}

void test_plan_validation_rejects_more_than_three_open_valves() {
    ActuatorPlan plan = canonicalPlan(Operation::Parked);
    plan.valves = bit(Valve::A) | bit(Valve::B) | bit(Valve::C) | bit(Valve::D);
    TEST_ASSERT_BITS_HIGH(kTooManyValves, validatePlan(plan, SafetyContext{false}));
}

void test_plan_validation_rejects_nonexistent_valves() {
    ActuatorPlan plan = canonicalPlan(Operation::Parked);
    plan.valves = static_cast<ValveMask>(kAllValves | 0x0800);
    TEST_ASSERT_BITS_HIGH(kUnknownValve, validatePlan(plan, SafetyContext{false}));
}

void test_refill_is_forbidden_during_an_existing_dispense_window() {
    const ActuatorPlan refill = canonicalPlan(Operation::CarbonatorRefill);
    TEST_ASSERT_BITS_HIGH(kRefillDuringDispense,
                          validatePlan(refill, SafetyContext{true}));
    TEST_ASSERT_TRUE(isPlanSafe(refill, SafetyContext{false}));
}

void test_one_plan_cannot_request_refill_and_open_a_dispense_window() {
    ActuatorPlan impossible = canonicalPlan(Operation::DispenseA);
    impossible.refill_pump = true;
    TEST_ASSERT_BITS_HIGH(kRefillDuringDispense,
                          validatePlan(impossible, SafetyContext{false}));
}

void test_transition_closes_outgoing_valves_before_opening_incoming_valves() {
    const ValveMask current = canonicalPlan(Operation::DispenseA).valves;
    const ValveMask target = canonicalPlan(Operation::FunnelFillA).valves;
    const ValveTransition transition = planValveTransition(current, target);

    TEST_ASSERT_EQUAL_UINT8(kSafetyOk, transition.target_violations);
    TEST_ASSERT_EQUAL_UINT8(2, transition.stage_count);
    TEST_ASSERT_EQUAL_HEX16(0, transition.stages[0]);
    TEST_ASSERT_EQUAL_HEX16(target, transition.stages[1]);
}

void test_transition_retains_only_shared_valves_during_break_stage() {
    const ValveMask current = canonicalPlan(Operation::DispenseA).valves;
    const ValveMask target = canonicalPlan(Operation::AirPurgeThroughA).valves;
    const ValveTransition transition = planValveTransition(current, target);

    TEST_ASSERT_EQUAL_UINT8(2, transition.stage_count);
    TEST_ASSERT_EQUAL_HEX16(bit(Valve::G), transition.stages[0]);
    TEST_ASSERT_EQUAL_HEX16(target, transition.stages[1]);
}

void test_transition_does_not_add_redundant_break_stage() {
    const ValveMask target = canonicalPlan(Operation::DispenseA).valves;

    ValveTransition transition = planValveTransition(0, target);
    TEST_ASSERT_EQUAL_UINT8(1, transition.stage_count);
    TEST_ASSERT_EQUAL_HEX16(target, transition.stages[0]);

    transition = planValveTransition(target, 0);
    TEST_ASSERT_EQUAL_UINT8(1, transition.stage_count);
    TEST_ASSERT_EQUAL_HEX16(0, transition.stages[0]);

    transition = planValveTransition(target, target);
    TEST_ASSERT_EQUAL_UINT8(0, transition.stage_count);
}

void test_transition_with_unsafe_target_fails_closed() {
    const ValveMask unsafe = bit(Valve::A) | bit(Valve::B) | bit(Valve::C) | bit(Valve::D);
    const ValveTransition transition = planValveTransition(bit(Valve::E), unsafe);

    TEST_ASSERT_BITS_HIGH(kTooManyValves, transition.target_violations);
    TEST_ASSERT_EQUAL_UINT8(1, transition.stage_count);
    TEST_ASSERT_EQUAL_HEX16(0, transition.stages[0]);
}

void test_every_valve_mask_transition_is_safe_and_off_before_on() {
    for (ValveMask current = 0; current <= kAllValves; ++current) {
        for (ValveMask target = 0; target <= kAllValves; ++target) {
            const ValveTransition transition = planValveTransition(current, target);
            const bool target_safe = countOpenValves(target) <= kMaxOpenValves;

            if (!target_safe) {
                TEST_ASSERT_BITS_HIGH(kTooManyValves, transition.target_violations);
                TEST_ASSERT_EQUAL_UINT8(1, transition.stage_count);
                TEST_ASSERT_EQUAL_HEX16(0, transition.stages[0]);
                continue;
            }

            TEST_ASSERT_EQUAL_UINT8(kSafetyOk, transition.target_violations);
            if (current == target) {
                TEST_ASSERT_EQUAL_UINT8(0, transition.stage_count);
                continue;
            }

            TEST_ASSERT_GREATER_THAN_UINT8(0, transition.stage_count);
            TEST_ASSERT_LESS_OR_EQUAL_UINT8(2, transition.stage_count);
            TEST_ASSERT_EQUAL_HEX16(target, transition.stages[transition.stage_count - 1]);
            for (uint8_t stage = 0; stage < transition.stage_count; ++stage) {
                TEST_ASSERT_EQUAL_HEX16(
                    0, static_cast<ValveMask>(transition.stages[stage] & ~kAllValves));
                TEST_ASSERT_LESS_OR_EQUAL_UINT8(
                    kMaxOpenValves, countOpenValves(transition.stages[stage]));
            }

            const ValveMask closing = static_cast<ValveMask>(current & ~target);
            const ValveMask opening = static_cast<ValveMask>(target & ~current);
            if (closing != 0 && opening != 0) {
                TEST_ASSERT_EQUAL_UINT8(2, transition.stage_count);
                TEST_ASSERT_EQUAL_HEX16(
                    static_cast<ValveMask>(current & target), transition.stages[0]);
                TEST_ASSERT_EQUAL_HEX16(
                    0, static_cast<ValveMask>(transition.stages[0] & opening));
            }
        }
    }
}

void test_prime_wire_timing_contract_is_500_2000_60000_ms() {
    TEST_ASSERT_EQUAL_UINT32(500, kPrimeTickPeriodMs);
    TEST_ASSERT_EQUAL_UINT32(2000, kPrimeTickGraceMs);
    TEST_ASSERT_EQUAL_UINT32(60000, kPumpRunCeilingMs);
    TEST_ASSERT_EQUAL_UINT32(PRIME_TICK_MS, kPrimeTickPeriodMs);
    TEST_ASSERT_EQUAL_UINT32(PRIME_TICK_GRACE_MS, kPrimeTickGraceMs);
    TEST_ASSERT_EQUAL_UINT32(PRIME_MAX_MS, kPumpRunCeilingMs);
}

void test_prime_tick_is_not_stale_at_exact_grace_boundary() {
    PumpTimer timer;
    timer.beginPrime(1000);
    TEST_ASSERT_EQUAL(PumpStopReason::None, timer.service(3000));
    TEST_ASSERT_TRUE(timer.active());
    TEST_ASSERT_EQUAL(PumpStopReason::TickTimeout, timer.service(3001));
    TEST_ASSERT_FALSE(timer.active());
}

void test_regular_prime_ticks_keep_run_alive_until_hard_ceiling() {
    PumpTimer timer;
    timer.beginPrime(1000);
    for (uint32_t elapsed = kPrimeTickPeriodMs;
         elapsed < kPumpRunCeilingMs;
         elapsed += kPrimeTickPeriodMs) {
        timer.primeTick(1000 + elapsed);
        TEST_ASSERT_EQUAL(PumpStopReason::None, timer.service(1000 + elapsed));
    }
    timer.primeTick(1000 + kPumpRunCeilingMs);
    TEST_ASSERT_EQUAL(PumpStopReason::Ceiling,
                      timer.service(1000 + kPumpRunCeilingMs));
    TEST_ASSERT_FALSE(timer.active());
}

void test_tick_timeout_wins_when_timeout_and_ceiling_are_both_due() {
    PumpTimer timer;
    timer.beginPrime(42);
    TEST_ASSERT_EQUAL(PumpStopReason::TickTimeout,
                      timer.service(42 + kPumpRunCeilingMs));
}

void test_expired_prime_cannot_be_revived_by_a_buffered_late_tick() {
    PumpTimer timer;
    timer.beginPrime(100);

    TEST_ASSERT_EQUAL(PumpStopReason::TickTimeout,
                      timer.service(101 + kPrimeTickGraceMs));
    TEST_ASSERT_FALSE(timer.active());
    timer.primeTick(101 + kPrimeTickGraceMs);
    TEST_ASSERT_FALSE(timer.active());
    TEST_ASSERT_EQUAL(PumpStopReason::None,
                      timer.service(102 + kPrimeTickGraceMs));
}

void test_bounded_run_clamps_and_completes_at_its_elapsed_duration() {
    PumpTimer timer;
    TEST_ASSERT_EQUAL_UINT32(kPumpRunCeilingMs,
                             timer.beginBounded(900, kPumpRunCeilingMs + 1));
    TEST_ASSERT_EQUAL(PumpStopReason::None,
                      timer.service(900 + kPumpRunCeilingMs - 1));
    TEST_ASSERT_TRUE(timer.active());
    TEST_ASSERT_EQUAL(PumpStopReason::BoundedComplete,
                      timer.service(900 + kPumpRunCeilingMs));
    TEST_ASSERT_FALSE(timer.active());
}

void test_zero_duration_bounded_run_completes_on_first_service() {
    PumpTimer timer;
    TEST_ASSERT_EQUAL_UINT32(0, timer.beginBounded(123, 0));
    TEST_ASSERT_EQUAL(PumpStopReason::BoundedComplete, timer.service(123));
}

void test_prime_timeout_is_rollover_safe() {
    PumpTimer timer;
    const uint32_t start = UINT32_MAX - 999;
    timer.beginPrime(start);
    timer.primeTick(start + 500u);

    TEST_ASSERT_EQUAL(PumpStopReason::None,
                      timer.service(start + 500u + kPrimeTickGraceMs));
    TEST_ASSERT_EQUAL(PumpStopReason::TickTimeout,
                      timer.service(start + 500u + kPrimeTickGraceMs + 1u));
}

void test_bounded_completion_is_rollover_safe() {
    PumpTimer timer;
    const uint32_t start = UINT32_MAX - 9;
    timer.beginBounded(start, 20);

    TEST_ASSERT_EQUAL_UINT32(19, timer.elapsedMs(start + 19u));
    TEST_ASSERT_EQUAL(PumpStopReason::None, timer.service(start + 19u));
    TEST_ASSERT_EQUAL(PumpStopReason::BoundedComplete, timer.service(start + 20u));
}

void test_prime_session_activation_is_authoritative_and_idempotent() {
    PrimeSession session;
    TEST_ASSERT_EQUAL(PrimeSessionPhase::Off, session.snapshot().phase);

    TEST_ASSERT_TRUE(session.activate(1, 0x12345678u, 100));
    const PrimeSessionSnapshot &ready = session.snapshot();
    TEST_ASSERT_EQUAL(PrimeSessionPhase::Ready, ready.phase);
    TEST_ASSERT_EQUAL_UINT8(1, ready.channel);
    TEST_ASSERT_EQUAL(PrimeSessionOwner::None, ready.owner);
    TEST_ASSERT_EQUAL(PrimeSessionOutcome::None, ready.outcome);
    TEST_ASSERT_EQUAL_UINT32(0x12345678u, ready.session_token);
    TEST_ASSERT_EQUAL_UINT32(1, ready.revision);

    TEST_ASSERT_TRUE(session.activate(1, 0x12345678u, 200));
    TEST_ASSERT_EQUAL_UINT32(1, session.snapshot().revision);
    TEST_ASSERT_FALSE(session.activate(0, 0x87654321u, 200));
    TEST_ASSERT_FALSE(session.activate(2, 0x87654321u, 200));
    TEST_ASSERT_FALSE(session.activate(0, 0, 200));

    // A valid different token rejected while READY is not poisoned; after the
    // current visit explicitly closes, its retry may become the next session.
    TEST_ASSERT_TRUE(session.cancel(
        0x12345678u, PrimeSessionOutcome::Canceled, 0));
    TEST_ASSERT_TRUE(session.activate(0, 0x87654321u, 300));
}

void test_cancelled_activation_token_cannot_resurrect_session() {
    PrimeSession session;
    TEST_ASSERT_TRUE(session.activate(0, 0x11111111u, 100));
    TEST_ASSERT_TRUE(session.cancel(
        0x11111111u, PrimeSessionOutcome::Stopped, 0));
    TEST_ASSERT_EQUAL(PrimeSessionPhase::Off, session.snapshot().phase);
    TEST_ASSERT_EQUAL_UINT32(0x11111111u, session.snapshot().session_token);
    TEST_ASSERT_FALSE(session.activate(0, 0x11111111u, 200));
    TEST_ASSERT_EQUAL(PrimeSessionPhase::Off, session.snapshot().phase);

    TEST_ASSERT_TRUE(session.activate(0, 0x22222222u, 300));
    TEST_ASSERT_EQUAL(PrimeSessionPhase::Ready, session.snapshot().phase);
    TEST_ASSERT_TRUE(session.cancel(
        0x22222222u, PrimeSessionOutcome::Canceled, 0));

    // History spans later visits, so a delayed retry of the first accepted SET
    // still cannot reopen after a newer session has also closed.
    TEST_ASSERT_FALSE(session.activate(0, 0x11111111u, 400));
    TEST_ASSERT_EQUAL(PrimeSessionPhase::Off, session.snapshot().phase);
}

void test_cancel_tombstones_an_activation_that_has_not_arrived() {
    PrimeSession nonActivator;
    TEST_ASSERT_FALSE(nonActivator.cancel(
        0x20111111u, PrimeSessionOutcome::Canceled, 0));
    TEST_ASSERT_TRUE(nonActivator.activate(0, 0x20111111u, 50));

    PrimeSession session;
    constexpr uint32_t pendingToken = 0x21111111u;

    TEST_ASSERT_TRUE(session.cancel(
        pendingToken, PrimeSessionOutcome::Canceled, 0, true));
    TEST_ASSERT_EQUAL(PrimeSessionPhase::Off, session.snapshot().phase);
    TEST_ASSERT_EQUAL(PrimeSessionOutcome::Canceled, session.snapshot().outcome);
    TEST_ASSERT_EQUAL_UINT32(pendingToken, session.snapshot().session_token);
    const uint32_t tombstoneRevision = session.snapshot().revision;

    // An exact retry is idempotent, and the delayed ACTIVATE is permanently
    // rejected even though CANCEL reached the main board first.
    TEST_ASSERT_TRUE(session.cancel(
        pendingToken, PrimeSessionOutcome::Canceled, 0, true));
    TEST_ASSERT_EQUAL_UINT32(tombstoneRevision, session.snapshot().revision);
    TEST_ASSERT_FALSE(session.activate(0, pendingToken, 200));

    constexpr uint32_t newerToken = 0x22222222u;
    TEST_ASSERT_TRUE(session.activate(1, newerToken, 300));
    TEST_ASSERT_TRUE(session.cancel(
        newerToken, PrimeSessionOutcome::Canceled, 0));
    const uint32_t newerRevision = session.snapshot().revision;

    // A very late cancel for an older remembered visit cannot replace the
    // authoritative token retained by the newer completed visit.
    TEST_ASSERT_FALSE(session.cancel(
        pendingToken, PrimeSessionOutcome::Canceled, 0, true));
    TEST_ASSERT_EQUAL_UINT32(newerToken, session.snapshot().session_token);
    TEST_ASSERT_EQUAL_UINT32(newerRevision, session.snapshot().revision);
}

void test_session_replay_window_covers_every_delayed_j9_activation() {
    PrimeSession session;
    constexpr uint32_t oldToken = 0x31000000u;
    TEST_ASSERT_TRUE(session.activate(0, oldToken, 100));
    TEST_ASSERT_TRUE(session.cancel(oldToken, PrimeSessionOutcome::Canceled, 0));

    // More complete visits than J9 can retain concurrently must not evict a
    // token that could still be delayed in its fixed application queue.
    for (uint32_t i = 0; i < kPrimeEnclosureDelayedTokenMax; ++i) {
        const uint32_t token = 0x32000000u + i;
        TEST_ASSERT_TRUE(session.activate(i & 1u, token, 200 + i));
        TEST_ASSERT_TRUE(session.cancel(token, PrimeSessionOutcome::Canceled, 0));
    }

    TEST_ASSERT_FALSE(session.activate(0, oldToken, 500));
    TEST_ASSERT_EQUAL(PrimeSessionPhase::Off, session.snapshot().phase);
}

void test_only_matching_query_renews_current_session_lease() {
    PrimeSession session;
    session.activate(0, 0xA0u, 100);
    TEST_ASSERT_FALSE(session.query(0, 200));
    TEST_ASSERT_FALSE(session.query(0xB0u, 300));
    TEST_ASSERT_TRUE(session.query(0xA0u, 400));
    TEST_ASSERT_FALSE(session.leaseExpired(400 + kPrimeSessionLeaseGraceMs));
    TEST_ASSERT_TRUE(session.leaseExpired(401 + kPrimeSessionLeaseGraceMs));
}

void test_hold_is_bound_to_session_channel_source_and_press_token() {
    PrimeSession session;
    session.activate(1, 0xA1u, 100);

    TEST_ASSERT_EQUAL(
        PrimeHoldDecision::Ignore,
        session.holdStart(PrimeSessionOwner::Enclosure, 0, 0xA1u, 0xB1u, 110));
    TEST_ASSERT_EQUAL(
        PrimeHoldDecision::Ignore,
        session.holdStart(PrimeSessionOwner::Enclosure, 1, 0xA2u, 0xB1u, 110));
    TEST_ASSERT_EQUAL(
        PrimeHoldDecision::StartPump,
        session.holdStart(PrimeSessionOwner::Enclosure, 1, 0xA1u, 0xB1u, 110));

    session.pumpStarted(PrimeSessionOwner::Enclosure, 0xB1u);
    TEST_ASSERT_EQUAL(PrimeSessionPhase::Running, session.snapshot().phase);
    TEST_ASSERT_EQUAL(PrimeSessionOwner::Enclosure, session.snapshot().owner);
    TEST_ASSERT_EQUAL_UINT32(0xB1u, session.snapshot().hold_token);

    // A retried START for the same physical press is only another heartbeat.
    TEST_ASSERT_EQUAL(
        PrimeHoldDecision::RefreshPump,
        session.holdStart(PrimeSessionOwner::Enclosure, 1, 0xA1u, 0xB1u, 120));
    TEST_ASSERT_EQUAL(
        PrimeHoldDecision::Ignore,
        session.holdStart(PrimeSessionOwner::Faucet, 1, 0xA1u, 0xC1u, 120));
    TEST_ASSERT_EQUAL(PrimeSessionPhase::Running, session.snapshot().phase);
    TEST_ASSERT_EQUAL(PrimeSessionOwner::Enclosure, session.snapshot().owner);

    TEST_ASSERT_EQUAL(
        PrimeHoldDecision::Ignore,
        session.holdStop(PrimeSessionOwner::Enclosure, 1, 0xA1u, 0xB2u, 130));
    TEST_ASSERT_EQUAL(
        PrimeHoldDecision::Ignore,
        session.holdStop(PrimeSessionOwner::Faucet, 1, 0xA1u, 0xB1u, 130));
    TEST_ASSERT_EQUAL(
        PrimeHoldDecision::StopPump,
        session.holdStop(PrimeSessionOwner::Enclosure, 1, 0xA1u, 0xB1u, 130));
    session.pumpStopped(PrimeSessionOutcome::Stopped, 20);
    TEST_ASSERT_EQUAL(
        PrimeHoldDecision::Ignore,
        session.holdStop(PrimeSessionOwner::Faucet, 1, 0xA1u, 0xC1u, 140));
    TEST_ASSERT_EQUAL_UINT32(0xB1u, session.snapshot().hold_token);
}

void test_terminal_hold_returns_to_ready_and_rejects_stale_stop() {
    PrimeSession session;
    session.activate(0, 0xA2u, 100);
    TEST_ASSERT_EQUAL(
        PrimeHoldDecision::StartPump,
        session.holdStart(PrimeSessionOwner::Faucet, 0, 0xA2u, 0xB2u, 110));
    session.pumpStarted(PrimeSessionOwner::Faucet, 0xB2u);
    session.pumpStopped(PrimeSessionOutcome::Timeout, 2345);

    const PrimeSessionSnapshot &stopped = session.snapshot();
    TEST_ASSERT_EQUAL(PrimeSessionPhase::Ready, stopped.phase);
    TEST_ASSERT_EQUAL(PrimeSessionOwner::None, stopped.owner);
    TEST_ASSERT_EQUAL(PrimeSessionOutcome::Timeout, stopped.outcome);
    TEST_ASSERT_EQUAL_UINT32(2345, stopped.elapsed_ms);
    TEST_ASSERT_EQUAL_UINT32(0xB2u, stopped.hold_token);

    TEST_ASSERT_EQUAL(
        PrimeHoldDecision::Ignore,
        session.holdStart(PrimeSessionOwner::Faucet, 0, 0xA2u, 0xB2u, 120));
    TEST_ASSERT_EQUAL(
        PrimeHoldDecision::StartPump,
        session.holdStart(PrimeSessionOwner::Enclosure, 0, 0xA2u, 0xB3u, 120));
    session.pumpStarted(PrimeSessionOwner::Enclosure, 0xB3u);
    TEST_ASSERT_EQUAL(
        PrimeHoldDecision::Ignore,
        session.holdStop(PrimeSessionOwner::Faucet, 0, 0xA2u, 0xB2u, 130));
    TEST_ASSERT_EQUAL(PrimeSessionPhase::Running, session.snapshot().phase);
}

void test_refused_hold_token_cannot_replay_start_or_refusal() {
    PrimeSession session;
    session.activate(0, 0xA5u, 100);
    TEST_ASSERT_EQUAL(
        PrimeHoldDecision::StartPump,
        session.holdStart(PrimeSessionOwner::Enclosure, 0, 0xA5u, 0xB5u, 110));
    session.pumpRefused(0xB5u);
    TEST_ASSERT_EQUAL(PrimeSessionOutcome::Refused, session.snapshot().outcome);

    TEST_ASSERT_EQUAL(
        PrimeHoldDecision::Ignore,
        session.holdStart(PrimeSessionOwner::Enclosure, 0, 0xA5u, 0xB5u, 120));
    TEST_ASSERT_EQUAL(
        PrimeHoldDecision::StartPump,
        session.holdStart(PrimeSessionOwner::Enclosure, 0, 0xA5u, 0xB6u, 120));
}

void test_stop_before_start_records_terminal_causal_evidence() {
    PrimeSession session;
    session.activate(1, 0xA6u, 100);

    TEST_ASSERT_EQUAL(
        PrimeHoldDecision::RecordStopped,
        session.holdStop(PrimeSessionOwner::Enclosure, 1, 0xA6u, 0xB7u, 110));
    const PrimeSessionSnapshot &stopped = session.snapshot();
    TEST_ASSERT_EQUAL(PrimeSessionPhase::Ready, stopped.phase);
    TEST_ASSERT_EQUAL(PrimeSessionOwner::None, stopped.owner);
    TEST_ASSERT_EQUAL(PrimeSessionOutcome::Stopped, stopped.outcome);
    TEST_ASSERT_EQUAL_UINT32(0, stopped.elapsed_ms);
    TEST_ASSERT_EQUAL_UINT32(0xB7u, stopped.hold_token);
    TEST_ASSERT_EQUAL_UINT32(2, stopped.revision);

    // A STOP retry receives the same absolute snapshot without generating a
    // second transition or displacing newer state.
    TEST_ASSERT_EQUAL(
        PrimeHoldDecision::Ignore,
        session.holdStop(PrimeSessionOwner::Enclosure, 1, 0xA6u, 0xB7u, 120));
    TEST_ASSERT_EQUAL_UINT32(2, session.snapshot().revision);
}

void test_delayed_start_after_stop_before_start_cannot_run() {
    PrimeSession session;
    session.activate(0, 0xA7u, 100);
    TEST_ASSERT_EQUAL(
        PrimeHoldDecision::RecordStopped,
        session.holdStop(PrimeSessionOwner::Faucet, 0, 0xA7u, 0xB8u, 110));

    TEST_ASSERT_EQUAL(
        PrimeHoldDecision::Ignore,
        session.holdStart(PrimeSessionOwner::Faucet, 0, 0xA7u, 0xB8u, 120));
    TEST_ASSERT_EQUAL(PrimeSessionOutcome::Stopped, session.snapshot().outcome);
    TEST_ASSERT_EQUAL_UINT32(0xB8u, session.snapshot().hold_token);

    TEST_ASSERT_EQUAL(
        PrimeHoldDecision::StartPump,
        session.holdStart(PrimeSessionOwner::Faucet, 0, 0xA7u, 0xB9u, 130));
}

void test_other_endpoint_cannot_evict_delayed_hold_stop_evidence() {
    PrimeSession session;
    constexpr uint32_t sessionToken = 0xA7000001u;
    constexpr uint32_t enclosureHold = 0xB8000001u;
    session.activate(0, sessionToken, 100);
    TEST_ASSERT_EQUAL(
        PrimeHoldDecision::RecordStopped,
        session.holdStop(
            PrimeSessionOwner::Enclosure, 0, sessionToken, enclosureHold, 110));

    // Fill the faucet's complete replay window. With one shared ledger this
    // churn evicted the enclosure STOP and let its delayed START run; per-endpoint
    // ledgers preserve the causal evidence independently.
    for (uint32_t i = 0; i < kPrimeHoldTokenHistory; ++i) {
        TEST_ASSERT_EQUAL(
            PrimeHoldDecision::RecordStopped,
            session.holdStop(PrimeSessionOwner::Faucet, 0, sessionToken,
                             0xC8000000u + i, 120 + i));
    }

    TEST_ASSERT_EQUAL(
        PrimeHoldDecision::Ignore,
        session.holdStart(
            PrimeSessionOwner::Enclosure, 0, sessionToken, enclosureHold, 200));
    TEST_ASSERT_EQUAL(PrimeSessionPhase::Ready, session.snapshot().phase);
}

void test_hold_token_identity_includes_its_display_source() {
    PrimeSession session;
    constexpr uint32_t sessionToken = 0xA7000002u;
    constexpr uint32_t coincidentToken = 0xB8000002u;
    session.activate(1, sessionToken, 100);

    TEST_ASSERT_EQUAL(
        PrimeHoldDecision::StartPump,
        session.holdStart(PrimeSessionOwner::Enclosure, 1, sessionToken,
                          coincidentToken, 110));
    session.pumpStarted(PrimeSessionOwner::Enclosure, coincidentToken);
    session.pumpStopped(PrimeSessionOutcome::Stopped, 20);

    // Each display seeds tokens independently, so an equal 32-bit value from
    // the other endpoint is a distinct physical press.
    TEST_ASSERT_EQUAL(
        PrimeHoldDecision::StartPump,
        session.holdStart(PrimeSessionOwner::Faucet, 1, sessionToken,
                          coincidentToken, 140));
}

void test_stale_older_stop_does_not_overwrite_newer_ready_state() {
    PrimeSession session;
    session.activate(0, 0xA8u, 100);
    session.holdStop(PrimeSessionOwner::Enclosure, 0, 0xA8u, 0xBAu, 110);

    TEST_ASSERT_EQUAL(
        PrimeHoldDecision::StartPump,
        session.holdStart(PrimeSessionOwner::Enclosure, 0, 0xA8u, 0xBBu, 120));
    session.pumpRefused(0xBBu);
    const uint32_t newerRevision = session.snapshot().revision;
    TEST_ASSERT_EQUAL(PrimeSessionOutcome::Refused, session.snapshot().outcome);
    TEST_ASSERT_EQUAL_UINT32(0xBBu, session.snapshot().hold_token);

    TEST_ASSERT_EQUAL(
        PrimeHoldDecision::Ignore,
        session.holdStop(PrimeSessionOwner::Enclosure, 0, 0xA8u, 0xBAu, 130));
    TEST_ASSERT_EQUAL_UINT32(newerRevision, session.snapshot().revision);
    TEST_ASSERT_EQUAL(PrimeSessionOutcome::Refused, session.snapshot().outcome);
    TEST_ASSERT_EQUAL_UINT32(0xBBu, session.snapshot().hold_token);
}

void test_front_hold_replay_window_covers_delayed_start_after_stop() {
    PrimeSession session;
    session.activate(0, 0xA9u, 100);
    constexpr uint32_t oldToken = 0xBCu;
    TEST_ASSERT_EQUAL(
        PrimeHoldDecision::RecordStopped,
        session.holdStop(PrimeSessionOwner::Enclosure, 0, 0xA9u, oldToken, 110));

    // Fill every newer token position that the bounded J9 transport can still
    // delay. The oldest causal STOP must remain in the same-source ledger.
    for (uint32_t i = 0; i < kPrimeEnclosureDelayedTokenMax; ++i) {
        TEST_ASSERT_EQUAL(
            PrimeHoldDecision::RecordStopped,
            session.holdStop(
                PrimeSessionOwner::Enclosure, 0, 0xA9u, 0xC0u + i, 120 + i));
    }
    const uint32_t terminalRevision = session.snapshot().revision;

    TEST_ASSERT_EQUAL(
        PrimeHoldDecision::Ignore,
        session.holdStart(PrimeSessionOwner::Enclosure, 0, 0xA9u, oldToken, 300));
    TEST_ASSERT_EQUAL(
        PrimeHoldDecision::Ignore,
        session.holdStop(PrimeSessionOwner::Enclosure, 0, 0xA9u, oldToken, 310));
    TEST_ASSERT_EQUAL_UINT32(terminalRevision, session.snapshot().revision);
    TEST_ASSERT_EQUAL(PrimeSessionOutcome::Stopped, session.snapshot().outcome);
}

void test_faucet_hold_replay_window_covers_delayed_start_after_stop() {
    PrimeSession session;
    session.activate(1, 0xAAu, 100);
    constexpr uint32_t oldToken = 0xD0u;
    TEST_ASSERT_EQUAL(
        PrimeHoldDecision::RecordStopped,
        session.holdStop(PrimeSessionOwner::Faucet, 1, 0xAAu, oldToken, 110));

    // The J3 application queue and TinyProto window are both included in this
    // bound; changing either capacity without growing the ledger fails builds.
    for (uint32_t i = 0; i < kPrimeFaucetDelayedTokenMax; ++i) {
        TEST_ASSERT_EQUAL(
            PrimeHoldDecision::RecordStopped,
            session.holdStop(
                PrimeSessionOwner::Faucet, 1, 0xAAu, 0xE0u + i, 120 + i));
    }
    const uint32_t terminalRevision = session.snapshot().revision;

    TEST_ASSERT_EQUAL(
        PrimeHoldDecision::Ignore,
        session.holdStart(PrimeSessionOwner::Faucet, 1, 0xAAu, oldToken, 300));
    TEST_ASSERT_EQUAL(
        PrimeHoldDecision::Ignore,
        session.holdStop(PrimeSessionOwner::Faucet, 1, 0xAAu, oldToken, 310));
    TEST_ASSERT_EQUAL_UINT32(terminalRevision, session.snapshot().revision);
}

void test_newer_same_session_revision_supersedes_a_lost_stop_reply() {
    constexpr uint32_t sessionToken = 0x10203040u;
    constexpr uint32_t holdOne = 0x50607080u;
    PrimeSessionStatePayload state{
        PRIME_SESSION_RUNNING, 0, PRIME_OWNER_ENCLOSURE, PRIME_OUTCOME_NONE,
        50, 11, sessionToken, holdOne};

    // A newer heartbeat for the exact run is not terminal evidence.
    TEST_ASSERT_FALSE(primeStateSupersedesPendingStop(
        state, sessionToken, holdOne, PRIME_OWNER_ENCLOSURE, 10));

    // READY/H1 or any later H2 state in this session proves H1 cannot run.
    state.phase = PRIME_SESSION_READY;
    state.owner = PRIME_OWNER_NONE;
    state.outcome = PRIME_OUTCOME_STOPPED;
    TEST_ASSERT_TRUE(primeStateSupersedesPendingStop(
        state, sessionToken, holdOne, PRIME_OWNER_ENCLOSURE, 10));
    state.phase = PRIME_SESSION_RUNNING;
    state.owner = PRIME_OWNER_FAUCET;
    state.outcome = PRIME_OUTCOME_NONE;
    state.holdToken = 0x50607081u;
    state.revision = 12;
    TEST_ASSERT_TRUE(primeStateSupersedesPendingStop(
        state, sessionToken, holdOne, PRIME_OWNER_ENCLOSURE, 10));

    state.sessionToken = sessionToken + 1;
    TEST_ASSERT_FALSE(primeStateSupersedesPendingStop(
        state, sessionToken, holdOne, PRIME_OWNER_ENCLOSURE, 10));
    state.sessionToken = sessionToken;
    state.revision = 10;
    TEST_ASSERT_FALSE(primeStateSupersedesPendingStop(
        state, sessionToken, holdOne, PRIME_OWNER_ENCLOSURE, 10));

    // The signed revision comparison remains valid across uint32_t rollover.
    state.phase = PRIME_SESSION_READY;
    state.owner = PRIME_OWNER_NONE;
    state.revision = 1;
    TEST_ASSERT_TRUE(primeStateSupersedesPendingStop(
        state, sessionToken, holdOne, PRIME_OWNER_ENCLOSURE, UINT32_MAX));
}

void test_cancel_while_running_stays_off_after_physical_stop_completes() {
    PrimeSession session;
    session.activate(1, 0xA3u, 100);
    session.holdStart(PrimeSessionOwner::Faucet, 1, 0xA3u, 0xB4u, 110);
    session.pumpStarted(PrimeSessionOwner::Faucet, 0xB4u);

    TEST_ASSERT_TRUE(session.cancel(
        0xA3u, PrimeSessionOutcome::Canceled, 321));
    TEST_ASSERT_EQUAL(PrimeSessionPhase::Off, session.snapshot().phase);
    TEST_ASSERT_EQUAL(PrimeSessionOutcome::Canceled, session.snapshot().outcome);
    TEST_ASSERT_EQUAL_UINT32(321, session.snapshot().elapsed_ms);

    // The adapter now parks the physical pump. Its completion must not reopen
    // the explicitly canceled session.
    session.pumpStopped(PrimeSessionOutcome::Stopped, 322);
    TEST_ASSERT_EQUAL(PrimeSessionPhase::Off, session.snapshot().phase);
    TEST_ASSERT_EQUAL_UINT32(321, session.snapshot().elapsed_ms);
}

void test_prime_session_lease_is_exact_and_rollover_safe() {
    PrimeSession session;
    const uint32_t start = UINT32_MAX - 999;
    session.activate(0, 0xA4u, start);
    TEST_ASSERT_FALSE(session.leaseExpired(start + kPrimeSessionLeaseGraceMs));
    TEST_ASSERT_TRUE(session.leaseExpired(start + kPrimeSessionLeaseGraceMs + 1u));
}

void test_prime_session_wire_contract_has_dedicated_ids_and_exact_layouts() {
    TEST_ASSERT_EQUAL_HEX8(0x2A, MSG_PRIME_SESSION_SET);
    TEST_ASSERT_EQUAL_HEX8(0x2B, MSG_PRIME_SESSION_QUERY);
    TEST_ASSERT_EQUAL_HEX8(0x2C, MSG_RESP_PRIME_SESSION);
    TEST_ASSERT_EQUAL_HEX8(0x2D, MSG_PRIME_SESSION_HOLD_START);
    TEST_ASSERT_EQUAL_HEX8(0x2E, MSG_PRIME_SESSION_HOLD_TICK);
    TEST_ASSERT_EQUAL_HEX8(0x2F, MSG_PRIME_SESSION_HOLD_STOP);
    TEST_ASSERT_EQUAL_UINT32(6, sizeof(PrimeSessionRequestPayload));
    TEST_ASSERT_EQUAL_UINT32(4, sizeof(PrimeSessionQueryPayload));
    TEST_ASSERT_EQUAL_UINT32(9, sizeof(PrimeHoldPayload));
    TEST_ASSERT_EQUAL_UINT32(20, sizeof(PrimeSessionStatePayload));

    TEST_ASSERT_EQUAL_UINT8(
        PRIME_SESSION_OFF, static_cast<uint8_t>(PrimeSessionPhase::Off));
    TEST_ASSERT_EQUAL_UINT8(
        PRIME_SESSION_READY, static_cast<uint8_t>(PrimeSessionPhase::Ready));
    TEST_ASSERT_EQUAL_UINT8(
        PRIME_SESSION_RUNNING, static_cast<uint8_t>(PrimeSessionPhase::Running));
    TEST_ASSERT_EQUAL_UINT8(
        PRIME_OWNER_ENCLOSURE, static_cast<uint8_t>(PrimeSessionOwner::Enclosure));
    TEST_ASSERT_EQUAL_UINT8(
        PRIME_OWNER_FAUCET, static_cast<uint8_t>(PrimeSessionOwner::Faucet));
    TEST_ASSERT_EQUAL_UINT8(
        PRIME_OUTCOME_CANCELED,
        static_cast<uint8_t>(PrimeSessionOutcome::Canceled));
    TEST_ASSERT_EQUAL_UINT8(
        PRIME_OUTCOME_LEASE_EXPIRED,
        static_cast<uint8_t>(PrimeSessionOutcome::LeaseExpired));
}

}  // namespace

void setUp() {}
void tearDown() {}

int main(int, char **) {
    UNITY_BEGIN();
    RUN_TEST(test_logical_valve_inventory_is_eleven_bits);
    RUN_TEST(test_canonical_flavor_topology_plans_match_documented_states);
    RUN_TEST(test_carbonator_refill_uses_only_v_k_and_the_refill_pump);
    RUN_TEST(test_plan_validation_rejects_more_than_three_open_valves);
    RUN_TEST(test_plan_validation_rejects_nonexistent_valves);
    RUN_TEST(test_refill_is_forbidden_during_an_existing_dispense_window);
    RUN_TEST(test_one_plan_cannot_request_refill_and_open_a_dispense_window);
    RUN_TEST(test_transition_closes_outgoing_valves_before_opening_incoming_valves);
    RUN_TEST(test_transition_retains_only_shared_valves_during_break_stage);
    RUN_TEST(test_transition_does_not_add_redundant_break_stage);
    RUN_TEST(test_transition_with_unsafe_target_fails_closed);
    RUN_TEST(test_every_valve_mask_transition_is_safe_and_off_before_on);
    RUN_TEST(test_prime_wire_timing_contract_is_500_2000_60000_ms);
    RUN_TEST(test_prime_tick_is_not_stale_at_exact_grace_boundary);
    RUN_TEST(test_regular_prime_ticks_keep_run_alive_until_hard_ceiling);
    RUN_TEST(test_tick_timeout_wins_when_timeout_and_ceiling_are_both_due);
    RUN_TEST(test_expired_prime_cannot_be_revived_by_a_buffered_late_tick);
    RUN_TEST(test_bounded_run_clamps_and_completes_at_its_elapsed_duration);
    RUN_TEST(test_zero_duration_bounded_run_completes_on_first_service);
    RUN_TEST(test_prime_timeout_is_rollover_safe);
    RUN_TEST(test_bounded_completion_is_rollover_safe);
    RUN_TEST(test_prime_session_activation_is_authoritative_and_idempotent);
    RUN_TEST(test_cancelled_activation_token_cannot_resurrect_session);
    RUN_TEST(test_cancel_tombstones_an_activation_that_has_not_arrived);
    RUN_TEST(test_session_replay_window_covers_every_delayed_j9_activation);
    RUN_TEST(test_only_matching_query_renews_current_session_lease);
    RUN_TEST(test_hold_is_bound_to_session_channel_source_and_press_token);
    RUN_TEST(test_terminal_hold_returns_to_ready_and_rejects_stale_stop);
    RUN_TEST(test_refused_hold_token_cannot_replay_start_or_refusal);
    RUN_TEST(test_stop_before_start_records_terminal_causal_evidence);
    RUN_TEST(test_delayed_start_after_stop_before_start_cannot_run);
    RUN_TEST(test_other_endpoint_cannot_evict_delayed_hold_stop_evidence);
    RUN_TEST(test_hold_token_identity_includes_its_display_source);
    RUN_TEST(test_stale_older_stop_does_not_overwrite_newer_ready_state);
    RUN_TEST(test_front_hold_replay_window_covers_delayed_start_after_stop);
    RUN_TEST(test_faucet_hold_replay_window_covers_delayed_start_after_stop);
    RUN_TEST(test_newer_same_session_revision_supersedes_a_lost_stop_reply);
    RUN_TEST(test_cancel_while_running_stays_off_after_physical_stop_completes);
    RUN_TEST(test_prime_session_lease_is_exact_and_rollover_safe);
    RUN_TEST(test_prime_session_wire_contract_has_dedicated_ids_and_exact_layouts);
    return UNITY_END();
}
