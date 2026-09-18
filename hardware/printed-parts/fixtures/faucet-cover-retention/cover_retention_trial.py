"""Restore the exact A–F retention-trial artifacts from their committed archive.

The archive is the geometry input. Its original CAD recipe and production
references are identified by retained-artifacts.json's source commit.
"""

import hashlib
import io
import json
from pathlib import Path
import tempfile
import zipfile

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "retained-artifacts.json"
OUTPUTS = frozenset(
    [f"cover-retention-{label}{suffix}"
     for label in "abcdef" for suffix in (".step", ".stl", ".step.mesh")]
    + ["trial-geometry.json"]
)


def checked_bytes(data, reading, name):
    """Return bytes only when both the retained size and digest match."""
    if len(data) != reading["bytes"] or hashlib.sha256(data).hexdigest() != reading["sha256"]:
        raise ValueError(f"Retained artifact differs: {name}")
    return data


def read_manifest(path=MANIFEST):
    manifest = json.loads(Path(path).read_text())
    if manifest.get("schema") != 1 or set(manifest.get("outputs", {})) != OUTPUTS:
        raise ValueError("Expected the complete retained A–F artifact manifest")
    names = [manifest["archive"]["file"], *manifest["records"]]
    if any(Path(name).name != name or name in ("", ".", "..") for name in names):
        raise ValueError("Retained archive and records must be fixture-local files")
    if set(manifest["records"]) & OUTPUTS:
        raise ValueError("Retained records must be separate from restored outputs")
    return manifest


def snapshot(path=MANIFEST):
    """Verify the whole archive and every member before exposing any output."""
    path = Path(path)
    manifest = read_manifest(path)
    entry = manifest["archive"]
    raw = checked_bytes((path.parent / entry["file"]).read_bytes(), entry, entry["file"])
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        names = archive.namelist()
        if len(names) != len(OUTPUTS) or set(names) != OUTPUTS:
            raise ValueError("Retained archive must contain each A–F output exactly once")
        data = {name: checked_bytes(archive.read(name), reading, name)
                for name, reading in manifest["outputs"].items()}
    return manifest, data


def restore(destination=HERE, path=MANIFEST):
    """Write the complete verified snapshot, retaining every published byte."""
    _, data = snapshot(path)
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    for name, raw in data.items():
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=destination, prefix=".retained-", delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(raw)
            temporary.chmod(0o644)
            temporary.replace(destination / name)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
    return len(data)


def verify_files(directory, readings):
    """Check held files without updating artifacts or historical reports."""
    for name, reading in readings.items():
        checked_bytes((Path(directory) / name).read_bytes(), reading, name)
    return len(readings)


def verify(directory=HERE, path=MANIFEST):
    manifest, _ = snapshot(path)
    return {
        "outputs": verify_files(directory, manifest["outputs"]),
        "records": verify_files(directory, manifest["records"]),
        "source_commit": manifest["source_commit"],
        "printed_tip_stl_sha256": manifest["printed_tip_stl_sha256"],
    }


def main():
    print(f"Restored {restore()} exact retained outputs for covers A–F")


if __name__ == "__main__":
    main()
