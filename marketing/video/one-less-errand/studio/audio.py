#!/usr/bin/env python3
"""Compose and mix the 64-second One Less Errand film at 48 kHz.

The score, tactile sound effects and room responses are original synthesis.
The dry voice is edited from the project's recorded narration; no phrases are
time compressed. Run with tools/video-venv/bin/python.
"""
from __future__ import annotations

import json
import math
import re
import subprocess
import textwrap
from pathlib import Path

import numpy as np
from scipy import signal
from scipy.io import wavfile

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
PARENT = ROOT.parent
SR = 48000
DURATION = 64.0
N = round(SR * DURATION)
RNG = np.random.default_rng(814205)
EVENTS: list[dict] = []


def run(args):
    return subprocess.run(args, check=True, capture_output=True, text=True)


def filt(x, lo=None, hi=None, order=2):
    if lo and hi:
        cutoff, kind = [lo, hi], "bandpass"
    else:
        cutoff, kind = (lo, "highpass") if lo else (hi, "lowpass")
    return signal.sosfilt(signal.butter(order, cutoff, btype=kind, fs=SR, output="sos"), x, axis=0)


def taper(x, attack=.008, release=.08):
    x = np.asarray(x).copy()
    a, r = min(len(x), round(attack * SR)), min(len(x), round(release * SR))
    if a:
        x[:a] *= np.sin(np.linspace(0, np.pi / 2, a)) ** 2
    if r:
        x[-r:] *= np.cos(np.linspace(0, np.pi / 2, r)) ** 2
    return x


def add(dest, at, source, gain=1, pan=0):
    start = round(at * SR)
    stop = min(start + len(source), len(dest))
    if start < 0 or stop <= start:
        raise ValueError(f"Event outside film: {at}")
    angle = (np.clip(pan, -1, 1) + 1) * np.pi / 4
    dest[start:stop, 0] += source[:stop - start] * gain * np.cos(angle)
    dest[start:stop, 1] += source[:stop - start] * gain * np.sin(angle)


def log(at, description, duration=0, stem="score"):
    EVENTS.append({"start": round(at, 3), "end": round(at + duration, 3), "stem": stem, "description": description})


def hz(midi):
    return 440 * 2 ** ((midi - 69) / 12)


def key(midi, duration=4.7, muted=False):
    """A softly struck, slightly inharmonic string with a felt transient."""
    t = np.arange(round(duration * SR)) / SR
    f, x = hz(midi), np.zeros_like(t)
    life = (.38 if muted else 1.9) * (1 + (60 - midi) * .007)
    for partial, amp, decay in [(1, 1, 1), (2, .24, .58), (3, .085, .39), (4, .03, .25), (5, .008, .17)]:
        x += amp * np.sin(2 * np.pi * f * partial * (1 + .000065 * partial**2) * t) * np.exp(-t / (life * decay))
    x += .09 * np.sin(2 * np.pi * f * 1.001 * t + .31) * np.exp(-t / (life * .8))
    x += filt(RNG.normal(size=len(t)), lo=350, hi=3800) * np.exp(-t / .014) * .075
    return taper(filt(x, hi=4300 if muted else 6200), .006, .24)


def bass(midi, duration=2.5):
    t = np.arange(round(duration * SR)) / SR
    f = hz(midi)
    x = np.sin(2 * np.pi * f * t) + .23 * np.sin(2 * np.pi * 2 * f * t) + .055 * np.sin(2 * np.pi * 3 * f * t)
    return taper(x * np.exp(-t / 1.5), .025, .16)


def pad(notes, duration):
    """Very soft bowed harmonics; no exposed sustained oscillator lead."""
    t = np.arange(round(duration * SR)) / SR
    x = np.zeros_like(t)
    for i, midi in enumerate(notes):
        f = hz(midi)
        for detune, phase in [(.9988, .31 + i), (1.0012, .82 + i * 2)]:
            breath = .98 + .02 * np.sin(2 * np.pi * (.19 + .017 * i) * t + i)
            x += breath * (np.sin(2 * np.pi * f * detune * t + phase) + .12 * np.sin(4 * np.pi * f * detune * t + phase)) / (2 * len(notes))
    return taper(filt(x, hi=1700), 1.15, 1.65)


