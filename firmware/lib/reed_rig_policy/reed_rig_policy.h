#pragma once

#include <math.h>
#include <stdint.h>

#include "reed-sweep-rig-datums.h"

// The reed sweep rig's controller policy. It is free of Arduino, so the build host tests every
// decision in it: how a move gains and sheds speed, how the sled finds its home switch, what a
// sweep's legs are, when a reed's change counts, and where the sled may go.
//
// Positions are whole steps from the home switch's trip, positive into the tube. The comb's tab
// stands `tab_steps` behind home, and a position named to the person at the console is the
// sled's near face in millimetres from that tab.
namespace reed_rig {

constexpr int32_t kStepsPerMm = reed_sweep_datums::kStepsPerMm;
constexpr uint8_t kReeds = reed_sweep_datums::kStations;

inline int32_t stepsFromMm(float mm) {
    return static_cast<int32_t>(lroundf(mm * static_cast<float>(kStepsPerMm)));
}

inline float mmFromSteps(int32_t steps) {
    return static_cast<float>(steps) / static_cast<float>(kStepsPerMm);
}

inline float stepsPerSecond(float mm_per_s) {
    return mm_per_s * static_cast<float>(kStepsPerMm);
}

// ── Speeds ────────────────────────────────────────────────────────────────
// The motor starts at this speed and stops from it with no ramp.
constexpr float kInstantMmPerS = 5.0f;
// A move with no reed to read climbs to this, gaining and shedding speed at this rate.
constexpr float kTravelMmPerS = 20.0f;
constexpr float kAccelMmPerS2 = 60.0f;
// A sweep holds one speed from end to end, so it stays within what the motor takes at once.
constexpr float kDefaultSweepMmPerS = 2.0f;
constexpr float kSlowestSweepMmPerS = 0.1f;
constexpr float kFastestSweepMmPerS = kInstantMmPerS;

inline bool validSweepSpeed(float mm_per_s) {
    return mm_per_s >= kSlowestSweepMmPerS && mm_per_s <= kFastestSweepMmPerS;
}

// ── Where the sled may go ─────────────────────────────────────────────────
// The tab's distance behind home is set at the bench. It is believed only inside this.
constexpr float kMostTabMm = 5.0f;

inline bool validTabSteps(int32_t tab_steps) {
    return tab_steps > 0 && tab_steps <= stepsFromMm(kMostTabMm);
}

inline int32_t homeStepsFromSledMm(float sled_mm, int32_t tab_steps) {
    return stepsFromMm(sled_mm) - tab_steps;
}

inline float sledMmFromHomeSteps(int32_t position, int32_t tab_steps) {
    return mmFromSteps(position + tab_steps);
}

// The deepest the sled goes with all of it in the tube.
inline int32_t deepestFromHome(int32_t tab_steps) {
    return reed_sweep_datums::kDeepestFromTabSteps - tab_steps;
}

// A commanded position never lies behind home: the tab is there, and the switch's lever has
// little travel left once it has tripped.
inline bool reachable(int32_t position, int32_t tab_steps) {
    return position >= 0 && position <= deepestFromHome(tab_steps);
}

// Before the sled has been homed nothing says where it stands, so a jog only goes into the
// tube, away from the tab, and only this far at a time.
constexpr float kUnhomedJogMm = 20.0f;

// ── A move ────────────────────────────────────────────────────────────────
// A move of a known number of steps. It starts and ends at a speed the motor takes at once,
// and between them climbs to its cruise and comes down again at a steady rate.
class Move {
public:
    Move() : remaining_(0), direction_(0), cruise2_(0.0f), start2_(0.0f), speed2_(0.0f) {}

    // `steps` is signed: positive is into the tube.
    void begin(int32_t steps, float cruise_steps_per_s) {
        direction_ = steps > 0 ? 1 : (steps < 0 ? -1 : 0);
        remaining_ = steps < 0 ? -steps : steps;
        const float instant = stepsPerSecond(kInstantMmPerS);
        const float start = cruise_steps_per_s < instant ? cruise_steps_per_s : instant;
        cruise2_ = cruise_steps_per_s * cruise_steps_per_s;
        start2_ = start * start;
        speed2_ = start2_;
    }

