//! End-to-end controls use an analytic cube fixture and a private daemon/store.
use serde_json::{Value, json};
use std::{
    fs,
    io::{BufRead, BufReader, Write},
    os::unix::net::UnixListener,
    path::PathBuf,
    process::{Command, Stdio},
    sync::atomic::{AtomicUsize, Ordering},
    time::{Duration, SystemTime, UNIX_EPOCH},
};

#[test]
fn an_incompatible_daemon_is_left_running() {
    let f = Fixture::new();
    let listener = UnixListener::bind(&f.socket).unwrap();
    let responding = std::thread::spawn(move || {
        let (mut stream, _) = listener.accept().unwrap();
        let mut line = String::new();
        BufReader::new(&mut stream).read_line(&mut line).unwrap();
        let request: Value = serde_json::from_str(&line).unwrap();
        assert_eq!(request["op"], "ping");
        writeln!(stream, "{}", json!({"ok":true,"result":{"build_id":"legacy-test-fixture","protocol":1}})).unwrap();
        listener
    });
    let refused = f.command().arg("status").output().unwrap();
    assert!(!refused.status.success());
    assert!(String::from_utf8_lossy(&refused.stderr).contains("stop that daemon explicitly"));
    let listener = responding.join().unwrap();
    listener.set_nonblocking(true).unwrap();
    assert_eq!(listener.accept().unwrap_err().kind(), std::io::ErrorKind::WouldBlock);
    drop(listener);
    fs::remove_file(&f.socket).unwrap();
}

struct Fixture {
    root: PathBuf,
    socket: PathBuf,
    store: PathBuf,
}

fn payload(shift: f32) -> Vec<u8> {
    let points = [
        [-1., -1., -1.],
        [1., -1., -1.],
        [1., 1., -1.],
        [-1., 1., -1.],
        [-1., -1., 1.],
        [1., -1., 1.],
        [1., 1., 1.],
        [-1., 1., 1.],
    ];
    let indices: [u32; 36] = [
        0, 2, 1, 0, 3, 2, 4, 5, 6, 4, 6, 7, 0, 1, 5, 0, 5, 4, 1, 2, 6, 1, 6, 5, 2, 3, 7, 2, 7, 6,
        3, 0, 4, 3, 4, 7,
    ];
    let mut blob = vec![];
    let mut meshes = vec![];
    for (name, x) in [
        ("part-one", shift),
        ("part-two", shift + 5.0),
        ("", shift + 20.0),
    ] {
        let pos = blob.len();
        for p in points {
            for v in [p[0] + x, p[1], p[2]] {
                blob.extend_from_slice(&v.to_le_bytes());
            }
        }
        let nrm = blob.len();
        blob.extend_from_slice(&[0; 24 * 4]);
        let idx = blob.len();
        for i in indices {
            blob.extend_from_slice(&i.to_le_bytes());
        }
        let fac = blob.len();
        for i in [0u32, 11] {
            blob.extend_from_slice(&i.to_le_bytes());
        }
        meshes.push(json!({"name":name,"color":null,"pos":[pos,24],"nrm":[nrm,24],"idx":[idx,36],"fac":[fac,2]}));
    }
    let mut header =
        serde_json::to_vec(&json!({"v":3,"meshes":meshes,"src":"fixture","cut":{"bound":0.01}}))
            .unwrap();
    while (header.len() + 4) % 4 != 0 {
        header.push(b' ');
    }
    let mut bytes = (header.len() as u32).to_le_bytes().to_vec();
    bytes.extend(header);
    bytes.extend(blob);
    bytes
}

impl Fixture {
    fn new() -> Self {
        // macOS clocks tick in microseconds, so tests starting together need the counter.
        static FIXTURES: AtomicUsize = AtomicUsize::new(0);
        let nonce = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        let n = FIXTURES.fetch_add(1, Ordering::Relaxed);
        let root =
            std::env::temp_dir().join(format!("hsm-cli-{}-{n}-{nonce}", std::process::id()));
        fs::create_dir_all(&root).unwrap();
        fs::write(root.join("fixture.step.mesh"), payload(0.0)).unwrap();
        Self {
            socket: root.join("engine.sock"),
            store: root.join("store"),
            root,
        }
    }
    fn command(&self) -> Command {
        let mut c = Command::new(env!("CARGO_BIN_EXE_hsm"));
        c.arg("--root")
            .arg(&self.root)
            .arg("--scene")
            .arg("fixture.step")
            .arg("--socket")
            .arg(&self.socket)
            .arg("--store")
            .arg(&self.store);
        c
    }
    fn query(&self, args: &[&str]) -> Value {
        let output = self.command().args(args).output().unwrap();
        assert!(
            output.status.success(),
            "{}\n{}",
            String::from_utf8_lossy(&output.stdout),
            String::from_utf8_lossy(&output.stderr)
        );
        let value: Value = serde_json::from_slice(&output.stdout).unwrap();
        assert_eq!(value["ok"], true, "{value}");
        value
    }
}

