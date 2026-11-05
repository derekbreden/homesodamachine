"""The faucet, whole — every body above the counter, the countertop it clamps
through, and the four tubes running down past it into the umbilical.

`printed-parts/faucet/` holds the printed pieces individually and
`cut-parts/faucet/` the plate under the slab; this is the column they stack into,
with the harvested Westbrass they are built around
(`reference/touch-flo-faucet/westbrass-reference/`) and the display on the tip.

FRAME: the repo's +Z-up. +Z is height and the Westbrass's axis, +X is lateral,
-Y is the front — the gooseneck dispenses
toward -Y and the lever points toward -Y, so the water port and the flavor-tube
pill sit BEHIND the Westbrass's axis at +Y. Z = 0 is the above-counter plate's
top face; the countertop stands below the plate and above-counter gasket.

TWO WATER PORTS, and the tube in each is a different size. The blue 1/4" soda
umbilical tube lands on the compression port at the BOTTOM of the shank (Z = -50)
and water rises inside the shank; the 3/8"
soda faucet tube leaves the Westbrass's Ø10 top port and runs up the gooseneck,
sealed into that port by the printed TPU thimble. `assembly/faucet-and-umbilical.md` is the bench
that makes both up.

The column, top to bottom:

    display               Waveshare ESP32-S3-Touch-LCD-1.47, on the dispense tip
    shell                 three printed pieces, as printed — joint voids and all
    tubes                 3/8" soda faucet tube up the middle, two black 4 mm flavors behind it
    vent                  4 mm drain tube to the separate fault outlet
    lever                 canonical printed PET-GF lever in its nominal rest pose
    Westbrass             the harvested R2031-NL
    o-ring                printed TPU thimble in the Westbrass's top water port
    above-counter plate   printed oval with hidden base screws
    above-counter gasket  matching TPU oval
    countertop            30 mm slab
    under-counter plate   existing cut 316 SS plate
    soda umbilical tube   1/4" blue, on the shank's own compression port

AND BELOW THE PLATE, THE UMBILICAL — four tubes gathered into the pack a sleeve makes of
them, down to the end the installer pushes into the +Y wall of back-top:

    organizer        one PET-GF puck below the mounting workspace
    foam             CARGEN nitrile on the blue tube only, five segments butted
    sleeve           PET braid over the continuous tubes, cable and organizer
    tube collars     SODA on the blue, FLAVOR on each black, on the bare tails at the wall

Its run is drawn to `umbilical_drawn` rather than to the factory cut: the metre and a half between
the gather and the wall is one straight, and what a picture of it is worth is the end that has
features on it.

THE KERNEL CUTS THE FILES. `main` writes `numbers()` — every tube's centreline as `faucet_paths`
legs, the cable's sections, the display's boxes and seat, the umbilical's outlines, the colours,
and the parts and vendor bodies it stands in place — and `faucet_assembly.rs`, beside this
module, cuts `faucet-assembly.step` and the payload `/3d` draws from them. The CadQuery builders
here are for this module's readers: the install guide's art and the display snap trial.

Regenerate:
    tools/cad-venv/bin/python hardware/faucet-layout/faucet_assembly.py
"""

from __future__ import annotations

import functools
import json
import math
import sys
from pathlib import Path

_here = Path(__file__).resolve()
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware") / "scripts"),
)
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
if __name__ == "__main__":
    import _rust_part
    _rust_part.start()

import cadquery as cq
from _cadq_export import import_step
import _materials as _mat


_assembly_dir = Path(__file__).resolve().parent
_repo_hardware_dir = _assembly_dir.parent
_faucet_printed_dir = _repo_hardware_dir / "printed-parts" / "faucet"
_faucet_cut_dir = _repo_hardware_dir / "cut-parts" / "faucet"

ref_westbrass_step = (_repo_hardware_dir / "reference" / "touch-flo-faucet"
                 / "westbrass-reference" / "westbrass-reference.step")
under_counter_dxf = (_faucet_cut_dir / "under-counter-plate"
                     / "under-counter-plate.dxf")

sys.path.insert(0, str(_repo_hardware_dir / "printed-parts" / "cadlib"))
from world_workplane import WorldWorkplane, xy_plane_z_up

# Each printed part's build_*() returns +Z-up.
sys.path.insert(0, str(_faucet_printed_dir))  # for _faucet_interface
sys.path.insert(0, str(_faucet_printed_dir / "above-counter-plate"))
sys.path.insert(0, str(_faucet_printed_dir / "above-counter-gasket"))
sys.path.insert(0, str(_faucet_printed_dir / "tpu-o-ring"))
sys.path.insert(0, str(_faucet_printed_dir / "faucet-shell"))
sys.path.insert(0, str(_faucet_printed_dir / "faucet-display-cover"))
# The identification the tubes carry below the counter, and the filaments it prints in — one part
# and one colour table, shared with the chips on the +Y wall of back-top.
sys.path.insert(0, str(_faucet_printed_dir / "tube-collar"))
sys.path.insert(0, str(_faucet_printed_dir / "umbilical-organizer"))
sys.path.insert(0, str(_repo_hardware_dir / "printed-parts" / "enclosure" / "y-wall-of-back-top"))
import tube_collar
import umbilical_organizer
import _y_wall_dimensions as _rear
import above_counter_plate
import above_counter_gasket
import tpu_o_ring
import faucet_shell
import _faucet_interface as _fi
import faucet_display_cover
from _faucet_interface import (
    display_housing_width,
    display_housing_length,
    display_pcb_width,
    display_pcb_length,
    display_corner_r,
    display_pcb_corner_r,
    display_total_depth,
    display_pcb_bottom_z,
    display_pcb_top_z,
)


# Reference Westbrass geometry, shared with
# `../westbrass-reference/westbrass_reference.py`. The Westbrass's
# water port sits at depth Y = +port_center_depth (BEHIND its own axis,
# toward the back); +Z is the Westbrass's vertical axis.
from _rust_data import request as _data_request
import fits
from _cadq_export import note_read as _note_scalar_read


