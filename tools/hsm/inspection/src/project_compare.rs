//! Compares two Bambu print projects by value, member by member, to tell what a change to a
//! preparer changed in what it writes: two `.3mf` projects, two `.gcode.3mf` archives or two
//! preparers' output folders. Settings and records compare by value: key order is ignored and
//! numbers are equal by value wherever they appear, inside strings too. XML compares by element
//! and attribute value, a mesh as its triangles and paint with corners within a tolerance,
//! whatever their numbering, and G-code by the beads `hsm-gcode compare` matches. Hashes, thread
//! addresses and preparation times are masked.

use crate::gcode::compare as beads;
use anyhow::{bail, Context, Result};
use clap::Args;
use hsm_print_prep::mesh::stl_corners;
use hsm_print_prep::sha256_hex;
use hsm_print_prep::xml::{self, Element};
use serde_json::Value;
use std::borrow::Cow;
use std::collections::{BTreeMap, BTreeSet, HashMap};
use std::io::{Cursor, Read};
use std::path::{Path, PathBuf};

#[derive(Args)]
pub struct Options {
    /// The reference: a `.3mf` project, a `.gcode.3mf` archive or a preparer's output folder.
    a: PathBuf,
    /// What is compared with it, of the same kind.
    b: PathBuf,
    /// How far a mesh corner may lie from its counterpart and count as the same, in mm.
    #[arg(long, default_value_t = 1e-6)]
    mesh_tolerance: f64,
    /// How far a G-code bead may lie from the other slice's and count as on it, in mm.
    #[arg(long, default_value_t = 0.05)]
    bead_tolerance: f64,
    /// How many differences to list for each member.
    #[arg(long, default_value_t = 12)]
    limit: usize,
    /// List every member, not only the members that differ.
    #[arg(long)]
    all: bool,
}

/// The attribute that marks where a mesh was read out of its XML member.
const CUT: &str = "hsm-mesh";
/// The longest list of elements searched for the same elements in another order, each against
/// each.
const REORDER_LIMIT: usize = 1000;

pub fn run(options: Options) -> Result<i32> {
    println!("A {}\nB {}", options.a.display(), options.b.display());
    println!("Numbers compare by value, mesh corners within {} mm and G-code beads within {} mm. \
              Hashes, thread addresses and preparation times are masked.", options.mesh_tolerance, options.bead_tolerance);
    let checkouts = [checkout(&options.a), checkout(&options.b)];
    if let [Some(a), Some(b)] = &checkouts {
        if a != b {
            println!("A path into A's checkout, {a}, reads as the same path into B's, {b}.");
        }
    }
    let mut report = Report { options: &options, checkouts, identical: 0, by_value: 0, differing: 0, masked: 0,
                              slices: HashMap::new(), only: Vec::new() };
    match (options.a.is_dir(), options.b.is_dir()) {
        (true, true) => {
            let (a, b) = (files(&options.a)?, files(&options.b)?);
            for name in a.keys().chain(b.keys()).collect::<BTreeSet<_>>() {
                match (a.get(name), b.get(name)) {
                    (Some(x), Some(y)) => report.member(name, &read(x)?, &read(y)?)?,
                    (x, _) => report.only.push(format!("only in {}: {name}", if x.is_some() { 'A' } else { 'B' })),
                }
            }
        }
        (false, false) => {
            let (a, b) = (read(&options.a)?, read(&options.b)?);
            if a == b {
                println!("\nA and B are the same bytes.");
                return Ok(0);
            }
            if is_zip(&a) && is_zip(&b) {
                report.archive("", &a, &b)?;
            } else {
                let name = options.a.file_name().map(|n| n.to_string_lossy().into_owned()).unwrap_or_default();
                report.member(&name, &a, &b)?;
            }
        }
        _ => bail!("compare two files or two folders"),
    }
    Ok(report.finish())
}

fn read(path: &Path) -> Result<Vec<u8>> {
    std::fs::read(path).with_context(|| format!("reading {}", path.display()))
}

/// Every file below a folder, by its path from it; hidden files and links are left out.
fn files(root: &Path) -> Result<BTreeMap<String, PathBuf>> {
    let mut out = BTreeMap::new();
    let mut folders = vec![root.to_path_buf()];
    while let Some(folder) = folders.pop() {
        for entry in std::fs::read_dir(&folder).with_context(|| format!("reading {}", folder.display()))? {
            let entry = entry?;
            let (path, kind) = (entry.path(), entry.file_type()?);
            if entry.file_name().to_string_lossy().starts_with('.') {
                continue;
            }
            if kind.is_dir() {
                folders.push(path);
            } else if kind.is_file() {
                out.insert(path.strip_prefix(root)?.to_string_lossy().into_owned(), path);
            }
        }
    }
    Ok(out)
}

fn is_zip(bytes: &[u8]) -> bool {
    bytes.starts_with(b"PK\x03\x04")
}

/// The checkout a path lies in, found as the preparers find theirs.
fn checkout(path: &Path) -> Option<String> {
    let path = path.canonicalize().ok()?;
    let root = path.ancestors().find(|at| at.join("tools/hsm/Cargo.toml").is_file() && at.join("hardware").is_dir())?;
    Some(root.to_string_lossy().into_owned())
}

struct Report<'a> {
    options: &'a Options,
    /// A's checkout and B's, whose paths read alike.
    checkouts: [Option<String>; 2],
    identical: usize,
    by_value: usize,
    differing: usize,
    /// Hashes, thread addresses and preparation times that differ.
    masked: usize,
    /// Each pair of G-codes already compared, by their hashes, and the member it was.
    slices: HashMap<(String, String), String>,
    only: Vec<String>,
}

/// The differences found in one member, each a line of the report.
#[derive(Default)]
struct Found {
    lines: Vec<String>,
    masked: usize,
    checkouts: [Option<String>; 2],
}

