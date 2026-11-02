"""Check the broad production pump block against its cap and installed hardware."""
from pathlib import Path
import hashlib,json,sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path[:0]=[str(ROOT/'hardware/scripts'),str(ROOT/'hardware/printed-parts/cadlib'),
             str(ROOT/'hardware/printed-parts/cold-core'),str(ROOT/'hardware/manifold-layout')]
import cadquery as cq
import above_core
import above_core_parts as refs
import _above_core_mounts as mounts
import rear_snaps as snaps
from _cadq_export import export_step
from print_mesh import write_print_stl


def main():
    out=ROOT/'.cache/rear-snap-review'
    datum=mounts.pump_cradle_datums()
    cx,cy,cz=datum['centre_world_mm'];fy=datum['frame']['translation_mm'][1]
    face=above_core.specification()['cap_face_z_mm']
    fore,rear=datum['selected']['rail_stop_native_x_mm']
    wide=datum['stock_half_width_mm']+3.
    channel_fore=datum['selected']['cover_channel_fore_native_x_mm']
    plate=snaps.box(cx-wide-3,cx+wide+3,fy+min(fore[0],channel_fore)-3,fy+rear[1]+3,face-7.4,face)
    raw_mount=mounts.pump_cradle()
    recess=mounts.pump_lid_clearance()
    base=plate.fuse(raw_mount).cut(recess).clean()
    mount=raw_mount.cut(recess)
    cap=mounts.pump_snap_cap()
    assert cap.isValid() and len(cap.Solids())==1
    assert base.isValid() and len(base.Solids())==1
    assert base.intersect(cap).Volume()<1.e-7
    blocked=base.intersect(cap.translate((0,0,.75))).Volume()
    assert abs(blocked-28.34)<1.e-6
    objects=refs.components()
    b=mount.BoundingBox();neighbors={}
    for name,(shape,*_) in objects.items():
        if any(word in name for word in ('wire','wago')):continue
        q=shape.BoundingBox()
        if not (q.xmax>=b.xmin and q.xmin<=b.xmax and q.ymax>=b.ymin and q.ymin<=b.ymax and q.zmax>=b.zmin and q.zmin<=b.zmax):continue
        overlap=mount.intersect(shape).Volume()
        neighbors[name]=overlap
        assert overlap<1.e-5,(name,overlap)
    mesh=write_print_stl(base,HERE/'parts/production-pump-base.stl')
    export_step(base,str(out/'production-pump-base.step'))
    current_cap=write_print_stl(mounts.pump_snap_printable(),HERE/'parts/pump-box-cap.stl')
    assert current_cap.is_watertight
    export_step(mounts.pump_snap_printable(),str(out/'pump-box-cap.step'))
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    printed_cap=sha(HERE/'parts/pump-cap.stl')
    current_cap_digest=sha(HERE/'parts/pump-box-cap.stl')
    report={'native_valid':True,'solids':1,'watertight':bool(mesh.is_watertight),
      'faces':len(base.Faces()),'edges':len(base.Edges()),'volume_mm3':base.Volume(),
      'central_channel_width_mm':49.62,
      'channel_floor_world_z_mm':face-datum['selected']['cover_channel_recess_mm'],
      'channel_recess_mm':datum['selected']['cover_channel_recess_mm'],
      'remaining_lid_floor_mm':7.4-datum['selected']['cover_channel_recess_mm'],
      'cap_crown_mm':datum['selected']['cap_arch_wall_mm'],
      'cap_valid':True,'cap_solids':1,'cap_watertight':True,
      'cap_faces':len(cap.Faces()),'cap_edges':len(cap.Edges()),'cap_volume_mm3':cap.Volume(),
      'rail_bearing_widths_mm':[abs(r['outer_y_mm'])-24.81 for r in datum['rail_rooms']],
      'retention_bearing_mm2':blocked/.1,'seated_cap_intersection_mm3':0.,
      'installed_hardware_intersections_mm3':neighbors,'printed_cap_sha256':printed_cap,
      'production_cap_sha256':current_cap_digest,
      'production_cap_identical_to_printed_sample':current_cap_digest==printed_cap,
      'scope':'Broad carved base and filled box half-pipe cap. The flat catches remain unchanged; the body has a doubled crown. The previously launched arch cap is a baseline specimen. Physical holding force, body movement and vibration remain to be tested.',
      'input_sha256':{p:sha(ROOT/p) for p in ('hardware/printed-parts/cold-core/_above_core_mounts.py',
        'hardware/printed-parts/cold-core/foam-cap/foam_cap.rs','hardware/manifold-layout/above-core.json',
        'hardware/reference/g-ganen-pump/reference-parameters.json')}}
    (HERE/'production-pump-block.json').write_text(json.dumps(report,indent=2)+'\n')
    center=cq.Vector(cx,cy,(cap.BoundingBox().zmin+cap.BoundingBox().zmax)/2.)
    knife=snaps.box(-500,500,0,500,-500,500)
    def geometry(shape):
        v,f=shape.tessellate(.025,.08)
        return {'v':[[round(p.x,4),round(p.y,4),round(p.z,4)] for p in v],'f':[list(t) for t in f]}
    data={'full':{},'section':{},'bearing_mm':2.6,'leaf_mm':1.3}
    for name,shape in [('receiver',base),('cap',cap)]:
        shape=shape.translate(-center)
        data['full'][name]=[geometry(shape)];data['section'][name]=[geometry(shape.intersect(knife))]
    (out/'pump-block-geometry.json').write_text(json.dumps(data,separators=(',',':')))
    print(json.dumps(report,indent=2),flush=True)


if __name__=='__main__':main()
