"""Fuse clamp — the printed bracket that holds the SF76E's case against the compressor's
power box.

A [77](CLAMP_TF) °C cutoff opens on the temperature of ITS OWN CASE, so what the machine owes
the part is contact: the case pressed onto the moulded cover over the terminal block and the
PTC start relay, which is the surface whose temperature the cutoff exists to answer to. Leads
carry no thermal load, and a case laid loose against a face reads cabinet air.

    HEAD      a block on the seating plane with a channel through it, the channel's crown
              landing on the case's outboard generatrix — so the case is pinched between the
              cover and the crown, and the clamp never comes between the two
    NECK      one plank down the compressor's own front plane, from the head to the plate's
              front edge, bearing on the cover the whole way
    LEAVES    two of them, reaching aft off the neck into the [15](CLAMP_GAP) mm of air the
              power box hangs over its own mounting plate — the upper on the box's underside,
              the lower on the plate's crown

THE LEAVES ARE THE MOUNT, and that gap is the only place on this donor a clamp can be held.
The case's force is a NORMAL force. A cover has a front, a top, a bottom and two sides, every
one of them a plane whose normal is across that push; a hook over any of them resists nothing
pressing straight out of the front, and no band closes around a box whose aft face is moulded
onto the shell. The plate's four holes are spoken for — donor grommet and the floor's own
printed post rising through each — and the grommet is the isolation element, so anything
landing on that screw is fastened to the CABINET while the cover it presses rides the can. What
is left is the gap: a slot [15](CLAMP_GAP) mm tall whose two faces, the box's underside and the
plate's crown, both belong to the compressor. The leaves press it, so the clamp rides the
compressor, the vibration is common to the clamp, the cutoff and the face, and nothing bridges
to the cabinet.

EVERY FIT IS DRAWN ON THE THING IT CLOSES ON: the channel's depth is the case's own diameter,
the leaves span the gap's own height. The model is the nominal fit, and what makes each of them
a press is the print's own tolerance — taken up by the leaves, which are cantilevers and the
one compliant thing here.

NOTHING IS DRILLED AND THE COVER IS NOT TOUCHED. Everything the clamp closes on the donor
already has.

ONE WIDTH FOR THE WHOLE PART, [18](CLAMP_PART_X), and it comes from the lead: the channel holds
the whole [3](CLAMP_LEAD_STUB) mm of straight the SF/E datasheet reserves against a bend and
lets the lead go [0.5](CLAMP_LEAD_RELEASE) mm past it, leaving [16.5](CLAMP_SPLICE_FREE) mm of
the short lead in the open for the splice. Every feature is then a prism on that one width, so
the part is one profile swept across it and prints on its side with nothing under it.

The cutoff threads in along the channel from either end — the channel is open at both — so a
one-shot part is replaced without the clamp coming off and without the compressor being
disturbed.

Coordinate frame — the CUTOFF'S OWN, so `enclosure_assembly` lays both bodies with one turn on
one station and they cannot land apart:

- X = the cutoff's axis, across the cover's own [45](CLAMP_FACE_X) mm width.
- Z = 0 is the SEATING PLANE — the cover's outboard face, the plane `compressor.power_face`
  states. It is the plate's own front edge as well, since the box stands on that edge; +Z is out
  of it into the cabinet, and only the leaves reach behind it.
- Y is up, 0 on the face's centre — which is the case's own axis and the box's mid-height.

Run:
    tools/cad-venv/bin/python hardware/printed-parts/refrigeration/fuse-clamp/fuse_clamp.py
"""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (_hw / "scripts",
           _hw / "reference" / "compressor",
           _hw / "reference" / "sf76e-thermal-fuse"):
    sys.path.insert(0, str(_p))
sys.path.insert(0, str(next(p for p in _here.parents
                            if (p / "tools" / "docgen").is_dir()) / "tools"))
from _cadq_export import export_step  # noqa: E402
import _overlap  # noqa: E402
import _stated_bounds as _bounds  # noqa: E402
import compressor as _comp  # noqa: E402
import sf76e_thermal_fuse as _fuse  # noqa: E402
from docgen import substitute_md, substitute_py_comments  # noqa: E402

