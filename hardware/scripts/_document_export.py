"""Atomic PDF and analytical DXF exports without native CAD imports.

Writers fill a unique sibling temporary file, normalize document metadata, and
replace the target only when its bytes change. The shared output registry also
records unchanged exports for build tracing.
"""

import filecmp
import os
import re
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_WRITE_TARGETS = set()


def _pid_alive(pid):
    if not isinstance(pid, int) or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


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
#   `/Info` (tools/weld-rotator-guide/build.py).
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

    A build that raises unlinks its own temp. A killed process has no cleanup
    path, so the writing pid distinguishes its abandoned temp from a live
    writer's file. A pid the OS has reused reads as live and waits for a later
    sweep."""
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


def atomic_write(target_path, write_fn, *, canonicalize=None):
    """Write atomically; return True if the target's bytes changed, False if
    the new output matched the existing file (no rename performed)."""
    target = Path(target_path).resolve()
    try:
        _WRITE_TARGETS.add(target.relative_to(_ROOT).as_posix())
    except ValueError:
        pass                             # an output outside this repo is not a build-graph member
    target.parent.mkdir(parents=True, exist_ok=True)
    _sweep_orphan_temps(target)
    tmp_path = _make_sibling_tempfile(target)
    try:
        write_fn(tmp_path)
        if canonicalize is not None:
            canonicalize(tmp_path)
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


def export_dxf(source, target_path):
    """Export an analytical DXF document through its own ``saveas`` method."""
    atomic_write(target_path, lambda path: source.saveas(path))


def export_pdf(build, target_path):
    """Export a PDF written and saved by ``build(temporary_path)``."""
    atomic_write(target_path, build)
