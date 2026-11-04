//! Compare the declared cut, live tree bytes and pointer members from raw files.
use crate::bookkeeping_common::*;
use anyhow::{Context, Result, bail};
use hsm_build_data::payload;
use regex::Regex;
use serde_json::{Value, json};
use std::{
    collections::{BTreeMap, BTreeSet},
    fs,
    io::{self, Write},
    path::{Path, PathBuf},
};
fn expected(stdout: &str, failed: &BTreeSet<String>) -> BTreeSet<String> {
    let re = Regex::new(r"/bin/out/([^/]+)/(.+)$").unwrap();
    stdout
        .split_whitespace()
        .filter_map(|line| {
            let m = re.captures(line)?;
            (!failed.contains(&m[1]) && CAD.iter().any(|s| m[2].ends_with(s)))
                .then(|| m[2].to_owned())
        })
        .collect()
}
fn bazel(args: Vec<String>, timeout: u64) -> Result<Value> {
    println!(
        "{}",
        json!({"_hsm_callback":{"kind":"bazel","args":args,"timeout":timeout}})
    );
    io::stdout().flush()?;
    let mut line = String::new();
    io::stdin().read_line(&mut line)?;
    let value: Value = serde_json::from_str(&line)?;
    if let Some(error) = value.get("_hsm_callback_error") {
        bail!("Bazel: {error}")
    }
    value
        .get("_hsm_callback_result")
        .cloned()
        .context("Bazel callback result")
}
fn note(output: &mut String, annotate: bool, kind: &str, message: &str) {
    if annotate {
        *output += &format!("::{kind} title=cut-vs-pointers::{message}\n");
    }
}
fn tree(stale: &[String], compared: usize) -> (String, Vec<Value>, usize) {
    let mut output = String::new();
    if stale.is_empty() {
        output += &format!(
            "\n  THE TREE HOLDS WHAT THIS BUILD CUT for all {compared}, so every card, mass\n  and picture read off it describes the shape the generators now make.\n"
        );
        return (output, vec![], 0);
    }
    output += &format!(
        "\n  BUT {} OF THEM ARE NOT WHAT THE TREE HOLDS:\n",
        stale.len()
    );
    for k in stale.iter().take(20) {
        output += &format!("      {k}\n");
    }
    if stale.len() > 20 {
        output += &format!("      …and {} more\n", stale.len() - 20);
    }
    output += "\n  Every check that reads a solid reads the tree's copy, and these two disagree.\n  WHICH SIDE IS BEHIND IS NOT IN THE BYTES. Before sync_tree runs, the tree holds\n  the fetched bundle or the last hand cut, while bazel-bin holds this build's cut.\n  The latter is only as good as the source that action read:\n  a generator or a module dirty in the worktree cuts bytes no commit reproduces.\n  `git status` over what the cutting run imports is what separates them.\n";
    (
        output,
        vec![json!([
            "warning",
            "cut-vs-pointers",
            format!(
                "{} solids in the tree differ from what this build cut",
                stale.len()
            )
        ])],
        1,
    )
}
fn paths(directory: &Path, out: &mut Vec<PathBuf>) -> Result<()> {
    for e in fs::read_dir(directory)? {
        let e = e?;
        if e.file_type()?.is_dir() {
            paths(&e.path(), out)?;
        } else if e.path().is_file() {
            out.push(e.path());
        }
    }
    Ok(())
}
fn scan(r: &Value) -> Result<Value> {
    let root = Path::new(text(r, "root"));
    let out = Path::new(text(r, "out"));
    let expected = set(&r["expected"]);
    let failed = set(&r["failed"]);
    let pointers = &r["pointers"];
    let re = Regex::new(r"/bin/out/([^/]+)/(.+)$")?;
    let mut files = vec![];
    paths(out, &mut files)?;
    let mut cut: BTreeMap<String, Vec<PathBuf>> = BTreeMap::new();
    let mut skipped = 0;
    for path in files {
        let display = path.to_string_lossy();
        let Some(m) = re.captures(&display) else {
            continue;
        };
        if !expected.contains(&m[2]) {
            continue;
        }
        if failed.contains(&m[1]) {
            skipped += 1;
            continue;
        }
        cut.entry(m[2].to_owned()).or_default().push(path);
    }
    let absent = expected
        .difference(&cut.keys().cloned().collect())
        .cloned()
        .collect::<Vec<_>>();
    let (mut same, mut differ, mut fresh, mut twice, mut stale) =
        (vec![], vec![], vec![], vec![], vec![]);
    let mut hashes = BTreeMap::new();
    if absent.is_empty() {
        for (relative, files) in cut {
            let hashes_here = files
                .iter()
                .map(payload::digest)
                .collect::<Result<BTreeSet<_>>>()?;
            if hashes_here.len() > 1 {
                twice.push(relative);
                continue;
            }
            let here = hashes_here.into_iter().next().unwrap();
            let in_tree = root.join(&relative);
            if in_tree.exists() && payload::digest(in_tree)? != here {
                stale.push(relative.clone());
            }
            if pointers.get(&relative).is_none() {
                fresh.push(relative.clone());
            } else if pointers[&relative].as_str() == Some(here.as_str()) {
                same.push(relative.clone());
            } else {
                differ.push(relative.clone());
            }
            hashes.insert(relative, here);
        }
    }
    let compared = same.len() + differ.len();
    let materialized = compared + fresh.len();
    let steps = same
        .iter()
        .chain(&differ)
        .chain(&fresh)
        .filter(|k| k.ends_with(".step"))
        .count();
    Ok(
        json!({"same":same,"differ":differ,"fresh":fresh,"twice":twice,"stale":stale,"absent":absent,"skipped_failed":skipped,"compared":compared,"materialized":materialized,"steps":steps,"hashes":hashes}),
    )
}
fn main_run(r: &Value) -> Result<Value> {
    let root = Path::new(text(r, "root"));
    let pointer = Path::new(text(r, "pointers_path"));
    let annotate = r["annotate"] == true;
    let assume = r["assume_fresh"] == true;
    let mut output = String::new();
    macro_rules! done{($code:expr)=>{return Ok(json!({"output":output,"status":$code}))}}
    if !pointer.exists() {
        output += &format!(
            "  no pointer file at {}, so there is nothing to compare against\n",
            pointer.strip_prefix(root).unwrap_or(pointer).display()
        );
        done!(2)
    }
    let record: Value = serde_json::from_slice(&fs::read(pointer)?)?;
    let pointers = record.get("solids").cloned().unwrap_or(json!({}));
    if !truthy(&pointers) {
        output += "  the pointer file names no solids, so there is nothing to compare against\n";
        done!(2)
    }
    let labels = labels(text(r, "targets"));
    let failed = text(r, "failed")
        .split(',')
        .map(str::trim)
        .filter(|s| !s.is_empty())
        .map(|s| s.trim_start_matches('/').trim_start_matches(':').to_owned())
        .collect::<BTreeSet<_>>();
    let query = if labels.is_empty() {
        "deps(//:everything)".into()
    } else {
        format!("set({})", labels.join(" "))
    };
    let q = bazel(vec!["cquery".into(), query, "--output=files".into()], 300)?;
    if q["returncode"] != 0 {
        let detail = text(&q, "stderr")
            .lines()
            .find(|s| s.starts_with("ERROR"))
            .map(str::to_owned)
            .unwrap_or_else(|| format!("exit {}", q["returncode"]));
        bail!("SystemExit:   the build graph could not name the expected cut: {detail}")
    }
    let expected = expected(text(&q, "stdout"), &failed);
    if expected.is_empty() {
        output += "  NOTHING DECLARED: the requested target slice has no publishable outputs\n";
        note(
            &mut output,
            annotate,
            "warning",
            "nothing compared: target slice has no CAD outputs",
        );
        done!(3)
    }
    let info = bazel(vec!["info".into(), "bazel-bin".into()], 120).unwrap_or(Value::Null);
    let bin = if info["returncode"] == 0 && !text(&info, "stdout").trim().is_empty() {
        PathBuf::from(text(&info, "stdout").trim())
    } else {
        root.join("bazel-bin")
    };
    let out = bin.join("out");
    if !out.is_dir() {
        output += &format!(
            "  NOTHING CUT: {} does not exist, so this build cut no solids to compare.\n",
            out.display()
        );
        note(
            &mut output,
            annotate,
            "warning",
            "nothing compared: bazel-bin holds no outputs",
        );
        done!(3)
    }
    if !assume {
        let mut args = vec!["build".into(), "--check_up_to_date".into()];
        args.extend(if labels.is_empty() {
            vec!["//:everything".into()]
        } else {
            labels
        });
        let q = bazel(args, 900)?;
        if q["returncode"] != 0 {
            output += "  BAZEL-BIN IS NOT UP TO DATE with this tree, so some of what is sitting\n  there was cut for an older source and a difference would say nothing\n  about the kernels. Build the requested target slice first, or pass\n  --assume-fresh if\n  you know this output tree was written by the build that just ran.\n";
            for line in text(&q, "stderr")
                .lines()
                .filter(|s| s.to_lowercase().contains("not up to date"))
            {
                output += &format!("      {}\n", line.trim());
            }
            note(
                &mut output,
                annotate,
                "warning",
                "bazel-bin is not up to date — nothing compared",
            );
            done!(3)
        }
    }
    let data = scan(
        &json!({"root":root,"out":out,"expected":expected,"failed":failed,"pointers":pointers}),
    )?;
    let absent = strings(&data["absent"]);
    if !absent.is_empty() {
        output += &format!(
            "  INCOMPLETE CUT: {} of {} expected solid(s) are absent\n",
            absent.len(),
            expected.len()
        );
        for path in absent.iter().take(20) {
            output += &format!("      {path}\n");
        }
        note(
            &mut output,
            annotate,
            "error",
            "the build did not materialize every expected solid",
        );
        done!(3)
    }
    let same = strings(&data["same"]);
    let differ = strings(&data["differ"]);
    let fresh = strings(&data["fresh"]);
    let twice = strings(&data["twice"]);
    let stale = strings(&data["stale"]);
    let compared = data["compared"].as_u64().unwrap() as usize;
    let materialized = data["materialized"].as_u64().unwrap() as usize;
    let steps = data["steps"].as_u64().unwrap();
    let skipped = data["skipped_failed"].as_u64().unwrap();
    let failed_line = if skipped > 0 {
        format!(
            "  {skipped} held back as outputs of failed targets: {}\n",
            failed.iter().cloned().collect::<Vec<_>>().join(", ")
        )
    } else {
        String::new()
    };
    if materialized == 0 {
        output += &format!(
            "  NOTHING COMPARED — none of the {} expected solids was found\n  in bazel-bin. This is the absence of a measurement, not agreement.\n",
            expected.len()
        );
        if skipped > 0 {
            output += &format!(
                "  ({skipped} held back as outputs of failed targets: {})\n",
                failed.iter().cloned().collect::<Vec<_>>().join(", ")
            );
        }
        note(
            &mut output,
            annotate,
            "warning",
            "nothing compared: no solid of the pointer file's was cut",
        );
        done!(3)
    }
    output += &format!(
        "  {materialized} of {} expected solids were cut here and hashed ({steps} of them .step)\n",
        expected.len()
    );
    output += &failed_line;
    if !twice.is_empty() {
        output += &format!(
            "  {} cut by two targets that disagree with each other:\n",
            twice.len()
        );
        for path in twice.iter().take(10) {
            output += &format!("      {path}\n");
        }
        note(
            &mut output,
            annotate,
            "error",
            "two actions produced disagreeing bytes for one output",
        );
        done!(3)
    }
    if materialized != expected.len() {
        output += &format!(
            "  INCOMPLETE COMPARISON: {} expected solid(s) were not hashed\n",
            expected.len() - materialized
        );
        note(
            &mut output,
            annotate,
            "error",
            "not every expected solid was compared",
        );
        done!(3)
    }
    if !fresh.is_empty() {
        output += &format!(
            "  {} are new outputs with no historical pointer file member:\n",
            fresh.len()
        );
        for path in fresh.iter().take(20) {
            output += &format!("      {path}\n");
        }
    }
    if !differ.is_empty() {
        output += &format!("  {} DIFFER from the pointer file:\n", differ.len());
        for path in differ.iter().take(20) {
            let old = pointers[path].as_str().unwrap();
            let new = data["hashes"][path].as_str().unwrap();
            output += &format!(
                "      {path}\n        pointer file {}   cut here {}\n",
                &old[..old.len().min(16)],
                &new[..new.len().min(16)]
            );
        }
        if differ.len() > 20 {
            output += &format!("      …and {} more\n", differ.len() - 20);
        }
        output += "\n  THE BYTES DO NOT SAY WHY THEY DIFFER. Either this machine's OpenCASCADE\n  writes different bytes than the one that packed the pointer file, or the pointer file is\n  simply behind the tree's current source for these parts.\n";
        if assume {
            output += "  And a THIRD: --assume-fresh skipped the up-to-date check, so an output\n  bazel kept from an older run has not been ruled out. On this evidence\n  that is the likeliest of the three, not the least.\n";
        } else {
            output += "  bazel-bin is up to date, so a stale cut is excluded — but a pointer file older\n  than the geometry is not.\n";
        }
        output += "  WHAT SEPARATES THE READINGS IS GEOMETRY AND NOT ANOTHER HASH. Load the two\n  cuts and read face count, areas, bounding boxes and edges off them. This\n  repo's two machines are known to write different bytes for solids whose\n  geometry is identical, so `cut here` disagreeing across machines does NOT\n  establish that the kernels disagree.\n  Geometry agrees: the pointer file is simply behind, and a re-point here settles it.\n  Geometry disagrees: the pointer file belongs to whichever machine packs it — a re-point\n  here points at these bytes and the next re-point there points at them back, every lap.\n";
        note(
            &mut output,
            annotate,
            "warning",
            &format!(
                "{} of {compared} solids differ from the pointer file — compare against the other machine's cut hashes to read it",
                differ.len()
            ),
        );
        let (t, notes, _) = tree(&stale, compared);
        output += &t;
        for n in notes {
            note(
                &mut output,
                annotate,
                n[0].as_str().unwrap(),
                n[2].as_str().unwrap(),
            );
        }
        done!(1)
    }
    if !fresh.is_empty() {
        output.push('\n');
        if !same.is_empty() {
            output += &format!(
                "  THE {} EXISTING SOLIDS MATCH THE POINTER FILE; the {} new output(s) are ready to be pointed at.\n",
                same.len(),
                fresh.len()
            );
        } else {
            output +=
                "  EVERY OUTPUT IS NEW; there are no historical pointer file bytes to compare.\n";
        }
        let (t, notes, _) = tree(&stale, materialized);
        output += &t;
        for n in notes {
            note(
                &mut output,
                annotate,
                n[0].as_str().unwrap(),
                n[2].as_str().unwrap(),
            );
        }
        done!(1)
    }
    output += "\n  EVERY SOLID CUT HERE MATCHES THE POINTER FILE, byte for byte. This machine's OpenCASCADE\n  and the one that packed the pointer file agree, so a pointer file is a fact about the geometry\n  rather than about the machine that packed it.\n";
    note(
        &mut output,
        annotate,
        "notice",
        &format!("{compared} solids cut here match the pointer file byte for byte ({steps} .step)"),
    );
    let (t, notes, status) = tree(&stale, materialized);
    output += &t;
    for n in notes {
        note(
            &mut output,
            annotate,
            n[0].as_str().unwrap(),
            n[2].as_str().unwrap(),
        );
    }
    done!(status)
}
pub fn dispatch(op: &str, r: &Value) -> Result<Value> {
    Ok(match op {
        "labels" => json!(labels(text(r, "raw"))),
        "expected" => json!(expected(text(r, "stdout"), &set(&r["failed"]))),
        "sha256" => json!(payload::digest(Path::new(text(r, "path")))?),
        "scan" => return scan(r),
        "tree_verdict" => {
            let (output, notes, status) = tree(
                &strings(&r["stale"]),
                r["compared"].as_u64().unwrap_or(0) as usize,
            );
            json!({"output":output,"notes":notes,"status":status})
        }
        "main" => return main_run(r),
        _ => bail!("unknown cut comparison operation {op}"),
    })
}