def click(duration=.15, pitch=310, soft=False):
    t = np.arange(round(duration * SR)) / SR
    n = filt(RNG.normal(size=len(t)), lo=170, hi=2600 if soft else 5200)
    x = n * np.exp(-t / .008) + .19 * np.sin(2 * np.pi * pitch * t) * np.exp(-t / .024)
    return taper(x, .0008, .02)


def brush(duration=.13):
    t = np.arange(round(duration * SR)) / SR
    n = filt(RNG.normal(size=len(t)), lo=2900, hi=8200)
    return taper(n * np.exp(-t / .023), .004, .025)


def thud(duration=.28):
    t = np.arange(round(duration * SR)) / SR
    phase = 2 * np.pi * (49 * t + 26 * .014 * (1 - np.exp(-t / .014)))
    return taper(np.sin(phase) * np.exp(-t / .065), .001, .05)


def contact(kind="can", duration=.55):
    t = np.arange(round(duration * SR)) / SR
    modes = ([(162, .8, .04), (488, .38, .052), (914, .14, .034), (1748, .055, .027)] if kind == "can" else
             [(208, .8, .035), (473, .20, .024), (1201, .055, .021)])
    x = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t / d) for f, a, d in modes)
    x += .75 * filt(RNG.normal(size=len(t)), lo=85, hi=1900) * np.exp(-t / .009)
    return taper(x, .001, .06)


def handling(duration=.42):
    t = np.arange(round(duration * SR)) / SR
    n = filt(RNG.normal(size=len(t)), lo=180, hi=3900)
    amp = np.sin(np.pi * t / duration) ** 2 * (.45 + .55 * np.sin(2 * np.pi * 12.7 * t) ** 2)
    return taper(n * amp, .02, .04)


def glass(duration=1.0):
    t = np.arange(round(duration * SR)) / SR
    x = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t / d) for f, a, d in
            [(412, .40, .075), (706, .27, .105), (1112, .16, .12), (1840, .08, .09), (2913, .025, .07)])
    x += .45 * filt(RNG.normal(size=len(t)), lo=140, hi=1900) * np.exp(-t / .007)
    return taper(x, .001, .18)


def pour(duration=6.65):
    """A close stream, rising liquid level, and embedded bubble transients."""
    t = np.arange(round(duration * SR)) / SR
    air = filt(RNG.normal(size=len(t)), lo=1700, hi=7800)
    body = filt(RNG.normal(size=len(t)), lo=190, hi=1350)
    splash = filt(RNG.normal(size=len(t)), lo=520, hi=4600)
    envelope = .7 + .11 * np.sin(2 * np.pi * 2.13 * t) + .06 * np.sin(2 * np.pi * 6.79 * t)
    x = (.070 * air + .15 * splash + .095 * body) * envelope
    # Empty-glass body warms and lowers as the water level rises.
    resonance_phase = 2 * np.pi * (920 * t - 220 * t**2 / duration)
    x += .015 * np.sin(resonance_phase) * (.3 + .7 * np.sin(2 * np.pi * 10.1 * t) ** 2)
    for at in np.cumsum(RNG.uniform(.055, .19, 150)):
        if at > duration - .15:
            break
        dt = np.arange(round(.042 * SR)) / SR
        f = RNG.uniform(620, 2100) * (1 - .19 * at / duration)
        bubble = np.sin(2 * np.pi * f * (.36 * dt + .009 * (1 - np.exp(-dt / .009)))) * np.exp(-dt / .007)
        start = round(at * SR)
        x[start:start + len(dt)] += taper(bubble, .0006, .005) * RNG.uniform(.009, .031)
    return taper(x, .17, .28)


def fizz(duration=4.2):
    t = np.arange(round(duration * SR)) / SR
    x = filt(RNG.normal(size=len(t)), lo=3200, hi=10500) * .018 * np.exp(-t / 2.2)
    for at in np.cumsum(RNG.uniform(.015, .10, 220)):
        if at > duration - .05:
            break
        dt = np.arange(round(.018 * SR)) / SR
        f = RNG.uniform(2500, 6900)
        tick = np.sin(2 * np.pi * f * dt * (1 - 9 * dt)) * np.exp(-dt / .0022)
        atn = round(at * SR)
        x[atn:atn + len(dt)] += taper(tick, .0003, .003) * RNG.uniform(.007, .025) * np.exp(-at / 2.8)
    return taper(x, .07, .45)


