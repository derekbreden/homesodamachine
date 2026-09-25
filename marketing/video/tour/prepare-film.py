#!/usr/bin/env python3
"""Assemble the approved opening and the narrated chapters on one frame clock."""

import json
import math
from array import array
from pathlib import Path
import re
import subprocess
import sys
import wave

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
film = json.loads((ROOT / "film.json").read_text())
recording = json.loads((ROOT / "narration-full.json").read_text())
if recording["text"] != "\n\n".join(scene["text"] for scene in film["scenes"]):
    raise ValueError("The film narration differs from the recording script")
timings = json.loads((ROOT / "film-timing.json").read_text())
opening = json.loads((OUT / "timeline.json").read_text())
fps = opening["fps"]
rate = 48000

def stamp(seconds, separator="."):
    ms = round(seconds * 1000)
    hours, ms = divmod(ms, 3600000)
    minutes, ms = divmod(ms, 60000)
    seconds, ms = divmod(ms, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}{separator}{ms:03d}"

def read_wave(path):
    with wave.open(str(path)) as wav:
        if wav.getframerate() != rate or wav.getnchannels() != 1 or wav.getsampwidth() != 2:
            raise ValueError(f"Expected mono 48 kHz 16-bit WAV: {path}")
        return wav.readframes(wav.getnframes())

def taper(chunk):
    samples = array("h", chunk)
    if sys.byteorder != "little":
        samples.byteswap()
    count = min(round(rate * 0.008), len(samples) // 2)
    for i in range(count):
        gain = math.sin(i / max(1, count-1) * math.pi / 2) ** 2
        samples[i] = round(samples[i] * gain)
        samples[-1-i] = round(samples[-1-i] * gain)
    if sys.byteorder != "little":
        samples.byteswap()
    return samples.tobytes()

measurement = subprocess.run([
    "ffmpeg", "-hide_banner", "-i", str(OUT / "voice-master.wav"),
    "-af", "loudnorm=I=-16:TP=-1.5:LRA=7:print_format=json", "-f", "null", "-",
], capture_output=True, text=True, check=True)
measured = json.loads(re.search(r'\{\s*"input_i"[\s\S]*?\}', measurement.stderr).group())
target_loudness = float(measured["input_i"])
subprocess.run([
    "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
    "-i", str(ROOT / "audio/continuation.wav"),
    "-af", f"highpass=f=65,loudnorm=I={target_loudness}:TP=-1.5:LRA=7", "-ar", str(rate),
    str(OUT / "continuation-master.wav"),
], check=True)
continuation = read_wave(OUT / "continuation-master.wav")
assembled = bytearray(read_wave(OUT / "voice-master.wav"))
silence = lambda seconds: b"\0" * round(seconds * rate) * 2
captions = list(opening["captions"])
scenes = []

for index, (spec, timing) in enumerate(zip(film["scenes"], timings, strict=True)):
    if spec["id"] != timing["id"]:
        raise ValueError("Scene order differs from the recorded narration")
    start = len(assembled) / 2 / rate
    source_start = max(0, timing["start"] - 0.12)
    next_start = timings[index+1]["start"] - 0.12 if index+1 < len(timings) else len(continuation)/2/rate
    source_end = min(timing["end"] + 0.45, next_start)
    lead = spec["lead"]
    spoken_start = start + lead + timing["start"] - source_start
    # Preserve the voice's release inside the scene's hold; word timestamps can
    # finish before the final consonant has decayed.
    duration = lead + timing["end"] + 0.18 - source_start + spec["hold"]
    duration = math.ceil(duration * fps) / fps
    assembled.extend(silence(lead))
    assembled.extend(taper(continuation[round(source_start*rate)*2:round(source_end*rate)*2]))
    target_samples = round((start+duration)*rate)
    assembled.extend(b"\0" * (target_samples - len(assembled)//2) * 2)
    for caption in timing["captions"]:
        captions.append({**caption, "start": start+lead+caption["start"]-source_start,
                         "end": start+lead+caption["end"]-source_start})
    scenes.append({**spec, "start": start, "duration": duration, "end": start+duration,
                   "spokenStart": spoken_start, "spokenEnd": start+lead+timing["end"]-source_start})

assembled.extend(silence(film["tail"]))
frame_count = math.ceil(len(assembled) / 2 / rate * fps)
assembled.extend(b"\0" * (round(frame_count/fps*rate) - len(assembled)//2) * 2)
for i, caption in enumerate(captions):
    if i < len(opening["captions"]):
        continue
    next_start = captions[i+1]["start"] if i+1 < len(captions) else frame_count/fps
    caption["end"] = min(next_start-0.12, max(caption["end"]+0.25, caption["start"]+1.6))
    if caption["end"] <= caption["start"]:
        raise ValueError(f"Nonpositive caption: {caption}")

timeline = {"full": True, "title": film["title"], "openingDuration": opening["duration"],
            "fps": fps, "width": opening["width"], "height": opening["height"],
            "duration": frame_count/fps, "frames": frame_count, "scenes": scenes, "captions": captions}
(OUT / "film-timeline.json").write_text(json.dumps(timeline, indent=2)+"\n")
voice_path = OUT / "film-voice-master.wav"
temporary_voice_path = OUT / "film-voice-master.tmp.wav"
with wave.open(str(temporary_voice_path), "wb") as wav:
    wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(rate); wav.writeframes(assembled)
temporary_voice_path.replace(voice_path)
for suffix, separator in [("vtt", "."), ("srt", ",")]:
    content = "WEBVTT\n\n" if suffix == "vtt" else ""
    content += "\n\n".join(
        (f"{i+1}\n" if suffix == "srt" else "") +
        f"{stamp(c['start'], separator)} --> {stamp(c['end'], separator)}\n{c['text']}"
        for i,c in enumerate(captions)) + "\n"
    (OUT / f"film.{suffix}").write_text(content)
chapters = [{"title": "Inside the soda machine", "start": 0}]
for scene in scenes:
    if not any(chapter["title"] == scene["chapter"] for chapter in chapters):
        chapters.append({"title": scene["chapter"], "start": scene["start"]})
metadata = [";FFMETADATA1", "title=Inside the soda machine", "artist=Home Soda Machine"]
for i, chapter in enumerate(chapters):
    end = chapters[i+1]["start"] if i+1 < len(chapters) else timeline["duration"]
    metadata.extend(["[CHAPTER]", "TIMEBASE=1/1000", f"START={round(chapter['start']*1000)}",
                     f"END={round(end*1000)}", f"title={chapter['title']}"])
(OUT / "film-chapters.txt").write_text("\n".join(metadata)+"\n")
(OUT / "film-chapters.json").write_text(json.dumps(chapters,indent=2)+"\n")
print(json.dumps({"seconds": timeline["duration"], "frames": frame_count, "captions": len(captions),
                  "chapters": len(chapters), "opening_lufs": target_loudness}))
