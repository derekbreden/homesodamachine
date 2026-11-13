"""Projects model points into a render's pixels, for callouts drawn over hsm-render pictures."""
import math


def _norm(v):
    n = math.sqrt(sum(x * x for x in v))
    return [x / n for x in v]


def _cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def projector(cam, target, span, size, up=(0, 0, 1)):
    w, h = size
    f = _norm([-c for c in cam])
    r = _norm(_cross(f, list(up)))
    u = _cross(r, f)
    s = (h / 2) / span

    def proj(p):
        d = [p[i] - target[i] for i in range(3)]
        return (w / 2 + sum(a * b for a, b in zip(d, r)) * s, h / 2 - sum(a * b for a, b in zip(d, u)) * s)

    return proj
