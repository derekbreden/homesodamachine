use crate::shared::*;
use anyhow::{Context as _, Result, bail, ensure};
use hsm_documents::Variables;
use serde_json::{Value, json};
use std::{
    collections::{BTreeMap, BTreeSet, HashMap},
    path::{Path, PathBuf},
};

pub fn definitions() -> Value {
    let mut defs: Value = serde_json::from_str(include_str!("../catalog/printing.json"))
        .expect("print model declarations");
    let models = defs["parts"]
        .as_object()
        .unwrap()
        .values()
        .flat_map(|p| p.as_array().unwrap())
        .map(|p| {
            let step = p.as_str().unwrap();
            (step.to_owned(), json!(format!("{step}.npz")))
        })
        .collect::<serde_json::Map<String, Value>>();
    defs["model_of"] = json!(models);
    defs
}
const GROUPS: [(&str, &str); 10] = [
    ("shell", "SHELL"),
    ("cover", "FUNNEL_COVER"),
    ("bulk", "BULK"),
    ("ext", "EXT"),
    ("tight", "TIGHT"),
    ("small", "SMALL"),
    ("tool", "TOOL"),
    ("petgf", "PETGF"),
    ("rings", "RINGS"),
    ("aero", "AERO"),
];
const PRINTERS: f64 = 2.;
const DUTY: f64 = 0.65;