impl Found {
    /// Each side's text with a path into its own checkout written from `<checkout>`.
    fn rooted<'s>(&self, a: &'s str, b: &'s str) -> (Cow<'s, str>, Cow<'s, str>) {
        let swap = |s: &'s str, root: &Option<String>| match root {
            Some(root) if s.contains(root.as_str()) => Cow::Owned(s.replace(root.as_str(), "<checkout>")),
            _ => Cow::Borrowed(s),
        };
        (swap(a, &self.checkouts[0]), swap(b, &self.checkouts[1]))
    }

    fn add(&mut self, line: String) {
        self.lines.push(line);
    }

    fn value(&mut self, at: &str, a: impl std::fmt::Display, b: impl std::fmt::Display) {
        self.lines.push(format!("{at}: A {a}, B {b}"));
    }
}

impl Report<'_> {
    fn member(&mut self, name: &str, a: &[u8], b: &[u8]) -> Result<()> {
        if a == b {
            self.identical += 1;
            if self.options.all {
                println!("{name}: the same bytes");
            }
            return Ok(());
        }
        if is_zip(a) && is_zip(b) {
            return self.archive(name, a, b);
        }
        let mut found = Found { checkouts: self.checkouts.clone(), ..Found::default() };
        // A sliced archive's plate G-code is often beside it too, and its beads match slowly.
        let slices = name.to_ascii_lowercase().ends_with(".gcode").then(|| (sha256_hex(a), sha256_hex(b)));
        match slices.as_ref().and_then(|pair| self.slices.get(pair)) {
            Some(first) => found.add(format!("the same two G-codes as {first}")),
            None => {
                self.compare(name, a, b, &mut found).with_context(|| format!("comparing {name}"))?;
                if let Some(pair) = slices {
                    self.slices.insert(pair, name.to_string());
                }
            }
        }
        self.masked += found.masked;
        if found.lines.is_empty() {
            self.by_value += 1;
            if self.options.all {
                println!("{name}: equal by value");
            }
            return Ok(());
        }
        self.differing += 1;
        println!("\n{name}");
        for line in found.lines.iter().take(self.options.limit) {
            println!("  {line}");
        }
        if found.lines.len() > self.options.limit {
            println!("  ... {} more; --limit lists more", found.lines.len() - self.options.limit);
        }
        Ok(())
    }

    /// Every member of two zip archives, a member of either by itself named as such.
    fn archive(&mut self, name: &str, a: &[u8], b: &[u8]) -> Result<()> {
        let (mut x, mut y) = (open(a).context("opening A")?, open(b).context("opening B")?);
        let (in_a, in_b) = (member_names(&x)?, member_names(&y)?);
        for member in in_a.union(&in_b) {
            let shown = if name.is_empty() { member.clone() } else { format!("{name}:{member}") };
            match (in_a.contains(member), in_b.contains(member)) {
                (true, true) => {
                    let (p, q) = (unzip(&mut x, member)?, unzip(&mut y, member)?);
                    self.member(&shown, &p, &q)?;
                }
                (in_first, _) => self.only.push(format!("only in {}: {shown}", if in_first { 'A' } else { 'B' })),
            }
        }
        Ok(())
    }

    fn compare(&self, name: &str, a: &[u8], b: &[u8], found: &mut Found) -> Result<()> {
        let lower = name.to_ascii_lowercase();
        if lower.ends_with(".gcode") {
            return self.gcode(a, b, found);
        }
        if lower.ends_with(".stl") {
            meshes("triangles", &Mesh::stl(a)?, &Mesh::stl(b)?, self.options.mesh_tolerance, found);
            return Ok(());
        }
        let (Ok(x), Ok(y)) = (std::str::from_utf8(a), std::str::from_utf8(b)) else {
            found.add(format!("the bytes differ: A has {}, B {}", a.len(), b.len()));
            return Ok(());
        };
        let start = |s: &str| s.trim_start().chars().next();
        match (start(x), start(y)) {
            (Some('{' | '['), Some('{' | '[')) => {
                if let (Ok(p), Ok(q)) = (serde_json::from_str::<Value>(x), serde_json::from_str::<Value>(y)) {
                    json("", &p, &q, found);
                    return Ok(());
                }
            }
            (Some('<'), Some('<')) => {
                let (x, meshes_a) = cut_meshes(x)?;
                let (y, meshes_b) = cut_meshes(y)?;
                let (p, q) = (xml::parse(&x)?, xml::parse(&y)?);
                self.element(p.local(), &p, &q, (meshes_a.as_slice(), meshes_b.as_slice()), found);
                return Ok(());
            }
            _ => {}
        }
        lines(x, y, found);
        Ok(())
    }

    /// G-code equal by value line by line, or else its beads matched as `hsm-gcode compare`
    /// matches them.
    fn gcode(&self, a: &[u8], b: &[u8], found: &mut Found) -> Result<()> {
        let (x, y) = (std::str::from_utf8(a)?, std::str::from_utf8(b)?);
        let (mut p, mut q) = (x.lines(), y.lines());
        let (mut count_a, mut count_b, mut first) = (0, 0, None);
        loop {
            match (p.next(), q.next()) {
                (Some(l), Some(m)) => {
                    count_a += 1;
                    count_b += 1;
                    if first.is_none() && l != m && !by_value(l, m) {
                        first = Some((count_a, l, m));
                    }
                }
                (Some(_), None) => count_a += 1,
                (None, Some(_)) => count_b += 1,
                (None, None) => break,
            }
        }
        if first.is_none() && count_a == count_b {
            return Ok(());
        }
        let matched = beads::compare(a, b, self.options.bead_tolerance);
        if matched.groups_differing() > 0 {
            found.add(format!("beads: {}; hsm-gcode compare lists them", matched.summary()));
        } else {
            found.add(format!("the beads match: {}", matched.summary()));
            if let Some((line, l, m)) = first {
                found.add(format!("line {line}: A {}, B {}; hsm-gcode recipe compares the commands", quoted(l), quoted(m)));
            }
        }
        if count_a != count_b {
            found.add(format!("A has {count_a} lines, B {count_b}"));
        }
        Ok(())
    }

    /// Elements by name, attribute value and text; children that a key or an id names in any
    /// order, the other children in order.
    fn element(&self, at: &str, a: &Element, b: &Element, meshes_cut: (&[Mesh], &[Mesh]), found: &mut Found) {
        if a.name != b.name {
            found.value(at, &a.name, &b.name);
            return;
        }
        if a.local() == "mesh" {
            if let (Some(p), Some(q)) = (cut(a, meshes_cut.0), cut(b, meshes_cut.1)) {
                meshes(at, p, q, self.options.mesh_tolerance, found);
            }
            return;
        }
        let masked = a.local() == "metadata" && masked_key(&key(a));
        let (p, q) = (attribute_map(a), attribute_map(b));
        for name in p.keys().chain(q.keys()).collect::<BTreeSet<_>>() {
            let here = format!("{at}@{name}");
            match (p.get(name), q.get(name)) {
                (Some(x), Some(y)) => strings(&here, x, y, masked || masked_key(name), found),
                (x, y) => found.value(&here, present(x), present(y)),
            }
        }
        strings(&format!("{at} text"), a.text.trim(), b.text.trim(), masked, found);
        let (keyed_a, rest_a) = children(a);
        let (keyed_b, rest_b) = children(b);
        for k in keyed_a.keys().chain(keyed_b.keys()).collect::<BTreeSet<_>>() {
            let here = format!("{at}/{k}");
            match (keyed_a.get(k), keyed_b.get(k)) {
                (Some(x), Some(y)) => {
                    if x.len() != y.len() {
                        found.add(format!("{here}: A has {}, B {}", x.len(), y.len()));
                    }
                    for (x, y) in x.iter().zip(y) {
                        self.element(&here, x, y, meshes_cut, found);
                    }
                }
                (x, y) => found.value(&here, present(x), present(y)),
            }
        }
        if rest_a.len() != rest_b.len() {
            found.add(format!("{at}: A holds {} elements without a key or an id, B {}", rest_a.len(), rest_b.len()));
        }
        let mut in_order = Found { checkouts: found.checkouts.clone(), ..Found::default() };
        for ((x, y), label) in rest_a.iter().zip(&rest_b).zip(labels(&rest_a)) {
            self.element(&format!("{at}/{label}"), x, y, meshes_cut, &mut in_order);
        }
        found.masked += in_order.masked;
        if !in_order.lines.is_empty() && self.reordered(&rest_a, &rest_b, meshes_cut, found) {
            let names = rest_a.iter().map(|e| e.local()).collect::<BTreeSet<_>>();
            let names = if names.len() == 1 { format!("{} ", rest_a[0].local()) } else { String::new() };
            found.add(format!("{at}: the same {} {names}elements in another order", rest_a.len()));
        } else {
            found.lines.extend(in_order.lines);
        }
    }

    /// Whether two lists of elements hold the same elements, by value, in another order.
    fn reordered(&self, a: &[&Element], b: &[&Element], meshes_cut: (&[Mesh], &[Mesh]), found: &Found) -> bool {
        if a.len() != b.len() || a.len() < 2 || a.len() > REORDER_LIMIT || a.iter().chain(b).any(|e| e.local() == "mesh") {
            return false;
        }
        let mut used = vec![false; b.len()];
        a.iter().all(|x| {
            let same = |y: &Element| {
                let mut scratch = Found { checkouts: found.checkouts.clone(), ..Found::default() };
                self.element("", x, y, meshes_cut, &mut scratch);
                scratch.lines.is_empty()
            };
            match (0..b.len()).find(|&i| !used[i] && same(b[i])) {
                Some(i) => {
                    used[i] = true;
                    true
                }
                None => false,
            }
        })
    }
}

