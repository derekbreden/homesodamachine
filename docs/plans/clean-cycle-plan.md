---
name: Clean Cycle Plan
description: Clean cycle firmware (ESP32 state machine), S3 UI, and iOS UI — covers hardware wiring, command protocol, state machine, and UI across all three platforms
type: project
---

# Clean Cycle Plan

## Context

The clean cycle lets the user flush a flavor line with tap water when switching flavorings. Each flavor line is independent — you can clean one without emptying the other. The plumbing layout, parts, and physical design are already documented in `docs/plumbing.md` and `plumbing_details.md` in memory.

## Current GPIO Map

| GPIO | Use |
|------|-----|
| 33, 25, 26 | L298N A: pump 1 (ENA, IN1, IN2) |
| 12 | L298N A: dispensing solenoid 1 (ENB, direction hardwired) |
| 19, 18, 5 | L298N B: pump 2 (ENA, IN1, IN2) |
| 4 | L298N B: dispensing solenoid 2 (ENB, direction hardwired) |
| 13 | Flavor switch (air switch, latching toggle) |
| 22 | Prime button (momentary) |
| 23 | Flow meter pulse input |
| 32, 35 | UART to RP2040 (TX, RX) |
| 15, 34 | UART to ESP32-S3 (TX, RX) |
| 1, 3 | USB serial (TX0, RX0) |

**Free output-capable GPIOs:** 14, 16, 17, 21, 27 (plus 2, 0 which have boot-strap concerns)

## Hardware: L298N Board #3 (Clean Solenoids)

- Power: 12V and GND from same supply as existing L298N boards
- Hardwire IN1 → 5V, IN2 → GND (Channel A direction fixed)
- Hardwire IN3 → 5V, IN4 → GND (Channel B direction fixed)
- **Channel A ENA → ESP32 GPIO 27 = clean solenoid flavor 1**
- **Channel B ENB → ESP32 GPIO 17 = clean solenoid flavor 2**
- Only 2 signal wires from ESP32 to this board (plus shared power/ground)

**Why GPIO 27 and 17:** Both are standard output GPIOs with no boot-strap restrictions and no I2C conflict. GPIO 21 (I2C SDA) and 22 (I2C SCL) are kept available for a potential RTC module. GPIO 2 is avoided as a boot-strap pin.

## Design Decisions

**Per-flavor, not both-at-once.** Each flavor line is independent. The user picks which flavor to clean. This avoids edge cases (what if one bag is full and the other is empty?) and matches the physical design (independent solenoids, independent tees).

**Multi-cycle with tunable count.** One `CLEAN:n` command runs multiple fill+flush cycles automatically. The number of cycles, fill duration, and flush duration are all `#define` constants — tuning parameters to be dialed in through experimentation with the real hardware. Starting values are guesses.

**Dispensing is locked during clean.** The pump state machine must not run while a clean cycle is active on that flavor. The other flavor can still dispense normally. If the air switch is set to the flavor being cleaned, dispensing is blocked entirely.

**Timing constants (all tunable):**
- `CLEAN_CYCLES`: 3 (number of fill+flush cycles per clean command)
- `CLEAN_FILL_MS`: 10000 (10 seconds — needle valve trickle fills the platypus bag)
- `CLEAN_FLUSH_MS`: 15000 (15 seconds — pump empties the bag through the dispensing point)
- All three are starting guesses. Adjust after real-world testing.

## Command Protocol

| Command | Direction | Meaning |
|---------|-----------|---------|
| `CLEAN:1` | iOS/S3 → ESP32 | Start clean cycle (multiple fill+flush rounds) on flavor 1 |
| `CLEAN:2` | iOS/S3 → ESP32 | Start clean cycle (multiple fill+flush rounds) on flavor 2 |
| `CLEAN_ABORT` | iOS/S3 → ESP32 | Abort in-progress clean cycle immediately |

| Response | Direction | Meaning |
|----------|-----------|---------|
| `CLEAN:FILLING:n:c/t` | ESP32 → iOS/S3 | Fill phase started for flavor n, cycle c of t |
| `CLEAN:FLUSHING:n:c/t` | ESP32 → iOS/S3 | Flush phase started for flavor n, cycle c of t |
| `OK:CLEAN:n` | ESP32 → iOS/S3 | All cycles complete for flavor n |
| `OK:CLEAN_ABORT` | ESP32 → iOS/S3 | Abort acknowledged, solenoids/pump off |
| `ERR:CLEAN_BUSY` | ESP32 → iOS/S3 | Already cleaning (reject second CLEAN command) |
| `ERR:CLEAN_INVALID` | ESP32 → iOS/S3 | Bad flavor number |

## ESP32 Firmware (Commit 1)

**File: `src/main.cpp`**

