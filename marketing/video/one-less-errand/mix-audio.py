#!/usr/bin/env python3
"""Mix the original score and effects beneath the edited narration."""
import json
from pathlib import Path
import re
import subprocess
import numpy as np
from scipy.io import wavfile

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"out"
rate=48000
def read(path):
    sr,samples=wavfile.read(path)
    if sr!=rate or samples.dtype!=np.int16:
        raise ValueError(f"Expected 48 kHz 16-bit: {path}")
    samples=samples.astype(np.float64)/32768
    return np.repeat(samples[:,None],2,axis=1) if samples.ndim==1 else samples
voice=read(OUT/"voice-master.wav")
score=read(ROOT/"audio/score.wav")
effects=read(ROOT/"audio/effects.wav")
if voice.shape!=score.shape or score.shape!=effects.shape:
    raise ValueError("Audio stems differ in length or channel count")
time=np.arange(len(voice))/rate
duck=np.ones(len(voice))
for segment in json.loads((ROOT/"narration-timing.json").read_text()):
    onset=np.clip((time-(segment["start"]-.12))/.12,0,1)
    release=np.clip((segment["end"]+.5-time)/.5,0,1)
    duck=np.minimum(duck,1-(1-10**(-3/20))*np.minimum(onset,release))
mixed=voice+score*duck[:,None]+effects*10**(-1/20)
if np.max(np.abs(mixed))>=1:
    raise ValueError("Premaster clips")
wavfile.write(OUT/"mix-premaster.wav",rate,np.int16(np.clip(mixed,-1,1)*32767))
measure=subprocess.run(["ffmpeg","-hide_banner","-i",str(OUT/"mix-premaster.wav"),
    "-af","loudnorm=I=-17:TP=-1.5:LRA=20:print_format=json","-f","null","-"],capture_output=True,text=True,check=True)
levels=json.loads(re.search(r'\{\s*"input_i"[\s\S]*?\}',measure.stderr).group())
filter=("loudnorm=I=-17:TP=-1.5:LRA=20:linear=true:"+
    ":".join(f"{k}={levels[v]}" for k,v in [("measured_I","input_i"),("measured_TP","input_tp"),("measured_LRA","input_lra"),("measured_thresh","input_thresh"),("offset","target_offset")]))
subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(OUT/"mix-premaster.wav"),
    "-af",filter,"-ar",str(rate),str(OUT/"mix-master.wav")],check=True)
(OUT/"mix-levels.json").write_text(json.dumps(levels,indent=2)+"\n")
print(json.dumps({"frames":len(mixed),"premaster":levels},indent=2))
