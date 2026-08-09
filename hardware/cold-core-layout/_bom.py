"""Every cold-core row of the bill, against the body that realizes it.

`ledger/bom.md` is what the machine costs; this assembly is where those parts stand. `PARTS`
holds the two together — one entry per billed part the cold core carries, naming the text that
finds its row and the bodies `cold_core_assembly` places for it.

THE TABLE IS HELD TO THE BILL FROM BOTH ENDS. An entry whose `bills` text is not in `bom.md`
is a part that has left the bill, and a body placed under a name no entry claims is a body
nobody is buying. `check` reports each, so the table cannot drift from either side.

A part with no body is the reading this file exists for. Wire and fasteners are in the bill and
carry no solid here, so they stand in that list permanently and by name.
"""

from __future__ import annotations

import sys
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
if str(_here.parent) not in sys.path:
    sys.path.insert(0, str(_here.parent))

from _cold_scorecard import Check, verdict                # noqa: E402

BOM = _hw / "ledger" / "bom.md"

# label, the text that finds the row in bom.md, the bodies that realize it.
PARTS = (
    # §2 — the carbonator vessel
    ("316 tube", "OnlineMetals #12498", ("carbonator-tube",)),
    ("endcap plates", "SendCutSend 1/4\"-thick 316 SS circular endcap plate",
     ("endcap-bottom", "endcap-top")),
    ("sparge barb", "LTWFITTING 1/4\" hose barb", ("sparge-barb",)),
    ("vessel elbows", "TAISHER 2PCS 316L SS 90° Barstock Street Elbow",
     ("vessel-elbow-co2-in", "vessel-elbow-carb-water-out",
      "vessel-elbow-water-in", "vessel-elbow-prv")),
    ("sparge stone", "FERRODAY 0.5 µm sintered", ("sparge-stone",)),
    ("silicone stub", "Food-grade silicone tube stub", ("sparge-silicone-stub",)),
    ("PRV", "Control Devices SV-125", ("prv-sv125",)),
    ("PTFE thread tape", "Millrose 70894 Nickel Guard", ()),

    # §3 / §4 / §9 — the collets that land on vessel elbows
    ("PTC collets", "John Guest PP010822E",
     ("collet-co2-in", "collet-carb-water-out", "collet-water-in")),

    # §5 — refrigeration
    ("evaporator coil", "GOORY 1/4\" OD × 50 ft ACR copper coil",
     ("evap-coil", "evap-tail-inlet", "evap-tail-outlet")),
    ("tank probe", "TIEXYE DS18B20", ("probe-tank-ds18b20",)),
    ("coil probe", "DS18S20+ TO-92", ("probe-coil-ds18s20",)),

    # §6 — what fills the shell
    ("pour-in-place foam", "closed-cell pour-in-place PU foam", ()),
    ("foil tape", "3M 425 aluminum foil tape", ()),

    # §7 — the printed parts
    ("foam shell", "Cold-core inner shell (foam-shell)", ("foam-shell",)),
    ("foam cap top", "Cold-core foam cap — top", ("foam-cap-top",)),
    ("foam cap lid top", "Cold-core foam cap lid — top", ("foam-cap-lid-top",)),
    ("foam cap bottom", "Cold-core foam cap — bottom", ("foam-cap-bottom",)),
    ("foam cap lid bottom", "Cold-core foam cap lid — bottom", ("foam-cap-lid-bottom",)),
    ("copper plugs", "Copper-plug stack (3 plugs)",
     ("copper-plug-lower", "copper-plug-middle", "copper-plug-top")),
    ("PRV shroud", "PRV shroud", ("prv-shroud",)),
    ("reservoir body L", "Flavor reservoir body — left", ("reservoir-b",)),
    ("reservoir body R", "Flavor reservoir body — right", ("reservoir-a",)),
    ("reservoir cap L", "Flavor reservoir cap — left", ("reservoir-b-cap",)),
    ("reservoir cap R", "Flavor reservoir cap — right", ("reservoir-a-cap",)),
    ("reed bridge", "Carbonator reed bridge", ("reed-bridge",)),

    # §8 — the pockets' own hardware
    ("floor bulkheads", "PureSec 1/4\" RO push-to-connect 90° elbow bulkhead",
     ("bulkhead-reservoir-a", "bulkhead-reservoir-b")),
    ("bulkhead seals", "uxcell silicone flat washer",
     ("bulkhead-seal-a", "bulkhead-seal-b")),

    # §12 — level sensing
    ("floats", "YXQ 45 mm SS float switch", ("float-carb", "float-a", "float-b")),
    ("reed columns", "Pre-soldered reed-and-wire column", ()),
    ("float rods", "Tandefio 1/8\" × 12\" 316 SS round rod",
     ("float-rod-carb", "float-rod-a", "float-rod-b")),
    ("reeds", "Gebildet reed switches",
     ("reed-carb-1", "reed-carb-2",
      "reed-a-1", "reed-a-2", "reed-a-3", "reed-a-4",
      "reed-b-1", "reed-b-2", "reed-b-3", "reed-b-4")),

    # §13 — attach hardware and the cap vents
    ("heat-set inserts", "ruthex M3 Threaded Inserts", ()),
    ("cap clamp screws", "BNUOK M3 × 25 mm DIN 912", ()),
    ("reservoir cap screws", "BNUOK M3 × 12 mm DIN 912 socket head cap, 304 stainless", ()),
    ("vent membranes", "LVDALAB PTFE Membrane Filter",
     ("vent-membrane-a", "vent-membrane-b")),
)

# A length of tube is stock cut to fit, billed by the foot in §3 and §11, so a drawn line is
# not a part any row here claims.
UNBILLED_PREFIXES = ("line-",)


def _bill_text() -> str:
    return BOM.read_text(encoding="utf-8")


def check(placed: dict) -> Check:
    """Every billed cold-core part against the bodies that realize it."""
    bill = _bill_text()
    claimed = set()
    missing_row, no_body, absent = [], [], []
    for label, bills, bodies in PARTS:
        if bills not in bill:
            missing_row.append(f"{label}: no row in bom.md matching \"{bills}\"")
        if not bodies:
            no_body.append(f"{label} — billed, no solid here (\"{bills}\")")
            continue
        gone = [b for b in bodies if b not in placed]
        claimed.update(bodies)
        if gone:
            absent.append(f"{label}: {', '.join(gone)} not placed")

    unclaimed = sorted(n for n in placed
                       if n not in claimed and not n.startswith(UNBILLED_PREFIXES))
    covered = sum(1 for _l, _b, bodies in PARTS
                  if bodies and all(b in placed for b in bodies))
    detail = missing_row + absent + no_body
    detail += [f"placed, unbilled: {n}" for n in unclaimed]
    return Check("bom-covered", "Every billed cold-core part has a body here", "goal",
                 verdict(not detail), f"{covered}/{len(PARTS)}", "a body per billed part",
                 detail)


def report(placed: dict) -> None:
    c = check(placed)
    print(f"  bom coverage    {c.value} billed parts carry a body")
    for line in c.detail:
        print(f"    {line}")