fn open(bytes: &[u8]) -> Result<zip::ZipArchive<Cursor<&[u8]>>> {
    Ok(zip::ZipArchive::new(Cursor::new(bytes))?)
}

/// An archive's member names, its folders left out.
fn member_names(archive: &zip::ZipArchive<Cursor<&[u8]>>) -> Result<BTreeSet<String>> {
    let mut out = BTreeSet::new();
    for name in archive.file_names() {
        let name = name?;
        if !name.ends_with('/') {
            out.insert(name.into_owned());
        }
    }
    Ok(out)
}

fn unzip(archive: &mut zip::ZipArchive<Cursor<&[u8]>>, name: &str) -> Result<Vec<u8>> {
    let mut entry = archive.by_name(name)?;
    let mut bytes = Vec::with_capacity(entry.size() as usize);
    entry.read_to_end(&mut bytes).with_context(|| format!("reading {name}"))?;
    Ok(bytes)
}

impl Report<'_> {
    fn finish(&self) -> i32 {
        for line in &self.only {
            println!("{line}");
        }
        let members = self.identical + self.by_value + self.differing;
        println!("\n{members} members compared: {} the same bytes, {} equal by value, {} differ; {} only in one.",
            self.identical, self.by_value, self.differing, self.only.len());
        if self.masked > 0 {
            println!("{} masked values differ: hashes, thread addresses or preparation times.", self.masked);
        }
        if self.differing == 0 && self.only.is_empty() {
            println!("A and B are equal by value.");
            0
        } else {
            1
        }
    }
}

/// JSON by value, object keys in any order.
fn json(at: &str, a: &Value, b: &Value, found: &mut Found) {
    match (a, b) {
        (Value::Object(x), Value::Object(y)) => {
            for k in x.keys().chain(y.keys()).collect::<BTreeSet<_>>() {
                let here = if at.is_empty() { k.clone() } else { format!("{at}/{k}") };
                match (x.get(k), y.get(k)) {
                    (Some(p), Some(q)) if masked_key(k) => found.masked += usize::from(p != q),
                    (Some(p), Some(q)) => json(&here, p, q, found),
                    (p, q) => found.value(&here, p.map_or("absent".into(), show), q.map_or("absent".into(), show)),
                }
            }
        }
        (Value::Array(x), Value::Array(y)) => {
            for (i, (p, q)) in x.iter().zip(y).enumerate() {
                json(&format!("{at}[{i}]"), p, q, found);
            }
            if x.len() != y.len() {
                let (side, more) = if x.len() > y.len() { ('A', &x[y.len()..]) } else { ('B', &y[x.len()..]) };
                let more = more.iter().map(Value::to_string).collect::<Vec<_>>().join(", ");
                found.add(format!("{at}: A has {} items, B {}; {side} goes on with {}", x.len(), y.len(), clip(&more)));
            }
        }
        (Value::String(x), Value::String(y)) if at.contains("different_settings_to_system") => key_list(at, x, y, found),
        (Value::String(x), Value::String(y)) => strings(at, x, y, false, found),
        (Value::Number(x), Value::Number(y)) => {
            if !number_equal(x.as_f64().unwrap_or(f64::NAN), y.as_f64().unwrap_or(f64::NAN)) {
                found.value(at, x, y);
            }
        }
        _ if a != b => found.value(at, show(a), show(b)),
        _ => {}
    }
}

