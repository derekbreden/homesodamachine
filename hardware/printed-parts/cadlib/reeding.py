"""Reeded textures — half-round flutes, and the warps that bend the path they run on.

A field here reads (ACROSS, ALONG): the distance across the flutes, which decides which
groove a point falls in, and the distance along them, which the warp reads. Both are
lengths in mm measured ON THE SURFACE being cut, never in the part's own frame — so one
field lays one texture on a flat tile (across = x, along = y) and on a standing wall
(across = arc length round the wall, along = height), and a flute crosses a corner
without a seam because arc length does not know the corner is there.

Every field returns a 0…1 depth fraction. How deep 1 is belongs to the caller.

WARPING IS A SHEAR, not new geometry: `chevron` and `wave` ask `groove` about
`across + warp(along)`. Every flute shifts by the same amount at a given `along`, so
they stay exactly parallel and cannot collide — but their spacing measured across the
flute closes by the cosine of the limb angle, so a warped flute reads tighter on its
runs than at its turns.

THE LIMB ANGLE IS THE CONSTRAINT. On a standing wall the warp tilts the groove's own
side surface off vertical by the steepest angle its path makes. A sine's steepest limb
is 2πA/L and a rounded triangle's is less, so `warp_wavelength` is sized off the SINE at
L ≥ 2πA — `limb_angle_deg` reports what a caller actually bought.

PIERCING IS THE SAME FIELD READ AS A MASK. `pierce` is a predicate over `across` and not
a depth: a slot narrower than the groove is struck down the groove's own floor, on the
same centres, and the caller cuts through whatever section stands under it. BOTH JAMBS
RUN WITH THE FLUTES and the groove carries on past both ends of the slot at full depth,
so a pierced field crosses no flute anywhere and owes no stop treatment at any edge it
makes. What the slot is measured against is the MULLION between two slots — `mullion`
and `pierce_max` — and not the section behind the groove floor.
"""

import math

import numpy as np

flute_pitch = 5.0                # THE NOMINAL, which a flat tile and a coupon take as it
                                 # stands. A field that has to CLOSE on something — the box's
                                 # four walls close a whole number of grooves on one plan
                                 # perimeter — lands on its own spacing and passes it in.
flute_width = 4.0                # the land between two flutes is the difference

warp_amplitude = 5.0             # one full pitch: a flute swings into its neighbour's
                                 # station and back
warp_wavelength = 34.0           # >= 2 * pi * warp_amplitude, so the sine — the steeper
                                 # of the two waveforms — keeps its limb inside 45°
chevron_sharpness = 0.97         # 1 is a true triangle apex, 0 is a sine; between them
                                 # it is the radius the apex turns on

pierce_width = 3.1               # the slot struck down a groove's floor, sized on the
                                 # spacing the BOX lands on and not on `flute_pitch`
pierce_shell = 1.74              # the loops the exterior profile lays across a mullion —
                                 # 2 * 0.42 outer + 2 * 0.45 inner, the four the wall
                                 # already carries (enclosure/print-log.md)

_ROOT2 = math.sqrt(2.0)


def walk(segments, s):
    """A run's point and OUTWARD normal at arc length `s` from where that walk begins.

    Everything the field knows about a surface is here. A groove is struck at `s` and drawn
    through the stations either side of it, so a corner costs the field nothing to know about:
    the walk hands back a normal that has already turned.

    A segment is `(kind, length, data)`. A "line" carries its start, its unit tangent and its
    outward normal; an "arc" carries its centre, the angle its outward normal starts at and its
    radius, and TURNS AT ONE OVER THAT RADIUS — a quarter over `pi * r / 2`, and whatever sweep
    its own length comes to otherwise. A run whose plan is a cylinder with flats milled into it
    closes on two arcs of 33.3° and one of 66.6° (`faucet_shell.column_plan_segments`), and a
    turn fixed at a quarter can walk none of them."""
    total = sum(length for _kind, length, _data in segments)
    if not -1e-9 <= s <= total + 1e-9:
        raise AssertionError("arc length walked off the end of a run")
    s = min(max(s, 0.0), total)
    for kind, length, data in segments:
        if s <= length + 1e-9:
            if kind == "line":
                (px, py), (tx, ty), (nx, ny) = data
                return (px + tx * s, py + ty * s), (nx, ny)
            (cx, cy), a0, r = data
            a = a0 + s / r
            n = (math.cos(a), math.sin(a))
            return (cx + r * n[0], cy + r * n[1]), n
        s -= length
    raise AssertionError("arc length walked off the end of a run")


