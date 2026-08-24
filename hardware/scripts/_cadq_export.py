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
    from _cadq_export import export_dxf            # for ezdxf Drawings / flat cq sections
    from _cadq_export import export_pdf            # for ReportLab build callbacks

    export_step(model, str(out_path))
    export_assembly(assy, str(out_path))
    export_dxf(doc, str(out_path))
    export_pdf(lambda p: build_pdf_at(p), str(out_path))
"""

import atexit
import filecmp
import hashlib
import os
import re
import subprocess
import sys
import tempfile
import time
from collections import Counter, defaultdict
from pathlib import Path

# --- Build single-flight -----------------------------------------------------
# Every generator imports this module, so taking the global CAD build lock here
# covers all of them without editing 79 scripts. A newer build supersedes the one
# already running, and both say so — see _run_lock.py. Taken at import, before any
# geometry work, so the machine is freed as early as possible.
_HERE = Path(__file__).resolve()
_ROOT = _HERE.parents[2]

# WHERE THIS RUN'S SECONDS START. Every generator imports this module before it cuts
# anything. The interpreter's own start and CadQuery's import stand ahead of this line,
# and `build-time.md` counts a generator's seconds from here.
_STARTED = time.perf_counter()

from _run_lock import acquire as _acquire_build_lock

# WHAT THIS RUN IS, named once. The lock says it to whoever it supersedes, and
# `build-time.md` files this run's seconds under it.
_ENTRY = None
if sys.argv and sys.argv[0].endswith(".py"):
    _entry = Path(sys.argv[0]).resolve()
    try:
        _ENTRY = _entry.relative_to(_ROOT).as_posix()
    except ValueError:
        _ENTRY = _entry.name

# A BUILD THAT SCHEDULES ITS OWN ACTIONS HOLDS NO MUTEX. The lock is single-flight for a
# machine where anyone may start a generator by hand; under Bazel the graph decides what runs
# beside what, and a lock taken at import would serialize every action on one another.
if _ENTRY is not None and not os.environ.get("HSM_NO_BUILD_LOCK"):
    _acquire_build_lock(_ENTRY)

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

# OpenCASCADE hands out its entity IDs (`#1`, `#2`, …) in the order it emits records, and
# for geometry that order is the same every run — two processes cutting the same solid write
# the same bytes once the header above is scrubbed. The styling records are the exception:
# the colour map they come off iterates in heap order, so which body each chain decorates
# moves between runs while the ID slots stay put. That is a permutation, and it is the whole
# of what is left to canonicalize.
#
# So the pass below hashes the styling records only — a Merkle-style hash per record over its
# downstream refs, plus an iteratively-refined reverse hash carrying the upstream referrer
# pattern — and seats them in their own slots in that order. The forward+iterated-reverse
# combination is what tells apart chains that carry the same colour and hang off different
# bodies, which is every chain in an assembly whose parts share a material.
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
#   A PRODUCER THAT COMPRESSES ITS TRAILER IS OUT OF REACH HERE. Cairo
#   (rsvg-convert, weasyprint) and Skia (a browser's `page.pdf`) write the
#   same fields inside object streams the file-level regex cannot see.
#   Cairo honors SOURCE_DATE_EPOCH, so a producer using it can set that
#   and leave this a harmless no-op; a browser honors nothing, and what
#   settles it there is the merge — pypdf drops each appended document's
#   `/Info` (hardware/assembly/cards/_build.py).
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


# The only records OpenCASCADE emits in an order that moves between runs are the styling ones:
# the chain a colour hangs on, and the presentation representation that roots it. Every point,
# curve, face and solid comes out in the same order every run — measured across processes, not
# assumed. So the renumbering has to reach the styling chain and nothing else. On the enclosure
# assembly that is a few thousand records out of 858,000, and the difference between those two
# numbers is most of what a generator spends.
#
# MEMBERSHIP IS STRUCTURAL AND NOT A LIST OF TYPE NAMES. A list is the failure that does not
# announce itself: miss a type and it stays a "geometry" record holding a reference this pass
# just renumbered, which is a broken file that still parses. The rule instead is a peel from
# the top — a record joins the set only when EVERY record that references it has already
# joined. The presentation roots are referenced by nothing, so they open it; the chain beneath
# them is reachable only through presentation, so it follows; and the solid a STYLED_ITEM
# colours is referenced by the shape representation too, so it never joins. Nothing outside
# the set can reference into it, which is the one precondition renumbering the set alone
# needs, and the peel gives that by construction rather than by inspection.
_STEP_TYPE_RE = re.compile(r"^\s*([A-Z_0-9]+)\s*\(")
#: Only picks which unreferenced records open the peel. It never decides membership.
_STEP_PRESENTATION_ROOTS = (
    "MECHANICAL_DESIGN_GEOMETRIC_PRESENTATION_REPRESENTATION",
    "DRAUGHTING_MODEL",
    "PRESENTATION_LAYER_ASSIGNMENT",
)


class _StepParseError(Exception):
    """A body that does not read the way STEP is written. The caller keeps the file."""


def _canonicalize_step_entity_ids(text):
    """Renumber the styling records in the DATA section so the file is
    byte-stable across runs with identical source. Returns None where the
    body will not parse or carries no styling, and the caller then keeps
    the file as written. Pure-stdlib, no STEP parser dependency."""
    try:
        data_start = text.index(_STEP_DATA_MARKER)
        data_end = text.index(_STEP_ENDSEC_MARKER, data_start)
    except ValueError:
        return None
    header = text[: data_start + len(_STEP_DATA_MARKER)]
    body = text[data_start + len(_STEP_DATA_MARKER) : data_end]

    # ONE SWEEP over the body does both jobs, and doing them in one is the difference between
    # this pass costing what the file costs and costing what the styling costs. It locates
    # every record, and it counts how many times each id is referenced by something that is
    # not that record's own definition. The two are told apart by the character in front of
    # the match: a definition is the only `#` that opens a line, because OCCT indents every
    # continuation. COUNTS, NOT REFERRER LISTS — a list per record is several million tuples
    # built to answer a question about two thousand of them.
    starts = []
    ref_count = defaultdict(int)
    for match in _STEP_REF_RE.finditer(body):
        at = match.start()
        if (at == 0 or body[at - 1] == "\n") and body[match.end() : match.end() + 2].lstrip()[:1] == "=":
            starts.append((int(match.group(1)), at))
        else:
            ref_count[int(match.group(1))] += 1
    if not starts:
        return None

    span = {}
    orig_pos = {}
    for i, (eid, at) in enumerate(starts):
        span[eid] = (at, starts[i + 1][1] if i + 1 < len(starts) else len(body))
        orig_pos[eid] = i

    rhs_cache = {}

    def _rhs(eid):
        """The record's right-hand side, sliced out of the body the first time it is asked
        for. Most records are never asked for."""
        cached = rhs_cache.get(eid)
        if cached is None:
            at, end = span[eid]
            match = _STEP_RECORD_RE.match(body[at:end].strip())
            if match is None:
                raise _StepParseError
            cached = match.group(2)
            rhs_cache[eid] = cached
        return cached

    try:
        # The peel: a record joins the styling set only when every reference to it has come
        # from inside the set. `remaining` counts the references still outstanding, so a
        # record becomes admissible exactly when its count reaches zero, and the solid a
        # STYLED_ITEM colours never does — the shape representation holds one of its
        # references and that one is never spent. Nothing outside the set can point into it,
        # which is the precondition for renumbering the set alone, and it holds by
        # construction rather than by inspection.
        remaining = dict(ref_count)
        queue = []
        for eid, _ in starts:
            if ref_count.get(eid):
                continue                 # a root is what nothing points at
            match = _STEP_TYPE_RE.match(_rhs(eid))
            if match and match.group(1).startswith(_STEP_PRESENTATION_ROOTS):
                queue.append(eid)

        styling = set()
        refs_all = {}
        while queue:
            eid = queue.pop()
            if eid in styling:
                continue
            styling.add(eid)
            outgoing = [int(m.group(1)) for m in _STEP_REF_RE.finditer(_rhs(eid))]
            refs_all[eid] = outgoing
            for target in outgoing:
                if target not in span:
                    continue
                remaining[target] = remaining.get(target, 0) - 1
                if remaining[target] == 0:
                    queue.append(target)
        if not styling:
            return None

        # THE INVARIANT THE NARROWING RESTS ON, checked on every file rather than argued once
        # on one: every reference to a styling record comes from a styling record. The peel's
        # admission rule already implies it, so a mismatch here means the sweep miscounted —
        # a `#` inside a string literal read as a reference, or a continuation line that
        # opened with one — and not that the file is unusual. The file is then left exactly as
        # OCCT wrote it, which costs determinism and says so, rather than shuffling the
        # colours of a solid that would still open fine.
        inbound = Counter()
        for eid in styling:
            for target in refs_all[eid]:
                if target in styling:
                    inbound[target] += 1
        for eid in styling:
            if inbound[eid] != ref_count.get(eid, 0):
                return None

        # Forward hash over the styling records alone. A reference OUT of the set — the solid
        # a STYLED_ITEM colours — is hashed as the id itself, because those ids do not move
        # between runs; that makes a chain's hash carry the identity of the body it decorates,
        # which is what tells two chains apart when they carry the same colour.
        prev_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(max(prev_limit, len(styling) + 1000))
        try:
            fwd_hash = {}
            in_progress = set()

            def _fwd(eid):
                cached = fwd_hash.get(eid)
                if cached is not None:
                    return cached
                if eid in in_progress:
                    return "CYC%d" % eid  # cycles aren't expected in STEP, but break safely
                in_progress.add(eid)
                normalized = _STEP_REF_RE.sub(
                    lambda m: "<%s>" % (
                        _fwd(int(m.group(1))) if int(m.group(1)) in styling
                        else "#%s" % m.group(1)
                    ),
                    _rhs(eid),
                )
                digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
                in_progress.discard(eid)
                fwd_hash[eid] = digest
                return digest

            for eid in styling:
                _fwd(eid)
        finally:
            sys.setrecursionlimit(prev_limit)

        # Iteratively refine: each round, a record's rev hash mixes in the rev hashes of who
        # references it, so after enough rounds it carries its whole upstream signature. Every
        # referrer of a styling record is itself styling — that is what the peel established —
        # so these rounds never read outside the set.
        referrers = defaultdict(list)
        for eid in styling:
            for arg_pos, target in enumerate(refs_all[eid]):
                if target in styling:
                    referrers[target].append((eid, arg_pos))

        no_ref, one_ref, many_ref = [], {}, {}
        for eid in styling:
            refs = referrers.get(eid)
            if not refs:
                no_ref.append(eid)
            elif len(refs) == 1:
                one_ref[eid] = refs[0]
            else:
                many_ref[eid] = refs

        rev_hash = dict(fwd_hash)
        for eid in no_ref:
            rev_hash[eid] = hashlib.sha256(
                (fwd_hash[eid] + "|[]").encode("utf-8")
            ).hexdigest()

        # A ROUND ONLY EVER TELLS RECORDS APART, so one whose forward hash is shared by no
        # other is already as far apart as it can get and is settled before the first round.
        fwd_count = Counter(fwd_hash[eid] for eid in styling)
        settled = {eid for eid in styling if fwd_count[fwd_hash[eid]] == 1}

        stale = (set(one_ref) | set(many_ref)) - settled
        for _ in range(_STEP_REV_HASH_ITERATIONS):
            moved = {}
            for eid in stale:
                solo = one_ref.get(eid)
                if solo is not None:
                    ref_eid, arg_pos = solo
                    sig_text = "[('%s', %d)]" % (rev_hash[ref_eid], arg_pos)
                else:
                    sig_text = str(sorted(
                        (rev_hash[ref_eid], arg_pos)
                        for ref_eid, arg_pos in many_ref[eid]
                    ))
                digest = hashlib.sha256(
                    (fwd_hash[eid] + "|" + sig_text).encode("utf-8")
                ).hexdigest()
                if digest != rev_hash[eid]:
                    moved[eid] = digest
            if not moved:
                break
            rev_hash.update(moved)
            stale = set()
            for eid in moved:
                stale.update(
                    r for r in refs_all[eid] if r in styling and r not in settled
                )

        # The styling records go back into the id slots they already occupy, in canonical
        # order. The slots are the same set every run — it is which chain lands in which that
        # moves — so sorting the records against the sorted slots pins each chain to one name.
        # Original position breaks the tie for records the graph cannot tell apart.
        seating = dict(zip(
            sorted(styling, key=lambda e: (rev_hash[e], orig_pos[e])),
            sorted(styling),
        ))
        reseated = {}
        for old, slot in seating.items():
            reseated[slot] = _STEP_REF_RE.sub(
                lambda m: "#%d" % seating[int(m.group(1))]
                if int(m.group(1)) in seating
                else m.group(0),
                _rhs(old),
            )

        # Only the styling spans are rewritten. Every other byte of the body is the one OCCT
        # wrote, which is why this costs the styling and not the file.
        pieces = []
        cut = 0
        for eid in sorted(styling, key=lambda e: span[e][0]):
            at, end = span[eid]
            pieces.append(body[cut:at])
            pieces.append("#%d = %s;\n" % (eid, reseated[eid]))
            cut = end
        pieces.append(body[cut:])
    except _StepParseError:
        return None

    return header + "".join(pieces) + text[data_end:]


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


#: Every solid THIS RUN loaded off the disk. A solid one generator cuts and the next loads is an
#: edge no import statement carries, so no walk over import statements can find it — which is how
#: a cap cut at 09:56 stood in an assembly built at 15:00 with every digest agreeing.
_STEP_READS = set()
#: Every path `_atomic_write` was handed, whether or not the bytes moved. A run that lands on
#: the solid already in the tree performs no rename, and cutting it is still what it came for.
_WRITE_TARGETS = set()


#: Every path a run named as one it reads, whether or not this run reached it. A tool a run
#: WOULD start is a file it reads: a scene already current starts no browser, and the renderer
#: it did not start is still what draws that picture.
_READ_TARGETS = set()


def note_read(path):
    """Keep `path` as one this run reads, for a tool a conditional branch may not reach."""
    try:
        _READ_TARGETS.add(Path(path).resolve().relative_to(_ROOT).as_posix())
    except ValueError:
        pass                             # a file outside this repo is nothing this tree reads


def note_write(path):
    """Keep `path` as one this run makes, for a file no `open` in this process lands on.

    A picture drawn by node and a drawing drawn by blender are written by a tool this run
    starts, below Python. The call that starts the tool is the one place that names them."""
    try:
        _WRITE_TARGETS.add(Path(path).resolve().relative_to(_ROOT).as_posix())
    except ValueError:
        pass                             # a file outside this repo is nothing this tree cuts


# --- What this run cost ------------------------------------------------------
#
# `ledger/build-time.md` carries the seconds a generator takes. This files one reading of
# them under the entry script's name, on the way out — see `_build_time.py`.
#
# A run that cut nothing files nothing: an import that raised, a build superseded off the
# machine, a script that only measured. `_WRITE_TARGETS` is what `_atomic_write` was handed.
def _file_elapsed():
    if _ENTRY is None or not _WRITE_TARGETS:
        return
    try:
        import _build_time
        _build_time.record(_ENTRY, time.perf_counter() - _STARTED)
    except Exception:
        pass                             # a reading that does not land costs the ledger one run


atexit.register(_file_elapsed)


def import_step(path):
    """The solid at `path`, and the record that this run read it.

    THE READ IS DECLARED HERE OR IT IS NOT DECLARED. `cq.importers.importStep` called directly
    loads the same solid and tells nobody, and what nobody was told is what nothing rebuilds."""
    import cadquery as cq

    p = Path(path).resolve()
    try:
        _STEP_READS.add(p.relative_to(_ROOT).as_posix())
    except ValueError:
        pass                             # a solid outside this repo is nothing this tree cuts
    return cq.importers.importStep(str(p))


def import_assembly(path):
    """`{name: (shape, color)}` for every named body in the assembly at `path`, stood where it
    stands — the shape of `enclosure_assembly._solids`, which pairs a body with what a reader
    needs alongside it.

    `importStep` hands back one compound and drops every name with it, so a caller that wants
    the funnel gets the machine. This reads the same file through XCAF, which is where the
    names are, and hands back the bodies under the names `export_assembly` wrote.

    WHY A CALLER WOULD RATHER READ THIS THAN BUILD IT. Standing the appliance is a hundred
    seconds and reading this file is five, and the bodies are identical — the STEP is what the
    build wrote. A drawing, a scene or a picture wants placed geometry and no more; deriving it
    a second time buys a second chance to derive it differently.

    A BODY OF SEVERAL SOLIDS COMES BACK UNDER ITS OWN NAME. `_per_solid_color` splits one such
    body into a component per solid so the viewer's reader can find a colour on each, and names
    them `display/1`, `display/2` — `SOLID_INDEX_SEP` and an index, which `bodyName` in
    web/public/js/viewer/step.js strips back off. The pieces are compounded back here, so what
    a caller asks for is the body the assembly added and not one solid of it.

    THE COLOUR COMES BACK BECAUSE THE MATERIAL IS THE COLOUR, and because nothing downstream
    would say if it did not. `check_bodies_colored` reads `_solids`, which is the machine in
    envelope terms — a body loaded here and handed on without its colour is drawn in the
    viewer's default gray and passes every gate on the way."""
    import cadquery as cq
    from OCP.Quantity import Quantity_Color, Quantity_TOC_RGB
    from OCP.STEPCAFControl import STEPCAFControl_Reader
    from OCP.TCollection import TCollection_ExtendedString
    from OCP.TDataStd import TDataStd_Name
    from OCP.TDF import TDF_Label, TDF_LabelSequence
    from OCP.TDocStd import TDocStd_Document
    from OCP.TopLoc import TopLoc_Location
    from OCP.XCAFDoc import XCAFDoc_ColorType, XCAFDoc_DocumentTool

    p = Path(path).resolve()
    try:
        _STEP_READS.add(p.relative_to(_ROOT).as_posix())
    except ValueError:
        pass
    doc = TDocStd_Document(TCollection_ExtendedString("hsm"))
    reader = STEPCAFControl_Reader()
    reader.SetNameMode(True)
    reader.SetColorMode(True)
    reader.ReadFile(str(p))
    reader.Transfer(doc)
    tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())

    colors = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())

    def named(label):
        attr = TDataStd_Name()
        return (attr.Get().ToExtString()
                if label.FindAttribute(TDataStd_Name.GetID_s(), attr) else "")

    # SURFACE FIRST AND GENERIC AFTER, because that is the order the writer sets them: a body
    # given one colour carries it as a surface colour, and the generic slot is what a document
    # with no per-face styling falls back to. The lookup is by SHAPE — a colour in XCAF is
    # attached to the shape the label holds, and the tool resolves the label from it.
    def color_of(shape):
        shade = Quantity_Color()
        for kind in (XCAFDoc_ColorType.XCAFDoc_ColorSurf,
                     XCAFDoc_ColorType.XCAFDoc_ColorGen):
            if colors.GetColor(shape, kind, shade):
                return cq.Color(shade.Red(), shade.Green(), shade.Blue())
        return None

    # A COMPONENT CARRIES THE PLACEMENT AND THE PROTOTYPE CARRIES THE SHAPE. The name is on
    # whichever of the two the writer put it on, so the component's is preferred and the
    # prototype's answers when it has none; the colour is looked for on both, the same way.
    out = {}

    def walk(label, place):
        kids = TDF_LabelSequence()
        tool.GetComponents_s(label, kids)
        if kids.Length() == 0:
            shape = tool.GetShape_s(label)
            if shape is not None and not shape.IsNull():
                out.setdefault(named(label), []).append(
                    (cq.Shape.cast(shape.Moved(place)), color_of(shape)))
            return
        for i in range(1, kids.Length() + 1):
            part = kids.Value(i)
            here = TopLoc_Location(place.Transformation()
                                   * tool.GetLocation_s(part).Transformation())
            proto = TDF_Label()
            if tool.GetReferredShape_s(part, proto):
                inner = TDF_LabelSequence()
                tool.GetComponents_s(proto, inner)
                if inner.Length() == 0:
                    shape = tool.GetShape_s(proto)
                    if shape is not None and not shape.IsNull():
                        name = named(part) or named(proto)
                        out.setdefault(name, []).append(
                            (cq.Shape.cast(shape.Moved(here)), color_of(shape)))
                else:
                    walk(proto, here)
            else:
                walk(part, here)

    free = TDF_LabelSequence()
    tool.GetFreeShapes(free)
    for i in range(1, free.Length() + 1):
        walk(free.Value(i), TopLoc_Location())

    bodies = {}
    for name, found in out.items():
        base = name.rsplit(SOLID_INDEX_SEP, 1)[0] if SOLID_INDEX_SEP in name else name
        bodies.setdefault(base, []).extend(found)
    placed = {}
    for name, found in bodies.items():
        shapes = [shape for shape, _color in found]
        shade = next((color for _shape, color in found if color is not None), None)
        placed[name] = (shapes[0] if len(shapes) == 1
                        else cq.Compound.makeCompound(shapes), shade)
    return placed


