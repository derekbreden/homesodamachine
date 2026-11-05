//! Conversions between typed values and the adapter's `Val`, Python-compatible formatting,
//! argument binding for exported functions and calls on opaque Python objects.

use super::Runtime;
use anyhow::{Context, Result, bail, ensure};
pub use hsm_documents::interop::Val;
use hsm_documents::interop::callback;
use serde_json::json;
use std::path::PathBuf;

/// Python's `str(float)`.
pub fn pystr(x: f64) -> String {
    Val::Float(x).str().expect("float text")
}
/// A float formatted with a Python format specification, as an f-string writes it.
pub fn ff(x: f64, spec: &str) -> String {
    hsm_documents::interop::format(&Val::Float(x), spec).expect("format specification")
}
/// An int formatted with a Python format specification.
pub fn fi(x: i64, spec: &str) -> String {
    hsm_documents::interop::format(&Val::Int(x), spec).expect("format specification")
}
/// Any value formatted as an f-string replacement field writes it.
pub fn fv(x: &Val, spec: &str) -> Result<String> {
    hsm_documents::interop::format(x, spec)
}
/// Python's `round(x, digits)`.
pub fn round_to(x: f64, digits: i32) -> f64 {
    if digits >= 0 {
        hsm_documents::format_number(x, &format!(".{digits}f"))
            .expect("round")
            .parse()
            .expect("rounded number")
    } else {
        let scale = 10f64.powi(-digits);
        (x / scale).round_ties_even() * scale
    }
}
/// Python's `round(x)`.
pub fn round_int(x: f64) -> i64 {
    x.round_ties_even() as i64
}
/// Python's `%` on floats: the result takes the divisor's sign.
pub fn pymod(a: f64, b: f64) -> f64 {
    let r = a % b;
    if r != 0. && (r < 0.) != (b < 0.) { r + b } else { r }
}
/// `math.dist`.
pub fn dist(a: &[f64], b: &[f64]) -> f64 {
    let mut n = 0f64;
    for (a, b) in a.iter().zip(b) {
        n = n.hypot(a - b);
    }
    n
}
/// `math.hypot(*values)`, folded the way the runtime folds it.
pub fn hypot(values: &[f64]) -> f64 {
    values.iter().fold(0f64, |a, &b| a.hypot(b))
}
/// `math.radians` and `math.degrees`, as the runtime computes them.
pub fn radians(x: f64) -> f64 {
    x * std::f64::consts::PI / 180.
}
pub fn degrees(x: f64) -> f64 {
    x * 180. / std::f64::consts::PI
}
/// `math.isclose` with the default tolerances.
pub fn isclose(a: f64, b: f64) -> bool {
    (a - b).abs() <= 0f64.max(1e-9 * a.abs().max(b.abs()))
}
/// Python's `sum` of floats: left to right from the integer zero.
pub fn fsum(values: impl IntoIterator<Item = f64>) -> f64 {
    let mut total = 0f64;
    for value in values {
        total += value;
    }
    total
}
pub fn fmin(values: impl IntoIterator<Item = f64>) -> f64 {
    let mut it = values.into_iter();
    let mut best = it.next().expect("min of an empty sequence");
    for v in it {
        if v < best {
            best = v;
        }
    }
    best
}
pub fn fmax(values: impl IntoIterator<Item = f64>) -> f64 {
    let mut it = values.into_iter();
    let mut best = it.next().expect("max of an empty sequence");
    for v in it {
        if v > best {
            best = v;
        }
    }
    best
}
pub fn pmin(a: f64, b: f64) -> f64 {
    if b < a { b } else { a }
}
pub fn pmax(a: f64, b: f64) -> f64 {
    if b > a { b } else { a }
}

