#pragma once

#include <stdint.h>

#include "proto_msg.h"

namespace ratio_session {

// How long a visit stands after the machine display last stated it. It states it on every
// poll, so this spans several polls even at a dark display's pace.
constexpr uint32_t kLeaseMs = 3000;

// The machine display's Ratio page, open for one flavor, as the main board holds it for both
// glasses. Stating a visit opens it and stating it again keeps it open. Closing it from either
// glass keeps its token, and a statement of that token still on its way is answered closed. A
// visit nobody has stated for kLeaseMs reads as closed and opens again on its next statement:
// the page can still be up behind a link that went quiet, and nothing closed it.
class Session {
public:
    // True when this opened what was not open.
    bool open(uint8_t channel, uint32_t token, uint32_t nowMs) {
        if (channel > PUMP_CHANNEL_B || token == 0 || token == closed_) return false;
        const bool was = isOpen(nowMs) && token_ == token && channel_ == channel;
        token_ = token;
        channel_ = channel;
        statedMs_ = nowMs;
        return !was;
    }

    // True when this closed the visit that was open.
    bool close(uint32_t token, uint32_t nowMs) {
        if (token == 0 || token != token_) return false;
        const bool was = isOpen(nowMs);
        closed_ = token;
        return was;
    }

    bool isOpen(uint32_t nowMs) const {
        return token_ != 0 && token_ != closed_ && nowMs - statedMs_ < kLeaseMs;
    }

    // The visit as either glass is told it; the caller adds the ratios.
    void read(uint32_t nowMs, RatioSessionStatePayload &state) const {
        state.open = isOpen(nowMs) ? 1 : 0;
        state.channel = channel_;
        state.token = token_;
    }

private:
    uint32_t token_ = 0;
    uint32_t closed_ = 0;
    uint32_t statedMs_ = 0;
    uint8_t channel_ = PUMP_CHANNEL_A;
};

}  // namespace ratio_session
