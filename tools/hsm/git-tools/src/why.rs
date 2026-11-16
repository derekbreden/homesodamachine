//! git-why follows a line's history past the commits where git loses track of it, through the
//! Agent Trace records kept in git notes.
use anyhow::{Context, Result, bail, ensure};
use serde_json::{Value, json};
use std::{
    env, fs,
    io::{Read, Write},
    path::Path,
    process::{Command, Stdio},
    time::{SystemTime, UNIX_EPOCH},
};

/// One Agent Trace record per line, attached to each commit that rewrote lines git can't follow.
const NOTES: &str = "refs/notes/agent-trace";
/// Where a link push parks the remote's notes while it merges them in.
const REMOTE_NOTES: &str = "refs/notes/agent-trace-remote";
/// The `related` link type naming the line a range was rewritten from.
const DERIVED_FROM: &str = "derived_from";
/// The metadata namespace holding a link's note.
const NAMESPACE: &str = "com.homesodamachine";
/// How many hops a trail may take before it counts as a loop.
const MAX_HOPS: usize = 32;
const NULL_SHA: &str = "0000000000000000000000000000000000000000";

const USAGE: &str = "usage:
  git why <path> <line | /regex/> [--rev REV] [--json]
  git why <path>:<line>
  git why link <commit>:<path>:<line[-end]> <from-commit>:<from-path>:<line[-end]> [--note TEXT] [--no-push]";

fn main() {
    if let Err(error) = run() {
        eprintln!("git why: {error:#}");
        std::process::exit(1);
    }
}

fn run() -> Result<()> {
    let args: Vec<String> = env::args().skip(1).collect();
    let root = git(None, &["rev-parse", "--show-toplevel"])?.trim().to_string();
    match args.first().map(String::as_str) {
        None | Some("-h") | Some("--help") => {
            println!("{USAGE}");
            Ok(())
        }
        Some("link") => link(&root, &args[1..]),
        _ => follow(&root, &args),
    }
}

fn git(root: Option<&str>, args: &[&str]) -> Result<String> {
    let mut command = Command::new("git");
    if let Some(root) = root {
        command.arg("-C").arg(root);
    }
    let out = command.args(args).stdin(Stdio::null()).output().context("running git")?;
    if !out.status.success() {
        bail!("git {}: {}", args.join(" "), String::from_utf8_lossy(&out.stderr).trim());
    }
    Ok(String::from_utf8_lossy(&out.stdout).into_owned())
}

fn git_stdin(root: &str, args: &[&str], input: &str) -> Result<()> {
    let mut child = Command::new("git")
        .arg("-C")
        .arg(root)
        .args(args)
        .stdin(Stdio::piped())
        .stdout(Stdio::null())
        .stderr(Stdio::piped())
        .spawn()
        .context("running git")?;
    child.stdin.take().context("git stdin")?.write_all(input.as_bytes())?;
    let out = child.wait_with_output()?;
    ensure!(out.status.success(), "git {}: {}", args.join(" "), String::from_utf8_lossy(&out.stderr).trim());
    Ok(())
}

// --- following a line ---

struct Blame {
    commit: String,
    path: String,
    line: u64,
    content: String,
}

struct Link {
    commit: String,
    path: String,
    start: u64,
    note: Option<String>,
}

fn follow(root: &str, args: &[String]) -> Result<()> {
    let (mut rev, mut json_out, mut positional) = (None, false, vec![]);
    let mut i = 0;
    while i < args.len() {
        match args[i].as_str() {
            "--rev" => {
                rev = Some(args.get(i + 1).context("--rev needs a revision")?.clone());
                i += 1;
            }
            "--json" => json_out = true,
            other => positional.push(other.to_string()),
        }
        i += 1;
    }
    let (path, spec) = match positional.as_slice() {
        [path, line] => (path.clone(), line.clone()),
        [one] => match one.rsplit_once(':') {
            Some((path, line)) => (path.to_string(), line.to_string()),
            None => bail!("{USAGE}"),
        },
        _ => bail!("{USAGE}"),
    };
    let range = if spec.starts_with('/') { format!("{spec},+1") } else { format!("{0},{0}", spec.parse::<u64>().context("line number")?) };
    let mut path = repo_path(root, &path)?;
    fetch_notes_once(root);

    let mut hops: Vec<(Blame, Option<Link>)> = vec![];
    let mut at = (rev, range);
    for _ in 0..MAX_HOPS {
        let blame = blame(root, at.0.as_deref(), &path, &at.1)?;
        if blame.commit == NULL_SHA {
            hops.push((blame, None));
            break;
        }
        let link = derived_from(&records(root, &blame.commit), &blame.commit, &blame.path, blame.line);
        let next = link.as_ref().map(|l| (l.commit.clone(), l.path.clone(), l.start));
        hops.push((blame, link));
        match next {
            Some((commit, next_path, line)) => {
                path = next_path;
                at = (Some(commit), format!("{line},{line}"));
            }
            None => break,
        }
    }
    let last = &hops.last().context("no blame")?.0;
    let message = if last.commit == NULL_SHA { String::new() } else { git(Some(root), &["show", "-s", "--format=%B", &last.commit])? };
    let unlinked = last.commit != NULL_SHA && !records(root, &last.commit).is_empty();
    if json_out {
        print_json(root, &hops, &message, unlinked)
    } else {
        print_text(root, &hops, &message, unlinked)
    }
}

