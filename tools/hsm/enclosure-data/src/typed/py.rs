//! Values at the Python boundary: argument binding, conversions and provider objects.
use anyhow::{Context, Result, bail, ensure};
pub use hsm_documents::interop::{Args, Kwargs, Val};
use hsm_documents::interop::{builtin_module, callback};
use serde_json::{Value, json};
use std::path::{Path, PathBuf};

/// Python's binding of positional and keyword arguments to named parameters.
/// `positional` names may arrive either way; `keyword` names only by keyword.
pub struct Bound {
    values: Vec<Option<Val>>,
    names: Vec<&'static str>,
}

pub fn bind(args: Args, mut kwargs: Kwargs, positional: &[&'static str], keyword: &[&'static str]) -> Result<Bound> {
    ensure!(args.len() <= positional.len(), "too many positional arguments");
    let mut values: Vec<Option<Val>> = Vec::with_capacity(positional.len() + keyword.len());
    let mut args = args.into_iter();
    for name in positional {
        let given = args.next();
        let named = kwargs.iter().position(|(key, _)| key == name).map(|i| kwargs.remove(i).1);
        ensure!(!(given.is_some() && named.is_some()), "multiple arguments for {name}");
        values.push(given.or(named));
    }
    for name in keyword {
        values.push(kwargs.iter().position(|(key, _)| key == name).map(|i| kwargs.remove(i).1));
    }
    ensure!(kwargs.is_empty(), "unexpected keyword arguments {:?}", kwargs.iter().map(|(k, _)| k).collect::<Vec<_>>());
    Ok(Bound { values, names: positional.iter().chain(keyword).copied().collect() })
}

impl Bound {
    fn index(&self, name: &str) -> usize {
        self.names.iter().position(|n| *n == name).unwrap_or_else(|| panic!("parameter {name} is not bound"))
    }
    /// A required parameter.
    pub fn req(&mut self, name: &str) -> Result<Val> {
        let i = self.index(name);
        self.values[i].take().with_context(|| format!("missing argument {name}"))
    }
    /// An optional parameter; `None` where the caller left it out.
    pub fn opt(&mut self, name: &str) -> Option<Val> {
        let i = self.index(name);
        self.values[i].take()
    }
    /// An optional parameter whose omission and explicit `None` read the same.
    pub fn some(&mut self, name: &str) -> Option<Val> {
        self.opt(name).filter(|v| !matches!(v, Val::None))
    }
    pub fn f64(&mut self, name: &str) -> Result<f64> {
        self.req(name)?.num()
    }
    pub fn f64_or(&mut self, name: &str, default: f64) -> Result<f64> {
        self.opt(name).map(|v| v.num()).transpose().map(|v| v.unwrap_or(default))
    }
    pub fn string(&mut self, name: &str) -> Result<String> {
        self.req(name)?.str()
    }
    pub fn string_or(&mut self, name: &str, default: &str) -> Result<String> {
        self.opt(name).map(|v| v.str()).transpose().map(|v| v.unwrap_or_else(|| default.to_owned()))
    }
    pub fn bool_or(&mut self, name: &str, default: bool) -> Result<bool> {
        self.opt(name).map(|v| v.truthy()).transpose().map(|v| v.unwrap_or(default))
    }
}

pub fn call(f: &Val, args: Args) -> Result<Val> {
    f.call(args, vec![])
}
pub fn call_kw(f: &Val, args: Args, kwargs: Vec<(&str, Val)>) -> Result<Val> {
    f.call(args, kwargs.into_iter().map(|(k, v)| (k.to_owned(), v)).collect())
}
pub fn method(object: &Val, name: &str, args: Args) -> Result<Val> {
    object.attr(name)?.call(args, vec![])
}
pub fn item(object: &Val, key: impl Into<Val>) -> Result<Val> {
    object.get(key.into())
}

/// A provider value copied into local containers in one callback; local values return as they are.
/// Opaque leaves (library objects) stay references.
pub fn snapshot(value: &Val) -> Result<Val> {
    if !matches!(value, Val::Ref(_)) {
        return Ok(value.clone());
    }
    Val::decode(callback(json!({"op": "snapshot", "object": value.encode()?}))?)
}

