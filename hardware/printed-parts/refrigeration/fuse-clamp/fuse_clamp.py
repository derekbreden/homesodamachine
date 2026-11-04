"""Fuse clamp — the printed bracket that holds the SF76E's case against the compressor's
power box.

A [77](CLAMP_TF) °C cutoff opens on the temperature of ITS OWN CASE, so what the machine owes
the part is contact: the case pressed onto the moulded cover over the terminal block and the
PTC start relay, which is the surface whose temperature the cutoff exists to answer to. Leads
carry no thermal load, and a case laid loose against a face reads cabinet air.

    HEAD      a block on the seating plane with a channel through it, the channel's crown
              landing on the case's outboard generatrix — so the case is pinched between the
              cover and the crown, and the clamp never comes between the two
    NECK      one plank down the cover's own flank, from the head to the plate's crown,
              bearing on the cover the whole way
    LEAVES    two of them, reaching inboard off the neck into the [15](CLAMP_GAP) mm of air the
              power box hangs over its own base plate — the upper on the box's underside,
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

THE FLANK AND NOT THE FRONT. The box's -Y face is the deepest plane the donor has, so a part
standing proud of it is the frontmost body in the cabinet and the appliance's own front wall
answers to this clamp. The flank costs the machine nothing: the plate reaches past it, so the
head stands over the can's own metal, and the gap the leaves press runs the box's whole
footprint and is entered from here as readily as from the front. What the front had that this
does not is the shell, which stands on the box's aft plane — a leaf reaching off the front runs
AT the belly, and one reaching off the flank runs along under the box, fenced by the box's own
[45](CLAMP_BOX_DEPTH) mm of width.

Coordinate frame — the CUTOFF'S OWN, so `enclosure_assembly` lays both bodies with one turn on
one station and they cannot land apart:

- X = the cutoff's axis, across the cover's own [27.5](CLAMP_FACE_X) mm flank.
- Z = 0 is the SEATING PLANE — the cover's +X flank, the plane `compressor.power_face` states;
  +Z is out of it into the cabinet, and only the leaves reach behind it.
- Y is up, 0 on the face's centre — which is the case's own axis and the box's mid-height.

THE KERNEL CUTS THE FILES. This module holds the numbers and writes the ones the geometry takes
(`numbers()`) to `fuse-clamp.numbers.json`; `fuse_clamp.rs`, beside it, cuts `fuse-clamp.step`,
its payload and `fuse-clamp.stl` from them (`hardware/scripts/_rust_part.py`), once the part has
held its pinch: a case grown [0.01](CLAMP_CONTACT_TOL) mm proud of its own diameter meets the
crown. `build()` draws the same part in CadQuery, which is the body `enclosure_assembly` seats.

Run:
    tools/cad-venv/bin/python hardware/printed-parts/refrigeration/fuse-clamp/fuse_clamp.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (_hw / "scripts",
           _hw / "printed-parts" / "cadlib",
           _hw / "reference" / "compressor",
           _hw / "reference" / "sf76e-thermal-fuse"):
    sys.path.insert(0, str(_p))
sys.path.insert(0, str(next(p for p in _here.parents
                            if (p / "tools" / "docgen").is_dir()) / "tools"))
if __name__ == "__main__":
    import _rust_part
    _rust_part.start()

import cadquery as cq  # noqa: E402
from _materials import M_PETG_BLACK, linear  # noqa: E402
import _stated_bounds as _bounds  # noqa: E402
import compressor as _comp  # noqa: E402
import sf76e_thermal_fuse as _fuse  # noqa: E402
import fits  # noqa: E402
from docgen import substitute_md, substitute_py_comments  # noqa: E402

# --- the donor, read off its own module -----------------------------------
# Every figure the clamp closes on comes from the part it closes on, so a re-calipered
# compressor moves the clamp rather than leaving it holding air.

def _reference_inputs(method='state'):
    values = {'fits': {'slip': fits.slip}}
    if method == 'numbers':
        values['fuse_color'] = list(linear(M_PETG_BLACK))
    return values

import pathlib as _reference_pathlib
_reference_hardware = next(p for p in _reference_pathlib.Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('fuse_clamp', inputs=_reference_inputs())
globals().update({name: _reference_values[name] for name in ('FACE_X', 'FACE_Y', 'BOX_FLOOR', 'GAP', 'PLATE_TOP', 'BOX_DEPTH', 'FLANK_REACH', 'CASE_D', 'CASE_L', 'LEAD_STUB', 'LEAD_SHORT', 'TF_C', 'SLIP', 'CHANNEL_H', 'CHANNEL_Z', 'CROWN', 'HEAD_Z', 'LEAD_RELEASE', 'PART_X', 'HEAD_PAD', 'HEAD_Y', 'SPLICE_REACH', 'NECK_Z', 'LEAF_Y', 'LEAF_REACH', 'LEAF_SLOT', 'LEAF_LEAD_IN', 'SPLICE_FREE', 'CONTACT_TOL')})

# how far a leaf may reach off this flank before it comes out under the far one.

# --- the cutoff, read off its own module ----------------------------------

# --- the head -------------------------------------------------------------
# The channel is the case's whole seat. Its depth is the case's OWN DIAMETER, so the crown lands
# on the outboard generatrix and the pinch is cover — case — crown with nothing in between; its
# height is one slip over the case, so the walls fence the case without ever taking the load.
# How far past the no-bend zone the channel lets the lead go. A lead is wire past this and the
# clamp has no business on it; a lead is the part's own pose before it, and the channel holds it.
# The band of head that lies on the cover above and below the channel — what the crown's
# reaction spreads into, and the clamp's own datum for how deep the channel stands.
# What a crimp splice needs of the short lead once the channel has let go of it.

# --- the neck and the leaves ----------------------------------------------
# Each leaf's section, and how far back into the gap they reach. Thin and long is the point:
# they are cantilevers, and their bending is the whole of what takes up a gap the donor does not
# promise to the tenth. What is left between them is the slot they close into.

# What the channel leaves of the short lead, in the open, for the splice.
# How close the clamp's crown must stand to the case before the pair counts as touching.


# --- the bounds this clamp states about the donor -------------------------
#
# Everything the clamp takes hold of belongs to a part nobody here draws. These are the claims
# that hold about it, read the moment this module is, and rendered on the enclosure card by
# `enclosure_assembly.carry_stated_bounds` — so a re-calipered compressor turns them red on the
# committed card rather than in a terminal.

_donor = _bounds.bound(
    "fuse-clamp-donor", "The clamp closes on features the compressor actually has",
    "head inside the flank's face, leaves filling its gap and under its own box")
for _ok, _note in _reference_data('fuse_clamp', '_donor_readings', (), {}, inputs=_reference_inputs()):
    _donor(_ok, _note)


def _profile():
    "The part's whole silhouette in the Y-Z plane, as the polygon it is swept across X on.\n\n    Read from the head's outboard top corner: the head stands proud of the neck by what the\n    crown needs over the case, the neck runs down the cover's own flank to the plate's crown,\n    and the two leaves reach inboard off it into the gap — each chamfered at its tip so it\n    starts into that gap rather than butting the metal at the mouth of it."
    return _reference_data('fuse_clamp', '_profile', (), {}, inputs=_reference_inputs())


def numbers():
    "What `fuse_clamp.rs` cuts the part from: the profile's corners and the channel, in the\n    cutoff's own frame, the case it holds its pinch on, and the body's name and colour."
    return _reference_data('fuse_clamp', 'numbers', (), {}, inputs=_reference_inputs('numbers'))


def build():
    """The profile swept the part's one width, with the channel cut through it."""
    section = _profile()
    part = (
        cq.Workplane("YZ", origin=(-PART_X / 2.0, 0.0, 0.0))
        .polyline(section + section[:1]).wire().extrude(PART_X)
    )
    channel = cq.Workplane("XY", origin=(0.0, 0.0, CHANNEL_Z / 2.0)).box(
        PART_X + 2.0, CHANNEL_H, CHANNEL_Z)
    return part.cut(channel).val()


def selftest():
    # The part is one claim about a cutoff, and the program reads it back off the solid it cuts.
    import _rust_part

    _rust_part.check("refrigeration", "fuse-clamp", numbers())
    return _bounds.report()


def main():
    import _rust_part
    said = _rust_part.cut('refrigeration', 'fuse-clamp', numbers(), _here.parent)
    part = said['bodies'][0]
    _reference_data('fuse_clamp', '_report', (part, said['files']), {}, inputs=_reference_inputs())
    variables = _reference_data('fuse_clamp', '_docvars', (part,), {}, inputs=_reference_inputs())
    substitute_py_comments(Path(__file__), variables=variables)
    substitute_md(_here.parent / 'README.md', variables=variables)
    print('-> README.md')


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    main()
