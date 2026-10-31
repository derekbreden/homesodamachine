//! End-to-end controls use an analytic cube fixture and a private daemon/store.
use fs2::FileExt;
use serde_json::{Value, json};
use std::{
    fs::{self, OpenOptions},
    io::{BufRead, BufReader, Write},
    os::unix::net::UnixListener,
    path::PathBuf,
    process::{Command, Stdio},
    sync::atomic::{AtomicUsize, Ordering},
    time::{Duration, SystemTime, UNIX_EPOCH},
};

#[test]
fn replacement_waits_for_scene_destruction_after_socket_removal() {
    let f = Fixture::new();
    let lock = OpenOptions::new()
        .create(true)
        .truncate(false)
        .read(true)
        .write(true)
        .open(f.socket.with_extension("daemon.lock"))
        .unwrap();
    lock.lock_exclusive().unwrap();
    let listener = UnixListener::bind(&f.socket).unwrap();
    let socket = f.socket.clone();
    let retiring = std::thread::spawn(move || {
        for stream in listener.incoming() {
            let mut stream = stream.unwrap();
            let mut line = String::new();
            BufReader::new(&mut stream).read_line(&mut line).unwrap();
            let request: Value = serde_json::from_str(&line).unwrap();
            let response = json!({"ok":true,"result":{"build_id":"old-build"}});
            writeln!(stream, "{response}").unwrap();
            if request["op"] == "shutdown" {
                break;
            }
        }
        fs::remove_file(socket).unwrap();
        // Model a large scene still dropping after its endpoint has closed.
        std::thread::sleep(Duration::from_millis(150));
        drop(lock);
    });
    f.query(&["status"]);
    retiring.join().unwrap();
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