def _atomic_write(target_path, write_fn):
    """Write atomically; return True if the target's bytes changed, False if
    the new output matched the existing file (no rename performed)."""
    target = Path(target_path).resolve()
    try:
        _WRITE_TARGETS.add(target.relative_to(_ROOT).as_posix())
    except ValueError:
        pass                             # a solid outside this repo is nothing this tree cuts
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


# --- The mesh payload --------------------------------------------------------
#
# The shape is still in hand when a STEP is written, so its tessellation goes over
# with it and the page renders from that instead of reading the STEP back through
# occt in wasm. `loadStepFile` PREFERS a payload to the STEP beside it, so a payload
# older than the STEP is every reader — the page, the elevations, the scene shots —
# drawing a model the STEP no longer holds.
#
# EXCEPT WHERE NOBODY WILL EVER READ IT. An action holds a sandbox: `.step.mesh` is in
# no `outs`, so the one written there is discarded when the sandbox goes, and no reader
# in the tree is either helped or misled by it. That is a tessellation per exported
# solid — 103 across a full build — bought for nothing. HSM_SKIP_MESH_PAYLOAD says so,
# and the tree's payloads stay the business of the runs that keep them: a hand run and
# the dev-server watcher, neither of which sets it.
#
# A run that needs a payload IN the action writes its own and does not come through
# here — `render_scenes.draw_part` calls `_write_mesh_payload` directly, because the
# viewer it stands really does read one.


