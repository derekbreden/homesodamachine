"""neoFit ABCVU44 flow-control bulkhead, 1/4" tube — the flow regulator on the
flavor tap. It sits between the water split's flavor run and V-A, throttling the
clean-water feed down to the flavor manifold's low (<10 PSI) working pressure
([`fluid-topology.md`](/hardware/topology/fluid-topology.md) tube segments 1 + 2).

A tee in form: two 1/4" PTC collets in line carrying the water, and a needle
stem standing perpendicular off the body — a brass bulkhead nut, a threaded
barrel and a knurled slotted head. The needle throttles the run; the barrel is
what a panel would clamp. Acetal body, EPDM O-rings, NSF 51 + 61.

External envelope only — the needle, the seat and the O-rings are not modeled.

  PROVISIONAL: the neoFit catalogue lists the flow-control valves by part number
and pack quantity without a dimensioned drawing, so this envelope is scaled off
the manufacturer's product photograph against the one dimension it shares with
the rest of the pack — the 1/4" PTC collet OD. Reconcile against a measured
ABCVU44 as parts come in hand (same note as reference/water-split).

Frame: +X = flow (inlet at −X, outlet at +X), the needle stem standing along +Z
so a hand reaches it from above. Body centre at the origin, both collet faces on
the Z = 0 plane — placed by a pure translation in the enclosure.

Geometry is in the frozen STEP and display payload beside this module.
`frozen-asset.json` records their bytes and source snapshot.
"""

from pathlib import Path

_here = Path(__file__).resolve()
STEP_PATH = _here.parent / "neofit-flow-control.step"
PAYLOAD_PATH = _here.parent / "neofit-flow-control.step.mesh"
ASSET_MANIFEST_PATH = _here.parent / "frozen-asset.json"

COLLET_D = 13.7      # 1/4" PTC collet OD — the pack's shared 1/4" PTC dimension
REACH = 23.0         # collet face from the body centre; run length is twice this
TUBE_D = 6.35        # 1/4" OD LLDPE both ports accept
HUB = 14.0           # central body

NUT_ACROSS_CORNERS = 17.0   # brass bulkhead nut on the stem
NUT_LENGTH = 6.0
BARREL_D, BARREL_LENGTH = 12.0, 9.0     # threaded barrel the panel clamps
KNURL_D, KNURL_LENGTH = 10.0, 12.0      # knurled slotted adjuster head
STEM_REACH = HUB / 2.0 + NUT_LENGTH + BARREL_LENGTH + KNURL_LENGTH


def inlet():
    """The PTC collet the tap-water line from the split's flavor run pushes into:
    (position, outward axis)."""
    return (-REACH, 0.0, 0.0), (-1.0, 0.0, 0.0)


def outlet():
    """The PTC collet feeding V-A's inlet: (position, outward axis)."""
    return (REACH, 0.0, 0.0), (1.0, 0.0, 0.0)


def adjuster():
    """The tip of the knurled adjuster head — the face a screwdriver reaches:
    (position, outward axis). Not a port; the service reach the pack holds open."""
    return (0.0, 0.0, STEM_REACH), (0.0, 0.0, 1.0)


def run_barrel():
    """The round run between the hub and the INLET collet face — `(station, radius, length)`.

    The shape a printed seat can close on. The hub is a box and the stem standing off it is the
    adjuster a hand has to reach, so what is left is the run — and the inlet half of it, because
    the outlet's is the half the tap's own line leaves along.

    `station` is its mid-point and the flow axis through it, in the frame both ports are stated
    in."""
    near, far = HUB / 2.0, REACH
    return (((-(near + far) / 2.0, 0.0, 0.0), (-1.0, 0.0, 0.0)),
            COLLET_D / 2.0, far - near)


def main():
    print("neofit-flow-control")
    print(f"  STEP: {STEP_PATH}")
    print(f"  Display payload: {PAYLOAD_PATH}")


if __name__ == "__main__":
    main()