/// A value Python sees.
pub trait ToVal {
    fn to_val(&self) -> Val;
}
impl ToVal for Val {
    fn to_val(&self) -> Val {
        self.clone()
    }
}
impl ToVal for f64 {
    fn to_val(&self) -> Val {
        Val::Float(*self)
    }
}
impl ToVal for i64 {
    fn to_val(&self) -> Val {
        Val::Int(*self)
    }
}
impl ToVal for i32 {
    fn to_val(&self) -> Val {
        Val::Int(*self as i64)
    }
}
impl ToVal for usize {
    fn to_val(&self) -> Val {
        Val::Int(*self as i64)
    }
}
impl ToVal for bool {
    fn to_val(&self) -> Val {
        Val::Bool(*self)
    }
}
impl ToVal for str {
    fn to_val(&self) -> Val {
        Val::Str(self.into())
    }
}
impl ToVal for String {
    fn to_val(&self) -> Val {
        Val::Str(self.clone())
    }
}
impl ToVal for PathBuf {
    fn to_val(&self) -> Val {
        Val::Path(self.clone())
    }
}
impl<T: ToVal> ToVal for Option<T> {
    fn to_val(&self) -> Val {
        self.as_ref().map_or(Val::None, ToVal::to_val)
    }
}
impl<T: ToVal> ToVal for Vec<T> {
    fn to_val(&self) -> Val {
        Val::list(self.iter().map(ToVal::to_val).collect())
    }
}
impl<T: ToVal, const N: usize> ToVal for [T; N] {
    fn to_val(&self) -> Val {
        Val::Tuple(self.iter().map(ToVal::to_val).collect())
    }
}
impl<T: ToVal + ?Sized> ToVal for &T {
    fn to_val(&self) -> Val {
        (**self).to_val()
    }
}
macro_rules! tuple_to_val {
    ($($n:ident),+) => {
        impl<$($n: ToVal),+> ToVal for ($($n,)+) {
            #[allow(non_snake_case)]
            fn to_val(&self) -> Val {
                let ($($n,)+) = self;
                Val::Tuple(vec![$($n.to_val()),+])
            }
        }
    };
}
tuple_to_val!(A);
tuple_to_val!(A, B);
tuple_to_val!(A, B, C);
tuple_to_val!(A, B, C, D);
tuple_to_val!(A, B, C, D, E);
tuple_to_val!(A, B, C, D, E, F);

/// A Python tuple of any length.
pub struct Tuple<T>(pub Vec<T>);
impl<T: ToVal> ToVal for Tuple<T> {
    fn to_val(&self) -> Val {
        Val::Tuple(self.0.iter().map(ToVal::to_val).collect())
    }
}
pub fn tuple<T: ToVal>(values: &[T]) -> Val {
    Val::Tuple(values.iter().map(ToVal::to_val).collect())
}
pub fn list<T: ToVal>(values: &[T]) -> Val {
    Val::list(values.iter().map(ToVal::to_val).collect())
}

/// An insertion-ordered dict with string keys, built from typed values.
#[derive(Default, Clone)]
pub struct Dict(pub Vec<(Val, Val)>);
impl Dict {
    pub fn new() -> Self {
        Self(vec![])
    }
    pub fn set(&mut self, key: impl ToVal, value: impl ToVal) -> &mut Self {
        let key = key.to_val();
        let value = value.to_val();
        if let Some(row) = self
            .0
            .iter_mut()
            .find(|(k, _)| hsm_documents::interop::eq(k, &key).unwrap_or(false))
        {
            row.1 = value;
        } else {
            self.0.push((key, value));
        }
        self
    }
    pub fn with(mut self, key: impl ToVal, value: impl ToVal) -> Self {
        self.set(key, value);
        self
    }
    pub fn val(&self) -> Val {
        Val::dict(self.0.clone())
    }
}
impl ToVal for Dict {
    fn to_val(&self) -> Val {
        self.val()
    }
}
/// `dict![key => value, ...]` builds an ordered dict of typed values.
#[macro_export]
macro_rules! dict {
    ($($k:expr => $v:expr),* $(,)?) => {{
        #[allow(unused_mut)]
        let mut d = $crate::recipes::Dict::new();
        $( d.set($k, $v); )*
        d.val()
    }};
}
/// `args![a, b, ...]`: positional arguments for a Python call.
#[macro_export]
macro_rules! args {
    ($($v:expr),* $(,)?) => { vec![$($crate::recipes::ToVal::to_val(&$v)),*] };
}
/// `kw![name => value, ...]`: keyword arguments for a Python call.
#[macro_export]
macro_rules! kw {
    ($($k:expr => $v:expr),* $(,)?) => {
        vec![$((String::from($k), $crate::recipes::ToVal::to_val(&$v))),*]
    };
}

