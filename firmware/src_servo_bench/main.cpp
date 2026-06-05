// servo-bench: push a button, an MG90S servo sweeps a true 90 degrees of
// travel and back. Throwaway bench rig — see README.md in this folder for
// wiring, calibration, and tear-down. Sibling of ../src_reed_bench/.
// Not production firmware.
//
//   Button: one leg -> GPIO 27, other leg -> GND  (internal pull-up; press=LOW)
//   Servo (MG90S 3-pin plug):
//     signal (orange) -> GPIO 13
//     V+     (red)    -> 5V
//     GND    (brown)  -> GND
//
// Each press toggles the servo and echoes the angle + the exact pulse width
// sent to serial at 115200, so the console confirms what the servo did.

#include <Arduino.h>
#include <ESP32Servo.h>

static const int PIN_BUTTON = 27;  // momentary button to GND, INPUT_PULLUP
static const int PIN_SERVO  = 13;  // servo signal line

static const int ANGLE_A = 0;      // rest angle
static const int ANGLE_B = 90;     // actuated angle — 90 deg of travel from rest

// ── Servo travel calibration (this specific MG90S unit) ───────────────────
// What's calibrated here is the TRAVEL between the two positions — a true
// 90 deg of swept arc — not where either endpoint points in absolute space.
// A hobby servo's shaft angle is a linear function of PWM pulse width
// (continuous, NOT stepped by gear teeth), so we anchor a rest pulse and add a
// per-degree slope, then command the servo in microseconds:
//
//     pulse_us(angle) = REST_US + angle * US_PER_DEG
//
// US_PER_DEG — the servo's REAL microseconds per degree, and the one knob that
//              sets travel: span = (ANGLE_B - ANGLE_A) * US_PER_DEG. It must
//              equal the real slope for commanded degrees to equal swept
//              degrees. The generic ~10.56 us/deg (a 500-2400 us / 180 deg
//              datasheet span) undershoots badly here — 90 deg commanded sweeps
//              visibly less than 90 — so it is tuned up against the observed
//              arc. Bracketed: a 950 us span fell short of 90, the old 1267 us
//              span overshot it, so the true value sits between.
// REST_US    — pulse at the rest angle. Sets only WHERE the sweep sits (absolute
//              orientation is irrelevant here); any safe value works, and it
//              does not affect the amount of travel.
static const float US_PER_DEG = 12.32f;   // real us/deg — tune until travel = 90 deg
static const float REST_US    = 1000.0f;  // pulse at rest; sweep position only

static int pulseFor(int angle) {
  return (int)lroundf(REST_US + angle * US_PER_DEG);
}

static const unsigned long DEBOUNCE_MS = 40;
static const unsigned long BEAT_MS = 10000;

Servo servo;
bool atB = false;             // which of the two positions we're parked at
int lastButton = HIGH;        // pull-up idle reads HIGH
unsigned long lastEdgeMs = 0;
unsigned long lastBeatMs = 0;

static void moveTo(int angle) {
  servo.writeMicroseconds(pulseFor(angle));
}

void setup() {
  Serial.begin(115200);
  delay(200);
  pinMode(PIN_BUTTON, INPUT_PULLUP);

  ESP32PWM::allocateTimer(0);
  servo.setPeriodHertz(50);             // 50 Hz analog-servo frame
  servo.attach(PIN_SERVO, 500, 2500);   // bounds for writeMicroseconds()
  moveTo(ANGLE_A);

  Serial.println();
  Serial.println("=== servo-bench ===");
  Serial.printf("button: GPIO %d (to GND, internal pull-up)\n", PIN_BUTTON);
  Serial.printf("servo : GPIO %d signal | V+ to 5V | GND to GND\n", PIN_SERVO);
  Serial.printf("calibration: %d deg = %d us, %d deg = %d us (span %d us, %.2f us/deg)\n",
                ANGLE_A, pulseFor(ANGLE_A), ANGLE_B, pulseFor(ANGLE_B),
                pulseFor(ANGLE_B) - pulseFor(ANGLE_A), US_PER_DEG);
  Serial.printf("press the button -> servo sweeps %d <-> %d deg of travel\n", ANGLE_A, ANGLE_B);
  Serial.printf("parked at %d deg (%d us)\n", ANGLE_A, pulseFor(ANGLE_A));
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
      moveTo(angle);
      Serial.printf("t=%lu ms  button -> servo %d deg (%d us)\n",
                    millis(), angle, pulseFor(angle));
    }
  }

  // Heartbeat so the console shows the board is alive before you press anything.
  if (millis() - lastBeatMs > BEAT_MS) {
    lastBeatMs = millis();
    int parked = atB ? ANGLE_B : ANGLE_A;
    Serial.printf("t=%lu ms  alive, parked at %d deg (%d us), press the button\n",
                  millis(), parked, pulseFor(parked));
  }

  delay(5);
}
