"""Draws the book's diagrams: plastic as courses of beads on a bed, seen in section or from above.

Every drawing uses the same four colours so a reader learns them once:
slate = plastic already printed, orange = the course being laid (still soft),
blue hatch = printed to be thrown away (fin or support), dashed red = cut away or missing.
"""
import math

COLD = "#5f7180"
HOT = "#f26a21"
SCAFFOLD = "#4a90d9"
INK = "#111a22"
MUTED = "#5b6873"
FAINT = "#a9b3bb"
BAD = "#c2392b"
GOOD = "#1d7d55"
BRASS = "#b8862b"
WASH = "#e9edf0"

BEAD_W = 42.0
ROW_H = 24.0


def n(v):
    """A number as short text."""
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def defs(grid_x=0.0, grid_y=0.0):
    """Kept so older drawings still work. block(), course(), bed() and scaffold() no longer need it;
    they draw plain strokes, which stay small and sharp in the PDF. Prefer those over pattern fills."""
    gx, gy = grid_x % BEAD_W, grid_y % ROW_H
    bead = f'<rect x="1.5" y="1.5" width="{BEAD_W - 3}" height="{ROW_H - 3}" rx="{(ROW_H - 3) / 2}"'
    return (
        "<defs>"
        f'<pattern id="cold" x="{n(gx)}" y="{n(gy)}" width="{n(BEAD_W)}" height="{n(ROW_H)}" patternUnits="userSpaceOnUse">{bead} fill="{COLD}"/></pattern>'
        f'<pattern id="hot" x="{n(gx)}" y="{n(gy)}" width="{n(BEAD_W)}" height="{n(ROW_H)}" patternUnits="userSpaceOnUse">{bead} fill="{HOT}"/></pattern>'
        f'<pattern id="blue" x="{n(gx)}" y="{n(gy)}" width="{n(BEAD_W)}" height="{n(ROW_H)}" patternUnits="userSpaceOnUse">{bead} fill="{SCAFFOLD}"/></pattern>'
        '<pattern id="hatch" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
        f'<rect width="14" height="14" fill="#e6f0fa"/><rect width="5" height="14" fill="{SCAFFOLD}"/></pattern>'
        '<pattern id="bedhatch" width="18" height="18" patternUnits="userSpaceOnUse" patternTransform="rotate(-45)">'
        f'<rect width="18" height="18" fill="white"/><rect width="3" height="18" fill="{INK}"/></pattern>'
        "</defs>"
    )


def svg(w, h, body, title, desc="", style=""):
    """Wraps a drawing. title and desc are read by screen readers and by agents; write them as
    plain sentences that say what the drawing shows."""
    d = f"<desc>{desc}</desc>" if desc else ""
    st = f' style="{style}"' if style else ""
    return f'<svg viewBox="0 0 {n(w)} {n(h)}" role="img"{st}><title>{title}</title>{d}{body}</svg>'


def row_y(row, bed_y):
    """Top of a course; row 0 sits on the bed."""
    return bed_y - (row + 1) * ROW_H


def _colour(kind):
    return {"cold": COLD, "hot": HOT, "blue": SCAFFOLD}.get(kind, kind)


_BEAD = ROW_H - 3  # a bead's height; its stroke is this wide with round ends


def block(x0, x1, row0, row1, bed_y, kind="cold"):
    """Courses row0..row1 inclusive between x0 and x1 (row 0 sits on the bed). x1 - x0 should be a
    whole number of beads (multiples of BEAD_W); kind is "cold", "hot" or "blue"."""
    count = max(1, round((x1 - x0) / BEAD_W))
    w = (x1 - x0) / count
    d = "".join(f"M{n(x0 + 1.5 + _BEAD / 2)} {n(row_y(r, bed_y) + ROW_H / 2)}H{n(x1 - 1.5 - _BEAD / 2)}" for r in range(row0, row1 + 1))
    return (f'<path d="{d}" fill="none" stroke="{_colour(kind)}" stroke-width="{n(_BEAD)}" stroke-linecap="round" '
            f'stroke-dasharray="{n(w - 3 - _BEAD)} {n(3 + _BEAD)}"/>')


def course(x0, x1, y, fill=COLD, h=ROW_H):
    """One course anywhere (a lean, a corbel), its top at y, as beads side by side between x0 and x1."""
    count = max(1, round((x1 - x0) / BEAD_W))
    w = (x1 - x0) / count
    bh = h - 3
    return (f'<path d="M{n(x0 + 1.5 + bh / 2)} {n(y + h / 2)}H{n(x1 - 1.5 - bh / 2)}" fill="none" stroke="{fill}" stroke-width="{n(bh)}" '
            f'stroke-linecap="round" stroke-dasharray="{n(w - 3 - bh)} {n(3 + bh)}"/>')


def strand(x0, x1, y, fill=HOT, h=ROW_H):
    """One unbroken road seen from the side, such as a bridge strand."""
    return f'<rect x="{n(x0 + 1.5)}" y="{n(y + 1.5)}" width="{n(x1 - x0 - 3)}" height="{n(h - 3)}" rx="{n((h - 3) / 2)}" fill="{fill}"/>'


def bed(x0, x1, bed_y):
    """The print bed: a heavy line with hatching under it."""
    ticks = "".join(f"M{n(x)} {n(bed_y + 6)}l-16 20" for x in _frange(x0 + 18, x1, 18))
    return (f'<path d="{ticks}" stroke="{INK}" stroke-width="3" fill="none"/>'
            f'<rect x="{n(x0)}" y="{n(bed_y)}" width="{n(x1 - x0)}" height="7" fill="{INK}"/>')


def _frange(a, b, step):
    out = []
    while a <= b:
        out.append(a)
        a += step
    return out


