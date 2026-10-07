"""Read supplier-required radial backing from current stock and native model roads.

The emitted radial section uses each model road's own width and layer slab.
It establishes nominal deposition, without measuring strength or lifetime.
"""
from pathlib import Path
import argparse,hashlib,json,sys,zipfile
import numpy as np
import shapely
from shapely.geometry import LineString,box
import trimesh
from review_roads import layers,MODEL
from review_dense_regions import sections
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'tools/docgen').is_dir())

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def stations():
    # Reuse the current station definitions, without loading the six native parts
    # or overwriting the separate whole-enclosure qualification record.
    source=ROOT/'hardware/printed-parts/enclosure/enclosure/heat-set-review/audit.py'
    text=source.read_text().split('\nshapes={}')[0]
    ns={'__file__':str(source)};exec(compile(text,str(source),'exec'),ns)
    return [r for r in ns['station_rows'] if r['piece']=='back-top' and r['family']=='electronics']

def spans(shape,ray):
    origin=np.array(ray.coords[0]);direction=np.array(ray.coords[-1])-origin;direction/=np.linalg.norm(direction)
    out=[]
    for part in shapely.get_parts(shape.intersection(ray)):
        if part.geom_type=='LineString' and part.length>.001:
            ends=(np.array(part.coords)[[0,-1]]-origin)@direction
            out.append([float(ends.min()),float(ends.max())])
    return sorted(out)

