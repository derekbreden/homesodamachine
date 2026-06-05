// reed-bench: print MCP23017 input state to the serial console as reeds open
// and close. Throwaway bench rig — see README.md in this folder for wiring,
// intent, and tear-down. Not production firmware.
//
//   ESP32 <-> MCP23017 (I2C):  3V3->VCC, GND->GND, GPIO21->SDA, GPIO22->SCL,
//     A0/A1/A2->GND (address 0x20), RESET->VCC.
//   Reeds:  signal -> an MCP23017 GPIO pin (PA0..),  common -> GND.
//     The chip's internal pull-ups are enabled, so no external resistors.
//
//   1 = reed open,  0 = reed closed (magnet near).

#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_MCP23X17.h>

static const uint8_t MCP_ADDR = 0x20;  // A0/A1/A2 -> GND

Adafruit_MCP23X17 mcp;
uint16_t lastState = 0xFFFF;

// Print one byte as 4_4 binary, MSB first: e.g. 1111_0000.
static void printBits8(uint8_t v) {
  for (int i = 7; i >= 0; i--) {
    Serial.print((v >> i) & 1);
    if (i == 4) Serial.print('_');
  }
}

void setup() {
  Serial.begin(115200);
  delay(200);
  Wire.begin();  // ESP32 default I2C: SDA=GPIO21, SCL=GPIO22

  // Retry forever until the MCP23017 ACKs its address. Never silently proceed.
  while (!mcp.begin_I2C(MCP_ADDR)) {
    Serial.printf("MCP23017 not found at 0x%02X — check wiring / A0-A2 jumpers."
                  " retrying...\n", MCP_ADDR);
    delay(1000);
  }

  // All 16 pins as inputs with the chip's internal weak pull-up enabled.
  for (uint8_t i = 0; i < 16; i++) mcp.pinMode(i, INPUT_PULLUP);

  Serial.println();
  Serial.println("=== reed-bench ===");
  Serial.printf("MCP23017 @ 0x%02X | I2C SDA=21 SCL=22 | serial 115200\n", MCP_ADDR);
  Serial.println("polling all 16 pins: PA0..PA7, PB0..PB7");
  Serial.println("legend: 1 = reed open, 0 = reed closed (magnet near)");

  lastState = mcp.readGPIOAB();  // low byte = port A, high byte = port B
  Serial.print("initial   PA=");
  printBits8(lastState & 0xFF);
  Serial.print("  PB=");
  printBits8(lastState >> 8);
  Serial.println();
}

void loop() {
  uint16_t state = mcp.readGPIOAB();
  if (state != lastState) {
    Serial.printf("t=%8.3f  PA=", millis() / 1000.0f);
    printBits8(state & 0xFF);
    Serial.print("  PB=");
    printBits8(state >> 8);

    // Tag every bit that flipped, and the direction it flipped.
    uint16_t diff = state ^ lastState;
    for (int i = 0; i < 16; i++) {
      if (diff & (1 << i)) {
        const char* port = i < 8 ? "PA" : "PB";
        int idx = i < 8 ? i : i - 8;
        Serial.printf("  %s%d:%d->%d", port, idx,
                      (lastState >> i) & 1, (state >> i) & 1);
      }
    }
    Serial.println();
    lastState = state;
  }
  delay(15);  // ~15 ms poll — reeds are slow and we don't want to flood serial
}
