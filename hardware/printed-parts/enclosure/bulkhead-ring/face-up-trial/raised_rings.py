"""Face-up raised TAP/FLAVOR lettering, with the existing fitting seats intact."""
import hashlib
import json
from pathlib import Path
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tools').is_dir())
sys.path[:0] = [str(HERE.parent), str(ROOT / 'hardware/scripts')]
import bulkhead_ring as ring
from _cadq_export import export_assembly, note_write, _write_mesh_payload, _per_solid_color

STATIONS = ('water', 'flavor-a', 'flavor-b')
RISE = .48


def name(station):
    return f'bulkhead-ring-{station}-raised'


def build(station):
    body = ring.build_ring(station)
    original = ring.build_word(station)
    word = cq.Compound.makeCompound([
        s.fuse(s.translate((0, RISE, 0))).clean() for s in original.Solids()
    ])
    return body, word


def print_pose(shape):
    return shape.rotate((0, 0, 0), (1, 0, 0), 90).rotate((0, 0, 0), (0, 0, 1), 180)


def main():
    readings = {}
    for station in STATIONS:
        body, word = build(station)
        whole = body.fuse(*word.Solids()).clean()
        assert whole.isValid() and len(whole.Solids()) == 1
        assert abs(body.intersect(word).Volume()) < 1e-6
        assert abs(body.BoundingBox().ylen - ring.THICK) < 1e-6
        assert abs(word.BoundingBox().ymax - ring.THICK - RISE) < 1e-6
        flange_r = ring.FAMILIES[ring.family(station)].flange_footprint() / 2
        flange = cq.Solid.makeCylinder(flange_r, RISE + 1, cq.Vector(0, ring.THICK, 0), cq.Vector(0, 1, 0))
        assert abs(word.intersect(flange).Volume()) < 1e-6
        assembly = cq.Assembly()
        assembly.add(body, name=name(station), color=ring._filament(ring._rear.chip_color(ring.FLUIDS[station])))
        assembly.add(word, name=name(station)+'-word', color=ring._filament(ring._rear.word_color(ring.FLUIDS[station])))
        out = HERE / (name(station)+'.step')
        export_assembly(assembly, str(out))
        whole.copy(mesh=False).exportStl(str(out.with_suffix('.stl')), tolerance=.005, angularTolerance=.05, relative=False)
        note_write(out.with_suffix('.stl'))
        _write_mesh_payload(out, _per_solid_color(assembly))
        readings[station] = {
            'word': ring.STATIONS[station].word,
            'mounting_thickness_mm': ring.THICK,
            'letter_rise_mm': RISE,
            'letter_solids': len(word.Solids()),
            'flange_to_word_band_gap_mm': word.BoundingBox().zmin - flange_r,
            'flange_intersection_mm3': abs(word.intersect(flange).Volume()),
            'first_plane_mm': print_pose(whole).BoundingBox().zmin,
            'top_plane_mm': print_pose(whole).BoundingBox().zmax,
            'body_colour': 'white' if station == 'water' else 'black',
            'word_colour': 'black' if station == 'water' else 'white',
        }
    paths = [Path(__file__), Path(ring.__file__)] + [HERE/(name(s)+e) for s in STATIONS for e in ('.step', '.stl')]
    report = {'pass': True, 'stations': readings,
              'scope': 'Geometry preparation. Physical nameplate acceptance and measured Mark2 alignment remain prerequisites for printing these rings.',
              'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
    (HERE/'geometry-check.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(readings, indent=2))


if __name__ == '__main__':
    main()