/// Bambu's `different_settings_to_system` names the keys a preset changes, joined by `;`, in an
/// order that means nothing: a project's and a record's copies of it compare as sets of keys.
fn key_list(at: &str, a: &str, b: &str, found: &mut Found) {
    let set = |s: &'_ str| s.split(';').filter(|k| !k.is_empty()).map(String::from).collect::<BTreeSet<_>>();
    let (p, q) = (set(a), set(b));
    let lists = [('A', &p, &q), ('B', &q, &p)].map(|(side, own, other)| {
        let only = own.difference(other).map(String::as_str).collect::<Vec<_>>();
        (!only.is_empty()).then(|| format!("only {side} lists {}", only.join(", ")))
    });
    let lists = lists.into_iter().flatten().collect::<Vec<_>>();
    if !lists.is_empty() {
        found.add(format!("{at}: {}", lists.join("; ")));
    }
}

fn show(v: &Value) -> String {
    clip(&v.to_string())
}

fn quoted(s: &str) -> String {
    clip(&Value::String(s.into()).to_string())
}

fn clip(s: &str) -> String {
    match s.char_indices().nth(100) {
        Some((at, _)) => format!("{}…", &s[..at]),
        None => s.to_string(),
    }
}

fn present<T>(v: Option<T>) -> &'static str {
    if v.is_some() { "present" } else { "absent" }
}

/// Plain text line by line, each line by value.
fn lines(a: &str, b: &str, found: &mut Found) {
    let (x, y): (Vec<&str>, Vec<&str>) = (a.lines().collect(), b.lines().collect());
    if x.len() != y.len() {
        found.add(format!("A has {} lines, B {}", x.len(), y.len()));
    }
    for (i, (p, q)) in x.iter().zip(&y).enumerate() {
        strings(&format!("line {}", i + 1), p, q, false, found);
    }
}

/// Two strings by value, or masked: a masked pair only counts whether it differs. A string of
/// several lines shows its first line that differs, and each side shows from just before where
/// the two part.
fn strings(at: &str, a: &str, b: &str, masked: bool, found: &mut Found) {
    if a == b || by_value(a, b) {
        return;
    }
    let (a, b) = found.rooted(a, b);
    let (a, b) = (a.as_ref(), b.as_ref());
    if a == b || by_value(a, b) {
        return;
    }
    let (p, q) = (run_masked(a), run_masked(b));
    if masked || (matches!((&p, &q), (Cow::Owned(_), _) | (_, Cow::Owned(_))) && by_value(&p, &q)) {
        found.masked += 1;
        return;
    }
    let (mut x, mut y, mut n) = (a.lines(), b.lines(), 0);
    let (p, q, line) = loop {
        n += 1;
        match (x.next(), y.next()) {
            (Some(p), Some(q)) if p == q || by_value(p, q) => {}
            (None, None) => break (a, b, None),
            (p, q) => break (p.unwrap_or(""), q.unwrap_or(""), Some(n)),
        }
    };
    let several = a.lines().nth(1).is_some() || b.lines().nth(1).is_some();
    let at = match line {
        Some(n) if several => format!("{at} line {n}"),
        _ => at.to_string(),
    };
    let (i, j) = parting(p, q);
    found.value(&at, from(p, i), from(q, j));
}

/// Where two strings part, in each: at the first piece that differs, inside a run of text where
/// the run first differs.
fn parting(a: &str, b: &str) -> (usize, usize) {
    let (mut x, mut y) = (Pieces { s: a, at: 0 }, Pieces { s: b, at: 0 });
    loop {
        let (i, j) = (x.at, y.at);
        match (x.next(), y.next()) {
            (Some(Piece::Text(p)), Some(Piece::Text(q))) if p == q => {}
            (Some(Piece::Number(p)), Some(Piece::Number(q))) if number_equal(p, q) => {}
            (Some(Piece::Text(p)), Some(Piece::Text(q))) => {
                let same = p.char_indices().zip(q.chars()).find(|((_, c), d)| c != d).map_or(p.len().min(q.len()), |((k, _), _)| k);
                return (i + same, j + same);
            }
            _ => return (i, j),
        }
    }
}

/// A string quoted from a few characters before `at`.
fn from(s: &str, at: usize) -> String {
    let start = s[..at].char_indices().rev().nth(19).map_or(0, |(k, _)| k);
    format!("{}{}", if start > 0 { "…" } else { "" }, quoted(&s[start..]))
}

/// Whether a key names a hash or a preparation time: when a project or record was made, or how
/// long Bambu Studio took to slice it.
fn masked_key(key: &str) -> bool {
    let key = key.to_ascii_lowercase();
    ["sha", "sha1", "sha256", "md5", "hash", "digest", "utc"].iter().any(|end| key.ends_with(end))
        || matches!(key.as_str(), "creationdate" | "modificationdate" | "prepare_time" | "export_time" | "sliced_time"
            | "sliced_time_with_cache" | "generate_support_material_time" | "infill_time" | "make_perimeters_time")
}

