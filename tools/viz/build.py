#!/usr/bin/env python3
"""Build one standalone page from real geometry, real renders, or a hand-authored fragment.

RUN BY HAND. NOT A STEP OF THE BUILD. This lives under `tools/`, which `tools/bazel/trace_inputs.py`
names in `ELSEWHERE`; it writes wherever `--out` says and nothing into the tree.

    python3 tools/viz/build.py SPEC.json --out PAGE.html
    python3 tools/viz/build.py --step hardware/faucet-layout/faucet-assembly.step --title "Faucet" --out PAGE.html
    python3 tools/viz/build.py --fragment widget.html --title "Pour timing" --out PAGE.html
    python3 tools/viz/build.py selftest

A 3D panel draws the triangles the /3d viewer draws: the payload the export wrote beside the STEP
(`hardware/scripts/_mesh_payload.py`), in the viewer's colours, finishes, light and ground. A
payload whose `src` digest is not the STEP's own is stale, and one that is missing is absent;
either way the STEP is read with occt-import-js, which is the viewer's route when it has no
payload (`tools/viz/step-mesh.cjs`). The footer says which route each model took.

The page follows the Artifact page contract (no document skeleton, `<title>` first, tokens on
`:root` with both dark blocks, scripts only from cdn.jsdelivr.net, 16 MB at most), so the same
file is sent to the side panel, screenshotted by `tools/viz/shot.mjs`, or published as is.

SPEC.json:

    {
      "title": "Nameplate snaps",                  page name, two to four words
      "lede": "Three snap depths, one camera.",    one line under it
      "view": "iso",                               iso front back left right top bottom
      "frame": "shared",                           one target and span for every panel, or "each"
      "sync": true,                                turning one panel turns them all
      "panels": [
        {"name": "Current", "caption": "Snap 1.2 mm", "step": "hardware/.../plate.step"},
        {"name": "Deeper", "pick": true, "models": [
            {"step": "hardware/manifold-layout/enclosure-assembly.step",
             "only": ["nameplate*", "enclosure-front*"],
             "highlight": ["nameplate*"], "ghost": ["enclosure-front*"]}]},
        {"name": "As printed", "image": "renders/plate.png"},
        {"name": "Snap sequence", "html": "lane.html"}
      ]
    }

`only` keeps the solids whose names match and drops the rest from the page; `highlight` draws
matches in the viewer's selection amber; `ghost` draws them translucent and leaves them out of
the framing. Names are the solid names the viewer's picker shows; `--list-solids` prints them.
Panels are lettered A, B, C in order unless a panel gives its own `label`.
"""

from __future__ import annotations

import argparse
import array
import base64
import datetime
import fnmatch
import gzip
import hashlib
import html
import json
import re
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
TEMPLATE = HERE / "page.html"
FINISHES = REPO / "web" / "public" / "finishes.json"
STEP_MESH = HERE / "step-mesh.cjs"

PAGE_LIMIT = 16_000_000   # the Artifact page limit, data URIs included
PAGE_HEAVY = 6_000_000    # past this a phone takes seconds to open the page
FINISH_TOL2 = 4e-4 * 4e-4  # the viewer's own match tolerance (web/public/js/viewer/step.js)
VIEWS = ("iso", "front", "back", "left", "right", "top", "bottom")
IMAGE_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
               ".webp": "image/webp", ".gif": "image/gif", ".svg": "image/svg+xml"}

# The inline widget's colour ramps (50 fill, 600 stroke, 800 title, 200 dark stroke, 100 dark
# title), so a fragment written for the inline surface draws the same when it is promoted here.
RAMPS = {
    "purple": ("#EEEDFE", "#CECBF6", "#AFA9EC", "#534AB7", "#3C3489"),
    "teal": ("#E1F5EE", "#9FE1CB", "#5DCAA5", "#0F6E56", "#085041"),
    "coral": ("#FAECE7", "#F5C4B3", "#F0997B", "#993C1D", "#712B13"),
    "pink": ("#FBEAF0", "#F4C0D1", "#ED93B1", "#993556", "#72243E"),
    "gray": ("#F1EFE8", "#D3D1C7", "#B4B2A9", "#5F5E5A", "#444441"),
    "blue": ("#E6F1FB", "#B5D4F4", "#85B7EB", "#185FA5", "#0C447C"),
    "green": ("#EAF3DE", "#C0DD97", "#97C459", "#3B6D11", "#27500A"),
    "amber": ("#FAEEDA", "#FAC775", "#EF9F27", "#854F0B", "#633806"),
    "red": ("#FCEBEB", "#F7C1C1", "#F09595", "#A32D2D", "#791F1F"),
}