def _assembly_data(fn="datums", **values):
    root = _repo_hardware_dir.parent
    for name in (
        "hardware/reference/touch-flo-faucet/display-reference/component-envelopes.json",
        "hardware/reference/touch-flo-faucet/display-reference/buttons.json",
        "hardware/printed-parts/faucet/lever-replica/lever-replica.frame.json",
        "hardware/cut-parts/faucet/under-counter-plate/under-counter-plate.dxf",
    ):
        _note_scalar_read(root / name)
    if fn == "numbers":
        values["colors"] = {name: list(_mat.linear(color)) for name, color in body_colors.items()}
        values["collar_palette"] = {name: [_rear.chip_color(row.fluid), _rear.word_color(row.fluid)]
                                    for name, row in tube_collar.STATIONS.items()}
    return _data_request("faucet-data", "faucet-data", {
        "op": "assembly", "fn": fn, "root": str(root), "slip": fits.slip,
        "collar": tube_collar._collar_values["datums"], **values,
    })


globals().update(_assembly_data())


# Soda faucet tube — ⌀ (3/8" LLDPE) — seated in the
# Westbrass's 10.0 mm water port and running up through the gooseneck. The
# 0.475 mm diametric (0.2375 mm radial) gap is sealed by a printed TPU
# bushing on the real tube (not modeled).
# — 3/8" LLDPE in millimeters.


# Black 4 mm flavor tubes pass behind the Westbrass, on either side of D.
# The lower row shares the purchased plate's rear channel with D and ribbon;
# the shared paths return it to the centered neck and symmetric drink face.
# The upper organizer follows the mounting row; gather returns begin below it.
# — black LLDPE in millimeters.


# — tangent to the Westbrass's +Y (back) face.


# THE COUNTER THE STACK CLAMPS THROUGH. The slab is not a part — it is the customer's kitchen — but
# it is what sets where the cut plate lands and so where the umbilical hangs from, and the assembly
# carries it at the figure `assembly/faucet-and-umbilical.md` sums its tube lengths on: 30 mm of 3 cm
# stone. The 19–38 mm routing envelope reserves straight tube/cable clearance;
# it does not establish the retained donor clamp's maximum deck thickness.


# The plate's underside: the first plane below the counter a tube is free to bend on.

# Factory bends begin below the steel at the thickest routing-envelope slab.


# Below the plate the four tubes gather under one sleeve
# (`faucet-and-umbilical.md` §3). The flavor pair holds its lower X spacing
# and touches the foam on the blue tube. D touches its opposite side.
#
# CARGEN nitrile foam, 1/4" ID × 3/8" wall, on the blue tube only — the cold run. Its OD is what the
# pack is built around and what does not pass the countertop hole, which is why the blue tube is
# entirely below the counter.


# Where each flavour tube's axis stands in depth once it is tangent to that foam, at the X it
# already has. Same Pythagorean tangency `flavor_tube_depth_upper` is struck on, one circle out.
# — tangent to the foam on the blue tube.


# The dedicated white vent line passes between the flavor pair. Below the counter it
# steps forward below the organizer, then gathers against the cold-line foam.


# Continuous black flavor runs pass the organizer, then gather against the
# insulated soda line in tangent R30 arcs. Both finishes use these same runs.


def return_x(x_sign):
    return _assembly_data('return_x', args=[x_sign])


def flavor_mount_x(x_sign):
    return _assembly_data('flavor_mount_x', args=[x_sign])


def step_theta(x_sign):
    return _assembly_data('step_theta', args=[x_sign])


def organizer_flavor_xy(x_sign):
    return _assembly_data('organizer_flavor_xy', args=[x_sign])


# The organizer stands on the parallel bare tubes below the mounting workspace.
# Z=0 remains the above-counter plate's top face. One puck ships per umbilical.


# Both mounting returns finish above the gather into the insulated pack.


def gather_offset(x_sign):
    return _assembly_data('gather_offset', args=[x_sign])


def gather_theta(x_sign):
    return _assembly_data('gather_theta', args=[x_sign])


def gather_rise(x_sign):
    return _assembly_data('gather_rise', args=[x_sign])


# THE PACK STARTS where the longer gather lands, and the foam and the braid's run over the pack start
# with it.


# THE FACTORY CUT, off `faucet-and-umbilical.md` §1 — what the bench cuts, installer-trim allowance
# included. The blue is measured from the shank's bottom face and the flavour pair from the printed
# tip. `main` prints where the two land against each other; what the assembly DRAWS is below.


# WHAT IS DRAWN IS THE TERMINATED END. Between the pack and the wall the umbilical is one straight run
# of more than a metre, and a picture of that is a line with a faucet on it. So the drawing carries
# the length that has features on it — the organizer, the sleeve, the plane it stops on, and the four
# tails and their collars below that — measured down from the Westbrass's compression port, the way
# the countertop below is drawn 120 mm square rather than to a kitchen.


# Carbonated water arrives at the OTHER port: the compression fitting on the
# bottom of the shank, below the countertop's top
# face, and rises inside the shank to it. So the blue tube is 1/4" and is
# entirely below the counter, where the 3/8" soda faucet tube above is not. The
# harvested Westbrass models no shank bore and no fitting, so this butts on the
# shank's own bottom face.


# All four tails share the termination plane.
# — the square-cut end, as drawn.


# The foam's own run on that tube (`faucet-and-umbilical.md` §3): five 1-ft segments butted from the
# pack's first plane, bare above it past the mounting returns to the compression end, and bare again at the
# wall. `foam_length` is what the five come to; what is drawn is the run's two ends.

# of bare blue tube below the compression port.


# — tight upstream pack depth.


# Lower centerlines use the shared smooth transition in faucet_paths.py.
# These dimensional references remain available to the assembly/document readers.


# — per-bend angle absorbing the S-bend depth offset.


# — S-bend starts here.


# Above the lever the shared gooseneck bends toward −Y. Soda follows its
# circular centerline; the flavor and drain paths retain their own spacing
# through the seal spread. D ends at the wet chamber. The flavor pair returns
# to its display-face spacing before the final straight.
# The tip's exit angle below horizontal = (bend1_sweep + bend2_sweep) - 90°.


# — bend-1 midpoint, 35 mm above lever_top_z.

# — bend-1 start.


