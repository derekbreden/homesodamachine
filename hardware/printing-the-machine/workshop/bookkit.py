"""Page system for "Printing the Machine": parts, page furniture, text blocks, photographs,
model pictures and bound settings. A chapter module builds Page objects out of these."""
import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

RUN = Path(__file__).parent
ROOT = RUN.parents[2]
DIST = RUN / "dist"
ART = DIST / "art"
META = RUN / "art-src"
BOOK = "Printing the Machine"
TOC = []  # (part key, page title, page number) for every page; the build fills it before the contents page is made
GITHUB = "https://github.com/derekbreden/homesodamachine"

# key: title on the page, text on the thumb tab, colour, tab position down the page edge
PARTS = {
    "front": ("", "", "#111a22", None),
    "any": ("Before any filament", "ANY", "#111a22", 330),
    "petgf": ("PET-GF", "PET-GF", "#3a4654", 690),
    "petg": ("PETG", "PETG", "#1f8aa5", 1050),
    "tpu": ("TPU", "TPU", "#a8458a", 1410),
    "aero": ("ASA Aero", "AERO", "#b58a12", 1770),
    "petcf": ("PET-CF", "PET-CF", "#6b5b4a", 2130),
    "h2c": ("The H2C", "H2C", "#1d7d55", 2490),
    "back": ("At the back", "", "#111a22", None),
}


@dataclass
class Page:
    slug: str          # file name after the number, lower-case words joined by hyphens
    title: str         # the PDF outline entry and browser title
    part: str          # a key of PARTS
    body: str          # HTML between the running head and the footer
    right: str = ""    # right side of the running head
    cls: str = ""      # extra class on the article: "cover" drops the head, tab and footer


def _plain(title):
    """A page title as the PDF outline shows it: real characters, with only the three HTML-special ones escaped."""
    import html
    return html.unescape(title).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _fit(slug):
    """The scale the last whole-book build found this page needs for its content to fit (1 when it fits)."""
    f = META / "_sizes.json"
    if not f.exists():
        return 1
    return json.loads(f.read_text()).get("fit", {}).get(slug, 1)


def leaf(page, folio):
    title, tab, color, top = PARTS[page.part]
    if page.cls == "cover":
        inner = page.body
    else:
        tabdiv = f'<div class="tab" style="top:{top}px">{tab}</div>' if top else ""
        z = _fit(page.slug)
        zoom = f' style="zoom:{z}"' if z < 1 else ""
        inner = (f'<header class="run"><span><span class="chip"></span>{title or BOOK}</span><span>{page.right}</span></header>\n'
                 f'<main><div class="fit"{zoom}>\n{page.body}\n</div><i class="end"></i></main>\n'
                 f'<footer><span>{BOOK}</span><span class="folio">{folio:02d}</span></footer>\n{tabdiv}')
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{_plain(page.title)}</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<article class="page card {page.cls}" style="--part:{color}">
{inner}
</article>
</body>
</html>
"""


# ----------------------------------------------------------------------------- text blocks
def head(kicker, rule, lede="", size=176, lede_size=None, top=70):
    """Kicker, the page's one-line rule, and an optional lede under it."""
    ls = f' style="font-size:{lede_size}px"' if lede_size else ""
    led = f'<p class="lede"{ls}>{lede}</p>' if lede else ""
    return f'<p class="kicker" style="margin-top:{top}px">{kicker}</p><h1 class="rule" style="font-size:{size}px">{rule}</h1>{led}'


def scope(seen, not_tried="", label="Seen in"):
    """Says which plastic, printer, plate and nozzle the page's evidence comes from, e.g.
    scope("PET-GF · Mark 1 and Mark2 · textured PEI · left 0.4 mm", not_tried="PETG, TPU").
    For a page that is geometry or method, label="Holds for" and seen="any filament · shown here in PET-GF"."""
    nt = f'<span class="nt">Not tried in: {not_tried}</span>' if not_tried else ""
    return f'<p class="scope"><b>{label}</b> {seen}{nt}</p>'


def fig(src, alt, lab="", cap="", h=700, pos="50% 50%", zoom=None, style=""):
    """A photograph, cropped to h pixels tall. pos chooses which part shows ("x% y%").
    zoom (a percentage over 100) enlarges it first, e.g. zoom=170 shows the middle 60 percent;
    keep zoom large enough that the picture still fills the box. lab is its date, printer and
    plastic; cap says what happened."""
    labs = f'<span class="lab">{lab}</span>' if lab else ""
    caps = f'<figcaption class="cap">{labs}{cap}</figcaption>' if (lab or cap) else ""
    st = f' style="{style}"' if style else ""
    if zoom:
        img = f'<div class="photo" role="img" aria-label="{alt}" style="height:{h}px; background:url(art/{src}) {pos} / {zoom}% auto no-repeat"></div>'
    else:
        img = f'<img class="photo" src="art/{src}" alt="{alt}" style="height:{h}px; object-position:{pos}">'
    return f'<figure{st}>{img}{caps}</figure>'


