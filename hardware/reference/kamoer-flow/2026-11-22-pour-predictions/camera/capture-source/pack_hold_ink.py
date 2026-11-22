"""Archive the lossless dry-print samples used to check apparent motion during a particular hold."""
import argparse
import json
import sys
from pathlib import Path
sys.path.append('/opt/homebrew/lib/python3.13/site-packages')
from read_hold_ink import read
import register_cup

p=Path(__file__).resolve().parent
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('label');ap.add_argument('before');ap.add_argument('after')
    ap.add_argument('--rows',nargs=2,type=float,required=True);a=ap.parse_args()
    out=p/'evidence/hold-ink'/a.label;out.mkdir(parents=True,exist_ok=True);sources=[]
    for role,window in [('start',a.before),('finish',a.after)]:
        w=p/'windows'/window
        register_cup.pack_color(w/'color.png',out/(role+'.png'))
        source=json.loads((w/'color.json').read_text());sources.append({'role':role,'window':window,'pts_ns':source['pts_ns'],'seq':source['seq']})
    z=read(out/'start.png',out/'finish.png',a.rows,out/'reference.npz')
    (out/'measurements.json').write_text(json.dumps({'photographs':sources,'camera_rows':a.rows,'registration':z},indent=2)+'\n')
