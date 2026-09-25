#!/usr/bin/env python3
"""Generate the tour voiceover using a local Gemini credential."""

import argparse
import base64
import json
import os
from pathlib import Path
import urllib.error
import urllib.request
import wave

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--key-file", type=Path, default=Path.home() / "Developer/.gemini_key")
    parser.add_argument("--voice")
    parser.add_argument("--output", type=Path, default=ROOT / "audio/narration.wav")
    args = parser.parse_args()
    config = json.loads((ROOT / "narration.json").read_text())
    key = os.environ.get("GEMINI_API_KEY") or args.key_file.expanduser().read_text().strip()
    if key.startswith(("export ", "GEMINI_API_KEY=", "GOOGLE_API_KEY=")):
        key = key.split("=", 1)[1].strip().strip("\"'")
    payload = {
        "model": config["model"],
        "input": [{"type": "user_input", "content": [{
            "type": "text", "text": config["text"],
            "annotations": [{"type": "speech_metadata", "style": config["style"]}],
        }]}],
        "response_format": {"type": "audio"},
        "generation_config": {"speech_config": [{"voice": args.voice or config["voice"]}]},
    }
    request = urllib.request.Request(
        "https://generativelanguage.googleapis.com/v1beta/interactions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            result = json.load(response)
    except urllib.error.HTTPError as error:
        detail = error.read().decode().replace(key, "[REDACTED]")
        raise SystemExit(f"Gemini HTTP {error.code}: {detail[:2000]}") from None
    blocks = [content for step in result.get("steps", [])
              if step.get("type") == "model_output"
              for content in step.get("content", []) if content.get("type") == "audio"]
    if not blocks:
        raise SystemExit("Gemini returned no audio block.")
    audio = base64.b64decode(blocks[-1]["data"])
    if audio[:4] != b"RIFF":
        raise SystemExit("Expected WAV audio from the Gemini interactions endpoint.")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(audio)
    with wave.open(str(args.output)) as wav:
        duration = wav.getnframes() / wav.getframerate()
    print(json.dumps({"output": str(args.output), "voice": args.voice or config["voice"],
                      "duration": round(duration, 3), "bytes": len(audio)}))


if __name__ == "__main__":
    main()
