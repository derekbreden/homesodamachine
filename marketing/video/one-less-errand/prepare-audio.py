#!/usr/bin/env python3
"""Place the recorded narration and captions on the film's picture clock."""
from array import array
import difflib
import json
from pathlib import Path
import re
import subprocess
import wave

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
OUT.mkdir(exist_ok=True)
story = json.loads((ROOT / "story.json").read_text())
words = json.loads((ROOT / "narration-words.json").read_text())
authored = [w for s in story["scenes"] for w in s["text"].split()]
normalize = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
expected, heard = list(map(normalize, authored)), [normalize(w["word"]) for w in words]
if expected != heard:
    raise ValueError("Narration differs: " + str([o for o in difflib.SequenceMatcher(None, expected, heard).get_opcodes() if o[0] != "equal"]))

with wave.open(str(ROOT / "audio/narration.wav")) as source:
    rate, channels, width = source.getframerate(), source.getnchannels(), source.getsampwidth()
    if channels != 1 or width != 2:
        raise ValueError("Expected mono 16-bit narration")
    samples = array("h", source.readframes(source.getnframes()))
target = array("h", [0]) * round(story["duration"] * rate)
captions, segments = [], []
cursor = 0
audio_scenes = []
for scene in story["scenes"]:
    if "phraseAt" in scene:
        if len(scene["phraseAt"]) != len(scene["captionPhrases"]):
            raise ValueError(f"Phrase timing mismatch: {scene['id']}")
        audio_scenes.extend({**scene, "id": f"{scene['id']}-{i+1}",
            "voiceAt": at, "text": phrase, "captionPhrases": [phrase]}
            for i, (at, phrase) in enumerate(zip(scene["phraseAt"], scene["captionPhrases"])))
    else:
        audio_scenes.append(scene)
for scene in audio_scenes:
    count = len(scene["text"].split())
    spoken = words[cursor:cursor + count]
    next_start = words[cursor+count]["start"] if cursor+count < len(words) else len(samples)/rate
    previous_end = words[cursor-1]["end"] if cursor else 0
    source_start = max(0, spoken[0]["start"] - .18, previous_end + .12 if cursor else 0)
    source_end = min(len(samples)/rate, spoken[-1]["end"] + .45, next_start - .12)
    dest_start = max(scene["start"] + .1, scene["voiceAt"] - (spoken[0]["start"] - source_start))
    dest_end = dest_start + source_end-source_start
    if dest_end > scene["end"]-.08:
        raise ValueError(f"Narration overruns {scene['id']}: {dest_end:.2f}>{scene['end']}")
    chunk = samples[round(source_start*rate):round(source_end*rate)]
    fade = min(round(rate*.008), len(chunk)//2)
    for i in range(fade):
        gain = (i / max(1, fade-1)) ** 2
        chunk[i] = round(chunk[i]*gain)
        chunk[-1-i] = round(chunk[-1-i]*gain)
    at = round(dest_start*rate)
    target[at:at+len(chunk)] = chunk
    shift = dest_start-source_start
    begin = 0
    if " ".join(scene["captionPhrases"]) != scene["text"]:
        raise ValueError(f"Caption mismatch: {scene['id']}")
    for phrase in scene["captionPhrases"]:
        end = begin + len(phrase.split())
        captions.append({"start": spoken[begin]["start"]+shift,
                         "end": spoken[end-1]["end"]+shift+.24, "text": phrase})
        begin = end
    segments.append({"id": scene["id"], "sourceStart": source_start,
                     "sourceEnd": source_end, "start": dest_start, "end": dest_end})
    cursor += count
for i, cap in enumerate(captions):
    next_start = captions[i+1]["start"] if i+1 < len(captions) else story["duration"]-.3
    cap["end"] = min(next_start-.12, max(cap["end"], cap["start"]+1.3))
with wave.open(str(OUT / "voice-edited.wav"), "wb") as wav:
    wav.setparams((1, 2, rate, 0, "NONE", "not compressed"))
    wav.writeframes(target.tobytes())
subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(OUT/"voice-edited.wav"),
                "-af","highpass=f=65,loudnorm=I=-17:TP=-2:LRA=8","-ar","48000",str(OUT/"voice-master.wav")],check=True)
timeline = {**story, "frames": round(story["duration"]*story["fps"]), "captions": captions}
(OUT/"timeline.json").write_text(json.dumps(timeline,indent=2)+"\n")
(ROOT/"narration-timing.json").write_text(json.dumps(segments,indent=2)+"\n")
def stamp(t, separator="."):
    milliseconds = round(t*1000)
    h, milliseconds = divmod(milliseconds,3600000)
    m, milliseconds = divmod(milliseconds,60000)
    s, milliseconds = divmod(milliseconds,1000)
    return f"{h:02}:{m:02}:{s:02}{separator}{milliseconds:03}"
(OUT/"film.vtt").write_text("WEBVTT\n\n"+"\n\n".join(f"{stamp(c['start'])} --> {stamp(c['end'])}\n{c['text']}" for c in captions)+"\n")
(OUT/"film.srt").write_text("\n\n".join(f"{i+1}\n{stamp(c['start'],',')} --> {stamp(c['end'],',')}\n{c['text']}" for i,c in enumerate(captions))+"\n")
print(json.dumps({"words": len(words), "captions": len(captions), "segments": segments},indent=2))
