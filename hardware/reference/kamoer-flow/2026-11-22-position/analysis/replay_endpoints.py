"""Replay the camera coordinates stored in the bench journals from their lossless image evidence."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
from prospective_reader import read
from endpoint_read import read_endpoint

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('record',type=Path,help='Archived experiment directory')
    args=parser.parse_args()
    base=args.record
    index=json.loads((base/'frames/index.json').read_text())
    cfg=json.loads((base/'analysis/prospective_cup.json').read_text())
    l,t,r,b=index['roi_ltrb'];w,h=index['source_size']
    n=0;worst=0;seen=set()
    for logfile in sorted((base/'logs').glob('*.jsonl')):
        for line in logfile.read_text().splitlines():
            event=json.loads(line)
            candidates=[event.get(k) for k in ['pre','post','reading','first','final']]+list((event.get('late') or {}).values())
            for sample in candidates:
                if not isinstance(sample,dict) or 'right_y' not in sample or 'sightlines' not in sample or sample['label'] in seen:continue
                lab=sample['label'];seen.add(lab);f=base/'frames'/(lab+'.png')
                assert hashlib.sha256(f.read_bytes()).hexdigest()==index['windows'][lab]['sha256'],lab
                im=np.zeros((h,w),dtype='uint8')
                with Image.open(f) as roi: im[t:b,l:r]=roi
                value=read_endpoint(im,cfg) if 'reader' in sample else read(im,cfg)
                assert value['ok']==sample['ok'],lab
                worst=max(worst,max(abs(value[key]-sample[key]) for key in ('right_y','left_y','nominal_ml')))
                n+=1
    if not n or worst>0.00011: raise ValueError((n,worst))
    print(f'{n} recorded endpoint observations reproduced; largest coordinate or nominal-volume difference {worst:.5f}.')
if __name__=='__main__':main()
