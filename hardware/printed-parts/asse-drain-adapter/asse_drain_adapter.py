"""TPU vent cup with an aft-facing 4 mm drain socket.

The scanned ASSE's exposed vent stem enters the vertical cup. A printed
quarter turn carries its open drain to a horizontal socket on native -X.
Both sockets retain a separate four-inch tie land. Native +Z points into
its vent mouth; the printable frame tips both bores upward at 45 degrees.
"""
from pathlib import Path
import math
import sys

HERE = Path(__file__).resolve().parent
HARDWARE = HERE.parents[1]
sys.path.insert(0, str(HARDWARE / "scripts"))
sys.path.insert(0, str(HARDWARE / "reference/multiplex-asse1022"))

if __name__ == '__main__':
    import _rust_part
    _rust_part.start()

BARB_BORE = 6.10
TUBE_BORE = 3.80
TUBE_DEPTH = 14.0
REDUCER_LENGTH = 5.50  # Open taper below the vent tip, before the turn.
MIN_WALL = 3.45  # Shared relaxed radial minimum, under both tie lands.
GROOVE_DEPTH = .50
BARB_OD = BARB_BORE + 2 * (MIN_WALL + GROOVE_DEPTH)
TUBE_OD = TUBE_BORE + 2 * (MIN_WALL + GROOVE_DEPTH)
GROOVE_FLAT = 2.80  # Existing 0.1-inch / 2.54 mm-wide four-inch ties.
GROOVE_RAMP = 1.0  # At most .5 mm radial growth / mm build rise.
BARB_TIE_Z = 5.5
INSTALLED_REACH = 8.6  # Below the scanned vent hex, on the exposed stem.


ELBOW_REACH = 25.4
ELBOW_R = 4.05
TURN_START_Z = -REDUCER_LENGTH
SOCKET_DROP = -TURN_START_Z+ELBOW_R


def tube_mouth(vent_tip):
    x, y, z = vent_tip
    return (x-ELBOW_REACH,y,z-SOCKET_DROP)


def numbers(*, installed=False):
    """The authored bores, stock and tie lands, independent of native solids."""
    from _material_base import M_TPU_BLACK
    from _materials import linear
    if installed:
        import multiplex_asse1022 as bfp
    barb = bfp.VENT_D if installed else BARB_BORE
    tube = 4. if installed else TUBE_BORE
    rb = math.sqrt(BARB_OD**2+barb**2-BARB_BORE**2)/2.
    rt = math.sqrt(TUBE_OD**2+tube**2-TUBE_BORE**2)/2.
    flat_z = -(rb+SOCKET_DROP+rt)/math.sqrt(2.)+.6
    return dict(barb_bore=barb,tube_bore=tube,barb_radius=rb,tube_radius=rt,
        installed_reach=INSTALLED_REACH,socket_drop=SOCKET_DROP,
        elbow_reach=ELBOW_REACH,elbow_radius=ELBOW_R,turn_start_z=TURN_START_Z,
        reducer_length=REDUCER_LENGTH,groove_depth=GROOVE_DEPTH,
        groove_flat=GROOVE_FLAT,groove_ramp=GROOVE_RAMP,
        groove_centres=(INSTALLED_REACH-BARB_TIE_Z,ELBOW_REACH-6.),
        flat_z=flat_z,
        print_shift=((ELBOW_REACH+SOCKET_DROP+rt-rb-INSTALLED_REACH)/(2*math.sqrt(2.)),0.,-flat_z),
        color=list(linear(M_TPU_BLACK)))


def _readme(output, volume):
    sys.path.insert(0, str(HARDWARE.parent / "tools"))
    from docgen import substitute_md
    substitute_md(output / "README.md", variables={
        "BARB_BORE": f"{BARB_BORE:.2f}", "BARB_DEPTH": f"{INSTALLED_REACH:g}",
        "TUBE_BORE": f"{TUBE_BORE:.2f}", "TUBE_DEPTH": f"{TUBE_DEPTH:g}",
        "BARB_OD": f"{BARB_OD:g}", "TUBE_OD": f"{TUBE_OD:g}",
        "MIN_WALL": f"{MIN_WALL:.2f}",
        "SOCKET_DROP": f"{SOCKET_DROP:.2f}", "REDUCER_LENGTH": f"{REDUCER_LENGTH:.2f}",
        "VOLUME": f"{volume/1000:.3f}",
    })


def main(output=None):
    import _rust_part
    _rust_part.start()
    out = HERE if output is None else Path(output)
    out.mkdir(parents=True, exist_ok=True)
    result = _rust_part.cut('tooling','asse-drain-adapter',numbers(),out)
    _readme(out, result['bodies'][0]['volume'])
    print(f"asse-drain-adapter: {result['bodies'][0]['volume']/1000:.3f} cm3")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    main(args.output)
