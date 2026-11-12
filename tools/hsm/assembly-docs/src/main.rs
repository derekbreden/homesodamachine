//! Assembly procedures, wiring schedules and installation facts.
//! Raw dimensions arrive from provider interfaces; the calculations and document writes live here.
use anyhow::{Context, Result, bail, ensure};
use hsm_documents::{Kind, Variables};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use std::{
    collections::BTreeMap,
    io::{self, BufRead, Write},
    path::{Path, PathBuf},
};
#[path = "../../../../hardware/assembly/calibration_inputs.rs"]
mod calibration_inputs;
mod marketing;
mod procedures;

#[derive(Deserialize)]
struct Request {
    root: PathBuf,
    driver: String,
    #[serde(default)]
    input: Value,
    #[serde(default)]
    write: bool,
    #[serde(default)]
    operation: String,
}
#[derive(Serialize)]
struct Job {
    path: String,
    kind: String,
    variables: Variables,
}
#[derive(Serialize, Default)]
struct Output {
    exports: BTreeMap<String, Value>,
    jobs: Vec<Job>,
    stdout: String,
    data_reads: Vec<String>,
    maintained: Vec<String>,
}
impl Output {
    fn document(path: &str, variables: Variables) -> Self {
        Self {
            jobs: vec![Job {
                path: path.into(),
                kind: "markdown".into(),
                variables,
            }],
            stdout: format!(
                "-> {}\n",
                Path::new(path).file_name().unwrap().to_string_lossy()
            ),
            ..Self::default()
        }
    }
}
fn n(input: &Value, name: &str) -> Result<f64> {
    input
        .get(name)
        .and_then(Value::as_f64)
        .with_context(|| format!("missing numeric provider {name}"))
}
fn list<'a>(input: &'a Value, name: &str) -> Result<&'a Vec<Value>> {
    input
        .get(name)
        .and_then(Value::as_array)
        .with_context(|| format!("missing list provider {name}"))
}
fn fmt(number: f64, spec: &str) -> Result<String> {
    if spec == "d" {
        return Ok(format!("{}", number as i64));
    }
    if spec == "02x" {
        return Ok(format!("{:02x}", number as i64));
    }
    if spec == "," {
        return hsm_documents::format_number(number, ",.0f");
    }
    if spec.is_empty() {
        return Ok(if number.fract() == 0. {
            format!("{}", number as i64)
        } else {
            number.to_string()
        });
    }
    hsm_documents::format_number(number, spec)
}
fn round(number: f64, digits: i32) -> f64 {
    let scale = 10_f64.powi(digits);
    (number * scale).round_ties_even() / scale
}
fn fraction(value: f64, max_den: u64) -> String {
    // Continued-fraction bounds, including Fraction.limit_denominator's tie rule.
    let (mut p0, mut q0, mut p1, mut q1) = (0_u64, 1_u64, 1_u64, 0_u64);
    let mut value_left = value;
    loop {
        let a = value_left.floor() as u64;
        let q2 = q0 + a * q1;
        if q2 > max_den {
            break;
        }
        let p2 = p0 + a * p1;
        (p0, q0, p1, q1) = (p1, q1, p2, q2);
        let rest = value_left - a as f64;
        if rest == 0. {
            return if q1 == 1 {
                p1.to_string()
            } else {
                format!("{p1}/{q1}")
            };
        }
        value_left = 1. / rest;
    }
    let k = (max_den - q0) / q1;
    let (p, q) = (p0 + k * p1, q0 + k * q1);
    let (p, q) = if (p1 as f64 / q1 as f64 - value).abs() <= (p as f64 / q as f64 - value).abs() {
        (p1, q1)
    } else {
        (p, q)
    };
    if q == 1 {
        p.to_string()
    } else {
        format!("{p}/{q}")
    }
}
fn dispatch(request: &Request) -> Result<Output> {
    let mut output = match request.driver.as_str() {
        "install-envelope" | "target-market" => marketing::run(request)?,
        _ => procedures::run(request)?,
    };
    if request.write {
        let caller = if matches!(request.driver.as_str(), "install-envelope" | "target-market") {
            "/tools/hsm/assembly-docs/src/marketing.rs"
        } else {
            "/tools/hsm/assembly-docs/src/procedures.rs"
        }.to_owned();
        for job in &output.jobs {
            let kind = match job.kind.as_str() {
                "markdown" => Kind::Markdown,
                "mermaid" => Kind::Mermaid,
                _ => bail!("unknown document kind"),
            };
            let result = hsm_documents::substitute(
                &request.root.join(&job.path),
                kind,
                &job.variables,
                Some(&caller),
                caller.starts_with("/hardware/")
                    && request.root.join("tools/hsm/Cargo.toml").is_file(),
            )?;
            output
                .maintained
                .extend(result.maintained.into_iter().map(|p| {
                    p.strip_prefix(&request.root)
                        .unwrap_or(&p)
                        .to_string_lossy()
                        .into_owned()
                }));
        }
    }
    Ok(output)
}
fn main() -> Result<()> {
    let mut stdout = io::stdout().lock();
    if let Some(line) = io::stdin().lock().lines().next() {
        let line = line?;
        let result: Result<Output> = serde_json::from_str(&line)
            .context("assembly document request")
            .and_then(|request| dispatch(&request));
        let value = match result {
            Ok(output) => serde_json::to_value(output)?,
            Err(error) => json!({"error":format!("{error:#}")}),
        };
        serde_json::to_writer(&mut stdout, &value)?;
        writeln!(stdout)?;
        stdout.flush()?;
    }
    Ok(())
}
