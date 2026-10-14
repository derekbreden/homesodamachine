#!/usr/bin/env python3
"""Render and finish the studio film, with resumable source frame sequences."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ACTION_SHOTS = {"can", "case", "carry", "shelf", "under", "select", "lever", "pour", "fizz"}
MECHANISM_SHOTS = {"under", "select", "lever"}
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--fps", type=int, default=4, help="Source cadence for slow camera moves")
parser.add_argument("--action-fps", type=int, default=8, help="Source cadence for object and liquid movement")
parser.add_argument("--mechanism-fps", type=int, default=24, help="Native source cadence for cabinet, display and lever movement")
parser.add_argument("--width", type=int, default=1920)
parser.add_argument("--samples", type=int, default=16)
parser.add_argument("--shots", nargs="+", help="Render selected shots; retain the other source sequences")
parser.add_argument("--fresh", action="store_true", help="Replace the selected shots' generated frames")
parser.add_argument("--blender", default=shutil.which("blender") or "/Applications/Blender.app/Contents/MacOS/Blender")
parser.add_argument("--picture-only", action="store_true")
parser.add_argument("--finish-only", action="store_true")
args = parser.parse_args()
story = json.loads((HERE / "story.json").read_text())
out = HERE / "out"
out.mkdir(exist_ok=True)
shots = [s["id"] for s in story["scenes"] if s["id"] not in {"reset", "closing"}]
rates = {shot: args.mechanism_fps if shot in MECHANISM_SHOTS else
         args.action_fps if shot in ACTION_SHOTS else args.fps for shot in shots}
frames_root = out / "frames" / f"{args.fps}-{args.action_fps}-{args.mechanism_fps}fps-{args.width}px-{args.samples}spp"
plan = {"width": args.width, "height": round(args.width*9/16), "samples": args.samples,
        "source_fps": rates, "frames": str(frames_root.relative_to(HERE)),
        "delivery_fps": story["fps"], "duration": story["duration"]}
(out / "render-plan.json").write_text(json.dumps(plan, indent=2) + "\n")

def run(command):
    print("RUN " + " ".join(map(str, command)), flush=True)
    subprocess.run(list(map(str, command)), cwd=ROOT, check=True)

if not args.finish_only:
    # Separate Blender lifetimes keep each shot's acceleration data bounded on
    # the shared render host. Completed frames remain available for a resume.
    for shot, fps in rates.items():
        if args.shots and shot not in args.shots:
            continue
        if args.fresh and (frames_root / shot).exists():
            shutil.rmtree(frames_root / shot)
        run([args.blender, "--background", "--factory-startup", "--python-exit-code", "1", "--python", HERE / "stage.py", "--",
             "--shots", shot, "--fps", fps, "--width", args.width, "--samples", args.samples,
             "--frames-root", frames_root])
if not args.picture_only:
    audio_runtime = ROOT / "tools/video-venv/bin/python"
    run([audio_runtime, HERE / "audio.py"])
    run([audio_runtime, HERE / "finish.py", "--fps", args.fps, "--frames", frames_root,
         *[value for shot, fps in rates.items() if fps != args.fps
           for value in ("--source-fps", f"{shot}={fps}")]])
