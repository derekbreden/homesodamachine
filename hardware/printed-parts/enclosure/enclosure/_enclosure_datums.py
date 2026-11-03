"""Enclosure numbers and frames for the Rust producers.

The enclosure's scalar source uses vectors, planes and placements. These are numeric
values here; every solid operation is an explicit Rust construction recipe. The normal
driver loads this namespace before the source, without loading a Python CAD kernel.
"""
from __future__ import annotations

import importlib
import math
from pathlib import Path
import sys


class Vector:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        if isinstance(x, Vector):
            x, y, z = x.toTuple()
        elif not isinstance(x, (int, float)):
            x, y, z = x
        self.x, self.y, self.z = map(float, (x, y, z))

    def toTuple(self):
        return self.x, self.y, self.z

    def __iter__(self):
        return iter(self.toTuple())

    def __getitem__(self, key):
        return self.toTuple()[key]

    def __add__(self, other):
        return Vector(*(a+b for a, b in zip(self, Vector(other))))

    def __sub__(self, other):
        return Vector(*(a-b for a, b in zip(self, Vector(other))))

    def __mul__(self, scale):
        return Vector(*(a*scale for a in self))

    __rmul__ = __mul__

    def __truediv__(self, scale):
        return self*(1.0/scale)

    def __neg__(self):
        return self*-1.0

    add, sub, multiply = __add__, __sub__, __mul__

    @property
    def Length(self):
        return math.sqrt(self.dot(self))

    def normalized(self):
        return self/self.Length

    def dot(self, other):
        return sum(a*b for a, b in zip(self, Vector(other)))

    def cross(self, other):
        a, b, c = self
        d, e, f = Vector(other)
        return Vector(b*f-c*e, c*d-a*f, a*e-b*d)

    def getAngle(self, other):
        other = Vector(other)
        return math.acos(max(-1.0, min(1.0, self.dot(other)/(self.Length*other.Length))))

    def __repr__(self):
        return f'Vector{self.toTuple()!r}'


class Plane:
    def __init__(self, origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0, 0, 1)):
        self.origin = Vector(origin)
        self.zDir = Vector(normal).normalized()
        self.xDir = (Vector(xDir)-self.zDir*self.zDir.dot(xDir)).normalized()
        self.yDir = self.zDir.cross(self.xDir)

    @classmethod
    def named(cls, name, origin=(0, 0, 0)):
        axes = {'XY': ((1,0,0),(0,0,1)), 'YZ': ((0,1,0),(1,0,0)),
                'XZ': ((1,0,0),(0,-1,0)), 'YX': ((0,1,0),(0,0,-1)),
                'ZY': ((0,0,1),(-1,0,0)), 'ZX': ((0,0,1),(0,1,0))}
        x, z = axes[name]
        return cls(origin, x, z)

    def toWorldCoords(self, point):
        point = tuple(point)
        if len(point) == 2:
            point = (*point, 0.0)
        return self.origin+self.xDir*point[0]+self.yDir*point[1]+self.zDir*point[2]

    def toLocalCoords(self, point):
        point = Vector(point)-self.origin
        return Vector(*(point.dot(axis) for axis in (self.xDir, self.yDir, self.zDir)))

    @property
    def location(self):
        return Location(self)


class _Matrix:
    def __init__(self, rows):
        self.rows = rows

    def Transformation(self):
        return self

    def Value(self, row, column):
        return self.rows[row-1][column-1]


class Location:
    def __init__(self, point=(0,0,0), axis=None, angle=0.0):
        if isinstance(point, Location):
            self.rows = point.rows
        elif isinstance(point, Plane):
            self.rows = tuple(tuple(axis[k] for axis in
                              (point.xDir, point.yDir, point.zDir))+ (point.origin[k],)
                              for k in range(3))
        else:
            point = Vector(point)
            if axis is None:
                rotation = ((1.,0.,0.),(0.,1.,0.),(0.,0.,1.))
            else:
                x, y, z = Vector(axis).normalized()
                c, s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
                d = 1.0-c
                rotation = ((c+x*x*d,x*y*d-z*s,x*z*d+y*s),
                            (y*x*d+z*s,c+y*y*d,y*z*d-x*s),
                            (z*x*d-y*s,z*y*d+x*s,c+z*z*d))
            self.rows = tuple(tuple(row)+(point[k],) for k, row in enumerate(rotation))
        self.wrapped = _Matrix(self.rows)

    def __mul__(self, other):
        other = Location(other)
        rows = tuple(tuple(sum(self.rows[i][k]*other.rows[k][j] for k in range(3))
                           for j in range(3))+
                     (self.rows[i][3]+sum(self.rows[i][k]*other.rows[k][3]
                                          for k in range(3)),) for i in range(3))
        result = Location()
        result.rows, result.wrapped = rows, _Matrix(rows)
        return result

    @property
    def inverse(self):
        rows = tuple(tuple(self.rows[j][i] for j in range(3))+
                     (-sum(self.rows[j][i]*self.rows[j][3] for j in range(3)),)
                     for i in range(3))
        result = Location()
        result.rows, result.wrapped = rows, _Matrix(rows)
        return result


class Workplane:
    """A numeric graph result and its frame; it constructs no geometry."""
    def __init__(self, plane='XY', origin=(0,0,0), obj=None):
        self.plane = plane if isinstance(plane, Plane) else Plane.named(plane, origin)
        self.objects = [] if obj is None else [obj]

    def val(self):
        if not self.objects:
            raise TypeError('normal enclosure geometry must be a Rust recipe')
        return self.objects[0]

    def vals(self):
        return self.objects

    def __getattr__(self, name):
        if name in ('fuse', 'cut', 'intersect', 'clean', 'translate', 'rotate', 'mirror', 'moved'):
            def operation(*args, **kwargs):
                args = tuple(a.val() if isinstance(a, Workplane) else a for a in args)
                return Workplane(self.plane, obj=getattr(self.val(), name)(*args, **kwargs))
            return operation
        raise AttributeError(f'{name}: normal enclosure geometry must be a Rust recipe')


class Shape:
    """An annotation marker; numeric construction recipes own geometry."""


def install():
    """Make the source's datum names numeric before its first import."""
    scripts = Path(__file__).resolve().parents[3]/'scripts'
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    import _rust_part
    _rust_part.start()
    _rust_part._STANDINS.update(Vector=Vector, Plane=Plane, Location=Location,
                               Workplane=Workplane, Shape=Shape, Solid=Shape,
                               Compound=Shape, Face=Shape, Wire=Shape, Edge=Shape,
                               MESH=False, __path__=[])


def load():
    """The current scalar enclosure source, with Rust construction recipes."""
    install()
    return importlib.import_module('enclosure')
