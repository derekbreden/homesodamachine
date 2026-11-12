#include <algorithm>
#include <functional>
#include <stdlib.h>

#include "../machine_host/machine_host.h"

// A month at a kitchen sink, for the production machine code to live through on the build
// host: a carbonator that drains and fills, a cooling loop that warms and cools, a household
// that pours, and the troubles a month can bring. The machine's own code decides everything
// it would decide on the board; what is invented here is the kitchen.
//
// The kitchen's numbers are a plausible kitchen and not a measured one. What a run proves is
// how the control behaves in it: what it never does, and that it finds its way back.

namespace {

namespace plant {

// The carbonator, as millilitres above empty. A reed is closed while the water stands
// within its window.
constexpr float kLowReedMl    = 700.0f;
constexpr float kHighReedMl   = 1200.0f;
constexpr float kReedWindowMl = 60.0f;
constexpr float kTankTopMl    = 1500.0f;   // the float can go no higher than this

constexpr float kPourMlPerS   = 39.0f;     // a glass in about nine seconds
constexpr float kRefillMlPerS = 15.0f;
constexpr uint32_t kPulsesPerSample = machine_policy::kFlowFullPulses;

constexpr float kAmbientC     = 22.0f;
constexpr float kTapC         = 15.0f;
constexpr float kTankWarmS    = 72000.0f;  // time constant of the foamed core warming
constexpr float kCoolCPerS    = 1.0f / 360.0f;
constexpr float kCoilFloorC   = -6.0f;     // where the suction line settles while running
constexpr float kCoilRunS     = 120.0f;
constexpr float kCoilRestS    = 300.0f;

}  // namespace plant

constexpr uint64_t kSecond = 1000;
constexpr uint64_t kMinute = 60 * kSecond;
constexpr uint64_t kHour   = 60 * kMinute;
constexpr uint64_t kDay    = 24 * kHour;
constexpr uint32_t kDays   = 30;

constexpr uint32_t kActiveStepMs = machine_policy::kFlowSampleMs;
constexpr uint32_t kIdleStepMs   = 1000;

// How long after a trouble ends a glass may still be a poor one: a refill, and the wait for
// the drivers to be verified again.
constexpr uint64_t kGraceMs = 15 * kMinute;

// The month's last days, by which every trouble is long over.
constexpr uint64_t kLateFrom = 27 * kDay;

// How long someone waits before trying the faucet again after a poor glass.
constexpr uint64_t kTryAgainMs = 3 * kMinute;

struct Glass {
    uint64_t at;
    uint32_t ms;
    uint8_t  channel;
};

enum class Poured { Soda, Plain, Dry };

struct Kitchen {
    // The plant.
    float levelMl   = plant::kHighReedMl - plant::kReedWindowMl;
    float tankC     = plant::kAmbientC;
    float coilC     = plant::kAmbientC;
    float coilFloor = plant::kCoilFloorC;
    bool  waterOn   = true;
    bool  tankProbe = true;
    bool  coilProbe = true;
    bool  powered   = true;

    // The clock: milliseconds since the month began.
    uint64_t t = 0;

    // The glass being poured.
    bool     faucetOpen   = false;
    uint64_t faucetCloses = 0;
    float    glassWaterMl = 0;
    uint32_t glassFlavorMs = 0;
    uint32_t glassMs      = 0;

    // What happened.
    uint32_t glasses = 0, soda = 0, plain = 0, dry = 0;
    uint32_t unexplained = 0;              // poor glasses outside any trouble's window
    uint32_t lateGlasses = 0, lateSoda = 0;   // in the month's last days
    std::vector<std::pair<uint64_t, uint64_t>> troubles;   // [from, until] in month time

