#pragma once

#include <stdint.h>

// ════════════════════════════════════════════════════════════
//  U6 — DS3231SN, on the I2C bus at 0x68
// ════════════════════════════════════════════════════════════
//
// The main board carries a TCXO clock and a CR2032 (BT1) to run it through a power
// cut, which is what lets quiet hours mean anything. This is the whole of what
// the appliance needs from it: what hour is it, and is that answer trustworthy.
//
// Trustworthy is the point. OSF (status bit 7) latches whenever the oscillator
// has stopped since it was last cleared — a dead coin cell, a first power-up, a
// board that sat in a box. While OSF is set the time is garbage, so rtcHour()
// answers -1 and quiet hours stay off rather than engaging at the wrong hour.

void rtcBegin();

// 0..23, or -1 when the RTC is absent, unset, or has lost its oscillator.
// Cached — the bus is read every RTC_REFRESH_MS, not on every call.
int  rtcHour();

bool rtcPresent();
bool rtcValid();      // present, answering, and OSF clear

// "2026-08-19 14:32:05", or "unset" — into a caller's buffer.
void rtcStamp(char *out, size_t n);

// Sets the clock, clears OSF, and clears EOSC so the oscillator runs on battery.
bool rtcSet(int year, int mon, int day, int hour, int min, int sec);

// Die temperature off the TCXO's own sensor — proof the oscillator block is powered.
bool rtcTemp(float *outC);
