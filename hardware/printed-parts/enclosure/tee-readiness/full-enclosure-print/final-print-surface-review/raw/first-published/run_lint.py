"""Read the exact published print meshes; write only this private audit folder."""
from contextlib import redirect_stderr
from datetime import datetime, timezone
from pathlib import Path
import gc
import hashlib
import io
import json
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'hardware/cad-artifacts.json').exists())
sys.path.insert(0, str(ROOT / 'hardware/scripts'))
import geometry_lint as gl


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def label(path):
    return str(Path(path).resolve().relative_to(ROOT))


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


enc = ROOT / 'hardware/printed-parts/enclosure/enclosure'
carrier = ROOT / 'hardware/printed-parts/enclosure/tee-carrier'
foam = ROOT / 'hardware/printed-parts/cold-core/foam-cap'
lid_inputs = ROOT / '.cache/prints/2026-09-21-g-ganen-foam-cap-lid-top-h2c-v2/inputs'
rows = [(enc / f'enclosure-{n}.stl', enc / f'enclosure-{n}.step')
        for n in ('front-top', 'front-bottom', 'back-bottom')]
rows += [(carrier / f'enclosure-tee-carrier-{n}.stl', carrier / f'enclosure-tee-carrier-{n}.step')
         for n in ('left', 'right')]
rows += [(foam / 'foam-cap-top.stl', foam / 'foam-cap-top.step'),
         (lid_inputs / 'foam-cap-lid-top.stl', foam / 'foam-cap-lid-top.step')]
summary = []
for mesh_path, native_path in rows:
    started = time.monotonic()
    pointer_path = ROOT / 'hardware/cad-artifacts.json'
    pointer_bytes = pointer_path.read_bytes()
    pointers = json.loads(pointer_bytes)
    targets = [native_path, Path(str(native_path) + '.mesh')]
    derivative = mesh_path.parent != native_path.parent
    if not derivative:
        targets += [mesh_path]
    published = {}
    for target in targets:
        actual = sha(target)
        if pointers['solids'].get(label(target)) != actual:
            raise ValueError(f'This artifact is not the current published pointer: {target}')
        published[label(target)] = actual
    if derivative:
        manifest_path = lid_inputs / 'print-inputs.json'
        manifest = json.loads(manifest_path.read_text())
        part = manifest['parts']['foam-cap-lid-top']
        if (Path(part['native_source']).resolve() != native_path.resolve()
                or part['native_source_sha256'] != sha(native_path)
                or Path(part['stl']).resolve() != mesh_path.resolve()
                or part['stl_sha256'] != sha(mesh_path)):
            raise ValueError('The derivative lid mesh is not bound to the published native lid')
    mesh_digest = sha(mesh_path)
    answers_path = native_path.with_suffix('.lint-answers')
    answers_text = answers_path.read_text() if answers_path.exists() else ''
    answers_digest = sha(answers_path) if answers_path.exists() else None
    print(f'START {mesh_path.stem}; published native/payload and print input verified', flush=True)
    errors = io.StringIO()
    with redirect_stderr(errors):
        mesh, found = gl.lint(mesh_path)
    entries = gl.parse_answers(answers_text)
    opened, answered = {}, []
    for kind, findings in found.items():
        opened[kind], matches = gl.split_answered(findings, entries)
        answered += [{'finding': finding, 'reason': reason} for finding, reason in matches]
    current_pointers = json.loads(pointer_path.read_text())
    drift = [name for name, digest in published.items()
             if sha(ROOT / name) != digest or current_pointers['solids'].get(name) != digest]
    if sha(mesh_path) != mesh_digest:
        drift.append(label(mesh_path))
    if answers_path.exists() and sha(answers_path) != answers_digest:
        drift.append(label(answers_path))
    report = {
        'status': 'read_only_lint_complete' if not errors.getvalue() and not drift else 'lint_input_or_pass_error',
        'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'mesh': label(mesh_path), 'mesh_sha256': mesh_digest,
        'native': label(native_path), 'published_member_sha256': published,
        'publication_pointer_sha256_at_start': hashlib.sha256(pointer_bytes).hexdigest(),
        'publication_source': pointers.get('source'),
        'derivative_print_mesh_from_published_native': derivative,
        'derivative_manifest_sha256': sha(manifest_path) if derivative else None,
        'answers': label(answers_path) if answers_path.exists() else None,
        'answers_sha256': answers_digest, 'printed_facets': len(mesh.faces),
        'lint_source_sha256': sha(Path(gl.__file__)), 'errors': errors.getvalue(), 'input_drift': drift,
        'unanswered_count': sum(len(v) for v in opened.values()), 'answered_count': len(answered),
        'open': opened, 'answered': answered,
        'scope': 'Mesh anomalies and exact existing answer-anchor matches only; no new physical acceptance or support approval.',
        'seconds': time.monotonic() - started,
    }
    save(HERE / (mesh_path.stem + '.json'), report)
    if answers_text:
        (HERE / (mesh_path.stem + '.answers-read.txt')).write_text(answers_text)
    text = [f'{mesh_path.stem}: {report["unanswered_count"]} open / {len(answered)} existing matches',
            f'Native: {label(native_path)}', f'Mesh SHA256: {mesh_digest}']
    for kind, findings in opened.items():
        for finding in findings:
            text += [f'[{kind}] {finding["line"]}', *finding['pick'], '']
    (HERE / (mesh_path.stem + '.open.txt')).write_text('\n'.join(text) + '\n')
    row = {k: report[k] for k in ('status', 'mesh', 'mesh_sha256', 'unanswered_count', 'answered_count', 'seconds')}
    summary.append(row)
    save(HERE / 'summary.json', {'status': 'in_progress', 'parts': summary})
    print(json.dumps(row), flush=True)
    del mesh, found, report
    gc.collect()
    if errors.getvalue() or drift:
        raise ValueError(f'Incomplete lint or input drift: {errors.getvalue()}, {drift}')
save(HERE / 'summary.json', {'status': 'all_requested_parts_linted_read_only', 'parts': summary,
                           'back_top_excluded_pending_regulator_correction': True})