    // A person who gets a poor glass goes to the machine, does what its display says and
    // has it try the water again, then tries the faucet again shortly.
    bool asksAgain = false;
    bool tryingAgain = false;
    uint32_t retries = 0;                  // asks that found a refill standing latched
    std::vector<Glass> again;
    std::vector<std::pair<uint64_t, std::function<void(Kitchen &)>>> later;
    std::function<void(Kitchen &)> watch;
    uint64_t refillOnSince = 0;
    uint32_t refills = 0;
    uint32_t compressorRuns = 0;
    float    peakLevelMl = 0;
    float    warmestAfterFirstDayC = -100.0f;
    uint32_t boots = 0;

    // Watched every step.
    bool     compressorWas = false;
    uint32_t compressorOffAt = 0;          // host::now when relay #1 last opened
    bool     compressorEverOff = false;
    bool     refillWas = false;
    uint32_t shortRestarts = 0;            // relay #1 closed inside its minimum off-time
    uint32_t fanlessSteps = 0;             // relay #1 closed with the condenser fan off
    uint32_t refillDuringDispense = 0;
    uint32_t refillWithoutValve = 0;
    uint32_t tooManyValves = 0;
    uint32_t refillChatter = 0;            // relay #2 closed again within a second of opening
    uint64_t refillOffAt = 0;
    bool     refillEverOff = false;
    // Pumping on one owed refill since it was asked for or someone last asked again, through
    // every restart, and the most that ever reached.
    uint64_t pumpedUnasked = 0;
    uint64_t mostPumpedUnasked = 0;
    uint64_t pumpedMs = 0;
};

bool relayClosed(int pin) { return host::modes[pin] == OUTPUT; }

uint8_t valveCount(uint16_t mask) {
    uint8_t n = 0;
    for (; mask; mask &= static_cast<uint16_t>(mask - 1)) n++;
    return n;
}

// What a power cut leaves: nothing in RAM, a clock at zero, and every chip reset.
void boot(Kitchen &k, uint32_t clockAt = 0) {
    host::now = clockAt;
    memset(host::duties, 0, sizeof(host::duties));
    memset(host::modes, 0, sizeof(host::modes));
    host::bus.reset();
    gasTrip = gasRaw = false;
    gasChanged = 0;
    reedCacheValid = false;
    reedIdleMs = 0;
    flowEdges = 0;
    reservoirLevel[0] = reservoirLevel[1] = machine_policy::ReservoirLevel();
    machineSimClear();
    machineFlowSimulate(0, 0);
    machineBegin();
    k.powered         = true;
    k.compressorWas   = false;
    k.compressorEverOff = false;
    k.refillWas       = false;
    k.refillEverOff   = false;
    k.boots++;
}

void cutPower(Kitchen &k) {
    // Every load drops with the supply.
    memset(host::duties, 0, sizeof(host::duties));
    memset(host::modes, 0, sizeof(host::modes));
    host::bus.reset();
    k.powered = false;
}

bool inTrouble(const Kitchen &k, uint64_t at) {
    for (const auto &window : k.troubles)
        if (at >= window.first && at <= window.second + kGraceMs) return true;
    return false;
}

void closeGlass(Kitchen &k) {
    const float expected = plant::kPourMlPerS * static_cast<float>(k.glassMs) / 1000.0f;
    Poured got = Poured::Soda;
    if (k.glassWaterMl < expected * 0.5f) got = Poured::Dry;
    else if (k.glassFlavorMs == 0) got = Poured::Plain;
    k.glasses++;
    if (got == Poured::Soda) k.soda++;
    if (got == Poured::Plain) k.plain++;
    if (got == Poured::Dry) k.dry++;
    if (got != Poured::Soda && !inTrouble(k, k.t)) k.unexplained++;
    if (k.t >= kLateFrom) {
        k.lateGlasses++;
        if (got == Poured::Soda) k.lateSoda++;
    }
    k.faucetOpen = false;
    if (got != Poured::Soda && k.asksAgain && !k.tryingAgain && k.powered) {
        if (machineRefillRetry()) {
            k.retries++;
            k.pumpedUnasked = 0;
        }
        k.again.push_back({k.t + kTryAgainMs, 6000, host::flavor});
    }
    k.tryingAgain = false;
}

// One step of the kitchen, then one pass of the machine.
void step(Kitchen &k, uint32_t dtMs) {
    const float dt = static_cast<float>(dtMs) / 1000.0f;
    const bool compressor = k.powered && relayClosed(PIN_RELAY_COMPRESSOR);
    const bool refill     = k.powered && relayClosed(PIN_RELAY_REFILL);
    const uint16_t valves = k.powered ? machineValvesOpen() : 0;
    const bool vK = valves & machine_policy::valveBit(machine_policy::Valve::K);
    const bool flavorPump = k.powered && (host::duties[PIN_PUMP_A] || host::duties[PIN_PUMP_B]);

    // Water.
    if (refill && vK && k.waterOn && k.levelMl < plant::kTankTopMl) {
        const float added = std::min(plant::kRefillMlPerS * dt, plant::kTankTopMl - k.levelMl);
        k.tankC   = (k.levelMl * k.tankC + added * plant::kTapC) / (k.levelMl + added);
        k.levelMl += added;
    }
    uint32_t pulses = 0;
    if (k.faucetOpen) {
        k.glassMs += dtMs;
        const float drawn = std::min(plant::kPourMlPerS * dt, k.levelMl);
        k.levelMl      -= drawn;
        k.glassWaterMl += drawn;
        if (drawn > 0) {
            pulses = (plant::kPulsesPerSample * dtMs + kActiveStepMs / 2) / kActiveStepMs;
            if (flavorPump) k.glassFlavorMs += dtMs;
        }
    }
    k.peakLevelMl = std::max(k.peakLevelMl, k.levelMl);

    // Cold.
    k.tankC += (plant::kAmbientC - k.tankC) * dt / plant::kTankWarmS;
    if (compressor) k.tankC -= plant::kCoolCPerS * dt;
    const float coilToward = compressor ? k.coilFloor : k.tankC;
    const float coilTau    = compressor ? plant::kCoilRunS : plant::kCoilRestS;
    k.coilC += (coilToward - k.coilC) * std::min(1.0f, dt / coilTau);
    if (k.t > kDay) k.warmestAfterFirstDayC = std::max(k.warmestAfterFirstDayC, k.tankC);

    k.t += dtMs;
    if (k.faucetOpen && k.t >= k.faucetCloses) closeGlass(k);
    if (!k.powered) return;

    // What the machine reads.
    host::probeTankC     = k.tankC;
    host::probeTankValid = k.tankProbe;
    host::probeCoilC     = k.coilC;
    host::probeCoilValid = k.coilProbe;
    uint8_t &reeds = host::bus.at(pcba::MCP_RESERVOIR_B, host::kGpioB);
    reeds |= 0x30;
    if (k.levelMl >= plant::kLowReedMl - plant::kReedWindowMl &&
        k.levelMl <= plant::kLowReedMl + plant::kReedWindowMl) reeds &= static_cast<uint8_t>(~0x10);
    if (k.levelMl >= plant::kHighReedMl - plant::kReedWindowMl &&
        k.levelMl <= plant::kHighReedMl + plant::kReedWindowMl) reeds &= static_cast<uint8_t>(~0x20);
    for (uint32_t i = 0; i < pulses; i++) flowIsr();

    host::now += dtMs;
    machineService();

    // What it did, held to what it must never do.
    const bool compressorNow = relayClosed(PIN_RELAY_COMPRESSOR);
    const bool refillNow     = relayClosed(PIN_RELAY_REFILL);
    const uint16_t open      = machineValvesOpen();
    if (compressorNow && !k.compressorWas) {
        k.compressorRuns++;
        const uint32_t rested = k.compressorEverOff ? host::now - k.compressorOffAt : host::now;
        if (rested < machine_policy::kMinOffMs) k.shortRestarts++;
    }
    if (!compressorNow && k.compressorWas) {
        k.compressorOffAt   = host::now;
        k.compressorEverOff = true;
    }
    if (compressorNow && !pcba::expanders().currentOutputs().condenserFan) k.fanlessSteps++;
    if (refillNow && machineDispenseWindowOpen()) k.refillDuringDispense++;
    if (refillNow && !(open & machine_policy::valveBit(machine_policy::Valve::K))) k.refillWithoutValve++;
    if (valveCount(open) > 3) k.tooManyValves++;
    if (refillNow && !k.refillWas) {
        k.refills++;
        k.refillOnSince = k.t;
        // A pour takes the pump down and gives it back when it ends; nothing else starts
        // it again within a second of stopping it.
        if (k.refillEverOff && k.t - k.refillOffAt < kSecond && !k.faucetOpen) k.refillChatter++;
    }
    if (!refillNow && k.refillWas) {
        k.refillOffAt   = k.t;
        k.refillEverOff = true;
    }
    if (refillNow) {
        k.pumpedMs      += dtMs;
        k.pumpedUnasked += dtMs;
        k.mostPumpedUnasked = std::max(k.mostPumpedUnasked, k.pumpedUnasked);
    }
    MachineThermal thermal;
    machineThermal(thermal);
    if (thermal.refillState == static_cast<uint8_t>(machine_policy::RefillState::Idle)) k.pumpedUnasked = 0;
    k.compressorWas = compressorNow;
    k.refillWas     = refillNow;
}

struct Event {
    uint64_t at;
    std::function<void(Kitchen &)> what;
};

// A household's month: glasses through the waking day, a second glass now and then, and a
// pitcher some days. The same month every run.
std::vector<Glass> household(uint32_t seed) {
    std::vector<Glass> glasses;
    uint32_t state = seed;
    auto roll = [&state](uint32_t below) {
        state = state * 1664525u + 1013904223u;
        return (state >> 8) % below;
    };
    for (uint32_t day = 0; day < kDays; day++) {
        const uint32_t count = 6 + roll(7);
        std::vector<uint64_t> starts;
        for (uint32_t i = 0; i < count; i++)
            starts.push_back(day * kDay + 7 * kHour + roll(15 * 60) * kMinute + roll(60) * kSecond);
        std::sort(starts.begin(), starts.end());
        uint64_t freeFrom = 0;
        for (uint64_t at : starts) {
            at = std::max(at, freeFrom);
            uint32_t ms = 5000 + roll(5000);
            if (roll(12) == 0) ms = 25000;   // a pitcher
            const uint8_t channel = roll(10) < 7 ? 0 : 1;
            glasses.push_back({at, ms, channel});
            freeFrom = at + ms + 20 * kSecond;
            if (roll(5) == 0) {              // and one for someone else
                glasses.push_back({freeFrom, 5000 + roll(4000), channel});
                freeFrom += 30 * kSecond;
            }
        }
    }
    return glasses;
}

// Run the month: glasses and events in time order, the machine stepped finely while anything
// moves and by the second while nothing does.
void live(Kitchen &k, std::vector<Glass> glasses, std::vector<Event> events) {
    std::sort(events.begin(), events.end(), [](const Event &a, const Event &b) { return a.at < b.at; });
    size_t nextGlass = 0, nextEvent = 0;
    const uint64_t end = kDays * kDay;
    uint64_t busyUntil = 0;
    auto open = [&k](const Glass &g, bool again) {
        host::flavor    = g.channel;
        k.faucetOpen    = true;
        k.tryingAgain   = again;
        k.faucetCloses  = k.t + g.ms;
        k.glassWaterMl  = 0;
        k.glassFlavorMs = 0;
        k.glassMs       = 0;
    };
    while (k.t < end) {
        while (nextEvent < events.size() && events[nextEvent].at <= k.t) events[nextEvent++].what(k);
        for (size_t i = 0; i < k.later.size();) {
            if (k.later[i].first > k.t) { i++; continue; }
            const std::function<void(Kitchen &)> what = k.later[i].second;
            k.later.erase(k.later.begin() + static_cast<long>(i));
            what(k);
        }
        if (k.watch) k.watch(k);
        if (!k.faucetOpen && !k.again.empty() && k.again.front().at <= k.t) {
            const Glass g = k.again.front();
            k.again.erase(k.again.begin());
            open(g, true);
        } else if (!k.faucetOpen && nextGlass < glasses.size() && glasses[nextGlass].at <= k.t) {
            open(glasses[nextGlass++], false);
        }
        const bool moving = k.faucetOpen || (k.powered && machineState() != ST_IDLE);
        if (moving) busyUntil = k.t + 3 * kSecond;
        uint64_t dt = (moving || k.t < busyUntil) ? kActiveStepMs : kIdleStepMs;
        auto until = [&dt, &k](uint64_t at) {
            dt = std::min<uint64_t>(dt, std::max<uint64_t>(1, at > k.t ? at - k.t : 1));
        };
        if (nextEvent < events.size()) until(events[nextEvent].at);
        for (const auto &due : k.later) until(due.first);
        if (!k.faucetOpen && nextGlass < glasses.size()) until(glasses[nextGlass].at);
        if (!k.faucetOpen && !k.again.empty()) until(k.again.front().at);
        step(k, static_cast<uint32_t>(dt));
    }
}

uint32_t noted(machine_log::Kind kind) {
    uint32_t n = 0;
    for (const machine_log::Entry &entry : host::noted)
        if (entry.kind == kind) n++;
    return n;
}

uint32_t notedRefills(machine_log::RefillEnd end) {
    uint32_t n = 0;
    for (const machine_log::Entry &entry : host::noted)
        if (entry.kind == machine_log::Kind::Refill && entry.detail == static_cast<uint8_t>(end)) n++;
    return n;
}

void never(const Kitchen &k) {
    TEST_ASSERT_EQUAL_UINT32_MESSAGE(0, k.shortRestarts, "the compressor restarted inside its minimum off-time");
    TEST_ASSERT_EQUAL_UINT32_MESSAGE(0, k.fanlessSteps, "the compressor ran with its condenser fan off");
    TEST_ASSERT_EQUAL_UINT32_MESSAGE(0, k.refillDuringDispense, "the refill pump ran while a dispense was open");
    TEST_ASSERT_EQUAL_UINT32_MESSAGE(0, k.refillWithoutValve, "the refill pump ran against a closed V-K");
    TEST_ASSERT_EQUAL_UINT32_MESSAGE(0, k.tooManyValves, "more than three valves were open at once");
    TEST_ASSERT_EQUAL_UINT32_MESSAGE(0, k.refillChatter, "the refill pump was switched off and straight back on");
    TEST_ASSERT_FALSE_MESSAGE(host::pumpClosedAgainstDrive, "a valve closed against a running flavor pump");
    TEST_ASSERT_TRUE_MESSAGE(k.peakLevelMl <= plant::kHighReedMl + plant::kReedWindowMl,
                             "the carbonator was filled past its high reed");
    TEST_ASSERT_TRUE_MESSAGE(k.mostPumpedUnasked <= machine_policy::kRefillCeilingMs + kIdleStepMs,
                             "one refill was pumped past its ceiling with nobody asking for it");
}

void report(const char *name, const Kitchen &k) {
    printf("\n%s: %lu glasses — %lu soda, %lu plain, %lu dry; %lu refills, %lu compressor runs, %lu boots, "
           "%lu times someone had it try the water again\n",
           name, (unsigned long)k.glasses, (unsigned long)k.soda, (unsigned long)k.plain,
           (unsigned long)k.dry, (unsigned long)k.refills, (unsigned long)k.compressorRuns,
           (unsigned long)k.boots, (unsigned long)k.retries);
    printf("  record: %lu pours, %lu refills full, %lu timed out, %lu compressor runs, %lu cold, %lu io, %lu gas\n",
           (unsigned long)noted(machine_log::Kind::Pour),
           (unsigned long)notedRefills(machine_log::RefillEnd::Full),
           (unsigned long)notedRefills(machine_log::RefillEnd::Timeout),
           (unsigned long)noted(machine_log::Kind::Compressor), (unsigned long)noted(machine_log::Kind::Cold),
           (unsigned long)noted(machine_log::Kind::Io), (unsigned long)noted(machine_log::Kind::Gas));
    printf("  the model's tank peaked at %.1f C after the first day; faults sounded %lu, alarms %lu\n",
           k.warmestAfterFirstDayC, (unsigned long)host::played[SND_FAULT], (unsigned long)host::played[SND_ALARM]);
}

void fresh() {
    host::keepEvents = false;
    host::events.clear();
    host::noted.clear();
    memset(host::played, 0, sizeof(host::played));
    host::flavor = 0;
    host::ratio  = 20;
    host::probeCount = 2;
    host::refillOwedInFlash  = false;
    host::refillSpentInFlash = 0;
    host::refillOwedWrites   = 0;
    host::refillSpentWrites  = 0;
    host::flashForgets       = false;
    host::busMs             = 1;   // a bus that takes time, as the board's does
    host::gasMv             = 0;
    host::attachSucceeds    = true;
    host::pumpClosedAgainstDrive = false;
}

// The clock starts close enough to its wrap that the month crosses it.
constexpr uint32_t kClockNearWrap = 0xFFFFFFFFu - static_cast<uint32_t>(10 * kDay);

void test_an_ordinary_month() {
    fresh();
    Kitchen k;
    boot(k, kClockNearWrap);
    const std::vector<Glass> glasses = household(20261112u);
    live(k, glasses, {});
    report("an ordinary month", k);

    never(k);
    TEST_ASSERT_EQUAL_UINT32(glasses.size(), k.glasses);
    TEST_ASSERT_EQUAL_UINT32_MESSAGE(k.glasses, k.soda, "a glass in an ordinary month was not soda");
    TEST_ASSERT_EQUAL_UINT32(0, host::played[SND_FAULT]);
    TEST_ASSERT_EQUAL_UINT32(0, host::played[SND_ALARM]);
    TEST_ASSERT_EQUAL_UINT32(0, notedRefills(machine_log::RefillEnd::Timeout));
    TEST_ASSERT_EQUAL_UINT32(0, noted(machine_log::Kind::Io));
    TEST_ASSERT_EQUAL_UINT32(0, noted(machine_log::Kind::Cold));
    TEST_ASSERT_EQUAL_UINT32(0, noted(machine_log::Kind::Gas));
    // A pitcher can outrun the carbonator: the flow stops and starts as the refill catches
    // up, and each stretch of it is a pour to the machine.
    TEST_ASSERT_TRUE(noted(machine_log::Kind::Pour) >= k.glasses);
    TEST_ASSERT_TRUE(k.refills > kDays);
    TEST_ASSERT_TRUE(k.compressorRuns > kDays);
    TEST_ASSERT_EQUAL_UINT32(k.compressorRuns, noted(machine_log::Kind::Compressor) + (k.compressorWas ? 1 : 0));
    TEST_ASSERT_EQUAL_UINT32(1, k.boots);
}

// The same household, in a month where the water is shut off for a morning, the power goes
// four times — once in the middle of a refill and once just after a pitcher has taken the
// water below the low reed — a probe stops answering, the bus glitches twice, the gas alarm
// trips, and the suction line runs cold enough to reach the freeze cutoff.
void test_a_month_of_trouble() {
    fresh();
    Kitchen k;
    // Two things carry a machine through this month: the flash keeping an owed refill and
    // the pumping time spent on it, and someone at the machine having it try the water again
    // after a refill has timed out, which nothing else does. Run with either taken away to
    // see what it is for: MONTH_FLASH_FORGETS=1 or MONTH_NOBODY_ASKS=1.
    host::flashForgets = getenv("MONTH_FLASH_FORGETS") != nullptr;
    k.asksAgain        = getenv("MONTH_NOBODY_ASKS") == nullptr;
    boot(k, kClockNearWrap);

    const uint64_t pitcherAt = 6 * kDay + 10 * kHour;
    std::vector<Glass> glasses;
    for (const Glass &g : household(20261112u))
        if (g.at + 5 * kMinute < pitcherAt || g.at > pitcherAt + 5 * kMinute) glasses.push_back(g);
    glasses.push_back({pitcherAt, 28000, 0});
    std::sort(glasses.begin(), glasses.end(), [](const Glass &a, const Glass &b) { return a.at < b.at; });

    auto trouble = [&k](uint64_t from, uint64_t until) { k.troubles.push_back({from, until}); };
    auto cutFor = [](Kitchen &kitchen, uint64_t outage) {
        cutPower(kitchen);
        kitchen.later.push_back({kitchen.t + outage, [](Kitchen &back) { boot(back); }});
    };
    std::vector<Event> events;

    // The power goes while nothing is happening.
    events.push_back({2 * kDay + 3 * kHour, [&](Kitchen &kitchen) { cutFor(kitchen, 10 * kMinute); }});
    trouble(2 * kDay + 3 * kHour, 2 * kDay + 3 * kHour + 10 * kMinute);

    // The power goes in the middle of a refill.
    bool cutMidRefill = false, cutMidRefillDone = false;
    events.push_back({4 * kDay, [&](Kitchen &) { cutMidRefill = true; }});
    trouble(4 * kDay, 5 * kDay);

    // A pitcher takes the water below the low reed, and the power goes as the refill begins.
    events.push_back({pitcherAt + 30 * kSecond, [&](Kitchen &kitchen) { cutFor(kitchen, 5 * kMinute); }});
    trouble(pitcherAt, pitcherAt + 10 * kMinute);

    // The water is shut off for a morning.
    events.push_back({9 * kDay + 9 * kHour, [](Kitchen &kitchen) { kitchen.waterOn = false; }});
    events.push_back({9 * kDay + 13 * kHour, [](Kitchen &kitchen) { kitchen.waterOn = true; }});
    trouble(9 * kDay + 9 * kHour, 10 * kDay);

    // The tank probe stops answering for half an hour.
    events.push_back({13 * kDay + 15 * kHour, [](Kitchen &kitchen) { kitchen.tankProbe = false; }});
    events.push_back({13 * kDay + 15 * kHour + 30 * kMinute, [](Kitchen &kitchen) { kitchen.tankProbe = true; }});

    // The bus glitches once at rest and once in the middle of a glass.
    events.push_back({16 * kDay + 11 * kHour, [](Kitchen &) {
        host::bus.failRead(pcba::MCP_RESERVOIR_A, host::kGpioB);
    }});
    trouble(16 * kDay + 11 * kHour, 16 * kDay + 11 * kHour + kMinute);
    bool glitchMidGlass = false;
    events.push_back({16 * kDay + 18 * kHour, [&](Kitchen &) { glitchMidGlass = true; }});
    trouble(16 * kDay + 18 * kHour, 17 * kDay);

    // The gas alarm trips for three minutes.
    events.push_back({19 * kDay + 14 * kHour, [](Kitchen &) { host::gasMv = GAS_TRIP_MV + 500; }});
    events.push_back({19 * kDay + 14 * kHour + 3 * kMinute, [](Kitchen &) { host::gasMv = 0; }});
    trouble(19 * kDay + 14 * kHour, 19 * kDay + 14 * kHour + 3 * kMinute);

    // The suction line runs colder than the freeze cutoff for two hours.
    events.push_back({22 * kDay + 8 * kHour, [](Kitchen &kitchen) {
        kitchen.coilFloor = machine_policy::kFreezeCutoffC - 2.0f;
    }});
    events.push_back({22 * kDay + 10 * kHour, [](Kitchen &kitchen) { kitchen.coilFloor = plant::kCoilFloorC; }});

    // The power is out for two hours in the night.
    events.push_back({25 * kDay + kHour, [&](Kitchen &kitchen) { cutFor(kitchen, 2 * kHour); }});
    trouble(25 * kDay + kHour, 25 * kDay + 3 * kHour);

    k.watch = [&](Kitchen &kitchen) {
        if (cutMidRefill && !cutMidRefillDone && kitchen.powered && relayClosed(PIN_RELAY_REFILL) &&
            kitchen.t - kitchen.refillOnSince >= 5 * kSecond) {
            cutMidRefillDone = true;
            cutFor(kitchen, 2 * kMinute);
        }
        if (glitchMidGlass && kitchen.faucetOpen && kitchen.glassMs >= 1500) {
            glitchMidGlass = false;
            host::bus.failRead(pcba::MCP_RESERVOIR_A, host::kGpioB);
        }
    };

    live(k, glasses, events);
    report("a month of trouble", k);

    never(k);
    TEST_ASSERT_TRUE(cutMidRefillDone);
    TEST_ASSERT_EQUAL_UINT32_MESSAGE(0, k.unexplained, "a poor glass came with no trouble to explain it");
    TEST_ASSERT_TRUE(k.lateGlasses > 0);
    TEST_ASSERT_EQUAL_UINT32_MESSAGE(k.lateGlasses, k.lateSoda, "the month did not end with every glass a soda");
    // The water being shut off leaves a refill timed out, and it is someone at the machine
    // that sets it filling again.
    TEST_ASSERT_TRUE(k.retries >= 1);
    TEST_ASSERT_EQUAL_UINT32(5, k.boots);

    // It ends as a machine that is working: its drivers verified, nothing latched, water in it.
    TEST_ASSERT_TRUE(machineIoReady());
    MachineThermal thermal;
    machineThermal(thermal);
    TEST_ASSERT_NOT_EQUAL(static_cast<uint8_t>(machine_policy::RefillState::Timeout), thermal.refillState);
    TEST_ASSERT_TRUE(k.levelMl >= plant::kLowReedMl - plant::kReedWindowMl);

    // And the record says what happened to it.
    TEST_ASSERT_TRUE(notedRefills(machine_log::RefillEnd::Timeout) >= 1);
    TEST_ASSERT_TRUE(noted(machine_log::Kind::Io) >= 2);
    TEST_ASSERT_TRUE(noted(machine_log::Kind::Gas) >= 1);
    TEST_ASSERT_TRUE(noted(machine_log::Kind::Cold) >= 2);
    TEST_ASSERT_TRUE(host::played[SND_ALARM] >= 1);
    TEST_ASSERT_TRUE(host::played[SND_FAULT] >= 1);

    // The flash is written when a refill is owed and when it is paid, and for each step of
    // pumping, and no oftener.
    TEST_ASSERT_TRUE(host::refillOwedWrites <= 2 * k.refills + 2 * k.boots);
    TEST_ASSERT_TRUE(host::refillSpentWrites <=
                     2 * k.refills + 2 * k.boots + k.pumpedMs / machine_policy::kRefillKeepStepMs);
}

}  // namespace

void setUp() {}
void tearDown() {}

int main(int, char **) {
    UNITY_BEGIN();
    RUN_TEST(test_an_ordinary_month);
    RUN_TEST(test_a_month_of_trouble);
    return UNITY_END();
}
