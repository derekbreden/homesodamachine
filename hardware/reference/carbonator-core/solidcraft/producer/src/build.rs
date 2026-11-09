//! Build native SolidCraft parts, shallow assemblies and opaque published references from their scalar interfaces.
use serde_json::{Value, json};
use std::{error::Error, fs, path::PathBuf, process::Command};
type Result<T = ()> = std::result::Result<T, Box<dyn Error>>;
const ROOT: &str = "hardware/reference/carbonator-core/solidcraft";
struct Design {
    commands: Vec<Value>,
    next: u64,
}
impl Design {
    fn new(label: &str, id: &str) -> Self {
        let mut d = Self {
            commands: vec![],
            next: 1,
        };
        d.cmd(
            "document.metadata.set",
            json!({"values":{"description":label,"part_number":id}}),
        );
        d
    }
    fn cmd(&mut self, c: &str, p: Value) {
        self.commands.push(json!({"command":c,"params":p}));
    }
    fn part(&mut self, label: &str) {
        self.cmd("component.create", json!({"name":label}));
        self.next += 2;
    }
    fn param(&mut self, k: &str, v: f64) {
        self.cmd(
            "parameters.add",
            json!({"name":k,"expression":format!("{v} mm"),"favorite":true}),
        );
    }
    fn feature(&mut self, c: &str, p: Value) -> u64 {
        let id = self.next;
        self.next += 1;
        self.cmd(c, p);
        id
    }
    fn cylinder(
        &mut self,
        body: &str,
        diam: Value,
        height: Value,
        base: Value,
        axis: Value,
        op: &str,
    ) {
        self.feature("solid.cylinder",json!({"diameter":diam,"height":height,"base":base,"axis":axis,"body_name":body,"operation":op,"targets":if op=="new_body"{vec![]}else{vec![body]},"name":if op=="cut"{format!("Bore {body}")}else{body.into()}}));
    }
    fn box_cut(&mut self, body: &str, lo: [f64; 3], hi: [f64; 3], name: &str) {
        self.feature("solid.box",json!({"length":hi[0]-lo[0],"width":hi[1]-lo[1],"height":hi[2]-lo[2],"corner":lo,"operation":"cut","targets":[body],"name":name}));
    }
    fn appearance(&mut self, bodies: &[&str], color: &str, metal: f64) {
        self.cmd("appearance.assign",json!({"bodies":bodies,"color":color,"pbr":{"metallic":metal,"roughness":0.32,"dielectric_ior":1.5}}));
    }
    fn material(&mut self, bodies: &[&str], name: &str) {
        self.cmd("material.assign", json!({"bodies":bodies,"material":name}));
    }
    fn polygon(&mut self, name: &str, plane: Value, points: Value) -> u64 {
        let id = self.feature("sketch.create", json!({"plane":plane,"name":name}));
        self.cmd("sketch.line", json!({"points":points,"closed":true}));
        self.cmd("sketch.finish", json!({}));
        id
    }
    fn hex(&mut self, body: &str, af: f64, h: f64, base: [f64; 3], along_x: bool, op: &str) {
        let plane = if along_x {
            json!({"origin":base,"x_dir":[0,1,0],"y_dir":[0,0,1]})
        } else {
            json!({"origin":base,"x_dir":[1,0,0],"y_dir":[0,1,0]})
        };
        let r = af / 3_f64.sqrt();
        let pts = (0..6)
            .map(|i| {
                let a = (i as f64 * 60.).to_radians();
                [r * a.cos(), r * a.sin()]
            })
            .collect::<Vec<_>>();
        let s = self.polygon("Wrench flats", plane, json!(pts));
        self.feature("solid.extrude",json!({"sketch":s,"distance":h,"operation":if op=="new_body"{"new"}else{op},"targets":if op=="new_body"{vec![]}else{vec![body]},"body_name":body,"name":"Wrench section"}));
    }
    fn insert(&mut self, key: &str, label: &str, matrix: Option<Value>) -> u64 {
        self.cmd("component.activate", json!({"component":0}));
        let occ = self.next + 1;
        self.cmd(
            "component.insert_design",
            json!({"path":format!("{key}.sc"),"name":label}),
        );
        self.next += 3;
        if let Some(m) = matrix {
            self.cmd(
                "occurrence.move",
                json!({"occurrence":occ,"matrix":m,"move_grounded":true}),
            );
        }
        occ
    }
    fn rigid(&mut self, a: u64, b: u64, name: &str) {
        self.cmd(
            "joint.as_built",
            json!({"type":"rigid","a":a,"b":b,"name":name}),
        );
        self.next += 1;
    }
    fn pipe(&mut self, label: &str, segments: &[Value], diam: f64) {
        let sk = self.feature(
            "sketch.create",
            json!({"plane":"XY","name":format!("{label} path")}),
        );
        self.cmd("sketch.options", json!({"sketch_3d":true}));
        for s in segments {
            self.cmd(s["command"].as_str().unwrap(), s["params"].clone());
        }
        self.cmd("sketch.finish", json!({}));
        let wires = (1..=segments.len())
            .map(|i| format!("w{i}"))
            .collect::<Vec<_>>();
        self.feature(
            "solid.pipe",
            json!({"path_sketch":sk,"path":wires,"diameter":diam,"body_name":label,"name":label}),
        );
    }
}
fn n(c: &Value, p: &str) -> f64 {
    p.split('.')
        .fold(c, |v, k| &v[k])
        .as_f64()
        .unwrap_or_else(|| panic!("numeric contract {p}"))
}
fn colour(c: &Value, name: &str) -> String {
    let v = &c["colours"][name];
    format!(
        "#{:02x}{:02x}{:02x}",
        v[0].as_u64().unwrap(),
        v[1].as_u64().unwrap(),
        v[2].as_u64().unwrap()
    )
}
fn v3(v: &Value) -> [f64; 3] {
    std::array::from_fn(|i| v[i].as_f64().unwrap())
}
fn translated(p: [f64; 3]) -> Value {
    json!([
        [1., 0., 0., p[0]],
        [0., 1., 0., p[1]],
        [0., 0., 1., p[2]],
        [0., 0., 0., 1.]
    ])
}
fn frame(x: [f64; 3], z: [f64; 3], p: [f64; 3]) -> Value {
    let y = [
        z[1] * x[2] - z[2] * x[1],
        z[2] * x[0] - z[0] * x[2],
        z[0] * x[1] - z[1] * x[0],
    ];
    json!([
        [x[0], y[0], z[0], p[0]],
        [x[1], y[1], z[1], p[1]],
        [x[2], y[2], z[2], p[2]],
        [0., 0., 0., 1.]
    ])
}
struct Builder {
    native: PathBuf,
    scratch: PathBuf,
    only: Vec<String>,
}
impl Builder {
    fn build(&self, key: &str, d: Design) -> Result<Value> {
        let output = self.native.join(format!("{key}.json"));
        if !self.only.is_empty() && !self.only.iter().any(|s| s == key) {
            return Ok(serde_json::from_slice(&fs::read(output)?)?);
        }
        let recipe = self.scratch.join(format!("{key}-commands.json"));
        fs::write(
            &recipe,
            serde_json::to_vec_pretty(&json!({"commands":d.commands}))?,
        )?;
        println!("Building {key}");
        let log = Command::new("solidcraft-cli")
            .current_dir(&self.native)
            .arg("run")
            .arg(&recipe)
            .args(["--save"])
            .arg(self.native.join(format!("{key}.sc")))
            .args(["--out"])
            .arg(&output)
            .arg("--out")
            .arg(self.scratch.join(format!("{key}.obj")))
            .arg("--results")
            .arg("--json-out")
            .arg(self.scratch.join(format!("{key}-result.json")))
            .output()?;
        fs::write(self.scratch.join(format!("{key}.log")), &log.stderr)?;
        if !log.status.success() {
            return Err(format!("{key}: {}", String::from_utf8_lossy(&log.stderr)).into());
        }
        let mut model: Value = serde_json::from_slice(&fs::read(&output)?)?;
        if let Some(links) = model.get_mut("links").and_then(Value::as_object_mut) {
            for link in links.values_mut() {
                if let Some(path) = link["path"].as_str() {
                    link["path"] = json!(
                        std::path::Path::new(path)
                            .file_name()
                            .unwrap()
                            .to_string_lossy()
                    );
                }
            }
        }
        fs::write(&output, serde_json::to_string_pretty(&model)? + "\n")?;
        Ok(model)
    }
    fn reference(&self, key: &str, label: &str, id: &str, exclude: &[&str]) -> Result<Value> {
        let full: Value =
            serde_json::from_slice(&fs::read(self.native.join(format!("{key}.json")))?)?;
        let names = full["features"]
            .as_array()
            .unwrap()
            .iter()
            .filter_map(|f| f["body_names"].as_array())
            .flatten()
            .filter_map(Value::as_str)
            .filter(|s| exclude.iter().any(|t| s.contains(t)))
            .collect::<Vec<_>>();
        let input = if names.is_empty() {
            key.to_string()
        } else {
            let mut stage = Design::new(label, id);
            stage.insert(key, label, None);
            stage.cmd("component.break_link", json!({"component":label}));
            stage.feature("solid.remove", json!({"bodies":names}));
            if key == "weldment" {
                let c: Value = serde_json::from_slice(&fs::read(
                    self.native.parent().unwrap().join("contracts.json"),
                )?)?;
                stage.cylinder(
                    "Published barrel",
                    c["tube"]["outer_diameter"].clone(),
                    c["tube"]["length"].clone(),
                    json!([0, 0, 0]),
                    json!("Z"),
                    "new_body",
                );
                stage.cylinder(
                    "Published barrel",
                    c["tube"]["bore_diameter"].clone(),
                    c["tube"]["length"].clone(),
                    json!([0, 0, 0]),
                    json!("Z"),
                    "cut",
                );
                stage.material(&["Published barrel"], "Stainless Steel");
                stage.appearance(&["Published barrel"], "#b4bbc5", 0.8);
            }
            let sk = format!("{key}-stage");
            self.build(&sk, stage)?;
            sk
        };
        let mut d = Design::new(label, id);
        d.insert(&input, label, None);
        d.cmd("component.break_link", json!({"component":label}));
        self.build(&format!("{key}-reference"), d)
    }
}
pub fn run() -> Result {
    let repo = std::env::current_dir()?;
    let native = repo.join(ROOT).join("native");
    fs::create_dir_all(&native)?;
    let mut only = std::env::args().skip(2).collect::<Vec<_>>();
    let output = if let Some(at) = only.iter().position(|v| v == "--out") {
        only.remove(at);
        only.remove(at)
    } else {
        format!(
            ".cache/runs/solidcraft-levels-{}-{}",
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)?
                .as_secs(),
            std::process::id()
        )
    };
    let scratch = repo.join(output);
    fs::create_dir_all(&scratch)?;
    println!("Display exports: {}", scratch.display());
    let b = Builder {
        native,
        scratch,
        only,
    };
    let c: Value = serde_json::from_slice(&fs::read(repo.join(ROOT).join("contracts.json"))?)?;
    let cap_t = n(&c, "cap.thickness");
    let recess = n(&c, "cap.recess");
    let l = n(&c, "tube.length");
    let rxy = [
        c["cap"]["register_xy"][0].as_f64().unwrap(),
        c["cap"]["register_xy"][1].as_f64().unwrap(),
    ];
    let mut d = Design::new("Prepared carbonator tube with rim earth tap", "HSM-0008");
    d.part("Vessel tube");
    for (k, p) in [
        ("outer_diameter", "tube.outer_diameter"),
        ("bore_diameter", "tube.bore_diameter"),
        ("length", "tube.length"),
    ] {
        d.param(k, n(&c, p));
    }
    d.cylinder(
        "Vessel tube",
        json!("outer_diameter"),
        json!("length"),
        json!([0, 0, 0]),
        json!("Z"),
        "new_body",
    );
    d.cylinder(
        "Vessel tube",
        json!("bore_diameter"),
        json!("length"),
        json!([0, 0, 0]),
        json!("Z"),
        "cut",
    );
    let contact = v3(&c["bond"]["contact"]);
    let out = v3(&c["bond"]["out"]);
    d.feature("solid.hole",json!({"position":contact,"direction":out.map(|v|-v),"thread":"M3","depth":n(&c,"tube.wall")+1.,"targets":["Vessel tube"],"name":"Earth clamp tap"}));
    d.material(&["Vessel tube"], "Stainless Steel");
    d.appearance(&["Vessel tube"], "#b4bbc5", 0.8);
    b.build("vessel-tube", d)?;
    let mut d = Design::new(
        "Machined carbonator endcap with port pilots and conical blind rod register",
        "HSM-0009",
    );
    d.part("Machined endcap");
    for (k, p) in [
        ("cap_diameter", "cap.diameter"),
        ("thickness", "cap.thickness"),
        ("tap_pilot", "cap.port_diameter"),
        ("register_diameter", "cap.register_diameter"),
        ("register_depth", "cap.register_depth"),
    ] {
        d.param(k, n(&c, p));
    }
    d.cylinder(
        "Machined endcap",
        json!("cap_diameter"),
        json!("thickness"),
        json!([0, 0, 0]),
        json!("Z"),
        "new_body",
    );
    for y in [
        -n(&c, "cap.port_spacing") / 2.,
        n(&c, "cap.port_spacing") / 2.,
    ] {
        d.cylinder(
            "Machined endcap",
            json!("tap_pilot"),
            json!("thickness"),
            json!([0, y, 0]),
            json!("Z"),
            "cut",
        );
    }
    d.cmd("parameters.add",json!({"name":"drill_point","expression":format!("{} deg",n(&c,"cap.register_point_angle"))}));
    d.cmd("parameters.add",json!({"name":"register_cone_height","expression":"register_diameter / (2 * tan(drill_point / 2))"}));
    d.cylinder(
        "Machined endcap",
        json!("register_diameter"),
        json!("register_depth - register_cone_height"),
        json!([rxy[0], rxy[1], "thickness"]),
        json!([0, 0, -1]),
        "cut",
    );
    d.feature("solid.cone",json!({"radius":"register_diameter / 2","top_radius":0,"height":"register_cone_height","base":[rxy[0],rxy[1],"thickness - register_depth + register_cone_height"],"axis":[0,0,-1],"operation":"cut","targets":["Machined endcap"],"name":"Register drill point"}));
    d.material(&["Machined endcap"], "Stainless Steel");
    d.appearance(&["Machined endcap"], "#c0c6cf", 0.8);
    b.build("machined-cap", d)?;
    let mut d = Design::new(
        "Flat-ended float guide rod from the controlled finished-length drawing",
        "HSM-0336",
    );
    d.part("Guide rod");
    d.param("finished_length", n(&c, "rod.length"));
    d.param("diameter", n(&c, "rod.diameter"));
    d.cylinder(
        "Guide rod",
        json!("diameter"),
        json!("finished_length"),
        json!([0, 0, 0]),
        json!("Z"),
        "new_body",
    );
    d.material(&["Guide rod"], "Stainless Steel");
    d.appearance(&["Guide rod"], "#aeb8c3", 0.8);
    b.build("guide-rod", d)?;
    let mut d = Design::new("Welded upper float stop", "HSM-0459");
    d.part("Upper stop");
    d.cylinder(
        "Upper stop",
        c["stop"]["diameter"].clone(),
        c["stop"]["height"].clone(),
        json!([0, 0, 0]),
        json!("Z"),
        "new_body",
    );
    d.cylinder(
        "Upper stop",
        c["stop"]["bore"].clone(),
        c["stop"]["height"].clone(),
        json!([0, 0, 0]),
        json!("Z"),
        "cut",
    );
    d.material(&["Upper stop"], "Stainless Steel");
    d.appearance(&["Upper stop"], "#aeb8c3", 0.8);
    b.build("upper-stop", d)?;
    let mut d = Design::new(
        "ASA Aero float shell with enclosed annular magnet pocket",
        "HSM-0033",
    );
    d.part("ASA Aero float shell");
    for (k, p) in [
        ("diameter", "float.diameter"),
        ("height", "float.height"),
        ("guide_bore", "float.bore"),
    ] {
        d.param(k, n(&c, p));
    }
    d.cylinder(
        "ASA Aero float shell",
        json!("diameter"),
        json!("height"),
        json!([0, 0, 0]),
        json!("Z"),
        "new_body",
    );
    d.cylinder(
        "ASA Aero float shell",
        json!("guide_bore"),
        json!("height"),
        json!([0, 0, 0]),
        json!("Z"),
        "cut",
    );
    d.cylinder(
        "Magnet pocket tool",
        c["float"]["pocket_od"].clone(),
        c["float"]["pocket_depth"].clone(),
        json!([0, 0, n(&c, "float.magnet_seat")]),
        json!("Z"),
        "new_body",
    );
    d.cylinder(
        "Magnet pocket tool",
        c["float"]["pocket_id"].clone(),
        c["float"]["pocket_depth"].clone(),
        json!([0, 0, n(&c, "float.magnet_seat")]),
        json!("Z"),
        "cut",
    );
    d.feature("solid.combine",json!({"target":"ASA Aero float shell","tools":["Magnet pocket tool"],"operation":"cut","keep_tools":false,"name":"Enclosed ring magnet pocket"}));
    d.cmd(
        "material.create",
        json!({"name":"ASA Aero","density_g_cm3":0.65,"color":"#e6e3dc"}),
    );
    d.material(&["ASA Aero float shell"], "ASA Aero");
    d.appearance(&["ASA Aero float shell"], "#e6e3dc", 0.);
    b.build("float-shell", d)?;
    let mut d = Design::new("RC62 ring magnet", "HSM-0034");
    d.part("RC62 ring magnet");
    d.cylinder(
        "RC62 ring magnet",
        c["float"]["magnet_od"].clone(),
        c["float"]["magnet_thickness"].clone(),
        json!([0, 0, 0]),
        json!("Z"),
        "new_body",
    );
    d.cylinder(
        "RC62 ring magnet",
        c["float"]["magnet_id"].clone(),
        c["float"]["magnet_thickness"].clone(),
        json!([0, 0, 0]),
        json!("Z"),
        "cut",
    );
    d.appearance(&["RC62 ring magnet"], "#8e949e", 1.);
    b.build("ring-magnet", d)?;
    let mut d = Design::new("Magnetic level float", "HSM-0032");
    let shell = d.insert("float-shell", "Float shell", None);
    let magnet = d.insert(
        "ring-magnet",
        "RC62 magnet",
        Some(translated([0., 0., n(&c, "float.magnet_seat")])),
    );
    d.rigid(shell, magnet, "Magnet seat");
    b.build("float", d)?;
    b.reference("float", "Magnetic float", "HSM-0032", &["RC62"])?;
    let mut d = Design::new("Bottom endcap and seated guide rod", "HSM-0565");
    let cap = d.insert("machined-cap", "Bottom endcap", None);
    let rod = d.insert(
        "guide-rod",
        "Guide rod",
        Some(translated([
            rxy[0],
            rxy[1],
            cap_t - n(&c, "rod.register_seat_depth"),
        ])),
    );
    d.rigid(cap, rod, "Guide rod in drill-point seat");
    b.build("lower-cap", d)?;
    b.reference("lower-cap", "Bottom endcap and guide", "HSM-0565", &[])?;
    let mut d = Design::new("Top endcap and welded float stop", "HSM-0566");
    let cap = d.insert("machined-cap", "Top endcap", None);
    let stop = d.insert(
        "upper-stop",
        "Upper stop",
        Some(translated([rxy[0], rxy[1], cap_t])),
    );
    d.rigid(cap, stop, "Stop concentric with register");
    b.build("upper-cap", d)?;
    b.reference("upper-cap", "Top endcap and stop", "HSM-0566", &[])?;
    let mut d = Design::new(
        "Carbonator vessel weldment with captive guided magnetic float",
        "HSM-0567",
    );
    d.param("float_z", c["float"]["at"][2].as_f64().unwrap());
    let tube = d.insert("vessel-tube", "Vessel tube", None);
    let lower = d.insert(
        "lower-cap-reference",
        "Bottom endcap and guide",
        Some(translated([0., 0., recess])),
    );
    d.rigid(tube, lower, "Lower cap weld fit");
    let upper = d.insert(
        "upper-cap-reference",
        "Top endcap and stop",
        Some(frame([-1., 0., 0.], [0., 0., -1.], [0., 0., l - recess])),
    );
    d.rigid(tube, upper, "Upper cap weld fit");
    let fl = d.insert(
        "float-reference",
        "Magnetic float",
        Some(translated([
            rxy[0],
            rxy[1],
            c["float"]["at"][2].as_f64().unwrap() - n(&c, "float.height") / 2.,
        ])),
    );

    d.cmd("joint.create",json!({"type":"slider","a":{"occurrence":tube,"point":[rxy[0],rxy[1],0],"z":[0,0,1],"x":[1,0,0]},"b":{"occurrence":fl,"point":[rxy[0],rxy[1],c["float"]["at"][2]],"z":[0,0,1],"x":[1,0,0]},"flip":true,"values":["float_z"],"limits":[c["float"]["travel"]],"name":"Captive float travel"}));
    b.build("weldment", d)?;
    b.reference(
        "weldment",
        "Carbonator vessel weldment",
        "HSM-0567",
        &["Vessel tube", "Guide rod", "Upper stop", "ASA Aero"],
    )?;
    build_outer(&b, &c)?;
    Ok(())
}
fn build_outer(b: &Builder, c: &Value) -> Result {
    let mut d = Design::new(
        "TAISHER street elbow with orthogonal flow bores and female socket",
        "HSM-0010",
    );
    d.part("Street elbow");
    let af = n(c, "street_elbow.hex");
    let up = 21.35;
    let leg = n(c, "street_elbow.leg");
    d.hex("Street elbow", af, up, [0., 0., 0.], false, "new_body");
    d.hex("Street elbow", af, leg, [0., 0., 0.], true, "join");
    d.cylinder(
        "Street elbow",
        json!(n(c, "street_elbow.male_radius") * 2.),
        c["street_elbow"]["male_length"].clone(),
        json!([0, 0, up]),
        json!("Z"),
        "join",
    );
    d.cylinder(
        "Street elbow",
        c["street_elbow"]["bore"].clone(),
        json!(up + n(c, "street_elbow.male_length")),
        json!([0, 0, 0]),
        json!("Z"),
        "cut",
    );
    d.cylinder(
        "Street elbow",
        c["street_elbow"]["bore"].clone(),
        json!(leg),
        json!([0, 0, 0]),
        json!("X"),
        "cut",
    );
    d.cylinder(
        "Street elbow",
        json!(2. * n(c, "street_elbow.socket_radius")),
        c["street_elbow"]["socket_depth"].clone(),
        json!([leg - n(c, "street_elbow.socket_depth"), 0, 0]),
        json!("X"),
        "cut",
    );
    d.material(&["Street elbow"], "Stainless Steel");
    d.appearance(&["Street elbow"], "#b4bbc5", 0.8);
    b.build("street-elbow", d)?;
    let mut d = Design::new("Drilled water-inlet jet cap", "HSM-0011");
    d.part("Water inlet jet");
    d.cylinder(
        "Water inlet jet",
        c["jet"]["diameter"].clone(),
        c["jet"]["height"].clone(),
        json!([0, 0, 0]),
        json!("Z"),
        "new_body",
    );
    d.cylinder(
        "Water inlet jet",
        c["jet"]["bore"].clone(),
        c["jet"]["height"].clone(),
        json!([0, 0, 0]),
        json!("Z"),
        "cut",
    );
    d.material(&["Water inlet jet"], "Stainless Steel");
    d.appearance(&["Water inlet jet"], "#b4bbc5", 0.8);
    b.build("jet-cap", d)?;
    let mut d = Design::new("Water-inlet jet elbow", "HSM-0338");
    let e = d.insert("street-elbow", "Street elbow", None);
    let jet = d.insert(
        "jet-cap",
        "Jet cap",
        Some(translated([0., 0., up + n(c, "street_elbow.male_length")])),
    );
    d.rigid(e, jet, "Jet cap weld at male tip");
    b.build("inlet", d)?;
    b.reference("inlet", "Water-inlet jet elbow", "HSM-0338", &[])?;
    let mut d = Design::new(
        "neoFit male push-fit elbow with socket and flow bores",
        "HSM-0375",
    );
    d.part("neoFit elbow");
    let radius = n(c, "male_elbow.diameter") / 2.;
    let reach = n(c, "male_elbow.mouth_reach");
    let ar = n(c, "male_elbow.axis_reach");
    d.cylinder(
        "neoFit elbow",
        c["male_elbow"]["diameter"].clone(),
        json!(reach),
        json!([0, 0, 0]),
        json!("X"),
        "new_body",
    );
    d.cylinder(
        "neoFit elbow",
        c["male_elbow"]["post"].clone(),
        json!(radius + ar),
        json!([0, 0, -radius]),
        json!("Z"),
        "join",
    );
    d.cylinder(
        "neoFit elbow",
        json!(2. * n(c, "street_elbow.male_radius")),
        c["male_elbow"]["thread"].clone(),
        json!([0, 0, ar]),
        json!("Z"),
        "join",
    );
    d.cylinder(
        "neoFit elbow",
        c["male_elbow"]["tube"].clone(),
        c["male_elbow"]["insertion"].clone(),
        json!([reach - n(c, "male_elbow.insertion"), 0, 0]),
        json!("X"),
        "cut",
    );
    d.cylinder(
        "neoFit elbow",
        c["male_elbow"]["bore"].clone(),
        json!(reach),
        json!([0, 0, 0]),
        json!("X"),
        "cut",
    );
    d.cylinder(
        "neoFit elbow",
        c["male_elbow"]["bore"].clone(),
        json!(ar + n(c, "male_elbow.thread")),
        json!([0, 0, 0]),
        json!("Z"),
        "cut",
    );
    d.appearance(&["neoFit elbow"], &colour(c, "pushfit"), 0.);
    b.build("pushfit-elbow", d)?;
    let mut d = Design::new("SV125 pressure relief valve envelope", "HSM-0012");
    d.part("Pressure relief valve");
    let ml = n(c, "prv.male_length");
    let hh = n(c, "prv.hex_height");
    d.cylinder(
        "Pressure relief valve",
        json!(2. * n(c, "street_elbow.male_radius")),
        json!(ml),
        json!([0, 0, -ml]),
        json!("Z"),
        "new_body",
    );
    d.hex(
        "Pressure relief valve",
        n(c, "prv.hex"),
        hh,
        [0., 0., 0.],
        false,
        "join",
    );
    d.cylinder(
        "Pressure relief valve",
        json!(2. * n(c, "prv.cap_radius")),
        c["prv"]["cap_height"].clone(),
        json!([0, 0, hh]),
        json!("Z"),
        "join",
    );
    d.appearance(&["Pressure relief valve"], &colour(c, "brass"), 0.8);
    b.build("relief-valve", d)?;
    let mut d = Design::new(
        "PETG pressure relief shroud with downward vent socket",
        "HSM-0024",
    );
    d.part("PRV shroud");
    d.cylinder(
        "PRV shroud",
        c["shroud"]["outer_diameter"].clone(),
        c["shroud"]["length"].clone(),
        json!([0, 0, 0]),
        json!("Z"),
        "new_body",
    );
    d.cylinder(
        "PRV shroud",
        c["shroud"]["inner_diameter"].clone(),
        json!(n(c, "shroud.cavity") + 0.1),
        json!([0, 0, -0.1]),
        json!("Z"),
        "cut",
    );
    d.cylinder(
        "PRV shroud",
        c["shroud"]["vent_diameter"].clone(),
        json!(n(c, "shroud.outer_diameter") / 2. + 0.1),
        json!([0, 0, n(c, "shroud.vent_z")]),
        json!([0, -1, 0]),
        "cut",
    );
    d.cylinder(
        "PRV shroud",
        c["shroud"]["vent_diameter"].clone(),
        json!(n(c, "shroud.outer_diameter") / 2. + 0.1),
        json!([
            0,
            0,
            n(c, "shroud.vent_z") - n(c, "shroud.supported_surface")
        ]),
        json!([0, -1, 0]),
        "cut",
    );
    d.appearance(&["PRV shroud"], "#222832", 0.);
    b.build("prv-shroud", d)?;
    let mut d = Design::new(
        "Bench-assembled pressure relief elbow, valve and shroud",
        "HSM-0553",
    );
    let e = d.insert("street-elbow", "Street elbow", None);
    let valve = d.insert(
        "relief-valve",
        "Pressure relief valve",
        Some(frame([0., 1., 0.], [1., 0., 0.], [leg, 0., 0.])),
    );
    d.rigid(e, valve, "Valve socket make-up");
    let shroud = d.insert(
        "prv-shroud",
        "PRV shroud",
        Some(frame([0., -1., 0.], [1., 0., 0.], [leg, 0., 0.])),
    );
    d.rigid(e, shroud, "Shroud seat");
    b.build("relief", d)?;
    b.reference("relief", "Pressure-relief assembly", "HSM-0553", &[])?;
    let mut d = Design::new("Fitted carbonator vessel", "HSM-0004");
    let vessel = d.insert("weldment-reference", "Vessel weldment", None);
    for p in c["ports"].as_array().unwrap() {
        let name = p["name"].as_str().unwrap();
        let key = match name {
            "water-in" => "inlet-reference",
            "prv" => "relief-reference",
            _ => "pushfit-elbow",
        };
        let o = d.insert(
            key,
            name,
            Some(frame(v3(&p["out"]), v3(&p["up"]), v3(&p["corner"]))),
        );
        d.rigid(vessel, o, &format!("{name} port make-up"));
    }
    b.build("vessel", d)?;
    b.reference("vessel", "Carbonator vessel", "HSM-0004", &[])?;
    build_instrumentation(b, c)
}
fn build_instrumentation(b: &Builder, c: &Value) -> Result {
    let mut d = Design::new(
        "Formed evaporator coil and free tails with reed-bridge lift",
        "HSM-0015",
    );
    d.part("Evaporator coil");
    let points = c["coil"]["points"].as_array().unwrap();
    let mut sampled = points.iter().step_by(3).cloned().collect::<Vec<_>>();
    if sampled.last() != points.last() {
        sampled.push(points.last().unwrap().clone());
    }
    d.pipe(
        "Copper winding",
        &[json!({"command":"sketch.spline3d","params":{"points":sampled}})],
        n(c, "coil.tube_diameter"),
    );
    let mut copper = vec!["Copper winding"];
    for (i, t) in c["coil"]["tails"].as_array().unwrap().iter().enumerate() {
        let name = if i == 0 {
            "Inlet copper tail"
        } else {
            "Outlet copper tail"
        };
        let segs=t["segments"].as_array().unwrap().iter().map(|s|if s["type"]=="arc"{json!({"command":"sketch.arc3d","params":{"start":s["start"],"through":s["mid"],"end":s["end"]}})}else{json!({"command":"sketch.line3d","params":{"points":[s["start"],s["end"]]}})}).collect::<Vec<_>>();
        d.pipe(name, &segs, n(c, "coil.tube_diameter"));
        copper.push(name);
    }
    for command in &mut d.commands {
        if command["command"] == "solid.pipe" {
            command["params"]["wall"] = c["coil"]["wall"].clone();
        }
    }
    d.feature("solid.split_face",json!({"body":"Copper winding","faces":[[n(c,"coil.radius")+n(c,"coil.tube_diameter")/2.,0.,n(c,"coil.bottom")+n(c,"coil.pitch")/4.],[n(c,"coil.radius")+n(c,"coil.tube_diameter")/2.-n(c,"coil.wall"),0.,n(c,"coil.bottom")+n(c,"coil.pitch")/4.]],"plane":"YZ","name":"Winding reference face boundaries"}));
    d.material(&copper, "Copper");
    d.appearance(&copper, &colour(c, "copper"), 0.85);
    b.build("coil", d)?;
    let mut d = Design::new(
        "Printed reed bridge with cylinder fit, side ramps, glass pockets and lead groove",
        "HSM-0029",
    );
    d.part("Reed bridge");
    let inner = n(c, "bridge.inner");
    let skirt = n(c, "bridge.skirt");
    let plateau = n(c, "bridge.plateau");
    let bottom = n(c, "bridge.bottom");
    let top = n(c, "bridge.top");
    let pb = n(c, "bridge.plateau_bottom");
    let pt = n(c, "bridge.plateau_top");
    let sk = d.polygon(
        "Radial ramp profile",
        json!({"origin":[0,0,0],"x_dir":[1,0,0],"y_dir":[0,0,1]}),
        json!([
            [inner, bottom],
            [skirt, bottom],
            [plateau, pb],
            [plateau, pt],
            [skirt, top],
            [inner, top]
        ]),
    );
    d.feature("solid.revolve",json!({"sketch":sk,"axis":"Z","body_name":"Reed bridge","name":"Cylindrical fit and end ramps"}));
    let mut plan = vec![json!([0, 0])];
    plan.extend(c["bridge"]["plan"].as_array().unwrap().iter().cloned());
    let sk = d.polygon(
        "Side ramp plan",
        json!({"origin":[0,0,bottom-0.1],"x_dir":[1,0,0],"y_dir":[0,1,0]}),
        json!(plan),
    );
    d.feature("solid.extrude",json!({"sketch":sk,"distance":top-bottom+0.2,"operation":"intersect","targets":["Reed bridge"],"name":"Side ramps"}));
    let half = n(c, "bridge.pocket_width") / 2.;
    let gw = n(c, "bridge.groove_width");
    let gy = n(c, "bridge.groove_y");
    let notch = n(c, "bridge.notch_length");
    for z in c["bridge"]["reed_z"].as_array().unwrap() {
        let z = z.as_f64().unwrap();
        let lo = z - n(c, "bridge.pocket_length") / 2.;
        let hi = z + n(c, "bridge.pocket_length") / 2.;
        d.box_cut(
            "Reed bridge",
            [inner - 0.1, -half, lo],
            [plateau + 0.1, half, hi],
            "Reed glass pocket",
        );
        for z in [lo, hi - notch] {
            d.box_cut(
                "Reed bridge",
                [skirt, -half, z],
                [plateau + 0.1, gy + gw / 2., z + notch],
                "Lead cross notch",
            );
        }
    }
    d.box_cut(
        "Reed bridge",
        [skirt, gy - gw / 2., pb],
        [plateau + 0.1, gy + gw / 2., top + 0.1],
        "Vertical lead groove",
    );
    d.appearance(&["Reed bridge"], "#262c34", 0.);
    b.build("reed-bridge", d)?;
    let mut d = Design::new("TO-92 temperature probe capture envelope", "HSM-0016");
    d.part("Temperature probe");
    let w = n(c, "probes.width");
    let h = n(c, "probes.height");
    d.feature(
        "solid.box",
        json!({"length":w,"width":w,"height":h,"center":[0,0,0],"body_name":"Temperature probe"}),
    );
    let edges = [
        [-w / 2., -w / 2., 0.],
        [w / 2., -w / 2., 0.],
        [-w / 2., w / 2., 0.],
        [w / 2., w / 2., 0.],
    ];
    d.feature("solid.fillet",json!({"body":"Temperature probe","edges":edges,"radius":n(c,"probes.corner"),"name":"Package capture corners"}));
    d.appearance(&["Temperature probe"], "#282c32", 0.);
    let mut other = Design {
        commands: d.commands.clone(),
        next: d.next,
    };
    other.commands[0]["params"]["values"]["part_number"] = json!("HSM-0017");
    b.build("probe", d)?;
    b.build("probe-coil", other)?;
    let mut d = Design::new("MDSR reed switch glass capture envelope", "HSM-0036");
    d.part("Reed switch");
    d.cylinder(
        "Reed switch glass",
        c["reeds"]["diameter"].clone(),
        c["reeds"]["length"].clone(),
        json!([0, 0, -n(c, "reeds.length") / 2.]),
        json!("Z"),
        "new_body",
    );
    d.appearance(&["Reed switch glass"], "#659a9b", 0.15);
    b.build("reed", d)?;
    let mut d = Design::new("Finished carbonator earth clamp screw", "HSM-0382");
    d.part("Earth clamp screw");
    d.cylinder(
        "Earth clamp screw",
        c["bond"]["head_diameter"].clone(),
        c["bond"]["head_height"].clone(),
        json!([0, 0, -n(c, "bond.head_height")]),
        json!("Z"),
        "new_body",
    );
    d.cylinder(
        "Earth clamp screw",
        c["bond"]["thread"].clone(),
        c["bond"]["screw_length"].clone(),
        json!([0, 0, 0]),
        json!("Z"),
        "join",
    );
    d.material(&["Earth clamp screw"], "Stainless Steel");
    d.appearance(&["Earth clamp screw"], "#a7afba", 0.8);
    b.build("earth-screw", d)?;
    let mut d = Design::new("Earth clamp washer capture envelope", "HSM-0381");
    d.part("Earth lockwasher");
    d.cylinder(
        "Earth lockwasher",
        c["bond"]["washer_od"].clone(),
        c["bond"]["washer_thickness"].clone(),
        json!([0, 0, 0]),
        json!("Z"),
        "new_body",
    );
    d.cylinder(
        "Earth lockwasher",
        c["bond"]["washer_bore"].clone(),
        c["bond"]["washer_thickness"].clone(),
        json!([0, 0, 0]),
        json!("Z"),
        "cut",
    );
    d.appearance(&["Earth lockwasher"], "#a7afba", 0.8);
    b.build("earth-washer", d)?;
    let mut d = Design::new(
        "Earth lead attached terminal and conductor exit interface; free harness dressing is outside the assembly pose",
        "HSM-0378",
    );
    d.part("Earth lead interface");
    d.cylinder(
        "Earth ring terminal",
        c["bond"]["ring_eye"].clone(),
        c["bond"]["ring_thickness"].clone(),
        json!([0, 0, 0]),
        json!("Z"),
        "new_body",
    );
    d.cylinder(
        "Earth ring terminal",
        c["bond"]["thread"].clone(),
        c["bond"]["ring_thickness"].clone(),
        json!([0, 0, 0]),
        json!("Z"),
        "cut",
    );
    d.cylinder(
        "Terminal crimp barrel",
        c["bond"]["ring_barrel"].clone(),
        c["bond"]["ring_barrel_length"].clone(),
        json!([0, 3, n(c, "bond.ring_barrel") / 2.]),
        json!("Y"),
        "new_body",
    );
    d.appearance(
        &["Earth ring terminal", "Terminal crimp barrel"],
        "#aeb7c0",
        0.8,
    );
    b.build("earth-lead", d)?;
    let mut d = Design::new("Instrumented carbonator and coil assembly", "HSM-0554");
    let vessel = d.insert("vessel-reference", "Carbonator vessel", None);
    let coil = d.insert("coil", "Evaporator coil", None);
    d.rigid(vessel, coil, "Coil winding and supported tail interface");
    let bridge = d.insert(
        "reed-bridge",
        "Reed bridge",
        Some(frame([0., -1., 0.], [0., 0., 1.], [0., 0., 0.])),
    );
    d.rigid(vessel, bridge, "Bridge slip fit and reed stations");
    for (k, label) in [
        ("carbonator", "DS18B20 carbonator probe"),
        ("coil", "DS18S20 coil probe"),
    ] {
        let p = d.insert(
            if k == "coil" { "probe-coil" } else { "probe" },
            label,
            Some(translated(v3(&c["probes"][k]))),
        );
        d.rigid(vessel, p, &format!("{label} bond"));
    }
    for (i, p) in c["reeds"]["positions"]
        .as_array()
        .unwrap()
        .iter()
        .enumerate()
    {
        let o = d.insert(
            "reed",
            &format!("Carbonator reed {}", i + 1),
            Some(translated(v3(p))),
        );
        d.rigid(vessel, o, "Reed pocket station");
    }
    let axis = v3(&c["bond"]["screw_axis"]);
    let under = v3(&c["bond"]["screw_underhead"]);
    for (key, label, p) in [
        ("earth-screw", "Earth clamp screw", under),
        ("earth-washer", "Earth lockwasher", under),
        (
            "earth-lead",
            "Earth lead interface",
            v3(&c["bond"]["contact"]),
        ),
    ] {
        let placement = if key == "earth-lead" {
            let out = v3(&c["bond"]["out"]);
            frame([-out[1], out[0], 0.], out, p)
        } else {
            frame([0., 0., 1.], axis, p)
        };
        let o = d.insert(key, label, Some(placement));
        d.rigid(vessel, o, "Earth clamp stack");
    }
    b.build("instrumented", d)?;
    b.reference(
        "instrumented",
        "Instrumented carbonator and coil assembly",
        "HSM-0554",
        &[],
    )?;
    let mut d = Design::new("Repeated instrumented assembly loading study", "");
    d.insert("instrumented-reference", "Instrumented carbonator", None);
    b.build("instrumented-parent", d)?;
    Ok(())
}
