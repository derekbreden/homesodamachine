#!/usr/bin/env python3
"""Generate animation frames from the app icon SVG.

Produces 16 SVG frames with:
  - Sinusoidal liquid surface wave (sloshing)
  - Bubbles rising, reaching surface, popping, respawning

Outputs: tools/anim_frames/frame_XX.svg and tools/anim_frames/preview.gif
"""

import argparse
import math
import os
import struct

NUM_FRAMES = 16
OUT_DIR = os.path.join(os.path.dirname(__file__), "anim_frames")
SVG_SIZE = 1024  # original SVG viewBox
RENDER_SIZE = 240  # render at 2x the 240px target for quality, then GIF at this size

# Glass clip boundaries (from SVG)
GLASS_LEFT_TOP = 310
GLASS_RIGHT_TOP = 714
GLASS_BOTTOM = 777
LIQUID_TOP_BASE = 347  # base Y of liquid surface

# Wave parameters
WAVE_AMPLITUDE = 9  # pixels of vertical wave motion
WAVE_POINTS = 40  # number of points along the surface for smooth wave

# Bubble definitions: (cx, cy_start, radius, speed_factor, phase)
# cy range: liquid surface (~347) to glass bottom (~750)
BUBBLES = [
    # speed MUST be integer for seamless looping (1 = one rise-pop cycle per loop)
    # phase offsets stagger the bubbles so they don't all move in unison
    # 4 bubbles matching iOS GlassAnimationView — all submerged at t=0
    {"cx": 440, "r": 42, "phase": 0.0, "speed": 1},
    {"cx": 580, "r": 35, "phase": 0.20, "speed": 1},
    {"cx": 500, "r": 30, "phase": 0.42, "speed": 1},
    {"cx": 620, "r": 26, "phase": 0.62, "speed": 1},
]

# Travel range for bubbles
BUBBLE_BOTTOM = 740
# BUBBLE_TOP is computed per-bubble: surface + radius, so the top edge
# of the bubble touches the surface rather than the center overshooting it


def lerp_glass_x(y):
    """Get glass edge X at a given Y (linear taper from top to bottom)."""
    t = (y - 247) / (777 - 247)
    left = 310 + t * (340 - 310)
    right = 714 + t * (684 - 714)
    return left, right


def wave_surface_y(x, frame, num_frames):
    """Compute the liquid surface Y at position x for a given frame."""
    t = frame / num_frames  # 0..1 through the cycle
    # Normalize x across the glass width at the surface
    x_norm = (x - GLASS_LEFT_TOP) / (GLASS_RIGHT_TOP - GLASS_LEFT_TOP)
    # Two overlapping sine waves for natural sloshing
    y_offset = (
        WAVE_AMPLITUDE * 0.7 * math.sin(2 * math.pi * (t + x_norm * 1.2))
        + WAVE_AMPLITUDE * 0.3 * math.sin(2 * math.pi * (t * 2 - x_norm * 0.8 + 0.5))
    )
    return LIQUID_TOP_BASE + y_offset


def make_liquid_path(frame, num_frames):
    """Generate the liquid fill path with wavy top edge."""
    points = []
    for i in range(WAVE_POINTS + 1):
        x_norm = i / WAVE_POINTS
        x = GLASS_LEFT_TOP + x_norm * (GLASS_RIGHT_TOP - GLASS_LEFT_TOP)
        y = wave_surface_y(x, frame, num_frames)
        points.append((x, y))

    # Build SVG path: wavy top, then down right side, across bottom, up left side
    d = f"M{points[0][0]:.1f} {points[0][1]:.1f}"
    for x, y in points[1:]:
        d += f" L{x:.1f} {y:.1f}"
    # Close: go down to bottom-right, across bottom, up to start
    d += f" L{GLASS_RIGHT_TOP} 800 L{GLASS_LEFT_TOP} 800 Z"
    return d


