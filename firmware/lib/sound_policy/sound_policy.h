#pragma once

#include <stdint.h>

// ── What a setting does to a sound ────────────────────────────────────────
// The volume and quiet-hours decision, and the amplitude conversion under it,
// with nothing of the coil in the way: no LEDC, no NVS, no clock of its own.
// sound.cpp holds the pin, the sequencer and the stored settings and asks
// here; `pio test -e native` asks the same questions without a board.
//
// THE ALARM'S EXEMPTION IS THE POINT. A gas alarm a volume setting could mute
// would be a safety defect, so `levelFor` answers an unsilenceable sound before
// it reads a single field of Settings — and that is a property a test can hold
// against every setting the two of them can be in.
// The loudest a note gets. The diaphragm follows the pulse train's
// fundamental, whose amplitude goes as sin(pi*d), so 50% is the peak and
// everything above it mirrors back down.
static const int SOUND_MAX_DUTY = 50;

namespace sound_policy {

// No clock. `hourNow()` answers this when U6 does not, or when its time cannot
// be believed, and quiet hours never engage against it.
constexpr int kNoHour = -1;

// The stored settings, clamped on the way in so nothing downstream has to.
struct Settings {
    uint8_t volume;       // 0..100; 0 mutes everything but an unsilenceable sound
    bool    quietOn;
    uint8_t quietStart;   // hour, 0..23
    uint8_t quietEnd;     // hour, 0..23; start > end wraps midnight
    uint8_t quietVolume;  // 0..100, the ceiling while quiet hours are in force

    Settings();
};

// Every field held to its own range. A value out of range is the same as one
// never written: volumes clamp to 100 and hours fall back to 0.
Settings clamped(Settings settings);

// Whether the quiet window is in force at `hour`. False without a clock, false
// while quiet hours are off, and false for a window whose ends are the same
// hour — an empty window rather than a whole day.
bool inQuietHours(const Settings &settings, int hour);

// What a sound plays at, 0..100. An unsilenceable sound is answered at 100
// before any setting is consulted; everything else takes the volume, held down
// to the quiet ceiling while the window is in force.
uint8_t levelFor(const Settings &settings, int hour, bool unsilenceable);

// The duty that plays `nominalDuty` at `factor` of its loudness — the volume
// setting as a fraction, times whatever envelope the step's own shape applies.
//
// DUTY IS NOT LOUDNESS. The diaphragm follows the pulse train's fundamental,
// whose amplitude goes as sin(pi*d), so scaling duty directly would barely move
// the top half of the control's travel. The scale is applied in amplitude and
// converted back. A nonzero factor always returns a nonzero duty: a sound that
// is not silenced makes something.
uint8_t dutyForFactor(uint8_t nominalDuty, float factor);

}  // namespace sound_policy
