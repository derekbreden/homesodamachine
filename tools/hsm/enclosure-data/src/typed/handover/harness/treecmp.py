"""Compare two kept work trees file by file, as batch.py hashes them plus one more mask.

usage: treecmp.py <workA> <workB> [--all]

Each file is normalized as batch.normalized does (its tree's work path and this crate's source
sites masked); then every 64-hex string that is the raw sha256 of a file of the same tree is
replaced by that file's relative path, since that file is compared on its own; a part program's
scratch directory under the parts cache (`tmp/<pid>-<n>`) is masked too. Prints each
differing file and where it differs: the first differing JSON paths, or the differing npz members.
"""
import hashlib
import importlib.util
import io
import json
import os
import re
import sys
import zipfile
from pathlib import Path

RUN = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('batch', RUN / 'harness/batch.py')
batch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch)
NOISE = {'hardware/ledger/.build-time.samples.json'}
HEX = re.compile(rb'[0-9a-f]{64}')
# A part program's scratch directory, `<pid>-<n>` under the parts cache: new on every run.
PARTS_TMP = re.compile(rb'(Library/Caches/hsm/parts/tmp/)\d+-\d+')


def files(work):
    out = {}
    for dirpath, dirnames, filenames in os.walk(work):
        dirnames[:] = [d for d in dirnames if d != '__pycache__' and not os.path.islink(os.path.join(dirpath, d))]
        for f in filenames:
            p = os.path.join(dirpath, f)
            if os.path.islink(p) or f == '.staged.json':
                continue
            out[os.path.relpath(p, work)] = p
    return out


def digests(paths):
    out = {}
    for rel, p in paths.items():
        h = hashlib.sha256()
        with open(p, 'rb') as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b''):
                h.update(chunk)
        out[h.hexdigest().encode()] = rel
    return out


def normalized(rel, data, work, names):
    body = PARTS_TMP.sub(rb'\1<TMP>', batch.normalized(rel, data, str(work).encode()))
    return HEX.sub(lambda m: b'<sha256:' + names[m.group()].encode() + b'>' if m.group() in names else m.group(), body)


def json_diff(a, b, path='', out=None, limit=8):
    out = [] if out is None else out
    if len(out) >= limit:
        return out
    if type(a) is not type(b):
        out.append(f'{path}: {json.dumps(a)[:120]} != {json.dumps(b)[:120]}')
    elif isinstance(a, dict):
        for k in list(a) + [k for k in b if k not in a]:
            if k not in a or k not in b:
                out.append(f'{path}/{k}: only in {"B" if k not in a else "A"}')
            else:
                json_diff(a[k], b[k], f'{path}/{k}', out, limit)
            if len(out) >= limit:
                break
    elif isinstance(a, list):
        if len(a) != len(b):
            out.append(f'{path}: length {len(a)} != {len(b)}')
        for i, (x, y) in enumerate(zip(a, b)):
            json_diff(x, y, f'{path}[{i}]', out, limit)
            if len(out) >= limit:
                break
    elif a != b:
        out.append(f'{path}: {json.dumps(a)[:120]} != {json.dumps(b)[:120]}')
    return out


def explain(rel, da, db, wa, wb, na, nb):
    if rel.endswith('.json'):
        try:
            a = json.loads(normalized(rel, da, wa, na))
            b = json.loads(normalized(rel, db, wb, nb))
            return json_diff(a, b)
        except ValueError:
            pass
    if rel.endswith('.npz') and da[:2] == b'PK' and db[:2] == b'PK':
        za, zb = zipfile.ZipFile(io.BytesIO(da)), zipfile.ZipFile(io.BytesIO(db))
        ma, mb = za.namelist(), zb.namelist()
        lines = [] if ma == mb else [f'members differ: {sorted(set(ma) ^ set(mb))[:10]}']
        for m in ma:
            if m in mb:
                xa = normalized(m, batch._npy(za.read(m), str(wa).encode()), wa, na)
                xb = normalized(m, batch._npy(zb.read(m), str(wb).encode()), wb, nb)
                if xa != xb:
                    lines.append(f'member {m}: {len(xa)} vs {len(xb)} bytes')
        return lines[:12]
    if rel.endswith('.mesh'):
        la, lb = int.from_bytes(da[:4], 'little'), int.from_bytes(db[:4], 'little')
        try:
            ha = json.loads(normalized('h.json', da[4:4 + la], wa, na))
            hb = json.loads(normalized('h.json', db[4:4 + lb], wb, nb))
            lines = json_diff(ha, hb)
            if da[4 + la:] != db[4 + lb:]:
                lines.append(f'body differs ({len(da) - 4 - la} vs {len(db) - 4 - lb} bytes)')
            return lines
        except ValueError:
            pass
    return [f'{len(da)} vs {len(db)} bytes']


def main():
    wa, wb = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    fa, fb = files(wa), files(wb)
    na, nb = digests(fa), digests(fb)
    differ = 0
    for rel in sorted(set(fa) | set(fb)):
        if rel in NOISE:
            continue
        if rel not in fa or rel not in fb:
            print('only in', 'B' if rel not in fa else 'A', rel)
            differ += 1
            continue
        da, db = Path(fa[rel]).read_bytes(), Path(fb[rel]).read_bytes()
        if normalized(rel, da, wa, na) != normalized(rel, db, wb, nb):
            differ += 1
            print('DIFFER', rel)
            for line in explain(rel, da, db, wa, wb, na, nb):
                print('   ', line)
    print(f'{differ} of {len(set(fa) | set(fb))} files differ (noise excluded: {sorted(NOISE)})')


main()
