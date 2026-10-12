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
    preparation = json.loads((HERE / "print-preparation.json").read_text())
    sources = [HERE / name for name in (
        "README.md", "feature-guide.md", "manifest.json", "print-preparation.json",
        "geometry.json", "assembly-review.json", "print-plan.json", "native-summary.json", "reference-card.csv",
        "the-pour.step.png", "the-pour-rear.step.png")]
    sources.extend(sorted(HERE.glob("*.py")))
    sources.append(HERE / manifest["assembly"])
    for part in manifest["parts"]:
        sources.extend((ROOT / part["stl"], ROOT / part["step"]))
        for volume in part.get("material_volumes", []):
            sources.extend(ROOT / volume[key] for key in ("stl", "step") if key in volume)
        for key in ("stl", "step"):
            if key in part.get("seated_display", {}):
                sources.append(ROOT / part["seated_display"][key])
    for project in preparation["projects"]:
        path = ROOT / project["project"]
        sources.extend((path, path.with_suffix(".print.json")))
    # Editable source projects carry every material assignment and schedule.
    # Locally sliced archives remain identified by hash in the reading records.
    sources = list(dict.fromkeys(sources))
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
    release_tag = "the-pour-" + manifest["version"].lower()
    download_url = f"https://github.com/derekbreden/homesodamachine/releases/download/{release_tag}/{destination.name}"
    record = {"schema": 1, "name": manifest["title"],
              "release_tag": release_tag, "download_url": download_url,
              "archive": destination.name, "bytes": destination.stat().st_size,
              "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
              "files": files}
    (HERE / "print-kit.json").write_text(json.dumps(record, indent=2) + "\n")
    print(f"{destination.name}: {len(files)} files, {destination.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
