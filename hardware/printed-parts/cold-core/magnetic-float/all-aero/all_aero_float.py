"""One-piece ASA Aero bench float with an RC62 at its axial midplane.

Frame: open guide bore on Z, flat print bottom at Z=0. The enclosed annular
pocket is filled with the magnet during a native layer pause.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents
            if (p / "hardware/scripts/_rust_part.py").is_file())
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "hardware/scripts"))
if __name__ == '__main__':
    import _rust_part
    _rust_part.start()

sys.path.insert(0, str(HERE.parents[1]))
from _float_interface import (
    diameter, bore_diameter, guide_diameter, magnet_od, magnet_id,
    magnet_thickness, magnet_tolerance, magnet_mass, pocket_od, pocket_id,
    pocket_depth, water_density, design_foam_density, minimum_reserve_lift_g,
    height_increment, layer_height, xy_contour_compensation, xy_hole_compensation,
    annular_area, pocket_volume, minimum_height, height, magnet_midplane,
    magnet_seat, pocket_roof, pause_before_z, rod_axis_from_inner_wall,
    minimum_wall_clearance, maximum_wall_clearance, magnet_above_waterline,
)


def measurements():
    from _cold_core_data import read
    return read("aero-measurements")


def numbers():
    """The Rust scalar recipe in the guide-bore frame."""
    from _cold_core_data import read
    from _materials import linear
    return read("aero-numbers", colors={"aero": list(linear("#EEE4C4")),
                                       "magnet": list(linear("#737D88"))})


def write(output=HERE):
    import _rust_part
    from flute_payload import cut as write_print_payload
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    _rust_part.cut('cold-core', 'all-aero-float', numbers(), output)
    write_print_payload(output / 'float-aero.step', output / 'float-aero.stl')
    info = measurements()
    (output / 'design.json').write_text(json.dumps(info, indent=2) + '\n')
    print(json.dumps({"height_mm": height, "minimum_height_mm": minimum_height,
                      "midplane_mm": magnet_midplane, "buoyancy": info["buoyancy"]}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=HERE)
    args = parser.parse_args()
    write(args.output)
