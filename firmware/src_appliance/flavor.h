#pragma once

#include <stdint.h>

// Main-board-authoritative flavor selection. The faucet may render its cached
// value immediately at boot, but this state is what future dispense logic reads.
void flavorBegin();

// Performs a due Preferences write. Call only from a quiet, idle part of the
// main loop; returns true when persistence status changed.
bool flavorService();

// A first-ever main board adopts the faucet's saved candidate. Once a valid
// main board value exists, synchronization never overwrites it.
bool flavorSynchronize(uint8_t candidate);

// Absolute selection, never toggle. Returns false only for an invalid channel.
bool flavorSelect(uint8_t flavor);

uint8_t  flavorSelected();
bool     flavorEstablished();
bool     flavorPersisted();
bool     flavorPersistenceError();
uint32_t flavorRevision();

// Which logo a channel wears, and the pair as a whole. A set naming a logo no
// image carries artwork for is refused rather than clamped.
uint8_t flavorArt(uint8_t channel);
bool    flavorArtSet(uint8_t a0, uint8_t a1);

// What a channel pours at — 1:ratio, water to concentrate — held and
// persisted beside the selection. A set outside FLAVOR_RATIO_MIN..MAX is
// refused rather than clamped.
uint8_t flavorRatio(uint8_t channel);
bool    flavorRatioSet(uint8_t r0, uint8_t r1);