1. **Add clean solenoid pin definitions:**
   ```cpp
   #define CLEAN_SOL1_PIN 27   // clean solenoid flavor 1, L298N #3 Channel A ENA
   #define CLEAN_SOL2_PIN 17   // clean solenoid flavor 2, L298N #3 Channel B ENB
   ```
   `pinMode` as OUTPUT in `setup()`, `digitalWrite LOW` (solenoids closed by default)

2. **Clean cycle state variables:**
   ```cpp
   enum CleanState { CLEAN_IDLE, CLEAN_FILLING, CLEAN_FLUSHING };
   CleanState cleanState = CLEAN_IDLE;
   uint8_t    cleanFlavor = 0;        // 0 or 1 (index into flavors[])
   uint8_t    cleanCycle  = 0;        // current cycle (0-based)
   unsigned long cleanPhaseStart = 0;

   #define CLEAN_CYCLES     3      // number of fill+flush rounds
   #define CLEAN_FILL_MS   10000   // 10 seconds fill
   #define CLEAN_FLUSH_MS  15000   // 15 seconds flush
   ```

3. **`processConfigCommand()` additions:**
   ```cpp
   } else if (strncmp(cmd, "CLEAN:", 6) == 0) {
     int flav = atoi(cmd + 6);   // 1 or 2
     if (flav < 1 || flav > 2) {
       out.printf("ERR:CLEAN_INVALID\n");
     } else if (cleanState != CLEAN_IDLE) {
       out.printf("ERR:CLEAN_BUSY\n");
     } else {
       cleanFlavor = flav - 1;
       cleanCycle = 0;
       startCleanFill(out);
     }
   } else if (strcmp(cmd, "CLEAN_ABORT") == 0) {
     abortClean(out);
   }
   ```

4. **Clean cycle functions:**
   - `startCleanFill(Stream &out)`: close dispensing solenoid, open clean solenoid, pump off, set state to CLEAN_FILLING, record `cleanPhaseStart = millis()`, send `CLEAN:FILLING:n:c/t`
   - `startCleanFlush(Stream &out)`: close clean solenoid, open dispensing solenoid, pump on at full speed, set state to CLEAN_FLUSHING, record `cleanPhaseStart = millis()`, send `CLEAN:FLUSHING:n:c/t`
   - `finishClean(Stream &out)`: pump off, dispensing solenoid off, clean solenoid off (all safe), set state to CLEAN_IDLE, send `OK:CLEAN:n`
   - `abortClean(Stream &out)`: same as finishClean but sends `OK:CLEAN_ABORT`

5. **Main loop integration:**
   - Add a clean cycle check block (runs every loop iteration when `cleanState != CLEAN_IDLE`):
     ```cpp
     if (cleanState == CLEAN_FILLING && (now - cleanPhaseStart >= CLEAN_FILL_MS)) {
       startCleanFlush(Serial);  // transition to flush
     } else if (cleanState == CLEAN_FLUSHING && (now - cleanPhaseStart >= CLEAN_FLUSH_MS)) {
       cleanCycle++;
       if (cleanCycle < CLEAN_CYCLES) {
         startCleanFill(Serial);   // next cycle
       } else {
         finishClean(Serial);      // all cycles done
       }
     }
     ```
   - **Interlock with pump state machine:** At the top of the pump/valve control section, check:
     ```cpp
     bool cleaningActiveFlavor = (cleanState != CLEAN_IDLE && cleanFlavor == activeFlavor);
     ```
     If true, skip pump state machine and valve control entirely (don't open dispensing solenoid, don't run pump). The clean cycle controls those directly.
   - If the other flavor is active and not being cleaned, it dispenses normally.

6. **Response routing:** Broadcast status to both Serial and stS3. Keep it simple — USB debug output is always useful, and the S3 forwards to BLE automatically.

## S3 Config Display (Commit 2)

**File: `src_config/main.cpp`**

1. **Add to settings menu:**
   ```cpp
   enum SettingsItem { SET_BACK, SET_FACTORY_RESET, SET_CLEAN_CYCLE, SET_ABOUT, SETTINGS_COUNT };
   const char* settingsLabels[] = { "Back", "Factory Reset", "Clean Cycle", "About" };
   ```

2. **Clean cycle sub-page (new state):**
   - Tapping "Clean Cycle" enters a flavor selection view (not a confirmation dialog):
     - "Flavor 1" / "Flavor 2" / "Back"
     - Encoder rotates selection, tap confirms
   - After selecting a flavor, show confirmation: "Clean Flavor 1?" → Yes / No (like factory reset)
   - On Yes: send `CLEAN:1` (or `CLEAN:2`) via `stSendText(stLink, "CLEAN:1")`
   - Show "Filling... (1/3)" (blue text) while `CLEAN:FILLING:n:c/t` is active
   - Show "Flushing... (1/3)" (blue text) when `CLEAN:FLUSHING:n:c/t` received
   - On `OK:CLEAN:n`: show "Done" briefly, return to clean cycle sub-page (user can run again)
   - Encoder locked during active cycle (like factory reset)
   - Long-press or tap during cycle sends `CLEAN_ABORT` (provide an escape hatch)

