"""Compare seam candidates with the actual placed machine, within its assembly run.

Call compare(a) after constructing the fresh enclosure assembly. These are corner
stock envelopes, not a screw capacity or a drop model. No second pack is built.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import sys

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'tools/docgen').is_dir())
ENC = ROOT / 'hardware/printed-parts/enclosure/enclosure'
sys.path[:0] = [str(ENC), str(ROOT / 'hardware/manifold-layout')]
import enclosure as e
import enclosure_assembly as ea
import cadquery as cq


def compare(a):
    paths = [ENC / 'enclosure.py', ENC / '_enclosure_interface.py',
             ROOT / 'hardware/manifold-layout/enclosure_assembly.py',
             ROOT / 'hardware/manifold-layout/enclosure-box.json',
             ROOT / 'hardware/printed-parts/cold-core/_cold_core_interface.py']
    paths += list(ENC.glob('enclosure-*.step'))
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    rows = []
    candidates = []
    required_cap_rows = []
    for side, xe, sx in (('west', -107.5, 1), ('east', 107.5, -1)):
        for name, reach, axis, radius in (('M3', 14.0, 209.9, 7.9),
                                          ('M5-short candidate', 17.5, 215.9, 8.9)):
            # Full lower/middle corner required by the two stations' connected jamb.
            xa, xb = sorted((xe + sx * e.wall, xe + sx * (e.wall + reach)))
            probe = e._ybox(xa, xb, 197.0, axis + radius, 41.0, e.z_seam)
            candidates.append(dict(side=side, candidate=name, x_mm=[xa, xb],
                                   y_mm=[197.0, axis + radius], z_mm=[41.0, e.z_seam]))
            pb = probe.BoundingBox()
            for component, shape, _colour in ea.ml.placed_leaves(a):
                if component.startswith(('enclosure', 'grip-cover')):
                    continue
                bb = shape.BoundingBox()
                if any((getattr(pb, f'{axis}max') < getattr(bb, f'{axis}min') or
                        getattr(pb, f'{axis}min') > getattr(bb, f'{axis}max')) for axis in 'xyz'):
                    continue
                overlap = abs(probe.intersect(shape).Volume())
                if overlap > 1e-5 or component == 'cold-core/foam-shell':
                    rows.append(dict(side=side, candidate=name, component=component,
                                     overlap_mm3=overlap,
                                     component_bbox_mm={f'{axis}{end}':getattr(bb,f'{axis}{end}')
                                                        for axis in 'xyz' for end in ('min','max')}))
        # Minimal closed-end M5 witness: only the pilot's own Ø6.4 footprint,
        # not a bounding rectangle or enlarged boss. Even this required cap
        # must fit before the surrounding root/ligament can be considered.
        for name, screw, pilot, head, shank in (
                ('M5×10 socket-head lower-shank bound', 10.0, 6.8, 5.0, 4.0),
                ('M5×12 socket-head reviewed candidate', 12.0, 8.5, 5.0, 4.0),
                ('M5×12 button-head on fixed 9 mm flank', 12.0, 6.8, 3.0, 6.0)):
            body, cap = 5.8, 3.0
            seat = xe + sx * head
            insert_top = seat + sx * shank
            blind = insert_top + sx * pilot
            cap_end = blind + sx * cap
            witness = cq.Solid.makeCylinder(3.2, cap,
                         cq.Vector(blind, 215.9, 48.9), cq.Vector(sx, 0, 0))
            chain = dict(side=side, candidate=name, head_recess_mm=head,
                         shank_mm=shank, pilot_mm=6.4, insert_length_mm=body,
                         pilot_depth_mm=pilot, blind_relief_mm=pilot-body,
                         screw_length_mm=screw, tip_clearance_mm=shank+pilot-screw,
                         cap_mm=cap, insert_top_x_mm=insert_top,
                         head_plus_shank_mm=head+shank,
                         full_insert_thread_reach_mm=screw-shank,
                         blind_x_mm=blind, cap_end_x_mm=cap_end,
                         inward_band_mm=abs(cap_end-xe)-e.wall,
                         cap_witness_radius_mm=3.2, intersections=[])
            for component, shape, _colour in ea.ml.placed_leaves(a):
                if component.startswith(('enclosure', 'grip-cover')):
                    continue
                bb = shape.BoundingBox(); wb = witness.BoundingBox()
                if any((getattr(wb, f'{axis}max') < getattr(bb, f'{axis}min') or
                        getattr(wb, f'{axis}min') > getattr(bb, f'{axis}max')) for axis in 'xyz'):
                    continue
                overlap = abs(witness.intersect(shape).Volume())
                if overlap > 1e-5:
                    chain['intersections'].append(dict(component=component, overlap_mm3=overlap))
            required_cap_rows.append(chain)
    unchanged = hashes == {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    report = dict(generated_utc=datetime.now(timezone.utc).isoformat(),
        scope='Actual native placed solids against connected lower/middle corner envelopes; no strength allowable or drop qualification.',
        inputs_unchanged=unchanged, source_and_native_sha256=hashes,
        candidates=candidates, intersections=rows,
        required_m5_closed_caps=required_cap_rows,
        lower_m3=dict(clearance_hole_mm=3.3, axis_y_mm=209.9, free_edge_y_mm=200.0,
                      net_edge_ligament_mm=8.25, shank_mm=5.5,
                      projected_strip_area_per_plane_mm2=45.375),
        status='pass' if unchanged and all(r['overlap_mm3'] <= 1e-5 for r in rows if r['candidate']=='M3') else 'fail')
    (Path(__file__).parent / 'placement-comparison.json').write_text(json.dumps(report, indent=2)+'\n')
    return report
