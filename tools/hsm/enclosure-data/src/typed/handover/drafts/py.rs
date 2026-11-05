//! The arithmetic the enclosure recipes were written against, as plain functions on `f64`
//! and `i64`. Each one gives the same bits as the expression it names did, so a value moved
//! onto a typed path reads the same in every output that prints or keys on it.
//!
//! Where a Python-facing result kept an integer's type, the typed code keeps an `i64`;
//! [`Num`] holds a number whose type depends on the caller.
use anyhow::{Context, Result, bail, ensure};
use hsm_documents::interop::Val;
use std::cmp::Ordering;

/// `math.pi`.
pub const PI: f64 = std::f64::consts::PI;

/// `math.radians(x)`: `x * pi / 180`, rounded after each step.
pub fn radians(x: f64) -> f64 {
    x * PI / 180.
}

/// `math.degrees(x)`: `x * 180 / pi`, rounded after each step.
pub fn degrees(x: f64) -> f64 {
    x * 180. / PI
}

/// `math.hypot(*values)`: a running `hypot` from zero.
pub fn hypot(values: &[f64]) -> f64 {
    values.iter().fold(0f64, |a, &b| a.hypot(b))
}

/// `math.hypot(a, b)`.
pub fn hypot2(a: f64, b: f64) -> f64 {
    0f64.hypot(a).hypot(b)
}

/// `math.dist(a, b)`: a running `hypot` of the differences from zero.
pub fn dist(a: &[f64], b: &[f64]) -> f64 {
    a.iter().zip(b).fold(0f64, |n, (a, b)| n.hypot(a - b))
}

/// `sum(values)` over floats: a left fold from the integer zero.
pub fn sum(values: impl IntoIterator<Item = f64>) -> f64 {
    values.into_iter().fold(0.0, |a, b| a + b)
}

/// `x // y` on floats: the quotient's floor.
pub fn floordiv(x: f64, y: f64) -> f64 {
    (x / y).floor()
}

/// `x % y` on floats: the remainder carrying the divisor's sign.
pub fn modulo(x: f64, y: f64) -> f64 {
    let rem = x % y;
    if rem != 0. && rem.signum() != y.signum() {
        rem + y
    } else {
        rem
    }
}

/// `x // y` on integers.
pub fn ifloordiv(x: i64, y: i64) -> i64 {
    (x as f64 / y as f64).floor() as i64
}

/// `x % y` on integers.
pub fn imodulo(x: i64, y: i64) -> i64 {
    modulo(x as f64, y as f64) as i64
}

/// `x ** y` on floats.
pub fn pow(x: f64, y: f64) -> f64 {
    x.powf(y)
}

/// `round(x)`: the nearest integer, ties to even.
pub fn round(x: f64) -> i64 {
    x.round_ties_even() as i64
}

/// `round(x, digits)`: the value its fixed-point text reads back as.
pub fn round_to(x: f64, digits: i32) -> f64 {
    if digits >= 0 {
        hsm_documents::format_number(x, &format!(".{digits}f"))
            .expect("fixed-point text")
            .parse()
            .expect("fixed-point text reads back")
    } else {
        let scale = 10f64.powi(-digits);
        (x / scale).round_ties_even() * scale
    }
}

/// `math.floor`, `math.ceil` and `math.trunc` give integers.
pub fn floor(x: f64) -> i64 {
    x.floor() as i64
}
pub fn ceil(x: f64) -> i64 {
    x.ceil() as i64
}
pub fn trunc(x: f64) -> i64 {
    x.trunc() as i64
}

/// `math.isclose(a, b, rel_tol=rel, abs_tol=abs)`; the defaults are `1e-9` and `0.0`.
pub fn isclose(a: f64, b: f64, rel: f64, abs: f64) -> bool {
    (a - b).abs() <= abs.max(rel * a.abs().max(b.abs()))
}

/// The ordering `<` gives two floats; unordered values are an error where one is compared.
pub fn cmp(a: f64, b: f64) -> Ordering {
    a.partial_cmp(&b).expect("ordered values")
}

/// `min(values)`: the first of the smallest.
pub fn min(values: impl IntoIterator<Item = f64>) -> f64 {
    let mut it = values.into_iter();
    let mut best = it.next().expect("min of no values");
    for v in it {
        if cmp(v, best).is_lt() {
            best = v;
        }
    }
    best
}

/// `max(values)`: the first of the largest.
pub fn max(values: impl IntoIterator<Item = f64>) -> f64 {
    let mut it = values.into_iter();
    let mut best = it.next().expect("max of no values");
    for v in it {
        if cmp(v, best).is_gt() {
            best = v;
        }
    }
    best
}

