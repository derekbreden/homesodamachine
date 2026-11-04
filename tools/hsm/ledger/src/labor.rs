use crate::{printing, shared::*};
use anyhow::{Context as _, Result, bail, ensure};
use hsm_documents::Variables;
use serde_json::{Value, json};
use std::collections::BTreeMap;

const BATCH: f64 = 10.;
const RATE: f64 = 100.;
const INCREMENTS: [f64; 17] = [
    5., 10., 15., 20., 25., 30., 45., 60., 75., 90., 105., 120., 150., 180., 240., 300., 360.,
];
fn run_ladder() -> Vec<f64> {
    [
        5. / 60.,
        10. / 60.,
        15. / 60.,
        30. / 60.,
        45. / 60.,
        1.,
        2.,
        3.,
    ]
    .into_iter()
    .chain(INCREMENTS)
    .collect()
}
fn hm(mins: f64) -> String {
    let total = (mins + 0.5).floor() as i64;
    let (h, m) = (total.div_euclid(60), total.rem_euclid(60));
    if h == 0 {
        format!("{m} m")
    } else if m == 0 {
        format!("{h} h")
    } else {
        format!("{h} h {m} m")
    }
}
fn short(mins: f64) -> String {
    if mins < 1. {
        format!("{} s", fmt((mins * 60.).round_ties_even(), ".0f"))
    } else {
        hm(mins)
    }
}
fn figure(mins: f64) -> String {
    fmt(round(mins + 1e-9, 1), ",g")
}
fn usd(mins: f64) -> String {
    money(mins / 60. * RATE)
}
fn minutes(cell: &str) -> f64 {
    re(r"^\**\s*\[?([0-9][0-9,]*(?:\.[0-9]+)?)\]?")
        .captures(cell)
        .and_then(|c| c[1].replace(',', "").parse().ok())
        .unwrap_or(0.)
}
fn duration(text: &str) -> Option<f64> {
    let caps = re(r"^(?:([0-9]+) h)? ?(?:([0-9]+) m)? ?(?:([0-9]+) s)?$").captures(text.trim())?;
    if (1..=3).all(|i| caps.get(i).is_none()) {
        return None;
    }
    let get = |i| {
        caps.get(i)
            .map(|s| s.as_str().parse::<f64>().unwrap())
            .unwrap_or(0.)
    };
    Some(get(1) * 60. + get(2) + get(3) / 60.)
}
fn run_of(cell: &str) -> Value {
    let cleaned = re(r"\s+").replace_all(cell.trim(), " ");
    let pattern = r"^(?P<setup>[0-9][0-9 hms]*?) setup an? (?P<run>[a-z][a-z-]*)(?: of (?P<cap>[0-9]+))? · (?P<each>[0-9][0-9 hms]*?) an? (?P<piece>[a-z][a-z -]*?) · (?P<per>[0-9]+) an? machine$";
    let Some(m) = re(pattern).captures(&cleaned) else {
        return json!("is not `<setup> setup a <run> of <n> · <time> a <piece> · <n> a machine`");
    };
    let (setup, each) = (duration(&m["setup"]), duration(&m["each"]));
    let (Some(setup), Some(each)) = (setup, each) else {
        return json!("has a time that is not `30 s`, `15 m` or `1 h 15 m`");
    };
    let cap = m.name("cap").map(|s| s.as_str().parse::<i64>().unwrap());
    if (&m["run"] == "batch") != cap.is_none() {
        return json!("sizes a batch, or leaves another run unsized");
    }
    json!({"setup":setup,"run":&m["run"],"cap":cap,"each":each,"piece":&m["piece"],"per":m["per"].parse::<i64>().unwrap()})
}
fn per_machine(run: &Value, batch: f64) -> Result<f64> {
    let pieces = batch * num(&run["per"])?;
    let runs = if run["cap"].is_null() {
        1.
    } else {
        (pieces / num(&run["cap"])?).ceil()
    };
    Ok((runs * num(&run["setup"])? + pieces * num(&run["each"])?) / batch)
}
fn on_ladder(value: f64, ladder: &[f64]) -> bool {
    ladder.iter().any(|i| (value - i).abs() < 1e-6)
}
fn nearest(value: f64, ladder: &[f64]) -> f64 {
    *ladder
        .iter()
        .min_by(|a, b| {
            ((*a - value).abs())
                .total_cmp(&(*b - value).abs())
                .then(a.total_cmp(b))
        })
        .unwrap()
}
fn parse(lines: &[String]) -> Result<(Vec<Value>, Vec<String>)> {
    let (mut rows, mut offenders, mut current, mut sub, mut col) =
        (vec![], vec![], None, None, None);
    for (i, line) in lines.iter().enumerate() {
        if line.starts_with("## ") {
            current = section(line);
            sub = None;
            continue;
        }
        if let Some(heading) = line.strip_prefix("### ") {
            sub = Some(heading.trim().to_owned());
            continue;
        }
        let Some(section) = current else { continue };
        if !line.starts_with('|') {
            continue;
        }
        let c = cells(line);
        if c.len() < 2 || separator(&c) {
            continue;
        }
        let first = c[0].trim();
        if first.to_lowercase() == "operation" {
            col = c.iter().position(|v| v == "Run");
            continue;
        }
        if first.starts_with("**") {
            continue;
        }
        let loc = format!("  §{section} {}", text_prefix(first, 52));
        let spec = col
            .filter(|j| *j < c.len() - 1)
            .map(|j| c[j].as_str())
            .unwrap_or("");
        if !spec.is_empty() {
            let run = run_of(spec);
            if let Some(error) = run.as_str() {
                offenders.push(format!("{loc}: Run cell {error}"));
                rows.push(json!([
                    i,
                    section,
                    sub,
                    first,
                    minutes(c.last().unwrap()),
                    Value::Null
                ]));
                continue;
            }
            for label in ["setup", "each"] {
                let v = num(&run[label])?;
                let ladder = run_ladder();
                if !on_ladder(v, &ladder) {
                    offenders.push(format!(
                        "{loc}: {label} {} — say {}",
                        short(v),
                        short(nearest(v, &ladder))
                    ));
                }
            }
            rows.push(json!([
                i,
                section,
                sub,
                first,
                figure(per_machine(&run, BATCH)?)
                    .replace(',', "")
                    .parse::<f64>()?,
                run
            ]));
            continue;
        }
        let v = minutes(c.last().unwrap());
        if !on_ladder(v, &INCREMENTS) {
            offenders.push(format!(
                "{loc}: {} min — say {}",
                figure(v),
                hm(nearest(v, &INCREMENTS))
            ));
        }
        rows.push(json!([i, section, sub, first, v, Value::Null]));
    }
    Ok((rows, offenders))
}
fn write_runs(lines: &[String], rows: &[Value]) -> Result<Vec<String>> {
    let mut out = lines.to_vec();
    for row in rows {
        if row[5].is_null() {
            continue;
        }
        let i = row[0].as_u64().context("labor row index")? as usize;
        let trimmed = out[i]
            .trim_end()
            .strip_suffix('|')
            .unwrap_or(out[i].trim_end());
        let (head, last) = trimmed.rsplit_once('|').context("labor run row")?;
        let tail = re(r"^(\s*)[0-9][0-9.,]*").replacen(last, 1, |m: &regex::Captures| {
            format!("{}{}", &m[1], figure(row[4].as_f64().unwrap()))
        });
        out[i] = format!("{head}|{tail}|");
    }
    Ok(out)
}
pub fn casting_estimate(request: &Value, ctx: &mut Context) -> Result<Value> {
    let path = ctx.path(
        request,
        "design",
        "hardware/printed-parts/zone-c/funnel-mold/design.json",
    );
    let data = ctx.json(path)?;
    let volume = num(&data["volume_ml"]["funnel"])?;
    ensure!(volume > 0., "Funnel CAD volume must be positive");
    let density = request["density"].as_f64().unwrap_or(1.13);
    let allowance = request["allowance"].as_f64().unwrap_or(0.10);
    let finished = volume * density;
    Ok(
        json!({"volume_ml":volume,"density_g_ml":density,"finished_g":finished,"mix_allowance":allowance,"mixed_g":finished*(1.+allowance)}),
    )
}
pub fn casting_figures(est: &Value) -> Result<Variables> {
    Ok(Variables::from([
        (
            "FUNNEL_VOLUME_ML".into(),
            fmt(num(&est["volume_ml"])?, ".1f"),
        ),
        (
            "FUNNEL_DENSITY_G_ML".into(),
            fmt(num(&est["density_g_ml"])?, ".2f"),
        ),
        (
            "FUNNEL_FINISHED_G".into(),
            fmt(num(&est["finished_g"])?, ".0f"),
        ),
        (
            "FUNNEL_MIX_ALLOWANCE".into(),
            format!("{}%", fmt(num(&est["mix_allowance"])? * 100., ".0f")),
        ),
        ("FUNNEL_MIXED_G".into(), fmt(num(&est["mixed_g"])?, ".0f")),
    ]))
}
fn main(request: &Value, ctx: &mut Context) -> Result<Value> {
    let path = ctx.path(request, "labor", "hardware/ledger/labor.md");
    let text = ctx.read(&path)?;
    let lines = text.lines().map(str::to_owned).collect::<Vec<_>>();
    let (rows, offenders) = parse(&lines)?;
    let mut sums = BTreeMap::new();
    let mut printed = 0.;
    for row in &rows {
        let n = row[1].as_i64().unwrap();
        let v = num(&row[4])?;
        *sums.entry(n).or_insert(0.) += v;
        if row[2].as_str() == Some("Printed parts") {
            printed += v;
        }
    }
    let grand = sums.values().sum();
    let printing = printing::estimate(request, ctx)?;
    let orphans = strings(&printing["unassigned"])?;
    if !orphans.is_empty() {
        return Ok(main_result(
            1,
            format!(
                "bom.md §7 rows with no machine-time rate group:\n{}\n",
                orphans.join("\n")
            ),
        ));
    }
    let mut vars = Variables::from([
        ("BATCH_SIZE".into(), "10".into()),
        ("LABOR_RATE".into(), "$100".into()),
        ("LAB_HM_PRINTED".into(), hm(printed)),
        (
            "LAB_PRINT_KG".into(),
            fmt(num(&printing["total_kg"])?, ".3f"),
        ),
        (
            "LAB_PRINT_H".into(),
            fmt(num(&printing["total_hours"])?, ".1f"),
        ),
    ]);
    let cast = casting_estimate(request, ctx)?;
    vars.extend(casting_figures(&cast)?);
    for (n, v) in &sums {
        vars.insert(format!("LAB_SEC{n}"), figure(*v));
        vars.insert(format!("LAB_HM{n}"), hm(*v));
        vars.insert(format!("LAB_USD{n}"), usd(*v));
    }
    vars.insert("LAB_HM".into(), hm(grand));
    vars.insert("LAB_USD".into(), usd(grand));
    let written = write_runs(&lines, &rows)?;
    if request["check"].as_bool().unwrap_or(false) {
        if !offenders.is_empty() {
            return Ok(main_result(
                1,
                format!(
                    "labor.md estimates off the increment ladder:\n{}\n",
                    offenders.join("\n")
                ),
            ));
        }
        let mut stale = stale(&text, &vars);
        for row in &rows {
            let i = row[0].as_u64().unwrap() as usize;
            if !row[5].is_null() && written[i] != lines[i] {
                let c = cells(&lines[i]);
                stale.push(format!(
                    "  {}: {} min should be {}",
                    text_prefix(&c[0], 52),
                    figure(minutes(c.last().unwrap())),
                    figure(num(&row[4])?)
                ));
            }
        }
        return Ok(if stale.is_empty() {
            main_result(0, "labor.md totals ✓\n".into())
        } else {
            main_result(
                1,
                format!(
                    "labor.md markers are stale — run _labor_totals.py:\n{}\n",
                    stale.join("\n")
                ),
            )
        });
    }
    if written != lines {
        ctx.write(&path, (written.join("\n") + "\n").as_bytes())?;
    }
    ctx.substitute(&path, &vars, "/hardware/scripts/_labor_totals.py")?;
    let mut out = String::new();
    for (n, v) in &sums {
        out += &format!("  §{n:<2} {:>10}   {:>10}\n", hm(*v), usd(*v));
    }
    out += &format!("  ── {:>10}   {:>10}\n", hm(grand), usd(grand));
    if !offenders.is_empty() {
        out += &format!("\noff the increment ladder:\n{}\n", offenders.join("\n"));
    }
    Ok(main_result(0, out))
}
pub fn dispatch(op: &str, r: &Value, ctx: &mut Context) -> Result<Value> {
    Ok(match op {
        "constants" => {
            json!({"batch_size":10,"labor_rate":100,"increments":INCREMENTS,"run_increments":run_ladder()})
        }
        "hm" => json!(hm(num(&r["minutes"])?)),
        "short" => json!(short(num(&r["minutes"])?)),
        "figure" => json!(figure(num(&r["minutes"])?)),
        "usd" => json!(usd(num(&r["minutes"])?)),
        "minutes" => json!(minutes(arg(r, "cell")?)),
        "duration" => json!(duration(arg(r, "text")?)),
        "run_of" => run_of(arg(r, "cell")?),
        "per_machine" => json!(per_machine(
            &r["run"],
            r["batch"].as_f64().unwrap_or(BATCH)
        )?),
        "on_ladder" => json!(on_ladder(
            num(&r["value"])?,
            &r["ladder"]
                .as_array()
                .context("ladder array")?
                .iter()
                .map(num)
                .collect::<Result<Vec<_>>>()?
        )),
        "parse" => json!(parse(&strings(&r["lines"])?)?),
        "write_runs" => json!(write_runs(
            &strings(&r["lines"])?,
            r["rows"].as_array().context("labor rows")?
        )?),
        "casting_estimate" => casting_estimate(r, ctx)?,
        "casting_figures" => {
            let est = casting_estimate(r, ctx)?;
            json!(casting_figures(&est)?)
        }
        "main" => main(r, ctx)?,
        _ => bail!("unknown labor operation: {op}"),
    })
}
