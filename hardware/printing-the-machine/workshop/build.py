"""Builds the book's leaves. `preview <chapter>` draws one chapter's pages for checking;
`all` writes every leaf in order into dist/ and draws the whole book."""
import importlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import bookkit as b

ONLY = None  # set to a list of chapter names to build part of the book
ORDER = ["front", "anyfil", "petgf_setup", "petgf_overhangs", "petgf_supports", "petgf_design",
         "petgf_fits", "petg", "tpu", "aero", "petcf", "h2c", "back"]


def load(name):
    return importlib.import_module(f"chapters.{name}").pages()


def stage(pages, dest, first=1):
    dest.mkdir(parents=True, exist_ok=True)
    for old in dest.glob("*.html"):
        old.unlink()
    base = f'<head>\n<base href="file://{b.DIST}/">'
    for i, p in enumerate(pages):
        html = b.resolve(b.leaf(p, first + i)).replace("<head>", base, 1)
        (dest / f"{i + 1:02d}-{p.slug}.html").write_text(html)


def draw(src, out):
    out.mkdir(parents=True, exist_ok=True)
    for old in list(out.glob("*.png")) + list(out.glob("*.pdf")):
        old.unlink()
    r = subprocess.run(
        ["tools/run", "--", "node", "tools/render/render-card.js", "--batch", str(src), str(out),
         "--size", "2550x3300", "--pdf", "8.5x11in"],
        cwd=b.ROOT, capture_output=True, text=True)
    text = r.stdout + r.stderr
    problems = [l for l in text.splitlines() if any(w in l for w in ("OVERFLOW", "CLIPPED", "SPILL", "FAILED", "rror"))]
    small = out / "small"
    small.mkdir(exist_ok=True)
    for old in small.glob("*.png"):
        old.unlink()
    for png in sorted(out.glob("*.png")):
        subprocess.run(["sips", "-Z", "1100", str(png), "--out", str(small / png.name)], capture_output=True)
    return r.returncode, problems


def sync_static():
    b.DIST.mkdir(exist_ok=True)
    shutil.copyfile(b.RUN / "style.css", b.DIST / "style.css")


def preview(name):
    sync_static()
    pages = load(name)
    src = b.RUN / "preview" / name / "src"
    out = b.RUN / "preview" / name / "out"
    stage(pages, src)
    code, problems = draw(src, out)
    print(f"{name}: {len(pages)} pages -> {out}/small/*.png")
    for i, p in enumerate(pages):
        print(f"  {i + 1:02d} {p.slug}")
    for l in problems:
        print("  PROBLEM", l[l.find("out/") + 4:] if "out/" in l else l)
    if not problems:
        print("  no overflow or clipping")
    return code


def everything(draw_pages=True):
    sync_static()
    chapters = {}
    for name in ORDER:
        if ONLY and name not in ONLY:
            continue
        try:
            chapters[name] = load(name)
        except ModuleNotFoundError:
            print("  (no chapter yet:", name + ")")
    # the contents page lists every page, so number them first and then make the front matter again
    flat = [p for name in ORDER if name in chapters for p in chapters[name]]
    b.TOC[:] = [(p.part, p.title, i + 1) for i, p in enumerate(flat)]
    if "front" in chapters:
        chapters["front"] = load("front")
    pages = [p for name in ORDER if name in chapters for p in chapters[name]]
    for old in b.DIST.glob("*.html"):
        old.unlink()
    for i, p in enumerate(pages):
        (b.DIST / f"{i + 1:02d}-{p.slug}.html").write_text(b.leaf(p, i + 1))
    (b.DIST / "guide-inputs.json").write_text(json.dumps(b.SOURCES, indent=2) + "\n")
    (b.ART / "manifest.json").write_text(json.dumps(b.manifest(), indent=1) + "\n")
    readme(pages)
    src = b.RUN / "preview" / "_all" / "src"
    out = b.RUN / "preview" / "_all" / "out"
    stage(pages, src)
    # keep no more pixels of each photograph than the page shows: measure, then let asset() copy them again
    if not ONLY:
        m = subprocess.run(["tools/run", "--", "node", str(b.RUN / "measure.mjs"), str(src), str(b.META / "_sizes.json")],
                           cwd=b.ROOT, capture_output=True, text=True)
        print(" ", (m.stdout.strip().splitlines() or [m.stderr.strip()[-300:]])[-1])
        for name in chapters:
            load(name)
        (b.ART / "manifest.json").write_text(json.dumps(b.manifest(), indent=1) + "\n")
        for i, p in enumerate(pages):
            (b.DIST / f"{i + 1:02d}-{p.slug}.html").write_text(b.leaf(p, i + 1))
        stage(pages, src)
    if not draw_pages:
        print(f"{len(pages)} leaves written and measured, not drawn")
        return 0
    code, problems = draw(src, out)
    pdfs = sorted(str(p) for p in out.glob("*.pdf"))
    book = b.RUN / "preview" / "book.pdf"
    subprocess.run(["pdfunite", *pdfs, str(book)], check=True)
    print(f"{len(pages)} pages -> {book}")
    for i, p in enumerate(pages):
        print(f"  {i + 1:02d} [{p.part}] {p.title}")
    for l in problems:
        print("  PROBLEM", l[l.find("out/") + 4:] if "out/" in l else l)
    return code