def _write_mesh_payload(target, source):
    """Tessellate `source` into `<target>.mesh`, beside the STEP it was exported to.

    THE GENERATOR IS STILL HOLDING THE SHAPE. The page reads the same triangles either way —
    through `occt-import-js` off the STEP's text in wasm, or off this. On the enclosure the
    parse is the whole cost of opening the model, against a fraction of that for the
    tessellation that produced the STEP in the first place, so the parse buys nothing but a
    round trip through text.

    It is not committed and not required: `_mesh_payload` writes what the wasm parse returns,
    so a page that does not find one reads the STEP and shows the same model. Returns the path,
    or None — every failure here just means the page parses the STEP instead."""
    try:
        import _mesh_payload
        meshes = (_mesh_payload.from_assembly(source) if hasattr(source, "toCompound")
                  else _mesh_payload.from_shape(source))
        if not meshes:
            return None
        path = str(target) + ".mesh"
        _mesh_payload.write(meshes, path, src=_mesh_payload.source_digest(target))
        return path
    except Exception as exc:
        print(f"[_cadq_export] tessellation for {target.name} skipped: {exc}", file=sys.stderr)
        return None


def _payload_current(target, mesh):
    """Whether `mesh` describes the STEP as it now stands AND states the version the
    page reads. `_mesh_payload.VERSION` names what a mesh entry carries; the page decodes
    that version and reads the STEP for any other, so a payload of an older one is a
    payload to write again — the STEP's bytes need not have moved for that to be true.

    WHETHER IT ANSWERS TO THIS STEP IS READ OFF ITS BYTES AND NEVER OFF ITS MTIME. A cache
    that restores outputs stamps what it restores with the time it restored it, so a payload
    of older descent arrives NEWER than the STEP just cut beside it, and an mtime test calls
    it current precisely when it is not. What is asked is descent and not agreement — a
    payload under `pack.BUNDLED_PAYLOAD_DIRS` carries flutes its STEP does not
    (`flute_payload`), and replacing it with a plain tessellation because the two surfaces
    differ would serve a smooth box. The digest `write` records is what settles it, and every
    writer of a payload records one."""
    try:
        import _mesh_payload
        if _mesh_payload.read_version(mesh) != _mesh_payload.VERSION:
            return False
        return _mesh_payload.read_source(mesh) == _mesh_payload.source_digest(target)
    except Exception:
        return False


