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
import hashlib
import json
import re
import sys
from pathlib import Path

REPO = next(p for p in Path(__file__).resolve().parents if (p / "hardware").is_dir())
sys.path.insert(0, str(REPO / "tools"))
from docgen import cells                                        # noqa: E402

BOM = REPO / "hardware" / "ledger" / "bom.md"
PARTS_DIR = REPO / "hardware" / "printed-parts"

# A volume is a function of the solid's bytes, and is held under a hash of them.
_VOL_CACHE = REPO / ".cache" / "bom-volumes.json"

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
        "cold-core/copper-plugs/copper-plug-west.step",
        "cold-core/copper-plugs/copper-plug-port.step",
    ],
    "PRV shroud": ["cold-core/prv-shroud/prv-shroud.step"],
    "Flavor reservoir body — left": ["cold-core/reservoir/reservoir-left.step"],
    "Flavor reservoir body — right": ["cold-core/reservoir/reservoir-right.step"],
    "Flavor reservoir cap — left": ["cold-core/reservoir/reservoir-cap-left.step"],
    "Flavor reservoir cap — right": ["cold-core/reservoir/reservoir-cap-right.step"],
    "Enclosure — front bottom + front top (two quadrants)": [
        "enclosure/enclosure/enclosure-front-bottom.step",
        "enclosure/enclosure/enclosure-front-top.step",
    ],
    # THE FIFTH PIECE OF THE BOX, and the one that leaves it loaded: the front wall's flat
    # span and the block behind it that both pumps stand in come off the plate as one solid
    # (`enclosure.build_cartridge`), and the cap that closes on both heads comes off it as a
    # second (`enclosure.build_pump_cap`). ONE ROW FOR THE PAIR, because they are screwed
    # together on the bench and ride as one. A pump tray is the pump cartridge's own material,
    # so nothing stands under a pump that ships on its own — the valve trays' bargain below.
    "Enclosure — pump cartridge + cap (one set)": [
        "enclosure/enclosure/enclosure-pump-cartridge.step",
        "enclosure/enclosure/enclosure-pump-cap.step",
    ],
    "Carbonator reed bridge": ["cold-core/reed-bridge/reed-bridge.step"],
    "Enclosure — back bottom + back top (two quadrants)": [
        "enclosure/enclosure/enclosure-back-bottom.step",
        "enclosure/enclosure/enclosure-back-top.step",
    ],
    # BACK-TOP'S CEILING, printed apart from the piece it closes. That piece prints mouth-down on
    # its seam rim, so a ceiling drawn in it is a slab laid 195 mm up over the open service bay;
    # this is that slab, flat on the bed and slid into a dado down each of back-top's two side
    # strips. Its own row because it is its own plate — and it carries the meter's two saddles and
    # three of the ceiling's ribs, which are the mass that left the row above.
    "Enclosure — ceiling panel": ["enclosure/ceiling-panel/ceiling-panel.step"],
    # THE DISPLAY'S OWN PIECE OF THE BOX, printed apart from the piece it fills: the border that
    # drops into the 45° facet's inset and laps the glass all round. It is the display's whole
    # fastening, so it ships on every unit the screen does.
    "Display cover plate": ["enclosure/display-cover/display-cover.step"],
    # ONE ROW, FIVE CHIPS AND THE FIVE WORDS THEY CARRY — one file per crossing the +Y wall of
    # back-top passes a tube through, and each holds both bodies: the chip, and the word standing in the
    # recess cut into it. Two spools go on the plate and the row prices both.
    "Bulkhead ring — one per +Y-wall crossing": [
        "enclosure/bulkhead-ring/bulkhead-ring-water.step",
        "enclosure/bulkhead-ring/bulkhead-ring-carb.step",
        "enclosure/bulkhead-ring/bulkhead-ring-flavor-a.step",
        "enclosure/bulkhead-ring/bulkhead-ring-flavor-b.step",
        "enclosure/bulkhead-ring/bulkhead-ring-co2.step",
    ],
    # AND ONE COLLAR PER CHIP, on the same five stations and off the same two spools — the tube
    # carrying the word the ring it goes through carries. Three go on at the umbilical bench and
    # two in the install kit, and the row prices all five.
    "Tube collar — one per +Y-wall crossing": [
        "faucet/tube-collar/tube-collar-water.step",
        "faucet/tube-collar/tube-collar-carb.step",
        "faucet/tube-collar/tube-collar-flavor-a.step",
        "faucet/tube-collar/tube-collar-flavor-b.step",
        "faucet/tube-collar/tube-collar-co2.step",
    ],
    # ONE ROW AND ONE FILE, holding both bodies the way a bulkhead ring's does: the plate, and the
    # lettering standing in the recess cut into it. The file is unit 0001's; every unit's is the
    # same plate with four different figures in it, so one mass prices the run.
    "Nameplate — one per unit, serialized": [
        "enclosure/nameplate/nameplate-001.step",
    ],
    "ASSE drip pan": [
        "enclosure/asse-drip-pan/asse-drip-pan.step",
    ],
    "Fuse clamp": ["refrigeration/fuse-clamp/fuse-clamp.step"],
    # NO VALVE TRAY ROW AND NO PUMP TRAY ROW. Every valve in the machine stands in four bosses
    # (`valve_seat`), and every set of them is printed into a part already billed: three on the
    # cold core's cap lid (`_cold_core_interface.cap_cradles`) and eight on the two valve trays
    # (`enclosure._valve_trays`), which are `enclosure-front-top`'s own material. So a valve's
    # seat is priced as part of the piece that carries it, and nothing stands under one that
    # ships on its own.
    "Faucet shell (3-piece: bottom + middle + top)": [
        "faucet/faucet-shell/faucet-shell-bottom.step",
        "faucet/faucet-shell/faucet-shell-middle.step",
        "faucet/faucet-shell/faucet-shell-top.step",
    ],
    "Above-counter plate": ["faucet/above-counter-plate/above-counter-plate.step"],
}