def rounded_rect_segments(x_len, y_len, r):
    """A rounded rectangle centred on the origin, as segments, walked from the MIDDLE OF ITS
    −X WALL heading −Y — four straight runs and the four quarter turns between them.

    THE DATUM IS THE WALL CENTRE, and that is what makes the field symmetric. `reeding.groove`
    is an even function of arc length, so a field struck from a station on a mirror plane of
    the footprint is symmetric about that plane at any pitch — nothing has to be arranged for
    it. The OTHER mirror plane is the one that has to be bought, and an even flute count is
    what buys it: reflecting about it maps `s` to `half - s`, which is a whole number of
    pitches from `-s` only when the count is even.

    A piece that installs spun a half turn buys the same thing with the same coin. The spin
    maps `s` to `s + half`; on an even count that is a whole number of pitches and the two
    pieces' grooves land on each other."""
    run_x = x_len - 2.0 * r
    run_y = y_len - 2.0 * r
    turn = math.pi * r / 2.0
    x0, x1 = -x_len / 2.0, x_len / 2.0
    y0, y1 = -y_len / 2.0, y_len / 2.0
    return (
        ("line", run_y / 2.0, ((x0, 0.0), (0.0, -1.0), (-1.0, 0.0))),
        ("arc", turn, ((x0 + r, y0 + r), math.pi, r)),
        ("line", run_x, ((x0 + r, y0), (1.0, 0.0), (0.0, -1.0))),
        ("arc", turn, ((x1 - r, y0 + r), -math.pi / 2.0, r)),
        ("line", run_y, ((x1, y0 + r), (0.0, 1.0), (1.0, 0.0))),
        ("arc", turn, ((x1 - r, y1 - r), 0.0, r)),
        ("line", run_x, ((x1 - r, y1), (-1.0, 0.0), (0.0, 1.0))),
        ("arc", turn, ((x0 + r, y1 - r), math.pi / 2.0, r)),
        ("line", run_y / 2.0, ((x0, y1 - r), (0.0, -1.0), (-1.0, 0.0))),
    )



def groove(across, pitch=flute_pitch, width=flute_width):
    """Half-round grooves `width` across on `pitch` centres, as a 0…1 depth fraction."""
    offset = (across + pitch / 2.0) % pitch - pitch / 2.0
    return np.sqrt(np.clip(1.0 - (offset / (width / 2.0)) ** 2, 0.0, None))


def _phase(along):
    return 2.0 * np.pi * along / warp_wavelength


def rounded_triangle(along):
    """A triangle wave of amplitude 1 whose apex turns on a radius. `arcsin` of a sine
    scaled short of 1 never reaches the corner, and `chevron_sharpness` is how close it
    gets — a sharp apex reads as a blob and not a crease at any bead the box lays."""
    return (np.arcsin(chevron_sharpness * np.sin(_phase(along)))
            / math.asin(chevron_sharpness))


def limb_angle_deg(slope_factor):
    """The steepest angle a warped flute's path makes with its own axis — on a standing
    wall, how far the groove's side surface tilts off vertical."""
    return math.degrees(math.atan(
        slope_factor * 2.0 * math.pi * warp_amplitude / warp_wavelength))


def chevron_limb_deg():
    return limb_angle_deg(chevron_sharpness / math.asin(chevron_sharpness))


def wave_limb_deg():
    return limb_angle_deg(1.0)


def straight(across, along):
    return groove(across)


def chevron(across, along):
    return groove(across + warp_amplitude * rounded_triangle(along))


def wave(across, along):
    return groove(across + warp_amplitude * np.sin(_phase(along)))


def cross(across, along, pitch=6.0, width=3.4):
    """The same grooves on both diagonals, deeper winning — a diamond knurl."""
    return np.maximum(groove((across + along) / _ROOT2, pitch, width),
                      groove((across - along) / _ROOT2, pitch, width))


def pierce(across, pitch=flute_pitch, slot=pierce_width, every=1, datum=0.0):
    """Which `across` stations stand over open air — `slot` across, down the floor of
    every `every`-th groove, on the same centres `groove` strikes.

    `datum` is the centre of a pierced groove, which is all `every` needs to count from;
    at `every` = 1 it does not read.

    `pitch` DEFAULTS TO THE NOMINAL and a caller whose field closes on something passes
    the spacing it landed on — as `pierce_width` is itself sized against.

    The jambs stand `slot / 2` off the groove's own centre, so what is left over one is
    `groove(slot / 2)` of the depth — the section a mullion is thinnest at."""
    offset = (across + pitch / 2.0) % pitch - pitch / 2.0
    index = np.rint(across / pitch) - round(datum / pitch)
    return (np.abs(offset) <= slot / 2.0) & (np.mod(index, every) == 0)


def mullion(pitch=flute_pitch, slot=pierce_width, every=1):
    """The solid standing between two slots, measured across."""
    return every * pitch - slot


def pierce_max(shell=pierce_shell, pitch=flute_pitch, every=1):
    """The widest slot that still leaves `shell` of mullion between two of them."""
    return every * pitch - shell


def open_fraction(pitch=flute_pitch, slot=pierce_width, every=1):
    """How much of a pierced field is open, as a fraction — free area per unit height
    over the wall's own area per unit height."""
    return slot / (every * pitch)
