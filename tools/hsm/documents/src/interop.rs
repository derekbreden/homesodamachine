//! Values passed by statically compiled document functions and explicit
//! third-party primitive calls. No source-language parser or evaluator runs.
use anyhow::{Context, Result, bail, ensure};
use serde_json::{Value, json};
use std::cell::RefCell;
use std::io::{self, Write};
use std::path::{Path, PathBuf};
use std::rc::Rc;

pub type Args = Vec<Val>;
pub type Kwargs = Vec<(String, Val)>;
pub type Native = Rc<dyn Fn(Args, Kwargs) -> Result<Val>>;
pub type Entries = Rc<RefCell<Vec<(Val, Val)>>>;

#[derive(Clone)]
pub enum Val {
    None,
    Bool(bool),
    Int(i64),
    Float(f64),
    Str(String),
    Bytes(Vec<u8>),
    List(Rc<RefCell<Vec<Val>>>),
    Tuple(Vec<Val>),
    Dict(Entries),
    Set(Rc<RefCell<Vec<Val>>>),
    FrozenSet(Vec<Val>),
    Namespace(Entries),
    Ref(Value),
    Func(Native),
    Path(PathBuf),
    Type(String),
    Slice {
        start: Option<i64>,
        stop: Option<i64>,
        step: i64,
    },
}
impl std::fmt::Debug for Val {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.repr().unwrap_or_else(|_| "<value>".into()))
    }
}
impl Default for Val {
    fn default() -> Self {
        Self::None
    }
}
impl From<&str> for Val {
    fn from(v: &str) -> Self {
        Self::Str(v.into())
    }
}
impl From<String> for Val {
    fn from(v: String) -> Self {
        Self::Str(v)
    }
}
impl From<f64> for Val {
    fn from(v: f64) -> Self {
        Self::Float(v)
    }
}
impl From<i64> for Val {
    fn from(v: i64) -> Self {
        Self::Int(v)
    }
}
impl From<usize> for Val {
    fn from(v: usize) -> Self {
        Self::Int(v as i64)
    }
}
impl From<bool> for Val {
    fn from(v: bool) -> Self {
        Self::Bool(v)
    }
}

type Dispatcher = fn(Value) -> Result<Value>;
thread_local! {
    static DISPATCH: RefCell<Option<Dispatcher>> = const {RefCell::new(None)};
}

/// A primitive may call a compiled closure before it returns. Dispatch those
/// nested calls in this process, retaining its module and object identities.
pub fn set_dispatch(dispatch: Dispatcher) {
    DISPATCH.with(|held| *held.borrow_mut() = Some(dispatch));
}

pub fn callback(query: Value) -> Result<Value> {
    let dispatch = DISPATCH.with(|held| *held.borrow());
    let mut stdout = io::stdout().lock();
    writeln!(
        stdout,
        "{}",
        json!({"_hsm_callback":query,"_hsm_reentrant":dispatch.is_some()})
    )?;
    stdout.flush()?;
    drop(stdout);
    loop {
        let mut line = String::new();
        ensure!(
            io::stdin().read_line(&mut line)? > 0,
            "primitive callback closed its response stream"
        );
        let reply: Value = serde_json::from_str(&line)?;
        if let Some(request) = reply.get("_hsm_request") {
            let result =
                dispatch.context("this program has no nested dispatcher")?(request.clone());
            let value = match result {
                Ok(value) => value,
                Err(error) => json!({"error":format!("{error:#}")}),
            };
            println!("{}", json!({"_hsm_nested_result":value}));
            io::stdout().flush()?;
            continue;
        }
        if let Some(error) = reply.get("_hsm_callback_error") {
            bail!("{}", error.as_str().unwrap_or("primitive callback failed"));
        }
        return reply
            .get("_hsm_callback_result")
            .cloned()
            .context("missing primitive callback result");
    }
}
fn remote(op: &str, object: &Val, fields: Value) -> Result<Val> {
    let mut query = fields.as_object().cloned().unwrap_or_default();
    query.insert("op".into(), json!(op));
    query.insert("object".into(), object.encode()?);
    Val::decode(callback(Value::Object(query))?)
}
fn key_index(entries: &[(Val, Val)], key: &Val) -> Result<Option<usize>> {
    for (i, (held, _)) in entries.iter().enumerate() {
        if eq(held, key)? {
            return Ok(Some(i));
        }
    }
    Ok(None)
}
fn index(value: i64, length: usize) -> Result<usize> {
    let i = if value < 0 {
        value + length as i64
    } else {
        value
    };
    ensure!(i >= 0 && i < length as i64, "index out of range");
    Ok(i as usize)
}
fn slice_indices(
    start: Option<i64>,
    stop: Option<i64>,
    step: i64,
    length: usize,
) -> Result<Vec<usize>> {
    ensure!(step != 0, "slice step cannot be zero");
    let n = length as i64;
    let adjust = |value: i64| {
        let v = if value < 0 { value + n } else { value };
        if step > 0 {
            v.clamp(0, n)
        } else {
            v.clamp(-1, n - 1)
        }
    };
    let mut i = start
        .map(adjust)
        .unwrap_or(if step > 0 { 0 } else { n - 1 });
    let stop = stop.map(adjust).unwrap_or(if step > 0 { n } else { -1 });
    let mut out = Vec::new();
    while if step > 0 { i < stop } else { i > stop } {
        out.push(i as usize);
        i += step;
    }
    Ok(out)
}
fn float_string(v: f64) -> String {
    if v.is_nan() {
        return "nan".into();
    }
    if v == f64::INFINITY {
        return "inf".into();
    }
    if v == f64::NEG_INFINITY {
        return "-inf".into();
    }
    let text = v.to_string();
    let negative = text.starts_with('-');
    let raw = text.trim_start_matches('-');
    let dot = raw.find('.').unwrap_or(raw.len());
    let mut digits = raw.replace('.', "");
    let leading = digits.bytes().take_while(|&b| b == b'0').count();
    if leading == digits.len() {
        return if negative {
            "-0.0".into()
        } else {
            "0.0".into()
        };
    }
    let exponent = dot as i32 - leading as i32 - 1;
    digits.drain(..leading);
    if exponent < -4 || exponent >= 16 {
        while digits.ends_with('0') {
            digits.pop();
        }
        let mut mantissa = digits[..1].to_owned();
        if digits.len() > 1 {
            mantissa.push('.');
            mantissa.push_str(&digits[1..]);
        }
        format!(
            "{}{mantissa}e{exponent:+03}",
            if negative { "-" } else { "" }
        )
    } else if !text.contains('.') {
        text + ".0"
    } else {
        text
    }
}

