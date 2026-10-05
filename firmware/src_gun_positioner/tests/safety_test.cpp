#include <array>
#include "check.h"
#include <cstdio>
#include "../motion_policy.h"
#include "../safety_policy.h"
#include "../driver_profile.h"

using namespace gun_positioner;
const Health good{true, 0, true, true};

MotionPolicy at_state(State state) {
    MotionPolicy m;
    if (state == State::Unreferenced) return m;
    CHECK(m.reference(1, 0, good));
    if (state == State::Referenced) return m;
    CHECK(m.arm(2, 0, good));
    if (state == State::Armed) return m;
    CHECK(m.move(3, 0, 1000000, {16, 0, 0, 0, 0, 0}, good));
    if (state == State::Fault) m.fail(Fault::UserStop);
    return m;
}

int main() {
    for (State state : {State::Unreferenced, State::Referenced, State::Armed, State::Moving, State::Fault}) {
        auto m = at_state(state);
        DriverVerification v;
        CHECK(!v.sample_supply(true));
        const uint32_t checked_epoch = v.epoch();
        CHECK(v.finish(checked_epoch) && v.ready());
        CHECK(v.sample_supply(false) && !v.ready());
        Health bad = good; bad.motor_supply_ok = false; bad.drivers_ok = v.ready();
        CHECK(m.tick(250, bad) == 0);
        CHECK(!m.referenced() && !m.enabled());
        // Restoring VM before the next 50 ms UART poll cannot resurrect an origin.
        CHECK(v.sample_supply(true) && !v.ready());
        m.fail(Fault::Supply);
        CHECK(!v.finish(checked_epoch)); // A VM cycle during a UART scan rejects that scan.
        Health restored = good; restored.drivers_ok = v.ready();
        const uint32_t next = m.last_sequence + 1;
        CHECK(!m.arm(next, 500, restored));
        CHECK(!m.clear(next, 500, restored));
        CHECK(v.finish(v.epoch())); // Test stand-in for a complete successful fresh scan.
        restored.drivers_ok = v.ready();
        CHECK(m.clear(next, 750, restored));
        CHECK(!m.referenced() && !m.enabled());
        CHECK(m.reference(next + 1, 1000, restored));
        CHECK(m.arm(next + 2, 1250, restored));
    }
    // A reset of even the final driver, a config mismatch, warning/short or
    // failed read prevents a full scan from granting verification.
    CHECK(kGconf == 0xc4);
    CHECK(kCurrentScales[2] == (POSITIONER_LOADED_PROFILE ? 22 : 10));
    CHECK(kCurrentScales[4] == (POSITIONER_LOADED_PROFILE ? 14 : 10));
    for (unsigned i = 0; i < 6; ++i) {
        CHECK(kVsense[i] == (POSITIONER_LOADED_PROFILE && i == 2 ? 0 : 1));
        CHECK(((kChopconfs[i] >> 17) & 1) == kVsense[i]);
        CHECK(((kChopconfs[i] >> 24) & 15) == 4); // Sixteen microsteps in both voltage ranges.
    }
    const DriverSnapshot clean{0, 0, kGconf, kChopconfs[0]};
    unsigned reads = 0;
    auto all_good = [&](unsigned i, DriverSnapshot &s) {
        CHECK(i == reads++); s = clean; s.chopconf = kChopconfs[i]; return true;
    };
    CHECK(check_six_drivers(all_good, kGconf, kChopconfs) && reads == 6);
    for (unsigned bad_axis = 0; bad_axis < 6; ++bad_axis) {
        for (unsigned defect = 0; defect < 8; ++defect) {
            reads = 0;
            auto one_bad = [&](unsigned i, DriverSnapshot &s) {
                ++reads; s = clean; s.chopconf = kChopconfs[i];
                if (i != bad_axis) return true;
                switch (defect) {
                case 0: s.gstat = 1; break; // Reset.
                case 1: s.gstat = 2; break; // Driver error.
                case 2: s.gstat = 4; break; // Charge-pump undervoltage.
                case 3: s.drv_status = 1; break; // Thermal warning.
                case 4: s.gconf ^= 1; break;
                case 5: s.chopconf ^= 1; break;
                case 6: return false;
                case 7: s.chopconf ^= 1u << 17; break; // Wrong per-axis current voltage range.
                }
                return true;
            };
            CHECK(!check_six_drivers(one_bad, kGconf, kChopconfs));
            CHECK(reads == bad_axis + 1);
        }
    }
    for (unsigned bit = 0; bit < 6; ++bit) {
        auto s = clean; s.drv_status = 1u << bit;
        CHECK(!driver_snapshot_ok(s, kGconf, kChopconfs[0]));
    }
    auto stealth = clean; stealth.drv_status = 1u << 30;
    CHECK(!driver_snapshot_ok(stealth, kGconf, kChopconfs[0]));
    TickLiveness live;
    CHECK(!live.can_feed_watchdog(0));
    CHECK(live.can_feed_watchdog(1));
    for (unsigned busy_foreground = 0; busy_foreground < 10000; ++busy_foreground)
        CHECK(!live.can_feed_watchdog(1)); // A stopped ISR cannot receive another kick.
    CHECK(live.can_feed_watchdog(2));
    CHECK(!live.can_feed_watchdog(2));
    CHECK(live.can_feed_watchdog(UINT32_MAX));
    CHECK(live.can_feed_watchdog(0)); // Counter wrap still proves new progress.
    std::puts("PASS: VM cycle invalidates verification/reference in all five states; scans reject old epochs and all six driver defects including per-axis VSENSE; stopped timer cannot feed watchdog");
}
