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
constexpr float kDefaultOverlapDegrees = 20.0f;
constexpr float kMinOverlapDegrees = 0.0f;
constexpr float kMaxOverlapDegrees = 60.0f;

constexpr uint16_t kPedalDebounceMs = 20;
constexpr uint16_t kMinimumPulseWidthUs = 3;

inline bool validTravelSpeed(float mm_per_s) {
    return mm_per_s >= kMinTravelMmPerS && mm_per_s <= kMaxTravelMmPerS;
}

inline bool validOverlap(float degrees) {
    return degrees >= kMinOverlapDegrees && degrees <= kMaxOverlapDegrees;
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

inline uint32_t lapPulses(float overlap_degrees) {
    return static_cast<uint32_t>(
        static_cast<float>(kTablePulsesPerRev) *
        (360.0f + overlap_degrees) / 360.0f + 0.5f);
}

enum class Mode : uint8_t {
    Lap = 0,
    Jog,
};

enum class Event : uint8_t {
    None = 0,
    Armed,
    Started,
    Released,
    LapComplete,
    Stopped,
};

// Pedal and lap policy is Arduino-free so exact pulse limits and every
// deadman transition are testable on the build host.  It powers up disarmed:
// a pedal held during reset cannot move the table until it has been released.
class MotionPolicy {
public:
    MotionPolicy()
        : mode_(Mode::Lap),
          armed_(false),
          running_(false),
          emitted_pulses_(0),
          target_pulses_(lapPulses(kDefaultOverlapDegrees)) {}

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

    Event pulseEmitted() {
        if (!running_) return Event::None;

        ++emitted_pulses_;
        if (mode_ == Mode::Lap && emitted_pulses_ >= target_pulses_) {
            running_ = false;
            armed_ = false;
            return Event::LapComplete;
        }
        return Event::None;
    }

    Event stop() {
        if (!running_) return Event::None;
        running_ = false;
        return Event::Stopped;
    }

    bool setMode(Mode mode) {
        if (running_) return false;
        mode_ = mode;
        return true;
    }

    bool setLapTarget(uint32_t pulses) {
        if (running_ || pulses == 0) return false;
        target_pulses_ = pulses;
        return true;
    }

    bool armed() const { return armed_; }
    bool running() const { return running_; }
    Mode mode() const { return mode_; }
    uint32_t emittedPulses() const { return emitted_pulses_; }
    uint32_t targetPulses() const { return target_pulses_; }

private:
    Mode mode_;
    bool armed_;
    bool running_;
    uint32_t emitted_pulses_;
    uint32_t target_pulses_;
};

}  // namespace weld_rotator_policy