/// `min(a, b)` and `max(a, b)`.
pub fn min2(a: f64, b: f64) -> f64 {
    if cmp(b, a).is_lt() { b } else { a }
}
pub fn max2(a: f64, b: f64) -> f64 {
    if cmp(b, a).is_gt() { b } else { a }
}

/// `min(values, key=key)`: the first value whose key is smallest.
pub fn min_by_key<T, K: PartialOrd>(values: impl IntoIterator<Item = T>, key: impl Fn(&T) -> K) -> T {
    let mut best: Option<(T, K)> = None;
    for v in values {
        let k = key(&v);
        if best.as_ref().is_none_or(|(_, b)| k.partial_cmp(b).expect("ordered keys").is_lt()) {
            best = Some((v, k));
        }
    }
    best.expect("min of no values").0
}

/// `max(values, key=key)`: the first value whose key is largest.
pub fn max_by_key<T, K: PartialOrd>(values: impl IntoIterator<Item = T>, key: impl Fn(&T) -> K) -> T {
    let mut best: Option<(T, K)> = None;
    for v in values {
        let k = key(&v);
        if best.as_ref().is_none_or(|(_, b)| k.partial_cmp(b).expect("ordered keys").is_gt()) {
            best = Some((v, k));
        }
    }
    best.expect("max of no values").0
}

/// `sorted(values)` on floats: a stable ascending sort.
pub fn sorted(mut values: Vec<f64>) -> Vec<f64> {
    values.sort_by(|a, b| cmp(*a, *b));
    values
}

/// `sorted((a, b))`.
pub fn sorted2(a: f64, b: f64) -> [f64; 2] {
    if cmp(b, a).is_lt() { [b, a] } else { [a, b] }
}

/// `sorted(values, key=key)`: stable by key.
pub fn sorted_by_key<T, K: PartialOrd>(mut values: Vec<T>, key: impl Fn(&T) -> K) -> Vec<T> {
    values.sort_by(|a, b| key(a).partial_cmp(&key(b)).expect("ordered keys"));
    values
}

/// `str(x)` and `repr(x)` of a float: the shortest text that reads back as `x`.
pub fn float_text(x: f64) -> String {
    Val::Float(x).str().expect("float text")
}

/// `format(value, spec)` and an f-string field `{value:spec}`.
pub fn format(value: impl Into<Val>, spec: &str) -> String {
    hsm_documents::interop::format(&value.into(), spec).expect("format spec")
}

/// A number whose integer or float type is the caller's: what reaches a document keeps it.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Num {
    Int(i64),
    Float(f64),
}

impl Num {
    pub fn f(self) -> f64 {
        match self {
            Num::Int(n) => n as f64,
            Num::Float(x) => x,
        }
    }
    fn arith(self, other: Num, value: f64) -> Num {
        match (self, other) {
            (Num::Int(_), Num::Int(_)) if value.is_finite() && value.fract() == 0. => {
                Num::Int(value as i64)
            }
            _ => Num::Float(value),
        }
    }
    pub fn add(self, other: Num) -> Num {
        self.arith(other, self.f() + other.f())
    }
    pub fn sub(self, other: Num) -> Num {
        self.arith(other, self.f() - other.f())
    }
    pub fn mul(self, other: Num) -> Num {
        self.arith(other, self.f() * other.f())
    }
    pub fn neg(self) -> Num {
        match self {
            Num::Int(n) => Num::Int(-n),
            Num::Float(x) => Num::Float(-x),
        }
    }
    pub fn abs(self) -> Num {
        match self {
            Num::Int(n) => Num::Int(n.abs()),
            Num::Float(x) => Num::Float(x.abs()),
        }
    }
    pub fn val(self) -> Val {
        match self {
            Num::Int(n) => Val::Int(n),
            Num::Float(x) => Val::Float(x),
        }
    }
    pub fn from_val(value: &Val) -> Result<Num> {
        Ok(match value {
            Val::Int(n) => Num::Int(*n),
            Val::Bool(b) => Num::Int(*b as i64),
            Val::Float(x) => Num::Float(*x),
            other => Num::Float(other.num().with_context(|| format!("number from {other:?}"))?),
        })
    }
}

impl From<f64> for Num {
    fn from(x: f64) -> Self {
        Num::Float(x)
    }
}
impl From<i64> for Num {
    fn from(n: i64) -> Self {
        Num::Int(n)
    }
}
impl From<Num> for Val {
    fn from(n: Num) -> Self {
        n.val()
    }
}
impl PartialOrd for Num {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        self.f().partial_cmp(&other.f())
    }
}

