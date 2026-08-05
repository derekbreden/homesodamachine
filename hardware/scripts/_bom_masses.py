#!/usr/bin/env python3
"""Compute bom.md §7's printed-part masses from each part's own CAD solid and
write them into the Mass + $ cells — so "geometry-derived" is a property of the
table rather than a claim about it.

Third of the three ledger drivers: _bom_sync.py owns the geometry-derived
QUANTITY markers, _bom_totals.py owns the COST rollups, this owns the MASS
column of §7 and the $ that follows from it.

    mass = Σ(solid volume) × density        $ = mass × the material's $/kg

Every `<!--@printed-->` row names its geometry in PARTS below. A row with no
entry, an entry naming a file that is not there, or a material with no density
is an ERROR, not a skipped row — a printed part cannot enter the table without
the solid that gives it a mass.

The masses are only as current as the STEPs they read. `npm --prefix web run
build:check` is what proves those match their generators; run it first when the
numbers matter.

Run:  tools/cad-venv/bin/python hardware/scripts/_bom_masses.py            # write
      tools/cad-venv/bin/python hardware/scripts/_bom_masses.py --check    # report only, exit 1 on drift

Then `_bom_totals.py` to carry the new line costs into the section + grand totals.
"""
import re
import sys
from pathlib import Path

REPO = next(p for p in Path(__file__).resolve().parents if (p / "hardware").is_dir())
BOM = REPO / "hardware" / "ledger" / "bom.md"
PARTS_DIR = REPO / "hardware" / "printed-parts"

# Density (g/cm³) and price ($/kg), both as §7's own prose states them. Colour
# changes what a part looks like, not what it costs, so translucent PETG is PETG.
MATERIALS = {
    "PETG": (1.27, 11.20),
    "PET-CF": (1.30, 39.32),
}

# Row label in §7 -> the STEP solids that ship as that row. A row covering
# several pieces (an enclosure half, the plug stack) lists them all; the mass is
# their sum, which is what the Qty cell already says the row is.
PARTS = {
    "Cold-core inner shell (foam-shell)": ["cold-core/foam-shell/foam-shell.step"],
    "Cold-core foam cap — top": ["cold-core/foam-cap/foam-cap-top.step"],
    "Cold-core foam cap lid — top": ["cold-core/foam-cap/foam-cap-lid-top.step"],
    "Cold-core foam cap — bottom": ["cold-core/foam-cap/foam-cap-bottom.step"],
    "Cold-core foam cap lid — bottom": ["cold-core/foam-cap/foam-cap-lid-bottom.step"],
    "Copper-plug stack (3 plugs)": [
        "cold-core/copper-plugs/copper-plug-lower.step",
        "cold-core/copper-plugs/copper-plug-middle.step",
        "cold-core/copper-plugs/copper-plug-top.step",
    ],
    "PRV shroud": ["cold-core/prv-shroud/prv-shroud.step"],
    "Flavor reservoir body — left": ["cold-core/reservoir/reservoir-left.step"],
    "Flavor reservoir body — right": ["cold-core/reservoir/reservoir-right.step"],
    "Flavor reservoir cap — left": ["cold-core/reservoir/reservoir-cap-left.step"],
    "Flavor reservoir cap — right": ["cold-core/reservoir/reservoir-cap-right.step"],
    "AC hub plate": ["electronics/ac-hub/ac-hub.step"],
    "Enclosure — front bottom + front top (two pieces)": [
        "enclosure/enclosure/enclosure-front-bottom.step",
        "enclosure/enclosure/enclosure-front-top.step",
    ],
    "Carbonator reed bridge": ["cold-core/reed-bridge/reed-bridge.step"],
    "Enclosure — back bottom + back top (two pieces)": [
        "enclosure/enclosure/enclosure-back-bottom.step",
        "enclosure/enclosure/enclosure-back-top.step",
    ],
    "Drip pan": [
        "enclosure/drip-pan/drip-pan.step",
    ],
    # One part, five off — the same solid five times, which is what the row's Qty
    # says and what its mass has to be: the front column's three and the aft
    # stand's forward two. The sixth cradle carries ONE valve, so it is the
    # family's one-seat part rather than a two-seat plate with a seat empty —
    # an unfilled seat renders a valve that is not in this list.
    "Valve tray — two-valve (5 off)": ["valve-manifold/two-valve-tray/two-valve-tray.step"] * 5,
    "Valve tray — single-valve (1 off)": [
        "valve-manifold/single-valve-tray/single-valve-tray.step"],
    "Faucet touch-flo shell (3-piece: bottom + middle + top)": [
        "faucet/touch-flo-shell/touch-flo-shell-bottom.step",
        "faucet/touch-flo-shell/touch-flo-shell-middle.step",
        "faucet/touch-flo-shell/touch-flo-shell-top.step",
    ],
    "Faucet mounting plate": ["faucet/touch-flo-mounting-plate/touch-flo-mounting-plate.step"],
}

