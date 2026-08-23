#include "axs5106l.h"

AXS5106L::AXS5106L(int8_t rst_pin, int8_t int_pin)
    : _rst(rst_pin), _int(int_pin) {}

void IRAM_ATTR AXS5106L::isr(void *arg) {
  AXS5106L *self = (AXS5106L *)arg;
  self->_intFlag = true;
  self->_intCount = self->_intCount + 1;
}

bool AXS5106L::readReg(uint8_t reg, uint8_t *data, uint8_t len) {
  _wire->beginTransmission(AXS5106L_ADDR);
  _wire->write(reg);
  if (_wire->endTransmission() != 0) return false;
  if (_wire->requestFrom((uint8_t)AXS5106L_ADDR, len) != len) return false;
  _wire->readBytes(data, len);
  return true;
}

void AXS5106L::begin(TwoWire &wire, uint8_t rotation, uint16_t width, uint16_t height) {
  _wire = &wire;
  _rotation = rotation;
  _width = width;
  _height = height;
  _intFlag = false;
  _touchDown = false;
  _lastSampleMs = 0;
  _lastContactMs = 0;

  pinMode(_rst, OUTPUT);
  digitalWrite(_rst, LOW);
  delay(200);
  digitalWrite(_rst, HIGH);
  delay(300);

  attachInterruptArg(digitalPinToInterrupt(_int), isr, this, FALLING);

  uint8_t id[3] = {0};
  if (readReg(AXS5106L_ID_REG, id, 3)) {
    Serial.printf("AXS5106L id: %02X %02X %02X\n", id[0], id[1], id[2]);
  } else {
    Serial.println("AXS5106L: ID read failed (I2C)");
  }
}

void AXS5106L::mapPoint(const uint8_t *data, uint16_t *x, uint16_t *y) {
  uint16_t rawX = (((uint16_t)(data[2] & 0x0F)) << 8) | data[3];
  uint16_t rawY = (((uint16_t)(data[4] & 0x0F)) << 8) | data[5];

  switch (_rotation) {
    case 1:
      *x = rawY;
      *y = rawX;
      break;
    case 2:
      *x = rawX;
      *y = _height - 1 - rawY;
      break;
    case 3:
      *x = _width - 1 - rawY;
      *y = _height - 1 - rawX;
      break;
    default:
      *x = _width - 1 - rawX;
      *y = rawY;
      break;
  }
}

bool AXS5106L::getTouch(uint16_t *x, uint16_t *y) {
  const uint32_t now = millis();
  const bool reportPending = _intFlag;
  if (reportPending) _intFlag = false;

  // AXS5106L reports current touch state through the same registers after the
  // initial interrupt. If we treated each quiet poll as a release, LVGL would
  // turn a physical hold into rapid press/release pairs.
  const bool refreshActive = _touchDown &&
      static_cast<uint32_t>(now - _lastSampleMs) >= kActivePollMs;
  if (reportPending || refreshActive) {
    uint8_t data[14] = {0};  // [?, count, then 6 bytes per point x2]
    if (readReg(AXS5106L_TOUCH_DATA_REG, data, sizeof(data))) {
      _lastSampleMs = now;
      if (data[1] == 0) {
        // An explicit empty contact list is a release and stops prime now.
        _touchDown = false;
      } else {
        mapPoint(data, &_lastX, &_lastY);
        _lastContactMs = now;
        _touchDown = true;
      }
    } else if (_touchDown &&
               static_cast<uint32_t>(now - _lastContactMs) >= kReadFailureReleaseMs) {
      // Never let a stale cached contact run the pump after the touch bus has
      // stopped providing trustworthy state.
      _touchDown = false;
    }
  }

  if (!_touchDown) return false;
  *x = _lastX;
  *y = _lastY;
  return true;
}
