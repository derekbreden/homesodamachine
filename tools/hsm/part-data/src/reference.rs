//! Dimensional reference catalog and source readers, with JSON type marshalling.
use anyhow::{Result, bail};
use serde_json::{Value, json};
use std::{
    cmp::Ordering,
    collections::{BTreeMap, BTreeSet},
    fs,
    path::{Path, PathBuf},
};
type Env = BTreeMap<String, Value>;
struct Context {
    root: PathBuf,
    reads: BTreeSet<String>,
    cache: BTreeMap<String, Env>,
    inputs: Value,
    messages: Vec<String>,
    overrides: Value,
    holder_updates: Value,
}
#[path = "reference_catalog.rs"]
mod catalog;
use catalog::{call, globals};
#[path = "storage.rs"]
mod storage;
fn g(e: &Env, k: &str) -> Value {
    e.get(k)
        .unwrap_or_else(|| panic!("Unknown reference datum {k}"))
        .clone()
}
fn missing(k: &str) -> Value {
    panic!("Missing reference argument {k}")
}
fn n(v: &Value) -> f64 {
    if let Some(b) = v.as_bool() {
        return if b { 1.0 } else { 0.0 };
    }
    v.as_f64()
        .unwrap_or_else(|| panic!("Expected number, got {v}"))
}
fn j(x: f64) -> Value {
    json!(x)
}
fn t(v: Vec<Value>) -> Value {
    json!({"$tuple":v})
}
fn tuple(v: &Value) -> bool {
    v.get("$tuple").is_some()
}
fn seq(v: Value) -> Vec<Value> {
    if let Some(a) = v.as_array() {
        return a.clone();
    }
    if let Some(a) = v["$tuple"].as_array() {
        return a.clone();
    }
    if let Some(a) = v["$dict"].as_array() {
        return a.iter().map(|p| p[0].clone()).collect();
    }
    if let Some(o) = v.as_object() {
        return o.keys().map(|k| json!(k)).collect();
    }
    if let Some(s) = v.as_str() {
        return s.chars().map(|c| json!(c.to_string())).collect();
    }
    panic!("Expected sequence, got {v}")
}
fn truth(v: &Value) -> bool {
    if let Some(value) = v.get("$dict") {
        return truth(value);
    }
    match v {
        Value::Null => false,
        Value::Bool(v) => *v,
        Value::Number(_) => n(v) != 0.0,
        Value::String(v) => !v.is_empty(),
        Value::Array(v) => !v.is_empty(),
        Value::Object(v) => {
            if let Some(a) = v.get("$tuple") {
                truth(a)
            } else {
                !v.is_empty()
            }
        }
    }
}
fn string(v: &Value) -> String {
    if v.get("$env").is_some() {
        return storage::display(v);
    }
    if let Some(s) = v.as_str() {
        return s.to_owned();
    }
    if v.is_null() {
        return "None".into();
    }
    if let Some(b) = v.as_bool() {
        return if b { "True" } else { "False" }.into();
    }
    if let Some(i) = v.as_i64() {
        return i.to_string();
    }
    if let Some(f) = v.as_f64() {
        return if f.fract() == 0.0 {
            format!("{f:.1}")
        } else {
            f.to_string()
        };
    }
    if tuple(v) {
        return format!(
            "({})",
            seq(v.clone())
                .iter()
                .map(string)
                .collect::<Vec<_>>()
                .join(", ")
        );
    }
    v.to_string()
}
fn cmp(a: &Value, b: &Value) -> Ordering {
    if a.is_number() && b.is_number() {
        return n(a).total_cmp(&n(b));
    }
    if let (Some(a), Some(b)) = (a.as_str(), b.as_str()) {
        return a.cmp(b);
    }
    if (a.is_array() || tuple(a)) && (b.is_array() || tuple(b)) {
        let (aa, bb) = (seq(a.clone()), seq(b.clone()));
        for (a, b) in aa.iter().zip(&bb) {
            let c = cmp(a, b);
            if c != Ordering::Equal {
                return c;
            }
        }
        return aa.len().cmp(&bb.len());
    }
    a.to_string().cmp(&b.to_string())
}
fn equal(a: &Value, b: &Value) -> bool {
    if (a.is_number() || a.is_boolean()) && (b.is_number() || b.is_boolean()) {
        n(a) == n(b)
    } else if let (Some(a), Some(b)) = (a["$dict"].as_array(), b["$dict"].as_array()) {
        a.len() == b.len()
            && a.iter()
                .all(|p| b.iter().any(|q| equal(&p[0], &q[0]) && equal(&p[1], &q[1])))
    } else if (a.is_array() && b.is_array()) || (tuple(a) && tuple(b)) {
        let (aa, bb) = (seq(a.clone()), seq(b.clone()));
        aa.len() == bb.len() && aa.iter().zip(&bb).all(|(a, b)| equal(a, b))
    } else if let (Some(a), Some(b)) = (a.as_object(), b.as_object()) {
        a.len() == b.len()
            && a.iter()
                .all(|(k, v)| b.get(k).is_some_and(|other| equal(v, other)))
    } else {
        a == b
    }
}
fn object(rows: Vec<(Value, Value)>) -> Value {
    let mut out: Vec<Vec<Value>> = vec![];
    for (k, v) in rows {
        if let Some(row) = out.iter_mut().find(|r| equal(&r[0], &k)) {
            row[1] = v
        } else {
            out.push(vec![k, v]);
        }
    }
    json!({"$dict":out})
}
fn merge(values: Vec<Value>) -> Value {
    let mut rows = vec![];
    for value in values {
        for pair in seq(method(value, "items", vec![])) {
            rows.push((ix(pair.clone(), json!(0)), ix(pair, json!(1))));
        }
    }
    object(rows)
}
fn kwarg(v: &Value, key: &str) -> Option<Value> {
    if let Some(rows) = v["$dict"].as_array() {
        rows.iter().find(|r| r[0] == key).map(|r| r[1].clone())
    } else {
        v.get(key).cloned()
    }
}
fn ix(v: Value, index: Value) -> Value {
    if let Some(rows) = v["$dict"].as_array() {
        return rows
            .iter()
            .find(|p| equal(&p[0], &index))
            .unwrap_or_else(|| panic!("No reference key {index}"))[1]
            .clone();
    }
    if v.is_object() && !tuple(&v) {
        return v
            .get(index.as_str().unwrap_or(&string(&index)))
            .unwrap_or_else(|| panic!("No reference key {index}"))
            .clone();
    }
    let a = seq(v);
    let i = n(&index) as i64;
    let i = if i < 0 { a.len() as i64 + i } else { i };
    a.get(i as usize)
        .unwrap_or_else(|| panic!("Reference index {i} out of range"))
        .clone()
}
fn slice(v: Value, lo: Value, hi: Value) -> Value {
    let a = seq(v.clone());
    let len = a.len() as i64;
    let idx = |v: &Value, default: i64| {
        if v.is_null() {
            default
        } else {
            let i = n(v) as i64;
            if i < 0 { (len + i).max(0) } else { i.min(len) }
        }
    };
    let lo = idx(&lo, 0) as usize;
    let hi = idx(&hi, len) as usize;
    let out = if hi >= lo { a[lo..hi].to_vec() } else { vec![] };
    if v.is_string() {
        json!(out.iter().map(|v| v.as_str().unwrap()).collect::<String>())
    } else if tuple(&v) {
        t(out)
    } else {
        json!(out)
    }
}
fn b(op: &str, a: Value, b: Value) -> Value {
    if op == "/" && a.get("$path").is_some() {
        return json!({"$path":Path::new(a["$path"].as_str().unwrap()).join(b.as_str().unwrap()).to_string_lossy()});
    }
    if op == "+" && a.is_string() && b.is_string() {
        return json!(a.as_str().unwrap().to_owned() + b.as_str().unwrap());
    }
    if op == "+" && (a.is_array() || tuple(&a)) {
        let mut out = seq(a.clone());
        out.extend(seq(b));
        return if tuple(&a) { t(out) } else { json!(out) };
    }
    if op == "*" && (a.is_array() || tuple(&a)) {
        let values = seq(a.clone());
        let out: Vec<_> = values
            .iter()
            .cycle()
            .take(values.len() * (n(&b) as usize))
            .cloned()
            .collect();
        return if tuple(&a) { t(out) } else { json!(out) };
    }
    if let (Some(x), Some(y)) = (a.as_i64(), b.as_i64()) {
        match op {
            "+" => return json!(x + y),
            "-" => return json!(x - y),
            "*" => return json!(x * y),
            "%" => return json!(x.rem_euclid(y)),
            _ => {}
        }
    }
    let (x, y) = (n(&a), n(&b));
    j(match op {
        "+" => x + y,
        "-" => x - y,
        "*" => x * y,
        "/" => x / y,
        "//" => (x / y).floor(),
        "%" => x.rem_euclid(y),
        "**" => x.powf(y),
        _ => panic!("Unknown numeric operator {op}"),
    })
}
fn u(op: &str, v: Value) -> Value {
    match op {
        "-" => {
            if let Some(i) = v.as_i64() {
                json!(-i)
            } else {
                j(-n(&v))
            }
        }
        "+" => v,
        "not" => json!(!truth(&v)),
        _ => panic!("Unknown unary operator"),
    }
}
fn compare(op: &str, a: Value, b: Value) -> bool {
    match op {
        "==" => equal(&a, &b),
        "!=" => !equal(&a, &b),
        "<" => cmp(&a, &b) == Ordering::Less,
        "<=" => cmp(&a, &b) != Ordering::Greater,
        ">" => cmp(&a, &b) == Ordering::Greater,
        ">=" => cmp(&a, &b) != Ordering::Less,
        "in" | "not in" => {
            let found = if b.is_string() {
                b.as_str().unwrap().contains(&string(&a))
            } else {
                seq(b).iter().any(|v| equal(v, &a))
            };
            if op == "in" { found } else { !found }
        }
        _ => panic!("Unknown comparison"),
    }
}
fn unique(v: Vec<Value>) -> Value {
    let mut out = vec![];
    for p in v {
        if !out.iter().any(|q| equal(q, &p)) {
            out.push(p)
        }
    }
    json!(out)
}
fn builtin(name: &str, args: Vec<Value>) -> Value {
    match name {
        "isinstance" => {
            let choices = if tuple(&args[1]) {
                seq(args[1].clone())
            } else {
                vec![args[1].clone()]
            };
            json!(
                choices
                    .iter()
                    .any(|kind| match kind["$class"].as_str().unwrap_or("") {
                        "int" => args[0].as_i64().is_some() || args[0].is_boolean(),
                        "float" => args[0].is_number() && args[0].as_i64().is_none(),
                        "tuple" => tuple(&args[0]),
                        "list" => args[0].is_array(),
                        "str" => args[0].is_string(),
                        "bool" => args[0].is_boolean(),
                        "Heap" => storage::kind(&args[0]) == Some("Heap"),
                        "Env" => matches!(storage::kind(&args[0]), Some("Env" | "Heap")),
                        "Holder" => storage::kind(&args[0]) == Some("Holder"),
                        _ => false,
                    })
            )
        }
        "tuple" => t(seq(args[0].clone())),
        "list" => json!(seq(args[0].clone())),
        "str" => json!(string(&args[0])),
        "bool" => json!(truth(&args[0])),
        "len" => json!(seq(args[0].clone()).len()),
        "float" => j(if args[0].is_string() {
            args[0].as_str().unwrap().parse().unwrap()
        } else {
            n(&args[0])
        }),
        "int" => json!(n(&args[0]) as i64),
        "abs" => {
            if let Some(i) = args[0].as_i64() {
                json!(i.abs())
            } else {
                j(n(&args[0]).abs())
            }
        }
        "range" => {
            let (start, end, step) = match args.as_slice() {
                [e] => (0, n(e) as i64, 1),
                [s, e] => (n(s) as i64, n(e) as i64, 1),
                [s, e, t] => (n(s) as i64, n(e) as i64, n(t) as i64),
                _ => panic!("range arguments"),
            };
            let mut out = vec![];
            let mut i = start;
            while if step > 0 { i < end } else { i > end } {
                out.push(json!(i));
                i += step
            }
            json!(out)
        }
        "enumerate" => json!(
            seq(args[0].clone())
                .into_iter()
                .enumerate()
                .map(|(i, v)| t(vec![json!(i), v]))
                .collect::<Vec<_>>()
        ),
        "zip" => {
            let lists: Vec<_> = args.into_iter().map(seq).collect();
            let len = lists.iter().map(Vec::len).min().unwrap_or(0);
            json!(
                (0..len)
                    .map(|i| t(lists.iter().map(|p| p[i].clone()).collect()))
                    .collect::<Vec<_>>()
            )
        }
        "sum" => seq(args[0].clone())
            .into_iter()
            .fold(json!(0), |a, bv| b("+", a, bv)),
        "min" | "max" => {
            let values = if args.len() == 1 {
                seq(args[0].clone())
            } else {
                args
            };
            values
                .into_iter()
                .reduce(|a, b| {
                    if (cmp(&a, &b) == Ordering::Less) == (name == "min") {
                        a
                    } else {
                        b
                    }
                })
                .expect("empty minimum/maximum")
        }
        "sorted" => {
            let mut values = seq(args[0].clone());
            values.sort_by(cmp);
            json!(values)
        }
        "reversed" => {
            let mut values = seq(args[0].clone());
            values.reverse();
            json!(values)
        }
        "all" => json!(seq(args[0].clone()).iter().all(truth)),
        "any" => json!(seq(args[0].clone()).iter().any(truth)),
        "next" => seq(args[0].clone())
            .into_iter()
            .next()
            .or_else(|| args.get(1).cloned())
            .expect("No next reference item"),
        "round" => {
            let precision = args.get(1).map(n).unwrap_or(0.0) as usize;
            let text =
                hsm_documents::format_number(n(&args[0]), &format!(".{precision}f")).unwrap();
            if args.len() == 1 {
                json!(text.parse::<f64>().unwrap() as i64)
            } else {
                j(text.parse().unwrap())
            }
        }
        "dict" => {
            if args.is_empty() {
                json!({})
            } else {
                args[0].clone()
            }
        }
        _ => panic!("Unknown builtin {name}"),
    }
}
fn math_fn(name: &str, args: Vec<Value>) -> Value {
    if name == "dist" {
        let (a, b) = (seq(args[0].clone()), seq(args[1].clone()));
        return j(a
            .iter()
            .zip(&b)
            .map(|(a, b)| (n(a) - n(b)).powi(2))
            .sum::<f64>()
            .sqrt());
    }
    let a = n(&args[0]);
    match name {
        "sqrt" => j(a.sqrt()),
        "sin" => j(a.sin()),
        "cos" => j(a.cos()),
        "tan" => j(a.tan()),
        "asin" => j(a.asin()),
        "acos" => j(a.acos()),
        "atan" => j(a.atan()),
        "atan2" => j(a.atan2(n(&args[1]))),
        "radians" => j(a.to_radians()),
        "degrees" => j(a.to_degrees()),
        "ceil" => json!(a.ceil() as i64),
        "floor" => json!(a.floor() as i64),
        "hypot" => j(a.hypot(n(&args[1]))),
        "dist" => {
            let (a, b) = (seq(args[0].clone()), seq(args[1].clone()));
            j(a.iter()
                .zip(&b)
                .map(|(a, b)| (n(a) - n(b)).powi(2))
                .sum::<f64>()
                .sqrt())
        }
        _ => panic!("Unknown math function {name}"),
    }
}
fn method(v: Value, name: &str, args: Vec<Value>) -> Value {
    match name {
        "fromkeys" => object(
            seq(args[0].clone())
                .into_iter()
                .map(|v| (v, Value::Null))
                .collect(),
        ),
        "replace" => json!(
            v.as_str()
                .unwrap()
                .replace(args[0].as_str().unwrap(), args[1].as_str().unwrap())
        ),
        "relative_to" => {
            let base = args[0]["$path"].as_str().unwrap();
            let relative = Path::new(v["$path"].as_str().unwrap())
                .strip_prefix(base)
                .unwrap();
            json!({"$path":relative.to_string_lossy()})
        }
        "as_posix" => json!(v["$path"].as_str().unwrap().replace('\\', "/")),
        "format" => {
            let text = v.as_str().unwrap();
            let mut rest = text;
            let mut output = String::new();
            let mut index = 0;
            while let Some(at) = rest.find('{') {
                output.push_str(&rest[..at]);
                let tail = &rest[at + 1..];
                let end = tail.find('}').expect("Unclosed storage format");
                let field = &tail[..end];
                let (number, spec) = field.split_once(':').unwrap_or((field, ""));
                let which = if number.is_empty() {
                    let i = index;
                    index += 1;
                    i
                } else {
                    number.parse().unwrap()
                };
                output.push_str(&format_value(args[which].clone(), spec).expect("Storage format"));
                rest = &tail[end + 1..];
            }
            output.push_str(rest);
            json!(output)
        }
        "get" => kwarg(&v, &string(&args[0]))
            .unwrap_or_else(|| args.get(1).cloned().unwrap_or(Value::Null)),
        "items" => {
            if let Some(rows) = v["$dict"].as_array() {
                json!(rows.iter().map(|r| t(seq(r.clone()))).collect::<Vec<_>>())
            } else {
                json!(
                    v.as_object()
                        .unwrap()
                        .iter()
                        .map(|(k, v)| t(vec![json!(k), v.clone()]))
                        .collect::<Vec<_>>()
                )
            }
        }
        "keys" => json!(seq(v)),
        "values" => {
            if let Some(rows) = v["$dict"].as_array() {
                json!(rows.iter().map(|r| r[1].clone()).collect::<Vec<_>>())
            } else {
                json!(v.as_object().unwrap().values().cloned().collect::<Vec<_>>())
            }
        }
        "copy" => v,
        "startswith" => json!(v.as_str().unwrap().starts_with(args[0].as_str().unwrap())),
        "endswith" => json!(v.as_str().unwrap().ends_with(args[0].as_str().unwrap())),
        "lower" => json!(v.as_str().unwrap().to_lowercase()),
        "upper" => json!(v.as_str().unwrap().to_uppercase()),
        "isupper" => {
            let s = v.as_str().unwrap();
            json!(
                s.chars().any(char::is_alphabetic)
                    && s.chars()
                        .filter(|c| c.is_alphabetic())
                        .all(char::is_uppercase)
            )
        }
        "join" => json!(
            seq(args[0].clone())
                .iter()
                .map(string)
                .collect::<Vec<_>>()
                .join(v.as_str().unwrap())
        ),
        "index" => json!(
            seq(v)
                .iter()
                .position(|p| equal(p, &args[0]))
                .expect("item not found")
        ),
        "count" => json!(seq(v).iter().filter(|p| equal(p, &args[0])).count()),
        _ => panic!("Unknown value method {name}"),
    }
}
fn mutate(e: &mut Env, key: &str, method: &str, item: Value) {
    if method == "update" {
        let mut current = g(e, key);
        let pairs = seq(self::method(item, "items", vec![]));
        for pair in pairs {
            let name = ix(pair.clone(), json!(0));
            let value = ix(pair, json!(1));
            if let Some(rows) = current.get_mut("$dict").and_then(Value::as_array_mut) {
                if let Some(row) = rows.iter_mut().find(|r| equal(&r[0], &name)) {
                    row[1] = value
                } else {
                    rows.push(json!([name, value]));
                }
            } else {
                current[name.as_str().unwrap()] = value;
            }
        }
        e.insert(key.into(), current);
        return;
    }
    let mut a = seq(g(e, key));
    if method == "append" {
        a.push(item)
    } else {
        a.extend(seq(item))
    }
    e.insert(key.into(), json!(a));
}
fn pop(e: &mut Env, key: &str) {
    let mut a = seq(g(e, key));
    a.pop();
    e.insert(key.into(), json!(a));
}
fn setitem(e: &mut Env, key: &str, index: Value, item: Value) {
    let mut value = g(e, key);
    if let Some(rows) = value.get_mut("$dict").and_then(Value::as_array_mut) {
        if let Some(row) = rows.iter_mut().find(|r| equal(&r[0], &index)) {
            row[1] = item;
        } else {
            rows.push(json!([index, item]));
        }
    } else if value.is_array() {
        value[n(&index) as usize] = item;
    } else {
        value[index.as_str().unwrap()] = item;
    }
    e.insert(key.into(), value);
}
fn extend_env(e: &mut Env, value: Value) {
    for pair in seq(method(value, "items", vec![])) {
        let key = ix(pair.clone(), json!(0));
        let value = ix(pair, json!(1));
        e.insert(key.as_str().unwrap().into(), value);
    }
}
fn assign_attribute(e: &mut Env, name: &str, key: &str, item: Value) {
    let mut value = g(e, name);
    storage::assign(&mut value, key, item);
    e.insert(name.into(), value);
}
fn register_path(cx: &mut Context, value: Value) {
    let text = value["$path"]
        .as_str()
        .unwrap_or_else(|| value.as_str().expect("Reference path"));
    if let Ok(relative) = Path::new(text).strip_prefix(&cx.root) {
        cx.reads
            .insert(relative.to_string_lossy().replace('\\', "/"));
    }
}
fn path(cx: &Context, name: &str) -> Value {
    json!({"$path":cx.root.join(name).to_string_lossy()})
}
fn attr_value(v: Value, key: &str) -> Value {
    if v.get("$env").is_some() || v.get("$holder").is_some() || v.get("$namespace").is_some() {
        return storage::attribute(&v, key);
    }
    if key == "parent" && v.get("$path").is_some() {
        return json!({"$path":Path::new(v["$path"].as_str().unwrap()).parent().unwrap().to_string_lossy()});
    }
    ix(v, json!(key))
}
fn attr(cx: &mut Context, module: &str, key: &str) -> Result<Value> {
    Ok(g(&globals(cx, module)?, key))
}
fn read_file(cx: &mut Context, v: Value) -> Result<Value> {
    let p = PathBuf::from(
        v["$path"]
            .as_str()
            .unwrap_or_else(|| v.as_str().expect("source path")),
    );
    if let Ok(rel) = p.strip_prefix(&cx.root) {
        cx.reads.insert(rel.to_string_lossy().replace('\\', "/"));
    }
    Ok(json!(fs::read_to_string(p)?))
}
struct Ordered(Value);
impl<'de> serde::Deserialize<'de> for Ordered {
    fn deserialize<D: serde::Deserializer<'de>>(d: D) -> std::result::Result<Self, D::Error> {
        struct Visitor;
        impl<'de> serde::de::Visitor<'de> for Visitor {
            type Value = Ordered;
            fn expecting(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
                write!(f, "a reference JSON value")
            }
            fn visit_bool<E: serde::de::Error>(self, v: bool) -> std::result::Result<Ordered, E> {
                Ok(Ordered(json!(v)))
            }
            fn visit_i64<E: serde::de::Error>(self, v: i64) -> std::result::Result<Ordered, E> {
                Ok(Ordered(json!(v)))
            }
            fn visit_u64<E: serde::de::Error>(self, v: u64) -> std::result::Result<Ordered, E> {
                Ok(Ordered(json!(v)))
            }
            fn visit_f64<E: serde::de::Error>(self, v: f64) -> std::result::Result<Ordered, E> {
                Ok(Ordered(json!(v)))
            }
            fn visit_str<E: serde::de::Error>(self, v: &str) -> std::result::Result<Ordered, E> {
                Ok(Ordered(json!(v)))
            }
            fn visit_none<E: serde::de::Error>(self) -> std::result::Result<Ordered, E> {
                Ok(Ordered(Value::Null))
            }
            fn visit_unit<E: serde::de::Error>(self) -> std::result::Result<Ordered, E> {
                Ok(Ordered(Value::Null))
            }
            fn visit_seq<A: serde::de::SeqAccess<'de>>(
                self,
                mut a: A,
            ) -> std::result::Result<Ordered, A::Error> {
                let mut rows = vec![];
                while let Some(Ordered(v)) = a.next_element::<Ordered>()? {
                    rows.push(v)
                }
                Ok(Ordered(json!(rows)))
            }
            fn visit_map<A: serde::de::MapAccess<'de>>(
                self,
                mut a: A,
            ) -> std::result::Result<Ordered, A::Error> {
                let mut rows = vec![];
                while let Some((k, Ordered(v))) = a.next_entry::<String, Ordered>()? {
                    rows.push((json!(k), v))
                }
                Ok(Ordered(object(rows)))
            }
        }
        d.deserialize_any(Visitor)
    }
}
fn parse_json(v: Value) -> Result<Value> {
    Ok(serde_json::from_str::<Ordered>(v.as_str().unwrap())?.0)
}
fn format_value(v: Value, spec: &str) -> Result<String> {
    if v.is_string() {
        let spec = spec.strip_suffix('s').unwrap_or(spec);
        let mut width = spec;
        let align = if spec.starts_with('>') {
            '>'
        } else if spec.starts_with('^') {
            '^'
        } else {
            '<'
        };
        if spec.starts_with(['<', '>', '^']) {
            width = &spec[1..]
        }
        let width = width.parse::<usize>().unwrap_or(0);
        let value = string(&v);
        return Ok(match align {
            '>' => format!("{value:>width$}"),
            '^' => format!("{value:^width$}"),
            _ => format!("{value:<width$}"),
        });
    }
    if let Some(spec) = spec.strip_suffix('d') {
        let (align, width) = if spec.starts_with(['<', '>', '^']) {
            (spec.chars().next().unwrap(), &spec[1..])
        } else {
            ('>', spec)
        };
        let width = width.parse::<usize>().unwrap_or(0);
        let value = n(&v) as i64;
        return Ok(match align {
            '<' => format!("{value:<width$}"),
            '^' => format!("{value:^width$}"),
            _ => format!("{value:>width$}"),
        });
    }
    if spec.is_empty() {
        Ok(string(&v))
    } else if spec.chars().all(|c| c.is_ascii_digit()) {
        let width = spec.parse::<usize>()?;
        Ok(if spec.starts_with('0') {
            format!("{:0width$}", n(&v) as i64)
        } else {
            format!("{:width$}", n(&v) as i64)
        })
    } else if let Some(width) = spec.strip_suffix('s') {
        let width = width.parse::<usize>().unwrap_or(0);
        Ok(format!("{:<width$}", string(&v)))
    } else {
        let split = spec
            .find('.')
            .unwrap_or_else(|| spec.len().saturating_sub(1));
        let prefix = &spec[..split];
        if !prefix.is_empty() && prefix.chars().all(|c| c.is_ascii_digit()) {
            let width = prefix.parse::<usize>()?;
            let value = hsm_documents::format_number(n(&v), &spec[split..])?;
            Ok(format!("{value:>width$}"))
        } else {
            hsm_documents::format_number(n(&v), spec)
        }
    }
}

