//! Declared Bazel output bytes are compared with the tree and published pointer members.
use anyhow::{Context, Result, bail};
use clap::Parser;
use hsm_build_data::payload;
use serde_json::Value;
use std::{
    collections::{BTreeMap, BTreeSet},
    fs,
    io::Read,
    path::{Path, PathBuf},
    process::{Command, Output, Stdio},
    thread,
    time::{Duration, Instant},
};

const CAD: [&str; 4] = [".step", ".stl", ".glb", ".step.mesh"];
#[derive(Parser)]
#[command(
    name = "hsm-cut-vs-pointers",
    about = "Compare this Bazel target slice's output bytes with the published members"
)]
struct Args {
    #[arg(long)]
    annotate: bool,
    #[arg(long, default_value = "")]
    failed: String,
    #[arg(long)]
    assume_fresh: bool,
    #[arg(long, default_value = "")]
    targets: String,
}
fn labels(raw: &str) -> Vec<String> {
    raw.split(|c: char| c.is_whitespace() || c == ',')
        .filter(|s| !s.is_empty())
        .map(|s| {
            if s.starts_with("//") {
                s.into()
            } else {
                format!("//:{}", s.trim_start_matches(':'))
            }
        })
        .collect::<BTreeSet<_>>()
        .into_iter()
        .collect()
}
fn declared_path(line: &str) -> Option<(&str, &str)> {
    let (_, tail) = line
        .rsplit_once("/bin/out/")
        .or_else(|| line.rsplit_once("/bazel-bin/out/"))?;
    tail.split_once('/')
}
fn expected(stdout: &str, failed: &BTreeSet<String>) -> BTreeSet<String> {
    stdout
        .split_whitespace()
        .filter_map(|line| {
            let (target, path) = declared_path(line)?;
            (!failed.contains(target) && CAD.iter().any(|s| path.ends_with(s))).then(|| path.into())
        })
        .collect()
}
fn bazel(ctx: &crate::ContextData, args: &[String], timeout: Duration) -> Result<Output> {
    let mut command = Command::new("bazel");
    command
        .args(args)
        .current_dir(&ctx.root)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    if let Some(lease) = &ctx.lease {
        lease.apply(&mut command)?;
    }
    let mut child = hsm_run_slots::ipc::spawn(&mut command).context("starting Bazel")?;
    let mut stdout = child.stdout.take().context("Bazel stdout")?;
    let mut stderr = child.stderr.take().context("Bazel stderr")?;
    let out = thread::spawn(move || {
        let mut bytes = vec![];
        stdout.read_to_end(&mut bytes).map(|_| bytes)
    });
    let err = thread::spawn(move || {
        let mut bytes = vec![];
        stderr.read_to_end(&mut bytes).map(|_| bytes)
    });
    let began = Instant::now();
    let mut timed_out = false;
    let status = loop {
        if let Some(status) = child.try_wait()? {
            break status;
        }
        if began.elapsed() >= timeout {
            timed_out = true;
            let _ = child.kill();
            break child.wait()?;
        }
        thread::sleep(Duration::from_millis(25));
    };
    let stdout = out
        .join()
        .map_err(|_| anyhow::anyhow!("reading Bazel stdout panicked"))??;
    let stderr = err
        .join()
        .map_err(|_| anyhow::anyhow!("reading Bazel stderr panicked"))??;
    if timed_out {
        bail!(
            "Bazel {} timed out: {}",
            args.first().map(String::as_str).unwrap_or("command"),
            String::from_utf8_lossy(&stderr)
        );
    }
    Ok(Output {
        status,
        stdout,
        stderr,
    })
}
fn note(output: &mut String, annotate: bool, kind: &str, message: &str) {
    if annotate {
        *output += &format!("::{kind} title=cut-vs-pointers::{message}\n");
    }
}
fn tree(stale: &[String], compared: usize, annotate: bool) -> (String, i32) {
    if stale.is_empty() {
        return (
            format!(
                "\n  THE TREE HOLDS WHAT THIS BUILD CUT for all {compared} compared outputs.\n"
            ),
            0,
        );
    }
    let mut output = format!(
        "\n  {} tree output(s) differ from this build's bytes:\n",
        stale.len()
    );
    for path in stale.iter().take(20) {
        output += &format!("      {path}\n");
    }
    if stale.len() > 20 {
        output += &format!("      …and {} more\n", stale.len() - 20);
    }
    output += "  Geometry checks that read the tree describe those tree bytes. The hashes alone\n  do not establish which copy is current; inspect the producing sources and geometry.\n";
    note(
        &mut output,
        annotate,
        "warning",
        &format!(
            "{} solids in the tree differ from what this build cut",
            stale.len()
        ),
    );
    (output, 1)
}
fn paths(directory: &Path, out: &mut Vec<PathBuf>) -> Result<()> {
    for entry in fs::read_dir(directory)? {
        let entry = entry?;
        if entry.file_type()?.is_dir() {
            paths(&entry.path(), out)?;
        } else if entry.path().is_file() {
            out.push(entry.path());
        }
    }
    Ok(())
}
#[derive(Default, Debug)]
struct Scan {
    same: Vec<String>,
    differ: Vec<String>,
    fresh: Vec<String>,
    twice: Vec<String>,
    stale: Vec<String>,
    absent: Vec<String>,
    skipped_failed: usize,
    hashes: BTreeMap<String, String>,
    steps: usize,
}
impl Scan {
    fn materialized(&self) -> usize {
        self.same.len() + self.differ.len() + self.fresh.len()
    }
    fn compared(&self) -> usize {
        self.same.len() + self.differ.len()
    }
}
fn scan(
    root: &Path,
    out: &Path,
    expected: &BTreeSet<String>,
    failed: &BTreeSet<String>,
    pointers: &Value,
) -> Result<Scan> {
    let mut files = vec![];
    paths(out, &mut files)?;
    let mut cut: BTreeMap<String, Vec<PathBuf>> = BTreeMap::new();
    let mut data = Scan::default();
    for path in files {
        let relative = path.strip_prefix(out)?.to_string_lossy();
        let Some((target, relative)) = relative.split_once('/') else {
            continue;
        };
        if !expected.contains(relative) {
            continue;
        }
        if failed.contains(target) {
            data.skipped_failed += 1;
            continue;
        }
        cut.entry(relative.into()).or_default().push(path);
    }
    data.absent = expected
        .difference(&cut.keys().cloned().collect())
        .cloned()
        .collect();
    if !data.absent.is_empty() {
        return Ok(data);
    }
    for (relative, files) in cut {
        let hashes = files
            .iter()
            .map(payload::digest)
            .collect::<Result<BTreeSet<_>>>()?;
        if hashes.len() > 1 {
            data.twice.push(relative);
            continue;
        }
        let here = hashes.into_iter().next().context("cut output digest")?;
        let in_tree = root.join(&relative);
        if in_tree.exists() && payload::digest(in_tree)? != here {
            data.stale.push(relative.clone());
        }
        if pointers.get(&relative).is_none() {
            data.fresh.push(relative.clone());
        } else if pointers[&relative].as_str() == Some(&here) {
            data.same.push(relative.clone());
        } else {
            data.differ.push(relative.clone());
        }
        if relative.ends_with(".step") {
            data.steps += 1;
        }
        data.hashes.insert(relative, here);
    }
    Ok(data)
}
fn execute(ctx: &crate::ContextData, args: Args) -> Result<(String, i32)> {
    let pointer = ctx.root.join(crate::POINTERS);
    let mut output = String::new();
    macro_rules! done {
        ($code:expr) => {
            return Ok((output, $code))
        };
    }
    if !pointer.exists() {
        output += &format!(
            "  no pointer file at {}, so there is nothing to compare against\n",
            crate::POINTERS
        );
        done!(2);
    }
    let record: Value = serde_json::from_slice(&fs::read(pointer)?)?;
    let pointers = record
        .get("solids")
        .cloned()
        .unwrap_or(serde_json::json!({}));
    if pointers.as_object().is_none_or(|m| m.is_empty()) {
        output += "  the pointer file names no solids, so there is nothing to compare against\n";
        done!(2);
    }
    let labels = labels(&args.targets);
    let failed = args
        .failed
        .split(',')
        .map(str::trim)
        .filter(|s| !s.is_empty())
        .map(|s| s.trim_start_matches('/').trim_start_matches(':').into())
        .collect::<BTreeSet<String>>();
    let query = if labels.is_empty() {
        "deps(//:everything)".into()
    } else {
        format!("set({})", labels.join(" "))
    };
    let q = bazel(
        ctx,
        &["cquery".into(), query, "--output=files".into()],
        Duration::from_secs(300),
    )?;
    if !q.status.success() {
        let stderr = String::from_utf8_lossy(&q.stderr);
        let detail = stderr
            .lines()
            .find(|s| s.starts_with("ERROR"))
            .map(str::to_owned)
            .unwrap_or_else(|| format!("exit {}", q.status));
        bail!("the build graph could not name the expected cut: {detail}");
    }
    let expected = expected(&String::from_utf8_lossy(&q.stdout), &failed);
    if expected.is_empty() {
        output += "  NOTHING DECLARED: the requested target slice has no publishable outputs\n";
        note(
            &mut output,
            args.annotate,
            "warning",
            "nothing compared: target slice has no CAD outputs",
        );
        done!(3);
    }
    let info = bazel(
        ctx,
        &["info".into(), "bazel-bin".into()],
        Duration::from_secs(120),
    );
    let bin = match info {
        Ok(info)
            if info.status.success()
                && !String::from_utf8_lossy(&info.stdout).trim().is_empty() =>
        {
            PathBuf::from(String::from_utf8_lossy(&info.stdout).trim())
        }
        _ => ctx.root.join("bazel-bin"),
    };
    let out = bin.join("out");
    if !out.is_dir() {
        output += &format!(
            "  NOTHING CUT: {} does not exist, so this build cut no solids to compare.\n",
            out.display()
        );
        note(
            &mut output,
            args.annotate,
            "warning",
            "nothing compared: bazel-bin holds no outputs",
        );
        done!(3);
    }
    if !args.assume_fresh {
        let mut command = vec!["build".into(), "--check_up_to_date".into()];
        command.extend(if labels.is_empty() {
            vec!["//:everything".into()]
        } else {
            labels
        });
        let q = bazel(ctx, &command, Duration::from_secs(900))?;
        if !q.status.success() {
            output += "  BAZEL-BIN IS NOT UP TO DATE with this tree, so its bytes do not establish\n  what the current source cuts. Build the requested slice first, or use\n  --assume-fresh immediately after the build that wrote these outputs.\n";
            for line in String::from_utf8_lossy(&q.stderr)
                .lines()
                .filter(|s| s.to_lowercase().contains("not up to date"))
            {
                output += &format!("      {}\n", line.trim());
            }
            note(
                &mut output,
                args.annotate,
                "warning",
                "bazel-bin is not up to date — nothing compared",
            );
            done!(3);
        }
    }
    let data = scan(&ctx.root, &out, &expected, &failed, &pointers)?;
    if !data.absent.is_empty() {
        output += &format!(
            "  INCOMPLETE CUT: {} of {} expected solid(s) are absent\n",
            data.absent.len(),
            expected.len()
        );
        for path in data.absent.iter().take(20) {
            output += &format!("      {path}\n");
        }
        note(
            &mut output,
            args.annotate,
            "error",
            "the build did not materialize every expected solid",
        );
        done!(3);
    }
    let materialized = data.materialized();
    let compared = data.compared();
    if materialized == 0 {
        output += &format!(
            "  NOTHING COMPARED: none of the {} expected solids was hashed.\n",
            expected.len()
        );
        note(
            &mut output,
            args.annotate,
            "warning",
            "nothing compared: no solid of the pointer file's was cut",
        );
        done!(3);
    }
    output += &format!(
        "  {materialized} of {} expected solids were cut here and hashed ({} of them .step)\n",
        expected.len(),
        data.steps
    );
    if data.skipped_failed > 0 {
        output += &format!(
            "  {} held back as outputs of failed targets: {}\n",
            data.skipped_failed,
            failed.iter().cloned().collect::<Vec<_>>().join(", ")
        );
    }
    if !data.twice.is_empty() {
        output += &format!(
            "  {} cut by two targets that disagree with each other:\n",
            data.twice.len()
        );
        for path in data.twice.iter().take(10) {
            output += &format!("      {path}\n");
        }
        note(
            &mut output,
            args.annotate,
            "error",
            "two actions produced disagreeing bytes for one output",
        );
        done!(3);
    }
    if materialized != expected.len() {
        output += &format!(
            "  INCOMPLETE COMPARISON: {} expected solid(s) were not hashed\n",
            expected.len() - materialized
        );
        note(
            &mut output,
            args.annotate,
            "error",
            "not every expected solid was compared",
        );
        done!(3);
    }
    if !data.fresh.is_empty() {
        output += &format!(
            "  {} are new outputs with no historical pointer file member:\n",
            data.fresh.len()
        );
        for path in data.fresh.iter().take(20) {
            output += &format!("      {path}\n");
        }
    }
    if !data.differ.is_empty() {
        output += &format!("  {} DIFFER from the pointer file:\n", data.differ.len());
        for path in data.differ.iter().take(20) {
            let old = pointers[path].as_str().unwrap_or("");
            let new = &data.hashes[path];
            output += &format!(
                "      {path}\n        pointer file {}   cut here {}\n",
                old.chars().take(16).collect::<String>(),
                new.chars().take(16).collect::<String>()
            );
        }
        if data.differ.len() > 20 {
            output += &format!("      …and {} more\n", data.differ.len() - 20);
        }
        output += "\n  The bytes alone do not say whether the geometry changed, the pointer file\n  is behind, or another exporter wrote equivalent geometry differently.\n";
        if args.assume_fresh {
            output += "  --assume-fresh also leaves stale Bazel outputs unexcluded.\n";
        } else {
            output += "  Bazel's up-to-date check excludes stale outputs for this target slice.\n";
        }
        output += "  Compare the geometry before drawing conclusions from differing hashes.\n";
        note(
            &mut output,
            args.annotate,
            "warning",
            &format!(
                "{} of {compared} solids differ from the pointer file — compare their geometry",
                data.differ.len()
            ),
        );
        output += &tree(&data.stale, compared, args.annotate).0;
        done!(1);
    }
    if !data.fresh.is_empty() {
        if data.same.is_empty() {
            output +=
                "\n  EVERY OUTPUT IS NEW; there are no historical pointer file bytes to compare.\n";
        } else {
            output += &format!(
                "\n  THE {} EXISTING SOLIDS MATCH THE POINTER FILE; the {} new output(s) are ready to be pointed at.\n",
                data.same.len(),
                data.fresh.len()
            );
        }
        output += &tree(&data.stale, materialized, args.annotate).0;
        done!(1);
    }
    output += "\n  EVERY SOLID CUT HERE MATCHES THE POINTER FILE, byte for byte.\n";
    note(
        &mut output,
        args.annotate,
        "notice",
        &format!(
            "{compared} solids cut here match the pointer file byte for byte ({} .step)",
            data.steps
        ),
    );
    let (text, status) = tree(&data.stale, materialized, args.annotate);
    output += &text;
    done!(status);
}
pub fn run(ctx: &crate::ContextData, args: &[String]) -> Result<i32> {
    let args = match Args::try_parse_from(
        std::iter::once("hsm-cut-vs-pointers".into()).chain(args.iter().cloned()),
    ) {
        Ok(args) => args,
        Err(error) => {
            let status = error.exit_code();
            error.print()?;
            return Ok(status);
        }
    };
    let (output, status) = execute(ctx, args)?;
    print!("{output}");
    Ok(status)
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;
    #[test]
    fn declared_targets_and_failed_outputs() {
        assert_eq!(
            labels("alpha, :beta //:alpha\n//pkg:gamma"),
            vec!["//:alpha", "//:beta", "//pkg:gamma"]
        );
        let stdout = "bazel-out/darwin-fastbuild/bin/out/alpha/hardware/a.step\nbazel-out/darwin-fastbuild/bin/out/beta/hardware/b.stl\nbazel-out/darwin-fastbuild/bin/out/alpha/report.json\nbazel-out/darwin-fastbuild/bin/out/alpha/hardware/a.step.mesh";
        assert_eq!(
            expected(stdout, &BTreeSet::from(["beta".into()])),
            BTreeSet::from(["hardware/a.step".into(), "hardware/a.step.mesh".into()])
        );
    }
    #[test]
    fn absent_expected_and_disagreeing_producers_are_incomplete() {
        let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("../../../.cache/runs");
        fs::create_dir_all(&root).unwrap();
        let root = root.join(format!(
            "cut-fixture-{}-{}",
            std::process::id(),
            crate::now().to_bits()
        ));
        fs::create_dir(&root).unwrap();
        let out = root.join("bin/out");
        fs::create_dir_all(out.join("first/hardware")).unwrap();
        fs::create_dir_all(out.join("second/hardware")).unwrap();
        fs::write(out.join("first/hardware/a.step"), b"one").unwrap();
        fs::write(out.join("second/hardware/a.step"), b"two").unwrap();
        let data = scan(
            &root,
            &out,
            &BTreeSet::from(["hardware/a.step".into(), "hardware/b.stl".into()]),
            &BTreeSet::new(),
            &json!({}),
        )
        .unwrap();
        assert_eq!(data.absent, vec!["hardware/b.stl"]);
        assert_eq!(data.materialized(), 0);
        let data = scan(
            &root,
            &out,
            &BTreeSet::from(["hardware/a.step".into()]),
            &BTreeSet::new(),
            &json!({}),
        )
        .unwrap();
        assert_eq!(data.twice, vec!["hardware/a.step"]);
        fs::remove_dir_all(root).unwrap();
    }
    #[test]
    fn hash_comparison_separates_new_members_and_tree_staleness() {
        let parent = Path::new(env!("CARGO_MANIFEST_DIR")).join("../../../.cache/runs");
        fs::create_dir_all(&parent).unwrap();
        let root = parent.join(format!(
            "cut-fixture-{}-{}",
            std::process::id(),
            crate::now().to_bits()
        ));
        let out = root.join("bin/out");
        fs::create_dir_all(out.join("alpha/hardware")).unwrap();
        fs::create_dir_all(root.join("hardware")).unwrap();
        fs::write(out.join("alpha/hardware/a.step"), b"current").unwrap();
        fs::write(root.join("hardware/a.step"), b"old").unwrap();
        fs::write(out.join("alpha/hardware/b.stl"), b"new").unwrap();
        let hash = payload::digest(out.join("alpha/hardware/a.step")).unwrap();
        let data = scan(
            &root,
            &out,
            &BTreeSet::from(["hardware/a.step".into(), "hardware/b.stl".into()]),
            &BTreeSet::new(),
            &json!({"hardware/a.step":hash}),
        )
        .unwrap();
        assert_eq!(data.same, vec!["hardware/a.step"]);
        assert_eq!(data.stale, vec!["hardware/a.step"]);
        assert_eq!(data.fresh, vec!["hardware/b.stl"]);
        assert_eq!(tree(&data.stale, data.materialized(), true).1, 1);
        fs::remove_dir_all(root).unwrap();
    }
}
