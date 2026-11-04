use anyhow::{Context, Result, bail};
use hsm_documents::{Kind, Variables};
use serde_json::{Value, json};
use std::io::{self, BufRead, Read, Write};
use std::path::Path;

fn argument<'a>(request: &'a Value, key: &str) -> Result<&'a str> {
    request[key]
        .as_str()
        .with_context(|| format!("missing string {key}"))
}

fn execute(request: &Value) -> Result<Value> {
    let op = argument(request, "op")?;
    Ok(match op {
        "substitute" => {
            let kind = match argument(request, "kind")? {
                "md" => Kind::Markdown,
                "mmd" => Kind::Mermaid,
                "py" => Kind::Python,
                kind => bail!("unknown substitution kind {kind}"),
            };
            let vars: Variables = serde_json::from_value(request["variables"].clone())?;
            serde_json::to_value(hsm_documents::substitute(
                Path::new(argument(request, "path")?),
                kind,
                &vars,
                request["caller"].as_str(),
                request["figures"].as_bool().unwrap_or(false),
            )?)?
        }
        "cells" => json!(hsm_documents::cells(argument(request, "text")?)),
        "pid-alive" => json!(hsm_documents::pid_alive(
            request["pid"].as_i64().unwrap_or(0) as i32
        )),
        "umask" => {
            #[cfg(unix)]
            {
                unsafe extern "C" {
                    fn umask(mask: u32) -> u32;
                }
                let mask = unsafe { umask(0) };
                unsafe {
                    umask(mask);
                }
                json!(mask)
            }
            #[cfg(not(unix))]
            {
                json!(0)
            }
        }
        "unlink" => {
            match std::fs::remove_file(argument(request, "path")?) {
                Ok(()) => (),
                Err(error) if error.kind() == std::io::ErrorKind::NotFound => (),
                Err(error) => return Err(error.into()),
            }
            Value::Null
        }
        "render" => {
            let vars: Variables = serde_json::from_value(request["variables"].clone())?;
            let text = argument(request, "text")?;
            match argument(request, "kind")? {
                "md" => {
                    let (text, figures) =
                        hsm_documents::markdown(text, &vars, request["caller"].as_str());
                    json!({"text":text,"figures":figures})
                }
                "mmd" => json!({"text": hsm_documents::mermaid(text, &vars)}),
                "py" => json!({"text": hsm_documents::python_comments(text, &vars)}),
                kind => bail!("unknown render kind {kind}"),
            }
        }
        "prepare" => {
            let path = Path::new(argument(request, "path")?);
            if let Some(parent) = path.parent() {
                std::fs::create_dir_all(parent)?;
            }
            hsm_documents::sweep_orphan_temps(path)?;
            let temporary = hsm_documents::sibling_tempfile(
                path,
                request["pid"].as_u64().unwrap_or(std::process::id() as u64) as u32,
            )?;
            #[cfg(unix)]
            if let Some(mode) = request["mode"].as_u64() {
                use std::os::unix::fs::PermissionsExt;
                std::fs::set_permissions(&temporary, std::fs::Permissions::from_mode(mode as u32))?;
            }
            json!(temporary)
        }
        "sweep" => {
            hsm_documents::sweep_orphan_temps(Path::new(argument(request, "path")?))?;
            Value::Null
        }
        "matches" => json!(hsm_documents::matches_existing_target(
            Path::new(argument(request, "temporary")?),
            Path::new(argument(request, "path")?)
        )?),
        "finish" => json!(hsm_documents::finish_atomic(
            Path::new(argument(request, "temporary")?),
            Path::new(argument(request, "path")?),
            request["canonicalize"].as_bool().unwrap_or(true)
        )?),
        "canonicalize" => {
            hsm_documents::canonicalize_file(
                Path::new(argument(request, "path")?),
                argument(request, "kind")?,
            )?;
            Value::Null
        }
        "canonicalize-bytes" => {
            let bytes: Vec<u8> = serde_json::from_value(request["bytes"].clone())?;
            json!(match argument(request, "kind")? {
                "classes" => hsm_documents::canonicalize_dxf_classes(&bytes),
                "dxf" => hsm_documents::canonicalize_dxf(&bytes),
                "pdf" => hsm_documents::canonicalize_pdf(&bytes),
                kind => bail!("unknown format {kind}"),
            })
        }
        "format" => {
            let mut out = Vec::new();
            for row in request["rows"].as_array().context("format rows")? {
                let value = row[0].as_f64().context("numeric format value")?;
                out.push(hsm_documents::format_number(
                    value,
                    row[1].as_str().context("format spec")?,
                )?);
            }
            json!(out)
        }
        op => bail!("unknown document operation {op}"),
    })
}

fn main() -> Result<()> {
    if std::env::args().any(|a| a == "--serve") {
        let stdin = io::stdin();
        let mut stdout = io::stdout().lock();
        for line in stdin.lock().lines() {
            let result = line
                .map_err(anyhow::Error::from)
                .and_then(|line| serde_json::from_str::<Value>(&line).map_err(Into::into))
                .and_then(|request| execute(&request));
            let reply = match result {
                Ok(value) => value,
                Err(error) => json!({"error":format!("{error:#}")}),
            };
            writeln!(stdout, "{}", serde_json::to_string(&reply)?)?;
            stdout.flush()?;
        }
        return Ok(());
    }
    let mut input = String::new();
    io::stdin().read_to_string(&mut input)?;
    let request: Value = serde_json::from_str(&input)?;
    if let Some(batch) = request.as_array() {
        let out: Vec<_> = batch.iter().map(execute).collect::<Result<_>>()?;
        println!("{}", serde_json::to_string(&out)?);
    } else {
        println!("{}", serde_json::to_string(&execute(&request)?)?);
    }
    Ok(())
}
