//! Managed document markers and deterministic document exports.
//!
//! Callers supply the source identity explicitly, so the same document and
//! sidecar are written from a native Rust generator or a compatibility driver.

use anyhow::{Context, Result, bail};
use serde::Serialize;
use std::collections::{BTreeMap, BTreeSet};
use std::fs::{self, OpenOptions};
use std::io::Write;
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicU64, Ordering};
use std::time::{SystemTime, UNIX_EPOCH};

pub type Variables = BTreeMap<String, String>;

#[derive(Clone, Copy, Debug)]
pub enum Kind {
    Markdown,
    Mermaid,
    Python,
}

#[derive(Debug, Serialize)]
pub struct Substitution {
    pub maintained: Vec<PathBuf>,
    pub changed: bool,
}

const SOURCES: &str = "## Sources\n[value](NAME) texts are updated by:\n";

/// The cells of a Markdown row, preserving an empty first or last cell.
pub fn cells(row: &str) -> Vec<String> {
    let mut parts: Vec<_> = row.split('|').collect();
    if parts.first().is_some_and(|s| s.trim().is_empty()) {
        parts.remove(0);
    }
    if parts.last().is_some_and(|s| s.trim().is_empty()) {
        parts.pop();
    }
    parts.into_iter().map(|s| s.trim().to_owned()).collect()
}

/// Every managed marker, as UTF-8 byte bounds and its value and name.
pub fn markers(text: &str) -> Vec<(usize, usize, &str, &str)> {
    let mut out = Vec::new();
    let mut pos = 0;
    while let Some(relative) = text[pos..].find('[') {
        let start = pos + relative;
        let Some(close) = text[start + 1..].find(']') else {
            break;
        };
        let close = start + 1 + close;
        let tail = &text[close + 1..];
        if let Some(rest) = tail.strip_prefix('(')
            && let Some(end) = rest.find(')')
        {
            let name = &rest[..end];
            let valid = name
                .as_bytes()
                .first()
                .is_some_and(|c| c.is_ascii_uppercase() || *c == b'_')
                && name
                    .bytes()
                    .all(|c| c.is_ascii_uppercase() || c.is_ascii_digit() || c == b'_');
            if valid {
                let end = close + 3 + end;
                out.push((start, end, &text[start + 1..close], name));
                pos = end;
                continue;
            }
        }
        // A failed outer '[' can contain a valid inner marker.
        pos = start + 1;
    }
    out
}

fn replace_markers(text: &str, variables: &Variables) -> String {
    let mut out = String::with_capacity(text.len());
    let mut pos = 0;
    for (start, end, _, name) in markers(text) {
        out.push_str(&text[pos..start]);
        if let Some(value) = variables.get(name) {
            out.push('[');
            out.push_str(value);
            out.push_str("](");
            out.push_str(name);
            out.push(')');
        } else {
            out.push_str(&text[start..end]);
        }
        pos = end;
    }
    out.push_str(&text[pos..]);
    out
}

/// Bounds of the first well-formed Sources block, including its bullets.
pub fn sources_section(text: &str) -> Option<(usize, usize)> {
    for (start, _) in text.match_indices(SOURCES) {
        let mut end = start + SOURCES.len();
        let first = end;
        while let Some(tail) = text[end..].strip_prefix("- `") {
            let Some(close) = tail.find(['`', '\n']) else {
                break;
            };
            if close == 0 || tail.as_bytes()[close] != b'`' {
                break;
            }
            let after = end + 3 + close + 1;
            if after == text.len() {
                end = after;
                break;
            }
            if text.as_bytes()[after] != b'\n' {
                break;
            }
            end = after + 1;
        }
        if end > first {
            return Some((start, end));
        }
    }
    None
}

fn render_sources(bullets: &BTreeSet<String>) -> String {
    let mut out = SOURCES.to_owned();
    for bullet in bullets {
        out.push_str("- `");
        out.push_str(bullet);
        out.push_str("`\n");
    }
    out
}

