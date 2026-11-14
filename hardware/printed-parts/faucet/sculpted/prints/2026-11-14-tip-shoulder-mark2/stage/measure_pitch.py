"""Read actual emitted donor roads and normal spacing in the transformed tip."""
from __future__ import annotations
from collections import defaultdict
from pathlib import Path
import argparse,json,numpy as np

from tip_tape import source, layout, physical_phase


def summarize(rows):
    out={}
    for k,values in sorted(rows.items()):
        v=np.concatenate(values)
        out[str(k)]={"count":len(v),"min_1pct_median_99pct_max_mm":np.quantile(v,[0,.01,.5,.99,1]).tolist(),
                     "over_.30_pct":100*float(np.mean(v>.30)),"under_.16_pct":100*float(np.mean(v<.16))}
    return out


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('gcode',type=Path)
    p.add_argument('donor',type=Path)
    p.add_argument('warp',type=Path)
    p.add_argument('output',type=Path)
    args=p.parse_args()
    warp, delta=layout(json.loads(args.warp.read_text()),json.loads(args.donor.read_text()))
    rows=defaultdict(list)
    worst={}
    last_model_level=None
    for level,moves in source.groups(args.gcode):
        u = float(level) + delta[2]
        if u>62.5:
            break
        real=[m for m in moves if m.deposition and m.e and not m.feature.startswith('Support') and m.bead_height]
        if not real:
            continue
        model_step=u - last_model_level if last_model_level is not None else u
        last_model_level=u
        y=(np.array([m.start[1]+m.end[1] for m in real])*.5)+delta[1]
        zs=(np.array([m.start[2]+m.end[2] for m in real])*.5)+delta[2]
        h=np.array([float(m.bead_height) for m in real])
        d_dy=(warp.forward(y+.0001,zs)-warp.forward(y-.0001,zs))/.0002
        # Prior commanded course is normally .24 below virtual. Use actual emitted
        # layer thickness for bridges/ordinary walls as a separate envelope measure.
        current=warp.forward(y,zs)
        abs_step=(current-warp.forward(y,zs-model_step))
        normal=abs_step/np.hypot(1,d_dy)
        bead_envelope=(current-warp.forward(y,zs-h))/np.hypot(1,d_dy)
        phase=physical_phase(warp,u)
        rows[phase].append(normal)
        rows[phase+' nominal bridge/declared'].append(bead_envelope)
        for name in set(m.feature for m in real):
            mask=np.array([m.feature==name for m in real])
            rows[f'{phase} / {name}'].append(normal[mask])
        pick=int(np.argmax(normal))
        if normal[pick]>worst.get(phase,{}).get('pitch_mm',0):
            m=real[pick]
            worst[phase]=dict(virtual_z=u, xy=[float((m.start[0]+m.end[0])*.5+delta[0]),float(y[pick])], physical_z=float(current[pick]),
                              pitch_mm=float(normal[pick]), feature=m.feature, declared_height_mm=float(h[pick]))
    args.output.write_text(json.dumps({"purpose":__doc__,"measured":summarize(rows),"worst_normal_pitch":worst},indent=2)+'\n')


if __name__=='__main__':
    main()
