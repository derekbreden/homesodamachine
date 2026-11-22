"""Compare corresponding local fronts between the original and final full-resolution photographs."""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image

CONTACTS=((990,989),(1450,894),(1986,931),(1986,862))


def measure(before,after):
    images=[np.asarray(Image.open(path),dtype=float) for path in (before,after)]
    result={}
    for x,y in CONTACTS:
        lines=[im[:,x-4:x+5].mean(axis=1) for im in images]
        rows=np.arange(y-18,y+19);shifts=np.arange(-12,12.001,.05)
        original=lines[0][rows];full=np.arange(len(lines[1]))
        scores=np.array([np.corrcoef(original,np.interp(rows+s,full,lines[1]))[0,1] for s in shifts])
        i=int(np.argmax(scores))
        result[f'x{x}-y{y}']={'columns':[x-4,x+4],'rows':[int(rows[0]),int(rows[-1])],'best_local_displacement_down_px':round(float(shifts[i]),2),
                               'normalized_profile_correlation':float(scores[i]),'on_search_boundary':bool(i==0 or i==len(scores)-1)}
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('before',type=Path);p.add_argument('after',type=Path);p.add_argument('--out',type=Path,required=True)
    args=p.parse_args();args.out.write_text(json.dumps(measure(args.before,args.after),indent=2)+'\n')
