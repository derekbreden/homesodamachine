"""Remove only the end-joining extrusion from specimen C's interface."""
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent/'petgf-interface-edges'))
from setback import moves


def main():
    exp = json.loads((HERE/'experiment.json').read_text())
    out = (ROOT/exp['project']).parent
    native = out/'native.gcode.3mf'
    with zipfile.ZipFile(native) as z:
        contents = {n:z.read(n) for n in z.namelist()}
    name = 'Metadata/plate_1.gcode'
    raw = contents[name]
    assert hashlib.md5(raw).hexdigest().upper().encode() == contents[name+'.md5']
    original = raw.decode()
    native_zs = {i:set() for i in range(1,5)}
    for _,_,m in moves(io.StringIO(original)):
        if m: native_zs[m['obj']].add(m['z'])
    c_top = max(native_zs[3])
    output, changed, c_zs, c_vertical = [], [], set(), 0
    for number, line, move in moves(io.StringIO(original)):
        replacement = line
        if move and move['obj'] == 3 and move['z'] == c_top:
            dx, dy = move['b'][0]-move['a'][0], move['b'][1]-move['a'][1]
            assert min(abs(dx),abs(dy)) < 1e-7, (number,dx,dy)
            c_zs.add(move['z'])
            if abs(dy) < 1e-7:
                replacement, count = re.subn(r'\sE[-+]?(?:\d*\.\d+|\d+\.?\d*)', '', line)
                assert count == 1
                changed.append(dict(line=number,z=move['z'],length_mm=abs(dx),removed_e=move['e']))
            else:
                c_vertical += 1
        output.append(replacement)
    assert len(c_zs) == 1 and len(changed) >= 20 and c_vertical >= 20
    final = ''.join(output)
    old_lines, new_lines = original.splitlines(True), final.splitlines(True)
    changed_numbers = {r['line'] for r in changed}
    assert len(old_lines) == len(new_lines)
    for i,(a,b) in enumerate(zip(old_lines,new_lines),1):
        if i not in changed_numbers: assert a == b
        else: assert re.sub(r'\sE[-+]?(?:\d*\.\d+|\d+\.?\d*)','',a) == b
    after_zs = {i:set() for i in range(1,5)}
    after_count = 0
    for _,_,m in moves(io.StringIO(final)):
        if not m: continue
        after_zs[m['obj']].add(m['z'])
        if m['obj'] == 3 and m['z'] == c_top:
            assert abs(m['a'][0]-m['b'][0]) < 1e-7
            after_count += 1
    assert after_count == c_vertical
    assert after_zs == native_zs and not after_zs[4], after_zs
    payload = final.encode()
    contents[name] = payload
    contents[name+'.md5'] = hashlib.md5(payload).hexdigest().upper().encode()
    target = out/'petgf-interface-patterns-mark2.gcode.3mf'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        for n,data in contents.items(): z.writestr(n,data)
    report = dict(source_bundle_sha256=hashlib.sha256(native.read_bytes()).hexdigest(),
        source_gcode_sha256=hashlib.sha256(raw).hexdigest(),
        bundle_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),gcode_sha256=hashlib.sha256(payload).hexdigest(),
        modification='Remove E words only from C interface end connections; retain all XYZ, feed, retraction and other commands.',
        all_other_lines_byte_identical=True,interface_z_by_object={str(k):sorted(v) for k,v in after_zs.items()},
        c_contact_plane_z=c_top,lower_branch_transition_preserved=True,
        c_independent_lines=c_vertical,removed_connection_count=len(changed),
        removed_connection_length_mm=sum(r['length_mm'] for r in changed),
        removed_filament_mm=sum(r['removed_e'] for r in changed),changed_lines=changed)
    (out/'pattern-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='changed_lines'},indent=2))


if __name__ == '__main__': main()
