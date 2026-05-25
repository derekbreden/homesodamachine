"""Atomic STEP / Assembly export helpers.

Concurrent runs targeting the same output file do not corrupt it: each call
writes to a unique temp file alongside the target and then renames atomically
via os.replace (POSIX-atomic rename). When two processes race — e.g. an agent
running the script directly while the dev server's watcher rebuilds the same
script — both produce complete files, last writer wins, and no consumer ever
observes a half-written .step.

Usage from any generate_step_cadquery.py:

    import sys
    from pathlib import Path
    sys.path.insert(
        0,
        str(next(p for p in Path(__file__).resolve().parents if p.name == "hardware")),
    )
    from _cadq_export import export_step          # for cq workplanes / solids
    from _cadq_export import export_assembly        # for cq.Assembly objects

    export_step(model, str(out_path))
    export_assembly(assy, str(out_path))
"""

import filecmp
import hashlib
import os
import re
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

# STEP files embed a wall-clock timestamp in the FILE_NAME header. Without
# normalization, every run produces different bytes for identical source —
# which churns git status and burns agent tokens chasing a non-change.
_STEP_TIMESTAMP_RE = re.compile(rb"'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'")
_STEP_CANONICAL_TIMESTAMP = b"'1970-01-01T00:00:00'"

# OpenCASCADE also assigns entity IDs (`#1`, `#2`, …) in non-deterministic
# order. Two runs producing the same geometry can interleave the IDs
# differently, again churning bytes for a non-change. We canonicalize by
# computing a Merkle-style hash per entity (recursive over its downstream
# refs) plus an iteratively-refined reverse hash that captures the upstream
# referrer pattern, then renumber 1..N in (rev_hash, original_position)
# order and rewrite every `#K` reference. The forward+iterated-reverse
# combination disambiguates entities that share content but live in
# different positions of the graph (very common for OCCT's redundant
# SURFACE_STYLE_USAGE / FILL_AREA_STYLE_COLOUR chains).
_STEP_RECORD_RE = re.compile(r"^#(\d+)\s*=\s*(.*?);\s*$", re.DOTALL)
_STEP_REF_RE = re.compile(r"#(\d+)")
_STEP_DATA_MARKER = "\nDATA;\n"
_STEP_ENDSEC_MARKER = "\nENDSEC;\n"
# Cap reverse-hash refinement; 20 rounds is more than enough for any real
# STEP graph (depth of upstream chain is small).
_STEP_REV_HASH_ITERATIONS = 20


def _canonicalize_step_entity_ids(text):
    """Renumber entity IDs in the DATA section so the file is byte-stable
    across runs with identical source. Returns None on parse failure so
    the caller can fall back to leaving IDs alone (which is the prior
    behavior). Pure-stdlib, no STEP parser dependency."""
    try:
        data_start = text.index(_STEP_DATA_MARKER)
        data_end = text.index(_STEP_ENDSEC_MARKER, data_start)
    except ValueError:
        return None
    header = text[: data_start + len(_STEP_DATA_MARKER)]
    body = text[data_start + len(_STEP_DATA_MARKER) : data_end]
    footer = text[data_end + 1 :]

    # Records can span multiple lines; assemble until a line ends with `;`.
    records = {}
    order = []
    buf = []
    for line in body.splitlines(keepends=True):
        buf.append(line)
        if line.rstrip().endswith(";"):
            joined = "".join(buf).strip()
            match = _STEP_RECORD_RE.match(joined)
            if match:
                eid = int(match.group(1))
                records[eid] = match.group(2)
                order.append(eid)
            buf = []
    if not records:
        return None

    # Recursion is bounded by entity-graph depth; raise the limit just for
    # the forward-hash walk and restore on the way out.
    prev_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(max(prev_limit, len(records) + 1000))
    try:
        fwd_hash = {}
        in_progress = set()

        def _fwd(eid):
            cached = fwd_hash.get(eid)
            if cached is not None:
                return cached
            if eid not in records:
                # External ref (shouldn't happen in well-formed STEP, but
                # we tolerate it by treating the id as an opaque token).
                return "EXT%d" % eid
            if eid in in_progress:
                # Cycles aren't expected in STEP, but break safely.
                return "CYC%d" % eid
            in_progress.add(eid)
            normalized = _STEP_REF_RE.sub(
                lambda m: "<%s>" % _fwd(int(m.group(1))),
                records[eid],
            )
            h = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
            in_progress.discard(eid)
            fwd_hash[eid] = h
            return h

        for eid in records:
            _fwd(eid)
    finally:
        sys.setrecursionlimit(prev_limit)

    # Build (target -> [(referrer, arg_position)]) so we can capture the
    # upstream pattern that distinguishes structurally-identical entities
    # plugged into structurally-different sites in the graph.
    referrers = defaultdict(list)
    for eid, rhs in records.items():
        for arg_pos, match in enumerate(_STEP_REF_RE.finditer(rhs)):
            target = int(match.group(1))
            if target in records:
                referrers[target].append((eid, arg_pos))

    # Iteratively refine: each round, an entity's rev hash mixes in the
    # rev hashes of who references it. After enough rounds the rev hash
    # captures the entire upstream subgraph signature.
    rev_hash = dict(fwd_hash)
    for _ in range(_STEP_REV_HASH_ITERATIONS):
        next_rev = {}
        for eid in records:
            sig = sorted(
                (rev_hash[ref_eid], arg_pos)
                for ref_eid, arg_pos in referrers[eid]
            )
            next_rev[eid] = hashlib.sha256(
                (fwd_hash[eid] + "|" + str(sig)).encode("utf-8")
            ).hexdigest()
        if next_rev == rev_hash:
            break
        rev_hash = next_rev

    # Stable canonical order: by rev hash, with original position as a
    # final tiebreaker for the (rare) cases where two entities are truly
    # indistinguishable in the graph.
    orig_pos = {eid: i for i, eid in enumerate(order)}
    sorted_ids = sorted(records, key=lambda e: (rev_hash[e], orig_pos[e]))
    new_id = {old: i + 1 for i, old in enumerate(sorted_ids)}

    out = [header]
    for canonical_id, old_id in enumerate(sorted_ids, start=1):
        rhs = records[old_id]
        new_rhs = _STEP_REF_RE.sub(
            lambda m: "#%d" % new_id[int(m.group(1))]
            if int(m.group(1)) in new_id
            else m.group(0),
            rhs,
        )
        out.append("#%d = %s;\n" % (canonical_id, new_rhs))
    out.append(footer)
    return "".join(out)


