//! Enclosure numbers and frames for the Rust producers.
//!
//! The enclosure's scalar source uses vectors, planes and placements. These are numeric
//! values here; every solid operation is an explicit Rust construction recipe. The normal
//! driver loads this namespace before the source, without loading a Python CAD kernel.
//!
//! # Typed API
//!
//! The stub classes `Vector`, `Plane`, `_Matrix`, `Location`, `Workplane` and `Shape` stay Python
//! classes: Python code makes their instances (every enclosure module's `cq.Vector(..)`,
//! `cq.Plane(..)` reaches them through `_rust_part._STANDINS`, which [`install_standins`] fills),
//! and their methods forward here as the `"Class.method"` entries. A converted module computes
//! with the native values instead and makes Python instances only where a value leaves for Python:
//!
//! - [`Vector`], [`Plane`] and [`Location`] hold the numbers. Their methods compute what the Python
//!   methods return, bit for bit: [`Vector::add`], [`Vector::sub`], [`Vector::mul`] (`v * s`),
//!   [`Vector::div`] (`v / s`, which is `v * (1.0 / s)`), [`Vector::neg`], [`Vector::dot`],
//!   [`Vector::length`] (`.Length`), [`Vector::normalized`], [`Vector::cross`],
//!   [`Vector::get_angle`], [`Vector::repr`]; [`Plane::new`] (`Plane(origin, xDir, normal)`),
//!   [`Plane::named`], [`Plane::to_world`] (`toWorldCoords`), [`Plane::to_local`]
//!   (`toLocalCoords`), [`Plane::location`]; [`Location::identity`] (`Location()`),
//!   [`Location::at`] (`Location(point, axis, angle)`), [`Location::from_plane`]
//!   (`Location(plane)`), [`Location::mul`], [`Location::inverse`], [`Location::value`]
//!   (`wrapped.Value(row, column)`).
//! - From Python values: [`Vector::of`] is `Vector(value)` with one argument (a `Vector` instance,
//!   a sequence of three, or a number for `x`); [`Vector::args`] is `Vector(x, y, z)`;
//!   [`Location::of`] is `Location(value)`; [`Vector::read`], [`Plane::read`] and
//!   [`Location::read`] read an instance's fields.
//! - To Python values: [`Vector::to_val`], [`Plane::to_val`] and [`Location::to_val`] make stub
//!   instances holding the same numbers, with the fields their classes' own methods set, in the
//!   same order; [`Vector::tuple_val`] is `toTuple()`; [`Location::rows_val`] is `.rows`.
//! - At the namespace boundary all three are [`py::Py`]: `to_py` is `to_val` and `from_py` is
//!   `read`, with the registry serving the request ([`rt::current`]). `from_py` takes only a Python
//!   instance: a tuple that should become a vector is `[f64; 3]` or [`Vector::of`].
//! - [`install_standins`] and [`load`] are the module's `install()` and `load()`.
//!
//! Failures carry the runtime's texts: `division by zero` (normalizing a zero vector), `math
//! domain error` (the length of a vector holding a NaN), `unordered numeric comparison` (an angle
//! with a NaN), `missing key 'XQ'` (an unknown plane name), `index out of range`.
#![allow(non_snake_case)]
use super::num::{self, Num};
use super::py::{self, Val};
use super::rt::{self, Ns, Rt};
use anyhow::{Context, Result, bail, ensure};
use hsm_documents::interop;
use std::cell::RefCell;
use std::rc::Rc;

pub const TYPED: bool = true;
const MODULE: &str = "_enclosure_datums";

/// The module's typed state: its namespace (the classes are read from it where the generated
/// code reads them) and Python helpers made on first use.
struct State {
    ns: Ns,
    /// `builtins.isinstance`.
    isinstance: RefCell<Option<Val>>,
    /// `operator.attrgetter('x', 'y', 'z')`: a vector's fields in one callback.
    xyz: RefCell<Option<Val>>,
    /// `operator.attrgetter('origin.x', ..., 'zDir.z')`: a plane's fields in one callback.
    frame: RefCell<Option<Val>>,
    /// `object.__new__`.
    new: RefCell<Option<Val>>,
}

fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

/// A Python value made once and kept.
fn cached(cell: &RefCell<Option<Val>>, make: impl FnOnce() -> Result<Val>) -> Result<Val> {
    if let Some(value) = cell.borrow().clone() {
        return Ok(value);
    }
    let value = make()?;
    *cell.borrow_mut() = Some(value.clone());
    Ok(value)
}

const PLANE_FIELDS: [&str; 12] = [
    "origin.x", "origin.y", "origin.z", "xDir.x", "xDir.y", "xDir.z", "yDir.x", "yDir.y", "yDir.z",
    "zDir.x", "zDir.y", "zDir.z",
];

