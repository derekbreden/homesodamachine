"""Production display mounting and the pump's flange-to-port-wall space, for /3d.

Run manually through tools/run.py. The orange space and blue wall plane are
layout annotations; all other bodies come from the current production meshes.
"""
from pathlib import Path
import hashlib
import json
import sys

import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tools').is_dir())
ENC = HERE.parent / 'enclosure'
COVER = HERE.parent / 'display-cover'
GLB = ROOT / 'hardware/assembly/scenes/glb'
RUN = ROOT / '.cache/runs/pump-port-review-20261106'
sys.path[:0] = [str(HERE.parent / 'nameplate'), str(ROOT / 'hardware/scripts')]
from attachment_view import payload_meshes, READ_SHA
from _mesh_payload import write as write_payload


def box(low, high):
    low, high = np.asarray(low), np.asarray(high)
    return trimesh.creation.box(extents=high-low,
        transform=trimesh.transformations.translation_matrix((low+high)/2))


def boolean(op, *parts):
    return getattr(trimesh.boolean, op)(list(parts), engine='manifold')


def material(mesh, color, alpha=1.):
    mesh = mesh.copy()
    mesh.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(
        baseColorFactor=np.round(np.r_[color[:3], alpha]*255).astype(np.uint8),
        metallicFactor=0., roughnessFactor=.7, doubleSided=True,
        alphaMode='BLEND' if alpha < 1. else 'OPAQUE'))
    return mesh


def save(name, rows, render=False):
    rows = [(title, trimesh.graph.smooth_shade(mesh, angle=np.radians(30), facet_minarea=None),
             color, *opacity) for title, mesh, color, *opacity in rows]
    scene = trimesh.Scene()
    for title, mesh, color, *opacity in rows:
        scene.add_geometry(material(mesh, color, opacity[0] if opacity else 1.), node_name=title)
    target = GLB / (name+'.glb')
    target.write_bytes(scene.export(file_type='glb'))
    if render:
        packed = []
        for title, mesh, color, *_ in rows:
            packed.append(dict(name=title, color=color[:3],
                pos=mesh.vertices.reshape(-1).tolist(),
                nrm=mesh.vertex_normals.reshape(-1).tolist(),
                idx=mesh.faces.reshape(-1).tolist(), fac=[0,len(mesh.faces)-1]))
        write_payload(packed, RUN/(name+'.mesh'))
    print(target.name, flush=True)
    return str(target.relative_to(ROOT/'hardware'))