def room(src, wet=.35, decay=.42):
    result = src.copy()
    for channel in range(2):
        t = np.arange(round(2.5 * SR)) / SR
        ir = filt(RNG.normal(size=len(t)), lo=220, hi=4800) * np.exp(-t / decay) * .00062
        ir[:round(.033 * SR)] = 0
        for delay, gain in [(.039, .13), (.083, .079), (.141, .039), (.233, .023)]:
            ir[round((delay + channel * .008) * SR)] += gain
        result[:, channel] += signal.fftconvolve(src[:, channel], ir, mode="full")[:len(src)] * wet
    return result


def write_wav(path, samples):
    if not np.all(np.isfinite(samples)) or np.max(np.abs(samples)) >= 1:
        raise ValueError(f"Invalid audio or clipping in {path}")
    wavfile.write(path, SR, np.int16(samples * 32767))


def measure(path):
    result = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af",
                  "loudnorm=I=-17:TP=-1.5:LRA=20:print_format=json", "-f", "null", "-"])
    return json.loads(re.search(r'\{\s*"input_i"[\s\S]*?\}', result.stderr).group())


def stamp(seconds, separator="."):
    ms = round(seconds * 1000)
    hour, ms = divmod(ms, 3600000)
    minute, ms = divmod(ms, 60000)
    second, ms = divmod(ms, 1000)
    return f"{hour:02}:{minute:02}:{second:02}{separator}{ms:03}"


def make_voice():
    words = json.loads((PARENT / "narration-words.json").read_text())
    sr, source = wavfile.read(PARENT / "audio/narration.wav")
    source = source.astype(float) / 32768
    source = signal.resample_poly(source, SR, sr)
    voice = np.zeros((N, 2))
    # Each edit is an unchanged passage from the recorded performance.
    passages = [
        ("wish", .8, 0.0, 1.38, ["You wanted a glass of soda."]),
        ("store", 4.8, 2.12, 4.78, ["Somehow, that became a trip to the store."]),
        ("cart", 8.5, 5.64, 6.56, ["A case in the cart."]),
        ("car", 10.9, 7.2, 7.82, ["Into the car."]),
        ("kitchen-carry", 12.15, 8.28, 9.04, ["Into the kitchen."]),
        ("shelf-carry", 13.35, 9.74, 10.34, ["Onto a shelf."]),
        ("again", 14.7, 11.4, 13.84, ["And when the cans are gone,", "you do it all again."]),
        ("waiting", 20.5, 14.98, 17.26, ["What if the next glass was already waiting?"]),
        ("under", 26.0, 21.4, 25.3, ["Cold carbonated water.", "Two flavors, ready under the counter."]),
        ("flavor", 31.4, 26.42, 27.06, ["Choose your flavor."]),
        ("faucet", 34.8, 28.1, 28.74, ["Open the faucet."]),
        ("glass", 37.5, 29.34, 31.52, ["Cold soda, straight into your glass."]),
        ("home", 53.2, 32.56, 34.52, ["With a faucet that feels at home in your kitchen."]),
        ("closing", 59.2, 46.9, 49.44, ["A glass of soda.", "One less errand."]),
    ]
    edits, captions = [], []
    normal = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
    for name, at, first, last, phrases in passages:
        spoken = [w for w in words if w["start"] >= first - .001 and w["end"] <= last + .001]
        if [normal(w["word"]) for w in spoken] != [normal(w) for text in phrases for w in text.split()]:
            raise ValueError(f"Narration text mismatch at {name}")
        begin = max(0, first - .16)
        end = min(len(source) / SR, last + .24)
        chunk = taper(source[round(begin * SR):round(end * SR)], .007, .035)
        add(voice, at - first + begin, chunk, math.sqrt(2))
        shift, cursor = at - first, 0
        for text in phrases:
            count = len(text.split())
            selected = spoken[cursor:cursor + count]
            captions.append({"start": round(selected[0]["start"] + shift, 3),
                             "end": round(selected[-1]["end"] + shift + .27, 3), "text": text})
            cursor += count
        edits.append({"id": name, "source_start": round(begin, 3), "source_end": round(end, 3),
                      "start": round(at - first + begin, 3), "end": round(at + end - first, 3),
                      "first_word_at": at, "last_word_at": round(at + last - first, 3), "text": " ".join(phrases)})
    for i, caption in enumerate(captions):
        next_start = captions[i + 1]["start"] if i + 1 < len(captions) else 63.7
        caption["end"] = round(min(next_start - .09, max(caption["end"], caption["start"] + 1.05)), 3)
    write_wav(OUT / "voice-edited.wav", voice)
    # A broad low-frequency cleanup and gentle peak compression keep the dry
    # intimate recording present without flattening its pauses and inflection.
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(OUT / "voice-edited.wav"),
         "-af", "highpass=f=72,acompressor=threshold=0.105:ratio=2.2:attack=9:release=95:knee=3:makeup=1.16,loudnorm=I=-18.4:TP=-3.0:LRA=12",
         "-ar", str(SR), str(OUT / "voice-master.wav")])
    for suffix, separator in [("vtt", "."), ("srt", ",")]:
        entries = []
        for i, cap in enumerate(captions):
            text = "\n".join(textwrap.wrap(cap["text"], 42))
            prefix = f"{i + 1}\n" if suffix == "srt" else ""
            entries.append(f"{prefix}{stamp(cap['start'], separator)} --> {stamp(cap['end'], separator)}\n{text}")
        (OUT / f"film.{suffix}").write_text(("WEBVTT\n\n" if suffix == "vtt" else "") + "\n\n".join(entries) + "\n")
    return edits, captions


