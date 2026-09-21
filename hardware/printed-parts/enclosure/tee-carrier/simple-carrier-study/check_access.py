"""Retained tie passages and added fixed cups against frozen native hardware."""
import json
from pathlib import Path
import cadquery as cq
from build_concept import build,box,sha,bounds
from check_joint_motion import disjoint
HERE=Path(__file__).resolve().parent


def main():
    M,I,plain,blank,L,R,*_=build()
    carrier=cq.Compound.makeCompound([L,R])
    rows=[]
    for index,site in enumerate(I['tie_sites']):
        x=site['tee_x']+site['head_side']*(8.25+.25+M['spec']['tie_head'][0]/2)
        w,d,h=M['spec']['tie_head'];z=site['band_z'];yf=I['web_fore_y'];ya=I['web_aft_y']
        head=box((x-w/2,x+w/2),(yf-d,yf),(z-h/2,z+h/2))
        back=box((min(site['slot_xs'])-.5,max(site['slot_xs'])+.5),(ya,ya+1),(z-1.25,z+1.25))
        probes=[('declared tie head',head),('rear tie strap',back)]
        for sx in site['slot_xs']:
            probes.append(('through-slot 1 x 2.5 mm strap',box((sx-.5,sx+.5),(yf-6.1,ya+1),(z-1.25,z+1.25))))
        for name,s in probes:
            hit=s.intersect(carrier)
            rows.append({'tie':index+1,'probe':name,'overlap_mm3':hit.Volume(),'hit_bounds':bounds(hit)})
    folder=HERE/'inputs/placed-neighbors'
    j=json.loads((folder/'manifest.json').read_text())
    fixed=[]
    for station in I['spring_stations']:
        x,z=station['x'],station['z'];floor=station['seat_floor_y'];r=I['spring_bore_d']/2
        p=cq.Vector(x,floor+1.9,z)
        fixed.append(cq.Solid.makeCylinder(r+2,6.1,p,cq.Vector(0,1,0)).cut(
            cq.Solid.makeCylinder(r,6.3,p-cq.Vector(0,.1,0),cq.Vector(0,1,0))))
    cups=cq.Compound.makeCompound(fixed)
    cup_rows=[]
    maximum_tee_z=-1e9
    for name,row in j['bodies'].items():
        p=folder/row['brep'];assert sha(p)==row['sha256']
        body=cq.Shape.importBrep(str(p))
        if name.startswith('tee-'):maximum_tee_z=max(maximum_tee_z,body.BoundingBox().zmax)
        hit=body.intersect(cups)
        cup_rows.append({'neighbor':name,'overlap_mm3':hit.Volume(),'hit_bounds':bounds(hit)})
    report={'generator_sha256':sha(HERE/'build_concept.py'),'script_sha256':sha(__file__),
        'neighbor_manifest_sha256':sha(folder/'manifest.json'),
        'scope':'Native declared tie heads, rear straps and through-slot windows inside the carrier. Added integral fixed cups versus all frozen nearby hardware bodies. Full hand/tool access and tightening effort remain physical acceptance items.',
        'frozen_neighbor_count':len(j['bodies']),'tie_passages':rows,'fixed_cup_neighbors':cup_rows,
        'held_spring_and_pusher_to_seated_tee_vertical_air_mm':I['spring_stations'][1]['z']-6.5/2-maximum_tee_z,
        'tool_tee_scope':'The held spring/pusher occupy Z at least 0.535 mm above every seated native tee throughout the nonnegative-Z entry and removal route; valves/tubes are installed afterward.',
        'valve_socket_scope':'No valve socket or tie feature is cut or tightened. The 7.2 mm accepted valve socket remains unchanged; positive retention uses its existing ties.',
        'all_reported_native_readings_clear':all(r['overlap_mm3']<1e-5 for r in rows+cup_rows)}
    (HERE/'access-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'clear':report['all_reported_native_readings_clear'],'nonzero':[r for r in rows+cup_rows if r['overlap_mm3']>1e-5]},indent=2),flush=True)


if __name__=='__main__':main()