impl Drop for Fixture {
    fn drop(&mut self) {
        let _ = self.command().arg("stop").output();
        let _ = fs::remove_dir_all(&self.root);
    }
}

#[test]
fn the_default_endpoint_names_the_build_without_starting_a_daemon() {
    let f = Fixture::new();
    let private = f.command().arg("endpoint").output().unwrap();
    assert!(private.status.success());
    assert!(!f.socket.exists());
    let out = Command::new(env!("CARGO_BIN_EXE_hsm"))
        .env_remove("HSM_SOCKET")
        .arg("--root").arg(&f.root).arg("endpoint").output().unwrap();
    assert!(out.status.success(), "{}", String::from_utf8_lossy(&out.stderr));
    let endpoint: Value = serde_json::from_slice(&out.stdout).unwrap();
    let build = endpoint["build_id"].as_str().unwrap();
    assert_eq!(build.len(), 64);
    let socket = endpoint["socket"].as_str().unwrap();
    assert!(socket.contains("/engine-") && socket.ends_with(".sock"));
    assert!(socket.len() < 104);
    assert_eq!(PathBuf::from(endpoint["executable"].as_str().unwrap()),
               PathBuf::from(env!("CARGO_BIN_EXE_hsm")).canonicalize().unwrap());
}

#[test]
fn an_explicit_socket_refuses_different_budgets_without_stopping_its_daemon() {
    let f = Fixture::new();
    let before = f.query(&["status"]);
    for flag in ["--cache-mb", "--build-mb", "--keep-mb"] {
        let refused = f.command().args([flag, "1", "status"]).output().unwrap();
        assert!(!refused.status.success(), "{flag}");
        assert!(String::from_utf8_lossy(&refused.stderr).contains("serves configuration"), "{flag}");
    }
    let after = f.query(&["status"]);
    assert_eq!(before["result"]["pid"], after["result"]["pid"]);
    assert_eq!(before["result"]["cache"], after["result"]["cache"]);
}

#[test]
fn an_idle_daemon_exits_and_the_next_query_starts_another() {
    let f = Fixture::new();
    let pid = f.query(&["--idle-minutes", "0.01", "status"])["result"]["pid"].clone();
    let waiting = std::time::Instant::now();
    while f.socket.exists() {
        assert!(waiting.elapsed() < Duration::from_secs(10), "an idle daemon kept its socket");
        std::thread::sleep(Duration::from_millis(50));
    }
    let next = f.query(&["where", "part-one"]);
    assert_eq!(next["result"]["data"]["parts"][0]["name"], "part-one");
    assert_ne!(f.query(&["status"])["result"]["pid"], pid);
}

