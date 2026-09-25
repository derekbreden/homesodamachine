#!/usr/bin/env python3
"""Align the authored continuation to a Whisper word transcript for review."""

import difflib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
film = json.loads((ROOT / "film.json").read_text())
transcript = json.loads((ROOT / "out/continuation.json").read_text())
spoken = [word for segment in transcript["segments"] for word in segment.get("words", [])]
authored = [word for scene in film["scenes"] for word in scene["text"].split()]
normalize = lambda value: re.sub(r"[^a-z0-9]", "", value.lower())
matcher = difflib.SequenceMatcher(None, list(map(normalize, authored)),
                                [normalize(w["word"]) for w in spoken], autojunk=False)
timing = [None] * len(authored)
differences = []
for kind, a, b, c, d in matcher.get_opcodes():
    if kind == "equal":
        for i, j in zip(range(a, b), range(c, d)):
            timing[i] = [spoken[j]["start"], spoken[j]["end"]]
    else:
        differences.append({"authored": " ".join(authored[a:b]),
                            "heard": " ".join(w["word"].strip() for w in spoken[c:d]),
                            "at": spoken[min(c, len(spoken)-1)]["start"]})
        if a < b:
            start = spoken[c]["start"] if c < d else spoken[max(0, c-1)]["end"]
            end = spoken[d-1]["end"] if c < d else spoken[min(c, len(spoken)-1)]["start"]
            for i in range(a, b):
                timing[i] = [start + (end-start)*(i-a)/(b-a), start + (end-start)*(i-a+1)/(b-a)]

result = []
cursor = 0
for scene in film["scenes"]:
    words = scene["text"].split()
    times = timing[cursor:cursor+len(words)]
    if any(t is None for t in times):
        raise SystemExit(f"Missing alignment in {scene['id']}")
    captions = []
    if scene.get("captionPhrases"):
        if " ".join(scene["captionPhrases"]) != scene["text"]:
            raise SystemExit(f"Caption wording differs from narration in {scene['id']}")
        begin = 0
        for phrase in scene["captionPhrases"]:
            end = begin + len(phrase.split())
            captions.append({"start": times[begin][0], "end": times[end-1][1], "text": phrase})
            begin = end
        result.append({"id": scene["id"], "start": times[0][0], "end": times[-1][1], "captions": captions})
        cursor += len(words)
        continue
    begin = 0
    for i, word in enumerate(words):
        chunk = " ".join(words[begin:i+1])
        next_word = words[i+1] if i+1 < len(words) else ""
        boundary = word.endswith((".", "?", "!")) or len(chunk + " " + next_word) > 76 or i-begin >= 10
        if boundary or i == len(words)-1:
            captions.append({"start": times[begin][0], "end": times[i][1], "text": chunk})
            begin = i+1
    result.append({"id": scene["id"], "start": times[0][0], "end": times[-1][1],
                   "captions": captions})
    cursor += len(words)
(ROOT / "film-timing.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"scenes": len(result), "differences": differences}, indent=2))