/// Read a typed value from a Python value.
pub trait FromVal: Sized {
    fn from_val(v: &Val) -> Result<Self>;
}
impl FromVal for Val {
    fn from_val(v: &Val) -> Result<Self> {
        Ok(v.clone())
    }
}
impl FromVal for f64 {
    fn from_val(v: &Val) -> Result<Self> {
        v.num()
    }
}
impl FromVal for i64 {
    fn from_val(v: &Val) -> Result<Self> {
        match v {
            Val::Int(n) => Ok(*n),
            Val::Bool(b) => Ok(i64::from(*b)),
            Val::Ref(_) => v.integer(),
            _ => bail!("expected an integer, got {}", v.repr()?),
        }
    }
}
impl FromVal for bool {
    fn from_val(v: &Val) -> Result<Self> {
        v.truthy()
    }
}
impl FromVal for String {
    fn from_val(v: &Val) -> Result<Self> {
        match v {
            Val::Str(s) => Ok(s.clone()),
            _ => v.str(),
        }
    }
}
impl FromVal for PathBuf {
    fn from_val(v: &Val) -> Result<Self> {
        match v {
            Val::Path(p) => Ok(p.clone()),
            _ => Ok(PathBuf::from(v.str()?)),
        }
    }
}
impl<T: FromVal> FromVal for Vec<T> {
    fn from_val(v: &Val) -> Result<Self> {
        own(v)?.iter()?.iter().map(T::from_val).collect()
    }
}
impl<T: FromVal> FromVal for Option<T> {
    fn from_val(v: &Val) -> Result<Self> {
        if matches!(v, Val::None) {
            Ok(None)
        } else {
            T::from_val(v).map(Some)
        }
    }
}
impl<const N: usize> FromVal for [f64; N] {
    fn from_val(v: &Val) -> Result<Self> {
        let items = own(v)?.iter()?;
        ensure!(items.len() == N, "expected {N} numbers, got {}", items.len());
        let mut out = [0.; N];
        for (slot, item) in out.iter_mut().zip(&items) {
            *slot = item.num()?;
        }
        Ok(out)
    }
}
macro_rules! tuple_from_val {
    ($len:expr; $($n:ident $i:tt),+) => {
        impl<$($n: FromVal),+> FromVal for ($($n,)+) {
            fn from_val(v: &Val) -> Result<Self> {
                let items = own(v)?.iter()?;
                ensure!(items.len() == $len, "expected {} values, got {}", $len, items.len());
                Ok(($($n::from_val(&items[$i])?,)+))
            }
        }
    };
}
tuple_from_val!(2; A 0, B 1);
tuple_from_val!(3; A 0, B 1, C 2);
tuple_from_val!(4; A 0, B 1, C 2, D 3);
tuple_from_val!(5; A 0, B 1, C 2, D 3, E 4);

/// A Python container by value: a reference into the Python process is copied once.
pub fn own(v: &Val) -> Result<Val> {
    if let Val::Ref(_) = v {
        Val::decode(callback(
            json!({"op":"snapshot","object":v.encode()?}),
        )?)
    } else {
        Ok(v.clone())
    }
}