impl State {
    fn class(&self, name: &str) -> Result<Val> {
        self.ns.get(name)
    }
    /// `isinstance(value, <class>)` for one of this module's classes. Only a Python object can be
    /// an instance of a Python class, so other values answer without a callback.
    fn is(&self, rt: &Rt, value: &Val, class: &str) -> Result<bool> {
        if !matches!(value, Val::Ref(_)) {
            return Ok(false);
        }
        let isinstance = cached(&self.isinstance, || rt.provider("builtins")?.attr("isinstance"))?;
        py::call(&isinstance, vec![value.clone(), self.class(class)?])?.truthy()
    }
    fn getter(&self, rt: &Rt, cell: &RefCell<Option<Val>>, fields: &[&str]) -> Result<Val> {
        cached(cell, || {
            let attrgetter = rt.provider("operator")?.attr("attrgetter")?;
            py::call(&attrgetter, fields.iter().map(|f| py::s(*f)).collect())
        })
    }
    /// `(v.x, v.y, v.z)` of a Python instance, the values as it holds them.
    fn xyz(&self, rt: &Rt, instance: &Val) -> Result<Vec<Val>> {
        let getter = self.getter(rt, &self.xyz, &["x", "y", "z"])?;
        py::unpack(&py::call(&getter, vec![instance.clone()])?, 3)
    }
    /// A plane instance's twelve numbers: origin, xDir, yDir, zDir.
    fn frame(&self, rt: &Rt, instance: &Val) -> Result<Vec<Val>> {
        let getter = self.getter(rt, &self.frame, &PLANE_FIELDS)?;
        py::unpack(&py::call(&getter, vec![instance.clone()])?, 12)
    }
    /// `object.__new__(<class>)`: an instance whose fields are set one by one.
    fn bare(&self, rt: &Rt, class: &str) -> Result<Val> {
        let new = cached(&self.new, || rt.provider("builtins")?.attr("object")?.attr("__new__"))?;
        py::call(&new, vec![self.class(class)?])
    }
}

/// `isinstance(value, (int, float))`.
fn is_number(value: &Val) -> bool {
    matches!(value, Val::Int(_) | Val::Bool(_) | Val::Float(_))
}

/// `float(value)` as the runtime converts: text parses, anything else reads as a number, and a
/// value that is not one reads 0.0.
fn float(value: &Val) -> Result<f64> {
    Ok(match value {
        Val::Str(text) => text.parse()?,
        other => other.num().unwrap_or(0.),
    })
}

/// `math.sqrt` as the runtime's `math` computes it.
fn sqrt(x: f64) -> Result<f64> {
    ensure!(x >= 0., "math domain error");
    Ok(x.sqrt())
}

/// `math.acos`.
fn acos(x: f64) -> Result<f64> {
    let angle = x.acos();
    ensure!(angle.is_finite(), "math domain error");
    Ok(angle)
}

/// `min(a, b)` and `max(a, b)`: the first wins a tie; a NaN does not compare.
fn ordered(a: f64, b: f64) -> Result<()> {
    ensure!(a.partial_cmp(&b).is_some(), "unordered numeric comparison");
    Ok(())
}

fn index(items: &[Val], i: usize) -> Result<Val> {
    items.get(i).cloned().context("index out of range")
}

/// A point or direction; every component is a float.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Vector {
    pub x: f64,
    pub y: f64,
    pub z: f64,
}

impl Vector {
    pub const fn new(x: f64, y: f64, z: f64) -> Vector {
        Vector { x, y, z }
    }
    fn ints(v: [i64; 3]) -> Vector {
        Vector::new(v[0] as f64, v[1] as f64, v[2] as f64)
    }
    /// `toTuple()`.
    pub fn tuple(&self) -> [f64; 3] {
        [self.x, self.y, self.z]
    }
    /// `toTuple()` as Python sees it: a tuple of three floats.
    pub fn tuple_val(&self) -> Val {
        py::ftuple(&self.tuple())
    }
    /// `self + other`.
    pub fn add(&self, other: &Vector) -> Vector {
        Vector::new(self.x + other.x, self.y + other.y, self.z + other.z)
    }
    /// `self - other`.
    pub fn sub(&self, other: &Vector) -> Vector {
        Vector::new(self.x - other.x, self.y - other.y, self.z - other.z)
    }
    /// `self * scale`.
    pub fn mul(&self, scale: f64) -> Vector {
        Vector::new(self.x * scale, self.y * scale, self.z * scale)
    }
    /// `self / scale`: `self * (1.0 / scale)`.
    pub fn div(&self, scale: f64) -> Result<Vector> {
        ensure!(scale != 0., "division by zero");
        Ok(self.mul(1.0 / scale))
    }
    /// `-self`: `self * -1.0`.
    pub fn neg(&self) -> Vector {
        self.mul(-1.0)
    }
    /// The products summed in order from zero.
    pub fn dot(&self, other: &Vector) -> f64 {
        num::sum([self.x * other.x, self.y * other.y, self.z * other.z])
    }
    /// `.Length`: `math.sqrt(self.dot(self))`.
    pub fn length(&self) -> Result<f64> {
        sqrt(self.dot(self))
    }
    /// `self / self.Length`.
    pub fn normalized(&self) -> Result<Vector> {
        self.div(self.length()?)
    }
    pub fn cross(&self, other: &Vector) -> Vector {
        let (a, b, c) = (self.x, self.y, self.z);
        let (d, e, f) = (other.x, other.y, other.z);
        Vector::new(b * f - c * e, c * d - a * f, a * e - b * d)
    }
    /// `math.acos(max(-1.0, min(1.0, self.dot(other)/(self.Length*other.Length))))`.
    pub fn get_angle(&self, other: &Vector) -> Result<f64> {
        let dot = self.dot(other);
        let scale = self.length()? * other.length()?;
        ensure!(scale != 0., "division by zero");
        let cosine = dot / scale;
        ordered(1.0, cosine)?;
        let low = num::min2(1.0, cosine);
        ordered(-1.0, low)?;
        acos(num::max2(-1.0, low))
    }
    /// `repr(v)`: `Vector(1.0, 2.0, 3.0)`.
    pub fn repr(&self) -> Result<String> {
        Ok(format!("Vector{}", self.tuple_val().repr()?))
    }

