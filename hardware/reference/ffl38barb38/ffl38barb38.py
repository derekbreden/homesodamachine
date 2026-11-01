"""brewhardware FFL38BARB38 swivel flare adapter, 3/8" female flare × 3/8" OD
hose barb — the single piece that turns the ASSE 1022's male flare outlet into a
barb for the JoyTube silicone hose running to the SeaFlo pump suction
([`ledger/bom.md`](/hardware/ledger/bom.md) §3).

External envelope only — a chrome-plated brass swivel nut (a wrench hex, which
spins on the barb stem and never touches water) and a 304 SS barb stem with its
ridges as stacked cones. The flare seal is flat-faced, so no tape: the nut pulls
the ASSE 1022's flare nose against the adapter's seat.

Frame: +X = flow axis, the swivel-nut face at X = 0 — it lands flat on the ASSE
1022's outlet face, so the two mate at that plane. Centered on Y and Z.

Geometry is in the frozen STEP and display payload beside this module.
`frozen-asset.json` records their bytes and source snapshot.
"""

from pathlib import Path

_HERE = Path(__file__).resolve().parent
STEP_PATH = _HERE / "ffl38barb38.step"
PAYLOAD_PATH = _HERE / "ffl38barb38.step.mesh"
ASSET_MANIFEST_PATH = _HERE / "frozen-asset.json"

NUT_ACROSS_CORNERS = 22.0   # 3/4" swivel nut hex (19.05 across flats)
NUT_LENGTH = 14.0           # nut body along the flow axis — the flare it draws up
NUT_BORE_D = 15.88          # 3/8" flare thread major Ø — bored through, so the ASSE
                            # 1022's flare nose occupies the nut rather than its metal
STEM_D = 11.0               # barb stem shoulder Ø, between nut and ridges
STEM_LENGTH = 6.0
BARB_D = 9.53               # 3/8" hose barb ridge Ø
BARB_ROOT_D = 7.9           # between ridges
BARB_RIDGES = 3
RIDGE_PITCH = 5.5
HOSE_ID = 9.53              # the 3/8" ID silicone hose it takes
LENGTH = NUT_LENGTH + STEM_LENGTH + BARB_RIDGES * RIDGE_PITCH


def flare_face():
    """The swivel nut's seating face: (position, outward axis). It lands flat on
    the ASSE 1022's flare outlet, so this face and that one are the same plane."""
    return (0.0, 0.0, 0.0), (-1.0, 0.0, 0.0)


def barb_tip():
    """The barb tip the silicone hose slips over: (position, outward axis)."""
    return (LENGTH, 0.0, 0.0), (1.0, 0.0, 0.0)


def main():
    print("brewhardware FFL38BARB38 3/8\" FFL × 3/8\" hose-barb adapter")
    print(f"  Nut {NUT_ACROSS_CORNERS} across corners × {NUT_LENGTH:g}; "
          f"{BARB_RIDGES} ridges Ø{BARB_D} at {RIDGE_PITCH:g} pitch; total {LENGTH:g} mm")
    print(f"  STEP: {STEP_PATH}")
    print(f"  Display payload: {PAYLOAD_PATH}")


if __name__ == "__main__":
    main()
