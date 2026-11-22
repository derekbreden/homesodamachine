// Replay the appliance's pour policy against the specified sequence of meter readings.
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <vector>
#include "pour_policy.h"

struct Stage { int end_ms; unsigned pulses; };

int main(int argc, char** argv) {
    if (argc < 4 || argc % 2 != 0) return 2;
    const auto ratio = static_cast<uint8_t>(std::stoi(argv[1]));
    std::vector<Stage> stages;
    int end = 0;
    for (int i = 2; i < argc; i += 2) {
        end += std::stoi(argv[i+1]);
        stages.push_back({end, static_cast<unsigned>(std::stoul(argv[i]))});
    }
    machine_policy::Pour pour;
    int on = -1;
    size_t stage = 0;
    for (int now=0; now <= end+4000; ++now) {
        while (stage < stages.size() && now >= stages[stage].end_ms) ++stage;
        if (now % machine_policy::kFlowSampleMs == 0)
            pour.sample(stage < stages.size() ? stages[stage].pulses : 0);
        const auto action = pour.service(now,ratio);
        if (action == machine_policy::PourAction::Start || action == machine_policy::PourAction::PumpOn)
            on = now;
        if (action == machine_policy::PourAction::PumpOff && on >= 0) {
            std::cout << on << ' ' << now-on << '\n';
            on = -1;
        }
        if (action == machine_policy::PourAction::Stop)
            std::cout << "stop " << now << '\n';
    }
}
