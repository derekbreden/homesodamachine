#!/usr/bin/env python3
"""Record the explainer with Gemini Charon and align its recorded words.

Run with tools/video-venv/bin/python. Credentials stay in the local environment
or the existing user-owned key file; no credential is written to production data.
"""

from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import urllib.error
import urllib.request
import wave

ROOT = Path(__file__).resolve().parent
API = "https://generativelanguage.googleapis.com/v1beta/interactions"


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def credential(path: Path) -> str:
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        key = path.expanduser().read_text().strip()
    if key.startswith(("export ", "GEMINI_API_KEY=", "GOOGLE_API_KEY=")):
        key = key.split("=", 1)[1].strip().strip("\"'")
    if not key:
        raise SystemExit("No local Gemini credential is configured.")
    return key


def record(config: dict, key_file: Path, source: Path) -> dict:
    key = credential(key_file)
    payload = {
        "model": config["model"],
        "input": [{"type": "user_input", "content": [{
            "type": "text", "text": config["text"],
            "annotations": [{"type": "speech_metadata", "style": config["style"]}],
        }]}],
        "response_format": {"type": "audio", "mime_type": "audio/wav", "sample_rate": 24000},
        "generation_config": {"speech_config": [{"voice": config["voice"]}]},
    }
    request = urllib.request.Request(
        API, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": key}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=600) as response:
            result = json.load(response)
    except urllib.error.HTTPError as error:
        detail = error.read().decode().replace(key, "[REDACTED]")
        raise SystemExit(f"Gemini HTTP {error.code}: {detail[:1800]}") from None
    blocks = [content for step in result.get("steps", [])
              if step.get("type") == "model_output"
              for content in step.get("content", []) if content.get("type") == "audio"]
    if not blocks:
        raise SystemExit("Gemini returned no audio block.")
    audio = base64.b64decode(blocks[-1]["data"])
    if audio[:4] != b"RIFF":
        raise SystemExit("Gemini did not return the requested WAV recording.")
    source.write_bytes(audio)
    return {"service": "Google Gemini Interactions API", "model": config["model"],
            "voice": config["voice"], "generated_at": datetime.now(timezone.utc).isoformat(),
            "script_sha256": hashlib.sha256(config["text"].encode()).hexdigest(),
            "source_sha256": hashlib.sha256(audio).hexdigest()}


def wav_info(path: Path) -> dict:
    with wave.open(str(path)) as wav:
        return {"sample_rate": wav.getframerate(), "channels": wav.getnchannels(),
                "sample_width": wav.getsampwidth(), "frames": wav.getnframes(),
                "duration": round(wav.getnframes() / wav.getframerate(), 6)}


def normalized(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower().replace("₂", "2"))


def timestamp(seconds: float, separator=".") -> str:
    total = round(max(0, seconds) * 1000)
    hour, rest = divmod(total, 3600000)
    minute, rest = divmod(rest, 60000)
    second, milli = divmod(rest, 1000)
    return f"{hour:02d}:{minute:02d}:{second:02d}{separator}{milli:03d}"


def align(config: dict, source: Path, output_dir: Path, model: str) -> dict:
    import mlx_whisper

    result = mlx_whisper.transcribe(str(source), path_or_hf_repo=model,
                                   language="en", word_timestamps=True,
                                   initial_prompt=config["text"], condition_on_previous_text=False,
                                   verbose=False, temperature=0)
    raw_words = [word for segment in result.get("segments", [])
                 for word in segment.get("words", []) if word.get("word", "").strip()]
    words = [{"word": w["word"].strip(), "start": round(w["start"], 3),
              "end": round(w["end"], 3), "probability": round(w.get("probability", 0), 4)}
             for w in raw_words]
    write_json(output_dir / "transcription.json", result)
    write_json(output_dir / "narration-words.json", words)
    # The transcript comes from the source script. Whisper supplies only timing.
    # A sequential dynamic-programming match tolerates punctuation and compounds.
    import difflib

    expected = config["text"].split()
    expected_keys = [normalized(w) for w in expected]
    spoken_keys = [normalized(w["word"]) for w in words]
    matcher = difflib.SequenceMatcher(a=expected_keys, b=spoken_keys, autojunk=False)
    mapping = {}
    discrepancies = []
    for tag, a0, a1, b0, b1 in matcher.get_opcodes():
        if tag == "equal":
            mapping.update((a0 + i, b0 + i) for i in range(a1 - a0))
        else:
            discrepancies.append({"type": tag, "script": expected[a0:a1],
                                  "heard": [w["word"] for w in words[b0:b1]],
                                  "script_range": [a0, a1], "word_range": [b0, b1]})
            if a1 > a0 and b1 > b0:
                for i in range(a1 - a0):
                    mapping[a0 + i] = min(b1 - 1, b0 + round(i * (b1 - b0 - 1) / max(1, a1 - a0 - 1)))
    captions, cursor = [], 0
    for phrase in config["caption_phrases"]:
        tokens = phrase.split()
        first, last = cursor, cursor + len(tokens) - 1
        if [normalized(w) for w in tokens] != expected_keys[first:last + 1]:
            raise SystemExit(f"Caption phrase does not match the script at word {cursor}: {phrase}")
        while first not in mapping and first < last:
            first += 1
        while last not in mapping and last > first:
            last -= 1
        if first not in mapping or last not in mapping:
            raise SystemExit(f"No word timing found for caption: {phrase}")
        captions.append({"start": words[mapping[first]]["start"],
                         "spoken_end": words[mapping[last]]["end"], "text": phrase})
        cursor += len(tokens)
    for i, caption in enumerate(captions):
        end = caption["spoken_end"] + .18
        if i + 1 < len(captions):
            end = min(end, captions[i + 1]["start"] - .035)
        caption["end"] = round(max(caption["spoken_end"], end), 3)
    write_json(output_dir / "captions.json", captions)
    write_json(output_dir / "alignment-review.json", {
        "model": model, "script_words": len(expected), "recognized_words": len(words),
        "discrepancies": discrepancies,
        "first_word": words[0] if words else None, "last_word": words[-1] if words else None})
    (output_dir / "narration.vtt").write_text("WEBVTT\n\n" + "\n\n".join(
        f"{timestamp(c['start'])} --> {timestamp(c['end'])}\n{c['text']}" for c in captions) + "\n")
    (output_dir / "narration.srt").write_text("\n\n".join(
        f"{i + 1}\n{timestamp(c['start'], ',')} --> {timestamp(c['end'], ',')}\n{c['text']}"
        for i, c in enumerate(captions)) + "\n")
    return {"words": len(words), "captions": len(captions), "discrepancies": discrepancies,
            "spoken_start": words[0]["start"], "spoken_end": words[-1]["end"]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=ROOT / "narration.json")
    parser.add_argument("--key-file", type=Path, default=Path.home() / "Developer/.gemini_key")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "audio")
    parser.add_argument("--align-only", action="store_true")
    parser.add_argument("--no-align", action="store_true")
    parser.add_argument("--whisper-model", default="mlx-community/whisper-base.en-mlx")
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    args.output_dir.mkdir(parents=True, exist_ok=True)
    source = args.output_dir / "narration-source.wav"
    provenance_path = args.output_dir / "provenance.json"
    if not args.align_only:
        provenance = record(config, args.key_file, source)
        # Preserve the connected take and its natural word speed.
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(source),
                        "-ar", "48000", "-ac", "1", "-c:a", "pcm_s24le",
                        str(args.output_dir / "narration.wav")], check=True)
        provenance["source_format"] = wav_info(source)
        # ffprobe supports the 24-bit WAV without depending on Python's wave codec support.
        probe = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries",
                                        "stream=sample_rate,channels,bits_per_raw_sample:format=duration",
                                        "-of", "json", str(args.output_dir / "narration.wav")])
        provenance["production_format"] = json.loads(probe)
        write_json(provenance_path, provenance)
        print(json.dumps({"recorded": str(source), **provenance["source_format"]}), flush=True)
    if not args.no_align:
        alignment = align(config, source, args.output_dir, args.whisper_model)
        print(json.dumps(alignment, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
