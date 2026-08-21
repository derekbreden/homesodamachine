"""Texture coupon, vent — a section of front-bottom's ±X flank with the condenser vents
pierced down the flutes that are already there, printed the way that piece prints:
STANDING, floor on the bed, build axis up the wall.

Frame: the outer face looks +Y and the interior lies at −Y, so `across` is world X — the
flank is a straight run where the vents stand — and `along` is world Z. The land plane is
y = 0, a groove floors at y = −`flute_depth`, and the inner face is at y = −`wall`. z = 0
is the bed.

THE VENT IS THE GROOVE, PIERCED. A slot narrower than the flute is cut down the flute's
own floor, clean through the section under it. Both jambs run WITH the groove and the
groove carries on past both ends of the slot at full depth, so NOTHING CROSSES A FLUTE
anywhere on this coupon and no `enclosure._flute_stop` treatment is owed at any edge the
opening makes — the box's own rule, that a rim running with the flutes is not one of them.

THE SLOT IS MEASURED AGAINST THE MULLION. A slot takes its width out of the pitch, and
the exterior profile lays [1.74 mm](PIERCE_SHELL) of loops across the mullion that is
left — 2 × 0.42 outer + 2 × 0.45 inner, `enclosure/print-log.md`. At
[4.9569 mm](FLUTE_PITCH) of pitch that ceilings a slot down every groove at
[3.2169 mm](PIERCE_CEILING), which is `reeding.pierce_max`; the [3 mm](SLOT_A) zone
leaves [1.9569 mm](MULLION_A) of mullion, [0.2169 mm](SPARE_A) over the loops. The groove
floor already shipping on the box runs on [0.06 mm](GROOVE_FLOOR_SPARE) of the same
spare. Behind the groove floor stands the flank's whole [6 mm](FLANK_T), which is
the depth the slot is cut through.

THREE ZONES ACROSS, so one print answers the question. They share one field: the pitch,
the profile, the depth and the fade are the same the whole way across, and only the slot
differs.

  * [3 mm](SLOT_A) down EVERY groove — the scheme the box takes.
  * [3.2 mm](SLOT_B) down EVERY groove — the ceiling, to see whether a mullion run down
    to the loops alone telegraphs through to the show face.
  * [4 mm](SLOT_C) down ALTERNATE grooves — the full groove width, which puts the jamb
    on the land's own edge and reads as a balustrade rather than as a vent.

One unpierced groove piers between two zones, and one stands at each end.

EACH SLOT IS A VERTICAL PRISM DRAWN IN XY, terminated top and bottom by a ceiling struck
at `relief_chamfer`, the 45° every relief on this box rises at. The bottom termination
only takes material away as the print climbs and the top one closes at exactly the angle
the box supports nothing steeper than, so the whole coupon prints with no support. Both
sit down inside the groove, in its own shadow, where the slot is narrower than it.

THE LABEL STANDS PROUD OF THE INNER FACE. An engraved one takes its depth out of the
section the flute over it stands on, and `../texture-corner/` printed that: it read
through to the show face as a mark you could find with a fingertip.

An inner foot ramps 45° off the wall at the base, and the field fades to nothing over the
same height at the bed and again at the top arris — `enclosure`'s own `flute_rise`, on the
same smoothstep — so the first layers go down as a clean solid and no groove runs off an
edge to scallop it.
"""

import math
import sys
from pathlib import Path

import cadquery as cq
import trimesh

_here = Path(__file__).resolve()
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware") / "scripts"),
)
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
from _cadq_export import export_assembly
from _materials import WALL_COLORS, one_body
from docgen import substitute_md, substitute_py_comments
import reeding

C_COUPON = WALL_COLORS["front-bottom"]

# --- the wall this is a section of -------------------------------------------------

# THE PITCH IS THE BOX'S, and it is a consequence and not a choice: `enclosure.flute_count`
# grooves close on `enclosure.plan_perimeter` exactly, and the spacing is whatever that
# division lands on.
plan_perimeter = 1333.398224     # = enclosure.plan_perimeter(outer), a 215 × 462 plan on
flute_count = 269                #   `corner_round` 12
pitch = plan_perimeter / flute_count

