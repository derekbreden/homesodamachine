#pragma once

#include <stdint.h>

// ── The refill ────────────────────────────────────────────────────────────
// One donut magnet rides the water in the carbonator and two reeds stand on
// the bridge beside it: CLO at 67.12 mm closes as the level falls past it and
// asks for water, CHI at 95.25 mm closes as the level reaches it and ends the
// draw. Between the two the donut is off both reeds, so a refill is a latch
// from the one to the other and not a level a single reading answers.
//
// The SeaFlo draws 5 A and the main board peaks at 3.33 A against a 6.7 A
// supply, so relay #2 is off while a dispense window is open. CLO closes
// mid-pour — the level falls past it while the glass is filling — so the ask
// arrives inside exactly the window that refuses it, waits in Queued, and
// runs when the pour ends. A dispense that opens mid-refill sends the draw
// back to Queued and takes the relay down with it.
//
// machine.cpp holds relay #2 and V-K and asks here;
// `machine_policy::Operation::CarbonatorRefill` is the plan it applies.
namespace machine_policy {

// CLO held this long before the ask is believed. The donut is on a rod in a
// tube being bubbled, and the surface it rides is not still.
constexpr uint32_t kRefillDebounceMs = 1500;

// Pumping time, not wall time: a draw interrupted by three pours has spent
// none of its ceiling waiting for them.
constexpr uint32_t kRefillCeilingMs = 180000;

enum class RefillState : uint8_t {
    Idle = 0,
    Queued,    // CLO asked; the dispense window or another operation holds it
    Filling,
    Timeout,   // pumped kRefillCeilingMs without reaching CHI — latched
    Fault,     // CLO and CHI closed together, which one magnet cannot do — latched
};

enum class RefillAction : uint8_t {
    None = 0,
    Start,   // apply the CarbonatorRefill plan: V-K open, relay #2 on
    Stop,    // relay #2 off, V-K closed
};

// The two carbonator reeds. `valid` is the expander's own health: reeds that
// could not be read are not reeds that read open.
struct RefillReading {
    bool lowClosed;
    bool highClosed;
    bool valid;

    RefillReading();
};

// What else has a claim on the actuators this pass.
struct RefillContext {
    bool dispenseOpen;   // machineDispenseWindowOpen()
    bool machineIdle;    // nothing else owns the manifold

    RefillContext();
};

class Refill {
public:
    Refill();

    void reading(const RefillReading &r, uint32_t now_ms);

    RefillAction service(uint32_t now_ms, const RefillContext &ctx);

    // Leave Timeout or Fault. Idle and the two running states are unmoved.
    void clear(uint32_t now_ms);

    void reset(uint32_t now_ms);

    RefillState state() const;
    const char *stateName() const;
    bool        pumpOn() const;

    // Pumping time in the campaign that is running, or the one that timed out.
    uint32_t pumpedMs(uint32_t now_ms) const;

private:
    void enter(RefillState s, uint32_t now_ms);

    RefillState   state_;
    bool          pump_on_;
    RefillReading last_;
    bool          low_seen_;        // CLO has been closed continuously since:
    uint32_t      low_since_ms_;
    uint32_t      pumped_ms_;       // accumulated over the campaign
    uint32_t      filling_since_ms_;
};

}  // namespace machine_policy
