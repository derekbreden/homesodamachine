"""Atomic STEP / Assembly / DXF / PDF export helpers.

Concurrent runs targeting the same output file do not corrupt it: each call
writes to a unique temp file alongside the target and then renames atomically
via os.replace (POSIX-atomic rename). When two processes race — e.g. an agent
running the script directly while the dev server's watcher rebuilds the same
script — both produce complete files, last writer wins, and no consumer ever
observes a half-written .step. Each temp names the pid writing it, so an export
can clear the temps of builds that were killed before they could clean up after
themselves without touching one a live build is still filling.

Usage from any generator script:

    import sys
    from pathlib import Path
    sys.path.insert(
        0,
        str(next(p for p in Path(__file__).resolve().parents if p.name == "hardware") / "scripts"),
    )
    from _cadq_export import export_step          # for cq workplanes / solids
    from _cadq_export import export_assembly        # for cq.Assembly objects
    from _cadq_export import export_dxf            # for ezdxf Drawing objects
    from _cadq_export import export_pdf            # for ReportLab build callbacks

    export_step(model, str(out_path))
    export_assembly(assy, str(out_path))
    export_dxf(doc, str(out_path))
    export_pdf(lambda p: build_pdf_at(p), str(out_path))
"""

import atexit
import filecmp
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

# --- Build single-flight -----------------------------------------------------
# Every generator imports this module, so taking the global CAD build lock here
# covers all of them without editing 79 scripts. A newer build supersedes the one
# already running, and both say so — see _run_lock.py. Taken at import, before any
# geometry work, so the machine is freed as early as possible.
from _run_lock import acquire as _acquire_build_lock

if sys.argv and sys.argv[0].endswith(".py"):
    _entry = Path(sys.argv[0]).resolve()
    _root = Path(__file__).resolve().parent.parent.parent
    try:
        _label = str(_entry.relative_to(_root))
    except ValueError:
        _label = _entry.name
    _acquire_build_lock(_label)

# The lock's own test for whether a pid is still running, reused by the temp sweep
# to tell an abandoned file from one a live build is still writing.
from _run_lock import _alive as _pid_alive

# STEP files embed a wall-clock timestamp in the FILE_NAME header. Without
# normalization, every run produces different bytes for identical source —
# which churns git status and burns agent tokens chasing a non-change.
_STEP_TIMESTAMP_RE = re.compile(rb"'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'")
_STEP_CANONICAL_TIMESTAMP = b"'1970-01-01T00:00:00'"

