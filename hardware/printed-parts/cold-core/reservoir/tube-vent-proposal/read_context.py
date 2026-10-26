"""Freeze placed native appliance obstacles for the reservoir proposal review."""
from pathlib import Path
import argparse, os, sys, json, hashlib
os.environ['HSM_NO_BUILD_LOCK']='1'
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'hardware/scripts').is_dir())
CORE=ROOT/'hardware/printed-parts/cold-core'
for path in (ROOT/'hardware/scripts',ROOT/'hardware/manifold-layout',CORE,
             CORE/'reservoir',ROOT/'hardware/printed-parts/cadlib'):
    sys.path.insert(0,str(path))
from _cadq_export import import_assembly
import _above_core_mounts as mounts
from _foam_cap import top_cap_height
import _cold_core_interface as interface


def freeze(output):
    output.mkdir(parents=True,exist_ok=True)
    source=ROOT/'hardware/manifold-layout/enclosure-assembly.step'
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    placed=import_assembly(source)
    metadata={}
    for name,(shape,_) in placed.items():
        native=mounts.world_shape_in_cap(shape).rotate((0,0,0),(0,0,1),180).translate(
            (0,0,interface.foam_shell_outer_height+top_cap_height))
        b=native.BoundingBox()
        if (b.zmax<197 or b.zmin>370 or b.xmax<-145 or b.xmin>145 or
                b.ymax<-95 or b.ymin>95):continue
        filename=hashlib.sha256(name.encode()).hexdigest()[:16]+'.brep'
        native.exportBrep(str(output/filename))
        metadata[name]={'file':filename,'bounds':[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]}
    (output/'native-index.json').write_text(json.dumps({
        'source':str(source.relative_to(ROOT)),'sha256':digest,'parts':metadata},indent=2)+'\n')
    print(f'Frozen {len(metadata)} placed bodies under {output}')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    freeze(parser.parse_args().output)