flute_width = reeding.flute_width       # 4.0 — the groove, the land is the difference
flute_depth = 1.2                # = enclosure.flute_depth
flute_samples = 13               # = enclosure.flute_samples, stations per groove
flute_rise = 5.0                 # = enclosure.flute_rise, the fade at bed and top arris
flute_fade_steps = 12            # = enclosure.flute_fade_steps, stations in that ramp

box_wall = 3.0                   # = enclosure.wall, the section a groove is struck into
# BOTH BOTTOM PIECES CARRY 2 * `enclosure.wall` DOWN THEIR SIDES — the Z lip's own skin,
# slab to rim — so a vent on front-bottom's flank pierces [6 mm](FLANK_T).
wall = 2.0 * box_wall
relief_chamfer = 45.0            # = enclosure.relief_chamfer

height = 120.0
foot = 5.0                       # inner ramp at the base, 45° since it is also its width

# --- the three zones ---------------------------------------------------------------

# (label, scheme, slot width, one slot every this many grooves)
ZONES = (("3.00", "EVERY", 3.000, 1),
         ("3.20", "EVERY", 3.200, 1),
         ("4.00", "ALT", 4.000, 2))
zone_flutes = 8                  # grooves each zone spends
pier_flutes = 1                  # unpierced grooves between two zones, and one at each end,
                                 # so every slot on the coupon has a whole mullion either
                                 # side of it

slot_z = (32.0, 92.0)            # the band the vents open over

label_size = 9.0
scheme_size = 4.5
label_z = 20.5
scheme_z = 11.5
label_proud = 0.8
label_bite = 0.2                 # how far the glyph solid starts inside the inner face
label_font = "Helvetica"
label_kind = "bold"

flute_total = len(ZONES) * zone_flutes + (len(ZONES) + 1) * pier_flutes
# Groove centres sit at whole multiples of `pitch`, which is the phase `reeding.groove`
# and `reeding.pierce` both strike on, so the coupon's own ends fall on land centres.
flute_centres = tuple(k * pitch for k in range(flute_total))
x0 = -pitch / 2.0
x1 = (flute_total - 0.5) * pitch
coupon_x = x1 - x0


def zone_flute_range(index):
    """Which groove indices one zone spends, first and one past the last."""
    first = pier_flutes + index * (zone_flutes + pier_flutes)
    return first, first + zone_flutes


def zone_span(index):
    """One zone's across extent, land centre to land centre."""
    first, last = zone_flute_range(index)
    return (first - 0.5) * pitch, (last - 0.5) * pitch


def slots():
    """Every slot the coupon opens, as (zone index, groove centre, slot width). The mask
    is `reeding.pierce` read at each groove's own centre, with the zone's first groove as
    its datum, so `every` counts from the zone and not from the coupon's end."""
    out = []
    for index, (_label, _scheme, slot, every) in enumerate(ZONES):
        first, last = zone_flute_range(index)
        datum = flute_centres[first]
        for centre in flute_centres[first:last]:
            if reeding.pierce(centre, pitch, slot, every, datum):
                out.append((index, centre, slot))
    return tuple(out)


# --- the wall ----------------------------------------------------------------------


def _reeded_wire(scale, z):
    """The coupon's plan at `scale` of full groove depth, as one closed wire on `z`.

    A land is a straight run and a groove is one spline through `flute_samples` stations
    of `reeding.groove` — the same curve `enclosure._reeded_wire` draws the box's whole
    plan with, and the same one `../texture-corner/` printed."""
    half = flute_width / 2.0
    stations = [half * (2.0 * i / (flute_samples - 1) - 1.0) for i in range(flute_samples)]
    depths = [scale * flute_depth * float(reeding.groove(t, pitch, flute_width))
              for t in stations]
    wire = cq.Workplane("XY", origin=(0.0, 0.0, z)).moveTo(x0, 0.0)
    for centre in flute_centres:
        wire = wire.lineTo(centre - half, 0.0)
        wire = wire.spline([(centre + t, -d) for t, d in zip(stations[1:], depths[1:])],
                           includeCurrent=True)
    wire = wire.lineTo(x1, 0.0).lineTo(x1, -wall).lineTo(x0, -wall)
    return wire.close().wire().val()


