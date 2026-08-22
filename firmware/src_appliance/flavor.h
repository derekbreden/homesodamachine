#pragma once

#include <stdint.h>

// Controller-authoritative flavor selection. The faucet may render its cached
// value immediately at boot, but this state is what future dispense logic reads.
void flavorBegin();

// Performs a due Preferences write. Call only from a quiet, idle part of the
// main loop; returns true when persistence status changed.
bool flavorService();

// A first-ever controller adopts the faucet's saved candidate. Once a valid
// controller value exists, synchronization never overwrites it.
bool flavorSynchronize(uint8_t candidate);

// Absolute selection, never toggle. Returns false only for an invalid channel.
bool flavorSelect(uint8_t flavor);

uint8_t  flavorSelected();
bool     flavorEstablished();
bool     flavorPersisted();
bool     flavorPersistenceError();
uint32_t flavorRevision();