/// A local value as plain JSON: tuples and lists as arrays, dicts and namespaces as objects.
pub fn plain(v: &Val) -> Result<Value> {
    Ok(match v {
        Val::None => Value::Null,
        Val::Bool(b) => json!(b),
        Val::Int(i) => json!(i),
        Val::Float(f) => json!(f),
        Val::Str(s) => json!(s),
        Val::Path(p) => json!(p.to_string_lossy()),
        Val::Tuple(rows) | Val::FrozenSet(rows) => Value::Array(rows.iter().map(plain).collect::<Result<_>>()?),
        Val::List(rows) | Val::Set(rows) => Value::Array(rows.borrow().iter().map(plain).collect::<Result<_>>()?),
        Val::Dict(rows) | Val::Namespace(rows) => Value::Object(
            rows.borrow().iter().map(|(k, v)| Ok((k.str()?, plain(v)?))).collect::<Result<_>>()?,
        ),
        Val::Ref(_) => plain(&snapshot(v)?)?,
        _ => bail!("not plain data: {}", v.repr()?),
    })
}

pub fn f64s(v: &Val) -> Result<Vec<f64>> {
    v.iter()?.iter().map(Val::num).collect()
}
pub fn v3(v: &Val) -> Result<[f64; 3]> {
    let r = f64s(v)?;
    ensure!(r.len() == 3, "expected three coordinates, got {}", r.len());
    Ok([r[0], r[1], r[2]])
}
pub fn v2(v: &Val) -> Result<[f64; 2]> {
    let r = f64s(v)?;
    ensure!(r.len() == 2, "expected two coordinates, got {}", r.len());
    Ok([r[0], r[1]])
}
pub fn strings(v: &Val) -> Result<Vec<String>> {
    v.iter()?.iter().map(Val::str).collect()
}
pub fn path(v: &Val) -> Result<PathBuf> {
    Ok(match v {
        Val::Path(p) => p.clone(),
        _ => PathBuf::from(v.str()?),
    })
}

pub fn tuple<T: Into<Val>>(values: impl IntoIterator<Item = T>) -> Val {
    Val::Tuple(values.into_iter().map(Into::into).collect())
}
pub fn list<T: Into<Val>>(values: impl IntoIterator<Item = T>) -> Val {
    Val::list(values.into_iter().map(Into::into).collect())
}
pub fn ftuple(values: &[f64]) -> Val {
    Val::Tuple(values.iter().map(|&v| Val::Float(v)).collect())
}
pub fn flist(values: &[f64]) -> Val {
    Val::list(values.iter().map(|&v| Val::Float(v)).collect())
}
/// A dict with string keys, in the given order.
pub fn dict<K: Into<String>>(rows: impl IntoIterator<Item = (K, Val)>) -> Val {
    Val::dict(rows.into_iter().map(|(k, v)| (Val::Str(k.into()), v)).collect())
}
/// A module's `__doc__`.
pub fn doc(text: Option<&str>) -> Val {
    text.map_or(Val::None, |t| Val::Str(t.into()))
}
pub fn s(text: impl Into<String>) -> Val {
    Val::Str(text.into())
}
/// A JSON array of strings.
pub fn json_strings(value: &Value) -> Result<Vec<String>> {
    value.as_array().context("a JSON list of names")?.iter()
        .map(|v| v.as_str().map(str::to_owned).context("a JSON name"))
        .collect()
}
/// A JSON value as the containers Python's json.loads makes: lists and string-keyed dicts.
pub fn from_json(value: Value) -> Result<Val> {
    Ok(match value {
        Value::Array(rows) => Val::list(rows.into_iter().map(from_json).collect::<Result<_>>()?),
        Value::Object(rows) => Val::dict(rows.into_iter().map(|(k, v)| Ok((Val::Str(k), from_json(v)?))).collect::<Result<_>>()?),
        other => Val::decode(other)?,
    })
}

/// `value.get(key, default)` as Python's mapping method.
pub fn dget(value: &Val, key: &str, default: Val) -> Result<Val> {
    method(value, "get", vec![s(key), default])
}
/// `value[key]` with a string key.
pub fn at(value: &Val, key: &str) -> Result<Val> {
    value.get(Val::Str(key.into()))
}

