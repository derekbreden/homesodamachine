#pragma once
#include <array>
#include <cstdint>

namespace gun_positioner {
#ifndef POSITIONER_LOADED_PROFILE
#define POSITIONER_LOADED_PROFILE 0
#endif
static_assert(POSITIONER_LOADED_PROFILE == 0 || POSITIONER_LOADED_PROFILE == 1,
              "Choose a documented profile");
constexpr const char *kProfileName = POSITIONER_LOADED_PROFILE ? "loaded-development" : "bench";
constexpr uint32_t kGconf = (1u << 2) | (1u << 6) | (1u << 7);
// SpreadCycle: TOFF=5, TBL=2, HSTART=HEND=0; 16 external microsteps,
// interpolation off. Each axis's VSENSE is part of its verified CHOPCONF.
constexpr uint32_t kBaseChopconf = (4u << 24) | (2u << 15) | 5;
constexpr std::array<uint8_t, 6> kCurrentScales = {
    10, 10, POSITIONER_LOADED_PROFILE ? 22 : 10, 10, POSITIONER_LOADED_PROFILE ? 14 : 10, 10
};
constexpr std::array<uint8_t, 6> kVsense = {
    1, 1, POSITIONER_LOADED_PROFILE ? 0 : 1, 1, 1, 1
};
constexpr std::array<uint32_t, 6> kChopconfs = {
    kBaseChopconf | (uint32_t(kVsense[0]) << 17),
    kBaseChopconf | (uint32_t(kVsense[1]) << 17),
    kBaseChopconf | (uint32_t(kVsense[2]) << 17),
    kBaseChopconf | (uint32_t(kVsense[3]) << 17),
    kBaseChopconf | (uint32_t(kVsense[4]) << 17),
    kBaseChopconf | (uint32_t(kVsense[5]) << 17)
};
// R110: CS10/VSENSE1=.337 A RMS. Loaded Z CS22/VSENSE0=1.271 A RMS
// (1.797 A peak nominal); pitch CS14/VSENSE1=.459 A RMS. These are
// estimates, not measured current. Equal hold/run avoids current transitions.
}