/// The text with what each run writes afresh as `#`: a hash, hexadecimal digits as many as an
/// MD5, SHA-1 or SHA-256 has; a thread's address, `0x` and its hexadecimal digits; and a date
/// with its time.
fn run_masked(s: &str) -> Cow<'_, str> {
    let bytes = s.as_bytes();
    let hex = |w: &[u8]| w.iter().all(u8::is_ascii_hexdigit);
    let (mut out, mut last, mut i) = (String::new(), 0, 0);
    while i < bytes.len() {
        if !bytes[i].is_ascii_alphanumeric() || (i > 0 && bytes[i - 1].is_ascii_alphanumeric()) {
            i += 1;
            continue;
        }
        let start = i;
        if let Some(end) = date_time_end(bytes, start) {
            i = end;
        } else {
            while i < bytes.len() && bytes[i].is_ascii_alphanumeric() {
                i += 1;
            }
            let word = &bytes[start..i];
            let address = word.len() >= 10 && (word.starts_with(b"0x") || word.starts_with(b"0X")) && hex(&word[2..]);
            if !address && !(matches!(word.len(), 32 | 40 | 64) && hex(word)) {
                continue;
            }
        }
        out.push_str(&s[last..start]);
        out.push('#');
        last = i;
    }
    if last == 0 {
        return Cow::Borrowed(s);
    }
    out.push_str(&s[last..]);
    Cow::Owned(out)
}

/// Where a date and time that starts at `i` ends: ISO 8601's year, month, day, hours and minutes,
/// a space allowed for its `T`, with or without seconds, their fraction and a zone.
fn date_time_end(b: &[u8], i: usize) -> Option<usize> {
    let digits = |at: usize, n: usize| (at + n <= b.len() && b[at..at + n].iter().all(u8::is_ascii_digit)).then_some(at + n);
    let one = |at: usize, of: &[u8]| (at < b.len() && of.contains(&b[at])).then_some(at + 1);
    let mut at = digits(i, 4)?;
    for (separator, width) in [(&b"-"[..], 2), (b"-", 2), (b"T ", 2), (b":", 2)] {
        at = digits(one(at, separator)?, width)?;
    }
    if let Some(seconds) = one(at, b":").and_then(|s| digits(s, 2)) {
        at = seconds;
        if let Some(fraction) = one(at, b".").filter(|&f| digits(f, 1).is_some()) {
            at = (fraction..b.len()).find(|&k| !b[k].is_ascii_digit()).unwrap_or(b.len());
        }
    }
    if let Some(zone) = one(at, b"Z") {
        at = zone;
    } else if let Some(hours) = one(at, b"+-").and_then(|s| digits(s, 2)) {
        at = one(hours, b":").and_then(|s| digits(s, 2)).or_else(|| digits(hours, 2)).unwrap_or(hours);
    }
    Some(at)
}

/// Whether two strings are the same text around the same numbers, each number by value.
fn by_value(a: &str, b: &str) -> bool {
    let (mut x, mut y) = (Pieces { s: a, at: 0 }, Pieces { s: b, at: 0 });
    loop {
        match (x.next(), y.next()) {
            (None, None) => return true,
            (Some(Piece::Text(p)), Some(Piece::Text(q))) if p == q => {}
            (Some(Piece::Number(p)), Some(Piece::Number(q))) if number_equal(p, q) => {}
            _ => return false,
        }
    }
}

/// Numbers equal to one part in a billion, or within a billionth below one.
fn number_equal(x: f64, y: f64) -> bool {
    x == y || (x - y).abs() <= 1e-9 * x.abs().max(y.abs()).max(1.0)
}

enum Piece<'a> {
    Text(&'a str),
    Number(f64),
}

/// A string as runs of text and the numbers between them.
struct Pieces<'a> {
    s: &'a str,
    at: usize,
}

impl<'a> Iterator for Pieces<'a> {
    type Item = Piece<'a>;

    fn next(&mut self) -> Option<Piece<'a>> {
        let bytes = self.s.as_bytes();
        let start = self.at;
        if start >= bytes.len() {
            return None;
        }
        if let Some(end) = number_end(bytes, start) {
            self.at = end;
            return Some(Piece::Number(self.s[start..end].parse().unwrap_or(f64::NAN)));
        }
        self.at = (start + 1..bytes.len()).find(|&i| number_end(bytes, i).is_some()).unwrap_or(bytes.len());
        Some(Piece::Text(&self.s[start..self.at]))
    }
}

/// Where a number that starts at `i` ends: a sign, digits with a point or a point with digits,
/// and an exponent.
fn number_end(b: &[u8], i: usize) -> Option<usize> {
    let digits = |from: usize| (from..b.len()).find(|&k| !b[k].is_ascii_digit()).unwrap_or(b.len());
    let start = i + usize::from(matches!(b[i], b'+' | b'-'));
    let whole = digits(start);
    let mut end = whole;
    if b.get(end) == Some(&b'.') {
        let fraction = digits(end + 1);
        if whole > start || fraction > end + 1 {
            end = fraction;
        }
    }
    if end == start {
        return None;
    }
    if matches!(b.get(end), Some(b'e' | b'E')) {
        let sign = end + 1 + usize::from(matches!(b.get(end + 1), Some(b'+' | b'-')));
        let power = digits(sign);
        if power > sign {
            end = power;
        }
    }
    Some(end)
}

/// The mesh read out where a `<mesh>` element was.
fn cut<'m>(e: &Element, list: &'m [Mesh]) -> Option<&'m Mesh> {
    e.attribute(CUT).and_then(|n| n.parse::<usize>().ok()).and_then(|n| list.get(n))
}

fn attribute_map(e: &Element) -> BTreeMap<&str, &str> {
    e.attributes.iter().map(|(k, v)| (k.as_str(), v.as_str())).collect()
}

/// The key a `metadata` element names: its `key` or `name`, else its attribute names.
fn key(e: &Element) -> String {
    e.attribute("key").or_else(|| e.attribute("name")).map(String::from)
        .unwrap_or_else(|| e.attributes.iter().map(|(k, _)| k.as_str()).collect::<Vec<_>>().join(","))
}

/// An element's children that a key names, in any order: `metadata` by its key and the others by
/// their id. The rest, in order.
fn children(e: &Element) -> (BTreeMap<String, Vec<&Element>>, Vec<&Element>) {
    let (mut keyed, mut rest) = (BTreeMap::<String, Vec<&Element>>::new(), Vec::new());
    for c in &e.children {
        if c.local() == "metadata" {
            keyed.entry(format!("metadata[{}]", key(c))).or_default().push(c);
        } else if let Some(id) = c.attribute("id") {
            keyed.entry(format!("{}[id={id}]", c.local())).or_default().push(c);
        } else {
            rest.push(c);
        }
    }
    (keyed, rest)
}

