#pragma once

#include <array>
#include <cstdint>
#include <cstdlib>
#include "geometry_generated.h"

// Count coordinates describe emitted STEP edges since a manually established
// central datum. They never describe observed gun position.
namespace gun_positioner {
constexpr unsigned kAxes = 6;
constexpr uint32_t kTickUs = 250;
constexpr uint32_t kHeartbeatTimeoutUs = 500000;
constexpr int32_t kMaxJogCounts = 640; // 0.1 mm screw extension per request.
constexpr uint32_t kMinDurationUs = 100000;
constexpr uint32_t kMaxDurationUs = 2000000;
#ifndef POSITIONER_MAX_RATE
#define POSITIONER_MAX_RATE 2000
#endif
constexpr uint32_t kMaxRate = POSITIONER_MAX_RATE; // Counts/second/axis, cubic peak.
constexpr uint32_t kMaxAcceleration = 12000; // Counts/second^2/axis.

struct Health {
    bool stop_closed = false;
    uint8_t open_limit_mask = 0x3f;
    bool motor_supply_ok = false;
    bool drivers_ok = false;
};

enum class State { Unreferenced, Referenced, Armed, Moving, Fault };
enum class Fault { None, Stop, Limit, Supply, Driver, HostTimeout, Timing, UserStop };

inline const char *state_name(State s) {
    switch (s) {
    case State::Unreferenced: return "unreferenced";
    case State::Referenced: return "referenced";
    case State::Armed: return "armed";
    case State::Moving: return "moving";
    case State::Fault: return "fault";
    }
    return "invalid";
}
inline const char *fault_name(Fault f) {
    switch (f) {
    case Fault::None: return "none";
    case Fault::Stop: return "stop_loop";
    case Fault::Limit: return "travel_loop";
    case Fault::Supply: return "motor_supply";
    case Fault::Driver: return "driver";
    case Fault::HostTimeout: return "host_timeout";
    case Fault::Timing: return "pulse_timing";
    case Fault::UserStop: return "user_stop";
    }
    return "invalid";
}

class MotionPolicy {
public:
    State state = State::Unreferenced;
    Fault fault = Fault::None;
    std::array<int32_t, kAxes> count{};
    std::array<int32_t, kAxes> delta{};
    std::array<uint32_t, kAxes> emitted{};
    uint32_t last_sequence = 0;
    uint32_t move_sequence = 0;
    uint32_t completed_sequence = 0;
    uint64_t completed_us = 0;
    uint64_t last_host_us = 0;
    uint64_t start_us = 0;
    uint64_t last_tick_us = 0;
    uint32_t duration_us = 0;
    const char *error = "none";

