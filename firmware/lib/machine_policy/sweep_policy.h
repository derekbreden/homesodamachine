#pragma once

#include <stdint.h>

#include "pour_policy.h"
#include "refill_policy.h"

// ── The sweep ─────────────────────────────────────────────────────────────
// A carbonator that was drained and opened holds air. A fill squeezes that air into the
// headspace, where it stands in for CO2 the feed would have put there and leaves only
// dissolved in what is poured. Nothing on the board lets gas out of the tank: the one way
// out is the faucet, through the bottom port the water leaves by, and only while no water
// covers that port. So the air goes before the water comes. With the tank dry and the
// cylinder open, the lever at the faucet lets CO2 through the tank and out, and the air
// leaves with it.
//
// The meter stands on that line, at the tank's outlet. Its pulses while a sweep is owed
// are gas, and they are the only evidence the board has that the cylinder is open and the
// lever is down. The meter counts volume at the tank's own pressure, so its pulses measure
// the sweep in tank volumes whatever that pressure settles at. The lever let go pauses the
// count, and the count is kept until the sweep is done.
//
// What the meter makes of gas is not known until a carbonator is wet. A hand is holding the
// lever down for as long as this takes, so time with gas moving ends the sweep too: a meter
// that turns slowly on gas costs that hand a bounded hold and no more.
//
// The count reaching its target is the moment to say so, and the lever is still down. A fill
// begun then would send its first water out of the open faucet, so the sweep stays owed
// until the meter has gone quiet: the hand has let go.
//
// machine.cpp keeps `owed` in flash, holds the refill and the pour while it stands, and
// asks for the first fill when the lever is let go. A reed that stays closed says the tank
// holds water, which a sweep cannot work through, and the sweep is dropped.
namespace machine_policy {

// The meter's pulses for a litre through it, and what the dry carbonator holds.
constexpr uint32_t kSweepPulsesPerLitre = 2280;
constexpr uint32_t kSweepTankMl         = 1526;

// The gas a sweep passes through the tank, in tenths of the tank's volume.
constexpr uint32_t kSweepTankVolumesX10 = 25;

constexpr uint32_t kSweepTargetPulses =
    kSweepPulsesPerLitre * kSweepTankMl / 1000 * kSweepTankVolumesX10 / 10;

// Time with gas moving that ends the sweep whatever the meter has counted.
constexpr uint32_t kSweepCeilingMs      = 30000;
constexpr uint32_t kSweepCeilingSamples = kSweepCeilingMs / kFlowSampleMs;

// Readings in a row with nothing counted before the gas is taken to have stopped.
constexpr uint32_t kSweepQuietSamples = 4;

// How long the meter stays quiet after the target before the lever is taken to be let go.
constexpr uint32_t kSweepReleaseMs      = 1000;
constexpr uint32_t kSweepReleaseSamples = kSweepReleaseMs / kFlowSampleMs;

// How long a carbonator reed stays closed before the tank is believed to hold water.
constexpr uint32_t kSweepWetMs      = 3000;
constexpr uint32_t kSweepWetSamples = kSweepWetMs / kFlowSampleMs;

enum class SweepState : uint8_t {
    Clear = 0,   // no sweep is owed
    Owed,        // waiting for gas
    Flowing,     // gas is moving through the tank
    Releasing,   // the target is met and the lever is still down
};

enum class SweepAction : uint8_t {
    None = 0,
    Began,      // gas started moving
    Paused,     // it stopped short of the target
    Done,       // the target is met
    Released,   // the lever is let go and the sweep is no longer owed
    Moot,       // the tank holds water and the sweep is dropped
};

class Sweep {
public:
    Sweep();

    // A dry tank that has stood open to the air. The count starts from nothing.
    void owe();

    // The sweep is given up, and its count with it.
    void clear();

    // A flow reading, pulses over the last kFlowSampleMs, beside the carbonator's reeds.
    SweepAction sample(uint32_t pulses, const RefillReading &reeds);

    SweepState  state() const;
    const char *stateName() const;
    bool        owed() const;      // from owe() until the lever is let go, the tank is found wet, or clear()
    bool        flowing() const;   // gas is moving and the count is short of its target
    bool        done() const;      // the target is met and the lever is still down
    uint32_t    pulses() const;    // counted in the sweep that is owed, or the one that just ended
    uint32_t    flowedMs() const;  // time with gas moving in that sweep
    uint8_t     percent() const;   // of the count's target or the time's, whichever is further on

private:
    SweepState state_;
    uint32_t   pulses_;
    uint32_t   flowed_;   // readings with gas moving
    uint32_t   quiet_;
    uint32_t   wet_;
};

}  // namespace machine_policy