def _write_payload_beside(target_path, source=None):
    """Tessellate `source` beside the STEP just written, when a reader in the tree will
    have it.

    A payload no older than the STEP and of the version the page reads was made from these
    bytes, so a build that moved nothing re-tessellates nothing. Tessellating is
    best-effort: a shape that will not mesh leaves the STEP alone and the page parses it."""
    target = Path(target_path).resolve()
    if target.suffix != ".step" or source is None:
        return
    if os.environ.get("HSM_SKIP_MESH_PAYLOAD"):
        return
    mesh = target.with_name(target.name + ".mesh")
    if not _payload_current(target, mesh):
        _write_mesh_payload(target, source)


def export_step(model, target_path):
    """cq.exporters.export with atomic write."""
    import cadquery as cq
    _atomic_write(target_path, lambda p: cq.exporters.export(model, p))
    _write_payload_beside(target_path, model)


#: What separates a body from the index of one of its solids, in the names
#: `_per_solid_color` mints. `bodyName` in web/public/js/viewer/step.js strips it
#: back off, so the index reaches the STEP and never reaches a reader.
#:
#: `_canonicalize_step_entity_ids` above rewrites `#<digits>` as an entity reference,
#: string literals included, in the styling records and only those. The names minted here
#: reach PRODUCT, which it leaves as written.
SOLID_INDEX_SEP = "/"


