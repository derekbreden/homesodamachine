#pragma once
#include <array>
#include <cstdint>
namespace pgfun_positioner {
constexpr int32_t kCountsPerRev = 640000;
constexpr std::array<int32_t, 2> kMinCount = {-1777, -1777};
constexpr std::array<int32_t, 2> kMaxCount = {1777, 1777};
constexpr const char *kGeometrySha256 = "a2df443043284d9804a77a7942adb7e5720643fd6ed9bf4a08c14d620236a5c1";
}