# --- the donor, read off its own module -----------------------------------
# Every figure the clamp closes on comes from the part it closes on, so a re-calipered
# compressor moves the clamp rather than leaving it holding air.
FACE_X = _comp.POWER_X                        # [45](CLAMP_FACE_X) — the cover's own width
FACE_Y = _comp.POWER_Z                        # its standing height, the same figure
BOX_FLOOR = -FACE_Y / 2.0                     # the box's underside — the gap's own ceiling
GAP = _comp.POWER_GAP                         # [15](CLAMP_GAP) of air under the box
PLATE_TOP = BOX_FLOOR - GAP                   # the plate crown — the gap's own floor
BOX_DEPTH = _comp.POWER_Y                     # how far back the box reaches, to the shell

# --- the cutoff, read off its own module ----------------------------------
CASE_D = _fuse.BODY_D
CASE_L = _fuse.BODY_L
LEAD_STUB = _fuse.LEAD_STUB                   # [3](CLAMP_LEAD_STUB), the datasheet's no-bend zone
LEAD_SHORT = _fuse.LEAD_SHORT                 # the shorter of the two leads, and the binding one
TF_C = _fuse.TF_C                             # [77](CLAMP_TF) °C — what the contact is for

# --- the head -------------------------------------------------------------
# The channel is the case's whole seat. Its depth is the case's OWN DIAMETER, so the crown lands
# on the outboard generatrix and the pinch is cover — case — crown with nothing in between; its
# height is one slip over the case, so the walls fence the case without ever taking the load.
SLIP = 0.2
CHANNEL_H = CASE_D + 2.0 * SLIP
CHANNEL_Z = CASE_D
CROWN = 2.5                                   # the section over the case
HEAD_Z = CHANNEL_Z + CROWN
# How far past the no-bend zone the channel lets the lead go. A lead is wire past this and the
# clamp has no business on it; a lead is the part's own pose before it, and the channel holds it.
LEAD_RELEASE = 0.5
PART_X = CASE_L + 2.0 * (LEAD_STUB + LEAD_RELEASE)   # [18](CLAMP_PART_X), and the whole part's
# The band of head that lies on the cover above and below the channel — what the crown's
# reaction spreads into, and the clamp's own datum for how deep the channel stands.
HEAD_PAD = 6.7
HEAD_Y = CHANNEL_H / 2.0 + HEAD_PAD
# What a crimp splice needs of the short lead once the channel has let go of it.
SPLICE_REACH = 12.0

# --- the neck and the leaves ----------------------------------------------
NECK_Z = 3.5                                  # the plank's own section, out of the face
# Each leaf's section, and how far back into the gap they reach. Thin and long is the point:
# they are cantilevers, and their bending is the whole of what takes up a gap the donor does not
# promise to the tenth. What is left between them is the slot they close into.
LEAF_Y = 2.5
LEAF_REACH = 22.0
LEAF_SLOT = GAP - 2.0 * LEAF_Y                # [10](CLAMP_LEAF_SLOT) between the two
LEAF_LEAD_IN = 1.5                            # the 45° that starts a leaf into the gap

# What the channel leaves of the short lead, in the open, for the splice.
SPLICE_FREE = LEAD_SHORT - (PART_X - CASE_L) / 2.0
# How close the clamp's crown must stand to the case before the pair counts as touching.
CONTACT_TOL = 0.01


def shell_front_z(x: float) -> float:
    """Where the compressor's SHELL stands, at one X across the box, in this frame.

    The box's aft face is on the shell's own tangent and the ellipse falls away from it either
    side, so how far a leaf may reach back is a function of where across the plate it runs."""
    half = _comp.SHELL_X / 2.0
    if abs(x) >= half:
        return -math.inf
    y = _comp.SHELL_OFFSET_Y - (_comp.SHELL_Y / 2.0) * math.sqrt(1.0 - (x / half) ** 2)
    return _comp.POWER_Y0 - y