# Flavor tubes sit further +Y than the soda faucet tube (deeper, behind it).
# The gooseneck bends toward -Y, so the flavor tubes are on the OUTSIDE
# of every bend: they trace parallel-offset arcs sharing each bend's
# center of curvature with water, at the larger radius water_r +
# offset_depth. At the bare gooseneck radius the perpendicular component
# of the centerline separation shrinks below water_r + flavor_r and the
# tubes ride into each other through the bend.

# — parallel offset of gn_bend1_r.

# — parallel offset of gn_bend2_r.


def load_westbrass():
    """The harvested Westbrass, authored Z-up in the repo frame."""
    return import_step(str(ref_westbrass_step))


def load_above_counter_plate():
    """The printed above-counter plate, +Z-up."""
    return above_counter_plate.build_above_counter_plate()


def load_above_counter_gasket():
    """The printed-TPU above-counter gasket, +Z-up."""
    return above_counter_gasket.build_above_counter_gasket()


def load_display_cover():
    """Nominal seated cover surface, with its relaxed print supplied separately."""
    return faucet_display_cover.build_seated_display_cover()


def load_shell_pieces():
    """The two faucet-shell pieces, +Z-up, in assembled position —
    as printed, joint void and all."""
    full = faucet_shell.build_shell()
    return (
        faucet_shell.build_shell_base(full),
        faucet_shell.build_shell_tip(full),
    )


def _arc_from_tangent(start, tangent, radius, theta_rad, ccw):
    return _assembly_data('_arc_from_tangent', args=[start, tangent, radius, theta_rad, ccw])


def _gooseneck_segments(start, tangent, bend1_r, bend2_r):
    return _assembly_data('_gooseneck_segments', args=[start, tangent, bend1_r, bend2_r])


_paths = faucet_shell._paths


def _legs_json(legs):
    """`faucet_paths` legs as the kernel's paths read them: `{"line": [a, b]}`,
    `{"arc": [a, mid, b]}`, `{"spline": points}` and `{"hermite": [a, b, ta, tb]}`."""
    return [{kind: [[float(c) for c in p] for p in (rest[0] if kind == "spline" else rest)]}
            for kind, *rest in legs]


def _scalar_dimensions(paths=None, hulls=None):
    return _assembly_data("_scalar_dimensions", paths=paths, hulls=hulls)


def _legs_wire(legs):
    """`faucet_paths` legs as one CadQuery wire."""
    return cq.Wire.assembleEdges([_paths.leg_edge(leg) for leg in legs])


def _soda_faucet_legs():
    return _assembly_data('_soda_faucet_legs', args=[])


def _soda_faucet_path():
    return cq.Workplane(obj=_legs_wire(_soda_faucet_legs()))


def build_soda_faucet_tube():
    """Ø soda_faucet_tube_od tube along `_soda_faucet_path`."""
    # Circular cross-section perpendicular to the path's starting +Z tangent.
    profile = (cq.Workplane("XY", origin=(0, port_center_depth, soda_faucet_tube_z_bottom))
               .circle(soda_faucet_tube_r))
    return profile.sweep(_soda_faucet_path(), transition="round")


def _length(path):
    return path.wire().val().Length()


def _faucet_flavor_path(x_sign=1):
    """Shared production centreline: lower row, centered neck and symmetric face."""
    return cq.Workplane(obj=_paths.path_wire("flavor",under_counter_plate_bottom_z,x_sign))


def _step_legs(x_sign, bottom_z):
    return _assembly_data('_step_legs', args=[x_sign, bottom_z])


def _step_path(x_sign, bottom_z):
    """Mounting row to organizer, then R30 return below it to the gather.

    Each return lies in its own vertical plane. Coordinates are relative
    to the flavor's mounting axis and the plate underside.
    """
    return cq.Workplane(obj=_legs_wire(_step_legs(x_sign, bottom_z)))


def _gather_legs(x_sign, top_z):
    return _assembly_data('_gather_legs', args=[x_sign, top_z])


def _gather_path(x_sign, top_z):
    return cq.Workplane(obj=_legs_wire(_gather_legs(x_sign, top_z)))


def flavor_centerlines(x_sign):
    """Every piece of one flavor tube's centreline, tip to tail, as the paths its sweeps run: the
    faucet's run, the step to its return axis, the gather into the pack, the splay at the
    wall."""
    return (_faucet_flavor_path(x_sign), _step_path(x_sign, gather_start_z),
            _gather_path(x_sign, gather_start_z), _splay_path(x_sign))


def flavor_path_above_pack(x_sign):
    return _assembly_data('flavor_path_above_pack', args=[x_sign])


def flavor_path_above_foot():
    return _assembly_data('flavor_path_above_foot', args=[])


# The lane the SIG-6 ribbon rides in, between the tube pack and the braid's inner face. The braid
# stands off every tube in the pack by it.
#
# Four 28 AWG silicone conductors lie side by side. The received ribbon's
# measured 4.6 × 1.18 mm section is recorded beside its reference hardware.


def build_display_ribbon():
    """The SIG-6 cable's measured flat envelope through the faucet.

    The lower handoff passes through the mounting stack; the upper end reaches the
    factory fan-out beside the PCB, 0.30 mm below its measured underside.
    """
    parts = [
        build_lower_display_ribbon().val(),
        faucet_shell.build_signal_transition_ribbon().val(),
        faucet_shell.build_display_ribbon_transition().val(),
    ]
    joined=parts[0].fuse(*parts[1:],tol=1e-5)
    if not joined.isValid() or len(joined.Solids())!=1:
        raise ValueError("the complete flat ribbon must form one continuous envelope")
    return cq.Workplane(obj=joined)


def _ribbon_return_legs():
    return _assembly_data('_ribbon_return_legs', args=[])


def build_lower_display_ribbon():
    """Mounted ribbon follows the rear of D into the loose organizer bore.

    The free return starts below the maximum routing slab. Its continuation
    ends below the puck; the harness carries on under the braid.
    """
    plate_z = under_counter_plate_bottom_z
    mounted = faucet_shell.build_lower_signal_ribbon().val().intersect(
        cq.Solid.makeBox(200.0,200.0,400.0,cq.Vector(-100.0,-100.0,plate_z)))
    start_xy = (faucet_shell.signal_lower_exit_x,faucet_shell.signal_lower_exit_y)
    path = cq.Workplane(obj=_legs_wire(_ribbon_return_legs()))
    stub = (cq.Workplane("XY",origin=(*start_xy,plate_z)).rect(cable_width,cable_lane)
            .sweep(path,transition="round").val())
    joined = mounted.fuse(stub,tol=1e-5).clean()
    if not joined.isValid() or len(joined.Solids()) != 1:
        raise ValueError("the mounted ribbon and external return must form one valid solid")
    return cq.Workplane(obj=joined)