fn argument(args: &[Value], kwargs: &Value, index: usize, name: &str) -> Value {
    args.get(index)
        .cloned()
        .or_else(|| kwarg(kwargs, name))
        .unwrap_or_else(|| missing(name))
}
fn profile(v: Value) -> Vec<[f64; 2]> {
    seq(v)
        .into_iter()
        .map(|p| [n(&ix(p.clone(), json!(0))), n(&ix(p, json!(1)))])
        .collect()
}
fn interpolate(rows: &[[f64; 2]], x: f64) -> f64 {
    let i = rows.partition_point(|p| p[0] <= x);
    if i == 0 {
        return rows[0][1];
    }
    if i == rows.len() {
        return rows[rows.len() - 1][1];
    }
    let [a, ra] = rows[i - 1];
    let [b, rb] = rows[i];
    let slope = (rb - ra) / (b - a);
    slope * (x - a) + ra
}
fn pump_barb(cx: &mut Context, port: &str) -> Result<Vec<[f64; 2]>> {
    let key = match port {
        "suction" => "port_yminus",
        "discharge" => "port_yplus",
        _ => bail!("Unknown pump joint port {port}"),
    };
    let record = call(
        cx,
        "g_ganen_pump",
        "port_profile",
        vec![json!(key)],
        json!({}),
        None,
    )?;
    let mut rows = seq(ix(record, json!("profile")))
        .into_iter()
        .map(|r| {
            [
                n(&ix(r.clone(), json!("distance_from_tip_mm"))),
                n(&ix(r, json!("radius_mm"))),
            ]
        })
        .collect::<Vec<_>>();
    rows.sort_by(|a, b| a[0].total_cmp(&b[0]).then(a[1].total_cmp(&b[1])));
    Ok(rows)
}
fn pump_bore(cx: &mut Context, port: &str) -> Result<Vec<[f64; 2]>> {
    let e = globals(cx, "pump_barb_joint")?;
    let rows = pump_barb(cx, port)?;
    let r0 = n(&g(&e, "TUBE_ID")) / 2.0;
    let start = rows[0][0] + n(&g(&e, "TUBE_ROOT_SETBACK"));
    let mut trimmed = vec![[start, interpolate(&rows, start)]];
    trimmed.extend(rows.into_iter().filter(|p| p[0] > start));
    let mut out = vec![];
    for pair in trimmed.windows(2) {
        let ([x0, a], [x1, b]) = (pair[0], pair[1]);
        out.push([x0, a.max(r0)]);
        if (a - r0) * (b - r0) < 0.0 {
            out.push([x0 + (r0 - a) / (b - a) * (x1 - x0), r0]);
        }
    }
    out.push([0.0, trimmed[trimmed.len() - 1][1].max(r0)]);
    let stem = n(&attr(cx, "jg_pp061208w", "STEM_D")?) / 2.0;
    out.extend([[0.0, stem], [n(&g(&e, "TRIM")), stem]]);
    Ok(out)
}
fn band_diameter(cx: &mut Context, port: &str, xc: f64) -> Result<f64> {
    let e = globals(cx, "pump_barb_joint")?;
    let rows = pump_bore(cx, port)?;
    let band = n(&g(&e, "BAND_W"));
    let (lo, hi) = (xc - band / 2.0, xc + band / 2.0);
    let step = (hi - lo) / 180.0;
    let largest = (0..=180)
        .map(|i| interpolate(&rows, if i == 180 { hi } else { i as f64 * step + lo }))
        .fold(f64::NEG_INFINITY, f64::max);
    let od = n(&g(&e, "TUBE_OD"));
    let id = n(&g(&e, "TUBE_ID"));
    Ok(2.0 * (largest.powi(2) + (od.powi(2) - id.powi(2)) / 4.0).sqrt())
}
fn manual(
    cx: &mut Context,
    module: &str,
    name: &str,
    args: Vec<Value>,
    kwargs: Value,
) -> Result<Value> {
    if matches!(module, "g_ganen_installation" | "g_ganen_integration")
        && matches!(
            name,
            "parameters"
                | "port"
                | "suction"
                | "discharge"
                | "port_profile"
                | "sliding_rails"
                | "mount_slots"
        )
    {
        return call(cx, "g_ganen_pump", name, args, kwargs, None);
    }
    match (module, name) {
        ("asse1022_assembly", "port") => {
            let terminal = argument(&args, &kwargs, 0, "name");
            let key = terminal.as_str().unwrap();
            if key == "vent-tip" {
                return call(cx, "multiplex_asse1022", "vent", vec![], json!({}), None);
            }
            let e = globals(cx, module)?;
            let (local, shift) = match key {
                "tube-in" => (
                    call(cx, "jg_pp010822e", "tube_port", vec![], json!({}), None)?,
                    n(&g(&e, "PTC_X")),
                ),
                "tube-out" => (
                    call(cx, "flare38_14ptc", "tube_port", vec![], json!({}), None)?,
                    n(&g(&e, "OUTLET_X")),
                ),
                _ => bail!("Unknown ASSE terminal {key}"),
            };
            let p = ix(local.clone(), json!(0));
            let z = n(&attr(cx, "multiplex_asse1022", "BODY_CENTER_Z")?);
            Ok(t(vec![
                t(vec![
                    j(n(&ix(p.clone(), json!(0))) + shift),
                    ix(p.clone(), json!(1)),
                    j(n(&ix(p, json!(2))) + z),
                ]),
                ix(local, json!(1)),
            ]))
        }
        ("pump_barb_joint", "bore") => {
            let port = argument(&args, &kwargs, 0, "port");
            Ok(json!(
                pump_bore(cx, port.as_str().unwrap())?
                    .into_iter()
                    .map(|p| t(p.into_iter().map(j).collect()))
                    .collect::<Vec<_>>()
            ))
        }
        ("pump_barb_joint", "band_d") => {
            let port = argument(&args, &kwargs, 0, "port");
            Ok(j(band_diameter(
                cx,
                port.as_str().unwrap(),
                n(&argument(&args, &kwargs, 1, "xc")),
            )?))
        }
        ("g_ganen_installation", "bearing_z_from_frame") => {
            let at = n(&argument(&args, &kwargs, 0, "at_suction_z"));
            let suction = call(cx, module, "suction", vec![], json!({}), None)?;
            let seat = call(cx, module, "mount_seat_z", vec![], json!({}), None)?;
            Ok(j(at - n(&ix(ix(suction, json!(0)), json!(2))) + n(&seat)))
        }
        ("g_ganen_foot", "observed_pose") => {
            let row = argument(&args, &kwargs, 0, "row");
            let section = ix(
                ix(ix(row.clone(), json!("pose_observations")), json!(0)),
                json!("local_slot_sections"),
            );
            let origin = ix(section.clone(), json!("local_origin_reference_mm"));
            let z = seq(ix(
                ix(section, json!("reference_to_local_rotation")),
                json!(2),
            ))
            .iter()
            .map(n)
            .collect::<Vec<_>>();
            let side = if ix(row, json!("id")).as_str().unwrap().contains("yminus") {
                -1.0
            } else {
                1.0
            };
            let mut y = vec![
                -z[0] * z[1] * side,
                side - z[1] * z[1] * side,
                -z[2] * z[1] * side,
            ];
            let norm = y.iter().map(|v| v * v).sum::<f64>().sqrt();
            for v in &mut y {
                *v /= norm
            }
            let x = [
                y[1] * z[2] - y[2] * z[1],
                y[2] * z[0] - y[0] * z[2],
                y[0] * z[1] - y[1] * z[0],
            ];
            Ok(json!({"origin":origin,"x":x,"z":z}))
        }
        ("asse1022_threaded_chain", "placement") => {
            let record = argument(&args, &kwargs, 0, "record");
            let r = ix(record.clone(), json!("rotation"));
            let t = ix(record, json!("origin_mm"));
            let at = |i, j| n(&ix(ix(r.clone(), json!(i)), json!(j)));
            let angle = ((at(0, 0) + at(1, 1) + at(2, 2) - 1.0) / 2.0)
                .clamp(-1.0, 1.0)
                .acos();
            Ok(
                json!({"angle":angle.to_degrees(),"turn":angle>1e-10,"axis":[at(2,1)-at(1,2),at(0,2)-at(2,0),at(1,0)-at(0,1)],"translation":t}),
            )
        }
        _ => storage::manual(cx, module, name, args, kwargs),
    }
}

