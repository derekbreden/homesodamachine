#include "pour_policy.h"

namespace machine_policy {

void pourCycleTiming(uint32_t pulses, uint8_t ratio, uint32_t &on_ms, uint32_t &off_ms) {
    if (pulses < kFlowMinPulses) pulses = kFlowMinPulses;
    if (pulses > kFlowFullPulses) pulses = kFlowFullPulses;

    // What 1:20 produces at this flow.
    const uint32_t on_base  = kPourShapeOnBase + kPourShapeOnSlope * pulses;
    const uint32_t off_base = kPourShapeOffBase - kPourShapeOffSlope * pulses;
    const uint32_t total    = on_base + off_base;

    // 2.5 at 1:6, 1.0 at 1:20: the duty scales with how strong the pour is.
    const float scale = 2.5f - 1.5f * (float)((int)ratio - 6) / 14.0f;
    const float duty  = scale * (float)on_base / (float)total;

    if (duty >= 1.0f) {
        on_ms  = total;
        off_ms = 0;
    } else {
        off_ms = (uint32_t)((float)off_base / scale + 0.5f);
        on_ms  = (uint32_t)((float)off_ms * duty / (1.0f - duty) + 0.5f);
    }
    if (on_ms < kPourOnMinMs)  on_ms  = kPourOnMinMs;
    if (off_ms > kPourOffMaxMs) off_ms = kPourOffMaxMs;
}

Pour::Pour() { reset(); }

void Pour::reset() {
    phase_          = PourPhase::Idle;
    open_           = false;
    pump_on_        = false;
    last_pulses_    = 0;
    phase_start_ms_ = 0;
    pour_start_ms_  = 0;
    on_ms_          = 0;
    off_ms_         = 0;
    cycle_sum_      = 0;
    cycle_readings_ = 0;
    cycle_saw_zero_ = false;
}

void Pour::sample(uint32_t pulses) {
    last_pulses_ = pulses;
    if (phase_ == PourPhase::On || phase_ == PourPhase::Off) {
        cycle_sum_ += pulses;
        cycle_readings_++;
        if (pulses == 0) cycle_saw_zero_ = true;
    }
}

void Pour::beginCycle(uint32_t now_ms, uint32_t pulses, uint8_t ratio) {
    pourCycleTiming(pulses, ratio, on_ms_, off_ms_);
    cycle_sum_      = 0;
    cycle_readings_ = 0;
    cycle_saw_zero_ = false;
    phase_          = PourPhase::On;
    phase_start_ms_ = now_ms;
    pump_on_        = true;
}

PourAction Pour::service(uint32_t now_ms, uint8_t ratio) {
    if (open_ && static_cast<uint32_t>(now_ms - pour_start_ms_) >= kPourCeilingMs) {
        reset();
        return PourAction::Ceiling;
    }
    switch (phase_) {
        case PourPhase::Idle:
            if (last_pulses_ >= kFlowMinPulses) {
                const bool starting = !open_;
                if (starting) pour_start_ms_ = now_ms;
                open_ = true;
                beginCycle(now_ms, last_pulses_, ratio);
                return starting ? PourAction::Start : PourAction::PumpOn;
            }
            if (open_) {
                open_ = false;
                return PourAction::Stop;
            }
            return PourAction::None;

        case PourPhase::On:
            if (static_cast<uint32_t>(now_ms - phase_start_ms_) < on_ms_) return PourAction::None;
            phase_          = PourPhase::Off;
            phase_start_ms_ = now_ms;
            pump_on_        = false;
            return PourAction::PumpOff;

        case PourPhase::Off: {
            if (static_cast<uint32_t>(now_ms - phase_start_ms_) < off_ms_) return PourAction::None;
            const uint32_t avg = cycle_readings_ ? cycle_sum_ / cycle_readings_ : last_pulses_;
            if (cycle_saw_zero_) {
                phase_          = PourPhase::Cooldown;
                phase_start_ms_ = now_ms;
                return PourAction::None;
            }
            beginCycle(now_ms, avg, ratio);
            return PourAction::PumpOn;
        }

        case PourPhase::Cooldown:
            if (static_cast<uint32_t>(now_ms - phase_start_ms_) < kPourCooldownMs) return PourAction::None;
            phase_          = PourPhase::Idle;
            cycle_sum_      = 0;
            cycle_readings_ = 0;
            cycle_saw_zero_ = false;
            if (last_pulses_ >= kFlowMinPulses) return PourAction::None;   // Idle starts it again
            open_ = false;
            return PourAction::Stop;
    }
    return PourAction::None;
}

PourPhase Pour::phase() const   { return phase_; }
bool      Pour::flowing() const { return last_pulses_ >= kFlowMinPulses; }
bool      Pour::open() const    { return open_; }
bool      Pour::pumpOn() const  { return pump_on_; }
uint32_t  Pour::onMs() const    { return on_ms_; }
uint32_t  Pour::offMs() const   { return off_ms_; }
uint32_t  Pour::elapsedMs(uint32_t now_ms) const {
    return open_ ? static_cast<uint32_t>(now_ms - pour_start_ms_) : 0;
}

}  // namespace machine_policy
