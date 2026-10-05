#include "check.h"
#include <cstdio>
#include <cstring>
#include "../motion_policy.h"
using namespace gun_positioner;
const Health good{true, 0, true, true};

MotionPolicy armed() {
    MotionPolicy m;
    CHECK(!m.arm(1, 0, good));
    CHECK(m.reference(1, 0, good));
    CHECK(m.arm(2, 0, good));
    return m;
}
int main() {
    auto m = armed();
    CHECK(!m.move(2, 0, 1000000, {16, 0, 0, 0, 0, 0}, good));
    CHECK(m.last_sequence == 2); // Duplicate request never emits twice.
    CHECK(!m.move(3, 0, 0, {16, 0, 0, 0, 0, 0}, good));
    CHECK(!m.move(3, 0, 1000000, {0, 0, 0, 0, 0, 0}, good));
    CHECK(!m.move(3, 0, 1000000, {641, 0, 0, 0, 0, 0}, good));
    CHECK(!m.move(3, 0, 100000, {640, 0, 0, 0, 0, 0}, good));
    CHECK(!m.move(3, 0, 150000, {64, 0, 0, 0, 0, 0}, good));
    CHECK(!strcmp(m.error, "acceleration")); // Rate is legal in both named profiles.
    CHECK(m.move(3, 0, 1000000, {640, -321, 16, -7, 63, -640}, good));
    CHECK(!m.move(4, 0, 1000000, {1, 0, 0, 0, 0, 0}, good));
    uint32_t seq = 3;
    std::array<unsigned, kAxes> edges{};
    for (uint64_t t = 250; t <= 1010000; t += 250) {
        if (t % 100000 == 0) CHECK(m.ping(++seq, t));
        const uint8_t bits = m.tick(t, good);
        for (unsigned i = 0; i < kAxes; ++i) edges[i] += (bits >> i) & 1;
        CHECK(m.state != State::Fault);
    }
    CHECK(m.state == State::Armed);
    CHECK((m.count == std::array<int32_t, kAxes>{640, -321, 16, -7, 63, -640}));
    CHECK((edges == std::array<unsigned, kAxes>{640, 321, 16, 7, 63, 640}));
    CHECK(m.completed_sequence == 3 && m.completed_us == 1010000);
    CHECK(!m.move(seq + 1, 1010001, 1000000, {INT32_MIN, 0, 0, 0, 0, 0}, good));

    for (unsigned axis = 0; axis < kAxes; ++axis) {
        m = armed();
        std::array<int32_t, kAxes> d{}; d[axis] = 1;
        m.count[axis] = kMaxCount[axis];
        CHECK(!m.move(3, 0, 250000, d, good));
        d[axis] = -1; m.count[axis] = kMinCount[axis];
        CHECK(!m.move(3, 0, 250000, d, good));
        Health h = good; h.open_limit_mask = 1u << axis;
        CHECK(m.tick(250, h) == 0 && m.fault == Fault::Limit);
        CHECK(!m.referenced() && !m.enabled());
        CHECK(!m.clear(3, 1000, h));
        CHECK(m.clear(3, 1000, good));
        CHECK(m.state == State::Unreferenced);
    }
    m = armed();
    CHECK(m.tick(500000, good) == 0 && m.fault == Fault::HostTimeout);
    m = armed(); Health h = good; h.stop_closed = false;
    CHECK(m.tick(250, h) == 0 && m.fault == Fault::Stop);
    m = armed(); h = good; h.motor_supply_ok = false;
    CHECK(m.tick(250, h) == 0 && m.fault == Fault::Supply);
    m = armed(); h = good; h.drivers_ok = false;
    CHECK(m.tick(250, h) == 0 && m.fault == Fault::Driver);
    m = armed(); CHECK(m.move(3, 0, 1000000, {640, 0, 0, 0, 0, 0}, good));
    CHECK(m.tick(750, good) == 0 && m.fault == Fault::Timing);
    CHECK(!m.referenced());
    m = armed(); CHECK(m.disarm(3, 1000));
    CHECK(!m.referenced() && !m.enabled());
    MotionPolicy reset;
    CHECK(!reset.referenced() && !reset.enabled());
    CHECK(!reset.move(1, 0, 1000000, {16, 0, 0, 0, 0, 0}, good));
    for (unsigned bad_field = 0; bad_field < 4; ++bad_field) {
        Health unhealthy = good;
        if (bad_field == 0) unhealthy.stop_closed = false;
        if (bad_field == 1) unhealthy.open_limit_mask = 1;
        if (bad_field == 2) unhealthy.motor_supply_ok = false;
        if (bad_field == 3) unhealthy.drivers_ok = false;
        MotionPolicy fresh;
        CHECK(!fresh.reference(1, 0, unhealthy));
        CHECK(fresh.reference(1, 0, good));
        CHECK(!fresh.reference(2, 0, good));
        CHECK(!fresh.arm(2, 0, unhealthy));
        m = armed();
        CHECK(!m.move(3, 0, 1000000, {16, 0, 0, 0, 0, 0}, unhealthy));
    }
    m = armed(); CHECK(!m.reference(3, 0, good));
    CHECK(m.tick(499999, good) == 0 && m.state == State::Armed);
    CHECK(m.tick(500000, good) == 0 && m.fault == Fault::HostTimeout);
    // Each mid-move fault freezes issued history and stays latched when healthy.
    for (unsigned why = 0; why < 6; ++why) {
        m = armed(); CHECK(m.move(3, 0, 1000000, {640, 0, 0, 0, 0, 0}, good));
        for (uint64_t t = 250; t <= 400000; t += 250) m.tick(t, good);
        Health bad = good;
        if (why == 0) bad.stop_closed = false;
        if (why == 1) bad.open_limit_mask = 2;
        if (why == 2) bad.motor_supply_ok = false;
        if (why == 3) bad.drivers_ok = false;
        const uint64_t t = why == 4 ? 500000 : why == 5 ? 401000 : 400250;
        const auto before = m.count;
        CHECK(m.tick(t, bad) == 0 && m.state == State::Fault);
        CHECK(!m.reference(4, t, good)); CHECK(!m.arm(4, t, good));
        CHECK(!m.disarm(4, t));
        CHECK(!m.move(4, t, 1000000, {16, 0, 0, 0, 0, 0}, good));
        for (uint64_t after = t + 250; after < t + 700000; after += 250)
            CHECK(m.tick(after, good) == 0 && m.count == before);
    }
    m = armed(); CHECK(m.move(3, 0, 1000000, {640, 0, 0, 0, 0, 0}, good));
    for (uint64_t t = 250; t <= 400000; t += 250) m.tick(t, good);
    m.emitted[0] -= 2; // Invalid progress history must never produce a catch-up burst.
    CHECK(m.tick(400250, good) == 0 && m.fault == Fault::Timing);
    m = armed(); CHECK(m.move(3, 0, 1000000, {640, 0, 0, 0, 0, 0}, good));
    for (uint64_t t = 250; t <= 400000; t += 250) m.tick(t, good);
    const auto interrupted = m.count;
    CHECK(m.disarm(4, 400001));
    CHECK(m.tick(400250, good) == 0 && m.count == interrupted && !m.referenced());
    m = armed();
    CHECK(!m.clear(2, 0, good)); CHECK(!m.reference(2, 0, good));
    CHECK(!m.arm(2, 0, good)); CHECK(!m.ping(2, 0)); CHECK(!m.disarm(2, 0));
    m.last_sequence = UINT32_MAX - 1;
    CHECK(m.ping(UINT32_MAX, 0)); CHECK(!m.ping(0, 0));
    std::puts("PASS: exact coordinated edges, all bounds/rate/acceleration, state/health/sequence refusal, mid-move latched faults, catch-up refusal, disarm and timeout boundary");
}
