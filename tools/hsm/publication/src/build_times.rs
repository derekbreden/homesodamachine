//! Recorded Bazel full-build timings reach the site's list without starting a build.
use anyhow::{Context, Result};
use clap::Parser;
use fs2::FileExt;
use hsm_build_data::publication::archive;
use serde_json::{Value, json};
use std::{
    collections::{BTreeMap, BTreeSet},
    fs,
    path::{Path, PathBuf},
    thread,
    time::Duration,
};

const REL: &str = "web/public/build-times.json";
const LOCK: &str = ".cache/build-times.lock";
const MSG: &str = "build times: the full builds Bazel's records hold";
const TARGET: &str = "//:everything";
const KEEP: usize = 200;
#[derive(Parser)]
#[command(
    name = "hsm-build-times",
    about = "Put recorded full-build timings on the site without starting a build"
)]
struct Args {
    #[arg(long)]
    check: bool,
}

fn md5(bytes: &[u8]) -> String {
    let mut input = bytes.to_vec();
    let bits = (input.len() as u64).wrapping_mul(8);
    input.push(0x80);
    while input.len() % 64 != 56 {
        input.push(0);
    }
    input.extend_from_slice(&bits.to_le_bytes());
    let mut state = [0x67452301_u32, 0xefcdab89, 0x98badcfe, 0x10325476];
    let shifts = [7, 12, 17, 22, 5, 9, 14, 20, 4, 11, 16, 23, 6, 10, 15, 21];
    for block in input.chunks_exact(64) {
        let words = block
            .chunks_exact(4)
            .map(|v| u32::from_le_bytes(v.try_into().unwrap()))
            .collect::<Vec<_>>();
        let [mut a, mut b, mut c, mut d] = state;
        for i in 0..64 {
            let (f, g, shift) = match i {
                0..=15 => ((b & c) | (!b & d), i, shifts[i % 4]),
                16..=31 => ((d & b) | (!d & c), (5 * i + 1) % 16, shifts[4 + i % 4]),
                32..=47 => (b ^ c ^ d, (3 * i + 5) % 16, shifts[8 + i % 4]),
                _ => (c ^ (b | !d), (7 * i) % 16, shifts[12 + i % 4]),
            };
            let constant = ((i as f64 + 1.).sin().abs() * 4294967296.).floor() as u32;
            let next = b.wrapping_add(
                a.wrapping_add(f)
                    .wrapping_add(constant)
                    .wrapping_add(words[g])
                    .rotate_left(shift),
            );
            a = d;
            d = c;
            c = b;
            b = next;
        }
        for (old, add) in state.iter_mut().zip([a, b, c, d]) {
            *old = old.wrapping_add(add);
        }
    }
    state
        .into_iter()
        .flat_map(u32::to_le_bytes)
        .map(|b| format!("{b:02x}"))
        .collect()
}
fn output_base(ctx: &crate::ContextData) -> Result<PathBuf> {
    let home =
        std::env::var_os("HOME").context("home directory for Bazel's recorded output base")?;
    let user = ["LOGNAME", "USER", "LNAME", "USERNAME"]
        .iter()
        .find_map(|k| std::env::var(k).ok().filter(|s| !s.is_empty()))
        .unwrap_or_else(|| {
            ctx.command("id", &["-un".into()])
                .ok()
                .map(|r| String::from_utf8_lossy(&r.stdout).trim().into())
                .unwrap_or_default()
        });
    Ok(PathBuf::from(home)
        .join("Library/Caches/bazel")
        .join(format!("_bazel_{user}"))
        .join(md5(ctx.root.to_string_lossy().as_bytes())))
}
#[derive(Clone, Debug, PartialEq, Eq)]
struct CommandRecord {
    command: String,
    targets: Vec<String>,
    exit: String,
}
fn parse_commands(text: &str, found: &mut BTreeMap<String, CommandRecord>) {
    let mut args: Option<Vec<String>> = None;
    let mut current: Option<String> = None;
    for line in text.lines() {
        if let Some(tail) = line
            .split_once("GrpcServerImpl.executeCommand] [")
            .and_then(|(_, v)| v.trim_end().strip_suffix(']'))
        {
            args = Some(tail.split(", ").map(str::to_owned).collect());
            current = None;
        } else if let Some(tail) = line.split_once("Build identifier: ").map(|(_, v)| v) {
            let Some(args) = args.as_ref().filter(|v| !v.is_empty()) else {
                continue;
            };
            let id = tail.chars().take(36).collect::<String>();
            if id.len() != 36
                || !id
                    .bytes()
                    .all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b) || b == b'-')
            {
                continue;
            }
            let after = args
                .iter()
                .position(|s| s.starts_with("--client_cwd="))
                .unwrap_or(0)
                + 1;
            found.insert(
                id.clone(),
                CommandRecord {
                    command: args[0].clone(),
                    targets: args
                        .iter()
                        .skip(after)
                        .filter(|s| !s.starts_with('-'))
                        .cloned()
                        .collect(),
                    exit: "SUCCESS".into(),
                },
            );
            current = Some(id);
        } else if let Some(tail) = line
            .split_once("Exit status was DetailedExitCode{exitCode=")
            .map(|(_, v)| v)
        {
            if let Some(record) = current.as_ref().and_then(|id| found.get_mut(id)) {
                record.exit = tail
                    .chars()
                    .take_while(|c| c.is_ascii_uppercase() || *c == '_')
                    .collect();
            }
        }
    }
}
fn commands(base: &Path) -> BTreeMap<String, CommandRecord> {
    let mut found = BTreeMap::new();
    let mut logs = fs::read_dir(base)
        .into_iter()
        .flatten()
        .filter_map(|e| e.ok())
        .filter(|e| e.file_name().to_string_lossy().starts_with("java.log."))
        .map(|e| e.path())
        .collect::<Vec<_>>();
    logs.sort();
    for path in logs {
        if let Ok(bytes) = fs::read(path) {
            parse_commands(&String::from_utf8_lossy(&bytes), &mut found);
        }
    }
    found
}
fn profile_data(data: &Value) -> Option<Value> {
    let events = data
        .get("traceEvents")?
        .as_array()?
        .iter()
        .filter_map(|e| Some((e, e.get("ts")?.as_f64()?)))
        .collect::<Vec<_>>();
    let start = events.iter().map(|(_, ts)| *ts).min_by(f64::total_cmp)?;
    let end = events
        .iter()
        .map(|(e, ts)| ts + e.get("dur").and_then(Value::as_f64).unwrap_or(0.))
        .max_by(f64::total_cmp)?;
    let ran = events
        .iter()
        .filter(|(e, _)| e.get("cat").and_then(Value::as_str) == Some("action processing"))
        .filter_map(|(e, _)| {
            e.get("name")?
                .as_str()?
                .strip_prefix("Executing genrule //:")
                .map(str::to_owned)
        })
        .collect::<BTreeSet<_>>();
    Some(
        json!({"id":data["otherData"]["build_id"],"started":data["otherData"]["date"],"seconds":(((end-start)/1e6)*10.).round_ties_even()/10.,"ran":ran}),
    )
}
fn profile(path: &Path) -> Option<Value> {
    let bytes = archive::decompress(&fs::read(path).ok()?).ok()?;
    profile_data(&serde_json::from_slice::<Value>(&bytes).ok()?)
}
fn git_text(ctx: &crate::ContextData, args: &[&str]) -> String {
    ctx.git(args)
        .ok()
        .map(|v| String::from_utf8_lossy(&v.stdout).trim().into())
        .unwrap_or_default()
}
fn full_builds_at(ctx: &crate::ContextData, base: &Path) -> Vec<Value> {
    if !base.is_dir() {
        return vec![];
    }
    let logged = commands(base);
    let mut rows = vec![];
    let mut paths = fs::read_dir(base)
        .into_iter()
        .flatten()
        .filter_map(|e| e.ok())
        .filter(|e| {
            let name = e.file_name();
            let name = name.to_string_lossy();
            name.starts_with("command-") && name.ends_with(".profile.gz")
        })
        .map(|e| e.path())
        .collect::<Vec<_>>();
    paths.sort();
    for path in paths {
        if path.is_symlink() {
            continue;
        }
        let Some(got) = profile(&path) else {
            continue;
        };
        let Some(id) = got["id"].as_str().filter(|s| !s.is_empty()) else {
            continue;
        };
        let Some(cmd) = logged
            .get(id)
            .filter(|c| c.command == "build" && c.targets.iter().any(|t| t == TARGET))
        else {
            continue;
        };
        let Some(started) = got["started"].as_str() else {
            continue;
        };
        let before = format!("--before={started}");
        let commit = git_text(ctx, &["log", "-1", "--format=%h", &before, "HEAD"]);
        let steps = if commit.is_empty() {
            None
        } else {
            let spec = format!("{commit}:BUILD.bazel");
            let count = git_text(ctx, &["show", &spec]).matches("genrule(").count();
            (count > 0).then_some(count)
        };
        rows.push(json!({"id":id,"started":started,"commit":commit,"seconds":got["seconds"],"reran":got["ran"].as_array().map_or(0,Vec::len),"steps":steps,"finished":cmd.exit=="SUCCESS"}));
    }
    rows
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
    if args.check {
        let mut rows = full_builds_at(ctx, &output_base(ctx)?);
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
        .and_then(|v| serde_json::from_slice(&v).ok())
        .unwrap_or(Value::Null);
    let data = merge_rows(&existing, full_builds_at(ctx, &output_base(ctx)?));
    let text = render(&data)?;
    let same = fs::read_to_string(&output).ok().is_some_and(|v| v == text);
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
            let fields = [
                "id", "started", "commit", "seconds", "reran", "steps", "finished",
            ]
            .iter()
            .map(|key| {
                Ok(format!(
                    "      {}: {}",
                    serde_json::to_string(key)?,
                    serde_json::to_string(&row[*key])?
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
    #[test]
    fn bazel_workspace_digest_matches_md5_vectors() {
        assert_eq!(md5(b""), "d41d8cd98f00b204e9800998ecf8427e");
        assert_eq!(md5(b"abc"), "900150983cd24fb0d6963f7d28e17f72");
        assert_eq!(
            md5(b"The quick brown fox jumps over the lazy dog"),
            "9e107d9d372bb6826bd81d3542a419d6"
        );
    }
    #[test]
    fn server_logs_bind_targets_and_actual_exit_to_build_id() {
        let mut found = BTreeMap::new();
        parse_commands(
            "x GrpcServerImpl.executeCommand] [build, --client_cwd=/checkout, --jobs=2, //:everything]\nx Build identifier: 01234567-89ab-cdef-0123-456789abcdef\nx Exit status was DetailedExitCode{exitCode=BUILD_FAILURE, detail=none}\nx GrpcServerImpl.executeCommand] [cquery, --client_cwd=/checkout, deps(//:everything)]\nx Build identifier: aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            &mut found,
        );
        assert_eq!(
            found["01234567-89ab-cdef-0123-456789abcdef"],
            CommandRecord {
                command: "build".into(),
                targets: vec![TARGET.into()],
                exit: "BUILD_FAILURE".into()
            }
        );
        assert_eq!(
            found["aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"].command,
            "cquery"
        );
    }
    #[test]
    fn profile_counts_rerun_actions_without_counting_queries_or_duplicate_events() {
        let got=profile_data(&json!({"otherData":{"build_id":"build","date":"date"},"traceEvents":[{"ts":100,"dur":1234567},{"ts":120,"dur":100,"cat":"action processing","name":"Executing genrule //:alpha"},{"ts":140,"cat":"action processing","name":"Executing genrule //:alpha"},{"ts":200,"cat":"action processing","name":"Executing genrule //:beta"},{"name":"metadata"}]})).unwrap();
        assert_eq!(got["seconds"], 1.2);
        assert_eq!(got["ran"], json!(["alpha", "beta"]));
        assert!(profile_data(&json!({"traceEvents":[]})).is_none());
    }
    #[test]
    fn recorded_rows_stand_and_oldest_rows_fall_out_of_the_site_list() {
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
                .any(|r| r["id"] == "same")
        );
        let got = merge_rows(
            &existing,
            vec![json!({"id":"same","started":"9999","seconds":900})],
        );
        assert_eq!(got["builds"][0]["seconds"], 1.5);
    }
    #[test]
    fn site_json_keeps_row_field_order_and_fractional_seconds() {
        let row = json!({"id":"x","started":"date","commit":"head","seconds":1.0,"reran":0,"steps":null,"finished":true});
        let text = render(&json!({"builds":[row]})).unwrap();
        assert!(text.contains("\"seconds\": 1.0"));
        assert!(text.find("\"id\"").unwrap() < text.find("\"commit\"").unwrap());
        assert_eq!(
            serde_json::from_str::<Value>(&text).unwrap()["builds"][0]["finished"],
            true
        );
    }
}