/// Each element's name in a path, with its place among siblings of its name.
fn labels(elements: &[&Element]) -> Vec<String> {
    let mut counts: HashMap<&str, usize> = HashMap::new();
    elements.iter().for_each(|e| *counts.entry(e.local()).or_default() += 1);
    let mut seen: HashMap<&str, usize> = HashMap::new();
    elements.iter().map(|e| {
        let n = seen.entry(e.local()).or_default();
        *n += 1;
        if counts[e.local()] > 1 { format!("{}[{}]", e.local(), *n) } else { e.local().to_string() }
    }).collect()
}

/// A mesh's corners, its triangles as corner numbers, and each triangle's paint: its other
/// attributes in name order, empty when it has none.
#[derive(Default)]
struct Mesh {
    vertices: Vec<[f64; 3]>,
    triangles: Vec<[usize; 3]>,
    paint: Vec<String>,
}

impl Mesh {
    fn stl(bytes: &[u8]) -> Result<Mesh> {
        let vertices = stl_corners(bytes)?;
        let triangles = (0..vertices.len() / 3).map(|t| [3 * t, 3 * t + 1, 3 * t + 2]).collect::<Vec<_>>();
        Ok(Mesh { paint: vec![String::new(); triangles.len()], vertices, triangles })
    }

    /// The vertices and triangles inside a `<mesh>` element.
    fn read(body: &str) -> Result<Mesh> {
        let mut mesh = Mesh::default();
        for tag in body.split('<').skip(1) {
            let tag = tag.split('>').next().unwrap_or("").trim_end_matches('/');
            let (name, rest) = tag.split_once(|c: char| c.is_ascii_whitespace()).unwrap_or((tag, ""));
            if name == "vertex" {
                let mut p = [None; 3];
                for (k, v) in attributes(rest) {
                    if let Some(i) = ["x", "y", "z"].iter().position(|axis| *axis == k) {
                        p[i] = Some(v.parse::<f64>()?);
                    }
                }
                let [Some(x), Some(y), Some(z)] = p else { bail!("a vertex without x, y and z") };
                mesh.vertices.push([x, y, z]);
            } else if name == "triangle" {
                let (mut corners, mut paint) = ([None; 3], Vec::new());
                for (k, v) in attributes(rest) {
                    match ["v1", "v2", "v3"].iter().position(|c| *c == k) {
                        Some(i) => corners[i] = Some(v.parse::<usize>()?),
                        None if !v.is_empty() => paint.push(format!("{k}={v}")),
                        None => {}
                    }
                }
                let [Some(p), Some(q), Some(r)] = corners else { bail!("a triangle without v1, v2 and v3") };
                paint.sort();
                mesh.triangles.push([p, q, r]);
                mesh.paint.push(paint.join(" "));
            }
        }
        if mesh.triangles.iter().flatten().any(|&i| i >= mesh.vertices.len()) {
            bail!("a triangle names a vertex its mesh lacks");
        }
        Ok(mesh)
    }

    fn corners(&self, t: usize) -> [[f64; 3]; 3] {
        self.triangles[t].map(|i| self.vertices[i])
    }
}

/// A tag's `key="value"` pairs.
fn attributes(mut text: &str) -> impl Iterator<Item = (&str, &str)> {
    std::iter::from_fn(move || {
        let eq = text.find('=')?;
        let key = text[..eq].trim();
        let after = text[eq + 1..].trim_start();
        let quote = after.chars().next().filter(|c| *c == '"' || *c == '\'')?;
        let close = after[1..].find(quote)? + 1;
        let value = &after[1..close];
        text = &after[close + 1..];
        Some((key, value))
    })
}

/// The text with each `<mesh>` element's body read out, the element left empty with the
/// mesh's place in the list.
fn cut_meshes(text: &str) -> Result<(Cow<'_, str>, Vec<Mesh>)> {
    let mut meshes = Vec::new();
    let (mut out, mut rest) = (String::new(), text);
    while let Some(at) = open_tag(rest, "mesh") {
        let tail = &rest[at..];
        let head = tail.find('>').context("an unclosed <mesh> tag")?;
        let (body, after) = if tail[..head].ends_with('/') {
            ("", head + 1)
        } else {
            let close = tail.find("</mesh>").context("a <mesh> without its end")?;
            (&tail[head + 1..close], close + "</mesh>".len())
        };
        out.push_str(&rest[..at]);
        out.push_str(&format!("<mesh {CUT}=\"{}\"/>", meshes.len()));
        meshes.push(Mesh::read(body)?);
        rest = &tail[after..];
    }
    if meshes.is_empty() {
        return Ok((Cow::Borrowed(text), meshes));
    }
    out.push_str(rest);
    Ok((Cow::Owned(out), meshes))
}

/// Where the next `<name>` or `<name …>` tag opens.
fn open_tag(text: &str, name: &str) -> Option<usize> {
    let pattern = format!("<{name}");
    let mut from = 0;
    while let Some(i) = text[from..].find(&pattern) {
        let at = from + i;
        match text.as_bytes().get(at + pattern.len()) {
            Some(b'>' | b'/') => return Some(at),
            Some(c) if c.is_ascii_whitespace() => return Some(at),
            _ => from = at + pattern.len(),
        }
    }
    None
}

/// The largest distance along any axis between corresponding corners.
fn deviation(p: [[f64; 3]; 3], q: [[f64; 3]; 3]) -> f64 {
    (0..3).flat_map(|c| (0..3).map(move |k| (c, k))).map(|(c, k)| (p[c][k] - q[c][k]).abs()).fold(0.0, f64::max)
}

