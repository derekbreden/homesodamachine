#pragma once

// refill_store keeps one fact through a power cut: that the carbonator's water fell through
// its low reed and has not yet reached its high one. Below the low reed's window no reed is
// closed, so a board that restarts there has nothing else to tell it a refill is owed.

bool refillOwedLoad();
void refillOwedSave(bool owed);
