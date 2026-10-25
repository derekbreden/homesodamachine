"""Read current pump-manifold preparation figures without building an appliance."""

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
import enclosure_assembly as assembly  # Declares the placement source this procedure reads.
import manifold_layout as manifold
from docgen import substitute_md


def main():
    facts = _facts.read()
    box = facts.box
    returns = {tee: manifold.lower_link_length(connection)
               for connection, tee in manifold.LOWER_CONNECTIONS.items()}
    elbows = manifold.pump_plumbing()['Y-C']['return']['elbows']
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
        'CAP_SCREWS': f'{len(enc.cap_screw_ys(box["inner"], box["collet_plate"]))}',
        'CAP_SCREW_LEN': f'{enc.cap_screw_len:.4g}',
    }
    substitute_md(HERE / 'internal-plumbing.md', variables=variables)
    print('-> internal-plumbing.md')


if __name__ == '__main__':
    main()