/// A value as the Python side receives it. Containers keep the list or tuple they were.
pub trait IntoVal {
    fn into_val(self) -> Val;
}
impl IntoVal for Val {
    fn into_val(self) -> Val {
        self
    }
}
impl IntoVal for &Val {
    fn into_val(self) -> Val {
        self.clone()
    }
}
impl IntoVal for f64 {
    fn into_val(self) -> Val {
        Val::Float(self)
    }
}
impl IntoVal for i64 {
    fn into_val(self) -> Val {
        Val::Int(self)
    }
}
impl IntoVal for i32 {
    fn into_val(self) -> Val {
        Val::Int(self as i64)
    }
}
impl IntoVal for usize {
    fn into_val(self) -> Val {
        Val::Int(self as i64)
    }
}
impl IntoVal for bool {
    fn into_val(self) -> Val {
        Val::Bool(self)
    }
}
impl IntoVal for Num {
    fn into_val(self) -> Val {
        self.val()
    }
}
impl IntoVal for &str {
    fn into_val(self) -> Val {
        Val::Str(self.into())
    }
}
impl IntoVal for String {
    fn into_val(self) -> Val {
        Val::Str(self)
    }
}
impl<T: IntoVal> IntoVal for Option<T> {
    fn into_val(self) -> Val {
        self.map_or(Val::None, IntoVal::into_val)
    }
}
/// A `Vec` is a Python list.
impl<T: IntoVal> IntoVal for Vec<T> {
    fn into_val(self) -> Val {
        Val::list(self.into_iter().map(IntoVal::into_val).collect())
    }
}
/// A fixed-size array is a Python tuple.
impl<T: IntoVal, const N: usize> IntoVal for [T; N] {
    fn into_val(self) -> Val {
        Val::tuple(self.into_iter().map(IntoVal::into_val).collect())
    }
}
macro_rules! tuple_into_val {
    ($($name:ident),+) => {
        impl<$($name: IntoVal),+> IntoVal for ($($name,)+) {
            #[allow(non_snake_case)]
            fn into_val(self) -> Val {
                let ($($name,)+) = self;
                Val::tuple(vec![$($name.into_val()),+])
            }
        }
    };
}
tuple_into_val!(A);
tuple_into_val!(A, B);
tuple_into_val!(A, B, C);
tuple_into_val!(A, B, C, D);
tuple_into_val!(A, B, C, D, E);
tuple_into_val!(A, B, C, D, E, F);
tuple_into_val!(A, B, C, D, E, F, G);
tuple_into_val!(A, B, C, D, E, F, G, H);

/// A Python tuple of the given values.
pub fn tuple(values: Vec<Val>) -> Val {
    Val::tuple(values)
}

/// A Python list of the given values.
pub fn list(values: Vec<Val>) -> Val {
    Val::list(values)
}

/// A Python dict with string keys, in the order given.
pub fn dict(entries: Vec<(&str, Val)>) -> Val {
    Val::dict(entries.into_iter().map(|(k, v)| (Val::Str(k.into()), v)).collect())
}

/// A float read off a value the Python side handed over.
pub fn f(value: &Val) -> Result<f64> {
    value.num()
}

/// An integer read off a value the Python side handed over.
pub fn i(value: &Val) -> Result<i64> {
    value.integer()
}

/// Six floats read off a sequence.
pub fn six(value: &Val) -> Result<[f64; 6]> {
    let items = value.iter()?;
    ensure!(items.len() == 6, "six values, not {}", items.len());
    let mut out = [0.; 6];
    for (o, v) in out.iter_mut().zip(&items) {
        *o = v.num()?;
    }
    Ok(out)
}

/// `n` floats read off a sequence.
pub fn floats(value: &Val) -> Result<Vec<f64>> {
    value.iter()?.iter().map(Val::num).collect()
}

/// A field of a Python object or namespace the typed code reads.
pub fn attr(value: &Val, name: &str) -> Result<Val> {
    value.attr(name).with_context(|| format!("attribute {name}"))
}

/// A float attribute.
pub fn attr_f(value: &Val, name: &str) -> Result<f64> {
    attr(value, name)?.num().with_context(|| format!("float attribute {name}"))
}

/// Raise the error a recipe raises.
pub fn fail<T>(message: impl Into<String>) -> Result<T> {
    bail!(message.into())
}
