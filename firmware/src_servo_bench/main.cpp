// servo-bench: push a button, an MG90S servo moves. Throwaway bench rig —
// see README.md in this folder for wiring, intent, and tear-down. Sibling of
// ../src_reed_bench/ (same idea, different peripheral). Not production firmware.
//
//   Button: one leg -> GPIO 27, other leg -> GND  (internal pull-up; press=LOW)
//   Servo (MG90S 3-pin plug):
//     signal (orange) -> GPIO 13
//     V+     (red)    -> 5V
//     GND    (brown)  -> GND
//
// Each press toggles the servo between two angles and echoes the move to serial
// at 115200, so the console confirms what the servo did even if you look away.

#include <Arduino.h>
#include <ESP32Servo.h>

static const int PIN_BUTTON = 27;  // momentary button to GND, INPUT_PULLUP
static const int PIN_SERVO  = 13;  // servo signal line

static const int ANGLE_A = 0;
static const int ANGLE_B = 120;

static const unsigned long DEBOUNCE_MS = 40;
static const unsigned long BEAT_MS = 10000;

Servo servo;
bool atB = false;             // which of the two angles we're parked at
int lastButton = HIGH;        // pull-up idle reads HIGH
unsigned long lastEdgeMs = 0;
unsigned long lastBeatMs = 0;

void setup() {
  Serial.begin(115200);
  delay(200);
  pinMode(PIN_BUTTON, INPUT_PULLUP);

  ESP32PWM::allocateTimer(0);
  servo.setPeriodHertz(50);             // 50 Hz analog-servo frame
  servo.attach(PIN_SERVO, 500, 2400);   // MG90S pulse range ~500-2400 us
  servo.write(ANGLE_A);

  Serial.println();
  Serial.println("=== servo-bench ===");
  Serial.printf("button: GPIO %d (to GND, internal pull-up)\n", PIN_BUTTON);
  Serial.printf("servo : GPIO %d signal | V+ to 5V | GND to GND\n", PIN_SERVO);
  Serial.printf("press the button -> servo toggles %d <-> %d deg\n", ANGLE_A, ANGLE_B);
  Serial.printf("parked at %d deg\n", ANGLE_A);
}

void loop() {
  int b = digitalRead(PIN_BUTTON);

  // Accept a state change only once it's been stable past the debounce window.
  if (b != lastButton && (millis() - lastEdgeMs) > DEBOUNCE_MS) {
    lastEdgeMs = millis();
    lastButton = b;
    if (b == LOW) {  // pressed: pull-up line yanked to GND
      atB = !atB;
      int angle = atB ? ANGLE_B : ANGLE_A;
      servo.write(angle);
      Serial.printf("t=%lu ms  button -> servo %d deg\n", millis(), angle);
    }
  }

  // Heartbeat so the console shows the board is alive before you press anything.
  if (millis() - lastBeatMs > BEAT_MS) {
    lastBeatMs = millis();
    Serial.printf("t=%lu ms  alive, parked at %d deg, press the button\n",
                  millis(), atB ? ANGLE_B : ANGLE_A);
  }

  delay(5);
}
