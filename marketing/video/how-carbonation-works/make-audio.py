#!/usr/bin/env python3
"""Compose the film's original ambient score, restrained effects and stereo master.

Everything except the recorded Gemini voice is synthesized here. No stock sound,
samples, licensed music or additional generation service is used.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import butter, sosfilt

ROOT = Path(__file__).resolve().parent
AUDIO = ROOT / "audio"
RATE = 48000
SEED = 20261027
RNG = np.random.default_rng(SEED)


def write_json(name, data):
    (AUDIO / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def fade(length, attack=.08, release=.15):
    env = np.ones(length, np.float32)
    a, r = min(length, round(attack * RATE)), min(length, round(release * RATE))
    if a:
        env[:a] *= np.sin(np.linspace(0, np.pi/2, a)) ** 2
    if r:
        env[-r:] *= np.cos(np.linspace(0, np.pi/2, r)) ** 2
    return env


def filtered_noise(seconds, low, high):
    n = round(seconds * RATE)
    sound = RNG.standard_normal(n).astype(np.float32)
    sos = butter(3, [low, high], btype="bandpass", fs=RATE, output="sos")
    sound = sosfilt(sos, sound).astype(np.float32)
    sound /= max(1e-8, float(np.sqrt(np.mean(sound * sound))))
    return sound


def add(stem, mono, at, amplitude=1, pan=0):
    lo = max(0, round(at * RATE))
    n = min(len(mono), len(stem)-lo)
    if n <= 0:
        return
    angle = (pan + 1) * np.pi/4
    gains = np.array([np.cos(angle), np.sin(angle)], np.float32)
    stem[lo:lo+n] += mono[:n, None] * gains[None, :] * amplitude


def bell(frequency, seconds=2.8):
    t = np.arange(round(seconds * RATE)) / RATE
    signal = (np.sin(2*np.pi*frequency*t)*np.exp(-t*1.8)
              + .17*np.sin(2*np.pi*frequency*2.005*t)*np.exp(-t*3.7)
              + .045*np.sin(2*np.pi*frequency*3.997*t)*np.exp(-t*7.0))
    return signal.astype(np.float32) * fade(len(t), .006, .45)


def bubble(radius=1.0):
    seconds = .035 + .025 * radius
    t = np.arange(round(seconds * RATE)) / RATE
    f0 = 1400 / radius
    phase = 2*np.pi*(f0*t - f0*.36*t*t/seconds)
    env = (1-np.exp(-t/.0008))*np.exp(-t/(seconds*.18))
    sound = np.sin(phase)*env
    return sound.astype(np.float32)*fade(len(t), .001, .012)


def render_wav(raw, output, channels=2):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(RATE),
                    "-ac", str(channels), "-i", str(raw), "-c:a", "pcm_s24le", str(output)], check=True)


def loudness(path):
    process = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path),
                              "-af", "loudnorm=I=-16:TP=-1:LRA=8:print_format=json",
                              "-f", "null", "-"], check=True, capture_output=True, text=True)
    match = re.search(r"\{\s*\"input_i\".*?\}", process.stderr, re.S)
    return json.loads(match.group())


def main():
    timing = json.loads((AUDIO / "timing.json").read_text())
    duration = timing["frames"] / timing["fps"]
    n = round(duration * RATE)
    score = np.zeros((n, 2), np.float32)
    effects = np.zeros_like(score)
    voice_data = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(AUDIO / "voice-master.wav"),
                                          "-f", "f32le", "-ac", "1", "-ar", str(RATE), "-"])
    voice_mono = np.frombuffer(voice_data, dtype="<f4")
    voice = np.zeros(n, np.float32)
    voice[:min(n, len(voice_mono))] = voice_mono[:n]

    # Slow, open voicings support the explanation without a rhythmic metronome.
    harmony = [
        (0.0, 22.0, [146.832, 220.000, 329.628, 369.994]),       # D add9
        (19.0, 43.5, [123.471, 184.997, 246.942, 293.665]),      # B minor7
        (40.0, 71.8, [130.813, 195.998, 293.665, 369.994]),      # Open Lydian colour
        (68.5, 85.4, [164.814, 246.942, 329.628, 391.995]),      # E minor
        (81.5, duration, [146.832, 220.000, 293.665, 369.994]),   # D major
    ]
    for start, end, frequencies in harmony:
        count = round((end-start)*RATE)
        t = np.arange(count, dtype=np.float64)/RATE
        env = fade(count, 2.3, min(3.0, (end-start)/3))
        for j, f in enumerate(frequencies):
            phase = j*.91
            slow = .88+.12*np.sin(2*np.pi*(.047+j*.007)*t+phase)
            for channel, detune in [(0, .9997), (1, 1.0003)]:
                tone = (np.sin(2*np.pi*f*detune*t+phase)
                        + .065*np.sin(2*np.pi*f*2.002*detune*t+phase))
                lo=round(start*RATE)
                score[lo:lo+count, channel] += (tone*env*slow*.0028).astype(np.float32)
    # A small original glass-like figure at reveals and the final resolution.
    notes = [(0.15,587.33,-.22),(.82,880,.18),(7.9,659.26,-.1),
             (10.0,587.33,.2),(19.7,493.88,-.15),(31.0,739.99,.1),
             (41.1,587.33,-.1),(55.05,659.26,.15),(69.25,783.99,-.2),
             (82.8,739.99,.16),(96.4,587.33,-.12),(100.1,440,.12),(100.35,587.33,-.1)]
    for at, f, pan in notes:
        sound=bell(f)
        add(score,sound,at,.012,pan)
        add(score,sound,at+.143,.0015,-pan)
    score *= .012 / max(1e-8,float(np.sqrt(np.mean(score**2))))

    # Enclosure motion: a short air movement and quiet, rounded mechanical ticks.
    add(effects, filtered_noise(3.1,280,5200)*fade(round(3.1*RATE),.75,1.2),10.0,.007,-.3)
    for at, pan in [(10.35,-.35),(11.10,.25),(12.05,.1)]:
        t=np.arange(round(.12*RATE))/RATE
        tick=(np.sin(2*np.pi*340*t)+.3*np.sin(2*np.pi*690*t))*np.exp(-t*62)
        add(effects,tick.astype(np.float32)*fade(len(t),.002,.03),at,.012,pan)

    # Finite gas admission at the plain bottom port, followed by a quiet hold.
    gas_start, gas_end = 20.7, 30.4
    add(effects,filtered_noise(gas_end-gas_start,350,2300)*fade(round((gas_end-gas_start)*RATE),.65,1.0),gas_start,.0025,-.24)
    for at in np.arange(gas_start+.10,gas_end-.4,.105):
        jitter=float(RNG.uniform(-.03,.03));radius=float(RNG.uniform(.85,1.8))
        gain=float(RNG.uniform(.005,.013))
        add(effects,bubble(radius),at+jitter,gain,float(RNG.uniform(-.4,.08)))

    # The water texture follows the photographed jet window and ends at pump-off.
    jet_start, jet_end = 32.6, 68.5
    jet=filtered_noise(jet_end-jet_start,800,8500)
    t=np.arange(len(jet))/RATE
    jet*=((.82+.10*np.sin(2*np.pi*3.1*t)+.08*np.sin(2*np.pi*9.3*t))
          *fade(len(jet),1.15,.75))
    add(effects,jet,jet_start,.0058,-.08)
    mixing_start,mixing_end=42.5,61.4
    add(effects,filtered_noise(mixing_end-mixing_start,260,3100)*fade(round((mixing_end-mixing_start)*RATE),1.0,1.6),mixing_start,.0035,.08)
    for at in np.arange(mixing_start,mixing_end,.065):
        add(effects,bubble(float(RNG.uniform(.55,1.1))),float(at+RNG.uniform(-.015,.015)),
            float(RNG.uniform(.0018,.006)),float(RNG.uniform(-.32,.32)))

    # A restrained refrigerant flow; this does not turn heat graphics into rays.
    add(effects,filtered_noise(12.0,230,1900)*fade(round(12*RATE),1.5,2.0),70.5,.0038,.18)

    # The two pictured streams begin together; the sound ends with the pour.
    pour_start,pour_end=87.5,95.3
    pour=filtered_noise(pour_end-pour_start,280,7800)
    t=np.arange(len(pour))/RATE
    pour*=((.8+.12*np.sin(2*np.pi*5.3*t)+.08*np.sin(2*np.pi*13.1*t))
           *fade(len(pour),.30,.22))
    add(effects,pour,pour_start,.0088,.05)
    for at in np.arange(pour_start+.15,pour_end,.09):
        add(effects,bubble(float(RNG.uniform(.5,.9))),float(at),.003,float(RNG.uniform(-.2,.25)))
    for start,end,amp in [(.45,7.8,.0011),(95.3,101.65,.0019)]:
        sound=filtered_noise(end-start,3200,11500)*fade(round((end-start)*RATE),.6,1.2)
        add(effects,sound,start,amp,.04)

    # A slow speech-following reduction leaves the narration in front without pumping.
    block=480
    rms=np.sqrt(np.mean(np.pad(voice,(0,(-len(voice))%block)).reshape(-1,block)**2,axis=1))
    smooth=gaussian_filter1d(np.minimum(1,rms/.025),10)
    speech=np.interp(np.arange(n)/block,np.arange(len(smooth)),smooth).astype(np.float32)
    score*= (1-.40*speech)[:,None]
    effects*= (1-.22*speech)[:,None]
    final_fade=fade(n,.05,1.0)
    score*=final_fade[:,None];effects*=final_fade[:,None]
    premix=np.repeat(voice[:,None],2,axis=1)+score+effects

    with tempfile.TemporaryDirectory(prefix="hsm-carbonator-sound-") as temporary:
        work=Path(temporary)
        for name,data in [("score",score),("effects",effects)]:
            raw=work/(name+".f32");data.astype("<f4").tofile(raw)
            render_wav(raw,AUDIO/(name+"-stem.wav"))
        raw=work/"premix.f32";premix.astype("<f4").tofile(raw)
        premix_wav=work/"premix.wav";render_wav(raw,premix_wav)
        measured=loudness(premix_wav)
        filt=("loudnorm=I=-16:TP=-1:LRA=8:linear=true:"
              f"measured_I={measured['input_i']}:measured_TP={measured['input_tp']}:"
              f"measured_LRA={measured['input_lra']}:measured_thresh={measured['input_thresh']}:"
              f"offset={measured['target_offset']}:print_format=json")
        normalization=subprocess.run(["ffmpeg","-hide_banner","-y","-i",str(premix_wav),
                                      "-af",filt,"-ar",str(RATE),"-ac","2","-c:a","pcm_s24le",
                                      str(AUDIO/"mix-master.wav")],check=True,capture_output=True,text=True)
        norm_match=re.search(r"\{\s*\"input_i\".*?\}",normalization.stderr,re.S)
        final=loudness(AUDIO/"mix-master.wav")
    source_provenance=json.loads((AUDIO/"provenance.json").read_text())
    report={"duration":duration,"sample_rate":RATE,"channels":2,"bit_depth":24,
            "voice_service":source_provenance["service"],"voice_model":source_provenance["model"],
            "voice":source_provenance["voice"],"score":"Original procedural ambient composition",
            "effects":"Original procedural sound design; scene-following illustrative textures",
            "stock_assets":[],"random_seed":SEED,
            "master_integrated_lufs":float(final["input_i"]),
            "master_true_peak_dbtp":float(final["input_tp"]),
            "master_loudness_range_lu":float(final["input_lra"]),
            "normalization":json.loads(norm_match.group()) if norm_match else {},
            "premix_loudness":measured,"voice_word_speed_changed":False,
            "master_sha256":hashlib.sha256((AUDIO/"mix-master.wav").read_bytes()).hexdigest(),
            "stems":{"voice":"voice-master.wav","score":"score-stem.wav","effects":"effects-stem.wav"},
            "sound_clock":{"enclosure":[10.0,13.1],"gas_admission":[gas_start,gas_end],
                           "jet":[jet_start,jet_end],"entrainment":[mixing_start,mixing_end],
                           "evaporator_flow":[70.5,82.5],"pour":[pour_start,pour_end],
                           "closing_fizz":[95.3,101.65]},
            "score_harmony":[{"start":s,"end":e,"frequencies_hz":f} for s,e,f in harmony],
            "score_notes":[{"at":at,"frequency_hz":f,"pan":pan} for at,f,pan in notes]}
    write_json("audio-report.json",report)
    print(json.dumps({k:report[k] for k in ["duration","master_integrated_lufs","master_true_peak_dbtp",
                                            "master_loudness_range_lu","master_sha256"]},indent=2))


if __name__=="__main__":
    main()