def build_vent_seal(upstream=True):
    import vent_seals
    p=faucet_shell._paths
    station=p.UPSTREAM_GLAND_S if upstream else p.DOWNSTREAM_GLAND_S
    return faucet_shell._gland_world(vent_seals.build_installed_bung(upstream),station)


def _hull(circles) -> cq.Sketch:
    """The convex hull round `circles`, `(x, y, radius)` each, as a sketch."""
    sketch = cq.Sketch()
    for x, y, radius in circles:
        sketch = sketch.arc((x, y), radius, 0.0, 360.0)
    return sketch.hull()


def _bundle_circles(grow: float = 0.0):
    return _assembly_data('_bundle_circles', args=[grow])


def bundle_hull(grow: float = 0.0) -> cq.Sketch:
    """The pack's outline, standing `grow` off every tube in it.

    A braid lies on the tubes it is drawn over and bridges tangent between them: its inner face is
    this outline at `cable_lane` and its outer the same at `cable_lane` plus `sleeve_wall`.

    Growing every circle by `grow` offsets the hull by it — the boundary is arcs and the tangents
    between them, and a common growth carries each arc out and leaves each tangent where it lies."""
    return _hull(_bundle_circles(grow))


def _gather_circles(grow: float = 0.0):
    return _assembly_data('_gather_circles', args=[grow])


def gather_hull(grow: float = 0.0) -> cq.Sketch:
    """Clearance envelope below the mounting returns, over the tube gathers and foam start."""
    return _hull(_gather_circles(grow))


@functools.lru_cache(maxsize=None)
def _hull_face(grow: float):
    """`bundle_hull(grow)` as one planar face, read off the floor of a prism raised on it."""
    return (cq.Workplane(xy_plane_z_up).placeSketch(bundle_hull(grow))
            .extrude(1.0).faces("<Z").val())


def bundle_girth(grow: float = None) -> float:
    return _assembly_data('bundle_girth', args=[grow])


def bundle_bore() -> float:
    return _assembly_data('bundle_bore', args=[])


def _bare_bundle_circles(grow=0.0):
    return _assembly_data('_bare_bundle_circles', args=[grow])


def bare_bundle_hull(grow: float = 0.0) -> cq.Sketch:
    """Bare blue, flavor and drain tube envelope above the foam."""
    return _hull(_bare_bundle_circles(grow))


def bare_bundle_girth() -> float:
    return _assembly_data('bare_bundle_girth', args=[])


# behind the Westbrass's axis — the pack's own centre of area, which is what
# a collar's flag is turned away from. Ø is what the braid opens to over it
# — a 1" nominal PET braid that expands 50% (`ledger/bom.md` §11; the wall above is the figure the
# assembly draws it at).
# THE BRAID'S RUN IS THE FOAM'S, AND THE TOP ONE COVERS THE MOUNTING RETURNS. One braid segment goes over
# each foam segment as that segment seats (`faucet-and-umbilical.md` §3), so the two stop on one
# plane at the wall and the installer's trim takes one of each; the top segment runs on above its
# foam over the bare runs, to the plane the upper one starts on. What that leaves bare at the wall is
# `foam_bare_at_wall`, where the installer flexes the three apart and pushes each into its own union.


# THE TAILS COME APART BEFORE THE COLLARS GO ON. The +Y wall of back-top does not take this
# triangle — the installer flexes the three apart in the un-sleeved stretch and pushes each into its
# own union (`faucet-and-umbilical.md` §3) — and the collars need the same room: two of them clear
# when their tubes' axes stand further apart than the two reach. The flavour pair splays in X until
# the TIGHTEST of the three pairs makes that, which is a flavour tube against the blue standing
# forward of them, not the two flavours against each other.


# — each flavour tail's own X, off the Westbrass's axis.

# The splay, as the gather and the S-bend are: two arcs of one radius sharing an angle.

# — per-arc angle absorbing the lateral the pair comes out by.

# What it spends of the un-sleeved stretch getting there.


# Where the sleeve lets go and the splay takes over — one plane, so nothing runs bare and straight
# between them.

# WHERE THE THREE COLLARS HANG, level with each other, on the first plane below the splay — a bore
# is straight and a tube coming out of a bend is not, so no collar stands in one.


def _splay_legs(x_sign):
    return _assembly_data('_splay_legs', args=[x_sign])


def _splay_path(x_sign):
    return cq.Workplane(obj=_legs_wire(_splay_legs(x_sign)))


# Every bend spends more tube than its vertical drop. The factory cut
# includes this splay and the complete route above the pack.


# The soda tube bottoms on the thimble's cap and is trimmed flush at the printed tip.


# One complete tip-to-tail cut for each black flavor tube, using the longer path.


def tail_z(x_sign):
    return _assembly_data('tail_z', args=[x_sign])


# — how far apart the three tails land: the flavor cut's rounding to a
# whole millimetre, and flavor-a's shorter route against the one cut both take.


def _flavor_tube(path, start_z=0.0):
    """A 4 mm tube swept along `path`. A SWEEP CARRIES ITS PROFILE FROM WHERE THE PROFILE STANDS and
    not from the spine's first point, so the profile stands at the spine's start, `start_z` up the
    path's own Z."""
    return (cq.Workplane(xy_plane_z_up).workplane(offset=start_z).circle(flavor_tube_r)
            .sweep(path, transition="round"))


def build_flavor_faucet_run(x_sign):
    """One continuous black flavor run, dispense tip to gather start."""
    at_plate = (flavor_mount_x(x_sign),flavor_tube_depth_lower,under_counter_plate_bottom_z)
    path=_faucet_flavor_path(x_sign)
    plane=cq.Plane(origin=at_plate,xDir=(1,0,0),normal=(0,0,1))
    faucet=cq.Workplane(plane).circle(flavor_tube_r).sweep(path,transition="round")
    step=_flavor_tube(_step_path(x_sign,gather_start_z)).translate(at_plate)
    return faucet.union(step)