    /// `Vector(x, y, z)`: a `Vector` instance for `x` copies it, any other value that is not a
    /// number is unpacked into three; every component becomes a float.
    pub fn args(rt: &Rt, x: &Val, y: &Val, z: &Val) -> Result<Vector> {
        let st = state(rt)?;
        let (x, y, z) = if st.is(rt, x, "Vector")? {
            let t = st.xyz(rt, x)?;
            (t[0].clone(), t[1].clone(), t[2].clone())
        } else if !is_number(x) {
            let t = py::unpack(x, 3)?;
            (t[0].clone(), t[1].clone(), t[2].clone())
        } else {
            (x.clone(), y.clone(), z.clone())
        };
        Ok(Vector::new(float(&x)?, float(&y)?, float(&z)?))
    }
    /// `Vector(value)`.
    pub fn of(rt: &Rt, value: &Val) -> Result<Vector> {
        Vector::args(rt, value, &Val::Float(0.0), &Val::Float(0.0))
    }
    /// A Python `Vector` instance's components.
    pub fn read(rt: &Rt, instance: &Val) -> Result<Vector> {
        let t = state(rt)?.xyz(rt, instance)?;
        Ok(Vector::new(t[0].num()?, t[1].num()?, t[2].num()?))
    }
    /// A new Python `Vector` instance holding these components.
    pub fn to_val(&self, rt: &Rt) -> Result<Val> {
        py::call(&state(rt)?.class("Vector")?, vec![Val::Float(self.x), Val::Float(self.y), Val::Float(self.z)])
    }
}

const AXES: [(&str, [i64; 3], [i64; 3]); 6] = [
    ("XY", [1, 0, 0], [0, 0, 1]),
    ("YZ", [0, 1, 0], [1, 0, 0]),
    ("XZ", [1, 0, 0], [0, -1, 0]),
    ("YX", [0, 1, 0], [0, 0, -1]),
    ("ZY", [0, 0, 1], [-1, 0, 0]),
    ("ZX", [0, 0, 1], [0, 1, 0]),
];

/// `axes[name]` of `Plane.named`.
fn named_axes(name: &Val) -> Result<([i64; 3], [i64; 3])> {
    let found = match name {
        Val::Str(text) => AXES.iter().find(|(key, _, _)| key == text),
        _ => None,
    };
    let (_, x, z) = found.with_context(|| format!("missing key {}", name.repr().unwrap_or_default()))?;
    Ok((*x, *z))
}

fn int_tuple(v: [i64; 3]) -> Val {
    py::tuple(v.map(Val::Int))
}

/// A plane: an origin and three orthonormal directions.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Plane {
    pub origin: Vector,
    pub x_dir: Vector,
    pub y_dir: Vector,
    pub z_dir: Vector,
}