/// Calls and reads on a Python object, a compiled value or an owned container.
pub trait Obj {
    fn a(&self, name: &str) -> Result<Val>;
    fn m(&self, name: &str, args: Vec<Val>) -> Result<Val>;
    fn mk(&self, name: &str, args: Vec<Val>, kwargs: Vec<(String, Val)>) -> Result<Val>;
    fn c(&self, args: Vec<Val>) -> Result<Val>;
    fn ck(&self, args: Vec<Val>, kwargs: Vec<(String, Val)>) -> Result<Val>;
    /// `value[key]` for a string key.
    fn k(&self, key: &str) -> Result<Val>;
    /// `value[index]`.
    fn i(&self, index: i64) -> Result<Val>;
    fn kf(&self, key: &str) -> Result<f64>;
    fn ks(&self, key: &str) -> Result<String>;
    fn f(&self) -> Result<f64>;
    fn s(&self) -> Result<String>;
    fn v2(&self) -> Result<[f64; 2]>;
    fn v3(&self) -> Result<[f64; 3]>;
    fn kv3(&self, key: &str) -> Result<[f64; 3]>;
    fn kv2(&self, key: &str) -> Result<[f64; 2]>;
    fn get_opt(&self, key: &str) -> Result<Option<Val>>;
    fn items(&self) -> Result<Vec<(Val, Val)>>;
    fn list(&self) -> Result<Vec<Val>>;
    fn floats(&self) -> Result<Vec<f64>>;
    fn has(&self, key: &str) -> Result<bool>;
}
impl Obj for Val {
    fn a(&self, name: &str) -> Result<Val> {
        self.attr(name)
    }
    fn m(&self, name: &str, args: Vec<Val>) -> Result<Val> {
        self.attr(name)?.call(args, vec![])
    }
    fn mk(&self, name: &str, args: Vec<Val>, kwargs: Vec<(String, Val)>) -> Result<Val> {
        self.attr(name)?.call(args, kwargs)
    }
    fn c(&self, args: Vec<Val>) -> Result<Val> {
        self.call(args, vec![])
    }
    fn ck(&self, args: Vec<Val>, kwargs: Vec<(String, Val)>) -> Result<Val> {
        self.call(args, kwargs)
    }
    fn k(&self, key: &str) -> Result<Val> {
        self.get(Val::Str(key.into()))
            .with_context(|| format!("key {key}"))
    }
    fn i(&self, index: i64) -> Result<Val> {
        self.get(Val::Int(index))
    }
    fn kf(&self, key: &str) -> Result<f64> {
        self.k(key)?.num().with_context(|| format!("number {key}"))
    }
    fn ks(&self, key: &str) -> Result<String> {
        self.k(key)?.str()
    }
    fn f(&self) -> Result<f64> {
        self.num()
    }
    fn s(&self) -> Result<String> {
        self.str()
    }
    fn v2(&self) -> Result<[f64; 2]> {
        <[f64; 2]>::from_val(self)
    }
    fn v3(&self) -> Result<[f64; 3]> {
        <[f64; 3]>::from_val(self)
    }
    fn kv3(&self, key: &str) -> Result<[f64; 3]> {
        self.k(key)?.v3().with_context(|| format!("point {key}"))
    }
    fn kv2(&self, key: &str) -> Result<[f64; 2]> {
        self.k(key)?.v2().with_context(|| format!("pair {key}"))
    }
    fn get_opt(&self, key: &str) -> Result<Option<Val>> {
        let owned = own(self)?;
        for (k, v) in hsm_documents::interop::entries_of(&owned)? {
            if matches!(&k, Val::Str(s) if s == key) {
                return Ok(Some(v));
            }
        }
        Ok(None)
    }
    fn items(&self) -> Result<Vec<(Val, Val)>> {
        hsm_documents::interop::entries_of(&own(self)?)
    }
    fn list(&self) -> Result<Vec<Val>> {
        own(self)?.iter()
    }
    fn floats(&self) -> Result<Vec<f64>> {
        own(self)?.iter()?.iter().map(Val::num).collect()
    }
    fn has(&self, key: &str) -> Result<bool> {
        Ok(self.get_opt(key)?.is_some())
    }
}

/// Bind one call's arguments the way a Python signature does.
pub struct Call {
    args: Vec<Option<Val>>,
    kwargs: Vec<(String, Val)>,
}
impl Call {
    pub fn new(args: Vec<Val>, kwargs: Vec<(String, Val)>) -> Self {
        Self {
            args: args.into_iter().map(Some).collect(),
            kwargs,
        }
    }
    /// The parameter at `index` (positionally) or named `name`.
    pub fn take(&mut self, index: usize, name: &str) -> Result<Option<Val>> {
        let positional = self.args.get_mut(index).and_then(Option::take);
        let keyword = self
            .kwargs
            .iter()
            .position(|(k, _)| k == name)
            .map(|i| self.kwargs.remove(i).1);
        match (positional, keyword) {
            (Some(_), Some(_)) => bail!("multiple values for argument {name}"),
            (Some(v), None) | (None, Some(v)) => Ok(Some(v)),
            (None, None) => Ok(None),
        }
    }
    pub fn req<T: FromVal>(&mut self, index: usize, name: &str) -> Result<T> {
        let value = self
            .take(index, name)?
            .with_context(|| format!("missing argument {name}"))?;
        T::from_val(&value).with_context(|| format!("argument {name}"))
    }
    pub fn opt<T: FromVal>(&mut self, index: usize, name: &str, default: T) -> Result<T> {
        match self.take(index, name)? {
            Some(value) => T::from_val(&value).with_context(|| format!("argument {name}")),
            None => Ok(default),
        }
    }
    pub fn maybe<T: FromVal>(&mut self, index: usize, name: &str) -> Result<Option<T>> {
        match self.take(index, name)? {
            Some(value) => T::from_val(&value)
                .map(Some)
                .with_context(|| format!("argument {name}")),
            None => Ok(None),
        }
    }
    /// Keyword-only parameter.
    pub fn kw<T: FromVal>(&mut self, name: &str, default: T) -> Result<T> {
        self.opt(usize::MAX, name, default)
    }
    /// The positional arguments not bound, as `*args` receives them.
    pub fn rest(&mut self, from: usize) -> Vec<Val> {
        self.args
            .iter_mut()
            .skip(from)
            .filter_map(Option::take)
            .collect()
    }
    pub fn done(&self) -> Result<()> {
        ensure!(
            self.args.iter().all(Option::is_none),
            "too many positional arguments"
        );
        ensure!(self.kwargs.is_empty(), "unexpected keyword arguments");
        Ok(())
    }
}

