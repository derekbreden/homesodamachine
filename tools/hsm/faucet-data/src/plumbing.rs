//! Registered installation-art datums, geometry input, render jobs and image placement.
use anyhow::{Context, Result, bail, ensure};
use serde_json::{Value, json};
use std::path::{Path, PathBuf};
fn catalog() -> Value {
    serde_json::from_str(include_str!("plumbing_catalog.json")).unwrap()
}
pub fn datums(modern: bool, reach: f64, insertion: f64) -> Value {
    let all = catalog();
    let row = &all[if modern { "modern" } else { "legacy" }];
    let mut out = row["constants"].clone();
    if !modern {
        out["VALVE_CENTER_Z"] = out["STUB_CENTER"][2].clone();
        return out;
    }
    let n = |k: &str| out[k].as_f64().unwrap();
    let tube = n("PP0208_TUBE_OD");
    let right = n("UNION_X") + reach;
    let left = n("UNION_X") - reach;
    let started = right + n("RELEASE_STARTED_GAP");
    let tee = right + n("ASSEMBLY_FACE_GAP") + n("PP0208_REACH");
    let staged = tee + insertion + n("ASSEMBLY_STAGE_GAP");
    let tee_left = tee - n("PP0208_REACH");
    let tee_right = tee + n("PP0208_REACH");
    let branch = n("AXIS_Z") - n("PP0208_REACH");
    for (k, v) in [
        ("TUBE_OD", tube),
        ("UNION_REACH", reach),
        ("UNION_INSERTION", insertion),
        ("UNION_RIGHT_FACE", right),
        ("UNION_LEFT_FACE", left),
        ("RELEASE_STARTED_X", started),
        ("TEE_X", tee),
        ("TEE_STAGED_X", staged),
        ("TEE_LEFT_FACE", tee_left),
        ("TEE_RIGHT_FACE", tee_right),
        ("TEE_BRANCH_FACE_Z", branch),
    ] {
        out[k] = json!(v);
    }
    for (name, view) in row["views"].as_object().unwrap() {
        out[name] = view.clone();
    }
    out["SCENES"] = json!(
        row["scenes"]
            .as_array()
            .unwrap()
            .iter()
            .map(|s| json!([s[0], row["views"][s[1].as_str().unwrap()]]))
            .collect::<Vec<_>>()
    );
    out
}
fn color(v: &Value) -> Result<[f64; 3]> {
    let rgba =
        hsm_shared_data::color::rgba(v, &json!({}))?.context("instruction colour constructor")?;
    Ok([rgba[0], rgba[1], rgba[2]])
}
fn export_spec(r: &Value) -> Result<Value> {
    let mut colors = serde_json::Map::new();
    let mut dimensions = serde_json::Map::new();
    for (name, v) in r["facts"].as_object().context("plumbing source facts")? {
        if name.starts_with("C_") {
            colors.insert(name.clone(), json!(color(v)?));
        } else if name.chars().all(|c| !c.is_ascii_lowercase())
            && (v.is_number()
                || v.is_boolean()
                || v.as_array()
                    .is_some_and(|a| a.iter().all(|x| x.is_number() || x.is_boolean())))
        {
            dimensions.insert(name.clone(), v.clone());
        }
    }
    let modern = r["modern"].as_bool().unwrap_or(false);
    let mut spec = json!({"kind":if modern{"modern"}else{"legacy"},"names":r["names"],"dimensions":dimensions});
    if modern {
        spec["union"] = r["union"].clone();
    }
    Ok(json!({"plumbing_art":spec,"colors":colors}))
}
fn job(step: &Path, output: &Path, root: &Path, view: &Value, modern: bool) -> Result<Value> {
    let d = datums(modern, 0.0, 0.0);
    let mut job = json!({"step":step.strip_prefix(root.join("hardware"))?.to_string_lossy(),"out":output.to_string_lossy(),"cam":view["camera"],"up":[0.0,0.0,1.0],"target":view["target"],"size":d["RENDER_SIZE"],"span":view["span"],"bg":if modern{"#dce7e9"}else{"#ffffff"},"trim":false,"solid":true,"ortho":true,"ground":false,"fog":false});
    if modern {
        job["transparent"] = json!(true);
    }
    Ok(job)
}
pub fn canonicalize_png(path: &Path, transparent: bool) -> Result<()> {
    let bytes = std::fs::read(path)?;
    let mut decoder = png::Decoder::new(std::io::Cursor::new(bytes));
    decoder.set_transformations(png::Transformations::EXPAND | png::Transformations::STRIP_16);
    let mut reader = decoder.read_info()?;
    let mut buffer = vec![0; reader.output_buffer_size().context("PNG size")?];
    let info = reader.next_frame(&mut buffer)?;
    ensure!(
        (info.width, info.height) == (2000, 1100),
        "unexpected render size ({}, {}): {}",
        info.width,
        info.height,
        path.display()
    );
    buffer.truncate(info.buffer_size());
    let rgba = match info.color_type {
        png::ColorType::Rgba => buffer,
        png::ColorType::Rgb => buffer
            .chunks_exact(3)
            .flat_map(|p| [p[0], p[1], p[2], 255])
            .collect(),
        png::ColorType::Grayscale => buffer.iter().flat_map(|p| [*p, *p, *p, 255]).collect(),
        png::ColorType::GrayscaleAlpha => buffer
            .chunks_exact(2)
            .flat_map(|p| [p[0], p[0], p[0], p[1]])
            .collect(),
        png::ColorType::Indexed => bail!("indexed PNG survived expansion"),
    };
    if transparent {
        let minimum = rgba.chunks_exact(4).map(|p| p[3]).min().unwrap_or(0);
        let maximum = rgba.chunks_exact(4).map(|p| p[3]).max().unwrap_or(0);
        ensure!(
            minimum == 0 && maximum == 255,
            "render does not hold transparent scene art: {}",
            path.display()
        );
    }
    let mut encoded = Vec::new();
    {
        let mut encoder = png::Encoder::new(&mut encoded, 2000, 1100);
        encoder.set_color(png::ColorType::Rgba);
        encoder.set_depth(png::BitDepth::Eight);
        encoder.set_compression(png::Compression::High);
        let mut writer = encoder.write_header()?;
        writer.write_image_data(&rgba)?;
    }
    hsm_documents::write_if_changed(path, &encoded)?;
    Ok(())
}
pub fn dispatch(r: &Value) -> Result<Value> {
    let modern = r["modern"].as_bool().unwrap_or(false);
    Ok(match r["fn"].as_str().unwrap_or("datums") {
        "datums" => datums(
            modern,
            r["union_reach"].as_f64().unwrap_or(0.0),
            r["union_insertion"].as_f64().unwrap_or(0.0),
        ),
        "spec" => {
            let spec = export_spec(r)?;
            if let Some(path) = r["output"].as_str() {
                let mut data = serde_json::to_vec(&spec)?;
                data.push(b'\n');
                hsm_documents::write_if_changed(Path::new(path), &data)?;
            }
            spec
        }
        "job" => job(
            Path::new(r["step"].as_str().context("scene STEP")?),
            Path::new(r["output"].as_str().context("scene PNG")?),
            Path::new(r["root"].as_str().context("scene root")?),
            &r["view"],
            modern,
        )?,
        "legacy-jobs" => {
            let d = datums(false, 0.0, 0.0);
            let view = json!({"camera":d["RENDER_CAM"],"target":d["RENDER_TARGET"],"span":d["RENDER_ORTHO_SPAN"]});
            let root = Path::new(r["root"].as_str().context("scene root")?);
            let directory = Path::new(r["directory"].as_str().context("art directory")?);
            json!(
                d["SCENE_NAMES"]
                    .as_array()
                    .unwrap()
                    .iter()
                    .map(|v| {
                        let name = v.as_str().unwrap();
                        job(
                            Path::new(r["steps"][name].as_str().unwrap()),
                            &directory.join(format!("{name}.png")),
                            root,
                            &view,
                            false,
                        )
                    })
                    .collect::<Result<Vec<_>>>()?
            )
        }
        "canonicalize-png" => {
            canonicalize_png(Path::new(r["path"].as_str().context("PNG path")?), modern)?;
            Value::Null
        }
        "copy-step" => {
            let source = Path::new(r["source"].as_str().context("STEP source")?);
            let target = Path::new(r["target"].as_str().context("STEP target")?);
            let mut paths = vec![];
            for suffix in ["", ".mesh", ".npz"] {
                let from = PathBuf::from(format!("{}{suffix}", source.display()));
                let to = PathBuf::from(format!("{}{suffix}", target.display()));
                hsm_documents::write_if_changed(&to, &std::fs::read(&from)?)?;
                paths.push(to.to_string_lossy().into_owned());
            }
            json!(paths)
        }
        x => bail!("unknown plumbing source operation {x}"),
    })
}