impl Val {
    pub fn list(values: Vec<Val>) -> Self {
        Self::List(Rc::new(RefCell::new(values)))
    }
    pub fn tuple(values: Vec<Val>) -> Self {
        Self::Tuple(values)
    }
    pub fn dict(values: Vec<(Val, Val)>) -> Self {
        Self::Dict(Rc::new(RefCell::new(values)))
    }
    pub fn namespace(values: Vec<(Val, Val)>) -> Self {
        Self::Namespace(Rc::new(RefCell::new(values)))
    }
    pub fn frozen_set(values: Vec<Val>) -> Self {
        if let Self::Set(values) = Self::set_values(values) {
            Self::FrozenSet(values.borrow().clone())
        } else {
            unreachable!()
        }
    }
    pub fn set_values(values: Vec<Val>) -> Self {
        let mut unique = Vec::new();
        for value in values {
            if !unique.iter().any(|v| eq(v, &value).unwrap_or(false)) {
                unique.push(value);
            }
        }
        Self::Set(Rc::new(RefCell::new(unique)))
    }
    pub fn reference(value: Value) -> Self {
        Self::Ref(value)
    }
    pub fn function(f: impl Fn(Args, Kwargs) -> Result<Val> + 'static) -> Self {
        Self::Func(Rc::new(f))
    }
    pub fn encode(&self) -> Result<Value> {
        Ok(match self {
            Self::None => Value::Null,
            Self::Bool(v) => json!(v),
            Self::Int(v) => json!(v),
            Self::Float(v) => json!(v),
            Self::Str(v) => json!(v),
            Self::Bytes(bytes) => {
                let mut hex = String::with_capacity(bytes.len() * 2);
                const H: &[u8; 16] = b"0123456789abcdef";
                for b in bytes {
                    hex.push(H[(b >> 4) as usize] as char);
                    hex.push(H[(b & 15) as usize] as char);
                }
                json!({"$bytes":hex})
            }
            Self::FrozenSet(values) => {
                json!({"$frozenset":values.iter().map(Val::encode).collect::<Result<Vec<_>>>()?})
            }
            Self::Set(values) => {
                json!({"$set":values.borrow().iter().map(Val::encode).collect::<Result<Vec<_>>>()?})
            }
            Self::List(values) => Value::Array(
                values
                    .borrow()
                    .iter()
                    .map(Val::encode)
                    .collect::<Result<_>>()?,
            ),
            Self::Tuple(values) => {
                json!({"$tuple":values.iter().map(Val::encode).collect::<Result<Vec<_>>>()?})
            }
            Self::Dict(entries) => {
                json!({"$dict":entries.borrow().iter().map(|(k,v)|Ok(json!([k.encode()?,v.encode()?]))).collect::<Result<Vec<Value>>>()?})
            }
            Self::Ref(value) => value.clone(),
            Self::Path(path) => json!(path.to_string_lossy()),
            Self::Type(name) => {
                let module = if name == "NoneType" {
                    "types"
                } else if name == "Path" {
                    "pathlib"
                } else {
                    "builtins"
                };
                let imported = Self::decode(callback(json!({"op":"import","module":module}))?)?;
                imported.attr(name)?.encode()?
            }
            Self::Func(_) | Self::Namespace(_) => self.encode_ref()?,
            Self::Slice { start, stop, step } => json!({"$slice":[start,stop,step]}),
        })
    }
    pub fn decode(value: Value) -> Result<Self> {
        Ok(match value {
            Value::Null => Self::None,
            Value::Bool(v) => Self::Bool(v),
            Value::Number(v) => {
                if let Some(v) = v.as_i64() {
                    Self::Int(v)
                } else {
                    Self::Float(v.as_f64().context("floating number")?)
                }
            }
            Value::String(v) => Self::Str(v),
            Value::Array(v) => Self::list(v.into_iter().map(Self::decode).collect::<Result<_>>()?),
            Value::Object(mut obj) => {
                if obj.len() == 1 && obj.contains_key("$frozenset") {
                    return Ok(Self::frozen_set(
                        obj["$frozenset"]
                            .as_array()
                            .context("frozenset values")?
                            .iter()
                            .cloned()
                            .map(Self::decode)
                            .collect::<Result<_>>()?,
                    ));
                }
                if obj.len() == 1 && obj.contains_key("$set") {
                    return Ok(Self::set_values(
                        obj["$set"]
                            .as_array()
                            .context("set values")?
                            .iter()
                            .cloned()
                            .map(Self::decode)
                            .collect::<Result<_>>()?,
                    ));
                }
                if obj.len() == 1 && obj.contains_key("$path") {
                    return Ok(Self::Path(PathBuf::from(
                        obj["$path"].as_str().context("path value")?,
                    )));
                }
                if obj.len() == 1 && obj.contains_key("$slice") {
                    let a = obj["$slice"].as_array().context("slice value")?;
                    return Ok(Self::Slice {
                        start: a[0].as_i64(),
                        stop: a[1].as_i64(),
                        step: a[2].as_i64().unwrap_or(1),
                    });
                }
                if obj.len() == 1 && obj.contains_key("$native") {
                    return native_value(
                        obj["$native"]["id"].as_u64().context("native object id")?,
                    );
                }
                if obj.len() == 1 && obj.contains_key("$ref") {
                    Self::Ref(Value::Object(obj))
                } else if obj.len() == 1 && obj.contains_key("$tuple") {
                    Self::Tuple(
                        obj.remove("$tuple")
                            .unwrap()
                            .as_array()
                            .context("tuple rows")?
                            .iter()
                            .cloned()
                            .map(Self::decode)
                            .collect::<Result<_>>()?,
                    )
                } else if obj.len() == 1 && obj.contains_key("$dict") {
                    Self::dict(
                        obj.remove("$dict")
                            .unwrap()
                            .as_array()
                            .context("dict rows")?
                            .iter()
                            .map(|row| {
                                Ok((Self::decode(row[0].clone())?, Self::decode(row[1].clone())?))
                            })
                            .collect::<Result<_>>()?,
                    )
                } else if obj.len() == 1 && obj.contains_key("$bytes") {
                    let text = obj["$bytes"].as_str().context("hex bytes")?;
                    ensure!(text.len() % 2 == 0, "odd hex bytes");
                    Self::Bytes(
                        (0..text.len())
                            .step_by(2)
                            .map(|i| u8::from_str_radix(&text[i..i + 2], 16).map_err(Into::into))
                            .collect::<Result<_>>()?,
                    )
                } else {
                    Self::dict(
                        obj.into_iter()
                            .map(|(k, v)| Ok((Self::Str(k), Self::decode(v)?)))
                            .collect::<Result<_>>()?,
                    )
                }
            }
        })
    }
    pub fn num(&self) -> Result<f64> {
        match self {
            Self::Int(v) => Ok(*v as f64),
            Self::Float(v) => Ok(*v),
            Self::Bool(v) => Ok(if *v { 1. } else { 0. }),
            Self::Ref(_) => remote(
                "call",
                &remote("getattr", &import("builtins")?, json!({"name":"float"}))?,
                json!({"args":[self.encode()?]}),
            )?
            .num(),
            _ => bail!("expected number, got {}", self.repr()?),
        }
    }
    pub fn integer(&self) -> Result<i64> {
        match self {
            Self::Int(v) => Ok(*v),
            Self::Float(v) => Ok(*v as i64),
            Self::Bool(v) => Ok(i64::from(*v)),
            _ => Ok(self.num()? as i64),
        }
    }
    pub fn truthy(&self) -> Result<bool> {
        Ok(match self {
            Self::None => false,
            Self::Bool(v) => *v,
            Self::Int(v) => *v != 0,
            Self::Float(v) => *v != 0.,
            Self::Str(v) => !v.is_empty(),
            Self::Bytes(v) => !v.is_empty(),
            Self::List(v) | Self::Set(v) => !v.borrow().is_empty(),
            Self::FrozenSet(v) => !v.is_empty(),
            Self::Tuple(v) => !v.is_empty(),
            Self::Dict(v) | Self::Namespace(v) => !v.borrow().is_empty(),
            Self::Ref(_) => remote("bool", self, json!({}))?.truthy()?,
            _ => true,
        })
    }
    pub fn iter(&self) -> Result<Vec<Val>> {
        Ok(match self {
            Self::List(v) | Self::Set(v) => v.borrow().clone(),
            Self::FrozenSet(v) => v.clone(),
            Self::Tuple(v) => v.clone(),
            Self::Str(v) => v.chars().map(|c| Self::Str(c.to_string())).collect(),
            Self::Bytes(v) => v.iter().map(|&b| Self::Int(b as i64)).collect(),
            Self::Dict(v) | Self::Namespace(v) => {
                v.borrow().iter().map(|(k, _)| k.clone()).collect()
            }
            Self::Ref(_) => remote("iter", self, json!({}))?.iter()?,
            _ => bail!("value is not iterable: {}", self.repr()?),
        })
    }
    pub fn len(&self) -> Result<usize> {
        if matches!(self, Self::Ref(_)) {
            return Ok(remote("len", self, json!({}))?.integer()? as usize);
        }
        Ok(self.iter()?.len())
    }
    pub fn str(&self) -> Result<String> {
        Ok(match self {
            Self::None => "None".into(),
            Self::Bool(v) => {
                if *v {
                    "True".into()
                } else {
                    "False".into()
                }
            }
            Self::Int(v) => v.to_string(),
            Self::Float(v) => float_string(*v),
            Self::Str(v) => v.clone(),
            Self::Path(v) => v.to_string_lossy().into_owned(),
            Self::Ref(_) => remote("str", self, json!({}))?.str()?,
            _ => self.repr()?,
        })
    }
    pub fn repr(&self) -> Result<String> {
        Ok(match self {
            Self::Str(s) => {
                let quote = if s.contains('\'') && !s.contains('"') {
                    '"'
                } else {
                    '\''
                };
                let mut out = quote.to_string();
                for c in s.chars() {
                    match c {
                        '\\' => out.push_str("\\\\"),
                        '\n' => out.push_str("\\n"),
                        '\r' => out.push_str("\\r"),
                        '\t' => out.push_str("\\t"),
                        c if c == quote => {
                            out.push('\\');
                            out.push(c)
                        }
                        c => out.push(c),
                    }
                }
                out.push(quote);
                out
            }
            Self::List(v) => format!(
                "[{}]",
                v.borrow()
                    .iter()
                    .map(Val::repr)
                    .collect::<Result<Vec<_>>>()?
                    .join(", ")
            ),
            Self::Tuple(v) => format!(
                "({}{})",
                v.iter()
                    .map(Val::repr)
                    .collect::<Result<Vec<_>>>()?
                    .join(", "),
                if v.len() == 1 { "," } else { "" }
            ),
            Self::FrozenSet(v) => {
                if v.is_empty() {
                    "frozenset()".into()
                } else {
                    format!(
                        "frozenset({{{}}})",
                        v.iter()
                            .map(Val::repr)
                            .collect::<Result<Vec<_>>>()?
                            .join(", ")
                    )
                }
            }
            Self::Set(v) => {
                if v.borrow().is_empty() {
                    "set()".into()
                } else {
                    format!(
                        "{{{}}}",
                        v.borrow()
                            .iter()
                            .map(Val::repr)
                            .collect::<Result<Vec<_>>>()?
                            .join(", ")
                    )
                }
            }
            Self::Dict(v) | Self::Namespace(v) => format!(
                "{{{}}}",
                v.borrow()
                    .iter()
                    .map(|(k, v)| Ok(format!("{}: {}", k.repr()?, v.repr()?)))
                    .collect::<Result<Vec<_>>>()?
                    .join(", ")
            ),
            Self::Bytes(v) => format!("b{}", Self::Str(String::from_utf8_lossy(v).into()).repr()?),
            Self::Ref(_) => remote("repr", self, json!({}))?.str()?,
            Self::Func(_) => "<compiled Rust function>".into(),
            Self::Type(n) => format!("<class '{n}'>"),
            Self::Slice { .. } => "<slice>".into(),
            _ => self.str()?,
        })
    }
    pub fn get(&self, key: Val) -> Result<Val> {
        if matches!(self, Self::Ref(_)) {
            return remote("getitem", self, json!({"key":native_snapshot(&key)?}));
        }
        if let Self::Slice { start, stop, step } = key {
            if let Self::Bytes(bytes) = self {
                let indices = slice_indices(start, stop, step, bytes.len())?;
                return Ok(Self::Bytes(indices.into_iter().map(|i| bytes[i]).collect()));
            }
            if let Self::Str(text) = self {
                let chars = text.chars().collect::<Vec<_>>();
                let indices = slice_indices(start, stop, step, chars.len())?;
                return Ok(Self::Str(indices.into_iter().map(|i| chars[i]).collect()));
            }
            let values = self.iter()?;
            let selected = slice_indices(start, stop, step, values.len())?
                .into_iter()
                .map(|i| values[i].clone())
                .collect::<Vec<_>>();
            return Ok(match self {
                Self::Str(_) => Self::Str(
                    selected
                        .iter()
                        .map(Val::str)
                        .collect::<Result<Vec<_>>>()?
                        .concat(),
                ),
                Self::Bytes(_) => Self::Bytes(
                    selected
                        .iter()
                        .map(|v| Ok(v.integer()? as u8))
                        .collect::<Result<_>>()?,
                ),
                Self::Tuple(_) => Self::Tuple(selected),
                _ => Self::list(selected),
            });
        }
        match self {
            Self::List(v) | Self::Set(v) => {
                let v = v.borrow();
                Ok(v[index(key.integer()?, v.len())?].clone())
            }
            Self::Tuple(v) => Ok(v[index(key.integer()?, v.len())?].clone()),
            Self::Str(s) => {
                let values = s.chars().collect::<Vec<_>>();
                Ok(Self::Str(
                    values[index(key.integer()?, values.len())?].to_string(),
                ))
            }
            Self::Bytes(b) => Ok(Self::Int(b[index(key.integer()?, b.len())?] as i64)),
            Self::Dict(v) | Self::Namespace(v) => {
                let v = v.borrow();
                key_index(&v, &key)?
                    .map(|i| v[i].1.clone())
                    .with_context(|| format!("missing key {}", key.repr().unwrap_or_default()))
            }
            Self::Ref(_) => remote("getitem", self, json!({"key":native_snapshot(&key)?})),
            _ => bail!("value is not subscriptable"),
        }
    }
    pub fn set(&self, key: Val, value: Val) -> Result<()> {
        match self {
            Self::List(v) => {
                if let Val::Slice { start, stop, step } = key {
                    let replacement = value.iter()?;
                    let mut values = v.borrow_mut();
                    if step == 1 {
                        let n = values.len() as i64;
                        let adjust = |i: i64| if i < 0 { (i + n).clamp(0, n) } else { i.min(n) };
                        let start = start.map(adjust).unwrap_or(0) as usize;
                        let stop = stop.map(adjust).unwrap_or(n).max(start as i64) as usize;
                        values.splice(start..stop, replacement);
                    } else {
                        let indices = slice_indices(start, stop, step, values.len())?;
                        ensure!(
                            indices.len() == replacement.len(),
                            "extended slice assignment length differs"
                        );
                        for (i, value) in indices.into_iter().zip(replacement) {
                            values[i] = value;
                        }
                    }
                    return Ok(());
                }
                let mut v = v.borrow_mut();
                let i = index(key.integer()?, v.len())?;
                v[i] = value;
                Ok(())
            }
            Self::Dict(v) | Self::Namespace(v) => {
                let mut v = v.borrow_mut();
                if let Some(i) = key_index(&v, &key)? {
                    v[i].1 = value
                } else {
                    v.push((key, value));
                }
                Ok(())
            }
            Self::Ref(_) => {
                remote(
                    "setitem",
                    self,
                    json!({"key":native_snapshot(&key)?,"value":native_snapshot(&value)?}),
                )?;
                Ok(())
            }
            _ => bail!("value does not support assignment"),
        }
    }
    pub fn delete(&self, key: Val) -> Result<()> {
        match self {
            Self::List(v) => {
                if let Val::Slice { start, stop, step } = key {
                    let mut values = v.borrow_mut();
                    let mut indices = slice_indices(start, stop, step, values.len())?;
                    indices.sort_unstable_by(|a, b| b.cmp(a));
                    for i in indices {
                        values.remove(i);
                    }
                    return Ok(());
                }
                let i = index(key.integer()?, v.borrow().len())?;
                v.borrow_mut().remove(i);
                Ok(())
            }
            Self::Dict(v) | Self::Namespace(v) => {
                let i = key_index(&v.borrow(), &key)?.context("missing dict key")?;
                v.borrow_mut().remove(i);
                Ok(())
            }
            Self::Ref(_) => {
                remote("delitem", self, json!({"key":native_snapshot(&key)?}))?;
                Ok(())
            }
            _ => bail!("value does not support deletion"),
        }
    }
    pub fn setattr(&self, name: &str, value: Val) -> Result<()> {
        match self {
            Self::Namespace(_) => self.set(name.into(), value),
            Self::Func(function) => {
                let pointer = Rc::as_ptr(function) as *const () as usize;
                let attrs = FUNCTION_ATTRIBUTES.with(|held| {
                    held.borrow_mut()
                        .entry(pointer)
                        .or_insert_with(|| Rc::new(RefCell::new(Vec::new())))
                        .clone()
                });
                Self::Dict(attrs).set(name.into(), value)
            }
            Self::Ref(_) => {
                remote(
                    "setattr",
                    self,
                    json!({"name":name,"value":native_snapshot(&value)?}),
                )?;
                Ok(())
            }
            _ => bail!("attribute assignment on non-object"),
        }
    }
    pub fn attr(&self, name: &str) -> Result<Val> {
        if let Self::Func(function) = self {
            if name == "__call__" {
                return Ok(self.clone());
            }
            let pointer = Rc::as_ptr(function) as *const () as usize;
            let attrs = FUNCTION_ATTRIBUTES.with(|held| held.borrow().get(&pointer).cloned());
            return attrs
                .map(|attrs| Self::Dict(attrs).get(name.into()))
                .unwrap_or_else(|| Err(anyhow::anyhow!("function has no attribute {name}")));
        }
        if let Self::Namespace(entries) = self {
            let rows = entries.borrow();
            if let Some(i) = key_index(&rows, &name.into())? {
                return Ok(rows[i].1.clone());
            }
            let fallback = key_index(&rows, &"__getattr__".into())?.map(|i| rows[i].1.clone());
            drop(rows);
            if let Some(f) = fallback {
                return f.call(vec![name.into()], vec![]);
            }
            bail!("missing namespace attribute {name}");
        }
        if matches!(self, Self::Ref(_)) {
            let primitive = remote("getattr", self, json!({"name":name}))?;
            if name == "point" && primitive.attr("__call__").is_ok() {
                let image = self.clone();
                return Ok(Self::function(move |mut args, kwargs| {
                    if let Some(Self::Func(_)) = args.first() {
                        let callable = args[0].clone();
                        let table = (0..256)
                            .map(|i| callable.call(vec![Self::Int(i)], vec![]))
                            .collect::<Result<Vec<_>>>()?;
                        let bands = image.attr("getbands")?.call(vec![], vec![])?.len()?;
                        args[0] = Self::list((0..bands).flat_map(|_| table.clone()).collect());
                    }
                    primitive.call(args, kwargs)
                }));
            }
            return Ok(primitive);
        }
        if let Self::Path(path) = self {
            return path_attr(path, name);
        }
        if name == "__getitem__"
            && matches!(
                self,
                Self::Dict(_) | Self::List(_) | Self::Tuple(_) | Self::Str(_) | Self::Bytes(_)
            )
        {
            let receiver = self.clone();
            return Ok(Self::function(move |args, _| receiver.get(arg(&args, 0)?)));
        }
        if name == "__contains__"
            && matches!(
                self,
                Self::Dict(_)
                    | Self::List(_)
                    | Self::Tuple(_)
                    | Self::Set(_)
                    | Self::FrozenSet(_)
                    | Self::Str(_)
                    | Self::Bytes(_)
            )
        {
            let receiver = self.clone();
            return Ok(Self::function(move |args, _| {
                Ok(Val::Bool(receiver.contains(&arg(&args, 0)?)?))
            }));
        }
        if name == "__setitem__" && matches!(self, Self::Dict(_) | Self::List(_)) {
            let receiver = self.clone();
            return Ok(Self::function(move |args, _| {
                receiver.set(arg(&args, 0)?, arg(&args, 1)?)?;
                Ok(Self::None)
            }));
        }
        let supported = match self {
            Self::List(_) => [
                "append", "extend", "pop", "insert", "clear", "reverse", "copy", "sort", "remove",
                "index", "count",
            ]
            .contains(&name),
            Self::Dict(_) => [
                "items",
                "keys",
                "values",
                "get",
                "setdefault",
                "pop",
                "update",
                "copy",
                "clear",
            ]
            .contains(&name),
            Self::FrozenSet(_) => {
                ["copy", "union", "intersection", "difference", "issubset"].contains(&name)
            }
            Self::Set(_) => [
                "add",
                "pop",
                "update",
                "discard",
                "remove",
                "copy",
                "clear",
                "union",
                "intersection",
                "difference",
                "issubset",
            ]
            .contains(&name),
            Self::Str(_) => [
                "upper",
                "lower",
                "casefold",
                "strip",
                "rstrip",
                "lstrip",
                "startswith",
                "endswith",
                "replace",
                "translate",
                "join",
                "split",
                "rsplit",
                "partition",
                "rpartition",
                "splitlines",
                "removeprefix",
                "removesuffix",
                "find",
                "rfind",
                "index",
                "rindex",
                "count",
                "encode",
                "isdigit",
                "isdecimal",
                "isupper",
                "islower",
                "isalpha",
                "isalnum",
                "isspace",
                "format",
            ]
            .contains(&name),
            Self::Bytes(_) => ["decode", "hex"].contains(&name),
            Self::Tuple(_) => name == "index",
            Self::Type(kind) => {
                (kind == "dict" && name == "fromkeys") || (kind == "bytes" && name == "fromhex")
            }
            _ => false,
        };
        ensure!(supported, "value has no attribute {name}");
        let receiver = self.clone();
        let name = name.to_owned();
        Ok(Self::function(move |args, kwargs| {
            method(&receiver, &name, args, kwargs)
        }))
    }
    pub fn call(&self, args: Args, kwargs: Kwargs) -> Result<Val> {
        match self {
            Self::Func(f) => f(args, kwargs),
            Self::Ref(_) => remote(
                "call",
                self,
                json!({"args":args.iter().map(native_snapshot).collect::<Result<Vec<_>>>()?,"kwargs":native_snapshot(&Val::dict(kwargs.iter().map(|(k,v)|(Val::Str(k.clone()),v.clone())).collect()))?}),
            ),
            Self::Type(name) => construct(name, args, kwargs),
            _ => bail!("value is not callable: {}", self.repr()?),
        }
    }
    pub fn contains(&self, item: &Val) -> Result<bool> {
        match self {
            Self::Str(text) => Ok(text.contains(&item.str()?)),
            Self::Ref(_) => {
                remote("contains", self, json!({"item":native_snapshot(item)?}))?.truthy()
            }
            _ => {
                for value in self.iter()? {
                    if eq(&value, item)? {
                        return Ok(true);
                    }
                }
                Ok(false)
            }
        }
    }
}

