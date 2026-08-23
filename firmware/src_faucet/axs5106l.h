#pragma once

#include <Arduino.h>
#include <Wire.h>

// AXS5106L capacitive touch controller (I2C) — Waveshare ESP32-S3-Touch-LCD-1.47.
//
// INT means that a new touch report is ready; it is not the duration of a
// finger contact. A finger can remain down between reports, so getTouch()
// retains the last confirmed contact and refreshes the controller while one is
// active. Raw coordinates are in panel-native portrait space; begin() takes
// the display rotation and maps coordinates to match.

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
  void mapPoint(const uint8_t *data, uint16_t *x, uint16_t *y);

  TwoWire *_wire = nullptr;
  int8_t _rst, _int;
  uint8_t _rotation = 0;
  uint16_t _width = 0, _height = 0;
  volatile bool _intFlag = false;
  volatile uint32_t _intCount = 0;
  bool _touchDown = false;
  uint16_t _lastX = 0, _lastY = 0;
  uint32_t _lastSampleMs = 0;
  uint32_t _lastContactMs = 0;

  // The controller's reports are state updates rather than a continuous
  // pressed signal. Polling at this modest cadence makes a held pad stay held
  // even when an interrupt arrives only for a changed contact. A bus fault
  // may extend an active prime by at most this short grace interval.
  static constexpr uint32_t kActivePollMs = 12;
  static constexpr uint32_t kReadFailureReleaseMs = 48;
};