def make_surface_highlight_path(frame, num_frames):
    """Generate a highlight band that follows the wave surface."""
    top_points = []
    bot_points = []
    for i in range(WAVE_POINTS + 1):
        x_norm = i / WAVE_POINTS
        x = GLASS_LEFT_TOP + x_norm * (GLASS_RIGHT_TOP - GLASS_LEFT_TOP)
        y = wave_surface_y(x, frame, num_frames)
        top_points.append((x, y - 5))
        bot_points.append((x, y + 18))

    d = f"M{top_points[0][0]:.1f} {top_points[0][1]:.1f}"
    for x, y in top_points[1:]:
        d += f" L{x:.1f} {y:.1f}"
    for x, y in reversed(bot_points):
        d += f" L{x:.1f} {y:.1f}"
    d += " Z"
    return d


def bubble_state(bubble, frame, num_frames):
    """Compute bubble position and opacity for a given frame.

    Returns (cx, cy, r, opacity) or None if invisible.
    """
    t = ((frame / num_frames) * bubble["speed"] + bubble["phase"]) % 1.0

    # Per-bubble top: center stops where top edge just touches the surface
    r = bubble["r"]
    bubble_top = LIQUID_TOP_BASE + r + WAVE_AMPLITUDE

    # Travel from bottom to surface over t=0..0.75
    # Pop/fade over t=0.75..0.85
    # Invisible t=0.85..1.0 (respawn delay)

    if t < 0.75:
        # Rising phase
        rise_t = t / 0.75
        # Ease out (decelerate near surface, like real bubbles)
        ease_t = 1 - (1 - rise_t) ** 1.5
        cy = BUBBLE_BOTTOM - ease_t * (BUBBLE_BOTTOM - bubble_top)
        # Slight horizontal wobble
        cx = bubble["cx"] + 8 * math.sin(rise_t * math.pi * 3 + bubble["phase"] * 10)
        opacity = 0.8
        # Grow slightly as they rise (pressure decreases)
        r *= 1.0 + rise_t * 0.15
        return cx, cy, r, opacity
    elif t < 0.85:
        # Popping phase - at surface, shrinking and fading
        pop_t = (t - 0.75) / 0.10
        cy = bubble_top
        cx = bubble["cx"]
        opacity = 0.8 * (1 - pop_t)
        r = r * (1.15 - pop_t * 0.5)
        return cx, cy, r, opacity
    else:
        return None  # invisible during respawn delay


def generate_frame_svg(frame, num_frames):
    """Generate a complete SVG string for one animation frame."""
    liquid_path = make_liquid_path(frame, num_frames)
    highlight_path = make_surface_highlight_path(frame, num_frames)

    # Build bubble elements
    bubble_elements = []
    for b in BUBBLES:
        state = bubble_state(b, frame, num_frames)
        if state is None:
            continue
        cx, cy, r, opacity = state
        # Only render if inside the glass clip area and submerged
        if cy > 250 and cy < 780:
            surface_y = wave_surface_y(cx, frame, num_frames)
            if cy >= surface_y:
                bubble_elements.append(
                    f'    <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" '
                    f'fill="url(#bubbleGlow)" '
                    f'stroke="rgba(255,255,255,{opacity * 0.25:.2f})" '
                    f'stroke-width="2.5" opacity="{opacity:.2f}"/>'
                )

    bubbles_str = "\n".join(bubble_elements)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#1a1a2e"/>
      <stop offset="100%" stop-color="#16213e"/>
    </linearGradient>
    <linearGradient id="liquid" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#e94560"/>
      <stop offset="50%" stop-color="#c23373"/>
      <stop offset="100%" stop-color="#7b2ff7"/>
    </linearGradient>
    <linearGradient id="glassHighlight" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="rgba(255,255,255,0.15)"/>
      <stop offset="40%" stop-color="rgba(255,255,255,0)"/>
    </linearGradient>
    <radialGradient id="bubbleGlow">
      <stop offset="0%" stop-color="rgba(255,255,255,0.5)"/>
      <stop offset="100%" stop-color="rgba(255,255,255,0.1)"/>
    </radialGradient>
    <clipPath id="glassClip">
      <path d="M310 247 L340 747 Q345 777 380 777 L644 777 Q679 777 684 747 L714 247 Z"/>
    </clipPath>
  </defs>

  <!-- Background -->
  <rect width="1024" height="1024" fill="#1a1a2e"/>

  <!-- Glass body -->
  <path d="M310 247 L340 747 Q345 777 380 777 L644 777 Q679 777 684 747 L714 247 Z"
        fill="rgba(255,255,255,0.06)"
        stroke="rgba(255,255,255,0.25)"
        stroke-width="4"/>

  <!-- Liquid fill with wavy surface -->
  <g clip-path="url(#glassClip)">
    <path d="{liquid_path}" fill="url(#liquid)"/>
    <path d="{highlight_path}" fill="rgba(255,255,255,0.12)"/>
{bubbles_str}
  </g>

  <!-- Glass rim highlight -->
  <path d="M310 247 L714 247"
        stroke="rgba(255,255,255,0.35)"
        stroke-width="5"
        stroke-linecap="round"/>

  <!-- Glass left edge highlight -->
  <path d="M314 257 L342 737"
        stroke="rgba(255,255,255,0.1)"
        stroke-width="8"
        stroke-linecap="round"/>

  <!-- Glass surface highlight overlay -->
  <path d="M310 247 L340 747 Q345 777 380 777 L644 777 Q679 777 684 747 L714 247 Z"
        fill="url(#glassHighlight)"/>
