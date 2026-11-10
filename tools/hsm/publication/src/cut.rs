//! An optional cut comparison reads native producer receipts beside tree and published bytes.
use anyhow::{Context, Result, ensure};
use clap::Parser;
use hsm_build_data::payload;
use serde::Deserialize;
use serde_json::Value;
use std::{
    collections::{BTreeMap, BTreeSet},
    fs,
    path::{Path, PathBuf},
};

const CAD: [&str; 5] = [".step", ".stl", ".glb", ".step.mesh", ".glb.mesh"];
#[derive(Parser)]
#[command(
    name = "hsm-cut-vs-pointers",
    about = "Compare selected native producer output bytes with the tree and published members"
)]
struct Args {
    #[arg(long)]
    annotate: bool,
    #[arg(long, default_value = "")]
    failed: String,
    #[arg(
        long,
        help = "Trust the explicitly supplied completed receipt without probing current inputs"
    )]
    assume_fresh: bool,
    #[arg(long, default_value = "")]
    targets: String,
    #[arg(
        long,
        help = "Read a selected native build's receipt; requires --assume-fresh"
    )]
    receipt: Option<PathBuf>,
}
#[derive(Deserialize)]
struct NativeReceipt {
    schema: u64,
    #[serde(default)]
    selected: BTreeSet<String>,
    targets: BTreeMap<String, TargetReceipt>,
}
#[derive(Deserialize)]
struct TargetReceipt {
    status: String,
    #[serde(default)]
    declared_outputs: Vec<String>,
    #[serde(default)]
    outputs: BTreeMap<String, PathBuf>,
    #[serde(default)]
    file_hashes: BTreeMap<String, String>,
}
fn selectors(raw: &str) -> Vec<String> {
    raw.split(|c: char| c.is_whitespace() || c == ',')
        .filter(|s| !s.is_empty())
        .map(str::to_owned)
        .collect::<BTreeSet<_>>()
        .into_iter()
        .collect()
}
fn target_name(name: &str) -> &str {
    name.strip_prefix("//:")
        .or_else(|| name.strip_prefix(':'))
        .unwrap_or(name)
}
fn publishable(path: &str) -> bool {
    CAD.iter().any(|suffix| path.ends_with(suffix))
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
    output += "  Geometry checks that read the tree describe those tree bytes. Inspect the\n  producing sources and geometry before choosing which copy to publish.\n";
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
#[derive(Default, Debug)]
struct Scan {
    expected: BTreeSet<String>,
    same: Vec<String>,
    differ: Vec<String>,
    fresh: Vec<String>,
    twice: Vec<String>,
    stale: Vec<String>,
    absent: Vec<String>,
    not_current: Vec<String>,
    invalid: Vec<String>,
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
    receipt: &NativeReceipt,
    failed: &BTreeSet<String>,
    pointers: &Value,
) -> Result<Scan> {
    ensure!(
        receipt.schema == 1,
        "unsupported native cut receipt schema {}",
        receipt.schema
    );
    let mut data = Scan::default();
    let mut cut = BTreeMap::<String, Vec<(PathBuf, Option<String>)>>::new();
    for (name, target) in &receipt.targets {
        let declared = target
            .declared_outputs
            .iter()
            .filter(|path| publishable(path))
            .cloned()
            .collect::<BTreeSet<_>>();
        if failed.contains(target_name(name)) {
            data.skipped_failed += declared.len();
            continue;
        }
        data.expected.extend(declared.iter().cloned());
        if declared.is_empty() {
            continue;
        }
        if !matches!(target.status.as_str(), "built" | "cached") {
            data.not_current.push(format!("{name}: {}", target.status));
            continue;
        }
        for relative in declared {
            if let Some(path) = target.outputs.get(&relative) {
                ensure!(
                    path.is_absolute(),
                    "native output receipt is not absolute: {}",
                    path.display()
                );
                if path.is_file() {
                    let expected = target.file_hashes.get(&relative).cloned();
                    cut.entry(relative)
                        .or_default()
                        .push((path.clone(), expected));
                }
            }
        }
    }
    for target in receipt.selected.iter().filter(|target| {
        !receipt.targets.contains_key(*target) && !failed.contains(target_name(target))
    }) {
        data.not_current
            .push(format!("{target}: no completed target receipt"));
    }
    data.absent = data
        .expected
        .difference(&cut.keys().cloned().collect())
        .cloned()
        .collect();
    if !data.not_current.is_empty() || !data.absent.is_empty() {
        return Ok(data);
    }
    for (relative, files) in cut {
        let mut hashes = BTreeSet::new();
        for (path, expected) in &files {
            let hash = payload::digest(path)?;
            if expected.as_ref().is_some_and(|expected| *expected != hash) {
                data.invalid.push(relative.clone());
            }
            hashes.insert(hash);
        }
        if hashes.len() > 1 {
            data.twice.push(relative);
            continue;
        }
        let here = hashes.into_iter().next().context("cut output digest")?;
        let in_tree = root.join(&relative);
        if !in_tree.is_file() || payload::digest(in_tree)? != here {
            data.stale.push(relative.clone());
        }
        if pointers.get(&relative).is_none() {
            data.fresh.push(relative.clone());
        } else if pointers[&relative].as_str() == Some(here.as_str()) {
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
fn compare(
    root: &Path,
    receipt: &NativeReceipt,
    failed: &BTreeSet<String>,
    pointers: &Value,
    annotate: bool,
    assumed: bool,
) -> Result<(String, i32)> {
    let mut output = String::new();
    let data = scan(root, receipt, failed, pointers)?;
    macro_rules! done {
        ($code:expr) => {
            return Ok((output, $code))
        };
    }
    if data.expected.is_empty() {
        output +=
            "  NOTHING DECLARED: the selected native actions name no comparable geometry outputs\n";
        note(
            &mut output,
            annotate,
            "warning",
            "nothing compared: selected actions name no geometry outputs",
        );
        done!(3);
    }
    if !data.not_current.is_empty() {
        output += "  NOT CURRENT: native action receipts cannot establish this source's cut:\n";
        for target in data.not_current.iter().take(20) {
            output += &format!("      {target}\n");
        }
        output +=
            "  Run the selected print build to produce these outputs before comparing them.\n";
        note(
            &mut output,
            annotate,
            "warning",
            "selected native action outputs are not current — nothing compared",
        );
        done!(3);
    }
    if !data.absent.is_empty() {
        output += &format!(
            "  INCOMPLETE CUT: {} of {} expected solid(s) are absent from the recorded native outputs\n",
            data.absent.len(),
            data.expected.len()
        );
        for path in data.absent.iter().take(20) {
            output += &format!("      {path}\n");
        }
        note(
            &mut output,
            annotate,
            "error",
            "the native build did not retain every expected solid",
        );
        done!(3);
    }
    if !data.invalid.is_empty() {
        output += "  INVALID CUT: retained output bytes differ from their native receipt:\n";
        for path in data.invalid.iter().take(20) {
            output += &format!("      {path}\n");
        }
        note(
            &mut output,
            annotate,
            "error",
            "native output bytes differ from their recorded content identity",
        );
        done!(3);
    }
    if !data.twice.is_empty() {
        output += &format!(
            "  {} output(s) have disagreeing producer bytes:\n",
            data.twice.len()
        );
        for path in data.twice.iter().take(10) {
            output += &format!("      {path}\n");
        }
        note(
            &mut output,
            annotate,
            "error",
            "two native actions produced disagreeing bytes for one output",
        );
        done!(3);
    }
    let materialized = data.materialized();
    let compared = data.compared();
    if materialized == 0 {
        output += "  NOTHING COMPARED: no selected native geometry output was hashed.\n";
        note(
            &mut output,
            annotate,
            "warning",
            "nothing compared: no recorded output bytes",
        );
        done!(3);
    }
    output += &format!(
        "  {materialized} of {} expected solids read from native producer outputs and hashed ({} .step)\n",
        data.expected.len(),
        data.steps
    );
    if data.skipped_failed > 0 {
        output += &format!(
            "  {} output(s) excluded with the explicitly failed targets\n",
            data.skipped_failed
        );
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
        output += "\n  The bytes alone do not say whether the geometry changed or its published\n  pointer is behind. Compare the geometry before choosing what to publish.\n";
        if assumed {
            output += "  This explicitly supplied receipt is read as recorded; its source currentness\n  was not queried.\n";
        } else {
            output += "  The native cache probe establishes currentness for the selected inputs.\n";
        }
        note(
            &mut output,
            annotate,
            "warning",
            &format!(
                "{} of {compared} solids differ from the pointer file — compare their geometry",
                data.differ.len()
            ),
        );
        output += &tree(&data.stale, compared, annotate).0;
        done!(1);
    }
    if !data.fresh.is_empty() {
        if data.same.is_empty() {
            output +=
                "\n  EVERY OUTPUT IS NEW; there are no historical pointer file bytes to compare.\n";
        } else {
            output += &format!(
                "\n  THE {} EXISTING SOLIDS MATCH THE POINTER FILE; {} new output(s) are ready to be pointed at.\n",
                data.same.len(),
                data.fresh.len()
            );
        }
        output += &tree(&data.stale, materialized, annotate).0;
        done!(1);
    }
    output += "\n  EVERY SOLID CUT HERE MATCHES THE POINTER FILE, byte for byte.\n";
    note(
        &mut output,
        annotate,
        "notice",
        &format!(
            "{compared} solids cut here match the pointer file byte for byte ({} .step)",
            data.steps
        ),
    );
    let (text, status) = tree(&data.stale, materialized, annotate);
    output += &text;
    done!(status);
}
fn execute(ctx: &crate::ContextData, args: Args) -> Result<(String, i32)> {
    let driver = std::env::var("HSM_PRINT_BUILD").unwrap_or_else(|_| "hsm-print-build".into());
    execute_with(ctx, args, &driver)
}
fn execute_with(ctx: &crate::ContextData, args: Args, driver: &str) -> Result<(String, i32)> {
    ensure!(
        args.receipt.is_some() == args.assume_fresh,
        "--receipt and --assume-fresh are used together for an explicitly recorded cut"
    );
    ensure!(
        args.receipt.is_none() || args.targets.trim().is_empty(),
        "a supplied receipt already identifies its selected build; select --targets when producing that receipt"
    );
    let pointer = ctx.root.join(crate::POINTERS);
    if !pointer.exists() {
        return Ok((
            format!(
                "  no pointer file at {}, so there is nothing to compare against\n",
                crate::POINTERS
            ),
            2,
        ));
    }
    let record: Value = serde_json::from_slice(&fs::read(pointer)?)?;
    let pointers = record
        .get("solids")
        .cloned()
        .unwrap_or(serde_json::json!({}));
    if pointers.as_object().is_none_or(|m| m.is_empty()) {
        return Ok((
            "  the pointer file names no solids, so there is nothing to compare against\n".into(),
            2,
        ));
    }
    let failed = selectors(&args.failed)
        .into_iter()
        .map(|name| target_name(&name).to_owned())
        .collect::<BTreeSet<_>>();
    if let Some(path) = args.receipt {
        let path = if path.is_absolute() {
            path
        } else {
            ctx.root.join(path)
        };
        let receipt = serde_json::from_slice::<NativeReceipt>(
            &fs::read(&path)
                .with_context(|| format!("reading native cut receipt {}", path.display()))?,
        )?;
        return compare(&ctx.root, &receipt, &failed, &pointers, args.annotate, true);
    }
    let work = crate::Work::new(&ctx.root)?;
    let mut command = vec![
        "--root".into(),
        ctx.root.to_string_lossy().into_owned(),
        "--no-publish".into(),
        "--check-current".into(),
        "--run-dir".into(),
        work.path.to_string_lossy().into_owned(),
        "--".into(),
    ];
    command.extend(selectors(&args.targets));
    let result = ctx
        .command(driver, &command)
        .context("read native action currentness")?;
    let path = work.path.join("receipt.json");
    let bytes = fs::read(&path).with_context(|| {
        format!(
            "native cache probe wrote no output receipt ({}): {}",
            result.status,
            String::from_utf8_lossy(&result.stderr)
        )
    })?;
    let receipt = serde_json::from_slice::<NativeReceipt>(&bytes)
        .context("native cache probe output receipt")?;
    compare(
        &ctx.root,
        &receipt,
        &failed,
        &pointers,
        args.annotate,
        false,
    )
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
    fn fixture() -> crate::Work {
        crate::Work::new(
            Path::new(env!("CARGO_MANIFEST_DIR"))
                .ancestors()
                .nth(3)
                .unwrap(),
        )
        .unwrap()
    }
    fn receipt(targets: Value) -> NativeReceipt {
        serde_json::from_value(json!({"schema":1,"targets":targets})).unwrap()
    }
    #[test]
    fn selectors_and_failed_aliases_keep_native_names() {
        assert_eq!(
            selectors("alpha, //:beta\n:alpha"),
            vec!["//:beta", ":alpha", "alpha"]
        );
        assert_eq!(target_name("//:alpha"), "alpha");
        assert_eq!(target_name("alpha"), "alpha");
    }
    #[test]
    fn not_current_and_missing_outputs_cannot_read_as_agreement() {
        let work = fixture();
        let native = receipt(
            json!({"part":{"status":"not-current","declared_outputs":["hardware/a.step"],"outputs":{}}}),
        );
        let (text, status) = compare(
            &work.path,
            &native,
            &BTreeSet::new(),
            &json!({"hardware/a.step":"hash"}),
            true,
            false,
        )
        .unwrap();
        assert_eq!(status, 3);
        assert!(text.contains("NOT CURRENT"));
        let native = receipt(
            json!({"part":{"status":"cached","declared_outputs":["hardware/a.step"],"outputs":{"hardware/a.step":work.path.join("absent")}}}),
        );
        let (text, status) = compare(
            &work.path,
            &native,
            &BTreeSet::new(),
            &json!({}),
            false,
            false,
        )
        .unwrap();
        assert_eq!(status, 3);
        assert!(text.contains("INCOMPLETE CUT"));
    }
    #[test]
    fn immutable_producer_bytes_are_distinct_from_carried_tree_and_new_members() {
        let work = fixture();
        fs::create_dir_all(work.path.join("hardware")).unwrap();
        let a = work.path.join("cached-a");
        let b = work.path.join("cached-b");
        fs::write(&a, b"current").unwrap();
        fs::write(&b, b"new").unwrap();
        fs::write(work.path.join("hardware/a.step"), b"old tree").unwrap();
        fs::write(work.path.join("hardware/b.glb.mesh"), b"new").unwrap();
        let native = receipt(
            json!({"part":{"status":"cached","declared_outputs":["hardware/a.step","hardware/b.glb.mesh"],"outputs":{"hardware/a.step":a,"hardware/b.glb.mesh":b}}}),
        );
        let pointers = json!({"hardware/a.step":payload::digest(&a).unwrap()});
        let data = scan(&work.path, &native, &BTreeSet::new(), &pointers).unwrap();
        assert_eq!(data.same, vec!["hardware/a.step"]);
        assert_eq!(data.stale, vec!["hardware/a.step"]);
        assert_eq!(data.fresh, vec!["hardware/b.glb.mesh"]);
        assert_eq!(
            compare(
                &work.path,
                &native,
                &BTreeSet::new(),
                &pointers,
                false,
                false
            )
            .unwrap()
            .1,
            1
        );
    }
    #[test]
    fn failed_exclusion_and_disagreeing_producers_remain_explicit() {
        let work = fixture();
        let a = work.path.join("a");
        let b = work.path.join("b");
        fs::write(&a, b"one").unwrap();
        fs::write(&b, b"two").unwrap();
        let native = receipt(
            json!({"first":{"status":"built","declared_outputs":["hardware/a.step"],"outputs":{"hardware/a.step":a}},"second":{"status":"built","declared_outputs":["hardware/a.step"],"outputs":{"hardware/a.step":b}}}),
        );
        assert_eq!(
            compare(
                &work.path,
                &native,
                &BTreeSet::new(),
                &json!({}),
                false,
                true
            )
            .unwrap()
            .1,
            3
        );
        let pointers = json!({"hardware/a.step":payload::digest(&a).unwrap()});
        let data = scan(
            &work.path,
            &native,
            &BTreeSet::from(["second".into()]),
            &pointers,
        )
        .unwrap();
        assert_eq!(data.same, vec!["hardware/a.step"]);
        assert_eq!(data.skipped_failed, 1);
    }
    #[test]
    fn explicit_receipt_comparison_starts_no_driver() {
        let work = fixture();
        let source = work.path.join("cache-object");
        fs::write(&source, b"native output").unwrap();
        fs::create_dir_all(work.path.join("hardware")).unwrap();
        fs::write(work.path.join("hardware/a.step"), b"native output").unwrap();
        let hash = payload::digest(&source).unwrap();
        fs::write(
            work.path.join(crate::POINTERS),
            serde_json::to_vec(&json!({"solids":{"hardware/a.step":hash}})).unwrap(),
        )
        .unwrap();
        let path = work.path.join("receipt.json");
        fs::write(&path,serde_json::to_vec(&json!({"schema":1,"targets":{"part":{"status":"cached","declared_outputs":["hardware/a.step"],"outputs":{"hardware/a.step":source}}}})).unwrap()).unwrap();
        let ctx = crate::ContextData::with_config(&work.path, json!({}), json!({})).unwrap();
        let args = Args {
            annotate: false,
            failed: String::new(),
            assume_fresh: true,
            targets: String::new(),
            receipt: Some(path),
        };
        assert_eq!(execute(&ctx, args).unwrap().1, 0);
    }
    #[test]
    fn incomplete_selected_receipts_and_changed_recorded_bytes_are_not_agreement() {
        let work = fixture();
        let source = work.path.join("blob");
        fs::write(&source, b"later bytes").unwrap();
        let mut native = receipt(
            json!({"part":{"status":"cached","declared_outputs":["hardware/a.step"],"outputs":{"hardware/a.step":source},"file_hashes":{"hardware/a.step":"earlier hash"}}}),
        );
        let (output, status) = compare(
            &work.path,
            &native,
            &BTreeSet::new(),
            &json!({}),
            false,
            true,
        )
        .unwrap();
        assert_eq!(status, 3);
        assert!(output.contains("INVALID CUT"));
        native.selected.insert("missing-part".into());
        let (output, status) = compare(
            &work.path,
            &native,
            &BTreeSet::new(),
            &json!({}),
            false,
            true,
        )
        .unwrap();
        assert_eq!(status, 3);
        assert!(output.contains("no completed target receipt"));
    }
    #[test]
    fn selected_comparison_requests_only_a_cache_probe_without_publication() {
        use std::os::unix::fs::PermissionsExt;
        let work = fixture();
        fs::create_dir_all(work.path.join("hardware")).unwrap();
        let output = work.path.join("producer-output");
        fs::write(&output, b"native bytes").unwrap();
        fs::write(work.path.join("hardware/a.step"), b"native bytes").unwrap();
        let hash = payload::digest(&output).unwrap();
        fs::write(
            work.path.join(crate::POINTERS),
            serde_json::to_vec(&json!({"solids":{"hardware/a.step":hash}})).unwrap(),
        )
        .unwrap();
        fs::write(work.path.join("fake-receipt.json"),serde_json::to_vec(&json!({"schema":1,"selected":["part"],"targets":{"part":{"status":"cached","declared_outputs":["hardware/a.step"],"outputs":{"hardware/a.step":output}}}})).unwrap()).unwrap();
        let driver = work.path.join("cache-probe");
        fs::write(&driver,"#!/bin/sh\nset -eu\nno_publish=false\ncheck_current=false\nwhile [ \"$#\" -gt 0 ]; do\n case \"$1\" in\n --root) shift; root_arg=\"$1\";;\n --no-publish) no_publish=true;;\n --check-current) check_current=true;;\n --run-dir) shift; run_dir=\"$1\";;\n --) shift; break;;\n *) exit 9;;\n esac\n shift\ndone\n[ \"$no_publish\" = true ] && [ \"$check_current\" = true ]\ncp \"$root_arg/fake-receipt.json\" \"$run_dir/receipt.json\"\nprintf '%s\\n' \"$@\" > \"$root_arg/selectors.txt\"\n").unwrap();
        fs::set_permissions(&driver, fs::Permissions::from_mode(0o755)).unwrap();
        let ctx = crate::ContextData::with_config(&work.path, json!({}), json!({})).unwrap();
        let args = Args {
            annotate: false,
            failed: String::new(),
            assume_fresh: false,
            targets: "//:part".into(),
            receipt: None,
        };
        assert_eq!(
            execute_with(&ctx, args, driver.to_str().unwrap())
                .unwrap()
                .1,
            0
        );
        assert_eq!(
            fs::read_to_string(work.path.join("selectors.txt")).unwrap(),
            "//:part\n"
        );
    }
}
