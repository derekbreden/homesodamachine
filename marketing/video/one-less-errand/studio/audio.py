#!/usr/bin/env python3
"""Compose the story-led film around one connected voice performance.

Run with tools/video-venv/bin/python. --out selects a separate sound build;
the default is studio/out. The picture clock comes from story.json; --timing
applies an optional picture edit with pauses in the saved voice performance.
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
from timing import load_story

ROOT = Path(__file__).resolve().parent
SR = 48000
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


def pluck(midi, duration=1.6, damped=False, decay=None):
    """A short double-course string with a small wooden attack."""
    t = np.arange(round(duration*SR))/SR
    f, x = hz(midi), np.zeros_like(t)
    life = decay if decay is not None else (.30 if damped else .78)
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
    """A short weighted carton contact, with a little enclosed can resonance."""
    index %= 3
    t = np.arange(round((.25+index*.025)*SR))/SR
    f = [155, 126, 102][index]
    x = (.58*np.sin(2*np.pi*f*t)*np.exp(-t/(.027+index*.006))
         +.18*np.sin(2*np.pi*f*2.19*t)*np.exp(-t/.018)
         +filt(RNG.normal(size=len(t)), lo=180, hi=2900)*np.exp(-t/.014)*.44)
    x = taper(x, .0007, .05)
    return x/max(np.max(np.abs(x)), 1e-9)


def can_contact(index=0, duration=.35):
    """A full aluminum can meeting a support, with a brief shell resonance."""
    t = np.arange(round(duration*SR))/SR
    variation = [1, .975, 1.022][index % 3]
    hit = filt(RNG.normal(size=len(t)), lo=90, hi=1900)*np.exp(-t/.012)
    x = .58*hit+.46*np.sin(2*np.pi*155*variation*t)*np.exp(-t/.036)
    for frequency, amplitude, decay in [(484, .30, .055), (913, .15, .043), (1741, .055, .025)]:
        x += amplitude*np.sin(2*np.pi*frequency*variation*t)*np.exp(-t/decay)
    x = taper(x, .001, .06)
    return x/max(np.max(np.abs(x)), 1e-9)


def carton_move(duration=.28):
    t = np.arange(round(duration*SR))/SR
    x = filt(RNG.normal(size=len(t)), lo=220, hi=2700)*np.sin(np.pi*t/duration)**2
    x = taper(x, .012, .045)
    return x/max(np.max(np.abs(x)), 1e-9)


def load_movement(duration=.65):
    t = np.arange(round(duration*SR))/SR
    x = filt(RNG.normal(size=len(t)), lo=100, hi=780)
    x *= (.72+.28*np.sin(2*np.pi*6.8*t)**2)*np.sin(np.pi*t/duration)**2
    x = taper(x, .08, .12)
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


def tokens(text):
    return re.findall(r"[a-z0-9]+(?:['-][a-z0-9]+)*", text.lower().replace('’', "'"))


def caption_phrases(config):
    phrases = config.get('caption_phrases')
    if phrases is None:
        phrases = re.findall(r'[^.!?]+[.!?]*', config['text'])
    phrases = [phrase.strip() for phrase in phrases if phrase.strip()]
    if tokens(' '.join(phrases)) != tokens(config['text']):
        raise ValueError('Narration caption_phrases must contain the full script in spoken order.')
    return phrases


def insert_narration_pauses(source, source_sr, pauses, fps, offset):
    """Extend quiet source gaps while preserving the recorded words and breaths."""
    if not pauses:
        return source, []
    source = source.copy()
    fade_samples = round(.003*source_sr)
    pieces, edits, cursor, added = [], [], 0, 0
    for pause in sorted(pauses, key=lambda item: item['source_sample']):
        at = int(pause['source_sample'])
        if not 0 < at < len(source) or int(pause['frames']) <= 0:
            raise ValueError(f'Invalid narration pause: {pause["id"]}')
        # These edges lie in verified quiet samples, away from speech tails
        # and the next intake. Only the adjacent three milliseconds are faded.
        left, right = min(fade_samples, at), min(fade_samples, len(source)-at)
        source[at-left:at] *= np.cos(np.linspace(0, np.pi/2, left))**2
        source[at:at+right] *= np.sin(np.linspace(0, np.pi/2, right))**2
        count = round(int(pause['frames'])*source_sr/fps)
        pieces.extend([source[cursor:at], np.zeros(count)])
        edits.append({'id': pause['id'], 'after_scene': pause['after_scene'],
                      'source_sample': at, 'source_sample_rate': source_sr,
                      'source_time': at/source_sr, 'duration_frames': int(pause['frames']),
                      'duration_samples': count, 'duration_seconds': count/source_sr,
                      'start': offset+(at+added)/source_sr,
                      'end': offset+(at+added+count)/source_sr,
                      'quiet_edge_fade_seconds': .003})
        cursor, added = at, added+count
    pieces.append(source[cursor:])
    return np.concatenate(pieces), edits


def make_voice(out, story, count):
    offset = float(story['narration_offset'])
    config = json.loads((ROOT/'narration.json').read_text())
    source_path = ROOT/'audio/narration.wav'
    source_sr, source = wavfile.read(source_path)
    source = source.astype(float)/32768
    if source.ndim == 2:
        source = source.mean(axis=1)
    source_duration = len(source)/source_sr
    source, pause_edits = insert_narration_pauses(
        source, source_sr, story.get('narration_pauses', []), float(story['fps']), offset)
    common = math.gcd(source_sr, SR)
    source = signal.resample_poly(source, SR//common, source_sr//common)
    if round(offset*SR)+len(source) > count:
        raise ValueError('The complete voice performance extends beyond story.duration.')
    voice = np.zeros((count, 2))
    add(voice, offset, source, math.sqrt(2))
    write_wav(out/'voice-edited.wav', voice)
    run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', out/'voice-edited.wav',
         '-af', 'highpass=f=65,loudnorm=I=-18.5:TP=-3.0:LRA=14', '-ar', SR, out/'voice-master.wav'])
    words = json.loads((ROOT/'narration-words.json').read_text())
    word_tokens = [(token, word) for word in words for token in tokens(word['word'])]
    if [token for token, _ in word_tokens] != tokens(config['text']):
        raise ValueError('The saved word alignment does not match the narration script.')
    phrases = caption_phrases(config)

    def picture_time(source_time):
        added = sum(edit['duration_seconds'] for edit in pause_edits
                    if round(source_time*source_sr) >= edit['source_sample'])
        return offset+source_time+added

    captions, cursor = [], 0
    for phrase in phrases:
        selected = [word for _, word in word_tokens[cursor:cursor+len(tokens(phrase))]]
        captions.append({'start': round(picture_time(selected[0]['start']), 3),
                         'spoken_end': round(picture_time(selected[-1]['end']), 3), 'text': phrase})
        cursor += len(tokens(phrase))
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
                   'source_end': round(source_duration, 5), 'start': offset,
                   'end': round(offset+len(source)/SR, 5), 'first_word_at': round(picture_time(words[0]['start']), 5),
                   'last_word_at': round(picture_time(words[-1]['end']), 5),
                   'text': config['text'],
                   'editing': 'One complete performance; no cuts, time stretching, or rearrangement.',
                   'source_sha256': hashlib.sha256(source_path.read_bytes()).hexdigest()}
    if pause_edits:
        performance['editing'] = ('One complete performance with added quiet sentence-gap pauses. '
                                  'No recorded words or breaths are cut, stretched, or rearranged; '
                                  'three-millisecond fades touch only the quiet splice edges.')
        performance['sentence_gap_extensions'] = pause_edits
    return performance, captions


def make_score(story, count, events, captions):
    score = np.zeros((count, 2))
    scenes = {s['id']: s for s in story['scenes']}
    reveal_at = scenes['hero']['start']
    water_at = scenes['pour']['start']
    sensory_at = scenes['sensory']['start']
    serve_at = scenes['serve']['start']
    routine_at = scenes['case']['start']
    extra_question = scenes['question'].get('extra_frames', 0)/float(story['fps'])
    routine_end = reveal_at-extra_question
    carry_decay = story.get('score', {}).get('reveal_transition') == 'decay'
    tail = np.zeros_like(score) if carry_decay else None
    # A fixed eight-note cell gives the errands a routine, without speeding up
    # the narrator. Physical contacts carry their own picture-derived clock.
    beat, origin = .5625, routine_at+.125
    notes = [66, 69, 64, 66, 71, 69, 66, 64]
    for i in range(max(0, math.ceil((routine_end-origin)/beat))):
        midi = notes[i % len(notes)]
        at = origin+i*beat
        progress = np.clip((at-routine_at)/max(routine_end-routine_at, .01), 0, 1)
        gain = (.016 if i%2 == 0 else .012)*(1+.24*progress)
        add(score, at, pluck(midi, .88, damped=True), gain, -.16 if i%2 == 0 else .16)
        add(score, at, rim(), (.0045 if i%2 == 0 else .0025)*(1+.20*progress), .14)
        if i%2 == 0:
            root = [47, 43, 45, 47][(i//len(notes)) % 4]
            add(score, at, bass(root), .019*(1+.22*progress), -.025)
    for i, midi in enumerate([50, 57, 64, 66]):
        add(score, i*.019, pluck(midi, 1.7), .015*(1-i*.08), (i-1.5)*.12)
    voicings = [[47, 54, 57, 62], [43, 54, 57, 62], [45, 52, 55, 62], [47, 54, 57, 62]]
    cells = max(0, math.ceil((routine_end-routine_at)/(8*beat)))
    for cell in range(cells):
        at, voicing = routine_at+cell*8*beat, voicings[cell % len(voicings)]
        carry = carry_decay and cell == cells-1
        for i, midi in enumerate(voicing):
            duration = reveal_at+.35-at-i*.019 if carry else 1.7
            add(tail if carry else score, at+i*.019,
                pluck(midi, duration, decay=1.25 if carry else None),
                .015*(1-i*.08), (i-1.5)*.12)
        if carry:
            events.append({'start': at, 'end': reveal_at+.35, 'stem': 'score', 'id': 'question_decay',
                           'description': 'The final routine harmony rings with a soft 1.25-second decay through the question pause and overlaps the answer by 350 ms; no new pulse or attack is added in the pause.'})
    # The repeating expectation stops for a short breath before the answer.
    # Let the extended question beat carry the decay before the answer chord.
    edge = round(reveal_at*SR)
    clear = max(0, round((routine_end-.20)*SR))
    fade = max(0, clear-round(.22*SR))
    score[fade:clear] *= np.cos(np.linspace(0, np.pi/2, clear-fade))[:, None]**2
    score[clear:edge] = 0
    score[edge:] = 0
    if carry_decay:
        score += tail
    phrases = [
        (reveal_at, [50, 57, 59, 64, 66], .027, 3.1),
        (water_at, [47, 57, 62, 66], .014, 2.5),
        (sensory_at, [43, 54, 59, 62], .018, 2.5),
        (serve_at, [50, 57, 62, 66], .021, 2.6),
    ]
    if water_at-reveal_at > 3.8:
        phrases.append((reveal_at+(water_at-reveal_at)*.55, [43, 54, 59, 62], .016, 2.6))
    tagline = captions[-1]
    if tagline['start']-serve_at > .65:
        phrases.append((tagline['start']+.08, [50, 57, 62, 66], .021, 2.65))
    for at, voicing, gain, duration in phrases:
        for i, midi in enumerate(voicing):
            add(score, at+i*.021, struck(midi, duration), gain*(1-i*.10), (i-(len(voicing)-1)/2)*.12)
    last_note = min(tagline['spoken_end']+.82, story['duration']-1.55)
    add(score, max(serve_at, last_note-.65), struck(69, 1.65), .014, .14)
    add(score, max(serve_at+.10, last_note), struck(62, 1.65), .021, -.08)
    score = filt(room(score), lo=40, hi=7300)
    last = round((story['duration']-.42)*SR)
    score[last:] *= np.cos(np.linspace(0, np.pi/2, count-last))[:, None]**2
    score[-round(.06*SR):] = 0
    transition = ('a 220 ms pulse release leaves the last routine harmony decaying through the pause and into the answer'
                  if carry_decay else f'a 220 ms fade leads to a {round((.20+extra_question)*1000)} ms tonal breath before the reveal')
    events.extend([
        {'start': 0, 'end': routine_at, 'stem': 'score', 'description': 'A small double-course plucked figure introduces the wish for a drink.'},
        {'start': routine_at, 'end': reveal_at, 'stem': 'score',
         'description': f'The same eight-note pluck cell repeats with gently accumulating bass and rim pulse; {transition}.'},
        {'start': reveal_at, 'end': water_at, 'stem': 'score', 'description': 'The expected repetition gives way to open D-six/nine struck harmony at the faucet reveal.'},
        {'start': water_at, 'end': sensory_at, 'stem': 'score', 'description': 'Thin, rounded harmony leaves the close water in the foreground.'},
        {'start': sensory_at, 'end': serve_at, 'stem': 'score', 'description': 'Spacious struck harmony supports the intimate beverage macro.'},
        {'start': serve_at, 'end': story['duration'], 'stem': 'score', 'description': 'The completed drink receives a resolved D chord and descending A-to-D answer, followed by a natural closing decay.'},
    ])
    return score


def make_effects(story, count, events):
    fx = np.zeros((count, 2))
    scenes = {s['id']: s for s in story['scenes']}
    fps = float(story['fps'])
    opening_end = scenes['opening']['end']
    add(fx, 0, fizz(opening_end, 1.7), 4, .08)
    events.append({'start': 0, 'end': opening_end, 'stem': 'effects', 'description': 'Immediate fine carbonation for the close beverage photograph; no ice or can-opening effect.'})
    for index, event in enumerate(story.get('sound_events', [])):
        frame = int(event['frame']) if 'frame' in event else math.ceil(float(event['time'])*fps-1e-7)
        at, kind = frame/fps, event['kind']
        if not 0 <= at < story['duration']:
            raise ValueError(f'Sound event {event["id"]} lies outside the picture clock.')
        variation = int(event.get('variation', index))
        if kind == 'can_contact':
            sound = can_contact(variation, float(event.get('duration', .35)))
            gain, description = .048, 'Brief weighted can contact with softened aluminum shell resonance.'
        elif kind == 'case_contact':
            sound = case_contact(variation)
            gain, description = .060, 'Dry weighted carton contact with enclosed can resonance.'
        elif kind == 'carton_move':
            sound = carton_move(float(event.get('duration', .28)))
            gain, description = .022, 'Short carton movement matching the visible load.'
        elif kind == 'load_movement':
            sound = load_movement(float(event.get('duration', .65)))
            gain, description = .015, 'Restrained low movement texture beneath visible transport.'
        else:
            raise ValueError(f'Unknown sound event kind: {kind}')
        gain, pan = float(event.get('gain', gain)), float(event.get('pan', 0))
        add(fx, at, sound, gain, pan)
        events.append({'start': at, 'end': round(min(at+len(sound)/SR, story['duration']), 6),
                       'stem': 'effects', 'id': event['id'], 'kind': kind, 'picture_frame': frame,
                       'gain': gain, 'pan': pan, 'description': description})
    pouring = scenes['pour']
    add(fx, pouring['start'], pour(pouring['end']-pouring['start']), .76, .045)
    events.append({'start': pouring['start'], 'end': pouring['end'], 'stem': 'effects', 'description': 'Established stream begins exactly with the pour cut and stops at the sensory macro cut; no lever stop or click.'})
    sensory, serve = scenes['sensory'], scenes['serve']
    fizz_end = story['duration']
    carbonation = fizz(fizz_end-sensory['start'])
    time = sensory['start']+np.arange(len(carbonation))/SR
    perspective = np.interp(time, [sensory['start'], max(sensory['start'], serve['start']-.3),
                                 serve['start'], max(serve['start'], fizz_end-.65), fizz_end],
                            [6, 6, 3.5, 3.5, 0])
    add(fx, sensory['start'], carbonation*perspective, 1, .07)
    events.append({'start': sensory['start'], 'end': sensory['end'], 'stem': 'effects', 'description': 'Close fine carbonation across the sensory macro, easing back into the finished-drink perspective at the serve cut.'})
    events.append({'start': serve['start'], 'end': fizz_end, 'stem': 'effects', 'description': 'Continuous residual carbonation on the completed drink; no invented glass set-down or lever click.'})
    return filt(fx, lo=65, hi=11500)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=ROOT/'out')
    parser.add_argument('--timing', type=Path)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    story = load_story(args.timing)
    count, events = round(story['duration']*SR), []
    performance, captions = make_voice(out, story, count)
    score, fx = make_score(story, count, events, captions), make_effects(story, count, events)
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
    fps = float(story['fps'])
    report = {'output_directory': str(out), 'duration_seconds': story['duration'], 'sample_rate': SR, 'channels': 2, 'bits_per_sample': 16,
              'frames': count, 'picture_frames': round(story['duration']*fps), 'picture_fps': fps,
              'composition': 'Original repeating plucked-string motif, compact bass and rim pulse; a brief tonal breath gives way to open struck harmony at the faucet reveal, close water and a resolved closing cadence.',
              'source_voice': 'audio/narration.wav', 'voice_editing': performance['editing'],
              'master_target': {'integrated_lufs': -17, 'true_peak_ceiling_dbtp': -1.5},
              'levels': levels, 'narration_edits': [performance], 'captions': captions,
              'events': sorted(events, key=lambda e: (e['start'], e['stem'])),
              'review_scope': 'Source, waveform, level and event-clock review. No claim of firsthand listening or audiovisual approval.'}
    (out/'audio-report.json').write_text(json.dumps(report, indent=2)+'\n')
    plan_prefix = '' if args.timing is not None else 'out/'
    plan = {'duration': story['duration'], 'fps': fps, 'audio_master': plan_prefix+'mix-master.wav',
            'captions_file': plan_prefix+'film.vtt', 'tempo_bpm': 60/.5625,
            'tonal_arc': 'A small D-add-nine pluck identity becomes a recurring B-minor, G and A-suspended errand cell. The pulse ends before the reveal; open D-six/nine struck harmony answers, leaving space for the pour and fine fizz. A resolved D chord and A-to-D answer decay through the final readout.',
            'narration_edits': [performance], 'captions': captions, 'events': report['events']}
    plan_path = out/'audio-plan.json' if args.timing is not None else ROOT/'audio-plan.json'
    plan_path.write_text(json.dumps(plan, indent=2)+'\n')
    print(json.dumps({'master': str(out/'mix-master.wav'), 'levels': levels,
                      'narration_passages': 1, 'last_spoken_word_at': performance['last_word_at'],
                      'captions': len(captions), 'effects': len([e for e in events if e['stem'] == 'effects'])}, indent=2))


if __name__ == '__main__':
    main()
