//! A checkout without the payload a query asks for takes the one its pointer file names.
//!
//! `hardware/cad-artifacts.json` names every published payload by the SHA-256 of its bytes,
//! and `web/scripts/fetch-cad-artifacts.mjs` fills a tree with all of them. A query needs one:
//! the main checkout's copy when it holds those bytes, cloned, or else the store's object by
//! name, gunzipped. Either is held to the hash before it is renamed into place. A payload on
//! disk is never replaced, and nothing is built.
use anyhow::{Context, Result, bail, ensure};
use serde_json::Value;
use sha2::{Digest, Sha256};
use std::{
    fs::{self, File},
    io,
    path::{Path, PathBuf},
    process::{Command, Stdio},
};

pub const POINTERS: &str = "hardware/cad-artifacts.json";

/// The checkout holding `path`: its nearest ancestor with a `.git`.
fn checkout(path: &Path) -> Option<&Path> {
    path.ancestors().skip(1).find(|p| p.join(".git").exists())
}

/// A linked worktree's main checkout. Its `.git` file names the worktree's git directory,
/// whose `commondir` names the repository's.
fn main_checkout(root: &Path) -> Option<PathBuf> {
    let link = fs::read_to_string(root.join(".git")).ok()?;
    let gitdir = root.join(link.strip_prefix("gitdir:")?.trim());
    let common = gitdir.join(fs::read_to_string(gitdir.join("commondir")).ok()?.trim());
    Some(common.canonicalize().ok()?.parent()?.to_path_buf())
}

fn digest(path: &Path) -> Result<String> {
    let mut hash = Sha256::new();
    io::copy(&mut File::open(path)?, &mut hash)?;
    Ok(format!("{:x}", hash.finalize()))
}

/// The object at `url`, gunzipped into `part`.
fn download(url: &str, part: &Path) -> Result<()> {
    let mut curl = Command::new("curl")
        .args(["-fsSL", "--connect-timeout", "15", "--speed-limit", "1024"])
        .args(["--speed-time", "60", url])
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .context("start curl")?;
    let gunzip = Command::new("gzip")
        .arg("-dc")
        .stdin(curl.stdout.take().context("curl has no output")?)
        .stdout(File::create(part)?)
        .stderr(Stdio::piped())
        .output()
        .context("run gzip")?;
    let fetched = curl.wait_with_output()?;
    ensure!(
        fetched.status.success(),
        "{url}: {}",
        String::from_utf8_lossy(&fetched.stderr).trim()
    );
    ensure!(
        gunzip.status.success(),
        "{url}: gzip: {}",
        String::from_utf8_lossy(&gunzip.stderr).trim()
    );
    Ok(())
}

/// Puts the payload at `scene` in place when it is absent and its checkout's pointer file
/// names it. Anything else is left for the daemon to answer.
pub fn ensure(scene: &Path) -> Result<()> {
    if scene.as_os_str().is_empty() || scene.exists() {
        return Ok(());
    }
    let Some(root) = checkout(scene) else {
        return Ok(());
    };
    let Ok(text) = fs::read_to_string(root.join(POINTERS)) else {
        return Ok(());
    };
    let pointers: Value = serde_json::from_str(&text)
        .with_context(|| format!("read {}", root.join(POINTERS).display()))?;
    let rel = scene.strip_prefix(root)?.to_string_lossy().into_owned();
    let Some(hash) = pointers["solids"][&rel].as_str() else {
        return Ok(());
    };
    ensure!(
        hash.len() == 64 && hash.bytes().all(|b| b.is_ascii_hexdigit()),
        "{POINTERS} names {rel} by {hash:?}, which is not a SHA-256"
    );
    fs::create_dir_all(scene.parent().context("payload has no directory")?)?;
    let part = PathBuf::from(format!("{}.{}.part", scene.display(), std::process::id()));
    let settle = |from: &str| -> Result<()> {
        let got = digest(&part)?;
        ensure!(got == hash, "{from} holds {got}");
        fs::rename(&part, scene)?;
        eprintln!("hsm: {rel} is the published {hash}, from {from}");
        Ok(())
    };

    // The main checkout first, then the store and the release it falls back to: the order
    // `fetch-cad-artifacts.mjs` reads them in, behind a copy that needs no network.
    let mut copies = Vec::new();
    if let Some(main) = main_checkout(root) {
        let there = main.join(&rel);
        if there.is_file() {
            copies.push(there);
        }
    }
    let mut urls = Vec::new();
    let objects = pointers["store"]["objects"]
        .as_str()
        .or(pointers["release"]["objects"].as_str());
    if let Some(objects) = objects {
        let release = pointers["release"]["url"]
            .as_str()
            .and_then(|url| url.rfind('/').map(|end| &url[..=end]));
        for base in [pointers["store"]["url"].as_str(), release]
            .into_iter()
            .flatten()
        {
            urls.push(format!("{base}{objects}{hash}.gz"));
        }
    }
    let mut refused = Vec::new();
    let attempts = copies
        .iter()
        .map(|there| {
            // On APFS the copy is a clone: no bytes move until one side writes.
            (there.display().to_string(), fs::copy(there, &part).map(drop).map_err(Into::into))
        })
        .chain(urls.iter().map(|url| (url.clone(), download(url, &part))));
    for (from, fetched) in attempts {
        let taken = fetched.and_then(|()| settle(&from));
        let _ = fs::remove_file(&part);
        match taken {
            Ok(()) => return Ok(()),
            Err(e) => refused.push(format!("{e:#}")),
        }
    }
    bail!(
        "payload not found: {}; {POINTERS} names it as {hash}, and nothing supplied those bytes: {}",
        scene.display(),
        if refused.is_empty() {
            "it names no store".to_owned()
        } else {
            refused.join("; ")
        }
    )
}
