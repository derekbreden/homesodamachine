#pragma once

// The bench consoles share the drive pins, park behavior and timing that operate a head on J13.
#include <Arduino.h>

static const int PIN_PUMP_A = 17;        // U11.IN1 -> OUT1/OUT2 -> J13.AM1 / J13.AM2
static const int PIN_PUMP_B = 4;         // U12.IN1 -> OUT1/OUT2 -> J13.BM1 / J13.BM2
static const int PUMP_PWM_HZ   = 20000;  // above hearing — every sound in the room is mechanical
static const int PUMP_PWM_BITS = 8;      // ledcWrite(255) is a true 100%: the core maps it to full-on
static const int PUMP_MAX_S    = 60;     // ceiling on a held run, whatever the command asks for

struct Pump { const char *who; int pin; const char *driver; const char *j13; int mark; };
extern const Pump kPump[2];

static constexpr char kDoseUsage[] = "dose <a|b> <duty_pct> <on_ms> <off_ms> <count>";

void pumpPark(int pin);
bool pumpSet(int pin, int percent);
bool pumpKey();
bool isDoseCommand(const String &line);
void cmdDose(const String &line, char terminator, bool primeActive);