</svg>"""
    return svg


def render_frames(size):
    """Render the NUM_FRAMES SVGs to `size`x`size` RGB images composited onto
    the theme background, and write the source SVGs + a GIF preview to OUT_DIR.

    Each display compiles these frames at its own size, so the render size is a
    parameter: the 240px round config display and the 360px 4.3" front display
    share one animation, rendered natively for each (no upscaling)."""
    import io

    import cairosvg
    from PIL import Image

    os.makedirs(OUT_DIR, exist_ok=True)
    frames = []
    for i in range(NUM_FRAMES):
        svg = generate_frame_svg(i, NUM_FRAMES)
        with open(os.path.join(OUT_DIR, f"frame_{i:02d}.svg"), "w") as f:
            f.write(svg)
        png = cairosvg.svg2png(bytestring=svg.encode(), output_width=size, output_height=size)
        img = Image.open(io.BytesIO(png)).convert("RGBA")
        # Composite onto the theme background (0x1a1a2e); drop alpha for RGB565.
        bg = Image.new("RGBA", img.size, (26, 26, 46, 255))
        frames.append(Image.alpha_composite(bg, img).convert("RGB"))

    gif_path = os.path.join(OUT_DIR, "preview.gif")
    frames[0].save(gif_path, save_all=True, append_images=frames[1:], duration=100, loop=0)
    print(f"  GIF preview -> {gif_path}")
    return frames


def write_headers(frames, size, header_dir):
    """Write anim_NN.h RGB565 PROGMEM headers (matching logo_240.h format)."""
    os.makedirs(header_dir, exist_ok=True)
    for i, frame in enumerate(frames):
        data = frame.tobytes()  # RGB, 3 bytes per pixel
        vals = [f"0x{(((data[j] & 0xF8) << 8) | ((data[j + 1] & 0xFC) << 3) | (data[j + 2] >> 3)):04X}"
                for j in range(0, len(data), 3)]
        out = os.path.join(header_dir, f"anim_{i:02d}.h")
        with open(out, "w") as f:
            f.write(f"// Animation frame {i} - {size}x{size} RGB565 bitmap\n")
            f.write("// Auto-generated by tools/gen_animation_frames.py\n")
            f.write("#pragma once\n\n#include <Arduino.h>\n\n")
            f.write(f"const uint16_t anim_{i:02d}[{size} * {size}] PROGMEM = {{\n")
            for k in range(0, len(vals), 16):
                f.write("    " + ", ".join(vals[k:k + 16]) + ",\n")
            f.write("};\n")
        print(f"  Wrote {out}")


def main():
    default_dir = os.path.join(
        os.path.dirname(__file__), "..", "firmware", "src_config", "images"
    )
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--size", type=int, default=RENDER_SIZE,
                    help="square frame edge in px (default %(default)s)")
    ap.add_argument("--header-dir", default=default_dir,
                    help="output dir for anim_NN.h (default: firmware/src_config/images)")
    args = ap.parse_args()

    try:
        frames = render_frames(args.size)
    except ImportError as e:
        print(f"  Missing dependency: {e}\n  Install with: pip install cairosvg Pillow")
        return
    write_headers(frames, args.size, args.header_dir)


if __name__ == "__main__":
    main()
