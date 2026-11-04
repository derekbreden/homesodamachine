"""Scan-fitted neoFit ACVUS44 1/4-inch stem check, HSM-000383.

+X runs from the free stem tip at X0 to the socket mouth. The frozen model
retains the measured turned exterior; its bore and socket are display closures.
The native archive and physical selections are recorded in scan-evidence.json.
"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
STEP_PATH = HERE / 'neofit-acvus44-check.step'
PAYLOAD_PATH = HERE / 'neofit-acvus44-check.step.mesh'
ASSET_MANIFEST_PATH = HERE / 'frozen-asset.json'


_reference_hardware = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('neofit_acvus44_check')
globals().update({name: _reference_values[name] for name in ('STEM_D', 'PROFILE', 'LENGTH', 'SHOULDER', 'INSERTION', 'SOCKET_D', 'BORE_D')})



def stem_tip():
    return _reference_data('neofit_acvus44_check', 'stem_tip', (), {})


def tube_port():
    return _reference_data('neofit_acvus44_check', 'tube_port', (), {})


def main():
    import json
    sys.path.insert(0, str(HERE.parents[1] / 'scripts'))
    import _rust_part
    _rust_part.start()
    from _materials import M_NEOFIT_WHITE_ACETAL, linear
    parameters = json.loads((HERE / 'reference-parameters.json').read_text())
    _rust_part.cut('tooling', 'stem-check-reference',
                   {**parameters, 'color': linear(M_NEOFIT_WHITE_ACETAL)}, HERE)


if __name__ == '__main__':
    main()
