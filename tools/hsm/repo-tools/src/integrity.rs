//! Explicit source readings compare builder instructions, board pins and published model colours with their authorities.
use anyhow::{Context, Result, ensure};
use regex::Regex;
use serde::Deserialize;
use std::{
    collections::{BTreeMap, BTreeSet},
    io::Read,
    path::Path,
    process::Command,
};
#[derive(Deserialize)]
struct Rules {
    asin_waived: BTreeMap<String, String>,
    not_a_brand: BTreeSet<String>,
    brand_waived: BTreeMap<String, String>,
    generic: Vec<(String, String)>,
    cross: Vec<(String, String, String)>,
    no_pin: String,
    electrical: String,
}
fn rules() -> Result<Rules> {
    Ok(serde_json::from_str(include_str!("check-rules.json"))?)
}
fn report(failures: &[String], success: &str) -> i32 {
    if failures.is_empty() {
        println!("\n✓ {success}");
        0
    } else {
        println!("\nDRIFT: {} mismatch(es):", failures.len());
        for failure in failures {
            println!("  ✗ {failure}");
        }
        1
    }
}
fn locations(corpus: &BTreeMap<String, String>, token: &str) -> String {
    let token = token.to_lowercase();
    let all: Vec<_> = corpus
        .iter()
        .filter_map(|(name, text)| {
            text.lines()
                .position(|l| l.to_lowercase().contains(&token))
                .map(|i| format!("{name}:{}", i + 1))
        })
        .collect();
    let mut out = all.iter().take(3).cloned().collect::<Vec<_>>().join(", ");
    if all.len() > 3 {
        out += &format!(" +{} more", all.len() - 3);
    }
    out
}
pub fn ledger(root: &Path) -> Result<i32> {
    let r = rules()?;
    let bom = crate::text(root.join("hardware/ledger/bom.md"))?;
    let tools = crate::text(root.join("hardware/ledger/tools.md"))?;
    let history = crate::text(root.join("hardware/ledger/purchases.md"))?
        + &crate::text(root.join("hardware/ledger/inventory.md"))?;
    let carried = (bom.clone() + &tools).to_lowercase();
    let mut corpus = BTreeMap::new();
    for path in crate::files(&root.join("hardware/assembly")) {
        let rel = path.strip_prefix(root)?.to_string_lossy().into_owned();
        if path.extension().is_some_and(|e| e == "md")
            && path.parent() == Some(root.join("hardware/assembly").as_path())
        {
            corpus.insert(rel, crate::text(path)?);
        }
    }
    let asin = Regex::new(r"\bB0[A-Z0-9]{8}\b")?;
    let mut failures = Vec::new();
    let tokens: BTreeSet<_> = corpus
        .values()
        .flat_map(|s| asin.find_iter(s).map(|m| m.as_str().to_owned()))
        .collect();
    for token in tokens {
        if !r.asin_waived.contains_key(&token) && !carried.contains(&token.to_lowercase()) {
            failures.push(format!("ASIN cited by an instruction, carried by neither bom.md nor tools.md: {token} ({})",locations(&corpus,&token)));
        }
    }
    let brandish = Regex::new(r"\b[A-Z][A-Za-z]*[A-Z][A-Za-z0-9]*\b|\b[A-Z][a-z]{3,}\b")?;
    let orders = Regex::new(r"\.\s*Order|\bOrder #")?;
    let mut brands = BTreeSet::new();
    for line in history.lines().filter(|l| l.starts_with('|')) {
        if let Some(name) = line.split('|').nth(1) {
            let name = name.replace(['[', ']'], "").replace("~~", "");
            let name = orders.split(&name).next().unwrap_or("");
            for b in brandish.find_iter(name).map(|m| m.as_str()) {
                if b.len() >= 4 && !r.not_a_brand.contains(b) {
                    brands.insert(b.to_owned());
                }
            }
        }
    }
    let corpus_text = corpus.values().cloned().collect::<Vec<_>>().join("\n");
    let words_rx = Regex::new(r"[A-Za-z][A-Za-z0-9-]*")?;
    let words: BTreeSet<_> = words_rx
        .find_iter(&corpus_text)
        .map(|m| m.as_str())
        .collect();
    for b in &brands {
        if !r.brand_waived.contains_key(b)
            && words.contains(b.as_str())
            && !carried.contains(&b.to_lowercase())
        {
            failures.push(format!(
                "instruction names a purchased brand the ledger no longer carries: {b} ({})",
                locations(&corpus, b)
            ));
        }
    }
    let carried_names = (bom.clone() + &tools)
        .lines()
        .filter(|l| l.starts_with('|'))
        .filter_map(|l| l.split('|').nth(1))
        .collect::<Vec<_>>()
        .join("\n")
        .to_lowercase();
    for (pattern, needle) in &r.generic {
        let regex = Regex::new(&format!("(?i){pattern}"))?;
        let named: Vec<_> = corpus
            .iter()
            .flat_map(|(name, text)| {
                text.lines()
                    .enumerate()
                    .filter_map(|(i, l)| regex.is_match(l).then(|| format!("{name}:{}", i + 1)))
                    .collect::<Vec<_>>()
            })
            .collect();
        if !named.is_empty() && !carried_names.contains(needle) {
            failures.push(format!(
                "instructions name a generic material no ledger row carries: {needle:?} ({})",
                named.iter().take(3).cloned().collect::<Vec<_>>().join(", ")
            ));
        }
    }
    let section = Regex::new(r"^##\s+(\d+)\.")?;
    let cite = Regex::new(r"bom\.md[^§\n]{0,80}§\s*(\d+)")?;
    let mut sections = BTreeMap::<u32, String>::new();
    let mut current = None;
    for line in bom.lines() {
        if let Some(c) = section.captures(line) {
            current = Some(c[1].parse()?);
        } else if let Some(n) = current {
            sections
                .entry(n)
                .or_default()
                .push_str(&(line.to_owned() + "\n"));
        }
    }
    for (name, text) in &corpus {
        for (i, line) in text.lines().enumerate() {
            let cited = cite
                .captures_iter(line)
                .map(|c| c[1].parse())
                .collect::<std::result::Result<BTreeSet<u32>, _>>()?;
            if cited.is_empty() {
                continue;
            }
            for token in asin.find_iter(line).map(|m| m.as_str()) {
                if r.asin_waived.contains_key(token) {
                    continue;
                }
                let actual: BTreeSet<_> = sections
                    .iter()
                    .filter_map(|(n, body)| body.contains(token).then_some(*n))
                    .collect();
                if !actual.is_empty() && cited.is_disjoint(&actual) {
                    let joined = |s: &BTreeSet<u32>| {
                        s.iter().map(u32::to_string).collect::<Vec<_>>().join("/§")
                    };
                    failures.push(format!("instruction cites the wrong bom.md section for {token}: says §{}, the row is in §{} ({name}:{})",joined(&cited),joined(&actual),i+1));
                }
            }
        }
    }
    println!(
        "instructions: {} procedures | ledger brands: {} | waived: {} ASIN + {} brand",
        corpus.len(),
        brands.len(),
        r.asin_waived.len(),
        r.brand_waived.len()
    );
    Ok(report(
        &failures,
        "every part the instructions name is carried by bom.md or tools.md.",
    ))
}
pub fn pinmap(root: &Path) -> Result<i32> {
    let r = rules()?;
    let board = crate::text(root.join("hardware/pcb/pcba/pcba.tsx"))?;
    let pinout = crate::text(root.join("hardware/wiring/esp32-pinout.mmd"))?;
    let bom = crate::text(root.join("hardware/ledger/bom.md"))?;
    let used: BTreeSet<u32> = Regex::new(r"\bU1\.IO(\d+)|\.U1[AB]? > \.IO(\d+)")?
        .captures_iter(&board)
        .map(|c| c.get(1).or_else(|| c.get(2)).unwrap().as_str().parse())
        .collect::<std::result::Result<_, _>>()?;
    let mut roles = BTreeMap::<u32, String>::new();
    for c in Regex::new(r#"\["GPIO (\d+)\s+([^"]*)"\]"#)?.captures_iter(&pinout) {
        roles.insert(c[1].parse()?, c[2].trim().to_owned());
    }
    for c in Regex::new(r"%%\s*GPIO (\d+)\s+(\w[^\n]*)")?.captures_iter(&pinout) {
        roles
            .entry(c[1].parse()?)
            .or_insert_with(|| c[2].trim().to_owned());
    }
    let free: BTreeSet<u32> = Regex::new(r"GPIO (\d+)\s*-\s*free")?
        .captures_iter(&pinout)
        .map(|c| c[1].parse())
        .collect::<std::result::Result<_, _>>()?;
    let documented: BTreeSet<_> = roles.keys().copied().collect();
    let mut failures = Vec::new();
    for g in used.difference(&documented) {
        failures.push(format!(
            "GPIO{g}: used on the main board (pcba.tsx) but NOT documented in esp32-pinout.mmd"
        ));
    }
    for g in documented.difference(&used).filter(|g| !free.contains(*g)) {
        failures.push(format!(
            "GPIO{g}: documented in esp32-pinout.mmd (role {:?}) but NOT used on the main board",
            roles[g]
        ));
    }
    for (name, mk, bk) in &r.cross {
        if !Regex::new(mk)?.is_match(&board) {
            failures.push(format!(
                "cross-table: {name:?} expected on the main board (pcba.tsx /{mk}/) — not found"
            ));
        }
        if !Regex::new(bk)?.is_match(&bom) {
            failures.push(format!(
                "cross-table: {name:?} expected in the BOM (/{bk}/) — not found"
            ));
        }
    }
    let electrical = Regex::new(&format!("(?i){}", r.electrical))?;
    let no_pin = Regex::new(&r.no_pin)?;
    let cross = r
        .cross
        .iter()
        .map(|(_, _, bk)| Regex::new(bk))
        .collect::<std::result::Result<Vec<_>, _>>()?;
    for line in bom.lines().filter(|l| {
        l.starts_with('|')
            && !l.starts_with("| Part ")
            && !l.trim_start_matches('|').trim_start().starts_with("---")
    }) {
        let name = line.split('|').nth(1).unwrap_or("").trim();
        if electrical.is_match(name)
            && !no_pin.is_match(name)
            && !cross.iter().any(|r| r.is_match(name))
        {
            failures.push(format!(
                "untracked electrical BOM part (give it a CROSS pin entry, or add to NO_PIN): {}",
                name.chars().take(70).collect::<String>()
            ));
        }
    }
    println!(
        "board GPIOs in use: {} | documented: {} (free: {}) | cross-table fns: {}",
        used.len(),
        documented.len(),
        free.len(),
        r.cross.len()
    );
    Ok(report(
        &failures,
        "pin map in sync: the pinout and the BOM agree with the main board.",
    ))
}
pub fn purchases(root: &Path) -> Result<i32> {
    let program = crate::program(root, "purchases")?;
    let run = Command::new(program)
        .arg("--check")
        .current_dir(root)
        .status()?;
    Ok(run.code().unwrap_or(1))
}
fn carries_colour(path: &Path) -> bool {
    let Ok(mut file) = std::fs::File::open(path) else {
        return false;
    };
    let mut buffer = vec![0; 1 << 20];
    let mut tail = Vec::new();
    loop {
        let Ok(n) = file.read(&mut buffer) else {
            return false;
        };
        if n == 0 {
            return false;
        }
        tail.extend_from_slice(&buffer[..n]);
        if tail
            .windows(b"COLOUR_RGB".len())
            .any(|w| w == b"COLOUR_RGB")
        {
            return true;
        }
        let start = tail.len().saturating_sub(b"COLOUR_RGB".len() - 1);
        tail = tail[start..].to_vec();
    }
}
pub fn colours(root: &Path) -> Result<i32> {
    #[derive(Deserialize)]
    struct Selection {
        website: Website,
    }
    #[derive(Deserialize)]
    struct Website {
        solids: BTreeMap<String, String>,
    }
    let selection: Selection =
        serde_json::from_str(&crate::text(root.join("hardware/cad-artifacts.json"))?)?;
    let mut models: Vec<_> = selection
        .website
        .solids
        .into_keys()
        .filter(|p| p.starts_with("hardware/") && p.ends_with(".step"))
        .collect();
    models.sort();
    let mut absent = Vec::new();
    let mut grey = Vec::new();
    for path in &models {
        if !root.join(path).is_file() {
            absent.push(path);
            continue;
        }
        let payload = root.join(format!("{path}.mesh"));
        let coloured = if payload.is_file() {
            let header = hsm_build_data::payload::header(&payload)
                .with_context(|| format!("read {}", payload.display()))?;
            header["meshes"]
                .as_array()
                .context("payload mesh records")?
                .iter()
                .all(|m| m["color"].as_array().is_some_and(|c| !c.is_empty()))
        } else {
            carries_colour(&root.join(path))
        };
        if !coloured {
            grey.push(path);
        }
    }
    for path in &absent {
        println!("  not on this disk: {path}");
    }
    if !grey.is_empty() {
        println!("  {} model(s) the site lists name no colour:", grey.len());
        for path in &grey {
            println!("    {path}");
        }
        println!(
            "  The native producer supplies each body's material colour to the viewer payload."
        );
    }
    if !absent.is_empty() {
        println!(
            "step colours: {} of {} site models are not on this disk; node web/scripts/fetch-cad-artifacts.mjs fetches them.",
            absent.len(),
            models.len()
        );
    } else {
        println!(
            "step colours: {}/{} site models draw in the colour of what they are made of",
            models.len() - grey.len(),
            models.len()
        );
    }
    Ok(i32::from(!absent.is_empty() || !grey.is_empty()))
}
pub fn cli(root: &Path, args: &[String]) -> Result<i32> {
    ensure!(
        args.len() == 1,
        "check needs exactly one name: ledger, pinmap, purchase-evidence, step-colours, enclosure-mating-clearance or paths"
    );
    match args[0].as_str() {
        "ledger" => ledger(root),
        "pinmap" => pinmap(root),
        "purchase-evidence" => purchases(root),
        "step-colours" => colours(root),
        "paths" => crate::paths::cli(root, &[]),
        "enclosure-mating-clearance" => crate::mating::run(root),
        name => anyhow::bail!("unknown explicit check {name}"),
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    fn fixture(name: &str) -> std::path::PathBuf {
        let root = std::env::temp_dir().join(format!(
            "hsm-{name}-{}-{}",
            std::process::id(),
            crate::now().to_bits()
        ));
        std::fs::create_dir_all(&root).unwrap();
        root
    }
    fn write(root: &Path, name: &str, body: &str) {
        let path = root.join(name);
        std::fs::create_dir_all(path.parent().unwrap()).unwrap();
        std::fs::write(path, body).unwrap();
    }
    #[test]
    fn a_tool_note_does_not_stock_the_material() {
        let root = fixture("ledger-reading");
        write(
            &root,
            "hardware/ledger/bom.md",
            "## 1. Bench\n| part |\n| OldBrand B012345678 |\n",
        );
        write(
            &root,
            "hardware/ledger/tools.md",
            "| part | notes |\n| heat gun | heat-shrink activation |\n",
        );
        write(&root, "hardware/ledger/purchases.md", "| OldBrand |\n");
        write(&root, "hardware/ledger/inventory.md", "");
        write(
            &root,
            "hardware/assembly/example.md",
            "Use OldBrand B012345678 from bom.md §1, and heat-shrink.\n",
        );
        assert_eq!(ledger(&root).unwrap(), 1);
        write(
            &root,
            "hardware/ledger/bom.md",
            "## 1. Bench\n| part |\n| OldBrand B012345678 |\n| heat-shrink |\n",
        );
        assert_eq!(ledger(&root).unwrap(), 0);
        std::fs::remove_dir_all(root).unwrap();
    }
    #[test]
    fn viewer_payload_colour_takes_precedence_over_step_colour() {
        let root = fixture("model-colour");
        write(
            &root,
            "hardware/cad-artifacts.json",
            r#"{"website":{"solids":{"hardware/part.step":"fixture-hash"}}}"#,
        );
        write(&root, "hardware/part.step", "COLOUR_RGB\n");
        let write_payload = |colour: serde_json::Value| {
            let body =
                serde_json::to_vec(&serde_json::json!({"meshes":[{"color":colour}]})).unwrap();
            let mut bytes = (body.len() as u32).to_le_bytes().to_vec();
            bytes.extend(body);
            std::fs::write(root.join("hardware/part.step.mesh"), bytes).unwrap();
        };
        write_payload(serde_json::Value::Null);
        assert_eq!(colours(&root).unwrap(), 1);
        write_payload(serde_json::json!([0., 0., 0.]));
        assert_eq!(colours(&root).unwrap(), 0);
        std::fs::remove_dir_all(root).unwrap();
    }
}
