#pragma once

#include <stddef.h>
#include <stdint.h>
#include "proto_msg.h"

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
    FunnelFillA,
    FunnelFillB,
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

// A prime-ready session is opened by the enclosure, then either display may
// own one held run at a time. The pump timer above remains the independent
// actuator failsafe; this policy owns only session/endpoint authority.
constexpr uint32_t kPrimeSessionRenewPeriodMs = 500;
constexpr uint32_t kPrimeSessionLeaseGraceMs  = 5000;
// These ledgers cover every token that can still be delayed by the current
// ordered transports: J9 has eight queued application frames plus one in
// flight; J3 has eight queued application frames plus TinyProto's four-frame
// window. They are replay windows, not claims about hostile captured traffic.
constexpr uint8_t  kPrimeSessionTokenHistory  = PRIME_SESSION_REPLAY_HISTORY;
constexpr uint8_t  kPrimeHoldTokenHistory     = PRIME_HOLD_REPLAY_HISTORY;
constexpr uint8_t  kPrimeEnclosureDelayedTokenMax =
    PRIME_J9_APP_QUEUE_DEPTH + PRIME_J9_IN_FLIGHT_DEPTH;
constexpr uint8_t  kPrimeFaucetDelayedTokenMax =
    PRIME_J3_APP_QUEUE_DEPTH + PRIME_PROTO_LINK_WINDOW_DEPTH;
static_assert(kPrimeSessionTokenHistory > kPrimeEnclosureDelayedTokenMax,
              "prime session replay ledger must cover J9");
static_assert(kPrimeHoldTokenHistory > kPrimeEnclosureDelayedTokenMax,
              "enclosure hold replay ledger must cover J9");
static_assert(kPrimeHoldTokenHistory > kPrimeFaucetDelayedTokenMax,
              "faucet hold replay ledger must cover J3");

enum class PrimeSessionPhase : uint8_t {
    Off = 0,
    Ready,
    Running,
};

enum class PrimeSessionOwner : uint8_t {
    None = 0,
    Enclosure,
    Faucet,
};

enum class PrimeSessionOutcome : uint8_t {
    None = 0,
    Stopped,
    Timeout,
    Limit,
    Refused,
    Canceled,
    LeaseExpired,
};

enum class PrimeHoldDecision : uint8_t {
    Ignore = 0,
    StartPump,
    RefreshPump,
    StopPump,
    RecordStopped,
};

struct PrimeSessionSnapshot {
    PrimeSessionPhase phase;
    uint8_t channel;
    PrimeSessionOwner owner;
    PrimeSessionOutcome outcome;
    uint32_t elapsed_ms;
    uint32_t revision;
    uint32_t session_token;
    uint32_t hold_token;
};

class PrimeSession {
public:
    PrimeSession();

    // Activation tokens are nonzero and identify one enclosure visit to the
    // prime screen. Repeating the current activation is idempotent and renews
    // its lease. A canceled token cannot reopen its own session.
    bool activate(uint8_t channel, uint32_t session_token, uint32_t now_ms);
    bool query(uint32_t session_token, uint32_t now_ms);

    // Cancel succeeds for the current token. The sole session-creating
    // endpoint may request an OFF-state tombstone so a delayed ACTIVATE cannot
    // open an invisible session; non-activating endpoints leave that false.
    // The caller supplies live elapsed time before it stops the pump so OFF
    // remains authoritative while the physical stop is being completed.
    bool cancel(uint32_t session_token,
                PrimeSessionOutcome outcome,
                uint32_t elapsed_ms,
                bool tombstone_if_off = false);

    PrimeHoldDecision holdStart(PrimeSessionOwner source,
                                uint8_t channel,
                                uint32_t session_token,
                                uint32_t hold_token,
                                uint32_t now_ms);
    PrimeHoldDecision holdTick(PrimeSessionOwner source,
                               uint8_t channel,
                               uint32_t session_token,
                               uint32_t hold_token,
                               uint32_t now_ms);
    PrimeHoldDecision holdStop(PrimeSessionOwner source,
                               uint8_t channel,
                               uint32_t session_token,
                               uint32_t hold_token,
                               uint32_t now_ms);

    void pumpStarted(PrimeSessionOwner source, uint32_t hold_token);
    void pumpRefused(uint32_t hold_token);
    void pumpStopped(PrimeSessionOutcome outcome, uint32_t elapsed_ms);

    bool leaseExpired(uint32_t now_ms) const;
    bool runningOwnedBy(PrimeSessionOwner source) const;
    bool matches(uint8_t channel, uint32_t session_token) const;
    const PrimeSessionSnapshot &snapshot() const;

private:
    void renewFrom(PrimeSessionOwner source, uint32_t now_ms);
    void bumpRevision();
    bool sessionTokenSeen(uint32_t token) const;
    void rememberSessionToken(uint32_t token);
    bool holdTokenSeen(PrimeSessionOwner source, uint32_t token) const;
    void rememberHoldToken(PrimeSessionOwner source, uint32_t token);
    void resetHoldTokens();

    PrimeSessionSnapshot state_;
    uint32_t lease_renewed_ms_;
    uint32_t session_tokens_[kPrimeSessionTokenHistory];
    uint8_t session_token_count_;
    uint8_t next_session_token_;
    // A busy endpoint cannot evict the other endpoint's causal STOP/START
    // evidence. Enclosure and Faucet each receive their own bounded replay window.
    uint32_t hold_tokens_[2][kPrimeHoldTokenHistory];
    uint8_t hold_token_count_[2];
    uint8_t next_hold_token_[2];
};

}  // namespace machine_policy
