//! Native output carrying preserves authored text and the publisher's model cohort.
use crate::bookkeeping_common::*;
use crate::inventory;
use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::{
    collections::{BTreeMap, BTreeSet},
    fs,
    io::{Read, Write},
    os::unix::fs::OpenOptionsExt,
    path::{Path, PathBuf},
    sync::atomic::{AtomicU64, Ordering},
};
static CARRY_SERIAL: AtomicU64 = AtomicU64::new(0);
pub fn runtime(path: &str) -> bool {
    CAD.iter().any(|s| path.ends_with(s)) || path.ends_with(".scorecard.json")
}
pub fn publisher(path: &str, cfg: &Value) -> bool {
    runtime(path)
        || [
            ".npz",
            ".facts.json",
            ".numbers.json",
            ".print.json",
            ".readiness.json",
        ]
        .iter()
        .any(|s| path.ends_with(s))
        || ["hardware/cad-artifacts.json", "web/public/tube-routes.json"].contains(&path)
        || (path.starts_with("hardware/")
            && ["design.json", "geometry-check.json"]
                .contains(&path.rsplit('/').next().unwrap_or("")))
        || (path.starts_with("hardware/print-tests/")
            && path.contains("/prints/")
            && path.ends_with(".json"))
        || inventory::inert(path, cfg)
}
pub fn whole(path: &str) -> bool {
    [".json", ".png"].contains(&suffix(path)) || path == "hardware/ledger/purchases.export.csv"
}
/// The spans whose figures a carry may rewrite: all of a Markdown file, and a Mermaid file's
/// `%%` comment lines.
fn managed(text: &str, kind: &str) -> Vec<(usize, usize)> {
    if kind == ".md" {
        return vec![(0, text.len())];
    }
    let mut at = 0;
    text.split_inclusive('\n')
        .filter_map(|line| {
            let start = at;
            at += line.len();
            line.trim_start().starts_with("%%").then_some((start, at))
        })
        .collect()
}
fn figures(text: &str, kind: &str) -> BTreeMap<String, String> {
    let mut out = BTreeMap::new();
    for (a, b) in managed(text, kind) {
        for (_, _, value, name) in hsm_documents::markers(&text[a..b]) {
            out.insert(name.into(), value.into());
        }
    }
    out
}
fn fill(text: &str, figures: &BTreeMap<String, String>) -> String {
    let mut out = String::new();
    let mut at = 0;
    for (a, b, _, name) in hsm_documents::markers(text) {
        out.push_str(&text[at..a]);
        if let Some(value) = figures.get(name) {
            out.push_str(&format!("[{value}]({name})"));
        } else {
            out.push_str(&text[a..b]);
        }
        at = b;
    }
    out.push_str(&text[at..]);
    out
}
pub fn carried(built: &str, tracked: &str, kind: &str) -> String {
    let values = figures(built, kind);
    let mut out = tracked.to_owned();
    let spans = managed(tracked, kind)
        .into_iter()
        .collect::<BTreeSet<_>>();
    for (a, b) in spans.into_iter().rev() {
        out.replace_range(a..b, &fill(&out[a..b], &values));
    }
    if kind == ".md" {
        let valid = |text: &str| {
            hsm_documents::sources_section(text)
                .filter(|(_, b)| *b > 0 && text.as_bytes()[*b - 1] == b'\n')
        };
        if let Some((a, b)) = valid(built) {
            let section = &built[a..b];
            if let Some((a, b)) = valid(&out) {
                out.replace_range(a..b, section);
            } else {
                out = out.trim_end().to_owned() + "\n\n" + section;
            }
        }
    }
    out
}
fn same(a: &Path, b: &Path) -> Result<bool> {
    let mut a = fs::File::open(a)?;
    let mut b = fs::File::open(b)?;
    let (mut x, mut y) = ([0_u8; 65536], [0_u8; 65536]);
    loop {
        let n = a.read(&mut x)?;
        let m = b.read(&mut y)?;
        if n != m || x[..n] != y[..m] {
            return Ok(false);
        }
        if n == 0 {
            return Ok(true);
        }
    }
}

struct CarryTemporary(PathBuf);
impl Drop for CarryTemporary {
    fn drop(&mut self) {
        let _ = fs::remove_file(&self.0);
    }
}

