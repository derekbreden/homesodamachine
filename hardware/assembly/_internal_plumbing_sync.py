"""Read current pump-manifold preparation figures without building an appliance."""

import math
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
from _enclosure_datums import load as _enclosure_numbers
enc = _enclosure_numbers()
from _cadq_export import note_read
note_read(HW / 'manifold-layout/enclosure_assembly.py')
for source in _facts.sources():
    if Path(source).suffix in ('.py', '.rs', '.json', '.toml', '.lock', '.yaml', '.yml'):
        note_read(ROOT / source)
import manifold_layout as manifold
import above_core_routes
from docgen import substitute_md


def main():
    facts = _facts.read()
    box = facts.box
    returns = {tee: manifold.lower_link_length(connection)
               for connection, tee in manifold.LOWER_CONNECTIONS.items()}
    elbows = manifold.pump_plumbing()['Y-C']['return']['elbows']
    reservoir_a = above_core_routes.reservoir_a_route_specs()
    reservoir_a_lengths = {
        name: sum(math.dist(*segment['points_mm']) if segment['kind'] == 'line'
                  else segment['radius_mm'] * segment['angle_rad']
                  for segment in row['segments'])
        for name, row in reservoir_a.items()
    }
    variables = {
        'MANIFOLD_TEES': f'{len(manifold.PURCHASED_TEES)}',
        'DOCK_TEE_STROKE': f'{manifold._returns.tee.BRANCH_COLLET_TRAVEL:.3g} mm',
        'DOCK_TEE_INSERTION': f'{manifold._returns.RUN_INSERTION:.4g} mm',
        'DOCK_VALVE_INSERTION': f'{manifold._returns.VALVE_INSERTION_NOMINAL:.4g} mm',
        'DOCK_FORE_LINK': f'{manifold.FORE_STUB_EXPOSED:.6g} mm',
        'DOCK_UPPER_TAIL': f'{manifold.FORE_STUB_EXPOSED + manifold._returns.RUN_INSERTION + manifold._returns.VALVE_INSERTION_NOMINAL:.6g} mm',
        'DOCK_RETURN_INNER': f'{returns["Y-C"]:.4g} mm',
        'DOCK_RETURN_OUTER': f'{returns["Y-D"]:.4g} mm',
        'DOCK_ELBOW_SOCKET': f'{manifold._returns.elbow.SOCKET_INSERTION:.4g} mm',
        'DOCK_TEE_ELBOW_STEM': f'{elbows[0]["stem"]:.4g} mm',
        'DOCK_VALVE_ELBOW_STEM': f'{elbows[1]["stem"]:.4g} mm',
        'DOCK_VALVE_ELBOW_SHOWING': f'{elbows[1]["showing"]:.3g} mm',
        'DOCK_PUMP_TUBE_CUT': f'{manifold.PUMP_TUBE_CUT:.3g} mm',
        'DOCK_BODY_GAP': f'{enc.bay_back_y(box["collet_plate"]) - enc.pump_cartridge_aft_y(box["pump_trays"], box["collet_plate"]):.4g} mm',
        'RESERVOIR_A_FILL_WARM': f'{reservoir_a_lengths["fluid-14"]:.3f} mm',
        'RESERVOIR_A_DRAW_WARM': f'{reservoir_a_lengths["fluid-16"]:.3f} mm',
        'RESERVOIR_B_FILL_WARM': f'{next(run.length for run in facts.runs if run.id == "fluid-24"):.3f} mm',
    }
    substitute_md(HERE / 'internal-plumbing.md', variables=variables)
    print('-> internal-plumbing.md')


if __name__ == '__main__':
    main()
