#include "refill_policy.h"

namespace machine_policy {

RefillReading::RefillReading() : lowClosed(false), highClosed(false), valid(false) {}

RefillContext::RefillContext() : dispenseOpen(false), machineIdle(false) {}

Refill::Refill()
    : state_(RefillState::Idle),
      pump_on_(false),
      last_(),
      low_seen_(false),
      low_since_ms_(0),
      pumped_ms_(0),
      filling_since_ms_(0) {}

void Refill::reading(const RefillReading &r, uint32_t now_ms) {
    if (r.valid && r.lowClosed && !r.highClosed) {
        if (!low_seen_) {
            low_seen_     = true;
            low_since_ms_ = now_ms;
        }
    } else {
        low_seen_ = false;
    }
    last_ = r;
}

void Refill::enter(RefillState s, uint32_t now_ms) {
    state_           = s;
    filling_since_ms_ = now_ms;
}

void Refill::clear(uint32_t now_ms) {
    if (state_ != RefillState::Timeout && state_ != RefillState::Fault) return;
    pumped_ms_ = 0;
    enter(RefillState::Idle, now_ms);
}

void Refill::reset(uint32_t now_ms) {
    state_            = RefillState::Idle;
    pump_on_          = false;
    last_             = RefillReading();
    low_seen_         = false;
    low_since_ms_     = 0;
    pumped_ms_        = 0;
    filling_since_ms_ = now_ms;
}

RefillAction Refill::service(uint32_t now_ms, const RefillContext &ctx) {
    const bool was_on = pump_on_;

    // The draw's own clock runs only while the relay is closed.
    if (state_ == RefillState::Filling) {
        pumped_ms_ += now_ms - filling_since_ms_;
        filling_since_ms_ = now_ms;
    }

    // One transition per pass, until the state stands still. A debounced ask
    // with nothing else holding the actuators is the path that takes two.
    for (int guard = 0; guard < 4; guard++) {
        const RefillState before = state_;

        // One magnet cannot close two reeds 28 mm apart.
        if (last_.valid && last_.lowClosed && last_.highClosed) {
            if (state_ != RefillState::Fault) enter(RefillState::Fault, now_ms);
        } else {
            switch (state_) {
                case RefillState::Idle:
                    if (low_seen_ && now_ms - low_since_ms_ >= kRefillDebounceMs) {
                        pumped_ms_ = 0;
                        enter(RefillState::Queued, now_ms);
                    }
                    break;

                case RefillState::Queued:
                    if (!last_.valid || last_.highClosed)        enter(RefillState::Idle, now_ms);
                    else if (!ctx.dispenseOpen && ctx.machineIdle)
                        enter(RefillState::Filling, now_ms);
                    break;

                case RefillState::Filling:
                    if (ctx.dispenseOpen || !ctx.machineIdle || !last_.valid)
                        enter(RefillState::Queued, now_ms);
                    else if (last_.highClosed)                    enter(RefillState::Idle, now_ms);
                    else if (pumped_ms_ >= kRefillCeilingMs)      enter(RefillState::Timeout, now_ms);
                    break;

                case RefillState::Timeout:
                case RefillState::Fault:
                    break;
            }
        }

        if (state_ == before) break;
    }

    pump_on_ = (state_ == RefillState::Filling);

    if (pump_on_ && !was_on) return RefillAction::Start;
    if (!pump_on_ && was_on) return RefillAction::Stop;
    return RefillAction::None;
}

RefillState Refill::state() const { return state_; }
bool        Refill::pumpOn() const { return pump_on_; }

const char *Refill::stateName() const {
    switch (state_) {
        case RefillState::Idle:    return "idle";
        case RefillState::Queued:  return "queued";
        case RefillState::Filling: return "filling";
        case RefillState::Timeout: return "timeout";
        case RefillState::Fault:   return "fault";
    }
    return "?";
}

uint32_t Refill::pumpedMs(uint32_t now_ms) const {
    if (state_ != RefillState::Filling) return pumped_ms_;
    return pumped_ms_ + (now_ms - filling_since_ms_);
}

}  // namespace machine_policy