def _fade(sense, base):
    """The stations one fade is lofted through, bed or top arris — `flute_rise` of rise on
    `enclosure`'s own smoothstep, RULED between stations the way the box rules its."""
    marks = []
    for step in range(flute_fade_steps + 1):
        along = step / flute_fade_steps
        marks.append((base + sense * along * flute_rise, along * along * (3.0 - 2.0 * along)))
    return marks


def build_wall():
    """The plain fluted section — three bands on their own shared planes, one boolean."""
    bands = [
        cq.Solid.makeLoft([_reeded_wire(scale, z) for z, scale in _fade(+1.0, 0.0)], True),
        cq.Solid.extrudeLinear(
            cq.Face.makeFromWires(_reeded_wire(1.0, flute_rise)),
            cq.Vector(0.0, 0.0, height - 2.0 * flute_rise)),
        cq.Solid.makeLoft([_reeded_wire(scale, z) for z, scale in _fade(-1.0, height)], True),
    ]
    return bands[0].fuse(*bands[1:]).clean()


def build_foot():
    """A 45° ramp off the INSIDE face at the base — where it costs the show face nothing."""
    return (cq.Workplane("YZ", origin=(x0, 0.0, 0.0))
            .polyline([(-wall, 0.0), (-wall - foot, 0.0), (-wall, foot)])
            .close()
            .extrude(coupon_x)
            .val())


def build_slot_cutters():
    """One vertical prism per slot, drawn in XY and carried the band's height, its ceiling
    and its sill struck at `relief_chamfer` to a ridge on the groove's own centreline."""
    z_bottom, z_top = slot_z
    cutters = []
    for _index, centre, slot in slots():
        hip = slot / 2.0 * math.tan(math.radians(relief_chamfer))
        half = slot / 2.0
        section = [(centre, z_bottom),
                   (centre + half, z_bottom + hip),
                   (centre + half, z_top - hip),
                   (centre, z_top),
                   (centre - half, z_top - hip),
                   (centre - half, z_bottom + hip)]
        cutters.append(
            cq.Workplane(cq.Plane(origin=(0.0, 1.0, 0.0), xDir=(1, 0, 0), normal=(0, -1, 0)))
            .polyline(section).close().extrude(wall + 2.0).val())
    return cutters


def build_labels():
    """Each zone named on the inner face, STANDING PROUD of it. Read from inside the box,
    across runs left to right, so the glyphs go down unmirrored."""
    glyphs = []
    for index, (label, scheme, _slot, _every) in enumerate(ZONES):
        span = zone_span(index)
        centre = (span[0] + span[1]) / 2.0
        for text, size, z in ((label, label_size, label_z), (scheme, scheme_size, scheme_z)):
            plane = cq.Plane(origin=(centre, -wall + label_bite, z),
                             xDir=(1, 0, 0), normal=(0, -1, 0))
            glyphs.append(cq.Workplane(plane)
                          .text(text, size, label_proud + label_bite, combine=False,
                                font=label_font, kind=label_kind)
                          .val())
    return glyphs


def build_coupon():
    solid = build_wall().fuse(build_foot(), *build_labels()).clean()
    return solid.cut(*build_slot_cutters()).clean()


# --- what it came out as -----------------------------------------------------------


def _slab(solid, x_lo, x_hi, z):
    """The solid's own cross-section over an X band, 0.2 mm of height at `z`."""
    box = cq.Solid.makeBox(x_hi - x_lo, wall + 4.0, 0.2,
                           cq.Vector(x_lo, -wall - 2.0, z - 0.1))
    return solid.intersect(box)


def _thinnest(island):
    """The least section one mullion carries. The inner face is flat at −`wall` and the
    outer surface is everything the groove has taken out of it, so the thinnest station is
    the deepest point the island's own outer surface reaches — read off the tessellation,
    which carries the jamb's corner exactly."""
    vertices, _facets = island.tessellate(1e-4)
    return wall + min(v.y for v in vertices if v.y > -wall + 1e-6)