def build_flavor_umbilical_run(x_sign):
    """Continuous black flavor tube from gather start to its square-cut tail."""
    stop_z = gather_start_z
    gather = (_flavor_tube(_gather_path(x_sign, stop_z), stop_z - gather_start_z)
              .translate((return_x(x_sign), flavor_tube_depth_lower, gather_start_z)))
    tail = (_flavor_tube(_splay_path(x_sign))
            .translate((x_sign * flavor_tube_x_offset, pack_flavor_depth, splay_top_z)))
    return gather.union(tail)


def build_flavor_tube(x_sign):
    """One continuous black Ø4 mm flavor tube from dispense tip to tail."""
    return (build_flavor_faucet_run(x_sign)
            .union(build_flavor_umbilical_run(x_sign)))


def _drain_lower_legs():
    return _assembly_data('_drain_lower_legs', args=[])


def drain_legs():
    return _assembly_data('drain_legs', args=[])


def drain_path():
    return _legs_wire(drain_legs())


@functools.lru_cache(maxsize=None)
def drain_factory_cut_length():
    return _assembly_data('drain_factory_cut_length', args=[])


def build_drain_tube(envelope=False):
    """4 mm OD / 2.5 mm ID white LLDPE, tail to the separate underside outlet."""
    profile = (cq.Workplane("XY").workplane(offset=umbilical_tail_z)
               .center(drain_tail_x, drain_tail_y).circle(drain_tube_r))
    if not envelope:
        profile = profile.circle(_fi.drain_tube_id / 2)
    return profile.sweep(cq.Workplane(obj=drain_path()), transition="round")


# Nominal clearance-animation axis, parallel to world X. This is not a measured
# pin hinge: the donor lever seats down and forward around the valve cylinder,
# and the installed soda tube blocks its aft disengagement. The assembled
# contact motion is not yet measured; see faucet-shell/ASSEMBLY.md.


_lever_step = _faucet_printed_dir / "lever-replica" / "lever-replica.step"


def _lever_rest_offset(lever):
    """How far the printed lever, as its STEP holds it, moves to the rest pose: its top to
    `lever_top_z` and its aft extent to `lever_aft_y`."""
    bounds = lever.val().BoundingBox()
    return (0.0, lever_aft_y - bounds.ymax, lever_top_z - bounds.zmax)


def _lever_frame_offset():
    return _assembly_data('_lever_frame_offset', args=[])


def build_lever_at(angle_deg=0.0):
    """Canonical printed lever, rigidly placed at the nominal assembly datum.

    The part's top and aft extent sit at Z=52 and Y=9 mm in the rest pose.
    Installed contact motion is not measured.
    """
    sys.path.insert(0, str(_faucet_printed_dir / "lever-replica"))
    from lever_replica import build as build_native_lever

    lever = (import_step(_lever_step) if getattr(cq, "MESH", False)
             else build_native_lever())
    placed = lever.translate(_lever_frame_offset())
    return placed.rotate((0, lever_pivot_y, lever_pivot_z),
                         (1, lever_pivot_y, lever_pivot_z), angle_deg)


def build_lever():
    """The printed lever in its nominal rest position."""
    return build_lever_at(0.0)


# The M3 socket-head screw: its thread drawn as a plain shaft, its 2.5 mm hex socket from just
# below the head's underside.


def build_base_screw(x, y):
    """M3 socket-head screw in its installed position; thread is a cylinder."""
    f = faucet_shell
    seat = f.base_screw_seat_z
    shaft = (cq.Workplane("XY").workplane(offset=seat).center(x, y)
             .circle(base_screw_shaft_r).extrude(f.base_screw_length))
    head_bottom = seat - f.base_screw_head_height
    head = (cq.Workplane("XY").workplane(offset=head_bottom).center(x, y)
            .circle(base_screw_head_r).extrude(f.base_screw_head_height))
    socket = (cq.Workplane("XY").workplane(offset=head_bottom - base_screw_socket_below).center(x, y)
              .polygon(6, base_screw_socket_af / math.cos(math.pi / 6))
              .extrude(base_screw_socket_depth))
    return shaft.union(head).cut(socket)


def build_base_insert(x, y):
    """Actual insert outside diameter after heat setting; knurl omitted."""
    f = faucet_shell
    return (cq.Workplane("XY").workplane(offset=f.base_insert_bottom_z)
            .center(x, y).circle(f.base_insert_outer_dia / 2).circle(base_insert_inner_r)
            .extrude(f.base_insert_length))


# Faucet display — Waveshare ESP32-S3-Touch-LCD-1.47 (BOM §1),
# modeled as a dimensioned stand-in. Device dims live in
# _faucet_interface, shared with the shell's display cradle (table in
# display-reference/README.md). Component envelopes below the PCB come
# from the vendor model, with their heights corrected to the measured
# PCB underside. The metal feet retain their measured zero datum.
#
# Native frame: X = width, Y = length, Z = outward thickness; the feet
# plane at z = 0, screen faces +Z. The long axis follows the tip and
# the screen faces the user. Four printed pads carry the feet; the
# component spaces remain open to the tube passages. The bezel's
# lower enclosure rim lies in the dispense plane.

# Active (lit) display area, on the front face.


_display_component_path = (Path(__file__).resolve().parents[1]
                           / "reference/touch-flo-faucet/display-reference/component-envelopes.json")

_display_button_path = _display_component_path.parent / "buttons.json"

if abs(_display_components["measured_pcb_underside_above_feet_mm"] - display_pcb_bottom_z) > 1e-6:
    raise ValueError("display component envelopes need the current measured PCB height")


def build_display_buttons_native():
    """Vendor switch housings and actuators, corrected to the measured PCB height."""
    return cq.Workplane(obj=cq.Compound.makeCompound([
        cq.importers.importStep(str(_display_button_path.parent / row["file"])).val()
        for row in _display_buttons["buttons"]
    ]))


def _display_component_envelopes():
    return _assembly_data('_display_component_envelopes', args=[])


