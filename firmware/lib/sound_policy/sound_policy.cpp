#include "sound_policy.h"

#include <math.h>

namespace sound_policy {
namespace {

const float kPi = 3.14159265f;

uint8_t pct(uint8_t value) { return value > 100 ? 100 : value; }
uint8_t hour(uint8_t value) { return value > 23 ? 0 : value; }

}  // namespace

Settings::Settings()
    : volume(70), quietOn(false), quietStart(22), quietEnd(7), quietVolume(25) {}

Settings clamped(Settings settings) {
    settings.volume      = pct(settings.volume);
    settings.quietVolume = pct(settings.quietVolume);
    settings.quietStart  = hour(settings.quietStart);
    settings.quietEnd    = hour(settings.quietEnd);
    return settings;
}

bool inQuietHours(const Settings &settings, int h) {
    if (!settings.quietOn)                  return false;
    if (h < 0 || h > 23)                    return false;
    if (settings.quietStart == settings.quietEnd) return false;
    if (settings.quietStart < settings.quietEnd)
        return h >= settings.quietStart && h < settings.quietEnd;
    return h >= settings.quietStart || h < settings.quietEnd;   // the window wraps midnight
}

uint8_t levelFor(const Settings &settings, int h, bool unsilenceable) {
    if (unsilenceable) return 100;
    uint8_t level = pct(settings.volume);
    const uint8_t ceiling = pct(settings.quietVolume);
    if (inQuietHours(settings, h) && ceiling < level) level = ceiling;
    return level;
}

uint8_t dutyForFactor(uint8_t nominalDuty, float factor) {
    if (!nominalDuty || factor <= 0.0f) return 0;
    const float amp = sinf(kPi * (float)nominalDuty / 100.0f) * factor;
    if (amp <= 0.0f) return 0;
    if (amp >= 1.0f) return SOUND_MAX_DUTY;
    // asinf answers the branch below 50%, which is the one that is not a mirror.
    float duty = asinf(amp) * 100.0f / kPi;
    if (duty < 1.0f) duty = 1.0f;
    return (uint8_t)(duty + 0.5f);
}

}  // namespace sound_policy
