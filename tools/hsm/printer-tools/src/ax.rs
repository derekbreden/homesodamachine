//! Preserve the background accessibility sender and use the native visible picker for hidden popovers.
use crate::{
    archive::{self, Details},
    mqtt::Watch,
    send::Options,
    state,
    ui::{self, Ui},
};
use anyhow::{bail, Context, Result};
use regex::Regex;
use serde_json::Value;
use std::{
    collections::BTreeMap,
    path::{Path, PathBuf},
    process::Command,
    thread,
    time::{Duration, Instant},
};

#[derive(Clone, Debug)]
struct Node {
    index: usize,
    role: String,
    label: String,
    x: Option<i64>,
    y: Option<i64>,
    enabled: bool,
}
struct Ax {
    binary: PathBuf,
}
impl Ax {
    fn call(&self, args: &[String], check: bool) -> Result<String> {
        let result = Command::new(&self.binary).args(args).output()?;
        let text = format!(
            "{}{}",
            String::from_utf8_lossy(&result.stdout),
            String::from_utf8_lossy(&result.stderr)
        )
        .trim()
        .to_owned();
        if check && !result.status.success() {
            bail!("bambu-ax {} failed:\n{text}", args.join(" "))
        }
        Ok(text)
    }
    fn command(&self, args: &[&str], check: bool) -> Result<String> {
        self.call(
            &args.iter().map(|s| s.to_string()).collect::<Vec<_>>(),
            check,
        )
    }
    fn tree(&self, check: bool) -> Result<Vec<Node>> {
        parse(&self.command(&["tree"], check)?)
    }
    fn press(&self, label: &str, role: &str, check: bool) -> Result<()> {
        self.command(&["press", label, "--role", role], check)?;
        Ok(())
    }
    fn wait(
        &self,
        seconds: f64,
        check: bool,
        predicate: impl Fn(&[Node]) -> bool,
    ) -> Result<Option<Vec<Node>>> {
        let deadline = Instant::now() + Duration::from_secs_f64(seconds);
        while Instant::now() < deadline {
            let nodes = self.tree(check)?;
            if predicate(&nodes) {
                return Ok(Some(nodes));
            }
            thread::sleep(Duration::from_millis(500))
        }
        Ok(None)
    }
    fn close(&self) {
        let _ = self.press("cancel", "AXButton", false);
    }
    fn ensure(&self) -> Result<()> {
        let ready = || -> Result<bool> {
            Ok(self.command(&["state"], false)?.contains("My Printers")
                || self.command(&["tree"], false)?.contains("\"Devices\""))
        };
        if ready()? {
            return Ok(());
        }
        if !Command::new("pgrep")
            .args(["-f", "Bambu Connect.app/Contents/MacOS/Bambu Connect"])
            .output()?
            .status
            .success()
        {
            println!("Bambu Connect is not running; starting it in the background");
            Command::new("open")
                .args(["-g", "-a", "Bambu Connect"])
                .status()?;
        }
        let deadline = Instant::now() + Duration::from_secs(60);
        while Instant::now() < deadline {
            thread::sleep(Duration::from_secs(2));
            if ready()? {
                thread::sleep(Duration::from_secs(3));
                return Ok(());
            }
        }
        bail!("Bambu Connect did not come up")
    }
}
fn parse(text: &str) -> Result<Vec<Node>> {
    let re = Regex::new(
        r#"^#(?P<idx>\d+) (?P<indent> *)(?P<role>\S+)(?: "(?P<label>.*?)")?(?: \[(?P<acts>[^\]]*)\])?(?: @(?P<x>-?\d+),(?P<y>-?\d+) (?P<w>\d+)x(?P<h>\d+))?(?P<disabled> \(disabled\))?$"#,
    )?;
    text.lines()
        .filter_map(|line| re.captures(line))
        .map(|m| {
            Ok(Node {
                index: m["idx"].parse()?,
                role: m["role"].into(),
                label: m.name("label").map(|s| s.as_str()).unwrap_or("").into(),
                x: m.name("x").map(|s| s.as_str().parse()).transpose()?,
                y: m.name("y").map(|s| s.as_str().parse()).transpose()?,
                enabled: m.name("disabled").is_none(),
            })
        })
        .collect()
}
fn dialog(nodes: &[Node]) -> bool {
    nodes
        .iter()
        .any(|n| n.role == "AXGroup" && n.label == "Send to print")
}
fn selector(nodes: &[Node]) -> Option<&Node> {
    nodes.iter().find(|n| {
        n.role == "AXGroup"
            && matches!(
                n.label.as_str(),
                "Mark1 chevron_down" | "Mark2 chevron_down"
            )
    })
}
fn options(nodes: &[Node]) -> BTreeMap<String, (Option<String>, Vec<&Node>)> {
    let mut result = BTreeMap::new();
    let labels: Vec<_> = nodes
        .iter()
        .filter(|n| {
            n.role == "AXStaticText"
                && ui::OPTIONS.iter().any(|(key, _)| n.label == *key)
                && n.x.is_some()
        })
        .collect();
    for label in &labels {
        result.insert(label.label.clone(), (None, Vec::new()));
    }
    for button in nodes
        .iter()
        .filter(|n| n.role == "AXRadioButton" && n.x.is_some())
    {
        if let Some(label) = labels
            .iter()
            .filter(|n| {
                n.x < button.x && n.y.zip(button.y).is_some_and(|(a, b)| (a - b).abs() <= 12)
            })
            .max_by_key(|n| n.x)
        {
            result.get_mut(&label.label).unwrap().1.push(button)
        }
    }
    for (chosen, buttons) in result.values_mut() {
        buttons.sort_by_key(|n| n.x);
        for button in &*buttons {
            if nodes.iter().any(|child| {
                child.index == button.index + 1 && child.role == "AXImage" && child.label == "radio"
            }) {
                *chosen = Some(button.label.clone())
            }
        }
    }
    result
}
fn prepare(
    ax: &Ax,
    root: &Path,
    cache: &Path,
    options: &Options,
    details: &Details,
    imported: &Path,
    reading: &Value,
) -> Result<()> {
    ax.ensure()?;
    if dialog(&ax.tree(true)?) {
        ax.close();
        if ax
            .wait(10., true, |n| !n.is_empty() && !dialog(n))?
            .is_none()
        {
            bail!("An earlier send dialog would not close")
        }
    }
    let display = ui::shown(&options.printer)?;
    ax.press("Devices", "AXLink", true)?;
    thread::sleep(Duration::from_millis(1500));
    ax.press(display, "AXLink", true)?;
    if ax
        .wait(8., true, |ns| {
            ns.iter()
                .any(|n| n.role == "AXStaticText" && n.label == "Printing Progress")
                && ns
                    .iter()
                    .any(|n| n.role == "AXStaticText" && n.label == display)
        })?
        .is_none()
    {
        bail!("Could not open {display}'s device page")
    }
    let result = ax.call(
        &["import".into(), imported.to_string_lossy().into_owned()],
        true,
    )?;
    if !result.contains("-> loaded") {
        bail!("Import did not load {}: {result}", details.name)
    }
    let summary = ax.command(&["state"], true)?;
    if !summary.contains(&details.name) || !summary.contains("Compatible Printer") {
        bail!("The Print tab does not identify the imported archive")
    }
    ax.press("Print", "AXButton", true)?;
    let mut nodes = ax
        .wait(10., true, |n| dialog(n) && selector(n).is_some())?
        .context("The Send to print dialog did not open")?;
    if selector(&nodes).unwrap().label != format!("{display} chevron_down") {
        let row = ui::PRINTERS
            .iter()
            .position(|name| *name == options.printer)
            .unwrap() as i64;
        let mut selected = false;
        for _ in 0..3 {
            thread::sleep(Duration::from_secs(2));
            let current = selector(&nodes).context("Missing printer selector")?;
            let x = current.x.context("Selector has no position")?;
            let y = current.y.context("Selector has no position")?;
            ax.call(
                &[
                    "click".into(),
                    (x + 70).to_string(),
                    (y + 32).to_string(),
                    (x + 81).to_string(),
                    (y + 91 + 36 * row).to_string(),
                ],
                true,
            )?;
            if let Some(taken) = ax.wait(5., true, |n| {
                dialog(n)
                    && selector(n).is_some_and(|s| s.label == format!("{display} chevron_down"))
            })? {
                nodes = taken;
                selected = true;
                break;
            }
            nodes = ax
                .wait(3., true, |n| dialog(n) && selector(n).is_some())?
                .context("The dialog closed under the printer popover clicks")?;
        }
        if !selected {
            ax.close();
            bail!("The printer popover did not select {display}")
        }
    }
    drop(nodes);
    archive::verify_spools(details, reading)?;
    {
        let mut foreground = Ui::open(root, cache)?;
        if let Err(error) = ui::map_external(&mut foreground, details) {
            ax.close();
            return Err(error);
        }
    }
    let mut nodes = ax
        .wait(10., true, |n| self::options(n).len() == ui::OPTIONS.len())?
        .context("The dialog's print options did not appear")?;
    let desired = ui::wanted(&options.timelapse);
    for (name, want) in &desired {
        let current = self::options(&nodes);
        let (chosen, buttons) = current.get(name).context("Missing print option")?;
        if chosen.as_ref() == Some(want) {
            continue;
        }
        let target = buttons
            .iter()
            .find(|button| button.label == *want)
            .context("Missing print option button")?;
        ax.call(
            &[
                "press".into(),
                format!("#{}", target.index),
                "--expect".into(),
                want.clone(),
            ],
            true,
        )?;
        thread::sleep(Duration::from_millis(600));
        nodes = ax.tree(true)?;
    }
    let selected: BTreeMap<_, _> = self::options(&nodes)
        .into_iter()
        .filter_map(|(name, (value, _))| value.map(|value| (name, value)))
        .collect();
    if selected != desired {
        ax.close();
        bail!("The print options do not match the requested settings")
    }
    if selector(&nodes).is_none_or(|n| n.label != format!("{display} chevron_down")) {
        ax.close();
        bail!("The printer selector changed")
    }
    let mut foreground = Ui::open(root, cache)?;
    use ui::Input;
    ui::verify(&foreground.nodes()?, &options.printer, details, &desired)?;
    Ok(())
}
pub fn send(
    root: &Path,
    cache: &Path,
    options: &Options,
    details: &Details,
    imported: &Path,
    watch: &mut Watch,
) -> Result<Option<Value>> {
    let ax = Ax {
        binary: root.join("tools/bambu-ax/bambu-ax"),
    };
    let first = watch.activity.initial.clone();
    if !options.dry_run && state::manual_heat(&first) {
        wait_heat(watch, options.busy_wait)?;
    }
    for attempt in 0..options.attempts {
        let before = watch.fresh()?.clone();
        if state::accepted(&first, &before, &details.name) {
            return Ok(Some(before));
        }
        if !options.dry_run && !state::may_retry(&first, &before, watch.activity.activity, "") {
            bail!("The printer changed or is heating; nothing more was sent")
        }
        std::fs::copy(&options.path, imported)?;
        let prepared = prepare(&ax, root, cache, options, details, imported, &before);
        if let Err(error) = prepared {
            ax.close();
            return Err(error);
        }
        let ready = ax.wait(15., true, |ns| {
            ns.iter()
                .any(|n| n.role == "AXButton" && n.label == "confirm" && n.enabled)
        })?;
        if options.dry_run {
            ax.close();
            println!(
                "Dry run: Send is {}; dialog cancelled",
                if ready.is_some() {
                    "enabled"
                } else {
                    "disabled"
                }
            );
            return Ok(None);
        }
        if ready.is_none() {
            ax.close();
            bail!("Send stayed disabled; nothing was sent")
        }
        let current = watch.fresh()?.clone();
        if !state::may_retry(&first, &current, watch.activity.activity, "") {
            ax.close();
            bail!("The printer changed before Send; nothing more was sent")
        }
        archive::verify_spools(details, &current)?;
        if crate::digest(&options.path)? != details.sha256 {
            ax.close();
            bail!("The archive changed after import")
        }
        println!("Sending attempt {}: one accessibility press", attempt + 1);
        if let Err(error) = ax.press("confirm", "AXButton", true) {
            println!("Send input returned {error}; checking the printer before any further action")
        }
        let closed = ax
            .wait(30., false, |ns| !ns.is_empty() && !dialog(ns))?
            .is_some();
        let deadline = Instant::now() + options.timeout + Duration::from_secs(30);
        let extended = deadline + options.timeout;
        loop {
            watch.drain(Duration::from_secs(5))?;
            let mut current = watch.fresh()?.clone();
            if let Some(reply) = &watch.activity.reply {
                if !matches!(
                    reply["result"]
                        .as_str()
                        .map(str::to_ascii_lowercase)
                        .as_deref(),
                    Some("success" | "ok")
                ) {
                    ax.close();
                    bail!("Printer refused the job: {reply}")
                }
            }
            if state::accepted(&first, &current, &details.name) {
                watch.drain(Duration::from_secs(3))?;
                let current = watch.fresh()?.clone();
                if state::accepted(&first, &current, &details.name) {
                    if !closed {
                        ax.close()
                    }
                    return Ok(Some(current));
                }
            }
            let page = ax.command(&["state"], false)?;
            let lower = page.to_lowercase();
            if [
                "resource does not exist",
                "request failed",
                "upload failed",
                "network error",
                "failed to send",
            ]
            .iter()
            .any(|word| lower.contains(word))
            {
                ax.close();
                bail!("Bambu Connect rejected the send; no repeat send: {page}")
            }
            if Instant::now() < deadline {
                continue;
            }
            if ["sending", "uploading", "downloading"]
                .iter()
                .any(|word| lower.contains(word))
                && Instant::now() < extended
            {
                continue;
            }
            if !closed {
                ax.close()
            }
            if state::manual_heat(&current) && !watch.activity.activity {
                wait_heat(watch, options.busy_wait)?;
                current = watch.fresh()?.clone();
                if state::accepted(&first, &current, &details.name) {
                    return Ok(Some(current));
                }
            }
            if !state::may_retry(&first, &current, watch.activity.activity, &page) {
                bail!("The send has an uncertain or rejected result; no repeat send. Printer: {current}")
            }
            break;
        }
        if attempt + 1 < options.attempts {
            println!("No printer activity or transfer; opening a fresh send dialog")
        }
    }
    bail!("The printer received no job after the bounded send attempts")
}
fn wait_heat(watch: &mut Watch, timeout: Duration) -> Result<()> {
    let deadline = Instant::now() + timeout;
    while state::manual_heat(&watch.activity.reading) {
        if Instant::now() >= deadline {
            bail!("The printer kept a manual heat; nothing more was sent")
        }
        println!("Waiting for the manual heat to end");
        thread::sleep(Duration::from_secs(10));
        watch.fresh()?;
    }
    Ok(())
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn accessibility_option_radios_belong_to_the_nearest_label_on_the_left() {
        let nodes=parse("#1 AXStaticText \"Timelapse\" @10,20 50x20\n#2 AXRadioButton \"On\" @70,20 20x20\n#3 AXImage \"radio\"\n#4 AXRadioButton \"Off\" @100,20 20x20\n#5 AXStaticText \"Auto bed leveling\" @200,20 80x20\n#6 AXRadioButton \"On\" @300,20 20x20\n#7 AXRadioButton \"Off\" @330,20 20x20\n#8 AXImage \"radio\"\n#9 AXButton \"confirm\" @10,50 80x20 (disabled)").unwrap();
        let choices = options(&nodes);
        assert_eq!(choices["Timelapse"].0.as_deref(), Some("On"));
        assert_eq!(choices["Auto bed leveling"].0.as_deref(), Some("Off"));
        assert!(!nodes.last().unwrap().enabled);
    }
}
