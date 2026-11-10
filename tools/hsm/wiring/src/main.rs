//! This opt-in command exports the installed wiring's bench manifest, worksheet and native geometry.
use anyhow::{Context, Result, bail, ensure};
use hsm_run_slots::ipc;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::{
    collections::BTreeMap,
    fs,
    io::Read,
    path::{Path, PathBuf},
    process::Command,
};

#[allow(dead_code)]
#[path = "../../../../hardware/manifold-layout/installed-machine/cache.rs"]
mod cache;
#[allow(dead_code)]
#[path = "../../../../hardware/manifold-layout/installed-machine/design.rs"]
mod design;
#[allow(dead_code)]
#[path = "../../../../hardware/manifold-layout/machine_layout.rs"]
mod layout;
#[allow(dead_code)]
#[path = "../../../../hardware/manifold-layout/installed-machine/plan.rs"]
mod plan;
#[allow(dead_code)]
#[path = "../../../../hardware/manifold-layout/installed-machine/wiring.rs"]
mod wiring;

fn digest(path: &Path) -> Result<String> {
    let mut file = fs::File::open(path).with_context(|| format!("reading {}", path.display()))?;
    let mut hash = Sha256::new();
    let mut bytes = [0; 65536];
    loop {
        let count = file.read(&mut bytes)?;
        if count == 0 {
            break;
        }
        hash.update(&bytes[..count]);
    }
    Ok(format!("{:x}", hash.finalize()))
}

fn write_json(path: &Path, value: &Value) -> Result<()> {
    let mut bytes = serde_json::to_vec_pretty(value)?;
    bytes.push(b'\n');
    hsm_model_export::put(path, &bytes)
}

fn csv(value: &Value) -> String {
    let text = match value {
        Value::String(text) => text.clone(),
        Value::Null => String::new(),
        value => value.to_string(),
    };
    if text.contains([',', '"', '\r', '\n']) {
        format!("\"{}\"", text.replace('"', "\"\""))
    } else {
        text
    }
}

fn worksheet(manifest: &Value) -> Result<String> {
    let mut output = String::from(
        "wire_id,harness,net,from_terminal,to_terminal,awg,modeled_length_mm,route_status,start_status,end_status,service\n",
    );
    for row in manifest["routes"]
        .as_array()
        .context("the resolved conductor routes")?
    {
        let stock = row["stock"].as_str().context("conductor stock")?;
        let start = row["start"].as_str().context("conductor start")?;
        let end = row["end"].as_str().context("conductor end")?;
        output.push_str(
            &[
                &row["id"],
                &row["harness"],
                &row["net"],
                &row["start"],
                &row["end"],
                &manifest["stock"][stock]["awg"],
                &row["length_mm"],
                &row["route_status"],
                &manifest["terminals"][start]["status"],
                &manifest["terminals"][end]["status"],
                &row["service"],
            ]
            .into_iter()
            .map(csv)
            .collect::<Vec<_>>()
            .join(","),
        );
        output.push('\n');
    }
    Ok(output)
}

