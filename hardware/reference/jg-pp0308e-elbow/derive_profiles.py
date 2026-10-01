"""Rebuild the exterior modeling profiles from the unit-scale observations.

Axial medians describe the exposed +Y leg. Inspected front-facing shoulders
anchor the nearly radial portions of the outline. The +Z leg uses the same
form with the independently fitted root/collar offsets; its collet is symmetric.
"""
import json
import numpy as np
from scan_tools import HERE, observations


def main():
    record=json.loads((HERE/'scan-measurements.json').read_text())
    p,n,h=observations();r=np.hypot(p[:,0],p[:,2])
    outward=np.sum(p[:,[0,2]]*n[:,[0,2]],axis=1)>2
    profile=[]
    for t in np.arange(3.5,18.76,.25):
        mask=(abs(p[:,1]-t)<.10)&(r>4.4)&(r<8.6)&(h>18)&outward
        assert mask.sum()>20
        profile.append([round(float(t),4),round(float(np.median(r[mask])),4)])
    profile=[[2.5,4.08],[3.,4.24],*profile]
    profile=[row for row in profile if not(6.5<row[0]<7.25) and not(16.25<row[0]<17) and row[0]<18.5]
    profile.extend([[6.7,4.73],[6.963,4.92],[6.963,5.98],[7.1,6.25],
                    [16.4,7.98],[16.562,7.65],[16.562,7.33],[16.75,7.15],
                    [18.5,6.94],[18.7,6.53],[18.837,6.06]])
    profile.sort(key=lambda row:row[0])
    collet=[[18.837,5.30],[19,5.32],[19.25,5.27],[19.5,5.26],[19.75,5.23],
            [20,5.21],[20.25,5.15],[20.40,5.06],[20.50,4.92],[20.56239,4.73]]
    second=[]
    for t,radius in profile:
        correction=np.interp(t,[2.5,6.7,8.3,10.8,13.6,15.8,18.837],
                             [0,-.025,-.05124,-.05124,-.07293,-.07293,0])
        second.append([t,round(radius+correction,4)])
    for leg,body in [('y',profile),('z',second)]:
        record['profiles'][leg]['fixed_body']=body
        record['profiles'][leg]['collet']=collet
    (HERE/'scan-measurements.json').write_text(json.dumps(record,indent=2)+'\n')
    print('Axial modeling profiles rebuilt from source cloud and inspected shoulders.')

if __name__=='__main__':main()
