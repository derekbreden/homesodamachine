"""Replace scoped named roof members in existing STEP and viewer aggregates.

Updates named XCAF prototypes in the original STEP document and uses the
repository's assembly reader and viewer graft. Existing hierarchy, colors and
component placements remain in that document; no placement is recomputed.
"""
from pathlib import Path
import hashlib,json,os,sys
import cadquery as cq
import numpy as np
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools').is_dir())
ENC=ROOT/'hardware/printed-parts/enclosure/enclosure'
FUNNEL=HERE.parent
sys.path[:0]=[str(ROOT/'hardware/scripts'),str(ENC),str(FUNNEL)]
from _cadq_export import import_assembly,_atomic_write
import _mesh_payload,flute_payload
import funnel_frame as ff

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def fingerprint(s):
    def rounded(xs):return [round(float(x),5) for x in xs]
    def bounds(b):return rounded([b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax])
    faces=sorted((f.geomType(),round(f.Area(),5),bounds(f.BoundingBox()),rounded(f.Center().toTuple())) for f in s.Faces())
    edges=sorted((e.geomType(),round(e.Length(),5),bounds(e.BoundingBox()),rounded(e.Center().toTuple())) for e in s.Edges())
    vertices=sorted(rounded(v.Center().toTuple()) for v in s.Vertices())
    desc=dict(volume=round(s.Volume(),5),area=round(s.Area(),5),bounds=bounds(s.BoundingBox()),center=rounded(s.Center().toTuple()),faces=faces,edges=edges,vertices=vertices)
    return hashlib.sha256(json.dumps(desc,separators=(',',':')).encode()).hexdigest()
def color(c):return list(c.toTuple()) if c is not None else None
def payload_fingerprint(m):
    h=hashlib.sha256(json.dumps({k:m.get(k) for k in ('name','color')},sort_keys=True).encode())
    for k,t in (('pos','<f4'),('nrm','<f4'),('idx','<u4'),('fac','<u4')):h.update(np.asarray(m[k],dtype=t).tobytes())
    return h.hexdigest()

def native_replace(path,mapped):
    """Replace only target prototypes using the STEP reader/writer's XCAF API."""
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPCAFControl import STEPCAFControl_Reader,STEPCAFControl_Writer
    from OCP.TCollection import TCollection_ExtendedString
    from OCP.TDataStd import TDataStd_Name
    from OCP.TDF import TDF_Label,TDF_LabelSequence
    from OCP.TDocStd import TDocStd_Document
    from OCP.TopLoc import TopLoc_Location
    from OCP.XCAFDoc import XCAFDoc_DocumentTool
    doc=TDocStd_Document(TCollection_ExtendedString('hsm'))
    reader=STEPCAFControl_Reader();reader.SetNameMode(True);reader.SetColorMode(True)
    assert reader.ReadFile(str(path))==IFSelect_RetDone
    assert reader.Transfer(doc)
    tool=XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    found={};placements={}
    def named(label):
        value=TDataStd_Name()
        return value.Get().ToExtString() if label.FindAttribute(TDataStd_Name.GetID_s(),value) else ''
    def walk(label,place):
        children=TDF_LabelSequence();tool.GetComponents_s(label,children)
        for i in range(1,children.Length()+1):
            part=children.Value(i)
            here=TopLoc_Location(place.Transformation()*tool.GetLocation_s(part).Transformation())
            proto=TDF_Label()
            if not tool.GetReferredShape_s(part,proto):proto=part
            inner=TDF_LabelSequence();tool.GetComponents_s(proto,inner)
            if inner.Length():walk(proto,here)
            else:
                name=named(part) or named(proto)
                t=here.Transformation()
                placements[name]=[round(t.Value(r,c),12) for r in range(1,4) for c in range(1,5)]
                if name in mapped:
                    assert name not in found,(path,name,'duplicate target prototype')
                    found[name]=(proto,here)
    free=TDF_LabelSequence();tool.GetFreeShapes(free)
    for i in range(1,free.Length()+1):walk(free.Value(i),TopLoc_Location())
    assert set(found)==set(mapped),(path,set(mapped)-set(found))
    for name,(proto,place) in found.items():
        tool.SetShape(proto,mapped[name].wrapped.Moved(place.Inverted()))
    tool.UpdateAssemblies()
    writer=STEPCAFControl_Writer();writer.SetNameMode(True);writer.SetColorMode(True)
    writer.SetLayerMode(True)
    assert writer.Transfer(doc)
    def write(target):assert writer.Write(str(target))==IFSelect_RetDone
    _atomic_write(str(path),write)
    return placements

