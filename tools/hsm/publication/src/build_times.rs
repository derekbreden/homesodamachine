//! Completed native print-build receipts reach the site's timing history without starting a build.
use anyhow::{Context, Result};
use clap::Parser;
use fs2::FileExt;
use serde_json::{Value, json};
use std::{collections::BTreeMap, fs, path::Path, thread, time::Duration};

const REL: &str = "web/public/build-times.json";
const LOCK: &str = ".cache/build-times.lock";
const MSG: &str = "build times: completed native print builds";
const KEEP: usize = 200;
#[derive(Parser)]
#[command(
    name = "hsm-build-times",
    about = "Put completed native print-build timings on the site without starting a build"
)]
struct Args {
    #[arg(long)]
    check: bool,
}

fn utc_timestamp(nanoseconds: u64) -> Option<String> {
    let seconds: libc::time_t = (nanoseconds / 1_000_000_000).try_into().ok()?;
    let mut output = std::mem::MaybeUninit::<libc::tm>::uninit();
    if unsafe { libc::gmtime_r(&seconds, output.as_mut_ptr()) }.is_null() {
        return None;
    }
    let time = unsafe { output.assume_init() };
    let fraction = nanoseconds % 1_000_000_000;
    let fraction = if fraction == 0 {
        String::new()
    } else {
        format!(".{fraction:09}").trim_end_matches('0').to_owned()
    };
    Some(format!(
        "{:04}-{:02}-{:02}T{:02}:{:02}:{:02}{fraction}Z",
        time.tm_year + 1900,
        time.tm_mon + 1,
        time.tm_mday,
        time.tm_hour,
        time.tm_min,
        time.tm_sec
    ))
}
fn row(receipt: &Value) -> Option<Value> {
    if receipt["completed"] != true
        || receipt["full_build"] != true
        || receipt["check_current"] == true
    {
        return None;
    }
    let id = receipt["run_id"].as_str().filter(|id| !id.is_empty())?;
    let started_ns = receipt["started_unix_ns"]
        .as_u64()
        .or_else(|| receipt["started_unix_ns"].as_str()?.parse().ok())?;
    let started = utc_timestamp(started_ns)?;
    let seconds = receipt["wall_seconds"]
        .as_f64()
        .filter(|seconds| seconds.is_finite() && *seconds >= 0.)?;
    let commit = receipt["source_commit"].as_str()?;
    let commit = commit.get(..9).unwrap_or(commit);
    let finished = receipt["success"].as_bool()?;
    let targets = receipt["targets"].as_object()?;
    let reran = targets
        .values()
        .filter(|target| target["status"] == "built")
        .count();
    Some(
        json!({"id":format!("native:{id}"),"started":started,"commit":commit,"seconds":(seconds*10.).round_ties_even()/10.,"reran":reran,"steps":targets.len(),"finished":finished,"builder":"hsm-print-build"}),
    )
}
fn full_builds_at(base: &Path) -> Vec<Value> {
    let mut paths = fs::read_dir(base)
        .into_iter()
        .flatten()
        .filter_map(|entry| entry.ok())
        .filter(|entry| entry.file_type().is_ok_and(|kind| kind.is_dir()))
        .map(|entry| entry.path().join("result.json"))
        .collect::<Vec<_>>();
    paths.sort();
    paths
        .into_iter()
        .filter_map(|path| {
            let bytes = fs::read(path).ok()?;
            row(&serde_json::from_slice::<Value>(&bytes).ok()?)
        })
        .collect()
}
fn merge_rows(existing: &Value, rows: Vec<Value>) -> Value {
    let mut by_id = BTreeMap::new();
    for row in existing
        .get("builds")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
    {
        if let Some(id) = row.get("id").and_then(Value::as_str) {
            by_id.insert(id.to_string(), row.clone());
        }
    }
    for row in rows {
        if let Some(id) = row.get("id").and_then(Value::as_str) {
            by_id.entry(id.to_string()).or_insert(row);
        }
    }
    let mut builds = by_id.into_values().collect::<Vec<_>>();
    builds.sort_by(|a, b| {
        a["started"]
            .as_str()
            .unwrap_or("")
            .cmp(b["started"].as_str().unwrap_or(""))
    });
    if builds.len() > KEEP {
        builds.drain(..builds.len() - KEEP);
    }
    json!({"builds":builds})
}
fn committed(ctx: &crate::ContextData) -> Result<bool> {
    Ok(ctx
        .git(&["ls-files", "--error-unmatch", REL])?
        .status
        .success()
        && ctx
            .git(&["diff", "--quiet", "HEAD", "--", REL])?
            .status
            .success())
}
fn land(ctx: &crate::ContextData) -> Result<i32> {
    for attempt in 0..3 {
        let _ = ctx.git(&["add", REL])?;
        if ctx
            .git(&["commit", "--no-verify", "--only", "-m", MSG, "--", REL])?
            .status
            .success()
        {
            return Ok(0);
        }
        thread::sleep(Duration::from_millis(1500 * (attempt + 1)));
    }
    eprintln!("  build times did not commit; the next commit's run tries again");
    Ok(1)
}
pub fn run(ctx: &crate::ContextData, args: &[String]) -> Result<i32> {
    let args = match Args::try_parse_from(
        std::iter::once("hsm-build-times".into()).chain(args.iter().cloned()),
    ) {
        Ok(args) => args,
        Err(error) => {
            let status = error.exit_code();
            error.print()?;
            return Ok(status);
        }
    };
    let rows = full_builds_at(&ctx.root.join(".cache/runs"));
    if args.check {
        let mut rows = rows;
        rows.sort_by(|a, b| a["started"].as_str().cmp(&b["started"].as_str()));
        for row in rows {
            println!(
                "  {}  {:>7.1} s  reran {}{}",
                row["started"].as_str().unwrap_or(""),
                row["seconds"].as_f64().unwrap_or(0.),
                row["reran"],
                if row["finished"] == true {
                    ""
                } else {
                    "  (failed)"
                }
            );
        }
        return Ok(0);
    }
    let lock = ctx.root.join(LOCK);
    fs::create_dir_all(lock.parent().context("build timing lock parent")?)?;
    let held = fs::OpenOptions::new()
        .create(true)
        .write(true)
        .truncate(false)
        .open(lock)?;
    if let Err(error) = held.try_lock_exclusive() {
        if error.kind() == std::io::ErrorKind::WouldBlock {
            return Ok(0);
        }
        return Err(error.into());
    }
    let output = ctx.root.join(REL);
    let existing = fs::read(&output)
        .ok()
        .and_then(|bytes| serde_json::from_slice(&bytes).ok())
        .unwrap_or(Value::Null);
    let text = render(&merge_rows(&existing, rows))?;
    let same = fs::read_to_string(&output)
        .ok()
        .is_some_and(|value| value == text);
    if same && committed(ctx)? {
        return Ok(0);
    }
    if !same {
        fs::write(output, text)?;
    }
    land(ctx)
}
fn render(data: &Value) -> Result<String> {
    let rows = data["builds"]
        .as_array()
        .context("build timing rows")?
        .iter()
        .map(|row| {
            let mut names = vec![
                "id", "started", "commit", "seconds", "reran", "steps", "finished",
            ];
            if row.get("builder").is_some() {
                names.push("builder");
            }
            let fields = names
                .into_iter()
                .map(|key| {
                    Ok(format!(
                        "      {}: {}",
                        serde_json::to_string(key)?,
                        serde_json::to_string(&row[key])?
                    ))
                })
                .collect::<Result<Vec<_>>>()?;
            Ok(format!("    {{\n{}\n    }}", fields.join(",\n")))
        })
        .collect::<Result<Vec<_>>>()?;
    Ok(if rows.is_empty() {
        "{\n  \"builds\": []\n}\n".into()
    } else {
        format!("{{\n  \"builds\": [\n{}\n  ]\n}}\n", rows.join(",\n"))
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    fn receipt() -> Value {
        json!({"run_id":"run","completed":true,"full_build":true,"started_unix_ns":1_794_342_344_123_456_789u64,"source_commit":"head","success":true,"wall_seconds":12.345,"targets":{"a":{"status":"built","seconds":8.},"b":{"status":"cached","seconds":0.2},"c":{"status":"built","seconds":4.}}})
    }
    #[test]
    fn utc_dates_use_the_recorded_start_instead_of_filesystem_times() {
        assert_eq!(utc_timestamp(0).unwrap(), "1970-01-01T00:00:00Z");
        assert_eq!(
            utc_timestamp(1_000_000_001).unwrap(),
            "1970-01-01T00:00:01.000000001Z"
        );
        assert_eq!(
            utc_timestamp(86_400_000_000_000).unwrap(),
            "1970-01-02T00:00:00Z"
        );
    }
    #[test]
    fn native_rows_count_actual_actions_and_preserve_run_outcome() {
        let mut source = receipt();
        let got = row(&source).unwrap();
        assert_eq!(got["id"], "native:run");
        assert_eq!(got["reran"], 2);
        assert_eq!(got["steps"], 3);
        assert_eq!(got["seconds"], 12.3);
        assert_eq!(got["builder"], "hsm-print-build");
        source["success"] = json!(false);
        assert_eq!(row(&source).unwrap()["finished"], false);
    }
    #[test]
    fn partial_and_currentness_queries_are_not_completed_full_builds() {
        let mut source = receipt();
        source["completed"] = json!(false);
        assert!(row(&source).is_none());
        source["completed"] = json!(true);
        source["full_build"] = json!(false);
        assert!(row(&source).is_none());
        source["full_build"] = json!(true);
        source["check_current"] = json!(true);
        assert!(row(&source).is_none());
        assert!(row(&json!({})).is_none());
    }
    #[test]
    fn committed_history_stands_and_old_rows_fall_out_of_the_site_list() {
        let existing = json!({"builds":[{"id":"same","started":"0000","seconds":1.5}]});
        let rows = (0..KEEP + 1)
            .map(|n| json!({"id":format!("{n:04}"),"started":format!("{n:04}"),"seconds":n}))
            .chain([json!({"id":"same","started":"9999","seconds":900})])
            .collect();
        let got = merge_rows(&existing, rows);
        assert_eq!(got["builds"].as_array().unwrap().len(), KEEP);
        assert_eq!(got["builds"][0]["started"], "0001");
        assert!(
            !got["builds"]
                .as_array()
                .unwrap()
                .iter()
                .any(|row| row["id"] == "same")
        );
        let got = merge_rows(
            &existing,
            vec![json!({"id":"same","started":"9999","seconds":900})],
        );
        assert_eq!(got["builds"][0]["seconds"], 1.5);
    }
    #[test]
    fn malformed_or_unfinished_receipts_are_ignored_without_writing() {
        let work = crate::Work::new(
            Path::new(env!("CARGO_MANIFEST_DIR"))
                .ancestors()
                .nth(3)
                .unwrap(),
        )
        .unwrap();
        let root = &work.path;
        for name in ["native-full", "native-partial", "unfinished"] {
            fs::create_dir(root.join(name)).unwrap();
        }
        fs::write(
            root.join("native-full/result.json"),
            serde_json::to_vec(&receipt()).unwrap(),
        )
        .unwrap();
        let mut partial = receipt();
        partial["full_build"] = json!(false);
        fs::write(
            root.join("native-partial/result.json"),
            serde_json::to_vec(&partial).unwrap(),
        )
        .unwrap();
        fs::write(root.join("unfinished/result.json"), b"{").unwrap();
        let rows = full_builds_at(root);
        assert_eq!(rows.len(), 1);
        assert_eq!(rows[0]["id"], "native:run");
        assert!(!root.join(REL).exists());
        assert!(!root.join(LOCK).exists());
    }
    #[test]
    fn site_json_keeps_historical_rows_and_native_attribution() {
        let historical = json!({"id":"old","started":"date","commit":"head","seconds":1.0,"reran":0,"steps":null,"finished":true});
        let native = row(&receipt()).unwrap();
        let text = render(&json!({"builds":[historical.clone(),native]})).unwrap();
        assert!(text.contains("\"seconds\": 1.0"));
        let value: Value = serde_json::from_str(&text).unwrap();
        assert_eq!(value["builds"][0], historical);
        assert_eq!(value["builds"][1]["builder"], "hsm-print-build");
    }
}