fn atomic_carry(built: &Path, target: &Path, contents: Option<&str>) -> Result<()> {
    let parent = target.parent().context("carry destination parent")?;
    fs::create_dir_all(parent)?;
    let (temporary, mut output) = loop {
        let serial = CARRY_SERIAL.fetch_add(1, Ordering::Relaxed);
        let path = parent.join(format!(
            ".{}.carry-{}-{serial}",
            target
                .file_name()
                .context("carry destination name")?
                .to_string_lossy(),
            std::process::id()
        ));
        match fs::OpenOptions::new()
            .write(true)
            .create_new(true)
            .mode(0o600)
            .open(&path)
        {
            Ok(file) => break (CarryTemporary(path), file),
            Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => (),
            Err(error) => return Err(error.into()),
        }
    };
    if let Some(contents) = contents {
        output.write_all(contents.as_bytes())?;
    } else {
        std::io::copy(&mut fs::File::open(built)?, &mut output)?;
    }
    output.flush()?;
    output.set_permissions(
        fs::metadata(target)
            .or_else(|_| fs::metadata(built))?
            .permissions(),
    )?;
    drop(output);
    fs::rename(&temporary.0, target)?;
    Ok(())
}
#[derive(Debug, Default, Deserialize)]
pub struct CarryRequest {
    pub root: PathBuf,
    /// A source blob can serve distinct declared destinations.
    #[serde(default)]
    pub pairs: Vec<(PathBuf, String)>,
    #[serde(default)]
    pub rewritten: BTreeSet<String>,
    #[serde(default)]
    pub write: bool,
    #[serde(default)]
    pub runtime_only: bool,
    #[serde(default)]
    pub derived_only: bool,
    #[serde(default)]
    pub scope_only: bool,
    #[serde(default)]
    pub config: Value,
}

#[derive(Debug, Default, Serialize)]
pub struct CarryResult {
    pub output: String,
    pub status: Option<i32>,
    #[serde(skip_serializing_if = "Vec::is_empty")]
    pub pairs: Vec<(PathBuf, String)>,
    #[serde(skip_serializing_if = "Vec::is_empty")]
    pub written: Vec<String>,
}

/// Validated native receipt pairs replace generated bytes and splice figures into authored text.
pub fn carry_request(request: &CarryRequest) -> Result<CarryResult> {
    let root = &request.root;
    let mut pairs = request.pairs.clone();
    let mut output = String::new();
    let write = request.write;
    let rewritten = &request.rewritten;
    if request.runtime_only {
        pairs.retain(|(_, p)| runtime(p));
    }
    if request.derived_only && !pairs.is_empty() {
        let all = pairs.len();
        pairs.retain(|(_, p)| !publisher(p, &request.config));
        output += &format!(
            "  {} publisher-owned output(s) left in the tree\n",
            all - pairs.len()
        );
        if pairs.is_empty() {
            output += "  no derived outputs in the requested slice\n";
            return Ok(CarryResult {
                output,
                status: Some(0),
                ..CarryResult::default()
            });
        }
    }
    if pairs.is_empty() {
        output += "  nothing built — run the requested `hsm-print-build` producer slice first\n";
        return Ok(CarryResult {
            output,
            status: Some(1),
            ..CarryResult::default()
        });
    }
    if request.scope_only {
        return Ok(CarryResult {
            output,
            status: None,
            pairs,
            ..CarryResult::default()
        });
    }
    let (mut differs, mut missing, mut unknown) = (vec![], vec![], vec![]);
    for (built, relative) in &pairs {
        let b = built.as_path();
        let t = root.join(relative);
        let kind = suffix(relative);
        let spliceable = rewritten.contains(relative) && [".md", ".mmd"].contains(&kind);
        if !b.is_file() {
            missing.push(relative.to_owned());
        } else if rewritten.contains(relative) && !spliceable && !whole(relative) {
            unknown.push(relative.to_owned());
        } else if spliceable && t.is_file() {
            let old = read_text(&t)?;
            let want = carried(&read_text(b)?, &old, kind);
            if want != old {
                differs.push((built.clone(), t, relative.to_owned(), Some(want)));
            }
        } else if !t.is_file() || !same(b, &t)? {
            differs.push((built.clone(), t, relative.to_owned(), None));
        }
    }
    for (_, _, relative, _) in differs.iter().take(20) {
        output += &format!("  {relative}\n");
    }
    if differs.len() > 20 {
        output += &format!("  …and {} more\n", differs.len() - 20);
    }
    for relative in &unknown {
        output += &format!(
            "  {relative} is read back over and {} has no splice here — left alone rather than carried whole\n",
            suffix(relative)
        );
    }
    if write {
        for (b, t, _, want) in &differs {
            atomic_carry(b, t, want.as_deref())?;
        }
        output += &format!(
            "{} carried into the tree{}\n",
            differs.len(),
            if missing.is_empty() {
                String::new()
            } else {
                format!(", {} declared output(s) absent", missing.len())
            }
        );
    } else {
        output += &format!(
            "{}/{} artifacts in the tree are the ones the build cut{}{}\n",
            pairs.len() - differs.len() - missing.len() - unknown.len(),
            pairs.len(),
            if missing.is_empty() {
                String::new()
            } else {
                format!(", {} not built", missing.len())
            },
            if unknown.is_empty() {
                String::new()
            } else {
                format!(", {} with no splice", unknown.len())
            }
        );
    }
    Ok(CarryResult {
        output,
        status: Some(i32::from(
            !unknown.is_empty() || !missing.is_empty() || !write && !differs.is_empty(),
        )),
        written: if write {
            differs
                .iter()
                .map(|(_, _, relative, _)| relative.clone())
                .collect()
        } else {
            Vec::new()
        },
        ..CarryResult::default()
    })
}

