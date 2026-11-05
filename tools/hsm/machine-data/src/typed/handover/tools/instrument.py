"""Insert a coverage marker at the start of each commented function in a generated crate copy."""
import re, sys
from pathlib import Path
src = Path(sys.argv[1])
marker = 'Val::function(move |args,kwargs| {'
total = 0
for path in sorted((src / 'compiled').glob('*.rs')):
    if path.name == 'modules.rs':
        continue
    out, pending = [], None
    for line in path.read_text().splitlines(keepends=True):
        m = re.match(r'// (\S+\.py:\d+ \S+)', line)
        if m:
            pending = f'{path.stem}|{m.group(1)}'
            out.append(line)
            continue
        if pending and marker in line:
            i = line.index(marker) + len(marker)
            line = line[:i] + f'crate::compiled::cover({pending!r:s});'.replace("'", '"') + line[i:]
            pending = None
            total += 1
        out.append(line)
    path.write_text(''.join(out))
print('instrumented', total)
