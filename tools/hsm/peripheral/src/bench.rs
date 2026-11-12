//! The bench tools hold a connected machine to this laptop's bench state, and hold its console
//! open for a timed list of commands.
//!
//! A machine on a bench has no water to find, so the notices its firmware rightly puts on both
//! displays are in the way of whoever is working at them. The firmware stays the production
//! firmware. Which notices to keep off is this laptop's to say, in one file, and the watcher says
//! it to every main board on USB for as long as the board is there: `notice hold <name>…` on
//! the board's console is a lease the board lets lapse by itself once nobody renews it.
use crate::{option, serials, validate_args};
use anyhow::{Context, Result, bail, ensure};
use serialport::{ClearBuffer, SerialPort};
use std::{
    collections::BTreeMap,
    env, fs,
    io::ErrorKind,
    path::{Path, PathBuf},
    process::Command,
    thread,
    time::{Duration, Instant},
};

/// How often a hold is said again. The board's lease is many times longer, so a tool that has the
/// port for minutes costs nothing; this short, a board that restarts without leaving USB has its
/// notices back off within a few seconds.
const RENEW: Duration = Duration::from_secs(5);
/// A board that has just enumerated is still booting.
const SETTLE: Duration = Duration::from_secs(2);
const TICK: Duration = Duration::from_secs(1);
const LABEL: &str = "com.homesodamachine.bench";

fn home() -> Result<PathBuf> {
    Ok(PathBuf::from(env::var_os("HOME").context("HOME is not set")?))
}

fn state_path() -> Result<PathBuf> {
    if let Some(path) = env::var_os("HSM_BENCH_STATE") {
        return Ok(path.into());
    }
    Ok(home()?.join(".config/hsm-bench/hold"))
}

/// The notices this laptop keeps off a connected machine's displays. No file is none.
fn held() -> Result<Vec<String>> {
    let path = state_path()?;
    let text = match fs::read_to_string(&path) {
        Ok(text) => text,
        Err(error) if error.kind() == ErrorKind::NotFound => return Ok(Vec::new()),
        Err(error) => return Err(error).with_context(|| format!("read {}", path.display())),
    };
    Ok(text
        .lines()
        .filter(|line| !line.trim_start().starts_with('#'))
        .flat_map(str::split_whitespace)
        .map(str::to_owned)
        .collect())
}

fn hold(names: &[String]) -> Result<()> {
    let path = state_path()?;
    for name in names {
        ensure!(
            name.chars().all(|c| c.is_ascii_lowercase() || c.is_ascii_digit() || c == '-'),
            "a notice is named in lower-case letters, digits and hyphens: {name:?}"
        );
    }
    let mut text = String::from(
        "# The notices this laptop keeps off the displays of a machine on its USB.\n\
         # `hsm-peripheral bench` writes this file and tools/bench.md says what reads it.\n",
    );
    text.push_str(&names.join(" "));
    text.push('\n');
    crate::write(&path, text.as_bytes())
}

fn line_for(names: &[String]) -> String {
    if names.is_empty() {
        "notice release".to_owned()
    } else {
        format!("notice hold {}", names.join(" "))
    }
}

enum Told {
    Said(String),
    /// Another program has the port.
    Busy,
    /// The board is not answering this command: unpowered, restarting, or a build without it.
    Silent,
}

/// One line to a main board and the line it answers with, without restarting it.
fn tell(path: &str, line: &str) -> Result<Told> {
    let mut port = match serials::open_quiet(path, Duration::from_millis(20)) {
        Ok(port) => port,
        Err(error) if serials::busy(&error) => return Ok(Told::Busy),
        Err(error) => return Err(error.into()),
    };
    port.clear(ClearBuffer::Input)?;
    serials::send(&mut *port, format!("\n{line}\n").as_bytes())?;
    let deadline = Instant::now() + Duration::from_millis(700);
    let mut seen = Vec::new();
    while Instant::now() < deadline {
        seen.extend(serials::poll(&mut *port)?);
        let text = String::from_utf8_lossy(&seen);
        // A line is whole once the one after it has begun.
        let whole = text.rsplit_once('\n').map_or("", |(whole, _)| whole);
        if let Some(answer) = whole.lines().map(str::trim).find(|l| l.starts_with("[notice]")) {
            return Ok(Told::Said(answer.to_owned()));
        }
    }
    Ok(Told::Silent)
}

fn stamp() -> String {
    // SAFETY: time() and localtime_r() write only the two values handed to them, and strftime()
    // writes at most the buffer's length and returns how much.
    unsafe {
        let now = libc::time(std::ptr::null_mut());
        let mut local: libc::tm = std::mem::zeroed();
        libc::localtime_r(&now, &mut local);
        let mut buffer = [0u8; 32];
        let length = libc::strftime(
            buffer.as_mut_ptr().cast(),
            buffer.len(),
            c"%Y-%m-%d %H:%M:%S".as_ptr(),
            &local,
        );
        String::from_utf8_lossy(&buffer[..length]).into_owned()
    }
}

