#pragma once
#include <array>
#include <cstdint>
namespace pgfun_positioner {
constexpr int32_t kCountsPerRev = 640000;
constexpr std::array<int32_t, 2> kMinCount = {-1777, -1777};
constexpr std::array<int32_t, 2> kMaxCount = {1777, 1777};
constexpr const char *kGeometrySha256 = "09f3665148688bdbd9795258021a0ef286fc9b484ecf4db4f7ca0f8d2c31727b";
}
