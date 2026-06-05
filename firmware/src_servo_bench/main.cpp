// servo-bench: push a button, an MG90S servo toggles between 0 deg and a
// calibrated, true 90 deg. Throwaway bench rig — see README.md in this folder
// for wiring, calibration, and tear-down. Sibling of ../src_reed_bench/.
// Not production firmware.
//
//   Button: one leg -> GPIO 27, other leg -> GND  (internal pull-up; press=LOW)
//   Servo (MG90S 3-pin plug):
//     signal (orange) -> GPIO 13
//     V+     (red)    -> 5V
//     GND    (brown)  -> GND
//
// Each press toggles the servo and echoes the move (angle + the exact pulse
// width sent) to serial at 115200, so the console confirms what the servo did.

#include <Arduino.h>
#include <ESP32Servo.h>

static const int PIN_BUTTON = 27;  // momentary button to GND, INPUT_PULLUP
static const int PIN_SERVO  = 13;  // servo signal line

static const int ANGLE_A = 0;
static const int ANGLE_B = 90;

// ── Servo pulse-width calibration (this specific MG90S unit) ──────────────
// A hobby servo's shaft angle is set by the PWM pulse width via an internal
// feedback potentiometer — the motion is continuous, NOT quantized by gear
// teeth — but the pulse->angle endpoints drift from unit to unit. So instead
// of leaning on a generic 0-180 -> min/max mapping, we model the line
// explicitly and command the servo in microseconds:
//
//     pulse_us(angle) = CENTER_US + (angle - 90) * US_PER_DEG
//
// CENTER_US is the pulse that puts THIS servo's arm at a true, square 90 deg,
// tuned by eye against a square using the live pulse width each press logs
// (see README "Calibration"). Hobby servos cluster near a 1500 us center but
// vary per unit, so treat this as measured, not derived.
static const float CENTER_US  = 1600.0f;  // pulse at true 90 deg — tune to square
static const float US_PER_DEG = 10.56f;   // ~(2400-500)/180 slope; 2nd-order

static int pulseFor(int angle) {
  return (int)lroundf(CENTER_US + (angle - 90) * US_PER_DEG);
}

static const unsigned long DEBOUNCE_MS = 40;
static const unsigned long BEAT_MS = 10000;

Servo servo;
bool atB = false;             // which of the two angles we're parked at
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
  Serial.printf("calibration: 90 deg = %d us  (CENTER_US=%.0f, %.2f us/deg)\n",
                pulseFor(90), CENTER_US, US_PER_DEG);
  Serial.printf("press the button -> servo toggles %d <-> %d deg\n", ANGLE_A, ANGLE_B);
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