def measure(solid):
    """The realised field, read off the BUILT SOLID at mid-band — every island's across
    extent, every gap between two of them, and the least section a mullion carries.

    A zone's own span runs land centre to land centre over `zone_flutes` grooves, so what
    it holds is that zone's whole slots and the mullions strictly between them; the piers
    at the zone boundaries belong to the islands that bridge them and are counted in
    neither zone."""
    z = (slot_z[0] + slot_z[1]) / 2.0
    islands = sorted(_slab(solid, x0 - 1.0, x1 + 1.0, z).Solids(),
                     key=lambda s: s.BoundingBox().xmin)
    bounds = [(s.BoundingBox().xmin, s.BoundingBox().xmax) for s in islands]
    gaps = [(lo1 - hi0, (hi0 + lo1) / 2.0)
            for (_lo0, hi0), (lo1, _hi1) in zip(bounds, bounds[1:])]

    out = []
    for index, (label, scheme, slot, every) in enumerate(ZONES):
        lo, hi = zone_span(index)
        mine = [(w, at) for w, at in gaps if lo < at < hi]
        inside = [s for s in islands
                  if lo - 1e-6 <= s.BoundingBox().xmin and s.BoundingBox().xmax <= hi + 1e-6]
        walls = [(s.BoundingBox().xmin, s.BoundingBox().xmax) for s in inside]
        out.append({
            "label": label, "scheme": scheme, "slot": slot, "every": every,
            "span": hi - lo, "count": len(mine), "mullions": len(walls),
            "slot_min": min(w for w, _at in mine), "slot_max": max(w for w, _at in mine),
            "mullion_min": min(b - a for a, b in walls),
            "mullion_max": max(b - a for a, b in walls),
            "thinnest": min(_thinnest(s) for s in inside),
            "open_mm2_per_mm": sum(w for w, _at in mine),
            "open_fraction": sum(w for w, _at in mine) / (hi - lo),
        })
    return tuple(out)


# --- Export ------------------------------------------------------------------------