fn group_hits(label: &str) -> Vec<String> {
    definitions()["group_of"]
        .as_array()
        .unwrap()
        .iter()
        .filter(|v| label.contains(v[0].as_str().unwrap()))
        .map(|v| v[1].as_str().unwrap().to_owned())
        .collect()
}
fn group_of(label: &str) -> Result<String> {
    let hits = group_hits(label);
    ensure!(
        hits.len() == 1,
        "_bom_masses: §7 row {label:?} matches {} print configurations. Give it exactly one entry in GROUP_OF — a printed part cannot be priced without the plate it comes off.",
        hits.len()
    );
    Ok(hits[0].clone())
}
fn material_of(cell: &str) -> Result<String> {
    let name = cell.split('(').next().unwrap_or("").trim();
    ensure!(
        !definitions()["materials"][name].is_null(),
        "_bom_masses: no density for material {cell:?}"
    );
    Ok(name.to_owned())
}
fn drawn(path: &Path, ctx: &mut Context) -> Result<(f64, f64)> {
    ctx.reads.insert(path.to_string_lossy().into_owned());
    let (mut volume, mut area) = (0., 0.);
    hsm_kernel::import::visit_model(path, |_, body| {
        let solid = body.solid;
        let sum = solid
            .tris()
            .iter()
            .map(|t| {
                solid.verts()[t[0] as usize]
                    .dot(solid.verts()[t[1] as usize].cross(solid.verts()[t[2] as usize]))
            })
            .sum::<f64>();
        volume += sum / 6.;
        area += solid.area();
        Ok(())
    })?;
    Ok((volume, area))
}
fn measure(
    rel: &str,
    parts_dir: &Path,
    cache: &mut HashMap<String, (f64, f64)>,
    ctx: &mut Context,
) -> Result<(f64, f64)> {
    if let Some(value) = cache.get(rel) {
        return Ok(*value);
    }
    let path = parts_dir.join(rel);
    ensure!(
        path.exists(),
        "_bom_masses: {rel} has no STEP at {}",
        path.display()
    );
    ctx.reads.insert(path.to_string_lossy().into_owned());
    let defs = definitions();
    ensure!(
        defs["parts"].as_object().unwrap().values().any(|rows| rows
            .as_array()
            .unwrap()
            .iter()
            .any(|r| r.as_str() == Some(rel))),
        "_bom_masses: {rel} names no owned fine model"
    );
    let (volume, area) = drawn(&parts_dir.join(format!("{rel}.npz")), ctx)?;
    let value = (volume / 1000., area / 100.);
    cache.insert(rel.to_owned(), value);
    Ok(value)
}
fn laid(volume: f64, area: f64, group: &str) -> Result<f64> {
    let defs = definitions();
    let p = defs["profiles"][group]
        .as_array()
        .context("unknown print profile")?;
    let (shell, width, infill) = (num(&p[0])?, num(&p[1])?, num(&p[2])?);
    let wall = 20. * volume / area;
    let both = 2. * shell;
    let (laid, density) = if wall > both {
        (both, infill)
    } else {
        ((wall / width).floor() * width, infill.max(0.5))
    };
    Ok(volume * (laid + density * (wall - laid)) / wall)
}
fn mass_kg(
    label: &str,
    material: &str,
    dir: &Path,
    cache: &mut HashMap<String, (f64, f64)>,
    ctx: &mut Context,
) -> Result<f64> {
    let defs = definitions();
    let paths=defs["parts"][label].as_array().with_context(||format!("_bom_masses: §7 row {label:?} names no geometry. Add it to PARTS (or drop the row) — a printed part with no solid has no mass."))?;
    let group = group_of(label)?;
    let mut sum = 0.;
    for path in paths {
        let (v, a) = measure(path.as_str().unwrap(), dir, cache, ctx)?;
        sum += laid(v, a, &group)?;
    }
    Ok(sum * num(&defs["materials"][material][0])? / 1000.)
}
pub fn number(cell: &str) -> f64 {
    re(r"^\**\s*\[?(-?[0-9][0-9,]*(?:\.[0-9]+)?)\]?")
        .captures(cell)
        .and_then(|c| c[1].replace(',', "").parse().ok())
        .unwrap_or(0.)
}
fn is_data_row(c: &[String]) -> bool {
    if c.len() < 2 || separator(c) {
        return false;
    }
    let first = c[0].trim().to_lowercase();
    !first.starts_with("**")
        && !["part", "group", "process", "stage", "machine", ""].contains(&first.as_str())
}
fn printed_parts(text: &str) -> Result<Vec<(String, f64)>> {
    let (mut current, mut out) = (None, vec![]);
    for line in text.lines() {
        if line.starts_with("## ") {
            current = section(line);
            continue;
        }
        if current != Some(7) || !line.starts_with('|') {
            continue;
        }
        let c = cells(line);
        if !is_data_row(&c) || c.len() < 5 || c[0].to_lowercase().contains("total") {
            continue;
        }
        out.push((
            c[0].clone(),
            c[c.len() - 2].parse().context("BOM print mass")?,
        ));
    }
    Ok(out)
}
fn group_masses(text: &str) -> Result<(BTreeMap<String, f64>, Vec<String>)> {
    let mut kg = GROUPS
        .iter()
        .map(|(g, _)| (g.to_string(), 0.))
        .collect::<BTreeMap<_, _>>();
    let mut orphans = vec![];
    for (name, mass) in printed_parts(text)? {
        let hits = group_hits(&name);
        if hits.len() != 1 {
            orphans.push(format!(
                "  §7 {}: {} rate group",
                text_prefix(&name, 60),
                if hits.is_empty() { "no" } else { "ambiguous" }
            ));
            continue;
        }
        *kg.get_mut(&hits[0]).unwrap() += mass;
    }
    Ok((kg, orphans))
}
pub fn estimate(request: &Value, ctx: &mut Context) -> Result<Value> {
    let bom = ctx.path(request, "bom", "hardware/ledger/bom.md");
    let text = ctx.read(bom)?;
    let (mut kg, orphans) = group_masses(&text)?;
    let shell=ctx.json(ctx.path(request,"shell_slice","hardware/printed-parts/cold-core/foam-shell/prints/2026-10-26-mark2-round-ports-a2/preparation.json"))?;
    let shell_hours = num(&shell["native_slice"]["estimated_total_seconds"])? / 3600.;
    let faucet = ctx.json(ctx.path(
        request,
        "faucet_slice",
        "hardware/printed-parts/faucet/faucet-petgf.support-audit.json",
    ))?;
    let faucet_hours = faucet["plates"]
        .as_array()
        .context("faucet plates")?
        .iter()
        .map(|v| num(&v["estimated_total_seconds"]))
        .collect::<Result<Vec<_>>>()?
        .iter()
        .sum::<f64>()
        / 3600.;
    ensure!(
        faucet_hours > 0. && kg["petgf"] > 0.,
        "Faucet slice duration and filament mass must be positive"
    );
    let floats: Vec<_> = text
        .lines()
        .filter(|s| s.starts_with('|'))
        .map(cells)
        .filter(|c| c.first().is_some_and(|s| s == "ASA Aero magnetic float"))
        .collect();
    ensure!(
        floats.len() == 1 && floats[0].len() == 5,
        "Expected one ASA Aero magnetic float BOM row"
    );
    let qty = number(&floats[0][2]);
    ensure!(
        qty > 0. && qty.fract() == 0.,
        "ASA Aero float BOM quantity must be a positive integer"
    );
    let float=ctx.json(ctx.path(request,"float_slice","hardware/printed-parts/cold-core/magnetic-float/all-aero/mark2-print/v1/float-preflight.json"))?;
    let float = &float["native_slice_summary"];
    ensure!(
        num(&float["object_count"])? == 1.,
        "ASA Aero reference slice must contain one float"
    );
    let float_hours = num(&float["estimated_time_s"])? / 3600.;
    let float_kg = num(&float["object_feed_mass_g"])? / 1000.;
    ensure!(
        float_hours > 0. && float_kg > 0.,
        "ASA Aero slice duration and object feed must be positive"
    );
    kg.insert("aero".into(), qty * float_kg);
    let bulk_petg = round((14. + 22. / 60.) / 1.126, 1);
    let mut rates = BTreeMap::from([
        ("shell".to_owned(), round(shell_hours / kg["shell"], 1)),
        ("bulk".into(), round(shell_hours / kg["shell"], 1)),
        ("ext".into(), round((20. + 23. / 60.) / 0.653, 1)),
        ("tight".into(), round(bulk_petg * 2., 0)),
        ("small".into(), round(bulk_petg * 2.8, 0)),
        ("tool".into(), round(bulk_petg * 2.8, 0)),
        ("rings".into(), round(bulk_petg * 2.8, 0)),
        ("petgf".into(), round(faucet_hours / kg["petgf"], 1)),
        ("aero".into(), round(float_hours / float_kg, 1)),
    ]);
    let cover = ctx.json(ctx.path(
        request,
        "cover_slice",
        "hardware/printed-parts/zone-c/funnel-cover/native-slice-review.json",
    ))?;
    let cover_hours = num(&cover["estimated_seconds"])? / 3600.;
    let cover_kg = num(&cover["estimated_grams"])? / 1000. * 1.27
        / num(&cover["saved_profile_filament_density_g_cm3"][0])?;
    ensure!(
        cover_hours > 0. && kg["cover"] > 0.,
        "Funnel-cover native duration and BOM mass must be positive"
    );
    rates.insert("cover".into(), round(cover_hours / cover_kg, 1));
    let mut hours: BTreeMap<_, _> = kg.iter().map(|(g, v)| (g.clone(), *v * rates[g])).collect();
    hours.insert("shell".into(), shell_hours);
    hours.insert("petgf".into(), faucet_hours);
    hours.insert("aero".into(), qty * float_hours);
    let total_kg: f64 = GROUPS.iter().map(|(g, _)| kg[*g]).sum();
    let total_hours: f64 = GROUPS.iter().map(|(g, _)| hours[*g]).sum();
    Ok(
        json!({"kg":kg,"rates":rates,"hours":hours,"unassigned":orphans,"total_kg":total_kg,"total_hours":total_hours,"float_qty":qty as i64,"float_minutes":float_hours*60.}),
    )
}
fn read_sections(text: &str) -> (BTreeMap<i64, f64>, Vec<(i64, String, f64)>) {
    let (mut sums, mut rows, mut current) = (BTreeMap::new(), vec![], None);
    for line in text.lines() {
        if line.starts_with("## ") {
            current = section(line);
            continue;
        }
        let Some(s) = current else { continue };
        if !line.starts_with('|') {
            continue;
        }
        let c = cells(line);
        if !is_data_row(&c) {
            continue;
        }
        let hours = number(c.last().unwrap());
        *sums.entry(s).or_insert(0.) += hours;
        rows.push((s, c[0].clone(), hours));
    }
    (sums, rows)
}
fn turnaround(text: &str, wall: f64) -> f64 {
    let (mut total, mut inside) = (wall, false);
    for line in text.lines() {
        if line.starts_with("## ") {
            inside = line.starts_with("## Turnaround");
            continue;
        }
        if !inside || !line.starts_with('|') {
            continue;
        }
        let c = cells(line);
        if !is_data_row(&c) || c.len() < 2 || c[1].contains("(MT_H_PRINT_WALL)") {
            continue;
        }
        total += number(&c[1]);
    }
    total
}
fn ceiling(hours: f64) -> f64 {
    if hours == 0. {
        0.
    } else {
        (24. * 365. / hours).round_ties_even()
    }
}

