"""
The appliance the enclosure iso drawings show: THE MACHINE'S OWN WALLS.

`enclosure_assembly.build_enclosure_assembly()` places every body, seats what each wall
carries, and cuts the printed pieces of the box around them. This module takes
that one build and keeps what stands OUTSIDE the closed machine:

- the [4](PIECE_N) printed pieces — front/back × bottom/top — carrying the 45°
  display facet let into the top-front arris and the funnel throat cut through
  the top wall,
- the funnel standing in that throat and the display let into that facet,
- the length of each through-wall fitting that stands proud of the shell.

NOTHING HERE DRAWS A FEATURE OF ITS OWN. A port that moves in `enclosure_assembly`
moves in the drawing on the next run, a wall the pack hands no station is drawn
blank, and no number in the line art is a second machine's: the appliance is
[223 mm](APPLIANCE_W) wide, [487.8 mm](APPLIANCE_D) deep and [358 mm](APPLIANCE_H)
tall because that is what the box around the pack came out at.

Coordinates are the machine's own: +X across the width with x = 0 the axis the
pack is centred on, +Y front to back, +Z up off the floor slab.

substitute_py_comments rewrites the [value](NAME) links in this file's comments
on every run via refresh_comments(), which the drawing scripts call from their
main().
"""

import sys
from pathlib import Path

import cadquery as cq

_HERE = Path(__file__).resolve().parent
_HW = next(p for p in _HERE.parents if p.name == "hardware")
for _p in (next(p for p in _HERE.parents if (p / "tools" / "docgen").is_dir()) / "tools",
           _HW / "scripts",
           _HW / "manifold-layout",
           _HW / "printed-parts" / "enclosure" / "back-panel",
           _HW / "printed-parts" / "enclosure" / "port-ring"):
    sys.path.insert(0, str(_p))

from docgen import substitute_py_comments               # noqa: E402
import _boxes                                           # noqa: E402
import enclosure_assembly as _ea                                # noqa: E402
import _back_panel_dimensions as _rear                  # noqa: E402
import port_ring as _ring                               # noqa: E402


# ---------------------------------------------------------------------------
# The machine, once
# ---------------------------------------------------------------------------
#
# Built at import, and every figure below is read off this one assembly — so the
# two drawings that render it cannot show two machines, and neither can the
# quick-start sheet that embeds them.

_ASSY = _ea.build_enclosure_assembly()
_BOX = _ASSY.box
_SOLIDS = _ea._solids(_ASSY)

# The bounds the box came out at. A drawing that states its own is a drawing of
# a machine nobody builds.
OUTER = _BOX.outer
APPLIANCE_W = OUTER[1] - OUTER[0]
APPLIANCE_D = OUTER[3] - OUTER[2]
APPLIANCE_H = OUTER[5] - OUTER[4]

# The pieces the enclosure comes apart into, by the name they go into the
# assembly under. There is no panel among them — the front of this machine is
# `enclosure-front-*`'s own skin, and it is BLANK: `enclosure_assembly.pack()` fills
# `back_ports` with [6](BACK_PORT_N) stations and leaves `front_ports` at the
# `Pack` default, so the front wall is cut [0](FRONT_PORT_N) times and the
# drawing shows a face with nothing on it.
PIECES = tuple(n for n in _SOLIDS if n.startswith("enclosure-"))

# What a customer's line reaches. `enclosure_assembly.THROUGH_WALL` is the machine's own
# list of bodies clamped IN a wall rather than standing inside one, so the
# drawing carries exactly the fittings the machine presents to the room — the
# three umbilical unions in one row at [18.68 mm](PANEL_PITCH) pitch, the tap-water
# union on its own storey below them, the mains inlet, and the CO2 inlet under
# it. All of them on the back wall, because that is where the machine puts them.
FITTINGS = _ea.THROUGH_WALL

# Bodies seated in an OPENING rather than through a wall: the funnel standing in
# the top wall's throat, and the display let into the 45° facet. Each is drawn
# because a customer sees it — the funnel down the hopper, the screen on the
# facet — and neither is a feature this file draws.
SEATED = ("hopper-funnel", "display")


