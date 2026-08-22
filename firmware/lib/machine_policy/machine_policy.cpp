#include "machine_policy.h"

namespace machine_policy {
namespace {

constexpr ValveMask valves2(Valve a, Valve b) {
    return valveBit(a) | valveBit(b);
}

constexpr ValveMask valves3(Valve a, Valve b, Valve c) {
    return valveBit(a) | valveBit(b) | valveBit(c);
}

ActuatorPlan makePlan(Operation operation,
                      ValveMask valves,
                      uint8_t flavor_pumps,
                      bool refill_pump,
                      bool dispense_window) {
    const ActuatorPlan plan = {
        operation,
        valves,
        flavor_pumps,
        refill_pump,
        dispense_window,
    };
    return plan;
}

}  // namespace

ActuatorPlan canonicalPlan(Operation operation) {
    switch (operation) {
        case Operation::DispenseA:
            return makePlan(operation, valves2(Valve::E, Valve::G), kPumpA, false, true);
        case Operation::DispenseB:
            return makePlan(operation, valves2(Valve::H, Valve::J), kPumpB, false, true);
        case Operation::HopperFillA:
            return makePlan(operation, valves3(Valve::B, Valve::C, Valve::F), kPumpA, false, false);
        case Operation::HopperFillB:
            return makePlan(operation, valves3(Valve::B, Valve::D, Valve::I), kPumpB, false, false);
        case Operation::CleanWaterFillA:
            return makePlan(
                operation, valves3(Valve::A, Valve::C, Valve::F), kPumpNone, false, false);
        case Operation::CleanWaterFillB:
            return makePlan(
                operation, valves3(Valve::A, Valve::D, Valve::I), kPumpNone, false, false);
        case Operation::CleanFlushA:
            return makePlan(operation, valves2(Valve::E, Valve::G), kPumpA, false, false);
        case Operation::CleanFlushB:
            return makePlan(operation, valves2(Valve::H, Valve::J), kPumpB, false, false);
        case Operation::AirPurgeInA:
            return makePlan(operation, valves3(Valve::B, Valve::C, Valve::F), kPumpA, false, false);
        case Operation::AirPurgeInB:
            return makePlan(operation, valves3(Valve::B, Valve::D, Valve::I), kPumpB, false, false);
        case Operation::AirPurgeOutA:
            return makePlan(operation, valves2(Valve::E, Valve::G), kPumpA, false, false);
        case Operation::AirPurgeOutB:
            return makePlan(operation, valves2(Valve::H, Valve::J), kPumpB, false, false);
        case Operation::AirPurgeThroughA:
            return makePlan(operation, valves3(Valve::B, Valve::C, Valve::G), kPumpA, false, false);
        case Operation::AirPurgeThroughB:
            return makePlan(operation, valves3(Valve::B, Valve::D, Valve::J), kPumpB, false, false);
        case Operation::CarbonatorRefill:
            return makePlan(operation, valveBit(Valve::K), kPumpNone, true, false);
        case Operation::Parked:
        default:
            return makePlan(Operation::Parked, 0, kPumpNone, false, false);
    }
}

uint8_t countOpenValves(ValveMask valves) {
    uint8_t count = 0;
    while (valves != 0) {
        count = static_cast<uint8_t>(count + (valves & 1u));
        valves >>= 1;
    }
    return count;
}

uint8_t validatePlan(const ActuatorPlan &plan, SafetyContext context) {
    uint8_t violations = kSafetyOk;
    if ((plan.valves & static_cast<ValveMask>(~kAllValves)) != 0) {
        violations = static_cast<uint8_t>(violations | kUnknownValve);
    }
    if (countOpenValves(static_cast<ValveMask>(plan.valves & kAllValves)) > kMaxOpenValves) {
        violations = static_cast<uint8_t>(violations | kTooManyValves);
    }
    if (plan.refill_pump && (plan.dispense_window || context.dispense_window_open)) {
        violations = static_cast<uint8_t>(violations | kRefillDuringDispense);
    }
    return violations;
}

bool isPlanSafe(const ActuatorPlan &plan, SafetyContext context) {
    return validatePlan(plan, context) == kSafetyOk;
}

ValveTransition planValveTransition(ValveMask current, ValveMask target) {
    ValveTransition transition = {0, {0, 0}, kSafetyOk};

    const ActuatorPlan target_plan = {
        Operation::Parked,
        target,
        kPumpNone,
        false,
        false,
    };
    transition.target_violations = validatePlan(target_plan, SafetyContext{false});
    if (transition.target_violations != kSafetyOk) {
        // An invalid target fails closed. A caller may always apply stage zero
        // and does not need a separate emergency path to park every valve.
        transition.stage_count = 1;
        transition.stages[0] = 0;
        return transition;
    }

    current = static_cast<ValveMask>(current & kAllValves);
    if (current == target) return transition;

    const ValveMask closing = static_cast<ValveMask>(current & ~target);
    const ValveMask opening = static_cast<ValveMask>(target & ~current);
    if (closing != 0 && opening != 0) {
        transition.stage_count = 2;
        transition.stages[0] = static_cast<ValveMask>(current & target);
        transition.stages[1] = target;
    } else {
        transition.stage_count = 1;
        transition.stages[0] = target;
    }
    return transition;
}

PumpTimer::PumpTimer()
    : mode_(PumpRunMode::Idle),
      started_ms_(0),
      last_tick_ms_(0),
      bounded_duration_ms_(0) {}

void PumpTimer::beginPrime(uint32_t now_ms) {
    mode_ = PumpRunMode::Prime;
    started_ms_ = now_ms;
    last_tick_ms_ = now_ms;
    bounded_duration_ms_ = 0;
}

uint32_t PumpTimer::beginBounded(uint32_t now_ms, uint32_t requested_ms) {
    mode_ = PumpRunMode::Bounded;
    started_ms_ = now_ms;
    last_tick_ms_ = now_ms;
    bounded_duration_ms_ = requested_ms > kPumpRunCeilingMs
        ? kPumpRunCeilingMs
        : requested_ms;
    return bounded_duration_ms_;
}

void PumpTimer::primeTick(uint32_t now_ms) {
    if (mode_ == PumpRunMode::Prime) last_tick_ms_ = now_ms;
}

PumpStopReason PumpTimer::service(uint32_t now_ms) {
    if (mode_ == PumpRunMode::Prime) {
        if (static_cast<uint32_t>(now_ms - last_tick_ms_) > kPrimeTickGraceMs) {
            finish();
            return PumpStopReason::TickTimeout;
        }
        if (static_cast<uint32_t>(now_ms - started_ms_) >= kPumpRunCeilingMs) {
            finish();
            return PumpStopReason::Ceiling;
        }
    } else if (mode_ == PumpRunMode::Bounded) {
        if (static_cast<uint32_t>(now_ms - started_ms_) >= bounded_duration_ms_) {
            finish();
            return PumpStopReason::BoundedComplete;
        }
    }
    return PumpStopReason::None;
}

PumpStopReason PumpTimer::stop() {
    if (!active()) return PumpStopReason::None;
    finish();
    return PumpStopReason::Requested;
}

bool PumpTimer::active() const {
    return mode_ != PumpRunMode::Idle;
}

PumpRunMode PumpTimer::mode() const {
    return mode_;
}

uint32_t PumpTimer::elapsedMs(uint32_t now_ms) const {
    return active() ? static_cast<uint32_t>(now_ms - started_ms_) : 0;
}

uint32_t PumpTimer::boundedDurationMs() const {
    return mode_ == PumpRunMode::Bounded ? bounded_duration_ms_ : 0;
}

void PumpTimer::finish() {
    mode_ = PumpRunMode::Idle;
    bounded_duration_ms_ = 0;
}

}  // namespace machine_policy
