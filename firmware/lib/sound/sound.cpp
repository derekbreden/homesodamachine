#include <Arduino.h>
#include <Preferences.h>
#include <math.h>

#include "sound.h"

static const float PIf = 3.14159265f;

// ════════════════════════════════════════════════════════════
//  The vocabulary
// ════════════════════════════════════════════════════════════
//
// Duty numbers below are read against sin(pi*d), which is what the diaphragm
// answers — so 50 is the ceiling, 25 lands 3 dB under it, 12 about 9 dB under
// and 6 about 15 dB under. The spread is deliberate and is the whole budget:
// SND_ALARM holds the top alone.

// SND_TICK — the most-repeated sound in the machine, and the one that sets the
// floor. Three steps, 27 ms end to end, which the ear takes as one event.
//
// A click's authority is not its level, it is its shape. The first step is BODY:
// 1400 Hz for 3 ms is barely four cycles, far too few to be a pitch, and well off
// resonance where the diaphragm is inefficient — so it lands as a broadband thump
// rather than a tone, and it is what keeps the click from sounding thin. The
// second is the TIP, at resonance, where the diaphragm actually speaks and where
// the click gets its definition. The third is the RELEASE: cutting a driven coil
// square produces a turn-off transient of its own, so a click that ended flat
// would be two clicks. Decaying out of it leaves one.
//
// The duties look high against the rest of this table, and are not, because the
// ear integrates energy over 100-200 ms and none of this lasts 30. A 27 ms burst
// at duty 26 carries roughly the weight of a sustained tone 9 dB below it, which
// is what keeps the most-repeated sound in the machine underneath the alarm while
// still being something you can feel under a finger.
//
// It means "I registered your touch", NOT "that worked". If success were the
// only thing that sounded, silence would mean both "you missed the glass" and
// "the machine refused you", and on a capacitive panel with no travel and no
// detent those are exactly the two a user cannot otherwise tell apart. Firing
// on touch-down for every registered press leaves silence one meaning: the
// glass did not see you.
static const ToneStep kTick[] = {
    {1400,               0, 22, TONE_FLAT,   3},   // body — four cycles, a thump with no pitch in it
    {SOUND_RESONANCE_HZ, 0, 26, TONE_FLAT,   8},   // tip — at resonance, where it speaks
    {SOUND_RESONANCE_HZ, 0, 26, TONE_DECAY, 16},   // release — so the end is not a second click
};

// SND_ACK — a thing was committed. Two notes up, which is the shape that reads
// as "taken" rather than "finished".
static const ToneStep kAck[] = {
    {2200, 0, 18, TONE_FLAT, 60},
    {3300, 0, 18, TONE_FLAT, 80},
};

// SND_CHIME — an operation finished. The transducer has no decay of its own, so
// the ring is duty falling under a held pitch; without it a note ends square and
// sounds like a fault rather than a completion.
static const ToneStep kChime[] = {
    {3500, 0, 30, TONE_DECAY, 240},
    {0,    0, 0,  TONE_REST,   40},
    {2600, 0, 30, TONE_DECAY, 420},
};

// SND_REFUSE — the machine said no. Deliberately off resonance: down here the
// diaphragm is inefficient, so it is quiet and dull by physics as well as by
// level, and nobody mistakes it for an ack.
static const ToneStep kRefuse[] = {
    {320, 0, 40, TONE_FLAT, 160},
    {0,   0, 0,  TONE_REST,  60},
    {260, 0, 40, TONE_FLAT, 240},
};

// SND_WELCOME — the machine waking up. The one sound a customer hears every time
// they power the thing on, and the only one whose whole job is to be liked.
//
// A square wave cannot play a chord, so the chord is arpeggiated and the ear
// fuses it into one: a C major triad, rising. Major because it resolves upward
// and reads as an opening.
//
// It is said twice. C7-E7-G7 leaves off on the fifth, which is unfinished; a
// breath; then the same three-note shape a third higher, E7-G7-C8, which lands on
// the octave and finishes it. A motif restated at a new pitch is what makes a
// short melody memorable rather than merely pleasant, and memorable is the whole
// job of the one sound a customer hears every time they turn the machine on. It
// is also where the length comes from — a square wave grows harsh if you simply
// hold the notes longer, so the time is spent on structure instead.
//
// The arrival is the point. C8 is 4186 Hz — within 5% of where this diaphragm is
// loudest — so the phrase climbs INTO the resonance and the bloom at the top is
// the transducer's own, not something the duty numbers have to fake. Those duties
// fall as the pitch rises, compensating for the diaphragm getting more efficient
// on the way up, so the notes read as even and the bloom belongs to the last one
// alone. The second phrase sits a little above the first, so the restatement
// arrives as a lift.
//
// Then it is held a moment at full and let go rather than stopped: the sustain is
// what makes the arrival sound certain, and the decay is what makes the whole
// thing a chime instead of six beeps. Consecutive FLAT steps never drop the duty
// between them, so each phrase slurs.
//
// Roughly 2 kHz to 5 kHz is the whole of the range worth writing in: below it the
// diaphragm is inefficient, above it the resonance is behind you. Both phrases
// live inside that, which is why the melody moves rather than the register.
static const ToneStep kWelcome[] = {
    {2093, 0, 26, TONE_FLAT,   62},   // C7  ┐
    {2637, 0, 24, TONE_FLAT,   62},   // E7  │ the motif, left open on the fifth
    {3136, 0, 22, TONE_FLAT,   62},   // G7  ┘
    {0,    0,  0, TONE_REST,   26},   // a breath, so what follows lands as a restatement
    {2637, 0, 27, TONE_FLAT,   62},   // E7  ┐
    {3136, 0, 25, TONE_FLAT,   62},   // G7  │ the same shape a third higher, and it closes
    {4186, 0, 28, TONE_FLAT,   90},   // C8  ┘ the arrival, held a moment at full
    {4186, 0, 28, TONE_DECAY, 640},   // and released into the resonance
};