pub fn update_sources(text: &str, caller: &str) -> String {
    let mut text = text.to_owned();
    if !text.is_empty() && !text.ends_with('\n') {
        text.push('\n');
    }
    let mut paths = BTreeSet::from([caller.to_owned()]);
    if let Some((start, end)) = sources_section(&text) {
        for line in text[start + SOURCES.len()..end].lines() {
            if let Some(path) = line
                .trim()
                .strip_prefix("- `")
                .and_then(|s| s.strip_suffix('`'))
            {
                paths.insert(path.to_owned());
            }
        }
        return text[..start].to_owned() + &render_sources(&paths) + &text[end..];
    }
    if text.trim().is_empty() {
        render_sources(&paths)
    } else {
        text.trim_end().to_owned() + "\n\n" + &render_sources(&paths)
    }
}

pub fn markdown(text: &str, variables: &Variables, caller: Option<&str>) -> (String, Variables) {
    let split = sources_section(text).map_or(text.len(), |(start, _)| start);
    let (body, tail) = text.split_at(split);
    let carried = markers(body)
        .into_iter()
        .filter_map(|(_, _, _, name)| {
            variables
                .get(name)
                .map(|value| (name.to_owned(), value.clone()))
        })
        .collect();
    let mut text = replace_markers(body, variables) + tail;
    if let Some(caller) = caller {
        text = update_sources(&text, caller);
    }
    (text, carried)
}

pub fn mermaid(text: &str, variables: &Variables) -> String {
    text.split_inclusive('\n')
        .map(|line| {
            if line.trim_start().starts_with("%%") {
                replace_markers(line, variables)
            } else {
                line.to_owned()
            }
        })
        .collect()
}

fn string_end(bytes: &[u8], quote: usize) -> usize {
    let c = bytes[quote];
    let triple = bytes.get(quote..quote + 3) == Some(&[c, c, c]);
    let width = if triple { 3 } else { 1 };
    let mut pos = quote + width;
    while pos < bytes.len() {
        if bytes[pos] == b'\\' {
            pos = (pos + 2).min(bytes.len());
        } else if bytes[pos] == c && (!triple || bytes.get(pos..pos + 3) == Some(&[c, c, c])) {
            return pos + width;
        } else if !triple && bytes[pos] == b'\n' {
            return pos;
        } else {
            pos += 1;
        }
    }
    bytes.len()
}

fn string_prefix(text: &str, quote: usize) -> (usize, bool) {
    let mut start = quote;
    while start > 0
        && (text.as_bytes()[start - 1].is_ascii_alphabetic() || text.as_bytes()[start - 1] == b'_')
    {
        start -= 1;
    }
    let prefix = text[start..quote].to_ascii_lowercase();
    if matches!(prefix.as_str(), "r" | "u" | "b" | "br" | "rb") {
        (start, false)
    } else if matches!(prefix.as_str(), "f" | "fr" | "rf") {
        (start, true)
    } else {
        (quote, false)
    }
}

fn python_string(text: &str, quote: usize, regions: &mut Vec<(usize, usize, bool)>) -> usize {
    let (start, formatted) = string_prefix(text, quote);
    if !formatted {
        let end = string_end(text.as_bytes(), quote);
        regions.push((start, end, false));
        return end;
    }
    let bytes = text.as_bytes();
    let c = bytes[quote];
    let triple = bytes.get(quote..quote + 3) == Some(&[c, c, c]);
    let width = if triple { 3 } else { 1 };
    let mut pos = quote + width;
    while pos < bytes.len() {
        if bytes[pos] == b'\\' {
            if matches!(bytes.get(pos + 1), Some(b'{' | b'}')) {
                pos += 1;
            } else {
                pos = (pos + 2).min(bytes.len());
            }
        } else if bytes[pos] == c && (!triple || bytes.get(pos..pos + 3) == Some(&[c, c, c])) {
            return pos + width;
        } else if bytes.get(pos..pos + 2) == Some(b"{{") || bytes.get(pos..pos + 2) == Some(b"}}") {
            pos += 2;
        } else if bytes[pos] == b'{' {
            pos = python_field(text, pos + 1, regions);
        } else {
            pos += 1;
        }
    }
    bytes.len()
}

