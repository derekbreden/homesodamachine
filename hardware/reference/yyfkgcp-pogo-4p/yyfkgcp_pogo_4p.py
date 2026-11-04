"""YYFKGCP 4-pin magnetic pogo connector with ears (Amazon B0GCBNTBT8, `ledger/purchases.md`
§9). The FEMALE half carries four flush gold pads between two magnets; the MALE half carries
four spring pins between two magnets. Pressed face to face, the halves mate on their own axis.

External envelope only, read off the listing's two drawings. Either half is one moulded body
4.00 deep: a 17.54 x 4.00 stadium NOSE from the mating face to the ear plate, the EAR PLATE
1.00 thick under it, and the stadium again behind the plate. The plate runs past both ends of
the nose as two ears, each a semicircle on the body's own width, holed Ø1.50 on a 20.44
pitch; its front face stands 2.00 under the mating face. Four Ø0.70 solder tails stand 1.50
off the back on the contacts' 2.54 pitch. The magnets lie flush in the nose face on a 13.54
pitch, N at -X as drawn face-on, and are that face's own material here, not drawn apart from
it. The male's pins stand 1.00 above the nose at rest (5.00 ± 0.15 overall) and travel 1.10.

The ears' overall reach is not dimensioned; `EAR_L` is read off the drawing's scale, with the
ear ends' arcs concentric a little inboard of the holes.

    Rating, per contact   12 V, 2 A; 30 mΩ max at working height
    Spring                45 ± 10 gf at the 1.0 mm working height; 10,000 cycles
    Materials             UL94 V-0 housing; C3604 brass plunger and barrel, gold over nickel

Frame: the MATING FACE is the XY plane at Z = 0, facing +Z, and the body hangs -Z. The long
axis is X, contacts and ears on it. Origin at the face's centre — the station either half is
seated on, as `jhyossthi_pogo_dock` seats its pill.

Geometry is in the frozen STEPs and display payloads beside this module.
`frozen-asset.json` records their bytes and source snapshot.
"""

from pathlib import Path

_here = Path(__file__).resolve()
STEP_PATHS = {half: _here.parent / f"pogo-4p-{half}.step" for half in ("female", "male")}
PAYLOAD_PATHS = {half: step.with_name(step.name + ".mesh") for half, step in STEP_PATHS.items()}
ASSET_MANIFEST_PATH = _here.parent / "frozen-asset.json"

# The nose and the body behind the ear plate: one stadium, the body's whole depth.

_reference_hardware = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('yyfkgcp_pogo_4p')
globals().update({name: _reference_values[name] for name in ('BODY_L', 'BODY_W', 'BODY_T', 'EAR_FACE', 'EAR_T', 'EAR_PITCH', 'EAR_HOLE_D', 'EAR_L', 'PINS', 'PIN_PITCH', 'TAIL_D', 'TAIL_L', 'PIN_D', 'PIN_PROUD', 'STROKE', 'PAD_D', 'MAGNET_PITCH')})

# The ear plate: its front face under the mating face, its thickness, and the two holes.
# The plate's overall reach, end to end — read off the drawing, not dimensioned on it.
# The four contacts and their solder tails off the back.
# The male's plunger tip, how far it stands proud of the nose at rest, and its whole travel.
# The female's flush pad, and the magnets' pitch.


def contact_xs():
    "The four contacts' X stations, -X first."
    return _reference_data('yyfkgcp_pogo_4p', 'contact_xs', (), {})


def ear_xs():
    "The two ear holes' X stations."
    return _reference_data('yyfkgcp_pogo_4p', 'ear_xs', (), {})


def ear_back():
    "Mating face to the ear plate's back — the face the plate bears on when seated."
    return _reference_data('yyfkgcp_pogo_4p', 'ear_back', (), {})


def reach_back():
    "Mating face to the tails' tips."
    return _reference_data('yyfkgcp_pogo_4p', 'reach_back', (), {})


def main():
    for name, step in STEP_PATHS.items():
        print(name)
        print(f"  STEP: {step}")
        print(f"  Display payload: {PAYLOAD_PATHS[name]}")


if __name__ == "__main__":
    main()
