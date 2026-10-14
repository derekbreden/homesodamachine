#!/usr/bin/env python3
"""Finish the 64-second studio film from Blender's local PNG sequences.

    tools/cad-venv/bin/python marketing/video/one-less-errand/studio/finish.py --fps 24

``--fps`` is the rendered source cadence; delivery is always 1920 × 1080 at 24 fps.
Lower frame rates receive motion-compensated interpolation within each shot.
Use repeated ``--source-fps pour=12`` overrides for a different source cadence.
``--draft`` uses a faster encoder. ``--cards-only`` writes the closing-card proof.
The source frame sequence for each shot starts at 00000.png. Audio comes from
out/mix-master.wav, and the source timing comes from story.json beside this file.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    # Keep the command useful from a regular Python installation on this project.
    runtime = Path(__file__).resolve().parents[4] / "tools/cad-venv/bin/python"
    if runtime.exists() and Path(sys.executable).absolute() != runtime.absolute():
        import os
        os.execv(str(runtime), [str(runtime), str(Path(__file__).resolve()), *sys.argv[1:]])
    raise SystemExit("Pillow is required. Run this with tools/cad-venv/bin/python.")


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
OUT = HERE / "out"
WIDTH, HEIGHT, DELIVERY_FPS = 1920, 1080, 24
COBALT = (23, 73, 209)
ICE = (220, 230, 255)
WHITE = (255, 255, 255)
FONT = HERE / "fonts/Montserrat.ttf"
BRAND = REPO / "web/public/brand"
RESAMPLE = Image.Resampling.LANCZOS
DELIVERY_COLOR = ("scale=out_color_matrix=bt709:out_range=tv,format=yuv420p,"
                  "setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709,setsar=1")


def run(command: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(command, check=True, **kwargs)


def ffmpeg(*args: str) -> list[str]:
    return ["ffmpeg", "-hide_banner", "-loglevel", "warning", "-nostdin", "-y", *map(str, args)]


def font(size: int, weight: int = 500) -> ImageFont.FreeTypeFont:
    result = ImageFont.truetype(str(FONT), size)
    result.set_variation_by_axes([weight])
    return result


def tracked_text(text: str, size: int, weight: int = 500, tracking: float = 0,
                 color: tuple = WHITE) -> Image.Image:
    face = font(size, weight)
    # A large pad protects ascenders, descenders, and fractional glyph placement.
    width = math.ceil(face.getlength(text) + tracking * (len(text) - 1))
    layer = Image.new("RGBA", (width + size, size * 3))
    draw = ImageDraw.Draw(layer)
    for index, char in enumerate(text):
        x = size / 2 + face.getlength(text[:index + 1]) - face.getlength(char) + tracking * index
        draw.text((x, size * 2), char, font=face, fill=color, anchor="ls")
    return layer.crop(layer.getbbox())


def vector_png(source: Path, target: Path, width: int) -> Image.Image:
    """Rasterize the checked-in SVG artwork without substituting its lettering."""
    code = """
const sharp = require(process.argv[1]);
sharp(process.argv[2], {density: 288}).trim({threshold: 2})
 .resize({width: Number(process.argv[4])}).png().toFile(process.argv[3]);
