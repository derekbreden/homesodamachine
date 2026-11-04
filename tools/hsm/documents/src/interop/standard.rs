//! Native scalar document codecs and standard-library operations.
use super::*;
use regex::{Captures, Regex, RegexBuilder};
use serde::de::{self, DeserializeSeed, MapAccess, SeqAccess, Visitor};
use sha2::{Digest, Sha256};
use std::fmt;

struct Ordered;
impl<'de> DeserializeSeed<'de> for Ordered {
    type Value = Val;
    fn deserialize<D: de::Deserializer<'de>>(self, d: D) -> std::result::Result<Val, D::Error> {
        d.deserialize_any(self)
    }
}
impl<'de> Visitor<'de> for Ordered {
    type Value = Val;
    fn expecting(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "a JSON value")
    }
    fn visit_unit<E: de::Error>(self) -> std::result::Result<Val, E> {
        Ok(Val::None)
    }
    fn visit_none<E: de::Error>(self) -> std::result::Result<Val, E> {
        Ok(Val::None)
    }
    fn visit_bool<E: de::Error>(self, v: bool) -> std::result::Result<Val, E> {
        Ok(v.into())
    }
    fn visit_i64<E: de::Error>(self, v: i64) -> std::result::Result<Val, E> {
        Ok(Val::Int(v))
    }
    fn visit_u64<E: de::Error>(self, v: u64) -> std::result::Result<Val, E> {
        Ok(if v <= i64::MAX as u64 {
            Val::Int(v as i64)
        } else {
            Val::Float(v as f64)
        })
    }
    fn visit_f64<E: de::Error>(self, v: f64) -> std::result::Result<Val, E> {
        Ok(v.into())
    }
    fn visit_str<E: de::Error>(self, v: &str) -> std::result::Result<Val, E> {
        Ok(v.into())
    }
    fn visit_string<E: de::Error>(self, v: String) -> std::result::Result<Val, E> {
        Ok(v.into())
    }
    fn visit_seq<A: SeqAccess<'de>>(self, mut a: A) -> std::result::Result<Val, A::Error> {
        let mut rows = vec![];
        while let Some(v) = a.next_element_seed(Ordered)? {
            rows.push(v)
        }
        Ok(Val::list(rows))
    }
    fn visit_map<A: MapAccess<'de>>(self, mut a: A) -> std::result::Result<Val, A::Error> {
        let mut rows = vec![];
        while let Some(k) = a.next_key::<String>()? {
            rows.push((k.into(), a.next_value_seed(Ordered)?));
        }
        Ok(Val::dict(rows))
    }
}
fn json_load(text: &str) -> Result<Val> {
    let mut d = serde_json::Deserializer::from_str(text);
    let value = Ordered.deserialize(&mut d)?;
    d.end()?;
    Ok(value)
}
fn string_json(text: &str, ascii: bool) -> Result<String> {
    let text = serde_json::to_string(text)?;
    Ok(if ascii {
        super::super::ascii_json(&text)
    } else {
        text
    })
}
fn json_write(value: &Val, kwargs: &Kwargs, depth: usize) -> Result<String> {
    let pretty = option(kwargs, "indent").filter(|v| !matches!(v, Val::None));
    let indent = pretty
        .as_ref()
        .map(|v| match v {
            Val::Str(s) => Ok::<String, anyhow::Error>(s.clone()),
            _ => Ok(" ".repeat(v.integer()?.max(0) as usize)),
        })
        .transpose()?;
    let ascii = option(kwargs, "ensure_ascii")
        .map(|v| v.truthy())
        .transpose()?
        .unwrap_or(true);
    let sort = option(kwargs, "sort_keys")
        .map(|v| v.truthy())
        .transpose()?
        .unwrap_or(false);
    let separators = option(kwargs, "separators").map(|v| v.iter()).transpose()?;
    let comma = separators
        .as_ref()
        .map(|s| s[0].str())
        .transpose()?
        .unwrap_or_else(|| {
            if pretty.is_some() {
                ",".into()
            } else {
                ", ".into()
            }
        });
    let colon = separators
        .as_ref()
        .map(|s| s[1].str())
        .transpose()?
        .unwrap_or_else(|| ": ".into());
    let array = |values: Vec<Val>| -> Result<String> {
        if values.is_empty() {
            return Ok("[]".into());
        }
        let rows = values
            .iter()
            .map(|v| json_write(v, kwargs, depth + 1))
            .collect::<Result<Vec<_>>>()?;
        Ok(if let Some(indent) = &indent {
            format!(
                "[\n{}{}\n{}]",
                indent.repeat(depth + 1),
                rows.join(&(comma.clone() + "\n" + &indent.repeat(depth + 1))),
                indent.repeat(depth)
            )
        } else {
            "[".to_owned() + &rows.join(&comma) + "]"
        })
    };
    Ok(match value {
        Val::None => "null".into(),
        Val::Bool(v) => {
            if *v {
                "true".into()
            } else {
                "false".into()
            }
        }
        Val::Int(v) => v.to_string(),
        Val::Float(v) => {
            if v.is_nan() {
                "NaN".into()
            } else if *v == f64::INFINITY {
                "Infinity".into()
            } else if *v == f64::NEG_INFINITY {
                "-Infinity".into()
            } else {
                float_string(*v)
            }
        }
        Val::Str(v) => string_json(v, ascii)?,
        Val::List(v) => array(v.borrow().clone())?,
        Val::Tuple(v) => array(v.clone())?,
        Val::Dict(v) => {
            let mut entries = v.borrow().clone();
            if entries.is_empty() {
                return Ok("{}".into());
            }
            if sort {
                entries.sort_by(|a, b| cmp(&a.0, &b.0).unwrap_or(std::cmp::Ordering::Equal));
            }
            let mut rows = vec![];
            for (k, v) in entries {
                let key = match k {
                    Val::Str(s) => s,
                    Val::None => "null".into(),
                    Val::Bool(b) => {
                        if b {
                            "true".into()
                        } else {
                            "false".into()
                        }
                    }
                    Val::Int(i) => i.to_string(),
                    Val::Float(f) => float_string(f),
                    _ => bail!("JSON dictionary key is not a scalar"),
                };
                rows.push(string_json(&key, ascii)? + &colon + &json_write(&v, kwargs, depth + 1)?);
            }
            if let Some(indent) = indent {
                format!(
                    "{{\n{}{}\n{}}}",
                    indent.repeat(depth + 1),
                    rows.join(&(comma + "\n" + &indent.repeat(depth + 1))),
                    indent.repeat(depth)
                )
            } else {
                "{".to_owned() + &rows.join(&comma) + "}"
            }
        }
        Val::Ref(_) => {
            let concrete = remote("snapshot", value, json!({}))?;
            ensure!(
                !matches!(concrete, Val::Ref(_)),
                "object is not JSON serializable"
            );
            json_write(&concrete, kwargs, depth)?
        }
        _ => {
            if let Some(default) = option(kwargs, "default") {
                json_write(&default.call(vec![value.clone()], vec![])?, kwargs, depth)?
            } else {
                bail!("object is not JSON serializable: {}", value.repr()?)
            }
        }
    })
}
fn json_module() -> Val {
    let mut fields = vec![];
    for name in ["loads", "load", "dumps", "dump"] {
        let name = name.to_owned();
        let key = name.clone();
        fields.push((
            key.into(),
            Val::function(move |args, kwargs| {
                if name == "loads" || name == "load" {
                    let text = if name == "load" {
                        arg(&args, 0)?.attr("read")?.call(vec![], vec![])?.str()?
                    } else {
                        match arg(&args, 0)? {
                            Val::Bytes(b) => String::from_utf8(b)?,
                            v => v.str()?,
                        }
                    };
                    json_load(&text)
                } else {
                    let value = arg(&args, 0)?;
                    let text = json_write(&value, &kwargs, 0)?;
                    if name == "dump" {
                        arg(&args, 1)?
                            .attr("write")?
                            .call(vec![text.into()], vec![])?;
                        Ok(Val::None)
                    } else {
                        Ok(text.into())
                    }
                }
            }),
        ));
    }
    Val::namespace(fields)
}
fn bytes(value: Val) -> Result<Vec<u8>> {
    match value {
        Val::Bytes(b) => Ok(b),
        Val::Str(s) => Ok(s.into_bytes()),
        Val::Ref(_) => bytes(remote("snapshot", &value, json!({}))?),
        _ => bail!("expected byte buffer"),
    }
}
#[derive(Clone)]
enum HashState {
    Sha256(Sha256),
    Blake2b(blake2::Blake2bVar, usize),
}
impl HashState {
    fn update(&mut self, bytes: &[u8]) {
        match self {
            Self::Sha256(state) => sha2::Digest::update(state, bytes),
            Self::Blake2b(state, _) => blake2::digest::Update::update(state, bytes),
        }
    }
    fn digest(&self) -> Result<Vec<u8>> {
        Ok(match self {
            Self::Sha256(state) => state.clone().finalize().to_vec(),
            Self::Blake2b(state, size) => {
                use blake2::digest::VariableOutput;
                let mut bytes = vec![0; *size];
                state
                    .clone()
                    .finalize_variable(&mut bytes)
                    .map_err(|_| anyhow::anyhow!("blake2b digest size"))?;
                bytes
            }
        })
    }
}
fn hash_object(initial: HashState) -> Val {
    let size = match &initial {
        HashState::Sha256(_) => 32,
        HashState::Blake2b(_, size) => *size,
    };
    let algorithm = if matches!(initial, HashState::Sha256(_)) {
        "sha256"
    } else {
        "blake2b"
    };
    let block = if algorithm == "sha256" { 64 } else { 128 };
    let data = Rc::new(RefCell::new(initial));
    let mut fields = vec![
        ("digest_size".into(), Val::Int(size as i64)),
        ("block_size".into(), Val::Int(block)),
        ("name".into(), algorithm.into()),
    ];
    for name in ["update", "hexdigest", "digest", "copy"] {
        let state = data.clone();
        let name = name.to_owned();
        let key = name.clone();
        fields.push((
            key.into(),
            Val::function(move |args, _| {
                Ok(match name.as_str() {
                    "update" => {
                        let bytes = bytes(arg(&args, 0)?)?;
                        state.borrow_mut().update(&bytes);
                        Val::None
                    }
                    "hexdigest" => state
                        .borrow()
                        .digest()?
                        .iter()
                        .map(|b| format!("{b:02x}"))
                        .collect::<String>()
                        .into(),
                    "digest" => Val::Bytes(state.borrow().digest()?),
                    _ => hash_object(state.borrow().clone()),
                })
            }),
        ));
    }
    Val::namespace(fields)
}
fn hash_module() -> Val {
    Val::namespace(vec![
        (
            "sha256".into(),
            Val::function(|args, _| {
                let mut state = HashState::Sha256(Sha256::new());
                if let Some(data) = args.first() {
                    state.update(&bytes(data.clone())?);
                }
                Ok(hash_object(state))
            }),
        ),
        (
            "blake2b".into(),
            Val::function(|args, kwargs| {
                use blake2::digest::VariableOutput;
                let size = option(&kwargs, "digest_size")
                    .map(|v| v.integer())
                    .transpose()?
                    .unwrap_or(64) as usize;
                let mut state = HashState::Blake2b(
                    blake2::Blake2bVar::new(size)
                        .map_err(|_| anyhow::anyhow!("blake2b digest size"))?,
                    size,
                );
                if let Some(data) = args.first() {
                    state.update(&bytes(data.clone())?);
                }
                Ok(hash_object(state))
            }),
        ),
        (
            "file_digest".into(),
            Val::function(|args, _| {
                let stream = arg(&args, 0)?;
                let constructor = arg(&args, 1)?;
                let hash = if let Val::Str(name) = constructor {
                    hash_module().attr(&name)?.call(vec![], vec![])?
                } else {
                    constructor.call(vec![], vec![])?
                };
                loop {
                    let block = bytes(stream.attr("read")?.call(vec![Val::Int(1 << 18)], vec![])?)?;
                    if block.is_empty() {
                        break;
                    }
                    hash.attr("update")?.call(vec![Val::Bytes(block)], vec![])?;
                }
                Ok(hash)
            }),
        ),
    ])
}
fn compile(pattern: &str, flags: i64) -> Result<Regex> {
    Ok(RegexBuilder::new(pattern)
        .case_insensitive(flags & 2 != 0)
        .multi_line(flags & 8 != 0)
        .dot_matches_new_line(flags & 16 != 0)
        .ignore_whitespace(flags & 64 != 0)
        .build()?)
}
fn group_index(value: &Val, names: &[Option<String>]) -> Result<usize> {
    match value {
        Val::Str(name) => names
            .iter()
            .position(|n| n.as_ref() == Some(name))
            .context("unknown regex group"),
        _ => Ok(value.integer()? as usize),
    }
}
fn matched(regex: &Regex, text: &str, captures: &Captures<'_>, offset: usize) -> Val {
    let names = regex
        .capture_names()
        .map(|s| s.map(str::to_owned))
        .collect::<Vec<_>>();
    let groups = captures
        .iter()
        .map(|m| m.map(|m| (m.as_str().to_owned(), m.start() + offset, m.end() + offset)))
        .collect::<Vec<_>>();
    let mut fields = vec![("string".into(), text.into())];
    for name in [
        "group",
        "groups",
        "groupdict",
        "start",
        "end",
        "span",
        "__getitem__",
    ] {
        let name = name.to_owned();
        let key = name.clone();
        let groups = groups.clone();
        let names = names.clone();
        let text = text.to_owned();
        fields.push((
            key.into(),
            Val::function(move |args, _| {
                let group = |index: usize| -> Result<Val> {
                    Ok(groups
                        .get(index)
                        .context("regex group out of range")?
                        .as_ref()
                        .map(|g| Val::Str(g.0.clone()))
                        .unwrap_or(Val::None))
                };
                Ok(match name.as_str() {
                    "group" | "__getitem__" => {
                        let ids = if args.is_empty() {
                            vec![0]
                        } else {
                            args.iter()
                                .map(|v| group_index(v, &names))
                                .collect::<Result<_>>()?
                        };
                        let values = ids.into_iter().map(group).collect::<Result<Vec<_>>>()?;
                        if values.len() == 1 {
                            values[0].clone()
                        } else {
                            Val::tuple(values)
                        }
                    }
                    "groups" => Val::tuple(
                        (1..groups.len())
                            .map(|i| {
                                group(i).map(|g| {
                                    if matches!(g, Val::None) {
                                        args.first().cloned().unwrap_or(g)
                                    } else {
                                        g
                                    }
                                })
                            })
                            .collect::<Result<_>>()?,
                    ),
                    "groupdict" => Val::dict(
                        names
                            .iter()
                            .enumerate()
                            .filter_map(|(i, n)| n.as_ref().map(|n| (i, n)))
                            .map(|(i, n)| Ok((n.clone().into(), group(i)?)))
                            .collect::<Result<_>>()?,
                    ),
                    _ => {
                        let index = if args.is_empty() {
                            0
                        } else {
                            group_index(&args[0], &names)?
                        };
                        let bounds = groups
                            .get(index)
                            .context("regex group out of range")?
                            .as_ref()
                            .map(|(_, a, b)| {
                                (
                                    text[..*a].chars().count() as i64,
                                    text[..*b].chars().count() as i64,
                                )
                            })
                            .unwrap_or((-1, -1));
                        match name.as_str() {
                            "start" => Val::Int(bounds.0),
                            "end" => Val::Int(bounds.1),
                            _ => Val::tuple(vec![Val::Int(bounds.0), Val::Int(bounds.1)]),
                        }
                    }
                })
            }),
        ));
    }
    Val::namespace(fields)
}
fn replacement(text: &str, c: &Captures<'_>) -> String {
    let mut out = String::new();
    let mut chars = text.chars().peekable();
    while let Some(ch) = chars.next() {
        if ch != '\\' {
            out.push(ch);
            continue;
        }
        match chars.next() {
            Some('g') if chars.peek() == Some(&'<') => {
                chars.next();
                let mut group = String::new();
                for ch in chars.by_ref() {
                    if ch == '>' {
                        break;
                    }
                    group.push(ch)
                }
                if let Ok(i) = group.parse::<usize>() {
                    if let Some(m) = c.get(i) {
                        out.push_str(m.as_str())
                    }
                } else if let Some(m) = c.name(&group) {
                    out.push_str(m.as_str())
                }
            }
            Some(ch) if ch.is_ascii_digit() => {
                let mut group = ch.to_string();
                while chars.peek().is_some_and(char::is_ascii_digit) {
                    group.push(chars.next().unwrap());
                }
                if let Some(m) = group.parse::<usize>().ok().and_then(|i| c.get(i)) {
                    out.push_str(m.as_str())
                }
            }
            Some('n') => out.push('\n'),
            Some('t') => out.push('\t'),
            Some('r') => out.push('\r'),
            Some(ch) => out.push(ch),
            None => out.push('\\'),
        }
    }
    out
}
fn pattern_object(pattern: String, flags: i64) -> Result<Val> {
    let regex = Rc::new(compile(&pattern, flags)?);
    let mut fields = vec![
        ("pattern".into(), pattern.into()),
        ("flags".into(), Val::Int(flags)),
    ];
    for name in [
        "search",
        "match",
        "fullmatch",
        "findall",
        "finditer",
        "sub",
        "subn",
        "split",
    ] {
        let regex = regex.clone();
        let name = name.to_owned();
        let key = name.clone();
        fields.push((
            key.into(),
            Val::function(move |args, kwargs| {
                if name == "sub" || name == "subn" {
                    let repl = arg(&args, 0)?;
                    let text = arg(&args, 1)?.str()?;
                    let count = args
                        .get(2)
                        .cloned()
                        .or_else(|| option(&kwargs, "count"))
                        .map(|v| v.integer())
                        .transpose()?
                        .unwrap_or(0);
                    let mut out = String::new();
                    let mut at = 0;
                    let mut n = 0;
                    for capture in regex.captures_iter(&text) {
                        if count > 0 && n >= count {
                            break;
                        }
                        let m = capture.get(0).unwrap();
                        out.push_str(&text[at..m.start()]);
                        let rendered = if matches!(repl, Val::Func(_) | Val::Ref(_)) {
                            repl.call(vec![matched(&regex, &text, &capture, 0)], vec![])?
                                .str()?
                        } else {
                            replacement(&repl.str()?, &capture)
                        };
                        out.push_str(&rendered);
                        at = m.end();
                        n += 1;
                    }
                    out.push_str(&text[at..]);
                    return Ok(if name == "subn" {
                        Val::tuple(vec![out.into(), Val::Int(n)])
                    } else {
                        out.into()
                    });
                }
                let text = arg(&args, 0)?.str()?;
                if name == "findall" || name == "finditer" {
                    let mut rows = vec![];
                    for capture in regex.captures_iter(&text) {
                        rows.push(if name == "finditer" {
                            matched(&regex, &text, &capture, 0)
                        } else if regex.captures_len() == 1 {
                            capture.get(0).unwrap().as_str().into()
                        } else if regex.captures_len() == 2 {
                            capture.get(1).map(|m| m.as_str()).unwrap_or("").into()
                        } else {
                            Val::tuple(
                                (1..regex.captures_len())
                                    .map(|i| {
                                        Val::Str(
                                            capture.get(i).map(|m| m.as_str()).unwrap_or("").into(),
                                        )
                                    })
                                    .collect(),
                            )
                        });
                    }
                    return Ok(Val::list(rows));
                }
                if name == "split" {
                    let limit = args.get(1).map(Val::integer).transpose()?.unwrap_or(0);
                    let mut rows = vec![];
                    let mut at = 0;
                    let mut n = 0;
                    for capture in regex.captures_iter(&text) {
                        if limit > 0 && n >= limit {
                            break;
                        }
                        let m = capture.get(0).unwrap();
                        rows.push(text[at..m.start()].into());
                        for i in 1..regex.captures_len() {
                            rows.push(
                                capture
                                    .get(i)
                                    .map(|m| Val::Str(m.as_str().into()))
                                    .unwrap_or(Val::None),
                            );
                        }
                        at = m.end();
                        n += 1;
                    }
                    rows.push(text[at..].into());
                    return Ok(Val::list(rows));
                }
                let start = args
                    .get(1)
                    .map(Val::integer)
                    .transpose()?
                    .unwrap_or(0)
                    .max(0) as usize;
                let end = args
                    .get(2)
                    .map(Val::integer)
                    .transpose()?
                    .unwrap_or(text.chars().count() as i64)
                    .max(0) as usize;
                let positions = text
                    .char_indices()
                    .map(|(i, _)| i)
                    .chain(std::iter::once(text.len()))
                    .collect::<Vec<_>>();
                let start = positions[start.min(positions.len() - 1)];
                let end = positions[end.min(positions.len() - 1)].max(start);
                let part = &text[start..end];
                let capture = regex.captures(part).filter(|c| {
                    let m = c.get(0).unwrap();
                    (name == "search" || m.start() == 0)
                        && (name != "fullmatch" || m.end() == part.len())
                });
                Ok(capture
                    .map(|c| matched(&regex, &text, &c, start))
                    .unwrap_or(Val::None))
            }),
        ));
    }
    Ok(Val::namespace(fields))
}
fn re_module() -> Val {
    let mut fields = vec![];
    for (name, flag) in [
        ("I", 2),
        ("IGNORECASE", 2),
        ("M", 8),
        ("MULTILINE", 8),
        ("S", 16),
        ("DOTALL", 16),
        ("X", 64),
        ("VERBOSE", 64),
        ("ASCII", 256),
    ] {
        fields.push((name.into(), Val::Int(flag)));
    }
    fields.push((
        "compile".into(),
        Val::function(|args, kwargs| {
            pattern_object(
                arg(&args, 0)?.str()?,
                args.get(1)
                    .cloned()
                    .or_else(|| option(&kwargs, "flags"))
                    .map(|v| v.integer())
                    .transpose()?
                    .unwrap_or(0),
            )
        }),
    ));
    fields.push((
        "escape".into(),
        Val::function(|args, _| {
            let mut out = String::new();
            for ch in arg(&args, 0)?.str()?.chars() {
                if "()[]{}?*+-|^$\\.&~# \t\n\r\u{b}\u{c}".contains(ch) {
                    out.push('\\')
                }
                out.push(ch)
            }
            Ok(out.into())
        }),
    ));
    for name in [
        "search",
        "match",
        "fullmatch",
        "findall",
        "finditer",
        "sub",
        "subn",
        "split",
    ] {
        let name = name.to_owned();
        let key = name.clone();
        fields.push((
            key.into(),
            Val::function(move |mut args, mut kwargs| {
                let pattern = args.remove(0);
                let flags = option(&kwargs, "flags")
                    .map(|v| v.integer())
                    .transpose()?
                    .unwrap_or(0);
                kwargs.retain(|(k, _)| k != "flags");
                let pattern = if matches!(pattern, Val::Str(_)) {
                    pattern_object(pattern.str()?, flags)?
                } else {
                    pattern
                };
                pattern.attr(&name)?.call(args, kwargs)
            }),
        ));
    }
    Val::namespace(fields)
}
pub fn module(name: &str) -> Option<Val> {
    match name {
        "json" => Some(json_module()),
        "hashlib" => Some(hash_module()),
        "re" => Some(re_module()),
        "collections" => {
            let mut fields = vec![];
            for name in [
                "namedtuple",
                "defaultdict",
                "Counter",
                "deque",
                "OrderedDict",
                "ChainMap",
            ] {
                let name = name.to_owned();
                let key = name.clone();
                fields.push((
                    key.into(),
                    if name == "OrderedDict" {
                        Val::Type("dict".into())
                    } else {
                        Val::function(move |args, kwargs| {
                            let imported = Val::decode(callback(
                                json!({"op":"import","module":"collections"}),
                            )?)?;
                            imported.attr(&name)?.call(args, kwargs)
                        })
                    },
                ));
            }
            Some(Val::namespace(fields))
        }
        "time" => {
            static START: std::sync::OnceLock<std::time::Instant> = std::sync::OnceLock::new();
            let mut fields = vec![];
            for name in ["time", "perf_counter", "monotonic", "sleep"] {
                let name = name.to_owned();
                let key = name.clone();
                fields.push((
                    key.into(),
                    Val::function(move |args, _| {
                        Ok(match name.as_str() {
                            "time" => std::time::SystemTime::now()
                                .duration_since(std::time::UNIX_EPOCH)?
                                .as_secs_f64()
                                .into(),
                            "sleep" => {
                                std::thread::sleep(std::time::Duration::from_secs_f64(
                                    arg(&args, 0)?.num()?,
                                ));
                                Val::None
                            }
                            _ => START
                                .get_or_init(std::time::Instant::now)
                                .elapsed()
                                .as_secs_f64()
                                .into(),
                        })
                    }),
                ));
            }
            Some(Val::namespace(fields))
        }
        _ => None,
    }
}