impl Plane {
    /// `Plane(origin, xDir, normal)`: the normal normalized, `xDir` made square to it.
    pub fn new(origin: Vector, x_dir: Vector, normal: Vector) -> Result<Plane> {
        let z_dir = normal.normalized()?;
        let x_dir = square(&z_dir, &x_dir)?;
        let y_dir = z_dir.cross(&x_dir);
        Ok(Plane { origin, x_dir, y_dir, z_dir })
    }
    /// `Plane.named(name, origin)`.
    pub fn named(name: &str, origin: Vector) -> Result<Plane> {
        let (x, z) = named_axes(&py::s(name))?;
        Plane::new(origin, Vector::ints(x), Vector::ints(z))
    }
    /// `toWorldCoords(point)`; a point of two values lies in the plane.
    pub fn to_world(&self, point: &[f64]) -> Result<Vector> {
        let at = |i: usize| point.get(i).copied().context("index out of range");
        let (p0, p1) = (at(0)?, at(1)?);
        let p2 = if point.len() == 2 { 0.0 } else { at(2)? };
        Ok(self.origin.add(&self.x_dir.mul(p0)).add(&self.y_dir.mul(p1)).add(&self.z_dir.mul(p2)))
    }
    /// `toLocalCoords(point)`.
    pub fn to_local(&self, point: &Vector) -> Vector {
        let p = point.sub(&self.origin);
        Vector::new(p.dot(&self.x_dir), p.dot(&self.y_dir), p.dot(&self.z_dir))
    }
    /// `.location`.
    pub fn location(&self) -> Location {
        Location::from_plane(self)
    }
    /// A Python `Plane` instance's origin and directions.
    pub fn read(rt: &Rt, instance: &Val) -> Result<Plane> {
        let f = state(rt)?.frame(rt, instance)?;
        let v = |i: usize| -> Result<Vector> { Ok(Vector::new(f[i].num()?, f[i + 1].num()?, f[i + 2].num()?)) };
        Ok(Plane { origin: v(0)?, x_dir: v(3)?, y_dir: v(6)?, z_dir: v(9)? })
    }
    /// A new Python `Plane` instance holding these vectors, set in the order `__init__` sets them.
    pub fn to_val(&self, rt: &Rt) -> Result<Val> {
        let plane = state(rt)?.bare(rt, "Plane")?;
        plane.setattr("origin", self.origin.to_val(rt)?)?;
        plane.setattr("zDir", self.z_dir.to_val(rt)?)?;
        plane.setattr("xDir", self.x_dir.to_val(rt)?)?;
        plane.setattr("yDir", self.y_dir.to_val(rt)?)?;
        Ok(plane)
    }
}

/// `(Vector(xDir) - zDir*zDir.dot(xDir)).normalized()`.
fn square(z_dir: &Vector, x_dir: &Vector) -> Result<Vector> {
    x_dir.sub(&z_dir.mul(z_dir.dot(x_dir))).normalized()
}

/// A rigid placement: three rows of a rotation and a translation.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Location {
    pub rows: [[f64; 4]; 3],
}

const IDENTITY: [[f64; 3]; 3] = [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]];

/// The rotation of `angle` degrees about the unit axis `n`.
fn rotation(n: &Vector, angle: f64) -> [[f64; 3]; 3] {
    let (x, y, z) = (n.x, n.y, n.z);
    let (c, s) = (num::cos(num::radians(angle)), num::sin(num::radians(angle)));
    let d = 1.0 - c;
    [
        [c + x * x * d, x * y * d - z * s, x * z * d + y * s],
        [y * x * d + z * s, c + y * y * d, y * z * d - x * s],
        [z * x * d - y * s, z * y * d + x * s, c + z * z * d],
    ]
}

impl Location {
    /// `Location()`.
    pub fn identity() -> Location {
        Location::placed(&IDENTITY, &Vector::new(0., 0., 0.))
    }
    fn placed(rotation: &[[f64; 3]; 3], point: &Vector) -> Location {
        let p = point.tuple();
        Location { rows: [0, 1, 2].map(|k| [rotation[k][0], rotation[k][1], rotation[k][2], p[k]]) }
    }
    /// `Location(point, axis, angle)`: a rotation of `angle` degrees about `axis`, then `point`.
    pub fn at(point: &Vector, axis: Option<&Vector>, angle: f64) -> Result<Location> {
        let rotation = match axis {
            None => IDENTITY,
            Some(axis) => rotation(&axis.normalized()?, angle),
        };
        Ok(Location::placed(&rotation, point))
    }
    /// `Location(plane)`: the plane's directions as columns, its origin as the translation.
    pub fn from_plane(plane: &Plane) -> Location {
        let axes = [plane.x_dir.tuple(), plane.y_dir.tuple(), plane.z_dir.tuple()];
        let o = plane.origin.tuple();
        Location { rows: [0, 1, 2].map(|k| [axes[0][k], axes[1][k], axes[2][k], o[k]]) }
    }
    /// `self * other`.
    pub fn mul(&self, other: &Location) -> Location {
        let (a, b) = (&self.rows, &other.rows);
        let mut rows = [[0.; 4]; 3];
        for i in 0..3 {
            for j in 0..3 {
                rows[i][j] = num::sum((0..3).map(|k| a[i][k] * b[k][j]));
            }
            rows[i][3] = a[i][3] + num::sum((0..3).map(|k| a[i][k] * b[k][3]));
        }
        Location { rows }
    }
    /// `.inverse`.
    pub fn inverse(&self) -> Location {
        let r = &self.rows;
        let mut rows = [[0.; 4]; 3];
        for i in 0..3 {
            for j in 0..3 {
                rows[i][j] = r[j][i];
            }
            rows[i][3] = -num::sum((0..3).map(|j| r[j][i] * r[j][3]));
        }
        Location { rows }
    }
    /// `.wrapped.Transformation().Value(row, column)`, counted from one.
    pub fn value(&self, row: usize, column: usize) -> f64 {
        self.rows[row - 1][column - 1]
    }
    /// `.rows` as Python sees it: three tuples of four floats.
    pub fn rows_val(&self) -> Val {
        py::tuple(self.rows.iter().map(|row| py::ftuple(row)))
    }