pub fn eq(a: &Val, b: &Val) -> Result<bool> {
    if let (Some(a), Some(b)) = (set_items(a), set_items(b)) {
        return Ok(a.len() == b.len()
            && a.iter()
                .all(|v| b.iter().any(|w| eq(v, w).unwrap_or(false))));
    }

    Ok(match (a, b) {
        (Val::None, Val::None) => true,
        (Val::Str(a), Val::Str(b)) => a == b,
        (Val::Bytes(a), Val::Bytes(b)) => a == b,
        (Val::Path(a), Val::Path(b)) => a == b,
        (Val::Ref(a), Val::Ref(b)) => a == b,
        (Val::Tuple(a), Val::Tuple(b)) => sequence_eq(a, b)?,
        (Val::List(a), Val::List(b)) => sequence_eq(&a.borrow(), &b.borrow())?,
        (Val::Dict(a), Val::Dict(b)) => {
            let a = a.borrow();
            let b = b.borrow();
            if a.len() != b.len() {
                false
            } else {
                let mut yes = true;
                for (k, v) in a.iter() {
                    if let Some(i) = key_index(&b, k)? {
                        yes &= eq(v, &b[i].1)?
                    } else {
                        yes = false
                    }
                }
                yes
            }
        }
        (
            Val::Bool(_) | Val::Int(_) | Val::Float(_),
            Val::Bool(_) | Val::Int(_) | Val::Float(_),
        ) => a.num()? == b.num()?,
        (Val::Ref(_), _) => remote(
            "binary",
            a,
            json!({"operator":"eq","other":native_snapshot(&b)?}),
        )?
        .truthy()?,
        (_, Val::Ref(_)) => {
            remote("binary", b, json!({"operator":"eq","other":a.encode()?}))?.truthy()?
        }
        _ => false,
    })
}
fn sequence_eq(a: &[Val], b: &[Val]) -> Result<bool> {
    if a.len() != b.len() {
        return Ok(false);
    }
    for (a, b) in a.iter().zip(b) {
        if !eq(a, b)? {
            return Ok(false);
        }
    }
    Ok(true)
}
fn cmp(a: &Val, b: &Val) -> Result<std::cmp::Ordering> {
    match (a, b) {
        (Val::Str(a), Val::Str(b)) => Ok(a.cmp(b)),
        (Val::Tuple(a), Val::Tuple(b)) => {
            for (a, b) in a.iter().zip(b) {
                let order = cmp(a, b)?;
                if order != std::cmp::Ordering::Equal {
                    return Ok(order);
                }
            }
            Ok(a.len().cmp(&b.len()))
        }
        _ => a
            .num()?
            .partial_cmp(&b.num()?)
            .context("unordered numeric comparison"),
    }
}
pub fn compare(op: &str, a: Val, b: Val) -> Result<Val> {
    if (matches!(a, Val::Ref(_)) || matches!(b, Val::Ref(_)))
        && ["eq", "ne", "lt", "le", "gt", "ge"].contains(&op)
    {
        return remote(
            "binary",
            &a,
            json!({"operator":op,"other":native_snapshot(&b)?}),
        );
    }
    let result = match op {
        "eq" | "==" => eq(&a, &b)?,
        "ne" | "!=" => !eq(&a, &b)?,
        "is" => match (&a, &b) {
            (Val::None, Val::None) => true,
            (Val::List(a), Val::List(b)) => Rc::ptr_eq(a, b),
            (Val::Dict(a), Val::Dict(b)) | (Val::Namespace(a), Val::Namespace(b)) => {
                Rc::ptr_eq(a, b)
            }
            _ => eq(&a, &b)?,
        },
        "is_not" | "is not" => !compare("is", a, b)?.truthy()?,
        "in" => b.contains(&a)?,
        "not_in" | "not in" => !b.contains(&a)?,
        "lt" | "<" => cmp(&a, &b)?.is_lt(),
        "le" | "<=" => !cmp(&a, &b)?.is_gt(),
        "gt" | ">" => cmp(&a, &b)?.is_gt(),
        "ge" | ">=" => !cmp(&a, &b)?.is_lt(),
        _ => bail!("unknown comparison {op}"),
    };
    Ok(Val::Bool(result))
}
pub fn unary(op: &str, value: Val) -> Result<Val> {
    Ok(match op {
        "not" => Val::Bool(!value.truthy()?),
        "pos" | "+" => value,
        "neg" | "-" => match value {
            Val::Int(v) => Val::Int(-v),
            Val::Ref(_) => return remote("unary", &value, json!({"operator":"neg"})),
            _ => Val::Float(-value.num()?),
        },
        "invert" | "~" => Val::Int(!value.integer()?),
        _ => bail!("unknown unary operator {op}"),
    })
}
pub fn binary(op: &str, a: Val, b: Val) -> Result<Val> {
    if matches!(op, "mod" | "%") {
        if let Val::Str(pattern) = &a {
            return Ok(Val::Str(percent_format(pattern, &b)?));
        }
    }
    if matches!(a, Val::Ref(_)) || matches!(b, Val::Ref(_)) {
        let operator = match op {
            "or" | "|" => "or_",
            "and" | "&" => "and_",
            "+" => "add",
            "-" => "sub",
            "*" => "mul",
            "/" => "truediv",
            "//" => "floordiv",
            "%" => "mod",
            "**" => "pow",
            "^" => "xor",
            "<<" => "lshift",
            ">>" => "rshift",
            _ => op,
        };
        if set_items(&a).is_some() || set_items(&b).is_some() {
            let a = if matches!(a, Val::Ref(_)) {
                remote("snapshot", &a, json!({}))?
            } else {
                a
            };
            let b = if matches!(b, Val::Ref(_)) {
                remote("snapshot", &b, json!({}))?
            } else {
                b
            };
            if !matches!(a, Val::Ref(_)) && !matches!(b, Val::Ref(_)) {
                return binary(op, a, b);
            }
            return remote(
                "binary",
                &a,
                json!({"operator":operator,"other":native_snapshot(&b)?}),
            );
        }
        return remote(
            "binary",
            &a,
            json!({"operator":operator,"other":native_snapshot(&b)?}),
        );
    }
    if op == "add" || op == "+" {
        match (&a, &b) {
            (Val::Str(a), Val::Str(b)) => return Ok(Val::Str(a.clone() + b)),
            (Val::List(a), Val::List(b)) => {
                return Ok(Val::list([a.borrow().clone(), b.borrow().clone()].concat()));
            }
            (Val::Tuple(a), Val::Tuple(b)) => {
                return Ok(Val::Tuple([a.clone(), b.clone()].concat()));
            }
            (Val::Bytes(a), Val::Bytes(b)) => {
                return Ok(Val::Bytes([a.clone(), b.clone()].concat()));
            }
            _ => (),
        }
    }
    if op == "truediv" || op == "/" {
        if let Val::Path(path) = a {
            return Ok(Val::Path(path.join(b.str()?)));
        }
    }
    if op == "mul" || op == "*" {
        let (seq, count) = if matches!(
            a,
            Val::Str(_) | Val::List(_) | Val::Tuple(_) | Val::Bytes(_)
        ) {
            (&a, &b)
        } else {
            (&b, &a)
        };
        if let Ok(n) = count.integer() {
            let n = n.max(0) as usize;
            match seq {
                Val::Str(s) => return Ok(Val::Str(s.repeat(n))),
                Val::Bytes(s) => return Ok(Val::Bytes(s.repeat(n))),
                Val::List(s) => {
                    return Ok(Val::list((0..n).flat_map(|_| s.borrow().clone()).collect()));
                }
                Val::Tuple(s) => return Ok(Val::Tuple((0..n).flat_map(|_| s.clone()).collect())),
                _ => (),
            }
        }
    }
    if let (Some(av), Some(bv)) = (set_items(&a), set_items(&b)) {
        let mut out = Vec::new();
        match op {
            "or" | "|" => {
                out.extend(av.clone());
                out.extend(bv.clone())
            }
            "and" | "&" => {
                for v in av.iter() {
                    if bv.iter().any(|b| eq(v, b).unwrap_or(false)) {
                        out.push(v.clone())
                    }
                }
            }
            "sub" | "-" => {
                for v in av.iter() {
                    if !bv.iter().any(|b| eq(v, b).unwrap_or(false)) {
                        out.push(v.clone())
                    }
                }
            }
            _ => bail!("unsupported set operation {op}"),
        };
        return Ok(if matches!(a, Val::FrozenSet(_)) {
            Val::frozen_set(out)
        } else {
            Val::set_values(out)
        });
    }
    if matches!(op, "or" | "|") && matches!(a, Val::Dict(_)) && matches!(b, Val::Dict(_)) {
        let out = Val::dict(entries_of(&a)?);
        for (k, v) in entries_of(&b)? {
            out.set(k, v)?;
        }
        return Ok(out);
    }
    let x = a.num()?;
    let y = b.num()?;
    let both_int =
        matches!(a, Val::Int(_) | Val::Bool(_)) && matches!(b, Val::Int(_) | Val::Bool(_));
    let value = match op {
        "add" | "+" => x + y,
        "sub" | "-" => x - y,
        "mul" | "*" => x * y,
        "truediv" | "/" => {
            ensure!(y != 0., "division by zero");
            return Ok(Val::Float(x / y));
        }
        "floordiv" | "//" => {
            ensure!(y != 0., "division by zero");
            (x / y).floor()
        }
        "mod" | "%" => {
            ensure!(y != 0., "modulo by zero");
            let rem = x % y;
            if rem != 0. && rem.signum() != y.signum() {
                rem + y
            } else {
                rem
            }
        }
        "pow" | "**" => x.powf(y),
        "or" | "|" => return Ok(Val::Int(a.integer()? | b.integer()?)),
        "and" | "&" => return Ok(Val::Int(a.integer()? & b.integer()?)),
        "xor" | "^" => return Ok(Val::Int(a.integer()? ^ b.integer()?)),
        "lshift" | "<<" => return Ok(Val::Int(a.integer()? << b.integer()?)),
        "rshift" | ">>" => return Ok(Val::Int(a.integer()? >> b.integer()?)),
        _ => bail!("unknown binary operator {op}"),
    };
    Ok(if both_int && value.is_finite() && value.fract() == 0. {
        Val::Int(value as i64)
    } else {
        Val::Float(value)
    })
}

