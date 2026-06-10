#pragma once

#include <Arduino.h>
#include <Wire.h>

// AXS5106L capacitive touch controller (I2C) — Waveshare ESP32-S3-Touch-LCD-1.47.
//
// The chip raises INT (falling edge) for each touch report while a finger is
// down and reports nothing when idle, so "no interrupt since last poll" reads
// as released. Raw coordinates are in panel-native portrait space; begin()
// takes the display rotation and maps coordinates to match.

#define AXS5106L_ADDR            0x63
#define AXS5106L_ID_REG          0x08
#define AXS5106L_TOUCH_DATA_REG  0x01

class AXS5106L {
public:
  AXS5106L(int8_t rst_pin, int8_t int_pin);

  // wire must already be begin()'d on the touch I2C pins.
  // rotation/width/height follow the Arduino_GFX display they map onto.
  void begin(TwoWire &wire, uint8_t rotation, uint16_t width, uint16_t height);

  // True while a finger is down; fills x/y with display coordinates.
  bool getTouch(uint16_t *x, uint16_t *y);

  uint32_t intCount() const { return _intCount; }  // diagnostics

private:
  static void IRAM_ATTR isr(void *arg);
  bool readReg(uint8_t reg, uint8_t *data, uint8_t len);

  TwoWire *_wire = nullptr;
  int8_t _rst, _int;
  uint8_t _rotation = 0;
  uint16_t _width = 0, _height = 0;
  volatile bool _intFlag = false;
  volatile uint32_t _intCount = 0;
};
