//! The engine fingerprint binds cached geometry to the compiled Rust boolean source.
use sha2::{Digest, Sha256};
use std::{
    collections::BTreeSet,
    env, fs,
    path::{Path, PathBuf},
};

fn files(path: &Path, inputs: &mut BTreeSet<PathBuf>) {
    println!("cargo:rerun-if-changed={}", path.display());
    if path.is_dir() {
        for entry in fs::read_dir(path).expect("engine source directory") {
            files(&entry.expect("engine source entry").path(), inputs);
        }
    } else {
        inputs.insert(path.into());
    }
}

fn main() {
    let manifest = PathBuf::from(env::var_os("CARGO_MANIFEST_DIR").unwrap());
    let root = manifest.ancestors().nth(3).unwrap();
    let engine = root.join("vendor/manifold-rust");
    let mut inputs = BTreeSet::new();
    files(&engine.join("src"), &mut inputs);
    files(&engine.join("Cargo.toml"), &mut inputs);
    let mut hash = Sha256::new();
    let mut compiled = String::new();
    for path in inputs {
        hash.update(
            path.strip_prefix(root)
                .unwrap()
                .to_string_lossy()
                .as_bytes(),
        );
        hash.update([0]);
        hash.update(fs::read(&path).expect("engine source"));
        hash.update([0]);
        compiled.push_str(&format!("const _: &[u8] = include_bytes!({:?});\n", path));
    }
    fs::write(
        PathBuf::from(env::var_os("OUT_DIR").unwrap()).join("engine_inputs.rs"),
        compiled,
    )
    .expect("compiled engine inputs");
    println!(
        "cargo:rustc-env=HSM_MANIFOLD_IMPLEMENTATION={:x}",
        hash.finalize()
    );
}
