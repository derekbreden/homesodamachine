# Video cuts and captions

`hsm-marketing cut SOURCE CUTS OUTPUT` assembles authored source ranges and
freezes, applies dissolves and graphics, and burns captions into the picture.
Run it on demand through `tools/run`. Supply `--overlays SIDECAR` for the
[graphics and sound-cue manifest](overlays.md), or `--no-overlays`.

The cut list is either a JSON array of entries or an object containing `cuts`
and an optional `sources` object. Each key in `sources` is a source-video path;
its value supplies `transcript` and `sync_offset` for caption generation.
Paths resolve from the working directory. The command's source argument is the
default for entries without a `source` field.

| Entry field | Meaning |
| --- | --- |
| `type` | `range` or `freeze`; omitted means `range`. |
| `source` | Optional source-video path. |
| `start`, `end` | Range boundaries in source-video seconds. |
| `at`, `duration` | Freeze source time and held-picture duration, in seconds. Freezes contain silent audio. |
| `section` | Optional lower banner for a narrative section. |
| `tool` | Optional small tool or material label. |
| `label` | An editorial description. |
| `transcript`, `sync_offset` | Optional caption metadata overriding the source mapping. |

`--fade` sets the overlap between adjacent entries. A prepended `--title`
uses `--title-duration` and participates in the same dissolves. Overlay times
belong to the assembled output, including title, overlaps and freezes. Inspect
the selected source frame before placing an annotation over a freeze.

`hsm-marketing make-subtitles CUTS OUTPUT.ass` follows the same output clock.
Give it the same `--fade` and prepended `--title-duration` values as the cut
command. Every spoken cut needs its `source` path, even when the cut renderer
uses the default source argument. The caption generator reads Whisper segment
and word timestamps, drops words truncated by a source boundary, filters short
filler hallucinations, and splits phrases at words and sentence endings. A
freeze advances the clock without adding speech.

Caption metadata may be inline, in `sources`, or discovered beside the inputs:
the transcript is `transcripts/<source-stem>.json`, and the offset comes from
`<source-path>.sync.json`. The sign convention is `audio_time = video_time +
sync_offset`. `hsm-marketing sync VIDEO AUDIO` measures that offset from the
shared waveform; `-o OUTPUT` also replaces camera audio with the external track.

`hsm-marketing segment TRANSCRIPT` proposes candidate scenes by clustering
Whisper speech and adding context. Tune `--gap`, `--pad-before` and
`--pad-after` to the recording, then refine those candidates against the
picture. Its output preserves the included transcript segments and the chosen
parameters. Command help and the
[native implementation](../../tools/hsm/marketing/src/video.rs) own defaults.