def _outer_solid() -> cq.Shape:
    """The box's stated bounds as a solid — what `proud` cuts a fitting by."""
    ox0, ox1, oy0, oy1, oz0, oz1 = OUTER
    return (cq.Workplane("XY").box(ox1 - ox0, oy1 - oy0, oz1 - oz0, centered=False)
            .translate((ox0, oy0, oz0)).val())


_OUTSIDE = _outer_solid()


def proud(name: str) -> cq.Shape:
    """The length of one through-wall fitting that stands OUTSIDE the shell.

    The rest of it is inboard of its own wall with the closed box around it, so
    it can never be seen and only makes the tessellation heavier. The cut is
    against the box's own bounds rather than a named wall, so a fitting reseated
    on another wall keeps its proud end and loses its buried one just the same.
    """
    return _SOLIDS[name][0].cut(_OUTSIDE)


def build_appliance() -> cq.Workplane:
    """The appliance as the drawings see it: the printed pieces, what is seated
    in their openings, and the proud end of every through-wall fitting.

    A COMPOUND, not a fusion — the pieces meet on their seams and the drawing
    shows those seams, which is what a machine that comes apart into four
    printed pieces looks like from outside."""
    parts = [_SOLIDS[n][0] for n in PIECES + SEATED]
    parts += [proud(n) for n in FITTINGS]
    return cq.Workplane().add(cq.Compound.makeCompound(parts))


# ---------------------------------------------------------------------------
# Printed port markings
# ---------------------------------------------------------------------------
#
# The [3](MARKED_N) rings the rear wall wears: printed markings on the wall,
# not geometry. The renderer projects each circle to a filled, self-outlined
# SVG path and clips it by the projected silhouette of the fitting standing in
# it, so the visible remainder reads as a ring around the port.
#
# Each is struck on the FITTING ITSELF — its proud footprint gives the centre
# and the radius, the wall it crosses gives the plane, and its proud end gives
# the `target` an arrow aims at. A marking cannot land on a different column
# from the port it marks, and a port that moves takes its ring with it.
#
# WHICH colour goes on which port is the rear face's, not the drawing's:
# `_back_panel_dimensions.port_colors` is the one table, and the quick-start
# sheet aims its arrows off the same one. White is a colour here like any
# other — on the page it reads as the black outline this path draws around it.

CO2_DISC_COLOR = list(_rear.port_colors["co2"])
WATER_DISC_COLOR = list(_rear.port_colors["water"])
CARB_DISC_COLOR = list(_rear.port_colors["carb"])

# How far a marking stands out past the fitting it rings — the printed ring left
# showing around the fitting's own body, read off that part so the drawing and
# the ring on the machine are one figure.
PORT_MARK_RING = _ring.RING_W

# The six outer faces, as (axis index, outward sign, index into `OUTER`).
_WALLS = ((0, -1.0, 0), (0, 1.0, 1),
          (1, -1.0, 2), (1, 1.0, 3),
          (2, -1.0, 4), (2, 1.0, 5))


def _standing_wall(lo, hi):
    """Which wall a proud body stands out of — the outer face its own box
    reaches furthest past. READ, not stated, so the marking follows the port."""
    def reach(w):
        ax, sign, i = w
        return hi[ax] - OUTER[i] if sign > 0 else OUTER[i] - lo[ax]

    return max(_WALLS, key=reach)


def _mark_face(ax, sign, i, centre) -> float:
    """The face a marking lies on: the RING'S OWN outboard face where that port wears one, and
    the wall's own outer face where it does not. A ring stands `port_ring.THICK` off the wall,
    so that is the plane the colour a customer sees lies in — read off the part, so a thicker
    ring carries its marking out with it."""
    field = _BOX.port_field
    if field is None or (ax, i) != (1, 3):
        return OUTER[i] + sign * 0.05
    ringed = any(abs(px - centre[0]) < 1e-6 and abs(pz - centre[2]) < 1e-6
                 for px, pz, _d in field.pockets)
    return OUTER[i] + sign * ((_ring.THICK if ringed else 0.0) + 0.05)


