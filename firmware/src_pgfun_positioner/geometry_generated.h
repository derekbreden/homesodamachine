#pragma once
#include <array>
#include <cstdint>
namespace pgfun_positioner {
constexpr int32_t kCountsPerRev = 640000;
constexpr std::array<int32_t, 2> kMinCount = {-1777, -1777};
constexpr std::array<int32_t, 2> kMaxCount = {1777, 1777};
constexpr const char *kGeometrySha256 = "e90884a44104933991afa9be4f863ae3caa2037177d9af127f1f4e5e2485c297";
}
