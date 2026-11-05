//! Arithmetic and text the way the recipes' value runtime computes them.
//!
//! The runtime's `math`, `round`, `sum`, `min`, `max`, `sorted` and format specifications define
//! every number these modules write, so the typed modules compute through the same operations.
use anyhow::Result;
use hsm_documents::interop::{self, Val};
use std::cmp::Ordering;
use std::f64::consts::PI;

/// `format(x, spec)` / an f-string field.
pub fn fmt(x: f64, spec: &str) -> String {
    interop::format(&Val::Float(x), spec).expect("float format")
}
pub fn fmti(x: i64, spec: &str) -> String {
    interop::format(&Val::Int(x), spec).expect("int format")
}
/// `format(value, spec)` for any value.
pub fn fmtv(value: &Val, spec: &str) -> Result<String> {
    interop::format(value, spec)
}
/// `str(x)` of a float.
pub fn fstr(x: f64) -> String {
    Val::Float(x).str().expect("float text")
}

/// `math.sin(x)`: one libm `sin`. An optimized build merges a `sin` and a `cos` of one angle in
/// one block into a single `__sincos_stret` call, whose result can differ in the last place;
/// the runtime calls each on its own, and so does this.
#[inline(never)]
pub fn sin(x: f64) -> f64 {
    x.sin()
}
/// `math.cos(x)`: one libm `cos`, never merged with a `sin` (see [`sin`]).
#[inline(never)]
pub fn cos(x: f64) -> f64 {
    x.cos()
}

/// `round(x, digits)`.
pub fn round_to(x: f64, digits: i64) -> f64 {
    if digits >= 0 {
        hsm_documents::format_number(x, &format!(".{digits}f")).expect("round").parse().expect("rounded")
    } else {
        let scale = 10f64.powi(-digits as i32);
        (x / scale).round_ties_even() * scale
    }
}
/// `round(x)`.
pub fn round_int(x: f64) -> i64 {
    x.round_ties_even() as i64
}

pub fn radians(x: f64) -> f64 {
    x * PI / 180.
}
pub fn degrees(x: f64) -> f64 {
    x * 180. / PI
}
/// `math.hypot(*values)`.
pub fn hypot(values: &[f64]) -> f64 {
    values.iter().fold(0f64, |a, &b| a.hypot(b))
}
pub fn hypot2(a: f64, b: f64) -> f64 {
    0f64.hypot(a).hypot(b)
}
pub fn hypot3(a: f64, b: f64, c: f64) -> f64 {
    0f64.hypot(a).hypot(b).hypot(c)
}
/// `math.dist(a, b)`.
pub fn dist(a: &[f64], b: &[f64]) -> f64 {
    a.iter().zip(b).fold(0f64, |n, (a, b)| n.hypot(a - b))
}
pub fn isclose(a: f64, b: f64, rel: f64, abs: f64) -> bool {
    (a - b).abs() <= abs.max(rel * a.abs().max(b.abs()))
}
/// `a // b` for floats.
pub fn floordiv(a: f64, b: f64) -> f64 {
    (a / b).floor()
}
/// `a % b` for floats.
pub fn modulo(a: f64, b: f64) -> f64 {
    let rem = a % b;
    if rem != 0. && rem.signum() != b.signum() { rem + b } else { rem }
}
/// `math.floor`, `math.ceil` and `int()` of a float.
pub fn floor(x: f64) -> i64 {
    x.floor() as i64
}
pub fn ceil(x: f64) -> i64 {
    x.ceil() as i64
}

/// `max(a, b)`: the first wins a tie.
pub fn max2(a: f64, b: f64) -> f64 {
    if b > a { b } else { a }
}
/// `min(a, b)`: the first wins a tie.
pub fn min2(a: f64, b: f64) -> f64 {
    if b < a { b } else { a }
}
/// `max(values)` of a non-empty sequence.
pub fn max_of(values: impl IntoIterator<Item = f64>) -> Option<f64> {
    values.into_iter().fold(None, |best, x| Some(match best {
        Some(b) if !(x > b) => b,
        _ => x,
    }))
}
/// `min(values)` of a non-empty sequence.
pub fn min_of(values: impl IntoIterator<Item = f64>) -> Option<f64> {
    values.into_iter().fold(None, |best, x| Some(match best {
        Some(b) if !(x < b) => b,
        _ => x,
    }))
}
/// The index `max(range, key=...)` picks: the first of equal keys.
pub fn argmax<T>(items: &[T], key: impl Fn(&T) -> f64) -> Option<usize> {
    let mut best: Option<(usize, f64)> = None;
    for (i, item) in items.iter().enumerate() {
        let k = key(item);
        if best.is_none_or(|(_, b)| k > b) {
            best = Some((i, k));
        }
    }
    best.map(|(i, _)| i)
}
pub fn argmin<T>(items: &[T], key: impl Fn(&T) -> f64) -> Option<usize> {
    let mut best: Option<(usize, f64)> = None;
    for (i, item) in items.iter().enumerate() {
        let k = key(item);
        if best.is_none_or(|(_, b)| k < b) {
            best = Some((i, k));
        }
    }
    best.map(|(i, _)| i)
}