/// The path from the repository root, for a path given from the current directory.
fn repo_path(root: &str, given: &str) -> Result<String> {
    if let Ok(full) = fs::canonicalize(given) {
        if let Ok(rel) = full.strip_prefix(fs::canonicalize(root)?) {
            return Ok(rel.to_string_lossy().into_owned());
        }
    }
    let prefix = git(None, &["rev-parse", "--show-prefix"])?;
    Ok(format!("{}{}", prefix.trim(), given))
}

fn blame(root: &str, rev: Option<&str>, path: &str, range: &str) -> Result<Blame> {
    // -C -C -M: lines moved or copied unchanged from another file count as that file's, so only a
    // rewrite needs a recorded link.
    let mut args = vec!["blame", "--porcelain", "-C", "-C", "-M", "-L", range];
    if let Some(rev) = rev {
        args.push(rev);
    }
    args.extend(["--", path]);
    let out = git(Some(root), &args)?;
    let mut lines = out.lines();
    let head = lines.next().context("empty blame")?;
    let mut fields = head.split_whitespace();
    let commit = fields.next().context("blame commit")?.to_string();
    let line = fields.next().context("blame line")?.parse()?;
    let (mut blamed_path, mut content) = (path.to_string(), String::new());
    for row in lines {
        if let Some(name) = row.strip_prefix("filename ") {
            blamed_path = name.to_string();
        } else if let Some(text) = row.strip_prefix('\t') {
            content = text.to_string();
            break;
        }
    }
    Ok(Blame { commit, path: blamed_path, line, content })
}

/// The Agent Trace records attached to a commit, one JSON object per note line.
fn records(root: &str, commit: &str) -> Vec<Value> {
    git(Some(root), &["notes", "--ref", NOTES, "show", commit])
        .map(|text| text.lines().filter_map(|row| serde_json::from_str(row.trim()).ok()).collect())
        .unwrap_or_default()
}

/// The line a recorded link says this commit's line was rewritten from.
fn derived_from(records: &[Value], commit: &str, path: &str, line: u64) -> Option<Link> {
    for record in records {
        if record["vcs"]["revision"].as_str() != Some(commit) {
            continue;
        }
        let note = record["metadata"][NAMESPACE]["note"].as_str().map(str::to_string);
        for file in record["files"].as_array().into_iter().flatten() {
            if file["path"].as_str() != Some(path) {
                continue;
            }
            for conversation in file["conversations"].as_array().into_iter().flatten() {
                let urls: Vec<&str> = conversation["related"].as_array().into_iter().flatten()
                    .filter(|r| r["type"].as_str() == Some(DERIVED_FROM))
                    .filter_map(|r| r["url"].as_str())
                    .collect();
                for range in conversation["ranges"].as_array().into_iter().flatten() {
                    let (Some(start), Some(end)) = (range["start_line"].as_u64(), range["end_line"].as_u64()) else { continue };
                    if start <= line && line <= end {
                        if let Some(target) = urls.iter().find_map(|url| parse_permalink(url)) {
                            let offset = (line - start).min(target.2 - target.1);
                            return Some(Link { commit: target.0, path: target.3, start: target.1 + offset, note });
                        }
                    }
                }
            }
        }
    }
    None
}

