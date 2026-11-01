"""Tuple arithmetic for source-frame numbers; native builders retain their vectors."""

import math


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def scale(a, factor):
    return tuple(x * factor for x in a)


def unit(a):
    return scale(a, 1.0 / math.sqrt(sum(x * x for x in a)))


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def turned(vector, axis, radians):
    c, s = math.cos(radians), math.sin(radians)
    return add(add(scale(vector, c), scale(cross(axis, vector), s)),
               scale(axis, dot(axis, vector) * (1.0 - c)))
