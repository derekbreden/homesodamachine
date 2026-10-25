"""Manual native review and scoped aggregate refresh for the funnel's roof apron.

Run when reviewing this design, not from the generator or build. The existing
XCAF refresh utility preserves every unrelated assembly member and placement.
"""
from pathlib import Path
import argparse
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--geometry-only', action='store_true',
                        help='Review individual exports without refreshing the appliance assembly')
    args = parser.parse_args()
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
    roof = box.outer[5] + funnel.apron_rise
    cover = import_step(str(COVER / 'funnel-cover.step')).val().translate((cx, cy, roof))
    shells = {n: import_step(str(ENC / f'enclosure-{n}.step')).val()
              for n in ('front-top', 'back-top')}
    frame = import_step(str(FUNNEL / 'funnel-frame.step')).val().translate(
        (cx, cy, funnel_frame.datums()[0]))
    contacts = {}
    for name, body in [*shells.items(), ('funnel-frame', frame)]:
        common = installed.intersect(body)
        overlap = abs(common.Volume())
        assert overlap < 1e-4, (name, overlap)
        contacts[name] = {'overlap_mm3': overlap}
    lid_contact = {'silicone_overlap_mm3': abs(cover.intersect(installed).Volume())}
    assert lid_contact['silicone_overlap_mm3'] < 1e-4
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
        'scope': 'Individual native funnel, frame, cover and both upper-shell exports: seated contact and sampled silicone vertical removal. Mold closure/release is recorded separately in the mold design receipt. No measured spill exclusion, seal force, cleanability or lifetime result.',
        'source_sha256': {str(p.relative_to(ROOT)): sha(p) for p in (
            Path(__file__), HERE / 'step_patch.py', FUNNEL / 'funnel.py', COVER / 'funnel_cover.py',
            ROOT / 'hardware/printed-parts/zone-c/funnel-mold/funnel_mold.py',
            ROOT / 'hardware/manifold-layout/enclosure_assembly.py',
            ROOT / 'hardware/manifold-layout/_scorecard.py')},
        'native_sha256': {str(p.relative_to(ROOT)): sha(p) for p in (
            FUNNEL / 'funnel.step', FUNNEL / 'funnel-frame.step',
            COVER / 'funnel-cover.step',
            ROOT / 'hardware/printed-parts/zone-c/funnel-mold/cavity.step',
            ROOT / 'hardware/printed-parts/zone-c/funnel-mold/core.step',
            ENC / 'enclosure-front-top.step', ENC / 'enclosure-back-top.step')},
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
        'apron_underside_z_mm': seat + funnel.brim_thickness,
        'apron_thickness_mm': funnel.apron_rise,
        'nominal_roof_contact': contacts,
        'cover_contact': lid_contact,
        'sampled_vertical_removal': removal,
    }
    print('Funnel geometry, named contact and removal checks passed.', flush=True)
    if args.geometry_only:
        review['aggregate_refresh_run'] = False
        (HERE / 'native-review.json').write_text(json.dumps(review, indent=2) + '\n')
        return
    changes = {'funnel': installed, 'funnel-cover': cover}
    selected = {
        'funnel': translated_surface(local_surface(FUNNEL, 'funnel'), position),
        'funnel-cover': translated_surface(local_surface(COVER, 'funnel-cover'), (cx, cy, roof)),
    }
    backup = ROOT / 'tmp/funnel-cover-edge/before'
    backup.mkdir(parents=True, exist_ok=True)
    aggregates = {}
    for path in (ROOT / 'hardware/manifold-layout/enclosure-assembly.step',):
        for p in (path, path.with_name(path.name + '.mesh')):
            saved = backup / p.name
            if not saved.exists():
                shutil.copy2(p, saved)
        aggregates[str(path.relative_to(ROOT))] = refresh.refresh(path, changes, selected)
    review['aggregates'] = aggregates
    (HERE / 'native-review.json').write_text(json.dumps(review, indent=2) + '\n')
    print('Scoped native and viewer aggregates refreshed.', flush=True)


if __name__ == '__main__':
    main()
