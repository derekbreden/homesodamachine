#include "echo_policy.h"

namespace echo_policy {

EchoMatcher::EchoMatcher()
    : head_(0), tail_(0), count_(0), swallowed_(0), high_water_(0), desyncs_(0) {}

void EchoMatcher::sent(const uint8_t *bytes, size_t n) {
    for (size_t i = 0; i < n; i++) {
        // Cannot happen while a frame fits kCapacity; do not corrupt if it does.
        if (count_ == kCapacity) { tail_ = (tail_ + 1) % kCapacity; count_--; }
        expect_[head_] = bytes[i];
        head_ = (head_ + 1) % kCapacity;
        count_++;
    }
    if (count_ > high_water_) high_water_ = count_;
}

bool EchoMatcher::consumeEcho(uint8_t byte) {
    if (!count_) return false;
    if (byte != expect_[tail_]) {   // not our echo — a collision ate it
        count_ = 0;
        head_ = tail_ = 0;
        desyncs_++;
        return false;
    }
    tail_ = (tail_ + 1) % kCapacity;
    count_--;
    swallowed_++;
    return true;
}

}  // namespace echo_policy
