"""Materialize front-top and its flush sliding funnel frame; retain back-top."""
from pathlib import Path
import hashlib,json,os,sys,time
import cadquery as cq
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools').is_dir())
ENC=ROOT/'hardware/printed-parts/enclosure/enclosure'
FUNNEL=HERE.parent
sys.path[:0]=[str(ROOT/'hardware/scripts'),str(ENC),str(FUNNEL)]
import enclosure as e,_box_spec,flute_payload,funnel_frame as ff
from materialize_pump_cartridge import _declared_box

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    box,bounds,box_path=_declared_box(_box_spec,e)
    box=box._replace(pack=box.pack._replace(nameplate=box.pack.nameplate._replace(thick=3.36)))
    e.BOUNDS[:]=bounds;e._last_box[0]=box
    pieces={};cache={};started=time.monotonic()
    for name in ('front-top',):
        pieces[name]=e.build_piece(box,*name.split('-'),halves_cache=cache)
        s=pieces[name].val()
        assert s.isValid() and len(s.Solids())==1,name
        print(name,'built',round(time.monotonic()-started,1),'seconds',flush=True)
    e._report_bay_sill(pieces['front-top'],box)
    flat_wall=e._report_ridge_roof(pieces['front-top'],box)
    for name in e.PIECE_COLORS:
        if name not in pieces:
            pieces[name]=cq.importers.importStep(str(ENC/f'enclosure-{name}.step'))
    bodies={n:e._piece_mesh(p.val()) for n,p in pieces.items()}
    steel=[e._piece_mesh(e._collet_plate_body(box.pack.collet_plate))]
    output={}
    for name in ('front-top',):
        path=ENC/f'enclosure-{name}.step';part=pieces[name]
        held=os.environ.get('HSM_SKIP_MESH_PAYLOAD')
        os.environ['HSM_SKIP_MESH_PAYLOAD']='1'
        try:e.export_assembly(e.one_body(part,f'enclosure-{name}',e.PIECE_COLORS[name]),str(path))
        finally:
            if held is None:os.environ.pop('HSM_SKIP_MESH_PAYLOAD',None)
            else:os.environ['HSM_SKIP_MESH_PAYLOAD']=held
        rails=e.flute_rails(box,[m for n,m in bodies.items() if n!=name]+steel)
        mesh=e._flute_skin.flute(bodies[name],rails,e.flute_pitch(box.outer),e.flute_depth,e.flute_rise)
        mesh.export(str(path.with_suffix('.stl')))
        written=e.trimesh.load_mesh(path.with_suffix('.stl'))
        assert written.is_watertight and written.is_winding_consistent,name
        assert not e._flute_skin.non_manifold_edges(written),name
        flute_payload.cut(path,path.with_suffix('.stl'))
        output[name]={x.name:sha(x) for x in (path,path.with_suffix('.stl'),path.with_suffix('.step.mesh'))}
        print(name,'exported',round(time.monotonic()-started,1),'seconds',flush=True)
    ff.main()
    output['funnel-frame']={f'funnel-frame.{s}':sha(FUNNEL/f'funnel-frame.{s}') for s in ('step','stl','step.mesh')}
    sources={Path(__file__),box_path}
    for m in tuple(sys.modules.values()):
        s=getattr(m,'__file__',None)
        if s and str(s).endswith('.py'):
            p=Path(s).resolve()
            if p.is_relative_to(ROOT) and 'site-packages' not in str(p):sources.add(p)
    (HERE/'generation.json').write_text(json.dumps({'outputs':output,
        'source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in sorted(sources)},
        'box':str(box_path.relative_to(ROOT)),
        'retained_back_top_sha256':{f'enclosure-back-top.{s}':sha(ENC/f'enclosure-back-top.{s}') for s in ('step','stl','step.mesh')},
        'roof_datums_mm':ff.roof_datums(box.inner,box.pack.funnel,e.funnel_seat_z(box.outer),box.y_joint),
        'flat_front_wall':flat_wall,
        'scope':'Only front-top and funnel frame materialized. The raised removable front roof ends one running clearance before the Y seam. Back-top exports and the rear frame envelope are retained. Existing lower rails, socket, drain, silicone seat and installed component stations retain their datums.'},indent=2)+'\n')

if __name__=='__main__':main()
