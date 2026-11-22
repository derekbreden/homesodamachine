"""Re-register the compact native color tiles at both ends of each long unpowered hold."""
import argparse,json
from pathlib import Path
import register_cup
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('index',type=Path);p.add_argument('--out',type=Path);arg=p.parse_args();root=arg.index.parent
    result={}
    for name,item in json.loads(arg.index.read_text()).items():
        x,y=item['reference_right_and_mid_y']
        spans=[register_cup.form(root/v['file'],x,y,root/'dry-ink.npz',True) for v in item['color_windows']]
        result[name]={'dry_front_delta_y_px':{s:spans[-1][s]['dy']-spans[0][s]['dy'] for s in ['right','left']},
                      'spine_delta_x_px':{s:spans[-1][s]['spine_dx']-spans[0][s]['spine_dx'] for s in ['right','left']}}
    txt=json.dumps(result,indent=2)+'\n'
    if arg.out:arg.out.write_text(txt)
    else:print(txt,end='')
