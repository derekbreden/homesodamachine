// servo-bench: push a button, an MG90S servo sweeps a true 90 degrees of
// travel, then RELEASES (goes limp). Models actuating a quarter-turn valve:
// drive it to on/off, then let go — the valve holds its own position, so the
// servo never sits stalled against the valve's end stop (a sustained stall is
// heat, current, and wear), and it draws ~zero current between actuations.
// Throwaway bench rig — see README.md for wiring, calibration, and tear-down.
// Sibling of ../src_reed_bench/. Not production firmware.
//
//   Button: one leg -> GPIO 27, other leg -> GND  (internal pull-up; press=LOW)
//   Servo (MG90S 3-pin plug):
//     signal (orange) -> GPIO 13
//     V+     (red)    -> 5V
//     GND    (brown)  -> GND
//
// Each press drives to the next position and, after a settle delay, detaches.
// Both the move and the release are echoed to serial at 115200.

#include <Arduino.h>
#include <ESP32Servo.h>

static const int PIN_BUTTON = 27;  // momentary button to GND, INPUT_PULLUP
static const int PIN_SERVO  = 13;  // servo signal line

static const int ANGLE_A = 0;      // rest / valve "off"
static const int ANGLE_B = 90;     // actuated / valve "on" — 90 deg quarter turn

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
//              sets travel: span = (ANGLE_B - ANGLE_A) * US_PER_DEG. The generic
//              ~10.56 us/deg undershot badly here, so it's tuned up against the
//              observed arc (bracketed: a 950 us span fell short of 90, the old
//              1267 us span overshot).
// REST_US    — pulse at the rest angle. Sets only WHERE the sweep sits (absolute
//              orientation is irrelevant); any safe value, doesn't affect travel.
static const float US_PER_DEG = 12.32f;   // real us/deg — tune until travel = 90 deg
static const float REST_US    = 1000.0f;  // pulse at rest; sweep position only

static int pulseFor(int angle) {
  return (int)lroundf(REST_US + angle * US_PER_DEG);
}

// After commanding a move, keep the signal alive just long enough for the servo
// to physically arrive, then detach so it goes limp. SETTLE_MS must cover the
// worst-case travel time (an MG90S crosses ~90 deg in ~0.2 s unloaded; 500 ms is
// generous). Detach too early and it would stop mid-travel.
static const unsigned long SETTLE_MS   = 500;
static const unsigned long DEBOUNCE_MS = 40;
static const unsigned long BEAT_MS     = 10000;

Servo servo;
bool servoAttached = false;
bool detachPending = false;
unsigned long detachAt = 0;

bool atB = false;             // which of the two positions we last drove to
int lastAngle = ANGLE_A;
int lastButton = HIGH;        // pull-up idle reads HIGH
unsigned long lastEdgeMs = 0;
unsigned long lastBeatMs = 0;

// Attach (if needed), drive to the target, and schedule the release.
static void startMove(int angle) {
  if (!servoAttached) {
    servo.setPeriodHertz(50);             // 50 Hz analog-servo frame
    servo.attach(PIN_SERVO, 500, 2500);   // bounds for writeMicroseconds()
    servoAttached = true;
  }
  servo.writeMicroseconds(pulseFor(angle));
  lastAngle = angle;
  detachAt = millis() + SETTLE_MS;
  detachPending = true;
}

void setup() {
  Serial.begin(115200);
  delay(200);
  pinMode(PIN_BUTTON, INPUT_PULLUP);
  ESP32PWM::allocateTimer(0);

  Serial.println();
  Serial.println("=== servo-bench ===");
  Serial.printf("button: GPIO %d (to GND, internal pull-up)\n", PIN_BUTTON);
  Serial.printf("servo : GPIO %d signal | V+ to 5V | GND to GND\n", PIN_SERVO);
  Serial.printf("calibration: %d deg = %d us, %d deg = %d us (span %d us, %.2f us/deg)\n",
                ANGLE_A, pulseFor(ANGLE_A), ANGLE_B, pulseFor(ANGLE_B),
                pulseFor(ANGLE_B) - pulseFor(ANGLE_A), US_PER_DEG);
  Serial.printf("behavior: drive %d <-> %d deg, then release (limp) after %lu ms\n",
                ANGLE_A, ANGLE_B, SETTLE_MS);
  Serial.println("press the button to actuate — like turning a quarter-turn valve");

  startMove(ANGLE_A);  // drive to rest, then the loop releases it
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
      startMove(angle);
      Serial.printf("t=%lu ms  button -> drive to %d deg (%d us)\n",
                    millis(), angle, pulseFor(angle));
    }
  }

  // Release the servo once it's had time to reach the commanded position.
  if (detachPending && millis() >= detachAt) {
    servo.detach();
    // Detaching from the ESP32 LEDC peripheral can leave the signal pin stuck
    // HIGH — a continuously-high line is a garbage "pulse" the servo reads as a
    // command and actively drives to (a powered jerk, then it fights you), NOT
    // a clean release. Force a steady idle-LOW: no pulses = no command = the
    // servo de-energizes and truly goes limp.
    pinMode(PIN_SERVO, OUTPUT);
    digitalWrite(PIN_SERVO, LOW);
    servoAttached = false;
    detachPending = false;
    Serial.printf("t=%lu ms  released (limp) at %d deg — valve would hold itself\n",
                  millis(), lastAngle);
  }

  // Heartbeat: shows the board is alive and whether the servo is holding or limp.
  if (millis() - lastBeatMs > BEAT_MS) {
    lastBeatMs = millis();
    Serial.printf("t=%lu ms  alive, last move %d deg (%d us), servo %s\n",
                  millis(), lastAngle, pulseFor(lastAngle),
                  servoAttached ? "holding" : "released (limp)");
  }

  delay(5);
}