fn machine_main(request: &Value, ctx: &mut Context) -> Result<Value> {
    let est = estimate(request, ctx)?;
    let kg = &est["kg"];
    let rates = &est["rates"];
    let hours = &est["hours"];
    let print = num(&est["total_hours"])?;
    let wall = print / PRINTERS;
    let path = ctx.path(request, "machine_time", "hardware/ledger/machine-time.md");
    let text = ctx.read(&path)?;
    let (secs, rows) = read_sections(&text);
    let turn = turnaround(&text, wall);
    let get = |s| secs.get(&s).copied().unwrap_or(0.);
    let occ = BTreeMap::from([
        ("PRINT", wall),
        ("BENCH", get(4)),
        (
            "MOLD",
            rows.iter()
                .filter(|(s, n, _)| *s == 2 && n.contains("Silicone funnel"))
                .map(|(_, _, h)| *h)
                .sum(),
        ),
        ("CARBONATOR", get(3)),
    ]);
    let mut vars = Variables::from([
        ("MT_PRINTERS".into(), "2".into()),
        ("MT_MEASURED".into(), "14 h 22 m".into()),
        ("MT_MEASURED_KG".into(), "1.126".into()),
        (
            "MT_RATE_BULK_PETG".into(),
            fmt(round((14. + 22. / 60.) / 1.126, 1), "g"),
        ),
        (
            "MT_PETGF_CARRY".into(),
            format!(
                "{} %",
                fmt(((21. * 1.27) / (18. * 1.43) - 1.) * 100., ".1f")
            ),
        ),
        ("MT_MEASURED_EXT".into(), "20 h 23 m".into()),
        ("MT_MEASURED_EXT_KG".into(), "0.653".into()),
        ("MT_PETGF_DRY".into(), "10 h at 100 °C".into()),
        ("MT_DUTY".into(), "65 %".into()),
        ("MT_KG".into(), fmt(num(&est["total_kg"])?, ".3f")),
        ("MT_FLOAT_QTY".into(), est["float_qty"].to_string()),
        (
            "MT_FLOAT_MINUTES".into(),
            fmt(num(&est["float_minutes"])?, ".1f"),
        ),
        (
            "MT_KG_PETG_UNIT".into(),
            fmt(
                num(&kg["tight"])? + num(&kg["small"])? + num(&kg["cover"])?,
                ".2f",
            ),
        ),
        ("MT_H_PRINT".into(), fmt(print, ".1f")),
        ("MT_H_PRINT_WALL".into(), fmt(wall, ".1f")),
        ("MT_H_CURE".into(), fmt(get(2), ".1f")),
        ("MT_H_SOAK".into(), fmt(get(3), ".1f")),
        ("MT_H_RUN".into(), fmt(get(4), ".1f")),
        (
            "MT_UNITS_YEAR".into(),
            format!("~{}", fmt((ceiling(wall) * DUTY).round_ties_even(), ",.0f")),
        ),
        (
            "MT_UNITS_YEAR_3".into(),
            format!(
                "~{}",
                fmt(
                    (24. * 365. / (print / (PRINTERS + 1.)) * DUTY).round_ties_even(),
                    ",.0f"
                )
            ),
        ),
        ("MT_H_TURN".into(), fmt(turn, ".1f")),
        ("MT_DAYS_TURN".into(), fmt(turn / 24., ".1f")),
    ]);
    for key in ["BENCH", "MOLD", "CARBONATOR"] {
        vars.insert(format!("MT_OCC_{key}"), fmt(occ[key], ".1f"));
    }
    for (key, h) in &occ {
        vars.insert(format!("MT_CEIL_{key}"), fmt(ceiling(*h), ",.0f"));
    }
    for (g, tag) in GROUPS {
        vars.insert(format!("MT_RATE_{tag}"), fmt(num(&rates[g])?, "g"));
        vars.insert(format!("MT_KG_{tag}"), fmt(num(&kg[g])?, ".3f"));
        vars.insert(format!("MT_H_{tag}"), fmt(num(&hours[g])?, ".1f"));
    }
    let orphans = strings(&est["unassigned"])?;
    if request["check"].as_bool().unwrap_or(false) {
        if !orphans.is_empty() {
            return Ok(main_result(
                1,
                format!(
                    "bom.md §7 rows with no machine-time rate group:\n{}\n",
                    orphans.join("\n")
                ),
            ));
        }
        let stale = stale(&text, &vars);
        return Ok(if stale.is_empty() {
            main_result(0, "machine-time.md totals ✓\n".into())
        } else {
            main_result(
                1,
                format!(
                    "machine-time.md markers are stale — run _machine_time.py:\n{}\n",
                    stale.join("\n")
                ),
            )
        });
    }
    ctx.substitute(&path, &vars, "/hardware/scripts/_machine_time.py")?;
    let mut out = String::new();
    for (g, _) in GROUPS {
        let rate = num(&rates[g])?;
        let rate_text = if ["tight", "small", "tool", "rings"].contains(&g) {
            fmt(rate, "g")
        } else {
            fmt(rate, ".1f")
        };
        out += &format!(
            "  {g:<6} {:6.3} kg × {:>4} h/kg = {:6.1} h\n",
            num(&kg[g])?,
            rate_text,
            num(&hours[g])?
        );
    }
    out += &format!(
        "  {:<6} {:6.3} kg{:14} {print:6.1} h   → {wall:.1} h on 2 printers\n",
        "PRINT",
        num(&est["total_kg"])?,
        ""
    );
    out += &format!(
        "  cure {:.1} h · soak {:.1} h · run {:.1} h\n",
        get(2),
        get(3),
        get(4)
    );
    for key in ["PRINT", "BENCH", "MOLD", "CARBONATOR"] {
        let h = occ[key];
        out += &format!(
            "  {:<6} occupied {h:5.1} h/unit → ceiling {:>6}/yr\n",
            key.to_lowercase(),
            fmt(ceiling(h), ",.0f")
        );
    }
    out += &format!(
        "  throughput  {}/yr at 65% duty\n  turnaround  {turn:.1} h = {:.1} days\n",
        fmt((ceiling(wall) * DUTY).round_ties_even(), ",.0f"),
        turn / 24.
    );
    if !orphans.is_empty() {
        out += &format!("\nunassigned §7 rows:\n{}\n", orphans.join("\n"))
    }
    Ok(main_result(0, out))
}