def port_marking(name: str) -> dict:
    """One port's marking, in the shape the renderer takes: the disc's centre on
    the face that port's ring beds in, its axis out of that wall, its radius one
    `PORT_MARK_RING` past the fitting's own footprint, and `target` — the hole
    out at the fitting's proud end, which is what an arrow points at rather than
    the ring painted around it."""
    b = _boxes.boxed(proud(name))
    lo, hi = (b.xmin, b.ymin, b.zmin), (b.xmax, b.ymax, b.zmax)
    ax, sign, i = _standing_wall(lo, hi)
    centre = [(lo[k] + hi[k]) / 2.0 for k in range(3)]
    target = list(centre)
    centre[ax] = _mark_face(ax, sign, i, centre)
    target[ax] = hi[ax] if sign > 0 else lo[ax]
    axis = [0.0, 0.0, 0.0]
    axis[ax] = sign
    across = max(hi[k] - lo[k] for k in range(3) if k != ax)
    return {"center": centre, "axis": axis,
            "radius": across / 2.0 + PORT_MARK_RING, "target": target}


# The ports that carry a marking, by the name the machine seats each under.
# The two flavor unions carry none: the customer pushes black into either black
# and the manifold sorts them, so a ring there would mark a choice nobody makes.
MARKED_PORTS = (("co2-disc", "co2-inlet", CO2_DISC_COLOR),
                ("water-disc", "bulkhead-water", WATER_DISC_COLOR),
                ("carb-disc", "bulkhead-carb", CARB_DISC_COLOR))

# The hopper throat carries no marking — it is an opening, not a port — so the
# drawing hands out an aim point instead, on the funnel centre the top wall is
# cut at. Its face is the TOP one, which is the wall the opening is in.
THROAT_ANCHOR = "hopper-throat"


# Iso camera directions (the camera sits along these from the scene centre).
_ISO_CAM_DIR = {
    "front": (1.0, -1.0, 1.0),
    "back": (1.0, 1.0, 1.0),
}


def _faces_camera(axis, view: str) -> bool:
    """Whether a feature on a wall of this outward normal is turned toward the
    camera — the one rule both markings and anchors are filtered by, so nothing
    is painted onto a face the view cannot see."""
    cam = _ISO_CAM_DIR[view]
    return sum(axis[k] * cam[k] for k in range(3)) > 0


def markings(view: str) -> list:
    """The port markings visible in `view`, each paired with the fitting that
    occludes its centre."""
    out = []
    for id_, name, color in MARKED_PORTS:
        disc = port_marking(name)
        if _faces_camera(disc["axis"], view):
            out.append({"id": id_, "disc": disc, "color": color,
                        "clip": cq.Workplane().add(proud(name))})
    return out


def anchors(view: str) -> list:
    """Invisible aim points, projected through the same camera, so a consumer of
    the SVG can point at a feature that carries no marking of its own.

    One so far: the hopper throat, at the funnel centre `enclosure._hopper_hole`
    cuts the opening on, on the top wall's outer face."""
    if not _faces_camera((0.0, 0.0, 1.0), view):
        return []
    fx, fy = _BOX.funnel
    return [{"id": THROAT_ANCHOR, "point": [fx, fy, OUTER[5]]}]


def refresh_comments() -> None:
    """Refresh the [value](NAME) markdown links in this file's comments."""
    pitch = ((max(_ea.PANEL_X.values()) - min(_ea.PANEL_X.values()))
             / (len(_ea.PANEL_X) - 1))
    substitute_py_comments(
        Path(__file__),
        variables={
            "APPLIANCE_W": f"{APPLIANCE_W:.4g} mm",
            "APPLIANCE_D": f"{APPLIANCE_D:.4g} mm",
            "APPLIANCE_H": f"{APPLIANCE_H:.4g} mm",
            "PIECE_N": f"{len(PIECES):d}",
            "FRONT_PORT_N": f"{len(_BOX.front_ports):d}",
            "BACK_PORT_N": f"{len(_BOX.back_ports):d}",
            "PANEL_PITCH": f"{pitch:.4g} mm",
            "MARKED_N": f"{len(MARKED_PORTS):d}",
        },
        expected_counts={
            "APPLIANCE_W": 1,
            "APPLIANCE_D": 1,
            "APPLIANCE_H": 1,
            "PIECE_N": 1,
            "FRONT_PORT_N": 1,
            "BACK_PORT_N": 1,
            "PANEL_PITCH": 1,
            "MARKED_N": 1,
        },
    )


if __name__ == "__main__":
    refresh_comments()
    print(f"-> updated comments in {Path(__file__).name}")
