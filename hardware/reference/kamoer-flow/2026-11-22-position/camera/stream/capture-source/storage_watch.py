"""Bound temporary camera storage while keeping full-rate gate evidence and named endpoint measurements."""
from pathlib import Path
import hashlib,json,shutil,sys,time
import numpy as np
sys.path.append('/opt/homebrew/lib/python3.13/site-packages')
from PIL import Image
p=Path(__file__).resolve().parent
exp=p.parent/'experiments'
repo=p.parents[3]
soft=10_000_000_000
ceiling=13_000_000_000
def size(f):
    try:return f.stat().st_size if f.is_file() else 0
    except FileNotFoundError:return 0
def raw_to_sparse(f):
    out=p/'sparse-profiles'/f.name
    out.parent.mkdir(exist_ok=True)
    with np.load(f,allow_pickle=False) as a:
        mask=np.arange(len(a['pts_ns']))%30==0
        data={k:(a[k][mask] if k in ('profiles','pts_ns','seq') else a[k]) for k in a.files}
    np.savez_compressed(out,**data)
    f.unlink()
def reduced_window(d):
    w=d/'color.png';n=d/'native.png'
    if not w.exists() and not n.exists():return
    description={}
    for f in (w,n):
        if not f.exists():continue
        with Image.open(f) as im:
            crop=im.crop((950,300,2070,1205))
            out=d/(f.stem+'-cup.png')
            crop.save(out,compress_level=3)
            description[f.name]={'sha256_original':hashlib.sha256(f.read_bytes()).hexdigest(),'saved':out.name,'upright_crop_ltrb':[950,300,2070,1205]}
        f.unlink()
    (d/'storage-archive.json').write_text(json.dumps(description,indent=2)+'\n')
def measured():
    return sum(size(x) for x in p.rglob('*'))
def once():
    total=measured();free=shutil.disk_usage(p).free;now=time.time()
    if total>=soft or free<2_500_000_000:
        import band_evidence
        for j in exp.glob('*.jsonl'):band_evidence.export(j,p,p/'gate-bands')
        for f in sorted((p/'profiles').glob('*.npz')):
            if f.stat().st_mtime>now-900:break
            old=size(f);raw_to_sparse(f);total-=old;free+=old
            if total<soft*.9 and free>3_000_000_000:break
        if total>=soft or free<2_500_000_000:
            for d in sorted((p/'windows').iterdir(),key=lambda v:v.stat().st_mtime):
                if d.name.startswith('balance-') or d.name=='initial-frozen-idle' or d.stat().st_mtime>now-900:continue
                before=sum(size(x) for x in d.iterdir());reduced_window(d);diff=before-sum(size(x) for x in d.iterdir());total-=diff;free+=diff
                if total<soft*.9 and free>3_000_000_000:break
    val={'current_bytes':measured(),'free_bytes':shutil.disk_usage(p).free,'limit_bytes':ceiling,'wall_ns':time.time_ns()}
    tmp=p/'storage.json.tmp';tmp.write_text(json.dumps(val));tmp.replace(p/'storage.json')
while (p/'port.json').exists():
    once();time.sleep(20)
