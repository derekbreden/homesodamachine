# Explainer sound

The delivery master is `mix-master.wav`: 102.033333 seconds, stereo 48 kHz,
24-bit PCM. Its measured integrated loudness is −16.00 LUFS, true peak
−2.61 dBTP and loudness range 5.8 LU. Two-pass normalization remains linear.

`narration-source.wav` is the original connected Gemini Charon performance,
generated with `gemini-3.8-flash-tts`. `provenance.json` records its model,
generation time, script hash and recording hash. The request uses Google's
[Interactions TTS API](https://ai.google.dev/gemini-api/docs/speech-generation).
Credentials come from the local environment or the existing user-owned key file;
they are absent from production data.

The voice edit preserves recorded word speed. `edit-plan.json` records 17.700
seconds of opening/closing handles and inserted picture breaths at quiet phrase
gaps. `voice-master.wav` is the resulting 48 kHz mono voice, with a 65 Hz high-pass
and foreground voice normalization. The last spoken word ends at 99.980 seconds.

`score-stem.wav` is an original procedural ambient composition with slow open
voicings and a sparse glass-like figure. `effects-stem.wav` supplies restrained
enclosure motion, finite gas admission, jet and entrainment, refrigerant flow,
pour and fizz textures. The pictured pour and its sound run from 87.500 to
95.300 seconds. The score and effects ease below narration. All musical and
effects sounds are synthesized by `../make-audio.py`; no stock audio is used.

`captions-edited.json` and `narration-edited-words.json` describe the edited voice
clock. The canonical word list retains the script's spelling; the raw Whisper
recognition is retained in `narration-words.json` and `transcription.json`.
`film.srt` and `film.vtt` contain 40 balanced, synchronized English cues.
`timing.json` provides the scene cuts and the 3061-frame, 30 fps picture clock.

Rebuild derived sound from the retained recording and timing metadata:

```sh
tools/video-venv/bin/python marketing/video/how-carbonation-works/edit-audio.py
tools/video-venv/bin/python marketing/video/how-carbonation-works/make-audio.py
```

`../generate-narration.py --align-only` regenerates raw word and phrase timing
from the retained recording with the installed MLX Whisper model. Running that
script without `--align-only` requests a new Gemini performance.

`audio-report.json` records the stereo master measurements, hashes, sound clock,
stems and original composition parameters. `audio-review.txt` records an
independent review of the recorded narration.