fn main() -> Result<()> {
    let mut args = std::env::args().skip(1);
    let mut root = None;
    let mut work = None;
    let mut out = None;
    let mut numbers_only = false;
    while let Some(arg) = args.next() {
        match arg.as_str() {
            "--help" | "-h" => {
                println!(
                    "hsm-wiring [--root DIR] [--work DIR] [--output DIR] [--numbers-only]\nExports the saved machine's current wiring recipe, bench manifest, CSV and standalone STEP."
                );
                return Ok(());
            }
            "--root" => root = Some(PathBuf::from(args.next().context("--root DIR")?)),
            "--work" => work = Some(PathBuf::from(args.next().context("--work DIR")?)),
            "--output" | "--out" => out = Some(PathBuf::from(args.next().context("--output DIR")?)),
            "--numbers-only" => numbers_only = true,
            _ => bail!("unknown wiring argument {arg}"),
        }
    }
    let root = root.unwrap_or(std::env::current_dir()?).canonicalize()?;
    ensure!(
        root.join("hardware/wiring").is_dir(),
        "--root must name the repository"
    );
    std::env::set_current_dir(&root)?;
    let work = work.unwrap_or_else(|| root.join(".cache/realized/installed-machine"));
    let out = out.unwrap_or_else(|| root.join("hardware/wiring"));
    fs::create_dir_all(&out)?;
    let out = out.canonicalize()?;
    let lease = hsm_run_slots::acquire(
        "installed wiring bench export",
        hsm_run_slots::inherited()?,
        false,
    )?;
    let (mut numbers, mut manifest, physical_sha) = {
        let _assembly = cache::lock(&work)?;
        let mut spec = cache::retained_value(&root, &work, "placement")?
            .context("the normal print build has not retained the installed machine's placement")?;
        spec["metadata"]["wiring_context"] = plan::wiring_context(&root)?;
        let physical = work.join("mechanics/enclosure-assembly.step.npz");
        ensure!(
            physical.is_file(),
            "the normal print build has not retained the physical machine model"
        );
        let (numbers, manifest) = wiring::manual_request(&root, &spec, &physical)?;
        (numbers, manifest, digest(&physical)?)
    };
    numbers["file_stem"] = json!("enclosure-wiring");
    numbers["physical_fine_model_sha256"] = json!(physical_sha);
    manifest["physical_fine_model_sha256"] = json!(physical_sha);
    let numbers_path = out.join("enclosure-wiring.numbers.json");
    write_json(&numbers_path, &numbers)?;
    manifest["wiring_numbers_sha256"] = json!(digest(&numbers_path)?);
    let mut sources = BTreeMap::new();
    for name in [
        "hardware/manifold-layout/above-core.json",
        "hardware/wiring/installed/connector-map.json",
        "hardware/wiring/installed/route-overrides.json",
        "hardware/wiring/installed/bundle-routes.json",
        "hardware/wiring/installed/fixed-passages.json",
        "tools/hsm/assembly-docs/src/wiring/stock.json",
        "tools/hsm/assembly-docs/src/wiring/graph.rs",
        "tools/hsm/assembly-docs/src/wiring/routes.rs",
        "tools/hsm/assembly-docs/src/wiring/terminals.rs",
        "tools/hsm/assembly-docs/src/wiring/terminations.rs",
        "tools/hsm/assembly-docs/src/wiring/bundles.rs",
        "hardware/manifold-layout/installed-machine/wiring.rs",
        "hardware/manifold-layout/installed-machine/wiring/sources.rs",
    ] {
        sources.insert(name, digest(&root.join(name))?);
    }
    manifest["source_sha256"] = json!(sources);
    manifest["producer"] =
        json!({"command":"hsm-wiring","executable_sha256":digest(&std::env::current_exe()?)?});
    if !numbers_only {
        let program = root.join("tools/hsm/target/release/installed-wires");
        ensure!(
            program.is_file(),
            "build hsm-machine's installed-wires before exporting bench geometry"
        );
        let bench = root.join(".cache/realized/wiring-bench");
        fs::create_dir_all(&bench)?;
        let _bench = cache::lock(&bench)?;
        let mut command = Command::new(&program);
        command.arg(&numbers_path).arg(&bench).current_dir(&root);
        lease.apply(&mut command)?;
        let result = ipc::output(&mut command)?;
        ensure!(
            result.status.success(),
            "native wiring export failed:\n{}\n{}",
            String::from_utf8_lossy(&result.stderr),
            String::from_utf8_lossy(&result.stdout)
        );
        for suffix in ["step", "step.mesh", "step.npz"] {
            let name = format!("enclosure-wiring.{suffix}");
            hsm_model_export::put(&out.join(&name), &fs::read(bench.join(&name))?)?;
        }
        manifest["wiring_fine_model_sha256"] =
            json!(digest(&out.join("enclosure-wiring.step.npz"))?);
        manifest["wiring_step_sha256"] = json!(digest(&out.join("enclosure-wiring.step"))?);
        manifest["producer"]["geometry_executable_sha256"] = json!(digest(&program)?);
    }
    manifest["geometry_written"] = json!(!numbers_only);
    hsm_model_export::put(
        &out.join("enclosure-wiring.csv"),
        worksheet(&manifest)?.as_bytes(),
    )?;
    write_json(&out.join("enclosure-wiring.json"), &manifest)?;
    println!(
        "{}",
        json!({"output":out,"conductors":manifest["connection_count"],"geometry_written":!numbers_only,
        "physical_fine_model_sha256":physical_sha,"wiring_numbers_sha256":manifest["wiring_numbers_sha256"]})
    );
    Ok(())
}
