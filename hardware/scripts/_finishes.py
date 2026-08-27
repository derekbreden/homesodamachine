#!/usr/bin/env python3
"""_finishes.py — how each material on this machine takes the light, in one table.

A COLOUR IS HALF OF WHAT A MATERIAL LOOKS LIKE and until this table there was only that half.
A STEP carries `COLOUR_RGB` and nothing else — no roughness, no name — so a body reaches a
renderer already reduced to three numbers, and every one of them was drawn at one hardcoded
roughness. This is the other half, carried alongside rather than inside.

TWO MODULES OWN FINISHES AND THIS IS WHERE THEY MEET. `_materials.FINISHES` holds the 44
substances that module names, and `_routing.SPOOLS` holds the tube stock, whose finish rides the
`Spool` beside its colour because a spool is where a tube's facts live. `_materials` cannot reach
`_routing` — it sits at the BOTTOM of the import graph and an edge from there is an edge from
everything — so the merge happens up here.

Both renderers read this: `check_finishes.py` writes it to `web/public/finishes.json` for the
browser, and `assembly/scenes/render_scenes.py` bakes it into every scene GLB's PBR material.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import _materials as _mat                                        # noqa: E402
import _routing                                                  # noqa: E402


#: Colours where two substances genuinely share a triple, and the finish the pair is drawn at.
#: The value is the one that wins; the comment is why it is the one that wins.
SHARED = {
    # A TUBE AND A PRINT AT ONE COLOUR, twice, and both times because the identification scheme
    # and the filament that answers to it were chosen to match. `port_colors` and
    # `chip_filaments` are "a different product answering to the same name, and the two are a
    # few points apart" — except at these two, where they are not apart at all.
    #
    # THE PRINT'S FIGURE CARRIES BOTH PAIRS: far more bodies at either colour come off a plate
    # than off a spool, and the two estimates are a tenth apart in a table that is estimates
    # throughout. Separating them would take a measured colour for the LLDPE, which this tree
    # does not have.
    #
    #   black — neoFlo black LLDPE against Bambu PETG Basic Black, at `port_colors["flavor"]`:
    #           the five potted cold-core runs and the printed plugs beside them.
    #   white — neoFlo white LLDPE against PETG Basic White, at `port_colors["water"]`: the tap
    #           runs, the water chip and every word lettered in white.
    #
    # The `copper` spool is NOT here and needs no entry — `M_COPPER` is declared as that spool's
    # own stock at that spool's own triple, so the two agree and nothing has to give way.
    "black": "M_PETG_BLACK",
    "white": "the chip's PETG Basic White",
}


def rows():
    """Every finish this tree states, materials and tube stock together."""
    out = _mat.finish_rows()
    at = {tuple(r["rgb"]): r for r in out}
    for name, spool in sorted(_routing.SPOOLS.items()):
        raw = _routing.color(name)
        # Both spellings of a white, for the reason `_materials.finish_rows` states.
        for rgb in dict.fromkeys((_mat.linear(raw), _mat.linear(_mat.step_safe(raw)))):
            _place(name, spool, rgb, out, at)
    return sorted(out, key=lambda r: r["rgb"])


def _place(name, spool, rgb, out, at):
    """Give `rgb` the spool's finish, unless a material already claimed that colour."""
    held = at.get(rgb)
    if held is None:
        row = {"rgb": list(rgb), "roughness": spool.roughness, "metalness": spool.metalness}
        out.append(row)
        at[rgb] = row
        return
    if (held["roughness"], held["metalness"]) == (spool.roughness, spool.metalness):
        return
    if name not in SHARED:
        sys.exit(
            f"check_finishes: spool {name!r} and a material share the colour {rgb} but ask "
            f"for different finishes — spool {(spool.roughness, spool.metalness)} against "
            f"{(held['roughness'], held['metalness'])}. Give one of them its own colour, or "
            f"name the pair in SHARED and say which figure carries it.")


def find(rgb, tol=4e-4):
    """The finish for a linear triple, or `None` where the tree names no material at it.

    MATCHED ON DISTANCE, NOT ON A KEY, and for the same reason the browser matches that way:
    near black the linear palette is crowded enough that a byte holds two of its colours, so
    there is no rounding two readers could share. The closest two materials here stand 0.00162
    apart, so `tol` is a quarter of the gap and a hit is unambiguous."""
    best, bestd = None, tol * tol
    for row in rows():
        d = sum((row["rgb"][i] - rgb[i]) ** 2 for i in range(3))
        if d <= bestd:
            best, bestd = row, d
    return best