// SND_FAULT — needs attention, nothing is leaking. Twice, then a long gap, and
// it repeats: a pattern that stays legible across a room without being an alarm.
static const ToneStep kFault[] = {
    {2400, 0, 34, TONE_FLAT, 140},
    {0,    0, 0,  TONE_REST,  90},
    {2400, 0, 34, TONE_FLAT, 140},
    {0,    0, 0,  TONE_REST, 620},
};

// SND_ALARM — the gas trip, and the reason every other sound is held below 50%.
// Both pitches sit near resonance so both are as loud as this board gets, and
// they alternate hard: a steady tone becomes room noise within a minute, an
// alternating pair does not. Loops until soundStop(), and SND_F_UNSILENCEABLE
// puts it outside volume, mute and quiet hours.
static const ToneStep kAlarm[] = {
    {4000, 0, SOUND_MAX_DUTY, TONE_FLAT, 160},
    {3000, 0, SOUND_MAX_DUTY, TONE_FLAT, 160},
};

// SND_PROBE — the bench continuity probe's note. One pitch for every net, so
// probing needs no screen: touch and hold until it sounds.
static const ToneStep kProbe[] = {
    {2700, 0, SOUND_MAX_DUTY, TONE_FLAT, 150},
};

#define SND(arr) arr, (uint8_t)(sizeof(arr) / sizeof(*(arr)))

static const Sound kSound[SND_COUNT] = {
    {"none",   nullptr, 0,          PRIO_UI,    0,             0},
    {"tick",   SND(kTick),          PRIO_UI,    0,             0},
    {"ack",    SND(kAck),           PRIO_EVENT, 0,             0},
    {"chime",  SND(kChime),         PRIO_EVENT, 0,             0},
    {"refuse", SND(kRefuse),        PRIO_EVENT, 0,             0},
    {"welcome",SND(kWelcome),       PRIO_EVENT, 0,             0},
    {"fault",  SND(kFault),         PRIO_FAULT, 4,             0},
    {"alarm",  SND(kAlarm),         PRIO_ALARM, SOUND_FOREVER, SND_F_UNSILENCEABLE},
    {"probe",  SND(kProbe),         PRIO_EVENT, 0,             0},
};

// ════════════════════════════════════════════════════════════
//  Drive
// ════════════════════════════════════════════════════════════

static int  buzzPin  = -1;
static bool attached = false;
static int  curHz    = 0;

static const int LEDC_FULL = (1 << SOUND_LEDC_BITS) - 1;

static void driveOff() {
    if (attached) { ledcWrite(buzzPin, 0); ledcDetach(buzzPin); attached = false; }
    curHz = 0;
    if (buzzPin >= 0) {
        pinMode(buzzPin, OUTPUT);      // LEDC hands the pin back; Q1's base is held off here
        digitalWrite(buzzPin, LOW);
    }
}

static void drive(int hz, uint8_t dutyPct) {
    if (buzzPin < 0) return;
    if (dutyPct == 0) { if (attached) ledcWrite(buzzPin, 0); return; }
    if (hz < 80) hz = 80;              // below this the 10-bit timer cannot divide down
    if (!attached) {
        if (!ledcAttach(buzzPin, hz, SOUND_LEDC_BITS)) return;   // no LEDC channel free
        attached = true;
        curHz    = hz;
    } else if (hz != curHz) {
        ledcChangeFrequency(buzzPin, hz, SOUND_LEDC_BITS);
        curHz = hz;
    }
    if (dutyPct > SOUND_MAX_DUTY) dutyPct = SOUND_MAX_DUTY;
    ledcWrite(buzzPin, (uint32_t)dutyPct * LEDC_FULL / 100);
}