def native_stock():
    """Read full cylindrical supplier envelopes in the current back-top STEP."""
    source=ROOT/'hardware/printed-parts/enclosure/enclosure/heat-set-review/audit.py'
    text=source.read_text();prefix=text.split('\nshapes={}')[0]
    body=text[text.index('\ndef cylinder'):text.index('\nseam=[]')]
    setup="\nstation_rows=[r for r in station_rows if r['piece']=='back-top']\nshapes={'back-top':cq.importers.importStep(str(ENC/'enclosure-back-top.step')).val()}\n"
    ns={'__file__':str(source)};exec(compile(prefix+setup+body,str(source),'exec'),ns)
    rows=ns['station_rows'];enc=ROOT/'hardware/printed-parts/enclosure/enclosure'
    result={'scope':'Current back-top complete native insert envelopes. Supplier nominal pilot, radial surrounding-wall stock, blind relief, cap closure and whole-knurl insertion access. No printed fit, strength or lifetime qualification.',
        'reviewer_sha256':sha(__file__),'station_driver_sha256':sha(source),
        'source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in ns['source_paths']},
        'source_step_sha256':sha(enc/'enclosure-back-top.step'),'source_stl_sha256':sha(enc/'enclosure-back-top.stl'),
        'stations':rows,'passed':all(r['stock_rule_pass'] and r['blind_relief_pass'] and r['pocket_clear_pass'] and r['closed_blind_pass'] and r.get('insertion_access_pass',True) and r.get('screw_reach_pass',True) and r['manufacturer_pilot_pass'] is not False for r in rows)}
    (Path(__file__).parent/'reviews/insert-stock.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Current native insert stock',result['passed'],len(rows),flush=True)
    return result

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('job',type=Path,nargs='?',default=ROOT/'.cache/prints/2026-10-07-drain/back-top-mark2');ap.add_argument('--native-stock',action='store_true');args=ap.parse_args()
    if args.native_stock:
        native_stock();return
    job=args.job.resolve()
    prep=job/'back-top-black-z004-mark2.preparation.json';p=json.loads(prep.read_text());part=p['parts'][0];archive=job/'ready/back-top-black-z004-mark2.gcode.3mf';source=ROOT/part['source'];assert sha(source)==part['stl_sha256']
    center=np.array(part['source_center_mm']);rotation=np.array(part['build_transform'][:9]).reshape(3,3);translation=np.array(part['build_transform'][9:]);mesh=trimesh.load(source,force='mesh',process=True);mesh.vertices=(mesh.vertices-center)@rotation+translation
    records=[];targets=[]
    for row in stations():
        r={**row,'depth_samples':[]};records.append(r)
        for depth in [.2,1.,2.,3.,3.8]:
            point=(np.array(row['seat_mm'])+np.array(row['into'])*depth-center)@rotation+translation
            target={'record':len(records)-1,'depth_mm':depth,'point':point,'filled':[]};targets.append(target)
    with zipfile.ZipFile(archive) as z:
        for height,slab,roads,_ in layers(z.open('Metadata/plate_1.gcode')):
            wanted=[t for t in targets if abs(height-slab/2-t['point'][2])<4.5]
            if not wanted:continue
            roads=[r for r in roads if r[6]==part['identify_id'] and r[7] in MODEL]
            if not roads:continue
            a=np.array([r[:4] for r in roads]);width=np.array([r[4] for r in roads])
            low=np.minimum(a[:,:2],a[:,2:4])-width[:,None]/2;high=np.maximum(a[:,:2],a[:,2:4])+width[:,None]/2
            for t in wanted:
                x,y,z0=t['point'];hits=np.flatnonzero((low[:,1]<=y)&(high[:,1]>=y)&(low[:,0]<x+4.5)&(high[:,0]>x-4.5))
                if not len(hits):continue
                lines=np.array([LineString((roads[i][:2],roads[i][2:4])) for i in hits],dtype=object);beads=shapely.union_all(shapely.buffer(lines,width[hits]/2,quad_segs=64));ray=LineString(((x-5,y),(x+5,y)))
                for interval in shapely.get_parts(beads.intersection(ray)):
                    if interval.geom_type=='LineString' and interval.length>.001:t['filled'].append(box(interval.bounds[0],round(height-slab,5),interval.bounds[2],round(height,5)))
    cached={}
    for t in targets:
        row=records[t['record']];x,y,z=t['point'];key=round(y,6)
        if key not in cached:
            edges=trimesh.intersections.mesh_plane(mesh,[0,1,0],[0,y,0]);cached[key]=sections(edges[:,:,[0,2,1]])
        stock=cached[key];beads=shapely.union_all(t['filled']);samples=[]
        for degrees in range(0,360,45):
            radians=np.radians(degrees);direction=np.array([np.cos(radians),np.sin(radians)]);origin=np.array([x,z]);ray=LineString((origin,origin+direction*5.5))
            nominal=spans(stock,ray);nominal=[s for s in nominal if s[0]>=row['pilot_mm']/2-.25]
            first=nominal[0] if nominal else None
            inside=spans(beads,ray)
            outer=[] if first is None else [v for v in inside if v[1]>=first[0]+.1 and v[0]>=row['pilot_mm']/2-.5]
            fill=outer[0] if outer else None
            reach=0 if fill is None else fill[1]-fill[0]
            available=0 if first is None else first[1]-first[0]
            pilot=None if fill is None else fill[0]
            samples.append({'angle_degrees':degrees,'native_radial_stock_mm':available,
                'native_pilot_radius_mm':None if first is None else first[0],
                'printed_pilot_radius_mm':pilot,
                'printed_pilot_growth_mm':None if first is None or pilot is None else pilot-first[0],
                'nominal_knurl_radius_mm':2.3,
                'nominal_knurl_contact_depth_mm':None if pilot is None else max(0.,2.3-pilot),
                'printed_bore_protrusion_beyond_knurl_mm':None if pilot is None else max(0.,pilot-2.3),
                'printed_stock_intervals_mm':outer,
                'connected_nominal_radial_backing_mm':reach,
                'passed':available>=row['minimum_wall_mm'] and reach>=row['minimum_wall_mm']})
        row['depth_samples'].append({'insert_depth_mm':t['depth_mm'],'plate_axis_point_mm':t['point'].tolist(),'radial_readings':samples,'passed':all(s['passed'] for s in samples)})
    for row in records:row['passed']=all(d['passed'] for d in row['depth_samples'])
    result={'native_archive_sha256':sha(archive),'source_stl_sha256':sha(source),'preparation_sha256':sha(prep),'enclosure_box_sha256':sha(ROOT/'hardware/manifold-layout/enclosure-box.json'),'stations':records,'reviewer_sha256':sha(__file__),'buffer_quadrant_segments':64,'sampling':'Five depths through every 4 mm electronics insert; eight radial rays in each native stock section. Emitted model roads use their own width and whole layer slab. The first printed stock interval outside the pilot is measured from its actual commanded bore contour, independently of the native pilot surface. Bore growth and nominal Ø4.6 brass contact are retained separately from connected outer-stock thickness.','scope':'Strict geometric pore/bore diagnostic from nominal native stock and commanded deposition. Finite interval gaps remain open; no closing tolerance is applied. This is independent of the regional coverage and complete native supplier-envelope checks. Layer bonding, actual bead shape, insert installation, strength and lifetime remain physical properties. Axial blind-cap length is a separate geometric property.','passed':all(r['passed'] for r in records)}
    (job/'insert-radial-backing.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'passed':result['passed'],'station_count':len(records),'failed':[(r['seat_mm'],[(d['insert_depth_mm'],[(s['angle_degrees'],round(s['connected_nominal_radial_backing_mm'],4)) for s in d['radial_readings'] if not s['passed']]) for d in r['depth_samples'] if not d['passed']]) for r in records if not r['passed']]},indent=2),flush=True)
if __name__=='__main__':main()