    bool active() const { return remaining_ > 0; }
    int8_t direction() const { return direction_; }
    int32_t remaining() const { return remaining_; }
    float stepsPerS() const { return sqrtf(speed2_); }

    // The pause between steps at the speed the move stands at, in microseconds.
    uint32_t pauseUs() const {
        return static_cast<uint32_t>(1000000.0f / sqrtf(speed2_) + 0.5f);
    }

    // One step has been taken. The pause before the next, or 0 when the move is over.
    uint32_t step() {
        if (remaining_ == 0) return 0;
        --remaining_;
        if (remaining_ == 0) return 0;
        const float rate = 2.0f * stepsPerSecond(kAccelMmPerS2);
        // The steps it takes to come down from this speed to the one the move ends at.
        const float braking = (speed2_ - start2_) / rate;
        if (static_cast<float>(remaining_) <= braking) {
            speed2_ -= rate;
            if (speed2_ < start2_) speed2_ = start2_;
        } else if (speed2_ < cruise2_) {
            speed2_ += rate;
            if (speed2_ > cruise2_) speed2_ = cruise2_;
        }
        return pauseUs();
    }

    // Whether stopping dead now would be more than the motor takes at once.
    bool aboveInstant() const {
        const float instant = stepsPerSecond(kInstantMmPerS);
        return speed2_ > instant * instant * 1.0001f;
    }

    void halt() { remaining_ = 0; }

private:
    int32_t remaining_;
    int8_t direction_;
    float cruise2_;
    float start2_;
    float speed2_;
};

// ── An input that has to hold ─────────────────────────────────────────────
// A level counts as changed once it has held for a while. A contact's bounce does not.
class Debounced {
public:
    explicit Debounced(uint32_t hold_us = 0)
        : hold_us_(hold_us), stable_(false), pending_(false), since_us_(0) {}

    void reset(bool level) {
        stable_ = level;
        pending_ = false;
    }

    // A reading. True when the settled level changed with it.
    bool sample(bool level, uint32_t now_us) {
        if (level == stable_) {
            pending_ = false;
            return false;
        }
        if (!pending_) {
            pending_ = true;
            since_us_ = now_us;
        }
        if (static_cast<uint32_t>(now_us - since_us_) < hold_us_) return false;
        stable_ = level;
        pending_ = false;
        return true;
    }

    bool state() const { return stable_; }
    bool pending() const { return pending_; }

private:
    uint32_t hold_us_;
    bool stable_;
    bool pending_;
    uint32_t since_us_;
};

// ── The reeds ─────────────────────────────────────────────────────────────
// A reed's contacts bounce for well under this as they close.
constexpr uint32_t kReedHoldUs = 1000;
constexpr uint8_t kReedQueue = 64;

struct ReedEvent {
    uint8_t reed;
    bool closed;
    int32_t step;
    uint32_t at_us;
};

// Every reed's settled state, and a queue of its changes. A change is logged where the sled
// stood when the reed first read differently, not where the reading was believed.
class Reeds {
public:
    Reeds() : head_(0), count_(0), overflowed_(false) {
        for (uint8_t i = 0; i < kReeds; ++i) {
            inputs_[i] = Debounced(kReedHoldUs);
            first_step_[i] = 0;
            first_us_[i] = 0;
        }
    }

    // Take `closed_mask` as the settled state, with nothing queued.
    void reset(uint8_t closed_mask) {
        for (uint8_t i = 0; i < kReeds; ++i) inputs_[i].reset((closed_mask >> i) & 1u);
        head_ = 0;
        count_ = 0;
        overflowed_ = false;
    }

    // A reading of every reed, bit n set when reed n is closed, with where the sled stands.
    void sample(uint8_t closed_mask, int32_t step, uint32_t now_us) {
        for (uint8_t i = 0; i < kReeds; ++i) {
            const bool level = (closed_mask >> i) & 1u;
            const bool was_pending = inputs_[i].pending();
            const bool changed = inputs_[i].sample(level, now_us);
            if (!was_pending && (inputs_[i].pending() || changed)) {
                first_step_[i] = step;
                first_us_[i] = now_us;
            }
            if (changed) push(ReedEvent{i, level, first_step_[i], first_us_[i]});
        }
    }