// Duty is not loudness. The diaphragm follows the pulse train's fundamental,
// whose amplitude goes as sin(pi*d) — so a volume control that scaled duty
// directly would barely move across the top half of its travel. The scaling is
// done in amplitude and converted back to a duty here. asinf() always returns
// the branch below 50%, which is the one that is not a mirror.
static uint8_t dutyScaled(uint8_t nominalDuty, float factor) {
    if (!nominalDuty || factor <= 0.0f) return 0;
    float amp = sinf(PIf * (float)nominalDuty / 100.0f) * factor;
    if (amp <= 0.0f)  return 0;
    if (amp >= 1.0f)  return SOUND_MAX_DUTY;
    float d = asinf(amp) * 100.0f / PIf;
    if (d < 1.0f) d = 1.0f;            // a nonzero level always makes something
    return (uint8_t)(d + 0.5f);
}

// ════════════════════════════════════════════════════════════
//  Settings
// ════════════════════════════════════════════════════════════

static Preferences prefs;
static const char *NVS_NS = "hsmsound";

static uint8_t volumePct  = 70;
static bool    quietOn    = false;
static uint8_t quietStart = 22;
static uint8_t quietEnd   = 7;
static uint8_t quietPct   = 25;

static int (*hourNowFn)() = nullptr;

static void settingsSave() {
    if (!prefs.begin(NVS_NS, false)) return;
    prefs.putUChar("vol",    volumePct);
    prefs.putBool ("qOn",    quietOn);
    prefs.putUChar("qStart", quietStart);
    prefs.putUChar("qEnd",   quietEnd);
    prefs.putUChar("qVol",   quietPct);
    prefs.end();
}

static void settingsLoad() {
    // Opened read-WRITE even though nothing is written here: a read-only open of a
    // namespace that does not exist yet fails, and logs an nvs_open error on the
    // console of every factory-fresh board. Opening read-write creates it quietly,
    // and the defaults above stand until something calls a setter.
    if (!prefs.begin(NVS_NS, false)) return;
    volumePct  = prefs.getUChar("vol",    volumePct);
    quietOn    = prefs.getBool ("qOn",    quietOn);
    quietStart = prefs.getUChar("qStart", quietStart);
    quietEnd   = prefs.getUChar("qEnd",   quietEnd);
    quietPct   = prefs.getUChar("qVol",   quietPct);
    prefs.end();
    if (volumePct > 100) volumePct = 100;
    if (quietPct  > 100) quietPct  = 100;
    if (quietStart > 23) quietStart = 0;
    if (quietEnd   > 23) quietEnd   = 0;
}

void soundSetClock(int (*hourNow)()) { hourNowFn = hourNow; }

// Without a clock this is false, always. A machine that guessed at the hour in
// order to go quiet would go quiet at the wrong time, which is worse than not
// going quiet at all.
bool soundInQuietHours() {
    if (!quietOn || !hourNowFn) return false;
    int h = hourNowFn();
    if (h < 0 || h > 23)           return false;
    if (quietStart == quietEnd)    return false;
    if (quietStart < quietEnd)     return h >= quietStart && h < quietEnd;
    return h >= quietStart || h < quietEnd;   // the window wraps midnight
}

uint8_t soundLevelFor(SoundId id) {
    if (id == SND_NONE || id >= SND_COUNT) return 0;
    // The one exemption in the file. A gas alarm a setting could mute would be a
    // safety defect, so it is answered before any setting is consulted.
    if (kSound[id].flags & SND_F_UNSILENCEABLE) return 100;
    uint8_t lvl = volumePct;
    if (soundInQuietHours() && quietPct < lvl) lvl = quietPct;
    return lvl;
}

void soundSetVolume(uint8_t pct) {
    volumePct = pct > 100 ? 100 : pct;
    settingsSave();
}

void soundSetQuiet(bool on, uint8_t startHour, uint8_t endHour, uint8_t qPct) {
    quietOn    = on;
    quietStart = startHour > 23 ? 0 : startHour;
    quietEnd   = endHour   > 23 ? 0 : endHour;
    quietPct   = qPct > 100 ? 100 : qPct;
    settingsSave();
}

uint8_t soundVolume()      { return volumePct; }
bool    soundQuietOn()     { return quietOn; }
uint8_t soundQuietStart()  { return quietStart; }
uint8_t soundQuietEnd()    { return quietEnd; }
uint8_t soundQuietVolume() { return quietPct; }

const Sound *soundInfo(SoundId id) {
    return (id == SND_NONE || id >= SND_COUNT) ? nullptr : &kSound[id];
}

// ════════════════════════════════════════════════════════════
//  The sequencer
// ════════════════════════════════════════════════════════════