/// The members a module shows Python.
#[derive(Default)]
pub struct Namespace(Vec<(Val, Val)>);
impl Namespace {
    pub fn value(&mut self, name: &str, value: impl ToVal) -> &mut Self {
        let key = Val::Str(name.into());
        let value = value.to_val();
        if let Some(row) = self
            .0
            .iter_mut()
            .find(|(k, _)| matches!(k, Val::Str(s) if s == name))
        {
            row.1 = value;
        } else {
            self.0.push((key, value));
        }
        self
    }
    /// An exported function: its arguments are bound like the source signature.
    pub fn func(
        &mut self,
        rt: &Runtime,
        name: &str,
        f: impl Fn(&Runtime, &mut Call) -> Result<Val> + 'static,
    ) -> &mut Self {
        let rt = rt.clone();
        self.value(
            name,
            Val::function(move |args, kwargs| {
                let mut call = Call::new(args, kwargs);
                let value = f(&rt, &mut call)?;
                call.done()?;
                Ok(value)
            }),
        )
    }
    /// A member re-exported from a Python module.
    pub fn python(&mut self, rt: &Runtime, name: &str, module: &str, member: &str) -> Result<()> {
        let value = rt.pya(module, member)?;
        self.value(name, value);
        Ok(())
    }
    pub fn module(&mut self, rt: &Runtime, name: &str, module: &str) -> Result<()> {
        let value = rt.import_module(module)?;
        self.value(name, value);
        Ok(())
    }
    pub fn into_val(self) -> Val {
        Val::namespace(self.0)
    }
}

/// A fixed vector helper set for the 3-component arithmetic the recipes share.
pub fn add3(a: [f64; 3], b: [f64; 3]) -> [f64; 3] {
    [a[0] + b[0], a[1] + b[1], a[2] + b[2]]
}
pub fn sub3(a: [f64; 3], b: [f64; 3]) -> [f64; 3] {
    [a[0] - b[0], a[1] - b[1], a[2] - b[2]]
}
pub fn scale3(a: [f64; 3], k: f64) -> [f64; 3] {
    [a[0] * k, a[1] * k, a[2] * k]
}
pub fn neg3(a: [f64; 3]) -> [f64; 3] {
    [-a[0], -a[1], -a[2]]
}
/// Python's `sum(x * y for x, y in zip(a, b))`.
pub fn dot3(a: [f64; 3], b: [f64; 3]) -> f64 {
    0. + a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
}
pub fn cross3(a: [f64; 3], b: [f64; 3]) -> [f64; 3] {
    [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]
}
pub fn xy(p: [f64; 3]) -> [f64; 2] {
    [p[0], p[1]]
}
pub fn xyz(p: [f64; 2], z: f64) -> [f64; 3] {
    [p[0], p[1], z]
}
pub fn vals(values: &[f64]) -> Val {
    Val::Tuple(values.iter().map(|v| Val::Float(*v)).collect())
}
pub fn fail<T>(message: String) -> Result<T> {
    bail!("{message}")
}

