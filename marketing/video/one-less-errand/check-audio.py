#!/usr/bin/env python3
"""Independent audio review of a supplied production WAV or MP3."""
import base64
import json
from pathlib import Path
import sys
import urllib.error
import urllib.request

source = Path(sys.argv[1])
out = Path(sys.argv[2])
key = (Path.home()/"Developer/.gemini_key").read_text().strip()
if key.startswith(("export ", "GEMINI_API_KEY=", "GOOGLE_API_KEY=")):
    key = key.split("=",1)[1].strip().strip("\"'")
prompt = "Listen critically to this audio for a professional animated product film. Return a concise JSON assessment: usable (boolean), voice_delivery, intelligibility, sonic_defects, abrupt_or_cut_words (with timestamps), music_and_effect_balance if present, and specific improvements only if material. Assess actual sound, not presumed timing. Do not praise by default. The script mentions Home Soda Machine, Sculpted and Industrial faucet styles, black or white, and ends 'One less errand'."
payload = {"model":"gemini-3.8-flash", "input":[{"type":"text","text":prompt},
           {"type":"audio","data":base64.b64encode(source.read_bytes()).decode(),
            "mime_type":"audio/mp3" if source.suffix == ".mp3" else "audio/wav"}]}
request = urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/interactions",
    data=json.dumps(payload).encode(), headers={"Content-Type":"application/json","x-goog-api-key":key})
try:
    with urllib.request.urlopen(request,timeout=180) as response:
        result=json.load(response)
except urllib.error.HTTPError as error:
    raise SystemExit(f"Gemini HTTP {error.code}: {error.read().decode().replace(key,'[REDACTED]')[:400]}") from None
texts=[c["text"] for s in result.get("steps",[]) if s.get("type")=="model_output" for c in s.get("content",[]) if c.get("type")=="text"]
out.write_text("\n".join(texts)+"\n")
print(out.read_text())
