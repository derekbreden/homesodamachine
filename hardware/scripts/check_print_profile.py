#!/usr/bin/env python3
"""check_print_profile.py — a print log's stated settings are the slice's own.

A print log says what a plate was printed at, and names the file it read that off:

    ## The PET-GF15 exterior (settings per history-only `git:<rev>:<path>.3mf`)
    - `nozzle_temperature` **290 °C** (initial 290)

That heading is a claim about either a `.3mf` sitting beside it or an explicit `git:<rev>:<path>`
history reference. These numbers are not decoration — a nozzle temperature is what the next
person or agent slices at, and PET-GF at the wrong one is a plate of delamination.

WHAT MOVES THEM IS A RE-SAVE, NOT AN EDIT. Opening a project to refresh its models and saving it
back carries whatever the slicer had selected at the time: on 2026-08-29 one such re-save moved
`petgf.3mf`'s nozzle from 290 to 265, its printer preset from the +0.03 first layer to +0.02,
and its process from High Flow to Standard, none of them intended and none of them visible in a
diff of a zip. The prose beside it does not move at all, so the log goes on stating a
temperature the slice stopped holding, with nothing between them to notice.

FAILS (exit 1) when a stated figure is not what the named slice holds. A section that names a
file and states nothing is no claim and is not checked; a section stating a figure for a local
file that is not there, or for a history object Git cannot read, is a claim about nothing and
fails.

    python3 hardware/scripts/check_print_profile.py
"""

import io
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

_HW = Path(__file__).resolve().parent.parent

# The heading names the slice, so the claim carries its own source and this joins them on it
# rather than on a list kept somewhere else.
HEADING = re.compile(
    r"^#{2,3}[^\n]*settings per (?:\[`(?P<local>[^`]+\.3mf)`\]|"
    r"history-only `(?P<history>git:[^`]+\.3mf)`)", re.M)

# `**` closes before the parenthesis on the emphasised lines, so the bold runs are skipped
# wherever they fall rather than being written into the shape of the line.
#: One entry per figure a log states: the settings keys its two capture groups answer to, and
#: the pattern that finds it. The second key is the initial-layer figure, absent on most lines.
CLAIMS = (
    (("nozzle_temperature", "nozzle_temperature_initial_layer"),
     re.compile(r"`nozzle_temperature`\s*\**\s*([0-9.]+)\s*°C\s*\**\s*(?:\(initial\s*([0-9.]+)\))?")),
    (("layer_height", "initial_layer_print_height"),
     re.compile(r"`layer_height`\s*\**\s*([0-9.]+)\s*mm\s*\**\s*(?:\(initial\s*([0-9.]+)\))?")),
)


def settings(source: Path | bytes) -> dict:
    """A slice's settings, the process config under the filament one that overrides it."""
    archive = io.BytesIO(source) if isinstance(source, bytes) else source
    with zipfile.ZipFile(archive) as z:
        merged = json.loads(z.read("Metadata/project_settings.config"))
        if "Metadata/filament_settings_1.config" in z.namelist():
            merged.update(json.loads(z.read("Metadata/filament_settings_1.config")))
    return merged


def held(value):
    """The figure a settings key carries — the first slot where it is a per-filament list."""
    return value[0] if isinstance(value, list) else value


failures = []
drifted = []
claims = 0
logs = 0

for md in sorted(_HW.rglob("*print-log.md")):
    text = md.read_text()
    heads = [(m.start(), m.group("local") or m.group("history"))
             for m in HEADING.finditer(text)]
    if not heads:
        continue
    logs += 1
    edges = [h[0] for h in heads] + [len(text)]
    for i, (_start, name) in enumerate(heads):
        section = text[edges[i]:edges[i + 1]]
        stated = [(m, keys) for keys, rx in CLAIMS if (m := rx.search(section))]
        if not stated:
            continue                        # names a slice, states no figure: no claim to hold
        if name.startswith("git:"):
            _git, revision, rel = name.split(":", 2)
            shown = subprocess.run(
                ["git", "show", f"{revision}:{rel}"], cwd=_HW.parent,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if shown.returncode:
                failures.append(
                    f"{md.relative_to(_HW.parent)} states settings per {name}, which Git "
                    f"cannot read: {shown.stderr.decode(errors='replace').strip()}")
                continue
            source: Path | bytes = shown.stdout
        else:
            slice_path = md.parent / name
            rel = slice_path.relative_to(_HW.parent)
            if not slice_path.is_file():
                failures.append(f"{md.relative_to(_HW.parent)} states settings per {rel}, "
                                f"which is not in the tree")
                continue
            source = slice_path
        try:
            s = settings(source)
        except (OSError, KeyError, zipfile.BadZipFile, json.JSONDecodeError) as exc:
            failures.append(f"{name} does not read as a slice: {exc}")
            continue
        for m, keys in stated:
            for claimed, key in zip(m.groups(), keys):
                if claimed is None:
                    continue
                claims += 1
                actual = held(s.get(key))
                try:
                    same = actual is not None and float(claimed) == float(actual)
                except (TypeError, ValueError):
                    same = False
                if not same:
                    drifted.append(
                        f"{md.relative_to(_HW.parent)} states {key} {claimed} for {name}, "
                        f"which holds {actual}")

print(f"print profiles: {claims} stated figure(s) over {logs} log(s)")
if failures or drifted:
    print(f"\n{len(failures) + len(drifted)} stated setting(s) are not what the slice holds:")
    for f in failures + drifted:
        print(f"  ✗ {f}")
    if drifted:
        print("\n  Re-slicing carries whatever the slicer had selected. Either the log follows "
              "the slice, or the slice is restored to what the log says was printed.")
    sys.exit(1)
print("✓ every print log's stated settings are the ones its slice holds")
