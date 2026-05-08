#!/usr/bin/env python3
"""
sync.py — sync external (lav) audio to a video file by cross-correlation.

The two recordings should each contain a sharp shared event near their
start. A clap is the canonical choice — sub-30 ms broadband transient,
shows up as a clear peak in cross-correlation regardless of mic
placement. Whatever you use, do it within the first ~60s of recording
because we only search the first SEARCH_SECONDS of each.

Inputs:
- video : any file ffmpeg can read; we use its embedded camera audio
          for the correlation reference (don't need to demux first).
- audio : the external audio to sync (e.g. DJI Mic Mini lav).

Output:
- prints offset (seconds) to stdout, with this sign convention:
    offset = the time within the external audio file that aligns with
             video t=0.
    > 0: external started rolling BEFORE video — has lead-in to skip.
         Mux applies `-ss offset` to the external input.
    < 0: external started rolling AFTER video — needs to be delayed.
         Mux applies `-itsoffset abs(offset)` to the external input.
- writes a `.sync.json` sidecar next to the video with offset + confidence
- if --output is given, muxes the synced output: video stream copied,
  external audio replacing camera audio, encoded AAC 192k.

Why not just pad with silence? `-itsoffset` on the input is the same
thing without re-encoding; cleaner and lossless on the audio side.
Then -shortest cuts the muxed output to whichever input ends first
(usually the video, since we trim or delay the audio to match).

Why 8 kHz mono internally? Cross-correlation peak location is decided
by the lowest-frequency content present, and a clap has plenty of
sub-4-kHz energy. 8 kHz keeps memory + FFT cost trivial even on a 30
min recording. Adjust SAMPLE_RATE up only if you have an unusually
narrowband shared event.

Usage:
  ./tools/video-venv/bin/python marketing/video/sync.py \\
      <video.mp4> <audio.m4a> [-o <output.mp4>] [--search-seconds 120]

Without -o: prints offset, writes sidecar, no muxing — useful when
you want to inspect the offset before committing.

Dependencies: ffmpeg + ffprobe on PATH; numpy + scipy in
tools/video-venv (see workflow.md for setup).
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.signal import correlate, correlation_lags

SAMPLE_RATE = 8000  # 8 kHz mono is plenty for clap-peak alignment


def decode_to_array(path: str, sample_rate: int = SAMPLE_RATE,
                    max_seconds: float | None = None) -> np.ndarray:
    """Decode any ffmpeg-readable file to a mono float32 numpy array."""
    cmd = ["ffmpeg", "-i", path]
    if max_seconds is not None:
        cmd += ["-t", f"{max_seconds:.3f}"]
    cmd += [
        "-f", "s16le", "-ac", "1", "-ar", str(sample_rate),
        "-loglevel", "error", "pipe:1",
    ]
    proc = subprocess.run(cmd, capture_output=True, check=True)
    return np.frombuffer(proc.stdout, dtype=np.int16).astype(np.float32) / 32768.0


def find_offset_seconds(reference: np.ndarray, target: np.ndarray,
                        sample_rate: int) -> tuple[float, float]:
    """
    Compute the offset such that target[round(offset*sr):] aligns with reference[0:].

    Returns (offset_seconds, confidence_ratio). Confidence is peak / second-peak;
    >2 is a clear clap, <1.5 means correlation is ambiguous (no shared transient
    or both signals are mostly noise).
    """
    # Mean-remove to avoid DC bias dominating cross-correlation.
    a = reference - reference.mean()
    b = target - target.mean()

    corr = correlate(a, b, mode="full", method="fft")
    lags = correlation_lags(len(a), len(b), mode="full")
    abs_corr = np.abs(corr)

    peak_idx = int(np.argmax(abs_corr))
    peak_lag = int(lags[peak_idx])  # samples that target leads reference

    # Confidence: peak vs the next-highest local peak at least 0.5 s away.
    sr_window = sample_rate // 2
    masked = abs_corr.copy()
    lo = max(0, peak_idx - sr_window)
    hi = min(len(masked), peak_idx + sr_window + 1)
    masked[lo:hi] = 0
    second_peak = float(masked.max()) if masked.max() > 0 else 1.0
    confidence = float(abs_corr[peak_idx]) / second_peak

    # Convert lag to seconds. lag>0 means target leads reference;
    # we report offset as how-much-target-starts-AFTER-reference, so negate.
    offset_seconds = -peak_lag / sample_rate
    return offset_seconds, confidence


def mux(video: str, audio: str, output: str, offset_seconds: float) -> None:
    """Mux the external audio onto the video, applying offset.

    See module docstring for the sign convention. In short:
      offset >= 0 → external has lead-in; skip into it with -ss.
      offset <  0 → external started late; delay it with -itsoffset.
    """
    if offset_seconds >= 0:
        cmd = [
            "ffmpeg", "-y",
            "-i", video,
            "-ss", f"{offset_seconds:.3f}", "-i", audio,
            "-map", "0:v", "-map", "1:a",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-shortest", output,
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            "-i", video,
            "-itsoffset", f"{-offset_seconds:.3f}", "-i", audio,
            "-map", "0:v", "-map", "1:a",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-shortest", output,
        ]
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser(
        description="Cross-correlate camera audio against external audio "
                    "to find offset, then optionally mux.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("video", help="Video file (uses its embedded audio for the correlation reference)")
    ap.add_argument("audio", help="External audio file to sync to the video")
    ap.add_argument("-o", "--output", help="Output muxed file. Omit to dry-run.")
    ap.add_argument("--search-seconds", type=float, default=120.0,
                    help="Search window at start of each file (default: 120 s)")
    args = ap.parse_args()

    print(f"Decoding {args.video} (first {args.search_seconds}s)...", file=sys.stderr)
    ref = decode_to_array(args.video, max_seconds=args.search_seconds)
    print(f"Decoding {args.audio} (first {args.search_seconds}s)...", file=sys.stderr)
    tgt = decode_to_array(args.audio, max_seconds=args.search_seconds)

    print(f"Cross-correlating ({len(ref)} vs {len(tgt)} samples)...", file=sys.stderr)
    offset, confidence = find_offset_seconds(ref, tgt, SAMPLE_RATE)

    action = "skip into external (-ss)" if offset >= 0 else "delay external (-itsoffset)"
    print(f"Offset: {offset:+.3f} s  (confidence {confidence:.2f}; {action})",
          file=sys.stderr)
    if confidence < 1.5:
        print("WARNING: low confidence — verify by listening to a synced sample.",
              file=sys.stderr)

    sidecar_payload = json.dumps({
        "video": args.video,
        "audio": args.audio,
        "offset_seconds": offset,
        "confidence": confidence,
        "search_seconds": args.search_seconds,
        "sample_rate_hz": SAMPLE_RATE,
    }, indent=2)

    # Write sidecar next to the source video. Downstream tooling that has
    # the source path (e.g., for re-syncing) can find the offset there.
    src_sidecar = Path(args.video + ".sync.json")
    src_sidecar.write_text(sidecar_payload)
    print(f"wrote {src_sidecar}", file=sys.stderr)

    print(f"{offset:.6f}")  # stdout for piping

    if args.output:
        print(f"Muxing -> {args.output}", file=sys.stderr)
        mux(args.video, args.audio, args.output, offset)
        print(f"wrote {args.output}", file=sys.stderr)
        # Also write a sidecar next to the muxed output. Downstream
        # tooling that operates on the synced file (cut.py,
        # make-subtitles.py) finds it adjacent to the input it knows
        # about, without needing the original source video path.
        out_sidecar = Path(args.output + ".sync.json")
        out_sidecar.write_text(sidecar_payload)
        print(f"wrote {out_sidecar}", file=sys.stderr)


if __name__ == "__main__":
    main()
