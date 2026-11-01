"""Manual native reading of the bare G Ganen installation and exported lid.

No producer, printer or automatic build check is started. Run after exporting
current geometry; each report binds the inputs and artifacts it measured.
"""
from pathlib import Path
from argparse import ArgumentParser
import hashlib
import json
import sys
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path[:0]=[str(ROOT/'hardware/scripts'),str(ROOT/'hardware/manifold-layout'),
             str(ROOT/'hardware/printed-parts/cold-core')]
import cadquery as cq
from _cadq_export import import_step
import above_core as layout
import above_core_parts as parts
import _above_core_mounts as mounts
import g_ganen_installation as pump
import fits


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bounds(shape):
    b=shape.BoundingBox()
    return [[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]]


def run(*,include_routes=True,output=HERE/'native-installation-check.json'):
    started=time.monotonic()
    lid_path=ROOT/'hardware/printed-parts/cold-core/foam-cap/foam-cap-lid-top.step'
    inputs=[Path(__file__),HERE/'g_ganen_installation.py',Path(layout.__file__),
            Path(parts.__file__),Path(mounts.__file__),
            ROOT/'hardware/manifold-layout/above-core.json',
            pump.REFERENCE/'reference-parameters.json',lid_path]
    bindings={str(p.relative_to(ROOT)):sha(p) for p in inputs}
    shape=parts.pump_native().moved(layout.location('g-ganen-pump'))
    lid=import_step(str(lid_path)).val().moved(layout.frame_location(layout.cap_lid_pose()))
    bearing=mounts.pump_cradle()
    caps=[mounts.pump_snap_cap(i) for i in range(len(mounts.pump_cradle_datums()['caps']))]
    bb=shape.BoundingBox()
    # Restrict the material reading to the pump bay before the expensive common.
    bay=cq.Solid.makeBox(bb.xlen+.02,bb.ylen+.02,bb.zlen+.02,
        cq.Vector(bb.xmin-.01,bb.ymin-.01,bb.zmin-.01))
    stock=lid.intersect(bay)
    common=sum(s.Volume() for s in shape.intersect(stock).Solids())
    checks=[]
    def check(label,value,limit,relation='<='):
        good=value<=limit if relation=='<=' else value>=limit
        checks.append(dict(check=label,value=value,limit=limit,relation=relation,**{'pass':good}))
        print(label,value,'PASS' if good else 'FAIL',flush=True)
    check('installed rubber sliders',len(pump.feet_shapes()),0)
    check('pump foot screw axes',len(pump.mount_holes()),0)
    check('pump cup columns',int('g-ganen-pump' in mounts.deck_mounts()),0)
    check('bare casing front bearing allowance',
          abs(bb.zmin-layout.specification()['cap_face_z_mm']-fits.slip),1.e-5)
    check('pump overlap with installed lid',common,1.e-5)
    check('cradle native invalid',int(not bearing.isValid()),0)
    for i,cap in enumerate(caps):
        check(f'snap cap {i+1} native invalid',int(not cap.isValid()),0)
        check(f'snap cap {i+1} unexpected solid count',int(len(cap.Solids()) != 1),0)
        check(f'snap cap {i+1} overlap with pump',sum(s.Volume() for s in cap.intersect(shape).Solids()),1.e-5)
        check(f'snap cap {i+1} overlap with lid',sum(s.Volume() for s in cap.intersect(lid).Solids()),1.e-5)
    routes=[]
    if include_routes:
        import rear_plumbing
        for name,spec in rear_plumbing.route_specs().items():
            if 'pump-inlet' not in name:continue
            tube=parts.route_shape(spec)
            check(name+' native invalid',int(not tube.isValid()),0)
            routes.append(dict(id=name,segments=spec['segments'],owners=spec['owners']))
    out=dict(schema='g-ganen-installation/4',inputs=bindings,
        scope='Bare casing and fixed rails, integral motor half pipe, open rigid-body admission rooms, rail-end stops and removable upper snap. Native nominal geometry does not qualify spring force, vibration, printed fit or hose retention.',
        local_to_world=layout.pose('g-ganen-pump'),installed_bounds_mm=bounds(shape),
        cradle_bounds_mm=bounds(bearing),snap_cap_bounds_mm=[bounds(cap) for cap in caps],
        mount=mounts.pump_cradle_datums(),selected_feet=[],mount_rows=[],
        routes_checked=include_routes,routes=routes,checks=checks,
        all_pass=all(r['pass'] for r in checks),elapsed_seconds=time.monotonic()-started)
    if bindings!={str(p.relative_to(ROOT)):sha(p) for p in inputs}:
        raise RuntimeError('Installation inputs changed during reading')
    output.write_text(json.dumps(out,indent=2)+'\n')
    if not out['all_pass']:raise SystemExit(1)
    return out


if __name__=='__main__':
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('--skip-routes',action='store_true')
    parser.add_argument('--output',type=Path,default=HERE/'native-installation-check.json')
    args=parser.parse_args()
    run(include_routes=not args.skip_routes,output=args.output)
