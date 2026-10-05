#include <cstdio>
#include "../motion_policy.h"
using namespace gun_positioner;
int main() {
    const Health h{true, 0, true, true};
    MotionPolicy m;
    m.reference(1, 0, h); m.arm(2, 0, h);
    m.move(3, 0, 1000000, {640, -321, 16, -7, 63, -640}, h);
    uint32_t seq = 3;
    std::puts("{\"source\":\"policy_simulation\",\"type\":\"start\",\"time_us\":0,\"requested\":[640,-321,16,-7,63,-640],\"physical_observation\":null}");
    for (uint64_t t = kTickUs; t <= 1010000; t += kTickUs) {
        if (t % 100000 == 0) m.ping(++seq, t);
        const uint8_t mask = m.tick(t, h);
        if (mask) printf("{\"source\":\"policy_simulation\",\"type\":\"edge\",\"time_us\":%llu,\"axis_mask\":%u,\"count\":[%d,%d,%d,%d,%d,%d]}\n",
                         static_cast<unsigned long long>(t), mask, m.count[0], m.count[1],
                         m.count[2], m.count[3], m.count[4], m.count[5]);
    }
    printf("{\"source\":\"policy_simulation\",\"type\":\"complete\",\"time_us\":%llu,\"state\":\"%s\",\"physical_observation\":null}\n",
           static_cast<unsigned long long>(m.completed_us), state_name(m.state));
    return m.state == State::Armed ? 0 : 1;
}
