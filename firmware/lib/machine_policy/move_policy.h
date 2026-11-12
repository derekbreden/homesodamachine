#pragma once

#include <stdint.h>

#include "refill_policy.h"
#include "sweep_policy.h"

// ── The move ──────────────────────────────────────────────────────────────
// A machine that is to be moved has its tank emptied first: the supplies are shut, and the
// lever at the faucet lets out what the tank holds. Nothing on the board can see that done
// with the power off, and the faucet works without it. So the person says it at the
// machine's display before the plug comes out, and from then until the power goes the
// machine is moving.
//
// While it is moving no refill starts: the supply is shut and the tank is meant to empty.
// The meter's pulses open no pour: what leaves goes down the sink, and no flavor follows
// it. The power going is the end of it. machine.cpp keeps `moving` in flash, and a board
// that starts with it kept owes a sweep (sweep_policy.h), because a tank that was emptied
// and uncoupled has stood open to the air. That start is a first start again.
//
// What the board can tell of the drain is little. The meter turning says something is
// leaving, water or gas. The float passing the low reed says the water is below it. No reed
// stands lower, so nothing says the tank is empty: that is for whoever holds the lever to
// hear.
namespace machine_policy {

class Move {
public:
    Move();

    // The machine is to be moved. `belowLow` is what is already known of the water: a refill
    // that is owed is water that fell through the low reed.
    void begin(bool belowLow);

    // The move is called off.
    void end();

    // A flow reading, pulses over the last kFlowSampleMs, beside the carbonator's reeds.
    void sample(uint32_t pulses, const RefillReading &reeds);

    bool     moving() const;
    bool     flowing() const;    // something is leaving through the meter now
    bool     belowLow() const;   // the water has fallen through the low reed
    uint32_t pulses() const;     // counted since the move began

private:
    bool     moving_;
    bool     flowing_;
    bool     low_seen_;   // the low reed has read closed since the move began
    bool     below_;
    uint32_t pulses_;
    uint32_t quiet_;      // readings in a row with nothing counted
    uint32_t open_;       // readings in a row with neither reed closed, after the low one was
};

}  // namespace machine_policy
