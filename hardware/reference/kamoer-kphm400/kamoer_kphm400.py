"""Reference mock: Kamoer KPHM400-SW3B25 peristaltic pump, sub-categorized.

A coarse keep-out approximation of the pump as it sits inside the case,
sectioned into functional sub-bodies (head, rotor housing, motor body).
Envelopes are catalog-nominal, not a manufacturing drawing — see
`off-the-shelf-parts/kamoer-kphm400/extracted-results/geometry-description.md`.

The model is authored in the PUMP-CASE WORLD FRAME so it drops straight into
the case assembly: origin at the base-plate bore-opening face, footprint
centered at (cx, cy), and the pump's depth axis along world +Z (head front at
-Z, motor at +Z). Width and height lie in X and Y.

The head and the rotor housing are conformed to the case interior, imported live
from `pump_case`, so they fit the cavity rather than poking through it:
- The head is the datasheet head block clipped to the skirt + lower-extension
  inner cavity, so it fills that cavity and stops at every wall.
- The rotor housing is shaped to the octagon bore (ledges and all), filling
  the octagon seat from the base plane up to the tower-bore start.

The motor is the part's own can, not the hole it turns in. The three bodies end
at `pump_len` off the head's front face — the length the part measures — and the
tower bore the motor sits inside is a bound stated against that, not the thing
that sizes it. A consumer reading this module's STEP gets the pump.

The pump's two outlet barbs sit on the body's +Y face (`body_y_face`) at the
arch-notch positions and reach out toward the case wall (`y_face`); this model
draws no tubing — `barb(i)` is each as a station in the pump's own frame, for
whatever seats the pump and attaches downstream (see `pump_assembly.py`).
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (_hw / "scripts", _hw / "printed-parts" / "cadlib", _hw / "printed-parts" / "flavor" / "pump-case"):
    sys.path.insert(0, str(_p))
from _cadq_export import export_assembly
import _stated_bounds as _bounds
import pump_case as pc


# --- Case-interior anchors (derived live from pump_case) --------------------
cx, cy = pc.center_x, pc.center_y                 # footprint center
base_plane_z = 0.0                               # base-plate bore-opening plane
octagon_top_z = pc.bore_bottom_z                 # octagon seat depth / tower-bore start
arch_plane_z = pc.skirt_bottom_z                 # skirt-bottom plane: outlet-port level
tower_top_z = (pc.bore_bottom_z + pc.tower_height
               - pc.tower_cap_thickness)         # tower bore far face — the motor's headroom
y_face = pc.pos_y_face_y                          # case +Y outer footprint face
# Outlet-port X positions on the +Y face (mirrors cut_arch_notches) — where the
# pump's two barbs cross the wall and fittings attach.
arch_xs = (pc.corner_r + pc.arch_radius - 4.0,
           pc.footprint_x - pc.corner_r - pc.arch_radius + 4.0)

# --- Datasheet-nominal dimensions (external spec; geometry-description.md) --
head_w = 62.61               # square pump-head body, width and height
head_depth = 48.88           # head body depth, front face to rear
motor_dia = 35.73            # silver DC motor body (clears the tower bore)
pump_len = 111.43            # front face to motor end cap, excluding the 5.05 shaft nub
body_y_face = cy + head_w / 2  # pump body +Y face — the plane outlet fittings seat on

# --- Axial seams (case frame; -Z = head front, +Z = motor rear) -------------
head_front_z = base_plane_z - head_depth         # head front (clipped to cavity)
motor_end_z = head_front_z + pump_len            # motor end cap — the part's own far face


# --- The two barbs, as stations ---------------------------------------------
# A peristaltic head has no fixed sense — the rotor turns whichever way the motor is wired —
# so which barb draws is the assignment of whatever seats the pump.

def barb(i: int) -> tuple:
    """One of the two outlet barbs: `(position, outward axis)` in the pump's own frame.

    It stands on the body's +Y face at its arch notch, at the skirt-bottom plane the notches
    are cut on, and reaches out toward the case wall — so the axis is +Y."""
    return ((arch_xs[i], body_y_face, arch_plane_z), (0.0, 1.0, 0.0))


def barbs() -> tuple:
    """Both, in `arch_xs` order — west to east across the head's own face."""
    return tuple(barb(i) for i in range(len(arch_xs)))


