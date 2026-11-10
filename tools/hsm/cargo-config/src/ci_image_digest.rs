//! hsm-ci-image-digest identifies the repository inputs that define the shared CI image.

use sha2::{Digest, Sha256};
use std::env;
use std::ffi::OsString;
use std::fs;
use std::path::{Path, PathBuf};

const FILES: &[&str] = &[
    ".bazelversion",
    ".dockerignore",
    "tools/ci-image/Dockerfile",
    "tools/hsm/cargo-config/Cargo.toml",
    "tools/hsm/cargo-config/src/ci_image_digest.rs",
    "tools/render/package.json",
    "tools/render/package-lock.json",
    "web/package.json",
    "web/package-lock.json",
];
const TAG_HEX_LENGTH: usize = 16;
const USAGE: &str = "Usage: hsm-ci-image-digest [--root ROOT] [--inputs]\n\nPrint the content tag for the shared CI image. --inputs lists its repository inputs.";

type Result<T> = std::result::Result<T, String>;

fn default_root() -> PathBuf {
    env::var_os("HSM_WORKSPACE")
        .filter(|value| !value.is_empty())
        .map(PathBuf::from)
        .unwrap_or_else(|| {
            Path::new(env!("CARGO_MANIFEST_DIR"))
                .ancestors()
                .nth(3)
                .expect("cargo-config is under tools/hsm")
                .to_path_buf()
        })
}

fn inputs<'a>(root: &Path, names: &[&'a str]) -> Result<Vec<&'a str>> {
    let mut names = names.to_vec();
    names.sort_unstable();
    names.dedup();
    for name in &names {
        if !root.join(name).is_file() {
            return Err(format!("CI image input is absent: {name}"));
        }
    }
    Ok(names)
}

fn frame(hash: &mut Sha256, name: &str, data: &[u8]) -> Result<()> {
    let path_length = u32::try_from(name.len())
        .map_err(|_| format!("CI image input path is too long: {name}"))?;
    let content_length = u64::try_from(data.len())
        .map_err(|_| format!("CI image input is too large: {name}"))?;
    hash.update(path_length.to_be_bytes());
    hash.update(name.as_bytes());
    hash.update(content_length.to_be_bytes());
    hash.update(data);
    Ok(())
}

fn digest(root: &Path, names: &[&str]) -> Result<String> {
    let mut hash = Sha256::new();
    for name in inputs(root, names)? {
        let data = fs::read(root.join(name))
            .map_err(|error| format!("Cannot read CI image input {name}: {error}"))?;
        frame(&mut hash, name, &data)?;
    }
    Ok(format!("{:x}", hash.finalize())[..TAG_HEX_LENGTH].to_owned())
}

fn run(args: impl IntoIterator<Item = OsString>) -> Result<()> {
    let mut args = args.into_iter();
    let mut root = None;
    let mut list_inputs = false;
    while let Some(arg) = args.next() {
        if arg == "--root" {
            if root.is_some() {
                return Err("--root is supplied more than once".to_owned());
            }
            root = Some(PathBuf::from(
                args.next()
                    .filter(|value| !value.is_empty())
                    .ok_or_else(|| "--root requires a path".to_owned())?,
            ));
        } else if arg == "--inputs" {
            list_inputs = true;
        } else if arg == "--help" || arg == "-h" {
            println!("{USAGE}");
            return Ok(());
        } else {
            return Err(format!("Unknown argument: {}\n{USAGE}", arg.to_string_lossy()));
        }
    }
    let root = root.unwrap_or_else(default_root);
    if list_inputs {
        for name in inputs(&root, FILES)? {
            println!("{name}");
        }
    } else {
        println!("{}", digest(&root, FILES)?);
    }
    Ok(())
}

fn main() {
    if let Err(error) = run(env::args_os().skip(1)) {
        eprintln!("hsm-ci-image-digest: {error}");
        std::process::exit(1);
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::atomic::{AtomicU64, Ordering};

    static NEXT_FIXTURE: AtomicU64 = AtomicU64::new(0);

    struct Fixture(PathBuf);

    impl Fixture {
        fn new() -> Self {
            let root = Path::new(env!("CARGO_MANIFEST_DIR"))
                .ancestors()
                .nth(3)
                .unwrap()
                .join(".cache/runs")
                .join(format!(
                    "python-retirement-ci-digest-test-{}-{}",
                    std::process::id(),
                    NEXT_FIXTURE.fetch_add(1, Ordering::Relaxed)
                ));
            fs::create_dir_all(&root).unwrap();
            Self(root)
        }

        fn write(&self, name: &str, content: &[u8]) {
            let path = self.0.join(name);
            fs::create_dir_all(path.parent().unwrap()).unwrap();
            fs::write(path, content).unwrap();
        }
    }

    impl Drop for Fixture {
        fn drop(&mut self) {
            let _ = fs::remove_dir_all(&self.0);
        }
    }

    #[test]
    fn frame_matches_explicit_big_endian_wire_bytes() {
        let mut actual = Sha256::new();
        frame(&mut actual, "a", b"bc").unwrap();
        let expected = Sha256::digest(b"\x00\x00\x00\x01a\x00\x00\x00\x00\x00\x00\x00\x02bc");
        assert_eq!(actual.finalize(), expected);
    }

    #[test]
    fn framing_keeps_path_content_and_file_boundaries_distinct() {
        let mut left = Sha256::new();
        frame(&mut left, "a", b"bc").unwrap();
        let mut right = Sha256::new();
        frame(&mut right, "ab", b"c").unwrap();
        assert_ne!(left.finalize(), right.finalize());

        let mut left = Sha256::new();
        frame(&mut left, "a", b"b").unwrap();
        frame(&mut left, "c", b"d").unwrap();
        let mut right = Sha256::new();
        frame(&mut right, "a", b"bcd").unwrap();
        assert_ne!(left.finalize(), right.finalize());
    }

    #[test]
    fn input_order_and_duplicates_do_not_change_tag() {
        let fixture = Fixture::new();
        fixture.write("nested/z", b"last");
        fixture.write("a", b"first");
        assert_eq!(
            digest(&fixture.0, &["nested/z", "a", "a"]).unwrap(),
            digest(&fixture.0, &["a", "nested/z"]).unwrap()
        );
        assert_eq!(
            inputs(&fixture.0, &["nested/z", "a", "a"]).unwrap(),
            ["a", "nested/z"]
        );
    }

    #[test]
    fn missing_input_names_the_repository_path() {
        let fixture = Fixture::new();
        fixture.write("a", b"present");
        assert_eq!(
            digest(&fixture.0, &["a", "missing/input"]).unwrap_err(),
            "CI image input is absent: missing/input"
        );
    }

    #[test]
    fn empty_input_set_retains_the_original_digest_prefix() {
        assert_eq!(digest(Path::new("."), &[]).unwrap(), "e3b0c44298fc1c14");
    }
}