fn python_field(text: &str, mut pos: usize, regions: &mut Vec<(usize, usize, bool)>) -> usize {
    let bytes = text.as_bytes();
    let mut grouping = Vec::new();
    while pos < bytes.len() {
        match bytes[pos] {
            b'\'' | b'"' => pos = python_string(text, pos, regions),
            b'#' => {
                let end = text[pos..].find('\n').map_or(bytes.len(), |n| pos + n);
                regions.push((pos, end, true));
                pos = end;
            }
            b'(' | b'[' | b'{' => {
                grouping.push(bytes[pos]);
                pos += 1;
            }
            b'}' if grouping.is_empty() => return pos + 1,
            b')' | b']' | b'}' => {
                grouping.pop();
                pos += 1;
            }
            b':' if grouping.is_empty() => {
                pos += 1;
                while pos < bytes.len() {
                    if bytes[pos] == b'{' {
                        pos = python_field(text, pos + 1, regions);
                    } else if bytes[pos] == b'}' {
                        return pos + 1;
                    } else {
                        pos += 1;
                    }
                }
            }
            _ => pos += 1,
        }
    }
    pos
}

/// Comment and ordinary string token bounds. F-string literal segments are
/// excluded, matching Python 3.13's STRING/COMMENT token scopes.
mod python_checked;

/// Managed token bounds only when tokenization can finish. A carry into an
/// unfinished file must leave every byte where its author put it.
pub fn python_regions_checked(text: &str) -> Result<Vec<(usize, usize, bool)>> {
    python_checked::validate(text)?;
    Ok(python_regions(text))
}

pub fn python_regions(text: &str) -> Vec<(usize, usize, bool)> {
    let bytes = text.as_bytes();
    let mut regions = Vec::new();
    let mut pos = 0;
    while pos < bytes.len() {
        if bytes[pos] == b'#' {
            let end = text[pos..].find('\n').map_or(bytes.len(), |n| pos + n);
            regions.push((pos, end, true));
            pos = end;
        } else if bytes[pos] == b'\'' || bytes[pos] == b'"' {
            pos = python_string(text, pos, &mut regions);
        } else {
            pos += 1;
        }
    }
    regions
}

pub fn python_comments(text: &str, variables: &Variables) -> String {
    let mut out = String::with_capacity(text.len());
    let mut pos = 0;
    for (start, end, comment) in python_regions(text) {
        let region = &text[start..end];
        if comment
            || markers(region)
                .iter()
                .any(|(_, _, _, name)| variables.contains_key(*name))
        {
            out.push_str(&text[pos..start]);
            out.push_str(&replace_markers(region, variables));
            pos = end;
        }
    }
    out.push_str(&text[pos..]);
    out
}

fn normalized_text(path: &Path) -> Result<String> {
    Ok(fs::read_to_string(path)?
        .replace("\r\n", "\n")
        .replace('\r', "\n"))
}

/// Rewrite managed values; report every maintained file even when unchanged.
pub fn substitute(
    path: &Path,
    kind: Kind,
    variables: &Variables,
    caller: Option<&str>,
    record_figures: bool,
) -> Result<Substitution> {
    let text = normalized_text(path).with_context(|| format!("read {}", path.display()))?;
    let (new_text, figures) = match kind {
        Kind::Markdown => markdown(&text, variables, caller),
        Kind::Mermaid => (mermaid(&text, variables), Variables::new()),
        Kind::Python => (python_comments(&text, variables), Variables::new()),
    };
    let mut result = Substitution {
        maintained: vec![path.to_owned()],
        changed: new_text != text,
    };
    if result.changed {
        write_if_changed(path, new_text.as_bytes())?;
    }
    if matches!(kind, Kind::Markdown)
        && record_figures
        && let Some(caller) = caller
    {
        let sidecar = path.with_extension("figures.json");
        let mut held: BTreeMap<String, Variables> = fs::read(&sidecar)
            .ok()
            .and_then(|data| serde_json::from_slice(&data).ok())
            .unwrap_or_default();
        held.insert(caller.to_owned(), figures);
        // Python's json.dumps default escapes non-ASCII, while serde_json
        // writes UTF-8. Preserve the sidecar's existing ASCII encoding.
        let json = ascii_json(&serde_json::to_string_pretty(&held)?) + "\n";
        result.changed |= write_if_changed(&sidecar, json.as_bytes())?;
        result.maintained.push(sidecar);
    }
    Ok(result)
}

