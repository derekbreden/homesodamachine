#pragma once
#include <array>
#include <cstdint>
namespace gun_positioner {
constexpr std::array<uint8_t, 6> kStepPin = {2, 6, 8, 10, 12, 14};
constexpr std::array<uint8_t, 6> kDirPin = {3, 7, 9, 11, 13, 15};
constexpr std::array<uint8_t, 6> kLimitPin = {17, 18, 19, 20, 21, 22};
// Z's fixed thrust is at the top: positive carriage Z reduces physical screw
// span. These are initial electrical polarities, accepted only by observed sign.
constexpr std::array<bool, 6> kDirInvert = {false, false, true, false, false, false};
constexpr uint8_t kEnablePin = 16;
constexpr uint8_t kStopPin = 26;
constexpr uint8_t kSupplyPin = 27;
constexpr std::array<uint8_t, 2> kUartTxPin = {0, 4};
constexpr std::array<uint8_t, 2> kUartRxPin = {1, 5};
constexpr std::array<uint8_t, 6> kDriverBus = {0, 0, 0, 1, 1, 1};
constexpr std::array<uint8_t, 6> kDriverAddress = {0, 1, 2, 0, 1, 2};
constexpr uint32_t kStepMask = (1u << 2) | (1u << 6) | (1u << 8) |
                              (1u << 10) | (1u << 12) | (1u << 14);
}