class VizError(Exception):
    pass


# ── geometry ────────────────────────────────────────────────────────────────


def repo_path(p: str | Path) -> Path:
    path = Path(p)
    return path if path.is_absolute() else (REPO / path)


def shown(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO))
    except ValueError:
        return str(path)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_payload(path: Path) -> tuple[dict, bytes]:
    data = path.read_bytes()
    head_len = struct.unpack("<I", data[:4])[0]
    return json.loads(data[4:4 + head_len]), data[4 + head_len:]


def step_payload(step: Path) -> tuple[dict, bytes, str]:
    """The model's meshes and the route they came by: `payload` when the tessellation beside the
    STEP descends from these bytes, `payload (unstated)` when it names no source, `occt` when it
    is stale or absent and the STEP itself was read."""
    if not step.exists():
        raise VizError(f"no STEP at {shown(step)}")
    digest = sha256(step)
    beside = step.with_name(step.name + ".mesh")
    if beside.exists():
        head, blob = read_payload(beside)
        if head.get("v") in (2, 3):
            src = head.get("src")
            if src == digest:
                return head, blob, "payload"
            if src is None:
                return head, blob, "payload (unstated)"
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "read.mesh"
        try:
            run = subprocess.run(["node", str(STEP_MESH), str(step), str(out), digest],
                                 capture_output=True, text=True)
        except OSError as err:
            raise VizError(f"occt-import-js could not read {shown(step)}: {err}") from err
        if run.returncode != 0 or not out.exists():
            raise VizError(f"occt-import-js could not read {shown(step)}: {run.stderr.strip()[-400:]}")
        head, blob = read_payload(out)
    return head, blob, "occt"


def load_finishes() -> list[dict]:
    try:
        return json.loads(FINISHES.read_text()).get("finishes", [])
    except (OSError, ValueError):
        return []


def finish_for(color, finishes) -> list[float] | None:
    if not color:
        return None
    best, best_d = None, FINISH_TOL2
    for f in finishes:
        d = sum((a - b) ** 2 for a, b in zip(f["rgb"], color))
        if d <= best_d:
            best, best_d = [f["roughness"], f["metalness"]], d
    return best


def matches(name: str, globs) -> bool:
    return any(fnmatch.fnmatchcase(name, g) for g in globs or ())


class Models:
    """One embedded copy per (STEP, `only`) pair, however many panels draw it."""

    def __init__(self):
        self.meta: list[dict] = []
        self.blobs: list[bytes] = []
        self.keys: dict[tuple, int] = {}
        self.finishes = load_finishes()

    def add(self, step: Path, only) -> int:
        key = (str(step.resolve()), tuple(only or ()))
        if key in self.keys:
            return self.keys[key]
        head, blob, route = step_payload(step)
        meshes, out = [], bytearray()
        for m in head["meshes"]:
            name = m.get("name") or ""
            if only and not matches(name, only):
                continue
            pos = blob[m["pos"][0]: m["pos"][0] + 4 * m["pos"][1]]
            idx = blob[m["idx"][0]: m["idx"][0] + 4 * m["idx"][1]]
            color = m.get("color")
            xyz = array.array("f")
            xyz.frombytes(pos)
            entry = {"name": name, "color": color, "finish": finish_for(color, self.finishes),
                     "box": [[min(xyz[a::3]) for a in range(3)], [max(xyz[a::3]) for a in range(3)]]
                     if len(xyz) else None,
                     "pos": [len(out), m["pos"][1]]}
            out += pos
            entry["idx"] = [len(out), m["idx"][1]]
            out += idx
            meshes.append(entry)
        if not meshes:
            names = sorted({m.get("name") or "" for m in head["meshes"]})
            raise VizError(f"`only` {list(only)} matches no solid in {shown(step)}; it has {names[:40]}")
        tris = sum(m["idx"][1] for m in meshes) // 3
        self.meta.append({"step": shown(step), "route": route, "tris": tris,
                          "solids": len(meshes), "meshes": meshes})
        self.blobs.append(gzip.compress(bytes(out), 6))
        self.keys[key] = len(self.meta) - 1
        return self.keys[key]


