"""Reference mock: Kamoer KPHM400-SW3B25 peristaltic pump, sub-categorized.

A coarse keep-out approximation of the pump as it sits inside the case,
sectioned into functional sub-bodies (head, motor adapter, motor body, tubes).
Envelopes are catalog-nominal, not a manufacturing drawing — see
`off-the-shelf-parts/kamoer-kphm400/extracted-results/geometry-description.md`.

The model is authored in the PUMP-CASE WORLD FRAME so it drops straight into
the case assembly: origin at the base-plate bore-opening face, footprint
centered at (cx, cy), and the pump's depth axis along world +Z (head front at
-Z, motor at +Z). Width and height lie in X and Y.

The body parts are conformed to the case interior, imported live from
`pump_case`, so the pump fits the cavity rather than poking through it:
- The head is the datasheet head block clipped to the skirt + lower-extension
  inner cavity, so it fills that cavity and stops at every wall.
- The rotor housing is shaped to the octagon bore (ledges and all), filling
  the octagon seat from the base plane up to the tower-bore start.
- The motor body is a plain round cylinder filling the tower bore.
- The two tubes leave the +Y face along +Y through the case's arch notches,
  entirely external to the case.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (_hw / "scripts", _hw / "printed-parts" / "cadlib", _hw / "printed-parts" / "flavor" / "pump-case"):
    sys.path.insert(0, str(_p))
from _cadq_export import export_assembly
import pump_case as pc


# --- Case-interior anchors (derived live from pump_case) --------------------
cx, cy = pc.center_x, pc.center_y                 # footprint center
base_plane_z = 0.0                               # base-plate bore-opening plane
octagon_top_z = pc.bore_bottom_z                 # octagon seat depth / tower-bore start
arch_plane_z = pc.skirt_bottom_z                 # skirt-bottom plane: tube-exit level
tower_top_z = (pc.bore_bottom_z + pc.tower_height
               - pc.tower_cap_thickness)         # tower bore far face (motor end)
y_face = pc.pos_y_face_y                          # case +Y outer footprint face
# Tube passthrough X positions on the +Y face (mirrors cut_arch_notches).
arch_xs = (pc.corner_r + pc.arch_radius - 4.0,
           pc.footprint_x - pc.corner_r - pc.arch_radius + 4.0)

# --- Datasheet-nominal dimensions (external spec; geometry-description.md) --
head_w = 62.61               # square pump-head body, width and height
head_depth = 48.88           # head body depth, front face to rear
motor_dia = 35.73            # silver DC motor body (clears the tower bore)
tube_od = 8.0                # BPT tube / barb outer diameter
tube_len = 15.0              # total tube length, from the +Y face outward

# --- Axial seams (case frame; -Z = head front, +Z = motor rear) -------------
head_front_z = base_plane_z - head_depth         # head front (clipped to cavity)
tube_end_y = y_face + tube_len                    # tube far end


def _zcyl(r, z0, z1, ox=cx, oy=cy):
    return cq.Solid.makeCylinder(r, z1 - z0, cq.Vector(ox, oy, z0), cq.Vector(0, 0, 1))


def _ycyl(r, y0, y1, ox, oz):
    return cq.Solid.makeCylinder(r, y1 - y0, cq.Vector(ox, y0, oz), cq.Vector(0, 1, 0))


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
    """Silver DC motor: a plain round cylinder filling the tower bore."""
    return cq.Workplane(obj=_zcyl(motor_dia / 2, octagon_top_z, tower_top_z))


def _tube_solids():
    """The two +Y tubes (out through the arch notches) as individual solids."""
    return [_ycyl(tube_od / 2, y_face, tube_end_y, ox=bx, oz=arch_plane_z)
            for bx in arch_xs]


TUBE_COLOR = cq.Color(0.88, 0.88, 0.84)  # white plastic

_PARTS = [
    ("head",          build_head,          cq.Color(0.16, 0.16, 0.18)),  # black plastic
    ("rotor_housing", build_rotor_housing, cq.Color(0.30, 0.30, 0.33)),  # dark plastic boss
    ("motor_body",    build_motor_body,    cq.Color(0.74, 0.76, 0.80)),  # silver
]


def build_assembly():
    a = cq.Assembly(name="kamoer-kphm400")
    for name, builder, color in _PARTS:
        a.add(builder(), name=name, color=color)
    # Each tube goes in as its own solid (not one compound) so the STEP carries
    # the color per solid, where occt-import-js can read it back.
    for side, solid in zip(("pos", "neg"), _tube_solids()):
        a.add(solid, name=f"tube_{side}", color=TUBE_COLOR)
    return a


def build_scene():
    parts = [builder().val() for _, builder, _ in _PARTS]
    return cq.Compound.makeCompound(parts + _tube_solids())


def main():
    export_assembly(build_assembly(), str(_here.parent / "kamoer-kphm400.step"))
    bb = build_scene().BoundingBox()
    print("-> kamoer-kphm400.step")
    print("pump envelope  X[%.1f, %.1f]  Y[%.1f, %.1f]  Z[%.1f, %.1f]   (Z = depth axis, motor +Z)"
          % (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax))


if __name__ == "__main__":
    main()