def make_score():
    chore = np.zeros((N, 2))
    product = np.zeros_like(chore)
    add(chore, .28, key(74, 4), .038, -.12)
    add(chore, 2.6, key(69, 3.7), .022, .17)
    log(.28, "A bare two-note wish: D and A, answered by the closing cadence", 4.22)
    # A restrained 80 BPM pulse accumulates with the work of stocking cans.
    for bar, (at, voicing, root) in enumerate([
        (4.5, [54, 57, 61, 66], 35), (7.5, [55, 59, 62, 66], 31),
        (10.5, [54, 57, 61, 66], 35), (14.25, [54, 57, 61, 64], 42),
    ]):
        add(chore, at, bass(root, 3.2), .055, 0)
        for offset, note in [(0, voicing[0]), (.75, voicing[2]), (1.5, voicing[1]), (2.25, voicing[3])]:
            add(chore, at + offset, key(note, 1.7, True), .057 if offset in (0, 1.5) else .043, -.14 if offset < 1.5 else .14)
            add(chore, at + offset, click(.15, soft=True), .016, -.25)
        add(chore, at + .03, thud(), .030, .03)
        add(chore, at + 1.5, thud(), .021, .03)
        for offset in [.375, 1.125, 1.875, 2.625]:
            add(chore, at + offset, brush(), .011 + bar * .0015, .22)
        if bar >= 1:
            add(chore, at + 2.625, key(voicing[2] + 12, .7, True), .016, .26)
    # The repeated action runs out of steam during the reset; all room tails
    # are cleared before the new kitchen world arrives at 19.25 seconds.
    add(chore, 17.25, key(54, 1.6, True), .038, -.12)
    add(chore, 18.0, key(54, 1.7, True), .027, -.12)
    chore = room(chore, .38, .24)
    a, b = round(18.15 * SR), round(19.15 * SR)
    chore[a:b] *= np.cos(np.linspace(0, np.pi / 2, b - a))[:, None] ** 2
    chore[b:] = 0
    log(4.5, "B-minor errand cell: muted strings, soft bass, brushed pulse and tactile wood", 13.5)
    log(18, "The errand cell empties and its room tail disappears", 1.15)
    log(19.15, "Clean breath before the spacious kitchen harmony", .8)
    progression = [
        (19.95, [50, 57, 61, 66, 69], 38, 6.0),
        (25.5, [55, 57, 62, 66], 43, 5.7),
        (30.75, [54, 57, 62, 66], 47, 4.6),
        (34.5, [52, 59, 61, 64], 45, 3.5),
        (36.5, [50, 57, 59, 64, 66], 38, 7.6),
        (43.5, [55, 62, 66, 69], 43, 4.5),
        (47.5, [54, 57, 61, 64], 42, 3.5),
        (50.0, [54, 57, 62, 66], 47, 3.5),
        (52.5, [55, 57, 62, 66], 43, 4.4),
        (56.25, [52, 57, 59, 64], 45, 3.0),
        (58.5, [50, 57, 61, 66, 69], 38, 5.35),
    ]
    for at, voicing, root, duration in progression:
        for i, note in enumerate(voicing):
            add(product, at + i * .067, key(note, min(5.3, duration + .6)), .033 * (1 - i * .065), (i - (len(voicing) - 1) / 2) * .11)
        add(product, at + .055, bass(root, min(4, duration)), .039, -.015)
        add(product, at, pad(voicing[1:], duration), .021 if at < 36 else .026, .05)
    # An unhurried upper phrase has room to appear when the narration rests.
    for at, note, gain in [
        (23.7, 74, .025), (24.45, 69, .018),
        (29.95, 71, .020), (33.30, 69, .021),
        (40.8, 66, .023), (42.0, 69, .020),
        (45.35, 74, .025), (48.7, 73, .022),
        (51.1, 71, .023), (56.55, 69, .023),
        (57.3, 64, .021), (61.9, 66, .029), (62.75, 62, .030),
    ]:
        add(product, at, key(note, min(4.0, 64 - at)), gain, -.14 if note < 70 else .17)
    product = room(product, .80, .48)
    score = filt(chore + product, lo=37, hi=9200)
    # No rhythmic insistence once the faucet is in the home; the physical
    # actions and water supply the forward movement.
    log(19.95, "Open D-major-nine harmony, warm strings and a restrained upper phrase", 16.55)
    log(36.5, "D-six/nine holds the pour; percussion gives way to water", 7)
    log(43.5, "Bubbles in a quiet harmonic pocket, followed by the two design portraits", 9)
    log(58.5, "D-major cadence; two descending felt notes finish the original opening phrase", 5.5)
    fade = round(62.8 * SR)
    score[fade:] *= np.cos(np.linspace(0, np.pi / 2, N - fade))[:, None] ** 2
    score[-round(.08 * SR):] = 0
    return score


