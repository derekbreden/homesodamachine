#!/usr/bin/env python3
"""Render the original One Less Errand score and tactile effects at 48 kHz.

The notes, instruments, room response, and effects are synthesized locally.
There are no samples, borrowed compositions, runtime downloads, or audio inputs.
"""
from __future__ import annotations

import json
import math
import re
import subprocess
from pathlib import Path

import numpy as np
from scipy import signal
from scipy.io import wavfile

ROOT = Path(__file__).resolve().parent
SR = 48000
DURATION = 100
SAMPLES = SR * DURATION
RNG = np.random.default_rng(74261)
SCORE = np.zeros((SAMPLES, 2), dtype=np.float64)
EFFECTS = np.zeros((SAMPLES, 2), dtype=np.float64)
EVENTS: list[dict] = []


def hz(midi: float) -> float:
    return 440.0 * 2 ** ((midi - 69.0) / 12.0)


def filt(x, lo=None, hi=None, order=2):
    if lo is not None and hi is not None:
        sos = signal.butter(order, [lo, hi], btype="bandpass", fs=SR, output="sos")
    elif hi is not None:
        sos = signal.butter(order, hi, btype="lowpass", fs=SR, output="sos")
    else:
        sos = signal.butter(order, lo, btype="highpass", fs=SR, output="sos")
    return signal.sosfilt(sos, x, axis=0)


def taper(x, attack=0.006, release=0.06):
    x = np.array(x, copy=True)
    a, r = min(len(x), int(attack * SR)), min(len(x), int(release * SR))
    if a:
        x[:a] *= np.sin(np.linspace(0, np.pi / 2, a)) ** 2
    if r:
        x[-r:] *= np.cos(np.linspace(0, np.pi / 2, r)) ** 2
    return x


def add(dest, t0, mono, gain=1.0, pan=0.0):
    start = int(round(t0 * SR))
    if start < 0 or start >= len(dest):
        raise ValueError(f"Audio event outside film: {t0}")
    end = min(start + len(mono), len(dest))
    # Equal-power, modest stereo placement. A center event remains full in mono.
    p = (np.clip(pan, -1, 1) + 1) * np.pi / 4
    dest[start:end, 0] += mono[: end - start] * gain * np.cos(p)
    dest[start:end, 1] += mono[: end - start] * gain * np.sin(p)


def felt_key(midi, velocity=0.6, duration=4.8):
    """Soft electric/felt key with decaying, gently inharmonic partials."""
    t = np.arange(int(duration * SR)) / SR
    freq = hz(midi)
    base_decay = 1.45 + 0.009 * (72 - midi)
    x = np.zeros_like(t)
    # The fifth overtone is quiet; there is no exposed high sine bell tone.
    for k, amplitude, life in [(1, 1.0, 1.0), (2, 0.18, .51), (3, .085, .31),
                                (4, .032, .19), (5, .01, .11)]:
        detune = 1 + (0.00014 * k * k)
        phase = 2 * np.pi * freq * k * detune * t
        x += amplitude * np.sin(phase) * np.exp(-t / (base_decay * life))
    # Subtle detuned unison adds the small liveliness of a physical instrument.
    x += .075 * np.sin(2 * np.pi * freq * 1.0013 * t + .17) * np.exp(-t / 1.15)
    hammer = filt(RNG.normal(size=len(t)), lo=280, hi=3100)
    x += .065 * hammer * np.exp(-t / .022)
    x *= velocity * (.985 + .015 * np.sin(2 * np.pi * 3.2 * t))
    return taper(filt(x, hi=5200), .008, .18)


def bass(midi, duration=3.6):
    t = np.arange(int(duration * SR)) / SR
    f = hz(midi)
    x = (np.sin(2 * np.pi * f * t) + .21 * np.sin(2 * np.pi * f * 2 * t)
         + .042 * np.sin(2 * np.pi * f * 3 * t)) * np.exp(-t / 1.30)
    return taper(x, .040, .12)


def note(t, midi, gain=.05, pan=0, duration=4.8):
    add(SCORE, t, felt_key(midi, duration=duration), gain, pan)


def chord(t, notes, gain=.045, spread=.085, duration=5):
    for i, m in enumerate(notes):
        note(t + i * spread, m, gain * (1 - .045 * i),
             pan=(i - (len(notes) - 1) / 2) * .10, duration=duration)


def dull_tick(duration=.18):
    t = np.arange(int(duration * SR)) / SR
    noise = filt(RNG.normal(size=len(t)), lo=900, hi=2600)
    return taper(noise * np.exp(-t / .017), .001, .01)


