"""Upright 4P cable clips with9 mm rectangular hosts and16/24 mm spans.

Manual geometry generation only. Keeps relay_ribbon_trial.py and its exports
unchanged; creates no production geometry or print job.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import cadquery as cq

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
ORIGINAL=HERE/'relay_ribbon_trial.py'
HOST_WALL=9.0
SPANS=(16.0,24.0)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path):
    return str(Path(path).relative_to(ROOT))


def box(lo,hi):
    return cq.Solid.makeBox(*[b-a for a,b in zip(lo,hi)],cq.Vector(*lo))


def main():
    spec=importlib.util.spec_from_file_location('wall9_original_relay_clip',ORIGINAL)
    base=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base)
    previous_report_path=HERE/'geometry-report.json'
    previous=json.loads(previous_report_path.read_text())
    original_paths=[ORIGINAL,previous_report_path,*[ROOT/p for p in previous['files']]]
    original_hashes={rel(p):sha(p)for p in original_paths}
    if previous['source_sha256']!=sha(ORIGINAL):
        raise ValueError('Original geometry report does not bind its current source')
    if any(sha(ROOT/p)!=digest for p,digest in previous['files'].items()):
        raise ValueError('Original exported geometry differs from its report')
    if base.STOCK!=3.0 or base.WALL_BELOW_HOOK!=6.0 or abs(base.TOP-19.7)>1e-8:
        raise ValueError('Expected accepted3 mm hook section,6 mm wall extension and19.7 mm hook height')
    original_installed,_,_=base.build()
    window=box((0.,-base.SPAN/2,0.),(base.PROJECTION,base.SPAN/2,base.TOP))
    original_clip=original_installed.intersect(window)
    parts=HERE/'parts'
    parts.mkdir(exist_ok=True)
    variants=[]
    files={}
    for span in SPANS:
        run=span+12.
        wall=cq.Solid.makeBox(HOST_WALL,run,base.TOP+base.WALL_BELOW_HOOK,
                             cq.Vector(-HOST_WALL,-run/2,-base.WALL_BELOW_HOOK))
        clip=base.prism(base.SECTION,span)
        installed=wall.fuse(clip).clean()
        printed=base.print_pose(installed).clean()
        cropped=installed.intersect(window)
        missing=abs(original_clip.cut(cropped).Volume())
        extra=abs(cropped.cut(original_clip).Volume())
        centers=[]
        conductors=[]
        for i in range(4):
            x,z=base.GAP/2,base.SEAT_FLOOR+.25+base.WIRE_OD/2+i*base.RIBBON_PITCH
            centers.append([x,z])
            conductors.append(cq.Solid.makeCylinder(base.WIRE_OD/2,run,
                cq.Vector(x,-run/2,z),cq.Vector(0,1,0)))
        cable=cq.Compound.makeCompound(conductors)
        overlap=abs(installed.intersect(cable).Volume())
        clearance=installed.distance(cable)
        bed_faces=[f for f in printed.Faces()if f.geomType()=='PLANE'
                   and f.normalAt().z<-.9999 and abs(f.Center().z)<1e-5]
        if not printed.isValid()or len(printed.Solids())!=1:
            raise ValueError('Each complete coupon must be one valid native solid')
        if overlap>1e-8 or abs(clearance-.25)>1e-7 or missing>1e-8 or extra>1e-8:
            raise ValueError('Accepted section or seated cable clearance changed')
        stem=f'relay-ribbon-wall9-span{int(span)}'
        stl,step=parts/(stem+'.stl'),parts/(stem+'.step')
        cq.exporters.export(printed,str(stl),tolerance=.025,angularTolerance=.10)
        cq.exporters.export(printed,str(step))
        files.update({rel(p):sha(p)for p in (stl,step)})
        variants.append(dict(
            id=f'span{int(span)}',span_along_cable_mm=span,
            stl=rel(stl),step=rel(step),
            dimensions=dict(ribbon_width_mm=3*base.RIBBON_PITCH+base.WIRE_OD,
                ribbon_depth_mm=base.WIRE_OD,seat_depth_mm=base.GAP,
                seat_height_mm=base.SEAT_HEIGHT,mouth_depth_mm=base.MOUTH,
                hook_stock_mm=base.STOCK,beak_projection_mm=base.BEAK,
                projection_from_wall_mm=base.PROJECTION,host_wall_mm=HOST_WALL,
                host_run_mm=run,wall_below_hook_mm=base.WALL_BELOW_HOOK,
                overall_print_height_mm=base.TOP+base.WALL_BELOW_HOOK),
            print_native=base.signature(printed),installed_native=base.signature(installed),
            native_cross_section_comparison=dict(
                method='Native air-side solids compared in original central8 mm Y span; host excluded.',
                missing_mm3=missing,extra_mm3=extra,identical=True),
            readings=dict(native_seated_overlap_mm3=overlap,native_seated_clearance_mm=clearance,
                conductor_centers_installed_xz_mm=centers,
                conductor_centers_print_xz_mm=[[x,z+base.WALL_BELOW_HOOK]for x,z in centers],
                bed_contact_face_areas_mm2=sorted(f.Area()for f in bed_faces),
                total_native_bed_contact_mm2=sum(f.Area()for f in bed_faces)),
            print_pocket_bounds_mm=[0.,-span/2,base.SEAT_FLOOR+base.WALL_BELOW_HOOK,
                base.GAP,span/2,base.SEAT_ROOF+base.WALL_BELOW_HOOK],
            print_entry_core_bounds_mm=[0.,-span/2,base.SEAT_ROOF+base.WALL_BELOW_HOOK,
                base.MOUTH,span/2,base.TOP+base.WALL_BELOW_HOOK],
            corbel=dict(build_start_z_mm=base.WALL_BELOW_HOOK,
                build_end_z_mm=base.WALL_BELOW_HOOK+base.PROJECTION,slope_degrees=45.),
            retaining_lip=dict(projection_mm=base.BEAK,
                build_underside_z_mm=base.SEAT_ROOF+base.WALL_BELOW_HOOK)))
    if original_hashes!={rel(p):sha(p)for p in original_paths}:
        raise ValueError('An original input/export changed during generation')
    report=dict(
        scope='Two standalone cable-fit/spring-survival coupons; no production or wiring changes.',
        source=rel(Path(__file__)),source_sha256=sha(Path(__file__)),
        original_source=rel(ORIGINAL),original_source_sha256=sha(ORIGINAL),
        original_input_sha256=original_hashes,
        original_section_xz_mm=base.SECTION,
        intended_stock='BNTECHGO22 AWG black silicone4P J5 RELAYS ribbon',
        stock_basis='Modeled1.70 mm insulated OD on1.85 mm pitch; physical full-ribbon section unmeasured.',
        print_pose='Upright installed section translated+6 mm in Z; wall edge flat atZ0, entry+Z; no rotation.',
        identification='No raised geometry labels. Filenames/plate identities span16 and span24; rectangular host Y runs28 and36 mm respectively.',
        support_requirement='No brim and no supports inside the seat or entry. Native slice/path review required; geometry alone is not support acceptance.',
        variants=variants,files=files,
        evaluation='Actual ribbon insertion, retention, axial slide, release and layer/root survival remain physical observations.')
    (HERE/'wall9-span-geometry.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)


if __name__=='__main__':
    main()