    bool pop(ReedEvent &event) {
        if (count_ == 0) return false;
        event = queue_[head_];
        head_ = static_cast<uint8_t>((head_ + 1) % kReedQueue);
        --count_;
        return true;
    }

    // Bit n set when reed n is closed.
    uint8_t closed() const {
        uint8_t mask = 0;
        for (uint8_t i = 0; i < kReeds; ++i) {
            if (inputs_[i].state()) mask = static_cast<uint8_t>(mask | (1u << i));
        }
        return mask;
    }

    // A change was dropped because the queue was full.
    bool overflowed() const { return overflowed_; }
    void clearOverflow() { overflowed_ = false; }

private:
    void push(const ReedEvent &event) {
        if (count_ == kReedQueue) {
            overflowed_ = true;
            return;
        }
        queue_[(head_ + count_) % kReedQueue] = event;
        ++count_;
    }

    Debounced inputs_[kReeds];
    int32_t first_step_[kReeds];
    uint32_t first_us_[kReeds];
    ReedEvent queue_[kReedQueue];
    uint8_t head_;
    uint8_t count_;
    bool overflowed_;
};

// ── Homing ────────────────────────────────────────────────────────────────
// The home switch stands on the cradle and the rod's striker presses it a little before the
// sled reaches the comb's tab. Homing finds the step at which the switch trips as the sled
// creeps toward the tab, and how many steps back it lets go.
constexpr uint32_t kHomeHoldUs = 3000;
constexpr float kHomeSeekMmPerS = 4.0f;
constexpr float kHomeCreepMmPerS = 0.5f;
// How far the sled backs off a pressed switch before coming at it again.
constexpr float kHomeBackoffMm = 2.0f;
// The most the sled backs away looking for the switch to let go.
constexpr float kHomeEscapeMm = 15.0f;
// The most it seeks before giving up, past the deepest it could have stood.
constexpr float kHomeSeekSlackMm = 10.0f;

enum class HomeFault : uint8_t {
    None = 0,
    Unproven,      // the switch reads free and has not been seen to change since power-up
    StuckPressed,  // the switch never let go
    NotFound,      // the switch never tripped
};

class Homing {
public:
    enum class Phase : uint8_t { Idle = 0, Escaping, Clearing, Seeking, Creeping, Releasing, Done, Failed };

    // What to do before the next step: a direction, positive into the tube, and a speed. A
    // direction of 0 says there is nothing more to do.
    struct Order {
        int8_t direction;
        float steps_per_s;
    };

    Homing() : phase_(Phase::Idle), fault_(HomeFault::None), found_(false), count_(0), release_(0) {}

    // `pressed` is the switch as it reads now. `proven` says it has been seen to change since
    // power-up. A switch that reads free and was never seen to change may not be connected, and
    // seeking it would run the sled into the tab.
    void begin(bool pressed, bool proven) {
        fault_ = HomeFault::None;
        found_ = false;
        release_ = 0;
        count_ = 0;
        if (pressed) {
            phase_ = Phase::Escaping;
        } else if (!proven) {
            fail(HomeFault::Unproven);
        } else {
            phase_ = Phase::Seeking;
        }
    }