def can_contact(duration=.8):
    """Short weighted countertop contact, softened aluminum shell resonance."""
    t = np.arange(int(duration * SR)) / SR
    hit = filt(RNG.normal(size=len(t)), lo=80, hi=1800) * np.exp(-t / .012)
    body = .52 * np.sin(2 * np.pi * 155 * t) * np.exp(-t / .036)
    shell = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t / d)
                for f, a, d in [(484, .36, .055), (913, .17, .043), (1741, .068, .025)])
    return taper(hit * .70 + body + shell, .0015, .08)


def card_shuffle(duration=.30):
    t = np.arange(int(duration * SR)) / SR
    noise = filt(RNG.normal(size=len(t)), lo=220, hi=2600)
    return taper(noise * np.sin(np.pi * t / duration) ** 2, .01, .03)


def airy(duration=1.2):
    t = np.arange(int(duration * SR)) / SR
    n = filt(RNG.normal(size=len(t)), lo=240, hi=2500)
    return taper(n * np.sin(np.pi * t / duration) ** 2, .03, .12)


def glass_contact(duration=1.6):
    t = np.arange(int(duration * SR)) / SR
    # The glass is touched, not struck for an advertising chime.
    x = np.zeros_like(t)
    for f, a, d in [(680, .40, .11), (1063, .21, .12), (1698, .14, .095), (2570, .055, .07)]:
        x += a * np.sin(2 * np.pi * f * t) * np.exp(-t / d)
    x += .6 * filt(RNG.normal(size=len(t)), lo=200, hi=1600) * np.exp(-t / .01)
    return taper(x, .002, .2)


def button(duration=.12):
    t = np.arange(int(duration * SR)) / SR
    x = filt(RNG.normal(size=len(t)), lo=130, hi=2900) * np.exp(-t / .009)
    x += .22 * np.sin(2 * np.pi * 270 * t) * np.exp(-t / .016)
    return taper(x, .001, .018)


def water(duration):
    """Quiet illustrative water/pouring texture with changing bubble resonances."""
    t = np.arange(int(duration * SR)) / SR
    stream = filt(RNG.normal(size=len(t)), lo=340, hi=5600, order=2)
    modulation = 0.58 + .11 * np.sin(2 * np.pi * 2.7 * t) + .04 * np.sin(2 * np.pi * 7.31 * t)
    x = .10 * stream * modulation
    # Droplet impacts stay embedded in the stream instead of isolated game blips.
    for at in np.cumsum(RNG.uniform(.09, .23, 100)):
        if at >= duration - .25:
            break
        length = .055
        dt = np.arange(int(length * SR)) / SR
        f = RNG.uniform(430, 1600) * (1 - .23 * at / duration)
        ph = 2 * np.pi * f * (.018 * (1 - np.exp(-dt / .018)) + .34 * dt)
        droplet = np.sin(ph) * np.exp(-dt / .009) * RNG.uniform(.007, .02)
        start = int(at * SR)
        x[start:start + len(dt)] += taper(droplet, .001, .006)
    return taper(filt(x, hi=4600), .32, .40)


def event(t, description, duration=None, stem="effects"):
    EVENTS.append({"start": round(t, 3), **({"end": round(t + duration, 3)} if duration else {}),
                   "stem": stem, "description": description})


# A small wish: the opening leaves room for the first words and the can reveal.
note(1.10, 74, .060, -.12)
note(2.64, 69, .036, .12)
note(4.18, 66, .028, .0)
event(1.10, "Three-note felt-key introduction; curiosity without a rhythmic bed", 5, "score")

# A measured eight-second errand cycle. Identical rhythmic placement makes the
# repetition legible while voicing and ghost notes make it feel composed.
for cycle, base in enumerate([6.0, 14.0, 22.0]):
    add(SCORE, base + .20, bass(47), .021, -.02)
    motif = [(0.24, 66, .047), (1.74, 69, .041), (3.24, 74, .039),
             (4.74, 69, .043), (6.24, 64, .033), (6.99, 66, .028)]
    for offset, pitch, gain in motif:
        note(base + offset, pitch, gain, -.14 if pitch < 70 else .14, 3.3)
    if cycle:
        note(base + 3.31, 62, .024, -.20, 3.3)
    for tick in [0.24, 1.74, 3.24, 4.74, 6.24]:
        add(SCORE, base + tick, dull_tick(), .007, -.22)
    event(base, "Eight-second B-minor/add-nine errand motif; soft muted key and brushed pulse", 8, "score")

