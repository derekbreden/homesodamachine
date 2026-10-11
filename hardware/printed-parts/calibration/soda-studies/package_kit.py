"""Package the current printable reference and its editable recipes for download."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from urllib.parse import quote, urlsplit
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools").is_dir())


def portable_markdown(source, data, members):
    """Keep kit links local; point source evidence back to the public repository."""
    def replace(match):
        url = urlsplit(match.group(2))
        if url.scheme or not url.path:
            return match.group(0)
        target = (source.parent / url.path).resolve()
        if target in members:
            return match.group(0)
        relative = target.relative_to(ROOT).as_posix()
        host = "raw.githubusercontent.com" if target.name == "print-kit.zip" else "github.com"
        branch = "main" if host.startswith("raw.") else "blob/main"
        link = f"https://{host}/derekbreden/homesodamachine/{branch}/{quote(relative)}"
        if url.fragment:
            link += "#" + url.fragment
        return match.group(1) + link + ")"
    return re.sub(r"(!?\[[^\]]*\]\()([^\s)]+)\)", replace, data.decode()).encode()


def main():
    manifest = json.loads((HERE / "manifest.json").read_text())
    sources = [HERE / name for name in (
        "README.md", "feature-guide.md", "manifest.json", "print-preparation.json",
        "the-pour.step.png")]
    sources += sorted(HERE.rglob("*.stl"))
    sources += sorted(HERE.rglob("*.step"))
    sources += sorted((HERE / "prints").glob("*.3mf"))
    sources = [p for p in sources if not p.name.endswith(".gcode.3mf")]
    sources += sorted((HERE / "prints").glob("*.print.json"))
    members = {p.resolve() for p in sources}
    files = []
    destination = HERE / "print-kit.zip"
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for source in sources:
            data = source.read_bytes()
            source_digest = hashlib.sha256(data).hexdigest()
            if source.suffix == ".md":
                data = portable_markdown(source, data, members)
            relative = source.relative_to(HERE).as_posix()
            info = zipfile.ZipInfo(relative, (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, data)
            files.append({"path": relative, "bytes": len(data),
                          "sha256": hashlib.sha256(data).hexdigest(),
                          "source_sha256": source_digest})
    record = {"schema": 1, "name": manifest["title"],
              "archive": destination.name, "bytes": destination.stat().st_size,
              "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
              "files": files}
    (HERE / "print-kit.json").write_text(json.dumps(record, indent=2) + "\n")
    print(f"{destination.name}: {len(files)} files, {destination.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