/// A GitHub permalink, `…/blob/<commit>/<path>#L<a>[-L<b>]`, as (commit, a, b, path).
fn parse_permalink(url: &str) -> Option<(String, u64, u64, String)> {
    let (_, rest) = url.split_once("/blob/")?;
    let (location, anchor) = rest.split_once("#L")?;
    let (commit, path) = location.split_once('/')?;
    let (a, b) = match anchor.split_once("-L") {
        Some((a, b)) => (a.parse().ok()?, b.parse().ok()?),
        None => {
            let a = anchor.parse().ok()?;
            (a, a)
        }
    };
    Some((commit.to_string(), a, b, path.to_string()))
}

fn print_text(root: &str, hops: &[(Blame, Option<Link>)], message: &str, unlinked: bool) -> Result<()> {
    for (blame, link) in hops {
        if blame.commit == NULL_SHA {
            println!("Not committed yet\n    {}:{}  {}\n", blame.path, blame.line, blame.content.trim());
            continue;
        }
        let summary = git(Some(root), &["log", "-1", "--format=%h %ad %s", "--date=short", &blame.commit])?;
        println!("{}\n    {}:{}  {}", summary.trim_end(), blame.path, blame.line, blame.content.trim());
        if let Some(link) = link {
            let short = &link.commit[..link.commit.len().min(10)];
            println!("    ↳ rewritten from {}:{} at {short}{}", link.path, link.start, link.note.as_ref().map(|n| format!(": {n}")).unwrap_or_default());
        }
        println!();
    }
    let last = &hops.last().context("no hops")?.0;
    if unlinked {
        let short = &last.commit[..10];
        println!("{short} rewrote lines git can't follow, and no link records where this one came from.");
        println!("Find it in {short}^ and record it:\n  git why link {short}:{}:{} <from-commit>:<from-path>:<line>\n", last.path, last.line);
    }
    if !message.is_empty() {
        for row in message.trim_end().lines() {
            println!("    {row}");
        }
    }
    Ok(())
}

fn print_json(root: &str, hops: &[(Blame, Option<Link>)], message: &str, unlinked: bool) -> Result<()> {
    let mut rows = vec![];
    for (blame, link) in hops {
        let summary = if blame.commit == NULL_SHA { String::new() } else { git(Some(root), &["log", "-1", "--format=%ad%x09%s", "--date=short", &blame.commit])? };
        let (date, subject) = summary.trim_end().split_once('\t').unwrap_or(("", ""));
        rows.push(json!({
            "commit": blame.commit, "date": date, "subject": subject,
            "path": blame.path, "line": blame.line, "content": blame.content,
            "derived_from": link.as_ref().map(|l| json!({"commit": l.commit, "path": l.path, "line": l.start, "note": l.note})),
        }));
    }
    println!("{}", serde_json::to_string_pretty(&json!({"hops": rows, "message": message, "unlinked_migration": unlinked}))?);
    Ok(())
}

/// A checkout that has never fetched the notes takes them from origin once.
fn fetch_notes_once(root: &str) {
    if git(Some(root), &["rev-parse", "--verify", "--quiet", NOTES]).is_err() {
        let _ = git(Some(root), &["fetch", "-q", "origin", &format!("{NOTES}:{NOTES}")]);
    }
}

// --- recording a link ---

struct Place {
    commit: String,
    path: String,
    start: u64,
    end: u64,
}

fn place(root: &str, spec: &str) -> Result<Place> {
    let (commit, rest) = spec.split_once(':').context("expected <commit>:<path>:<line[-end]>")?;
    let (path, lines) = rest.rsplit_once(':').context("expected <commit>:<path>:<line[-end]>")?;
    let (start, end) = match lines.split_once('-') {
        Some((a, b)) => (a.parse()?, b.parse()?),
        None => {
            let a = lines.parse()?;
            (a, a)
        }
    };
    ensure!(start >= 1 && end >= start, "bad line range {lines}");
    let commit = git(Some(root), &["rev-parse", "--verify", &format!("{commit}^{{commit}}")])?.trim().to_string();
    let text = git(Some(root), &["show", &format!("{commit}:{path}")]).with_context(|| format!("{path} at {commit}"))?;
    ensure!(end as usize <= text.lines().count(), "{path} at {commit} has {} lines", text.lines().count());
    Ok(Place { commit, path: path.to_string(), start, end })
}

