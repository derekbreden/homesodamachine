"""Classify the retained published-mesh readings without changing production files."""
from pathlib import Path
import hashlib
import json
import math
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'hardware/cad-artifacts.json').exists())
sys.path.insert(0, str(ROOT / 'hardware/scripts'))
import geometry_lint as lint


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def point(finding):
    return tuple(float(x) for x in re.search(
        r'click: x=([^ ]+) y=([^ ]+) z=([^ ]+)', '\n'.join(finding['pick'])).groups())


def clicks(findings):
    return '\n'.join(f'click: x={x:.3f} y={y:.3f} z={z:.3f}'
                     for x, y, z in dict.fromkeys(point(f) for f in findings))


stock = json.loads((HERE / 'current-stock-probes.json').read_text())
corbel = next(p for p in stock['probes'] if p['name'].startswith('left Wago inward root'))
# The original rectangular probe included the air beneath the 45-degree corbel.
# On the left tower that plane is z = x + 368.05. At z=271.40 it
# crosses x=-96.65; the empty triangle ends at x=-95.21 and spans 7.09 in Y.
expected_air = .5 * (-95.21 - (-96.65)) ** 2 * (126.34 - 119.25)
corbel_assessment = {
    'original_report_preserved': True,
    'original_report_sha256': sha(HERE / 'current-stock-probes.json'),
    'original_probe_missing_mm3': corbel['missing_mm3'],
    'expected_45_degree_air_wedge_mm3': expected_air,
    'absolute_difference_mm3': abs(expected_air - corbel['missing_mm3']),
    'pass': abs(expected_air - corbel['missing_mm3']) < 1e-8,
    'reason': 'The over-broad rectangular probe crossed the intended underside corbel. '
              'The independently tested complete 3 mm Wago floor is present. '
              'The 0.838643 mm edge lies 1.461357 mm below that floor.',
}
assert corbel_assessment['pass']
assert all(p['pass'] for p in stock['probes'] if p is not corbel)

