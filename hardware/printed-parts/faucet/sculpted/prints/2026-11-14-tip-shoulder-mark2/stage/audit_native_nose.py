"""Compare donor and authored native-nose move sequences in an aligned physical frame."""
import argparse
import hashlib
import json
from pathlib import Path

from tip_tape import source, layout
from tip_warp import NORMAL_AGAIN


def normalize(move,shift=(0,0,0)):
    part=lambda pos: tuple(round(v+d,5) for v,d in zip(pos,shift))
    return (part(move.start),part(move.end),round(move.e,5) if move.e is not None else None,
            move.arc,move.fan,move.acceleration,round(move.feed,4))


def donor(path,shift,minz):
    for h,moves in source.groups(path):
        if float(h)+shift[2]<minz-1e-6:
            continue
        for move in source.active(moves):
            if move.deposition:
                yield normalize(move,shift)


def tape(path):
    xyz=(0.,0.,0.)
    feature='Custom'
    width=height=None
    is_nose=False
    fan=0
    accel=0
    feed=0
    for line in path.open():
        if line.startswith('; HSM_TIP_PHASE:'):
            is_nose=line.strip().endswith('tip native nose')
        elif not is_nose:
            continue
        elif line.startswith('; HSM_ENTRY_XYZ:'):
            xyz=tuple(map(float,line.split(':',1)[1].split()))
        elif line.startswith('; FEATURE:'):
            feature=line.split(':',1)[1].strip()
        elif line.startswith('; LINE_WIDTH:'):
            width=line.split(':',1)[1].strip()
        elif line.startswith('; LAYER_HEIGHT:'):
            height=line.split(':',1)[1].strip()
        elif line.startswith('M106 S'):
            fan=int(line.split('S',1)[1])
        elif line.startswith('M204 S'):
            accel=int(line.split('S',1)[1])
        elif line.startswith(('G1 ','G2 ','G3 ')):
            op,args=source.command(line)
            end=tuple(args.get(axis,old) for axis,old in zip('XYZ',xyz))
            feed=args.get('F',feed)
            arc=(op=='G2',args.get('I',0.),args.get('J',0.)) if op!='G1' else None
            move=source.Move(xyz,end,feed,args.get('E'),arc,feature,width,height,fan,accel,'nose')
            if move.deposition:
                yield normalize(move)
            xyz=end


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('donor',type=Path)
    p.add_argument('donor_report',type=Path)
    p.add_argument('warp_report',type=Path)
    p.add_argument('tape',type=Path)
    p.add_argument('audit',type=Path)
    a=p.parse_args()
    _,shift=layout(json.loads(a.warp_report.read_text()),json.loads(a.donor_report.read_text()))
    d=list(donor(a.donor,shift,NORMAL_AGAIN))
    t=list(tape(a.tape))
    err=[(i,x,y) for i,(x,y) in enumerate(zip(d,t)) if x[:-1]!=y[:-1]]
    differences=[(abs(x[-1]-y[-1]),abs(x[-1]-y[-1])/max(1.,x[-1])) for x,y in zip(d,t)]
    result={'purpose':__doc__,'donor_sha256':source.file_hash(a.donor),'authored_tape_sha256':source.file_hash(a.tape),
            'nose_growth_first_virtual_layer_mm':NORMAL_AGAIN,
            'donor_deposition_motion_count':len(d),'emitted_deposition_motion_count':len(t),
            'mismatched_deposition_motion_count':len(err),'first_mismatches':err[:8],
            'retained_feed_max_difference_mm_per_min':max(p[0] for p in differences),
            'retained_feed_max_relative_difference':max(p[1] for p in differences),
            'preserves_deposition_coordinates_e_fan_accel':len(d)==len(t) and not err}
    a.audit.write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':
    main()