static const Sound *cur        = nullptr;
static SoundId      curId      = SND_NONE;
static uint8_t      stepIdx    = 0;
static uint8_t      passesLeft = 0;
static float        curFactor  = 0.0f;   // the resolved level, 0..1
static uint32_t     stepStart  = 0;
static uint32_t     lastShape  = 0;
static bool         rawOwned   = false;  // soundToneRaw() has the pin

static bool stepIsShaped(const ToneStep &s) {
    return s.shape == TONE_DECAY || s.shape == TONE_SLIDE || s.shape == TONE_TREMOLO;
}

// The amplitude multiplier a shape applies at `elapsed` into its own step.
static void applyStep(uint32_t elapsed) {
    const ToneStep &s = cur->steps[stepIdx];
    float span = s.ms ? (float)elapsed / (float)s.ms : 1.0f;
    if (span > 1.0f) span = 1.0f;

    switch (s.shape) {
        case TONE_REST:
            drive(0, 0);
            return;

        case TONE_DECAY:
            drive(s.hz, dutyScaled(s.duty, curFactor * expf(-3.2f * span)));
            return;

        case TONE_SLIDE: {
            // Pitch is heard in ratios, so the slide is geometric: a linear ramp
            // stalls at the top and spends its time down where the diaphragm is quiet.
            int from = s.hz ? s.hz : 1;
            int to   = s.arg ? s.arg : from;
            drive((int)(from * powf((float)to / (float)from, span)), dutyScaled(s.duty, curFactor));
            return;
        }

        case TONE_TREMOLO: {
            float rate = s.arg ? (float)s.arg : 8.0f;
            float amp  = 0.55f + 0.45f * sinf(2.0f * PIf * rate * (float)elapsed / 1000.0f);
            drive(s.hz, dutyScaled(s.duty, curFactor * amp));
            return;
        }

        case TONE_FLAT:
        default:
            drive(s.hz, dutyScaled(s.duty, curFactor));
            return;
    }
}

static void enterStep(uint32_t now) {
    stepStart = now;
    lastShape = now;
    applyStep(0);
}

void soundStop() {
    cur   = nullptr;
    curId = SND_NONE;
    driveOff();
}

bool soundPlay(SoundId id) {
    if (id == SND_NONE || id >= SND_COUNT) return false;
    const Sound *s = &kSound[id];
    if (!s->steps || !s->count) return false;

    // Re-asserting a sound that is already looping is what a held condition does
    // every pass; it must not restart the pattern each time.
    if (cur == s && passesLeft == SOUND_FOREVER) return true;

    // Below what is sounding is dropped, not queued: there is one voice, and a
    // tick arriving mid-chime is worth less than the chime finishing.
    if (cur && s->priority < cur->priority) return false;

    uint8_t lvl = soundLevelFor(id);
    if (!lvl) return false;                      // silenced by volume, mute or quiet hours

    rawOwned   = false;
    cur        = s;
    curId      = id;
    stepIdx    = 0;
    passesLeft = s->repeats;
    curFactor  = (float)lvl / 100.0f;
    enterStep(millis());
    return true;
}

void soundService() {
    if (!cur || rawOwned) return;

    uint32_t now  = millis();
    const ToneStep &s = cur->steps[stepIdx];

    if (now - stepStart < s.ms) {
        // Mid-step. Only a shaped step has anything to recompute.
        if (stepIsShaped(s) && now - lastShape >= (uint32_t)SOUND_SHAPE_TICK_MS) {
            lastShape = now;
            applyStep(now - stepStart);
        }
        return;
    }

    if (++stepIdx >= cur->count) {
        if (passesLeft == SOUND_FOREVER) {
            stepIdx = 0;
        } else if (passesLeft) {
            passesLeft--;
            stepIdx = 0;
        } else {
            soundStop();
            return;
        }
    }
    enterStep(now);
}

bool    soundBusy()    { return cur != nullptr; }
SoundId soundPlaying() { return curId; }

void soundBegin(int pin) {
    buzzPin  = pin;
    attached = false;
    cur      = nullptr;
    curId    = SND_NONE;
    rawOwned = false;
    driveOff();       // parked before anything else runs — a reset mid-alarm comes up silent
    settingsLoad();
}

// ── Characterization ──────────────────────────────────────────────────────
// Below the sequencer, and it takes the pin off it. The bench measures the
// transducer with this; nothing in the appliance calls it.
void soundToneRaw(int hz, int dutyPct) {
    cur   = nullptr;
    curId = SND_NONE;
    if (hz <= 0 || dutyPct <= 0) { rawOwned = false; driveOff(); return; }
    rawOwned = true;
    drive(hz, (uint8_t)(dutyPct > SOUND_MAX_DUTY ? SOUND_MAX_DUTY : dutyPct));
}