    bool enabled() const { return state == State::Armed || state == State::Moving; }
    bool referenced() const {
        return state == State::Referenced || enabled();
    }
    bool healthy(const Health &h) const {
        return h.stop_closed && !h.open_limit_mask && h.motor_supply_ok && h.drivers_ok;
    }
    bool sequence(uint32_t seq) {
        if (last_sequence == UINT32_MAX || seq != last_sequence + 1) {
            error = "sequence";
            return false;
        }
        return true;
    }
    void accepted(uint32_t seq, uint64_t now) {
        last_sequence = seq;
        last_host_us = now;
        error = "none";
    }
    void fail(Fault why) {
        if (state != State::Fault) fault = why;
        state = State::Fault;
    }
    bool clear(uint32_t seq, uint64_t now, const Health &h) {
        if (!sequence(seq)) return false;
        if (enabled() || !healthy(h)) { error = "not_safe_to_clear"; return false; }
        state = State::Unreferenced;
        fault = Fault::None;
        accepted(seq, now);
        return true;
    }
    bool reference(uint32_t seq, uint64_t now, const Health &h) {
        if (!sequence(seq)) return false;
        if (state != State::Unreferenced || !healthy(h)) {
            error = "reference_requires_healthy_unreferenced"; return false;
        }
        count.fill(0);
        state = State::Referenced;
        accepted(seq, now);
        return true;
    }
    bool arm(uint32_t seq, uint64_t now, const Health &h) {
        if (!sequence(seq)) return false;
        if (state != State::Referenced || !healthy(h)) {
            error = "arm_requires_healthy_reference"; return false;
        }
        state = State::Armed;
        accepted(seq, now);
        return true;
    }
    bool ping(uint32_t seq, uint64_t now) {
        if (!sequence(seq)) return false;
        accepted(seq, now);
        return true;
    }
    bool disarm(uint32_t seq, uint64_t now) {
        if (!sequence(seq)) return false;
        if (state == State::Fault) { error = "fault_requires_clear"; return false; }
        state = State::Unreferenced;
        accepted(seq, now);
        return true;
    }
    bool move(uint32_t seq, uint64_t now, uint32_t duration,
              const std::array<int32_t, kAxes> &request, const Health &h) {
        if (!sequence(seq)) return false;
        if (state != State::Armed || !healthy(h)) {
            error = "move_requires_healthy_armed"; return false;
        }
        if (duration < kMinDurationUs || duration > kMaxDurationUs) {
            error = "duration"; return false;
        }
        bool nonzero = false;
        for (unsigned i = 0; i < kAxes; ++i) {
            const int64_t d = request[i];
            const uint64_t n = d < 0 ? -d : d;
            nonzero |= n != 0;
            if (n > kMaxJogCounts) { error = "jog_bound"; return false; }
            const int64_t end = int64_t(count[i]) + d;
            if (end < kMinCount[i] || end > kMaxCount[i]) {
                error = "soft_limit"; return false;
            }
            // Cubic s=3u²−2u³: peak rate=1.5N/T; peak accel=6N/T².
            if (3 * n * 1000000 > 2ull * kMaxRate * duration) {
                error = "rate"; return false;
            }
            if (6 * n * 1000000000000ull > uint64_t(kMaxAcceleration) * duration * duration) {
                error = "acceleration"; return false;
            }
        }
        if (!nonzero) { error = "zero_move"; return false; }
        delta = request;
        emitted.fill(0);
        duration_us = duration;
        start_us = now + 10000; // Driver wake and DIR setup, no pulse before this.
        last_tick_us = now;
        move_sequence = seq;
        state = State::Moving;
        accepted(seq, now);
        return true;
    }
    uint8_t tick(uint64_t now, const Health &h) {
        if (state == State::Fault) return 0;
        if (!h.stop_closed) { fail(Fault::Stop); return 0; }
        if (h.open_limit_mask) { fail(Fault::Limit); return 0; }
        if (!h.motor_supply_ok) { fail(Fault::Supply); return 0; }
        if (!enabled()) return 0;
        if (!h.drivers_ok) { fail(Fault::Driver); return 0; }
        if (now - last_host_us >= kHeartbeatTimeoutUs) { fail(Fault::HostTimeout); return 0; }
        if (state != State::Moving) return 0;
        if (now - last_tick_us > 2 * kTickUs) { fail(Fault::Timing); return 0; }
        last_tick_us = now;
        if (now < start_us) return 0;
        const uint64_t elapsed = now - start_us;
        const uint64_t u = elapsed >= duration_us ? 65536 : elapsed * 65536 / duration_us;
        const uint64_t progress_q32 = (u * u * (3 * 65536 - 2 * u)) >> 16;
        std::array<uint32_t, kAxes> desired{};
        uint8_t mask = 0;
        for (unsigned i = 0; i < kAxes; ++i) {
            const uint64_t n = delta[i] < 0 ? -int64_t(delta[i]) : delta[i];
            desired[i] = (n * progress_q32) >> 32;
            // No catch-up burst: a missed scheduler budget is a latched fault.
            if (desired[i] > emitted[i] + 1) { fail(Fault::Timing); return 0; }
            if (desired[i] != emitted[i]) mask |= 1u << i;
        }
        for (unsigned i = 0; i < kAxes; ++i) {
            if (mask & (1u << i)) {
                count[i] += delta[i] > 0 ? 1 : -1;
                emitted[i] = desired[i];
            }
        }
        if (elapsed >= duration_us) {
            state = State::Armed;
            completed_sequence = move_sequence;
            completed_us = now;
        }
        return mask;
    }
};
} // namespace gun_positioner