def build_display_components_native():
    """Underside envelopes with the two complete vendor switch shapes."""
    bodies = []
    for kind, at, *size in _display_component_envelopes():
        if kind == "cylinder":
            radius, height = size
            bodies.append(cq.Solid.makeCylinder(radius, height, cq.Vector(*at)))
        else:
            high, = size
            bodies.append(cq.Solid.makeBox(*(h - l for h, l in zip(high, at)), cq.Vector(*at)))
    bodies.extend(build_display_buttons_native().val().Solids())
    return cq.Workplane(obj=cq.Compound.makeCompound(bodies))


def _tip_centerline_world():
    return tuple(cq.Vector(*point) for point in _assembly_data("_tip_centerline_world"))


def _display_seat():
    return _assembly_data('_display_seat', args=[])


def _seat_on_tip(part):
    """Place a display part (native frame: X width, Y length, Z outward
    with the feet plane at z = 0) onto the dispense tip. The tip straight
    runs (gn_bend1_sweep + gn_bend2_sweep − 90°) below horizontal;
    rotating that angle about world X lays the part's length up the
    gooseneck and turns its screen (+Z) up toward the user. It is then
    offset out along the tip's top normal to the four feet pads. The
    feet datum and display center come from the shell's shared display
    constants, which leave 2 mm stock behind the dispense plane.
    """
    turn, seat = _display_seat()
    return part.rotate((0, 0, 0), (1, 0, 0), turn).translate(seat)


def _screen_pocket():
    """Active-area recess in the front face so the screen solid mates flush."""
    z0 = display_total_depth - display_screen_depth
    return (
        cq.Workplane("XY").workplane(offset=z0)
        .box(display_screen_width, display_screen_length, display_screen_depth + 1.0, centered=(True, True, False))
        .edges("|Z").fillet(display_screen_corner_r)
    )


def build_display_body():
    """Caliper-sized housing/PCB with individual underside component bounds."""
    pcb = (
        cq.Workplane("XY").workplane(offset=display_pcb_bottom_z)
        .box(display_pcb_width, display_pcb_length,
             display_pcb_top_z - display_pcb_bottom_z,
             centered=(True, True, False))
        .edges("|Z").fillet(display_pcb_corner_r)
    )
    housing = (
        cq.Workplane("XY").workplane(offset=display_pcb_top_z)
        .box(display_housing_width, display_housing_length,
             display_total_depth - display_pcb_top_z, centered=(True, True, False))
        .edges("|Z").fillet(display_corner_r)
    )
    parts = [pcb.val(), housing.val(), *build_display_components_native().val().Solids()]
    body = cq.Workplane(obj=parts[0].fuse(*parts[1:])).cut(_screen_pocket())
    return _seat_on_tip(body)


def build_display_screen():
    """Active (lit) display area, flush in the front face."""
    z0 = display_total_depth - display_screen_depth
    screen = (
        cq.Workplane("XY").workplane(offset=z0)
        .box(display_screen_width, display_screen_length, display_screen_depth, centered=(True, True, False))
        .edges("|Z").fillet(display_screen_corner_r)
    )
    return _seat_on_tip(screen)


# --- below the counter -------------------------------------------------------
#
# The slab, at `countertop_thickness` under the stack, drawn `countertop_slab_xy` square, which is
# enough to read as a slab around the under-counter plate.


def shank_hole_margin(center_y):
    return _assembly_data('shank_hole_margin', args=[center_y])


def flavor_hole_margin(center_y):
    return _assembly_data('flavor_hole_margin', args=[center_y])


def seated_hole_center_y():
    return _assembly_data('seated_hole_center_y', args=[])


# behind the Westbrass's axis, once it is back against the wall.

# of slab forward of the shank — the play the faucet has
# left to give, which is what lets the gasket cover the hole behind it.


def gasket_hole_cover():
    return _assembly_data('gasket_hole_cover', args=[])


def build_countertop():
    """The slab the stack clamps through, with its drilled hole."""
    slab = (
        cq.Workplane("XY").workplane(offset=countertop_bottom_z)
        .box(countertop_slab_xy, countertop_slab_xy, countertop_thickness,
             centered=(True, True, False))
    )
    hole = (
        cq.Workplane("XY").workplane(offset=countertop_bottom_z - 1.0)
        .center(0, countertop_hole_center_y)
        .circle(hole_radius)
        .extrude(countertop_thickness + 2.0)
    )
    return slab.cut(hole)


def build_under_counter_plate():
    """The cut plate, off the DXF the laser reads, at the slab's underside.

    That DXF's own X is world depth and its Y is world lateral (see the part's
    docstring), so the outline turns a quarter about Z on its way into this
    frame: DXF (x, y) lands at world (-y, x), which puts the pill pocket at
    world +Y over the flavor pair and opens both channels toward +X."""
    outline = cq.importers.importDXF(str(under_counter_dxf))
    plate = outline.wires().toPending().extrude(under_counter_plate_thickness)
    return (
        plate
        .rotate((0, 0, 0), (0, 0, 1), 90.0)
        .translate((0, 0, countertop_bottom_z - under_counter_plate_thickness))
    )


def build_o_ring():
    """The printed TPU thimble sealing the soda faucet tube into the Westbrass's
    Ø10 top port. Its Z = 0 face is the port floor and the tube bottoms on its
    cap, so the cap's top face is where the soda faucet tube starts."""
    return tpu_o_ring.build_o_ring().translate((
        0,
        +port_center_depth,
        soda_faucet_tube_z_bottom - tpu_o_ring.cap_thickness,
    ))


def build_soda_umbilical_tube(bottom_z=None):
    """The blue 1/4" soda umbilical tube, butted on the shank's bottom face and running down.
    It is on the Westbrass's own axis the whole way, so it takes no part in the gather — the
    flavour pair comes to IT."""
    bottom_z = umbilical_tail_z if bottom_z is None else bottom_z
    return (
        cq.Workplane("XY").workplane(offset=bottom_z)
        .circle(soda_umbilical_tube_r)
        .extrude(soda_umbilical_tube_z_top - bottom_z)
    )


def build_foam():
    """The CARGEN segments on the blue tube, drawn as the one sleeve their butts make.

    Five 1-ft lengths butted end to end (`faucet-and-umbilical.md` §3), bare at the compression end
    where the tube lands on the Westbrass and bare again at the wall, where the installer's
    trim takes a whole segment off in a nominal kitchen."""
    return (
        cq.Workplane("XY").workplane(offset=foam_z_bottom)
        .circle(foam_r).circle(soda_umbilical_tube_r)
        .extrude(foam_z_top - foam_z_bottom)
    )