/// Triangles by their corners, in order, and paint. Corners count as the same within
/// `tolerance`, whatever the vertices' numbering. Triangles that are out of place are matched
/// one to one, corners in any cyclic order, to tell a new order from new triangles.
fn meshes(at: &str, a: &Mesh, b: &Mesh, tolerance: f64, found: &mut Found) {
    let n = a.triangles.len();
    let in_order = (n == b.triangles.len()).then(|| (0..n).map(|t| deviation(a.corners(t), b.corners(t))).fold(0.0, f64::max));
    if in_order.is_some_and(|worst| worst <= tolerance) {
        let painted = (0..n).filter(|&t| a.paint[t] != b.paint[t]).count();
        if painted > 0 {
            found.add(format!("{at}: {painted} of {n} triangles are painted otherwise"));
        }
        return;
    }
    let cell = (4.0 * tolerance).max(1e-3);
    let key = |c: [[f64; 3]; 3]| [0, 1, 2].map(|k| ((c[0][k] + c[1][k] + c[2][k]) / 3.0 / cell).floor() as i64);
    let mut grid: HashMap<[i64; 3], Vec<usize>> = HashMap::new();
    for u in 0..b.triangles.len() {
        grid.entry(key(b.corners(u))).or_default().push(u);
    }
    let mut used = vec![false; b.triangles.len()];
    let (mut lost_a, mut painted) = (Vec::new(), 0);
    for t in 0..n {
        let c = a.corners(t);
        let [x, y, z] = key(c);
        let cells = (-1..=1).flat_map(move |i| (-1..=1).flat_map(move |j| (-1..=1).map(move |k| [x + i, y + j, z + k])));
        let same = |u: &usize| {
            let d = b.corners(*u);
            !used[*u] && (0..3).any(|r| deviation(c, [d[r], d[(r + 1) % 3], d[(r + 2) % 3]]) <= tolerance)
        };
        let counterpart = cells.filter_map(|cell| grid.get(&cell)).flat_map(|list| list.iter()).copied().find(|u| same(u));
        match counterpart {
            Some(u) => {
                used[u] = true;
                painted += usize::from(a.paint[t] != b.paint[u]);
            }
            None => lost_a.push(t),
        }
    }
    let lost_b: Vec<usize> = (0..b.triangles.len()).filter(|&u| !used[u]).collect();
    if lost_a.is_empty() && lost_b.is_empty() {
        found.add(format!("{at}: the same {n} triangles in another order"));
    } else {
        found.add(format!("{at}: {} of A's {n} triangles are not in B, and {} of B's {} not in A", lost_a.len(), lost_b.len(),
            b.triangles.len()));
        if let Some(worst) = in_order {
            found.add(format!("{at}: in file order, a corner moves by up to {worst:.3e} mm"));
        }
        for (side, mesh, lost) in [('A', a, &lost_a), ('B', b, &lost_b)] {
            if let Some((low, high)) = bounds(lost.iter().flat_map(|&t| mesh.corners(t))) {
                let p = |v: [f64; 3]| format!("({:.3}, {:.3}, {:.3})", v[0], v[1], v[2]);
                found.add(format!("{at}: those of {side} lie within {} to {} mm", p(low), p(high)));
            }
        }
    }
    if painted > 0 {
        found.add(format!("{at}: {painted} matching triangles are painted otherwise"));
    }
}

