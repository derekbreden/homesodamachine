"""Swap machine-data's generated source files for its typed ones in graph.json and BUILD.bazel
text, touching no other line.

usage: switch.py check                      — transform the working-tree files in memory, report
       switch.py write                      — rewrite the working-tree files in place
       switch.py blobs                      — print `<sha> <path>` for HEAD's files transformed
                                              (written to the object store with hash-object -w)
Every graph entry whose reads list a generated file reads the typed files instead; every BUILD
srcs list holding a generated file holds the typed files instead, each at its sorted place.
"""
import bisect, json, subprocess, sys
from pathlib import Path

REPO = Path('/Users/derekbredensteiner/Developer/homesodamachine')
CRATE = 'tools/hsm/machine-data/src/'
TYPED = sorted(f'{CRATE}typed/{p.name}' for p in (REPO / CRATE / 'typed').glob('*.rs'))


def generated(path):
    return path == f'{CRATE}compiled.rs' or path.startswith(f'{CRATE}compiled/')


def graph_text(text):
    graph = json.loads(text)
    if json.dumps(graph, indent=2) + '\n' != text:
        raise SystemExit('graph.json does not round-trip through json.dumps(indent=2)')
    changed = 0
    for entry in graph.values():
        if not isinstance(entry, dict) or not any(generated(r) for r in entry.get('reads', ())):
            continue
        reads = [r for r in entry['reads'] if not generated(r)]
        if reads != sorted(reads):
            raise SystemExit('a reads list is not sorted')
        for path in TYPED:
            if path not in reads:
                bisect.insort(reads, path)
        entry['reads'] = reads
        changed += 1
    out = json.dumps(graph, indent=2) + '\n'
    if 'machine-data/src/compiled' in out:
        raise SystemExit('a generated file is still named in graph.json')
    return out, changed


def build_text(text):
    lines = text.split('\n')
    out, changed, i = [], 0, 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not (stripped.startswith('"') and stripped.endswith('",')):
            out.append(line)
            i += 1
            continue
        # One run of string-literal lines at one indentation is one list.
        indent = line[:len(line) - len(line.lstrip())]
        j = i
        while j < len(lines) and lines[j].startswith(indent + '"') and lines[j].strip().endswith('",') \
                and lines[j][len(indent)] == '"':
            j += 1
        items = [l.strip()[1:-2] for l in lines[i:j]]
        if any(generated(p) for p in items):
            # The crate's own sources sit together, sorted; they are replaced as one run.
            at = [n for n, p in enumerate(items) if p.startswith(CRATE)]
            if at != list(range(at[0], at[-1] + 1)):
                raise SystemExit(f'the crate sources at line {i + 1} are not one run')
            run = [items[n] for n in at]
            if run != sorted(run):
                raise SystemExit(f'the crate sources at line {i + 1} are not sorted')
            run = sorted({p for p in run if not generated(p)} | set(TYPED))
            kept = items[:at[0]] + run + items[at[-1] + 1:]
            out.extend(f'{indent}"{p}",' for p in kept)
            changed += 1
        else:
            out.extend(lines[i:j])
        i = j
    result = '\n'.join(out)
    if 'machine-data/src/compiled' in result:
        raise SystemExit('a generated file is still named in BUILD.bazel')
    return result, changed


FILES = {'tools/bazel/graph.json': graph_text, 'BUILD.bazel': build_text}

if __name__ == '__main__':
    mode = sys.argv[1]
    report = {'typed_files': len(TYPED)}
    for path, transform in FILES.items():
        if mode == 'blobs':
            text = subprocess.run(['git', '-C', str(REPO), 'show', f'HEAD:{path}'], check=True,
                                  capture_output=True, text=True).stdout
        else:
            text = (REPO / path).read_text()
        result, changed = transform(text)
        report[path] = changed
        if mode == 'write':
            (REPO / path).write_text(result)
        elif mode == 'blobs':
            sha = subprocess.run(['git', '-C', str(REPO), 'hash-object', '-w', '--stdin'], input=result,
                                 check=True, capture_output=True, text=True).stdout.strip()
            print(sha, path)
    print(json.dumps(report), file=sys.stderr)