def make_effects():
    fx = np.zeros((N, 2))
    for at, kind, gain, pan in [(4.67, "can", .071, -.08), (7.7, "case", .074, -.04),
                               (10.67, "case", .064, .05), (11.92, "case", .055, -.03),
                               (13.17, "case", .057, .08), (14.48, "can", .061, -.07),
                               (16.92, "can", .026, .06), (18.08, "can", .021, -.05)]:
        add(fx, at, contact(kind), gain, pan)
        log(at, f"Close {kind} contact", .55, "effects")
    for at, gain in [(7.57, .027), (10.49, .024), (11.74, .022), (13, .023)]:
        add(fx, at, handling(.4), gain, -.08)
        log(at, "Carton and hand movement at the cut", .4, "effects")
    # A little low wheel texture supports the supermarket passage without
    # adding a literal noisy supermarket recording.
    t = np.arange(round(2.25 * SR)) / SR
    wheel = filt(RNG.normal(size=len(t)), lo=90, hi=630) * (.55 + .45 * np.sin(2 * np.pi * 7.7 * t) ** 2)
    add(fx, 8.0, taper(wheel, .28, .4), .022, -.06)
    log(8, "Restrained cart-wheel movement", 2.25, "effects")
    add(fx, 19.48, glass(), .066, .06)
    log(19.48, "An empty glass settles into the quiet kitchen", 1, "effects")
    add(fx, 32.4, click(.13, pitch=340, soft=True), .070, .03)
    log(32.4, "Damped flavor-selection contact", .13, "effects")
    add(fx, 35.25, click(.15, pitch=236, soft=True), .075, .01)
    add(fx, 35.28, handling(.16), .017, 0)
    log(35.25, "Faucet lever engages: a small mechanical detent and finger movement", .19, "effects")
    add(fx, 36.6, pour(6.64), .58, .055)
    log(36.6, "Close carbonated-water stream; liquid level changes the resonant glass body", 6.64, "effects")
    add(fx, 43.24, click(.12, pitch=240, soft=True), .025, .01)
    add(fx, 43.25, fizz(4.2), .73, .10)
    log(43.24, "A quiet release, then fine close bubbles with small irregular pops", 4.21, "effects")
    # The style shots remain composed and quiet; no transition swooshes.
    add(fx, 57.35, glass(), .033, .055)
    log(57.35, "Soft glass contact returns us to the kitchen", 1, "effects")
    fx = filt(room(fx, .16, .19), lo=66, hi=10700)
    fx[round(62.9 * SR):] *= np.cos(np.linspace(0, np.pi / 2, N - round(62.9 * SR)))[:, None] ** 2
    fx[-round(.08 * SR):] = 0
    return fx