    /// `Location(value)` with one argument: a `Location` copies its rows, a `Plane` gives its
    /// frame, anything else is a point.
    pub fn of(rt: &Rt, value: &Val) -> Result<Location> {
        let st = state(rt)?;
        if st.is(rt, value, "Location")? {
            return Location::read(rt, value);
        }
        if st.is(rt, value, "Plane")? {
            return Ok(Location::from_plane(&Plane::read(rt, value)?));
        }
        Location::at(&Vector::of(rt, value)?, None, 0.0)
    }
    /// A Python `Location` instance's rows.
    pub fn read(rt: &Rt, instance: &Val) -> Result<Location> {
        let _ = rt;
        Ok(Location { rows: rows(&instance.attr("rows")?)? })
    }
    /// A new Python `Location` instance holding these rows: `Location()`, then its `rows` and its
    /// `wrapped` matrix, as `__mul__` and `inverse` make their results.
    pub fn to_val(&self, rt: &Rt) -> Result<Val> {
        let st = state(rt)?;
        let result = py::call(&st.class("Location")?, vec![])?;
        let rows = self.rows_val();
        let wrapped = py::call(&st.class("_Matrix")?, vec![rows.clone()])?;
        result.setattr("rows", rows)?;
        result.setattr("wrapped", wrapped)?;
        Ok(result)
    }
}

/// A stand-in instance of `class` read back; any other value is not one.
fn instance<'a>(value: &'a Val, class: &str) -> Result<&'a Val> {
    ensure!(matches!(value, Val::Ref(_)), "expected a {class}, got {}", value.repr()?);
    Ok(value)
}

impl py::Py for Vector {
    /// A new `Vector` instance ([`Vector::to_val`]).
    fn to_py(&self) -> Result<Val> {
        self.to_val(&rt::current()?)
    }
    /// A `Vector` instance's components ([`Vector::read`]).
    fn from_py(value: &Val) -> Result<Self> {
        Vector::read(&rt::current()?, instance(value, "Vector")?)
    }
}
impl py::Py for Plane {
    /// A new `Plane` instance ([`Plane::to_val`]).
    fn to_py(&self) -> Result<Val> {
        self.to_val(&rt::current()?)
    }
    /// A `Plane` instance's origin and directions ([`Plane::read`]).
    fn from_py(value: &Val) -> Result<Self> {
        Plane::read(&rt::current()?, instance(value, "Plane")?)
    }
}
impl py::Py for Location {
    /// A new `Location` instance ([`Location::to_val`]).
    fn to_py(&self) -> Result<Val> {
        self.to_val(&rt::current()?)
    }
    /// A `Location` instance's rows ([`Location::read`]).
    fn from_py(value: &Val) -> Result<Self> {
        Location::read(&rt::current()?, instance(value, "Location")?)
    }
}

/// Three rows of four numbers, read as `rows[i][j]`.
fn rows(value: &Val) -> Result<[[f64; 4]; 3]> {
    let value = py::snapshot(value)?;
    let mut rows = [[0.; 4]; 3];
    for (i, row) in rows.iter_mut().enumerate() {
        let held = value.get(Val::Int(i as i64))?;
        for (j, cell) in row.iter_mut().enumerate() {
            *cell = held.get(Val::Int(j as i64))?.num()?;
        }
    }
    Ok(rows)
}

/// `n - 1` of a matrix index as the runtime subtracts.
fn before(n: &Val) -> Result<Val> {
    if is_number(n) {
        return Ok(Num::of(n)?.sub(Num::I(1)).val());
    }
    interop::binary("sub", n.clone(), Val::Int(1))
}

/// `self * scale` of a Python `Vector` instance.
fn scaled(rt: &Rt, this: &Val, scale: &Val) -> Result<Val> {
    if is_number(scale) {
        return Vector::read(rt, this)?.mul(Num::of(scale)?.f()).to_val(rt);
    }
    // A scale that is no number multiplies each component as the runtime's `*` does.
    let st = state(rt)?;
    let mut products = vec![];
    for a in st.xyz(rt, this)? {
        products.push(interop::binary("mul", a, scale.clone())?);
    }
    py::call(&st.class("Vector")?, products)
}

/// `Workplane.val()`.
fn workplane_val(this: &Val) -> Result<Val> {
    let objects = this.attr("objects")?;
    if !objects.truthy()? {
        bail!("normal enclosure geometry must be a Rust recipe");
    }
    objects.get(Val::Int(0))
}

const OPERATIONS: [&str; 8] = ["fuse", "cut", "intersect", "clean", "translate", "rotate", "mirror", "moved"];