fn mass_main(request: &Value, ctx: &mut Context) -> Result<Value> {
    let path = ctx.path(request, "bom", "hardware/ledger/bom.md");
    let text = ctx.read(&path)?;
    let dir = ctx.path(request, "parts_dir", "hardware/printed-parts");
    let defs = definitions();
    let mut cache = HashMap::new();
    let mut seen = BTreeSet::new();
    let mut totals = BTreeMap::new();
    let (mut out, mut drift, mut translucent) = (vec![], vec![], 0.);
    for line in text.lines() {
        if !line.contains("<!--@printed-->") {
            out.push(line.to_owned());
            continue;
        }
        let mut c = cells(line);
        ensure!(c.len() >= 5, "invalid printed BOM row");
        let label = c[0].clone();
        let mat = material_of(&c[2])?;
        let kg = mass_kg(&label, &mat, &dir, &mut cache, ctx)?;
        seen.insert(label.clone());
        *totals.entry(mat.clone()).or_insert(0.) += kg;
        if c[2].contains("translucent") {
            translucent += kg
        }
        let cost = kg * num(&defs["materials"][&mat][1])?;
        let want = fmt(kg, ".3f");
        if c[3] != want {
            drift.push(format!("  {label}: {} -> {want} kg", c[3]));
        }
        c[3] = want;
        c[4] = re(r"(?:\$[0-9.,]+|—)")
            .replacen(&c[4], 1, regex::NoExpand(&format!("${cost:.2}")))
            .into_owned();
        out.push(format!("| {} |", c.join(" | ")));
    }
    let missing: Vec<_> = defs["parts"]
        .as_object()
        .unwrap()
        .keys()
        .filter(|k| !seen.contains(*k))
        .cloned()
        .collect();
    ensure!(
        missing.is_empty(),
        "_bom_masses: PARTS names rows §7 does not have: {}",
        missing.join(", ")
    );
    let grand: f64 = totals.values().sum();
    let petg = totals.get("PETG").copied().unwrap_or(0.);
    let petgf = totals.get("PET-GF").copied().unwrap_or(0.);
    let summary = format!(
        "By material: PETG ≈ {petg:.2} kg / {} — of which the four translucent reservoir parts are ≈ {translucent:.2} kg / {} — and PET-GF ≈ {petgf:.2} kg / {}.",
        money(petg * 11.20),
        money(translucent * 11.20),
        money(petgf * 25.02)
    );
    for line in &mut out {
        if line.starts_with("| **Printed parts total**") {
            let stated = cells(line)[3].clone();
            let want = format!("**~{grand:.2}**");
            if stated != want {
                drift.push(format!("  Printed parts total: {stated} -> {want} kg"));
                *line = line.replacen(&stated, &want, 1);
            }
        } else if line.starts_with("By material: PETG") {
            if *line != summary {
                drift.push("  By material line".into())
            }
            *line = summary.clone();
        }
    }
    if request["check"].as_bool().unwrap_or(false) {
        return Ok(if drift.is_empty() {
            main_result(0, "_bom_masses: §7 matches the solids ✓\n".into())
        } else {
            main_result(
                1,
                format!(
                    "_bom_masses: §7 disagrees with the solids it is derived from:\n{}\n\n  fix: tools/cad-venv/bin/python hardware/scripts/_bom_masses.py\n  then: tools/cad-venv/bin/python hardware/scripts/_bom_totals.py  (carries the new line costs into the section + grand totals)\n",
                    drift.join("\n")
                ),
            )
        });
    }
    ctx.write(&path, (out.join("\n") + "\n").as_bytes())?;
    let mut output = format!(
        "-> bom.md ({} rows re-derived, printed total {grand:.2} kg)\n",
        drift.len()
    );
    for row in drift {
        output += &format!("{row}\n")
    }
    Ok(main_result(0, output))
}

