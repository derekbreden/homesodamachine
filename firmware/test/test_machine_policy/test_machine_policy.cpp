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
    expectPlan(Operation::HopperFillA,
               bit(Valve::B) | bit(Valve::C) | bit(Valve::F), kPumpA, false, false);
    expectPlan(Operation::HopperFillB,
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
    const ValveMask target = canonicalPlan(Operation::HopperFillA).valves;
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
    RUN_TEST(test_bounded_run_clamps_and_completes_at_its_elapsed_duration);
    RUN_TEST(test_zero_duration_bounded_run_completes_on_first_service);
    RUN_TEST(test_prime_timeout_is_rollover_safe);
    RUN_TEST(test_bounded_completion_is_rollover_safe);
    return UNITY_END();
}
