#pragma once
#include <array>
#include <cstdint>
namespace pgfun_positioner {
// BIGTREETECH SKR Pico V1.0: X=swivel, Y=pivot. Integrated TMC2209 bus.
constexpr std::array<uint8_t, 2> kStepPin = {11, 6};
constexpr std::array<uint8_t, 2> kDirPin = {10, 5};
constexpr std::array<uint8_t, 2> kEnablePin = {12, 7};
constexpr std::array<uint8_t, 4> kAllEnablePin = {12, 7, 2, 15};
constexpr std::array<uint8_t, 2> kLimitPin = {4, 3};
constexpr std::array<bool, 2> kDirInvert = {false, false};
constexpr uint8_t kStopPin = 25;
constexpr uint8_t kPedalPin = 16;
constexpr uint8_t kSupplyPin = 27; // TH0: ADC1, onboard pull-up and RC filter.
constexpr std::array<uint8_t, 2> kUartTxPin = {0, 8};
constexpr std::array<uint8_t, 2> kUartRxPin = {1, 9};
constexpr std::array<uint8_t, 2> kDriverBus = {1, 1};
constexpr std::array<uint8_t, 2> kDriverAddress = {0, 2};
constexpr uint32_t kStepMask = (1u << 11) | (1u << 6);
}