def quote(text, who="DEREK", size=47):
    """Derek's words exactly as typed (keep his asterisks and spelling). who: "DEREK · 12 NOVEMBER 2026"."""
    return f'<blockquote style="font-size:{size}px">&ldquo;{text}&rdquo;<footer>{who}</footer></blockquote>'


def stat(big, small, hot=False):
    c = ' style="color:var(--hot)"' if hot else ""
    return f'<div class="stat"><p class="big"{c}>{big}</p><p class="tiny">{small}</p></div>'


def still_open(text):
    return f'<p class="open"><span class="tag open">Still open</span>{text}</p>'


def link(text, path, rev=None, anchor=""):
    """A link into the repository: the file at a Git revision, or on main when rev is None."""
    a = f"#{anchor}" if anchor else ""
    return f'<a href="{GITHUB}/blob/{rev or "main"}/{path}{a}">{text}</a>'


def model_link(text, find):
    """A link that opens the live 3D model with one solid or feature lit, e.g. find="feature: enclosure-front-bottom::west-z-rail"."""
    from urllib.parse import quote as q
    return f'<a href="https://homesodamachine.com/3d#step:manifold-layout%2Fenclosure-assembly.step?find={q(find)}">{text}</a>'


def record(*links):
    """The page's evidence, as links made with link()."""
    return '<div class="record"><h3>In the record</h3><p>' + " · ".join(links) + "</p></div>"


def table(rows, cls="recipe"):
    """rows: (name, value) pairs; value is usually setting(...)."""
    return f'<table class="{cls}">' + "".join(f'<tr><th scope="row">{a}</th><td>{b}</td></tr>' for a, b in rows) + "</table>"


def row(*cols, gap=60, align="flex-start", style=""):
    """Columns side by side. A column is HTML, or (css_flex, HTML) such as ("0 0 900px", html)."""
    out = []
    for c in cols:
        flex, inner = c if isinstance(c, tuple) else ("1 1 0", c)
        out.append(f'<div style="flex:{flex}; min-width:0">{inner}</div>')
    return f'<div class="row" style="gap:{gap}px; align-items:{align}; {style}">{"".join(out)}</div>'


def rulebar(top=56, bottom=44):
    return f'<div class="rulebar" style="margin:{top}px 0 {bottom}px"></div>'


def block(title, text, cls="small"):
    return f'<h2>{title}</h2><p class="{cls}">{text}</p>'


# ----------------------------------------------------------------------------- bound settings
SOURCES = {}


def source(name, path, revision=None, member=None):
    """Names a JSON file the book reads current values from: a file on disk, a file at a Git
    revision, or a member of a .3mf (member="Metadata/project_settings.config")."""
    entry = {"path": path}
    if revision:
        entry["revision"] = revision
    if member:
        entry["member"] = member
    if name in SOURCES and SOURCES[name] != entry:
        raise ValueError(f"source {name} already names {SOURCES[name]}")
    SOURCES[name] = entry
    return name


def setting(name, pointer):
    """A value read from its owning file when the book is bound. pointer is a JSON pointer such as
    "/layer_height" or "/nozzle_temperature/0". Use this for every current setting or current
    dimension; typed numbers go stale."""
    if name not in SOURCES:
        raise KeyError(f"unknown source {name}; call source() first")
    value(name, pointer)  # fail now if it does not resolve
    return "{{" + f"{name}:{pointer}" + "}}"


_cache = {}


def _load(name):
    if name not in _cache:
        s = SOURCES[name]
        if s.get("revision"):
            raw = subprocess.run(["git", "show", f"{s['revision']}:{s['path']}"], cwd=ROOT, capture_output=True, check=True).stdout
        elif s.get("member"):
            raw = subprocess.run(["unzip", "-p", str(ROOT / s["path"]), s["member"]], capture_output=True, check=True).stdout
        else:
            raw = (ROOT / s["path"]).read_bytes()
        _cache[name] = json.loads(raw)
    return _cache[name]


def value(name, pointer):
    """What a setting resolves to today (for checking; do not print it into a page)."""
    cur = _load(name)
    for tok in pointer.split("/")[1:]:
        tok = tok.replace("~1", "/").replace("~0", "~")
        cur = cur[int(tok)] if isinstance(cur, list) else cur[tok]
    if not isinstance(cur, (str, int, float)):
        raise TypeError(f"{name}:{pointer} is not a string or number")
    return cur


