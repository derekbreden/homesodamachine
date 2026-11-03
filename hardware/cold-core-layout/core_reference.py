"""Cold-core model references and scalar source-frame installation datums."""

from pathlib import Path
import sys


ROOT = next(p for p in Path(__file__).resolve().parents
            if (p / 'hardware/scripts/_assembly_model.py').is_file())
COLD = ROOT / 'hardware/printed-parts/cold-core'
for path in (ROOT / 'hardware/scripts', COLD, COLD / 'foam-assembly',
             ROOT / 'hardware/cold-core-layout'):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

CORE_MODEL = ROOT / 'hardware/cold-core-layout/cold-core-assembly.scene.npz'
CASING_MODEL = COLD / 'foam-assembly/foam-assembly.step.npz'


def datums():
    """The authored seats and ports; no geometry is constructed or loaded."""
    import _rust_part
    _rust_part.start()
    import _cold_core_interface as core
    import _copper_ports
    import foam_assembly as casing

    return {
        'front_wall_x': core.front_wall_x,
        'stack_floor_z': casing.stack_floor_z,
        'cap_face_z': casing.cap_face_z,
        'cap_face_over_floor': casing.cap_face_over_floor,
        'casing_foil_allowance': core.casing_foil_allowance,
        'seat': (core.front_wall_x, 0., casing.stack_floor_z),
        'copper_mouths': _copper_ports.stations(),
        'prv_vent_tip': casing.routes.routes['prv-vent'][-1],
        'conduit_mouths': {
            name: casing.cap_conduit_mouth(name) for name in casing.cap_conduits},
        'lid_anchor_xy': {
            name: casing.cap_anchor_station(name) for name in casing.cap_anchors},
        'side_anchor_xy': {
            name: casing.cap_side_anchor_station(name) for name in casing.cap_side_anchors},
        'deck_mount_xy': {
            name: casing.deck_mount_station(name) for name in core.deck_mounts},
    }


def casing_bounds(model=CASING_MODEL):
    """Rust's raw bounds of the three casing entries in their own assembly frame."""
    import _assembly_model

    model = Path(model)
    entries = _assembly_model.identity(model)
    reference = _assembly_model.instance(model, indices=range(len(entries)))
    bodies = _assembly_model.measure([reference], ())['bodies']
    return {
        'min': [min(row['min'][axis] for row in bodies) for axis in range(3)],
        'max': [max(row['max'][axis] for row in bodies) for axis in range(3)],
        'bodies': bodies,
    }


def instance(transform, *, model=CORE_MODEL, prefix='cold-core/'):
    """Ordered population metadata and one explicit installed 3x4-f64 reference."""
    import _assembly_model

    model = Path(model)
    identities = _assembly_model.identity(model)
    alpha = _assembly_model.document(model).get('alpha_by_name', {})
    return {
        'reference': _assembly_model.instance(
            model, indices=range(len(identities)), transform=transform, prefix=prefix),
        'identities': identities,
        'alpha_by_name': alpha,
    }