fn link(root: &str, args: &[String]) -> Result<()> {
    let (mut note, mut push, mut positional) = (None, true, vec![]);
    let mut i = 0;
    while i < args.len() {
        match args[i].as_str() {
            "--note" => {
                note = Some(args.get(i + 1).context("--note needs text")?.clone());
                i += 1;
            }
            "--no-push" => push = false,
            other => positional.push(other.to_string()),
        }
        i += 1;
    }
    let [at, from] = positional.as_slice() else { bail!("{USAGE}") };
    let (at, from) = (place(root, at)?, place(root, from)?);
    let url = format!("{}/blob/{}/{}#L{}{}", github_base(root)?, from.commit, from.path, from.start,
                      if from.end > from.start { format!("-L{}", from.end) } else { String::new() });
    let mut record = json!({
        "version": "0.1.0",
        "id": uuid4()?,
        "timestamp": now_rfc3339(),
        "vcs": {"type": "git", "revision": at.commit},
        "tool": {"name": "git-why", "version": env!("CARGO_PKG_VERSION")},
        "files": [{"path": at.path, "conversations": [{
            "ranges": [{"start_line": at.start, "end_line": at.end}],
            "related": [{"type": DERIVED_FROM, "url": url}],
        }]}],
    });
    if let Some(note) = &note {
        let mut namespace = serde_json::Map::new();
        namespace.insert(NAMESPACE.to_string(), json!({"note": note}));
        record["metadata"] = Value::Object(namespace);
    }
    let mut lines: Vec<String> = git(Some(root), &["notes", "--ref", NOTES, "show", &at.commit])
        .map(|text| text.lines().map(str::to_string).filter(|l| !l.trim().is_empty()).collect())
        .unwrap_or_default();
    lines.push(serde_json::to_string(&record)?);
    git_stdin(root, &["notes", "--ref", NOTES, "add", "-f", "-F", "-", &at.commit], &(lines.join("\n") + "\n"))?;
    println!("linked {}:{}:{} ← {url}", &at.commit[..10], at.path, at.start);
    if push {
        push_notes(root)?;
    }
    Ok(())
}

/// Pushes the notes, merging in any links someone else pushed first.
fn push_notes(root: &str) -> Result<()> {
    for _ in 0..4 {
        if git(Some(root), &["push", "-q", "origin", NOTES]).is_ok() {
            return Ok(());
        }
        git(Some(root), &["fetch", "-q", "origin", &format!("+{NOTES}:{REMOTE_NOTES}")])?;
        git(Some(root), &["notes", "--ref", NOTES, "merge", "-q", "-s", "cat_sort_uniq", REMOTE_NOTES])?;
    }
    bail!("could not push {NOTES}; the links are recorded locally")
}

fn github_base(root: &str) -> Result<String> {
    let url = git(Some(root), &["remote", "get-url", "origin"])?;
    let url = url.trim().trim_end_matches(".git");
    let slug = url.strip_prefix("git@github.com:").or_else(|| url.strip_prefix("https://github.com/")).context("origin is not on GitHub")?;
    Ok(format!("https://github.com/{slug}"))
}

fn uuid4() -> Result<String> {
    let mut b = [0u8; 16];
    fs::File::open(Path::new("/dev/urandom"))?.read_exact(&mut b)?;
    b[6] = (b[6] & 0x0f) | 0x40;
    b[8] = (b[8] & 0x3f) | 0x80;
    let h: Vec<String> = b.iter().map(|x| format!("{x:02x}")).collect();
    Ok(format!("{}-{}-{}-{}-{}", h[0..4].concat(), h[4..6].concat(), h[6..8].concat(), h[8..10].concat(), h[10..16].concat()))
}

fn now_rfc3339() -> String {
    let secs = SystemTime::now().duration_since(UNIX_EPOCH).map(|d| d.as_secs() as i64).unwrap_or(0);
    let (days, rem) = (secs.div_euclid(86_400), secs.rem_euclid(86_400));
    // Civil date from days since 1970-01-01 (Howard Hinnant's algorithm).
    let z = days + 719_468;
    let era = z.div_euclid(146_097);
    let doe = z - era * 146_097;
    let yoe = (doe - doe / 1_460 + doe / 36_524 - doe / 146_096) / 365;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let day = doy - (153 * mp + 2) / 5 + 1;
    let month = if mp < 10 { mp + 3 } else { mp - 9 };
    let year = yoe + era * 400 + i64::from(month <= 2);
    format!("{year:04}-{month:02}-{day:02}T{:02}:{:02}:{:02}Z", rem / 3_600, rem % 3_600 / 60, rem % 60)
}