"""
    run(["node", "-e", code, str(REPO / "tools/render/node_modules/sharp"),
         str(source), str(target), str(width)], stdout=subprocess.DEVNULL)
    return Image.open(target).convert("RGBA")


def ease(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return 1 - (1 - value) ** 3


def composite_at(frame: Image.Image, layer: Image.Image, xy: tuple[int, int], alpha: float):
    if alpha <= 0:
        return
    if alpha < 1:
        layer = layer.copy()
        layer.putalpha(layer.getchannel("A").point(lambda a: round(a * alpha)))
    frame.paste(layer, xy, layer)


def closing_assets(work: Path) -> list[tuple[Image.Image, tuple[int, int], float, float, int]]:
    logo = vector_png(BRAND / "wordmark-reverse.svg", work / "wordmark.png", 370)
    title = tracked_text("One less errand.", 138, 550, -4.1)
    domain = tracked_text("homesodamachine.com", 30, 450, .2, ICE)
    disclosure = tracked_text("IN DEVELOPMENT  ·  DESIGN FILM", 17, 550, 2.1, ICE)
    return [
        (logo, (145, 172), .06, .48, 0),
        (title, (145, 445), .18, .72, 22),
        (domain, (151, 632), .65, .52, 10),
        (disclosure, (151, 969), .9, .5, 0),
    ]


def closing_frame(t: float, assets) -> Image.Image:
    frame = Image.new("RGB", (WIDTH, HEIGHT), COBALT)
    for layer, (x, y), start, duration, travel in assets:
        progress = ease((t - start) / duration)
        composite_at(frame, layer, (x, round(y + travel * (1 - progress))), progress)
    return frame


def reset_frame() -> Image.Image:
    frame = Image.new("RGB", (WIDTH, HEIGHT), COBALT)
    title = tracked_text("Again.", 145, 650, -4)
    composite_at(frame, title, ((WIDTH - title.width) // 2,
                               (HEIGHT - title.height) // 2 - 8), 1)
    return frame


def encoder_args(draft: bool) -> list[str]:
    return ["-c:v", "libx264", "-preset", "veryfast" if draft else "slow",
            "-crf", "19" if draft else "16", "-pix_fmt", "yuv420p",
            "-r", str(DELIVERY_FPS), "-video_track_timescale", "24000",
            "-color_range", "tv",
            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
            "-movflags", "+faststart"]


def encode_card(shot: dict, target: Path, args, assets):
    frames = round((shot["end"] - shot["start"]) * DELIVERY_FPS)
    command = ffmpeg("-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{WIDTH}x{HEIGHT}",
                     "-framerate", str(DELIVERY_FPS), "-i", "pipe:0", "-an",
                     "-vf", DELIVERY_COLOR,
                     "-frames:v", str(frames), *encoder_args(args.draft), str(target))
    proc = subprocess.Popen(command, stdin=subprocess.PIPE)
    try:
        assert proc.stdin is not None
        reset = reset_frame().tobytes()
        for index in range(frames):
            data = closing_frame(index / DELIVERY_FPS, assets).tobytes() if shot["id"] == "closing" else reset
            proc.stdin.write(data)
        proc.stdin.close()
        if proc.wait():
            raise subprocess.CalledProcessError(proc.returncode, command)
    except BaseException:
        proc.kill()
        proc.wait()
        raise


def label_asset(text: str, target: Path):
    layer = Image.new("RGBA", (WIDTH, HEIGHT))
    if text == "__wordmark__":
        logo = vector_png(BRAND / "wordmark.svg", target.parent / "wordmark-cobalt.png", 290)
        layer.alpha_composite(logo, (135, 112))
        layer.save(target)
        return
    # Limit the protective gradient to the lower picture so the lighting survives.
    gradient = Image.new("RGBA", (1, HEIGHT))
    for y in range(HEIGHT):
        progress = max(0.0, (y - 760) / (HEIGHT - 760))
        gradient.putpixel((0, y), (7, 17, 40, round(85 * progress ** 1.4)))
    layer.alpha_composite(gradient.resize((WIDTH, HEIGHT)))
    label = tracked_text(text, 31, 500, .1)
    layer.alpha_composite(label, (135, 947 - label.height))
    layer.save(target)


LABELS = {"kitchen": [(.55, 5.9, "__wordmark__")],
          "carry": [(0, 1.25, "Into the car."),
                    (1.25, 2.5, "Into the kitchen."),
                    (2.5, 3.75, "Onto a shelf.")],
          "sculpted": [(0, 2.5, "Sculpted / Black")],
          "industrial": [(0, 2.5, "Industrial / White")]}


def encode_sequence(shot: dict, target: Path, args, work: Path):
    duration = shot["end"] - shot["start"]
    source_fps = args.source_fps.get(shot["id"], args.fps)
    source = args.frames / shot["id"] / "%05d.png"
    command = ffmpeg("-framerate", str(source_fps), "-start_number", "0", "-i", str(source))
    if source_fps < DELIVERY_FPS:
        # Minterpolate needs samples on both sides. Padding within this one shot
        # protects its first and last frames without exposing a neighboring cut.
        prepad, postpad = 2 / source_fps, 3 / source_fps
        cadence = (f"tpad=start_mode=clone:start_duration={prepad}:"
                   f"stop_mode=clone:stop_duration={postpad},"
                   f"minterpolate=fps={DELIVERY_FPS}:mi_mode=mci:mc_mode=aobmc:"
                   "me_mode=bidir:me=epzs:mb_size=16:search_param=24:vsbmc=1:"
                   "scd=fdiff:scd_threshold=10,"
                   f"trim=start={prepad}:duration={duration},setpts=PTS-STARTPTS")
    else:
        cadence = f"fps={DELIVERY_FPS},trim=duration={duration},setpts=PTS-STARTPTS"
    # Keep the context wall edges outside the carrying shot's delivered frame.
    framing = ",crop=iw*59/60:ih*59/60:iw/80:ih/120" if shot["id"] == "carry" else ""
    filters = (cadence + framing + f",scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease:flags=lanczos,"
               f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=0x1749D1,setsar=1,"
               f"trim=duration={duration}")
    if not args.no_labels and shot["id"] in LABELS:
        graph = f"[0:v]{filters}[picture];"
        previous = "picture"
        for index, (start, end, text) in enumerate(LABELS[shot["id"]], 1):
            label = work / f"label-{shot['id']}-{index}.png"
            label_asset(text, label)
            command += ["-loop", "1", "-framerate", str(DELIVERY_FPS), "-i", str(label)]
            overlay_source = f"{index}:v"
            if shot["id"] != "carry":
                graph += (f"[{index}:v]format=rgba,fade=t=in:st={start+.18}:d=0.3:alpha=1,"
                          f"fade=t=out:st={max(.5, end - .32)}:d=0.28:alpha=1[label{index}];")
                overlay_source = f"label{index}"
            graph += (f"[{previous}][{overlay_source}]overlay=0:0:shortest=1:"
                      f"format=auto:enable='gte(t,{start})*lt(t,{end})'[picture{index}];")
            previous = f"picture{index}"
        graph += f"[{previous}]{DELIVERY_COLOR}[out]"
        command += ["-filter_complex", graph, "-map", "[out]"]
    else:
        command += ["-vf", filters + "," + DELIVERY_COLOR]
    command += ["-an", "-frames:v", str(round(duration * DELIVERY_FPS)),
                *encoder_args(args.draft), str(target)]
    run(command)


def contain_frame(path: Path, size: tuple[int, int]) -> Image.Image:
    with Image.open(path) as source:
        source = source.convert("RGB")
        source.thumbnail(size, RESAMPLE)
        frame = Image.new("RGB", size, COBALT)
        frame.paste(source, ((size[0] - source.width) // 2, (size[1] - source.height) // 2))
        return frame


def preview_images(shots: list[dict], args, assets):
    # Use the wide home scene as a quiet photographic poster.
    for name in ("home", "kitchen", "wish"):
        candidates = sorted((args.frames / name).glob("[0-9]*.png"))
        if candidates:
            poster = contain_frame(candidates[len(candidates) // 2], (WIDTH, HEIGHT))
            poster.save(args.out / "poster.jpg", quality=94, subsampling=0)
            break
    else:
        closing_frame(3, assets).save(args.out / "poster.jpg", quality=94, subsampling=0)
    columns, tile_w, tile_h, caption_h = 4, 480, 270, 40
    rows = math.ceil(len(shots) / columns)
    sheet = Image.new("RGB", (columns * tile_w, rows * (tile_h + caption_h)), (13, 24, 46))
    draw = ImageDraw.Draw(sheet)
    caption_font = font(17, 500)
    for index, shot in enumerate(shots):
        candidates = sorted((args.frames / shot["id"]).glob("[0-9]*.png"))
        if candidates:
            tile = contain_frame(candidates[len(candidates) // 2], (tile_w, tile_h))
        elif shot["id"] == "closing":
            tile = closing_frame(3, assets).resize((tile_w, tile_h), RESAMPLE)
        elif shot["id"] == "reset":
            tile = reset_frame().resize((tile_w, tile_h), RESAMPLE)
        else:
            tile = Image.new("RGB", (tile_w, tile_h), COBALT)
        x, y = (index % columns) * tile_w, (index // columns) * (tile_h + caption_h)
        sheet.paste(tile, (x, y))
        draw.text((x + 14, y + tile_h + 11), f"{shot['start']:05.2f}  {shot['id']}",
                  fill=ICE, font=caption_font, anchor="lt")
    sheet.save(args.out / "contact-sheet.jpg", quality=92, subsampling=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--fps", type=float, default=24, help="Default Blender source frames per second (default: 24)")
    parser.add_argument("--source-fps", action="append", default=[], metavar="SHOT=FPS",
                        help="Override one source shot's cadence; may be repeated")
    parser.add_argument("--draft", action="store_true", help="Use faster encoding; delivery stays 1080p24")
    parser.add_argument("--force", action="store_true", help="Rebuild cached shot encodes")
    parser.add_argument("--no-labels", action="store_true", help="Omit the occasional scene labels")
    parser.add_argument("--cards-only", action="store_true", help="Write the closing card proof without source frames")
    parser.add_argument("--story", type=Path, default=HERE / "story.json")
    parser.add_argument("--frames", type=Path, default=OUT / "frames")
    parser.add_argument("--audio", type=Path, default=OUT / "mix-master.wav")
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    if args.fps <= 0 or not math.isfinite(args.fps):
        parser.error("--fps must be positive")
    overrides = {}
    for override in args.source_fps:
        try:
            name, rate = override.split("=", 1)
            rate = float(rate)
            if not name or rate <= 0 or not math.isfinite(rate):
                raise ValueError
            overrides[name] = rate
        except ValueError:
            parser.error("--source-fps requires SHOT=FPS with a positive frame rate")
    args.source_fps = overrides
    if not shutil.which("ffmpeg"):
        parser.error("ffmpeg is required")
    args.out.mkdir(parents=True, exist_ok=True)
    work = args.out / "finish-assets"
    work.mkdir(exist_ok=True)
    assets = closing_assets(work)
    closing_frame(3, assets).save(args.out / "closing-card.png")
    reset_frame().save(args.out / "reset-card.png")
    if args.cards_only:
        print(args.out / "closing-card.png")
        return

    story = json.loads(args.story.read_text())
    shots = story.get("shots", story.get("scenes"))
    if not shots:
        parser.error("The story must contain shots or scenes")
    duration = float(story.get("duration", shots[-1]["end"]))
    if not args.audio.exists():
        parser.error(f"Audio master is missing: {args.audio}")
    segments = args.out / "segments"
    segments.mkdir(exist_ok=True)
    cache_path = args.out / ".finish-cache.json"
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
    code_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    encodes = []
    for shot in shots:
        source_fps = args.source_fps.get(shot["id"], args.fps)
        source_frames = sorted((args.frames / shot["id"]).glob("[0-9]*.png"))
        if shot["id"] not in ("reset", "closing"):
            required = round((shot["end"] - shot["start"]) * source_fps)
            if len(source_frames) < required:
                parser.error(f"{shot['id']}: need {required} source frames at {source_fps:g} fps, found {len(source_frames)}")
            for index in range(required):
                if not (args.frames / shot["id"] / f"{index:05d}.png").exists():
                    parser.error(f"{shot['id']}: missing local frame {index:05d}.png")
        signature = hashlib.sha256(json.dumps({
            "shot": shot, "source_fps": source_fps, "draft": args.draft, "labels": not args.no_labels,
            "code": code_hash, "source": str(args.frames.resolve()),
            "font_modified": FONT.stat().st_mtime_ns,
            "wordmark_modified": (BRAND / "wordmark-reverse.svg").stat().st_mtime_ns,
            "frames": len(source_frames),
            "modified": max((p.stat().st_mtime_ns for p in source_frames), default=0),
        }, sort_keys=True).encode()).hexdigest()
        target = segments / f"{shot['id']}.mp4"
        if args.force or cache.get(shot["id"]) != signature or not target.exists():
            print(f"Finishing {shot['id']}  {shot['start']:05.2f}–{shot['end']:05.2f}", flush=True)
            if shot["id"] in ("reset", "closing"):
                encode_card(shot, target, args, assets)
            else:
                encode_sequence(shot, target, args, work)
            cache[shot["id"]] = signature
            cache_path.write_text(json.dumps(cache, indent=2) + "\n")
        encodes.append(target)

    # The concat demuxer preserves each frame exactly; the only final encode is AAC.
    concat = work / "sequence.ffconcat"
    concat.write_text("ffconcat version 1.0\n" + "".join(
        "file '" + str(path.resolve()).replace("'", "'\\''") + "'\n" for path in encodes))
    run(ffmpeg("-f", "concat", "-safe", "0", "-i", str(concat), "-i", str(args.audio),
               "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac",
               "-b:a", "320k", "-ar", "48000", "-t", str(duration), "-movflags", "+faststart",
               "-metadata", "title=One less errand. — Home Soda Machine",
               "-metadata", "comment=In development · Design film", str(args.out / "film.mp4")))
    preview_images(shots, args, assets)
    shutil.copyfile(BRAND / "wordmark-reverse.svg", args.out / "brand.svg")
    shutil.copyfile(FONT, args.out / "Montserrat.ttf")
    for name in ("film.vtt", "film.srt"):
        source = args.audio.parent / name
        target = args.out / name
        if source.exists() and source.resolve() != target.resolve():
            shutil.copyfile(source, target)
    shutil.copyfile(HERE / "preview.html", args.out / "index.html")
    print(f"Finished: {args.out / 'film.mp4'}", flush=True)


if __name__ == "__main__":
    main()
