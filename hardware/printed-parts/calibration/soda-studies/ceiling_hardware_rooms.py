"""Matched native roof pockets, separate from anchor stock and tie exits.

The caller owns layout. These source rooms are not a universal cutter set:
choose only the hardware that occupies the selected contact section. Material
removed for a repeated or omitted end fitting is not needed by its neighbour.
"""
from dataclasses import replace
import enclosure_features as f


def build(family='flow_meter'):
    e,b=f.source()
    if family=='flow_meter':
        native=f.flow_meter_anchors()
        who='digiten-flow'
    elif family=='asse':
        native=f.asse_anchor()
        who='asse1022-assembly'
    else:
        raise ValueError(family)
    origin=native.source_origin_mm
    cuts={}
    source_rows=[]
    for i,(name,x0,x1,y0,y1,top) in enumerate(b.pack.ceiling_reliefs):
        if name!=who:
            continue
        roof=min(top,b.inner[5])
        if roof<=e.back_top_ceiling_face()+e.stated_bound_tol:
            continue
        cuts[f'{name}_source_{i}']=e._ybox(x0,x1,y0,y1,
            e.back_top_ceiling_face()-1.,roof)
        source_rows.append((name,x0,x1,y0,y1,top))
    return f._feature(family+'_matched_hardware_roof_rooms',('E60',),
        origin=origin,cut=cuts,functions=('_back_top_ceiling',),
        source_print_up=(0,0,-1),
        backing={'native_ceiling_rows':source_rows,
                 'native_grown_roof_face_mm':e.back_top_ceiling_face()},
        mates=native.mates,group=native.group,
        notes=('Move these pockets with the matching source anchor, using the same origin and rotation.',
               'The anchor and tie exits are separate; restore only native bearing stock after roof pockets, then keep its own tie channels open.',
               'Full hardware and plumbing-line clearance remains a distinct assembly question.'))


if __name__=='__main__':
    from pathlib import Path
    import json
    results={name:build(name).report() for name in ('flow_meter','asse')}
    (Path(__file__).parent/'ceiling-hardware-rooms.json').write_text(
        json.dumps(results,indent=2)+'\n')
