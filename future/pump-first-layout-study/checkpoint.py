"""Save and restore the exact native study geometry, independently of live CAD.

The scene's manifests remain readable JSON. The native archive contains
their named B-reps and declared immutable check receipts under this study's
disposable cache, with content hashes.
The frozen reference STEP is handled by baseline.py.
"""
from pathlib import Path
import argparse,gzip,hashlib,io,json,tarfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
ARCHIVE=HERE/'inputs/candidate-native.tar.gz'
INDEX=HERE/'inputs/candidate-native.json'
PREFIX='.cache/pump-first-layout/'
MANIFESTS=[
    'funnel/candidate.json','funnel/candidate-aft-60-tooling.json',
    'funnel/shells.json','funnel/roof-stock.json','funnel/mating.json',
    'pump/candidate.json','pump/fluid24-candidate.json',
    'routing/candidate.json','structure/candidate.json','structure/print-parts.json',
    'structure/pan-slot.json',
    'structure/water5-key-pocket.json',
    'structure/print-material-union-check.json',
    'structure/held-original-print-checks.json',
    'structure/prv-factory-handling.json',
    'mounts/candidate.json','mounts/roof-candidate.json','mounts/floor-candidate.json',
    'mounts/shell-post.json','mounts/shell-pan-post.json',
    'mounts/fluid-candidate.json','mounts/body-candidate.json','mounts/needle-candidate.json',
    'mounts/wr-candidate.json','mounts/check-tee-candidate.json',
    'structure/roof-hatch.json','structure/scene-stock.json','wiring/candidate.json',
    'wiring/power-candidate.json','wiring/controls-candidate.json',
    'wiring/control-reserves.json','wiring/control-fanouts-check.json',
    'wiring/static-controls-pair-check.json','wiring/control-fluid-air-check.json',
    'wiring/control-terminal-owner-check.json',
    'wiring/front-loom-handling.json',
    'wiring/join-check.json','wiring/lower-lead-exits.json',
    'wiring/power-members-check.json',
    'routing/co2-candidate.json','routing/tube-hosts.json','routing/strict-route-audit.json',
    'routing/water-ring-finish.json',
    'routing/psu-surround-feasibility.json',
    'routing/psu-coupled-probe.json',
    'mounts/water5-hosts.json','native-audit.json','evidence-check.json',
    'pump/external-native-check.json','funnel/motion-check.json',
    'funnel/frame-continuous-closure-check.json','funnel/mating-final-frame.json',
    'mounts/native-check.json','mounts/floor-native-check.json',
    'structure/front-closure-check.json','structure/factory-slide-check.json',
    'structure/asse-factory-check.json',
    'structure/ground-make-up-check.json','structure/g2-factory-tool-probe.json',
    'structure/hatch-hose-check.json','structure/fastener-native-check.json']

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def native_paths(value):
    if isinstance(value,dict):
        if 'brep' in value:
            path=value['brep']
            if isinstance(path,str) and path.startswith(PREFIX) and '/baseline/' not in path:
                digest=value.get('sha256')
                if isinstance(digest,dict):digest=digest.get(path)
                if digest and sha(ROOT/path)!=digest:
                    raise ValueError('Stale native record '+path)
                yield path
        for child in value.values():yield from native_paths(child)
    elif isinstance(value,list):
        for child in value:yield from native_paths(child)
    elif isinstance(value,str) and value.startswith(PREFIX) and value.endswith('.brep') and '/baseline/' not in value:
        yield value

def cache_receipts(value):
    """Retain exact declared metadata dependencies used by received checks."""
    if isinstance(value,dict):
        reused=value.get('original_check_reuse')
        if isinstance(reused,dict):
            path=reused.get('receipt','')
            if not path.startswith(PREFIX) or not path.endswith('.json') or sha(ROOT/path)!=reused.get('receipt_sha256'):
                raise ValueError('Stale original-check receipt '+path)
            yield path
        for path,digest in value.get('source_inputs',{}).items():
            if path.startswith(PREFIX) and path.endswith('.json'):
                if not isinstance(digest,str) or sha(ROOT/path)!=digest:
                    raise ValueError('Stale cache receipt '+path)
                yield path
        for child in value.values():yield from cache_receipts(child)
    elif isinstance(value,list):
        for child in value:yield from cache_receipts(child)

def pack():
    import verify_evidence
    verify_evidence.main()
    evidence=HERE/'evidence-check.json'
    if not evidence.exists() or not json.loads(evidence.read_text()).get('pass'):
        raise ValueError('Current complete evidence-check.json required before checkpoint')
    paths=set();manifests={}
    for relative in MANIFESTS:
        path=HERE/relative
        if not path.exists():continue
        data=json.loads(path.read_text())
        manifests[relative]=sha(path);paths.update(native_paths(data));paths.update(cache_receipts(data))
    if not (HERE/'wiring/candidate.json').exists():raise ValueError('Complete wiring manifest required')
    raw=io.BytesIO();files={}
    with tarfile.open(fileobj=raw,mode='w') as tar:
        for name in sorted(paths):
            path=ROOT/name;data=path.read_bytes();info=tarfile.TarInfo(name)
            info.size=len(data);info.mode=0o644;info.mtime=0
            tar.addfile(info,io.BytesIO(data))
            files[name]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
    ARCHIVE.write_bytes(gzip.compress(raw.getvalue(),compresslevel=9,mtime=0))
    report={'archive':str(ARCHIVE.relative_to(ROOT)),'sha256':sha(ARCHIVE),
            'bytes':ARCHIVE.stat().st_size,'manifests_sha256':manifests,'files':files,
            'scope':'Exact reviewed native geometry snapshot. Restoring this archive changes only disposable study cache files.'}
    INDEX.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'native_files':sum(name.endswith('.brep') for name in files),
                      'receipt_files':sum(name.endswith('.json') for name in files),'compressed_bytes':report['bytes']}))

def restore():
    report=json.loads(INDEX.read_text())
    if sha(ARCHIVE)!=report['sha256']:raise ValueError('Native archive hash mismatch')
    for name,digest in report['manifests_sha256'].items():
        if sha(HERE/name)!=digest:raise ValueError('Changed scene manifest '+name)
    raw=gzip.decompress(ARCHIVE.read_bytes());count=0
    with tarfile.open(fileobj=io.BytesIO(raw),mode='r:') as tar:
        for member in tar:
            name=member.name;relative=Path(name)
            if not member.isfile() or not name.startswith(PREFIX) or '..' in relative.parts:
                raise ValueError('Unexpected native archive member '+name)
            expected=report['files'][name];data=tar.extractfile(member).read()
            if len(data)!=expected['bytes'] or hashlib.sha256(data).hexdigest()!=expected['sha256']:
                raise ValueError('Native member hash mismatch '+name)
            target=ROOT/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);count+=1
    import baseline
    baseline.prepare()
    print(json.dumps({'restored_native_files':count,'reference_sha256':baseline.prepare()['sha256']}))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['pack','restore']);args=parser.parse_args()
    pack() if args.action=='pack' else restore()
