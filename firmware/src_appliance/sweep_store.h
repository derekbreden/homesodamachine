#pragma once

// sweep_store keeps two facts through a power cut. One is that the carbonator stood drained
// and open to the air, and its gas has not been swept out since: nothing a sensor reads says
// so, and the first fill waits on it. The other is that the machine was moving, told so before
// its plug came out: the board that starts with it kept takes the first for true.

bool sweepOwedLoad();
void sweepOwedSave(bool owed);
bool sweepMovingLoad();
void sweepMovingSave(bool moving);
