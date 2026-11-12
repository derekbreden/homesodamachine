#pragma once

#include <stdint.h>

// refill_store keeps two facts through a power cut: that the carbonator's water fell through
// its low reed and has not yet reached its high one, and how much of the pumping ceiling has
// been spent on it. Below the low reed's window no reed is closed, so a board that restarts
// there has nothing else to tell it a refill is owed; and a ceiling that began again at every
// restart would not be one.
//
// It keeps a third for good: that this carbonator has been filled, which a refill ending at
// the high reed says. A board that was never part of a filled machine has no water to look
// after, and a start is where that matters (machine.cpp, "The water a start finds").

bool     refillOwedLoad();
void     refillOwedSave(bool owed);
uint32_t refillSpentLoad();
void     refillSpentSave(uint32_t spentMs);
bool     refillFilledLoad();
void     refillFilledSave(bool filled);
