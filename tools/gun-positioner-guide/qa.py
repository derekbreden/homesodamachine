#!/usr/bin/env python3
"""Verify published-build inputs and download contents after regenerating them."""
from pathlib import Path
import hashlib,json,subprocess,sys,zipfile
from decimal import Decimal
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/'hardware/gun-positioner'
CAD=ROOT/'hardware/printed-parts/fixtures/pgfun-positioner'
GUIDE=ROOT/'hardware/gun-positioner-guide'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    release=json.loads((DOC/'release-manifest.json').read_text())
    geom=json.loads((CAD/'motion-geometry.json').read_text())['sha256']
    assert release['geometry_sha256']==geom
    for rel,h in release['artifacts'].items():assert sha(ROOT/rel)==h,rel
    receipt=json.loads((GUIDE/'source-receipt.json').read_text())
    assert receipt['geometry_sha256']==geom
    for rel,h in receipt['sources'].items():assert sha(ROOT/rel)==h,rel
    assert sha(GUIDE/'gun-positioner-guide.pdf')==receipt['pdf_sha256']
    assert len(PdfReader(GUIDE/'gun-positioner-guide.pdf').pages)==receipt['pages']
    parts=json.loads((CAD/'print-manifest.json').read_text())['parts']
    with zipfile.ZipFile(CAD/'print-pack.zip')as pack:
        assert len([n for n in pack.namelist()if n.endswith('.stl')])==60
        for p in parts:assert hashlib.sha256(pack.read(p['name']+'.stl')).hexdigest()==p['sha256'],p['name']
    purchases=json.loads((DOC/'purchases.json').read_text())
    items=purchases['mechanism']+purchases['observation']
    assert all(p['prime']is True for p in items)
    assert sum(Decimal(str(p['subtotal']))for p in items)==Decimal('1003.86')
    check=json.loads((CAD/'clearance-check.json').read_text())
    assert check['geometry_sha256']==geom and not check['unintended_intersections']
    subprocess.run([sys.executable,str(ROOT/'firmware/src_pgfun_positioner/verify_assets.py')],check=True)
    print('Guide sources, release hashes, all 60 archived STLs, Prime total and firmware binding match')
if __name__=='__main__':main()