def scaffold(x0, x1, y0, y1):
    """Support body between y0 (top) and y1 (bottom): pale blue with blue hatching."""
    lines = []
    span = (y1 - y0)
    for t in _frange(x0 - span, x1, 20):
        ax, ay, bx, by = t, y1, t + span, y0
        if ax < x0:
            ay -= (x0 - ax)
            ax = x0
        if bx > x1:
            by += (bx - x1)
            bx = x1
        if ay > by:
            lines.append(f"M{n(ax)} {n(ay)}L{n(bx)} {n(by)}")
    return (f'<rect x="{n(x0)}" y="{n(y0)}" width="{n(x1 - x0)}" height="{n(y1 - y0)}" fill="#e6f0fa"/>'
            f'<path d="{"".join(lines)}" stroke="{SCAFFOLD}" stroke-width="6" fill="none"/>')


def missing(x0, y0, x1, y1):
    """Dashed outline of something that was cut away."""
    return f'<rect x="{n(x0)}" y="{n(y0)}" width="{n(x1 - x0)}" height="{n(y1 - y0)}" fill="none" stroke="{BAD}" stroke-width="3" stroke-dasharray="9 8"/>'


def nozzle(x, y, s=1.0):
    """A nozzle in section whose tip touches (x, y)."""
    w, h = 74 * s, 96 * s
    return (
        f'<path d="M{n(x - 9 * s)} {n(y)} L{n(x + 9 * s)} {n(y)} L{n(x + w / 2)} {n(y - 44 * s)} '
        f'L{n(x + w / 2)} {n(y - h)} L{n(x - w / 2)} {n(y - h)} L{n(x - w / 2)} {n(y - 44 * s)} Z" fill="{BRASS}"/>'
        f'<rect x="{n(x - w / 2 - 10 * s)}" y="{n(y - h - 34 * s)}" width="{n(w + 20 * s)}" height="{n(34 * s)}" fill="{INK}"/>'
    )


def nozzle_top(x, y, r=40):
    """A nozzle seen from above."""
    return (
        f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="{BRASS}"/><circle cx="{n(x)}" cy="{n(y)}" r="{n(r * 0.58)}" fill="{INK}"/>'
        f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r * 0.18)}" fill="{HOT}"/>'
    )


def road(d, color=HOT, width=21):
    """A free road drawn along an SVG path: a sag, a curl, a thread."""
    return f'<path d="{d}" stroke="{color}" stroke-width="{n(width)}" stroke-linecap="round" stroke-linejoin="round" fill="none"/>'


def callout(num, x, y, tx=None, ty=None, kind=""):
    """A numbered disc at (tx, ty) with a leader to (x, y)."""
    tx = x if tx is None else tx
    ty = y if ty is None else ty
    fill = {"hot": HOT, "scaffold": SCAFFOLD, "bad": BAD}.get(kind, INK)
    line = ""
    if (tx, ty) != (x, y):
        line = f'<path d="M{n(tx)} {n(ty)} L{n(x)} {n(y)}" stroke="{INK}" stroke-width="3" fill="none"/><circle cx="{n(x)}" cy="{n(y)}" r="7" fill="{INK}"/>'
    return (
        line
        + f'<circle cx="{n(tx)}" cy="{n(ty)}" r="31" fill="{fill}"/>'
        + f'<text x="{n(tx)}" y="{n(ty + 11)}" text-anchor="middle" class="d-num">{num}</text>'
    )


def label(x, y, text, size=27, anchor="start", fill=MUTED, weight=400, mono=True):
    """Text inside a drawing. Mono capitals for labels, sans for a short note."""
    fam = "IBM Plex Mono, monospace" if mono else "IBM Plex Sans, sans-serif"
    sp = f' letter-spacing="{n(0.06 * size)}"' if mono else ""
    return (
        f'<text x="{n(x)}" y="{n(y)}" text-anchor="{anchor}" font-family="{fam}" font-size="{n(size)}" '
        f'font-weight="{weight}" fill="{fill}"{sp}>{text}</text>'
    )


def line(x0, y0, x1, y1, color=INK, width=3, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="M{n(x0)} {n(y0)} L{n(x1)} {n(y1)}" stroke="{color}" stroke-width="{n(width)}" fill="none"{d}/>'


def arrow(x0, y0, x1, y1, color=INK, width=4):
    ang = math.atan2(y1 - y0, x1 - x0)
    a = 16
    p1 = (x1 - a * math.cos(ang - 0.45), y1 - a * math.sin(ang - 0.45))
    p2 = (x1 - a * math.cos(ang + 0.45), y1 - a * math.sin(ang + 0.45))
    return (
        f'<path d="M{n(x0)} {n(y0)} L{n(x1)} {n(y1)}" stroke="{color}" stroke-width="{n(width)}" fill="none"/>'
        f'<path d="M{n(x1)} {n(y1)} L{n(p1[0])} {n(p1[1])} L{n(p2[0])} {n(p2[1])} Z" fill="{color}"/>'
    )


def dim(x0, y0, x1, y1, text, off=34, color=INK):
    """A dimension line with ticks and a label beside its middle."""
    ang = math.atan2(y1 - y0, x1 - x0)
    nx, ny = -math.sin(ang), math.cos(ang)
    t = 12
    mx, my = (x0 + x1) / 2 + nx * off, (y0 + y1) / 2 + ny * off
    return (
        line(x0, y0, x1, y1, color, 3)
        + line(x0 - nx * t, y0 - ny * t, x0 + nx * t, y0 + ny * t, color, 3)
        + line(x1 - nx * t, y1 - ny * t, x1 + nx * t, y1 + ny * t, color, 3)
        + label(mx, my + 9, text, 27, anchor="middle", fill=color, weight=600)
    )