def list_solids(step: Path) -> list[str]:
    head, _, _ = step_payload(step)
    return [m.get("name") or "" for m in head["meshes"]]


# ── page ────────────────────────────────────────────────────────────────────


def esc(text) -> str:
    return html.escape(str(text), quote=True)


def shim_css() -> str:
    """The inline widget's tokens and SVG classes, drawn in this page's palette."""
    lines = [
        "<style>",
        ":root { --text-primary: var(--ink); --text-secondary: var(--muted); --text-muted: var(--muted);",
        "  --text-accent: var(--accent); --text-danger: #c2362f; --text-success: #2f7d32; --text-warning: #9a6200;",
        "  --surface-0: var(--ground); --surface-1: var(--ground); --surface-2: var(--paper); --surface-3: var(--paper);",
        "  --bg-accent: color-mix(in srgb, var(--accent) 12%, var(--paper)); --bg-danger: #fcebeb; --bg-success: #eaf3de; --bg-warning: #faeeda;",
        "  --border: var(--rule); --border-strong: color-mix(in srgb, var(--ink) 28%, transparent);",
        "  --border-stronger: color-mix(in srgb, var(--ink) 40%, transparent); --border-accent: var(--accent);",
        "  --font-sans: var(--text); --font-mono: var(--data); --font-voice: Georgia, serif; --radius: 8px;",
        "  --pad-sm: 8px; --pad-md: 12px; --pad-lg: 16px; --pad-xl: 24px;",
        "  --gap-xs: 4px; --gap-sm: 8px; --gap-md: 12px; --gap-lg: 16px; --gap-xl: 24px;",
        "  --p: var(--ink); --s: var(--muted); --t: var(--muted); --bg2: var(--ground); --b: var(--rule); }",
        ".viz-body svg text.t, .viz-stage svg text.t { font: 400 14px var(--text); fill: var(--ink); }",
        ".viz-body svg text.th, .viz-stage svg text.th { font: 500 14px var(--text); fill: var(--ink); }",
        ".viz-body svg text.ts, .viz-stage svg text.ts { font: 400 12px var(--text); fill: var(--muted); }",
        ".box { fill: var(--ground); stroke: var(--border-strong); }",
        ".node { cursor: pointer; } .node:hover { opacity: 0.82; }",
        ".arr { stroke: var(--muted); stroke-width: 1.5; fill: none; }",
        ".leader { stroke: var(--muted); stroke-width: 0.5; stroke-dasharray: 3 3; fill: none; }",
    ]
    for ramp, (f50, f100, f200, f600, f800) in RAMPS.items():
        shapes = ", ".join(f".c-{ramp} > {s}, {s}.c-{ramp}" for s in ("rect", "circle", "ellipse", "polygon"))
        lines.append(f"{shapes} {{ fill: {f50}; stroke: {f600}; }}")
        lines.append(f".c-{ramp} > text.t, .c-{ramp} > text.th {{ fill: {f800}; }} .c-{ramp} > text.ts {{ fill: {f600}; }}")
        dark = (f"{shapes} {{ fill: {f800}; stroke: {f200}; }} "
                f".c-{ramp} > text.t, .c-{ramp} > text.th {{ fill: {f100}; }} .c-{ramp} > text.ts {{ fill: {f200}; }}")
        lines.append(f"@media (prefers-color-scheme: dark) {{ :root:not([data-theme=\"light\"]) {dark} }}")
        lines.append(f":root[data-theme=\"dark\"] {dark}")
    lines.append("</style>")
    lines.append("<script>")
    lines.append("window.sendPrompt = function (text) { try { navigator.clipboard.writeText(text); } catch (e) {} "
                 "console.log('sendPrompt (copied to the clipboard here):', text); };")
    lines.append("window.openLink = function (url) { window.open(url, '_blank', 'noopener'); };")
    lines.append("</script>")
    return "\n".join(lines)