def refresh(path,changes,surfaces):
    old_sha=sha(path)
    old=import_assembly(str(path))
    names={name.replace('_','-'):name for name in old}
    mapped={names[k]:v for k,v in changes.items() if k in names}
    assert len(mapped)==len(changes),(path,changes.keys(),old.keys())
    retained={name:dict(geometry_sha256=fingerprint(s),color=color(c)) for name,(s,c) in old.items() if name not in mapped}
    before=flute_payload.read_payload(path.with_name(path.name+'.mesh'))
    assert before is not None,path
    retained_payload={m['name']:payload_fingerprint(m) for m in before if m['name'].replace('_','-').split('/')[0] not in changes}
    placements=native_replace(path,mapped)
    after=import_assembly(str(path))
    assert set(after)==set(old),(set(after)-set(old),set(old)-set(after))
    replacement_checks={}
    for name,s in mapped.items():
        landed=after[name][0]
        source_fingerprint=fingerprint(s)
        exported_fingerprint=fingerprint(landed)
        delta=None
        if source_fingerprint!=exported_fingerprint:
            delta=abs(s.cut(landed).Volume())+abs(landed.cut(s).Volume())
        a,b=s.BoundingBox(),landed.BoundingBox()
        error=max(abs(getattr(a,k)-getattr(b,k))
                  for k in ('xmin','xmax','ymin','ymax','zmin','zmax'))
        topology=lambda v:[len(v.Solids()),len(v.Faces()),len(v.Edges()),len(v.Vertices())]
        assert landed.isValid() and (delta is None or delta<1e-5) and error<1e-6 and topology(s)==topology(landed),(
            path,name,'replacement geometry changed during export',delta,error)
        # A newly placed spline can integrate with different numeric accuracy
        # after STEP serialization. Boolean equivalence and fixed topology are
        # the relevant geometry checks for that transformed target.
        replacement_checks[name]=dict(native_symmetric_difference_mm3=delta,
            max_bounds_error_mm=error,topology=topology(landed),valid=True,
            source_fingerprint=source_fingerprint,exported_fingerprint=exported_fingerprint,
            comparison='Matching normalized analytic face, edge, vertex and solid fingerprints; native Boolean equivalence only for serialization differences.')
        print(path.name,name,'replacement verified',flush=True)
    for name,record in retained.items():
        s,c=after[name]
        exported=fingerprint(s)
        if record['geometry_sha256']!=exported:
            prior=old[name][0]
            delta=abs(prior.cut(s).Volume())+abs(s.cut(prior).Volume())
            assert delta<1e-5,(path,name,'geometry moved',delta)
            record['serialization_equivalence_mm3']=delta
            record['exported_geometry_sha256']=exported
        assert record['color']==color(c),(path,name,'color moved')
    payload_path=path.with_name(path.name+'.mesh')
    landed=flute_payload.graft(payload_path,surfaces,same_frame=True)
    assert landed==len(changes),(path,landed,len(changes))
    meshes=flute_payload.read_payload(payload_path)
    for m in meshes:
        if m['name'] in retained_payload:assert retained_payload[m['name']]==payload_fingerprint(m),(path,m['name'],'unrelated viewer member moved')
    _mesh_payload.write(meshes,str(payload_path),src=_mesh_payload.source_digest(path))
    return dict(input_step_sha256=old_sha,output_step_sha256=sha(path),output_payload_sha256=sha(payload_path),
                replaced_members=sorted(mapped),retained_members=retained,
                replacement_geometry_checks=replacement_checks,
                native_component_placements=placements,
                retained_viewer_member_sha256=retained_payload,
                retained_member_count=len(retained),all_unrelated_native_names_geometry_placements_colors_and_viewer_arrays_preserved=True)

def main():
    current={n:cq.importers.importStep(str(ENC/f'enclosure-{n}.step')).val() for n in ('front-top','pump-cartridge')}
    changes={f'enclosure-{n}':s for n,s in current.items()}
    surfaces=flute_payload.surfaces((ENC,))
    selected={name:surfaces[name] for name in changes}
    report={}
    path=ENC/'enclosure.step'
    report[str(path.relative_to(ROOT))]=refresh(path,changes,selected)
    frame=cq.importers.importStep(str(FUNNEL/'funnel-frame.step')).val().translate((0,ff.center_y,ff.datums()[0]))
    frame_surface=flute_payload.surfaces((FUNNEL,))['funnel-frame'].copy()
    points=np.asarray(frame_surface['pos']).reshape(-1,3)
    frame_surface['pos']=(points+np.array([0,ff.center_y,ff.datums()[0]])).ravel().tolist()
    changes['funnel-frame']=frame;selected['funnel-frame']=frame_surface
    path=ROOT/'hardware/manifold-layout/enclosure-assembly.step'
    report[str(path.relative_to(ROOT))]=refresh(path,changes,selected)
    (HERE/'aggregate-refresh.json').write_text(json.dumps(dict(schema=1,scope='Scoped XCAF named-prototype replacement in each original STEP document and canonical viewer graft. Unrelated native geometry uses normalized analytic-face/edge/vertex fingerprints at 0.00001 mm; any serialization-only integration differences receive a native Boolean equivalence check. Existing hierarchy, placements and colors are retained. This is not a fresh full-machine motion scorecard.',source_sha256=sha(Path(__file__)),aggregates=report),indent=2)+'\n')
    print('Scoped enclosure and appliance aggregate replacement verified.',flush=True)

if __name__=='__main__':main()
