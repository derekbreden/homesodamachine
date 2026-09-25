#!/usr/bin/env python3
"""Place narration, pauses, and captions on the opening's frame clock."""

import json
import math
from pathlib import Path
import subprocess
import wave

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
OUT.mkdir(exist_ok=True)
edit = json.loads((ROOT / "edit.json").read_text())


def movie_time(source):
    return source + edit["lead"] + sum(p["duration"] for p in edit["pauses"] if p["at"] <= source)


def stamp(seconds, separator="."):
    ms = round(seconds * 1000)
    hours, ms = divmod(ms, 3600000)
    minutes, ms = divmod(ms, 60000)
    seconds, ms = divmod(ms, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}{separator}{ms:03d}"


with wave.open(str(ROOT / "audio/narration.wav")) as source:
    rate, channels, width = source.getframerate(), source.getnchannels(), source.getsampwidth()
    frames = source.readframes(source.getnframes())
    stride = channels * width
    silence = lambda duration: b"\0" * round(duration * rate) * stride
    assembled = bytearray(silence(edit["lead"]))
    previous = 0
    for pause in edit["pauses"]:
        at = round(pause["at"] * rate) * stride
        assembled.extend(frames[previous:at])
        assembled.extend(silence(pause["duration"]))
        previous = at
    assembled.extend(frames[previous:])
    assembled.extend(silence(edit["tail"]))
    duration = len(assembled) / stride / rate
    frame_count = math.ceil(duration * edit["fps"])
    assembled.extend(silence(frame_count / edit["fps"] - duration))
    with wave.open(str(OUT / "voice-edited.wav"), "wb") as target:
        target.setnchannels(channels)
        target.setsampwidth(width)
        target.setframerate(rate)
        target.writeframes(assembled)

captions = [{"start": movie_time(a), "end": movie_time(b), "text": text}
            for a, b, text in edit["captions"]]
for i, caption in enumerate(captions):
    next_start = captions[i + 1]["start"] if i + 1 < len(captions) else frame_count / edit["fps"]
    caption["end"] = min(next_start - 0.12, max(caption["end"], caption["start"] + 1.6))
timeline = {**edit, "duration": frame_count / edit["fps"], "frames": frame_count, "captions": captions}
(OUT / "timeline.json").write_text(json.dumps(timeline, indent=2) + "\n")
(OUT / "opening.vtt").write_text("WEBVTT\n\n" + "\n\n".join(
    f"{stamp(c['start'])} --> {stamp(c['end'])}\n{c['text']}" for c in captions) + "\n")
(OUT / "opening.srt").write_text("\n\n".join(
    f"{i+1}\n{stamp(c['start'], ',')} --> {stamp(c['end'], ',')}\n{c['text']}"
    for i, c in enumerate(captions)) + "\n")
subprocess.run([
    "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(OUT / "voice-edited.wav"),
    "-af", "highpass=f=65,loudnorm=I=-16:TP=-1.5:LRA=7", "-ar", "48000",
    str(OUT / "voice-master.wav"),
], check=True)
print(json.dumps({"seconds": timeline["duration"], "frames": frame_count, "captions": len(captions)}))