SHELL_AT_LEAF = max(shell_front_z(-PART_X / 2.0), shell_front_z(PART_X / 2.0))


# --- the bounds this clamp states about the donor -------------------------
#
# Everything the clamp takes hold of belongs to a part nobody here draws. These are the claims
# that hold about it, read the moment this module is, and rendered on the enclosure card by
# `enclosure_assembly.carry_stated_bounds` — so a re-calipered compressor turns them red on the
# committed card rather than in a terminal.

_donor = _bounds.bound(
    "fuse-clamp-donor", "The clamp closes on features the compressor actually has",
    "head inside the cover's face, leaves filling its gap and short of its shell")
_donor(PART_X <= FACE_X,
       f"the part is {PART_X:g} across a cover {FACE_X:g} wide — it hangs off the face it is "
       f"there to bear on")
_donor(HEAD_Y <= FACE_Y / 2.0,
       f"the head reaches y ±{HEAD_Y:g} on a cover {FACE_Y:g} tall — it stands off the top or "
       f"the bottom of the face it bears on")
_donor(abs(2.0 * LEAF_Y + LEAF_SLOT - GAP) < 1e-9,
       f"the two leaves and their slot come to {2.0 * LEAF_Y + LEAF_SLOT:g} in a gap of "
       f"{GAP:g} — the tongue no longer spans the one slot on this donor that holds it")
_donor(LEAF_SLOT > 2.0 * LEAF_LEAD_IN,
       f"the slot between the leaves is {LEAF_SLOT:g} and each lead-in takes {LEAF_LEAD_IN:g} "
       f"of leaf — there is nothing left for either to close into")
_donor(-LEAF_REACH > SHELL_AT_LEAF,
       f"the leaves reach z {-LEAF_REACH:g} and the shell's belly stands at {SHELL_AT_LEAF:.2f} "
       f"across the band they run in — the tongue is driven into the can")
_donor(LEAF_REACH < BOX_DEPTH,
       f"the leaves reach {LEAF_REACH:g} into a box {BOX_DEPTH:g} deep — they come out of the "
       f"back of the gap they are pressed in")

_bounds.bound(
    "fuse-clamp-lead", "The clamp lets the cutoff's lead go where a bend becomes legal",
    f"channel past the case ≥ {LEAD_STUB:g}, short lead left in the open ≥ {SPLICE_REACH:g}")(
    (PART_X - CASE_L) / 2.0 >= LEAD_STUB and SPLICE_FREE >= SPLICE_REACH,
    f"the channel runs {(PART_X - CASE_L) / 2.0:g} past the case's end against the "
    f"{LEAD_STUB:g} the datasheet reserves, and leaves {SPLICE_FREE:g} of the {LEAD_SHORT:g} "
    f"short lead in the open against the {SPLICE_REACH:g} a splice takes — a bend struck inside "
    f"the channel is a bend struck in the no-bend zone, and a splice inside it is a splice on a "
    f"lead the clamp is still holding")


def _profile():
    """The part's whole silhouette in the Y-Z plane, as the polygon it is swept across X on.

    Read from the head's outboard top corner: the head stands proud of the neck by what the
    crown needs over the case, the neck runs down the compressor's own front plane to the
    plate's crown, and the two leaves reach aft off it into the gap — each chamfered at its tip
    so it starts into that gap rather than butting the metal at the mouth of it."""
    return [
        (HEAD_Y, HEAD_Z),                                     # the head, outboard top
        (-HEAD_Y, HEAD_Z),                                    # the head, outboard bottom
        (-HEAD_Y, NECK_Z),                                    # step in to the neck
        (PLATE_TOP, NECK_Z),                                  # the neck, outboard bottom
        (PLATE_TOP, -LEAF_REACH + LEAF_LEAD_IN),              # the lower leaf, on the crown
        (PLATE_TOP + LEAF_LEAD_IN, -LEAF_REACH),              # its lead-in
        (PLATE_TOP + LEAF_Y, -LEAF_REACH),                    # up the leaf's tip
        (PLATE_TOP + LEAF_Y, 0.0),                            # forward along the slot
        (BOX_FLOOR - LEAF_Y, 0.0),                            # across the slot's front
        (BOX_FLOOR - LEAF_Y, -LEAF_REACH),                    # aft along the upper leaf
        (BOX_FLOOR - LEAF_LEAD_IN, -LEAF_REACH),              # its lead-in
        (BOX_FLOOR, -LEAF_REACH + LEAF_LEAD_IN),
        (BOX_FLOOR, 0.0),                                     # forward under the box
        (HEAD_Y, 0.0),                                        # up the seating plane to the head
    ]


