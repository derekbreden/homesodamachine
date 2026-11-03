"""Crop complete retention samples from the current production printed surfaces."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT/p) for p in ('hardware/scripts','hardware/printed-parts/cadlib',
    'hardware/printed-parts/cold-core','hardware/manifold-layout')]
import _rust_part
_rust_part.start()
import numpy as np
import trimesh
import above_core
import rear_plumbing
import rear_snaps as snaps
import fits


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=HERE/'v4')
    parser.add_argument('--check-fit',action='store_true')
    parser.add_argument('--families',nargs='+',choices=('pump','asse','pisco','meter','regulator'),
                        default=['pump','asse','pisco','meter','regulator'])
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True,exist_ok=True)
    inputs = output/'inputs'
    inputs.mkdir(exist_ok=True)
    began = time.monotonic()
    digests = {}

    def printed_input(source, name):
        """Format conversion only: retain the exact welded STL vertices and triangles."""
        mesh = trimesh.load_mesh(source,process=True)
        if not mesh.is_watertight:
            raise ValueError(f'{source}: production STL is not watertight')
        path = inputs/(name+'.npz')
        record = [[{'kind':'MESH','src':str(source.relative_to(ROOT)),'op':'read-stl'}]]
        np.savez(path,names=np.frombuffer(json.dumps([name]).encode(),dtype=np.uint8),
            colors=np.frombuffer(b'[null]',dtype=np.uint8),
            records=np.frombuffer(json.dumps(record).encode(),dtype=np.uint8),
            V0=np.asarray(mesh.vertices,dtype=np.float64),T0=np.asarray(mesh.faces,dtype=np.uint32),
            F0=np.zeros(len(mesh.faces),dtype=np.uint32))
        digests[str(source.relative_to(ROOT))] = hashlib.sha256(source.read_bytes()).hexdigest()
        return str(path),mesh.bounds

    enclosure = ROOT/'hardware/printed-parts/enclosure/enclosure'
    foam = ROOT/'hardware/printed-parts/cold-core/foam-cap'
    caps = ROOT/'hardware/printed-parts/enclosure/rear-equipment-caps'
    rear,rb = printed_input(enclosure/'enclosure-back-top.stl','rear-parent')
    lid = None
    if 'pump' in args.families:
        lid,_ = printed_input(foam/'foam-cap-lid-top.stl','lid-parent')
    installed = caps/'rear-equipment-caps-installed.step.npz'
    cap_numbers = json.loads((caps/'rear-equipment-caps.numbers.json').read_text())
    with np.load(installed) as a:
        names = json.loads(a['names'].tobytes())
        bounds = {n:np.array([a[f'V{i}'].min(0),a[f'V{i}'].max(0)]) for i,n in enumerate(names)}
    cap_shift = None
    if 'pump' in args.families:
        pump = json.loads((foam/'foam-cap.numbers.json').read_text())['pump']
        st = pump['snap_station']
        cx,_,cz = pump['centre_world_mm']
        roof = -(pump['bore_radius_mm']+pump['selected']['cap_arch_wall_mm'])
        cap_shift = [cx,st['y0'],cz-(st['tip']+roof)/2.]
        fy = pump['frame']['translation_mm'][1]
        selected = pump['selected']
        span = selected['motor_band_native_x_mm'] + [v for p in selected['rail_stop_native_x_mm'] for v in p]
        width = pump['stock_half_width_mm']+3.
    families = []
    cap_sources = {}
    for name in args.families:
        source = foam/'pump-snap-cap.stl' if name=='pump' else caps/(name+'-snap-cap.stl')
        cap_sources[name] = source
        cap_model,pb = printed_input(source,name+'-cap')
        if name=='pump':
            corners=np.array([[x,z,-y] for x in pb[:,0] for y in pb[:,1] for z in pb[:,2]])+cap_shift
            b=np.array([corners.min(0),corners.max(0)])
            low=[cx-width,fy+min(span)-3.,above_core.specification()['cap_lid_pose']['translation_mm'][2]]
            high=[cx+width,fy+max(span)+3.,b[1,2]]
            scope='Both fixed motor-rail stops, cradle, complete spring pockets and actual lid stock.'
        else:
            b=bounds[name+'-snap-cap']
            low=(b[0]-3.).tolist();high=(b[1]+3.).tolist()
            if name in ('asse','pisco'):
                low[1]=b[0,1]-fits.running-snaps.WALL-3.
                high[1],high[2]=float(rb[1,1]),float(rb[1,2])
                scope='Complete front and rear shoulders, spring pockets, actual roof and full rear bulkhead bore.'
            elif name=='meter':
                meter_cap=next(c for c in cap_numbers['caps'] if c['name']=='meter-snap-cap')
                low[1]=next(c['span'][0] for c in meter_cap['cuts'] if c['op']=='cylinder-y')-3.
                high[0],high[1]=float(rb[1,0]),float(rb[1,1])
                scope='Complete meter cup, wire exit, port collars, spring pockets, side wall and rear soda bulkhead bore.'
            else:
                mount=rear_plumbing.regulator_datums()
                low[0],high[0]=-mount['seat_y'][1]-3.,-mount['seat_y'][0]+3.
                low[1],high[1]=mount['axis'][0]-mount['station']['outer']-3.,mount['axis'][0]+mount['station']['outer']+3.
                high[2]=float(rb[1,2])
                scope='Full measured axial profile, both end shoulders, spring pockets and actual roof.'
        families.append({'name':name,'cap_print_model':cap_model,'installed_name':name+'-snap-cap',
            'crop_min':low,'crop_max':high,'cap_translation':cap_shift if name=='pump' else None,
            'on':[0,0,-1] if name=='pump' else [1,0,0] if name=='meter' else [0,0,1],
            'retention_scope':scope})
    numbers={'rear_print_model':rear,'lid_print_model':lid,
        'lid_translation':above_core.specification()['cap_lid_pose']['translation_mm'],
        'installed_caps':str(installed),'families':families,'check_fit':args.check_fit,
        'assembly_model':str(ROOT/'hardware/manifold-layout/enclosure-assembly.step.npz')}
    folder=output/'parts'
    folder.mkdir(parents=True,exist_ok=True)
    _rust_part.cut('tooling','rear-snap-retention',numbers,folder)
    report={'scope':'Complete retention in X, Y and Z, cropped from production prints.',
        'families':json.loads((folder/'fit.json').read_text()),'input_sha256':digests,'parts':[],
        'pisco_cap_y_mm':snaps.pisco_cap_span(rear_plumbing.snap_datums()['mouth_y'],
            json.loads((ROOT/'hardware/reference/compact-inline-candidates/dimensions.json').read_text())['pisco_rvfup_quarter']['fitted_exterior']['component_ranges_mm']['outlet_collet'][0],rear_plumbing.snap_datums()['rear']),
        'physical_result':'Awaiting this print trial.'}
    for family in families:
        for suffix in ('seat','cap'):
            name=family['name']+'-'+suffix
            path=folder/(name+'.stl')
            if suffix=='cap':
                shutil.copyfile(cap_sources[family['name']],path)
            mesh=trimesh.load_mesh(path,process=True)
            if not mesh.is_watertight or len(mesh.split())!=1:
                raise ValueError(f'{name}: one watertight print required')
            report['parts'].append({'name':name,'stl':str(path.relative_to(ROOT)),
                'step':str(path.with_suffix('.step').relative_to(ROOT)),
                'stl_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                'bounds_mm':mesh.bounds.tolist(),'volume_mm3':float(mesh.volume),
                'watertight':True,'solids':1,
                'print_orientation':'Production axial end down.' if suffix=='cap' else
                    'Actual production lid +Z up.' if family['name']=='pump' else 'Actual production back-top -Z up.'})
    report['elapsed_seconds']=time.monotonic()-began
    (output/'geometry.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'Exported {2*len(families)} complete retention pieces.',flush=True)


if __name__=='__main__':
    main()
