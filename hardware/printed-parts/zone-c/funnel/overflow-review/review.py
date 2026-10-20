"""Manual native review and scoped aggregate refresh for the funnel's roof apron.

Run when reviewing this design, not from the generator or build. The existing
XCAF refresh utility preserves every unrelated assembly member and placement.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import shutil
import sys

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'tools').is_dir())
HERE = Path(__file__).resolve().parent
FUNNEL = HERE.parent
ENC = ROOT / 'hardware/printed-parts/enclosure/enclosure'
COVER = FUNNEL.parent / 'funnel-cover'
sys.path[:0] = [str(ROOT / 'hardware/scripts'), str(FUNNEL), str(ENC), str(COVER)]
import cadquery as cq
import numpy as np
import funnel
import funnel_cover
import funnel_frame
import enclosure as enc
import _box_spec
import flute_payload
import step_patch
import _mesh_payload
from _cadq_export import import_step

spec = importlib.util.spec_from_file_location('scoped_refresh', FUNNEL / 'flush-roof-review/refresh_aggregate.py')
refresh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(refresh)
refresh.native_replace = step_patch.patch


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def translated_surface(surface, offset):
    result = surface.copy()
    result['pos'] = (np.asarray(result['pos']).reshape(-1, 3) + np.asarray(offset)).ravel().tolist()
    return result


def local_surface(directory, name):
    step = directory / (name + '.step')
    payload = step.with_name(step.name + '.mesh')
    assert _mesh_payload.read_source(payload) == _mesh_payload.source_digest(step)
    held = flute_payload.read_payload(payload)
    assert len(held) == 1 and held[0]['name'] == name
    return held[0]


def main():
    box, _ = _box_spec.read(enc.Box, enc.Bound, (enc.Pack, enc.PortField, enc.Nameplate))
    cx, cy = box.pack.funnel
    seat = enc.funnel_seat_z(box.outer)
    position = (cx, cy, seat)
    local = import_step(str(FUNNEL / 'funnel.step')).val()
    exterior, cavity, meta = funnel.build_solids()
    expected = exterior.cut(cavity)
    difference = local.cut(expected).Volume() + expected.cut(local).Volume()
    assert local.isValid() and len(local.Solids()) == 1 and difference < 1e-4
    installed = local.translate(position)
    rib = funnel.roof_seal().translate(position)
    roof = box.outer[5] + funnel.apron_rise
    cover = import_step(str(COVER / 'funnel-cover.step')).val().translate((cx, cy, roof))
    shells = {n: import_step(str(ENC / f'enclosure-{n}.step')).val()
              for n in ('front-top', 'back-top')}
    frame = import_step(str(FUNNEL / 'funnel-frame.step')).val().translate(
        (cx, cy, funnel_frame.datums()[0]))
    contacts = {}
    for name, body in [*shells.items(), ('funnel-frame', frame)]:
        common = installed.intersect(body)
        outside = abs(common.cut(rib).Volume()) if abs(common.Volume()) > 1e-8 else 0.0
        assert outside < 1e-4, (name, outside)
        contacts[name] = {'nominal_contact_mm3': abs(common.Volume()),
                          'outside_roof_rib_mm3': outside}
    lid_contact = funnel_cover.contact_reading(cover, installed, cx, cy, roof)
    assert lid_contact['pad_contact_mm3'] > 0 and lid_contact['outside_pads_mm3'] < 1e-4
    removal = []
    for lift in (0.5, 1, 3, 6, 12, 24, 52):
        moved = installed.translate((0, 0, lift))
        clashes = {name: abs(moved.intersect(body).Volume())
                   for name, body in [*shells.items(), ('funnel-frame', frame)]}
        assert max(clashes.values()) < 1e-4, (lift, clashes)
        removal.append({'lift_mm': lift, 'rigid_overlap_mm3': clashes})
    capacity = cavity.intersect(funnel._box(600, 600, meta['end_z'], meta['top_z'], 0, 0)).Volume() / 1000
    bounds = installed.BoundingBox()
    review = {
        'schema': 1,
        'scope': 'Native geometry, mold closure/release and sampled vertical removal. No measured spill exclusion, seal force, cleanability or lifetime result.',
        'source_sha256': {str(p.relative_to(ROOT)): sha(p) for p in (
            Path(__file__), HERE / 'step_patch.py', FUNNEL / 'funnel.py', COVER / 'funnel_cover.py',
            ROOT / 'hardware/printed-parts/zone-c/funnel-mold/funnel_mold.py',
            ROOT / 'hardware/manifold-layout/enclosure_assembly.py',
            ROOT / 'hardware/manifold-layout/_scorecard.py')},
        'native_sha256': {str(p.relative_to(ROOT)): sha(p) for p in (
            FUNNEL / 'funnel.step', FUNNEL / 'funnel-frame.step',
            COVER / 'funnel-cover.step',
            ROOT / 'hardware/printed-parts/zone-c/funnel-mold/cavity.step',
            ROOT / 'hardware/printed-parts/zone-c/funnel-mold/core.step')},
        'finished_funnel_native_difference_mm3': difference,
        'capacity_to_mouth_ml': capacity,
        'native_silicone_volume_ml': local.Volume() / 1000,
        'funnel_seat_world_mm': position,
        'apron_bounds_world_mm': [bounds.xmin, bounds.xmax,
                                 cy + funnel.apron_y - funnel.apron_depth / 2,
                                 cy + funnel.apron_y + funnel.apron_depth / 2],
        'mouth_and_cover_seat_z_mm': roof,
        'height_with_cover_mm': cover.BoundingBox().zmax,
        'rigid_roof_z_mm': box.outer[5],
        'roof_rib_lowest_z_mm': seat + funnel.brim_thickness - funnel.seal_preload,
        'roof_rib_bottom_contact_width_mm': 1.5,
        'nominal_roof_contact': contacts,
        'cover_contact': lid_contact,
        'sampled_vertical_removal': removal,
    }
    print('Funnel geometry, named contact and removal checks passed.', flush=True)
    surfaces = flute_payload.surfaces((ENC,))
    changes = {'enclosure-front-top': shells['front-top']}
    selected = {name: surfaces[name] for name in changes}
    backup = ROOT / 'tmp/funnel-runoff/aggregate-before'
    backup.mkdir(parents=True, exist_ok=True)
    aggregates = {}
    for path in (ENC / 'enclosure.step', ROOT / 'hardware/manifold-layout/enclosure-assembly.step'):
        for p in (path, path.with_name(path.name + '.mesh')):
            saved = backup / p.name
            if not saved.exists():
                shutil.copy2(p, saved)
        if path.name == 'enclosure-assembly.step':
            changes.update({'funnel': installed, 'funnel-cover': cover})
            selected['funnel'] = translated_surface(local_surface(FUNNEL, 'funnel'), position)
            selected['funnel-cover'] = translated_surface(local_surface(COVER, 'funnel-cover'), (cx, cy, roof))
        aggregates[str(path.relative_to(ROOT))] = refresh.refresh(path, changes, selected)
    review['aggregates'] = aggregates
    (HERE / 'native-review.json').write_text(json.dumps(review, indent=2) + '\n')
    print('Scoped native and viewer aggregates refreshed.', flush=True)


if __name__ == '__main__':
    main()