/// `Workplane.<name>(*args, **kwargs)`: the operation on the held object, kept in a new
/// `Workplane` on the same plane.
fn operation(rt: &Rt, this: &Val, name: &str, args: py::Args, kwargs: py::Kwargs) -> Result<Val> {
    let st = state(rt)?;
    let mut values = Vec::with_capacity(args.len());
    for a in args {
        values.push(if st.is(rt, &a, "Workplane")? { workplane_val(&a)? } else { a });
    }
    let workplane = st.class("Workplane")?;
    let plane = this.attr("plane")?;
    let made = workplane_val(this)?.attr(name)?.call(values, kwargs)?;
    workplane.call(vec![plane], vec![("obj".into(), made)])
}

/// `Plane.named(cls, name, origin)`.
fn plane_named(cls: &Val, name: &Val, origin: Val) -> Result<Val> {
    let (x, z) = named_axes(name)?;
    py::call(cls, vec![origin, int_tuple(x), int_tuple(z)])
}

/// `install()`: make the source's datum names numeric before its first import.
pub fn install_standins(rt: &Rt) -> Result<()> {
    let st = state(rt)?;
    let file = py::path(&st.ns.get("__file__")?)?;
    let resolved = py::resolve(&file)?;
    let scripts = resolved.ancestors().nth(4).context("index out of range")?.join("scripts");
    let text = py::path_str(&scripts);
    if !py::sys_path_has(rt, &text)? {
        py::sys_path_insert(rt, &text)?;
    }
    let rust_part = rt.import("_rust_part")?;
    py::method(&rust_part, "start", vec![])?;
    let update = rust_part.attr("_STANDINS")?.attr("update")?;
    let shape = st.class("Shape")?;
    py::call_kw(&update, vec![], vec![
        ("Vector", st.class("Vector")?),
        ("Plane", st.class("Plane")?),
        ("Location", st.class("Location")?),
        ("Workplane", st.class("Workplane")?),
        ("Shape", shape.clone()),
        ("Solid", shape.clone()),
        ("Compound", shape.clone()),
        ("Face", shape.clone()),
        ("Wire", shape.clone()),
        ("Edge", shape),
        ("MESH", Val::Bool(false)),
        ("__path__", Val::list(vec![])),
    ])?;
    Ok(())
}