fn say(text: &str) {
    println!("{}  {text}", stamp());
}

struct Board {
    due: Instant,
    /// The line last answered, and the answer: a change in either is worth a line in the log.
    line: String,
    answer: String,
    quiet: bool,
}

/// `bench-watch`: say this laptop's bench state to every main board on USB, for as long as each
/// is there. It opens a port only for the fraction of a second an exchange takes, and leaves one
/// another program has alone.
pub fn watch(args: &[String]) -> Result<()> {
    ensure!(validate_args(args, &[], &[])?.is_empty(), "bench-watch");
    say(&format!("watching; the bench state is {}", state_path()?.display()));
    let mut boards = BTreeMap::<String, Board>::new();
    let mut state_error = String::new();
    loop {
        let names = match held() {
            Ok(names) => {
                state_error.clear();
                names
            }
            Err(error) => {
                let text = format!("{error:#}");
                if text != state_error {
                    say(&format!("the bench state cannot be read, so nothing is held: {text}"));
                    state_error = text;
                }
                Vec::new()
            }
        };
        let line = line_for(&names);
        let present = serials::ports_with_id(serials::CH340).unwrap_or_default();
        boards.retain(|path, _| {
            let here = present.iter().any(|port| &port.port_name == path);
            if !here {
                say(&format!("{path} left"));
            }
            here
        });
        let now = Instant::now();
        for port in &present {
            let path = &port.port_name;
            let board = boards.entry(path.clone()).or_insert_with(|| {
                say(&format!("{path} is here"));
                Board {
                    due: now + SETTLE,
                    line: String::new(),
                    answer: String::new(),
                    quiet: false,
                }
            });
            // A board told to hold nothing has nothing to be told again.
            if now < board.due || (names.is_empty() && board.line == line) {
                continue;
            }
            match tell(path, &line) {
                Ok(Told::Said(answer)) => {
                    if board.line != line || board.answer != answer {
                        say(&format!("{path}  {line}  ->  {answer}"));
                    }
                    board.line = line.clone();
                    board.answer = answer;
                    board.quiet = false;
                    board.due = now + RENEW;
                }
                Ok(Told::Busy) => board.due = now + TICK,
                Ok(Told::Silent) => {
                    if !board.quiet {
                        say(&format!("{path} does not answer `{line}`"));
                    }
                    board.quiet = true;
                    board.answer.clear();
                    board.due = now + RENEW;
                }
                Err(error) => {
                    if !board.quiet {
                        say(&format!("{path}: {error:#}"));
                    }
                    board.quiet = true;
                    board.due = now + RENEW;
                }
            }
        }
        thread::sleep(TICK);
    }
}

fn each_board(line: &str) -> Result<()> {
    let ports = serials::ports_with_id(serials::CH340)?;
    if ports.is_empty() {
        println!("no main board is on USB");
    }
    for port in ports {
        let started = Instant::now();
        loop {
            match tell(&port.port_name, line)? {
                Told::Said(answer) => {
                    println!("{}  {answer}", port.port_name);
                    break;
                }
                Told::Busy if started.elapsed() < Duration::from_secs(3) => {
                    thread::sleep(Duration::from_millis(50));
                }
                Told::Busy => {
                    println!("{}  another program has the port", port.port_name);
                    break;
                }
                Told::Silent => {
                    println!("{}  no answer to `{line}`", port.port_name);
                    break;
                }
            }
        }
    }
    Ok(())
}

fn plist_path() -> Result<PathBuf> {
    Ok(home()?.join(format!("Library/LaunchAgents/{LABEL}.plist")))
}

fn launchctl(args: &[&str]) -> Result<bool> {
    Ok(Command::new("launchctl").args(args).output()?.status.success())
}

fn domain() -> String {
    // SAFETY: getuid() reads the process's own user id and cannot fail.
    format!("gui/{}", unsafe { libc::getuid() })
}