fn ascii_json(text: &str) -> String {
    let mut out = String::with_capacity(text.len());
    for c in text.chars() {
        if (c as u32) < 0x7f {
            out.push(c);
        } else {
            let mut buf = [0_u16; 2];
            for value in c.encode_utf16(&mut buf) {
                out.push_str(&format!("\\u{value:04x}"));
            }
        }
    }
    out
}

static TEMP_SEQUENCE: AtomicU64 = AtomicU64::new(0);

pub fn pid_alive(pid: i32) -> bool {
    if pid <= 0 {
        return false;
    }
    #[cfg(unix)]
    {
        unsafe extern "C" {
            fn kill(pid: i32, signal: i32) -> i32;
        }
        unsafe { kill(pid, 0) == 0 }
    }
    #[cfg(not(unix))]
    {
        pid == std::process::id() as i32
    }
}

pub fn sweep_orphan_temps(target: &Path) -> Result<()> {
    let parent = target.parent().unwrap_or(Path::new("."));
    let suffix = target
        .extension()
        .map(|s| format!(".{}", s.to_string_lossy()))
        .unwrap_or_default();
    for entry in fs::read_dir(parent)? {
        let entry = entry?;
        let name = entry.file_name();
        let name = name.to_string_lossy();
        if !name.starts_with('.') || !name.ends_with(&suffix) {
            continue;
        }
        let stem_path = Path::new(name.as_ref());
        let Some(stem) = stem_path.file_stem().and_then(|s| s.to_str()) else {
            continue;
        };
        let mut parts = stem.rsplitn(3, '.');
        let _random = parts.next();
        let Some(pid) = parts
            .next()
            .filter(|p| !p.is_empty() && p.bytes().all(|c| c.is_ascii_digit()))
            .and_then(|p| p.parse::<i32>().ok())
        else {
            continue;
        };
        if parts.next().is_some() && !pid_alive(pid) {
            let _ = fs::remove_file(entry.path());
        }
    }
    Ok(())
}

pub fn sibling_tempfile(target: &Path, owner_pid: u32) -> Result<PathBuf> {
    let parent = target.parent().unwrap_or(Path::new("."));
    fs::create_dir_all(parent)?;
    let name = target
        .file_name()
        .context("document target has no filename")?
        .to_string_lossy();
    let suffix = target
        .extension()
        .map(|s| format!(".{}", s.to_string_lossy()))
        .unwrap_or_default();
    loop {
        let stamp = SystemTime::now().duration_since(UNIX_EPOCH)?.as_nanos();
        let sequence = TEMP_SEQUENCE.fetch_add(1, Ordering::Relaxed);
        let path = parent.join(format!(".{name}.{owner_pid}.{stamp:x}{sequence:x}{suffix}"));
        match OpenOptions::new().write(true).create_new(true).open(&path) {
            Ok(_) => return Ok(path),
            Err(e) if e.kind() == std::io::ErrorKind::AlreadyExists => continue,
            Err(e) => return Err(e.into()),
        }
    }
}

pub fn matches_existing_target(temporary: &Path, target: &Path) -> Result<bool> {
    if !target.exists() {
        return Ok(false);
    }
    if fs::metadata(target)?.len() != fs::metadata(temporary)?.len() {
        return Ok(false);
    }
    Ok(fs::read(target)? == fs::read(temporary)?)
}

pub fn finish_atomic(temporary: &Path, target: &Path, canonicalize: bool) -> Result<bool> {
    if canonicalize {
        match target.extension().and_then(|s| s.to_str()) {
            Some("pdf") => canonicalize_file(temporary, "pdf")?,
            Some("dxf") => canonicalize_file(temporary, "dxf")?,
            _ => (),
        }
    }
    if matches_existing_target(temporary, target)? {
        fs::remove_file(temporary)?;
        return Ok(false);
    }
    fs::rename(temporary, target)?;
    Ok(true)
}

