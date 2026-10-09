#pragma once

// Host declarations only. The integration suite supplies all definitions;
// no serial device, GPIO, interrupt or PWM peripheral is opened.
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

#define IRAM_ATTR

enum {
    LOW = 0, HIGH = 1, INPUT = 2, OUTPUT = 3,
    INPUT_PULLUP = 4, INPUT_PULLDOWN = 5, FALLING = 6,
};

unsigned long millis();
void pinMode(int pin, int mode);
void digitalWrite(int pin, int value);
uint32_t analogReadMilliVolts(int pin);
bool ledcAttach(int pin, uint32_t hz, uint8_t bits);
bool ledcWrite(int pin, uint32_t duty);
bool ledcDetach(int pin);
void noInterrupts();
void interrupts();
int digitalPinToInterrupt(int pin);
void attachInterrupt(int pin, void (*handler)(), int mode);

struct HostSerial {
    void println(const char *) {}
    void printf(const char *, ...) {}
};
extern HostSerial Serial;