def _text(html):
    """Plain text of an HTML fragment."""
    import html as h
    import re
    return re.sub(r"\s+", " ", h.unescape(re.sub(r"<[^>]+>", " ", html))).strip()


def readme(pages):
    """The index agents start from: where to begin for a job, then every page's rule by part."""
    import re
    files = {p.slug: f"{i + 1:02d}-{p.slug}.html" for i, p in enumerate(pages)}
    titles = {p.slug: _text(p.title) for p in pages}
    out = ["# Printing the Machine", "",
           "What nine months of printing the Home Soda Machine taught us about FDM, one plastic at a time.",
           "[Illustrated PDF](printing-the-machine.pdf) · [Website reader](https://homesodamachine.com/read/printing-the-machine/printing-the-machine.pdf)", "",
           "Each page of the book is one HTML file in this folder, built on one real print. Its title is the rule that print taught.",
           "Every page says which plastic, printer, plate and nozzle its evidence comes from. A lesson learned in one plastic is",
           "not a rule for another, so read the part for the plastic you are printing.", ""]
    start = b.RUN / "readme-start.md"
    if start.exists():
        text = start.read_text().rstrip()
        def link(m):
            slug = m.group(1)
            if slug not in files:
                raise KeyError(f"readme-start.md names a page that is not in the book: {slug}")
            return f"[{titles[slug]}]({files[slug]})"
        out += [re.sub(r"\[\[([a-z0-9-]+)\]\]", link, text), ""]
    out += ["## Every page, by part"]
    last = None
    for i, p in enumerate(pages):
        if p.cls == "cover":
            continue
        title = b.PARTS[p.part][0] or "Front matter"
        if p.part != last:
            out += ["", f"### {title}", ""]
            last = p.part
        lede = re.search(r'<p class="lede"[^>]*>(.*?)</p>', p.body, re.S)
        scope = re.search(r'<p class="scope">(.*?)</p>', p.body, re.S)
        line = f"- [{_text(p.title)}]({i + 1:02d}-{p.slug}.html)"
        if lede:
            line += " — " + _text(lede.group(1))
        if scope:
            seen = re.sub(r'<span class="nt">.*?</span>', "", scope.group(1), flags=re.S)
            line += f" *{_text(seen)}.*"
        if "{{" in line:
            raise ValueError(f"the index line for {p.slug} carries a bound value; keep settings out of its lede and scope")
        out.append(line)
    keep = b.RUN / "readme-keeping.md"
    if keep.exists():
        out += ["", keep.read_text().rstrip()]
    (b.DIST / "README.md").write_text("\n".join(out) + "\n")


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "preview":
        sys.exit(preview(sys.argv[2]))
    if len(sys.argv) >= 2 and sys.argv[1] == "all":
        ONLY = sys.argv[2:] or None
        sys.exit(everything())
    if len(sys.argv) == 2 and sys.argv[1] == "leaves":
        sys.exit(everything(draw_pages=False))
    print(__doc__)
    sys.exit(1)
