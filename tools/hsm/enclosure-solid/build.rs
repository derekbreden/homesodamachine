//! The stage identity binds retained geometry to the implementation compiled into this library.
use sha2::{Digest, Sha256};
use std::{
    collections::BTreeSet,
    env, fs,
    path::{Path, PathBuf},
    process::Command,
};

fn files(path: &Path, out: &mut BTreeSet<PathBuf>) {
    println!("cargo:rerun-if-changed={}", path.display());
    if path.is_dir() {
        for entry in fs::read_dir(path).expect("geometry source directory") {
            files(&entry.expect("geometry source entry").path(), out);
        }
    } else if path.is_file() {
        out.insert(path.into());
    }
}

fn main() {
    let manifest = PathBuf::from(env::var_os("CARGO_MANIFEST_DIR").unwrap());
    let workspace = manifest.parent().unwrap();
    let root = workspace.parent().unwrap().parent().unwrap();
    let solid = root.join("hardware/printed-parts/enclosure/enclosure/solid");
    let mut sources = BTreeSet::new();
    for path in [
        workspace.join("kernel/src"),
        workspace.join("manifold/src"),
        root.join("vendor/manifold-rust/src"),
        root.join("hardware/printed-parts/enclosure/enclosure/numbers"),
        solid,
    ] {
        files(&path, &mut sources);
    }
    for path in [
        workspace.join("kernel/Cargo.toml"),
        workspace.join("manifold/Cargo.toml"),
        workspace.join("manifold/build.rs"),
        root.join("vendor/manifold-rust/Cargo.toml"),
        manifest.join("Cargo.toml"),
        manifest.join("build.rs"),
        root.join("hardware/printed-parts/enclosure/nameplate/snap_geometry.rs"),
    ] {
        files(&path, &mut sources);
    }
    let mut hash = Sha256::new();
    let mut compiled_inputs = String::new();
    for path in sources {
        if path.starts_with(root.join("hardware/printed-parts/enclosure/enclosure/solid"))
            && matches!(
                path.file_name().and_then(|name| name.to_str()),
                Some("run.rs" | "pieces.rs" | "sources.rs")
            )
        {
            continue;
        }
        hash.update(
            path.strip_prefix(root)
                .unwrap()
                .to_string_lossy()
                .as_bytes(),
        );
        hash.update([0]);
        hash.update(fs::read(&path).expect("geometry source"));
        hash.update([0]);
        compiled_inputs.push_str(&format!(
            "const _: &[u8] = include_bytes!({:?});\n",
            path.to_string_lossy()
        ));
    }
    fs::write(
        PathBuf::from(env::var_os("OUT_DIR").unwrap()).join("stage_inputs.rs"),
        compiled_inputs,
    )
    .expect("compiled stage inputs");
    // External dependency records follow the locked dependency closure, so unrelated workspace
    // packages do not change the identity.
    let lock = workspace.join("Cargo.lock");
    println!("cargo:rerun-if-changed={}", lock.display());
    let lock = fs::read_to_string(lock).expect("workspace lock");
    let packages: Vec<&str> = lock.split("[[package]]").skip(1).collect();
    let field = |record: &str, key: &str| {
        record.lines().find_map(|line| {
            line.strip_prefix(&format!("{key} = \""))
                .and_then(|s| s.strip_suffix('"'))
                .map(str::to_owned)
        })
    };
    let mut pending = vec![
        ("hsm-enclosure-solid".to_owned(), None),
        ("hsm-kernel".to_owned(), None),
    ];
    let mut visited = BTreeSet::new();
    while let Some((name, version)) = pending.pop() {
        for record in &packages {
            if field(record, "name").as_deref() != Some(&name)
                || version
                    .as_ref()
                    .is_some_and(|version| field(record, "version").as_ref() != Some(version))
            {
                continue;
            }
            let key = (name.clone(), field(record, "version").unwrap());
            if !visited.insert(key) {
                continue;
            }
            hash.update(record.as_bytes());
            let mut dependencies = false;
            for line in record.lines() {
                if line == "dependencies = [" {
                    dependencies = true;
                    continue;
                }
                if dependencies && line == "]" {
                    break;
                }
                if dependencies {
                    if let Some(dep) = line
                        .trim()
                        .strip_prefix('"')
                        .and_then(|s| s.strip_suffix("\","))
                    {
                        let mut words = dep.split_whitespace();
                        pending.push((
                            words.next().unwrap().into(),
                            words.next().map(str::to_owned),
                        ));
                    }
                }
            }
        }
    }
    for name in [
        "TARGET",
        "CARGO_CFG_TARGET_FEATURE",
        "CARGO_ENCODED_RUSTFLAGS",
    ] {
        println!("cargo:rerun-if-env-changed={name}");
        hash.update(env::var(name).unwrap_or_default());
    }
    if let Ok(compiler) = env::var("RUSTC") {
        if let Ok(version) = Command::new(compiler).arg("-vV").output() {
            hash.update(version.stdout);
        }
    }
    println!(
        "cargo:rustc-env=HSM_STAGE_IMPLEMENTATION={:x}",
        hash.finalize()
    );
}