def main():
    RUN.mkdir(parents=True, exist_ok=True)
    GLB.mkdir(parents=True, exist_ok=True)
    dimensions = json.loads((COVER/'mount-dimensions.json').read_text())
    physical = json.loads((ROOT/'hardware/manifold-layout/machine-export-physical.numbers.json').read_text())['spec']
    frame = np.eye(4)
    frame[:3] = next(p['transform'] for p in physical['instances'] if p.get('name')=='display-cover')
    inverse = np.linalg.inv(frame)
    normal = frame[:3, 2]
    def read(path, include=lambda _: True):
        rows = payload_meshes(path, include)
        for _, mesh, _ in rows:
            # Viewer face seams duplicate vertices; welding preserves the surface.
            mesh.merge_vertices()
        return rows
    selected = read(ROOT/'hardware/manifold-layout/enclosure-assembly.step.mesh',
        lambda n: n.startswith(('pump-a-', 'pump-b-', 'display/', 'funnel/')) or n=='funnel')
    pumps = [(n, m, c) for n, m, c in selected if n.startswith('pump-')]
    screens = [(n, m.copy(), c) for n, m, c in selected if n.startswith('display/')]
    screen_front = max(np.max(trimesh.transform_points(m.vertices, inverse)[:, 2]) for _, m, _ in screens)
    desired = -dimensions['cover_mm'][2] - dimensions['gasket_thickness_mm']
    display_shift = desired-screen_front
    for _, mesh, _ in screens:
        mesh.vertices += normal*display_shift
    cover_rows = read(COVER/'display-cover.step.mesh')
    gasket_rows = read(HERE.parent/'display-gasket/display-gasket.step.mesh')
    fasteners = read(COVER/'display-cover-fasteners.step.mesh')
    def placed(rows, shift=0.):
        out = []
        for name, mesh, color in rows:
            mesh=mesh.copy(); mesh.apply_transform(frame); mesh.vertices += normal*shift
            out.append((name, mesh, color))
        return out
    cover_world = placed(cover_rows)
    gasket_world = placed(gasket_rows)
    hardware_world = placed(fasteners)
    front = trimesh.load_mesh(ENC/'enclosure-front-top.stl', process=True)
    local = front.copy(); local.apply_transform(inverse)
    cover = trimesh.load_mesh(COVER/'display-cover.stl', process=True)
    print('Checking installed display interfaces', flush=True)
    def volume(a, b):
        return abs(float(boolean('intersection', a, b).volume))
    cover_overlap = volume(front, cover_world[0][1])
    screws = [(n,m,c) for n,m,c in hardware_world if 'screw' in n]
    screw_readings = []
    for name, mesh, _ in screws:
        screw_readings.append(dict(name=name, enclosure_overlap_mm3=volume(front,mesh),
            glass_and_module_overlap_mm3=sum(volume(mesh,m) for _,m,_ in screens)))
    stations = np.asarray(dimensions['stations_local_xy_mm'])
    origins=np.c_[stations, np.full(4, -dimensions['cover_mm'][2]+.01)]
    points, ray_ids, _ = local.ray.intersects_location(origins, np.tile([0.,0.,-1.],(4,1)), multiple_hits=True)
    pilot_readings=[]
    for i, station in enumerate(stations):
        zs=sorted(points[ray_ids==i,2].tolist(),reverse=True)
        pilot_readings.append(dict(station_local_xy_mm=station.tolist(), axial_hits_local_z_mm=zs,
            backing_mm=(zs[0]-zs[1]) if len(zs)>1 else None))
    bores=[-82.1,-22.35,22.35,82.1]
    open_bores=(~front.contains(np.array([[x,90.,196.174] for x in bores]))).tolist()
    closed_slots=front.contains(np.array([[x,90.,185.] for x in bores])).tolist()
    fitted=read(ENC/'enclosure.step.mesh',lambda n:n=='enclosure_pump_retainer')
    retainer=fitted[0][1]
    head_rear=max(float(m.bounds[1,1]) for n,m,_ in pumps if n.endswith('-head'))
    wall=82.515
    candidate=76.5
    bands=[]
    for name, mesh, _ in pumps:
        if not name.endswith('-head'): continue
        low,high=mesh.bounds
        region=box([low[0],head_rear,low[2]],[high[0],wall,high[2]])
        bands.append((name+' flange-to-wall span — includes retainer stock',region,[1.,.52,.08],.4))
    bay=boolean('intersection',front,box([-108.,4.,136.],[108.,123.,245.]))
    study_plane=box([-104.5,candidate-.06,175.],[104.5,candidate+.06,245.])
    gap_rows=[('Production pump bay — section',bay,[.31,.33,.36],.3),*pumps,
        ('Current seated retainer',retainer,[.24,.31,.37],.25),*bands,
        ('Wall-position study — retainer and tee stack need matching revision',study_plane,[.1,.52,.95],.35)]
    gap_view=save('pump-port-space',gap_rows,render=True)
    section=box([-86.,-48.,-24.],[86.,48.,1.]); section.apply_transform(frame)
    seat=boolean('intersection',front,section)
    detail=[('Production housing — section',seat,[.30,.32,.35]),*screens,*gasket_world,*cover_world,*hardware_world]
    display_view=save('display-side-screws',detail,render=True)
    exploded=[('Production housing — section',seat,[.30,.32,.35]),*screens,*placed(gasket_rows,5.),
        *placed(cover_rows,14.)]
    for name, mesh, color in fasteners:
        exploded.extend(placed([(name,mesh,color)],28. if 'screw' in name else 0.))
    exploded_view=save('display-side-screws-separated',exploded,render=True)
    context=[]
    for piece in ('front-bottom','back-bottom','front-top','back-top'):
        context.extend(read(ENC/f'enclosure-{piece}.step.mesh'))
    context.extend(fitted);context.extend(pumps);context.extend(screens)
    context.extend(cover_world);context.extend(gasket_world);context.extend(hardware_world)
    context.extend((n,m,c) for n,m,c in selected if n.startswith('funnel'))
    full_view=save('display-side-screws-full-context',context,render=True)
    records=dict(geometry='Current production front-top, display bezel, gasket and hardware. Orange marks the flange-to-wall span, including existing retainer stock. Blue marks a proposed wall position; both are layout annotations.',
        display_frame_world=frame.tolist(), display_module_normal_adjustment_mm=display_shift,
        dimensions=dimensions, cover_enclosure_overlap_mm3=cover_overlap, screws=screw_readings,
        pilot_backing=pilot_readings, tee_wall_bores_open=open_bores, tube_loading_slots_closed=closed_slots,
        front_top_watertight=front.is_watertight, cover_watertight=cover.is_watertight,
        pump_gap=dict(axis='Y',rigid_flange_rear_y_mm=head_rear,wall_front_y_mm=wall,gap_mm=wall-head_rear,
            study_wall_front_y_mm=candidate,study_shift_mm=wall-candidate,study_flange_gap_mm=candidate-head_rear,
            scope='Wall-position study only. The retainer aft edge, wing Y span, tee stack and fore valve supports require a coordinated revision before moving this wall.'),
        views=dict(pump_space=gap_view,display=display_view,separated=exploded_view,full_context=full_view),
        source_sha256={str(p.relative_to(ROOT)):sha for p,sha in READ_SHA.items()})
    records['source_sha256'][str((ENC/'enclosure-front-top.stl').relative_to(ROOT))]=hashlib.sha256((ENC/'enclosure-front-top.stl').read_bytes()).hexdigest()
    (HERE/'review.json').write_text(json.dumps(records,indent=2)+'\n')
    print(json.dumps({k:records[k] for k in ['cover_enclosure_overlap_mm3','screws','pilot_backing','tee_wall_bores_open','tube_loading_slots_closed','pump_gap']},indent=2),flush=True)


if __name__=='__main__':
    main()
