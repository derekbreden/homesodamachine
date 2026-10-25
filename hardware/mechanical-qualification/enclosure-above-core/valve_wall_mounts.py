"""Manual open-bench seating of the back-top's two socket-mounted valves.

The back-top rests roof-down. Bare V-A enters through its open front at world
X=-40 and 12 mm below its selected height, moves aft to a 6.2 mm +Y post
disengagement, moves laterally to its plate, rises 12 mm, then seats along -Y.
V-K enters through the open underside directly below its plate and seats along
-Y. Native per-solid bounding prisms enclose each straight handling motion,
followed by 13 native axial positions. This is a geometric reading, not hand
access, insertion force or retention qualification.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT/'hardware/scripts'), str(ROOT/'hardware/manifold-layout'),
               str(ROOT/'hardware/printed-parts/enclosure/enclosure')]
import cadquery as cq
from _cadq_export import import_step
import above_core as layout
import above_core_parts as parts
import _above_core_shell as shell


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def volume(shape):
    return 0. if shape.isNull() else abs(shape.Volume())


def bounds(shape):
    b = shape.BoundingBox()
    return [b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax]


def nearby(a, b):
    return all(a[i+3] >= b[i] and b[i+3] >= a[i] for i in range(3))


def common(shape, obstacle):
    if not nearby(bounds(shape), bounds(obstacle)):
        return 0.
    return volume(shape.intersect(obstacle, tol=1e-6))


def continuous_bounds(body, start, end, fixed):
    """A separate bounding prism encloses each complete native solid's motion."""
    rows=[]
    for index,solid in enumerate(body.Solids()):
        b=bounds(solid)
        lo=[b[i]+min(start[i],end[i]) for i in range(3)]
        hi=[b[i+3]+max(start[i],end[i]) for i in range(3)]
        prism=cq.Solid.makeBox(*(hi[i]-lo[i] for i in range(3)),cq.Vector(*lo))
        for other,obstacle in fixed.items():
            rows.append({'solid':index,'obstacle':other,
                         'common_mm3':common(prism,obstacle)})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--back-top', type=Path,
        default=ROOT/'hardware/printed-parts/enclosure/enclosure/enclosure-back-top.step')
    parser.add_argument('--add-seats', action='store_true',
        help='Fuse production sidewall plates into a pre-export native back-top fixture')
    parser.add_argument('--output', type=Path, default=HERE/'valve-wall-mount-review.json')
    args = parser.parse_args()
    args.back_top = args.back_top.resolve()
    stock = (cq.Shape.importBrep(str(args.back_top)) if args.back_top.suffix == '.brep'
             else import_step(args.back_top).val())
    seats = shell.valve_seats()
    if args.add_seats:
        stock = stock.fuse(*seats.values()).clean()
    fixed = {'enclosure-back-top': stock}
    bodies = {name: layout.place(parts.valve_native(name),name) for name in seats}
    rows = []
    for name, body in bodies.items():
        if name=='valve-v-a':
            dx=-40.-layout.pose(name)['translation_mm'][0]
            fore=bounds(stock)[1]-1.-bounds(body)[4]
            paths=[('Fore entry',(dx,fore,-12.),(dx,6.2,-12.)),
                   ('Lateral handling',(dx,6.2,-12.),(0.,6.2,-12.)),
                   ('Raise to plate',(0.,6.2,-12.),(0.,6.2,0.))]
        else:
            # All of the bare valve starts below the complete open lower rim.
            dz=bounds(stock)[2]-1.-bounds(body)[5]
            paths=[('Underside entry',(0.,6.2,dz),(0.,6.2,0.))]
        handling=[]
        for label,start,end in paths:
            readings=continuous_bounds(body,start,end,fixed)
            handling.append({'phase':label,'start_translation_mm':start,
                'end_translation_mm':end,'continuous_native_solid_bounds':readings,
                'passed':all(row['common_mm3']<=1e-6 for row in readings)})
        axial = []
        for index in range(13):
            dy = 6.2*(12-index)/12.
            at = body.translate((0., dy, 0.))
            for other, obstacle in fixed.items():
                axial.append({'offset_y_mm': dy, 'obstacle': other,
                              'common_mm3': common(at, obstacle)})
        passed = all(row['passed'] for row in handling) and all(
            row['common_mm3'] <= 1e-6 for row in axial)
        rows.append({'valve': name, 'passed': passed,
            'disengaged_translation_y_mm': 6.2,
            'axial_translation_y_mm': [6.2, 0.],
            'stage_present_bodies': sorted(fixed),
            'handling':handling,
            'native_axial_positions': axial})
        fixed[name] = body
        print(name, 'passed', passed, 'max common',
              max(row['common_mm3'] for row in axial+[
                  item for phase in handling for item in phase['continuous_native_solid_bounds']]),
              flush=True)
    report = {
        'schema': 1, 'reviewed_date': '2026-10-24',
        'scope': __doc__.strip(),
        'reproduce': 'tools/cad-venv/bin/python hardware/mechanical-qualification/enclosure-above-core/valve_wall_mounts.py',
        'approved_mount_basis': 'hardware/manifold-layout/studies/wall-supported/support-plan.json',
        'assembly_prerequisites': [
            'Back-top is separate from the core and rests on its roof with its front and underside open.',
            'Bring bare V-A through the open front at worldX=-40 and 12 mm below its selected height; move aft to +Y6.2, move laterally to selectedX, raise12, then seat along -Y. Seat bare V-K second through the underside directly below its plate.',
            'The water header, fitted elbows, relays, ASSE, gas group, core equipment and lead dress are not present in this bare-valve stage.',
            'Complete the approved back-top plumbing subassembly before the separate column-closing motion.'],
        'valve_pose_world': {name: layout.pose(name) for name in bodies},
        'mounts': shell.valve_seat_datums(),
        'stock': {'valid': stock.isValid(), 'solids': len(stock.Solids()),
                  'faces': len(stock.Faces()), 'volume_mm3': volume(stock),
                  'bounds_mm': bounds(stock)},
        'checks': rows, 'passed': stock.isValid() and len(stock.Solids()) == 1
                                  and all(row['passed'] for row in rows),
        'fixture': {'path': str(args.back_top.relative_to(ROOT)),
                    'sha256': sha(args.back_top), 'production_seats_fused': args.add_seats},
        'source_sha256': {str(path.relative_to(ROOT)): sha(path) for path in (
            ROOT/'hardware/manifold-layout/above-core.json',
            ROOT/'hardware/manifold-layout/above_core_parts.py',
            ROOT/'hardware/printed-parts/enclosure/enclosure/_above_core_shell.py',
            ROOT/'hardware/printed-parts/valve-seat/valve_seat.py')},
        'limits': 'Sampled native axial motion plus conservative continuous straight handling bounds. No purchased female-disconnect envelope, flexible-lead motion, hand reach, insertion force, new print-orientation fit, retention or load-capacity qualification. This empty-back-top procedure does not establish late valve installation into a populated appliance or the separate carried-group closing motion.'}
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print('PASSED', report['passed'], '->', args.output, flush=True)


if __name__ == '__main__':
    main()
