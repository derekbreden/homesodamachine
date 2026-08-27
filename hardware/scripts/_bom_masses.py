#!/usr/bin/env python3
"""Compute bom.md §7's printed-part masses from each part's own CAD solid and
write them into the Mass + $ cells — so "derived" is a property of the table
rather than a claim about it.

Third of the three ledger drivers: _bom_sync.py owns the geometry-derived
QUANTITY markers, _bom_totals.py owns the COST rollups, this owns the MASS
column of §7 and the $ that follows from it.

    mass = Σ(what a slice of the solid lays) × density   $ = mass × $/kg

WHAT A PRINT LAYS IS NOT THE SOLID. Two wall loops per face and 15 % grid between
them, on a box whose pieces are mostly air by volume: the front-top's 1379 cm³ of
geometry comes off the plate as 456. So the mass here is SHELL PLUS INFILL, taken
off the part's own volume and area — both read from the one STEP — at the settings
of the slice that part ships on. PROFILES below holds those settings and states
the residual against every slice that has been measured.

Every `<!--@printed-->` row names its geometry in PARTS below and its print
configuration in GROUP_OF. A row with no entry, an entry naming a file that is not
there, a row in neither list, or a material with no density is an ERROR, not a
skipped row — a printed part cannot enter the table without the solid that gives
it a mass and the profile that says how much of it is laid.

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

# Volume and area are functions of the solid's bytes, and are held under a hash
# of them.
_VOL_CACHE = REPO / ".cache" / "bom-volumes.json"

# Density (g/cm³) and price ($/kg), both as §7's own prose states them. Colour
# changes what a part looks like, not what it costs, so translucent PETG is PETG.
MATERIALS = {
    "PETG": (1.27, 11.20),
    "PET-GF": (1.43, 25.02),
}

# WHAT A PRINT LAYS, by print configuration — (shell per face mm, line width mm,
# sparse infill fraction). Five configurations, one per plate the build actually
# runs, each read off a committed slice named beside it. The same five
# `_machine_time.py` prices in hours, off the GROUP_OF list below.
#
#     wall = 2V/A                        the mean wall the solid presents
#     laid = min(2 × shell, wall) + infill × whatever is left of that wall
#
# A wall thicker than its own two shells is loops around sparse fill, which is the
# box. A wall THINNER than them is all loops, and loops are whole beads: what does
# not divide by the line width is gap fill, and gap fill lays about GAP of it.
#
# Against the two slices that report both grams and geometry, the model reads:
#
#   enclosure-front-top, PET-GF, 0.24 layer   213.06 m = 512.5 cm³   model 456.4 (−11 %)
#   cold-core foam shell, 0.8 nozzle          1142.47 g = 899.6 cm³  model 886.4 (−1.5 %)
#
# EACH RESIDUAL BELONGS TO THE PLATE BESIDE IT, and validates the formula rather than the part:
# `laid` is a function of the solid and the profile, so a residual measured on one solid holds
# for any other run on the same profile. The shell's plate ran PETG and its grams are divided
# by PETG's density to reach that cm³; the shell ships in PET-GF now, which changes what the
# volume weighs and not what the volume is.
#
# THE MODEL IS THE PART AND THE SLICE IS THE PLATE. Supports, brim and purge are
# filament off the same spool and are not here — the front-top's tree supports are
# most of that 11 %. Nothing is fitted to close it, because nothing measures it
# but the one slice.
PROFILES = {
    # enclosure/print-log.md — 0.4 nozzle, `wall_loops` 2 classic, outer 0.42 +
    # inner 0.45, 15 % grid. Every exterior piece ships on it.
    "ext":   (0.87, 0.45, 0.15),
    # foam-shell/print-log.md — 0.8 nozzle, `wall_loops` 2, `line_width` 0.82, 15 % grid. The
    # cold core's five foam bodies ship on it in PET-GF15, on the 0.8 mm tungsten carbide.
    "bulk":  (1.64, 0.82, 0.15),
    # reservoir/print-log.md — 0.6 nozzle, `wall_loops` 6 arachne, 0.60, and
    # `sparse_infill_density` 100 %: a syrup-tight wall is solid by the time it closes,
    # so these four rows come out at their geometry and the model changes nothing.
    "tight": (3.60, 0.60, 1.00),
    # faucet-shell/print-log.md attempt 20 — 0.6 nozzle, `wall_loops` 6, 0.62, 100 %.
    "petgf": (3.72, 0.62, 1.00),
    # No slice of its own. A part this small is nearly all perimeter whatever it is
    # sliced at, so it carries the exterior's figures and lands near solid anyway.
    "small": (0.87, 0.45, 0.15),
}

#: What gap fill lays in a wall too thin to tile with whole beads, as a fraction of
#: the remainder — the one figure here fitted rather than read off a profile. The
#: cold-core shell is the slice that sets it: 899.6 cm³ of filament against a 2.33 mm
#: mean wall holding two 0.82 beads with 0.69 mm over.
GAP = 0.5

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
    # (`enclosure.build_pump_cartridge`), and the cap that closes on both heads comes off it as a
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
    # strips. Its own row because it is its own plate — and it carries the flow meter's two anchors and
    # three of the ceiling's ribs, which are the mass that left the row above.
    "Enclosure — ceiling panel": ["enclosure/ceiling-panel/ceiling-panel.step"],
    # THE ENCLOSURE DISPLAY'S OWN PIECE OF THE BOX, printed apart from the piece it fills: the border that
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
    "Faucet shell (2-piece: base + tip)": [
        "faucet/faucet-shell/faucet-shell-base.step",
        "faucet/faucet-shell/faucet-shell-tip.step",
    ],
    # The faucet display's face plate is its own row and not the shell's: it
    # is a separate print, screwed on, and the customer sees it as its own
    # surface across the seam.
    "Faucet display cover plate": [
        "faucet/faucet-display-cover/faucet-display-cover.step",
    ],
    "Above-counter plate": ["faucet/above-counter-plate/above-counter-plate.step"],
}

# §7 row-name fragment -> the PROFILES key that row ships on. Every row must match
# exactly one, here and in `_machine_time.py`, which imports this list to price the
# same rows in hours: a printed part cannot enter §7 without saying what plate it
# comes off.
GROUP_OF = [
    ("Cold-core inner shell",       "bulk"),
    ("Cold-core foam cap",          "bulk"),
    ("Enclosure —",                 "ext"),
    ("Display cover plate",         "ext"),
    ("Flavor reservoir",            "tight"),
    ("Faucet shell",                "petgf"),
    ("Faucet display cover plate",  "petgf"),
    ("Above-counter plate",         "petgf"),
    ("Copper-plug stack",           "small"),
    ("PRV shroud",                  "small"),
    ("Carbonator reed bridge",      "small"),
    ("ASSE drip pan",               "small"),
    ("Fuse clamp",                  "small"),
    ("Bulkhead ring",               "small"),
    ("Tube collar",                 "small"),
    ("Nameplate",                   "small"),
]

PRINTED = "<!--@printed-->"
_SOLIDS: dict[str, tuple] = {}


def _held():
    """What the cache holds: sha256 of a STEP -> [volume cm³, area cm²]."""
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


def measure(rel):
    """(volume cm³, area cm²) for the solid, memoized — a piece may appear in more
    than one row. AREA IS THE SECOND HALF OF A MASS: `laid_cm3` needs the surface
    the wall loops run around as much as the volume they enclose, and one import
    answers both. An entry the cache holds as a bare volume is a reading from
    before the area was wanted, and is re-measured rather than half-believed."""
    if rel not in _SOLIDS:
        path = PARTS_DIR / rel
        if not path.exists():
            sys.exit(f"_bom_masses: {rel} has no STEP at {path}")
        key = hashlib.sha256(path.read_bytes()).hexdigest()
        held = _held()
        got = held.get(key)
        if isinstance(got, list) and len(got) == 2:
            _SOLIDS[rel] = tuple(got)
        else:
            from _cadq_export import import_step

            solid = import_step(str(path)).val()
            _SOLIDS[rel] = (solid.Volume() / 1000.0, solid.Area() / 100.0)
            held[key] = list(_SOLIDS[rel])
            _hold(held)
    return _SOLIDS[rel]


def laid_cm3(volume, area, group):
    """The filament a print of this solid lays, in cm³ — the block at PROFILES.

    `volume` cm³ and `area` cm² are one solid's, so 2V/A is its mean wall in cm and
    ×10 is the same wall in mm, which is the unit a line width is in."""
    shell, width, infill = PROFILES[group]
    wall = 20.0 * volume / area
    both = 2.0 * shell
    if wall > both:
        laid, density = both, infill            # loops around sparse fill
    else:
        laid, density = (wall // width) * width, max(infill, GAP)   # all loops, and the gap
    return volume * (laid + density * (wall - laid)) / wall


def group_of(label):
    """The PROFILES key §7's row `label` prints on."""
    hits = [g for frag, g in GROUP_OF if frag in label]
    if len(hits) != 1:
        sys.exit(
            f"_bom_masses: §7 row {label!r} matches {len(hits)} print configurations. "
            f"Give it exactly one entry in GROUP_OF — a printed part cannot be priced "
            f"without the plate it comes off.")
    return hits[0]


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
    group = group_of(label)
    return sum(laid_cm3(*measure(f), group) for f in PARTS[label]) * density / 1000.0


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
    petg, petgf = totals.get("PETG", 0.0), totals.get("PET-GF", 0.0)
    summary = (
        f"By material: PETG ≈ {petg:.2f} kg / ${petg * MATERIALS['PETG'][1]:,.2f} — of which "
        f"the four translucent reservoir parts are ≈ {translucent:.2f} kg / "
        f"${translucent * MATERIALS['PETG'][1]:,.2f} — and PET-GF ≈ {petgf:.2f} kg / "
        f"${petgf * MATERIALS['PET-GF'][1]:,.2f}.")

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
            print("_bom_masses: §7 disagrees with the solids it is derived from:")
            print("\n".join(drift))
            print("\n  fix: tools/cad-venv/bin/python hardware/scripts/_bom_masses.py"
                  "\n  then: tools/cad-venv/bin/python hardware/scripts/_bom_totals.py"
                  "  (carries the new line costs into the section + grand totals)")
            return 1
        print("_bom_masses: §7 matches the solids ✓")
        return 0

    BOM.write_text("\n".join(body) + "\n", encoding="utf-8")
    print(f"-> bom.md ({len(drift)} rows re-derived, printed total {grand:.2f} kg)")
    for d in drift:
        print(d)
    return 0


if __name__ == "__main__":
    sys.exit(main())
