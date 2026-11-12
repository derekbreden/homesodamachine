#pragma once

// sweep_store keeps one fact through a power cut: that the carbonator stood drained and open
// to the air, and its gas has not been swept out since. Nothing a sensor reads says so, and
// the first fill waits on it.

bool sweepOwedLoad();
void sweepOwedSave(bool owed);
