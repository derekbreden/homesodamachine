"""Register two stationary photographs to the dry printed cup faces and project their motion to the liquid row."""
import argparse
import json
from pathlib import Path

import numpy as np
import register_cup

def read(before,after,centers,anchor):
    register_cup.build(before,anchor)
    result={}
    for surface,x,y in [('inner',1450,centers[0]),('outer',1920,centers[1])]:
        pre=register_cup.form(before,y,y,anchor);post=register_cup.form(after,y,y,anchor)
        ds=[post[s]['dy']-pre[s]['dy'] for s in ('left','right')]
        fraction=(x-1180)/(1730-1180)
        result[surface]={'raw_surface_row':y,'left_and_right_dry_apparent_dy_px':ds,
                         'linear_projection_dy_px':float(ds[0]+fraction*(ds[1]-ds[0])),
                         'outside_print_columns':bool(fraction>1 or fraction<0),
                         'dry_fit_residual_by_face_px':[post[s]['dry_fit_max_residual_px'] for s in ('left','right')],
                         'horizontal_spine_shift_by_face_px':[post[s]['spine_dx'] for s in ('left','right')]}
    return result

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('start',type=Path);ap.add_argument('finish',type=Path)
    ap.add_argument('--rows',nargs=2,type=float,required=True);ap.add_argument('--anchor',type=Path,required=True);ap.add_argument('--out',type=Path)
    a=ap.parse_args();txt=json.dumps(read(a.start,a.finish,a.rows,a.anchor),indent=2)+'\n'
    if a.out:a.out.write_text(txt)
    else:print(txt,end='')
