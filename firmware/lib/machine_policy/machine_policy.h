#pragma once

#include <stddef.h>
#include <stdint.h>

namespace machine_policy {

// Logical valve identity follows hardware/topology/fluid-topology.md.  The
// physical MCP23017 bit order belongs in the hardware driver, not in policy.
enum class Valve : uint8_t {
    A = 0,
    B,
    C,
    D,
    E,
    F,
    G,
    H,
    I,
    J,
    K,
};

using ValveMask = uint16_t;

constexpr uint8_t   kValveCount       = 11;
constexpr uint8_t   kMaxOpenValves    = 3;
constexpr ValveMask kAllValves        = (ValveMask{1} << kValveCount) - 1;
constexpr ValveMask valveBit(Valve v) {
    return ValveMask{1} << static_cast<uint8_t>(v);
}

enum PumpMask : uint8_t {
    kPumpNone = 0,
    kPumpA    = 1u << 0,
    kPumpB    = 1u << 1,
};

// Each name is retained even where the topology deliberately aliases another
// operation.  Policy can therefore preserve user intent while sharing the same
// safe actuator plan.
enum class Operation : uint8_t {
    Parked = 0,
    DispenseA,
    DispenseB,
    HopperFillA,
    HopperFillB,
    CleanWaterFillA,
    CleanWaterFillB,
    CleanFlushA,
    CleanFlushB,
    AirPurgeInA,
    AirPurgeInB,
    AirPurgeOutA,
    AirPurgeOutB,
    AirPurgeThroughA,
    AirPurgeThroughB,
    CarbonatorRefill,
};

struct ActuatorPlan {
    Operation operation;
    ValveMask valves;
    uint8_t flavor_pumps;
    bool refill_pump;
    bool dispense_window;
};

// Returns the documented actuator plan for an operation. CarbonatorRefill is
// the separate V-K + SeaFlo path shown in fluid-topology-carbonator.mmd.
ActuatorPlan canonicalPlan(Operation operation);

struct SafetyContext {
    // A refill request may arrive while another subsystem owns the dispense
    // window, so this state is explicit rather than inferred only from `plan`.
    bool dispense_window_open;
};

enum SafetyViolation : uint8_t {
    kSafetyOk                    = 0,
    kUnknownValve               = 1u << 0,
    kTooManyValves              = 1u << 1,
    kRefillDuringDispense       = 1u << 2,
};

uint8_t countOpenValves(ValveMask valves);
uint8_t validatePlan(const ActuatorPlan &plan, SafetyContext context);
bool isPlanSafe(const ActuatorPlan &plan, SafetyContext context);

// Valve writes are whole logical states, not individual set/clear operations.
// A transition that both closes and opens valves has two ordered stages:
// retain only shared valves, then apply the target. This guarantees that every
// outgoing valve is closed before any incoming valve is opened.
struct ValveTransition {
    uint8_t stage_count;
    ValveMask stages[2];
    uint8_t target_violations;
};

ValveTransition planValveTransition(ValveMask current, ValveMask target);

// Prime timing is a wire/user-experience contract shared with proto_msg.h.
// Keeping it pure allows exact boundary and rollover tests without a clock,
// GPIO, display, sound, or Arduino runtime.
constexpr uint32_t kPrimeTickPeriodMs = 500;
constexpr uint32_t kPrimeTickGraceMs  = 2000;
constexpr uint32_t kPumpRunCeilingMs  = 60000;

enum class PumpRunMode : uint8_t {
    Idle = 0,
    Prime,
    Bounded,
};

enum class PumpStopReason : uint8_t {
    None = 0,
    Requested,
    TickTimeout,
    Ceiling,
    BoundedComplete,
};

class PumpTimer {
public:
    PumpTimer();

    void beginPrime(uint32_t now_ms);

    // Starts a timed run and returns the accepted duration. Durations above the
    // same 60-second pump ceiling used by prime are clamped.
    uint32_t beginBounded(uint32_t now_ms, uint32_t requested_ms);

    // A tick refreshes only an active prime, matching the current controller.
    void primeTick(uint32_t now_ms);

    // Evaluates and consumes a terminal event. Tick timeout intentionally wins
    // if timeout and the prime ceiling become true on the same service call.
    PumpStopReason service(uint32_t now_ms);
    PumpStopReason stop();

    bool active() const;
    PumpRunMode mode() const;
    uint32_t elapsedMs(uint32_t now_ms) const;
    uint32_t boundedDurationMs() const;

private:
    void finish();

    PumpRunMode mode_;
    uint32_t started_ms_;
    uint32_t last_tick_ms_;
    uint32_t bounded_duration_ms_;
};

}  // namespace machine_policy
