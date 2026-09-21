"""Read-only native pump cartridge/cap equality after the rear/core boundary move."""
from collections import namedtuple
from datetime import datetime,timezone
import hashlib,json,os,sys,time,tempfile,zipfile,argparse
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'hardware/scripts').is_dir())
os.environ['HSM_NO_BUILD_LOCK']='1'
sys.path[:0]=[str(ROOT/'hardware/manifold-layout')]
import cadquery as cq
import enclosure_assembly as ea
import _box_spec
enc=ea._enc
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--baseline',type=Path,default=HERE/'fit-correction-baseline.zip')
parser.add_argument('--output',type=Path,default=HERE/'pump-rear-boundary-equivalence.json')
args=parser.parse_args()
temporary=tempfile.TemporaryDirectory(prefix='hsm-pump-baseline-');baseline=Path(temporary.name)
with zipfile.ZipFile(args.baseline) as archive:
    manifest=json.loads(archive.read('manifest.json'))
    for name,row in manifest['files'].items():
        if Path(name).name!=name:raise ValueError('Baseline archive entries must be flat')
        data=archive.read(name)
        if hashlib.sha256(data).hexdigest()!=row['sha256']:raise ValueError(name+' digest mismatch')
        (baseline/name).write_bytes(data)
def input_label(p):return args.baseline.name+'::'+p.name if p.parent==baseline else str(p.relative_to(ROOT))
path=baseline/'enclosure-box.json'
fields=json.loads(path.read_text())['box']['pack']['fields']
input_pack=enc.Pack if tuple(fields)==enc.Pack._fields else namedtuple('Pack',fields)
box,_=_box_spec.read(enc.Box,enc.Bound,(input_pack,enc.PortField,enc.Nameplate),path=path)
box=box._replace(pack=enc.Pack(**box.pack._asdict()))
inner=list(box.inner);outer=list(box.outer)
inner[3]=enc.rear_plane_y;outer[3]=enc.rear_plane_y+enc.wall
candidate=box._replace(inner=tuple(inner),outer=tuple(outer))
inputs={str(args.baseline.relative_to(ROOT)):sha(args.baseline),input_label(path):sha(path)}
sources={str(Path(m.__file__).relative_to(ROOT)):sha(Path(m.__file__)) for m in (enc,enc._interface,ea._tray)}
report={'status':'running','created_at_utc':datetime.now(timezone.utc).isoformat(),
    'scope':'Current cartridge/cap builders, frozen fitted front datums, only rear inner/outer boundaries moved; native equality with frozen canonical exports. No export written; not a full-Box assembly claim.',
    'input_sha256':inputs,'source_sha256':sources,'old_rear':[box.inner[3],box.outer[3]],
    'new_rear':[candidate.inner[3],candidate.outer[3]],'checks':[]}
out=args.output
cache={}
for name,fn in (('pump-cartridge',enc.build_pump_cartridge),('pump-cap',enc.build_pump_cap)):
    p=baseline/f'enclosure-{name}.step'
    inputs[input_label(p)]=sha(p)
    inputs[input_label(p.with_suffix('.stl'))]=sha(p.with_suffix('.stl'))
    tick=time.monotonic();current=fn(candidate,cache).val();frozen=cq.importers.importStep(str(p)).val()
    a,b=current.cut(frozen).Volume(),frozen.cut(current).Volume()
    row={'part':name,'candidate_extra_mm3':a,'frozen_extra_mm3':b,'seconds':time.monotonic()-tick,
         'pass':a<=1e-5 and b<=1e-5}
    report['checks'].append(row);out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(row),flush=True)
report['source_hashes_unchanged_at_end']=all(sha(ROOT/p)==v for p,v in sources.items())
report['status']='native_pump_geometry_identical' if all(r['pass'] for r in report['checks']) else 'failed'
out.write_text(json.dumps(report,indent=2)+'\n')
if report['status']=='failed':raise SystemExit('Native pump geometry changed')
