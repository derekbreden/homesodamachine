//! Path readings resolve authored links against the checkout, fetched solids, literal site routes and named archived revisions.
use anyhow::{Result, ensure};
use regex::Regex;
use std::{
    collections::{BTreeMap, BTreeSet},
    path::Path,
};
const SOURCE: &[&str] = &[
    "py", "rs", "cpp", "c", "h", "hpp", "js", "mjs", "ts", "tsx", "sh", "swift", "kt", "mmd",
];
const KNOWN: &[&str] = &[
    "md", "py", "rs", "js", "mjs", "ts", "tsx", "json", "cpp", "c", "h", "hpp", "sh", "swift",
    "kt", "mmd", "step", "stl", "3mf", "dxf", "svg", "png", "jpg", "jpeg", "glb", "pdf", "csv",
    "html", "css", "yaml", "yml", "xml", "ini", "toml", "lock", "txt", "bazel", "tsv",
];
const SYSTEM: &[&str] = &[
    "tmp", "Users", "home", "opt", "usr", "var", "private", "etc", "dev", "mnt", "proc", "root",
    "srv", "sys", "bin", "sbin", "lib", "Volumes",
];
const SKIP: &[&str] = &[
    "node_modules/",
    "tools/cad-venv/",
    "tools/pcb-venv/",
    "tools/video-venv/",
    "tools/hsm/vendor/",
    ".pio/",
];
fn extension(s: &str) -> &str {
    s.rsplit_once('.').map_or("", |(_, ext)| ext)
}
fn boundary(text: &str, at: usize, extra: &str) -> bool {
    text[..at]
        .chars()
        .next_back()
        .is_none_or(|c| !c.is_alphanumeric() && c != '_' && !extra.contains(c))
}
fn placeholder(path: &str) -> bool {
    if ["...", "*", "{", "}", "$", "%s", "XX", "NN", "_N."]
        .iter()
        .any(|p| path.contains(p))
    {
        return true;
    }
    path.split('/').any(|s| {
        [
            "foo", "bar", "baz", "qux", "path", "to", "NAME", "name", "<board>", "<name>", "<dir>",
            "<n>", "a", "b", "x", "y",
        ]
        .contains(&s)
            || (s.starts_with('<')
                && s.ends_with('>')
                && !s.contains(char::is_whitespace)
                && !KNOWN.contains(&extension(&s[1..s.len() - 1])))
    })
}
fn normalize(path: &str) -> String {
    let mut parts = Vec::new();
    for part in path.split('/') {
        match part {
            "" | "." => {}
            ".." if parts.last().is_some_and(|p| *p != "..") => {
                parts.pop();
            }
            other => parts.push(other),
        }
    }
    if parts.is_empty() {
        ".".into()
    } else {
        parts.join("/")
    }
}
fn parent(path: &str) -> &str {
    path.rsplit_once('/').map_or(".", |(p, _)| p)
}
fn line(text: &str, offset: usize) -> usize {
    text.as_bytes()[..offset]
        .iter()
        .filter(|c| **c == b'\n')
        .count()
        + 1
}
fn fences(text: &str) -> String {
    let mut inside = false;
    text.split('\n')
        .map(|l| {
            if l.trim_start().starts_with("```") {
                inside = !inside;
                ""
            } else if inside {
                ""
            } else {
                l
            }
        })
        .collect::<Vec<_>>()
        .join("\n")
}
fn code_spans(text: &str) -> String {
    let b = text.as_bytes();
    let mut out = b.to_vec();
    let mut i = 0;
    while i < b.len() {
        if b[i] != b'`' {
            i += 1;
            continue;
        }
        let start = i;
        while i < b.len() && b[i] == b'`' {
            i += 1;
        }
        let n = i - start;
        let mut j = i;
        while j < b.len() && b[j] != b'\n' {
            if b[j..].starts_with(&b[start..i]) {
                out[start..j + n].fill(b' ');
                i = j + n;
                break;
            }
            j += 1;
        }
    }
    String::from_utf8(out).expect("blanked code spans")
}
fn md_targets(text: &str) -> Result<Vec<(usize, String)>> {
    let text = text
        .split("## Sources\n[value](NAME) texts are updated by:\n- `")
        .next()
        .unwrap_or(text);
    let body = code_spans(&fences(text));
    let pattern = Regex::new(r"\[[^\]]*\]\(([^)]+)\)")?;
    let marker = Regex::new(r"^[A-Z_][A-Z0-9_]*$")?;
    let mut out = Vec::new();
    for m in pattern.captures_iter(&body) {
        let whole = m.get(0).unwrap();
        if whole.start() > 0 && body.as_bytes()[whole.start() - 1] == b'!' {
            continue;
        }
        let target = m[1].trim();
        let target = if target.starts_with('<') && target.ends_with('>') {
            &target[1..target.len() - 1]
        } else {
            target
        };
        if ["http://", "https://", "mailto:", "tel:", "#", "data:"]
            .iter()
            .any(|p| target.starts_with(p))
            || marker.is_match(target)
        {
            continue;
        }
        out.push((line(&body, whole.start()), target.to_owned()));
    }
    Ok(out)
}
// The lexer keeps source comments and Python docstrings while retaining source line positions.
fn comments(rel: &str, text: &str) -> String {
    let b = text.as_bytes();
    let mut out = vec![b' '; b.len()];
    for (i, c) in b.iter().enumerate() {
        if *c == b'\n' {
            out[i] = *c;
        }
    }
    let hash = rel.ends_with(".sh") || rel.ends_with(".py");
    let python = rel.ends_with(".py");
    let pct = rel.ends_with(".mmd");
    let mut i = 0;
    while i < b.len() {
        if python && (b[i..].starts_with(b"\"\"\"") || b[i..].starts_with(b"'''")) {
            let line_start = text[..i].rfind('\n').map_or(0, |n| n + 1);
            let docstring = text[line_start..i].trim().is_empty();
            let q = &b[i..i + 3];
            let start = i;
            i += 3;
            while i < b.len() && !b[i..].starts_with(q) {
                i += 1;
            }
            i = (i + 3).min(b.len());
            if docstring {
                out[start..i].copy_from_slice(&b[start..i]);
            }
            continue;
        }
        if !hash && !pct && b[i] == b'r' {
            let mut q = i + 1;
            while q < b.len() && b[q] == b'#' {
                q += 1;
            }
            if q < b.len() && b[q] == b'"' {
                let mut end = vec![b'"'];
                end.extend_from_slice(&b[i + 1..q]);
                i = q + 1;
                while i < b.len() && !b[i..].starts_with(&end) {
                    i += 1;
                }
                i = (i + end.len()).min(b.len());
                continue;
            }
        }
        if b[i] == b'"'
            || b[i] == b'`'
            || b[i] == b'\'' && (hash || b[i + 1..].iter().take(6).any(|c| *c == b'\''))
        {
            let quote = b[i];
            i += 1;
            while i < b.len() {
                if b[i] == b'\\' {
                    i = (i + 2).min(b.len());
                } else if b[i] == quote {
                    i += 1;
                    break;
                } else {
                    i += 1;
                }
            }
            continue;
        }
        let one = hash && b[i] == b'#'
            || pct && b[i..].starts_with(b"%%")
            || !hash && !pct && b[i..].starts_with(b"//");
        if one {
            let start = i;
            while i < b.len() && b[i] != b'\n' {
                i += 1;
            }
            out[start..i].copy_from_slice(&b[start..i]);
            continue;
        }
        if !hash && !pct && b[i..].starts_with(b"/*") {
            let start = i;
            let mut depth = 1;
            i += 2;
            while i < b.len() && depth != 0 {
                if b[i..].starts_with(b"/*") {
                    depth += 1;
                    i += 2;
                } else if b[i..].starts_with(b"*/") {
                    depth -= 1;
                    i += 2;
                } else {
                    i += 1;
                }
            }
            out[start..i].copy_from_slice(&b[start..i]);
            continue;
        }
        i += 1;
    }
    String::from_utf8(out).expect("comments preserve complete source characters")
}
fn source_targets(rel: &str, text: &str) -> Result<Vec<(usize, String)>> {
    let body = comments(rel, text);
    let rx = Regex::new(r"/?[A-Za-z0-9_][A-Za-z0-9_.-]*(?:/[A-Za-z0-9_.-]+)+")?;
    Ok(rx
        .find_iter(&body)
        .filter(|m| boundary(&body, m.start(), "./-"))
        .filter_map(|m| {
            let target = m
                .as_str()
                .trim_end_matches(['.', ',', ';', ':', ')', '"', '\'', '`']);
            KNOWN
                .contains(&extension(target))
                .then(|| (line(&body, m.start()), target.to_owned()))
        })
        .collect())
}
fn clean(target: &str) -> String {
    let path = target.split(['#', '?']).next().unwrap_or("");
    let suffix = Regex::new(r":\d+(?:-\d+)?$").unwrap();
    suffix
        .replace(path, "")
        .trim_end_matches(['.', ',', ';', ':', ')', '"', '\'', '`'])
        .to_owned()
}
fn blocks(text: &str) -> Vec<(usize, String)> {
    let mut out = Vec::new();
    let (mut start, mut current) = (0, String::new());
    for (i, l) in text.split('\n').enumerate() {
        if l.trim().is_empty() {
            if !current.is_empty() {
                out.push((start, std::mem::take(&mut current)));
            }
        } else {
            if current.is_empty() {
                start = i + 1;
            } else {
                current.push('\n');
            }
            current.push_str(l);
        }
    }
    if !current.is_empty() {
        out.push((start, current));
    }
    out
}
fn routes(text: &str) -> Result<BTreeSet<String>> {
    let rx = Regex::new(r#"\bapp\.get\(\s*["'](/[^"'\n]*)["']"#)?;
    Ok(rx
        .captures_iter(text)
        .filter(|c| !c[1].contains([':', '*']))
        .map(|c| c[1].to_owned())
        .collect())
}
struct Revisions<'a> {
    root: &'a Path,
    commits: BTreeMap<String, bool>,
    paths: BTreeMap<(String, String), bool>,
}
impl Revisions<'_> {
    fn commit(&mut self, r: &str) -> bool {
        *self.commits.entry(r.into()).or_insert_with(|| {
            crate::command(
                self.root,
                "git",
                &[
                    "rev-parse",
                    "--verify",
                    "--quiet",
                    &format!("{r}^{{commit}}"),
                ],
            )
            .is_ok_and(|r| r.status.success())
        })
    }
    fn holds(&mut self, r: &str, p: &str) -> bool {
        *self.paths.entry((r.into(), p.into())).or_insert_with(|| {
            crate::command(self.root, "git", &["cat-file", "-e", &format!("{r}:{p}")])
                .is_ok_and(|r| r.status.success())
        })
    }
}
fn reference_words(text: &str) -> Result<Vec<(usize, String)>> {
    let rx = Regex::new(r"(?:archive|superseded|pattern)[\w./-]*|[\w.-]*-last-known")?;
    Ok(rx
        .find_iter(text)
        .filter(|m| boundary(text, m.start(), "/-"))
        .map(|m| {
            (
                line(text, m.start()),
                m.as_str()
                    .trim_end_matches(['.', ',', ';', ':', '`'])
                    .to_owned(),
            )
        })
        .collect())
}
pub fn scan(root: &Path) -> Result<(Vec<String>, [usize; 4])> {
    let listed = crate::command(root, "git", &["ls-files", "-z"])?;
    ensure!(listed.status.success(), "read git index");
    let files: BTreeSet<_> = String::from_utf8_lossy(&listed.stdout)
        .split('\0')
        .filter(|p| !p.is_empty())
        .map(str::to_owned)
        .collect();
    let mut dirs = BTreeSet::new();
    for file in &files {
        let mut p = parent(file);
        while p != "." {
            dirs.insert(p.to_owned());
            p = parent(p);
        }
    }
    let mut held = files.clone();
    held.extend(dirs);
    let solids = crate::text(root.join("hardware/cad-artifacts.json"))
        .ok()
        .and_then(|s| serde_json::from_str::<serde_json::Value>(&s).ok())
        .and_then(|v| {
            v["solids"]
                .as_object()
                .map(|o| o.keys().cloned().collect::<BTreeSet<_>>())
        })
        .unwrap_or_default();
    held.extend(solids.iter().cloned());
    let tags: BTreeSet<_> = crate::git(root, &["tag", "-l"])?
        .lines()
        .map(str::to_owned)
        .collect();
    let mut site = BTreeSet::new();
    for file in files
        .iter()
        .filter(|p| p.starts_with("web/") && ["js", "mjs"].contains(&extension(p)))
    {
        if let Ok(text) = crate::text(root.join(file)) {
            site.extend(routes(&text)?);
        }
    }
    let top: BTreeSet<_> = files
        .iter()
        .filter_map(|f| f.split_once('/').map(|(h, _)| h))
        .filter(|h| !h.contains('.'))
        .collect();
    let pinned = hsm_build_data::inventory::pinned(root, &files)?;
    let mut revisions = Revisions {
        root,
        commits: BTreeMap::new(),
        paths: BTreeMap::new(),
    };
    let mut bad = Vec::new();
    let sha = Regex::new(r"[0-9a-f]{8,40}")?;
    let blob = Regex::new(
        r#"https://github\.com/([\w.-]+/[\w.-]+)/blob/([0-9a-f]{7,40})/([^)\s#"'<>]+)"#,
    )?;
    let revision = Regex::new(r"([\w.][\w./-]*):([\w][\w./-]*\.[\w]+|[\w][\w./-]*/)")?;
    for rel in files.iter().filter(|p| {
        let ext = extension(p);
        (ext == "md" || SOURCE.contains(&ext))
            && !SKIP.iter().any(|s| p.starts_with(s))
            && !(p.starts_with("calibration/") && p["calibration/".len()..].contains('/'))
            && !pinned.contains(*p)
            && p.as_str() != "tools/hsm/repo-tools/src/paths.rs"
    }) {
        let Ok(text) = crate::text(root.join(rel)) else {
            continue;
        };
        let md = extension(rel) == "md";
        let body = if md {
            fences(&text)
        } else {
            comments(rel, &text)
        };
        let targets = if md {
            md_targets(&text)?
        } else {
            source_targets(rel, &text)?
        };
        let blocks = blocks(&body);
        for (line, word) in reference_words(&body)? {
            if (word.starts_with("archive-")
                || word.starts_with("superseded-")
                || word.ends_with("-last-known"))
                && !tags.contains(&word)
            {
                bad.push(format!(
                    "{rel}:{line} — `{word}` is named as a tag; no such tag"
                ));
            }
        }
        for (line, target) in targets {
            let path = clean(&target);
            if path.is_empty() || placeholder(&path) {
                continue;
            }
            let mut candidates = if path.starts_with('/') {
                if site.contains(if path.trim_end_matches('/').is_empty() {
                    "/"
                } else {
                    path.trim_end_matches('/')
                }) {
                    continue;
                }
                vec![if let Some(reader) = path.strip_prefix("/read/") {
                    format!("hardware/{reader}")
                } else {
                    path.trim_start_matches('/').to_owned()
                }]
            } else if md {
                vec![format!("{}/{path}", parent(rel))]
            } else {
                let head = path.split('/').next().unwrap_or("");
                let own = rel.split('/').next().unwrap_or("");
                let sibling = format!("{}/{path}", parent(rel));
                let top_path = format!("{own}/{path}");
                let hw = format!("hardware/{path}");
                if top.contains(head) {
                    vec![path.clone(), sibling, top_path, hw]
                } else {
                    vec![top_path, sibling, hw, path.clone()]
                }
            };
            for c in &mut candidates {
                *c = normalize(c);
            }
            if candidates
                .iter()
                .any(|c| held.contains(c) || root.join(c).exists())
            {
                continue;
            }
            let mut nearest = candidates
                .iter()
                .find(|c| held.contains(parent(c)))
                .unwrap_or(&candidates[0])
                .clone();
            let block = blocks
                .iter()
                .rev()
                .find(|(start, _)| *start <= line)
                .map_or("", |(_, b)| b.as_str());
            let mut refs: BTreeSet<_> = reference_words(block)?
                .into_iter()
                .map(|(_, r)| r)
                .filter(|r| tags.contains(r))
                .collect();
            for m in sha.find_iter(block).filter(|m| {
                boundary(block, m.start(), "/")
                    && block[m.end()..]
                        .chars()
                        .next()
                        .is_none_or(|c| !c.is_alphanumeric() && c != '_' && c != '/')
            }) {
                if revisions.commit(m.as_str()) {
                    refs.insert(m.as_str().to_owned());
                }
            }
            if refs
                .iter()
                .any(|r| candidates.iter().any(|c| revisions.holds(r, c)))
            {
                continue;
            }
            for r in &refs {
                if let Some(near) = candidates.iter().find(|c| revisions.holds(r, parent(c))) {
                    nearest = near.clone();
                    break;
                }
            }
            if !md {
                let head = path.trim_start_matches('/').split('/').next().unwrap_or("");
                if SYSTEM.contains(&head) || !top.contains(head) && refs.is_empty() {
                    continue;
                }
            }
            bad.push(if refs.is_empty() {
                format!("{rel}:{line} — {nearest} is held nowhere, and no tag is named for it")
            } else {
                format!(
                    "{rel}:{line} — {nearest} is not at HEAD, and not at {} either",
                    refs.into_iter().collect::<Vec<_>>().join(", ")
                )
            });
        }
        for m in blob.captures_iter(&body) {
            if m[1].to_lowercase() != "derekbreden/homesodamachine" {
                continue;
            }
            let line = line(&body, m.get(0).unwrap().start());
            let (r, p) = (&m[2], &m[3]);
            if !revisions.commit(r) {
                bad.push(format!("{rel}:{line} — blob URL pinned to {r}, a commit this repo does not have; tools/git-history/commit-map names its successor"));
            } else if !revisions.holds(r, p) {
                bad.push(format!(
                    "{rel}:{line} — {p} is not at {r}, which its blob URL pins it to"
                ));
            }
        }
        for m in revision.captures_iter(&body) {
            if !boundary(&body, m.get(0).unwrap().start(), "/:-") {
                continue;
            }
            let (r, p) = (&m[1], m[2].trim_end_matches('/'));
            if tags.contains(r) && !placeholder(p) && !revisions.holds(r, p) {
                bad.push(format!(
                    "{rel}:{} — {r}:{p} does not resolve at that tag",
                    line(&body, m.get(0).unwrap().start())
                ));
            }
        }
    }
    Ok((bad, [files.len(), solids.len(), tags.len(), site.len()]))
}
fn selftest() -> Result<()> {
    ensure!(
        md_targets("Eleven [11](VALVE_COUNT) valves, see [bom](/hardware/ledger/bom.md).")?
            == vec![(1, "/hardware/ledger/bom.md".into())],
        "substitution marker"
    );
    ensure!(
        md_targets("```\n[x](/nope.md)\n```\n[y](/hardware/README.md)")?
            == vec![(4, "/hardware/README.md".into())],
        "fenced notation"
    );
    ensure!(
        md_targets("[a](</hardware/ledger/bom.md>)")?
            == vec![(1, "/hardware/ledger/bom.md".into())],
        "bracketed URL"
    );
    ensure!(
        md_targets("Links read `[text](href)`; see [y](/hardware/README.md).")?
            == vec![(1, "/hardware/README.md".into())],
        "inline code"
    );
    ensure!(
        clean("/hardware/pcb/pcba/pcba.tsx:210") == "/hardware/pcb/pcba/pcba.tsx",
        "line suffix"
    );
    ensure!(
        clean("/hardware/README.md#parts") == "/hardware/README.md",
        "fragment"
    );
    ensure!(
        routes("app.get(\"/drawings\", h); app.get(\"/tour/:step\", h); app.post(\"/api/x\", h);")?
            == BTreeSet::from(["/drawings".into()]),
        "literal routes"
    );
    ensure!(
        source_targets(
            "x.js",
            "const u = \"https://e.com/hardware/no.md\"; // hardware/yes.md\n"
        )? == vec![(1, "hardware/yes.md".into())],
        "comment outside a string"
    );
    ensure!(
        source_targets("x.js", "const g = \"/*\";\nfoo(\"hardware/no.md\");\n")?.is_empty(),
        "block token in string"
    );
    ensure!(
        source_targets(
            "x.py",
            "\"\"\"See hardware/a.md.\"\"\"\n# and hardware/b.md\nP = \"hardware/c.md\"\n"
        )? == vec![(1, "hardware/a.md".into()), (2, "hardware/b.md".into())],
        "Python comments and docstring"
    );
    ensure!(
        source_targets(
            "x.rs",
            "let raw = r#\"// hardware/no.md\"#; // hardware/yes.rs\n"
        )? == vec![(1, "hardware/yes.rs".into())],
        "Rust raw string"
    );
    for p in [
        "hardware/foo/bar/foo_bar.py",
        "hardware/path/to/x.svg",
        "web/.../pcb-pick.js",
        "hardware/<board>/x.md",
    ] {
        ensure!(placeholder(p), "placeholder {p}");
    }
    ensure!(
        !placeholder("sessions/<Comments are a code smell.md>"),
        "malformed filename is a finding"
    );
    ensure!(!placeholder("hardware/ledger/bom.md"), "real path");
    ensure!(
        blocks("a\nb\n\nc")
            .iter()
            .map(|(n, _)| *n)
            .collect::<Vec<_>>()
            == vec![1, 4],
        "paragraph span"
    );
    ensure!(
        normalize("hardware/../web/lib/./shell.js") == "web/lib/shell.js",
        "collapsed reference"
    );
    Ok(())
}
pub fn cli(root: &Path, args: &[String]) -> Result<i32> {
    if args.first().is_some_and(|a| a == "selftest") {
        selftest()?;
        println!("paths selftest: every rule holds");
        return Ok(0);
    }
    ensure!(args.is_empty(), "paths accepts only selftest");
    let (bad, [files, solids, tags, routes]) = scan(root)?;
    if bad.is_empty() {
        println!(
            "paths: every reference lands — {files} tracked, {solids} fetched solids, {tags} tags, {routes} site routes"
        );
        Ok(0)
    } else {
        for finding in &bad {
            println!("  {finding}");
        }
        println!("\n{} reference(s) name a path nothing holds.", bad.len());
        Ok(1)
    }
}
#[cfg(test)]
mod tests {
    #[test]
    fn authored_reference_rules() {
        super::selftest().unwrap();
    }
}
