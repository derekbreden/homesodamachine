"""Manual native receipt for the continuous aft water-in passage.

Run through tmp/takeover/cadq after the cap and cold core are exported. This
reads native artifacts and the named pressure-tube path; it does not generate
an enclosure or appliance, run in a build hook, or qualify physical hardware.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT/'hardware/scripts'), str(ROOT/'hardware/manifold-layout'),
               str(ROOT/'hardware/cold-core-layout'),
               str(ROOT/'hardware/printed-parts/cold-core'),
               str(ROOT/'hardware/printed-parts/cold-core/foam-assembly')]
import cadquery as cq
from _cadq_export import import_assembly, import_step
import above_core as layout
import above_core_parts as parts
import above_core_routes as routes
import _above_core_mounts as mounts
import _cold_core_interface as core
import _internal_routes as internal
import _internals as internals
import cold_core_assembly as assembly
import foam_assembly as foam


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def volume(shape):
    return abs(shape.Volume()) if not shape.isNull() else 0.


def bounds(shape):
    box = shape.BoundingBox()
    return [[box.xmin, box.ymin, box.zmin], [box.xmax, box.ymax, box.zmax]]


def shell_world_point(point):
    return layout.point(layout.cap_lid_pose(),
        (-point[0],-point[1],point[2]-core.foam_shell_outer_height-foam.top_cap_height))


def shell_world_shape(shape):
    return (shape.translate((0.,0.,-core.foam_shell_outer_height-foam.top_cap_height))
            .rotate((0.,0.,0.),(0.,0.,1.),180.)
            .moved(layout.frame_location(layout.cap_lid_pose())))


def sweep_edge(edge, radius):
    return (cq.Workplane(cq.Plane(origin=edge.startPoint(),normal=edge.tangentAt(0.)))
            .circle(radius).sweep(cq.Wire.assembleEdges([edge]),isFrenet=False).val())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=HERE/'water-in-passage-review.json')
    parser.add_argument('--context-json', type=Path,
                        help='Completed bounded native corridor context receipt to bind, without repeating it')
    args = parser.parse_args()
    previous = json.loads(args.output.read_text()) if args.output.exists() else {}
    cap_dir = ROOT/'hardware/printed-parts/cold-core/foam-cap'
    cup = (import_step(cap_dir/'foam-cap-top.step').val()
           .translate((0.,0.,-foam.top_cap_height))
           .moved(layout.frame_location(layout.cap_lid_pose())))
    lid = (import_step(cap_dir/'foam-cap-lid-top.step').val()
           .moved(layout.frame_location(layout.cap_lid_pose())))
    cca_path = ROOT/'hardware/cold-core-layout/cold-core-assembly.step'
    actual = import_assembly(cca_path)
    named = {name.rsplit('/',1)[-1]:shell_world_shape(shape)
             for name,(shape,_color) in actual.items()}
    points = [shell_world_point(point) for point in assembly.trimmed_routes()['water-in']]
    segments = routes._rounded(points,14.)
    wire = parts.route_wire({'segments':segments})
    tube_parts = [sweep_edge(edge,core.lldpe_tube_od/2.) for edge in wire.Edges()]
    nominal_tube = tube_parts[0].fuse(*tube_parts[1:]).clean()
    exported_tube = named['line-water-in']
    features = mounts.water_in_features()
    air = features['cut']
    cup_stock = features['cup_add'].cut(air)
    lid_stock = features['lid_add'].cut(air)
    sensor = mounts.cable_guide_points('sensor-cable')
    sensor_air = internal.build_route(sensor['points_mm'],sensor['bend_radius_mm'],
                                     core.cap_conduit_bore_radius)
    floor_z = (layout.cap_lid_pose()['translation_mm'][2]-foam.top_cap_height
               +core.cap_shell_clearance)
    floor_rows = []
    for index,segment in enumerate(segments):
        if any(abs(p[2]-points[-1][2]+14.)>1e-7 for p in segment['points_mm']):
            continue
        edge = parts.route_wire({'segments':[segment]})
        tangent = edge.tangentAt(0.)
        floor_edge = edge.translate((0.,0.,floor_z+core.wall_and_floor_thickness/2.-points[-1][2]+14.))
        plane = cq.Plane(origin=floor_edge.startPoint(), normal=tangent,
                         xDir=(-tangent.y,tangent.x,0.))
        probe = (cq.Workplane(plane).rect(2.*core.cap_conduit_bore_radius,
                                        core.wall_and_floor_thickness)
                 .sweep(floor_edge,isFrenet=False).val())
        floor_rows.append({'segment':index,'thickness_mm':core.wall_and_floor_thickness,
                           'probe_volume_mm3':volume(probe),
                           'missing_stock_mm3':volume(probe.cut(cup))})
    stem=parts._module('water_passage_neofit_stem',
                       'reference/neofit-stem-elbow/neofit_stem_elbow.py')
    warm_mouth = layout.point(layout.snapshot_pose('carbonator-fold'),stem.socket()[0])
    warm_path = routes._rounded([warm_mouth,(*warm_mouth[:2],318.5),
                                (*points[-1][:2],318.5),points[-1]],18.)
    warm_exposed = parts.route_wire({'segments':warm_path}).Length()
    receiving = stem.SOCKET_INSERTION
    context = previous.get('bounded_context_receipt')
    if args.context_json:
        context = json.loads(args.context_json.read_text())
        context = {key:value for key,value in context.items() if key not in ('seconds',)}
        context['scope'] = ('Completed corridor candidate against the recorded exported core '
            'and all125 cached electrical bodies. The current artifact reading below '
            'separately binds the final cup/lid and complete internal tube. This receipt '
            'is reused only while its centerline and recorded context remain unchanged.')
        context['candidate_receipt_sha256'] = sha(args.context_json)
        directory=ROOT/'tmp/above-core-electrical-fixture/wiring'
        index=json.loads((directory/'index.json').read_text())['parts']
        context['electrical_body_sha256'] = {name:sha(directory/file) for name,file in index.items()}
    context_matches = (context is not None and len(points)==len(context['points_world_mm'])
                       and max(math.dist(a,b) for a,b in zip(points,context['points_world_mm']))<1e-6)
    report = {
        'schema':1,'reviewed_date':'2026-10-28',
        'scope':('Manual nominal native reading of the straight water-in guide, its floor-rooted '
                 'column and one continuous tube through the plain guide. The source '
                 'metal elbow/adapter keep their poses; the check elbow faces up. No physical fit, '
                 'hand access, pressure, sealing, retention, thermal or lifetime qualification.'),
        'reproduce':'tools/cad-venv/bin/python hardware/mechanical-qualification/enclosure-above-core/water_in_passage.py',
        'guide_world_mm':list(points[-1]),'internal_points_world_mm':points,
        'minimum_radius_mm':min(segment['radius_mm'] for segment in segments if segment['kind']=='arc'),
        'passage_diameter_mm':2.*core.cap_conduit_bore_radius,
        'side_and_roof_stock_mm':3.,'cup_floor_specification_mm':core.wall_and_floor_thickness,
        'horizontal_floor_backing_mm':features['horizontal_floor_backing_mm'],
        'floor_scope':'The straight cylindrical guide crosses the cup floor; no horizontal passage runs through the cup.',
        'floor_scope_sources':['hardware/printed-parts/cold-core/_cold_core_interface.py:43',
                               'hardware/printed-parts/cold-core/foam-cap/dry-closure-review.json'],
        'cup_floor_outer_world_z_mm':floor_z,'horizontal_floor_probes':floor_rows,
        'sensor_passage_wall_mm':air.distance(sensor_air),
        'carrier_root_connectivity_basis':'The complete named sleeve is present in the valid single-solid cup and overlaps its retained floor; the source clips new stock at the existing outer floor face.',
        'new_cup_stock_bounds_world_mm':bounds(features['cup_add']),
        'cup':{'valid':cup.isValid(),'solids':len(cup.Solids()),
               'passage_contact_mm3':volume(air.intersect(cup)),
               'tube_contact_mm3':volume(nominal_tube.intersect(cup)),
               'missing_named_sleeve_stock_mm3':volume(cup_stock.cut(cup))},
        'lid':{'valid':lid.isValid(),'solids':len(lid.Solids()),
               'passage_contact_mm3':volume(air.intersect(lid)),
               'tube_contact_mm3':volume(nominal_tube.intersect(lid)),
               'missing_named_sleeve_stock_mm3':volume(lid_stock.cut(lid))},
        'exported_internal_tube':{'body':'line-water-in','valid':exported_tube.isValid(),
            'solids':len(exported_tube.Solids()),'bounds_world_mm':bounds(exported_tube),
            'solid_tube_volume_mm3':volume(exported_tube),
            'segmented_nominal_volume_mm3':volume(nominal_tube),
            'volume_difference_mm3':abs(volume(exported_tube)-volume(nominal_tube))},
        'continuous_tube_accounting':{
            'internal_span_mm':wire.Length(),'warm_span_mm':warm_exposed+receiving,
            'modeled_total_mm':wire.Length()+warm_exposed+receiving,
            'warm_exposed_mm':warm_exposed,'warm_elbow_receiving_mm':receiving,
            'warm_elbow_receiving_basis':'ATEU44 female socket published B=.665 inch; distinct from the ACHV receiving-depth family inference for its male stem.',
            'carbonator_nominal_adapter_standoff_mm':internals.PTC_STANDOFF,
            'carbonator_socket_receiving_depth_mm':None,
            'carbonator_allowance_basis':('The internal CAD span starts at the metal elbow '
                'mouth and includes the nominal 18.5 mm adapter standoff. Actual receiving depth '
                'is unmeasured; replace that nominal allowance with the installed receiving mark.'),
            'plain_guide_joint':False,'plain_guide_insertion_mm':0.,'plain_guide_cut':False},
        'source_hosts':{name:{'contact_mm3':volume(nominal_tube.intersect(named[name]))}
                        for name in ('collet-water-in','carbonator-elbow-water-in')},
        'bounded_context_centerline_matches_current':context_matches,
        'bounded_context_receipt':context,'source_hashes_sha256':{},'exported_solids_sha256':{},
    }
    for rel in ['hardware/manifold-layout/above-core.json',
                'hardware/printed-parts/cold-core/_above_core_mounts.py',
                'hardware/printed-parts/cold-core/_cold_core_interface.py',
                'hardware/printed-parts/cold-core/_internal_routes.py',
                'hardware/printed-parts/cold-core/_foam_cap.py',
                'hardware/printed-parts/cold-core/_foam_shell.py',
                'hardware/cold-core-layout/cold_core_assembly.py']:
        report['source_hashes_sha256'][rel]=sha(ROOT/rel)
    for rel in ['hardware/printed-parts/cold-core/foam-shell/foam-shell.step',
                'hardware/printed-parts/cold-core/foam-cap/foam-cap-top.step',
                'hardware/printed-parts/cold-core/foam-cap/foam-cap-lid-top.step',
                'hardware/printed-parts/cold-core/foam-assembly/foam-assembly.step',
                'hardware/cold-core-layout/cold-core-assembly.step']:
        report['exported_solids_sha256'][rel]=sha(ROOT/rel)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({key:report[key] for key in ('cup','lid','sensor_passage_wall_mm',
          'continuous_tube_accounting','bounded_context_centerline_matches_current')},indent=2))
    print('->',args.output.relative_to(ROOT))


if __name__=='__main__':
    main()
