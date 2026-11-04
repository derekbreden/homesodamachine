"""Read current enclosure assembly figures from the canonical appliance facts."""
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
from _cold_core_interface import outer_shell_y_length

_assembly_doc_root = next(p for p in Path(__file__).resolve().parents if (p / "hardware/scripts").is_dir())
sys.path.insert(0, str(_assembly_doc_root / "hardware/assembly"))
from _rust_docs import update as _update


def _inputs():
    facts = _facts.read()
    box = facts.box
    outer = box['outer']
    plate = box['collet_plate']
    compressor, condenser = (facts.bb('compressor'), facts.bb('condenser+fan'))
    return {
        'compressor.xmax': compressor.xmax,
        'condenser.xmax': condenser.xmax,
        'compressor.xmin': compressor.xmin,
        'condenser.xmin': condenser.xmin,
        'outer[1]': outer[1],
        'outer[0]': outer[0],
        'outer[3]': outer[3],
        'outer[2]': outer[2],
        'outer[5]': outer[5],
        'outer[4]': outer[4],
        'enc.wall': enc.wall,
        'enc.floor_t': enc.floor_t,
        'enc.front_wall': enc.front_wall,
        'enc.front_top_flank_t': enc.front_top_flank_t,
        'enc.back_top_flank_t': enc.back_top_flank_t,
        'enc.appliance_height': enc.appliance_height,
        "box['y_joint']": box['y_joint'],
        "enc.y_stack_figures(box['inner'])": enc.y_stack_figures(box['inner']),
        "box['splits'][0]": box['splits'][0],
        "enc._z_rail_travel(box['inner'], box['y_joint'], 'front', plate if box['pump_bay'] else None, box['vent_chase'])": enc._z_rail_travel(box['inner'], box['y_joint'], 'front', plate if box['pump_bay'] else None, box['vent_chase']),
        "plate['holes']": plate['holes'],
        'enc.appliance_width': enc.appliance_width,
        'outer_shell_y_length': outer_shell_y_length,
        'enc.side_band_inset': enc.side_band_inset,
        'enc.core_hold_reach': enc.core_hold_reach,
        'enc.rear_seam_clear': enc.rear_seam_clear,
        'enc.lip_len': enc.lip_len,
        'facts.constants.FLOOR_GROMMET_SQUEEZE': facts.constants.FLOOR_GROMMET_SQUEEZE,
    }


def main():
    _update('enclosure-mechanical', _inputs())


if __name__ == "__main__":
    main()