# Set the room response before the midpoint release so every old tail stops.
def room(src, wet=.18):
    output = src.copy()
    for ch in range(2):
        ir_len = int(1.85 * SR)
        ir_t = np.arange(ir_len) / SR
        ir = RNG.normal(size=ir_len) * np.exp(-ir_t / .33)
        ir = filt(ir, lo=160, hi=3800)
        ir[:int(.030 * SR)] = 0
        ir *= .0007
        for delay, value in [(0.039, .13), (.079, .081), (.127, .050), (.213, .026), (.341, .015)]:
            ir[int((delay + ch * .009) * SR)] += value
        output[:, ch] += signal.fftconvolve(src[:, ch], ir, mode="full")[:len(src)] * wet
    return output

SCORE = room(SCORE, .8)
a, b = int(29.30 * SR), int(30.0 * SR)
SCORE[a:b] *= np.cos(np.linspace(0, np.pi / 2, b - a))[:, None] ** 2
SCORE[b:] = 0

# The same tonal world opens into D major; the music now breathes between notes.
product = np.zeros_like(SCORE)
chore = SCORE
SCORE = product
progression = [
    (32.4, [50, 57, 61, 66], 38),       # D maj7; reveal settles
    (37.0, [55, 62, 66, 69], 43),       # G maj9
    (41.3, [59, 62, 66, 69], 47),       # B minor7
    (46.1, [57, 64, 66, 73], 45),       # A add6/9; selection
    (50.4, [50, 57, 61, 66], 38),       # D major
    (55.0, [55, 62, 66, 69], 43),       # G major, under the pour
    (59.3, [57, 64, 66, 73], 45),       # A; anticipation
    (63.1, [50, 57, 61, 66], 38),       # D; product beauty
    (67.4, [55, 62, 66, 69], 43),
    (71.1, [59, 62, 66, 69], 47),       # industrial
    (75.3, [57, 64, 66, 73], 45),
    (79.1, [55, 62, 66, 69], 43),       # finishes
    (83.2, [50, 57, 61, 66], 38),
    (87.1, [59, 62, 66, 69], 47),       # four choices
    (90.4, [57, 64, 66, 73], 45),
    (94.1, [50, 57, 61, 66, 69], 38),   # home; warm stable cadence
]
for t, voicing, root in progression:
    chord(t, voicing, .040 if t < 63 else .046, spread=.105, duration=5)
    add(SCORE, t + .09, bass(root, duration=4.3), .019 if t < 63 else .022, 0)

# A restrained melody only emerges when the image can carry itself.
for t, pitch, gain in [
    (34.50, 69, .028), (35.50, 66, .023),
    (39.15, 71, .022), (43.35, 69, .024),
    (44.80, 66, .020), (48.20, 64, .022),
    (52.20, 66, .023), (57.05, 69, .026),
    (61.05, 73, .022), (65.25, 74, .029),
    (69.38, 71, .027), (73.20, 69, .026),
    (77.50, 66, .024), (81.12, 69, .028),
    (85.15, 66, .025), (89.12, 64, .024),
    (92.05, 61, .025), (95.05, 66, .030),
    (96.15, 62, .037),
]:
    note(t, pitch, gain, -.1 if pitch < 69 else .12)
SCORE = chore + room(SCORE, .93)
event(30, "Quiet pivot; no tonal score until 32.4 s", 2.4, "score")
event(32.4, "Spacious D-major felt-key progression, open voicings and warm bass", 61.7, "score")
event(94.1, "Final D-major resolution with a descending two-note finish", 5.9, "score")

# Tactile scene cues. All remain deliberately below the spoken lead.
for t, gain, pan in [(1.16, .048, -.06), (6.12, .058, -.10), (6.55, .032, .08),
                      (7.02, .028, -.05), (14.27, .047, .10), (18.27, .040, -.10),
                      (22.28, .046, -.08), (24.25, .030, .11), (27.02, .045, -.05)]:
    add(EFFECTS, t, can_contact(), gain, pan)
    event(t, "Soft can/case contact")
for t, gain, pan in [(7.42, .020, -.14), (14.55, .030, .10), (18.50, .027, -.10),
                     (22.57, .021, -.08), (26.10, .025, .12)]:
    add(EFFECTS, t, card_shuffle(.45), gain, pan)
    event(t, "Short carton/handling movement", .45)
# Understated cart/transport texture; no literal engine, store or room ambience.
for t in [8.1, 15.1, 23.05]:
    duration = 1.75
    dt = np.arange(int(duration * SR)) / SR
    rumble = filt(RNG.normal(size=len(dt)), lo=100, hi=780)
    rumble *= .65 + .35 * np.sin(2 * np.pi * 7.3 * dt) ** 2
    add(EFFECTS, t, taper(rumble, .22, .4), .012, 0)
    event(t, "Very quiet textured movement", duration)

