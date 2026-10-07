"""Route the counted reed-A trunk from its admitted bare exit to its service fork."""
from pathlib import Path
import argparse,hashlib,json,sys
import cadquery as cq
import numpy as np

HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1]
sys.path[:0]=[str(HERE),str(STUDY)]
from controls_looms import definition,circle_points,hull,native_hits,loaded_digest,STATIC_JOINTS
from controls_harness import ControlsGuide,control_occupied_points
from controls import port
from native_harness import bounds

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--search-states',type=int,default=1200000)
    args=parser.parse_args()
    _,network,sections,fanouts=definition()
    flat=[np.asarray([-54.5,y,z]) for y in [450.85,465.15] for z in [254.95,256.65]]
    first=hull(circle_points((-31,458.3,253.4),(0,0,1),6.4)+flat)
    transition=hull(flat+circle_points((-62,458,259),(0,0,1),6.4))
    bare=cq.Compound.makeCompound([first,transition])
    origin=port('control-reed-a-bare-exit',(-62,458,259),(0,0,1),'Reed-A counted bare/round transition')
    target=port('control-service-fork-A',(-52.8,407.5,326.4),(0,1,0),'Reed-A fork aft approach')
    for p in [origin,target]:
        p.update(diameter_mm=6.4,bend_radius_mm=6.)
        p['lead_paths']=[[p['point'],(np.asarray(p['point'])+np.asarray(p['axis'])*d).tolist()] for d in [8.4,12.6,16.8,20]]
    fork=hull(circle_points(target['point'],target['axis'],6.4)+
      circle_points((-57.8,403.2,326.4),(0,-1,0),4.3)+
      circle_points((-47.8,403.2,326.4),(0,0,-1),4.3))
    ports=[p for n in network for p in [n['from_dock'],n['to_dock']]]+[origin,target]
    guide=ControlsGuide(ports,diameter=6.4,hardware_only=True)
    guide.bend_radius=6.;guide.max_states=args.search_states
    fixed={n:s for n,(s,_) in sections.items() if n!='control-service-reeds-A'}
    fixed['control-service-fork-A']=fork
    fixed['control-reed-a-bare-exit']=bare
    fixed.update({'control-'+n:s for n,(s,_,_) in fanouts.items()})
    chunks=[]
    for name,shape in fixed.items():
        guide.obstacles[name]=shape;guide.models[name]=shape;guide.records[name]={}
        chunks.append(control_occupied_points(name,shape,None))
    guide.voxels=np.vstack([guide.voxels,*chunks]);guide.refresh()
    output=ROOT/'.cache/pump-first-layout/wiring/controls';output.mkdir(parents=True,exist_ok=True)
    report={'pass':False,'scope':'Counted eight-wire R6 service trunk between the accepted bare exit and a named aft-entry dressing fork; actual constituent turns remain unlocated.'}
    try:
        routed,record=guide.route(origin,target,'control-reed-a-round-trunk')
        joined=cq.Compound.makeCompound([first,transition,routed])
        blocked={n:s for n,s in guide.obstacles.items() if n not in ['control-service-fork-A','control-reed-a-bare-exit']}
        hits=native_hits(joined,blocked,['cold-core/foam-cap-lid-top'])
        fork_hits=native_hits(fork,{n:s for n,s in blocked.items() if n!='control-service-fork-A'})
        declared={frozenset(pair) for pair in STATIC_JOINTS}
        fork_continuity=[hit for hit in fork_hits if frozenset(['control-service-fork-A',hit['part']]) in declared]
        fork_hits=[hit for hit in fork_hits if hit not in fork_continuity]
        report.update(record,conductor_count=8,actual_bore_mm=6.8,packing_radius_mm=2.35,
          minimum_nominal_round_trunk_wire_centre_radius_mm=3.65,
          flat_exit_cross_section_mm=[14.3,1.7],flat_exit_z_mm=[254.95,256.65],
          fork_axis_mm=target['point'],fork_incoming_axis=[0,-1,0],
          native_interferences=hits,fork_interferences=fork_hits,fork_declared_continuity=fork_continuity,
          input_geometry_sha256={n:loaded_digest(s) for n,s in guide.obstacles.items()},
          source_sha256={str(Path(__file__).relative_to(ROOT)):hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
        report['pass']=joined.isValid() and fork.isValid() and not hits and not fork_hits
        for name,shape in [('reed-a-service-route',joined),('reed-a-service-fork',fork)]:
            path=output/(name+'.brep');shape.exportBrep(str(path))
            entry={'brep':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bounds':bounds(shape)}
            if name=='reed-a-service-route':report.update(entry)
            else:report['aft_fork']=entry
    except ValueError as error:report['error']=str(error)
    (HERE/'reed-a-service-route.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__':main()