# cq.Assembly.save mints a fresh v1 (time-based) UUID for any assembly node
# left unnamed and emits it as that node's PRODUCT id + name. Like the
# timestamp it differs every run, and it poisons the entity-ID renumbering
# below: the changed PRODUCT shifts the forward+reverse hashes of the whole
# product-structure subtree, which reshuffles every #id in the file. Scrub
# all UUIDs to one fixed value so an unnamed assembly is still byte-stable.
# A named assembly carries its name here instead of a UUID (no-op); a
# single-solid STEP has no PRODUCT at all.
_STEP_UUID_RE = re.compile(
    rb"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)
_STEP_CANONICAL_UUID = b"00000000-0000-0000-0000-000000000000"

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

# DXF non-determinism comes from four ezdxf-internal sources:
#
#   1. Wall-clock save times in four header variables, stored as Julian
#      dates: $TDCREATE, $TDUCREATE, $TDUPDATE, $TDUUPDATE.
#   2. Random UUIDs in two header variables: $FINGERPRINTGUID,
#      $VERSIONGUID, freshly generated on every save.
#   3. CLASSES-section entries emitted in dict-iteration order (varies
#      with PYTHONHASHSEED across runs, and across ezdxf versions).
#   4. ezdxf's own signature strings ("<version> @ <ISO-timestamp>")
#      embedded as the value of group code 1 in two DICTIONARYVAR
#      records near end-of-file.
#
# DXF format reminder: pairs of (group-code, value) lines. Group codes
# are right-aligned in a 3-char field — "  9", " 40", "  2", "  0", "  1".
_DXF_HEADER_TIMESTAMP_RE = re.compile(
    rb"(  9\n\$TD(?:U?CREATE|U?UPDATE)\n 40\n)[\d.]+\n"
)
_DXF_CANONICAL_TIMESTAMP = rb"\g<1>2440587.5\n"  # Julian date for 1970-01-01.

_DXF_HEADER_GUID_RE = re.compile(
    rb"(  9\n\$(?:FINGERPRINT|VERSION)GUID\n  2\n)\{[0-9A-Fa-f-]+\}\n"
)
_DXF_CANONICAL_GUID = rb"\g<1>{00000000-0000-0000-0000-000000000000}\n"

_DXF_EZDXF_SIGNATURE_RE = re.compile(
    rb"(\d+\.\d+\.\d+) @ "
    rb"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[+-]\d{2}:\d{2})?"
)
_DXF_CANONICAL_SIGNATURE = rb"\g<1> @ 1970-01-01T00:00:00.000000+00:00"

_DXF_CLASSES_SECTION_OPEN_RE = re.compile(rb"  0\nSECTION\n  2\nCLASSES\n")
_DXF_CLASSES_SECTION_CLOSE_RE = re.compile(rb"  0\nENDSEC\n")
_DXF_CLASS_BLOCK_RE = re.compile(rb"  0\nCLASS\n")
_DXF_CLASS_NAME_RE = re.compile(rb"  1\n([^\n]+)\n")

# PDF non-determinism. Two producers in this repo, two shapes:
#
#   ReportLab (Canvas.save) writes /CreationDate, /ModDate, and the
#   trailer /ID array as plain (uncompressed) bytes near end-of-file.
#   The regex patterns below catch all three.
#
#   Cairo (rsvg-convert, weasyprint, etc.) writes the same fields but
#   bundles them inside compressed object streams that the file-level
#   regex can't reach. Cairo honors SOURCE_DATE_EPOCH instead — set it
#   at the producer (see hardware/quickstart/appliance_quickstart.py),
#   and _canonicalize_pdf becomes a harmless no-op on Cairo output.
#
# Entries:
#   /CreationDate and /ModDate — PDF dates: D:YYYYMMDDHHMMSSOHH'MM'.
#   /ID array in the trailer — two hex strings; ReportLab regenerates
#       both on every save (the first is meant to be permanent).
_PDF_DATE_RE = re.compile(
    rb"\(D:\d{14}(?:Z|[-+]\d{2}'\d{2}')\)"
)
_PDF_CANONICAL_DATE = rb"(D:19700101000000+00'00')"

_PDF_ID_RE = re.compile(
    rb"(/ID\s*\[)<[0-9a-fA-F]+><[0-9a-fA-F]+>(\])"
)
_PDF_CANONICAL_ID = (
    rb"\g<1>"
    rb"<00000000000000000000000000000000>"
    rb"<00000000000000000000000000000000>"
    rb"\g<2>"
)


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
    new_data = _STEP_UUID_RE.sub(_STEP_CANONICAL_UUID, new_data)
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


def _canonicalize_dxf_classes_section(data):
    """Stable-sort the CLASS entries inside the CLASSES section. Each
    entry runs from `  0\\nCLASS\\n` up to (but not including) the next
    `  0\\nCLASS\\n` or `  0\\nENDSEC\\n`. Sort key is the DXF class
    name in group code 1 — the first `  1\\n<name>\\n` pair inside the
    block. Returns the original bytes unchanged if the CLASSES section
    is absent or malformed."""
    open_m = _DXF_CLASSES_SECTION_OPEN_RE.search(data)
    if open_m is None:
        return data
    close_m = _DXF_CLASSES_SECTION_CLOSE_RE.search(data, open_m.end())
    if close_m is None:
        return data
    body_start = open_m.end()
    body_end = close_m.start()
    body = data[body_start:body_end]

    starts = [m.start() for m in _DXF_CLASS_BLOCK_RE.finditer(body)]
    if len(starts) < 2:
        return data

    entries = []
    for i, s in enumerate(starts):
        e = starts[i + 1] if i + 1 < len(starts) else len(body)
        entries.append(body[s:e])

    def _key(entry):
        m = _DXF_CLASS_NAME_RE.search(entry)
        return m.group(1) if m else b""

    sorted_entries = sorted(entries, key=_key)
    if sorted_entries == entries:
        return data
    return data[:body_start] + b"".join(sorted_entries) + data[body_end:]


def _canonicalize_dxf(dxf_path):
    """Normalize ezdxf output for byte-stable hashing across runs:
    pin the four header save-time stamps, the two header GUIDs, and the
    two ezdxf signature timestamps; stable-sort the CLASSES section by
    class name. No-op on already-canonical files."""
    with open(dxf_path, "rb") as f:
        data = f.read()
    new_data = _DXF_HEADER_TIMESTAMP_RE.sub(_DXF_CANONICAL_TIMESTAMP, data)
    new_data = _DXF_HEADER_GUID_RE.sub(_DXF_CANONICAL_GUID, new_data)
    new_data = _DXF_EZDXF_SIGNATURE_RE.sub(_DXF_CANONICAL_SIGNATURE, new_data)
    new_data = _canonicalize_dxf_classes_section(new_data)
    if new_data != data:
        with open(dxf_path, "wb") as f:
            f.write(new_data)


def _canonicalize_pdf(pdf_path):
    """Normalize ReportLab PDF output for byte-stable hashing across
    runs: pin /CreationDate and /ModDate to the epoch, zero out both
    halves of the trailer /ID array. No-op on already-canonical files."""
    with open(pdf_path, "rb") as f:
        data = f.read()
    new_data = _PDF_DATE_RE.sub(_PDF_CANONICAL_DATE, data)
    new_data = _PDF_ID_RE.sub(_PDF_CANONICAL_ID, new_data)
    if new_data != data:
        with open(pdf_path, "wb") as f:
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
    atomic. The name carries the writing pid — `.<target>.<pid>.<rand><suffix>`
    — which is what `_sweep_orphan_temps` reads."""
    fd, tmp_path = tempfile.mkstemp(
        prefix=f".{target.name}.{os.getpid()}.",
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


def _sweep_orphan_temps(target):
    """Drop the temps in `target`'s directory whose writing build is gone.

    A build that raises unlinks its own temp, but SIGKILL has no exception path
    to run — and the dev-server watcher supersedes with SIGKILL deliberately,
    because CadQuery sits inside OCCT calls that ignore SIGTERM for seconds at a
    time (web/dev-server/server.js). So a killed generator leaves its temp
    behind, and the assemblies it leaves are the largest files in the tree.

    The pid in the name is what makes the sweep safe to run unconditionally:
    builds are single-flight but not exclusively so — one that yields to a
    protected commit gate takes no lock and runs alongside it (_run_lock), and
    HSM_NO_BUILD_LOCK opts out entirely — so a temp being written right now can
    be sitting in this directory, and it is the live pid that spares it. Best
    effort in the other direction: a pid the OS has since handed to an unrelated
    process reads as live, and its temp waits for a later sweep."""
    for p in target.parent.glob(f".*{target.suffix}"):
        owner = p.stem.rsplit(".", 2)          # `.<target>`, `<pid>`, `<rand>`
        if len(owner) != 3 or not owner[1].isdigit() or _pid_alive(int(owner[1])):
            continue
        try:
            p.unlink()
        except OSError:
            pass


def _matches_existing_target(tmp_path, target):
    """True if `target` is already byte-identical to `tmp_path` — i.e.
    the rename would be a no-op."""
    return target.exists() and filecmp.cmp(tmp_path, str(target), shallow=False)


def _atomic_write(target_path, write_fn):
    """Write atomically; return True if the target's bytes changed, False if
    the new output matched the existing file (no rename performed)."""
    target = Path(target_path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    _sweep_orphan_temps(target)
    tmp_path = _make_sibling_tempfile(target)
    try:
        write_fn(tmp_path)
        if target.suffix == ".step":
            _canonicalize_step(tmp_path)
        elif target.suffix == ".dxf":
            _canonicalize_dxf(tmp_path)
        elif target.suffix == ".pdf":
            _canonicalize_pdf(tmp_path)
        # Skip the rename when content matches — keeps target.mtime stable
        # and leaves git status clean across no-op regenerations.
        if _matches_existing_target(tmp_path, target):
            os.unlink(tmp_path)
            return False
        os.replace(tmp_path, target)
        return True
    except BaseException:
        _unlink_if_exists(tmp_path)
        raise


# --- Grid thumbnails ---------------------------------------------------------
#
# The viewer's grid shows a server-rendered PNG per STEP (web serves it at
# /thumbs/<file>.step.png) so browsing the catalog downloads small images
# instead of fetching every STEP and rendering it in the browser. The PNG is a
# pure function of the STEP, so it's regenerated here, right where the STEP is
# produced — meaning a direct run that writes a STEP (an agent, by hand, a batch
# build) refreshes its own thumbnail.
#
# Rendering is deferred to one batch at process exit (tools/render/
# render-thumbnails.js boots the viewer + a headless browser once per run, not
# once per part) and gated on the thumbnail being absent or older than its
# STEP — so no-op regenerations cost nothing. It's best-effort: a
# missing Node/render toolchain logs a warning and is skipped, never failing
# the STEP export itself. Set HSM_SKIP_THUMBNAILS=1 to skip entirely (fast CAD
# iteration / Python-only CI). The dev-server watcher sets it and rebuilds
# thumbnails off its own critical path instead, so a live save never blocks on a
# browser boot (web/dev-server/server.js).
#
# The shape is still in hand at this point, so its tessellation goes over with
# it (_mesh_payload) and the page renders from that instead of reading the STEP
# back through occt in wasm — the expensive half of a thumbnail by an order of
# magnitude. Tessellating is best-effort in the same way the render is: a shape
# that won't mesh queues the STEP alone and the page falls back to parsing it.

# `tools/` is shared machinery with ONE copy at the repo root, so it gets its own
# anchor rather than a walk up from this file: an edition's copy of this module sits
# the same distance below its own root, and a fixed walk would point the render tool
# at a tools/ its edition does not have. The tool is already edition-aware — it
# classifies each .step against the content roots itself — so only finding it is the
# question. `tools/docgen` is the sentinel every other shared-machinery anchor uses.
_TOOLS_ROOT = next(p for p in Path(__file__).resolve().parents
                   if (p / "tools" / "docgen").is_dir())
_THUMBNAIL_TOOL = _TOOLS_ROOT / "tools" / "render" / "render-thumbnails.js"
_pending_thumbnails = {}       # abs .step path -> abs payload path, or None
_thumbnail_tmpdir = None
_thumbnail_atexit_registered = False


def _write_mesh_payload(target, source):
    """Tessellate `source` beside the STEP it was exported to, into a temp the
    render tool reads and this process deletes. Returns the path, or None —
    every failure here just means the page parses the STEP instead."""
    global _thumbnail_tmpdir
    try:
        import _mesh_payload
        meshes = (_mesh_payload.from_assembly(source) if hasattr(source, "toCompound")
                  else _mesh_payload.from_shape(source))
        if not meshes:
            return None
        if _thumbnail_tmpdir is None:
            _thumbnail_tmpdir = tempfile.mkdtemp(prefix=f"hsm-mesh.{os.getpid()}.")
        path = os.path.join(_thumbnail_tmpdir, f"{len(_pending_thumbnails)}.mesh")
        _mesh_payload.write(meshes, path)
        return path
    except Exception as exc:
        print(f"[_cadq_export] tessellation for {target.name} skipped: {exc}", file=sys.stderr)
        return None


def _thumbnail_current(target, thumb):
    """Whether `thumb` was rendered from the STEP as it now stands. `_atomic_write` leaves an
    unchanged target's mtime alone, so a STEP newer than its thumbnail is one whose bytes have
    moved since the render — by this build or by one that rendered nothing."""
    try:
        return thumb.stat().st_mtime_ns >= target.stat().st_mtime_ns
    except OSError:
        return False


def _queue_thumbnail(target_path, source=None):
    if os.environ.get("HSM_SKIP_THUMBNAILS"):
        return
    target = Path(target_path).resolve()
    if target.suffix != ".step":
        return
    if _thumbnail_current(target, target.with_name(target.name + ".png")):
        return
    _pending_thumbnails[str(target)] = _write_mesh_payload(target, source) if source else None
    global _thumbnail_atexit_registered
    if not _thumbnail_atexit_registered:
        atexit.register(_render_pending_thumbnails)
        _thumbnail_atexit_registered = True


def _render_pending_thumbnails():
    if not _pending_thumbnails:
        return
    queued = dict(sorted(_pending_thumbnails.items()))
    _pending_thumbnails.clear()
    node = shutil.which("node")
    if node is None or not _THUMBNAIL_TOOL.exists():
        reason = "node not found on PATH" if node is None else "render tool missing"
        print(
            f"[_cadq_export] thumbnail render skipped for {len(queued)} part(s): {reason}",
            file=sys.stderr,
        )
    else:
        try:
            print(f"[_cadq_export] rendering {len(queued)} thumbnail(s)...", file=sys.stderr)
            handed = {k: v for k, v in queued.items() if v}
            args = [k for k in queued if k not in handed]
            if handed:  # the manifest lives in the payload dir, and goes with it
                manifest = os.path.join(_thumbnail_tmpdir, "payloads.json")
                with open(manifest, "w") as f:
                    json.dump(handed, f)
                args = ["--payloads", manifest, *args]
            subprocess.run(
                [node, str(_THUMBNAIL_TOOL), *args],
                cwd=str(_TOOLS_ROOT),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=600,
                check=False,
            )
        except Exception as exc:  # best-effort: a thumbnail must never break export
            print(f"[_cadq_export] thumbnail render failed: {exc}", file=sys.stderr)
    if _thumbnail_tmpdir:
        shutil.rmtree(_thumbnail_tmpdir, ignore_errors=True)


def export_step(model, target_path):
    """cq.exporters.export with atomic write."""
    import cadquery as cq
    _atomic_write(target_path, lambda p: cq.exporters.export(model, p))
    _queue_thumbnail(target_path, model)


def export_assembly(assembly, target_path):
    """cq.Assembly.export with atomic write. (Assembly.save is its deprecated
    alias — it just delegates to .export — and warns on every call.)"""
    _atomic_write(target_path, lambda p: assembly.export(p))
    _queue_thumbnail(target_path, assembly)


def export_dxf(doc, target_path):
    """ezdxf Drawing.saveas with atomic write and canonical output."""
    _atomic_write(target_path, lambda p: doc.saveas(p))


def export_pdf(build, target_path):
    """Atomic-write PDF with canonical output. `build(out_path)` is the
    caller's drawing function — it constructs a ReportLab Canvas at
    `out_path`, draws on it, and calls `.save()` itself. The wrapper
    supplies a temp path, canonicalizes the result, and renames into
    place only when the bytes change."""
    _atomic_write(target_path, build)
