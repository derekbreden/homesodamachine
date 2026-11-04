"""Read current pump-manifold preparation figures without building an appliance."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = next((p for p in HERE.parents if (p / 'hardware' / 'scripts').is_dir()))
HW = ROOT / 'hardware'
for path in (ROOT / 'tools', HW / 'scripts', HW / 'manifold-layout', HW / 'printed-parts' / 'cadlib', HW / 'printed-parts' / 'cold-core', HW / 'printed-parts' / 'enclosure' / 'enclosure'):
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

_assembly_doc_root = next(p for p in Path(__file__).resolve().parents if (p / "hardware/scripts").is_dir())
sys.path.insert(0, str(_assembly_doc_root / "hardware/assembly"))
from _rust_docs import update as _update


def _inputs():
    facts = _facts.read()
    box = facts.box
    returns = {tee: manifold.lower_link_length(connection) for connection, tee in manifold.LOWER_CONNECTIONS.items()}
    elbows = manifold.pump_plumbing()['Y-C']['return']['elbows']
    return {
        'reservoir_a_route_specs': above_core_routes.reservoir_a_route_specs(),
        'manifold.PURCHASED_TEES': manifold.PURCHASED_TEES,
        'manifold._returns.tee.BRANCH_COLLET_TRAVEL': manifold._returns.tee.BRANCH_COLLET_TRAVEL,
        'manifold._returns.RUN_INSERTION': manifold._returns.RUN_INSERTION,
        'manifold._returns.VALVE_INSERTION_NOMINAL': manifold._returns.VALVE_INSERTION_NOMINAL,
        'manifold.FORE_STUB_EXPOSED': manifold.FORE_STUB_EXPOSED,
        "returns['Y-C']": returns['Y-C'],
        "returns['Y-D']": returns['Y-D'],
        'manifold._returns.elbow.SOCKET_INSERTION': manifold._returns.elbow.SOCKET_INSERTION,
        "elbows[0]['stem']": elbows[0]['stem'],
        "elbows[1]['stem']": elbows[1]['stem'],
        "elbows[1]['showing']": elbows[1]['showing'],
        'manifold.PUMP_TUBE_CUT': manifold.PUMP_TUBE_CUT,
        "enc.bay_back_y(box['collet_plate'])": enc.bay_back_y(box['collet_plate']),
        "enc.pump_cartridge_aft_y(box['pump_trays'], box['collet_plate'])": enc.pump_cartridge_aft_y(box['pump_trays'], box['collet_plate']),
        "next((run.length for run in facts.runs if run.id == 'fluid-24'))": next((run.length for run in facts.runs if run.id == 'fluid-24')),
    }


def main():
    _update('internal-plumbing', _inputs())


if __name__ == "__main__":
    main()