def _canonicalize_step(step_path):
    """Normalize STEP output for byte-stable hashing across runs:
    overwrite the FILE_NAME timestamp with a fixed value, and renumber
    entity IDs into a content-derived canonical order. Both are no-ops
    on already-canonical files."""
    with open(step_path, "rb") as f:
        data = f.read()
    new_data = _STEP_TIMESTAMP_RE.sub(_STEP_CANONICAL_TIMESTAMP, data, count=1)
    # Entity-ID canonicalization is text-based; decode using STEP's
    # ASCII-only conventions. If parsing fails for any reason, fall back
    # silently to the timestamp-only canonicalization rather than risking
    # a broken file.
    try:
        text = new_data.decode("ascii", errors="strict")
    except UnicodeDecodeError:
        text = None
    if text is not None:
        canonicalized = _canonicalize_step_entity_ids(text)
        if canonicalized is not None:
            new_data = canonicalized.encode("ascii")
    if new_data != data:
        with open(step_path, "wb") as f:
            f.write(new_data)


def _current_umask():
    """Read the process umask without changing it (os.umask only offers
    a swap; the only way to read is set-then-restore)."""
    umask = os.umask(0)
    os.umask(umask)
    return umask


def _make_sibling_tempfile(target):
    """Create an empty temp file next to `target`, sharing its suffix so
    write_fn's format dispatch (cq.exporters.export keys on the
    extension) picks the same format as the eventual target. Same
    directory keeps the final rename on one filesystem so os.replace is
    atomic."""
    fd, tmp_path = tempfile.mkstemp(
        prefix=f".{target.name}.",
        suffix=target.suffix,
        dir=str(target.parent),
    )
    os.close(fd)
    # mkstemp creates files at 0600; restore umask-default so the renamed
    # target ends up at 0644 rather than a private 0600.
    os.chmod(tmp_path, 0o666 & ~_current_umask())
    return tmp_path


def _unlink_if_exists(path):
    try:
        os.unlink(path)
    except FileNotFoundError:
        pass


def _matches_existing_target(tmp_path, target):
    """True if `target` is already byte-identical to `tmp_path` — i.e.
    the rename would be a no-op."""
    return target.exists() and filecmp.cmp(tmp_path, str(target), shallow=False)


def _atomic_write(target_path, write_fn):
    target = Path(target_path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = _make_sibling_tempfile(target)
    try:
        write_fn(tmp_path)
        if target.suffix == ".step":
            _canonicalize_step(tmp_path)
        # Skip the rename when content matches — keeps target.mtime stable
        # and leaves git status clean across no-op regenerations.
        if _matches_existing_target(tmp_path, target):
            os.unlink(tmp_path)
            return
        os.replace(tmp_path, target)
    except BaseException:
        _unlink_if_exists(tmp_path)
        raise


def export_step(model, target_path):
    """cq.exporters.export with atomic write."""
    import cadquery as cq
    _atomic_write(target_path, lambda p: cq.exporters.export(model, p))


def export_assembly(assembly, target_path):
    """cq.Assembly.save with atomic write."""
    _atomic_write(target_path, lambda p: assembly.save(p))