def build():
    """The profile swept the part's one width, with the channel cut through it."""
    part = (
        cq.Workplane("YZ", origin=(-PART_X / 2.0, 0.0, 0.0))
        .polyline(_profile()).close().extrude(PART_X)
    )
    channel = cq.Workplane("XY", origin=(0.0, 0.0, CHANNEL_Z / 2.0)).box(
        PART_X + 2.0, CHANNEL_H, CHANNEL_Z)
    return part.cut(channel).val()


# --- Holds ----------------------------------------------------------------
# The part is one claim about a cutoff and one about a cover. Each hold reads its claim back off
# the solids rather than off the constants that produced them.

def pinch_hold():
    """The crown lands ON the case and nowhere in it, and touches nothing else the part has.

    Read against the cutoff's OWN SOLID, drawn in this same frame on this same seating plane:
    the two bodies share a channel and a case, and the only reading that says the clamp closes on
    one is the pair itself. Grown by `CONTACT_TOL` the case must meet the crown — a clamp
    standing off is a case lying loose on a face — and at its own diameter it must not, because
    a crown drawn into the case is a fuse the machine crushes rather than holds."""
    clamp, cutoff = build(), _fuse.build()
    _shape, crush = _overlap.common(clamp, cutoff)
    if crush > 1e-6:
        raise ValueError(
            f"the clamp and the cutoff share {crush:.3f} mm³ — the channel is cut shallower than "
            f"the Ø{CASE_D:g} case is round, or its walls have closed on the leads, and either "
            f"way the part is drawn through the body it is there to hold.")
    grown = cq.Solid.makeCylinder(
        CASE_D / 2.0 + CONTACT_TOL, CASE_L,
        cq.Vector(-CASE_L / 2.0, 0.0, CASE_D / 2.0), cq.Vector(1, 0, 0))
    _shape, touch = _overlap.common(clamp, grown)
    if touch <= 0.0:
        raise ValueError(
            f"a case grown {CONTACT_TOL:g} mm proud of its own Ø{CASE_D:g} still misses the "
            f"clamp — the crown stands off the generatrix it is meant to bear on, so nothing "
            f"presses the case onto the cover and a {TF_C:g} °C cutoff is reading cabinet air.")


def face_hold():
    """Nothing the clamp puts behind the seating plane stands where the box is.

    The leaves are the whole of what reaches back, and they run in the air under the cover. A
    body drawn into that cover is a clamp that cannot be installed, and a head bedded into it is
    a head whose channel never reaches the case."""
    box = cq.Workplane("XY", origin=(0.0, 0.0, -BOX_DEPTH / 2.0)).box(
        FACE_X, FACE_Y, BOX_DEPTH)
    _shape, vol = _overlap.common(build(), box.val())
    if vol > 1e-6:
        raise ValueError(
            f"the clamp fills {vol:.3f} mm³ of the power box's own body — Z = 0 is the cover's "
            f"face, and everything this part puts behind it belongs in the {GAP:g} mm of air "
            f"under the box.")


def selftest():
    pinch_hold()
    face_hold()
    return _bounds.report()