fn bounds(points: impl Iterator<Item = [f64; 3]>) -> Option<([f64; 3], [f64; 3])> {
    points.fold(None, |range, p| match range {
        None => Some((p, p)),
        Some((low, high)) => Some(([0, 1, 2].map(|k| low[k].min(p[k])), [0, 1, 2].map(|k| high[k].max(p[k])))),
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn numbers_compare_by_value_inside_strings() {
        assert!(by_value("15", "15.0"));
        assert!(by_value("324.9", "324.900"));
        assert!(by_value("1 0 0 162.500000000", "1 0 0 162.5"));
        assert!(by_value("50%", "50.0%"));
        assert!(by_value("-0.000000000", "0"));
        assert!(!by_value("15", "15.1"));
        assert!(!by_value("part 15", "part15"));
        assert!(!by_value("support", "supports"));
    }

    #[test]
    fn hashes_and_preparation_times_are_masked() {
        let a = serde_json::json!({"project_sha256": "aa", "prepared_utc": "2026-11-15T03:00:00+00:00",
            "gcode": {"plate_1.gcode": "df571caf3da7c4f9c9ac2fb1328f032b1ea129cf7f2be7e99bbaeeaae3912e36"},
            "slice_result": {"export_time": 2020, "total_predication": 1157.2}});
        let b = serde_json::json!({"project_sha256": "bb", "prepared_utc": "2026-11-16T04:00:00+00:00",
            "gcode": {"plate_1.gcode": "08dd02657eaa46ab1ade1926238ab2f47c81811168aff5b6f098d1da75908d87"},
            "slice_result": {"export_time": 2100, "total_predication": 1157.2}});
        let mut found = Found::default();
        json("", &a, &b, &mut found);
        assert!(found.lines.is_empty(), "{:?}", found.lines);
        assert_eq!(found.masked, 4);
        let c = serde_json::json!({"slice_result": {"total_predication": 1200.0}});
        let d = serde_json::json!({"slice_result": {"total_predication": 1157.2}});
        let mut found = Found::default();
        json("", &c, &d, &mut found);
        assert_eq!(found.lines, ["slice_result/total_predication: A 1200.0, B 1157.2"]);
        let mut found = Found::default();
        strings("line 2", "[2026-11-15 15:55:46.515132] [0x000000017037f000] [error]   ZFiller: encounter idx from clip: 424",
            "[2026-11-15 15:56:11.849715] [0x000000016d85f000] [error]   ZFiller: encounter idx from clip: 424", false, &mut found);
        assert!(found.lines.is_empty(), "{:?}", found.lines);
        assert_eq!(found.masked, 1);
        strings("observed_date", "2026-09-20", "2026-09-21", false, &mut found);
        assert_eq!(found.lines, ["observed_date: A \"2026-09-20\", B \"2026-09-21\""]);
    }

    #[test]
    fn changed_key_lists_compare_as_sets() {
        let a = serde_json::json!({"different_settings_to_system": ["b;a", "c"],
            "supplied_settings": {"different_settings_to_system": {"value": ["e;f"], "reason": "the recipe"}}});
        let b = serde_json::json!({"different_settings_to_system": ["a;b", "c;d"],
            "supplied_settings": {"different_settings_to_system": {"value": ["f;e"], "reason": "the recipe"}}});
        let mut found = Found::default();
        json("", &a, &b, &mut found);
        assert_eq!(found.lines, ["different_settings_to_system[1]: only B lists d"]);
    }

    #[test]
    fn a_setting_of_several_lines_shows_its_line_that_differs() {
        let a = serde_json::json!({"machine_start_gcode": "M104 S0\nG29.1 Z0.12\nM400", "compatible_printers": ["H2C"]});
        let b = serde_json::json!({"machine_start_gcode": "M104 S0.0\nG29.1 Z0.08\nM400", "compatible_printers": ["H2C", "H2D"]});
        let mut found = Found::default();
        json("", &a, &b, &mut found);
        assert_eq!(found.lines, ["compatible_printers: A has 1 items, B 2; B goes on with \"H2D\"",
            "machine_start_gcode line 2: A \"G29.1 Z0.12\", B \"G29.1 Z0.08\""]);
    }

    fn model(vertices: &str, triangles: &str) -> String {
        format!("<?xml version='1.0'?><model unit=\"millimeter\"><metadata name=\"Title\">t</metadata><resources>\
                 <object id=\"1\" type=\"model\"><mesh><vertices>{vertices}</vertices><triangles>{triangles}</triangles>\
                 </mesh></object></resources></model>")
    }

    fn compared(a: &str, b: &str) -> Found {
        let options = Options { a: PathBuf::new(), b: PathBuf::new(), mesh_tolerance: 1e-6, bead_tolerance: 0.05, limit: 12, all: false };
        let report = Report { options: &options, checkouts: [None, None], identical: 0, by_value: 0, differing: 0, masked: 0, slices: HashMap::new(),
                              only: Vec::new() };
        let mut found = Found::default();
        report.compare("3D/Objects/object_1.model", a.as_bytes(), b.as_bytes(), &mut found).unwrap();
        found
    }

    const SQUARE: &str = "<vertex x=\"0\" y=\"0\" z=\"0\"/><vertex x=\"1\" y=\"0\" z=\"0\"/><vertex x=\"1\" y=\"1\" z=\"0\"/>\
                          <vertex x=\"0\" y=\"1\" z=\"0\"/>";

    #[test]
    fn meshes_compare_by_corners_whatever_their_numbering() {
        let a = model(SQUARE, "<triangle v1=\"0\" v2=\"1\" v3=\"2\"/><triangle v1=\"0\" v2=\"2\" v3=\"3\" paint_seam=\"8\"/>");
        let renumbered = "<vertex x=\"1.0000004\" y=\"1\" z=\"0\"/><vertex x=\"0\" y=\"0\" z=\"0\"/><vertex x=\"1\" y=\"0\" z=\"0\"/>\
                          <vertex x=\"0\" y=\"1\" z=\"0\"/>";
        let b = model(renumbered, "<triangle v1=\"1\" v2=\"2\" v3=\"0\"/><triangle v1=\"1\" v2=\"0\" v3=\"3\" paint_seam=\"8\"/>");
        assert!(compared(&a, &b).lines.is_empty());
        let reordered = model(SQUARE, "<triangle v1=\"0\" v2=\"2\" v3=\"3\" paint_seam=\"8\"/><triangle v1=\"1\" v2=\"2\" v3=\"0\"/>");
        assert_eq!(compared(&a, &reordered).lines, ["model/resources/object[id=1]/mesh: the same 2 triangles in another order"]);
        let unpainted = model(SQUARE, "<triangle v1=\"0\" v2=\"1\" v3=\"2\"/><triangle v1=\"0\" v2=\"2\" v3=\"3\"/>");
        assert_eq!(compared(&a, &unpainted).lines, ["model/resources/object[id=1]/mesh: 1 of 2 triangles are painted otherwise"]);
        let moved = model(&SQUARE.replace("x=\"1\" y=\"1\"", "x=\"1.1\" y=\"1\""), "<triangle v1=\"0\" v2=\"1\" v3=\"2\"/>\
                          <triangle v1=\"0\" v2=\"2\" v3=\"3\" paint_seam=\"8\"/>");
        let lines = compared(&a, &moved).lines;
        assert_eq!(lines[0], "model/resources/object[id=1]/mesh: 2 of A's 2 triangles are not in B, and 2 of B's 2 not in A");
    }

    #[test]
    fn settings_metadata_compares_as_a_map() {
        let a = "<config><object id=\"2\"><metadata key=\"name\" value=\"lever\"/><metadata key=\"wall_loops\" value=\"3\"/>\
                 </object></config>";
        let b = "<config><object id=\"2\"><metadata key=\"wall_loops\" value=\"3.0\"/><metadata key=\"name\" value=\"lever\"/>\
                 </object></config>";
        assert!(compared(a, b).lines.is_empty());
        let c = b.replace("3.0", "4");
        assert_eq!(compared(a, &c).lines, ["config/object[id=2]/metadata[wall_loops]@value: A \"3\", B \"4\""]);
        let two = "<config><object id=\"3\"><metadata key=\"name\" value=\"G1\"/></object>\
                   <object id=\"6\"><metadata key=\"name\" value=\"G2\"/></object><plate/></config>";
        let swapped = "<config><object id=\"6\"><metadata key=\"name\" value=\"G2\"/></object>\
                       <object id=\"3\"><metadata key=\"name\" value=\"G1\"/></object><plate/></config>";
        assert!(compared(two, swapped).lines.is_empty());
        let items = "<config><assemble><assemble_item object_id=\"3\" transform=\"1 0 0\"/><assemble_item object_id=\"6\" \
                     transform=\"0 1 0\"/></assemble></config>";
        let reversed = "<config><assemble><assemble_item object_id=\"6\" transform=\"0 1 0\"/><assemble_item object_id=\"3\" \
                        transform=\"1 0 0\"/></assemble></config>";
        assert_eq!(compared(items, reversed).lines, ["config/assemble: the same 2 assemble_item elements in another order"]);
    }
}
