"""Native forming envelope consumed by the Rust funnel frame.

This declared producer retains the funnel's normal-offset construction. Its
receipt keys the inputs and files so a direct frame run can reuse the same
asset as a normal build, or produce it when the inputs have changed.
"""
from pathlib import Path
import hashlib
import json

import funnel_frame as frame

HERE = Path(__file__).resolve().parent
ROOT = frame.ROOT
ASSETS = HERE / 'forming-clearance'
STEP = ASSETS / 'forming-clearance.step'
PAYLOAD = ASSETS / 'forming-clearance.step.mesh'
RECEIPT = ASSETS / 'inputs.json'
SOURCES = (
    Path(__file__), Path(frame.__file__), Path(frame.funnel.__file__),
    Path(frame.elbow_cradle.__file__),
    ROOT / 'hardware/reference/neofit-stem-elbow/reference-parameters.json',
    ROOT / 'hardware/printed-parts/cadlib/fits.py',
    ROOT / 'hardware/scripts/_cadq_export.py',
    ROOT / 'hardware/scripts/_mesh_payload.py',
    ROOT / 'hardware/scripts/_payload_rules.py',
    ROOT / 'hardware/scripts/_rust_part.py',
)


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _inputs():
    return {str(path.relative_to(ROOT)): _sha(path) for path in SOURCES}


def ensure():
    """The current declared payload, with native work only on an input miss."""
    inputs = _inputs()
    try:
        saved = json.loads(RECEIPT.read_text())
        current = (saved['inputs'] == inputs and saved['files'] == {
            STEP.name: _sha(STEP), PAYLOAD.name: _sha(PAYLOAD)})
    except (OSError, ValueError, KeyError):
        current = False
    if not current:
        main()
    return PAYLOAD


def main():
    from _cadq_export import export_step
    import _mesh_payload
    import _rust_part
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.IMeshTools import IMeshTools_Parameters

    ASSETS.mkdir(parents=True, exist_ok=True)
    forming = frame.forming_clearance()
    # Keep the native trim used by frame.build with the normal-offset surface.
    forming = forming.intersect(frame.funnel._box(
        400.0, 400.0, -frame.funnel.drop, 0.0, 0.0, 0.0))
    # Mesh the actual normal-offset BRep; the STEP is its review representation.
    # This surface supplies a Boolean cutter, at one fifth of the final rule.
    linear = _rust_part.LINEAR / 5
    meshed = forming.copy(mesh=False)
    mesh = IMeshTools_Parameters()
    mesh.Deflection = mesh.DeflectionInterior = linear
    mesh.Angle = mesh.AngleInterior = _rust_part.ANGULAR
    mesh.EnableControlSurfaceDeflectionAllSurfaces = True
    mesh.ForceFaceDeflection = True
    triangulator = BRepMesh_IncrementalMesh(meshed.wrapped, mesh)
    if not triangulator.IsDone():
        raise ValueError('the native forming surface could not be triangulated')
    pos, nrm, idx, fac = _mesh_payload._solid_arrays(meshed.wrapped)
    export_step(forming, STEP)
    _mesh_payload.write([{'name': 'forming-clearance', 'color': None,
                          'pos': pos, 'nrm': nrm, 'idx': idx, 'fac': fac}],
                        PAYLOAD, src=_sha(STEP))
    receipt = {'inputs': _inputs(), 'files': {
        STEP.name: _sha(STEP), PAYLOAD.name: _sha(PAYLOAD)},
        'provider': 'funnel_frame.forming_clearance',
        'geometry': 'native normal-offset BRep trimmed to the frame seats',
        'linear_mm': linear, 'angular_rad': _rust_part.ANGULAR,
        'surface_deflection_control': 'all surfaces',
        'force_face_deflection': True}
    RECEIPT.write_text(json.dumps(receipt, indent=2) + '\n')
    print('-> forming-clearance STEP, kernel-rule payload and input receipt')


if __name__ == '__main__':
    from _rust_part import start
    start()
    main()
