#include "sweep_policy.h"

namespace machine_policy {

Sweep::Sweep() : state_(SweepState::Clear), pulses_(0), flowed_(0), quiet_(0) {}

void Sweep::owe() {
    state_  = SweepState::Owed;
    pulses_ = 0;
    flowed_ = 0;
    quiet_  = 0;
}

void Sweep::clear() {
    state_  = SweepState::Clear;
    pulses_ = 0;
    flowed_ = 0;
    quiet_  = 0;
}

bool Sweep::giveUpWhileFlowing() {
    if (state_ != SweepState::Flowing) return false;
    state_ = SweepState::Releasing;
    quiet_ = 0;
    return true;
}

SweepAction Sweep::sample(uint32_t pulses) {
    if (state_ == SweepState::Clear) return SweepAction::None;

    if (state_ == SweepState::Releasing) {
        if (pulses >= kFlowMinPulses) {
            quiet_ = 0;
        } else if (++quiet_ >= kSweepReleaseSamples) {
            state_ = SweepState::Clear;
            quiet_ = 0;
            return SweepAction::Released;
        }
        return SweepAction::None;
    }

    if (pulses >= kFlowMinPulses) {
        quiet_ = 0;
        pulses_ = pulses > kSweepTargetPulses - pulses_ ? kSweepTargetPulses : pulses_ + pulses;
        if (flowed_ < kSweepCeilingSamples) flowed_++;
        if (pulses_ >= kSweepTargetPulses || flowed_ >= kSweepCeilingSamples) {
            state_ = SweepState::Releasing;
            return SweepAction::Done;
        }
        if (state_ == SweepState::Owed) {
            state_ = SweepState::Flowing;
            return SweepAction::Began;
        }
        return SweepAction::None;
    }

    if (state_ == SweepState::Flowing && ++quiet_ >= kSweepQuietSamples) {
        state_ = SweepState::Owed;
        quiet_ = 0;
        return SweepAction::Paused;
    }
    return SweepAction::None;
}

SweepState Sweep::state() const { return state_; }

const char *Sweep::stateName() const {
    switch (state_) {
        case SweepState::Clear:     return "clear";
        case SweepState::Owed:      return "owed";
        case SweepState::Flowing:   return "flowing";
        case SweepState::Releasing: return "releasing";
    }
    return "?";
}

bool     Sweep::owed() const    { return state_ != SweepState::Clear; }
bool     Sweep::flowing() const { return state_ == SweepState::Flowing; }
bool     Sweep::done() const    { return state_ == SweepState::Releasing; }
uint32_t Sweep::pulses() const  { return pulses_; }
uint32_t Sweep::flowedMs() const { return flowed_ * kFlowSampleMs; }

uint8_t Sweep::percent() const {
    if (pulses_ >= kSweepTargetPulses || flowed_ >= kSweepCeilingSamples) return 100;
    const uint32_t counted = static_cast<uint32_t>(static_cast<uint64_t>(pulses_) * 100 / kSweepTargetPulses);
    const uint32_t timed   = flowed_ * 100 / kSweepCeilingSamples;
    return static_cast<uint8_t>(counted > timed ? counted : timed);
}

}  // namespace machine_policy
