//! Construct native identification chips and replay their historical clearance edit through SolidCraft's commands.
use serde_json::{Value, json};
use std::{
    error::Error,
    fs,
    path::{Path, PathBuf},
    process::Command,
    time::Instant,
};
type Result<T = ()> = std::result::Result<T, Box<dyn Error>>;
const ROOT: &str = "hardware/reference/rear-identification/solidcraft";

fn cmd(commands: &mut Vec<Value>, command: &str, params: Value) {
    commands.push(json!({"command":command,"params":params}));
}
fn run(commands: Vec<Value>, key: &str, out: &Path, save: Option<&Path>) -> Result<Value> {
    let script = out.join(format!("{key}-commands.json"));
    fs::write(
        &script,
        serde_json::to_vec_pretty(&json!({"commands":commands}))?,
    )?;
    let result = out.join(format!("{key}-results.json"));
    let start = Instant::now();
    let mut process = Command::new("solidcraft-cli");
    process
        .arg("run")
        .arg(&script)
        .args(["--timings", "--results", "--json-out"])
        .arg(&result);
    if let Some(save) = save {
        process.arg("--save").arg(save);
    }
    let output = process.output()?;
    fs::write(out.join(format!("{key}.log")), &output.stderr)?;
    if !output.status.success() {
        return Err(format!("{key}: {}", String::from_utf8_lossy(&output.stderr)).into());
    }
    let mut result: Value = serde_json::from_slice(&fs::read(result)?)?;
    result["process_wall_ms"] = json!(start.elapsed().as_secs_f64() * 1000.);
    fs::write(
        out.join(format!("{key}-results.json")),
        serde_json::to_vec_pretty(&result)?,
    )?;
    println!(
        "{key}: {:.1} ms",
        result["process_wall_ms"].as_f64().unwrap_or(0.)
    );
    Ok(result)
}
fn construct(input: &Value, root: &Path, out: &Path) -> Result {
    let mut commands = Vec::new();
    cmd(
        &mut commands,
        "document.metadata.set",
        json!({"values":{"description":"Complete identification chips from the historical interfaces","part_number":"SolidCraft identification replay"}}),
    );
    for (name, value) in [
        ("side_clearance", input["clearance_before"].clone()),
        ("nominal_width", input["nominal_width"].clone()),
        ("thickness", input["thickness"].clone()),
        ("word_depth", input["word_depth"].clone()),
        ("word_rise", input["word_rise"].clone()),
    ] {
        cmd(
            &mut commands,
            "parameters.add",
            json!({"name":name,"expression":format!("{} mm",value),"favorite":true}),
        );
    }
    let mut next = 1;
    let mut stocks = Vec::new();
    for (i, part) in input["parts"].as_array().ok_or("parts")?.iter().enumerate() {
        let key = part["key"].as_str().ok_or("part identity")?;
        let word = part["word"].as_str().ok_or("word")?;
        let name = format!("{key} identification chip");
        let body = format!("bulkhead-ring-{key}");
        cmd(&mut commands, "component.activate", json!({"component":0}));
        cmd(&mut commands, "component.create", json!({"name":name}));
        let component = next;
        let occurrence = next + 1;
        next += 2;
        cmd(
            &mut commands,
            "appearance.assign",
            json!({"components":[name],"color":part["word_color"],"pbr":{"metallic":0.,"roughness":0.4,"dielectric_ior":1.5}}),
        );
        let sketch = next;
        next += 1;
        cmd(
            &mut commands,
            "sketch.create",
            json!({"plane":{"origin":[0.,0.,part["word_center"]],
            "x_dir":[-1,0,0],"y_dir":[0,0,1]},"offset":"thickness - word_depth","name":format!("{word} original lettering")}),
        );
        cmd(
            &mut commands,
            "sketch.insert_svg",
            json!({"text":fs::read_to_string(root.join(format!("lettering/{word}.svg")))?,"align":"center","at":[0,0]}),
        );
        cmd(&mut commands, "sketch.finish", json!({}));
        cmd(
            &mut commands,
            "solid.extrude",
            json!({"sketch":sketch,"distance":"word_depth + word_rise","operation":"new","body_name":format!("{body}-word"),"name":format!("{word} ink")}),
        );
        next += 1;
        stocks.push((i, part, component, occurrence, sketch));
    }
    for (i, part, component, occurrence, sketch) in stocks {
        let key = part["key"].as_str().ok_or("part identity")?;
        let body = format!("bulkhead-ring-{key}");
        cmd(
            &mut commands,
            "component.activate",
            json!({"component":component}),
        );
        cmd(
            &mut commands,
            "solid.box",
            json!({"length":"nominal_width - 2 * side_clearance","width":"thickness",
            "height":part["top"].as_f64().unwrap()+part["bottom"].as_f64().unwrap(),
            "corner":["-nominal_width / 2 + side_clearance",json!(0),json!(-part["bottom"].as_f64().unwrap())],"body_name":body,"name":"Retaining-channel width"}),
        );
        cmd(
            &mut commands,
            "solid.cylinder",
            json!({"diameter":part["bore_diameter"],"height":"thickness + .2 mm",
            "base":[part["bore"][0],json!(-0.1),part["bore"][1]],"axis":[0,1,0],"operation":"cut","targets":[body],"name":"Original fitting bore"}),
        );
        cmd(
            &mut commands,
            "solid.extrude",
            json!({"sketch":sketch,"distance":"word_depth + word_rise","operation":"cut","targets":[body],"name":"Ink recess"}),
        );
        cmd(
            &mut commands,
            "appearance.assign",
            json!({"bodies":[body],"color":part["chip_color"],"pbr":{"metallic":0.,"roughness":0.4,"dielectric_ior":1.5}}),
        );
        let x = (i % 3) as f64 * 50. - 50.;
        let y = (i / 3) as f64 * 50. - 25.;
        cmd(
            &mut commands,
            "occurrence.move",
            json!({"occurrence":occurrence,"matrix":[[-1.,0.,0.,x],[0.,0.,1.,y],[0.,1.,0.,0.],[0.,0.,0.,1.]],"move_grounded":true}),
        );
    }
    cmd(&mut commands, "component.activate", json!({"component":0}));
    cmd(
        &mut commands,
        "file.export",
        json!({"path":root.join("native/before.json"),"format":"json"}),
    );
    run(
        commands,
        "construct",
        out,
        Some(&root.join("native/before.sc")),
    )?;
    Ok(())
}
fn exports(input: &Value, root: &Path, out: &Path, variant: &str, edit: bool) -> Result<Value> {
    let before: Value = serde_json::from_slice(&fs::read(root.join("native/before.json"))?)?;
    let mut commands = Vec::new();
    cmd(
        &mut commands,
        "doc.open",
        json!({"path":root.join("native/before.sc")}),
    );
    if edit {
        cmd(
            &mut commands,
            "parameters.change",
            json!({"name":"side_clearance","expression":format!("{} mm",input["clearance_after"])}),
        );
        cmd(
            &mut commands,
            "file.save_as",
            json!({"path":root.join("native/after.sc"),"cache":true,"overwrite":true}),
        );
        cmd(
            &mut commands,
            "file.export",
            json!({"path":root.join("native/after.json"),"format":"json"}),
        );
    }
    let files = out.join(format!("native-{variant}"));
    fs::create_dir_all(&files)?;
    cmd(
        &mut commands,
        "file.export",
        json!({"path":files.join("complete-set.3mf"),"format":"3mf","objects":"component","quality":"fine"}),
    );
    let mut parts = Vec::new();
    for part in input["parts"].as_array().ok_or("parts")? {
        let key = part["key"].as_str().ok_or("part identity")?;
        let name = format!("{key} identification chip");
        let component = before["components"]
            .as_array()
            .ok_or("native components")?
            .iter()
            .find(|c| c["name"] == name)
            .ok_or("native chip component")?["id"]
            .clone();
        let names: Vec<String> = before["features"]
            .as_array()
            .ok_or("native features")?
            .iter()
            .filter(|f| f["component"] == component)
            .flat_map(|f| f["body_names"].as_array().into_iter().flatten())
            .filter_map(Value::as_str)
            .map(str::to_owned)
            .collect::<std::collections::BTreeSet<_>>()
            .into_iter()
            .collect();
        cmd(
            &mut commands,
            "file.export",
            json!({"path":files.join(format!("{key}.3mf")),"format":"3mf-tagged","bodies":names,"quality":"fine"}),
        );
        parts.push((key.to_owned(), names));
    }
    for (key, names) in &parts {
        let target = format!("bulkhead-ring-{key}");
        let tools: Vec<&String> = names.iter().filter(|n| **n != target).collect();
        cmd(
            &mut commands,
            "solid.combine",
            json!({"target":target,"tools":tools,"operation":"join"}),
        );
        cmd(
            &mut commands,
            "file.export",
            json!({"path":files.join(format!("{key}.stl")),"format":"stl","bodies":[target],"quality":"fine"}),
        );
    }
    run(
        commands,
        if edit { "native-edit" } else { "native-before" },
        out,
        None,
    )
}
fn main() -> Result {
    let args: Vec<String> = std::env::args().collect();
    let out = PathBuf::from(
        args.windows(2)
            .find(|v| v[0] == "--out")
            .ok_or("--out requires a temporary run directory")?[1]
            .clone(),
    );
    fs::create_dir_all(&out)?;
    let out = out.canonicalize()?;
    let root = Path::new(ROOT).canonicalize()?;
    fs::create_dir_all(root.join("native"))?;
    let input: Value = serde_json::from_slice(&fs::read(root.join("inputs.json"))?)?;
    match args.get(1).map(String::as_str) {
        Some("construct") => construct(&input, &root, &out),
        Some("export-before") => {
            exports(&input, &root, &out, "before", false)?;
            Ok(())
        }
        Some("replay") => {
            exports(&input, &root, &out, "after", true)?;
            Ok(())
        }
        _ => Err("construct | export-before | replay --out RUN".into()),
    }
}