#[derive(Debug, Default, Serialize)]
pub struct StageSelection {
    pub paths: Vec<Vec<u8>>,
    pub held: Vec<Vec<u8>>,
    pub staged: Vec<Vec<u8>>,
    pub tracked: Vec<Vec<u8>>,
}

/// Derived staging leaves the publisher's model cohort at its committed bytes.
pub fn stage_selection(status: &[u8], config: &Value) -> StageSelection {
    let mut selection = StageSelection::default();
    for entry in status
        .split(|byte| *byte == 0)
        .filter(|entry| !entry.is_empty())
    {
        if entry.len() < 3 {
            continue;
        }
        let path = &entry[3..];
        if publisher(&String::from_utf8_lossy(path), config) {
            selection.held.push(path.to_vec());
            if ![b' ', b'?'].contains(&entry[0]) {
                selection.staged.push(path.to_vec());
            }
            if &entry[..2] != b"??" && entry[0] != b'A' {
                selection.tracked.push(path.to_vec());
            }
        } else {
            selection.paths.push(path.to_vec());
        }
    }
    selection
}

pub fn drop_paths(dirty: &[String], made: &BTreeSet<String>) -> (Vec<String>, Vec<String>) {
    dirty.iter().cloned().partition(|path| {
        !(glob("hardware/**/*.rs", path) || path == "tools/hsm/build-plan/graph.json")
            && made.contains(path)
    })
}
#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;
    use std::os::unix::fs::PermissionsExt;

    struct Fixture(PathBuf);
    impl Fixture {
        fn new() -> Self {
            let serial = CARRY_SERIAL.fetch_add(1, Ordering::Relaxed);
            let root = Path::new(env!("CARGO_MANIFEST_DIR"))
                .join("../../../.cache/runs")
                .join(format!("sync-fixture-{}-{serial}", std::process::id()));
            fs::create_dir_all(&root).unwrap();
            Self(root)
        }
        fn built(&self, target: &str, path: &str, bytes: &[u8]) -> PathBuf {
            let built = self.0.join("results").join(target).join(path);
            fs::create_dir_all(built.parent().unwrap()).unwrap();
            fs::write(&built, bytes).unwrap();
            built
        }
        fn tree(&self, path: &str, bytes: &[u8]) -> PathBuf {
            let file = self.0.join(path);
            fs::create_dir_all(file.parent().unwrap()).unwrap();
            fs::write(&file, bytes).unwrap();
            file
        }
    }
    impl Drop for Fixture {
        fn drop(&mut self) {
            let _ = fs::remove_dir_all(&self.0);
        }
    }

    #[test]
    fn authored_markdown_keeps_its_prose_and_receives_current_figures_and_sources() {
        let source = "## Sources\n[value](NAME) texts are updated by:\n- `/hardware/sync.rs`\n";
        let built = format!("Older prose. Depth [7](DEPTH).\n\n{source}");
        assert_eq!(
            carried(
                &built,
                "Authored prose. Depth [3](DEPTH), [?](LATER).\n",
                ".md"
            ),
            format!("Authored prose. Depth [7](DEPTH), [?](LATER).\n\n{source}")
        );
        assert_eq!(
            carried(
                "%% span [7](SPAN)\nflowchart LR\n A[old]\n",
                "%% span [3](SPAN)\nflowchart LR\n A[authored [3](SPAN)]\n",
                ".mmd"
            ),
            "%% span [7](SPAN)\nflowchart LR\n A[authored [3](SPAN)]\n"
        );
    }

    #[test]
    fn carry_updates_generated_bytes_and_retains_unknown_rewritten_media() {
        let fixture = Fixture::new();
        let export = "hardware/ledger/purchases.export.csv";
        let protected = "hardware/ledger/notes.csv";
        let built = fixture.built("ledger", export, b"purchase_id,total_minor\nx,17\n");
        let other = fixture.built("ledger", protected, b"stale text\n");
        let protected_file = fixture.tree(protected, b"authored text\n");
        let mut request = CarryRequest {
            root: fixture.0.clone(),
            pairs: vec![(built.clone(), export.into()), (other, protected.into())],
            rewritten: [export, protected].map(str::to_owned).into(),
            ..CarryRequest::default()
        };
        let comparison = carry_request(&request).unwrap();
        assert_eq!(comparison.status, Some(1));
        assert!(!fixture.0.join(export).exists());
        request.write = true;
        let result = carry_request(&request).unwrap();
        assert_eq!(result.status, Some(1));
        assert_eq!(result.written, [export]);
        assert_eq!(
            fs::read(fixture.0.join(export)).unwrap(),
            fs::read(built).unwrap()
        );
        assert_eq!(fs::read(protected_file).unwrap(), b"authored text\n");
        assert!(result.output.contains("notes.csv is read back over"));
        request.pairs.retain(|(_, path)| path == export);
        request.write = false;
        assert_eq!(carry_request(&request).unwrap().status, Some(0));
    }

    #[test]
    fn atomic_splice_keeps_authored_text_and_target_permissions() {
        let fixture = Fixture::new();
        let path = "hardware/part/README.md";
        let built = fixture.built("part", path, b"Old description. [8](WIDTH) mm.\n");
        let target = fixture.tree(path, b"Current description. [2](WIDTH) mm.\n");
        fs::set_permissions(&target, fs::Permissions::from_mode(0o640)).unwrap();
        let request = CarryRequest {
            root: fixture.0.clone(),
            pairs: vec![(built, path.into())],
            rewritten: [path.to_owned()].into(),
            write: true,
            ..CarryRequest::default()
        };
        let result = carry_request(&request).unwrap();
        assert_eq!(result.status, Some(0));
        assert_eq!(result.written, [path]);
        assert_eq!(
            fs::read(&target).unwrap(),
            b"Current description. [8](WIDTH) mm.\n"
        );
        assert_eq!(
            fs::metadata(&target).unwrap().permissions().mode() & 0o777,
            0o640
        );
        assert_eq!(fs::read_dir(target.parent().unwrap()).unwrap().count(), 1);
    }

    #[test]
    fn available_outputs_carry_while_missing_declared_outputs_remain_visible() {
        let fixture = Fixture::new();
        let good = "hardware/good.stl";
        let pairs = vec![
            (fixture.built("good", good, b"new mesh"), good.into()),
            (
                fixture.0.join("results/missing/hardware/missing.stl"),
                "hardware/missing.stl".into(),
            ),
        ];
        let result = carry_request(&CarryRequest {
            root: fixture.0.clone(),
            pairs,
            write: true,
            ..CarryRequest::default()
        })
        .unwrap();
        assert_eq!(result.status, Some(1));
        assert_eq!(result.written, [good]);
        assert_eq!(fs::read(fixture.0.join(good)).unwrap(), b"new mesh");
    }

    #[test]
    fn a_shared_content_blob_carries_to_every_declared_destination() {
        let fixture = Fixture::new();
        let blob = fixture.built("content", "shared-blob", b"same printed solid");
        let paths = ["hardware/left.stl", "hardware/right.stl"];
        let mut request = CarryRequest {
            root: fixture.0.clone(),
            pairs: paths
                .iter()
                .map(|p| (blob.clone(), (*p).to_owned()))
                .collect(),
            write: true,
            scope_only: true,
            ..CarryRequest::default()
        };
        assert_eq!(carry_request(&request).unwrap().pairs, request.pairs);
        assert!(paths.iter().all(|p| !fixture.0.join(p).exists()));
        request.scope_only = false;
        let result = carry_request(&request).unwrap();
        assert_eq!(result.status, Some(0));
        assert_eq!(result.written, paths);
        for path in paths {
            assert_eq!(
                fs::read(fixture.0.join(path)).unwrap(),
                b"same printed solid"
            );
        }
    }

    #[test]
    fn derived_staging_preserves_the_publisher_cohort() {
        let status = b" M hardware/part/README.md\0M  hardware/part/part.stl\0?? hardware/part/new.step.mesh\0A  hardware/part/new.facts.json\0 M hardware/cad-artifacts.json\0";
        let selected = stage_selection(status, &json!({}));
        assert_eq!(selected.paths, [b"hardware/part/README.md".to_vec()]);
        assert_eq!(selected.held.len(), 4);
        assert_eq!(
            selected.staged,
            [
                b"hardware/part/part.stl".to_vec(),
                b"hardware/part/new.facts.json".to_vec()
            ]
        );
        assert_eq!(
            selected.tracked,
            [
                b"hardware/part/part.stl".to_vec(),
                b"hardware/cad-artifacts.json".to_vec()
            ]
        );
    }
}