def data_uri(path: Path) -> str:
    mime = IMAGE_TYPES.get(path.suffix.lower())
    if not mime:
        raise VizError(f"{shown(path)} is not an image this page can carry ({', '.join(IMAGE_TYPES)})")
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def normalise(spec: dict, base: Path) -> dict:
    """Spec paths resolve against the spec's own folder first, then the repo."""
    def resolve(p):
        cand = (base / p) if not Path(p).is_absolute() else Path(p)
        return cand if cand.exists() else repo_path(p)

    panels = []
    for i, p in enumerate(spec.get("panels", [])):
        p = dict(p)
        p.setdefault("label", chr(ord("A") + i) if i < 26 else str(i + 1))
        if "step" in p:
            p["models"] = [{"step": p.pop("step"), **{k: p.pop(k) for k in ("only", "highlight", "ghost", "color") if k in p}}]
        for m in p.get("models", []):
            m["step"] = resolve(m["step"])
        for k in ("image", "html"):
            if k in p:
                p[k] = resolve(p[k])
        panels.append(p)
    spec = dict(spec)
    spec["panels"] = panels
    if "fragment" in spec:
        spec["fragment"] = resolve(spec["fragment"])
    if spec.get("view", "iso") not in VIEWS and not isinstance(spec.get("view"), dict):
        raise VizError(f"view {spec['view']!r} is not one of {', '.join(VIEWS)}")
    if not spec.get("title"):
        raise VizError("the page needs a title (two to four words that name it)")
    return spec