PRINTED = "<!--@printed-->"
_VOLUMES: dict[str, float] = {}


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def volume_cm3(rel):
    """The solid's volume in cm³, memoized — a piece may appear in more than one row."""
    if rel not in _VOLUMES:
        import cadquery as cq

        path = PARTS_DIR / rel
        if not path.exists():
            raise SystemExit(f"_bom_masses: {rel} has no STEP at {path}")
        _VOLUMES[rel] = cq.importers.importStep(str(path)).val().Volume() / 1000.0
    return _VOLUMES[rel]


def material_of(cell):
    """The material cell names a stock; the parenthetical is its colour."""
    name = cell.split("(")[0].strip()
    if name not in MATERIALS:
        raise SystemExit(f"_bom_masses: no density for material {cell!r}")
    return name


def mass_kg(label, material):
    density, _price = MATERIALS[material]
    if label not in PARTS:
        raise SystemExit(
            f"_bom_masses: §7 row {label!r} names no geometry. Add it to PARTS "
            f"(or drop the row) — a printed part with no solid has no mass.")
    return sum(volume_cm3(f) for f in PARTS[label]) * density / 1000.0


def main():
    check = "--check" in sys.argv
    text = BOM.read_text(encoding="utf-8")
    out, drift, seen = [], [], set()
    totals = {}          # material -> kg
    translucent = 0.0

    for line in text.splitlines():
        if PRINTED not in line:
            out.append(line)
            continue
        c = cells(line)
        label, material_cell, stated = c[0], c[2], c[3]
        material = material_of(material_cell)
        kg = mass_kg(label, material)
        seen.add(label)
        totals[material] = totals.get(material, 0.0) + kg
        if "translucent" in material_cell:
            translucent += kg
        cost = kg * MATERIALS[material][1]
        want_mass, want_cost = f"{kg:.3f}", f"${cost:.2f}"
        if stated != want_mass:
            drift.append(f"  {label}: {stated} -> {want_mass} kg")
        c[3] = want_mass
        c[4] = re.sub(r"\$[0-9.,]+", want_cost, c[4], count=1)
        out.append("| " + " | ".join(c) + " |")

    missing = set(PARTS) - seen
    if missing:
        raise SystemExit("_bom_masses: PARTS names rows §7 does not have: "
                         + ", ".join(sorted(missing)))

    grand = sum(totals.values())
    petg, petcf = totals.get("PETG", 0.0), totals.get("PET-CF", 0.0)
    summary = (
        f"By material: PETG ≈ {petg:.2f} kg / ${petg * MATERIALS['PETG'][1]:,.2f} — of which "
        f"the four translucent reservoir parts are ≈ {translucent:.2f} kg / "
        f"${translucent * MATERIALS['PETG'][1]:,.2f} — and PET-CF ≈ {petcf:.2f} kg / "
        f"${petcf * MATERIALS['PET-CF'][1]:,.2f}.")

    body = []
    for line in out:
        if line.startswith("| **Printed parts total**"):
            # Its Qty + Material cells are empty; replace the mass in place rather
            # than rebuilding the row around them.
            stated = cells(line)[3]
            want = f"**~{grand:.2f}**"
            if stated != want:
                drift.append(f"  Printed parts total: {stated} -> {want} kg")
                line = line.replace(stated, want, 1)
        elif line.startswith("By material: PETG"):
            if line != summary:
                drift.append("  By material line")
            line = summary
        body.append(line)

    if check:
        if drift:
            print("_bom_masses: §7 disagrees with the geometry it is derived from:")
            print("\n".join(drift))
            print("\n  fix: tools/cad-venv/bin/python hardware/scripts/_bom_masses.py"
                  "\n  then: tools/cad-venv/bin/python hardware/scripts/_bom_totals.py"
                  "  (carries the new line costs into the section + grand totals)")
            return 1
        print("_bom_masses: §7 matches the geometry ✓")
        return 0

    BOM.write_text("\n".join(body) + "\n", encoding="utf-8")
    print(f"-> bom.md ({len(drift)} rows re-derived, printed total {grand:.2f} kg)")
    for d in drift:
        print(d)
    return 0


if __name__ == "__main__":
    sys.exit(main())
