#!/usr/bin/env python3
"""Compose the 18-second film around one uninterrupted voice performance.

Run with tools/video-venv/bin/python. --out selects a separate sound build;
the default is studio/out. The picture clock comes from story.json.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import textwrap
import numpy as np
from scipy import signal
from scipy.io import wavfile
from errands import normalized_events

ROOT = Path(__file__).resolve().parent
SR, FPS = 48000, 24
RNG = np.random.default_rng(301814)


def run(args):
    return subprocess.run(list(map(str, args)), check=True, capture_output=True, text=True)


def filt(x, lo=None, hi=None, order=2):
    cutoff, kind = ([lo, hi], 'bandpass') if lo and hi else ((lo, 'highpass') if lo else (hi, 'lowpass'))
    return signal.sosfilt(signal.butter(order, cutoff, btype=kind, fs=SR, output='sos'), x, axis=0)


def taper(x, attack=.004, release=.06):
    x = np.asarray(x).copy()
    a, r = min(len(x), round(attack*SR)), min(len(x), round(release*SR))
    if a:
        x[:a] *= np.sin(np.linspace(0, np.pi/2, a))**2
    if r:
        x[-r:] *= np.cos(np.linspace(0, np.pi/2, r))**2
    return x


def add(dest, at, source, gain=1, pan=0):
    start = round(at*SR)
    stop = min(len(dest), start+len(source))
    if start < 0 or stop <= start:
        return
    angle = (np.clip(pan, -1, 1)+1)*np.pi/4
    dest[start:stop, 0] += source[:stop-start]*gain*np.cos(angle)
    dest[start:stop, 1] += source[:stop-start]*gain*np.sin(angle)


def hz(midi):
    return 440*2**((midi-69)/12)


def pluck(midi, duration=1.6, damped=False):
    """A short double-course string with a small wooden attack."""
    t = np.arange(round(duration*SR))/SR
    f, x = hz(midi), np.zeros_like(t)
    life = .30 if damped else .78
    for partial in range(1, 9):
        amp = (-1 if partial % 3 == 0 else 1)*.78**(partial-1)/partial
        envelope = np.exp(-t/(life/(1+.31*(partial-1))))
        x += amp*envelope*(np.sin(2*np.pi*f*partial*t)+.29*np.sin(2*np.pi*f*partial*1.0024*t+.17))
    x += filt(RNG.normal(size=len(t)), lo=700, hi=5300)*np.exp(-t/.008)*.048
    return taper(filt(x, hi=4700), .0025, .14)


def struck(midi, duration=3.5):
    """A rounded struck tine; every sustained note has a physical decay."""
    t = np.arange(round(duration*SR))/SR
    f = hz(midi)
    x = (np.sin(2*np.pi*f*t)*np.exp(-t/1.30)
         +.20*np.sin(2*np.pi*f*2.002*t)*np.exp(-t/.55)
         +.055*np.sin(2*np.pi*f*3.006*t)*np.exp(-t/.24))
    return taper(x, .009, .24)


def bass(midi, duration=.85):
    t = np.arange(round(duration*SR))/SR
    f = hz(midi)
    return taper((np.sin(2*np.pi*f*t)+.19*np.sin(4*np.pi*f*t))*np.exp(-t/.27), .009, .07)


def rim(duration=.075):
    t = np.arange(round(duration*SR))/SR
    x = filt(RNG.normal(size=len(t)), lo=850, hi=3800)*np.exp(-t/.008)
    return taper(x+.13*np.sin(2*np.pi*410*t)*np.exp(-t/.014), .0007, .015)


def case_contact(index):
    """One dry graphic weight contact, without imaginary handling Foley."""
    t = np.arange(round((.25+index*.025)*SR))/SR
    f = [155, 126, 102][index]
    x = (.58*np.sin(2*np.pi*f*t)*np.exp(-t/(.027+index*.006))
         +.18*np.sin(2*np.pi*f*2.19*t)*np.exp(-t/.018)
         +filt(RNG.normal(size=len(t)), lo=180, hi=2900)*np.exp(-t/.014)*.44)
    x = taper(x, .0007, .05)
    return x/max(np.max(np.abs(x)), 1e-9)


def fizz(duration, strength=1):
    t = np.arange(round(duration*SR))/SR
    x = filt(RNG.normal(size=len(t)), lo=3600, hi=11200)*.0033
    for at in np.cumsum(RNG.uniform(.016, .068, round(duration*45)+15)):
        if at > duration-.025:
            break
        dt = np.arange(round(.022*SR))/SR
        f = RNG.uniform(2700, 7100)
        grain = np.sin(2*np.pi*f*(dt-4*dt*dt))*np.exp(-dt/.0025)
        start = round(at*SR)
        x[start:start+len(dt)] += taper(grain, .0003, .004)*RNG.uniform(.002, .008)
    x *= (.65+.35*np.exp(-t/1.8))*strength
    return taper(x, .004, min(.48, duration*.22))


def pour(duration):
    """Continuous close water, a changing glass resonance, and fine bubbles."""
    t = np.arange(round(duration*SR))/SR
    u = t/duration
    air = filt(RNG.normal(size=len(t)), lo=1850, hi=8800)
    body = filt(RNG.normal(size=len(t)), lo=180, hi=1350)
    splash = filt(RNG.normal(size=len(t)), lo=620, hi=4700)
    movement = .92+.055*np.sin(2*np.pi*2.17*t)+.035*np.sin(2*np.pi*6.13*t+.8)
    x = (.034*air*(1-.18*u)+.080*splash+.052*body*(.7+.3*u))*movement
    x += .006*np.sin(2*np.pi*(1050*t-290*t*t/(2*duration)))*(.7+.3*np.sin(2*np.pi*9.7*t)**2)
    for at in np.cumsum(RNG.uniform(.065, .16, round(duration*13)+10)):
        if at > duration-.05:
            break
        dt = np.arange(round(.035*SR))/SR
        f = RNG.uniform(900, 2400)*(1-.13*at/duration)
        bubble = np.sin(2*np.pi*f*(dt-5*dt*dt))*np.exp(-dt/.004)
        start = round(at*SR)
        x[start:start+len(dt)] += taper(bubble, .0004, .005)*RNG.uniform(.003, .009)
    # The two-millisecond edge begins on the first established-flow frame.
    return taper(x, .002, .012)


def room(src, wet=.30):
    result = src.copy()
    for ch in range(2):
        for delay, gain in [(.043, .14), (.079, .075), (.131, .04), (.197, .021)]:
            n = round((delay+ch*.004)*SR)
            result[n:, ch] += src[:-n, ch]*gain*wet
    return result


def write_wav(path, samples):
    if not np.all(np.isfinite(samples)) or np.max(np.abs(samples)) >= 1:
        raise ValueError(f'Invalid audio or clipping in {path}')
    wavfile.write(path, SR, np.int16(samples*32767))


def measure(path):
    result = run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af',
                  'loudnorm=I=-17:TP=-1.5:LRA=20:print_format=json', '-f', 'null', '-'])
    return json.loads(re.search(r'\{\s*"input_i"[\s\S]*?\}', result.stderr).group())


def stamp(seconds, separator='.'):
    ms = round(seconds*1000)
    hour, ms = divmod(ms, 3600000)
    minute, ms = divmod(ms, 60000)
    second, ms = divmod(ms, 1000)
    return f'{hour:02}:{minute:02}:{second:02}{separator}{ms:03}'


def make_voice(out, story, count):
    offset = float(story['narration_offset'])
    source_path = ROOT/'audio/narration.wav'
    source_sr, source = wavfile.read(source_path)
    source = source.astype(float)/32768
    if source.ndim == 2:
        source = source.mean(axis=1)
    common = math.gcd(source_sr, SR)
    source = signal.resample_poly(source, SR//common, source_sr//common)
    voice = np.zeros((count, 2))
    add(voice, offset, source, math.sqrt(2))
    write_wav(out/'voice-edited.wav', voice)
    run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', out/'voice-edited.wav',
         '-af', 'highpass=f=65,loudnorm=I=-18.5:TP=-3.0:LRA=14', '-ar', SR, out/'voice-master.wav'])
    words = json.loads((ROOT/'narration-words.json').read_text())
    phrases = ["That's Diet Mountain Dew, straight from your faucet.",
               "The soda you love, made with Pepsi's own concentrate,",
               'without the cases to carry home.', 'Just open the faucet.',
               'Cold and fully carbonated, whenever you want it.',
               'Home Soda Machine.', 'One less errand.']
    captions, cursor = [], 0
    for phrase in phrases:
        selected = words[cursor:cursor+len(phrase.split())]
        captions.append({'start': round(offset+selected[0]['start'], 3),
                         'spoken_end': round(offset+selected[-1]['end'], 3), 'text': phrase})
        cursor += len(selected)
    for i, cap in enumerate(captions):
        next_start = captions[i+1]['start'] if i+1 < len(captions) else story['duration']-.2
        cap['end'] = round(min(next_start-.08, max(cap['spoken_end']+.24, cap['start']+1.15)), 3)
    for suffix, separator in [('vtt', '.'), ('srt', ',')]:
        entries = []
        for i, cap in enumerate(captions):
            prefix = f'{i+1}\n' if suffix == 'srt' else ''
            text = '\n'.join(textwrap.wrap(cap['text'], 42))
            entries.append(f"{prefix}{stamp(cap['start'], separator)} --> {stamp(cap['end'], separator)}\n{text}")
        (out/f'film.{suffix}').write_text(('WEBVTT\n\n' if suffix == 'vtt' else '')+'\n\n'.join(entries)+'\n')
    performance = {'id': 'connected-performance', 'source': 'audio/narration.wav', 'source_start': 0,
                   'source_end': round(len(source)/SR, 5), 'start': offset,
                   'end': round(offset+len(source)/SR, 5), 'first_word_at': offset,
                   'last_word_at': round(offset+words[-1]['end'], 5),
                   'text': json.loads((ROOT/'narration.json').read_text())['text'],
                   'editing': 'One complete performance; no cuts, time stretching, or rearrangement.',
                   'source_sha256': hashlib.sha256(source_path.read_bytes()).hexdigest()}
    return performance, captions


def make_score(story, count, events):
    score = np.zeros((count, 2))
    scenes = {s['id']: s for s in story['scenes']}
    water_at = scenes['pour']['start']
    sensory_at = scenes['sensory']['start']
    serve_at = scenes['serve']['start']
    # 106 2/3 BPM; graphic contacts become the final three pulse accents.
    beat, origin = .5625, .3958333333333333
    notes = [66, 69, 64, 66, 71, 69, 66, 64, 66, 69, 71, 73, 69, 64]
    for i, midi in enumerate(notes):
        at = origin+i*beat
        add(score, at, pluck(midi, .88, damped=True), .022 if i%2 == 0 else .016, -.16 if i%2 == 0 else .16)
        if at < 6.25:
            add(score, at, rim(), .009 if i%2 == 0 else .005, .14)
        if i%2 == 0:
            root = 50 if at < 2.125 else 47 if at < 4.375 else 43 if at < 6.25 else 45
            add(score, at, bass(root), .026, -.025)
    for at, voicing in [(0, [50, 57, 64, 66]), (2.125, [47, 54, 57, 62]),
                        (4.375, [43, 54, 57, 62]), (6.25, [45, 52, 55, 62])]:
        for i, midi in enumerate(voicing):
            add(score, at+i*.019, pluck(midi, 1.7), .018*(1-i*.08), (i-1.5)*.12)
    edge = round(water_at*SR)
    score[edge-round(.045*SR):edge] *= np.cos(np.linspace(0, np.pi/2, round(.045*SR)))[:, None]**2
    score[edge:] = 0
    for at, voicing, gain, duration in [
        (water_at, [50, 57, 59, 64, 66], .027, 3.1),
        (10.583333, [43, 54, 59, 62], .017, 2.5),
        (serve_at, [47, 57, 62, 66], .021, 2.6),
        (14.75, [50, 57, 62, 66], .024, 2.85),
    ]:
        for i, midi in enumerate(voicing):
            add(score, at+i*.021, struck(midi, duration), gain*(1-i*.10), (i-(len(voicing)-1)/2)*.12)
    add(score, 15.375, struck(69, 1.65), .014, .14)
    add(score, 16.125, struck(62, 1.65), .021, -.08)
    score = filt(room(score), lo=40, hi=7300)
    last = round((story['duration']-.34)*SR)
    score[last:] *= np.cos(np.linspace(0, np.pi/2, count-last))[:, None]**2
    score[-round(.06*SR):] = 0
    events.extend([
        {'start': 0, 'end': water_at, 'stem': 'score', 'description': 'Original double-course pluck motif, short bass and restrained rim pulse; graphic contacts carry the final accents.'},
        {'start': water_at, 'end': sensory_at, 'stem': 'score', 'description': 'Pulse clears at established flow; open D-six/nine struck harmony gives water the foreground.'},
        {'start': sensory_at, 'end': serve_at, 'stem': 'score', 'description': 'Open struck harmony supports the intimate beverage macro, with a rounded answer at 10.583333 seconds.'},
        {'start': serve_at, 'end': story['duration'], 'stem': 'score', 'description': 'Struck-chord answer and descending A-to-D closing notes, with a completed studio decay.'},
    ])
    return score


def make_effects(story, count, events):
    fx = np.zeros((count, 2))
    scenes = {s['id']: s for s in story['scenes']}
    opening_end = scenes['drink']['end']
    add(fx, 0, fizz(opening_end, 1.7), 4, .08)
    events.append({'start': 0, 'end': opening_end, 'stem': 'effects', 'description': 'Immediate fine carbonation for the close beverage photograph; no ice or can-opening effect.'})
    burden = scenes['burden']
    for index, (fraction, name) in enumerate(normalized_events()):
        at = math.ceil((burden['start']+fraction*(burden['end']-burden['start']))*FPS-1e-7)/FPS
        add(fx, at, case_contact(index), [.036, .048, .064][index], [-.08, .03, .08][index])
        events.append({'start': at, 'end': round(at+.25+index*.025, 6), 'stem': 'effects', 'id': name,
                       'picture_frame': round(at*FPS), 'normalized_contact': fraction,
                       'description': f'Dry graphic case contact {index+1}; increasing mass, no handling or transition swoosh.'})
    pouring = scenes['pour']
    add(fx, pouring['start'], pour(pouring['end']-pouring['start']), .76, .045)
    events.append({'start': pouring['start'], 'end': pouring['end'], 'stem': 'effects', 'description': 'Established stream begins exactly with the pour cut and stops at the sensory macro cut; no lever stop or click.'})
    sensory, serve = scenes['sensory'], scenes['serve']
    fizz_end = min(serve['end'], serve['start']+3.05)
    carbonation = fizz(fizz_end-sensory['start'])
    time = sensory['start']+np.arange(len(carbonation))/SR
    perspective = np.interp(time, [sensory['start'], serve['start']-.3, serve['start'], fizz_end],
                            [6, 6, 3.5, 3.5])
    add(fx, sensory['start'], carbonation*perspective, 1, .07)
    events.append({'start': sensory['start'], 'end': sensory['end'], 'stem': 'effects', 'description': 'Close fine carbonation across the sensory macro, easing back into the finished-drink perspective at the serve cut.'})
    events.append({'start': serve['start'], 'end': fizz_end, 'stem': 'effects', 'description': 'Continuous residual carbonation on the completed drink; no invented glass set-down or lever click.'})
    return filt(fx, lo=65, hi=11500)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=ROOT/'out')
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    story = json.loads((ROOT/'story.json').read_text())
    count, events = round(story['duration']*SR), []
    performance, captions = make_voice(out, story, count)
    score, fx = make_score(story, count, events), make_effects(story, count, events)
    time, duck = np.arange(count)/SR, np.ones(count)
    for cap in captions:
        attack = np.clip((time-(cap['start']-.13))/.13, 0, 1)
        release = np.clip((cap['spoken_end']+.34-time)/.34, 0, 1)
        duck = np.minimum(duck, 1-(1-10**(-3.0/20))*np.minimum(attack, release))
    score *= 2.6*duck[:, None]
    write_wav(out/'score.wav', score)
    write_wav(out/'effects.wav', fx)
    _, voice_int = wavfile.read(out/'voice-master.wav')
    voice = voice_int.astype(float)/32768
    write_wav(out/'mix-premaster.wav', voice+score+fx)
    premaster = measure(out/'mix-premaster.wav')
    norm = 'loudnorm=I=-17:TP=-1.5:LRA=14:linear=true:'+':'.join(
        f'{key}={premaster[value]}' for key, value in
        [('measured_I', 'input_i'), ('measured_TP', 'input_tp'), ('measured_LRA', 'input_lra'),
         ('measured_thresh', 'input_thresh'), ('offset', 'target_offset')])
    run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', out/'mix-premaster.wav',
         '-af', norm, '-ar', SR, '-c:a', 'pcm_s16le', out/'mix-master.wav'])
    run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', out/'mix-master.wav',
         '-c:a', 'libmp3lame', '-b:a', '192k', out/'audio-review.mp3'])
    levels = {name: measure(out/f'{name}.wav') for name in ['voice-master', 'score', 'effects', 'mix-master']}
    levels = {name: {'integrated_lufs': float(value['input_i']), 'true_peak_dbtp': float(value['input_tp']),
                     'loudness_range_lu': float(value['input_lra'])} for name, value in levels.items()}
    report = {'output_directory': str(out), 'duration_seconds': story['duration'], 'sample_rate': SR, 'channels': 2, 'bits_per_sample': 16,
              'frames': count, 'picture_frames': round(story['duration']*FPS), 'picture_fps': FPS,
              'composition': 'Original short plucked-string motif, compact bass and rim pulse, opening into decaying struck harmony at active flow. No sustained pads.',
              'source_voice': 'audio/narration.wav', 'voice_editing': performance['editing'],
              'master_target': {'integrated_lufs': -17, 'true_peak_ceiling_dbtp': -1.5},
              'levels': levels, 'narration_edits': [performance], 'captions': captions,
              'events': sorted(events, key=lambda e: (e['start'], e['stem'])),
              'review_scope': 'Source, waveform, level and event-clock review. No claim of firsthand listening or audiovisual approval.'}
    (out/'audio-report.json').write_text(json.dumps(report, indent=2)+'\n')
    plan = {'duration': story['duration'], 'fps': FPS, 'audio_master': 'out/mix-master.wav',
            'captions_file': 'out/film.vtt', 'tempo_bpm': 60/.5625,
            'tonal_arc': 'D-add-nine pluck identity; B-minor and G lead to an A-suspended burden. D-six/nine opens on the water cut; a closing struck D chord and A-to-D answer decay through the final readout.',
            'narration_edits': [performance], 'captions': captions, 'events': report['events']}
    (ROOT/'audio-plan.json').write_text(json.dumps(plan, indent=2)+'\n')
    print(json.dumps({'master': str(out/'mix-master.wav'), 'levels': levels,
                      'narration_passages': 1, 'last_spoken_word_at': performance['last_word_at'],
                      'captions': len(captions), 'effects': len([e for e in events if e['stem'] == 'effects'])}, indent=2))


if __name__ == '__main__':
    main()
