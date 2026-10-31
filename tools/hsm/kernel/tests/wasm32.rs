//! The kernel without Manifold builds for wasm32, in a target directory of its own beside the
//! one running this test.
use std::path::Path;
use std::process::Command;

#[test]
fn builds_for_wasm32() {
    let exe = std::env::current_exe().unwrap();
    let target = exe.parent().and_then(Path::parent).and_then(Path::parent).unwrap();
    let status = Command::new(env!("CARGO"))
        .args(["build", "--quiet", "-p", "hsm-kernel", "--no-default-features", "--target", "wasm32-unknown-unknown"])
        .current_dir(env!("CARGO_MANIFEST_DIR"))
        .env("CARGO_TARGET_DIR", target.join("wasm32"))
        .status()
        .unwrap();
    assert!(status.success(), "cargo build --target wasm32-unknown-unknown failed");
}
