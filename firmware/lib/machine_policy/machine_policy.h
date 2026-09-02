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

// ── The funnel fill ───────────────────────────────────────────────────────
// A fill draws what was poured into the funnel — one 440 mL concentrate
// bottle, which is what the funnel is sized for — down the channel's own path
// into its reservoir. The KPHM600 head is rated 380–600 mL/min, so the slowest
// rated head empties a bottle in 70 s; a run draws for 80 s so the line behind
// the funnel is drawn clear as well, and ends the moment the reservoir's full
// reed closes. A head turning on air is the air-purge-in state of this same
// path, so a funnel that empties early costs nothing.
constexpr uint32_t kFillPlannedMs    = 80000;
constexpr uint32_t kFillBottleMl     = 440;
constexpr uint32_t kFillSlowestMlMin = 380;
constexpr uint32_t kFillReedPeriodMs = 250;    // how often the reservoir is read while drawing
// The pump stops before its valves close: a head spinning down against a
// closed outlet is pressure with nowhere to go.
constexpr uint32_t kFillParkDwellMs  = 250;
constexpr uint8_t  kReservoirReedFull = 1u << 3;   // bit 3 of a reservoir's closed-reed mask

enum class FillEnd : uint8_t {
    None = 0,
    Full,     // the reservoir's full reed closed
    Planned,  // the planned draw elapsed
};

// Whether a fill that has drawn for `elapsed_ms` should end, and why. Full wins
// over the clock when both are true on the same service call.
FillEnd fillShouldEnd(uint32_t elapsed_ms, uint32_t planned_ms, uint8_t reservoir_closed_mask);

// The channel's funnel path.
Operation fillOperation(uint8_t channel);

// ── The clean cycle ───────────────────────────────────────────────────────
// Tap water goes through the channel the way concentrate does, kCleanRounds
// times over. A round fills the reservoir with tap water through the idle
// pump — V-A, the channel's select and its return, tap pressure across a
// parked head — until the full reed closes, then draws it out through the
// faucet on the dispense path — the channel's draw and its flavor tube, pump
// on — until the empty reed opens and kCleanFlushTailMs more has drawn the
// flavor tube clear. Each step also ends at its planned time.
constexpr uint8_t  kCleanRounds            = 3;
constexpr uint32_t kCleanWaterFillPlannedMs = 90000;
constexpr uint32_t kCleanFlushPlannedMs     = 150000;
constexpr uint32_t kCleanFlushTailMs        = 8000;
constexpr uint32_t kCleanReedPeriodMs       = kFillReedPeriodMs;
// Between steps every valve is closed for this long, after the pump has stopped.
constexpr uint32_t kCleanSettleMs           = kFillParkDwellMs;
constexpr uint8_t  kReservoirReedEmpty      = 1u << 0;   // bit 0 of a reservoir's closed-reed mask

enum class CleanStep : uint8_t {
    WaterFill = 0,   // tap water in, pump off
    Flush,           // pump on, out through the faucet
};

enum class CleanEnd : uint8_t {
    None = 0,
    Reed,     // the step's own reed said so
    Planned,  // the step's planned time elapsed
};

// The topology state a step of the channel's clean cycle runs.
Operation cleanOperation(uint8_t channel, CleanStep step);

// A water fill ends when the full reed closes, or at its planned time.
CleanEnd cleanWaterFillShouldEnd(uint32_t elapsed_ms, uint32_t planned_ms,
                                 uint8_t reservoir_closed_mask);

// A flush ends kCleanFlushTailMs after the empty reed opens, or at its planned
// time. The opening counts once the reed has been seen closed during this
// flush. `empty_opened_at_ms` is the elapsed time at which it opened, or
// UINT32_MAX while it has not.
CleanEnd cleanFlushShouldEnd(uint32_t elapsed_ms, uint32_t planned_ms,
                             bool empty_seen_closed, uint32_t empty_opened_at_ms);

// How much of the cycle is left, as a time: what remains of the step running
// now plus every step still to come, each at its planned length. Steps 0..2R-1
// alternate water fill and flush; `step_index` is the one running.
uint32_t cleanCycleLeftMs(uint8_t step_index, uint8_t rounds,
                          uint32_t step_elapsed_ms, uint32_t step_planned_ms,
                          uint32_t water_fill_planned_ms, uint32_t flush_planned_ms);

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

    // A tick refreshes only an active prime, matching the current owner.
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