def _sleeve_neck_wires(wall):
    """The braid's neck between the gather and the organizer, `wall` out from its inner face: the
    bare tubes' outline at the gather's top and the puck's round at its foot, which the braid is
    ruled across."""
    bare = (cq.Workplane(xy_plane_z_up).workplane(offset=gather_start_z)
            .placeSketch(bare_bundle_hull(cable_lane + wall)).extrude(0.01)
            .faces("<Z").wires().val())
    puck = cq.Wire.makeCircle(umbilical_organizer.OD / 2 + wall,
                              cq.Vector(*umbilical_organizer.CENTRE_XY, organizer_bottom_z),
                              cq.Vector(0, 0, 1))
    return [bare, puck]


def build_sleeve():
    """The braid over the assembled bundle: over the bare runs from the upper one's top, and over the
    pack from the foam's first plane down to its last.

    What it leaves bare at the bottom is what the installer flexes apart to reach three bulkheads
    standing on one line, and it is where the collars ride.

    DRAWN AS ONE RUN AND FITTED IN SEGMENTS — five of them, one to each of the foam's, the top one
    carried on up over the bare tubes. It lies on what is inside it, so it steps where the foam starts:
    over the bare tubes' outline above that plane and the pack's below it."""
    def sleeve(hull, z_bottom, z_top):
        def prism(grow):
            return (cq.Workplane(xy_plane_z_up).workplane(offset=z_bottom)
                    .placeSketch(hull(grow)).extrude(z_top - z_bottom))
        return prism(cable_lane + sleeve_wall).cut(prism(cable_lane))
    def organizer_ring(z_bottom, z_top):
        return (cq.Workplane("XY").workplane(offset=z_bottom)
                .center(*umbilical_organizer.CENTRE_XY)
                .circle(umbilical_organizer.OD/2+sleeve_wall)
                .circle(umbilical_organizer.OD/2).extrude(z_top-z_bottom))
    outer = cq.Solid.makeLoft(_sleeve_neck_wires(sleeve_wall))
    inner = cq.Solid.makeLoft(_sleeve_neck_wires(0.0))
    return (sleeve(gather_hull, umbilical_z_bottom, gather_start_z)
            .union(sleeve(bundle_hull, sleeve_z_bottom, umbilical_z_bottom))
            .union(cq.Workplane(obj=outer.cut(inner)))
            .union(organizer_ring(organizer_bottom_z,organizer_top_z)))


def build_collar(which, x, y):
    """One tube collar threaded onto the tube at `(x, y)`, as `(collar, word)`.

    The part's own +Y is outboard along its tube, which here is DOWN toward the tail: a quarter turn
    about X lays that on −Z and stands the flag on +Y, and a turn about Z then points the flag out
    of the bundle, away from `sleeve_center_y`, so no two of the three face each other."""
    bodies = (tube_collar.split(import_step(str(tube_collar.STEPS[which])).val())
              if getattr(cq, "MESH", False) else
              (tube_collar.build_collar(which), tube_collar.build_word(which)))
    return tuple(
        body.rotate((0, 0, 0), (1, 0, 0), -90.0)
            .rotate((0, 0, 0), (0, 0, 1), _collar_azimuth(x, y))
            .translate((x, y, collar_top_z))
        for body in bodies
    )


def _collar_azimuth(x, y):
    return _assembly_data('_collar_azimuth', args=[x, y])


# The tails the collars thread onto, `(station, x, y)`.


def _collar_colors(which):
    """A collar's chip colour and its word's: the filaments its chip on the +Y wall prints in."""
    fluid = tube_collar.STATIONS[which].fluid
    return (cq.Color(*(c / 255.0 for c in _rear.chip_color(fluid))),
            cq.Color(*(c / 255.0 for c in _rear.word_color(fluid))))


def umbilical_collars():
    """The three collars the bench threads on, as `(name, solid, colour)` — one per tail, each in
    the filament its chip on the +Y wall of back-top prints in."""
    out = []
    for which, x, y in collar_tails:
        chip, lettering = _collar_colors(which)
        collar, word = build_collar(which, x, y)
        out.append((f"collar_{which.replace('-', '_')}", collar, chip))
        out.append((f"collar_{which.replace('-', '_')}_word", word, lettering))
    return out


# THE COLOUR OF EACH BODY. The umbilical tubes carry the identification colour of their stock, off
# the one table that says what a colour means on this machine — `_y_wall_dimensions.port_colors`,
# the same read by the bulkhead rings, the runs inside the cabinet and the collars on these three
# tails. The blue 1/4-inch soda umbilical tube stops on the Westbrass's lower compression port. The
# separate 3/8-inch soda faucet tube follows the selected faucet finish. Both continuous 4 mm
# flavor runs retain their black stock color.
#
# The donor faucet is matte black (`ledger/bom.md` §9, Westbrass A2031-NL-62) and the printed
# stack around it is PET-GF15; what a hand meets above the counter is one colour end to end.
# Every one of these is `_materials`, so a body here and its own card are one colour.
#
# The gooseneck's 1.47" Waveshare (`ledger/bom.md` §1) is black at the customer-facing display and
# under its black printed cover. The glass is drawn dark because a screen is lit only while the
# machine is dispensing, and a render that paints it lit is drawing a state rather than a part.
def _spool(fluid):
    return cq.Color(*_assembly_data("rgb8-srgb", rgb=_rear.port_colors[fluid]))


body_colors = {
    "black_lldpe": _spool("flavor"),
    "carb": _spool("carb"),
    "drain": _spool("drain"),
    "donor_black": _mat.M_DONOR_BLACK,
    "faucet_black": _mat.C_FAUCET_BLACK,
    "tpu_black": _mat.M_TPU_BLACK,
    "brass": _mat.M_BRASS,
    "display_black": _mat.C_FAUCET_DISPLAY,
    "display_glass": _mat.C_FAUCET_DISPLAY_GLASS,
    "silicone_black": _mat.M_SILICONE_BLACK,
    "stone": cq.Color(0.55, 0.55, 0.58, 0.25),  # the kitchen's slab — context, not a part
    "steel": _mat.M_STAINLESS,                  # the 316 SS under-counter cut plate
    "foam_black": _mat.M_NITRILE_BLACK,         # CARGEN nitrile, on the blue tube only
    "sleeve_black": _mat.M_PET_BRAID,           # PET braid, over the lot
}


