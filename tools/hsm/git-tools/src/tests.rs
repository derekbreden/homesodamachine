use super::*;
use tempfile::TempDir;

struct Fixture {
    _dir: TempDir,
    a: Repo,
    b: Repo,
}
impl Fixture {
    fn new() -> Result<Self> {
        let dir = TempDir::new()?;
        let bare = dir.path().join("remote.git");
        let a = Repo {
            root: dir.path().join("a"),
        };
        let b = Repo {
            root: dir.path().join("b"),
        };
        fs::create_dir_all(&a.root)?;
        let initial = Repo {
            root: dir.path().to_path_buf(),
        };
        initial.git(&["init", "--bare", bare.to_str().unwrap()])?;
        a.git(&["init", "-b", "main"])?;
        for repo in [&a] {
            repo.git(&["config", "user.email", "fixture@example.invalid"])?;
            repo.git(&["config", "user.name", "Fixture"])?;
        }
        fs::write(a.root.join("shared"), "top\n\n\n\n\n\n\n\n\nbottom\n")?;
        fs::write(a.root.join("staged"), "base\n")?;
        a.git(&["add", "shared", "staged"])?;
        a.git(&["commit", "-m", "base"])?;
        a.git(&["remote", "add", "origin", bare.to_str().unwrap()])?;
        a.git(&["push", "-u", "origin", "main"])?;
        initial.git(&[
            "clone",
            "-b",
            "main",
            bare.to_str().unwrap(),
            b.root.to_str().unwrap(),
        ])?;
        b.git(&["config", "user.email", "other@example.invalid"])?;
        b.git(&["config", "user.name", "Other"])?;
        Ok(Self { _dir: dir, a, b })
    }
    fn commit(repo: &Repo, path: &str, text: &str, msg: &str) -> Result<()> {
        fs::write(repo.root.join(path), text)?;
        repo.git(&["add", "--", path])?;
        repo.git(&["commit", "-m", msg, "--", path])?;
        Ok(())
    }
}

#[test]
fn fast_forward_and_no_change() -> Result<()> {
    let f = Fixture::new()?;
    Fixture::commit(&f.a, "first", "one\n", "first")?;
    assert_eq!(f.a.land(false)?, 0);
    assert_eq!(
        f.a.git(&["rev-parse", "HEAD"])?,
        f.a.git(&["rev-parse", UPSTREAM])?
    );
    assert_eq!(f.a.land(false)?, 0);
    Ok(())
}

#[test]
fn replay_retains_working_and_staged_edits() -> Result<()> {
    let f = Fixture::new()?;
    Fixture::commit(&f.a, "local", "local\n", "local source")?;
    Fixture::commit(&f.b, "remote", "remote\n", "remote source")?;
    f.b.git(&["push", "origin", "main"])?;
    fs::write(f.a.root.join("staged"), "staged edit\n")?;
    f.a.git(&["add", "staged"])?;
    fs::write(f.a.root.join("shared"), "in flight\n")?;
    assert_eq!(f.a.land(false)?, 0);
    assert_eq!(fs::read_to_string(f.a.root.join("shared"))?, "in flight\n");
    assert_eq!(f.a.git(&["show", ":staged"])?, "staged edit");
    assert_eq!(fs::read_to_string(f.a.root.join("remote"))?, "remote\n");
    assert_eq!(fs::read_to_string(f.a.root.join("local"))?, "local\n");
    assert_eq!(
        f.a.git(&["rev-parse", "HEAD"])?,
        f.a.git(&["rev-parse", UPSTREAM])?
    );
    assert!(
        f.a.git(&["log", "-1", "--format=%an <%ae>"])?
            .contains("Fixture <fixture@example.invalid>")
    );
    assert!(!f.a.root.join(".git/hsm-land-merge").exists());
    Ok(())
}

#[test]
fn twin_patch_is_not_replayed() -> Result<()> {
    let f = Fixture::new()?;
    Fixture::commit(&f.a, "same", "same change\n", "one author")?;
    Fixture::commit(&f.b, "same", "same change\n", "another author")?;
    f.b.git(&["push", "origin", "main"])?;
    assert_ne!(
        f.a.git(&["rev-parse", "HEAD"])?,
        f.b.git(&["rev-parse", "HEAD"])?
    );
    assert_eq!(f.a.land(false)?, 0);
    assert_eq!(
        f.a.git(&["rev-parse", "HEAD"])?,
        f.b.git(&["rev-parse", "HEAD"])?
    );
    Ok(())
}

#[test]
fn behind_merges_separate_text_edits() -> Result<()> {
    let f = Fixture::new()?;
    Fixture::commit(
        &f.b,
        "shared",
        "remote top\n\n\n\n\n\n\n\n\nbottom\n",
        "incoming",
    )?;
    f.b.git(&["push", "origin", "main"])?;
    fs::write(
        f.a.root.join("shared"),
        "top\n\n\n\n\n\n\n\n\nlocal bottom\n",
    )?;
    assert_eq!(f.a.land(false)?, 0);
    let merged = fs::read_to_string(f.a.root.join("shared"))?;
    assert!(merged.starts_with("remote top"));
    assert!(merged.ends_with("local bottom\n"));
    Ok(())
}

