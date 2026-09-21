"""Bind intentional back-top features to current published picks; no geometry edits."""
from pathlib import Path
import hashlib
import json
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'hardware/cad-artifacts.json').exists())
sys.path.insert(0, str(ROOT / 'hardware/scripts'))
import geometry_lint as lint

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
report = json.loads((HERE / 'enclosure-back-top.json').read_text())
answers = ROOT / report['answers']
assert sha(answers) == report['answers_sha256'], 'Concurrent answer edits'
pointer = json.loads((ROOT / 'hardware/cad-artifacts.json').read_text())
for name, digest in report['published_member_sha256'].items():
    assert sha(ROOT / name) == digest and pointer['solids'][name] == digest

entries = lint.parse_answers(answers.read_text())
found = [f for rows in report['open'].values() for f in rows]
found += [row['finding'] for row in report['answered']]
point = lambda f: tuple(float(x) for x in re.search(
    r'click: x=([^ ]+) y=([^ ]+) z=([^ ]+)', '\n'.join(f['pick'])).groups())
close = lambda a, b: abs(a - b) < .002
groups = []
assigned = []


def group(kind, prefix, predicate, *, reason=None):
    old = [r for k, r, _ in entries if k == kind and r.startswith(prefix)]
    assert len(old) == 1, prefix
    selection = [f for f in found if f['class'] == kind and predicate(point(f))]
    assert selection, prefix
    for f in selection:
        assert id(f) not in assigned, ('Duplicate assignment', point(f))
        assigned.append(id(f))
    groups.append({'class': kind, 'reason': reason or old[0], 'findings': selection})


group('step', 'The CO2 nut land', lambda p: close(p[0],13.216), reason=(
    'The CO2 nut land at Y466.3 stands 1 mm inside the Y465.3 wall field. '
    '`port_clamp_stack` retains 5 mm of wall plus chip at this station, and '
    '`station_land_draft` joins the two planes. The offset is the bulkhead fitting\'s '
    'clamp land, backed by the rear wall.'))
group('step', 'The PRV duct', lambda p: close(p[0],-104.5))
group('sliver', 'This face is the ceiling slab', lambda p: close(p[0],2.45))
group('sliver', 'The keystone receptacle', lambda p: close(p[0],-37.81))
group('sliver', 'The ASSE anchor', lambda p: close(p[0],-78.07))
group('sliver', 'The PRV duct', lambda p: close(p[0],-104.125) and p[1]>300)
group('sliver', 'The flank-section bottoms', lambda p: close(abs(p[0]),104.125) and p[1]<300)
group('sliver', 'These narrow faces bound the regulator', lambda p: close(p[0],-99.031), reason=(
    'This horizontal face bounds the regulator hub\'s 1.062178 mm-deep clearance pocket '
    'at X-99.562178..-98.5. It is the pocket edge in the thick flank, not a separate strip. '
    'The smooth native wall retains 7.937822 mm to X-107.5; the deepest 1.2 mm exterior '
    'flute leaves 6.737822 mm. The lower return is 45 degrees, and the locating barrel '
    'seat and supporting columns keep their full sections.'))
group('sliver', 'These two vertical returns join the flow-meter', lambda p: close(p[0],-12.36))
group('sliver', 'The aft end wall of the ASSE', lambda p: close(p[0],-93.227), reason=(
    'The aft end wall of the ASSE ceiling pocket has a 1 mm run beyond the anchor, '
    'not a 1 mm material thickness. The purchased body ends at Y410.51 and the pocket '
    'at Y412.51, keeping its 2 mm routing clearance. The complete shell lies west of '
    'this face, with 14.273 mm continuous stock at the anchor point.'))
group('sliver', 'These shoulders join the narrower', lambda p: close(p[0],32.029) or close(p[0],44.871))
group('ceiling', 'The ASSE pan', lambda p: close(p[0],-82.85))
group('ceiling', 'The pan sleeve', lambda p: close(p[0],-74.85))
group('ceiling', 'The nameplate bar', lambda p: close(p[2],266.15))
group('ceiling', 'The flavour-line anchor', lambda p: close(p[0],-88.285))
group('ceiling', 'The lower ledge inside', lambda p: close(p[0],38.16) and close(p[2],243.5))
group('ceiling', 'Relay 2', lambda p: close(p[0],97.375) and close(p[2],258.9))
group('ceiling', 'The ASSE tie cavity', lambda p: close(p[0],-100))
group('ceiling', 'The regulator and water-split', lambda p: close(p[1],256.81) or close(p[1],228.26))
group('ceiling', 'The C14 tunnel', lambda p: close(p[0],66.9))
group('ceiling', 'The rear Z-slide feet', lambda p: close(abs(p[0]),101.125))
group('ceiling', 'The keystone pocket', lambda p: close(p[0],-37.81))
group('ceiling', 'The PRV mouth', lambda p: close(p[0],-92))
group('ceiling', 'The joined upper main-board', lambda p: close(p[0],97.375) and close(p[2],327.2))
group('ceiling', 'The pan\'s flange', lambda p: close(p[0],-80.85))
group('ceiling', 'These two flat shoulders', lambda p: close(p[2],255.85))
group('ceiling', 'The ceiling-mounted anchors', lambda p: (
    close(p[0],2.45) or close(p[0],-40.81) or close(p[0],38.45)
    or close(p[0],18.345) or close(p[0],57.975)))
group('ceiling', 'The funnel brim', lambda p: close(p[0],0) and close(p[2],349))
assert len(assigned) == len(found) == 45

text = []
for row in groups:
    text += [f'[{row["class"]}] {row["reason"]}', f'file: {report["native"]}']
    text += [f'click: x={x:.3f} y={y:.3f} z={z:.3f}' for x,y,z in map(point,row['findings'])]
    text += ['']
proposed = '\n'.join(text).rstrip()+'\n'
new_entries = lint.parse_answers(proposed)
assert not any(lint.split_answered([f for f in found if f['class']==kind],new_entries)[0]
               for kind in report['open'])
(HERE / 'enclosure-back-top.lint-answers.proposed').write_text(proposed)
read = json.loads((ROOT/'hardware/manifold-layout/enclosure-box.json').read_text())
pack = dict(zip(read['box']['pack']['fields'],read['box']['pack']['values']))
relief, = pack['flank_reliefs']
assert relief[0] == 'flow-regulator'
record = {'status':'all_45_current_findings_classified','native_sha256':sha(ROOT/report['native']),
          'mesh_sha256':report['mesh_sha256'],'answer_input_sha256':sha(answers),
          'proposed_sha256':sha(HERE/'enclosure-back-top.lint-answers.proposed'),
          'current_box_sha256':sha(ROOT/'hardware/manifold-layout/enclosure-box.json'),
          'regulator_relief':relief,'groups':groups,
          'actual_support_topology':'Pending fresh ceiling-down production slice; no prior roads approved.'}
(HERE/'back-top-answer-assessment.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'status':record['status'],'groups':len(groups),'regulator_relief':relief},indent=2))