def main():
    OUT.mkdir(exist_ok=True)
    edits, captions = make_voice()
    score, fx = make_score(), make_effects()
    # A gentle phrase-level dip is inaudible as an effect and keeps the voice
    # in front; it never follows individual words or pumps with percussion.
    time = np.arange(N) / SR
    duck = np.ones(N)
    for edit in edits:
        attack = np.clip((time - (edit["first_word_at"] - .18)) / .18, 0, 1)
        release = np.clip((edit["last_word_at"] + .65 - time) / .65, 0, 1)
        duck = np.minimum(duck, 1 - (1 - 10 ** (-3.5 / 20)) * np.minimum(attack, release))
    score *= duck[:, None]
    # Music is allowed to draw breath in the physical pour and hero pauses.
    score *= 1.05
    write_wav(OUT / "score.wav", score)
    write_wav(OUT / "effects.wav", fx)
    _, voice_int = wavfile.read(OUT / "voice-master.wav")
    voice = voice_int.astype(float) / 32768
    mix = voice + score + fx
    write_wav(OUT / "mix-premaster.wav", mix)
    premaster = measure(OUT / "mix-premaster.wav")
    norm = "loudnorm=I=-17:TP=-1.5:LRA=20:linear=true:" + ":".join(
        f"{key}={premaster[value]}" for key, value in
        [("measured_I", "input_i"), ("measured_TP", "input_tp"), ("measured_LRA", "input_lra"),
         ("measured_thresh", "input_thresh"), ("offset", "target_offset")])
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(OUT / "mix-premaster.wav"),
         "-af", norm, "-ar", str(SR), "-c:a", "pcm_s16le", str(OUT / "mix-master.wav")])
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(OUT / "mix-master.wav"),
         "-c:a", "libmp3lame", "-b:a", "192k", str(OUT / "audio-review.mp3")])
    levels = {name: measure(OUT / f"{name}.wav") for name in ["voice-master", "score", "effects", "mix-master"]}
    report = {"duration_seconds": DURATION, "sample_rate": SR, "channels": 2, "bits_per_sample": 16,
              "frames": N, "picture_frames": 1536, "picture_fps": 24,
              "composition": "Original synthesized 80 BPM muted-string errand groove, spacious D-major product score, tactile contacts, glass, carbonated water and fizz.",
              "source_voice": "../audio/narration.wav", "voice_editing": "Original pacing; no time stretching. Unused style narration omitted.",
              "master_target": {"integrated_lufs": -17, "true_peak_ceiling_dbtp": -1.5},
              "levels": {name: {"integrated_lufs": float(value["input_i"]), "true_peak_dbtp": float(value["input_tp"]),
                                "loudness_range_lu": float(value["input_lra"])} for name, value in levels.items()},
              "narration_edits": edits, "captions": captions, "events": sorted(EVENTS, key=lambda e: (e["start"], e["stem"]))}
    (OUT / "audio-report.json").write_text(json.dumps(report, indent=2) + "\n")
    plan = {"duration": DURATION, "fps": 24, "audio_master": "out/mix-master.wav", "captions_file": "out/film.vtt",
            "tempo_bpm": 80, "tonal_arc": "B-minor/add-nine errand pulse opens into D-major/nine. Final D-major cadence answers the opening wish.",
            "narration_edits": edits, "captions": captions, "events": report["events"]}
    (ROOT / "audio-plan.json").write_text(json.dumps(plan, indent=2) + "\n")
    print(json.dumps({"master": str(OUT / "mix-master.wav"), "levels": report["levels"], "narration_passages": len(edits), "captions": len(captions)}, indent=2))


if __name__ == "__main__":
    main()