# --- What the three bodies claim about the part and its case ----------------
# The head and the boss are sized off `pump_case`; only the motor is sized off the
# part, taking whatever those two leave inside `pump_len`. So the span is right by
# construction and the thing that can drift is the case: seams that march past the
# part leave no can, and a tower that stops short leaves the motor nowhere to turn.
_bounds.state(
    "kamoer-boss-leaves-motor", "The case-derived seams leave the part a motor",
    f"a boss ending before the part's {motor_end_z:g} mm",
    octagon_top_z < motor_end_z,
    f"the octagon seat runs to {octagon_top_z:g} mm and the part's end cap is at "
    f"{motor_end_z:g}, so `pump_case`'s seams have marched past the pump and there is "
    f"no can left to draw.")
_bounds.state(
    "kamoer-motor-clears-tower", "The case's tower bore is deep enough for the motor",
    f"a bore reaching {motor_end_z:g} mm or past it",
    tower_top_z >= motor_end_z,
    f"the motor ends at {motor_end_z:g} mm and the tower bore stops at {tower_top_z:g}, "
    f"so the can bottoms out {motor_end_z - tower_top_z:g} mm before the pump is home.")


def _zcyl(r, z0, z1, ox=cx, oy=cy):
    return cq.Solid.makeCylinder(r, z1 - z0, cq.Vector(ox, oy, z0), cq.Vector(0, 0, 1))


def _zbox(w, d, z0, z1, ox=cx, oy=cy):
    return (cq.Workplane("XY")
            .box(w, d, z1 - z0, centered=(True, True, False))
            .translate((ox, oy, z0))
            .val())


def _case_cavity():
    """The case's skirt + lower-extension interior void, rebuilt from
    pump_case's inner profiles — the space the pump head occupies."""
    skirt = pc.loft_profile_stack(0, pc.skirt_z_steps, pc.skirt_inner_profiles)
    ramp_h = (pc.skirt_base_half_extent + pc.skirt_wide_flare_per_side
              - pc.skirt_narrow_half_extent)
    uniform = pc.lower_height - ramp_h - pc.lower_footprint_straight
    steps = [-pc.lower_footprint_straight, -ramp_h, -uniform]
    lower = pc.loft_profile_stack(pc.skirt_bottom_z, steps,
                                  pc._lower_profile_set(pc.skirt_wall))
    return skirt.union(lower)


def build_head():
    """Datasheet head block clipped to the case cavity: fills the skirt +
    lower-extension void and stops at every wall instead of poking through."""
    box = _zbox(head_w, head_w, head_front_z, base_plane_z)
    cavity = _case_cavity().val()
    return cq.Workplane(obj=box.intersect(cavity))


def build_rotor_housing():
    """The head's rear boss, shaped to the octagon bore (ledges included), so it
    fills the octagon seat from the base plane up to the tower-bore start."""
    boss = (pc.WorldWorkplane(pc.xy_plane_z_up)
            .workplane(offset=base_plane_z)
            .center(cx, cy)
            .polyline(pc.bore_profile).close()
            .extrude(octagon_top_z - base_plane_z))
    return cq.Workplane(obj=boss.val())


def build_motor_body():
    """Silver DC motor: a plain round cylinder from the boss's rear face to the
    part's own end cap. The tower bore is what it turns inside, not its length."""
    return cq.Workplane(obj=_zcyl(motor_dia / 2, octagon_top_z, motor_end_z))


# The pump's body sub-bodies as (name, builder, color). Public so the pump
# assembly (pump + fittings) can seat the same body without redrawing it.
BODY_PARTS = [
    ("head",          build_head,          cq.Color(0.16, 0.16, 0.18)),  # black plastic
    ("rotor_housing", build_rotor_housing, cq.Color(0.30, 0.30, 0.33)),  # dark plastic boss
    ("motor_body",    build_motor_body,    cq.Color(0.74, 0.76, 0.80)),  # silver
]


def build_assembly():
    a = cq.Assembly(name="kamoer-kphm400")
    for name, builder, color in BODY_PARTS:
        a.add(builder(), name=name, color=color)
    return a


def build_scene():
    parts = [builder().val() for _, builder, _ in BODY_PARTS]
    return cq.Compound.makeCompound(parts)


def main():
    export_assembly(build_assembly(), str(_here.parent / "kamoer-kphm400.step"))
    bb = build_scene().BoundingBox()
    print("-> kamoer-kphm400.step")
    print("pump envelope  X[%.1f, %.1f]  Y[%.1f, %.1f]  Z[%.1f, %.1f]   (Z = depth axis, motor +Z)"
          % (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax))
    # The solids are what a consumer imports, so the length is checked on them
    # rather than on the constants they were drawn from.
    print("depth %.2f against the part's %.2f%s"
          % (bb.zmax - bb.zmin, pump_len,
             "" if abs((bb.zmax - bb.zmin) - pump_len) < 1e-6 else "   <-- DOES NOT MATCH"))


if __name__ == "__main__":
    main()