fn json() -> Val {
    builtin_module("json").expect("the runtime's json module")
}
/// `json.loads(text)`: dicts keep the document's key order.
pub fn json_loads(text: &str) -> Result<Val> {
    json().attr("loads")?.call(vec![s(text)], vec![])
}
/// `json.dumps(value, **kwargs)`.
pub fn json_dumps(value: &Val, kwargs: Vec<(&str, Val)>) -> Result<String> {
    call_kw(&json().attr("dumps")?, vec![value.clone()], kwargs)?.str()
}

fn path_method(path: &Path, name: &str, args: Args, kwargs: Vec<(&str, Val)>) -> Result<Val> {
    call_kw(&Val::Path(path.to_owned()).attr(name)?, args, kwargs)
}
/// `Path(p).resolve()`.
pub fn resolve(path: &Path) -> Result<PathBuf> {
    match path_method(path, "resolve", vec![], vec![])? {
        Val::Path(p) => Ok(p),
        other => bail!("resolve gave {}", other.repr()?),
    }
}
/// `path.mkdir(parents=True, exist_ok=True)`.
pub fn mkdirs(path: &Path) -> Result<()> {
    path_method(path, "mkdir", vec![], vec![("parents", Val::Bool(true)), ("exist_ok", Val::Bool(true))])?;
    Ok(())
}
/// `path.read_text()`, recorded as a read.
pub fn read_text(path: &Path) -> Result<String> {
    path_method(path, "read_text", vec![], vec![])?.str()
}
/// `str(path)`.
pub fn path_str(path: &Path) -> String {
    path.to_string_lossy().into_owned()
}