#[test]
fn queries_restart_worktrees_and_invalidation() {
    let f = Fixture::new();
    let first = f.query(&["where"]);
    assert_eq!(
        first["result"]["data"]["parts"].as_array().unwrap().len(),
        3
    );
    assert_eq!(first["result"]["cut"]["bound"], 0.01);
    let pid = f.query(&["status"])["result"]["pid"].clone();
    let gap = f.query(&["gap", "part-one", "part-two"]);
    assert_eq!(gap["result"]["data"]["gap"]["clearance_mm"], 3.0);
    assert_eq!(f.query(&["status"])["result"]["pid"], pid);
    let moved = f.query(&[
        "move",
        "part-one",
        "--by",
        "4",
        "0",
        "0",
        "--against",
        "part-two",
    ]);
    assert!(
        (moved["result"]["data"]["overlaps"][0]["volume_mm3"]
            .as_f64()
            .unwrap()
            - 4.0)
            .abs()
            < 1e-9
    );
    assert_eq!(
        f.query(&["gap", "part-one", "part-two"])["result"]["data"]["gap"]["clearance_mm"],
        3.0
    );
    let hit = f.query(&[
        "ray",
        "--origin",
        "0",
        "0",
        "5",
        "--direction",
        "0",
        "0",
        "-1",
    ]);
    assert_eq!(hit["result"]["data"]["closest"]["hit"]["distance_mm"], 4.0);
    let surface = f.query(&[
        "ray",
        "--origin",
        "0",
        "0",
        "1",
        "--direction",
        "0",
        "0",
        "-1",
    ]);
    assert_eq!(
        surface["result"]["data"]["closest"]["hit"]["distance_mm"],
        0.0
    );
    assert!(
        f.query(&[
            "section", "part-one", "--normal", "0", "0", "1", "--offset", "0"
        ])["result"]["data"]["section"]["segments"]
            .as_array()
            .unwrap()
            .len()
            > 0
    );
    let ambiguous = f
        .command()
        .args(["gap", "part", "part-two"])
        .output()
        .unwrap();
    assert!(!ambiguous.status.success());
    assert!(String::from_utf8_lossy(&ambiguous.stdout).contains("matches 2 solids"));

    let other = f.root.join("other-worktree");
    fs::create_dir(&other).unwrap();
    fs::write(other.join("same.step.mesh"), payload(0.0)).unwrap();
    f.query(&[
        "request",
        &json!({"scene":other.join("same.step.mesh"),"op":"where","pattern":"part-one"})
            .to_string(),
    ]);
    assert_eq!(f.query(&["status"])["result"]["cache"]["payload_loads"], 1);

    fs::write(f.root.join("fixture.step.mesh"), payload(10.0)).unwrap();
    let updated = f.query(&["where", "part-one"]);
    assert_ne!(
        updated["result"]["payload_sha256"],
        first["result"]["payload_sha256"]
    );
    assert_eq!(updated["result"]["data"]["parts"][0]["min_mm"][0], 9.0);
    f.query(&["stop"]);
    f.query(&["where"]);
    assert_eq!(f.query(&["status"])["result"]["cache"]["payload_loads"], 1);
    assert_ne!(f.query(&["status"])["result"]["pid"], pid);

    fs::write(f.root.join("fixture.step.mesh"), b"bad").unwrap();
    let bad = f.command().arg("where").output().unwrap();
    assert!(!bad.status.success());
    assert!(String::from_utf8_lossy(&bad.stdout).contains("truncated payload"));
    f.query(&["status"]);
}

