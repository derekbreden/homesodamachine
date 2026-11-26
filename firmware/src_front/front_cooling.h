#pragma once

#include <stdio.h>
#include "cold_policy.h"
#include "proto_msg.h"

// The front panel presents the controller's cooling state and each probe reading.
namespace front_ui {

enum class CoolingState : uint8_t {
  Unavailable, ProbeFault, FreezeProtection, Running, StartupWait, RestartHold, Idle, Paused
};

constexpr bool temperatureAvailable(bool available, int16_t cx10) {
  return available && cx10 != TEMP_UNREAD;
}

inline CoolingState coolingState(bool available, const StatusPayload &status) {
  using machine_policy::ColdState;
  if (!available) return CoolingState::Unavailable;
  // On a gas trip the hardware holds the relay open and the controller resets the loop.
  if (status.flags & STATUS_F_GAS_TRIP) return CoolingState::Paused;
  const auto cold = static_cast<ColdState>(status.coldState);
  switch (cold) {
    case ColdState::Fault:  return CoolingState::ProbeFault;
    case ColdState::Freeze: return CoolingState::FreezeProtection;
    case ColdState::Off:
    case ColdState::Holding:
    case ColdState::On: break;
    default: return CoolingState::Unavailable;
  }
  if (status.tankCx10 == TEMP_UNREAD || status.coilCx10 == TEMP_UNREAD)
    return CoolingState::ProbeFault;
  if (status.flags & STATUS_F_COMPRESSOR) return CoolingState::Running;
  if (cold == ColdState::Holding) {
    const uint16_t seconds = status.startupCoolingS;
    return seconds != 0 && seconds != STARTUP_COOLING_RUNNING
        ? CoolingState::StartupWait : CoolingState::RestartHold;
  }
  return cold == ColdState::Off ? CoolingState::Idle : CoolingState::Paused;
}

enum class Degrees { Whole, Tenths };

inline void formatTemperature(char *out, size_t n, int16_t cx10, bool available,
                              uint8_t unit, Degrees precision) {
  if (!temperatureAvailable(available, cx10)) {
    snprintf(out, n, "--");
    return;
  }
  const bool celsius = unit == TEMP_UNIT_CELSIUS;
  const int numerator = celsius ? cx10 : 32 * 50 + cx10 * 9;
  const int denominator = celsius ? 10 : 50;
  const int magnitude = numerator < 0 ? -numerator : numerator;
  const int scale = precision == Degrees::Whole ? 1 : 10;
  const int rounded = (magnitude * scale + denominator / 2) / denominator;
  const char *sign = numerator < 0 && rounded ? "-" : "";
  const char suffix = celsius ? 'C' : 'F';
  if (precision == Degrees::Whole) {
    snprintf(out, n, "%s%d°%c", sign, rounded, suffix);
  } else {
    snprintf(out, n, "%s%d.%d°%c", sign, rounded / 10, rounded % 10, suffix);
  }
}

inline void formatHoldTime(char *out, size_t n, uint16_t seconds) {
  snprintf(out, n, "%u:%02u", unsigned(seconds / 60), unsigned(seconds % 60));
}

}  // namespace front_ui