pub fn atomic_write(
    target: &Path,
    writer: impl FnOnce(&Path) -> Result<()>,
    canonicalize: bool,
) -> Result<bool> {
    if let Some(parent) = target.parent() {
        fs::create_dir_all(parent)?;
    }
    sweep_orphan_temps(target)?;
    let temporary = sibling_tempfile(target, std::process::id())?;
    let result = writer(&temporary).and_then(|()| finish_atomic(&temporary, target, canonicalize));
    if result.is_err() {
        let _ = fs::remove_file(&temporary);
    }
    result
}

pub fn write_if_changed(path: &Path, bytes: &[u8]) -> Result<bool> {
    if fs::read(path).is_ok_and(|old| old == bytes) {
        return Ok(false);
    }
    let permissions = fs::metadata(path).ok().map(|m| m.permissions());
    atomic_write(
        path,
        |temporary| {
            let mut stream = OpenOptions::new()
                .write(true)
                .truncate(true)
                .open(temporary)?;
            stream.write_all(bytes)?;
            if let Some(permissions) = permissions {
                fs::set_permissions(temporary, permissions)?;
            }
            Ok(())
        },
        false,
    )
}

fn find_bytes(data: &[u8], pattern: &[u8], from: usize) -> Option<usize> {
    data.get(from..)?
        .windows(pattern.len())
        .position(|w| w == pattern)
        .map(|n| from + n)
}

pub fn canonicalize_dxf_classes(data: &[u8]) -> Vec<u8> {
    let opening = b"  0\nSECTION\n  2\nCLASSES\n";
    let Some(start) = find_bytes(data, opening, 0).map(|n| n + opening.len()) else {
        return data.to_vec();
    };
    let Some(end) = find_bytes(data, b"  0\nENDSEC\n", start) else {
        return data.to_vec();
    };
    let body = &data[start..end];
    let mut starts = Vec::new();
    let mut pos = 0;
    while let Some(start) = find_bytes(body, b"  0\nCLASS\n", pos) {
        starts.push(start);
        pos = start + 10;
    }
    if starts.len() < 2 {
        return data.to_vec();
    }
    let mut entries: Vec<_> = starts
        .iter()
        .enumerate()
        .map(|(i, &s)| &body[s..starts.get(i + 1).copied().unwrap_or(body.len())])
        .collect();
    let original = entries.clone();
    entries.sort_by_key(|entry| {
        find_bytes(entry, b"  1\n", 0)
            .and_then(|n| {
                let tail = &entry[n + 4..];
                tail.iter()
                    .position(|&c| c == b'\n')
                    .filter(|&n| n > 0)
                    .map(|n| &tail[..n])
            })
            .unwrap_or(b"")
    });
    if entries == original {
        return data.to_vec();
    }
    let mut out = data[..start].to_vec();
    for entry in entries {
        out.extend(entry);
    }
    out.extend(&data[end..]);
    out
}

fn replace_runs(
    data: &[u8],
    mut replacement: impl FnMut(&[u8], usize) -> Option<(usize, Vec<u8>)>,
) -> Vec<u8> {
    let mut out = Vec::with_capacity(data.len());
    let mut pos = 0;
    while pos < data.len() {
        if let Some((end, bytes)) = replacement(data, pos) {
            out.extend(bytes);
            pos = end;
        } else {
            out.push(data[pos]);
            pos += 1;
        }
    }
    out
}

fn take_digits(data: &[u8], pos: usize) -> usize {
    data[pos..]
        .iter()
        .take_while(|b| b.is_ascii_digit())
        .count()
        + pos
}