/// `Path.resolve()`, as the runtime resolves a path: the canonical path, or the absolute path
/// with `.` and `..` folded when the file is missing.
pub fn resolve(path: &std::path::Path) -> PathBuf {
    if let Ok(found) = std::fs::canonicalize(path) {
        return found;
    }
    let absolute = if path.is_absolute() {
        path.to_owned()
    } else {
        std::env::current_dir().unwrap_or_default().join(path)
    };
    let mut clean = PathBuf::new();
    for component in absolute.components() {
        match component {
            std::path::Component::ParentDir => {
                clean.pop();
            }
            std::path::Component::CurDir => (),
            component => clean.push(component.as_os_str()),
        }
    }
    clean
}
/// `next(p for p in path.parents if p.name == name)`.
pub fn ancestor(path: &std::path::Path, name: &str) -> Result<PathBuf> {
    path.ancestors()
        .skip(1)
        .find(|p| p.file_name().is_some_and(|n| n == name))
        .map(std::path::Path::to_owned)
        .with_context(|| format!("no {name} above {}", path.display()))
}
/// `next(p for p in path.parents if test(p))`.
pub fn ancestor_where(
    path: &std::path::Path,
    test: impl Fn(&std::path::Path) -> bool,
) -> Result<PathBuf> {
    path.ancestors()
        .skip(1)
        .find(|p| test(p))
        .map(std::path::Path::to_owned)
        .with_context(|| format!("no matching directory above {}", path.display()))
}
/// `path.parents[n]`.
pub fn parent_n(path: &std::path::Path, n: usize) -> PathBuf {
    path.ancestors().nth(n + 1).unwrap_or(path).to_owned()
}
/// `str(path)`.
pub fn ps(path: &std::path::Path) -> String {
    path.to_string_lossy().into_owned()
}
/// `Path.read_text()`, registered as a read.
pub fn read_text(path: &std::path::Path) -> Result<String> {
    hsm_documents::interop::note_io(path, false);
    Ok(std::fs::read_to_string(path)
        .with_context(|| format!("read {}", path.display()))?
        .replace("\r\n", "\n")
        .replace('\r', "\n"))
}
/// `Path.write_text(text)`, registered as a write.
pub fn write_text(path: &std::path::Path, text: &str) -> Result<()> {
    std::fs::write(path, text).with_context(|| format!("write {}", path.display()))?;
    hsm_documents::interop::note_io(path, true);
    Ok(())
}
/// `json.loads(text)` as the runtime decodes it.
pub fn json_loads(text: &str) -> Result<Val> {
    hsm_documents::interop::builtin_module("json")
        .context("json module")?
        .attr("loads")?
        .call(vec![Val::Str(text.into())], vec![])
}
/// `json.dumps(value, **kwargs)` as the runtime writes it.
pub fn json_dumps(value: &Val, kwargs: Vec<(String, Val)>) -> Result<String> {
    hsm_documents::interop::builtin_module("json")
        .context("json module")?
        .attr("dumps")?
        .call(vec![value.clone()], kwargs)?
        .str()
}

