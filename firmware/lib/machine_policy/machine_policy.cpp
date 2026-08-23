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
        case Operation::FunnelFillA:
            return makePlan(operation, valves3(Valve::B, Valve::C, Valve::F), kPumpA, false, false);
        case Operation::FunnelFillB:
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

PrimeSession::PrimeSession()
    : state_{PrimeSessionPhase::Off,
             0,
             PrimeSessionOwner::None,
             PrimeSessionOutcome::None,
             0,
             0,
             0,
             0},
      lease_renewed_ms_(0),
      session_tokens_{},
      session_token_count_(0),
      next_session_token_(0),
      hold_tokens_{},
      hold_token_count_{},
      next_hold_token_{} {}

bool PrimeSession::activate(uint8_t channel,
                            uint32_t session_token,
                            uint32_t now_ms) {
    if (channel > 1 || session_token == 0) return false;

    if (state_.phase != PrimeSessionPhase::Off &&
        state_.channel == channel && state_.session_token == session_token) {
        lease_renewed_ms_ = now_ms;
        return true;
    }

    // Only accepted activations enter the history. A SET rejected while another
    // session is active may therefore be retried later, while a delayed retry
    // of any recent accepted visit can never resurrect it after cancellation.
    if (sessionTokenSeen(session_token)) return false;
    if (state_.phase != PrimeSessionPhase::Off) return false;

    state_.phase = PrimeSessionPhase::Ready;
    state_.channel = channel;
    state_.owner = PrimeSessionOwner::None;
    state_.outcome = PrimeSessionOutcome::None;
    state_.elapsed_ms = 0;
    state_.session_token = session_token;
    state_.hold_token = 0;
    lease_renewed_ms_ = now_ms;
    resetHoldTokens();
    rememberSessionToken(session_token);
    bumpRevision();
    return true;
}

bool PrimeSession::query(uint32_t session_token, uint32_t now_ms) {
    if (state_.phase == PrimeSessionPhase::Off || session_token == 0 ||
        session_token != state_.session_token) return false;
    lease_renewed_ms_ = now_ms;
    return true;
}

bool PrimeSession::cancel(uint32_t session_token,
                          PrimeSessionOutcome outcome,
                          uint32_t elapsed_ms,
                          bool tombstone_if_off) {
    if (session_token == 0) return false;

    if (state_.phase == PrimeSessionPhase::Off) {
        // An absolute CANCEL may overtake or survive an ACTIVATE in the
        // display/controller transport. Tombstone a fresh token while OFF so
        // that any delayed ACTIVATE with that token remains permanently inert.
        if (!tombstone_if_off) return false;
        if (state_.session_token == session_token &&
            sessionTokenSeen(session_token)) return true;
        if (sessionTokenSeen(session_token)) return false;
        rememberSessionToken(session_token);
        state_.owner = PrimeSessionOwner::None;
        state_.outcome = outcome;
        state_.elapsed_ms = elapsed_ms;
        state_.session_token = session_token;
        state_.hold_token = 0;
        bumpRevision();
        return true;
    }

    if (session_token != state_.session_token) return false;

    state_.phase = PrimeSessionPhase::Off;
    state_.owner = PrimeSessionOwner::None;
    state_.outcome = outcome;
    state_.elapsed_ms = elapsed_ms;
    bumpRevision();
    return true;
}

PrimeHoldDecision PrimeSession::holdStart(PrimeSessionOwner source,
                                          uint8_t channel,
                                          uint32_t session_token,
                                          uint32_t hold_token,
                                          uint32_t now_ms) {
    if (source == PrimeSessionOwner::None || hold_token == 0 ||
        !matches(channel, session_token)) return PrimeHoldDecision::Ignore;

    if (state_.phase == PrimeSessionPhase::Ready &&
        !holdTokenSeen(source, hold_token)) {
        rememberHoldToken(source, hold_token);
        renewFrom(source, now_ms);
        return PrimeHoldDecision::StartPump;
    }
    if (state_.phase == PrimeSessionPhase::Running) {
        if (state_.owner == source && state_.hold_token == hold_token) {
            renewFrom(source, now_ms);
            return PrimeHoldDecision::RefreshPump;
        }
        // A matching-session START refused behind another active hold still
        // consumes its press token. Its later STOP must remain stale instead of
        // becoming a new READY terminal after the active hold finishes.
        if (!holdTokenSeen(source, hold_token))
            rememberHoldToken(source, hold_token);
    }
    return PrimeHoldDecision::Ignore;
}

PrimeHoldDecision PrimeSession::holdTick(PrimeSessionOwner source,
                                         uint8_t channel,
                                         uint32_t session_token,
                                         uint32_t hold_token,
                                         uint32_t now_ms) {
    if (state_.phase != PrimeSessionPhase::Running ||
        state_.owner != source || state_.hold_token != hold_token ||
        !matches(channel, session_token)) return PrimeHoldDecision::Ignore;
    renewFrom(source, now_ms);
    return PrimeHoldDecision::RefreshPump;
}