    Order next(bool pressed) {
        switch (phase_) {
            case Phase::Escaping:
                if (!pressed) return enter(Phase::Clearing, pressed);
                if (count_ >= stepsFromMm(kHomeEscapeMm)) return fail(HomeFault::StuckPressed);
                return Order{1, stepsPerSecond(kHomeSeekMmPerS)};
            case Phase::Clearing:
                if (count_ >= stepsFromMm(kHomeBackoffMm)) {
                    return enter(found_ ? Phase::Creeping : Phase::Seeking, pressed);
                }
                return Order{1, stepsPerSecond(kHomeSeekMmPerS)};
            case Phase::Seeking:
                if (pressed) {
                    found_ = true;
                    return enter(Phase::Escaping, pressed);
                }
                if (count_ >= reed_sweep_datums::kDeepestFromTabSteps + stepsFromMm(kHomeSeekSlackMm)) {
                    return fail(HomeFault::NotFound);
                }
                return Order{-1, stepsPerSecond(kHomeSeekMmPerS)};
            case Phase::Creeping:
                if (pressed) return enter(Phase::Releasing, pressed);
                if (count_ >= stepsFromMm(kHomeEscapeMm + kHomeBackoffMm)) return fail(HomeFault::NotFound);
                return Order{-1, stepsPerSecond(kHomeCreepMmPerS)};
            case Phase::Releasing:
                if (!pressed) {
                    release_ = count_;
                    phase_ = Phase::Done;
                    return Order{0, 0.0f};
                }
                if (count_ >= stepsFromMm(kHomeEscapeMm)) return fail(HomeFault::StuckPressed);
                return Order{1, stepsPerSecond(kHomeCreepMmPerS)};
            case Phase::Idle:
            case Phase::Done:
            case Phase::Failed:
                break;
        }
        return Order{0, 0.0f};
    }

    // A step in the ordered direction was taken.
    void stepped() { ++count_; }

    Phase phase() const { return phase_; }
    bool done() const { return phase_ == Phase::Done; }
    bool failed() const { return phase_ == Phase::Failed; }
    HomeFault fault() const { return fault_; }

    // Once done: how many steps past the trip the switch let go. The sled stands there.
    int32_t releaseSteps() const { return release_; }

private:
    Order enter(Phase phase, bool pressed) {
        phase_ = phase;
        count_ = 0;
        return next(pressed);
    }

    Order fail(HomeFault fault) {
        fault_ = fault;
        phase_ = Phase::Failed;
        return Order{0, 0.0f};
    }

    Phase phase_;
    HomeFault fault_;
    bool found_;
    int32_t count_;
    int32_t release_;
};

inline const char *homeFaultText(HomeFault fault) {
    switch (fault) {
        case HomeFault::Unproven:
            return "press the home switch's lever once by hand, then send home again";
        case HomeFault::StuckPressed:
            return "the home switch never let go";
        case HomeFault::NotFound:
            return "the home switch never tripped";
        case HomeFault::None:
            break;
    }
    return "";
}

// ── A sweep ───────────────────────────────────────────────────────────────
// The rod's roller has play in the sled's slot, so the sled only follows after the play is
// taken up. Every leg that is read therefore begins from a stop the sled reached the same way.
constexpr float kRunInMm = 1.0f;

struct Leg {
    int32_t target;
    float steps_per_s;
    // Whether the reeds' changes on this leg are the sweep's record.
    bool logged;
    // The leg's number among the logged ones, from 1; 0 on a leg that is not.
    uint16_t traverse;
};

// A sweep's legs in order: out past its near end and back to it, then out to its far end and
// back, as many times as asked.
class SweepPlan {
public:
    SweepPlan() : from_(0), to_(0), steps_per_s_(0.0f), legs_(0), next_(0) {}

    // `from` and `to` are steps from home, `from` the nearer the tab.
    void begin(int32_t from, int32_t to, float sweep_steps_per_s, uint16_t cycles) {
        from_ = from;
        to_ = to;
        steps_per_s_ = sweep_steps_per_s;
        legs_ = static_cast<uint32_t>(cycles) * 2u + 2u;
        next_ = 0;
    }

    bool next(Leg &leg) {
        if (next_ >= legs_) return false;
        const uint32_t index = next_++;
        if (index == 0) {
            const int32_t run_in = from_ + stepsFromMm(kRunInMm);
            leg = Leg{run_in < to_ ? run_in : to_, stepsPerSecond(kTravelMmPerS), false, 0};
        } else if (index == 1) {
            leg = Leg{from_, stepsPerSecond(kInstantMmPerS), false, 0};
        } else {
            const uint16_t traverse = static_cast<uint16_t>(index - 1u);
            leg = Leg{(traverse % 2u) ? to_ : from_, steps_per_s_, true, traverse};
        }
        return true;
    }

    uint16_t traverses() const { return static_cast<uint16_t>(legs_ - 2u); }

private:
    int32_t from_;
    int32_t to_;
    float steps_per_s_;
    uint32_t legs_;
    uint32_t next_;
};

}  // namespace reed_rig
