#!/usr/bin/env python3
"""Package the checked exports, source, photographs and modeling records."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
NAME = 'xlaserlab-sup29f-xh'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'output'/NAME)
    args = parser.parse_args()
    output = args.output.resolve()
    validation = json.loads((output/'validation.json').read_text())
    if validation['detailed_stl_sha256'] != sha(output/(NAME+'.stl')):
        raise ValueError('Validation belongs to a different STL')
    if not validation['mesh']['watertight']:
        raise ValueError('Cannot package an open STL')
    for name in ('preview.png', 'side.png', 'rear.png', 'top.png',
                 'validation.json', 'mesh-check.json', 'cad-check.json'):
        shutil.copyfile(output/name, HERE/name)
    record = json.loads((HERE/'scan-evidence.json').read_text())
    record['reconstruction']['pinned_surfaces_sha256'] = sha(
        HERE/'source/reconstructed-surfaces.npz')
    (HERE/'scan-evidence.json').write_text(json.dumps(record, indent=2)+'\n')
    exports = [NAME+'.stl', NAME+'.glb', NAME+'.step',
               NAME+'.step.mesh', NAME+'-cad.stl']
    files = {name: output/name for name in exports}
    for path in HERE.rglob('*'):
        if path.is_file() and '__pycache__' not in path.parts and path.name not in (
                'reference-models.zip', 'delivery-manifest.json'):
            files[path.relative_to(HERE).as_posix()] = path
    manifest = {name: {'sha256': sha(path), 'bytes': path.stat().st_size}
                for name, path in sorted(files.items())}
    package = HERE/'reference-models.zip'
    with zipfile.ZipFile(package, 'w', compression=zipfile.ZIP_DEFLATED,
                         compresslevel=9) as z:
        for name, path in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 5, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, path.read_bytes(), compresslevel=9)
        z.writestr('manifest.json', json.dumps(manifest, indent=2)+'\n')
    with zipfile.ZipFile(package) as z:
        if z.testzip() is not None:
            raise ValueError('Corrupt model package')
        for name, entry in manifest.items():
            if hashlib.sha256(z.read(name)).hexdigest() != entry['sha256']:
                raise ValueError(f'Package checksum mismatch: {name}')
    manifest[package.name] = {'sha256': sha(package), 'bytes': package.stat().st_size}
    (HERE/'delivery-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(f'Verified {len(files)} files; package {package.stat().st_size:,} bytes')


if __name__ == '__main__':
    main()