def resolve(html):
    """Fills every bound setting in a leaf, as the binder does."""
    out, rest = [], html
    while "{{" in rest:
        before, after = rest.split("{{", 1)
        key, rest = after.split("}}", 1)
        name, pointer = key.split(":", 1)
        out.append(before)
        out.append(str(value(name, pointer)))
    out.append(rest)
    return "".join(out)


# ----------------------------------------------------------------------------- pictures
def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _drawn_width(name):
    """How wide the build last measured this picture on a page, in page pixels; None before the first whole-book build."""
    f = META / "_sizes.json"
    if not f.exists():
        return None
    return json.loads(f.read_text()).get("need", {}).get(name)


def asset(name, src, revision=None, max_px=1700, kind="Bench photograph"):
    """Copies a photograph or figure from the repository into the book's art folder, turned upright and
    scaled so its long side is at most max_px, and records where it came from. src is a repo path;
    revision is the Git revision that holds it when it is no longer in the tree. Returns the file
    name for fig(). Crop with fig(pos=..., zoom=...) and its height, not by editing pixels.
    The whole-book build then keeps no more pixels than the page shows."""
    ART.mkdir(parents=True, exist_ok=True)
    META.mkdir(parents=True, exist_ok=True)
    out = ART / name
    meta = META / (name + ".json")
    max_px = min(max_px, 2000)
    drawn = _drawn_width(name)
    width = max(480, int(drawn * 0.7) + 1) if drawn else None  # about 210 pixels to the printed inch
    want = {"kind": kind, "source": src, "revision": revision, "max_px": max_px, "width_px": width, "made_with": "magick auto-orient"}
    if out.exists() and meta.exists():
        have = json.loads(meta.read_text())
        if all(have.get(k) == v for k, v in want.items()):
            return name
    tmp = META / ("_src_" + name + Path(src).suffix)
    if revision:
        tmp.write_bytes(subprocess.run(["git", "show", f"{revision}:{src}"], cwd=ROOT, capture_output=True, check=True).stdout)
    else:
        tmp.write_bytes((ROOT / src).read_bytes())
    cmd = ["magick", str(tmp), "-auto-orient", "-resize", f"{max_px}x{max_px}>"]
    if width:
        cmd += ["-resize", f"{width}x>"]
    cmd += ["-strip"]
    if not name.lower().endswith(".png"):
        cmd += ["-quality", "76"]
    subprocess.run(cmd + [str(out)], capture_output=True, check=True)
    want.update(source_sha256=_sha(tmp), image_sha256=_sha(out))
    tmp.unlink()
    meta.write_text(json.dumps(want, indent=1))
    return name


def render(name, job):
    """A picture of the model from hsm-render. job is the renderer's job without "out"; see the
    examples in the chapters. Returns the file name for an <img>. Drawn again only when the job
    changes."""
    ART.mkdir(parents=True, exist_ok=True)
    META.mkdir(parents=True, exist_ok=True)
    out = ART / name
    meta = META / (name + ".render.json")
    job = dict(job)
    job.setdefault("transparent", True)
    job.setdefault("ground", False)
    job.setdefault("fog", False)
    job.setdefault("ortho", True)
    job["out"] = str(out.relative_to(ROOT))
    text = json.dumps(job, sort_keys=True)
    if out.exists() and meta.exists() and meta.read_text() == text:
        return name
    jobs = META / (name + ".jobs.json")
    jobs.write_text(json.dumps([job]))
    r = subprocess.run(["tools/run", "--", "tools/hsm/target/release/hsm-render", "--root", ".", "--jobs", str(jobs)],
                       cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0 or not out.exists():
        raise RuntimeError(f"hsm-render failed for {name}: {r.stdout[-400:]} {r.stderr[-400:]}")
    jobs.unlink()
    # a palette of the picture's own colours: a fifth of the bytes, the same to the eye
    subprocess.run(["pngquant", "--quality", "80-98", "--speed", "1", "--skip-if-larger", "--force", "--ext", ".png", str(out)], capture_output=True)
    meta.write_text(text)
    return name


def manifest():
    """Every picture's source, gathered for art/manifest.json."""
    images, renders = {}, []
    for m in sorted(META.glob("*.json")):
        if m.name.endswith(".render.json"):
            renders.append(json.loads(m.read_text()))
        elif not m.name.endswith(".jobs.json") and not m.name.startswith("_"):
            images[m.name[:-5]] = json.loads(m.read_text())
    return {"purpose": "Trace the book's pictures to photographs in the repository and to model payloads.",
            "images": images, "renders": renders}
