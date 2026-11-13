"""Copies the built book from dist/ into the repository as hardware/printing-the-machine/: the leaves,
their stylesheet, the index, the bound-setting sources, and only the pictures a page shows."""
import json
import re
import shutil
import sys
from pathlib import Path

RUN = Path(__file__).parent
ROOT = RUN.parents[2]
DIST = RUN / "dist"
DEST = ROOT / "hardware" / "printing-the-machine"


def main():
    leaves = sorted(DIST.glob("[0-9][0-9]-*.html"))
    used = set()
    for leaf in leaves:
        text = leaf.read_text()
        used |= set(re.findall(r'src="art/([^"]+)"', text))
        used |= set(re.findall(r"url\(art/([^)]+)\)", text))
    missing = [n for n in sorted(used) if not (DIST / "art" / n).is_file()]
    if missing:
        sys.exit(f"pages name pictures that do not exist: {missing}")
    (DEST / "art").mkdir(parents=True, exist_ok=True)
    for old in list(DEST.glob("[0-9][0-9]-*.html")) + list((DEST / "art").iterdir()):
        old.unlink()
    for leaf in leaves:
        shutil.copyfile(leaf, DEST / leaf.name)
    for name in ("style.css", "README.md", "guide-inputs.json"):
        shutil.copyfile(DIST / name, DEST / name)
    for name in sorted(used):
        shutil.copyfile(DIST / "art" / name, DEST / "art" / name)
    m = json.loads((DIST / "art" / "manifest.json").read_text())
    images = {k: v for k, v in m["images"].items() if k in used}
    renders = []
    for job in m["renders"]:
        name = Path(job["out"]).name
        if name in used:
            job = dict(job)
            job["out"] = f"hardware/printing-the-machine/art/{name}"
            renders.append(job)
    listed = set(images) | {Path(j["out"]).name for j in renders}
    manifest = {"purpose": m["purpose"], "images": images, "renders": renders,
                "drawn_from_the_book_itself": sorted(used - listed)}
    (DEST / "art" / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    size = sum(f.stat().st_size for f in (DEST / "art").iterdir())
    print(f"{len(leaves)} leaves, {len(used)} pictures ({size / 1048576:.1f} MB) -> {DEST}")
    print("  pictures in no manifest entry:", sorted(used - listed))


if __name__ == "__main__":
    main()