fn arg(args: &[Val], index: usize) -> Result<Val> {
    args.get(index)
        .cloned()
        .with_context(|| format!("missing argument {index}"))
}
fn option(kwargs: &Kwargs, name: &str) -> Option<Val> {
    kwargs
        .iter()
        .find(|(k, _)| k == name)
        .map(|(_, v)| v.clone())
}
fn method(receiver: &Val, name: &str, args: Args, kwargs: Kwargs) -> Result<Val> {
    match receiver {
        Val::List(values) => match name {
            "append" => {
                values.borrow_mut().push(arg(&args, 0)?);
                return Ok(Val::None);
            }
            "extend" => {
                let more = arg(&args, 0)?.iter()?;
                values.borrow_mut().extend(more);
                return Ok(Val::None);
            }
            "pop" => {
                let i = index(
                    args.first().map(Val::integer).transpose()?.unwrap_or(-1),
                    values.borrow().len(),
                )?;
                return Ok(values.borrow_mut().remove(i));
            }
            "insert" => {
                let n = values.borrow().len() as i64;
                let i = arg(&args, 0)?.integer()?;
                let i = if i < 0 { (i + n).max(0) } else { i.min(n) } as usize;
                values.borrow_mut().insert(i, arg(&args, 1)?);
                return Ok(Val::None);
            }
            "clear" => {
                values.borrow_mut().clear();
                return Ok(Val::None);
            }
            "reverse" => {
                values.borrow_mut().reverse();
                return Ok(Val::None);
            }
            "copy" => return Ok(Val::list(values.borrow().clone())),
            "sort" => {
                let sorted = sorted(values.borrow().clone(), &kwargs)?;
                *values.borrow_mut() = sorted;
                return Ok(Val::None);
            }
            "remove" => {
                let key = arg(&args, 0)?;
                let i = values
                    .borrow()
                    .iter()
                    .position(|v| eq(v, &key).unwrap_or(false))
                    .context("value is not in list")?;
                values.borrow_mut().remove(i);
                return Ok(Val::None);
            }
            "index" => {
                let key = arg(&args, 0)?;
                return Ok(Val::Int(
                    values
                        .borrow()
                        .iter()
                        .position(|v| eq(v, &key).unwrap_or(false))
                        .context("value is not in list")? as i64,
                ));
            }
            "count" => {
                let key = arg(&args, 0)?;
                return Ok(Val::Int(
                    values
                        .borrow()
                        .iter()
                        .filter(|v| eq(v, &key).unwrap_or(false))
                        .count() as i64,
                ));
            }
            _ => (),
        },
        Val::Dict(entries) => match name {
            "items" => {
                return Ok(Val::list(
                    entries
                        .borrow()
                        .iter()
                        .map(|(k, v)| Val::Tuple(vec![k.clone(), v.clone()]))
                        .collect(),
                ));
            }
            "keys" => {
                return Ok(Val::list(
                    entries.borrow().iter().map(|(k, _)| k.clone()).collect(),
                ));
            }
            "values" => {
                return Ok(Val::list(
                    entries.borrow().iter().map(|(_, v)| v.clone()).collect(),
                ));
            }
            "get" => {
                let key = arg(&args, 0)?;
                return Ok(entries
                    .borrow()
                    .iter()
                    .find(|(k, _)| eq(k, &key).unwrap_or(false))
                    .map(|(_, v)| v.clone())
                    .unwrap_or(args.get(1).cloned().unwrap_or(Val::None)));
            }
            "setdefault" => {
                let key = arg(&args, 0)?;
                if let Some(i) = key_index(&entries.borrow(), &key)? {
                    return Ok(entries.borrow()[i].1.clone());
                }
                let value = args.get(1).cloned().unwrap_or(Val::None);
                entries.borrow_mut().push((key, value.clone()));
                return Ok(value);
            }
            "pop" => {
                let key = arg(&args, 0)?;
                let i = key_index(&entries.borrow(), &key)?;
                return if let Some(i) = i {
                    Ok(entries.borrow_mut().remove(i).1)
                } else {
                    args.get(1).cloned().context("missing dict key")
                };
            }
            "update" => {
                if let Some(value) = args.first() {
                    for (k, v) in entries_of(value)? {
                        receiver.set(k, v)?;
                    }
                }
                for (k, v) in kwargs {
                    receiver.set(k.into(), v)?;
                }
                return Ok(Val::None);
            }
            "copy" => return Ok(Val::dict(entries.borrow().clone())),
            "clear" => {
                entries.borrow_mut().clear();
                return Ok(Val::None);
            }
            _ => (),
        },
        Val::FrozenSet(values) => {
            let result = method(&Val::set_values(values.clone()), name, args, kwargs)?;
            return Ok(if let Val::Set(v) = result {
                Val::frozen_set(v.borrow().clone())
            } else {
                result
            });
        }
        Val::Set(values) => match name {
            "pop" => return values.borrow_mut().pop().context("pop from an empty set"),
            "add" => {
                let value = arg(&args, 0)?;
                if !values
                    .borrow()
                    .iter()
                    .any(|v| eq(v, &value).unwrap_or(false))
                {
                    values.borrow_mut().push(value);
                }
                return Ok(Val::None);
            }
            "update" => {
                for group in args {
                    for v in group.iter()? {
                        method(receiver, "add", vec![v], vec![])?;
                    }
                }
                return Ok(Val::None);
            }
            "discard" | "remove" => {
                let key = arg(&args, 0)?;
                let i = values
                    .borrow()
                    .iter()
                    .position(|v| eq(v, &key).unwrap_or(false));
                if let Some(i) = i {
                    values.borrow_mut().remove(i);
                } else if name == "remove" {
                    bail!("set element not found");
                }
                return Ok(Val::None);
            }
            "copy" => return Ok(Val::set_values(values.borrow().clone())),
            "clear" => {
                values.borrow_mut().clear();
                return Ok(Val::None);
            }
            "union" | "intersection" | "difference" => {
                let mut out = receiver.clone();
                for other in args {
                    out = binary(
                        match name {
                            "union" => "or",
                            "intersection" => "and",
                            _ => "sub",
                        },
                        out,
                        Val::set_values(other.iter()?),
                    )?;
                }
                return Ok(out);
            }
            "issubset" => {
                let other = arg(&args, 0)?;
                for item in values.borrow().iter() {
                    if !other.contains(item)? {
                        return Ok(false.into());
                    }
                }
                return Ok(true.into());
            }
            _ => (),
        },
        Val::Str(text) => match name {
            "translate" => {
                let table = arg(&args, 0)?;
                let mut out = String::new();
                for ch in text.chars() {
                    match table.get(Val::Int(ch as i64)) {
                        Err(_) => out.push(ch),
                        Ok(Val::None) => (),
                        Ok(Val::Str(replacement)) => out.push_str(&replacement),
                        Ok(value) => out.push(
                            char::from_u32(value.integer()? as u32)
                                .context("translation code point out of range")?,
                        ),
                    }
                }
                return Ok(Val::Str(out));
            }
            "isupper" => {
                return Ok((text.chars().any(char::is_uppercase)
                    && !text.chars().any(char::is_lowercase))
                .into());
            }
            "islower" => {
                return Ok((text.chars().any(char::is_lowercase)
                    && !text.chars().any(char::is_uppercase))
                .into());
            }
            "isalpha" => {
                return Ok((!text.is_empty() && text.chars().all(char::is_alphabetic)).into());
            }
            "isalnum" => {
                return Ok((!text.is_empty() && text.chars().all(char::is_alphanumeric)).into());
            }
            "isspace" => {
                return Ok((!text.is_empty() && text.chars().all(char::is_whitespace)).into());
            }
            "isdecimal" => {
                return Ok((!text.is_empty() && text.chars().all(|c| c.is_ascii_digit())).into());
            }
            "upper" => return Ok(text.to_uppercase().into()),
            "lower" => return Ok(text.to_lowercase().into()),
            "casefold" => return Ok(text.to_lowercase().into()),
            "strip" | "rstrip" | "lstrip" => {
                let chars = args.first().map(Val::str).transpose()?;
                let pattern = |c: char| chars.as_ref().map_or(c.is_whitespace(), |s| s.contains(c));
                return Ok(match name {
                    "strip" => text.trim_matches(pattern),
                    "lstrip" => text.trim_start_matches(pattern),
                    _ => text.trim_end_matches(pattern),
                }
                .to_owned()
                .into());
            }
            "startswith" | "endswith" => {
                let patterns = arg(&args, 0)?;
                let patterns = if matches!(patterns, Val::Tuple(_)) {
                    patterns.iter()?
                } else {
                    vec![patterns]
                };
                let start = args.get(1).map(Val::integer).transpose()?.unwrap_or(0);
                let end = args.get(2).map(Val::integer).transpose()?;
                let s = receiver
                    .get(Val::Slice {
                        start: Some(start),
                        stop: end,
                        step: 1,
                    })?
                    .str()?;
                let yes = patterns.iter().any(|p| {
                    p.str().is_ok_and(|p| {
                        if name == "startswith" {
                            s.starts_with(&p)
                        } else {
                            s.ends_with(&p)
                        }
                    })
                });
                return Ok(yes.into());
            }
            "replace" => {
                let from = arg(&args, 0)?.str()?;
                let to = arg(&args, 1)?.str()?;
                let count = args.get(2).map(Val::integer).transpose()?.unwrap_or(-1);
                return Ok(if count < 0 {
                    text.replace(&from, &to)
                } else {
                    text.replacen(&from, &to, count as usize)
                }
                .into());
            }
            "join" => {
                return Ok(arg(&args, 0)?
                    .iter()?
                    .iter()
                    .map(Val::str)
                    .collect::<Result<Vec<_>>>()?
                    .join(text)
                    .into());
            }
            "partition" | "rpartition" => {
                let separator = arg(&args, 0)?.str()?;
                ensure!(!separator.is_empty(), "empty separator");
                let found = if name == "partition" {
                    text.find(&separator)
                } else {
                    text.rfind(&separator)
                };
                return Ok(if let Some(at) = found {
                    Val::tuple(vec![
                        text[..at].to_owned().into(),
                        separator.clone().into(),
                        text[at + separator.len()..].to_owned().into(),
                    ])
                } else if name == "partition" {
                    Val::tuple(vec![text.clone().into(), "".into(), "".into()])
                } else {
                    Val::tuple(vec!["".into(), "".into(), text.clone().into()])
                });
            }
            "split" | "rsplit" => {
                let separator = args
                    .first()
                    .filter(|v| !matches!(v, Val::None))
                    .map(Val::str)
                    .transpose()?;
                let limit = args.get(1).map(Val::integer).transpose()?.unwrap_or(-1);
                let mut parts = if let Some(sep) = separator {
                    ensure!(!sep.is_empty(), "empty separator");
                    if limit < 0 {
                        text.split(&sep).map(str::to_owned).collect::<Vec<_>>()
                    } else if name == "split" {
                        text.splitn(limit as usize + 1, &sep)
                            .map(str::to_owned)
                            .collect()
                    } else {
                        let mut rows = text
                            .rsplitn(limit as usize + 1, &sep)
                            .map(str::to_owned)
                            .collect::<Vec<_>>();
                        rows.reverse();
                        rows
                    }
                } else {
                    text.split_whitespace().map(str::to_owned).collect()
                };
                if limit >= 0 && parts.len() > limit as usize + 1 {
                    let rest = parts.split_off(limit as usize);
                    parts.push(rest.join(" "));
                }
                return Ok(Val::list(parts.into_iter().map(Val::Str).collect()));
            }
            "splitlines" => {
                let keep = args.first().map(Val::truthy).transpose()?.unwrap_or(false);
                let parts = if keep {
                    text.split_inclusive('\n')
                        .map(str::to_owned)
                        .collect::<Vec<_>>()
                } else {
                    text.lines().map(str::to_owned).collect::<Vec<_>>()
                };
                return Ok(Val::list(parts.into_iter().map(Val::Str).collect()));
            }
            "removeprefix" => {
                let p = arg(&args, 0)?.str()?;
                return Ok(text.strip_prefix(&p).unwrap_or(text).to_owned().into());
            }
            "removesuffix" => {
                let p = arg(&args, 0)?.str()?;
                return Ok(text.strip_suffix(&p).unwrap_or(text).to_owned().into());
            }
            "find" | "rfind" | "index" | "rindex" => {
                let needle = arg(&args, 0)?.str()?;
                let found = if name.starts_with('r') {
                    text.rfind(&needle)
                } else {
                    text.find(&needle)
                };
                if name.ends_with("index") {
                    ensure!(found.is_some(), "substring not found");
                }
                return Ok(Val::Int(
                    found
                        .map(|i| text[..i].chars().count() as i64)
                        .unwrap_or(-1),
                ));
            }
            "count" => return Ok(Val::Int(text.matches(&arg(&args, 0)?.str()?).count() as i64)),
            "encode" => return Ok(Val::Bytes(text.as_bytes().to_vec())),
            "isdigit" => {
                return Ok((!text.is_empty() && text.chars().all(|c| c.is_ascii_digit())).into());
            }
            "format" => {
                let mut out = String::new();
                let mut tail = text.as_str();
                let mut next = 0;
                while let Some(i) = tail.find('{') {
                    out.push_str(&tail[..i]);
                    if tail[i..].starts_with("{{") {
                        out.push('{');
                        tail = &tail[i + 2..];
                        continue;
                    }
                    let end = tail[i + 1..].find('}').context("unclosed format brace")? + i + 1;
                    let field = &tail[i + 1..end];
                    let (key, spec) = field.split_once(':').unwrap_or((field, ""));
                    let value = if key.is_empty() {
                        let v = arg(&args, next)?;
                        next += 1;
                        v
                    } else if let Ok(i) = key.parse::<usize>() {
                        arg(&args, i)?
                    } else {
                        option(&kwargs, key).context("format key")?
                    };
                    out.push_str(&format(&value, spec)?);
                    tail = &tail[end + 1..];
                }
                out.push_str(tail);
                return Ok(out.replace("}}", "}").into());
            }
            _ => (),
        },
        Val::Bytes(bytes) => match name {
            "decode" => return Ok(String::from_utf8(bytes.clone())?.into()),
            "hex" => return Ok(Val::Str(bytes.iter().map(|b| format!("{b:02x}")).collect())),
            _ => (),
        },
        Val::Type(kind) if kind == "dict" && name == "fromkeys" => {
            let value = args.get(1).cloned().unwrap_or(Val::None);
            return Ok(Val::dict(
                arg(&args, 0)?
                    .iter()?
                    .into_iter()
                    .map(|k| (k, value.clone()))
                    .collect(),
            ));
        }
        Val::Type(kind) if kind == "bytes" && name == "fromhex" => {
            return Val::decode(json!({"$bytes":arg(&args,0)?.str()?}));
        }
        Val::Tuple(values) if name == "index" => {
            let key = arg(&args, 0)?;
            return Ok(Val::Int(
                values
                    .iter()
                    .position(|v| eq(v, &key).unwrap_or(false))
                    .context("tuple index not found")? as i64,
            ));
        }
        _ => (),
    }
    bail!("unsupported native {}.{name}", receiver.repr()?)
}
pub fn entries_of(value: &Val) -> Result<Vec<(Val, Val)>> {
    match value {
        Val::Ref(_) => entries_of(&remote("snapshot", value, json!({}))?),
        Val::Dict(e) | Val::Namespace(e) => Ok(e.borrow().clone()),
        _ => value
            .iter()?
            .iter()
            .map(|v| {
                let pair = v.iter()?;
                ensure!(pair.len() == 2, "dictionary entry needs two values");
                Ok((pair[0].clone(), pair[1].clone()))
            })
            .collect(),
    }
}
fn sorted(mut values: Vec<Val>, kwargs: &Kwargs) -> Result<Vec<Val>> {
    if let Some(key) = option(kwargs, "key").filter(|v| !matches!(v, Val::None)) {
        let mut decorated = values
            .into_iter()
            .map(|v| Ok((key.call(vec![v.clone()], vec![])?, v)))
            .collect::<Result<Vec<_>>>()?;
        decorated.sort_by(|a, b| cmp(&a.0, &b.0).unwrap_or(std::cmp::Ordering::Equal));
        values = decorated.into_iter().map(|(_, v)| v).collect();
    } else {
        values.sort_by(|a, b| cmp(a, b).unwrap_or(std::cmp::Ordering::Equal));
    }
    if option(kwargs, "reverse")
        .map(|v| v.truthy())
        .transpose()?
        .unwrap_or(false)
    {
        values.reverse();
    }
    Ok(values)
}
fn construct(name: &str, args: Args, kwargs: Kwargs) -> Result<Val> {
    let first = args.first().cloned().unwrap_or(Val::None);
    Ok(match name {
        "str" => {
            if args.is_empty() {
                "".into()
            } else {
                first.str()?.into()
            }
        }
        "bool" => first.truthy()?.into(),
        "int" => {
            if let Val::Str(s) = first {
                Val::Int(i64::from_str_radix(
                    s.trim(),
                    args.get(1).map(Val::integer).transpose()?.unwrap_or(10) as u32,
                )?)
            } else {
                Val::Int(first.integer().unwrap_or(0))
            }
        }
        "float" => {
            if let Val::Str(s) = first {
                Val::Float(s.parse()?)
            } else {
                Val::Float(first.num().unwrap_or(0.))
            }
        }
        "list" => Val::list(if args.is_empty() {
            vec![]
        } else {
            first.iter()?
        }),
        "tuple" => Val::Tuple(if args.is_empty() {
            vec![]
        } else {
            first.iter()?
        }),
        "set" => Val::set_values(if args.is_empty() {
            vec![]
        } else {
            first.iter()?
        }),
        "frozenset" => Val::frozen_set(if args.is_empty() {
            vec![]
        } else {
            first.iter()?
        }),
        "dict" => {
            let out = Val::dict(if args.is_empty() {
                vec![]
            } else {
                entries_of(&first)?
            });
            for (k, v) in kwargs {
                out.set(k.into(), v)?;
            }
            out
        }
        "bytes" => match first {
            Val::Bytes(v) => Val::Bytes(v),
            Val::Str(s) => Val::Bytes(s.into_bytes()),
            Val::Int(n) => Val::Bytes(vec![0; n as usize]),
            Val::None => Val::Bytes(vec![]),
            _ => Val::Bytes(
                first
                    .iter()?
                    .iter()
                    .map(|v| Ok(v.integer()? as u8))
                    .collect::<Result<_>>()?,
            ),
        },
        "Path" => {
            let mut path = PathBuf::new();
            for arg in args {
                path.push(arg.str()?);
            }
            Val::Path(path)
        }
        "bytearray" | "memoryview" => {
            let module = Val::decode(callback(json!({"op":"import","module":"builtins"}))?)?;
            module.attr(name)?.call(args, kwargs)?
        }
        _ => bail!("unknown native type {name}"),
    })
}
pub fn import(name: &str) -> Result<Val> {
    if let Some(module) = builtin_module(name) {
        return Ok(module);
    }
    Val::decode(callback(json!({"op":"import","module":name}))?)
}
pub fn builtin(name: &str) -> Option<Val> {
    if [
        "str",
        "bytearray",
        "memoryview",
        "int",
        "float",
        "bool",
        "list",
        "tuple",
        "dict",
        "set",
        "frozenset",
        "bytes",
        "Path",
    ]
    .contains(&name)
    {
        return Some(Val::Type(name.into()));
    }
    let name = name.to_owned();
    if ![
        "len",
        "range",
        "enumerate",
        "zip",
        "sum",
        "min",
        "max",
        "sorted",
        "reversed",
        "abs",
        "round",
        "any",
        "all",
        "repr",
        "format",
        "map",
        "filter",
        "next",
        "iter",
        "isinstance",
        "getattr",
        "hasattr",
        "setattr",
        "callable",
        "print",
        "ord",
        "chr",
        "hex",
        "open",
        "vars",
        "id",
        "type",
    ]
    .contains(&name.as_str())
    {
        return None;
    }
    Some(Val::function(move |args, kwargs| {
        Ok(match name.as_str() {
            "len" => Val::Int(arg(&args, 0)?.len()? as i64),
            "range" => {
                let (start, end, step) = match args.len() {
                    1 => (0, args[0].integer()?, 1),
                    2 => (args[0].integer()?, args[1].integer()?, 1),
                    _ => (
                        arg(&args, 0)?.integer()?,
                        arg(&args, 1)?.integer()?,
                        arg(&args, 2)?.integer()?,
                    ),
                };
                ensure!(step != 0, "range step zero");
                let mut out = Vec::new();
                let mut i = start;
                while if step > 0 { i < end } else { i > end } {
                    out.push(Val::Int(i));
                    i += step;
                }
                Val::list(out)
            }
            "enumerate" => {
                let start = args.get(1).map(Val::integer).transpose()?.unwrap_or(0);
                Val::list(
                    arg(&args, 0)?
                        .iter()?
                        .into_iter()
                        .enumerate()
                        .map(|(i, v)| Val::Tuple(vec![Val::Int(start + i as i64), v]))
                        .collect(),
                )
            }
            "zip" => {
                let columns = args.iter().map(Val::iter).collect::<Result<Vec<_>>>()?;
                let length = columns.iter().map(Vec::len).min().unwrap_or(0);
                if option(&kwargs, "strict")
                    .map(|v| v.truthy())
                    .transpose()?
                    .unwrap_or(false)
                {
                    ensure!(
                        columns.iter().all(|c| c.len() == length),
                        "zip argument lengths differ"
                    );
                }
                Val::list(
                    (0..length)
                        .map(|i| Val::Tuple(columns.iter().map(|c| c[i].clone()).collect()))
                        .collect(),
                )
            }
            "sum" => {
                let mut out = args.get(1).cloned().unwrap_or(Val::Int(0));
                for value in arg(&args, 0)?.iter()? {
                    out = binary("add", out, value)?;
                }
                out
            }
            "min" | "max" => {
                let values = if args.len() == 1 {
                    args[0].iter()?
                } else {
                    args
                };
                let mut best = option(&kwargs, "default");
                let key = option(&kwargs, "key");
                let mut best_key = None;
                for v in values {
                    let k = if let Some(key) = &key {
                        key.call(vec![v.clone()], vec![])?
                    } else {
                        v.clone()
                    };
                    if best_key
                        .as_ref()
                        .map(|b| cmp(&k, b))
                        .transpose()?
                        .map_or(true, |o| if name == "min" { o.is_lt() } else { o.is_gt() })
                    {
                        best = Some(v);
                        best_key = Some(k);
                    }
                }
                best.context("empty min/max")?
            }
            "sorted" => Val::list(sorted(arg(&args, 0)?.iter()?, &kwargs)?),
            "reversed" => {
                let mut out = arg(&args, 0)?.iter()?;
                out.reverse();
                Val::list(out)
            }
            "abs" => {
                let v = arg(&args, 0)?;
                match v {
                    Val::Int(n) => Val::Int(n.abs()),
                    _ => Val::Float(v.num()?.abs()),
                }
            }
            "round" => {
                let x = arg(&args, 0)?.num()?;
                if let Some(d) = args.get(1) {
                    let d = d.integer()?;
                    Val::Float(if d >= 0 {
                        crate::format_number(x, &format!(".{d}f"))?.parse()?
                    } else {
                        let scale = 10f64.powi(-d as i32);
                        (x / scale).round_ties_even() * scale
                    })
                } else {
                    Val::Int(x.round_ties_even() as i64)
                }
            }
            "any" | "all" => {
                let values = arg(&args, 0)?.iter()?;
                let mut answer = name == "all";
                for value in values {
                    let truth = value.truthy()?;
                    if name == "any" && truth {
                        answer = true;
                        break;
                    }
                    if name == "all" && !truth {
                        answer = false;
                        break;
                    }
                }
                answer.into()
            }
            "repr" => arg(&args, 0)?.repr()?.into(),
            "format" => format(
                &arg(&args, 0)?,
                &args.get(1).map(Val::str).transpose()?.unwrap_or_default(),
            )?
            .into(),
            "map" => {
                let f = arg(&args, 0)?;
                let lists = args[1..]
                    .iter()
                    .map(Val::iter)
                    .collect::<Result<Vec<_>>>()?;
                let n = lists.iter().map(Vec::len).min().unwrap_or(0);
                Val::list(
                    (0..n)
                        .map(|i| f.call(lists.iter().map(|v| v[i].clone()).collect(), vec![]))
                        .collect::<Result<_>>()?,
                )
            }
            "filter" => {
                let f = arg(&args, 0)?;
                let mut out = Vec::new();
                for v in arg(&args, 1)?.iter()? {
                    let keep = if matches!(f, Val::None) {
                        v.truthy()?
                    } else {
                        f.call(vec![v.clone()], vec![])?.truthy()?
                    };
                    if keep {
                        out.push(v)
                    }
                }
                Val::list(out)
            }
            "iter" => {
                let values = Rc::new(RefCell::new(arg(&args, 0)?.iter()?.into_iter()));
                Val::function(move |_, _| values.borrow_mut().next().context("StopIteration"))
            }
            "next" => {
                let v = arg(&args, 0)?;
                let result = if matches!(v, Val::Func(_)) {
                    v.call(vec![], vec![])
                } else if matches!(v, Val::Ref(_)) {
                    remote("next", &v, json!({}))
                } else {
                    v.iter()?.into_iter().next().context("StopIteration")
                };
                match result {
                    Ok(v) => v,
                    Err(e) => {
                        if let Some(default) = args.get(1) {
                            default.clone()
                        } else {
                            return Err(e);
                        }
                    }
                }
            }
            "getattr" => {
                let value = arg(&args, 0)?;
                match value.attr(&arg(&args, 1)?.str()?) {
                    Ok(v) => v,
                    Err(e) => {
                        if let Some(default) = args.get(2) {
                            default.clone()
                        } else {
                            return Err(e);
                        }
                    }
                }
            }
            "hasattr" => arg(&args, 0)?.attr(&arg(&args, 1)?.str()?).is_ok().into(),
            "setattr" => {
                arg(&args, 0)?.setattr(&arg(&args, 1)?.str()?, arg(&args, 2)?)?;
                Val::None
            }
            "callable" => {
                let value = arg(&args, 0)?;
                if matches!(value, Val::Ref(_)) {
                    let module =
                        Val::decode(callback(json!({"op":"import","module":"builtins"}))?)?;
                    module.attr("callable")?.call(vec![value], vec![])?
                } else {
                    matches!(value, Val::Func(_) | Val::Type(_)).into()
                }
            }
            "isinstance" => is_instance(&arg(&args, 0)?, &arg(&args, 1)?)?.into(),
            "ord" => Val::Int(
                arg(&args, 0)?
                    .str()?
                    .chars()
                    .next()
                    .context("ord empty string")? as i64,
            ),
            "chr" => char::from_u32(arg(&args, 0)?.integer()? as u32)
                .context("invalid code point")?
                .to_string()
                .into(),
            "hex" => format!("{:#x}", arg(&args, 0)?.integer()?).into(),
            "print" => {
                let sep = option(&kwargs, "sep")
                    .map(|v| v.str())
                    .transpose()?
                    .unwrap_or_else(|| " ".into());
                let _ = sep;
                let module = Val::decode(callback(json!({"op":"import","module":"builtins"}))?)?;
                module.attr("print")?.call(args, kwargs)?
            }
            "open" => {
                if let Some(p) = args.first() {
                    if let Ok(path) = p.str() {
                        let mode = args
                            .get(1)
                            .map(Val::str)
                            .transpose()?
                            .unwrap_or_else(|| "r".into());
                        note_io(Path::new(&path), mode.contains(['w', 'a', '+']));
                    }
                }
                let builtins = Val::decode(callback(json!({"op":"import","module":"builtins"}))?)?;
                builtins.attr("open")?.call(args, kwargs)?
            }
            "type" => {
                let v = arg(&args, 0)?;
                match v {
                    Val::None => Val::Type("NoneType".into()),
                    Val::Bool(_) => Val::Type("bool".into()),
                    Val::Int(_) => Val::Type("int".into()),
                    Val::Float(_) => Val::Type("float".into()),
                    Val::Str(_) => Val::Type("str".into()),
                    Val::Bytes(_) => Val::Type("bytes".into()),
                    Val::List(_) => Val::Type("list".into()),
                    Val::Tuple(_) => Val::Type("tuple".into()),
                    Val::Dict(_) => Val::Type("dict".into()),
                    Val::Set(_) => Val::Type("set".into()),
                    Val::FrozenSet(_) => Val::Type("frozenset".into()),
                    v => Val::decode(callback(json!({"op":"import","module":"builtins"}))?)?
                        .attr("type")?
                        .call(vec![v], vec![])?,
                }
            }
            "id" => {
                let v = arg(&args, 0)?;
                if matches!(v, Val::Ref(_)) {
                    Val::decode(callback(json!({"op":"import","module":"builtins"}))?)?
                        .attr("id")?
                        .call(vec![v], vec![])?
                } else if let Some(id) = v.encode_ref()?["$native"]["id"].as_i64() {
                    Val::Int(id)
                } else {
                    Val::Int(v.integer().unwrap_or(0))
                }
            }
            "vars" => match arg(&args, 0)? {
                Val::Namespace(v) => Val::Dict(v),
                v => {
                    let builtins =
                        Val::decode(callback(json!({"op":"import","module":"builtins"}))?)?;
                    builtins.attr("vars")?.call(vec![v], kwargs)?
                }
            },
            _ => bail!("unsupported builtin {name}"),
        })
    }))
}
fn is_instance(value: &Val, kind: &Val) -> Result<bool> {
    if matches!(value, Val::Ref(_)) && matches!(kind, Val::Type(_)) {
        let module = Val::decode(callback(json!({"op":"import","module":"builtins"}))?)?;
        return module
            .attr("isinstance")?
            .call(vec![value.clone(), kind.clone()], vec![])?
            .truthy();
    }
    match kind {
        Val::Tuple(kinds) => {
            for k in kinds {
                if is_instance(value, k)? {
                    return Ok(true);
                }
            }
            Ok(false)
        }
        Val::Type(name) => Ok(match name.as_str() {
            "NoneType" => matches!(value, Val::None),
            "str" => matches!(value, Val::Str(_)),
            "int" => matches!(value, Val::Int(_) | Val::Bool(_)),
            "float" => matches!(value, Val::Float(_)),
            "bool" => matches!(value, Val::Bool(_)),
            "list" => matches!(value, Val::List(_)),
            "tuple" => matches!(value, Val::Tuple(_)),
            "dict" => matches!(value, Val::Dict(_)),
            "set" => matches!(value, Val::Set(_)),
            "frozenset" => matches!(value, Val::FrozenSet(_)),
            "bytes" => matches!(value, Val::Bytes(_)),
            "Path" => matches!(value, Val::Path(_)),
            _ => false,
        }),
        Val::Ref(_) => {
            let b = Val::decode(callback(json!({"op":"import","module":"builtins"}))?)?;
            b.attr("isinstance")?
                .call(vec![value.clone(), kind.clone()], vec![])?
                .truthy()
        }
        _ => Ok(false),
    }
}
/// The percent formatting used by authored text and file compositions.
fn percent_format(pattern: &str, values: &Val) -> Result<String> {
    let fields = if let Val::Tuple(values) = values {
        values.clone()
    } else {
        vec![values.clone()]
    };
    let mut field = 0usize;
    let mut at = 0usize;
    let chars = pattern.chars().collect::<Vec<_>>();
    let mut out = String::new();
    let take = |field: &mut usize| -> Result<Val> {
        let value = fields
            .get(*field)
            .cloned()
            .context("not enough arguments for format string")?;
        *field += 1;
        Ok(value)
    };
    while at < chars.len() {
        if chars[at] != '%' {
            out.push(chars[at]);
            at += 1;
            continue;
        }
        at += 1;
        ensure!(at < chars.len(), "incomplete format string");
        if chars[at] == '%' {
            out.push('%');
            at += 1;
            continue;
        }
        let key = if chars[at] == '(' {
            at += 1;
            let start = at;
            let mut depth = 1;
            while at < chars.len() {
                if chars[at] == '(' {
                    depth += 1;
                }
                if chars[at] == ')' {
                    depth -= 1;
                    if depth == 0 {
                        break;
                    }
                }
                at += 1;
            }
            ensure!(at < chars.len(), "incomplete format key");
            let key = chars[start..at].iter().collect::<String>();
            at += 1;
            Some(key)
        } else {
            None
        };
        let mut left = false;
        let mut plus = false;
        let mut space = false;
        let mut zero = false;
        let mut alternate = false;
        while at < chars.len() && "-+ 0#".contains(chars[at]) {
            match chars[at] {
                '-' => left = true,
                '+' => plus = true,
                ' ' => space = true,
                '0' => zero = true,
                '#' => alternate = true,
                _ => (),
            }
            at += 1;
        }
        let mut width = 0usize;
        if chars.get(at) == Some(&'*') {
            let n = take(&mut field)?.integer()?;
            left |= n < 0;
            width = n.unsigned_abs() as usize;
            at += 1;
        } else {
            while chars.get(at).is_some_and(char::is_ascii_digit) {
                width = width * 10 + chars[at].to_digit(10).unwrap() as usize;
                at += 1;
            }
        }
        let mut precision = None;
        if chars.get(at) == Some(&'.') {
            at += 1;
            if chars.get(at) == Some(&'*') {
                precision = Some(take(&mut field)?.integer()?.max(0) as usize);
                at += 1;
            } else {
                let mut n = 0usize;
                while chars.get(at).is_some_and(char::is_ascii_digit) {
                    n = n * 10 + chars[at].to_digit(10).unwrap() as usize;
                    at += 1;
                }
                precision = Some(n);
            }
        }
        if chars.get(at).is_some_and(|c| "hlL".contains(*c)) {
            at += 1;
        }
        let kind = *chars.get(at).context("incomplete format string")?;
        at += 1;
        let value = if let Some(key) = key {
            values.get(Val::Str(key))?
        } else {
            take(&mut field)?
        };
        let mut text = match kind {
            's' | 'r' | 'a' => {
                let s = if kind == 's' {
                    value.str()?
                } else {
                    value.repr()?
                };
                if let Some(n) = precision {
                    s.chars().take(n).collect()
                } else {
                    s
                }
            }
            'c' => {
                if let Val::Str(s) = value {
                    ensure!(s.chars().count() == 1, "%c requires a single character");
                    s
                } else {
                    char::from_u32(value.integer()? as u32)
                        .context("%c character out of range")?
                        .to_string()
                }
            }
            'd' | 'i' | 'u' | 'o' | 'x' | 'X' => {
                let n = value.num()?.trunc() as i64;
                let magnitude = n.unsigned_abs();
                let mut digits = match kind {
                    'o' => format!("{magnitude:o}"),
                    'x' => format!("{magnitude:x}"),
                    'X' => format!("{magnitude:X}"),
                    _ => magnitude.to_string(),
                };
                if let Some(n) = precision {
                    if digits.len() < n {
                        digits = "0".repeat(n - digits.len()) + &digits;
                    }
                }
                let prefix = if alternate {
                    match kind {
                        'o' => "0o",
                        'x' => "0x",
                        'X' => "0X",
                        _ => "",
                    }
                } else {
                    ""
                };
                format!(
                    "{}{}{}",
                    if n < 0 {
                        "-"
                    } else if plus {
                        "+"
                    } else if space {
                        " "
                    } else {
                        ""
                    },
                    prefix,
                    digits
                )
            }
            'e' | 'E' | 'f' | 'F' | 'g' | 'G' => {
                let spec = format!(
                    "{}.{precision}{kind}",
                    if plus {
                        "+"
                    } else if space {
                        " "
                    } else {
                        ""
                    },
                    precision = precision.unwrap_or(6)
                );
                let mut s = crate::format_number(value.num()?, &spec)?;
                if alternate
                    && !s.contains('.')
                    && !s.to_ascii_lowercase().contains("inf")
                    && !s.to_ascii_lowercase().contains("nan")
                {
                    let pos = s.find(['e', 'E']).unwrap_or(s.len());
                    s.insert(pos, '.');
                }
                s
            }
            _ => bail!("unsupported percent format {kind}"),
        };
        let n = text.chars().count();
        if width > n {
            let pad = width - n;
            if left {
                text.push_str(&" ".repeat(pad));
            } else if zero && !matches!(kind, 's' | 'r' | 'a' | 'c') {
                let mut prefix = usize::from(text.starts_with(['-', '+', ' ']));
                if ["0x", "0X", "0o"]
                    .iter()
                    .any(|p| text[prefix..].starts_with(p))
                {
                    prefix += 2;
                }
                text = text[..prefix].to_owned() + &"0".repeat(pad) + &text[prefix..];
            } else {
                text = " ".repeat(pad) + &text;
            }
        }
        out.push_str(&text);
    }
    ensure!(
        field == fields.len() || matches!(values, Val::Dict(_) | Val::Ref(_)),
        "not all arguments converted during string formatting"
    );
    Ok(out)
}

