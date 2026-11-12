#include "move_policy.h"

namespace machine_policy {

Move::Move()
    : moving_(false), flowing_(false), low_seen_(false), below_(false), pulses_(0), quiet_(0), open_(0) {}

void Move::begin(bool belowLow) {
    moving_   = true;
    flowing_  = false;
    low_seen_ = belowLow;
    below_    = belowLow;
    pulses_   = 0;
    quiet_    = 0;
    open_     = 0;
}

void Move::end() { *this = Move(); }

void Move::sample(uint32_t pulses, const RefillReading &reeds) {
    if (!moving_) return;

    if (pulses >= kFlowMinPulses) {
        flowing_ = true;
        quiet_   = 0;
        pulses_ += pulses;
    } else if (flowing_ && ++quiet_ >= kSweepQuietSamples) {
        flowing_ = false;
        quiet_   = 0;
    }

    // Reeds that cannot be read say nothing of where the water is.
    if (!reeds.valid) return;
    if (reeds.highClosed) {
        low_seen_ = false;
        below_    = false;
        open_     = 0;
    } else if (reeds.lowClosed) {
        // In the low reed's window the water is at the mark, not below it.
        low_seen_ = true;
        below_    = false;
        open_     = 0;
    } else if (low_seen_ && !below_ && ++open_ >= kSweepQuietSamples) {
        below_ = true;
    }
}

bool     Move::moving() const { return moving_; }
bool     Move::flowing() const { return flowing_; }
bool     Move::belowLow() const { return below_; }
uint32_t Move::pulses() const { return pulses_; }

}  // namespace machine_policy
