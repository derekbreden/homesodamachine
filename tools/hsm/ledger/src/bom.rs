use crate::shared::*;
use anyhow::{Result, bail};
use hsm_documents::Variables;
use serde_json::{Value, json};
use std::collections::BTreeMap;

const MONEY: &str = r"\$\s?([0-9][0-9,]*(?:\.[0-9]{1,2})?)";
const CASH: &str = r"\$\s?([0-9][0-9,]*(?:\.[0-9]+)?)";
const PER: &str =
    r"\$\s?([0-9][0-9,]*(?:\.[0-9]+)?)\s*/\s*(?:ea|each|pc|ft|in|m|board|roll|plate|stick)\b";

fn amount(text: &str) -> f64 {
    re(MONEY)
        .captures(text)
        .map(|c| c[1].replace(',', "").parse().unwrap())
        .unwrap_or(0.)
}
fn figure(text: &str, pattern: &str) -> Option<(f64, i32)> {
    re(pattern).captures_iter(text).last().map(|c| {
        let s = c[1].replace(',', "");
        (
            s.parse().unwrap(),
            s.split_once('.').map(|(_, p)| p.len() as i32).unwrap_or(0),
        )
    })
}
fn reading(notes: &str, qty: &str, unit: &str, line: &str) -> Option<[f64; 4]> {
    let qty = qty.replace(',', "");
    let caps = re(r"-?[0-9][0-9,]*(?:\.[0-9]+)?").captures(&qty)?;
    let qty: f64 = caps[0].parse().ok()?;
    let printed = figure(unit, CASH)?;
    let line = amount(line);
    if line == 0. {
        return None;
    }
    let stated = figure(notes, PER);
    let (price, dec) = stated.filter(|(_, d)| *d > printed.1).unwrap_or(printed);
    Some([
        line,
        qty * price,
        qty * 0.5 * 10f64.powi(-dec) + 0.005,
        qty * printed.0,
    ])
}
fn parse(text: &str, auditing: bool) -> (BTreeMap<i64, f64>, Vec<String>, Vec<String>) {
    let (mut sums, mut current, mut audit, mut notes) = (BTreeMap::new(), None, vec![], vec![]);
    for line in text.lines() {
        if line.starts_with("## ") {
            current = section(line);
            continue;
        }
        let Some(section) = current else { continue };
        if !line.starts_with('|') {
            continue;
        }
        let c = cells(line);
        if c.is_empty() || separator(&c) {
            continue;
        }
        let first = c[0].replace('*', "").trim().to_lowercase();
        if first == "part" || first.contains("total") {
            continue;
        }
        *sums.entry(section).or_insert(0.) += amount(c.last().unwrap());
        if c.len() >= 5 && auditing {
            if let Some([line, want, slack, printed]) =
                reading(&c[1], &c[c.len() - 3], &c[c.len() - 2], &c[c.len() - 1])
            {
                let loc = format!("  §{section} {}", text_prefix(&c[0], 46));
                if (want - line).abs() > slack {
                    audit.push(format!(
                        "{loc}: line ${line:.2}, its own rate gives ${want:.2}"
                    ));
                } else if (printed - line).abs() > 0.005 {
                    notes.push(format!(
                        "{loc}: line ${line:.2}, printed unit × qty ${printed:.2}"
                    ));
                }
            }
        }
    }
    (sums, audit, notes)
}

pub fn dispatch(op: &str, request: &Value, context: &mut Context) -> Result<Value> {
    Ok(match op {
        "money" => json!(amount(arg(request, "text")?)),
        "figure" => json!(figure(
            arg(request, "text")?,
            request["pattern"].as_str().unwrap_or(CASH)
        )),
        "reading" => json!(reading(
            arg(request, "notes")?,
            arg(request, "qty")?,
            arg(request, "unit")?,
            arg(request, "line")?
        )),
        "parse" | "main" => {
            let path = context.path(request, "bom", "hardware/ledger/bom.md");
            let text = context.read(&path)?;
            let audit = request["audit"].as_bool().unwrap_or(false);
            let (sums, findings, notes) = parse(&text, audit);
            if op == "parse" {
                return Ok(json!([sums, findings, notes]));
            }
            let grand = sums.values().sum();
            let mut vars: Variables = sums
                .iter()
                .map(|(n, v)| (format!("BOM_SEC{n}"), money(*v)))
                .collect();
            vars.insert("BOM_GRAND".into(), money(grand));
            if request["check"].as_bool().unwrap_or(false) {
                let stale = stale(&text, &vars);
                let (status, out) = if stale.is_empty() {
                    (0, "bom.md totals ✓\n".into())
                } else {
                    (
                        1,
                        format!(
                            "bom.md totals are stale — run _bom_totals.py:\n{}\n",
                            stale.join("\n")
                        ),
                    )
                };
                main_result(status, out)
            } else {
                context.substitute(&path, &vars, "/hardware/scripts/_bom_totals.py")?;
                let mut out = String::new();
                for (n, v) in sums {
                    out += &format!("  §{n:<2} {:>10}\n", money(v))
                }
                out += &format!("  {:<3} {:>10}\n", "GRAND", money(grand));
                if audit {
                    if !findings.is_empty() {
                        out += &format!(
                            "\nthe line does not close against the row's own rate:\n{}\n",
                            findings.join("\n")
                        )
                    }
                    if !notes.is_empty() {
                        out += &format!(
                            "\ndisplay only — the two-decimal Unit column will not multiply out ({} rows; every line below is right):\n{}\n",
                            notes.len(),
                            notes.join("\n")
                        )
                    }
                    if findings.is_empty() {
                        out += "\nevery priced row closes against its own rate ✓\n"
                    }
                }
                main_result(0, out)
            }
        }
        _ => bail!("unknown BOM operation: {op}"),
    })
}
