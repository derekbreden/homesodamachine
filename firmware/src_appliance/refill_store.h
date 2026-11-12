#pragma once

#include <stdint.h>

// refill_store keeps two facts through a power cut: that the carbonator's water fell through
// its low reed and has not yet reached its high one, and how much of the pumping ceiling has
// been spent on it. Below the low reed's window no reed is closed, so a board that restarts
// there has nothing else to tell it a refill is owed; and a ceiling that began again at every
// restart would not be one.

bool     refillOwedLoad();
void     refillOwedSave(bool owed);
uint32_t refillSpentLoad();
void     refillSpentSave(uint32_t spentMs);
