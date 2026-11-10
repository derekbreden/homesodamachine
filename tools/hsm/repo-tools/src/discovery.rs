//! Missing-tools discovery counts scratch code and blocking waits in the repository's agent transcripts when requested.
use anyhow::{Context, Result, ensure};
use regex::Regex;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::{
    collections::{BTreeMap, BTreeSet, HashMap},
    io::{BufRead, BufReader},
    path::{Path, PathBuf},
    process::Command,
    sync::{Arc, Mutex},
};
const CODE: &[&str] = &["py", "mjs", "cjs", "js", "ts", "swift", "rs"];
const KINDS: &[&str] = &[
    ".step.mesh",
    ".facts.json",
    ".step",
    ".stp",
    ".stl",
    ".3mf",
    ".glb",
    ".gcode",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".svg",
    ".pdf",
];
#[derive(Clone, Serialize, Deserialize)]
pub struct Script {
    key: String,
    ts: String,
    gist: String,
    code: String,
    reads: Vec<String>,
    agent: String,
    sid: String,
}
#[derive(Clone, Serialize, Deserialize)]
pub struct Wait {
    agent: String,
    sid: String,
    seconds: f64,
    t0: String,
    what: String,
    #[serde(skip)]
    id: String,
}
#[derive(Serialize, Deserialize)]
pub struct Reading {
    days: f64,
    since: f64,
    made: f64,
    seconds: f64,
    sessions: usize,
    downloaded: u64,
    titles: BTreeMap<String, String>,
    scripts: Vec<Script>,
    waits: Vec<Wait>,
}
#[derive(Default)]
struct Session {
    agent: String,
    sid: String,
    path: PathBuf,
    title: String,
    title_from_index: bool,
    scripts: Vec<Script>,
    waits: Vec<Wait>,
    downloaded: u64,
    fork: bool,
}
struct Reader {
    root: PathBuf,
    tops: BTreeSet<String>,
    modules: BTreeMap<String, String>,
    path_rx: Regex,
    import_rx: Regex,
    crate_rx: Regex,
}
impl Reader {
    fn new(root: &Path) -> Result<Self> {
        let files = crate::git(root, &["ls-files"])?;
        let mut tops = BTreeSet::new();
        let mut by_name = BTreeMap::<String, Vec<String>>::new();
        let stop = [
            "__init__", "build", "common", "main", "test", "tests", "conftest", "setup", "config",
            "util", "utils", "helpers", "app", "index", "run", "cli", "lib",
        ];
        let package_name = Regex::new(r#"(?m)^name\s*=\s*"([^"]+)""#)?;
        for path in files.lines() {
            if let Some((top, _)) = path.split_once('/') {
                if !top.starts_with('.') {
                    tops.insert(top.to_owned());
                }
            }
            let p = Path::new(path);
            let ext = p.extension().and_then(|x| x.to_str());
            if ext == Some("py") || ext == Some("rs") {
                let name = p.file_stem().unwrap().to_string_lossy().into_owned();
                if !stop.contains(&name.as_str()) {
                    by_name.entry(name).or_default().push(path.into());
                }
            }
            if path.ends_with("Cargo.toml") {
                if let Ok(text) = crate::text(root.join(path)) {
                    if let Some(c) = package_name.captures(&text) {
                        let name = c[1].replace('-', "_");
                        if name.starts_with("hsm_") {
                            by_name.entry(name).or_default().push(path.into());
                        }
                    }
                }
            }
        }
        let modules = by_name
            .into_iter()
            .filter(|(_, v)| v.len() <= 2)
            .map(|(k, v)| {
                let value = if v.len() == 1 {
                    v[0].clone()
                } else {
                    format!("{k} source")
                };
                (k, value)
            })
            .collect();
        let path_rx = Regex::new(&format!(
            r"(?:{})/[\w.\-/*{{}}@+]+",
            tops.iter()
                .map(|s| regex::escape(s))
                .collect::<Vec<_>>()
                .join("|")
        ))?;
        Ok(Self {
            root: root.to_path_buf(),
            tops,
            modules,
            path_rx,
            import_rx: Regex::new(
                r"(?m)^[ \t]*(?:from[ \t]+([\w.]+)[ \t]+import[ \t]+\(?([\w \t,*]+)|import[ \t]+([\w. \t,]+))",
            )?,
            crate_rx: Regex::new(r"\b(?:use|extern\s+crate)\s+([a-zA-Z_]\w*)")?,
        })
    }
    fn scratch(&self, path: &str) -> bool {
        let ext = Path::new(path)
            .extension()
            .and_then(|x| x.to_str())
            .unwrap_or("");
        if !CODE.contains(&ext) {
            return false;
        }
        if Path::new(path).starts_with(self.root.join(".cache")) {
            return true;
        }
        let parts: BTreeSet<_> = path.split('/').collect();
        (parts.contains("scratchpad")
            || ["/tmp/", "/private/tmp/", "/var/folders/"]
                .iter()
                .any(|p| path.starts_with(p)))
            && !self.tops.iter().any(|t| parts.contains(t.as_str()))
    }
    fn reads(&self, code: &str) -> Vec<String> {
        let mut reads = BTreeSet::new();
        for m in self.path_rx.find_iter(code) {
            if code[..m.start()]
                .chars()
                .next_back()
                .is_some_and(|c| c.is_alphanumeric() || "_.-".contains(c))
            {
                continue;
            }
            let p = m
                .as_str()
                .trim_end_matches(['.', ',', ':', ';', ')', ']', '}', '\'', '"', '`']);
            let base = p.rsplit('/').next().unwrap_or("").to_lowercase();
            if let Some(kind) = KINDS.iter().find(|k| base.ends_with(**k)) {
                reads.insert(format!("*{kind}"));
            } else if !p.contains(['*', '{'])
                && base.contains('.')
                && !base.ends_with(".md")
                && self.root.join(p).exists()
            {
                reads.insert(p.to_owned());
            }
        }
        for c in self.import_rx.captures_iter(code) {
            let mut names = Vec::new();
            if let Some(module) = c.get(1) {
                names.push(module.as_str());
                names.extend(c.get(2).map_or("", |s| s.as_str()).split(','));
            } else {
                names.extend(c.get(3).map_or("", |s| s.as_str()).split(','));
            }
            for name in names {
                let name = name
                    .split(" as ")
                    .next()
                    .unwrap_or("")
                    .trim()
                    .rsplit('.')
                    .next()
                    .unwrap_or("");
                if let Some(path) = self.modules.get(name) {
                    reads.insert(path.clone());
                }
            }
        }
        for c in self.crate_rx.captures_iter(code) {
            if let Some(path) = self.modules.get(&c[1]) {
                reads.insert(path.clone());
            }
        }
        reads.into_iter().collect()
    }
}
fn gist(description: &str, code: &str) -> String {
    if !description.is_empty() {
        return description.split_whitespace().collect::<Vec<_>>().join(" ");
    }
    for line in code.lines() {
        let l = line.trim();
        if let Some(comment) = l
            .strip_prefix("//")
            .or_else(|| l.strip_prefix('#'))
            .or_else(|| l.strip_prefix("\"\"\""))
            .or_else(|| l.strip_prefix("'''"))
        {
            let comment = comment.trim().trim_end_matches(['\'', '"']);
            if !comment.is_empty() && !comment.starts_with('!') {
                return comment.into();
            }
        }
    }
    code.lines()
        .map(str::trim)
        .find(|l| {
            !l.is_empty()
                && !["import ", "from ", "#!", "cd ", "set ", "const ", "let "]
                    .iter()
                    .any(|p| l.starts_with(p))
        })
        .unwrap_or("")
        .into()
}
fn decode_literal(s: &str) -> String {
    if s.starts_with('"') {
        if let Ok(decoded) = serde_json::from_str::<String>(s) {
            return decoded;
        }
    }
    let body = s.get(1..s.len().saturating_sub(1)).unwrap_or("");
    let mut out = String::new();
    let mut chars = body.chars();
    while let Some(ch) = chars.next() {
        if ch != '\\' {
            out.push(ch);
            continue;
        }
        let Some(next) = chars.next() else {
            out.push('\\');
            break;
        };
        match next {
            'n' => out.push('\n'),
            'r' => out.push('\r'),
            't' => out.push('\t'),
            '\\' | '\'' | '"' | '`' | '$' => out.push(next),
            'u' | 'x' => {
                let n = if next == 'u' { 4 } else { 2 };
                let hex = chars.by_ref().take(n).collect::<String>();
                if let Some(c) = u32::from_str_radix(&hex, 16).ok().and_then(char::from_u32) {
                    out.push(c)
                } else {
                    out.push('\\');
                    out.push(next);
                    out.push_str(&hex)
                }
            }
            other => {
                out.push('\\');
                out.push(other)
            }
        }
    }
    out
}
fn inline_code(command: &str) -> Result<Vec<String>> {
    let lines: Vec<_> = command.lines().collect();
    let heredoc = Regex::new(r#"<<-?\s*(['"]?)([A-Za-z_]\w*)"#)?;
    let runner = Regex::new(r"\b(?:python3?(?:\.\d+)?|node|ruby|perl|osascript|swift|rustc)\b")?;
    let code_file = Regex::new(r">\s*\S+\.(?:py|mjs|cjs|js|ts|swift|rs)\b")?;
    let mut out = Vec::new();
    let mut i = 0;
    while i < lines.len() {
        if let Some(c) = heredoc.captures(lines[i]) {
            let tag = &c[2];
            let start = i + 1;
            let mut end = start;
            while end < lines.len() && lines[end].trim() != tag {
                end += 1;
            }
            if end < lines.len() && (runner.is_match(lines[i]) || code_file.is_match(lines[i])) {
                out.push(lines[start..end].join("\n"));
            }
            i = end;
        }
        i += 1;
    }
    let dash = Regex::new(
        r#"\b(?:python3?(?:\.\d+)?|node|osascript)\b[^\n|;&]*?\s-[ce]\s+("(?:[^"\\]|\\.)*"|'[^']*')"#,
    )?;
    for c in dash.captures_iter(command) {
        let quoted = &c[1];
        let body = &quoted[1..quoted.len() - 1];
        out.push(if quoted.starts_with('"') {
            body.replace("\\\"", "\"")
                .replace("\\$", "$")
                .replace("\\\\", "\\")
        } else {
            body.into()
        });
    }
    Ok(out)
}
fn js_commands(code: &str) -> Result<Vec<String>> {
    Ok(
        Regex::new(r#"\bcmd\s*:\s*("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|`(?:[^`\\]|\\.)*`)"#)?
            .captures_iter(code)
            .map(|c| decode_literal(&c[1]))
            .collect(),
    )
}
fn s<'a>(value: &'a Value, key: &str) -> &'a str {
    value[key].as_str().unwrap_or("")
}
fn json_args(payload: &Value) -> Value {
    payload["arguments"]
        .as_str()
        .and_then(|s| serde_json::from_str(s).ok())
        .unwrap_or_else(|| payload["arguments"].clone())
}
fn output_text(output: &Value) -> String {
    match output {
        Value::String(s) => s.clone(),
        Value::Array(a) => a.iter().filter_map(|v| v["text"].as_str()).collect(),
        Value::Null => String::new(),
        other => other.to_string(),
    }
}
fn number_key(value: &Value) -> String {
    value
        .as_str()
        .map(str::to_owned)
        .unwrap_or_else(|| value.to_string())
}
fn stamp(s: &str) -> f64 {
    let main = s.trim_end_matches('Z');
    let mut parts = main.split(['-', 'T', ':']);
    let ints: Vec<_> = parts
        .by_ref()
        .take(5)
        .map(|s| s.parse::<i32>().unwrap_or(0))
        .collect();
    if ints.len() != 5 {
        return 0.;
    }
    let seconds = parts
        .next()
        .unwrap_or("0")
        .split('+')
        .next()
        .unwrap_or("0")
        .parse::<f64>()
        .unwrap_or(0.);
    let mut tm: libc::tm = unsafe { std::mem::zeroed() };
    tm.tm_year = ints[0] - 1900;
    tm.tm_mon = ints[1] - 1;
    tm.tm_mday = ints[2];
    tm.tm_hour = ints[3];
    tm.tm_min = ints[4];
    tm.tm_sec = seconds as i32;
    unsafe { libc::timegm(&mut tm) as f64 + seconds.fract() }
}
fn date(stamp: f64, format: &str, utc: bool) -> String {
    let stamp = stamp as libc::time_t;
    let mut tm = std::mem::MaybeUninit::uninit();
    let mut buf = [0_i8; 96];
    let fmt = std::ffi::CString::new(format).unwrap();
    unsafe {
        let got = if utc {
            libc::gmtime_r(&stamp, tm.as_mut_ptr())
        } else {
            libc::localtime_r(&stamp, tm.as_mut_ptr())
        };
        if got.is_null() {
            return stamp.to_string();
        }
        let n = libc::strftime(buf.as_mut_ptr(), buf.len(), fmt.as_ptr(), tm.as_ptr());
        String::from_utf8_lossy(std::slice::from_raw_parts(buf.as_ptr().cast(), n)).into_owned()
    }
}
impl Session {
    fn script(&mut self, reader: &Reader, key: String, ts: &str, description: &str, code: &str) {
        if !code.trim().is_empty() {
            self.scripts.push(Script {
                key,
                ts: ts.into(),
                gist: gist(description, code),
                code: code.into(),
                reads: reader.reads(code),
                agent: self.agent.clone(),
                sid: self.sid.clone(),
            });
        }
    }
    fn wait(&mut self, seconds: f64, t0: String, what: String, id: String) {
        self.waits.push(Wait {
            seconds,
            t0,
            what,
            agent: self.agent.clone(),
            sid: self.sid.clone(),
            id,
        });
    }
    fn claude(&mut self, reader: &Reader, since: &str) -> Result<()> {
        let file = std::fs::File::open(&self.path)?;
        let mut calls = HashMap::<String, (String, String)>::new();
        for raw in BufReader::new(file).lines() {
            let Ok(raw) = raw else { continue };
            if raw.contains("\"custom-title\"") {
                if let Ok(d) = serde_json::from_str::<Value>(&raw) {
                    if let Some(t) = d["customTitle"].as_str().filter(|_| !self.title_from_index) {
                        self.title = t.into();
                    }
                }
            }
            if !raw.contains("\"tool_use\"") && !raw.contains("\"tool_result\"") {
                continue;
            }
            let Ok(d) = serde_json::from_str::<Value>(&raw) else {
                continue;
            };
            let ts = s(&d, "timestamp");
            let Some(content) = d["message"]["content"].as_array() else {
                continue;
            };
            for b in content {
                let inp = &b["input"];
                let id = s(b, "id");
                match s(b, "type") {
                    "tool_use" if ts >= since => match s(b, "name") {
                        "Bash" => {
                            let command = s(inp, "command");
                            for (i, body) in inline_code(command)?.iter().enumerate() {
                                self.script(
                                    reader,
                                    format!("{id}:{i}"),
                                    ts,
                                    s(inp, "description"),
                                    body,
                                );
                            }
                            if !inp["run_in_background"].as_bool().unwrap_or(false) {
                                calls.insert(
                                    id.into(),
                                    (
                                        ts.into(),
                                        if s(inp, "description").is_empty() {
                                            command.lines().next().unwrap_or("").into()
                                        } else {
                                            s(inp, "description").into()
                                        },
                                    ),
                                );
                            }
                        }
                        "Write" | "Edit" if reader.scratch(s(inp, "file_path")) => {
                            let code = inp["content"]
                                .as_str()
                                .or_else(|| inp["new_string"].as_str())
                                .unwrap_or("");
                            self.script(
                                reader,
                                id.into(),
                                ts,
                                if s(b, "name") == "Edit" {
                                    Path::new(s(inp, "file_path"))
                                        .file_name()
                                        .and_then(|s| s.to_str())
                                        .unwrap_or("")
                                } else {
                                    ""
                                },
                                code,
                            );
                        }
                        _ => {}
                    },
                    "tool_result" => {
                        if let Some((start, what)) = calls.remove(s(b, "tool_use_id")) {
                            if !ts.is_empty() {
                                self.wait(
                                    stamp(ts) - stamp(&start),
                                    start,
                                    what,
                                    s(b, "tool_use_id").into(),
                                );
                            }
                        }
                    }
                    _ => {}
                }
            }
        }
        Ok(())
    }
    fn codex(&mut self, reader: &Reader, since: &str) -> Result<()> {
        #[derive(Clone)]
        struct Event {
            t0: String,
            what: Option<String>,
            polls: BTreeSet<String>,
            id: String,
            held: f64,
        }
        let mut pending = HashMap::<String, (String, Event)>::new();
        let mut cells = HashMap::<String, Event>::new();
        let mut running = HashMap::<String, Event>::new();
        let polls = Regex::new(r"session_id\s*:\s*(\d+)")?;
        let cell = Regex::new(r"Script running with cell ID (\w+)")?;
        let still = Regex::new(r#""session_id":\s*(\d+)|Process running with session ID (\d+)"#)?;
        let file = std::fs::File::open(&self.path)?;
        for raw in BufReader::new(file).lines() {
            let Ok(raw) = raw else { continue };
            if !raw.contains("_call") {
                continue;
            }
            let Ok(d) = serde_json::from_str::<Value>(&raw) else {
                continue;
            };
            let ts = s(&d, "timestamp");
            if ts < since {
                continue;
            }
            let pl = &d["payload"];
            let name = s(pl, "name").rsplit('.').next().unwrap_or("");
            let cid = s(pl, "call_id");
            let kind = s(pl, "type");
            if kind == "custom_tool_call" && name == "exec" {
                let code = s(pl, "input");
                let commands = js_commands(code)?;
                for (i, cmd) in commands.iter().enumerate() {
                    for (j, body) in inline_code(cmd)?.iter().enumerate() {
                        self.script(reader, format!("{cid}:{i}:{j}"), ts, "", body);
                    }
                }
                let poll_set = polls
                    .captures_iter(code)
                    .map(|c| c[1].to_owned())
                    .filter(|n| running.contains_key(n))
                    .collect::<BTreeSet<_>>();
                if !commands.is_empty() || !poll_set.is_empty() {
                    pending.insert(
                        cid.into(),
                        (
                            ts.into(),
                            Event {
                                t0: ts.into(),
                                what: commands
                                    .first()
                                    .map(|c| c.lines().next().unwrap_or("").into()),
                                polls: poll_set,
                                id: cid.into(),
                                held: 0.,
                            },
                        ),
                    );
                }
            } else if kind == "function_call"
                && ["exec_command", "shell", "shell_command", "local_shell"].contains(&name)
            {
                let args = json_args(pl);
                let cmd = args
                    .get("cmd")
                    .or_else(|| args.get("command"))
                    .unwrap_or(&Value::Null);
                let command = if let Some(a) = cmd.as_array() {
                    a.last().and_then(Value::as_str).unwrap_or("")
                } else {
                    cmd.as_str().unwrap_or("")
                };
                for (j, body) in inline_code(command)?.iter().enumerate() {
                    self.script(reader, format!("{cid}:{j}"), ts, "", body);
                }
                pending.insert(
                    cid.into(),
                    (
                        ts.into(),
                        Event {
                            t0: ts.into(),
                            what: Some(command.lines().next().unwrap_or("").into()),
                            polls: BTreeSet::new(),
                            id: cid.into(),
                            held: 0.,
                        },
                    ),
                );
            } else if kind == "function_call" && ["wait", "write_stdin"].contains(&name) {
                let args = json_args(pl);
                if let Some(event) = cells.remove(&number_key(&args["cell_id"])) {
                    pending.insert(cid.into(), (ts.into(), event));
                } else {
                    let sid = number_key(&args["session_id"]);
                    if running.contains_key(&sid) {
                        pending.insert(
                            cid.into(),
                            (
                                ts.into(),
                                Event {
                                    t0: ts.into(),
                                    what: None,
                                    polls: BTreeSet::from([sid]),
                                    id: cid.into(),
                                    held: 0.,
                                },
                            ),
                        );
                    }
                }
            } else if kind == "custom_tool_call" && name == "apply_patch" {
                let mut current = None::<String>;
                let mut code = String::new();
                let mut save = |path: Option<String>, body: &mut String| {
                    if let Some(path) = path {
                        if reader.scratch(&path) {
                            self.script(reader, format!("{cid}:{path}"), ts, "", body);
                        }
                    }
                    body.clear();
                };
                for line in s(pl, "input").lines() {
                    if let Some(path) = line.strip_prefix("*** Add File: ") {
                        save(current.take(), &mut code);
                        current = Some(path.into());
                    } else if line.starts_with("*** ") {
                        save(current.take(), &mut code);
                    } else if let Some(line) = line.strip_prefix('+') {
                        if current.is_some() {
                            code.push_str(line);
                            code.push('\n');
                        }
                    }
                }
                save(current, &mut code);
            } else if ["custom_tool_call_output", "function_call_output"].contains(&kind) {
                if let Some((call, mut event)) = pending.remove(cid) {
                    event.held += stamp(ts) - stamp(&call);
                    let text = output_text(&pl["output"]);
                    if let Some(c) = cell.captures(&text) {
                        cells.insert(c[1].into(), event);
                        continue;
                    }
                    let active: BTreeSet<_> = still
                        .captures_iter(&text)
                        .filter_map(|c| {
                            c.get(1).or_else(|| c.get(2)).map(|m| m.as_str().to_owned())
                        })
                        .collect();
                    for poll in &event.polls {
                        if let Some(run) = running.get_mut(poll) {
                            run.held += event.held;
                            if !active.contains(poll) {
                                let run = running.remove(poll).unwrap();
                                self.wait(run.held, run.t0, run.what.unwrap_or_default(), run.id);
                            }
                        }
                    }
                    if event.what.is_some() {
                        let new: Vec<_> = active.difference(&event.polls).cloned().collect();
                        for n in &new {
                            running.entry(n.clone()).or_insert_with(|| {
                                let mut child = event.clone();
                                child.polls.clear();
                                child
                            });
                        }
                        if new.is_empty() {
                            self.wait(
                                event.held,
                                event.t0,
                                event.what.unwrap_or_default(),
                                event.id,
                            );
                        }
                    }
                }
            }
        }
        Ok(())
    }
}
#[cfg(target_os = "macos")]
fn offloaded(metadata: &std::fs::Metadata) -> bool {
    use std::os::macos::fs::MetadataExt;
    metadata.st_flags() & 0x40000000 != 0
}
#[cfg(not(target_os = "macos"))]
fn offloaded(_metadata: &std::fs::Metadata) -> bool {
    false
}
fn sessions(root: &Path, home: &Path) -> Result<Vec<Session>> {
    let mut titles = BTreeMap::new();
    let mut forks = BTreeSet::new();
    for path in crate::files(&home.join("Library/Application Support/Claude/claude-code-sessions"))
        .into_iter()
        .filter(|p| {
            p.file_name()
                .is_some_and(|n| n.to_string_lossy().starts_with("local_"))
                && p.extension().is_some_and(|s| s == "json")
        })
    {
        let Some(d) = crate::text(path)
            .ok()
            .and_then(|s| serde_json::from_str::<Value>(&s).ok())
        else {
            continue;
        };
        let mut ids = vec![s(&d, "cliSessionId").to_owned()];
        if let Some(prior) = d["priorCliSessionIds"].as_array() {
            ids.extend(prior.iter().filter_map(Value::as_str).map(str::to_owned));
        }
        for id in ids.into_iter().filter(|s| !s.is_empty()) {
            titles.insert(id.clone(), s(&d, "title").to_owned());
            if !s(&d, "forkedFromSessionId").is_empty() {
                forks.insert(id);
            }
        }
    }
    let common = crate::git(
        root,
        &["rev-parse", "--path-format=absolute", "--git-common-dir"],
    )?;
    let main = Path::new(&common).parent().unwrap_or(root);
    let prefix = main.to_string_lossy().replace(['/', '.'], "-");
    let mut sessions = Vec::new();
    if let Ok(dirs) = std::fs::read_dir(home.join(".claude/projects")) {
        for dir in dirs
            .flatten()
            .filter(|d| d.file_name().to_string_lossy().starts_with(&prefix))
        {
            for path in crate::files(&dir.path())
                .into_iter()
                .filter(|p| p.extension().is_some_and(|e| e == "jsonl"))
            {
                let rel = path.strip_prefix(dir.path()).unwrap_or(&path);
                let sid = rel
                    .components()
                    .next()
                    .unwrap()
                    .as_os_str()
                    .to_string_lossy()
                    .trim_end_matches(".jsonl")
                    .to_owned();
                sessions.push(Session {
                    agent: "claude".into(),
                    title: titles.get(&sid).cloned().unwrap_or_default(),
                    fork: forks.contains(&sid),
                    title_from_index: titles.get(&sid).is_some_and(|s| !s.is_empty()),
                    sid,
                    path,
                    ..Session::default()
                });
            }
        }
    }
    let mut databases = std::fs::read_dir(home.join(".codex"))
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        .filter_map(|p| {
            let name = p.file_name()?.to_str()?;
            let version = name
                .strip_prefix("state_")?
                .strip_suffix(".sqlite")?
                .parse::<u64>()
                .ok()?;
            Some((version, p))
        })
        .collect::<Vec<_>>();
    databases.sort_by_key(|(v, _)| *v);
    if let Some((_, db)) = databases.last() {
        let table = Command::new("sqlite3")
            .args(["-readonly", "-json"])
            .arg(db)
            .arg("PRAGMA table_info(threads)")
            .output()
            .context("read Codex transcript index with installed sqlite3")?;
        ensure!(
            table.status.success(),
            "read-only Codex index: {}",
            String::from_utf8_lossy(&table.stderr)
        );
        let columns: Vec<Value> = serde_json::from_slice(&table.stdout)?;
        let names: BTreeSet<_> = columns.iter().filter_map(|r| r["name"].as_str()).collect();
        let title = ["name", "title", "agent_nickname"]
            .iter()
            .filter(|n| names.contains(**n))
            .map(|n| format!("nullif({n}, '')"))
            .chain(std::iter::once("''".into()))
            .collect::<Vec<_>>()
            .join(", ");
        let repo = main
            .file_name()
            .and_then(|n| n.to_str())
            .unwrap_or("homesodamachine")
            .replace('\'', "''");
        let query = format!(
            "SELECT id, rollout_path, coalesce({title}) AS title FROM threads WHERE cwd LIKE '%/{repo}%' AND rollout_path IS NOT NULL"
        );
        let output = Command::new("sqlite3")
            .args(["-readonly", "-json"])
            .arg(db)
            .arg(query)
            .output()?;
        ensure!(
            output.status.success(),
            "read-only Codex index: {}",
            String::from_utf8_lossy(&output.stderr)
        );
        let rows: Vec<Value> = if output.stdout.is_empty() {
            Vec::new()
        } else {
            serde_json::from_slice(&output.stdout)?
        };
        for row in rows {
            sessions.push(Session {
                agent: "codex".into(),
                sid: s(&row, "id").into(),
                path: PathBuf::from(s(&row, "rollout_path")),
                title: s(&row, "title").into(),
                ..Session::default()
            });
        }
    }
    Ok(sessions)
}
pub fn gather(root: &Path, home: &Path, days: f64) -> Result<Reading> {
    let began = crate::now();
    let since = began - days * 86400.;
    let since_text = date(since, "%Y-%m-%dT%H:%M:%S", true);
    let reader = Arc::new(Reader::new(root)?);
    let sessions = sessions(root, home)?
        .into_iter()
        .filter(|s| {
            std::fs::metadata(&s.path).is_ok_and(|m| {
                m.modified()
                    .ok()
                    .and_then(|t| t.duration_since(std::time::UNIX_EPOCH).ok())
                    .is_some_and(|d| d.as_secs_f64() >= since)
            })
        })
        .collect::<Vec<_>>();
    let bytes: u64 = sessions
        .iter()
        .filter_map(|s| std::fs::metadata(&s.path).ok())
        .filter(offloaded)
        .map(|m| m.len())
        .sum();
    eprintln!(
        "reading {} transcripts, {:.1} GB of them from iCloud",
        sessions.len(),
        bytes as f64 / 1e9
    );
    let pending = Mutex::new(sessions.into_iter());
    let complete = Mutex::new(Vec::new());
    std::thread::scope(|scope| {
        for _ in 0..16 {
            let reader = &reader;
            let pending = &pending;
            let complete = &complete;
            let since_text = &since_text;
            scope.spawn(move || {
                loop {
                    let Some(mut session) = pending.lock().unwrap().next() else {
                        break;
                    };
                    if let Ok(metadata) = std::fs::metadata(&session.path) {
                        if offloaded(&metadata) {
                            session.downloaded = metadata.len();
                        }
                    }
                    let read = if session.agent == "claude" {
                        session.claude(reader, since_text)
                    } else {
                        session.codex(reader, since_text)
                    };
                    if let Err(error) = read {
                        eprintln!("  could not read {}: {error}", session.path.display());
                    }
                    complete.lock().unwrap().push(session);
                }
            });
        }
    });
    let mut sessions = complete.into_inner().unwrap();
    sessions.sort_by(|a, b| (a.fork, &a.path).cmp(&(b.fork, &b.path)));
    let mut scripts = Vec::new();
    let mut waits = Vec::new();
    let mut seen = BTreeSet::new();
    let mut titles = BTreeMap::new();
    let mut downloaded = 0;
    let mut unique = BTreeSet::new();
    for session in sessions {
        unique.insert((session.agent.clone(), session.sid.clone()));
        titles.insert(session.sid, session.title);
        downloaded += session.downloaded;
        for script in session.scripts {
            if seen.insert(script.key.clone()) {
                scripts.push(script);
            }
        }
        for mut wait in session.waits {
            if seen.insert(format!("wait:{}", wait.id)) {
                wait.what = wait.what.split_whitespace().collect::<Vec<_>>().join(" ");
                waits.push(wait);
            }
        }
    }
    let made = crate::now();
    let reading = Reading {
        days,
        since,
        made,
        seconds: made - began,
        sessions: unique.len(),
        downloaded,
        titles,
        scripts,
        waits,
    };
    crate::write_json(&root.join(".cache/missing_tools.json"), &reading)?;
    Ok(reading)
}
fn label(reading: &Reading, agent: &str, sid: &str) -> String {
    format!(
        "{} [{agent} {}]",
        reading
            .titles
            .get(sid)
            .filter(|s| !s.is_empty())
            .map_or("(untitled)", String::as_str),
        sid.chars().take(8).collect::<String>()
    )
}
fn short(text: &str, n: usize) -> String {
    text.chars().take(n).collect()
}
pub fn cli(root: &Path, args: &[String]) -> Result<i32> {
    let mut days: f64 = 7.;
    let mut show = None;
    let mut top = 15;
    let mut min_wait = 120.;
    let mut it = args.iter();
    while let Some(arg) = it.next() {
        match arg.as_str() {
            "--days" => days = it.next().context("--days needs a duration")?.parse()?,
            "--show" => show = Some(it.next().context("--show needs a row")?.as_str()),
            "--top" => top = it.next().context("--top needs a row count")?.parse()?,
            "--min-wait" => min_wait = it.next().context("--min-wait needs seconds")?.parse()?,
            "--help" | "-h" => {
                println!(
                    "repo-tools missing-tools [--days days] [--show ROW] [--top rows] [--min-wait seconds]\nReads repository Claude/Codex transcripts on request, including iCloud files. --show reuses a reading of the same window for up to twelve hours. The Codex index uses installed sqlite3 in read-only mode."
                );
                return Ok(0);
            }
            _ => anyhow::bail!("unknown missing-tools option {arg}"),
        }
    }
    ensure!(
        days.is_finite() && days >= 0.,
        "--days must be a finite nonnegative duration"
    );
    let cached = show
        .and_then(|_| crate::text(root.join(".cache/missing_tools.json")).ok())
        .and_then(|s| serde_json::from_str::<Reading>(&s).ok())
        .filter(|r| r.days == days && crate::now() - r.made < 12. * 3600.);
    let home = PathBuf::from(std::env::var_os("HOME").context("HOME for agent transcripts")?);
    let reading = if let Some(cached) = cached {
        cached
    } else {
        gather(root, &home, days)?
    };
    if let Some(row) = show {
        let mut hits = reading
            .scripts
            .iter()
            .filter(|s| s.reads.iter().any(|r| r == row))
            .collect::<Vec<_>>();
        hits.sort_by_key(|s| &s.ts);
        let mut codes = BTreeSet::new();
        let mut sessions = BTreeSet::new();
        for script in &hits {
            sessions.insert((&script.agent, &script.sid));
            if !codes.insert(&script.code) {
                continue;
            }
            let lines: Vec<_> = script.code.trim_matches('\n').lines().collect();
            println!(
                "\n== {}  {}\n   {}",
                short(&script.ts, 16).replace('T', " "),
                label(&reading, &script.agent, &script.sid),
                short(&script.gist, 110)
            );
            for l in lines.iter().take(80) {
                println!("   | {l}");
            }
            if lines.len() > 80 {
                println!("   | ... {} more lines", lines.len() - 80);
            }
        }
        println!(
            "\n{} scripts read {row}, {} of them different, in {} sessions",
            hits.len(),
            codes.len(),
            sessions.len()
        );
        return Ok(0);
    }
    let script_sessions: BTreeSet<_> = reading.scripts.iter().map(|s| (&s.agent, &s.sid)).collect();
    println!(
        "Code agents wrote for themselves, {} to {}: {} scripts in {} of {} sessions ({:.1} GB downloaded, {:.0} s)",
        date(reading.since, "%b %e", false),
        date(reading.made, "%b %e", false),
        reading.scripts.len(),
        script_sessions.len(),
        reading.sessions,
        reading.downloaded as f64 / 1e9,
        reading.seconds
    );
    let mut rows = BTreeMap::<&str, (usize, BTreeMap<(&str, &str), &Script>)>::new();
    for script in &reading.scripts {
        for key in &script.reads {
            let row = rows.entry(key).or_default();
            row.0 += 1;
            row.1.entry((&script.agent, &script.sid)).or_insert(script);
        }
    }
    let mut rows = rows
        .into_iter()
        .filter(|(_, (_, sessions))| sessions.len() > 1)
        .collect::<Vec<_>>();
    rows.sort_by(|a, b| {
        b.1.1
            .len()
            .cmp(&a.1.1.len())
            .then_with(|| b.1.0.cmp(&a.1.0))
            .then_with(|| a.0.cmp(b.0))
    });
    println!("\nWhat that code read, shared by more than one session\n  sessions  scripts  read");
    for (key, (count, sessions)) in rows.into_iter().take(top) {
        println!("  {:8}  {count:7}  {key}", sessions.len());
        for ((agent, sid), script) in sessions.into_iter().take(2) {
            println!(
                "                     {:64}  {}",
                short(&script.gist, 64),
                short(&label(&reading, agent, sid), 48)
            );
        }
    }
    let mut waits = reading
        .waits
        .iter()
        .filter(|w| w.seconds >= min_wait)
        .collect::<Vec<_>>();
    waits.sort_by(|a, b| b.seconds.total_cmp(&a.seconds));
    let mut spans = BTreeMap::<(&str, &str), Vec<(f64, f64)>>::new();
    for w in &waits {
        let lo = stamp(&w.t0);
        spans
            .entry((&w.agent, &w.sid))
            .or_default()
            .push((lo, lo + w.seconds));
    }
    let mut held = 0.;
    for spans in spans.values_mut() {
        spans.sort_by(|a, b| a.0.total_cmp(&b.0));
        let mut end = -1_f64;
        for (lo, hi) in spans {
            held += (*hi - lo.max(end)).max(0.);
            end = end.max(*hi);
        }
    }
    println!(
        "\nWaits of {} min or more: {}, holding their sessions {:.1} h in all",
        min_wait / 60.,
        waits.len(),
        held / 3600.
    );
    for wait in waits.into_iter().take(top) {
        println!(
            "  {:6.1} min  {}  {:64}  {}",
            wait.seconds / 60.,
            short(&wait.t0, 10),
            short(&wait.what, 64),
            short(&label(&reading, &wait.agent, &wait.sid), 48)
        );
    }
    Ok(0)
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn inline_interpreters_and_scratch_writes() {
        assert_eq!(inline_code("python3 - <<'PY'\nprint('hardware/a.step')\nPY\ncat > /tmp/scan.rs <<'RS'\nuse hsm_kernel::V3;\nRS").unwrap(),vec!["print('hardware/a.step')","use hsm_kernel::V3;"]);
        assert_eq!(
            js_commands("await tools.exec_command({cmd: \"python3 -c 'print(1)'\"})").unwrap(),
            vec!["python3 -c 'print(1)'"]
        );
    }
    #[test]
    fn utc_fractional_timestamps() {
        assert!(
            (stamp("2026-11-10T14:24:01.250Z") - stamp("2026-11-10T14:24:00Z") - 1.25).abs() < 1e-9
        );
    }
    #[test]
    fn yielded_cell_and_process_polls_count_only_time_held() {
        let path = std::env::temp_dir().join(format!(
            "hsm-discovery-{}-{}.jsonl",
            std::process::id(),
            crate::now().to_bits()
        ));
        let reader = Reader {
            root: PathBuf::from("/repo"),
            tops: BTreeSet::from(["hardware".into()]),
            modules: BTreeMap::new(),
            path_rx: Regex::new(r"hardware/[\w.\-/*{}@+]+").unwrap(),
            import_rx: Regex::new(r"(?m)^from ([\w.]+) import ([\w, ]+)|^import ([\w, ]+)")
                .unwrap(),
            crate_rx: Regex::new(r"\buse\s+(\w+)").unwrap(),
        };
        let event = |time: &str, payload: Value| serde_json::json!({"timestamp":format!("2026-11-10T00:00:{time}Z"),"payload":payload});
        let command =
            "python3 - <<'PY'\n# Read the payload\nprint('hardware/sample.step.mesh')\nPY";
        let input = format!(
            "await tools.exec_command({{cmd:{}}})",
            serde_json::to_string(command).unwrap()
        );
        let values = [
            event(
                "00",
                serde_json::json!({"type":"custom_tool_call","name":"exec","call_id":"start","input":input}),
            ),
            event(
                "02",
                serde_json::json!({"type":"custom_tool_call_output","call_id":"start","output":"Script running with cell ID cell_a"}),
            ),
            event(
                "03",
                serde_json::json!({"type":"function_call","name":"wait","call_id":"cell_wait","arguments":"{\"cell_id\":\"cell_a\"}"}),
            ),
            event(
                "06",
                serde_json::json!({"type":"function_call_output","call_id":"cell_wait","output":"{\"session_id\":9}"}),
            ),
            event(
                "07",
                serde_json::json!({"type":"custom_tool_call","name":"exec","call_id":"poll_1","input":"await tools.write_stdin({session_id:9})"}),
            ),
            event(
                "10",
                serde_json::json!({"type":"custom_tool_call_output","call_id":"poll_1","output":"{\"session_id\":9}"}),
            ),
            event(
                "11",
                serde_json::json!({"type":"custom_tool_call","name":"exec","call_id":"poll_2","input":"await tools.write_stdin({session_id:9})"}),
            ),
            event(
                "14",
                serde_json::json!({"type":"custom_tool_call_output","call_id":"poll_2","output":"Process exited with code 0"}),
            ),
        ];
        std::fs::write(
            &path,
            values
                .iter()
                .map(Value::to_string)
                .collect::<Vec<_>>()
                .join("\n"),
        )
        .unwrap();
        let mut session = Session {
            agent: "codex".into(),
            sid: "fixture".into(),
            path: path.clone(),
            ..Session::default()
        };
        session.codex(&reader, "2026-11-09").unwrap();
        std::fs::remove_file(path).unwrap();
        assert_eq!(session.scripts.len(), 1);
        assert_eq!(session.scripts[0].reads, vec!["*.step.mesh"]);
        assert_eq!(session.waits.len(), 1);
        assert_eq!(session.waits[0].seconds, 11.);
        assert_eq!(session.waits[0].id, "start");
    }
    #[test]
    fn codex_index_uses_available_title_columns_read_only() {
        let root = std::env::temp_dir().join(format!(
            "hsm-transcript-index-{}-{}",
            std::process::id(),
            crate::now().to_bits()
        ));
        let home = root.join("fixture-home");
        let codex = home.join(".codex");
        std::fs::create_dir_all(&codex).unwrap();
        assert!(
            Command::new("git")
                .args(["init", "--quiet"])
                .arg(&root)
                .status()
                .unwrap()
                .success()
        );
        let db = codex.join("state_1.sqlite");
        let cwd = root.to_string_lossy().replace('\'', "''");
        let sql = format!(
            "CREATE TABLE threads(id TEXT, rollout_path TEXT, title TEXT, cwd TEXT); INSERT INTO threads VALUES('fixture-id','/fixture/rollout.jsonl','Synthetic title','{cwd}');"
        );
        assert!(
            Command::new("sqlite3")
                .arg(&db)
                .arg(sql)
                .status()
                .unwrap()
                .success()
        );
        let before = std::fs::read(&db).unwrap();
        let found = sessions(&root, &home).unwrap();
        assert_eq!(found.len(), 1);
        assert_eq!(found[0].sid, "fixture-id");
        assert_eq!(found[0].title, "Synthetic title");
        assert_eq!(std::fs::read(db).unwrap(), before);
        std::fs::remove_dir_all(root).unwrap();
    }
}
