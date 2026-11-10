//! Publish SolidCraft's saved display bytes or native mesh export without remodelling their surfaces.
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::{
    collections::BTreeSet,
    error::Error,
    fs,
    io::{Cursor, Read, Write},
    path::Path,
    process::Command,
    time::Instant,
};
use zip::{ZipArchive, ZipWriter, write::SimpleFileOptions};

type Result<T = ()> = std::result::Result<T, Box<dyn Error>>;
const ROOT: &str = "hardware/reference/carbonator-core/solidcraft";
const WEB: &str = "web/public/solidcraft-lab/carbonator";
const RECIPE: &str = "native-display/3";

fn hash(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}
fn read_part(zip: &mut ZipArchive<Cursor<&[u8]>>, name: &str) -> Result<Vec<u8>> {
    let mut bytes = Vec::new();
    zip.by_name(name)?.read_to_end(&mut bytes)?;
    Ok(bytes)
}
fn preview(source: &Path, target: &Path, version: &str) -> Result<Option<Value>> {
    let bytes = fs::read(source)?;
    let mut zip = ZipArchive::new(Cursor::new(bytes.as_slice()))?;
    if zip.by_name("cache/preview.json").is_err() {
        return Ok(None);
    }
    let manifest = read_part(&mut zip, "cache/preview.json")?;
    let data = read_part(&mut zip, "cache/preview.bin")?;
    let document = read_part(&mut zip, "document.json")?;
    let meta: Value = serde_json::from_slice(&manifest)?;
    if meta["format"] != "solidcraft-preview/1"
        || meta["build"] != version
        || meta["document"] != hash(&document)
        || meta["payload"] != hash(&data)
    {
        return Ok(None);
    }
    let meshes = meta["meshes"]
        .as_array()
        .ok_or("native preview has no bodies")?;
    let mut triangles = 0u64;
    for mesh in meshes {
        let offset = mesh["offset"].as_u64().ok_or("native preview offset")? as usize;
        let slice = data
            .get(offset..offset + 24)
            .ok_or("native preview header")?;
        if &slice[..8] != b"SCMESH01" {
            return Err("native preview mesh encoding".into());
        }
        triangles += u64::from_le_bytes(slice[16..24].try_into()?) / 3;
    }
    let mut out = ZipWriter::new(fs::File::create(target)?);
    let options = SimpleFileOptions::default().compression_method(zip::CompressionMethod::Deflated);
    for (name, content) in [
        ("cache/preview.json", manifest),
        ("cache/preview.bin", data),
        ("document.json", document),
    ] {
        out.start_file(name, options)?;
        out.write_all(&content)?;
    }
    out.finish()?;
    Ok(Some(
        json!({"kind":"saved-preview", "triangles":triangles, "bodies":meshes.len(),
        "documentSha256":meta["document"], "payloadSha256":meta["payload"]}),
    ))
}
fn command(program: &str, args: &[String], log: &Path) -> Result<String> {
    let result = Command::new(program).args(args).output()?;
    let stdout = String::from_utf8_lossy(&result.stdout).to_string();
    fs::write(
        log,
        format!("{}{}", stdout, String::from_utf8_lossy(&result.stderr)),
    )?;
    if !result.status.success() {
        return Err(format!("{program} failed; see {}", log.display()).into());
    }
    Ok(stdout)
}
pub fn run() -> Result {
    let args: Vec<String> = std::env::args().collect();
    let scratch = args
        .windows(2)
        .find(|a| a[0] == "--out")
        .map(|a| Path::new(&a[1]))
        .ok_or("display --out requires a temporary run directory")?;
    fs::create_dir_all(scratch)?;
    let scratch = scratch.canonicalize()?;
    let root = Path::new(ROOT).canonicalize()?;
    let web = Path::new(WEB);
    let output = web.join("assets/native");
    fs::create_dir_all(&output)?;
    let output = output.canonicalize()?;
    let version = String::from_utf8(
        Command::new("solidcraft-cli")
            .arg("--version")
            .output()?
            .stdout,
    )?;
    let version = version
        .trim()
        .strip_prefix("solidcraft-cli ")
        .ok_or("CLI version")?;
    let catalog: Value = serde_json::from_slice(&fs::read(web.join("levels.json"))?)?;
    let sources: BTreeSet<String> = catalog["nodes"]
        .as_object()
        .ok_or("assembly catalog")?
        .iter()
        .map(|(key, node)| {
            if key == "instrumented-parent" {
                "instrumented-reference".to_owned()
            } else if key == "probe-coil" {
                "probe".to_owned()
            } else if node["reference"] == true {
                format!("{key}-reference")
            } else {
                key.clone()
            }
        })
        .collect();
    let old: Value = fs::read(output.join("index.json"))
        .ok()
        .and_then(|b| serde_json::from_slice(&b).ok())
        .unwrap_or(json!({}));
    let mut index = json!({"purpose":"Native display payloads retain SolidCraft's own triangulation and body colours.",
        "recipe":RECIPE,"solidcraft":version,"models":{}});
    let started = Instant::now();
    let mut reused = 0;
    let mut assemblies = Vec::new();
    for name in &sources {
        let source = root.join(format!("native/{name}.sc"));
        let sha = hash(&fs::read(&source)?);
        let previous = &old["models"][name];
        if old["recipe"] == RECIPE
            && old["solidcraft"] == version
            && previous["sourceSha256"] == sha
            && previous["kind"] == "assembly-preview"
        {
            assemblies.push((name.clone(), sha, previous["open"].clone(), 0.));
            continue;
        }
        if old["recipe"] == RECIPE
            && old["solidcraft"] == version
            && previous["sourceSha256"] == sha
            && let Some(file) = previous["file"].as_str()
            && fs::read(output.join(file)).is_ok_and(|b| previous["sha256"] == hash(&b))
        {
            index["models"][name] = previous.clone();
            reused += 1;
            continue;
        }
        let start = Instant::now();
        let packed = output.join(format!("{name}.preview.zip"));
        let mut display = preview(&source, &packed, version)?;
        let mut stages = Vec::new();
        let saved = scratch.join(format!("{name}.sc"));
        if display.is_none() {
            let ops = scratch.join(format!("{name}-save.json"));
            fs::write(
                &ops,
                serde_json::to_vec(&json!([{"command":"file.save_as","params":{
                "path":saved,"cache":true,"preview":true,"overwrite":true}}]))?,
            )?;
            // The CLI's cached-open path warms the same body meshes the application uses before saving.
            let log = command(
                "solidcraft-cli",
                &[
                    "bench-open".into(),
                    source.display().to_string(),
                    "--ops".into(),
                    ops.display().to_string(),
                ],
                &scratch.join(format!("{name}-save.log")),
            )?;
            stages = log
                .lines()
                .filter_map(|line| serde_json::from_str::<Value>(line).ok())
                .collect();
            display = preview(&saved, &packed, version)?;
        }
        let node = &catalog["nodes"][name.trim_end_matches("-reference")];
        let assembly = fs::read(root.join(format!(
            "native/{}.json",
            name.trim_end_matches("-reference")
        )))
        .ok()
        .and_then(|b| serde_json::from_slice::<Value>(&b).ok());
        if display.is_none()
            && node["children"].is_string()
            && node["barrel"] != true
            && node["omit"].as_array().is_none_or(Vec::is_empty)
            && assembly.as_ref().is_some_and(|a| {
                a["features"]
                    .as_array()
                    .is_some_and(|f| f.iter().all(|f| f["type"] == "import"))
            })
        {
            assemblies.push((
                name.clone(),
                sha,
                json!(stages.iter().find(|s| s["step"] == "evaluate")),
                start.elapsed().as_secs_f64() * 1000.,
            ));
            continue;
        }
        let (mut display, file) = match display {
            Some(display) => (display, format!("{name}.preview.zip")),
            None => {
                let target = output.join(format!("{name}.3mf"));
                let script = scratch.join(format!("{name}-export.json"));
                fs::write(
                    &script,
                    serde_json::to_vec(&json!({"commands":[
                        {"command":"doc.open","params":{"path":saved}},
                        {"command":"file.export","params":{"path":target,"format":"3mf-tagged","quality":"standard"}}
                    ]}))?,
                )?;
                command(
                    "solidcraft-cli",
                    &[
                        "run".into(),
                        script.display().to_string(),
                        "--timings".into(),
                        "--json-out".into(),
                        scratch
                            .join(format!("{name}-export-result.json"))
                            .display()
                            .to_string(),
                    ],
                    &scratch.join(format!("{name}-export.log")),
                )?;
                let bytes = fs::read(&target)?;
                let mut archive = ZipArchive::new(Cursor::new(bytes.as_slice()))?;
                let xml = String::from_utf8(read_part(&mut archive, "3D/3dmodel.model")?)?;
                (
                    json!({"kind":"native-export","triangles":xml.matches("<triangle ").count(),
                    "bodies":xml.matches("<mesh>").count(),"fallback":"SolidCraft omitted the saved display cache after warming its meshes."}),
                    format!("{name}.3mf"),
                )
            }
        };
        display["file"] = json!(file);
        display["sourceSha256"] = json!(sha);
        display["sha256"] = json!(hash(&fs::read(output.join(&file))?));
        display["bytes"] = json!(fs::metadata(output.join(&file))?.len());
        display["prepareMs"] = json!(start.elapsed().as_secs_f64() * 1000.);
        display["open"] = json!(stages.iter().find(|s| s["step"] == "evaluate"));
        println!(
            "{}: {} · {} triangles",
            name, display["kind"], display["triangles"]
        );
        index["models"][name] = display;
    }
    while !assemblies.is_empty() {
        let mut waiting = Vec::new();
        let count = assemblies.len();
        for (name, sha, open, prepare_ms) in assemblies {
            let start = Instant::now();
            let path = root.join(format!(
                "native/{}.json",
                name.trim_end_matches("-reference")
            ));
            let bytes = fs::read(path)?;
            let model: Value = serde_json::from_slice(&bytes)?;
            let mut entries = Vec::new();
            let mut dependencies = serde_json::Map::new();
            let mut triangles = 0;
            let mut bodies = 0;
            for occurrence in model["occurrences"]
                .as_array()
                .ok_or("native assembly occurrences")?
            {
                let component = occurrence["component"]
                    .as_u64()
                    .ok_or("native occurrence component")?
                    .to_string();
                let link = model["links"][&component]["path"]
                    .as_str()
                    .ok_or("native assembly link")?;
                let child = Path::new(link)
                    .file_stem()
                    .ok_or("native source name")?
                    .to_str()
                    .ok_or("native source encoding")?;
                let child = if child == "probe-coil" {
                    "probe"
                } else {
                    child
                };
                let display = &index["models"][child];
                if display.is_null() {
                    entries.clear();
                    break;
                }
                let file = display["file"].as_str().ok_or("native child display")?;
                let colors: Vec<Value> = model["features"]
                    .as_array()
                    .ok_or("native import features")?
                    .iter()
                    .filter(|f| f["component"] == occurrence["component"])
                    .flat_map(|f| f["body_names"].as_array().into_iter().flatten())
                    .map(|name| {
                        let body =
                            &model["appearances"]["bodies"][name.as_str().unwrap_or("")]["color"];
                        let color = if body.is_array() {
                            body
                        } else {
                            &model["appearances"]["components"][&component]["color"]
                        };
                        color
                            .as_array()
                            .map(|channels| {
                                json!(
                                    channels
                                        .iter()
                                        .map(|v| v.as_f64().unwrap_or(0.) / 255.)
                                        .collect::<Vec<_>>()
                                )
                            })
                            .unwrap_or(Value::Null)
                    })
                    .collect();
                entries.push(json!({"file":format!("parts/{file}"),"kind":display["kind"],"transform":occurrence["transform"],"colors":colors}));
                dependencies.insert(child.to_owned(), display["sha256"].clone());
                triangles += display["triangles"]
                    .as_u64()
                    .ok_or("native triangle count")?;
                bodies += display["bodies"].as_u64().ok_or("native body count")?;
            }
            if entries.is_empty() {
                waiting.push((name, sha, open, prepare_ms));
                continue;
            }
            let previous = &old["models"][&name];
            let file = format!("{name}.assembly.zip");
            let assembly_sha = hash(&bytes);
            if old["recipe"] == RECIPE
                && old["solidcraft"] == version
                && previous["sourceSha256"] == sha
                && previous["assemblySha256"] == assembly_sha
                && previous["dependencies"] == json!(dependencies)
                && fs::read(output.join(&file)).is_ok_and(|b| previous["sha256"] == hash(&b))
            {
                index["models"][&name] = previous.clone();
                reused += 1;
                continue;
            }
            let manifest = json!({"format":"solidcraft-display-assembly/1","occurrences":entries});
            let mut archive = ZipWriter::new(fs::File::create(output.join(&file))?);
            let options =
                SimpleFileOptions::default().compression_method(zip::CompressionMethod::Stored);
            archive.start_file("assembly.json", options)?;
            archive.write_all(&serde_json::to_vec(&manifest)?)?;
            for child in dependencies.keys() {
                let file = index["models"][child]["file"]
                    .as_str()
                    .ok_or("native display file")?;
                archive.start_file(format!("parts/{file}"), options)?;
                archive.write_all(&fs::read(output.join(file))?)?;
            }
            archive.finish()?;
            index["models"][&name] = json!({"kind":"assembly-preview","file":file,"sourceSha256":sha,
                "assemblySha256":assembly_sha,"dependencies":dependencies,"triangles":triangles,"bodies":bodies,
                "bytes":fs::metadata(output.join(&file))?.len(),"sha256":hash(&fs::read(output.join(&file))?),
                "prepareMs":prepare_ms+start.elapsed().as_secs_f64()*1000.,"open":open,
                "fallback":"The assembly package reuses its direct children's native saved meshes because the combined native preview is omitted."});
            println!("{name}: assembly of saved native meshes · {triangles} triangles");
        }
        if waiting.len() == count {
            return Err("native display dependencies could not be resolved".into());
        }
        assemblies = waiting;
    }
    fs::write(
        output.join("index.json"),
        serde_json::to_string_pretty(&index)? + "\n",
    )?;
    let summary = json!({"purpose":"This run prepares the assembly lab's native display payloads.",
        "solidcraft":version,"models":sources.len(),"reused":reused,"wallMs":started.elapsed().as_secs_f64()*1000.});
    fs::write(
        scratch.join("display-summary.json"),
        serde_json::to_string_pretty(&summary)? + "\n",
    )?;
    println!("{summary}");
    Ok(())
}
