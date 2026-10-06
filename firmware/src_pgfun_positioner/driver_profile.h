#pragma once
#include <array>
#include <cstdint>
namespace pgfun_positioner {
constexpr const char *kProfileName = "pgfun-50-64";
constexpr uint32_t kGconf = (1u << 2) | (1u << 6) | (1u << 7);
// SpreadCycle, 64 external microsteps (MRES=2), interpolation/CoolStep off.
constexpr uint32_t kBaseChopconf = (2u << 24) | (2u << 15) | 5;
constexpr std::array<uint8_t, 2> kCurrentScales = {13, 13};
constexpr std::array<uint8_t, 2> kVsense = {0, 0};
constexpr std::array<uint32_t, 2> kChopconfs = {kBaseChopconf, kBaseChopconf};
// R110, CS13, VSENSE0: 0.774 A RMS, about 1.094 A peak. Equal hold/run.
// These values configure the driver; physical current has not been measured.
}