def main():
    pinch_hold()
    face_hold()
    part = build()
    bb = part.BoundingBox()
    print("fuse clamp — the SF76E's case, held on the compressor's power box")
    print(f"  X[{bb.xmin:.2f}, {bb.xmax:.2f}]  Y[{bb.ymin:.2f}, {bb.ymax:.2f}]"
          f"  Z[{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  head    {PART_X:g} x {2 * HEAD_Y:g} x {HEAD_Z:g} on the seating plane, "
          f"{HEAD_PAD:g} of bearing above and below the channel")
    print(f"  channel {CHANNEL_H:g} x {CHANNEL_Z:g} through it — the crown on the Ø{CASE_D:g} "
          f"case's outboard generatrix, {SLIP:g} of slip a side")
    print(f"  neck    {NECK_Z:g} out of the face, down it from y {-HEAD_Y:g} to the plate's "
          f"crown at {PLATE_TOP:g}")
    print(f"  leaves  {LEAF_Y:g} thick, {LEAF_REACH:g} aft, {LEAF_SLOT:g} of slot between them "
          f"in the box's {GAP:g} of gap — {abs(-LEAF_REACH - SHELL_AT_LEAF):.2f} clear of the "
          f"shell")
    print(f"  lead    let go {(PART_X - CASE_L) / 2.0:g} off the case against the {LEAD_STUB:g} "
          f"no-bend zone, {SPLICE_FREE:g} of the short lead left for the splice")
    print(f"  volume  {part.Volume() / 1000.0:.2f} cm³")
    out = _here.parent / "fuse-clamp.step"
    export_step(part, str(out))
    print(f"-> {out.name}")

    variables = {
        "CLAMP_TF": f"{TF_C:g}",
        "CLAMP_FACE_X": f"{FACE_X:g}",
        "CLAMP_GAP": f"{GAP:g}",
        "CLAMP_PART_X": f"{PART_X:g}",
        "CLAMP_LEAD_STUB": f"{LEAD_STUB:g}",
        "CLAMP_LEAD_RELEASE": f"{LEAD_RELEASE:g}",
        "CLAMP_SPLICE_FREE": f"{SPLICE_FREE:g}",
        "CLAMP_SPLICE_REACH": f"{SPLICE_REACH:g}",
        "CLAMP_CASE_D": f"{CASE_D:g}",
        "CLAMP_CHANNEL_H": f"{CHANNEL_H:g}",
        "CLAMP_HEAD_Y": f"{2 * HEAD_Y:g}",
        "CLAMP_HEAD_Z": f"{HEAD_Z:g}",
        "CLAMP_NECK_Z": f"{NECK_Z:g}",
        "CLAMP_LEAF_Y": f"{LEAF_Y:g}",
        "CLAMP_LEAF_REACH": f"{LEAF_REACH:g}",
        "CLAMP_LEAF_SLOT": f"{LEAF_SLOT:g}",
        "CLAMP_VOL": f"{part.Volume() / 1000.0:.2f}",
    }
    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={
            "CLAMP_TF": 2, "CLAMP_FACE_X": 2, "CLAMP_GAP": 3, "CLAMP_PART_X": 2,
            "CLAMP_LEAD_STUB": 2, "CLAMP_LEAD_RELEASE": 1, "CLAMP_SPLICE_FREE": 1,
            "CLAMP_LEAF_SLOT": 1,
        },
    )
    substitute_md(
        _here.parent / "README.md",
        variables=variables,
        expected_counts={
            "CLAMP_TF": 1, "CLAMP_FACE_X": 1, "CLAMP_GAP": 3, "CLAMP_PART_X": 2,
            "CLAMP_LEAD_STUB": 2, "CLAMP_SPLICE_FREE": 1, "CLAMP_SPLICE_REACH": 1,
            "CLAMP_CASE_D": 1, "CLAMP_CHANNEL_H": 1,
            "CLAMP_HEAD_Y": 1, "CLAMP_HEAD_Z": 1, "CLAMP_NECK_Z": 1,
            "CLAMP_LEAF_Y": 1, "CLAMP_LEAF_REACH": 2, "CLAMP_LEAF_SLOT": 1, "CLAMP_VOL": 1,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    main()