pub fn format(value: &Val, spec: &str) -> Result<String> {
    if spec.is_empty() {
        return value.str();
    }
    let chars = spec.chars().collect::<Vec<_>>();
    let mut at = 0;
    let mut fill = ' ';
    let mut align = if matches!(value, Val::Str(_)) {
        '<'
    } else {
        '>'
    };
    let mut explicit_align = false;
    if chars.len() > 1 && matches!(chars[1], '<' | '>' | '^' | '=') {
        fill = chars[0];
        align = chars[1];
        at = 2;
        explicit_align = true;
    } else if chars
        .first()
        .is_some_and(|c| matches!(c, '<' | '>' | '^' | '='))
    {
        align = chars[0];
        at = 1;
        explicit_align = true;
    }
    let sign = if chars.get(at).is_some_and(|c| matches!(c, '+' | '-' | ' ')) {
        let s = chars[at];
        at += 1;
        Some(s)
    } else {
        None
    };
    let alternate = chars.get(at) == Some(&'#');
    if alternate {
        at += 1;
    }
    let zero = chars.get(at) == Some(&'0');
    if zero {
        fill = '0';
        if !explicit_align && !matches!(value, Val::Str(_)) {
            align = '=';
        }
    }
    let mut width = 0usize;
    while chars.get(at).is_some_and(char::is_ascii_digit) {
        width = width * 10 + chars[at].to_digit(10).unwrap() as usize;
        at += 1;
    }
    let grouping = if chars.get(at).is_some_and(|c| matches!(c, ',' | '_')) {
        let c = chars[at];
        at += 1;
        Some(c)
    } else {
        None
    };
    let precision = if chars.get(at) == Some(&'.') {
        at += 1;
        let mut n = 0usize;
        while chars.get(at).is_some_and(char::is_ascii_digit) {
            n = n * 10 + chars[at].to_digit(10).unwrap() as usize;
            at += 1;
        }
        Some(n)
    } else {
        None
    };
    let kind = chars.get(at).copied();
    let mut text = if let Val::Str(text) = value {
        let text = if let Some(n) = precision {
            text.chars().take(n).collect()
        } else {
            text.clone()
        };
        text
    } else if matches!(value, Val::Int(_) | Val::Bool(_))
        && kind.is_none_or(|c| matches!(c, 'd' | 'b' | 'o' | 'x' | 'X' | 'n'))
    {
        let n = value.integer()?;
        let magnitude = n.unsigned_abs();
        let kind = kind.unwrap_or('d');
        let mut digits = match kind {
            'b' => format!("{magnitude:b}"),
            'o' => format!("{magnitude:o}"),
            'x' => format!("{magnitude:x}"),
            'X' => format!("{magnitude:X}"),
            _ => magnitude.to_string(),
        };
        if let Some(separator) = grouping {
            let mut out = String::new();
            let group = if separator == '_' && matches!(kind, 'b' | 'o' | 'x' | 'X') {
                4
            } else {
                3
            };
            for (i, c) in digits.chars().enumerate() {
                if i > 0 && (digits.len() - i) % group == 0 {
                    out.push(separator);
                }
                out.push(c);
            }
            digits = out;
        }
        let prefix = if alternate {
            match kind {
                'b' => "0b",
                'o' => "0o",
                'x' => "0x",
                'X' => "0X",
                _ => "",
            }
        } else {
            ""
        };
        format!(
            "{}{}{}",
            if n < 0 {
                "-"
            } else if sign == Some('+') {
                "+"
            } else if sign == Some(' ') {
                " "
            } else {
                ""
            },
            prefix,
            digits
        )
    } else if kind.is_none() && precision.is_none() {
        let mut text = value.str()?;
        if !text.starts_with('-') {
            if sign == Some('+') {
                text.insert(0, '+')
            } else if sign == Some(' ') {
                text.insert(0, ' ')
            }
        }
        text
    } else {
        let mut numeric = String::new();
        if let Some(sign) = sign.filter(|&s| s != '-') {
            numeric.push(sign);
        }
        if grouping == Some(',') {
            numeric.push(',');
        }
        if let Some(n) = precision {
            numeric.push_str(&format!(".{n}"));
        }
        numeric.push(kind.unwrap_or('g'));
        let mut text = crate::format_number(value.num()?, &numeric)?;
        if kind.is_none() && !text.contains(['.', 'e', 'E']) {
            text.push_str(".0");
        }
        text
    };
    let length = text.chars().count();
    if length >= width {
        return Ok(text);
    }
    let pad = width - length;
    let padding = fill.to_string().repeat(pad);
    if align == '=' {
        let mut prefix = usize::from(text.starts_with(['-', '+', ' ']));
        if ["0x", "0X", "0b", "0o"]
            .iter()
            .any(|p| text[prefix..].starts_with(p))
        {
            prefix += 2;
        }
        text = text[..prefix].to_owned() + &padding + &text[prefix..];
        return Ok(text);
    }
    Ok(match align {
        '<' => text + &padding,
        '^' => fill.to_string().repeat(pad / 2) + &text + &fill.to_string().repeat(pad - pad / 2),
        _ => padding + &text,
    })
}