fn iso_date_end(data: &[u8], start: usize) -> Option<usize> {
    let pattern = b"dddd-dd-ddTdd:dd:dd";
    if data.len() < start + pattern.len() {
        return None;
    }
    if !pattern.iter().enumerate().all(|(i, &c)| {
        if c == b'd' {
            data[start + i].is_ascii_digit()
        } else {
            data[start + i] == c
        }
    }) {
        return None;
    }
    let mut end = start + pattern.len();
    if data.get(end) == Some(&b'.') {
        let after = take_digits(data, end + 1);
        if after > end + 1 {
            end = after;
        }
    }
    if matches!(data.get(end), Some(b'+' | b'-'))
        && data.len() >= end + 6
        && data[end + 1..end + 3].iter().all(u8::is_ascii_digit)
        && data[end + 3] == b':'
        && data[end + 4..end + 6].iter().all(u8::is_ascii_digit)
    {
        end += 6;
    }
    Some(end)
}

pub fn canonicalize_dxf(data: &[u8]) -> Vec<u8> {
    let replaced = replace_runs(data, |data, pos| {
        let tail = &data[pos..];
        for name in ["TDCREATE", "TDUCREATE", "TDUPDATE", "TDUUPDATE"] {
            let prefix = format!("  9\n${name}\n 40\n");
            if tail.starts_with(prefix.as_bytes()) {
                let start = pos + prefix.len();
                let end = start
                    + data[start..]
                        .iter()
                        .take_while(|b| b.is_ascii_digit() || **b == b'.')
                        .count();
                if end > start && data.get(end) == Some(&b'\n') {
                    return Some((end + 1, (prefix + "2440587.5\n").into_bytes()));
                }
            }
        }
        for name in ["FINGERPRINTGUID", "VERSIONGUID"] {
            let prefix = format!("  9\n${name}\n  2\n");
            if tail.starts_with(prefix.as_bytes()) && data.get(pos + prefix.len()) == Some(&b'{') {
                let start = pos + prefix.len() + 1;
                let end = start
                    + data[start..]
                        .iter()
                        .take_while(|b| b.is_ascii_hexdigit() || **b == b'-')
                        .count();
                if end > start && data.get(end..end + 2) == Some(b"}\n") {
                    return Some((
                        end + 2,
                        (prefix + "{00000000-0000-0000-0000-000000000000}\n").into_bytes(),
                    ));
                }
            }
        }
        if data[pos].is_ascii_digit() {
            let a = take_digits(data, pos);
            if data.get(a) != Some(&b'.') {
                return None;
            }
            let b = take_digits(data, a + 1);
            if b == a + 1 || data.get(b) != Some(&b'.') {
                return None;
            }
            let c = take_digits(data, b + 1);
            if c == b + 1 || data.get(c..c + 3) != Some(b" @ ") {
                return None;
            }
            let end = iso_date_end(data, c + 3)?;
            let mut replacement = data[pos..c + 3].to_vec();
            replacement.extend(b"1970-01-01T00:00:00.000000+00:00");
            return Some((end, replacement));
        }
        None
    });
    canonicalize_dxf_classes(&replaced)
}

pub fn canonicalize_pdf(data: &[u8]) -> Vec<u8> {
    replace_runs(data, |data, pos| {
        if data[pos..].starts_with(b"(D:") {
            let digits = pos + 3;
            if data.len() < digits + 15 || !data[digits..digits + 14].iter().all(u8::is_ascii_digit)
            {
                return None;
            }
            let suffix = digits + 14;
            let end = if data.get(suffix..suffix + 2) == Some(b"Z)") {
                suffix + 2
            } else if data.len() >= suffix + 8
                && matches!(data[suffix], b'+' | b'-')
                && data[suffix + 1..suffix + 3].iter().all(u8::is_ascii_digit)
                && data[suffix + 3] == b'\''
                && data[suffix + 4..suffix + 6].iter().all(u8::is_ascii_digit)
                && data.get(suffix + 6..suffix + 8) == Some(b"')")
            {
                suffix + 8
            } else {
                return None;
            };
            return Some((end, b"(D:19700101000000+00'00')".to_vec()));
        }
        if data[pos..].starts_with(b"/ID") {
            let mut at = pos + 3;
            while data.get(at).is_some_and(|b| b.is_ascii_whitespace()) {
                at += 1;
            }
            if data.get(at) != Some(&b'[') {
                return None;
            }
            let opening = at + 1;
            at += 1;
            for _ in 0..2 {
                if data.get(at) != Some(&b'<') {
                    return None;
                }
                let start = at + 1;
                at = start
                    + data[start..]
                        .iter()
                        .take_while(|b| b.is_ascii_hexdigit())
                        .count();
                if at == start || data.get(at) != Some(&b'>') {
                    return None;
                }
                at += 1;
            }
            if data.get(at) != Some(&b']') {
                return None;
            }
            let mut replacement = data[pos..opening].to_vec();
            replacement
                .extend(b"<00000000000000000000000000000000><00000000000000000000000000000000>]");
            return Some((at + 1, replacement));
        }
        None
    })
}

