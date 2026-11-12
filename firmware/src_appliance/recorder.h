#pragma once

#include <stdint.h>

#include "machine_log.h"

// recorder keeps the machine's record of what it did in the main board's spare flash: an
// entry queues in RAM when it happens and reaches the ring only while the machine is idle
// and quiet. machine.cpp notes; the console's `log` reads.

// After rtcBegin(), so the boot it notes carries the clock.
void recorderBegin();

// Every pass of the loop. `mayWrite` is false while anything runs or sounds: a flash write
// stalls the loop, and a sector erase stalls it for longer.
void recorderService(bool mayWrite);

void recorderNote(machine_log::Kind kind, uint8_t detail,
                  uint32_t a = 0, uint32_t b = 0, int16_t d = 0, int16_t e = 0);

// True once nothing is waiting to be written, or there is no ring to write it to.
bool recorderSettled();

// The newest `count` entries, oldest first, a line a pass so the loop keeps turning.
void recorderPrint(uint32_t count);

// Where the ring stands: its size, the next entry's number, what is waiting and what was lost.
void recorderReport();