thread_local! {
    static INPUTS:RefCell<Vec<PathBuf>>=const {RefCell::new(Vec::new())};
    static OUTPUTS:RefCell<Vec<PathBuf>>=const {RefCell::new(Vec::new())};
}
pub fn note_io(path: &Path, write: bool) {
    let path = if path.is_absolute() {
        path.to_owned()
    } else {
        std::env::current_dir().unwrap_or_default().join(path)
    };
    let register = |paths: &RefCell<Vec<PathBuf>>| {
        let mut paths = paths.borrow_mut();
        if !paths.contains(&path) {
            paths.push(path.clone())
        }
    };
    if write {
        OUTPUTS.with(register)
    } else {
        INPUTS.with(register)
    }
}
pub fn io_paths() -> (Vec<PathBuf>, Vec<PathBuf>) {
    (
        INPUTS.with(|p| p.borrow().clone()),
        OUTPUTS.with(|p| p.borrow().clone()),
    )
}
pub fn clear_io() {
    INPUTS.with(|p| p.borrow_mut().clear());
    OUTPUTS.with(|p| p.borrow_mut().clear());
}
fn resolved(path: &Path) -> Result<PathBuf> {
    if let Ok(found) = std::fs::canonicalize(path) {
        return Ok(found);
    }
    let absolute = if path.is_absolute() {
        path.to_owned()
    } else {
        std::env::current_dir()?.join(path)
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
    Ok(clean)
}
fn path_attr(path: &Path, name: &str) -> Result<Val> {
    ensure!(
        [
            "parent",
            "parents",
            "name",
            "stem",
            "suffix",
            "parts",
            "resolve",
            "absolute",
            "exists",
            "is_file",
            "is_dir",
            "is_absolute",
            "as_posix",
            "as_uri",
            "with_name",
            "with_suffix",
            "joinpath",
            "relative_to",
            "is_relative_to",
            "mkdir",
            "read_bytes",
            "read_text",
            "write_bytes",
            "write_text",
            "unlink",
            "rename",
            "replace",
            "stat",
            "glob",
            "rglob",
            "iterdir",
            "open"
        ]
        .contains(&name),
        "Path has no attribute {name}"
    );
    let field = match name {
        "parent" => Some(Val::Path(path.parent().unwrap_or(path).to_owned())),
        "parents" => Some(Val::Tuple(
            path.ancestors()
                .skip(1)
                .map(|p| Val::Path(p.to_owned()))
                .collect(),
        )),
        "name" => Some(
            path.file_name()
                .map(|v| v.to_string_lossy().to_string())
                .unwrap_or_default()
                .into(),
        ),
        "stem" => Some(
            path.file_stem()
                .map(|v| v.to_string_lossy().to_string())
                .unwrap_or_default()
                .into(),
        ),
        "suffix" => Some(
            path.extension()
                .map(|v| format!(".{}", v.to_string_lossy()))
                .unwrap_or_default()
                .into(),
        ),
        "parts" => Some(Val::Tuple(
            path.components()
                .map(|v| Val::Str(v.as_os_str().to_string_lossy().into()))
                .collect(),
        )),
        _ => None,
    };
    if let Some(field) = field {
        return Ok(field);
    }
    let path = path.to_owned();
    let name = name.to_owned();
    Ok(Val::function(move |args, kwargs| {
        Ok(match name.as_str() {
            "resolve" | "absolute" => Val::Path(resolved(&path)?),
            "exists" => path.exists().into(),
            "is_file" => path.is_file().into(),
            "is_dir" => path.is_dir().into(),
            "is_absolute" => path.is_absolute().into(),
            "as_posix" => path.to_string_lossy().to_string().into(),
            "as_uri" => {
                let absolute = resolved(&path)?;
                let mut uri = "file://".to_owned();
                for byte in absolute.to_string_lossy().as_bytes() {
                    if byte.is_ascii_alphanumeric() || b"/-._~".contains(byte) {
                        uri.push(*byte as char)
                    } else {
                        uri.push_str(&format!("%{byte:02X}"));
                    }
                }
                uri.into()
            }
            "with_name" => Val::Path(path.with_file_name(arg(&args, 0)?.str()?)),
            "with_suffix" => {
                let suffix = arg(&args, 0)?.str()?;
                ensure!(
                    suffix.is_empty() || suffix.starts_with('.'),
                    "invalid suffix"
                );
                let mut p = path.clone();
                p.set_extension(suffix.trim_start_matches('.'));
                Val::Path(p)
            }
            "joinpath" => {
                let mut out = path.clone();
                for part in args {
                    out.push(part.str()?);
                }
                Val::Path(out)
            }
            "relative_to" => Val::Path(path.strip_prefix(arg(&args, 0)?.str()?)?.to_owned()),
            "is_relative_to" => path.starts_with(arg(&args, 0)?.str()?).into(),
            "mkdir" => {
                let parents = option(&kwargs, "parents")
                    .map(|v| v.truthy())
                    .transpose()?
                    .unwrap_or(false);
                let exist = option(&kwargs, "exist_ok")
                    .map(|v| v.truthy())
                    .transpose()?
                    .unwrap_or(false);
                let result = if parents {
                    std::fs::create_dir_all(&path)
                } else {
                    std::fs::create_dir(&path)
                };
                if let Err(e) = result {
                    if !exist || e.kind() != std::io::ErrorKind::AlreadyExists {
                        return Err(e.into());
                    }
                }
                Val::None
            }
            "read_bytes" => {
                note_io(&path, false);
                Val::Bytes(std::fs::read(&path)?)
            }
            "read_text" => {
                note_io(&path, false);
                std::fs::read_to_string(&path)?
                    .replace("\r\n", "\n")
                    .replace('\r', "\n")
                    .into()
            }
            "write_bytes" => {
                let bytes = match arg(&args, 0)? {
                    Val::Bytes(b) => b,
                    other => other.str()?.into_bytes(),
                };
                std::fs::write(&path, &bytes)?;
                note_io(&path, true);
                Val::Int(bytes.len() as i64)
            }
            "write_text" => {
                let text = arg(&args, 0)?.str()?;
                std::fs::write(&path, &text)?;
                note_io(&path, true);
                Val::Int(text.chars().count() as i64)
            }
            "unlink" => {
                let result = std::fs::remove_file(&path);
                let missing = option(&kwargs, "missing_ok")
                    .map(|v| v.truthy())
                    .transpose()?
                    .unwrap_or(false);
                if let Err(e) = result {
                    if !missing || e.kind() != std::io::ErrorKind::NotFound {
                        return Err(e.into());
                    }
                }
                note_io(&path, true);
                Val::None
            }
            "rename" | "replace" => {
                let target = PathBuf::from(arg(&args, 0)?.str()?);
                std::fs::rename(&path, &target)?;
                note_io(&path, false);
                note_io(&target, true);
                Val::Path(target)
            }
            "stat" => {
                let m = std::fs::metadata(&path)?;
                let time = m
                    .modified()?
                    .duration_since(std::time::UNIX_EPOCH)?
                    .as_secs_f64();
                Val::namespace(vec![
                    ("st_size".into(), Val::Int(m.len() as i64)),
                    ("st_mtime".into(), time.into()),
                    ("st_mtime_ns".into(), Val::Int((time * 1e9) as i64)),
                ])
            }
            "glob" | "rglob" => {
                let pattern = arg(&args, 0)?.str()?;
                let mut paths = Vec::new();
                walk_paths(&path, &pattern, name == "rglob", &mut paths)?;
                Val::list(paths.into_iter().map(Val::Path).collect())
            }
            "iterdir" => Val::list(
                std::fs::read_dir(&path)?
                    .map(|e| Ok(Val::Path(e?.path())))
                    .collect::<Result<_>>()?,
            ),
            "open" => {
                let builtins = Val::decode(callback(json!({"op":"import","module":"builtins"}))?)?;
                let mut all = vec![Val::Path(path.clone())];
                all.extend(args);
                builtins.attr("open")?.call(all, kwargs)?
            }
            _ => bail!("unsupported Path method {name}"),
        })
    }))
}
fn glob_match(pattern: &str, text: &str) -> bool {
    if pattern == "*" {
        return true;
    }
    if let Some((a, b)) = pattern.split_once('*') {
        return text.starts_with(a) && text.ends_with(b);
    }
    pattern == text
}
fn walk_paths(path: &Path, pattern: &str, recurse: bool, out: &mut Vec<PathBuf>) -> Result<()> {
    if !path.is_dir() {
        return Ok(());
    }
    for entry in std::fs::read_dir(path)? {
        let p = entry?.path();
        let name = p.file_name().unwrap().to_string_lossy();
        if glob_match(pattern, &name) {
            out.push(p.clone())
        }
        if recurse && p.is_dir() {
            walk_paths(&p, pattern, true, out)?;
        }
    }
    Ok(())
}
pub fn builtin_module(name: &str) -> Option<Val> {
    if let Some(module) = standard::module(name) {
        return Some(module);
    }
    match name {
        "pathlib" => Some(Val::namespace(vec![
            ("Path".into(), Val::Type("Path".into())),
            ("PurePath".into(), Val::Type("Path".into())),
        ])),
        "math" => {
            let mut entries = vec![
                ("pi".into(), std::f64::consts::PI.into()),
                ("tau".into(), std::f64::consts::TAU.into()),
                ("e".into(), std::f64::consts::E.into()),
                ("inf".into(), f64::INFINITY.into()),
            ];
            for name in [
                "sqrt", "sin", "cos", "tan", "asin", "acos", "atan", "atan2", "ceil", "floor",
                "trunc", "fabs", "hypot", "dist", "radians", "degrees", "copysign", "isfinite",
                "isnan", "isinf", "isclose", "log", "log2", "log10", "exp", "comb",
            ] {
                let name = name.to_owned();
                let key = name.clone();
                entries.push((
                    key.into(),
                    Val::function(move |args, kwargs| {
                        let x = arg(&args, 0)?.num().ok();
                        let get = || x.context("math numeric argument");
                        Ok(match name.as_str() {
                            "sqrt" => {
                                let x = get()?;
                                ensure!(x >= 0., "math domain error");
                                x.sqrt().into()
                            }
                            "sin" => get()?.sin().into(),
                            "cos" => get()?.cos().into(),
                            "tan" => get()?.tan().into(),
                            "asin" => {
                                let x = get()?.asin();
                                ensure!(x.is_finite(), "math domain error");
                                x.into()
                            }
                            "acos" => {
                                let x = get()?.acos();
                                ensure!(x.is_finite(), "math domain error");
                                x.into()
                            }
                            "atan" => get()?.atan().into(),
                            "atan2" => get()?.atan2(arg(&args, 1)?.num()?).into(),
                            "ceil" => Val::Int(get()?.ceil() as i64),
                            "floor" => Val::Int(get()?.floor() as i64),
                            "trunc" => Val::Int(get()?.trunc() as i64),
                            "fabs" => get()?.abs().into(),
                            "hypot" => args
                                .iter()
                                .map(Val::num)
                                .collect::<Result<Vec<_>>>()?
                                .iter()
                                .fold(0f64, |a, &b| a.hypot(b))
                                .into(),
                            "dist" => {
                                let a = arg(&args, 0)?.iter()?;
                                let b = arg(&args, 1)?.iter()?;
                                ensure!(a.len() == b.len(), "distance dimensions");
                                let mut n = 0f64;
                                for (a, b) in a.iter().zip(&b) {
                                    n = n.hypot(a.num()? - b.num()?);
                                }
                                n.into()
                            }
                            "radians" => (get()? * std::f64::consts::PI / 180.).into(),
                            "degrees" => (get()? * 180. / std::f64::consts::PI).into(),
                            "copysign" => get()?.copysign(arg(&args, 1)?.num()?).into(),
                            "isfinite" => get()?.is_finite().into(),
                            "isnan" => get()?.is_nan().into(),
                            "isinf" => get()?.is_infinite().into(),
                            "isclose" => {
                                let a = get()?;
                                let b = arg(&args, 1)?.num()?;
                                let rel = option(&kwargs, "rel_tol")
                                    .map(|v| v.num())
                                    .transpose()?
                                    .unwrap_or(1e-9);
                                let abs = option(&kwargs, "abs_tol")
                                    .map(|v| v.num())
                                    .transpose()?
                                    .unwrap_or(0.);
                                ((a - b).abs() <= abs.max(rel * a.abs().max(b.abs()))).into()
                            }
                            "log" => {
                                let value = get()?.ln();
                                if let Some(base) = args.get(1) {
                                    (value / base.num()?.ln()).into()
                                } else {
                                    value.into()
                                }
                            }
                            "log2" => get()?.log2().into(),
                            "log10" => get()?.log10().into(),
                            "exp" => get()?.exp().into(),
                            "comb" => {
                                let n = arg(&args, 0)?.integer()?;
                                let k =
                                    arg(&args, 1)?.integer()?.min(n - arg(&args, 1)?.integer()?);
                                let mut out = 1i64;
                                for i in 0..k {
                                    out = out * (n - i) / (i + 1);
                                }
                                Val::Int(out)
                            }
                            _ => bail!("unknown native math function {name}"),
                        })
                    }),
                ));
            }
            Some(Val::namespace(entries))
        }
        _ => None,
    }
}

thread_local! {
    static NATIVE_OBJECTS:RefCell<Vec<Val>>=const{RefCell::new(Vec::new())};
    static FUNCTION_ATTRIBUTES:RefCell<std::collections::HashMap<usize,Entries>>=RefCell::new(std::collections::HashMap::new());
}
fn set_items(value: &Val) -> Option<Vec<Val>> {
    match value {
        Val::Set(values) => Some(values.borrow().clone()),
        Val::FrozenSet(values) => Some(values.clone()),
        _ => None,
    }
}
fn same_identity(a: &Val, b: &Val) -> bool {
    match (a, b) {
        (Val::Func(a), Val::Func(b)) => Rc::ptr_eq(a, b),
        (Val::List(a), Val::List(b)) | (Val::Set(a), Val::Set(b)) => Rc::ptr_eq(a, b),
        (Val::Dict(a), Val::Dict(b)) | (Val::Namespace(a), Val::Namespace(b)) => Rc::ptr_eq(a, b),
        _ => false,
    }
}
fn native_value(id: u64) -> Result<Val> {
    NATIVE_OBJECTS
        .with(|objects| objects.borrow().get(id.saturating_sub(1) as usize).cloned())
        .context("native object belongs to another worker or has expired")
}
impl Val {
    /// Explicitly retain a native object's identity across a primitive callback.
    /// Ordinary encode keeps public recipe containers concrete by value.
    pub fn encode_ref(&self) -> Result<Value> {
        let kind = match self {
            Self::Func(_) => "callable",
            Self::Namespace(_) => "namespace",
            Self::List(_) => "list",
            Self::Dict(_) => "dict",
            Self::Set(_) => "set",
            Self::Tuple(_) => "tuple",
            _ => return self.encode(),
        };
        let id = NATIVE_OBJECTS.with(|objects| {
            let mut objects = objects.borrow_mut();
            if let Some(i) = objects.iter().position(|v| same_identity(v, self)) {
                i + 1
            } else {
                objects.push(self.clone());
                objects.len()
            }
        });
        Ok(json!({"$native":{"id":id,"kind":kind}}))
    }
}
fn native_result(value: Val) -> Result<Value> {
    if let Val::Path(path) = &value {
        return Ok(json!({"$path":path.to_string_lossy()}));
    }
    if matches!(
        value,
        Val::Func(_) | Val::Namespace(_) | Val::List(_) | Val::Dict(_) | Val::Set(_)
    ) {
        value.encode_ref()
    } else {
        value.encode()
    }
}
/// Dispatch native proxy requests before the binary's domain requests.
/// Registry borrows end before any function runs, including recursive callbacks.
pub fn native_object(input: &Value) -> Option<Result<Value>> {
    let input = input.get("_hsm_native")?;
    Some((|| {
        let object = native_value(input["id"].as_u64().context("native object id")?)?;
        let operation = input["op"].as_str().context("native object operation")?;
        Ok(match operation {
            "call" => {
                let args = if input["args"].is_null() {
                    vec![]
                } else {
                    Val::decode(input["args"].clone())?.iter()?
                };
                let kwargs = if input["kwargs"].is_null() {
                    vec![]
                } else {
                    entries_of(&Val::decode(input["kwargs"].clone())?)?
                        .into_iter()
                        .map(|(k, v)| Ok((k.str()?, v)))
                        .collect::<Result<_>>()?
                };
                native_result(object.call(args, kwargs)?)?
            }
            "attr" => native_result(
                object.attr(input["name"].as_str().context("native attribute name")?)?,
            )?,
            "get" => native_result(object.get(Val::decode(input["key"].clone())?)?)?,
            "set" => {
                object.set(
                    Val::decode(input["key"].clone())?,
                    Val::decode(input["value"].clone())?,
                )?;
                Value::Null
            }
            "setattr" => {
                object.setattr(
                    input["name"].as_str().context("native attribute name")?,
                    Val::decode(input["value"].clone())?,
                )?;
                Value::Null
            }
            "delete" => {
                object.delete(Val::decode(input["key"].clone())?)?;
                Value::Null
            }
            "iter" => Value::Array(
                object
                    .iter()?
                    .into_iter()
                    .map(native_result)
                    .collect::<Result<_>>()?,
            ),
            "snapshot" => native_snapshot(&object)?,
            "len" => json!(object.len()?),
            "bool" => json!(object.truthy()?),
            "str" => json!(object.str()?),
            "repr" => json!(object.repr()?),
            "contains" => json!(object.contains(&Val::decode(input["item"].clone())?)?),
            "binary" => {
                let operator = input["operator"]
                    .as_str()
                    .context("native binary operator")?;
                let other = Val::decode(input["other"].clone())?;
                native_result(
                    if [
                        "eq", "ne", "lt", "le", "gt", "ge", "is", "is_not", "in", "not_in",
                    ]
                    .contains(&operator)
                    {
                        compare(operator, object, other)?
                    } else {
                        binary(operator, object, other)?
                    },
                )?
            }
            "unary" => native_result(unary(
                input["operator"]
                    .as_str()
                    .context("native unary operator")?,
                object,
            )?)?,
            "enter" => native_result(object.attr("__enter__")?.call(vec![], vec![])?)?,
            "exit" => {
                let args = if let Some(args) = input.get("args") {
                    Val::decode(args.clone())?.iter()?
                } else {
                    vec![Val::None, Val::None, Val::None]
                };
                ensure!(args.len() == 3, "context exit takes an exception triple");
                native_result(object.attr("__exit__")?.call(args, vec![])?)?
            }
            _ => bail!("unsupported native object operation {operation}"),
        })
    })())
}

mod standard;

pub fn native_snapshot(value: &Val) -> Result<Value> {
    Ok(match value {
        Val::List(values) => Value::Array(
            values
                .borrow()
                .iter()
                .map(native_snapshot)
                .collect::<Result<_>>()?,
        ),
        Val::Tuple(values) => {
            json!({"$tuple":values.iter().map(native_snapshot).collect::<Result<Vec<_>>>()?})
        }
        Val::Dict(values) => {
            json!({"$dict":values.borrow().iter().map(|(k,v)|Ok(json!([native_snapshot(k)?,native_snapshot(v)?]))).collect::<Result<Vec<Value>>>()?})
        }
        Val::Set(values) => {
            json!({"$set":values.borrow().iter().map(native_snapshot).collect::<Result<Vec<_>>>()?})
        }
        Val::FrozenSet(values) => {
            json!({"$frozenset":values.iter().map(native_snapshot).collect::<Result<Vec<_>>>()?})
        }
        Val::Path(path) => json!({"$path":path.to_string_lossy()}),
        _ => value.encode()?,
    })
}