#[test]
fn mcp_is_json_rpc_and_uses_the_shared_daemon() {
    let f = Fixture::new();
    let mut child = f
        .command()
        .arg("mcp")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .unwrap();
    let messages = [
        json!({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05"}}),
        json!({"jsonrpc":"2.0","method":"notifications/initialized"}),
        json!({"jsonrpc":"2.0","id":2,"method":"tools/list"}),
        json!({"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"hsm_gap","arguments":{"a":"part-one","b":"part-two"}}}),
        json!({"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"hsm_where","arguments":{"invalid":true}}}),
    ];
    let mut input = child.stdin.take().unwrap();
    for message in messages {
        writeln!(input, "{message}").unwrap();
    }
    drop(input);
    let out = child.wait_with_output().unwrap();
    assert!(
        out.status.success(),
        "{}",
        String::from_utf8_lossy(&out.stderr)
    );
    let lines: Vec<Value> = String::from_utf8(out.stdout)
        .unwrap()
        .lines()
        .map(|l| serde_json::from_str(l).unwrap())
        .collect();
    assert_eq!(lines.len(), 4);
    assert_eq!(lines[1]["result"]["tools"].as_array().unwrap().len(), 6);
    assert_eq!(lines[2]["result"]["isError"], false);
    assert_eq!(
        lines[2]["result"]["structuredContent"]["result"]["data"]["gap"]["clearance_mm"],
        3.0
    );
    assert_eq!(lines[3]["result"]["isError"], true);
    assert_eq!(f.query(&["status"])["result"]["cache"]["payload_loads"], 1);
}

fn rpc(command: &mut Command, messages: &[Value]) -> Vec<Value> {
    let mut child = command
        .arg("mcp")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .unwrap();
    let mut input = child.stdin.take().unwrap();
    for message in messages {
        writeln!(input, "{message}").unwrap();
    }
    drop(input);
    let out = child.wait_with_output().unwrap();
    assert!(out.status.success(), "{}", String::from_utf8_lossy(&out.stderr));
    String::from_utf8(out.stdout)
        .unwrap()
        .lines()
        .map(|l| serde_json::from_str(l).unwrap())
        .collect()
}

#[test]
fn mcp_names_its_checkout_and_follows_a_codex_turns_workspace() {
    let f = Fixture::new();
    let other = f.root.join("other");
    fs::create_dir(&other).unwrap();
    fs::write(other.join("fixture.step.mesh"), payload(10.0)).unwrap();
    let turn = |workspaces: Value| {
        json!({"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"hsm_where",
            "arguments":{"pattern":"part-one"},
            "_meta":{"x-codex-turn-metadata":{"workspaces":workspaces}}}})
    };
    let lines = rpc(
        &mut f.command(),
        &[
            json!({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18"}}),
            turn(json!({other.to_str().unwrap(): {"has_changes": false}})),
            turn(json!({f.root.to_str().unwrap(): {}, other.to_str().unwrap(): {}})),
        ],
    );
    let root = f.root.canonicalize().unwrap();
    assert!(
        lines[0]["result"]["instructions"]
            .as_str()
            .unwrap()
            .contains(root.to_str().unwrap())
    );
    let measured = |line: &Value| {
        line["result"]["structuredContent"]["result"]["data"]["parts"][0]["min_mm"][0].clone()
    };
    assert_eq!(measured(&lines[1]), 9.0);
    assert_eq!(measured(&lines[2]), -1.0);
}

fn sha256(bytes: &[u8]) -> String {
    use sha2::{Digest, Sha256};
    format!("{:x}", Sha256::digest(bytes))
}

fn gzip(bytes: &[u8]) -> Vec<u8> {
    let mut child = Command::new("gzip")
        .arg("-c")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .spawn()
        .unwrap();
    child.stdin.take().unwrap().write_all(bytes).unwrap();
    let out = child.wait_with_output().unwrap();
    assert!(out.status.success());
    out.stdout
}

#[test]
fn a_worktree_without_its_payload_takes_the_published_one() {
    let f = Fixture::new();
    let bytes = payload(0.0);
    let hash = sha256(&bytes);
    // A main checkout holding the payload, and a linked worktree of it holding none.
    let main = f.root.join("main");
    let worktree = f.root.join("worktree");
    let gitdir = main.join(".git/worktrees/wt");
    fs::create_dir_all(&gitdir).unwrap();
    fs::write(gitdir.join("commondir"), "../..\n").unwrap();
    fs::create_dir_all(main.join("hardware")).unwrap();
    fs::write(main.join("hardware/part.step.mesh"), &bytes).unwrap();
    fs::create_dir_all(worktree.join("hardware")).unwrap();
    fs::write(worktree.join(".git"), format!("gitdir: {}\n", gitdir.display())).unwrap();
    let objects = f.root.join("objects");
    fs::create_dir(&objects).unwrap();
    fs::write(objects.join(format!("s-{hash}.gz")), gzip(&bytes)).unwrap();
    let pointers = |hash: &str| {
        json!({"store":{"url":format!("file://{}/", objects.display()),"objects":"s-"},
            "solids":{"hardware/part.step.mesh":hash}})
        .to_string()
    };
    fs::write(worktree.join("hardware/cad-artifacts.json"), pointers(&hash)).unwrap();
    let mesh = worktree.join("hardware/part.step.mesh");
    let query = || {
        Command::new(env!("CARGO_BIN_EXE_hsm"))
            .arg("--root")
            .arg(&worktree)
            .args(["--scene", "hardware/part.step", "--socket"])
            .arg(&f.socket)
            .arg("--store")
            .arg(&f.store)
            .args(["where", "part-one"])
            .output()
            .unwrap()
    };
    let taken = |out: &std::process::Output, from: &str| {
        assert!(out.status.success(), "{}", String::from_utf8_lossy(&out.stderr));
        assert!(String::from_utf8_lossy(&out.stderr).contains(from));
        assert_eq!(fs::read(&mesh).unwrap(), bytes);
    };

    taken(&query(), main.to_str().unwrap());
    fs::remove_file(&mesh).unwrap();
    fs::remove_file(main.join("hardware/part.step.mesh")).unwrap();
    taken(&query(), "file://");

    // Bytes the pointer file does not name stay out of the tree.
    fs::remove_file(&mesh).unwrap();
    fs::write(main.join("hardware/part.step.mesh"), payload(1.0)).unwrap();
    fs::write(worktree.join("hardware/cad-artifacts.json"), pointers(&sha256(b"other"))).unwrap();
    let refused = query();
    assert!(!refused.status.success());
    assert!(String::from_utf8_lossy(&refused.stderr).contains("nothing supplied those bytes"));
    assert!(!mesh.exists());
    assert!(fs::read_dir(worktree.join("hardware")).unwrap().count() == 1);
}