add(EFFECTS, 29.76, airy(1.3), .020, 0)
event(29.76, "Gentle transition breath into the quiet counter", 1.3)
add(EFFECTS, 31.12, glass_contact(), .038, .08)
event(31.12, "Glass settles onto the counter")
add(EFFECTS, 48.05, button(), .080, .04)
event(48.05, "Soft flavor-selection click")
add(EFFECTS, 52.78, button(.16), .047, .01)
event(52.78, "Faucet begins to open")
add(EFFECTS, 54.0, water(7.9), .63, .045)
event(54.0, "Soft illustrative pour with embedded small droplets", 7.9)
add(EFFECTS, 61.83, button(.14), .035, .01)
event(61.83, "Faucet closes")
for t in [71.0, 79.0, 87.0]:
    add(EFFECTS, t - .10, airy(.44), .013, -.08)
    add(EFFECTS, t + .14, button(.12), .025, .08)
    event(t - .10, "Restrained finish/style transition", .54)
add(EFFECTS, 94.20, glass_contact(), .020, .10)
event(94.20, "Quiet tactile punctuation before the final resolve")
EFFECTS = room(EFFECTS, .22)

# DC/high-frequency cleanup and inaudible final fade. Levels remain uncompressed.
SCORE = filt(SCORE, lo=48, hi=5800)
EFFECTS = filt(EFFECTS, lo=85, hi=5800)
for audio in [SCORE, EFFECTS]:
    end_start = int(98.0 * SR)
    audio[end_start:] *= np.cos(np.linspace(0, np.pi / 2, len(audio) - end_start))[:, None] ** 2
    audio[-int(.12 * SR):] = 0

# Predictable conservative stem peaks; parent can mix without accidental clipping.
def normalize_peak(audio, target_db):
    peak = float(np.max(np.abs(audio)))
    return audio * (10 ** (target_db / 20) / max(peak, 1e-12))

SCORE = normalize_peak(SCORE, -18.0)
EFFECTS = normalize_peak(EFFECTS, -22.0)


def stats(audio):
    p = float(np.max(np.abs(audio)))
    rms = float(np.sqrt(np.mean(audio ** 2)))
    return {"peak_dbfs": round(20 * math.log10(max(p, 1e-12)), 3),
            "rms_dbfs": round(20 * math.log10(max(rms, 1e-12)), 3),
            "dc_max": float(np.max(np.abs(np.mean(audio, axis=0)))),
            "duration_seconds": len(audio) / SR,
            "sample_rate": SR, "channels": 2}


(ROOT / "audio").mkdir(exist_ok=True)
for name, audio in [("score", SCORE), ("effects", EFFECTS)]:
    wavfile.write(ROOT / "audio" / f"{name}.wav", SR,
                  np.int16(np.clip(audio, -1, 1) * 32767))
    assert np.all(np.isfinite(audio)), name
    assert np.max(np.abs(audio[-4800:])) == 0, name

manifest = {
    "title": "One Less Errand — original music and sound design",
    "duration_seconds": DURATION,
    "sample_rate": SR,
    "channels": 2,
    "composition": "Original locally synthesized felt-key score, bass, tactile effects and room response.",
    "tempo": "Opening: a repeated 8-second cell with a 1.5-second pulse. Product: freely spaced harmonic phrases.",
    "key": "B minor/add nine resolving to relative D major",
    "stems": {"score": {"file": "audio/score.wav", **stats(SCORE)},
              "effects": {"file": "audio/effects.wav", **stats(EFFECTS)}},
    "mix_recommendation": {
        "score_initial_gain_db": 0,
        "effects_initial_gain_db": -1,
        "narration_priority": "Keep voice near -18 LUFS; duck score an additional 2–4 dB during narration with 120 ms attack and 500 ms release. Avoid pumping on individual syllables.",
        "pivot": "Leave a narration-free beat near 30–32 seconds. The score intentionally stops at 30 seconds and resumes at 32.4 seconds.",
        "master_target": "About -17 LUFS integrated, no higher than -1.5 dBTP. Do not raise the score just to reach loudness; voice remains the reference.",
        "water": "Illustrative, softly filtered texture at 54.0–61.9 seconds. Shift the effect with picture if the animated pour starts or stops elsewhere.",
    },
    "events": sorted(EVENTS, key=lambda e: (e["start"], e["stem"])),
}
for name in ["score", "effects"]:
    measurement = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(ROOT / "audio" / f"{name}.wav"),
         "-af", "ebur128=peak=true:framelog=verbose", "-f", "null", "-"],
        check=True, capture_output=True, text=True,
    ).stderr
    manifest["stems"][name]["integrated_lufs"] = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", measurement)[-1])
    manifest["stems"][name]["true_peak_dbfs"] = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", measurement)[-1])
(ROOT / "sound-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps(manifest["stems"], indent=2))
