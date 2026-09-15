#!/usr/bin/env python3
"""Generate the enclosure display's falling-drop animation and motion review sheet.

    tools/cad-venv/bin/python tools/gen_animation_frames.py

Artwork and palette come from brand/mark.svg and brand/palette.json.
The enclosure plays 16 frames at 100 ms each. The faucet stays still while its
orange circle falls; a soft handoff introduces the next drop without an empty
frame. Frame zero is the static mark.
"""

import argparse
import copy
import math
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw

from build_brand_assets import NS, PALETTE, ROOT, render, svg

NUM_FRAMES = 16
FRAME_MS = 100
OUT_DIR = ROOT / "tools/anim_frames"
HEADER_DIR = ROOT / "firmware/src_front/images"
REVIEW_DIR = ROOT / "web/public/brand/motion"
SVG_SIZE = 1024
RENDER_SIZE = 360
VARIANTS = ("pulse", "fall", "float")


def smoothstep(value):
    t = min(1.0, max(0.0, value))
    return t * t * (3 - 2 * t)


def generate_frame_svg(frame, num_frames, variant="fall"):
    t = (frame % num_frames) / num_frames
    pulse = (1 - math.cos(2 * math.pi * t)) / 2
    if variant == "pulse":
        return svg(background=PALETTE["cobalt"], drop_offset=16 * pulse, drop_growth=6 * pulse)
    if variant == "float":
        return svg(background=PALETTE["cobalt"], drop_offset=36 * pulse)
    if variant != "fall":
        raise ValueError(f"Unknown motion variant: {variant}")
    # 192 source pixels is 67.5 px of travel on the panel. Easing holds a quiet
    # beginning and end; only the last six frames share two circular drops.
    # Their squared radii add to the static radius squared. Orange area stays
    # constant while the next bead grows beneath the outlet, in full color.
    fall = 192 * smoothstep(t / .875)
    handoff = smoothstep((t - .625) / .375)
    if t == 0:
        return svg(background=PALETTE["cobalt"])
    root = ET.fromstring(svg(background=PALETTE["cobalt"]))
    drop = root.find(f"{{{NS}}}circle")
    fresh = copy.deepcopy(drop)
    radius = float(drop.attrib["r"])
    top = float(drop.attrib["cy"]) - radius
    drop.set("cy", f'{float(drop.attrib["cy"]) + fall:.5f}')
    drop.set("r", f"{radius * math.sqrt(1 - handoff):.5f}")
    if handoff:
        fresh.set("id", "next-drop")
        fresh_radius = radius * math.sqrt(handoff)
        fresh.set("r", f"{fresh_radius:.5f}")
        fresh.set("cy", f"{top + fresh_radius:.5f}")
        root.append(fresh)
    return ET.tostring(root, encoding="unicode") + "\n"


def rgb565_preview(frame):
    # Expand the same channel bits the panel receives. A sprite frame is an
    # exact view of the RGB565 data, including the quantized background.
    raw = frame.tobytes()
    out = bytearray(len(raw))
    for j in range(0, len(raw), 3):
        r, g, b = raw[j] >> 3, raw[j + 1] >> 2, raw[j + 2] >> 3
        out[j:j+3] = bytes(((r << 3) | (r >> 2), (g << 2) | (g >> 4), (b << 3) | (b >> 2)))
    return Image.frombytes("RGB", frame.size, bytes(out))


def variant_frames(variant):
    return [render(generate_frame_svg(i, NUM_FRAMES, variant), RENDER_SIZE, opaque=True)
            for i in range(NUM_FRAMES)]


def render_frames():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frames = []
    for i in range(NUM_FRAMES):
        artwork = generate_frame_svg(i, NUM_FRAMES)
        (OUT_DIR / f"frame_{i:02d}.svg").write_text(artwork)
        frames.append(render(artwork, RENDER_SIZE, opaque=True))
    previews = [rgb565_preview(frame) for frame in frames]
    previews[0].save(OUT_DIR / "preview.gif", save_all=True, append_images=previews[1:],
                     duration=FRAME_MS, loop=0)
    return frames


def write_headers(frames):
    HEADER_DIR.mkdir(parents=True, exist_ok=True)
    size = RENDER_SIZE
    for i, frame in enumerate(frames):
        data = frame.tobytes()
        vals = [f"0x{(((data[j] & 0xF8) << 8) | ((data[j + 1] & 0xFC) << 3) | (data[j + 2] >> 3)):04X}"
                for j in range(0, len(data), 3)]
        with (HEADER_DIR / f"anim_{i:02d}.h").open("w") as f:
            f.write(f"// Falling-drop frame {i} — {size}x{size} RGB565 bitmap\n")
            f.write("// Generated from brand/mark.svg by tools/gen_animation_frames.py.\n")
            f.write("#pragma once\n\n#include <Arduino.h>\n\n")
            f.write(f"const uint16_t anim_{i:02d}[{size} * {size}] PROGMEM = {{\n")
            for k in range(0, len(vals), 16):
                f.write("    " + ", ".join(vals[k:k + 16]) + ",\n")
            f.write("};\n")
    print(f"Enclosure falling drop: {len(frames)} frames, {size} × {size}, RGB565.")


def write_review(frames):
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    for variant in VARIANTS:
        sequence = frames if variant == "fall" else variant_frames(variant)
        sprite = Image.new("RGB", (RENDER_SIZE * NUM_FRAMES, RENDER_SIZE))
        for i, frame in enumerate(sequence):
            sprite.paste(rgb565_preview(frame), (i * RENDER_SIZE, 0))
        sprite.save(REVIEW_DIR / f"{variant}.png", optimize=True)
    # A contact sheet keeps the complete installed sequence inspectable without
    # playing it. The web comparison uses unscaled 360 px frames from the sprites.
    contact = Image.new("RGB", (720, 816), "#F3F6FF")
    draw = ImageDraw.Draw(contact)
    for i, frame in enumerate(frames):
        x, y = (i % 4) * 180, (i // 4) * 204
        contact.paste(rgb565_preview(frame).resize((180, 180)), (x, y))
        draw.text((x + 8, y + 184), f"{i:02d} / {i * FRAME_MS} ms", fill=PALETTE["navy"])
    contact.save(OUT_DIR / "contact.png", optimize=True)
    template = ROOT / "brand/motion.html"
    (REVIEW_DIR.parent / "motion.html").write_text(template.read_text())
    print("Motion review: web/public/brand/motion.html")


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    frames = render_frames()
    write_headers(frames)
    write_review(frames)


if __name__ == "__main__":
    main()