fn agent(root: &Path, action: &str) -> Result<()> {
    let plist = plist_path()?;
    let target = format!("{}/{LABEL}", domain());
    match action {
        "install" => {
            let launcher = home()?.join(".local/bin/hsm-peripheral");
            ensure!(
                launcher.is_file(),
                "no {}; install the built tool with hsm-run --install-tools first",
                launcher.display()
            );
            let log = home()?.join(".config/hsm-bench/watch.log");
            let text = format!(
                "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n\
                 <!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n\
                 <plist version=\"1.0\">\n<dict>\n  \
                 <key>Label</key><string>{LABEL}</string>\n  \
                 <key>ProgramArguments</key>\n  \
                 <array><string>{}</string><string>bench-watch</string></array>\n  \
                 <key>WorkingDirectory</key><string>{}</string>\n  \
                 <key>RunAtLoad</key><true/>\n  \
                 <key>KeepAlive</key><true/>\n  \
                 <key>ProcessType</key><string>Background</string>\n  \
                 <key>StandardOutPath</key><string>{log}</string>\n  \
                 <key>StandardErrorPath</key><string>{log}</string>\n\
                 </dict>\n</plist>\n",
                launcher.display(),
                root.display(),
                log = log.display(),
            );
            fs::create_dir_all(log.parent().context("log directory")?)?;
            launchctl(&["bootout", &target])?;
            crate::write(&plist, text.as_bytes())?;
            ensure!(
                launchctl(&["bootstrap", &domain(), &plist.to_string_lossy()])?,
                "launchctl would not load {}",
                plist.display()
            );
            println!("watching from now and at every login: {}", plist.display());
            println!("its log: {}", log.display());
        }
        "remove" => {
            launchctl(&["bootout", &target])?;
            match fs::remove_file(&plist) {
                Ok(()) => println!("removed {}", plist.display()),
                Err(error) if error.kind() == ErrorKind::NotFound => {
                    println!("no watcher was installed")
                }
                Err(error) => return Err(error.into()),
            }
        }
        _ => bail!("bench agent install|remove"),
    }
    Ok(())
}

/// `bench`: this laptop's bench state, and what each connected machine says to it.
pub fn run(root: &Path, args: &[String]) -> Result<()> {
    const USAGE: &str = "bench [hold NOTICE... | off | agent install|remove]";
    let args = validate_args(args, &[], &[])?;
    match args.first().map(String::as_str) {
        None => {
            let names = held()?;
            println!(
                "this laptop holds off: {}   ({})",
                if names.is_empty() {
                    "nothing".to_owned()
                } else {
                    names.join(" ")
                },
                state_path()?.display()
            );
            let loaded = launchctl(&["print", &format!("{}/{LABEL}", domain())])?;
            println!(
                "the watcher is {}",
                if loaded {
                    "running"
                } else {
                    "not installed: hsm-peripheral bench agent install"
                }
            );
            each_board(&line_for(&names))
        }
        Some("hold") => {
            ensure!(args.len() >= 2, "{USAGE}");
            hold(&args[1..])?;
            each_board(&line_for(&args[1..]))
        }
        Some("off") => {
            ensure!(args.len() == 1, "{USAGE}");
            hold(&[])?;
            each_board(&line_for(&[]))
        }
        Some("agent") => {
            ensure!(args.len() == 2, "{USAGE}");
            agent(root, &args[1])
        }
        _ => bail!("{USAGE}"),
    }
}

/// `console-session`: hold the main board's console open across a timed list of lines and print
/// what the board said, so a run that takes minutes is one boot. Each step is seconds from the
/// start, a colon and the line; `RESET` in place of a line restarts the board.
pub fn session(args: &[String]) -> Result<()> {
    const USAGE: &str = "console-session [--port PORT] SECONDS:LINE...";
    let steps = validate_args(args, &[], &["--port"])?;
    ensure!(!steps.is_empty(), "{USAGE}");
    let path = option(args, "--port")?.map_or_else(serials::main_board_port, Ok)?;
    let mut timed = Vec::new();
    for step in &steps {
        let (at, line) = step.split_once(':').with_context(|| format!("{USAGE}: {step:?}"))?;
        let at: f64 = at.parse().with_context(|| format!("{USAGE}: {step:?}"))?;
        timed.push((Duration::from_secs_f64(at), line.to_owned()));
    }
    timed.sort_by_key(|(at, _)| *at);

    let mut port = serials::open_quiet(&path, Duration::from_millis(50))?;
    let started = Instant::now();
    let mut seen = Vec::new();
    let listen = |port: &mut dyn SerialPort, seen: &mut Vec<u8>, until: Duration| -> Result<()> {
        while started.elapsed() < until {
            seen.extend(serials::poll(port)?);
        }
        Ok(())
    };
    for (at, line) in &timed {
        listen(&mut *port, &mut seen, *at)?;
        if line == "RESET" {
            // The pulse a power cut's return gives the board: EN low, then released, with the
            // other strapping line left alone so it boots its firmware.
            port.write_request_to_send(true)?;
            thread::sleep(Duration::from_millis(120));
            port.write_request_to_send(false)?;
            seen.extend(format!("\n<<< t={}s  the board is restarted >>>\n", at.as_secs()).bytes());
        } else {
            serials::send(&mut *port, format!("\n{line}\n").as_bytes())?;
            seen.extend(format!("\n<<< t={}s  {line} >>>\n", at.as_secs()).bytes());
        }
    }
    let end = started.elapsed() + Duration::from_secs(5);
    listen(&mut *port, &mut seen, end)?;
    drop(port);
    for line in String::from_utf8_lossy(&seen).replace('\r', "").lines() {
        if !line.trim().is_empty() && line.trim() != ">" {
            println!("{line}");
        }
    }
    Ok(())
}