/// `load()`: the current scalar enclosure source, with Rust construction recipes.
pub fn load(rt: &Rt) -> Result<Val> {
    install_standins(rt)?;
    rt.import("enclosure")
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    rt.keep(MODULE, State {
        ns: ns.clone(),
        isinstance: RefCell::new(None),
        xyz: RefCell::new(None),
        frame: RefCell::new(None),
        new: RefCell::new(None),
    });
    ns.set("importlib", rt.import("importlib")?)?;
    ns.set("math", rt.import("math")?)?;
    rt.import("pathlib")?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    ns.set("sys", rt.import("sys")?)?;

    ns.def(rt, "Vector.__init__", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "x", "y", "z"], &[])?;
        let this = b.req("self")?;
        let x = b.opt("x").unwrap_or(Val::Float(0.0));
        let y = b.opt("y").unwrap_or(Val::Float(0.0));
        let z = b.opt("z").unwrap_or(Val::Float(0.0));
        let v = Vector::args(rt, &x, &y, &z)?;
        this.setattr("x", Val::Float(v.x))?;
        this.setattr("y", Val::Float(v.y))?;
        this.setattr("z", Val::Float(v.z))?;
        Ok(Val::None)
    })?;
    ns.def(rt, "Vector.toTuple", |rt, args, kwargs| {
        let this = py::bind(args, kwargs, &["self"], &[])?.req("self")?;
        Ok(Val::Tuple(state(rt)?.xyz(rt, &this)?))
    })?;
    ns.def(rt, "Vector.__iter__", |rt, args, kwargs| {
        let this = py::bind(args, kwargs, &["self"], &[])?.req("self")?;
        Ok(Val::Tuple(state(rt)?.xyz(rt, &this)?))
    })?;
    ns.def(rt, "Vector.__getitem__", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "key"], &[])?;
        let (this, key) = (b.req("self")?, b.req("key")?);
        Val::Tuple(state(rt)?.xyz(rt, &this)?).get(key)
    })?;
    ns.def(rt, "Vector.__add__", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "other"], &[])?;
        let (this, other) = (b.req("self")?, b.req("other")?);
        let other = Vector::of(rt, &other)?;
        Vector::read(rt, &this)?.add(&other).to_val(rt)
    })?;
    ns.def(rt, "Vector.__sub__", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "other"], &[])?;
        let (this, other) = (b.req("self")?, b.req("other")?);
        let other = Vector::of(rt, &other)?;
        Vector::read(rt, &this)?.sub(&other).to_val(rt)
    })?;
    ns.def(rt, "Vector.__mul__", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "scale"], &[])?;
        let (this, scale) = (b.req("self")?, b.req("scale")?);
        scaled(rt, &this, &scale)
    })?;
    ns.def(rt, "Vector.__truediv__", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "scale"], &[])?;
        let (this, scale) = (b.req("self")?, b.req("scale")?);
        if is_number(&scale) {
            return Vector::read(rt, &this)?.div(Num::of(&scale)?.f())?.to_val(rt);
        }
        interop::binary("mul", this, interop::binary("truediv", Val::Float(1.0), scale)?)
    })?;
    ns.def(rt, "Vector.__neg__", |rt, args, kwargs| {
        let this = py::bind(args, kwargs, &["self"], &[])?.req("self")?;
        Vector::read(rt, &this)?.neg().to_val(rt)
    })?;
    ns.def(rt, "Vector.Length", |rt, args, kwargs| {
        let this = py::bind(args, kwargs, &["self"], &[])?.req("self")?;
        Ok(Val::Float(Vector::read(rt, &this)?.length()?))
    })?;
    ns.def(rt, "Vector.normalized", |rt, args, kwargs| {
        let this = py::bind(args, kwargs, &["self"], &[])?.req("self")?;
        Vector::read(rt, &this)?.normalized()?.to_val(rt)
    })?;
    ns.def(rt, "Vector.dot", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "other"], &[])?;
        let (this, other) = (b.req("self")?, b.req("other")?);
        let other = Vector::of(rt, &other)?;
        Ok(Val::Float(Vector::read(rt, &this)?.dot(&other)))
    })?;
    ns.def(rt, "Vector.cross", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "other"], &[])?;
        let (this, other) = (b.req("self")?, b.req("other")?);
        let mine = Vector::read(rt, &this)?;
        mine.cross(&Vector::of(rt, &other)?).to_val(rt)
    })?;
    ns.def(rt, "Vector.getAngle", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "other"], &[])?;
        let (this, other) = (b.req("self")?, b.req("other")?);
        let other = Vector::of(rt, &other)?;
        Ok(Val::Float(Vector::read(rt, &this)?.get_angle(&other)?))
    })?;
    ns.def(rt, "Vector.__repr__", |rt, args, kwargs| {
        let this = py::bind(args, kwargs, &["self"], &[])?.req("self")?;
        Ok(Val::Str(format!("Vector{}", Val::Tuple(state(rt)?.xyz(rt, &this)?).repr()?)))
    })?;
    ns.set("Vector", rt.python_type(MODULE, "Vector")?)?;

    ns.def(rt, "Plane.__init__", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "origin", "xDir", "normal"], &[])?;
        let this = b.req("self")?;
        let origin = b.opt("origin").unwrap_or_else(|| int_tuple([0, 0, 0]));
        let x_dir = b.opt("xDir").unwrap_or_else(|| int_tuple([1, 0, 0]));
        let normal = b.opt("normal").unwrap_or_else(|| int_tuple([0, 0, 1]));
        this.setattr("origin", Vector::of(rt, &origin)?.to_val(rt)?)?;
        let z_dir = Vector::of(rt, &normal)?.normalized()?;
        this.setattr("zDir", z_dir.to_val(rt)?)?;
        let x_dir = square(&z_dir, &Vector::of(rt, &x_dir)?)?;
        this.setattr("xDir", x_dir.to_val(rt)?)?;
        this.setattr("yDir", z_dir.cross(&x_dir).to_val(rt)?)?;
        Ok(Val::None)
    })?;
    ns.def(rt, "Plane.named", |_rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["cls", "name", "origin"], &[])?;
        let (cls, name) = (b.req("cls")?, b.req("name")?);
        let origin = b.opt("origin").unwrap_or_else(|| int_tuple([0, 0, 0]));
        plane_named(&cls, &name, origin)
    })?;
    ns.def(rt, "Plane.toWorldCoords", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "point"], &[])?;
        let (this, point) = (b.req("self")?, b.req("point")?);
        let mut point = point.iter()?;
        if point.len() == 2 {
            point.push(Val::Float(0.0));
        }
        if point.len() >= 3 && point[..3].iter().all(is_number) {
            let p = [point[0].num()?, point[1].num()?, point[2].num()?];
            return Plane::read(rt, &this)?.to_world(&p)?.to_val(rt);
        }
        // Components that are no numbers scale the Python directions as the runtime's `*` does.
        let mul = |axis: &str, i: usize| -> Result<Val> { interop::binary("mul", this.attr(axis)?, index(&point, i)?) };
        let sum = interop::binary("add", this.attr("origin")?, mul("xDir", 0)?)?;
        let sum = interop::binary("add", sum, mul("yDir", 1)?)?;
        interop::binary("add", sum, mul("zDir", 2)?)
    })?;
    ns.def(rt, "Plane.toLocalCoords", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "point"], &[])?;
        let (this, point) = (b.req("self")?, b.req("point")?);
        let point = Vector::of(rt, &point)?;
        Plane::read(rt, &this)?.to_local(&point).to_val(rt)
    })?;
    ns.def(rt, "Plane.location", |rt, args, kwargs| {
        let this = py::bind(args, kwargs, &["self"], &[])?.req("self")?;
        py::call(&state(rt)?.class("Location")?, vec![this])
    })?;
    ns.set("Plane", rt.python_type(MODULE, "Plane")?)?;

    ns.def(rt, "_Matrix.__init__", |_rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "rows"], &[])?;
        let (this, rows) = (b.req("self")?, b.req("rows")?);
        this.setattr("rows", rows)?;
        Ok(Val::None)
    })?;
    ns.def(rt, "_Matrix.Transformation", |_rt, args, kwargs| {
        py::bind(args, kwargs, &["self"], &[])?.req("self")
    })?;
    ns.def(rt, "_Matrix.Value", |_rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "row", "column"], &[])?;
        let (this, row, column) = (b.req("self")?, b.req("row")?, b.req("column")?);
        this.attr("rows")?.get(before(&row)?)?.get(before(&column)?)
    })?;
    ns.set("_Matrix", rt.python_type(MODULE, "_Matrix")?)?;

    ns.def(rt, "Location.__init__", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "point", "axis", "angle"], &[])?;
        let this = b.req("self")?;
        let point = b.opt("point").unwrap_or_else(|| int_tuple([0, 0, 0]));
        let axis = b.opt("axis").unwrap_or(Val::None);
        let angle = b.opt("angle").unwrap_or(Val::Float(0.0));
        let st = state(rt)?;
        let rows = if st.is(rt, &point, "Location")? {
            point.attr("rows")?
        } else if st.is(rt, &point, "Plane")? {
            Location::from_plane(&Plane::read(rt, &point)?).rows_val()
        } else {
            let point = Vector::of(rt, &point)?;
            let rotation = if matches!(axis, Val::None) {
                IDENTITY
            } else {
                let axis = Vector::of(rt, &axis)?.normalized()?;
                rotation(&axis, angle.num().ok().context("math numeric argument")?)
            };
            Location::placed(&rotation, &point).rows_val()
        };
        this.setattr("rows", rows.clone())?;
        this.setattr("wrapped", py::call(&st.class("_Matrix")?, vec![rows])?)?;
        Ok(Val::None)
    })?;
    ns.def(rt, "Location.__mul__", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "other"], &[])?;
        let (this, other) = (b.req("self")?, b.req("other")?);
        let other = Location::of(rt, &other)?;
        Location::read(rt, &this)?.mul(&other).to_val(rt)
    })?;
    ns.def(rt, "Location.inverse", |rt, args, kwargs| {
        let this = py::bind(args, kwargs, &["self"], &[])?.req("self")?;
        Location::read(rt, &this)?.inverse().to_val(rt)
    })?;
    ns.set("Location", rt.python_type(MODULE, "Location")?)?;

    ns.def(rt, "Workplane.__init__", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "plane", "origin", "obj"], &[])?;
        let this = b.req("self")?;
        let plane = b.opt("plane").unwrap_or_else(|| py::s("XY"));
        let origin = b.opt("origin").unwrap_or_else(|| int_tuple([0, 0, 0]));
        let obj = b.opt("obj").unwrap_or(Val::None);
        let st = state(rt)?;
        let plane = if st.is(rt, &plane, "Plane")? { plane } else { plane_named(&st.class("Plane")?, &plane, origin)? };
        this.setattr("plane", plane)?;
        this.setattr("objects", Val::list(if matches!(obj, Val::None) { vec![] } else { vec![obj] }))?;
        Ok(Val::None)
    })?;
    ns.def(rt, "Workplane.val", |_rt, args, kwargs| {
        let this = py::bind(args, kwargs, &["self"], &[])?.req("self")?;
        workplane_val(&this)
    })?;
    ns.def(rt, "Workplane.vals", |_rt, args, kwargs| {
        let this = py::bind(args, kwargs, &["self"], &[])?.req("self")?;
        this.attr("objects")
    })?;
    ns.def(rt, "Workplane.__getattr__", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "name"], &[])?;
        let (this, name) = (b.req("self")?, b.req("name")?);
        if let Val::Str(text) = &name
            && OPERATIONS.contains(&text.as_str())
        {
            let text = text.clone();
            return Ok(state(rt)?.ns.function(rt, move |rt, args, kwargs| operation(rt, &this, &text, args, kwargs)));
        }
        bail!("{}: normal enclosure geometry must be a Rust recipe", num::fmtv(&name, "")?)
    })?;
    ns.set("Workplane", rt.python_type(MODULE, "Workplane")?)?;
    ns.set("Shape", rt.python_type(MODULE, "Shape")?)?;

    ns.def(rt, "install", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        install_standins(rt)?;
        Ok(Val::None)
    })?;
    ns.def(rt, "load", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        load(rt)
    })?;
    Ok(())
}

pub fn main_block(_rt: &Rt) -> Result<()> {
    Ok(())
}
