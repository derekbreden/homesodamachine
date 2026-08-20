#include <Arduino.h>
#include <Wire.h>

#include "rtc.h"
#include "pins.h"

static const uint8_t ADDR_RTC    = 0x68;
static const uint8_t REG_SECONDS = 0x00;
static const uint8_t REG_CONTROL = 0x0E;
static const uint8_t REG_STATUS  = 0x0F;
static const uint8_t REG_TEMP    = 0x11;

static const uint32_t RTC_REFRESH_MS = 30000;   // the hour does not move fast

static bool     present   = false;
static bool     valid     = false;
static int      hourCache = -1;
static uint32_t lastReadMs = 0;

static uint8_t bcdToBin(uint8_t v) { return (uint8_t)((v >> 4) * 10 + (v & 0x0F)); }
static uint8_t binToBcd(uint8_t v) { return (uint8_t)(((v / 10) << 4) | (v % 10)); }

static bool i2cRead(uint8_t reg, uint8_t *buf, uint8_t n) {
    Wire.beginTransmission(ADDR_RTC);
    Wire.write(reg);
    if (Wire.endTransmission(false) != 0) return false;
    if (Wire.requestFrom((int)ADDR_RTC, (int)n) != n) return false;
    for (uint8_t i = 0; i < n; i++) buf[i] = Wire.read();
    return true;
}

static bool i2cWrite(uint8_t reg, const uint8_t *buf, uint8_t n) {
    Wire.beginTransmission(ADDR_RTC);
    Wire.write(reg);
    for (uint8_t i = 0; i < n; i++) Wire.write(buf[i]);
    return Wire.endTransmission() == 0;
}

// One bus read, refreshing both the hour and whether it can be believed.
static void refresh() {
    lastReadMs = millis();

    uint8_t st;
    if (!i2cRead(REG_STATUS, &st, 1)) { present = false; valid = false; hourCache = -1; return; }
    present = true;

    // OSF set means the oscillator has stopped since it was last cleared, so
    // whatever the time registers hold is not the time.
    if (st & 0x80) { valid = false; hourCache = -1; return; }

    uint8_t tb[3];
    if (!i2cRead(REG_SECONDS, tb, 3)) { valid = false; hourCache = -1; return; }

    // Bit 6 of the hours register selects 12-hour mode. The DS3231 powers up in
    // 24-hour mode and rtcSet() writes it that way, but a clock set by something
    // else may not have, and a 12-hour reading taken as 24 would be off by twelve.
    uint8_t hr = tb[2];
    if (hr & 0x40) {
        int h12 = bcdToBin(hr & 0x1F);
        bool pm = hr & 0x20;
        hourCache = (h12 % 12) + (pm ? 12 : 0);
    } else {
        hourCache = bcdToBin(hr & 0x3F);
    }
    valid = hourCache >= 0 && hourCache <= 23;
    if (!valid) hourCache = -1;
}

void rtcBegin() {
    Wire.begin(PIN_SDA, PIN_SCL, 100000);
    refresh();
}

int rtcHour() {
    if (millis() - lastReadMs >= RTC_REFRESH_MS) refresh();
    return hourCache;
}

bool rtcPresent() { return present; }
bool rtcValid()   { if (millis() - lastReadMs >= RTC_REFRESH_MS) refresh(); return valid; }

void rtcStamp(char *out, size_t n) {
    uint8_t tb[7], st;
    if (!i2cRead(REG_STATUS, &st, 1) || !i2cRead(REG_SECONDS, tb, 7)) {
        snprintf(out, n, "no answer at 0x%02X", ADDR_RTC);
        return;
    }
    if (st & 0x80) { snprintf(out, n, "unset (OSF latched — 'rtc set' clears it)"); return; }
    uint8_t hr = tb[2];
    int hour = (hr & 0x40) ? ((bcdToBin(hr & 0x1F) % 12) + ((hr & 0x20) ? 12 : 0))
                           : bcdToBin(hr & 0x3F);
    snprintf(out, n, "20%02u-%02u-%02u %02u:%02u:%02u",
             bcdToBin(tb[6]), bcdToBin(tb[5] & 0x1F), bcdToBin(tb[4]),
             hour, bcdToBin(tb[1]), bcdToBin(tb[0] & 0x7F));
}

bool rtcSet(int year, int mon, int day, int hour, int min, int sec) {
    if (year < 2000 || year > 2099 || mon < 1 || mon > 12 || day < 1 || day > 31 ||
        hour < 0 || hour > 23 || min < 0 || min > 59 || sec < 0 || sec > 59)
        return false;

    uint8_t tb[7] = {
        binToBcd((uint8_t)sec), binToBcd((uint8_t)min), binToBcd((uint8_t)hour),  // bit 6 clear = 24h
        1,                                                                        // day-of-week, unused
        binToBcd((uint8_t)day), binToBcd((uint8_t)mon), binToBcd((uint8_t)(year - 2000)),
    };
    if (!i2cWrite(REG_SECONDS, tb, 7)) return false;

    // EOSC (control bit 7) high stops the oscillator on battery — a clock that
    // only runs while the machine is plugged in cannot carry quiet hours across
    // a power cut. Clear it, then clear OSF so the reading is believed again.
    uint8_t ctrl;
    if (i2cRead(REG_CONTROL, &ctrl, 1)) {
        ctrl &= ~0x80;
        i2cWrite(REG_CONTROL, &ctrl, 1);
    }
    uint8_t st;
    if (i2cRead(REG_STATUS, &st, 1)) {
        st &= ~0x80;
        i2cWrite(REG_STATUS, &st, 1);
    }
    refresh();
    return true;
}

bool rtcTemp(float *outC) {
    uint8_t t[2];
    if (!i2cRead(REG_TEMP, t, 2)) return false;
    *outC = (int8_t)t[0] + ((t[1] >> 6) * 0.25f);
    return true;
}