def commit_line() -> str:
    try:
        sha = subprocess.run(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        sha = "no commit"
    return f"Built {datetime.date.today().isoformat()} from {sha}"


ROUTES = {
    "payload": ", from the payload the export wrote beside the STEP",
    "payload (unstated)": ", from a payload beside the STEP that names no source",
    "occt": ", read from the STEP itself because the payload beside it is stale or absent",
}
AXES = "xyz"
# Grid columns by panel count, so a row never ends on one panel standing alone.
COLUMNS = {1: 1, 2: 2, 3: 3, 4: 2, 5: 3, 6: 3, 7: 4, 8: 4}


def union(boxes):
    boxes = [b for b in boxes if b]
    if not boxes:
        return None
    return [[min(b[0][a] for b in boxes) for a in range(3)], [max(b[1][a] for b in boxes) for a in range(3)]]


def measured(box, names, ref, ref_label) -> str:
    """Where the amber solids stand, read off their triangles, and how far they moved from the
    first panel that has any — so a caption states what the geometry says, not what was meant."""
    shown_names = ", ".join(names[:3]) + (f" +{len(names) - 3}" if len(names) > 3 else "")
    span = " · ".join(f'<span class="viz-nowrap">{AXES[a]} {box[0][a]:.2f} to {box[1][a]:.2f}'
                      f'{" mm" if a == 2 else ""}</span>' for a in range(3))
    line = f"Amber ({esc(shown_names)}): {span}"
    if ref is None:
        return line
    moved = [(AXES[a], (box[0][a] + box[1][a] - ref[0][a] - ref[1][a]) / 2) for a in range(3)]
    grown = [(AXES[a], (box[1][a] - box[0][a]) - (ref[1][a] - ref[0][a])) for a in range(3)]
    parts = [f"{ax} {d:+.2f}" for ax, d in moved if abs(d) >= 0.005]
    sizes = [f"{ax} {d:+.2f}" for ax, d in grown if abs(d) >= 0.005]
    if not parts and not sizes:
        return line + f"<br>Same place and size as {esc(ref_label)}"
    said = []
    if parts:
        said.append("centre moved " + ", ".join(parts) + " mm")
    if sizes:
        said.append("extent changed " + ", ".join(sizes) + " mm")
    return line + f"<br>From {esc(ref_label)}: " + "; ".join(said)


def render(spec: dict) -> tuple[str, Models]:
    models = Models()
    panel_specs, panel_html, sources = [], [], []
    ref_box, ref_label = None, None
    for i, p in enumerate(spec["panels"]):
        entry = {"label": p["label"], "name": p.get("name", "")}
        tag = esc(p["label"])
        name = esc(p.get("name", ""))
        pick = bool(p.get("pick"))
        head = (f'<div class="viz-panel-head"><span class="viz-tag">{tag}</span>'
                f'<span class="viz-name" id="viz-p{i}">{name}</span>'
                + ('<span class="viz-pick">Pick</span>' if pick else "")
                + '<button type="button" data-wide aria-pressed="false">Enlarge</button></div>')
        measure = ""
        if p.get("models"):
            uses, lit, lit_names = [], [], []
            for m in p["models"]:
                mid = models.add(m["step"], m.get("only"))
                meta = models.meta[mid]
                roles = {}
                for k, mesh in enumerate(meta["meshes"]):
                    if matches(mesh["name"], m.get("highlight")):
                        roles[k] = "hi"
                        lit.append(mesh["box"])
                        if mesh["name"] not in lit_names:
                            lit_names.append(mesh["name"] or "(unnamed)")
                    elif matches(mesh["name"], m.get("ghost")):
                        roles[k] = "ghost"
                if m.get("highlight") and "hi" not in roles.values():
                    raise VizError(f"`highlight` {m['highlight']} matches no solid in {meta['step']}")
                uses.append({"model": mid, "roles": roles, "color": m.get("color")})
                sources.append(f"{tag} · {esc(meta['step'])}: {meta['tris']:,} triangles in "
                               f"{meta['solids']} solid{'s' if meta['solids'] != 1 else ''}"
                               f"{ROUTES[meta['route']]}")
            entry["models"] = uses
            box = union(lit)
            if box:
                measure = f'<p class="viz-caption">{measured(box, lit_names, ref_box, ref_label)}</p>'
                if ref_box is None:
                    ref_box, ref_label = box, p["label"]
            stage = (f'<div class="viz-stage" data-3d tabindex="0" role="group" '
                     f'aria-label="{tag} · {name}: 3D view. Drag or use the arrow keys to turn it.">'
                     f'<p class="viz-note">Loading geometry…</p></div>')
        elif p.get("image"):
            alt = esc(p.get("alt") or p.get("caption") or p.get("name") or "render")
            stage = (f'<div class="viz-stage is-image"><img src="{data_uri(p["image"])}" alt="{alt}"></div>')
            sources.append(f"{tag} · {esc(shown(p['image']))}")
        elif p.get("html"):
            stage = f'<div class="viz-stage is-html">{p["html"].read_text()}</div>'
            sources.append(f"{tag} · drawn by hand ({esc(shown(p['html']))}), not read from a model")
        else:
            raise VizError(f"panel {p['label']} has no step, models, image or html")
        caption = f'<p class="viz-caption">{esc(p["caption"])}</p>' if p.get("caption") else ""
        # A lone panel, and a hand-drawn one (authored at the inline widget's 680 px), take the row.
        wide = " is-wide" if p.get("wide", len(spec["panels"]) == 1 or bool(p.get("html"))) else ""
        panel_html.append(f'<section class="viz-panel{" is-pick" if pick else ""}{wide}" data-panel="{i}" '
                          f'aria-labelledby="viz-p{i}">{head}{stage}{caption}{measure}</section>')
        panel_specs.append(entry)

    three_d = sum(1 for p in panel_specs if p.get("models"))
    view = spec.get("view", "iso")
    # Feature edges open on unless the page carries more triangles than they read well over.
    edges = spec.get("edges", sum(m["tris"] for m in models.meta) <= 400_000)
    bar = ""
    if three_d:
        buttons = "".join(
            f'<button type="button" data-view="{v}" aria-pressed="{str(v == view).lower()}">{label}</button>'
            for v, label in (("iso", "Iso"), ("front", "Front"), ("right", "Side"), ("top", "Top")))
        toggles = f'<button type="button" data-edges aria-pressed="{str(bool(edges)).lower()}">Edges</button>'
        if three_d > 1:
            toggles = (f'<button type="button" data-sync aria-pressed="{str(spec.get("sync", True) is not False).lower()}">'
                       f'Turn together</button>') + toggles
        bar = (f'<div class="viz-bar" role="toolbar" aria-label="View">'
               f'<div class="viz-group"><span>View</span>{buttons}</div>'
               f'<div class="viz-group">{toggles}</div></div>')

    lede = f'<p class="viz-lede">{esc(spec["lede"])}</p>' if spec.get("lede") else ""
    body = [f'<header class="viz-head"><h1>{esc(spec["title"])}</h1>{lede}</header>']
    if spec.get("fragment"):
        body.append(f'<div class="viz-body">{spec["fragment"].read_text()}</div>')
        sources.append(f"Drawn by hand ({esc(shown(spec['fragment']))}), not read from a model")
    if bar:
        body.append(bar)
    if panel_html:
        cols = COLUMNS.get(len(panel_html), 4)
        body.append(f'<div class="viz-grid" style="--cols: {cols}">' + "".join(panel_html) + "</div>")
    foot = "".join(f"<li>{s}</li>" for s in sources)
    tail = (" · 3D drawn with three.js 0.170.0 in the /3d viewer's colours, finishes and light"
            if three_d else "")
    body.append(f'<footer class="viz-foot">{commit_line()}{tail}<ul>{foot}</ul></footer>')

    page_spec = {"view": view, "frame": spec.get("frame", "shared"), "sync": spec.get("sync", True),
                 "edges": bool(edges), "panels": panel_specs,
                 "models": [{k: v for k, v in m.items() if k != "step"} for m in models.meta]}
    blobs = "\n".join(
        f'<script type="text/plain" id="viz-mesh-{i}">{base64.b64encode(b).decode()}</script>'
        for i, b in enumerate(models.blobs))
    text = TEMPLATE.read_text()
    needs_shim = bool(spec.get("fragment")) or any(p.get("html") for p in spec["panels"])
    for marker, value in (("TITLE", esc(spec["title"])), ("SHIM", shim_css() if needs_shim else ""),
                          ("BODY", "\n".join(body)),
                          ("SPEC", json.dumps(page_spec, separators=(",", ":")).replace("</", "<\\/")),
                          ("BLOBS", blobs)):
        text = text.replace(f"<!--VIZ:{marker}-->", value, 1)
    return text, models


def build(spec: dict, out: Path, base: Path) -> Path:
    spec = normalise(spec, base)
    text, models = render(spec)
    size = len(text.encode())
    if size > PAGE_LIMIT:
        raise VizError(f"the page is {size / 1e6:.1f} MB, past the {PAGE_LIMIT / 1e6:.0f} MB an Artifact carries; "
                       "narrow the models with `only`")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    print(out)
    for m in models.meta:
        print(f"  {m['step']}: {m['solids']} solid{'s' if m['solids'] != 1 else ''}, {m['tris']:,} triangles ({m['route']})")
    note = "  heavy for a phone — narrow with `only`" if size > PAGE_HEAVY else ""
    print(f"  {size / 1e6:.2f} MB{note}")
    return out


# ── selftest ────────────────────────────────────────────────────────────────


def selftest() -> int:
    """The payload reader against the layout `_mesh_payload.write` states, the `only`/role globs,
    and a whole page built from a synthetic model — no STEP, no node, no network."""
    tmp = Path(tempfile.mkdtemp())
    pos = array.array("f", [0, 0, 0, 10, 0, 0, 0, 10, 0, 0, 0, 10])
    idx = array.array("I", [0, 1, 2, 0, 1, 3, 0, 2, 3, 1, 2, 3])
    blob, entries = bytearray(), []
    for name, color in (("tee-y-a", [0.8, 0.1, 0.1]), ("valve-v-a", None)):
        e = {"name": name, "color": color}
        for key, arr in (("pos", pos), ("nrm", array.array("f")), ("idx", idx), ("fac", array.array("I"))):
            e[key] = [len(blob), len(arr)]
            blob += arr.tobytes()
        entries.append(e)
    step = tmp / "t.step"
    step.write_text("ISO-10303-21; synthetic\n")
    head = json.dumps({"v": 3, "meshes": entries, "src": sha256(step)}).encode()
    head += b" " * (-(len(head) + 4) % 4)
    (tmp / "t.step.mesh").write_bytes(struct.pack("<I", len(head)) + head + bytes(blob))

    got, _, route = step_payload(step)
    assert route == "payload", route
    assert [m["name"] for m in got["meshes"]] == ["tee-y-a", "valve-v-a"]
    assert matches("coil-v-a/2", ["coil-v-a/*"]) and not matches("coil-v-c/2", ["coil-v-a/*"])

    spec = {"title": "Self test", "panels": [
        {"name": "Both", "step": str(step), "highlight": ["tee-*"]},
        {"name": "Tee", "step": str(step), "only": ["tee-*"], "pick": True}]}
    out = build(spec, tmp / "page.html", tmp)
    text = out.read_text()
    assert text.startswith("<title>Self test</title>"), "the title must lead the file"
    assert "<!doctype" not in text.lower() and "<body" not in text.lower(), "an Artifact supplies its own skeleton"
    assert "<!--VIZ:" not in text, "a marker was left unfilled"
    page = json.loads(re.search(r'id="viz-spec">(.*?)</script>', text, re.S).group(1))
    assert len(page["models"]) == 2, "two `only` filters are two embedded models"
    assert page["panels"][0]["models"][0]["roles"] == {"0": "hi"}, page["panels"][0]
    assert "Amber (tee-y-a)" in text and "x 0.00 to 10.00" in text, "the amber solids are measured"
    raw = gzip.decompress(base64.b64decode(re.search(r'id="viz-mesh-1">([^<]*)<', text).group(1)))
    mesh = page["models"][1]["meshes"][0]
    assert mesh["pos"][0] % 4 == 0 and mesh["idx"][0] % 4 == 0, "typed-array views need 4-byte offsets"
    assert array.array("I", raw[mesh["idx"][0]: mesh["idx"][0] + 4 * mesh["idx"][1]]).tolist() == idx.tolist()

    step.write_text("ISO-10303-21; edited since the payload was cut\n")
    try:
        _, _, route = step_payload(step)
        assert route == "occt", route
    except VizError as err:
        assert "occt-import-js" in str(err), err
    print("selftest ok")
    return 0


# ── cli ─────────────────────────────────────────────────────────────────────


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("spec", nargs="?", help="SPEC.json, or `selftest`")
    ap.add_argument("--out", help="the page to write (.html)")
    ap.add_argument("--title")
    ap.add_argument("--lede")
    ap.add_argument("--step", action="append", default=[], help="one 3D panel per STEP")
    ap.add_argument("--image", action="append", default=[], help="one panel per render")
    ap.add_argument("--fragment", help="a hand-authored HTML/SVG fragment for the page body")
    ap.add_argument("--only", action="append", help="keep matching solids (every --step)")
    ap.add_argument("--highlight", action="append", help="draw matching solids in amber")
    ap.add_argument("--ghost", action="append", help="draw matching solids translucent")
    ap.add_argument("--view", default=None, choices=VIEWS)
    ap.add_argument("--list-solids", metavar="STEP", help="print the solid names a STEP carries")
    args = ap.parse_args(argv)

    try:
        if args.spec == "selftest":
            return selftest()
        if args.list_solids:
            for name in list_solids(repo_path(args.list_solids)):
                print(name or "(unnamed)")
            return 0
        if args.spec:
            spec_path = Path(args.spec).resolve()
            spec = json.loads(spec_path.read_text())
            base = spec_path.parent
        else:
            spec, base = {"panels": []}, Path.cwd()
            for s in args.step:
                panel = {"name": Path(s).stem, "step": s}
                for k in ("only", "highlight", "ghost"):
                    if getattr(args, k):
                        panel[k] = getattr(args, k)
                spec["panels"].append(panel)
            spec["panels"] += [{"name": Path(i).stem, "image": i} for i in args.image]
            if args.fragment:
                spec["fragment"] = args.fragment
        for k in ("title", "lede", "view"):
            if getattr(args, k):
                spec[k] = getattr(args, k)
        if not args.out:
            raise VizError("--out names the page to write")
        if not spec.get("panels") and not spec.get("fragment"):
            raise VizError("nothing to draw: give a spec, --step, --image or --fragment")
        build(spec, Path(args.out).resolve(), base)
        return 0
    except VizError as err:
        print(f"viz: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