#[test]
fn replay_preserves_an_in_flight_revert_of_a_committed_edit() -> Result<()> {
    let f = Fixture::new()?;
    Fixture::commit(
        &f.a,
        "shared",
        "local top\n\n\n\n\n\n\n\n\nbottom\n",
        "local first line",
    )?;
    Fixture::commit(
        &f.b,
        "shared",
        "top\n\n\n\n\n\n\n\n\nremote bottom\n",
        "remote last line",
    )?;
    f.b.git(&["push", "origin", "main"])?;
    fs::write(f.a.root.join("shared"), "top\n\n\n\n\n\n\n\n\nbottom\n")?;
    assert_eq!(f.a.land(false)?, 0);
    let head = f.a.git(&["show", "HEAD:shared"])?;
    assert!(head.starts_with("local top"));
    assert!(head.ends_with("remote bottom"));
    let work = fs::read_to_string(f.a.root.join("shared"))?;
    assert!(work.starts_with("top\n"));
    assert!(work.ends_with("remote bottom\n"));
    Ok(())
}

#[test]
fn frozen_commit_keeps_newer_worktree_and_unrelated_staging() -> Result<()> {
    let f = Fixture::new()?;
    let blob =
        f.a.output(&["hash-object", "-w", "--stdin"], Some(b"frozen upload\n"))?;
    assert!(blob.status.success());
    fs::write(f.a.root.join("shared"), "newer live output\n")?;
    fs::write(f.a.root.join("staged"), "other session staged\n")?;
    f.a.git(&["add", "staged"])?;
    let snapshot = json!({"message":"publish frozen output","files":[{"path":"shared","blob":string(&blob.stdout)}]});
    let result = f.a.commit_snapshot(&snapshot)?;
    assert_eq!(result["changed"], true);
    assert_eq!(f.a.git(&["show", "HEAD:shared"])?, "frozen upload");
    assert_eq!(f.a.git(&["show", ":shared"])?, "frozen upload");
    assert_eq!(
        fs::read_to_string(f.a.root.join("shared"))?,
        "newer live output\n"
    );
    assert_eq!(f.a.git(&["show", ":staged"])?, "other session staged");
    assert_eq!(f.a.git(&["show", "HEAD:staged"])?, "base");
    assert_eq!(f.a.land(false)?, 0);
    assert!(!f.a.root.join(".git/index.lock").exists());
    let again = f.a.commit_snapshot(&snapshot)?;
    assert_eq!(again["changed"], false);
    assert_eq!(again["commit"], result["commit"]);
    Ok(())
}

#[test]
fn frozen_commit_refuses_busy_index_without_removing_foreign_lock() -> Result<()> {
    let f = Fixture::new()?;
    let head = f.a.git(&["rev-parse", "HEAD"])?;
    let blob =
        f.a.output(&["hash-object", "-w", "--stdin"], Some(b"frozen\n"))?;
    fs::write(f.a.root.join(".git/index.lock"), b"another Git operation")?;
    assert!(
        f.a.commit_snapshot(
            &json!({"message":"publish","files":[{"path":"shared","blob":string(&blob.stdout)}]})
        )
        .is_err()
    );
    assert_eq!(f.a.git(&["rev-parse", "HEAD"])?, head);
    assert_eq!(
        fs::read(f.a.root.join(".git/index.lock"))?,
        b"another Git operation"
    );
    Ok(())
}

#[test]
fn frozen_commit_preserves_selected_intentional_staging() -> Result<()> {
    let f = Fixture::new()?;
    fs::write(f.a.root.join("shared"), "intentionally staged\n")?;
    f.a.git(&["add", "shared"])?;
    fs::write(f.a.root.join("shared"), "latest live\n")?;
    let blob =
        f.a.output(&["hash-object", "-w", "--stdin"], Some(b"uploaded bytes\n"))?;
    f.a.commit_snapshot(
        &json!({"message":"publish","files":[{"path":"shared","blob":string(&blob.stdout)}]}),
    )?;
    assert_eq!(f.a.git(&["show", ":shared"])?, "intentionally staged");
    assert_eq!(f.a.git(&["show", "HEAD:shared"])?, "uploaded bytes");
    assert_eq!(
        fs::read_to_string(f.a.root.join("shared"))?,
        "latest live\n"
    );
    Ok(())
}

#[test]
fn conflict_keeps_commit_recoverable_and_writes_named_markers() -> Result<()> {
    let f = Fixture::new()?;
    Fixture::commit(&f.a, "shared", "local\n", "local conflict")?;
    let original = f.a.git(&["rev-parse", "HEAD"])?;
    Fixture::commit(&f.b, "shared", "remote\n", "remote conflict")?;
    f.b.git(&["push", "origin", "main"])?;
    assert_eq!(f.a.land(false)?, 1);
    assert_eq!(f.a.git(&["rev-parse", "ORIG_HEAD"])?, original);
    assert_eq!(
        f.a.git(&["rev-parse", "HEAD"])?,
        f.b.git(&["rev-parse", "HEAD"])?
    );
    let work = fs::read_to_string(f.a.root.join("shared"))?;
    assert!(work.contains("<<<<<<< this tree"));
    assert!(work.contains("remote conflict"));
    assert!(work.contains("local\n"));
    assert!(work.contains("remote\n"));
    Ok(())
}

#[test]
fn check_does_not_change_head_index_or_working_files() -> Result<()> {
    let f = Fixture::new()?;
    Fixture::commit(&f.a, "local", "local\n", "local source")?;
    Fixture::commit(&f.b, "remote", "remote\n", "remote source")?;
    f.b.git(&["push", "origin", "main"])?;
    let head = f.a.git(&["rev-parse", "HEAD"])?;
    let index = f.a.git(&["ls-files", "--stage"])?;
    assert_eq!(f.a.land(true)?, 0);
    assert_eq!(f.a.git(&["rev-parse", "HEAD"])?, head);
    assert_eq!(f.a.git(&["ls-files", "--stage"])?, index);
    assert!(!f.a.root.join("remote").exists());
    Ok(())
}