/// `{**base, key: value, ...}`.
pub fn merged(base: &Val, rows: impl IntoIterator<Item = (&'static str, Val)>) -> Result<Val> {
    let out = Val::dict(vec![]);
    for key in base.iter()? {
        out.set(key.clone(), base.get(key)?)?;
    }
    for (key, value) in rows {
        out.set(s(key), value)?;
    }
    Ok(out)
}
/// `dict(value)`.
pub fn dict_of(value: &Val) -> Result<Val> {
    let out = Val::dict(vec![]);
    for key in value.iter()? {
        out.set(key.clone(), value.get(key)?)?;
    }
    Ok(out)
}

/// `sys.path.insert(0, text)` on the interpreter's own module search path.
pub fn sys_path_insert(rt: &super::rt::Rt, text: &str) -> Result<()> {
    method(&rt.import("sys")?.attr("path")?, "insert", vec![Val::Int(0), s(text)])?;
    Ok(())
}
/// `text in sys.path`.
pub fn sys_path_has(rt: &super::rt::Rt, text: &str) -> Result<bool> {
    rt.import("sys")?.attr("path")?.contains(&s(text))
}
/// Unpack a sequence of exactly `n` values.
pub fn unpack(value: &Val, n: usize) -> Result<Vec<Val>> {
    let values = value.iter()?;
    ensure!(values.len() == n, "unpack: expected {n}, got {}", values.len());
    Ok(values)
}
/// `f(*values)`.
pub fn splat(f: &Val, values: &Val) -> Result<Val> {
    f.call(value_list(values)?, vec![])
}
pub fn value_list(values: &Val) -> Result<Vec<Val>> {
    values.iter()
}

/// A typed value's Python form, both ways: how a typed function's parameters and result cross the
/// namespace boundary (a wrapper binding Python arguments, or a call into generated code).
///
/// `f64` accepts an int (as `float(x)` would); a parameter that may receive an int which reaches
/// output (a recorded number, text) is a `Num`. `Vec<T>` is a list and `Tup<T>` a tuple of any
/// length; Rust tuples and `[T; N]` are Python tuples; `Option<T>` is `T` or `None`; `()` is `None`.
pub trait Py: Sized {
    fn to_py(&self) -> Result<Val>;
    fn from_py(value: &Val) -> Result<Self>;
}
/// A Python tuple of any length.
#[derive(Clone, Debug, Default, PartialEq)]
pub struct Tup<T>(pub Vec<T>);

impl Py for Val {
    fn to_py(&self) -> Result<Val> {
        Ok(self.clone())
    }
    fn from_py(value: &Val) -> Result<Self> {
        Ok(value.clone())
    }
}
impl Py for f64 {
    fn to_py(&self) -> Result<Val> {
        Ok(Val::Float(*self))
    }
    fn from_py(value: &Val) -> Result<Self> {
        value.num()
    }
}
impl Py for i64 {
    fn to_py(&self) -> Result<Val> {
        Ok(Val::Int(*self))
    }
    fn from_py(value: &Val) -> Result<Self> {
        match value {
            Val::Int(i) => Ok(*i),
            Val::Bool(b) => Ok(i64::from(*b)),
            _ => bail!("expected an int, got {}", value.repr()?),
        }
    }
}
impl Py for bool {
    fn to_py(&self) -> Result<Val> {
        Ok(Val::Bool(*self))
    }
    fn from_py(value: &Val) -> Result<Self> {
        match value {
            Val::Bool(b) => Ok(*b),
            _ => value.truthy(),
        }
    }
}
impl Py for String {
    fn to_py(&self) -> Result<Val> {
        Ok(Val::Str(self.clone()))
    }
    fn from_py(value: &Val) -> Result<Self> {
        match value {
            Val::Str(s) => Ok(s.clone()),
            _ => bail!("expected a str, got {}", value.repr()?),
        }
    }
}
impl Py for () {
    fn to_py(&self) -> Result<Val> {
        Ok(Val::None)
    }
    fn from_py(_: &Val) -> Result<Self> {
        Ok(())
    }
}
impl Py for super::num::Num {
    fn to_py(&self) -> Result<Val> {
        Ok(Val::from(*self))
    }
    fn from_py(value: &Val) -> Result<Self> {
        super::num::Num::of(value)
    }
}
impl<T: Py> Py for Option<T> {
    fn to_py(&self) -> Result<Val> {
        match self {
            Some(v) => v.to_py(),
            None => Ok(Val::None),
        }
    }
    fn from_py(value: &Val) -> Result<Self> {
        match value {
            Val::None => Ok(None),
            _ => Ok(Some(T::from_py(value)?)),
        }
    }
}
impl<T: Py> Py for Vec<T> {
    fn to_py(&self) -> Result<Val> {
        Ok(Val::list(self.iter().map(Py::to_py).collect::<Result<_>>()?))
    }
    fn from_py(value: &Val) -> Result<Self> {
        value.iter()?.iter().map(T::from_py).collect()
    }
}
impl<T: Py> Py for Tup<T> {
    fn to_py(&self) -> Result<Val> {
        Ok(Val::tuple(self.0.iter().map(Py::to_py).collect::<Result<_>>()?))
    }
    fn from_py(value: &Val) -> Result<Self> {
        Ok(Tup(value.iter()?.iter().map(T::from_py).collect::<Result<_>>()?))
    }
}
impl<T: Py, const N: usize> Py for [T; N] {
    fn to_py(&self) -> Result<Val> {
        Ok(Val::tuple(self.iter().map(Py::to_py).collect::<Result<_>>()?))
    }
    fn from_py(value: &Val) -> Result<Self> {
        let items = value.iter()?;
        ensure!(items.len() == N, "expected {N} values, got {}", items.len());
        let typed = items.iter().map(T::from_py).collect::<Result<Vec<T>>>()?;
        typed.try_into().map_err(|_| anyhow::anyhow!("expected {N} values"))
    }
}
macro_rules! py_tuple {
    ($n:literal; $($t:ident $i:tt),+) => {
        impl<$($t: Py),+> Py for ($($t,)+) {
            fn to_py(&self) -> Result<Val> {
                Ok(Val::tuple(vec![$(self.$i.to_py()?),+]))
            }
            fn from_py(value: &Val) -> Result<Self> {
                let items = value.iter()?;
                ensure!(items.len() == $n, "expected {} values, got {}", $n, items.len());
                Ok(($($t::from_py(&items[$i])?,)+))
            }
        }
    };
}
py_tuple!(1; A 0);
py_tuple!(2; A 0, B 1);
py_tuple!(3; A 0, B 1, C 2);
py_tuple!(4; A 0, B 1, C 2, D 3);
py_tuple!(5; A 0, B 1, C 2, D 3, E 4);
py_tuple!(6; A 0, B 1, C 2, D 3, E 4, F 5);
py_tuple!(7; A 0, B 1, C 2, D 3, E 4, F 5, G 6);
py_tuple!(8; A 0, B 1, C 2, D 3, E 4, F 5, G 6, H 7);
/// The Python form of each value, for a call's positional arguments.
#[macro_export]
macro_rules! py_args {
    ($($v:expr),* $(,)?) => {
        vec![$($crate::typed::py::Py::to_py(&$v)?),*]
    };
}