summaries = []
proposal_dir = HERE / 'proposed-answers'
proposal_dir.mkdir(exist_ok=True)
for stem in ('enclosure-front-top', 'enclosure-front-bottom', 'enclosure-back-bottom',
             'enclosure-tee-carrier-left', 'enclosure-tee-carrier-right',
             'foam-cap-top', 'foam-cap-lid-top'):
    report = json.loads((HERE / f'{stem}.json').read_text())
    source = HERE / f'{stem}.answers-read.txt'
    original = source.read_text() if source.exists() else ''
    proposed = original
    groups = re.split(r'(?=^\[)', original, flags=re.M)
    open_rows = [f for rows in report['open'].values() for f in rows]
    classified = []

    def replace_group(prefix, extra, *, reason=None):
        global proposed
        matches = [g for g in groups if g.startswith(prefix)]
        assert len(matches) == 1, prefix
        old_group = matches[0]
        old_reason = old_group.splitlines()[0].split('] ', 1)[1]
        matched = [row['finding'] for row in report['answered'] if row['reason'] == old_reason]
        findings = matched + extra
        header = reason or old_group.splitlines()[0]
        native = report['native']
        new_group = f'{header}\nfile: {native}\n{clicks(findings)}\n\n'
        proposed = proposed.replace(old_group, new_group)
        classified.extend({'pick': point(f), 'class': f['class'], 'reason': header} for f in extra)

    def add_group(kind, reason, findings):
        global proposed
        proposed = proposed.rstrip() + f'\n\n[{kind}] {reason}\nfile: {report["native"]}\n{clicks(findings)}\n'
        classified.extend({'pick': point(f), 'class': kind, 'reason': reason} for f in findings)

    if stem == 'enclosure-front-top':
        replace_group('[step] The standing Z-seam', report['open']['step'])
        slivers = report['open']['sliver']
        by = lambda predicate: [f for f in slivers if predicate(point(f), f)]
        replace_group('[sliver] The aft flavour-valve tray', by(lambda p, f: abs(p[1]-176.690)<.002))
        replace_group('[sliver] These are the exposed ends of the carrier floor', by(lambda p, f: abs(p[1]-93.938)<.002))
        replace_group('[sliver] The outer tee well ends', by(lambda p, f: abs(p[1]-109.340)<.002))
        replace_group('[sliver] The outer valve', by(lambda p, f: p[1]>150 and abs(p[0])<100), reason=(
            '[sliver] The outer valve yoke-entry pocket enters the 9 mm flank by 1.35 mm, '
            'from |X|98.50 to |X|99.85. These narrow Y-normal faces are the aft ends of the '
            'open pockets, not freestanding strips. The nominal smooth flank backing is '
            '7.65 mm; the 1.2 mm exterior flutes leave at least 6.45 mm. Native full-stock '
            'probes retain 7.639 mm of continuous smooth-body X stock behind both complete '
            'pocket lengths. The 45-degree roofs in _front_top_flank_pockets preserve that backing.'))
        add_group('sliver', 'The yoke-entry pocket roof meets the underside corbel of the left '
                  'front Wago well here. Its 0.838643 mm exposed edge is below the well floor, '
                  'not a separate ligament. The complete 3 mm floor occupies Z272.85..275.85 '
                  'and remains present across the full tower. The pocket edge ends at '
                  'Z271.388643, 1.461357 mm below that floor; the remaining corbel joins the '
                  'tower to the full flank.', by(lambda p, f: abs(p[0]+97.5)<.002 and p[2]>270))
        add_group('sliver', 'These collinear STL triangles have zero area and a zero normal; '
                  'their strip dimensions are undefined. They add no surface area or volume '
                  'and do not describe a physical thin section. The complete unmodified mesh '
                  'is one watertight, consistently wound body. Removing these triangles alone '
                  'would break indexed edge adjacency and is not a geometry correction.',
                  by(lambda p, f: 'nan' in f['line'].lower()))
    elif stem == 'enclosure-front-bottom':
        replace_group('[ceiling] The front Z-slide', report['open']['ceiling'])
    elif stem == 'enclosure-back-bottom':
        replace_group('[ceiling] The rear Z-slide', report['open']['ceiling'])
        finite = [f for f in report['open']['sliver'] if 'nan' not in f['line'].lower()]
        zero = [f for f in report['open']['sliver'] if 'nan' in f['line'].lower()]
        entries = lint.parse_answers(original)
        letter_points = [p for k, reason, pts in entries if k == 'sliver' and reason.startswith('The disposal warning') for p in pts]
        translated = [min(math.dist(point(f), (p[0], p[1]+4.3, p[2])) for p in letter_points) for f in finite]
        assert len(finite) == 146 and max(translated) < .003
        replace_group('[sliver] These diagnostics are collinear', zero)
        replace_group('[sliver] The disposal warning', finite, reason=(
            '[sliver] The disposal warning has integral raised letters with 6.5 mm H capitals. '
            'These narrow faces are the letter strokes and the sides of their 0.6 mm outward '
            'projection. Every glyph is fused into the continuous rear wall behind the smooth '
            'field. The complete STL is one watertight, consistently wound body. The current '
            'production slice determines whether support contacts occur beneath the lettering; '
            'any contacts remain exposed on the rear exterior before assembly.'))
    elif stem == 'enclosure-tee-carrier-left':
        replace_group('[sliver] These 0.496 mm strips', [f for f in report['open']['sliver'] if point(f)[1] < 110])
        replace_group('[sliver] The 3 × 3 × 9 mm', [f for f in report['open']['sliver'] if point(f)[1] > 130])
    elif stem == 'foam-cap-lid-top':
        # Append only; the current file contains another agent's changes.
        add_group('ceiling', 'The fluid-14 tie tunnel is the open passage beneath its clamping '
                  'rib. Its flat roof bridges 2.8 mm along X between full 3 mm feet and spans '
                  '12.7 mm along Y. Native mouth probes verify 3.0 mm openings along both Y '
                  'directions above the 0.25 mm floor-relief lip. Detach any emitted support '
                  'from the roof, clear that lip and withdraw through an open mouth before '
                  'fitting tubing or ties. The current production slice supplies the actual '
                  'branch and contact geometry.', report['open']['ceiling'])
    if open_rows:
        new_entries = lint.parse_answers(proposed)
        unresolved = {kind: lint.split_answered(rows, new_entries)[0]
                      for kind, rows in report['open'].items()}
        assert sum(map(len, unresolved.values())) == 0, (stem, unresolved)
        (proposal_dir / f'{stem}.lint-answers').write_text(proposed)
    summaries.append({
        'part': stem, 'mesh_sha256': report['mesh_sha256'],
        'measured_report_sha256': sha(HERE / f'{stem}.json'),
        'unanswered_in_original_file': report['unanswered_count'],
        'existing_exact_matches': report['answered_count'], 'classified': classified,
        'private_proposal': str((proposal_dir / f'{stem}.lint-answers').relative_to(ROOT)) if open_rows else None,
        'unanswered_after_proposed_exact_anchors': 0,
        'fresh_slice_support_approval': False,
    })

assessment = {
    'status': 'retained_published_mesh_findings_classified',
    'production_files_changed': False,
    'scope': 'First published attempt; exact per-mesh hashes retained. Later native exports '
             'must be rebound after publication. These are geometry explanations, not print release.',
    'parts': summaries,
    'native_stock': {'complete_stock_probes_passed': 11, 'expected_corbel_air': corbel_assessment},
    'front_warning': 'The numerical zero-normal warning is explained by two zero-area mesh '
                     'triangles. No lint class failed. The original attempt/status is preserved.',
    'support_limit': 'Carrier existing answer paragraphs cite prior v1 slice tree/interface IDs. '
                     'They do not qualify future v2 support branches. Each fresh slice needs its own ledger.',
    'confirmed_physical_defects': [],
    'back_top_not_read': 'Awaiting corrected regulator placement and final publication.',
    'script_sha256': sha(__file__),
}
(HERE / 'assessment.json').write_text(json.dumps(assessment, indent=2) + '\n')
print(json.dumps({'status': assessment['status'], 'parts': len(summaries),
                  'proposed_answer_files': sum(p['private_proposal'] is not None for p in summaries),
                  'native_stock': assessment['native_stock']}, indent=2))