def build_assembly():
    """The faucet and its umbilical in the repo's +Z-up frame — the sub-assembly the bench bags,
    from the display on the tip down to the four square-cut tails and their collars."""
    c = body_colors
    shell_base, shell_tip = load_shell_pieces()
    assy = cq.Assembly(name="faucet-assembly")
    assy.add(load_westbrass(), name="westbrass", color=c["donor_black"])
    assy.add(build_soda_faucet_tube(), name="soda_faucet_tube", color=c["black_lldpe"])
    assy.add(build_o_ring(), name="tpu_o_ring", color=c["tpu_black"])
    for x_sign in flavor_sides:
        side = "pos_x" if x_sign > 0 else "neg_x"
        assy.add(build_flavor_faucet_run(x_sign), name=f"flavor_tube_{side}", color=c["black_lldpe"])
        assy.add(build_flavor_umbilical_run(x_sign), name=f"flavor_umbilical_tube_{side}",
                 color=c["black_lldpe"])
    assy.add(build_soda_umbilical_tube(), name="soda_umbilical_tube", color=c["carb"])
    assy.add(build_drain_tube(), name="drain_tube", color=c["drain"])
    assy.add(build_lever(), name="lever", color=c["donor_black"])
    assy.add(load_above_counter_plate(), name="above_counter_plate", color=c["faucet_black"])
    assy.add(load_above_counter_gasket(), name="above_counter_gasket", color=c["tpu_black"])
    assy.add(shell_base, name="shell_base", color=c["faucet_black"])
    assy.add(shell_tip, name="shell_tip", color=c["faucet_black"])
    assy.add(load_display_cover(), name="faucet-display-cover-seated", color=c["faucet_black"])
    for i, (x, y) in enumerate(faucet_shell.base_pod_centers, 1):
        assy.add(build_base_screw(x, y), name=f"base_screw_{i}", color=c["donor_black"])
        assy.add(build_base_insert(x, y), name=f"base_insert_{i}", color=c["brass"])
    assy.add(build_display_body(), name="faucet_display", color=c["display_black"])
    assy.add(build_display_screen(), name="faucet_display_screen", color=c["display_glass"])
    assy.add(build_display_ribbon(), name="display_signal_ribbon", color=c["silicone_black"])
    assy.add(build_countertop(), name="countertop", color=c["stone"])
    assy.add(build_under_counter_plate(), name="under_counter_plate", color=c["steel"])
    assy.add(build_foam(), name="cold_line_foam", color=c["foam_black"])
    assy.add(build_sleeve(), name="umbilical_sleeve", color=c["sleeve_black"])
    assy.add(umbilical_organizer.placed(organizer_top_z), name="umbilical-organizer",
             color=c["faucet_black"])
    for name, solid, color in umbilical_collars():
        assy.add(solid, name=name, color=color)
    return assy


def _section(wire):
    """`wire`'s edges as the kernel's loft sections take them, walked the way the wire walks them:
    `{"line": [a, b]}`, and `{"conic": {"c", "x", "y", "t0", "t1"}}` for a circle or an ellipse
    about `c` on the semi-axes `x` and `y`, from the angle `t0` to `t1`."""
    from OCP.BRep import BRep_Tool
    from OCP.BRepTools import BRepTools_WireExplorer
    from OCP.GeomAbs import GeomAbs_Circle, GeomAbs_Ellipse, GeomAbs_Line
    from OCP.GeomAdaptor import GeomAdaptor_Curve
    from OCP.TopAbs import TopAbs_REVERSED

    def xyz(p):
        return [p.X(), p.Y(), p.Z()]

    out = []
    walk = BRepTools_WireExplorer(wire.wrapped)
    while walk.More():
        edge = walk.Current()
        walk.Next()
        first, last = cq.Edge(edge)._bounds()
        curve = BRep_Tool.Curve_s(edge, 0.0, 0.0)
        adaptor = GeomAdaptor_Curve(curve)
        kind = adaptor.GetType()
        backward = edge.Orientation() == TopAbs_REVERSED
        if kind == GeomAbs_Line:
            ends = [xyz(curve.Value(first)), xyz(curve.Value(last))]
            out.append({"line": ends[::-1] if backward else ends})
        elif kind in (GeomAbs_Circle, GeomAbs_Ellipse):
            if kind == GeomAbs_Circle:
                conic = adaptor.Circle()
                rx = ry = conic.Radius()
            else:
                conic = adaptor.Ellipse()
                rx, ry = conic.MajorRadius(), conic.MinorRadius()
            at = conic.Position()
            out.append({"conic": {"c": xyz(at.Location()),
                                  "x": [v * rx for v in xyz(at.XDirection())],
                                  "y": [v * ry for v in xyz(at.YDirection())],
                                  "t0": last if backward else first,
                                  "t1": first if backward else last}})
        else:
            raise ValueError(f"a section edge on a curve of type {kind}")
    return out


def _moved_legs(legs, by):
    return _assembly_data("_moved_legs", legs=legs, by=by)


def _reversed_legs(legs):
    return _assembly_data("_reversed_legs", legs=legs)


def flavor_run_legs(x_sign):
    return _assembly_data('flavor_run_legs', args=[x_sign])


def flavor_umbilical_legs(x_sign):
    return _assembly_data('flavor_umbilical_legs', args=[x_sign])


def numbers():
    return _assembly_data("numbers")


def main():
    import _rust_part
    out = _assembly_dir / "faucet-assembly.step"
    said = _rust_part.cut("faucet", "faucet-assembly", numbers(), _assembly_dir)
    print("-> " + ", ".join(said["files"]))
    import flute_payload
    grafted = flute_payload.graft(
        Path(str(out) + ".mesh"), flute_payload.surfaces(flute_payload.FAUCET_DIRS))
    if grafted:
        print(f"-> {out.name}.mesh  ({grafted} printable piece(s))")
    report = _assembly_data("report")
    for line in report["lines"]:
        print(line)


if __name__ == "__main__":
    main()
