#pragma once

#include <stdint.h>

// ════════════════════════════════════════════════════════════
//  The machine's one voice — U8, off IO13
// ════════════════════════════════════════════════════════════
//
// U8 is an MLT-5020 passive magnetic transducer: a coil pulling on a ferrous
// diaphragm, with no amplitude input of its own. Q1 (S8050) switches its low
// side hard off IO13, so the coil sees 5 V or it sees nothing, and every sound
// the machine can make is made out of WHEN that switch closes.
//
//   PITCH   free — LEDC puts any frequency on IO13. Loudness is not flat across
//           it: the diaphragm is a resonator, loudest at SOUND_RESONANCE_HZ and
//           falling away either side. `ladder` on the bench console walks the
//           span so the peak is measured rather than trusted.
//   VOLUME  duty cycle, and only duty cycle. The diaphragm follows the pulse
//           train's fundamental, whose amplitude goes as sin(pi*d), so 50% duty
//           is the loudest a note gets and everything above it mirrors back down.
//           SOUND_MAX_DUTY is that ceiling.
//   SHAPE   ToneShape below — decay, slide, tremolo — walked by the sequencer.
//
// One coil on one LEDC channel is ONE VOICE. There are no chords, and no
// waveform but square. A play request at a lower priority than what is already
// sounding is dropped, not queued.
//
// ── The loudness budget ───────────────────────────────────────────────────
// sin(pi*d) spends about 24 dB between a 2% pulse and a 50% one, and that is
// the whole dynamic range this machine has. It is spent deliberately: the tick
// a user hears hundreds of times sits at the bottom, and the gas alarm — the
// one sound that has to carry into another room — holds the top alone. A tick
// at full duty would leave the alarm nowhere to go, which is why SND_TICK is
// quiet and why nothing but SND_ALARM is allowed at SOUND_MAX_DUTY.
//
// ── Silencing ─────────────────────────────────────────────────────────────
// Volume, mute and quiet hours all apply to every sound EXCEPT those carrying
// SND_F_UNSILENCEABLE. A gas alarm that a volume setting could mute would be a
// safety defect, so the flag is checked in one place (soundLevelFor) and the
// alarm is the only sound that carries it.
//
// ── Servicing ─────────────────────────────────────────────────────────────
// soundService() MUST be called from loop(). LEDC keeps oscillating in hardware
// once set, so a sequencer that stops being serviced leaves the coil energised
// at whatever step it reached — ~100 mA through Q1, indefinitely. Nothing here
// blocks: every step boundary is a millis() comparison, so calling it costs
// nothing when there is no sound.

// ── Drive limits ──────────────────────────────────────────────────────────
static const int SOUND_MAX_DUTY      = 50;    // % — the loudest a note gets; above this it mirrors
static const int SOUND_RESONANCE_HZ  = 4000;  // where the diaphragm is loudest; `ladder` measures it
static const int SOUND_LEDC_BITS     = 10;    // 0..1023; the 80 MHz APB holds this from ~77 Hz up
static const int SOUND_SHAPE_TICK_MS = 5;     // how often a shaped step is recomputed

static const uint8_t SOUND_FOREVER = 255;     // Sound::repeats — until soundStop()

// ── How one step of a sound behaves over its own duration ─────────────────
enum ToneShape : uint8_t {
    TONE_FLAT,     // hz held at duty for ms
    TONE_DECAY,    // hz held; duty falls exponentially to silence across ms
    TONE_SLIDE,    // duty held; hz slides geometrically from hz to arg across ms
    TONE_TREMOLO,  // hz held; duty swings at arg Hz
    TONE_REST,     // silence for ms
};

struct ToneStep {
    uint16_t hz;     // 0 with TONE_REST
    uint16_t arg;    // SLIDE: end hz.  TREMOLO: swing rate in Hz.  otherwise unused
    uint8_t  duty;   // 0..SOUND_MAX_DUTY, before the volume setting scales it
    uint8_t  shape;  // ToneShape
    uint16_t ms;
};