PrimeHoldDecision PrimeSession::holdStop(PrimeSessionOwner source,
                                         uint8_t channel,
                                         uint32_t session_token,
                                         uint32_t hold_token,
                                         uint32_t now_ms) {
    if (source == PrimeSessionOwner::None || hold_token == 0 ||
        !matches(channel, session_token)) return PrimeHoldDecision::Ignore;

    if (state_.phase == PrimeSessionPhase::Running) {
        return state_.owner == source && state_.hold_token == hold_token
            ? PrimeHoldDecision::StopPump
            : PrimeHoldDecision::Ignore;
    }

    if (state_.phase != PrimeSessionPhase::Ready ||
        holdTokenSeen(source, hold_token))
        return PrimeHoldDecision::Ignore;

    // STOP can legitimately outrun or survive a purged START. Record a causal
    // terminal state before any delayed START with this token can reach policy.
    rememberHoldToken(source, hold_token);
    renewFrom(source, now_ms);
    state_.owner = PrimeSessionOwner::None;
    state_.outcome = PrimeSessionOutcome::Stopped;
    state_.elapsed_ms = 0;
    state_.hold_token = hold_token;
    bumpRevision();
    return PrimeHoldDecision::RecordStopped;
}

void PrimeSession::pumpStarted(PrimeSessionOwner source, uint32_t hold_token) {
    if (state_.phase != PrimeSessionPhase::Ready ||
        source == PrimeSessionOwner::None || hold_token == 0) return;
    // holdStart() records the source-scoped token before the machine adapter
    // attempts the actuator transition.
    state_.phase = PrimeSessionPhase::Running;
    state_.owner = source;
    state_.outcome = PrimeSessionOutcome::None;
    state_.elapsed_ms = 0;
    state_.hold_token = hold_token;
    bumpRevision();
}

void PrimeSession::pumpRefused(uint32_t hold_token) {
    if (state_.phase != PrimeSessionPhase::Ready || hold_token == 0) return;
    // holdStart() already recorded this token even when the actuator refuses.
    state_.owner = PrimeSessionOwner::None;
    state_.outcome = PrimeSessionOutcome::Refused;
    state_.elapsed_ms = 0;
    state_.hold_token = hold_token;
    bumpRevision();
}

void PrimeSession::pumpStopped(PrimeSessionOutcome outcome, uint32_t elapsed_ms) {
    if (state_.phase != PrimeSessionPhase::Running) return;
    state_.phase = PrimeSessionPhase::Ready;
    state_.owner = PrimeSessionOwner::None;
    state_.outcome = outcome;
    state_.elapsed_ms = elapsed_ms;
    bumpRevision();
}

bool PrimeSession::leaseExpired(uint32_t now_ms) const {
    return state_.phase != PrimeSessionPhase::Off &&
           static_cast<uint32_t>(now_ms - lease_renewed_ms_) >
               kPrimeSessionLeaseGraceMs;
}

bool PrimeSession::runningOwnedBy(PrimeSessionOwner source) const {
    return state_.phase == PrimeSessionPhase::Running && state_.owner == source;
}

bool PrimeSession::matches(uint8_t channel, uint32_t session_token) const {
    return state_.phase != PrimeSessionPhase::Off &&
           state_.channel == channel && state_.session_token == session_token;
}

const PrimeSessionSnapshot &PrimeSession::snapshot() const {
    return state_;
}

void PrimeSession::renewFrom(PrimeSessionOwner source, uint32_t now_ms) {
    // The enclosure owns the ready screen and its query/hold traffic leases the
    // session. Faucet traffic still has the pump timer's independent heartbeat.
    if (source == PrimeSessionOwner::Front) lease_renewed_ms_ = now_ms;
}

void PrimeSession::bumpRevision() {
    ++state_.revision;
    if (state_.revision == 0) ++state_.revision;
}

bool PrimeSession::sessionTokenSeen(uint32_t token) const {
    for (uint8_t i = 0; i < session_token_count_; ++i) {
        if (session_tokens_[i] == token) return true;
    }
    return false;
}

void PrimeSession::rememberSessionToken(uint32_t token) {
    session_tokens_[next_session_token_] = token;
    next_session_token_ = static_cast<uint8_t>(
        (next_session_token_ + 1) % kPrimeSessionTokenHistory);
    if (session_token_count_ < kPrimeSessionTokenHistory)
        ++session_token_count_;
}

bool PrimeSession::holdTokenSeen(PrimeSessionOwner source, uint32_t token) const {
    const uint8_t endpoint = source == PrimeSessionOwner::Faucet ? 1 : 0;
    for (uint8_t i = 0; i < hold_token_count_[endpoint]; ++i) {
        if (hold_tokens_[endpoint][i] == token) return true;
    }
    return false;
}

void PrimeSession::rememberHoldToken(PrimeSessionOwner source, uint32_t token) {
    const uint8_t endpoint = source == PrimeSessionOwner::Faucet ? 1 : 0;
    hold_tokens_[endpoint][next_hold_token_[endpoint]] = token;
    next_hold_token_[endpoint] = static_cast<uint8_t>(
        (next_hold_token_[endpoint] + 1) % kPrimeHoldTokenHistory);
    if (hold_token_count_[endpoint] < kPrimeHoldTokenHistory)
        ++hold_token_count_[endpoint];
}

void PrimeSession::resetHoldTokens() {
    for (uint8_t endpoint = 0; endpoint < 2; ++endpoint) {
        hold_token_count_[endpoint] = 0;
        next_hold_token_[endpoint] = 0;
    }
}

}  // namespace machine_policy
