"""Load the complete selected frame used by manufacturing and motion checks."""
from pathlib import Path
import hashlib,json
import cadquery as cq
import sys

HERE=Path(__file__).resolve().parent
STUDY=HERE.parent
ROOT=STUDY.parents[1]
sys.path.insert(0,str(STUDY))
from evidence_binding import manifest_content_sha256

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def selected_frame(manifest):
    guide_path=STUDY/'routing/tube-hosts.json'
    if not guide_path.exists():
        record=manifest['parts']['funnel-frame']
    else:
        printed=json.loads((STUDY/'structure/print-parts.json').read_text())
        for path in [HERE/'candidate.json',guide_path]:
            canonical=str(path.relative_to(ROOT))
            content=printed.get('manifest_content_sha256',{})
            matches=(content[canonical]==manifest_content_sha256(path)) if canonical in content else printed.get('inputs_sha256',{}).get(canonical)==sha(path)
            if not matches:
                raise ValueError('Run structure/assemble_prints.py before the complete-frame proof: '+str(path))
        record=printed['parts']['funnel-frame']
    path=ROOT/record['brep']
    digest=record.get('sha256')
    if isinstance(digest,dict):digest=digest.get(record['brep'])
    if digest and digest!=sha(path):
        raise ValueError('Selected complete frame has changed: '+str(path))
    return cq.Shape.importBrep(str(path)),record
