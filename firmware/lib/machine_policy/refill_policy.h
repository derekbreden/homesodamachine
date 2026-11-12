#pragma once

#include <stdint.h>

// ── The refill ────────────────────────────────────────────────────────────
// One RC62 magnet in an ASA Aero float rides the water in the carbonator and two reeds stand on
// the bridge beside it. Design liquid targets are CLO at 67.098 mm and
// CHI at 95.250 mm above the bottom tube rim; the reed glass centers include
// immersion and directional activation offsets. Low asks for water, high ends it.
// Between activation windows both reeds can be open; the windows may overlap. A refill is a latch
// from the one to the other and not a level a single reading answers.
//
// The latch is the one thing known about the water once it has fallen through the low reed:
// a refill is owed until the high reed says it was paid. Below the low reed's window no reed
// is closed, so nothing a later reading shows can raise the ask again. It is therefore kept
// through everything that is not the high reed: a pour, reeds that cannot be read, a draw
// that timed out, and — in the flash machine.cpp keeps it in — a power cut.
//
// The pumping ceiling is what stops a draw that is going nowhere: a supply that is shut off,
// a line that has come off, a float that no longer rises. The machine cannot tell these
// apart, so the ceiling is spent once and only someone told to look can grant another. The
// time spent is therefore kept with the ask, counted ahead of the pump so that a restart
// never finds less than was pumped, and a board that restarts — once or in a loop — takes
// up the count it left and comes up latched when the count is the whole ceiling.
//
// The G Ganen is budgeted at 5 A and the main board peaks at 3.33 A against a
// 6.7 A supply, so relay #2 is off while a dispense window is open. CLO closes
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

// The step the kept pumping time moves in. While the pump runs the count stands at the end
// of the step it is in, so a restart costs a campaign at most one step it did not pump.
constexpr uint32_t kRefillKeepStepMs = 15000;

enum class RefillState : uint8_t {
    Idle = 0,
    Queued,    // CLO asked; the dispense window or another operation holds it
    Filling,
    Timeout,   // pumped kRefillCeilingMs without reaching CHI — latched
    Fault,     // reserved latched fault state; valid overlapping reed windows are allowed
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

    // Leave Timeout or Fault and try again with a whole ceiling: the refill is still owed.
    // Idle and the two running states are unmoved, and false says so.
    bool clear(uint32_t now_ms);

    // A boot that finds a refill was owed when the power went: queue it with the pumping
    // time already spent on it, or stand latched when that is the whole ceiling.
    void resume(uint32_t now_ms, uint32_t spent_ms = 0);

    // True from the ask until the high reed ends it.
    bool owed() const;

    void reset(uint32_t now_ms);

    RefillState state() const;
    const char *stateName() const;
    bool        pumpOn() const;

    // Pumping time in the campaign that is running, or the one that timed out.
    uint32_t pumpedMs(uint32_t now_ms) const;

    // The pumping time to keep through a restart: never less than was pumped.
    uint32_t keptMs() const;

private:
    void enter(RefillState s, uint32_t now_ms);

    RefillState   state_;
    bool          pump_on_;
    RefillReading last_;
    bool          low_seen_;        // CLO has been closed continuously since:
    uint32_t      low_since_ms_;
    uint32_t      pumped_ms_;       // accumulated over the campaign
    uint32_t      kept_ms_;         // what a restart is to find of it
    uint32_t      filling_since_ms_;
};

}  // namespace machine_policy
