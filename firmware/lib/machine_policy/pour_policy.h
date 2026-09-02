#pragma once

#include <stdint.h>

// ── The pour ──────────────────────────────────────────────────────────────
// Carbonated water is flowing at the faucet, and the selected channel's pump
// injects concentrate into it on a duty cycle. The DIGITEN meter's pulses are
// counted over kFlowSampleMs; each sample is a flow reading, kFlowMinPulses
// and up is flowing, kFlowFullPulses is full flow. A cycle is one on-phase and
// one off-phase with its timing locked at its start, from the flow reading
// and the channel's ratio; the next cycle takes the average reading over the
// last. A reading of zero inside a cycle sends the cycle into a cooldown with
// the pump off, and a cooldown that ends with nothing flowing ends the pour.
// This is src_prototype's loop, made pure so the timing and the sequence can
// be checked without a meter.
namespace machine_policy {

constexpr uint32_t kFlowSampleMs      = 50;
constexpr uint32_t kFlowMinPulses     = 1;
constexpr uint32_t kFlowFullPulses    = 6;
constexpr uint32_t kPourOnMinMs       = 50;
constexpr uint32_t kPourOffMaxMs      = 1000;
constexpr uint32_t kPourCooldownMs    = 1000;
constexpr uint32_t kPourCeilingMs     = 120000;   // a meter that never stops pulsing
constexpr uint32_t kPourShapeOnBase   = 20;
constexpr uint32_t kPourShapeOnSlope  = 30;
constexpr uint32_t kPourShapeOffBase  = 660;
constexpr uint32_t kPourShapeOffSlope = 60;

// The on and off times for one cycle at this flow reading and ratio. At 1:20
// full flow is 200 ms on and 300 ms off; at 1:6 full flow the pump stays on.
void pourCycleTiming(uint32_t pulses, uint8_t ratio, uint32_t &on_ms, uint32_t &off_ms);

enum class PourPhase : uint8_t {
    Idle = 0,
    On,
    Off,
    Cooldown,
};

// What the machine does next. Start opens the channel's dispense valves and
// turns its pump on; Stop turns the pump off if it is on and closes them.
enum class PourAction : uint8_t {
    None = 0,
    Start,
    PumpOn,
    PumpOff,
    Stop,
    Ceiling,   // Stop, because the pour ran kPourCeilingMs
};

class Pour {
public:
    Pour();

    // A flow reading: pulses counted over the last kFlowSampleMs.
    void sample(uint32_t pulses);

    // The clock. Called often; a phase ends here.
    PourAction service(uint32_t now_ms, uint8_t ratio);

    void reset();

    PourPhase phase() const;
    bool      flowing() const;
    bool      open() const;      // the dispense valves are open
    bool      pumpOn() const;
    uint32_t  onMs() const;      // the running cycle's timing
    uint32_t  offMs() const;
    uint32_t  elapsedMs(uint32_t now_ms) const;   // since the pour began

private:
    void beginCycle(uint32_t now_ms, uint32_t pulses, uint8_t ratio);

    PourPhase phase_;
    bool      open_;
    bool      pump_on_;
    uint32_t  last_pulses_;
    uint32_t  phase_start_ms_;
    uint32_t  pour_start_ms_;
    uint32_t  on_ms_;
    uint32_t  off_ms_;
    uint32_t  cycle_sum_;
    uint32_t  cycle_readings_;
    bool      cycle_saw_zero_;
};

}  // namespace machine_policy
