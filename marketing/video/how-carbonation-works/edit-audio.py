#!/usr/bin/env python3
"""Give the connected Gemini performance picture breaths without changing word speed."""
from __future__ import annotations

import difflib
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import textwrap
import wave

ROOT = Path(__file__).resolve().parent
AUDIO = ROOT / "audio"


def save(name, value):
    (AUDIO / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def stamp(t, sep="."):
    h, rest = divmod(round(t * 1000), 3600000)
    m, rest = divmod(rest, 60000)
    s, ms = divmod(rest, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"


CAPTION_BREAKS = {
    "At its center is a stainless steel carbonator:": "At its center is a\nstainless steel carbonator:",
    "Carbon dioxide enters through a port at the bottom.": "Carbon dioxide enters\nthrough a port at the bottom.",
    "As the pressures balance, gas admission stops.": "As the pressures balance,\ngas admission stops.",
    "As the level rises, a magnetic float follows it.": "As the level rises,\na magnetic float follows it.",
    "At the high-level signal, the refill pump stops.": "At the high-level signal,\nthe refill pump stops.",
    "through the coil and the stainless steel wall.": "through the coil\nand the stainless steel wall.",
    "The refrigeration loop carries that heat away.": "The refrigeration loop\ncarries that heat away.",
    "Cold water can hold more dissolved carbon dioxide.": "Cold water can hold\nmore dissolved carbon dioxide.",
    "ready for a separate stream of flavor at the faucet.": "ready for a separate stream\nof flavor at the faucet.",
}


def caption_lines(text):
    if text in CAPTION_BREAKS:
        return CAPTION_BREAKS[text]
    if len(text) <= 42:
        return text
    words = text.split()
    # Balance two lines instead of leaving an isolated word on the second.
    choices = [(abs(len(" ".join(words[:i]))-len(" ".join(words[i:]))), i)
               for i in range(2, len(words)-1)
               if max(len(" ".join(words[:i])), len(" ".join(words[i:]))) <= 44]
    if choices:
        _, cut = min(choices)
        return " ".join(words[:cut])+"\n"+" ".join(words[cut:])
    return textwrap.fill(text, width=44)


def main():
    import numpy as np

    captions = json.loads((AUDIO / "captions.json").read_text())
    words = json.loads((AUDIO / "narration-words.json").read_text())
    config = json.loads((ROOT / "narration.json").read_text())
    story = json.loads((ROOT / "story.json").read_text())
    source = AUDIO / "narration-source.wav"
    with wave.open(str(source)) as wav:
        rate, channels, width = wav.getframerate(), wav.getnchannels(), wav.getsampwidth()
        if channels != 1 or width != 2:
            raise SystemExit("This edit expects the recorded mono 16-bit Gemini source.")
        samples = np.frombuffer(wav.readframes(wav.getnframes()), dtype="<i2").copy()
    # Durations are extra picture space; the take's own breaths are preserved.
    extra = [(3, 1.40), (8, 1.60), (13, 1.55), (17, 1.25), (23, 1.50),
             (24, .55), (26, 1.25), (28, 1.65), (30, .55), (32, .70),
             (33, 1.30), (34, .70), (37, 1.05)]
    inserts = [{"source_at": 0.0, "added": 1.25, "purpose": "opening handle"}]
    for phrase, seconds in extra:
        a = captions[phrase]["spoken_end"] + .065
        b = captions[phrase + 1]["start"] - .065
        # Place the insertion at the quietest 16 ms inside the existing gap.
        candidates = np.arange(round(a * rate), round(b * rate), max(1, round(rate * .005)))
        half_window = round(rate * .008)
        if len(candidates):
            energies = [np.mean(np.abs(samples[max(0, x-half_window):x+half_window].astype(float))) for x in candidates]
            cut = int(candidates[int(np.argmin(energies))])
        else:
            cut = round((a + b) / 2 * rate)
        inserts.append({"source_at": round(cut / rate, 6), "added": seconds,
                        "after_caption": phrase, "after_text": captions[phrase]["text"],
                        "purpose": "picture breath"})
    inserts.append({"source_at": len(samples) / rate, "added": 1.40, "purpose": "closing handle"})
    output, cursor, added = [], 0, 0.0
    for item in inserts:
        frame = round(item["source_at"] * rate)
        output.append(samples[cursor:frame])
        output.append(np.zeros(round(item["added"] * rate), dtype="<i2"))
        item["edited_at"] = round(item["source_at"] + added, 6)
        added += item["added"]
        cursor = frame
    output.append(samples[cursor:])
    edited = np.concatenate(output)
    duration = len(edited) / rate

    def shift(t):
        return round(t + sum(i["added"] for i in inserts if i["source_at"] <= t + 1e-8), 3)

    edited_captions = []
    for c in captions:
        d = {"text": c["text"], "start": shift(c["start"]), "spoken_end": shift(c["spoken_end"])}
        d["end"] = round(max(d["spoken_end"] + .45, d["start"] + 1.8), 3)
        edited_captions.append(d)
    for i, c in enumerate(edited_captions[:-1]):
        c["end"] = min(c["end"], round(edited_captions[i+1]["start"]-.04, 3))
    for c in edited_captions:
        c["lines"] = caption_lines(c["text"]).splitlines()

    # Canonical words retain authored spelling; ASR supplies their source times.
    tokens = config["text"].split()
    normalize = lambda s: re.sub(r"[^a-z0-9]", "", s.lower().replace("₂", "2"))
    matcher = difflib.SequenceMatcher(a=list(map(normalize, tokens)),
                                    b=[normalize(w["word"]) for w in words], autojunk=False)
    canonical = []
    for tag, a0, a1, b0, b1 in matcher.get_opcodes():
        if tag == "equal":
            for i in range(a1-a0):
                w = words[b0+i]
                canonical.append({"word": tokens[a0+i], "start": shift(w["start"]), "end": shift(w["end"])})
        elif a1 > a0 and b1 > b0:
            # A hyphenated script word may occupy several recognized tokens.
            for i in range(a1-a0):
                lo = b0 + int(i * (b1-b0) / (a1-a0))
                hi = b0 + max(1, int((i+1) * (b1-b0) / (a1-a0))) - 1
                canonical.append({"word": tokens[a0+i], "start": shift(words[lo]["start"]),
                                  "end": shift(words[min(hi, b1-1)]["end"])})
        elif a1 > a0:
            raise SystemExit("A script word has no recognition match: " + " ".join(tokens[a0:a1]))

    scene_times = []
    for scene in story["scenes"]:
        first = next(i for i,c in enumerate(edited_captions) if c["text"] == scene["narration_start"])
        last = next(i for i,c in enumerate(edited_captions) if c["text"] == scene["narration_end"])
        scene_times.append({"id": scene["id"], "caption_range": [first, last],
                            "voice_start": edited_captions[first]["start"],
                            "voice_end": edited_captions[last]["spoken_end"]})
    fps = story["format"]["fps"]
    scene_times[0]["start"] = 0.0
    for i in range(1, len(scene_times)):
        cut = round((scene_times[i-1]["voice_end"] + scene_times[i]["voice_start"]) / 2 * fps) / fps
        scene_times[i]["start"] = round(cut, 6)
        scene_times[i-1]["end"] = round(cut, 6)
    scene_times[-1]["end"] = duration

    final = AUDIO / "voice-master.wav"
    with tempfile.TemporaryDirectory(prefix="hsm-carbonator-audio-") as temporary:
        raw = Path(temporary) / "edited.wav"
        with wave.open(str(raw), "wb") as wav:
            wav.setparams((1, 2, rate, 0, "NONE", "not compressed"))
            wav.writeframes(edited.tobytes())
        process = subprocess.run(["ffmpeg", "-hide_banner", "-y", "-i", str(raw),
                                  "-af", "highpass=f=65,loudnorm=I=-17:TP=-2:LRA=8:print_format=json",
                                  "-ar", "48000", "-ac", "1", "-c:a", "pcm_s24le", str(final)],
                                 check=True, capture_output=True, text=True)
        match = re.search(r"\{\s*\"input_i\".*?\}", process.stderr, re.S)
        loudness = json.loads(match.group()) if match else {}

    save("edit-plan.json", {"source": "narration-source.wav", "master": "voice-master.wav",
                           "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                           "master_sha256": hashlib.sha256(final.read_bytes()).hexdigest(),
                           "source_duration": len(samples)/rate, "duration": duration,
                           "added_seconds": added, "speed_change": False,
                           "processing": "65 Hz high-pass; voice normalized to -17 LUFS, -2 dBTP ceiling; 48 kHz mono 24-bit PCM",
                           "loudness": loudness, "insertions": inserts})
    save("captions-edited.json", edited_captions)
    save("narration-edited-words.json", canonical)
    save("timing.json", {"duration": duration, "fps": fps,
                         "frames": round(duration * fps), "scenes": scene_times})
    (AUDIO / "film.vtt").write_text("WEBVTT\n\n"+"\n\n".join(
        f"{stamp(c['start'])} --> {stamp(c['end'])}\n{caption_lines(c['text'])}" for c in edited_captions)+"\n")
    (AUDIO / "film.srt").write_text("\n\n".join(
        f"{i+1}\n{stamp(c['start'], ',')} --> {stamp(c['end'], ',')}\n{caption_lines(c['text'])}"
        for i,c in enumerate(edited_captions))+"\n")
    print(json.dumps({"duration": duration, "added_seconds": added,
                      "master": str(final), "scenes": scene_times}, indent=2))


if __name__ == "__main__":
    main()
