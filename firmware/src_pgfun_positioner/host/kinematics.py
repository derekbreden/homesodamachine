"""Count geometry is commanded motion; camera measurements establish position."""
import json
import math
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
RECORD=json.loads((ROOT/'hardware/printed-parts/fixtures/pgfun-positioner/motion-geometry.json').read_text())
G=RECORD['motion'];GEOMETRY_SHA=RECORD['sha256']
AXES=('yaw','pitch')
COUNTS_PER_REV=G['reduction']*G['motor_full_steps']*G['external_microsteps']
WORKING_LEVER=G['working_lever_mm']
SOFT_LIMIT=int(COUNTS_PER_REV*G['soft_limit_deg']/360)

def degrees_to_count(degrees):
    if not math.isfinite(degrees):raise ValueError('Finite angle required')
    return round(degrees*COUNTS_PER_REV/360)

def split_target(current,target):
    if len(current)!=2 or len(target)!=2 or any(abs(x)>SOFT_LIMIT for x in target):
        raise ValueError('Target outside mechanical count envelope')
    delta=[int(t)-int(c) for c,t in zip(current,target)]
    n=max(1,math.ceil(max(map(abs,delta))/256))
    previous=[0,0]
    for k in range(1,n+1):
        step=[round(v*k/n)-p for v,p in zip(delta,previous)]
        previous=[p+s for p,s in zip(previous,step)]
        if any(step):yield step

def aim_point(yaw_count,pitch_count):
    yaw=yaw_count*2*math.pi/COUNTS_PER_REV;pitch=pitch_count*2*math.pi/COUNTS_PER_REV
    # Rotations Z(swivel), then local X(pivot), at the nominal seam height.
    x=-WORKING_LEVER*math.cos(pitch)*math.sin(yaw)
    y=WORKING_LEVER*math.cos(pitch)*math.cos(yaw)-WORKING_LEVER
    z=WORKING_LEVER*math.sin(pitch)
    return [G['aim'][0]+x,G['aim'][1]+y,G['aim'][2]+z]