pub(super) fn request(v: &Value) -> Result<Value> {
    let root = v["root"]
        .as_str()
        .ok_or_else(|| anyhow::anyhow!("Missing reference root"))?;
    let module = v["module"]
        .as_str()
        .ok_or_else(|| anyhow::anyhow!("Missing reference module"))?;
    let mut cx = Context {
        root: root.into(),
        reads: BTreeSet::new(),
        cache: BTreeMap::new(),
        inputs: v["inputs"].clone(),
        messages: vec![],
        overrides: v["overrides"].clone(),
        holder_updates: Value::Null,
    };
    let result = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
        if v["method"].as_str().unwrap_or("state") == "state" {
            Ok(json!(globals(&mut cx, module)?))
        } else {
            call(
                &mut cx,
                module,
                v["method"].as_str().unwrap(),
                v["args"].as_array().cloned().unwrap_or_default(),
                v.get("kwargs").cloned().unwrap_or(json!({})),
                None,
            )
        }
    }))
    .map_err(|e| {
        anyhow::anyhow!(
            "{}",
            e.downcast_ref::<String>()
                .map(String::as_str)
                .or_else(|| e.downcast_ref::<&str>().copied())
                .unwrap_or("Invalid reference data")
        )
    })??;
    Ok(
        json!({"result":result,"reads":cx.reads,"messages":cx.messages,"holder_updates":cx.holder_updates}),
    )
}