3. **Response handling in `processTextLine()`:**
   ```cpp
   } else if (strncmp(line, "CLEAN:FILLING:", 14) == 0) {
     cleanPhase = 1;
     parseCleanProgress(line + 14);
     drawScreen();
   } else if (strncmp(line, "CLEAN:FLUSHING:", 15) == 0) {
     cleanPhase = 2;
     parseCleanProgress(line + 15);
     drawScreen();
   } else if (strncmp(line, "OK:CLEAN:", 9) == 0) {
     cleanPending = false;
     cleanPhase = 0;
     drawScreen();
   } else if (strcmp(line, "OK:CLEAN_ABORT") == 0) {
     cleanPending = false;
     cleanPhase = 0;
     drawScreen();
   }
   ```

## iOS App (Commit 3)

**File: `ios/SodaMachine/SodaMachine/BLE/BLEManager.swift`**

1. **Add observable state:**
   ```swift
   var cleanCycleActive = false
   var cleanCyclePhase: String? = nil   // "Filling... (1/3)", "Flushing... (2/3)", nil
   var cleanCycleCompleted = false
   ```

2. **Add methods:**
   ```swift
   func startCleanCycle(flavor: Int) {
     if demoMode {
       // Simulate: set phase to filling, delay, flushing, delay, completed
       return
     }
     cleanCycleActive = true
     cleanCyclePhase = "Filling..."
     send("CLEAN:\(flavor)")
   }

   func abortCleanCycle() {
     send("CLEAN_ABORT")
   }
   ```

3. **Response handling in `handleTextResponse()`:**
   ```swift
   } else if text.hasPrefix("CLEAN:FILLING:") {
     let progress = parseCleanProgress(text)
     cleanCyclePhase = "Filling... \(progress)"
   } else if text.hasPrefix("CLEAN:FLUSHING:") {
     let progress = parseCleanProgress(text)
     cleanCyclePhase = "Flushing... \(progress)"
   } else if text.hasPrefix("OK:CLEAN:") {
     cleanCycleActive = false
     cleanCyclePhase = nil
     cleanCycleCompleted = true
   } else if text == "OK:CLEAN_ABORT" {
     cleanCycleActive = false
     cleanCyclePhase = nil
   }
   ```

**File: `ios/SodaMachine/SodaMachine/Views/ConfigView.swift`**

4. **Add "Clean Cycle" to SettingsPageView:**
   - New button in the settings list: `settingsButton("Clean Cycle") { showCleanSheet = true }`
   - Tapping presents a sheet with:
     - Two buttons: "Clean Flavor 1" / "Clean Flavor 2"
     - Tapping either shows confirmation alert: "Clean Flavor 1?" with "Start" / "Cancel"
     - On confirm: call `ble.startCleanCycle(flavor: 1)`
     - Sheet content changes to progress view: phase text + spinner + "Abort" button
     - On completion: show "Done!" briefly, then reset to flavor selection
   - Sheet is better than alerts for this multi-step flow (selection + progress + abort in one place)

**Demo mode:** `startCleanCycle` in demo mode simulates with `DispatchQueue.main.asyncAfter` — loops through cycles with short delays, sets `cleanCycleCompleted = true` at end.

## Commit Sequence

1. **ESP32 clean cycle state machine** — pin defs, `CLEAN:n` / `CLEAN_ABORT` commands, multi-cycle fill/flush with tunable constants, pump interlock. Test via USB serial commands.
2. **S3 clean cycle UI** — settings sub-page with flavor selection, confirmation, progress display, abort.
3. **iOS clean cycle UI** — settings sheet with flavor selection, progress, abort, demo mode simulation.

## Open Questions (resolve during implementation)

1. **Tuning constants.** `CLEAN_CYCLES` (3), `CLEAN_FILL_MS` (10s), `CLEAN_FLUSH_MS` (15s) are all starting guesses. Needle valve setting determines actual fill rate. All three need real-world testing with the hardware connected.
2. **Pump speed during flush.** Full speed (255) seems right — we want to empty the bag completely. But if the bag overfills during the fill phase, high pump speed might cause pressure issues at zip-tie joints. Monitor during testing.
3. **Broadcast vs. targeted responses.** Plan says broadcast status to both Serial and S3. If this causes issues (e.g., S3 processing responses it didn't initiate), narrow to targeted delivery.