pub fn canonicalize_file(path: &Path, kind: &str) -> Result<()> {
    let original = fs::read(path)?;
    let canonical = match kind {
        "pdf" => canonicalize_pdf(&original),
        "dxf" => canonicalize_dxf(&original),
        _ => bail!("unknown document format {kind}"),
    };
    if original != canonical {
        fs::write(path, canonical)?;
    }
    Ok(())
}

/// The floating-point formats used by generated documents. Rounding happens
/// through Rust's correctly rounded decimal formatter, including ties to even.
pub fn format_number(value: f64, spec: &str) -> Result<String> {
    if spec.is_empty() {
        return Ok(value.to_string());
    }
    let mut spec = spec;
    let plus = spec.starts_with('+');
    let space = spec.starts_with(' ');
    if plus || space {
        spec = &spec[1..];
    }
    let grouped = spec.starts_with(',');
    if grouped {
        spec = &spec[1..];
    }
    let kind = spec.chars().last().unwrap_or('g');
    if !matches!(kind, 'g' | 'G' | 'f' | 'F' | 'e' | 'E' | '%') {
        bail!("unsupported numeric format {spec}");
    }
    let precision = spec[..spec.len() - 1]
        .strip_prefix('.')
        .map(str::parse::<usize>)
        .transpose()?
        .unwrap_or(6);
    let number = if kind == '%' { value * 100.0 } else { value };
    let mut text = if number.is_nan() {
        "nan".to_owned()
    } else if number == f64::INFINITY {
        "inf".to_owned()
    } else if number == f64::NEG_INFINITY {
        "-inf".to_owned()
    } else if matches!(kind, 'f' | 'F' | '%') {
        format!("{number:.precision$}")
    } else {
        let significant = if matches!(kind, 'g' | 'G') {
            precision.max(1)
        } else {
            precision + 1
        };
        let scientific = format!("{number:.digits$e}", digits = significant - 1);
        let (mantissa, exponent) = scientific.split_once('e').context("scientific exponent")?;
        let exponent: i32 = exponent.parse()?;
        if matches!(kind, 'e' | 'E') || exponent < -4 || exponent >= significant as i32 {
            let mantissa = if matches!(kind, 'g' | 'G') {
                mantissa.trim_end_matches('0').trim_end_matches('.')
            } else {
                mantissa
            };
            format!("{mantissa}e{exponent:+03}")
        } else {
            let decimals = (significant as i32 - exponent - 1).max(0) as usize;
            let fixed = format!("{number:.decimals$}");
            if fixed.contains('.') {
                fixed.trim_end_matches('0').trim_end_matches('.').to_owned()
            } else {
                fixed
            }
        }
    };
    if kind.is_ascii_uppercase() {
        text = text.to_ascii_uppercase();
    }
    if !text.starts_with('-') {
        if plus {
            text.insert(0, '+');
        } else if space {
            text.insert(0, ' ');
        }
    }
    if grouped && number.is_finite() {
        let end = text.find(['.', 'e', 'E']).unwrap_or(text.len());
        let start = usize::from(text.starts_with(['-', '+', ' ']));
        let mut grouped_text = String::new();
        for (i, c) in text[..end].chars().enumerate() {
            if i > start && (end - i).is_multiple_of(3) {
                grouped_text.push(',');
            }
            grouped_text.push(c);
        }
        grouped_text.push_str(&text[end..]);
        text = grouped_text;
    }
    if kind == '%' {
        text.push('%');
    }
    Ok(text)
}
