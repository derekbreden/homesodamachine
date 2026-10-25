"""Read the enclosure README's dimensions from canonical appliance facts."""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'hardware' / 'scripts').is_dir())
HW = ROOT / 'hardware'
for path in (ROOT / 'tools', HW / 'scripts', HW / 'manifold-layout',
             HW / 'printed-parts' / 'cadlib', HW / 'printed-parts' / 'cold-core',
             HERE / 'enclosure', HW / 'reference' / 'condenser-block'):
    sys.path.insert(0, str(path))

import _facts
import condenser_block as condenser
import enclosure
import enclosure_assembly as assembly  # Declares the placement source this reader follows.
from _cold_core_interface import foam_shell_outer_height, outer_shell_x_length, outer_shell_y_length
from docgen import substitute_md


facts = _facts.read()
box = facts.box
outer = box['outer']
compressor, block = facts.bb('compressor'), facts.bb('condenser+fan')
APPLIANCE_W = outer[1] - outer[0]
APPLIANCE_D = outer[3] - outer[2]
APPLIANCE_H = outer[5] - outer[4]


def main():
    # The front corner stations identify the floor footprint independently of
    # cap passages and equipment standing proud above it.
    core_front = min(y - radius for _x, y, radius in box['core_stops'])
    variables = {
        'FOAM_SHELL_X': f'{outer_shell_x_length:.4g}',
        'FOAM_SHELL_Y': f'{outer_shell_y_length:.4g}',
        'FOAM_SHELL_Z': f'{foam_shell_outer_height:.4g}',
        'APPLIANCE_WIDTH': f'{APPLIANCE_W:.4g} mm',
        'APPLIANCE_DEPTH': f'{APPLIANCE_D:.4g} mm',
        'APPLIANCE_HEIGHT': f'{APPLIANCE_H:.4g} mm',
        'WALL_STANDOFF': f'{enclosure.side_band_inset:.4g}',
        'COMP_BAY_W': f'{max(compressor.xmax, block.xmax) - min(compressor.xmin, block.xmin):.4g}',
        'COMP_BAY_D': f'{max(compressor.ymax, block.ymax) - min(compressor.ymin, block.ymin):.4g}',
        'COMP_BAY_TOP': f'{max(compressor.zmax, block.zmax):.4g}',
        'COMP_BAY_STEP': f'{abs(compressor.zmax - block.zmax):.4g}',
        'COMPRESSOR_ROOF': f'{compressor.zmax:.4g}',
        'MATE_X': f'{compressor.xmax:.4g}',
        'CONDENSER_ACROSS': f'{condenser.AIRFLOW:.4g}',
        'CONDENSER_LONG': f'{condenser.FACE_A:.4g}',
        'CONDENSER_STANDING': f'{condenser.FACE_B:.4g}',
        'CONDENSER_LIFT': f'{block.zmin:.4g}',
        'CORE_FRONT_Y': f'{core_front:.4g}',
        'CORE_CROWN': f'{facts.faces["foam-assembly.cap"]:.4g}',
        'BACK_Z_SEAM': f'{box["splits"][1]:.4g}',
        'BACK_BOTTOM_H': f'{facts.pieces["back-bottom"]["box"][5] - facts.pieces["back-bottom"]["box"][2]:.4g}',
        'BED_Z': f'{enclosure.H2C_Z:.4g}',
    }
    substitute_md(HERE / 'README.md', variables=variables)
    print('-> README.md')


if __name__ == '__main__':
    main()
