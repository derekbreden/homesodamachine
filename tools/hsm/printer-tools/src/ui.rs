//! Drive the existing native Bambu Connect input process only for explicit send commands.
use crate::archive::Details;
use anyhow::{bail, Context, Result};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::{
    collections::BTreeMap,
    fs,
    io::{BufRead, BufReader, Write},
    path::Path,
    process::{Child, ChildStdin, Command, Stdio},
    sync::mpsc::{self, Receiver},
    thread,
    time::{Duration, Instant},
};

pub const PRINTERS: [&str; 2] = ["H2C", "Mark2"];
pub const OPTIONS: [(&str, &str); 4] = [
    ("Timelapse", "On"),
    ("Auto bed leveling", "On"),
    ("Flow dynamic calibration", "Auto"),
    ("Nozzle Offset Calibration", "Auto"),
];
pub fn shown(printer: &str) -> Result<&'static str> {
    match printer {
        "H2C" => Ok("Mark1"),
        "Mark2" => Ok("Mark2"),
        _ => bail!("Unknown printer {printer}"),
    }
}
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Node {
    pub id: usize,
    pub parent: i64,
    pub role: String,
    #[serde(default)]
    pub label: String,
    #[serde(default)]
    pub rect: [f64; 4],
    #[serde(default)]
    pub enabled: bool,
}
pub trait Input {
    fn call(&mut self, request: Value) -> Result<Value>;
    fn nodes(&mut self) -> Result<Vec<Node>> {
        Ok(serde_json::from_value(
            self.call(json!({"command":"snapshot"}))?["nodes"].clone(),
        )?)
    }
    fn click(&mut self, label: &str, role: &str, nth: usize, prefix: bool) -> Result<Value> {
        let deadline = Instant::now() + Duration::from_secs(3);
        loop {
            match self.call(
                json!({"command":"click","label":label,"role":role,"nth":nth,"prefix":prefix}),
            ) {
                Err(error)
                    if error.to_string().contains("Control is covered")
                        && Instant::now() < deadline =>
                {
                    thread::sleep(Duration::from_millis(300))
                }
                result => return result,
            }
        }
    }
}
pub struct Ui {
    process: Child,
    input: Option<ChildStdin>,
    replies: Receiver<std::io::Result<String>>,
}
impl Ui {
    pub fn open(root: &Path, cache: &Path) -> Result<Self> {
        fs::create_dir_all(cache)?;
        let source = root.join("tools/bambu-ui/main.swift");
        let binary = cache.join("bambu-ui");
        if !binary.is_file() || binary.metadata()?.modified()? < source.metadata()?.modified()? {
            let status = Command::new(root.join("tools/run"))
                .arg("--")
                .args(["swiftc", "-O"])
                .arg(&source)
                .arg("-o")
                .arg(&binary)
                .status()?;
            if !status.success() {
                bail!("Compile native Bambu input process: {status}")
            }
        }
        let mut process = Command::new(binary)
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .spawn()?;
        let input = process.stdin.take();
        let stdout = process.stdout.take().unwrap();
        let (tx, replies) = mpsc::channel();
        thread::spawn(move || {
            for line in BufReader::new(stdout).lines() {
                if tx.send(line).is_err() {
                    break;
                }
            }
        });
        let mut ui = Self {
            process,
            input,
            replies,
        };
        ui.call(json!({"command":"focus"}))?;
        Ok(ui)
    }
    pub fn settled(&mut self) -> Result<Vec<Node>> {
        let deadline = Instant::now() + Duration::from_secs(15);
        let mut previous = Value::Null;
        let mut stable = Instant::now();
        while Instant::now() < deadline {
            let nodes = self.nodes()?;
            let fingerprint = json!(nodes
                .iter()
                .map(|n| (&n.role, &n.label, n.rect, n.enabled))
                .collect::<Vec<_>>());
            if fingerprint != previous {
                previous = fingerprint;
                stable = Instant::now()
            } else if dialog(&nodes)
                && selected_options(&nodes).len() == OPTIONS.len()
                && !matching(&nodes, "confirm", Some("AXButton")).is_empty()
                && stable.elapsed() >= Duration::from_millis(800)
            {
                return Ok(nodes);
            }
            thread::sleep(Duration::from_millis(200));
        }
        bail!("The print dialog kept changing while loading the printer")
    }
}
impl Input for Ui {
    fn call(&mut self, request: Value) -> Result<Value> {
        let input = self.input.as_mut().context("UI process is closed")?;
        serde_json::to_writer(&mut *input, &request)?;
        writeln!(input)?;
        input.flush()?;
        let line = self
            .replies
            .recv_timeout(Duration::from_secs(60))
            .context("The UI input process did not respond")??;
        let result: Value = serde_json::from_str(&line)?;
        if result["ok"] != true {
            bail!(
                "{} {}: {}",
                request["command"].as_str().unwrap_or(""),
                request["label"].as_str().unwrap_or(""),
                result["error"].as_str().unwrap_or("Unknown UI error")
            )
        }
        Ok(result)
    }
}
impl Drop for Ui {
    fn drop(&mut self) {
        self.input.take();
        let deadline = Instant::now() + Duration::from_secs(5);
        while Instant::now() < deadline {
            if self.process.try_wait().ok().flatten().is_some() {
                return;
            }
            thread::sleep(Duration::from_millis(50))
        }
        let _ = self.process.kill();
        let _ = self.process.wait();
    }
}
pub fn wait(
    ui: &mut impl Input,
    seconds: f64,
    predicate: impl Fn(&[Node]) -> bool,
) -> Result<Vec<Node>> {
    let deadline = Instant::now() + Duration::from_secs_f64(seconds);
    let mut nodes = Vec::new();
    while Instant::now() < deadline {
        nodes = ui.nodes()?;
        if predicate(&nodes) {
            return Ok(nodes);
        }
        thread::sleep(Duration::from_millis(200));
    }
    bail!(
        "The expected Bambu Connect control did not appear; page: {}",
        page_text(&nodes)
    )
}
pub fn matching<'a>(nodes: &'a [Node], label: &str, role: Option<&str>) -> Vec<&'a Node> {
    nodes
        .iter()
        .filter(|n| n.label == label && role.is_none_or(|role| n.role == role))
        .collect()
}
pub fn page_text(nodes: &[Node]) -> String {
    nodes
        .iter()
        .filter(|n| n.role == "AXStaticText")
        .map(|n| n.label.as_str())
        .collect::<Vec<_>>()
        .join(" | ")
}
pub fn visible_error(nodes: &[Node]) -> String {
    let mut found = Vec::new();
    for node in nodes.iter().filter(|n| n.role == "AXStaticText") {
        if [
            "resource does not exist",
            "request failed",
            "upload failed",
            "network error",
            "failed to send",
        ]
        .iter()
        .any(|term| node.label.to_lowercase().contains(term))
            && !found.contains(&node.label.as_str())
        {
            found.push(node.label.as_str())
        }
    }
    found.join(" | ")
}
pub fn dialog(nodes: &[Node]) -> bool {
    !matching(nodes, "Send to print", Some("AXGroup")).is_empty()
}
pub fn close_dialog(ui: &mut impl Input) -> Result<()> {
    let mut nodes = ui.nodes()?;
    if nodes.iter().any(|n| n.role == "AXSheet")
        && !matching(&nodes, "Close", Some("AXButton")).is_empty()
    {
        ui.click("Close", "AXButton", 0, false)?;
        nodes = wait(ui, 15., |ns| {
            matching(ns, "Close", Some("AXButton")).is_empty()
        })?;
    }
    if dialog(&nodes) {
        if let Err(error) = ui.click("cancel", "AXButton", 0, false) {
            if dialog(&ui.nodes()?) {
                return Err(error);
            }
        }
        wait(ui, 15., |ns| !dialog(ns))?;
    } else if nodes.iter().any(|n| n.role == "AXSheet")
        && !matching(&nodes, "Cancel", Some("AXButton")).is_empty()
    {
        ui.click("Cancel", "AXButton", 0, false)?;
    }
    Ok(())
}
pub fn selected_options(nodes: &[Node]) -> BTreeMap<String, String> {
    let mut selected = BTreeMap::new();
    let mut current = None;
    for node in nodes {
        if node.role == "AXStaticText" && OPTIONS.iter().any(|(name, _)| node.label == *name) {
            current = Some(&node.label)
        }
        if let Some(name) = current {
            if node.role == "AXRadioButton"
                && nodes.iter().any(|child| {
                    (child.parent == node.id as i64 || child.parent == node.parent)
                        && child.role == "AXImage"
                        && child.label == "radio"
                })
            {
                selected.insert(name.clone(), node.label.clone());
            }
        }
    }
    selected
}
pub fn wanted(timelapse: &str) -> BTreeMap<String, String> {
    OPTIONS
        .iter()
        .map(|(name, value)| {
            (
                name.to_string(),
                if *name == "Timelapse" {
                    timelapse
                } else {
                    value
                }
                .to_string(),
            )
        })
        .collect()
}
pub fn set_options(ui: &mut impl Input, desired: &BTreeMap<String, String>) -> Result<()> {
    let mut nodes = wait(ui, 15., |ns| selected_options(ns).len() == desired.len())?;
    for (label, want) in desired {
        if selected_options(&nodes).get(label) == Some(want) {
            continue;
        }
        let start = matching(&nodes, label, Some("AXStaticText"))
            .first()
            .context("Missing print option label")?
            .id;
        let end = nodes
            .iter()
            .filter(|n| n.id > start && n.role == "AXStaticText" && desired.contains_key(&n.label))
            .map(|n| n.id)
            .min()
            .unwrap_or(nodes.len());
        let candidate = nodes
            .iter()
            .find(|n| n.id > start && n.id < end && n.role == "AXRadioButton" && n.label == *want)
            .context("Missing print option button")?;
        let nth = matching(&nodes, want, Some("AXRadioButton"))
            .iter()
            .position(|n| n.id == candidate.id)
            .unwrap();
        ui.click(want, "AXRadioButton", nth, false)?;
        nodes = wait(ui, 15., |ns| selected_options(ns).get(label) == Some(want))?;
    }
    if selected_options(&nodes) != *desired {
        bail!("Print options do not match the requested settings")
    }
    Ok(())
}
pub fn nozzle_tiles(nodes: &[Node], nozzle: u8) -> Vec<&Node> {
    let left = matching(nodes, "Left Nozzle", Some("AXStaticText"));
    let right = matching(nodes, "Right Nozzle", Some("AXStaticText"));
    let options = matching(nodes, "Print Options", Some("AXStaticText"));
    if left.len() != 1 || right.len() != 1 || options.len() != 1 {
        return Vec::new();
    }
    let heading = if nozzle == 1 { left[0] } else { right[0] };
    let top = heading.rect[1] + heading.rect[3];
    let bottom = options[0].rect[1];
    let divider = right[0].rect[0];
    nodes
        .iter()
        .filter(|n| {
            n.role == "AXGroup"
                && !n.label.is_empty()
                && n.rect[2] > 0.
                && n.rect[3] > 0.
                && n.rect[1] >= top
                && n.rect[1] + n.rect[3] <= bottom
                && (if n.rect[0] >= divider { 2 } else { 1 }) == nozzle
        })
        .collect()
}
pub fn external_mapped(nodes: &[Node], nozzle: u8, kind: &str) -> bool {
    let tiles = nozzle_tiles(nodes, nozzle);
    let label = format!("Ext {kind}");
    tiles.len() == 1
        && (tiles[0].label == label
            || tiles[0].label == format!("{label} {}", if nozzle == 1 { "L" } else { "R" }))
}
pub fn map_external(ui: &mut impl Input, details: &Details) -> Result<()> {
    for (nozzle, filament) in &details.slots {
        let nodes = wait(ui, 15., |ns| {
            let tiles = nozzle_tiles(ns, *nozzle);
            tiles.len() == 1
                && !(tiles[0].label.starts_with("Ext ") && tiles[0].label.ends_with('?'))
        })?;
        if external_mapped(&nodes, *nozzle, &filament.kind) {
            continue;
        }
        let tile = nozzle_tiles(&nodes, *nozzle)[0];
        let nth = matching(&nodes, &tile.label, Some("AXGroup"))
            .iter()
            .position(|n| n.id == tile.id)
            .unwrap();
        let result=ui.call(json!({"command":"select_external","label":tile.label,"role":"AXGroup","nth":nth,"nozzle":nozzle,"filament":filament.kind}))?;
        wait(ui, 15., |ns| external_mapped(ns, *nozzle, &filament.kind))?;
        println!(
            "Mapped {} external {}: {}",
            if *nozzle == 1 { "left" } else { "right" },
            filament.kind,
            result["clicked"].as_str().unwrap_or("")
        );
    }
    Ok(())
}
pub fn verify(
    nodes: &[Node],
    printer: &str,
    details: &Details,
    desired: &BTreeMap<String, String>,
) -> Result<()> {
    if !dialog(nodes)
        || matching(nodes, &format!("{} chevron_down", shown(printer)?), None).len() != 1
    {
        bail!("The send dialog does not identify the requested printer")
    }
    let tiles: Vec<_> = nodes
        .iter()
        .filter(|n| n.role == "AXGroup" && n.label.starts_with("Ext "))
        .collect();
    if tiles.len() != details.slots.len() || !matching(nodes, "? ?", Some("AXGroup")).is_empty() {
        bail!("An external spool mapping is missing")
    }
    let right: Vec<_> = nodes
        .iter()
        .filter(|n| n.role == "AXStaticText" && n.label.starts_with("Right Nozzle"))
        .collect();
    if right.len() != 1 {
        bail!("The nozzle columns could not be identified")
    }
    for tile in tiles {
        let nozzle = if tile.rect[0] >= right[0].rect[0] {
            2
        } else {
            1
        };
        let filament = details
            .slots
            .get(&nozzle)
            .context("The external spool is mapped to the wrong nozzle")?;
        let label = format!("Ext {}", filament.kind);
        if tile.label != label
            && tile.label != format!("{label} {}", if nozzle == 1 { "L" } else { "R" })
        {
            bail!(
                "The selected tile reads {}, expected {}",
                tile.label,
                filament.kind
            )
        }
    }
    if selected_options(nodes) != *desired {
        bail!("The print options changed")
    }
    Ok(())
}
pub fn prepare(
    ui: &mut Ui,
    path: &Path,
    printer: &str,
    details: &Details,
    desired: &BTreeMap<String, String>,
) -> Result<Vec<Node>> {
    close_dialog(ui)?;
    ui.click("Devices", "AXLink", 0, false)?;
    let display = shown(printer)?;
    wait(ui, 15., |ns| {
        ns.iter()
            .filter(|n| {
                n.role == "AXLink"
                    && (n.label == display || n.label.starts_with(&format!("{display} ")))
            })
            .count()
            == 1
    })?;
    ui.click(display, "AXLink", 0, true)?;
    wait(ui, 15., |ns| {
        !matching(ns, "Printing Progress", Some("AXStaticText")).is_empty()
    })?;
    ui.click("Print", "AXLink", 0, false)?;
    let nodes = wait(ui, 15., |ns| {
        ns.iter()
            .filter(|n| {
                n.role == "AXButton"
                    && matches!(
                        n.label.as_str(),
                        "Import Gcode 3MF" | "import Import Gcode 3MF"
                    )
            })
            .count()
            == 1
    })?;
    let button = nodes
        .iter()
        .find(|n| {
            n.role == "AXButton"
                && matches!(
                    n.label.as_str(),
                    "Import Gcode 3MF" | "import Import Gcode 3MF"
                )
        })
        .unwrap();
    ui.click(&button.label, "AXButton", 0, false)?;
    wait(ui, 15., |ns| ns.iter().any(|n| n.role == "AXSheet"))?;
    ui.call(json!({"command":"open_path","path":path}))?;
    wait(ui, 15., |ns| {
        !matching(ns, "Open", Some("AXButton")).is_empty()
    })?;
    ui.click("Open", "AXButton", 0, false)?;
    let filename = path.file_name().unwrap().to_string_lossy();
    wait(ui, 30., |ns| {
        !ns.iter().any(|n| n.role == "AXSheet")
            && page_text(ns).contains(filename.as_ref())
            && page_text(ns).contains("Compatible Printer")
    })?;
    println!("Imported {}: {}", filename, details.objects.join(", "));
    ui.click("Print", "AXButton", 0, false)?;
    let mut nodes = ui.settled()?;
    let selectors: Vec<_> = nodes
        .iter()
        .filter(|n| ["Mark1 chevron_down", "Mark2 chevron_down"].contains(&n.label.as_str()))
        .collect();
    if selectors.len() != 1 {
        bail!("The send dialog has no unique printer selector")
    }
    let selector = selectors[0];
    if selector.label != format!("{display} chevron_down") {
        ui.call(json!({"command":"click_offsets","label":selector.label,"role":selector.role,"offsets":[[70,32],[81,91+36*PRINTERS.iter().position(|p|*p==printer).unwrap()]]}))?;
        wait(ui, 15., |ns| {
            !matching(ns, &format!("{display} chevron_down"), None).is_empty()
        })?;
        nodes = ui.settled()?;
    }
    drop(nodes);
    set_options(ui, desired)?;
    map_external(ui, details)?;
    wait(ui, 15., |ns| {
        matching(ns, "? ?", Some("AXGroup")).is_empty()
            && ns
                .iter()
                .filter(|n| n.role == "AXGroup" && n.label.starts_with("Ext "))
                .count()
                == details.slots.len()
            && !ns.iter().any(|n| {
                n.role == "AXGroup" && n.label.starts_with("Ext ") && n.label.ends_with('?')
            })
    })?;
    verify(&ui.nodes()?, printer, details, desired)?;
    wait(ui, 15., |ns| {
        !matching(ns, "confirm", Some("AXButton")).is_empty()
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::archive::Filament;
    struct Fixture {
        nodes: Vec<Node>,
        requests: Vec<Value>,
    }
    impl Input for Fixture {
        fn call(&mut self, request: Value) -> Result<Value> {
            self.requests.push(request.clone());
            if request["command"] == "snapshot" {
                return Ok(json!({"nodes":self.nodes}));
            }
            if request["command"] == "select_external" {
                let nozzle = request["nozzle"].as_u64().unwrap() as u8;
                let id = nozzle_tiles(&self.nodes, nozzle)[0].id;
                let kind = request["filament"].as_str().unwrap();
                self.nodes.iter_mut().find(|n| n.id == id).unwrap().label =
                    format!("Ext {kind} {}", if nozzle == 1 { "L" } else { "R" });
                return Ok(json!({"clicked":"fixture only"}));
            }
            bail!("Unexpected fixture input")
        }
    }
    fn node(id: usize, role: &str, label: &str, rect: [f64; 4]) -> Node {
        Node {
            id,
            parent: 0,
            role: role.into(),
            label: label.into(),
            rect,
            enabled: true,
        }
    }
    #[test]
    fn duplicate_unmapped_labels_are_selected_by_nozzle_column() {
        for offset in [0., 247.] {
            let mut fixture = Fixture {
                nodes: vec![
                    node(
                        1,
                        "AXStaticText",
                        "Left Nozzle",
                        [offset + 10., 10., 100., 20.],
                    ),
                    node(
                        2,
                        "AXStaticText",
                        "Right Nozzle",
                        [offset + 200., 10., 100., 20.],
                    ),
                    node(3, "AXGroup", "? ?", [offset + 20., 50., 80., 60.]),
                    node(4, "AXGroup", "? ?", [offset + 210., 50., 80., 60.]),
                    node(
                        5,
                        "AXStaticText",
                        "Print Options",
                        [offset + 10., 160., 200., 20.],
                    ),
                ],
                requests: Vec::new(),
            };
            let details = Details {
                name: String::new(),
                sha256: String::new(),
                gcode_sha256: String::new(),
                objects: vec![],
                slots: BTreeMap::from([
                    (
                        2,
                        Filament {
                            kind: "PETG".into(),
                            colour: "FFFFFF".into(),
                        },
                    ),
                    (
                        1,
                        Filament {
                            kind: "PLA".into(),
                            colour: "000000".into(),
                        },
                    ),
                ]),
            };
            let mut right_only = Fixture {
                nodes: fixture.nodes.clone(),
                requests: Vec::new(),
            };
            let mut right_details = details.clone();
            right_details.slots.remove(&1);
            map_external(&mut right_only, &right_details).unwrap();
            assert_eq!(
                right_only
                    .requests
                    .iter()
                    .find(|request| request["command"] == "select_external")
                    .unwrap()["nth"],
                1
            );
            map_external(&mut fixture, &details).unwrap();
            let selections: Vec<_> = fixture
                .requests
                .iter()
                .filter(|r| r["command"] == "select_external")
                .collect();
            assert_eq!(selections.len(), 2);
            assert_eq!(selections[0]["nth"], 0);
            assert_eq!(selections[1]["nth"], 0);
            assert!(external_mapped(&fixture.nodes, 1, "PLA"));
            assert!(!external_mapped(&fixture.nodes, 1, "PETG"));
            fixture.requests.clear();
            map_external(&mut fixture, &details).unwrap();
            assert!(!fixture
                .requests
                .iter()
                .any(|r| r["command"] == "select_external"));
        }
    }
}