/// `sum(values)` of floats: the runtime adds from the integer 0, so an empty sum is the int 0.
pub fn sum(values: impl IntoIterator<Item = f64>) -> f64 {
    values.into_iter().fold(0f64, |a, b| a + b)
}
/// `sum(values)` as the value the runtime returns, int 0 when there is nothing to add.
pub fn sum_val(values: &[f64]) -> Val {
    if values.is_empty() { Val::Int(0) } else { Val::Float(sum(values.iter().copied())) }
}

/// The runtime's ordering of two numbers; unordered pairs sort as equal.
pub fn order(a: f64, b: f64) -> Ordering {
    a.partial_cmp(&b).unwrap_or(Ordering::Equal)
}
/// `sorted(items, key=..., reverse=...)`: a stable ascending sort, reversed whole when asked.
pub fn sort_by_key<T>(items: &mut [T], key: impl Fn(&T) -> f64, reverse: bool) {
    items.sort_by(|a, b| order(key(a), key(b)));
    if reverse {
        items.reverse();
    }
}
/// `sorted` with a tuple key of numbers.
pub fn sort_by_keys<T>(items: &mut [T], key: impl Fn(&T) -> Vec<f64>, reverse: bool) {
    items.sort_by(|a, b| {
        let (a, b) = (key(a), key(b));
        for (x, y) in a.iter().zip(&b) {
            let o = order(*x, *y);
            if o != Ordering::Equal {
                return o;
            }
        }
        a.len().cmp(&b.len())
    });
    if reverse {
        items.reverse();
    }
}

/// A number that is an int or a float as Python holds it: arithmetic keeps the runtime's rule
/// that two ints give an int whenever the result is integral.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Num {
    I(i64),
    F(f64),
}
impl Num {
    pub fn of(v: &Val) -> Result<Num> {
        Ok(match v {
            Val::Int(i) => Num::I(*i),
            Val::Bool(b) => Num::I(*b as i64),
            _ => Num::F(v.num()?),
        })
    }
    pub fn f(self) -> f64 {
        match self {
            Num::I(i) => i as f64,
            Num::F(x) => x,
        }
    }
    pub fn val(self) -> Val {
        match self {
            Num::I(i) => Val::Int(i),
            Num::F(x) => Val::Float(x),
        }
    }
    fn combine(self, other: Num, value: f64) -> Num {
        match (self, other) {
            (Num::I(_), Num::I(_)) if value.is_finite() && value.fract() == 0. => Num::I(value as i64),
            _ => Num::F(value),
        }
    }
    pub fn add(self, o: Num) -> Num {
        self.combine(o, self.f() + o.f())
    }
    pub fn sub(self, o: Num) -> Num {
        self.combine(o, self.f() - o.f())
    }
    pub fn mul(self, o: Num) -> Num {
        self.combine(o, self.f() * o.f())
    }
    pub fn div(self, o: Num) -> Num {
        Num::F(self.f() / o.f())
    }
    pub fn neg(self) -> Num {
        match self {
            Num::I(i) => Num::I(-i),
            Num::F(x) => Num::F(-x),
        }
    }
    /// Three numbers of a sequence.
    pub fn three(v: &Val) -> Result<[Num; 3]> {
        let r = v.iter()?;
        anyhow::ensure!(r.len() == 3, "expected three coordinates, got {}", r.len());
        Ok([Num::of(&r[0])?, Num::of(&r[1])?, Num::of(&r[2])?])
    }
    pub fn vals(values: &[Num]) -> Val {
        Val::Tuple(values.iter().map(|n| n.val()).collect())
    }
    /// `min(self, other)`: the first wins a tie.
    pub fn min(self, o: Num) -> Num {
        if o.f() < self.f() { o } else { self }
    }
    pub fn max(self, o: Num) -> Num {
        if o.f() > self.f() { o } else { self }
    }
    pub fn fmt(self, spec: &str) -> String {
        interop::format(&self.val(), spec).expect("number format")
    }
}
impl From<Num> for Val {
    fn from(n: Num) -> Val {
        n.val()
    }
}
