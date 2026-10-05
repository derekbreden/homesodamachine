#pragma once

#include <array>
#include <cstdint>

namespace gun_positioner {
// Written by the pulse timer and read/committed with interrupts disabled.
// A complete UART check is valid only in the same observed VM epoch.
class DriverVerification {
    bool seen_supply_ = false;
    bool supply_ok_ = false;
    bool verified_ = false;
    uint32_t epoch_ = 0;
public:
    bool sample_supply(bool ok) volatile {
        const bool transition = seen_supply_ && ok != supply_ok_;
        const bool first = !seen_supply_;
        seen_supply_ = true;
        supply_ok_ = ok;
        if (!ok || transition || first) {
            verified_ = false;
            if (transition || first) ++epoch_;
        }
        // The first good boot sample establishes an unreferenced supply datum.
        // Every later rising edge, and every bad sample, invalidates reference.
        return !ok || transition;
    }
    uint32_t epoch() const volatile { return epoch_; }
    bool ready() const volatile { return verified_; }
    void invalidate() volatile { verified_ = false; }
    bool finish(uint32_t started_epoch) volatile {
        verified_ = seen_supply_ && supply_ok_ && started_epoch == epoch_;
        return verified_;
    }
};

struct DriverSnapshot {
    uint32_t gstat = 0;
    uint32_t drv_status = 0;
    uint32_t gconf = 0;
    uint32_t chopconf = 0;
};
inline bool driver_snapshot_ok(const DriverSnapshot &s, uint32_t gconf, uint32_t chopconf) {
    return !(s.gstat & 7) && !(s.drv_status & (0x3f | (1u << 30))) &&
           s.gconf == gconf && s.chopconf == chopconf;
}
template<class Read>
bool check_six_drivers(Read read, uint32_t gconf, const std::array<uint32_t, 6> &chopconfs) {
    for (unsigned i = 0; i < 6; ++i) {
        DriverSnapshot s;
        if (!read(i, s) || !driver_snapshot_ok(s, gconf, chopconfs[i])) return false;
    }
    return true;
}

// A busy foreground loop cannot keep a dead pulse/safety timer alive.
class TickLiveness {
    uint32_t last_ = 0;
public:
    bool can_feed_watchdog(uint32_t progress) {
        if (progress == last_) return false;
        last_ = progress;
        return true;
    }
};
} // namespace gun_positioner
