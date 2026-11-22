// The USB calibration console times J13 motor pulses while the rig measures liquid delivery.
#include <Arduino.h>
#include "pump_dose.h"

static void identify() {
    Serial.printf("PUMP_CALIBRATION state=idle sketch_bytes=%lu sketch_md5=%s\n",
                  (unsigned long)ESP.getSketchSize(), ESP.getSketchMD5().c_str());
}

void setup() {
    for (const Pump &pump : kPump) pinMode(pump.pin, INPUT);
    Serial.begin(115200);
    identify();
}

void loop() {
    static char buffer[96];
    static size_t used = 0;
    static bool invalid = false;
    while (Serial.available()) {
        const char c = Serial.read();
        if (c == '\r' || c == '\n') {
            buffer[used] = '\0';
            String line(buffer);
            line.trim();
            if (invalid) Serial.println("DOSE_ERROR reason=invalid_line");
            else if (isDoseCommand(line)) cmdDose(line, c, false);
            else if (line == "info" || line == "status" || line == "stop") identify();
            else if (line == "help") Serial.println(kDoseUsage);
            else if (used) Serial.println("DOSE_ERROR reason=unknown_command");
            used = 0;
            invalid = false;
        } else if (!invalid) {
            if ((c >= ' ' && c <= '~') || c == '\t') {
                if (used + 1 < sizeof(buffer)) { buffer[used++] = c; continue; }
            }
            invalid = true;
        }
    }
    delay(1);
}