// ── What may interrupt what ───────────────────────────────────────────────
// A request at a priority BELOW what is sounding is dropped. Equal or above
// pre-empts. So a tick never truncates a chime, and the alarm truncates anything.
enum SoundPriority : uint8_t {
    PRIO_UI    = 0,  // tick — the droppable one
    PRIO_EVENT = 1,  // ack, chime, refuse, ready
    PRIO_FAULT = 2,  // something needs attention
    PRIO_ALARM = 3,  // gas — pre-empts everything and ignores every silencer
};

static const uint8_t SND_F_UNSILENCEABLE = 1 << 0;  // ignores volume, mute and quiet hours

// ── The vocabulary ────────────────────────────────────────────────────────
// One definition, shared by the appliance and the bench, so the factory hears
// exactly what the customer hears.
enum SoundId : uint8_t {
    SND_NONE = 0,
    SND_TICK,     // a touch was registered — NOT "it worked"; see the note in sound.cpp
    SND_ACK,      // something was committed
    SND_CHIME,    // an operation finished
    SND_REFUSE,   // the machine said no
    SND_READY,    // the controller has booted and parked
    SND_FAULT,    // needs attention, nothing is leaking
    SND_ALARM,    // gas trip — loops until stopped, and cannot be silenced
    SND_PROBE,    // the bench continuity probe's note
    SND_COUNT
};

struct Sound {
    const char     *name;
    const ToneStep *steps;
    uint8_t         count;
    uint8_t         priority;
    uint8_t         repeats;   // extra passes after the first; SOUND_FOREVER = until stopped
    uint8_t         flags;
};

// ── Lifecycle ─────────────────────────────────────────────────────────────
// soundBegin() parks the pin before it does anything else, so a board that
// resets mid-alarm comes up silent. Settings are read from NVS here.
void soundBegin(int pin);
void soundService();   // from loop(), every pass — see the note above

// ── Playing ───────────────────────────────────────────────────────────────
// Returns false when the request was dropped: lower priority than what is
// sounding, or silenced by volume/mute/quiet hours. Re-requesting a sound that
// is already looping is a no-op that returns true rather than restarting it.
bool    soundPlay(SoundId id);
void    soundStop();
bool    soundBusy();
SoundId soundPlaying();
const Sound *soundInfo(SoundId id);   // nullptr when out of range

// ── Settings, persisted in NVS ────────────────────────────────────────────
// Volume is linear in ACOUSTIC AMPLITUDE, not in duty: scaling duty directly
// would compress badly near the top, because amplitude goes as sin(pi*d) and
// not as d. soundLevelFor() does the conversion.
void    soundSetVolume(uint8_t pct);       // 0..100; 0 mutes all but the alarm
uint8_t soundVolume();

// Quiet hours wrap midnight when start > end. Needs a clock: without one
// soundSetClock() is never set, hourNow() answers -1, and quiet hours never
// engage — the machine does not guess at the time in order to go quiet.
void    soundSetQuiet(bool on, uint8_t startHour, uint8_t endHour, uint8_t quietPct);
bool    soundQuietOn();
uint8_t soundQuietStart();
uint8_t soundQuietEnd();
uint8_t soundQuietVolume();
bool    soundInQuietHours();               // false when there is no clock

// The clock quiet hours reads. Return 0..23, or -1 for "no idea".
void    soundSetClock(int (*hourNow)());

// What a given sound would actually play at right now, 0..100. 0 means silenced.
uint8_t soundLevelFor(SoundId id);

// ── Characterization, for the bench ───────────────────────────────────────
// Direct drive, below the sequencer — it stops any sound in progress and owns
// the pin until soundToneRaw(0, 0). This is how `ladder`, `duty` and `sweep`
// measure the transducer; nothing in the appliance uses it.
void soundToneRaw(int hz, int dutyPct);