def _per_solid_color(assembly):
    """`assembly` with every colored body of several solids restated as one
    component per solid.

    OCCT-IMPORT-JS READS A COLOR OFF A COMPONENT, NOT OFF A SOLID: the viewer's
    reader looks the solid up in the shape tool (GetShapeColor in
    occt-import-js/src/importer-xcaf.cpp), and a solid sitting as a subshape of a
    multi-solid component has no label there to find. `_mesh_payload`'s selftest
    exports both shapes and reads them back through that reader.

    THE CALLER'S ASSEMBLY IS NOT TOUCHED — the split exists in the file, and every
    reader that names a body by name (the scorecard's tables, the web aliases, a
    `solid:` pick line) is handed the assembly as built. The index the split names
    carry comes off at the seam both routes into the viewer meet.

    An uncolored body is left whole."""
    import cadquery as cq

    obj, solids = assembly.obj, []
    if obj is not None:
        vals = obj.vals() if hasattr(obj, "vals") else [obj]
        solids = [s for v in vals for s in v.Solids()]
    split = assembly.color is not None and len(solids) > 1
    out = cq.Assembly(None if split else obj, name=assembly.name, loc=assembly.loc,
                      color=assembly.color, material=assembly.material,
                      metadata=assembly.metadata)
    if split:
        for i, solid in enumerate(solids, 1):
            out.add(solid, name=f"{assembly.name}{SOLID_INDEX_SEP}{i}", color=assembly.color)
    for child in assembly.children:
        out.add(_per_solid_color(child))
    return out


