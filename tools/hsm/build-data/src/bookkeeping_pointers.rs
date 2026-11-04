//! Ordered member-wise CAD pointer merge and native JSON rendering.
use anyhow::{Context, Result, bail};
use hsm_documents::interop::{Val, builtin_module, compare};
use serde_json::{Value, json};
use std::collections::BTreeSet;
const KEYS: [&str; 8] = [
    "_", "release", "store", "bundle", "solids", "sidecars", "moved", "made",
];
fn json_module() -> Val {
    builtin_module("json").expect("native JSON module")
}
fn parse(s: &str) -> Result<Val> {
    if s.trim().is_empty() {
        Ok(object())
    } else {
        json_module().attr("loads")?.call(vec![s.into()], vec![])
    }
}
fn render(v: &Val) -> Result<String> {
    Ok(json_module()
        .attr("dumps")?
        .call(
            vec![v.clone()],
            vec![
                ("indent".into(), Val::Int(2)),
                ("sort_keys".into(), Val::Bool(false)),
            ],
        )?
        .str()?
        + "\n")
}
fn object() -> Val {
    Val::dict(vec![])
}
fn get(v: &Val, key: &str) -> Val {
    v.get(key.into()).unwrap_or(Val::None)
}
fn has(v: &Val, key: &str) -> bool {
    v.get(key.into()).is_ok()
}
fn truth(v: &Val) -> bool {
    v.truthy().unwrap_or(false)
}
fn eq(a: &Val, b: &Val) -> bool {
    compare("eq", a.clone(), b.clone())
        .and_then(|v| v.truthy())
        .unwrap_or(false)
}
fn keys(v: &Val) -> Vec<String> {
    v.iter()
        .unwrap_or_default()
        .iter()
        .filter_map(|v| v.str().ok())
        .collect()
}
fn copy(v: &Val) -> Result<Val> {
    Ok(Val::dict(
        keys(v)
            .into_iter()
            .map(|k| Ok((k.clone().into(), v.get(k.into())?)))
            .collect::<Result<Vec<_>>>()?,
    ))
}
fn put(v: &Val, key: &str, value: Val) -> Result<()> {
    v.set(key.into(), value)
}
fn first(values: &[Val]) -> Val {
    values
        .iter()
        .find(|v| truth(v))
        .cloned()
        .unwrap_or_else(|| values.last().cloned().unwrap_or_default())
}
fn proves(line: &Val) -> bool {
    matches!(line, Val::Dict(_)) && truth(&get(line, "inputs")) && !truth(&get(line, "unproven"))
}
fn members(base: &Val, ours: &Val, theirs: &Val) -> Result<(Val, Vec<String>, Vec<String>)> {
    let out = object();
    let mut both = vec![];
    let mut notes = vec![];
    let all = keys(base)
        .into_iter()
        .chain(keys(ours))
        .chain(keys(theirs))
        .collect::<BTreeSet<_>>();
    for key in all {
        let vb = get(base, &key);
        let vo = get(ours, &key);
        let vt = get(theirs, &key);
        let value = if eq(&vo, &vt) || eq(&vt, &vb) {
            vo
        } else if eq(&vo, &vb) {
            vt
        } else if matches!(vt, Val::None) {
            both.push(key.clone());
            notes.push(format!(
                "{key}: retired on the incoming side and moved on main; main's stands"
            ));
            vo
        } else if matches!(vo, Val::None) {
            both.push(key.clone());
            notes.push(format!(
                "{key}: retired on main and moved on the incoming side; the incoming hash stands"
            ));
            vt
        } else {
            both.push(key.clone());
            notes.push(format!("{key}: moved on both sides; the incoming hash stands and its `made` line is unproven"));
            vt
        };
        if !matches!(value, Val::None) {
            put(&out, &key, value)?;
        }
    }
    Ok((out, both, notes))
}
fn made(ours: &Val, theirs: &Val, lines: &Val, both: &BTreeSet<String>) -> Result<Val> {
    let out = object();
    for relative in keys(lines).into_iter().collect::<BTreeSet<_>>() {
        let digest = get(lines, &relative);
        let mut found = vec![];
        for side in [theirs, ours] {
            let records = get(side, "made");
            let actual = if has(&get(side, "sidecars"), &relative) {
                get(&get(side, "sidecars"), &relative)
            } else {
                get(&get(side, "solids"), &relative)
            };
            if has(&records, &relative) && eq(&actual, &digest) {
                found.push(get(&records, &relative));
            }
        }
        if found.is_empty() {
            continue;
        }
        let line = found.iter().find(|v| proves(v)).unwrap_or(&found[0]);
        let line = if both.contains(&relative) {
            let v = copy(line)?;
            put(&v, "unproven", true.into())?;
            v
        } else {
            line.clone()
        };
        put(&out, &relative, line)?;
    }
    Ok(out)
}
fn seat(out: &Val, ours: &Val, theirs: &Val) -> Result<Val> {
    let mut order = KEYS
        .iter()
        .filter(|k| !matches!(get(out, k), Val::None))
        .map(|s| s.to_string())
        .collect::<Vec<_>>();
    let ours_keys = keys(ours);
    for (i, key) in ours_keys.iter().enumerate() {
        if KEYS.contains(&key.as_str())
            || !has(theirs, key)
            || !eq(&get(theirs, key), &get(ours, key))
        {
            continue;
        }
        let at = order
            .iter()
            .enumerate()
            .filter(|(_, k)| ours_keys[..i].contains(k))
            .map(|(j, _)| j + 1)
            .max()
            .unwrap_or(0);
        order.insert(at, key.clone());
        put(out, key, get(ours, key))?;
    }
    Ok(Val::dict(
        order
            .iter()
            .map(|k| (k.clone().into(), get(out, k)))
            .collect(),
    ))
}
fn merge(base: &Val, ours: &Val, theirs: &Val) -> Result<(Val, Vec<String>)> {
    if !truth(ours) {
        return Ok((copy(theirs)?, vec![]));
    }
    if !truth(theirs) {
        return Ok((copy(ours)?, vec![]));
    }
    let (solids, both_s, mut notes) = members(
        &get(base, "solids"),
        &get(ours, "solids"),
        &get(theirs, "solids"),
    )?;
    let (sidecars, both_c, n) = members(
        &get(base, "sidecars"),
        &get(ours, "sidecars"),
        &get(theirs, "sidecars"),
    )?;
    notes.extend(n);
    let digest = get(&get(base, "bundle"), "sha256");
    let ours_new = !eq(&get(&get(ours, "bundle"), "sha256"), &digest);
    let theirs_new = !eq(&get(&get(theirs, "bundle"), "sha256"), &digest);
    let mut side = if theirs_new && !ours_new {
        theirs
    } else {
        ours
    };
    if !truth(&get(side, "bundle")) {
        side = if truth(&get(theirs, "bundle")) {
            theirs
        } else {
            ours
        };
    }
    let release = object();
    for key in ["tag", "asset", "url"] {
        if has(&get(side, "release"), key) {
            put(&release, key, get(&get(side, "release"), key))?;
        }
    }
    let objects_o = get(&get(ours, "release"), "objects");
    let objects_t = get(&get(theirs, "release"), "objects");
    if truth(&objects_o) && truth(&objects_t) {
        put(&release, "objects", objects_o)?;
    }
    let bundle = copy(&get(side, "bundle"))?;
    let behind =
        truth(&get(&bundle, "behind")) || !eq(&solids, &first(&[get(side, "solids"), object()]));
    if has(&bundle, "behind") {
        bundle.delete("behind".into())?;
    }
    if behind && truth(&bundle) {
        put(&bundle, "behind", true.into())?;
    }
    let moved = object();
    for relative in keys(&solids) {
        let digest = get(&solids, &relative);
        let mut found = vec![];
        for side in [ours, theirs] {
            if eq(&get(&get(side, "solids"), &relative), &digest)
                && has(&get(side, "moved"), &relative)
            {
                found.push(get(&get(side, "moved"), &relative));
            }
        }
        if let Some(mut biggest) = found.first().cloned() {
            for v in found.into_iter().skip(1) {
                if compare("gt", v.clone(), biggest.clone())?.truthy()? {
                    biggest = v;
                }
            }
            put(&moved, &relative, biggest)?;
        }
    }
    let lines = copy(&solids)?;
    for key in keys(&sidecars) {
        put(&lines, &key, get(&sidecars, &key))?;
    }
    let both = both_s.into_iter().chain(both_c).collect();
    let made = made(ours, theirs, &lines, &both)?;
    let out = object();
    for (key, value) in [
        (
            "_",
            first(&[get(ours, "_"), get(theirs, "_"), get(base, "_")]),
        ),
        ("release", release),
        ("store", first(&[get(ours, "store"), get(theirs, "store")])),
        ("bundle", bundle),
        ("solids", solids),
        ("sidecars", sidecars),
        ("moved", if truth(&moved) { moved } else { Val::None }),
        ("made", if truth(&made) { made } else { Val::None }),
    ] {
        put(&out, key, value)?;
    }
    Ok((seat(&out, ours, theirs)?, notes))
}
pub fn dispatch(op: &str, r: &Value) -> Result<Value> {
    let args = r["args_json"]
        .as_array()
        .context("ordered JSON arguments")?
        .iter()
        .map(|v| parse(v.as_str().context("ordered JSON argument is text")?))
        .collect::<Result<Vec<_>>>()?;
    let a = |i| args.get(i).cloned().unwrap_or_default();
    let result = match op {
        "merge_members" => {
            let (v, b, n) = members(&a(0), &a(1), &a(2))?;
            Val::tuple(vec![
                v,
                Val::list(b.into_iter().map(Val::from).collect()),
                Val::list(n.into_iter().map(Val::from).collect()),
            ])
        }
        "_proves" => Val::Bool(proves(&a(0))),
        "merge_made" => made(
            &a(0),
            &a(1),
            &a(2),
            &a(3)
                .iter()?
                .iter()
                .map(Val::str)
                .collect::<Result<BTreeSet<_>>>()?,
        )?,
        "_seat" => seat(&a(0), &a(1), &a(2))?,
        "merge" => {
            let (v, n) = merge(&a(0), &a(1), &a(2))?;
            Val::tuple(vec![v, Val::list(n.into_iter().map(Val::from).collect())])
        }
        "render" => return Ok(json!(render(&a(0))?)),
        "merge_texts" => {
            let (v, n) = merge(
                &parse(&a(0).str()?)?,
                &parse(&a(1).str()?)?,
                &parse(&a(2).str()?)?,
            )?;
            Val::tuple(vec![
                render(&v)?.into(),
                Val::list(n.into_iter().map(Val::from).collect()),
            ])
        }
        _ => bail!("unknown pointer merge operation {op}"),
    };
    Ok(json!(render(&result)?))
}