PRINTED = "<!--@printed-->"
_VOLUMES: dict[str, float] = {}


def _held():
    """What the cache holds: sha256 of a STEP -> its volume in cm³."""
    try:
        return json.loads(_VOL_CACHE.read_text())
    except (OSError, ValueError):
        return {}


def _hold(held):
    """Keep what the cache learned, where there is somewhere to keep it.

    A SANDBOX REACHES THE WORKSPACE'S OWN `.cache`. Ninety-five genrule commands symlink it in
    — `ln -sfn $HSM_WORKSPACE/.cache .cache`, `//:bom-masses` among them — and it is a declared
    input of none of them. So this is one mutable store shared by every sandboxed action and
    named in no action key, and an entry in it is named by the sha256 of the STEP it was
    measured from. `//:pysrc` stages this file without the symlink, and there the write is the
    miss the `except` below carries."""
    try:
        _VOL_CACHE.parent.mkdir(parents=True, exist_ok=True)
        _VOL_CACHE.write_text(json.dumps(held, indent=1, sort_keys=True))
    except OSError:
        pass


def volume_cm3(rel):
    """The solid's volume in cm³, memoized — a piece may appear in more than one row."""
    if rel not in _VOLUMES:
        path = PARTS_DIR / rel
        if not path.exists():
            sys.exit(f"_bom_masses: {rel} has no STEP at {path}")
        key = hashlib.sha256(path.read_bytes()).hexdigest()
        held = _held()
        if key in held:
            _VOLUMES[rel] = held[key]
        else:
            from _cadq_export import import_step

            _VOLUMES[rel] = import_step(str(path)).val().Volume() / 1000.0
            held[key] = _VOLUMES[rel]
            _hold(held)
    return _VOLUMES[rel]


def material_of(cell):
    """The material cell names a stock; the parenthetical is its colour."""
    name = cell.split("(")[0].strip()
    if name not in MATERIALS:
        sys.exit(f"_bom_masses: no density for material {cell!r}")
    return name


def mass_kg(label, material):
    density, _price = MATERIALS[material]
    if label not in PARTS:
        sys.exit(
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
        sys.exit("_bom_masses: PARTS names rows §7 does not have: "
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
