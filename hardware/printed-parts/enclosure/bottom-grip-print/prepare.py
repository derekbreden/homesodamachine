"""Slice production bottoms with the physically accepted grip-slot bridges."""
from pathlib import Path
import argparse, hashlib, json, subprocess, sys, zipfile
import xml.etree.ElementTree as ET
import numpy as np
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/'tools').is_dir())
ENC = HERE.parent/'enclosure'
sys.path[:0] = [str(ENC),str(ROOT/'hardware/printed-parts/faucet')]
import enclosure as shell
import refresh_print_project as writer

NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
ET.register_namespace('',NS)
def tag(n): return '{'+NS+'}'+n
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main(printer, revision):
    piece,trim={'H2C':('front',.18),'Mark2':('back',.04)}[printer]
    name=f'enclosure-{piece}-bottom'
    stem=f'{name}-grip-bridges-{printer.lower()}-v{revision}'
    job=ROOT/'.cache/prints'/stem
    project=job/f'{stem}-input.3mf'
    if project.exists(): raise FileExistsError('Reviewed slice inputs are immutable; increment revision.')
    job.mkdir(parents=True,exist_ok=True)
    profile=ROOT/'hardware/printed-parts/petgf.3mf'
    report=writer.refresh(profile,project,parts=((name,ENC/f'{name}.stl',0.),),
                          offsets=((0.,0.),),z_trim=trim,
                          title=f'{piece.title()} bottom; accepted grip bridges; {printer}')
    with zipfile.ZipFile(project) as archive:
        members={n:archive.read(n) for n in archive.namelist()}
    settings=json.loads(members[writer.SETTINGS_MEMBER])
    settings.update(layer_height='0.24',initial_layer_print_height='0.2',
                    support_filament='1',support_interface_filament='1',flush_into_support='0')
    assert settings['support_type']=='tree(auto)'
    assert settings['wall_sequence']=='inner wall/outer wall'
    assert settings['infill_wall_overlap']=='15%' and settings['is_infill_first']=='0'
    members[writer.SETTINGS_MEMBER]=json.dumps(settings,indent=2).encode()
    ranges=ET.Element('objects');obj=ET.SubElement(ranges,'object',id='1')
    for lo,hi,height,walls in [(35.,41.5,.24,6),(41.5,44.3,.08,None)]:
        band=ET.SubElement(obj,'range',min_z=str(lo),max_z=str(hi))
        ET.SubElement(band,'option',opt_key='layer_height').text=str(height)
        if walls: ET.SubElement(band,'option',opt_key='wall_loops').text=str(walls)
    members['Metadata/layer_config_ranges.xml']=ET.tostring(ranges,encoding='utf-8',xml_declaration=True)
    part,=report['parts'];tree=ET.fromstring(members[part['member']])
    vertices=np.array([[float(v.get(a)) for a in 'xyz'] for v in tree.iter(tag('vertex'))])+part['source_center_mm']
    triangles=list(tree.iter(tag('triangle')))
    points=vertices[np.array([[int(t.get(a)) for a in ('v1','v2','v3')] for t in triangles])]
    normals=np.cross(points[:,1]-points[:,0],points[:,2]-points[:,0]);nz=normals[:,2]/np.maximum(np.linalg.norm(normals,axis=1),1e-30)
    grip=shell.grip_interface()
    roof=grip.ROOF;mouth=shell._handhold_y()[0 if piece=='front' else 1]
    ymin,ymax=((mouth-shell.handhold_wall-.01,mouth+.01) if piece=='front' else (mouth-.01,mouth+shell.handhold_wall+.01))
    half=grip.WING_SPAN/2+grip.WING_END_AIR
    slots=[box(side*grip.X_CENTER-half-.001,ymin,side*grip.X_CENTER+half+.001,ymax) for side in (-1,1)]
    blocked=unary_union(slots)
    # The slot's entry relief extends 0.10 mm past the nominal wall. Include
    # triangles crossing that relief when painting the complete slot roof.
    flat=(np.max(np.abs(points[:,:,2]-roof),axis=1)<.0001)&(nz<-.99)&(np.min(np.abs(points[:,:,0]),axis=1)>=grip.INNER_FACE-shell.handhold_wall-.001)&(np.min(points[:,:,1],axis=1)>=shell._handhold_y()[0]-shell.handhold_wall-.12)&(np.max(points[:,:,1],axis=1)<=shell._handhold_y()[1]+shell.handhold_wall+.12)
    exterior=(np.min(np.abs(points[:,:,0]),axis=1)>=grip.INNER_FACE-.001)&(np.min(points[:,:,1],axis=1)>=shell._handhold_y()[0]-shell.handhold_corner_r-.01)&(np.max(points[:,:,1],axis=1)<=shell._handhold_y()[1]+shell.handhold_corner_r+.01)&(np.min(points[:,:,2],axis=1)>=roof-shell.handhold_edge_r-.01)&(np.max(points[:,:,2],axis=1)<=roof+shell.handhold_edge_r+3.05)&(nz<-.00001)&~flat
    assert flat.sum()>0 and exterior.sum()>0
    flat_area=unary_union([Polygon(p[:,:2]) for p in points[flat]])
    # Whole-enclosure trees can grow past the blocked contact boundary.
    # Keep their wider interface roads away from the slot mouths as well.
    slot_support_halo=1.0
    permitted=flat_area.buffer(-.8).difference(blocked.buffer(slot_support_halo,join_style=2))
    blocked_area=0.;slot_area=0.
    def encode(p,depth=0):
        nonlocal blocked_area,slot_area
        polygon=Polygon(p[:,:2])
        if permitted.covers(polygon): return '0'
        if not permitted.intersects(polygon) or depth==10:
            blocked_area+=polygon.area;slot_area+=polygon.intersection(blocked).area
            return '8'
        a,b,c=p;ab,bc,ca=(a+b)/2,(b+c)/2,(c+a)/2
        return ''.join(encode(np.array(q),depth+1) for q in ((a,ab,ca),(ab,b,bc),(bc,c,ca),(ab,bc,ca)))+'3'
    for triangle,pts,isflat,isexterior in zip(triangles,points,flat,exterior):
        if isexterior: triangle.set('paint_supports','8')
        elif isflat: triangle.set('paint_supports',encode(pts))
    assert 30<slot_area<35,(slot_area,blocked_area)
    members[part['member']]=ET.tostring(tree,encoding='utf-8',xml_declaration=True)
    writer.archive_write(project,members)
    np.savez_compressed(job/"support-review-geometry.npz", exterior_triangles=points[exterior])
    report.update(printer_target=printer,piece=piece,revision=revision,stem=stem,project=project.name,
        requested_trim_mm=trim,project_sha256=sha(project),settings_sha256=hashlib.sha256(members[writer.SETTINGS_MEMBER]).hexdigest(),
        slot_bounds_cad_xy_mm=[list(s.bounds) for s in slots],slot_roof_cad_z_mm=roof,
        slot_floor_cad_z_mm=grip.BACK-grip.WING_THICK-grip.BEARING_AIR,
        support_review_geometry_sha256=sha(job/"support-review-geometry.npz"),
        blocked_slot_area_mm2=slot_area,blocked_ceiling_edge_area_mm2=blocked_area-slot_area,
        painted_exterior_triangles=int(exterior.sum()),painted_flat_triangles=int(flat.sum()),
        six_wall_print_z_mm=[35.,41.5],fine_flute_runout_print_z_mm=[41.5,44.3],
        flat_ceiling_support_inset_mm=.8,submitted=False,
        slot_support_halo_mm=slot_support_halo,
        source_sha256={str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),profile,ENC/f'{name}.stl',ENC/f'{name}.step',ENC/'_grip_interface.py',ENC/'enclosure.py']})
    (job/'preparation.json').write_text(json.dumps(report,indent=2)+'\n')
    ready=job/'ready';ready.mkdir()
    command=['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio','--slice','0','--arrange','0','--orient','0','--outputdir',str(ready),'--export-3mf',f'{stem}.gcode.3mf',str(project)]
    (job/'slice-command.json').write_text(json.dumps(command,indent=2)+'\n')
    with (ready/'slice.log').open('w') as log: rc=subprocess.run(command,cwd=ready,stdout=log,stderr=subprocess.STDOUT).returncode
    print(json.dumps({'printer':printer,'job':str(job),'slice_exit':rc,'blocked_slot_area_mm2':slot_area}),flush=True)
    return rc

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('printer',choices=('H2C','Mark2'));p.add_argument('--revision',type=int,default=1)
    a=p.parse_args();raise SystemExit(main(a.printer,a.revision))