pub fn dispatch(op: &str, request: &Value, ctx: &mut Context) -> Result<Value> {
    let mut cache = HashMap::new();
    Ok(match op {
        "definitions" => definitions(),
        "constants" => {
            let bulk_petg = round((14. + 22. / 60.) / 1.126, 1);
            let rates = json!({"shell":null,"cover":null,"bulk":null,"ext":round((20.+23./60.)/0.653,1),"tight":round(bulk_petg*2.,0),"small":round(bulk_petg*2.8,0),"tool":round(bulk_petg*2.8,0),"rings":round(bulk_petg*2.8,0),"petgf":null,"aero":null});
            let group_marker: serde_json::Map<String, Value> = GROUPS
                .into_iter()
                .map(|(g, m)| (g.to_owned(), json!(m)))
                .collect();
            json!({"printers":2,"duty":DUTY,"hours_per_year":24*365,"measured":["14 h 22 m",1.126,14.+22./60.],"measured_ext":["20 h 23 m",0.653,20.+23./60.],"petgf_carry":(21.*1.27)/(18.*1.43),"bulk_petg":bulk_petg,"rates":rates,"group_marker":group_marker})
        }
        "group_of" => json!(group_of(arg(request, "label")?)?),
        "material_of" => json!(material_of(arg(request, "cell")?)?),
        "laid" => json!(laid(
            num(&request["volume"])?,
            num(&request["area"])?,
            arg(request, "group")?
        )?),
        "drawn" => json!(drawn(&PathBuf::from(arg(request, "path")?), ctx)?),
        "measure" => json!(measure(
            arg(request, "rel")?,
            &ctx.path(request, "parts_dir", "hardware/printed-parts"),
            &mut cache,
            ctx
        )?),
        "mass_kg" => json!(mass_kg(
            arg(request, "label")?,
            arg(request, "material")?,
            &ctx.path(request, "parts_dir", "hardware/printed-parts"),
            &mut cache,
            ctx
        )?),
        "mass_main" => mass_main(request, ctx)?,
        "number" => json!(number(arg(request, "cell")?)),
        "is_data_row" => json!(is_data_row(&strings(&request["cells"])?)),
        "estimate" => estimate(request, ctx)?,
        "main" => machine_main(request, ctx)?,
        "printed_parts" | "group_masses" => {
            let path = ctx.path(request, "bom", "hardware/ledger/bom.md");
            let text = ctx.read(path)?;
            if op == "printed_parts" {
                json!(printed_parts(&text)?)
            } else {
                json!(group_masses(&text)?)
            }
        }
        "read_sections" | "turnaround" => {
            let path = ctx.path(request, "machine_time", "hardware/ledger/machine-time.md");
            let text = ctx.read(path)?;
            if op == "read_sections" {
                json!(read_sections(&text))
            } else {
                json!(turnaround(&text, num(&request["wall"])?))
            }
        }
        _ => bail!("unknown printing operation: {op}"),
    })
}
