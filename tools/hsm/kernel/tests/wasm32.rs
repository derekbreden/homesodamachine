//! The kernel and its Rust boolean engine build for wasm32 beside the host test artifacts.
use std::path::Path;
use std::process::Command;

#[test]
fn builds_for_wasm32() {
    let exe = std::env::current_exe().unwrap();
    let target = exe.parent().and_then(Path::parent).and_then(Path::parent).unwrap();
    let status = Command::new(env!("CARGO"))
        .args(["build", "--quiet", "--locked", "--lib", "-p", "hsm-kernel", "--target", "wasm32-unknown-unknown"])
        .current_dir(env!("CARGO_MANIFEST_DIR"))
        .env("CARGO_TARGET_DIR", target.join("wasm32"))
        .status()
        .unwrap();
    assert!(status.success(), "cargo build --target wasm32-unknown-unknown failed");
}