/// A Python number whose `int`-ness reaches an output: `int` stays `int` through `+ - *`,
/// `min` and `max` keep the operand they pick.
#[derive(Clone, Copy, Debug)]
pub enum Num {
    I(i64),
    F(f64),
}
impl Num {
    pub fn f(self) -> f64 {
        match self {
            Num::I(i) => i as f64,
            Num::F(x) => x,
        }
    }
    pub fn add(self, o: impl Into<Num>) -> Num {
        match (self, o.into()) {
            (Num::I(a), Num::I(b)) => Num::I(a + b),
            (a, b) => Num::F(a.f() + b.f()),
        }
    }
    pub fn sub(self, o: impl Into<Num>) -> Num {
        match (self, o.into()) {
            (Num::I(a), Num::I(b)) => Num::I(a - b),
            (a, b) => Num::F(a.f() - b.f()),
        }
    }
    pub fn mul(self, o: impl Into<Num>) -> Num {
        match (self, o.into()) {
            (Num::I(a), Num::I(b)) => Num::I(a * b),
            (a, b) => Num::F(a.f() * b.f()),
        }
    }
    pub fn neg(self) -> Num {
        match self {
            Num::I(a) => Num::I(-a),
            Num::F(a) => Num::F(-a),
        }
    }
    /// `min(self, o)`: `o` only when it is smaller.
    pub fn min(self, o: impl Into<Num>) -> Num {
        let o = o.into();
        if o.f() < self.f() { o } else { self }
    }
    /// `max(self, o)`: `o` only when it is greater.
    pub fn max(self, o: impl Into<Num>) -> Num {
        let o = o.into();
        if o.f() > self.f() { o } else { self }
    }
}
impl From<f64> for Num {
    fn from(x: f64) -> Self {
        Num::F(x)
    }
}
impl From<i64> for Num {
    fn from(x: i64) -> Self {
        Num::I(x)
    }
}
impl ToVal for Num {
    fn to_val(&self) -> Val {
        match self {
            Num::I(i) => Val::Int(*i),
            Num::F(x) => Val::Float(*x),
        }
    }
}
impl FromVal for Num {
    fn from_val(v: &Val) -> Result<Self> {
        Ok(match v {
            Val::Int(i) => Num::I(*i),
            Val::Bool(b) => Num::I(i64::from(*b)),
            Val::Float(x) => Num::F(*x),
            _ => Num::F(v.num()?),
        })
    }
}
impl<const N: usize> FromVal for [Num; N] {
    fn from_val(v: &Val) -> Result<Self> {
        let items = own(v)?.iter()?;
        ensure!(items.len() == N, "expected {N} numbers, got {}", items.len());
        let mut out = [Num::I(0); N];
        for (slot, item) in out.iter_mut().zip(&items) {
            *slot = Num::from_val(item)?;
        }
        Ok(out)
    }
}
pub fn fnum(values: &[f64]) -> Vec<Num> {
    values.iter().map(|&x| Num::F(x)).collect()
}

/// An insertion-ordered map, as a Python dict keeps its keys.
#[derive(Clone, Debug)]
pub struct OMap<V>(pub Vec<(String, V)>);
impl<V> Default for OMap<V> {
    fn default() -> Self {
        Self(vec![])
    }
}
impl<V: Clone> OMap<V> {
    pub fn new() -> Self {
        Self(vec![])
    }
    pub fn set(&mut self, key: &str, value: V) {
        if let Some(row) = self.0.iter_mut().find(|(k, _)| k == key) {
            row.1 = value;
        } else {
            self.0.push((key.to_owned(), value));
        }
    }
    pub fn get(&self, key: &str) -> Option<&V> {
        self.0.iter().find(|(k, _)| k == key).map(|(_, v)| v)
    }
    /// `d[key]`, with Python's KeyError.
    pub fn at(&self, key: &str) -> Result<&V> {
        self.get(key).with_context(|| format!("KeyError: {key:?}"))
    }
    pub fn keys(&self) -> impl Iterator<Item = &str> {
        self.0.iter().map(|(k, _)| k.as_str())
    }
    pub fn iter(&self) -> impl Iterator<Item = (&str, &V)> {
        self.0.iter().map(|(k, v)| (k.as_str(), v))
    }
    pub fn values(&self) -> impl Iterator<Item = &V> {
        self.0.iter().map(|(_, v)| v)
    }
    pub fn len(&self) -> usize {
        self.0.len()
    }
    pub fn is_empty(&self) -> bool {
        self.0.is_empty()
    }
}
impl<V: ToVal> ToVal for OMap<V> {
    fn to_val(&self) -> Val {
        Val::dict(
            self.0
                .iter()
                .map(|(k, v)| (Val::Str(k.clone()), v.to_val()))
                .collect(),
        )
    }
}
/// Python's `str(list_of_str)`.
pub fn repr_strs<'a>(items: impl IntoIterator<Item = &'a str>) -> String {
    let parts: Vec<String> = items
        .into_iter()
        .map(|s| Val::Str(s.to_owned()).repr().expect("repr"))
        .collect();
    format!("[{}]", parts.join(", "))
}

/// `with <context> as <entered>:` as the generated guide runtime runs it: `__exit__(None,
/// None, None)` follows the body whether or not the body failed, then its error propagates.
pub fn with<T>(context: &Val, body: impl FnOnce(Val) -> Result<T>) -> Result<T> {
    let entered = context.attr("__enter__")?.call(vec![], vec![])?;
    let result = body(entered);
    context
        .attr("__exit__")?
        .call(vec![Val::None, Val::None, Val::None], vec![])?;
    result
}
