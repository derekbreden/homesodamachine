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

inline void formatFahrenheit(char *out, size_t n, int16_t cx10, bool available) {
  if (!temperatureAvailable(available, cx10)) {
    snprintf(out, n, "--");
    return;
  }
  const int fiftiethsF = 32 * 50 + cx10 * 9;
  const int rounded = (fiftiethsF + (fiftiethsF < 0 ? -25 : 25)) / 50;
  snprintf(out, n, "%d°F", rounded);
}

inline void formatCelsius(char *out, size_t n, int16_t cx10, bool available) {
  if (!temperatureAvailable(available, cx10)) {
    snprintf(out, n, "--");
    return;
  }
  const int magnitude = cx10 < 0 ? -cx10 : cx10;
  snprintf(out, n, "%s%d.%d°C", cx10 < 0 ? "-" : "", magnitude / 10, magnitude % 10);
}

}  // namespace front_ui