def main():
    out_dir = _here.parent
    solid = build_coupon()
    print(f"solid: {'valid' if solid.isValid() else 'NOT VALID'}, "
          f"{len(solid.Solids())} solid, vol {solid.Volume() / 1000.0:.1f} cm3")

    step = out_dir / "texture-coupon-vent.step"
    export_assembly(one_body(solid, step.stem, C_COUPON), str(step))
    print(f"-> {step.name}")

    stl = out_dir / "texture-coupon-vent.stl"
    cq.exporters.export(cq.Workplane(obj=solid), str(stl), exportType="STL",
                        tolerance=0.01, angularTolerance=0.1)
    mesh = trimesh.load(str(stl), process=True)
    print(f"-> {stl.name}  ({len(mesh.faces)} facets, "
          f"{'watertight' if mesh.is_watertight else 'NOT WATERTIGHT'}, "
          f"{mesh.extents[0]:.1f} × {mesh.extents[1]:.1f} × {mesh.extents[2]:.1f} mm)")

    zones = measure(solid)
    print(f"{'zone':>6} {'slots':>6} {'slot mm':>16} {'mullion mm':>16} "
          f"{'thinnest':>9} {'open mm2/mm':>12} {'open %':>7}")
    for z in zones:
        print(f"{z['label']:>6} {z['count']:>6} "
              f"{z['slot_min']:>7.4f}–{z['slot_max']:<8.4f} "
              f"{z['mullion_min']:>7.4f}–{z['mullion_max']:<8.4f} "
              f"{z['thinnest']:>9.4f} {z['open_mm2_per_mm']:>12.3f} "
              f"{100.0 * z['open_fraction']:>7.2f}")

    ceiling = reeding.pierce_max(reeding.pierce_shell, pitch)
    jamb = flute_depth * float(reeding.groove(ZONES[0][2] / 2.0, pitch, flute_width))
    figures = {
        "FLUTE_PITCH": f"{pitch:.4f} mm",
        "PLAN_PERIMETER": f"{plan_perimeter:.3f} mm",
        "FLUTE_COUNT": f"{flute_count:g}",
        "FLUTE_WIDTH": f"{flute_width:.4g} mm",
        "FLUTE_DEPTH": f"{flute_depth:.4g} mm",
        "LAND": f"{pitch - flute_width:.4f} mm",
        "FLANK_T": f"{wall:.4g} mm",
        "VENT_Z": f"{height:.4g} mm",
        "VENT_X": f"{coupon_x:.4g} mm",
        "FLUTE_TOTAL": f"{flute_total:g}",
        "ZONE_FLUTES": f"{zone_flutes:g}",
        "ZONE_SPAN": f"{zones[0]['span']:.3f} mm",
        "SLOT_Z0": f"{slot_z[0]:.4g} mm",
        "SLOT_Z1": f"{slot_z[1]:.4g} mm",
        "SLOT_BAND": f"{slot_z[1] - slot_z[0]:.4g} mm",
        "FOOT": f"{foot:.4g} mm",
        "FLUTE_RISE": f"{flute_rise:.4g} mm",
        "RELIEF_CHAMFER": f"{relief_chamfer:.4g}°",
        "PIERCE_SHELL": f"{reeding.pierce_shell:.4g} mm",
        "PIERCE_CEILING": f"{ceiling:.4f} mm",
        "GROOVE_FLOOR_SPARE": f"{box_wall - flute_depth - reeding.pierce_shell:.4g} mm",
        "JAMB_OFFSET": f"{ZONES[0][2] / 2.0:.4g} mm",
        "JAMB_DEPTH": f"{jamb:.4f} mm",
        "JAMB_SECTION": f"{wall - jamb:.4f} mm",
        "SLOT_A": f"{ZONES[0][2]:.4g} mm",
        "SLOT_B": f"{ZONES[1][2]:.4g} mm",
        "SLOT_C": f"{ZONES[2][2]:.4g} mm",
        "MULLION_A": f"{reeding.mullion(pitch, ZONES[0][2], 1):.4f} mm",
        "MULLION_B": f"{reeding.mullion(pitch, ZONES[1][2], 1):.4f} mm",
        "MULLION_C": f"{reeding.mullion(pitch, ZONES[2][2], 2):.4f} mm",
        "SPARE_A": f"{reeding.mullion(pitch, ZONES[0][2], 1) - reeding.pierce_shell:.4f} mm",
        "SPARE_B": f"{reeding.mullion(pitch, ZONES[1][2], 1) - reeding.pierce_shell:.4f} mm",
        "THIN_A": f"{zones[0]['thinnest']:.4f} mm",
        "THIN_B": f"{zones[1]['thinnest']:.4f} mm",
        "THIN_C": f"{zones[2]['thinnest']:.4f} mm",
        "MEAS_A": f"{zones[0]['slot_min']:.4f}–{zones[0]['slot_max']:.4f} mm",
        "MEAS_B": f"{zones[1]['slot_min']:.4f}–{zones[1]['slot_max']:.4f} mm",
        "MEAS_C": f"{zones[2]['slot_min']:.4f}–{zones[2]['slot_max']:.4f} mm",
        "MEAS_MULLION_A": f"{zones[0]['mullion_min']:.4f} mm",
        "MEAS_MULLION_B": f"{zones[1]['mullion_min']:.4f} mm",
        "MEAS_MULLION_C": f"{zones[2]['mullion_min']:.4f} mm",
        "OPEN_A": f"{zones[0]['open_mm2_per_mm']:.3f} mm²/mm",
        "OPEN_B": f"{zones[1]['open_mm2_per_mm']:.3f} mm²/mm",
        "OPEN_C": f"{zones[2]['open_mm2_per_mm']:.3f} mm²/mm",
        "OPEN_PCT_A": f"{100.0 * zones[0]['open_fraction']:.1f} %",
        "OPEN_PCT_B": f"{100.0 * zones[1]['open_fraction']:.1f} %",
        "OPEN_PCT_C": f"{100.0 * zones[2]['open_fraction']:.1f} %",
        "SLOTS_A": f"{zones[0]['count']:g}",
        "SLOTS_B": f"{zones[1]['count']:g}",
        "SLOTS_C": f"{zones[2]['count']:g}",
        "VOLUME": f"{solid.Volume() / 1000.0:.1f} cm³",
    }
    substitute_md(out_dir / "README.md", variables=figures)
    substitute_py_comments(_here, variables=figures)
    print("-> README.md")


if __name__ == "__main__":
    main()
