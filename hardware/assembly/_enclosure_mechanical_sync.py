"""Read current enclosure assembly figures from the canonical appliance facts."""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'hardware' / 'scripts').is_dir())
HW = ROOT / 'hardware'
for path in (ROOT / 'tools', HW / 'scripts', HW / 'manifold-layout',
             HW / 'printed-parts' / 'cadlib', HW / 'printed-parts' / 'cold-core',
             HW / 'printed-parts' / 'enclosure' / 'enclosure'):
    sys.path.insert(0, str(path))

import _facts
import enclosure as enc
import enclosure_assembly as assembly
from _cold_core_interface import outer_shell_y_length
from docgen import substitute_md


def main():
    facts = _facts.read()
    box = facts.box
    outer = box['outer']
    plate = box['collet_plate']
    compressor, condenser = facts.bb('compressor'), facts.bb('condenser+fan')
    bay_width = max(compressor.xmax, condenser.xmax) - min(compressor.xmin, condenser.xmin)
    variables = {
        'BOX_SIZE': f'{outer[1] - outer[0]:.6g} × {outer[3] - outer[2]:.6g} × {outer[5] - outer[4]:.6g} mm',
        'WALL_T': f'{enc.wall:.4g} mm',
        'FLOOR_T': f'{enc.floor_t:.4g} mm',
        'FRONT_WALL': f'{enc.front_wall:.4g} mm',
        'FRONT_TOP_FLANK': f'{enc.front_top_flank_t:.4g} mm',
        'BACK_TOP_FLANK': f'{enc.back_top_flank_t:.4g} mm',
        'CEILING_LANE': f'{enc.appliance_height - enc.floor_t - enc.wall:.4g}',
        'LIP_UNDERWALL': f'{2 * enc.wall:.4g} mm',
        'Y_SEAM': f'{box["y_joint"]:.4g}',
        **enc.y_stack_figures(box['inner']),
        'Z_SEAM_FRONT': f'{box["splits"][0]:.4g}',
        'RAIL_TRAVEL_FRONT': f'{enc._z_rail_travel(box["inner"], box["y_joint"], "front", plate if box["pump_bay"] else None, box["vent_chase"]):.4g} mm',
        'DOCK_TEES': f'{len(plate["holes"])}',
        'APPLIANCE_W': f'{enc.appliance_width:.4g} mm',
        'COMP_BAY_X': f'{bay_width:.0f}',
        # The quarter-yawed floor footprint, beneath the proud cap uprights.
        'CORE_X': f'{outer_shell_y_length:.0f}',
        'SIDE_BAND': f'{enc.side_band_inset:.4g} mm',
        'CORE_HOLD_REACH': f'{enc.core_hold_reach:.4g} mm',
        'REAR_SEAM_CLEAR': f'{enc.rear_seam_clear:.4g} mm',
        'Y_OVERLAP': f'{enc.lip_len:.3g} mm',
        'GROMMET_SQUEEZE': f'{assembly.FLOOR_GROMMET_SQUEEZE:.4g}',
    }
    substitute_md(HERE / 'enclosure-mechanical.md', variables=variables)
    print('-> enclosure-mechanical.md')


if __name__ == '__main__':
    main()
