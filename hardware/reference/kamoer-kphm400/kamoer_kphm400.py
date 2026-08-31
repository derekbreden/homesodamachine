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
whatever seats the pump and attaches downstream.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (_hw / "scripts", _hw / "printed-parts" / "cadlib", _hw / "printed-parts" / "enclosure" / "pump-tray"):
    sys.path.insert(0, str(_p))
from _cadq_export import export_assembly
from _materials import C_PUMP_BOSS, C_PUMP_HEAD, C_PUMP_MOTOR
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
# Outlet-port X positions on the +Y face — where the pump's two built-in tube casings cross the
# wall. The two 12.75 mm casings span 72.50 mm outside-to-outside, putting their axes 59.75 mm
# apart — approximately the measured 60 mm centre pitch. Their 13 mm holder shafts leave
# 0.125 mm per side and span 72.75 mm outside-to-outside.
tube_casing_w = 12.75
shaft_w = 13.0
outlet_span_x = 72.50
barb_pitch = outlet_span_x - tube_casing_w
outlet_open_span_x = barb_pitch + shaft_w
arch_xs = (cx - barb_pitch / 2.0, cx + barb_pitch / 2.0)
skirt_depth = 8.0
skirt_support_air = 0.15
# The skirt's measured Y span and +Y holder clearance. Its +Y face is 30.11 mm from the pump
# axis; the cartridge opens 0.30 mm beyond it and carries only 3 mm of upper band behind that.
skirt_y = 62.5
skirt_y_max = 30.11
skirt_y_plus_air = 0.30
skirt_upper_band = 3.0
# The lower head body between the two skirt overhangs, measured along Y in the pump frame.
# Its holder room is 54.3 mm: 54 mm of body plus 0.15 mm per face. Place that room so the
# case-profile land is 5 mm on Y- and the remaining rectangular land is 3.482 mm on Y+.
skirt_body_y = 54.0
skirt_support_xy_air = 0.15
skirt_support_y_minus = 5.0
skirt_support_y_plus = 3.482
skirt_body_y_max = (
    skirt_y_max + skirt_y_plus_air - skirt_support_y_plus - skirt_support_xy_air)
skirt_body_y_min = skirt_body_y_max - skirt_body_y

# --- Datasheet-nominal dimensions (external spec; geometry-description.md) --
head_w = 62.61               # square pump-head body, width and height
head_depth = 48.88           # head body depth, front face to rear
motor_dia = 35.73            # silver DC motor body (clears the tower bore)
pump_len = 111.43            # front face to motor end cap, excluding the 5.05 shaft nub
body_y_face = cy + head_w / 2  # pump body +Y face — the plane outlet fittings seat on
# THE MOUNTING BRACKET, STATED AND NOT DRAWN. A stamped steel plate at the junction face between
# head and boss — `geometry-description.md` §3 — carrying the 4×M3 on a 50 mm square that the
# part is meant to be screwed down by. It stands PROUD OF THE HEAD all the way round, and that
# lip is what a zip tie closing on this pump reaches under. The three solids below are a coarse
# keep-out and none of them is this plate, so a consumer that needs it takes these two figures.
bracket_w = 68.6             # across the plate, against the head's own 62.61
bracket_t = 2.0              # through it, the thick end of the 1.5–2 the part measures
bracket_z = base_plane_z     # the junction face it sits on — the head's rear, the boss's front
# THE OUTLET SIDE FALLS BACK UNDER ITS BARBS, STATED AND NOT MEASURED HERE. The datasheet
# gives one envelope and this module drew it as a block, because nothing had ever needed the
# face: `pump_case`'s own wall stood well clear of it. What needs it is a seat that reaches in
# BEHIND the head to hold it — under the barbs the part falls back this far off the face they
# stand on, and holds that fall from its front face up. The figure is confirmed on the part,
# and it is confirmed as barely: a consumer taking a hold in it takes the whole of it.
outlet_relief = 2.075        # how far the outlet side stands fore of `body_y_face`, under the barbs
outlet_relief_run = 12.585   # how far up off the head's own front face it holds that fall
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
# AND THE CASE'S NOTCHES STAND ON THE PART'S TUBE CASINGS. Both modules state the same
# 59.75 mm pitch and this row keeps the two sources coincident.
_case_notch_xs = pc.arch_hole_xs
_notch_off = max(abs(a - b) for a, b in zip(arch_xs, _case_notch_xs))
_bounds.state(
    "kamoer-notches-on-tube-casings",
    "The case's arch notches stand on the part's own tube casings",
    "the two stations on one plane",
    _notch_off <= 1e-9,
    f"the case cuts its notches at {_case_notch_xs} and the part's tube casings stand at "
    f"{arch_xs}, "
    f"{_notch_off:g} mm apart. Strike `cut_arch_notches` off `barb_pitch`.")


def _zcyl(r, z0, z1, ox=cx, oy=cy):
    return cq.Solid.makeCylinder(r, z1 - z0, cq.Vector(ox, oy, z0), cq.Vector(0, 0, 1))


def _zbox(w, d, z0, z1, ox=cx, oy=cy):
    return (cq.Workplane("XY")
            .box(w, d, z1 - z0, centered=(True, True, False))
            .translate((ox, oy, z0))
            .val())


def build_head():
    """Datasheet head block clipped to the case cavity: fills the skirt +
    lower-extension void and stops at every wall instead of poking through.

    WHAT THE CLIP LEAVES THE PART IS ITS SEAT. The upper skirt runs 8 mm below the bracket
    plane, then steps to the narrower body on one horizontal face. The outlet side falls back
    under its tube casings, which is the one thing here the case did not shape and the
    datasheet does not carry — see `outlet_relief`."""
    box = _zbox(head_w, head_w, head_front_z, base_plane_z)
    relief = (cq.Workplane("XY")
              .box(head_w + 2.0, outlet_relief + 2.0, outlet_relief_run,
                   centered=(True, False, False))
              .translate((cx, body_y_face - outlet_relief, head_front_z))
              .val())
    head = box.intersect(pc.stepped_skirt_cavity(
        0.0, -skirt_depth,
        (skirt_body_y_min, skirt_body_y_max),
        skirt_y_max).val()).cut(relief)
    return cq.Workplane(obj=head)


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
    ("head",          build_head,          C_PUMP_HEAD),   # black moulded head
    ("rotor_housing", build_rotor_housing, C_PUMP_BOSS),   # the white bracket under it
    ("motor_body",    build_motor_body,    C_PUMP_MOTOR),  # the bare steel can
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
