#pragma once

#include <stdint.h>

namespace weld_rotator_policy {

// Physical contract shared with the printable rotator.  The tube is 5.000 in
// OD with a 0.065 in wall; travel speed is specified at the recessed ID corner
// where the end-cap weld is made.
constexpr float kPi = 3.14159265358979323846f;
constexpr float kTubeIdMm = 123.698f;
constexpr float kBeadCircumferenceMm = kPi * kTubeIdMm;

constexpr uint16_t kMotorFullStepsPerRev = 200;
constexpr uint8_t kDriverMicrosteps = 16;
constexpr uint16_t kMotorPulsesPerRev =
    kMotorFullStepsPerRev * kDriverMicrosteps;
constexpr uint8_t kMotorPulleyTeeth = 20;
constexpr uint8_t kTablePulleyTeeth = 90;
constexpr uint16_t kTablePulsesPerRev =
    kMotorPulsesPerRev * kTablePulleyTeeth / kMotorPulleyTeeth;

constexpr float kMinTravelMmPerS = 5.0f;
constexpr float kDefaultTravelMmPerS = 8.0f;
constexpr float kMaxTravelMmPerS = 15.0f;

constexpr uint16_t kPedalDebounceMs = 20;
constexpr uint16_t kMinimumPulseWidthUs = 3;

inline bool validTravelSpeed(float mm_per_s) {
    return mm_per_s >= kMinTravelMmPerS && mm_per_s <= kMaxTravelMmPerS;
}

inline float tableRpm(float travel_mm_per_s) {
    return travel_mm_per_s * 60.0f / kBeadCircumferenceMm;
}

inline float motorRpm(float travel_mm_per_s) {
    return tableRpm(travel_mm_per_s) *
           static_cast<float>(kTablePulleyTeeth) /
           static_cast<float>(kMotorPulleyTeeth);
}

inline float pulseHz(float travel_mm_per_s) {
    return motorRpm(travel_mm_per_s) * kMotorPulsesPerRev / 60.0f;
}

inline uint32_t halfPeriodUs(float travel_mm_per_s) {
    return static_cast<uint32_t>(500000.0f / pulseHz(travel_mm_per_s) + 0.5f);
}

// How far the table has come, for the operator watching the index mark.  The
// count is a readout and never a limit.
inline float degreesTurned(uint32_t pulses) {
    return static_cast<float>(pulses) * 360.0f /
           static_cast<float>(kTablePulsesPerRev);
}

enum class Event : uint8_t {
    None = 0,
    Armed,
    Started,
    Released,
    Stopped,
};

// Pedal policy is Arduino-free so every deadman transition is testable on the
// build host.  The pedal is the only thing that starts or stops the table:
// held is turning, released is stopped, and nothing counts against a limit.
// It powers up disarmed, so a pedal held down through a reset cannot move the
// table until it has been released once.
class MotionPolicy {
public:
    MotionPolicy() : armed_(false), running_(false), emitted_pulses_(0) {}

    Event updatePedal(bool pressed) {
        if (!armed_) {
            if (!pressed) {
                armed_ = true;
                return Event::Armed;
            }
            return Event::None;
        }

        if (pressed && !running_) {
            emitted_pulses_ = 0;
            running_ = true;
            return Event::Started;
        }

        if (!pressed && running_) {
            running_ = false;
            return Event::Released;
        }

        return Event::None;
    }

    void recordPulse() {
        if (running_) ++emitted_pulses_;
    }

    Event stop() {
        if (!running_) return Event::None;
        running_ = false;
        return Event::Stopped;
    }

    bool armed() const { return armed_; }
    bool running() const { return running_; }
    uint32_t emittedPulses() const { return emitted_pulses_; }

private:
    bool armed_;
    bool running_;
    uint32_t emitted_pulses_;
};

}  // namespace weld_rotator_policy
