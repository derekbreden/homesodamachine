"""The pressure vessel's constants and gas physics, computed by the Rust `assembly-docs`
program. `tools/model/model.py` and the all-aero float integration read them."""
import sys
from pathlib import Path
_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next((p for p in _here.parents if p.name == 'hardware')) / 'printed-parts' / 'cadlib'))
sys.path.insert(0, str(next((p for p in _here.parents if p.name == 'hardware')) / 'cut-parts' / 'carbonation' / 'float-rod'))
sys.path.insert(0, str(next((p for p in _here.parents if p.name == 'hardware')) / 'printed-parts' / 'cold-core'))
sys.path.insert(0, str(next((p for p in _here.parents if (p / 'tools' / 'docgen').is_dir())) / 'tools'))
sys.path.insert(0, str(next((p for p in _here.parents if p.name == 'hardware')) / 'cut-parts' / 'carbonation' / 'endcaps-circular'))
from _cold_core_interface import above_carbonator_elbows_height, below_carbonator_elbows_height, carbonator_height, carbonator_outer_radius
from endcap_circular_dxf import hole_diameter, register_radius
import float_rod_dimensions as rod_spec

_assembly_doc_root = next(p for p in Path(__file__).resolve().parents if (p / "hardware/scripts").is_dir())
sys.path.insert(0, str(_assembly_doc_root / "hardware/assembly"))
from _rust_docs import evaluate as _evaluate


def _inputs():
    return {
        'carbonator_outer_radius': carbonator_outer_radius,
        'rod_spec.finished_length': rod_spec.finished_length,
        'rod_spec.length_tolerance': rod_spec.length_tolerance,
        'above_carbonator_elbows_height': above_carbonator_elbows_height,
        'below_carbonator_elbows_height': below_carbonator_elbows_height,
        'carbonator_height': carbonator_height,
        'register_radius': register_radius,
        'hole_diameter': hole_diameter,
    }


globals().update(_evaluate('pressure-vessel', _inputs())["exports"])
carbonation_basis_c = tuple(carbonation_basis_c)


def _vapor_atm(t_c):
    return _evaluate("pressure-vessel", {**_inputs(), "t_c": t_c}, operation="vapor_atm")["exports"]["value"]


def _bunsen(a1, a2, a3, t_c):
    return _evaluate("pressure-vessel", {**_inputs(), "t_c": t_c, "a1": a1, "a2": a2, "a3": a3}, operation="bunsen")["exports"]["value"]


def headspace_air_atm(t_c):
    return _evaluate("pressure-vessel", {**_inputs(), "t_c": t_c}, operation="headspace_air_atm")["exports"]["value"]


def carbonation_volumes(t_c, air):
    return _evaluate("pressure-vessel", {**_inputs(), "t_c": t_c, "air": air}, operation="carbonation_volumes")["exports"]["value"]