def export_assembly(assembly, target_path):
    """cq.Assembly.export with atomic write. (Assembly.save is its deprecated
    alias — it just delegates to .export — and warns on every call.)

    What is written is the per-solid-color restatement, and the tessellation
    handed over beside it is taken from that same assembly — the two routes into
    the viewer have to agree, and agreeing on the uncolored one is not the way."""
    colored = _per_solid_color(assembly)
    _atomic_write(target_path, lambda p: colored.export(p))
    _write_payload_beside(target_path, colored)


def export_dxf(source, target_path):
    """Write a DXF with atomic write and canonical output. `source` is either an
    ezdxf Drawing, saved through its own .saveas, or a CadQuery shape of a flat
    section, handed to cq.exporters.export — which keys the format off the suffix
    the temp file shares with the target."""
    if hasattr(source, "saveas"):
        _atomic_write(target_path, lambda p: source.saveas(p))
        return
    import cadquery as cq
    _atomic_write(target_path, lambda p: cq.exporters.export(source, p))


def export_pdf(build, target_path):
    """Atomic-write PDF with canonical output. `build(out_path)` is the
    caller's drawing function — it constructs a ReportLab Canvas at
    `out_path`, draws on it, and calls `.save()` itself. The wrapper
    supplies a temp path, canonicalizes the result, and renames into
    place only when the bytes change."""
    _atomic_write(target_path, build)
