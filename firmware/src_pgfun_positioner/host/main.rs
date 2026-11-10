//! The positioner host exposes explicit operator commands and offline optical qualification.
use anyhow::{Context, Result, bail, ensure};
use hsm_pgfun_host::{
    self as host,
    client::{Client, SerialTransport},
    kinematics::Geometry,
    noise, observe, servo, trajectory,
};
use hsm_pgfun_observation::helper_stream::{HelperPaths, clock_check, list_cameras};
use serde::Serialize;
use sha2::{Digest, Sha256};
use std::{
    collections::BTreeMap,
    io::{self, Write},
    path::PathBuf,
    str::FromStr,
};

const HELP: &str = "pgfun-host runs the positioner's operator console and optical calibration.\n\n\
Usage: pgfun-host COMMAND [--root DIR] [--geometry FILE] ...\n\n\
  console --port PORT [--log FILE] | --list\n\
  observe --camera-id ID --config FILE --latest FILE --log FILE [--seconds S]\n\
  observe --list | --clock-check\n\
  response fit PAIRS MODEL\n\
  response qualify MODEL HOLDOUT OUTPUT\n\
  response learn --port PORT --latest FILE --output FILE --reference-central\n\
  response follow --port PORT --latest FILE --model FILE --target FILE --reference-central [--seconds S]\n\
  trajectory fit CAPTURE MODEL TARGET OUTPUT\n\
  trajectory qualify PROFILE CAPTURE CAPTURE --output FILE\n\
  trajectory capture --port PORT --latest FILE --output FILE --speed MM_S --direction cw|ccw --index LABEL --log FILE --reference-central [--profile FILE] [--seconds S]\n\
  trajectory replay --port PORT --profile FILE --log FILE --reference-central [--seconds S]\n\
  noise LOG CONFIG OUTPUT --receipt FILE\n\n\
Offline fit and qualification commands read saved files. Device commands open only the explicitly selected port or camera.";

struct Args {
    positional: Vec<String>,
    options: BTreeMap<String, String>,
    flags: Vec<String>,
}
impl Args {
    fn parse(values: impl Iterator<Item = String>) -> Result<Self> {
        let mut out = Self {
            positional: vec![],
            options: BTreeMap::new(),
            flags: vec![],
        };
        let mut values = values.peekable();
        while let Some(value) = values.next() {
            if let Some(key) = value.strip_prefix("--") {
                if ["list", "clock-check", "reference-central"].contains(&key) {
                    ensure!(!out.flags.iter().any(|v| v == key), "duplicate --{key}");
                    out.flags.push(key.into());
                } else {
                    let argument = values
                        .next()
                        .with_context(|| format!("--{key} requires a value"))?;
                    ensure!(!argument.starts_with("--"), "--{key} requires a value");
                    ensure!(
                        out.options.insert(key.into(), argument).is_none(),
                        "duplicate --{key}"
                    );
                }
            } else {
                out.positional.push(value);
            }
        }
        Ok(out)
    }
    fn option(&mut self, key: &str) -> Option<String> {
        self.options.remove(key)
    }
    fn required(&mut self, key: &str) -> Result<String> {
        self.option(key)
            .with_context(|| format!("--{key} required"))
    }
    fn path(&mut self, key: &str) -> Result<PathBuf> {
        Ok(self.required(key)?.into())
    }
    fn number<T: FromStr>(&mut self, key: &str, default: T) -> Result<T>
    where
        T::Err: std::fmt::Display,
    {
        self.option(key).map_or(Ok(default), |v| {
            v.parse().map_err(|e| anyhow::anyhow!("--{key}: {e}"))
        })
    }
    fn flag(&mut self, key: &str) -> bool {
        if let Some(index) = self.flags.iter().position(|v| v == key) {
            self.flags.remove(index);
            true
        } else {
            false
        }
    }
    fn reference(&mut self) -> Result<()> {
        ensure!(
            self.flag("reference-central"),
            "--reference-central acknowledges the aligned, removed parking pins"
        );
        Ok(())
    }
    fn positionals(&mut self, count: usize) -> Result<Vec<String>> {
        ensure!(
            self.positional.len() == count,
            "expected {count} file arguments"
        );
        Ok(std::mem::take(&mut self.positional))
    }
    fn done(&self) -> Result<()> {
        ensure!(
            self.positional.is_empty() && self.options.is_empty() && self.flags.is_empty(),
            "unexpected arguments: {:?} {:?} {:?}",
            self.positional,
            self.options,
            self.flags
        );
        Ok(())
    }
}
fn print(value: &impl Serialize) -> Result<()> {
    println!("{}", serde_json::to_string_pretty(value)?);
    Ok(())
}
fn console(client: &mut Client<SerialTransport>) -> Result<()> {
    println!(
        "clear; reference central; arm; jog yaw|pitch counts duration_ms; status; drivers; disarm; stop; recover; quit"
    );
    let mut input = Vec::new();
    loop {
        print!("pgfun> ");
        io::stdout().flush()?;
        let line = loop {
            ensure!(!host::interrupted(), "host interrupted");
            if let Some(end) = input.iter().position(|&v| v == b'\n') {
                let remainder = input.split_off(end + 1);
                let mut bytes = std::mem::replace(&mut input, remainder);
                bytes.truncate(end);
                break String::from_utf8(bytes)?;
            }
            let mut descriptor = libc::pollfd {
                fd: libc::STDIN_FILENO,
                events: libc::POLLIN,
                revents: 0,
            };
            let ready = unsafe { libc::poll(&mut descriptor, 1, 100) };
            if ready < 0 {
                let error = io::Error::last_os_error();
                if error.kind() == io::ErrorKind::Interrupted {
                    continue;
                }
                return Err(error.into());
            }
            if ready == 0 {
                continue;
            }
            let mut chunk = [0_u8; 4096];
            let length =
                unsafe { libc::read(libc::STDIN_FILENO, chunk.as_mut_ptr().cast(), chunk.len()) };
            if length < 0 {
                let error = io::Error::last_os_error();
                if error.kind() == io::ErrorKind::Interrupted {
                    continue;
                }
                return Err(error.into());
            }
            if length == 0 {
                if input.is_empty() {
                    return Ok(());
                }
                break String::from_utf8(std::mem::take(&mut input))?;
            }
            input.extend_from_slice(&chunk[..length as usize]);
        };
        let fields: Vec<_> = line.split_whitespace().collect();
        if fields.is_empty() {
            continue;
        }
        let command = (|| -> Result<()> {
            match fields.as_slice() {
                ["quit" | "exit"] => return Ok(()),
                ["status"] => print(&client.status()?),
                ["drivers"] => print(&client.drivers()?),
                ["stop"] => print(&client.stop()?),
                ["recover"] => print(&client.recover()?),
                ["clear"] => print(&client.request("CLEAR", &[])?),
                ["reference", "central"] => print(&client.request("REF", &[])?),
                ["arm"] => {
                    let reply = client.request("ARM", &[])?;
                    client.start_heartbeat()?;
                    print(&reply)
                }
                ["disarm"] => print(&client.request("DISARM", &[])?),
                ["jog", axis, counts, millis] => {
                    let index = match *axis {
                        "yaw" => 0,
                        "pitch" => 1,
                        _ => bail!("axis must be yaw or pitch"),
                    };
                    let mut delta = [0, 0];
                    delta[index] = counts.parse()?;
                    let duration: f64 = millis.parse()?;
                    ensure!(
                        duration.is_finite() && duration >= 0.,
                        "finite nonnegative duration required"
                    );
                    print(&client.move_counts(delta, (duration * 1000.) as u64)?)
                }
                _ => bail!("unknown command or argument count"),
            }
        })();
        if matches!(fields.as_slice(), ["quit" | "exit"]) {
            return Ok(());
        }
        if let Err(error) = command {
            eprintln!("{error:#}");
        }
    }
}

fn run() -> Result<()> {
    let values: Vec<_> = std::env::args().skip(1).collect();
    if values.is_empty() || values.iter().any(|v| v == "--help" || v == "-h") {
        println!("{HELP}");
        return Ok(());
    }
    let mut args = Args::parse(values.into_iter())?;
    ensure!(!args.positional.is_empty(), "a command is required");
    let command = args.positional.remove(0);
    let root = args
        .option("root")
        .map(PathBuf::from)
        .unwrap_or_else(host::root);
    let geometry_path = args
        .option("geometry")
        .map(PathBuf::from)
        .unwrap_or_else(|| {
            root.join("hardware/printed-parts/fixtures/pgfun-positioner/motion-geometry.json")
        });
    match command.as_str() {
        "console" => {
            if args.flag("list") {
                args.done()?;
                for port in serialport::available_ports()? {
                    println!("{} {:?}", port.port_name, port.port_type);
                }
                return Ok(());
            }
            let port = args.required("port")?;
            let log = args.option("log").map(PathBuf::from);
            args.done()?;
            let mut client = Client::open(&port, Geometry::read(&geometry_path)?, log.as_deref())?;
            let result = console(&mut client);
            let closed = client.close();
            result.and(closed)
        }
        "observe" => {
            if args.flag("list") {
                args.done()?;
                return print(&list_cameras(&HelperPaths::in_root(&root))?);
            }
            if args.flag("clock-check") {
                args.done()?;
                return print(&clock_check(&HelperPaths::in_root(&root))?);
            }
            let options = observe::ObserveOptions {
                camera_id: args.required("camera-id")?,
                config: args.path("config")?,
                latest: args.path("latest")?,
                log: args.path("log")?,
                seconds: args.number("seconds", 3600.)?,
            };
            args.done()?;
            observe::run(&root, &options)
        }
        "noise" => {
            let files = args.positionals(3)?;
            let receipt_path = args.path("receipt")?;
            args.done()?;
            let raw = std::fs::read(&files[0])?;
            let mut rows = vec![];
            for line in raw
                .split(|&b| b == b'\n')
                .filter(|line| !line.iter().all(u8::is_ascii_whitespace))
            {
                rows.push(serde_json::from_slice::<noise::NoiseSample>(line)?);
            }
            let (mut config, mut receipt) =
                noise::qualify(&rows, &host::read::<noise::NoiseConfig>(&files[1])?)?;
            receipt.source_sha256 = Some(format!("{:x}", Sha256::digest(&raw)));
            let mut encoded = serde_json::to_vec_pretty(&receipt)?;
            encoded.push(b'\n');
            config.noise_receipt_sha256 = Some(format!("{:x}", Sha256::digest(&encoded)));
            std::fs::write(receipt_path, encoded)?;
            host::write(&files[2], &config)
        }
        "response" => {
            ensure!(!args.positional.is_empty(), "response operation required");
            let operation = args.positional.remove(0);
            let geometry = Geometry::read(&geometry_path)?;
            match operation.as_str() {
                "fit" => {
                    let files = args.positionals(2)?;
                    args.done()?;
                    host::write(
                        &files[1],
                        &servo::fit(&geometry, &host::read::<Vec<_>>(&files[0])?)?,
                    )
                }
                "qualify" => {
                    let files = args.positionals(3)?;
                    args.done()?;
                    host::write(
                        &files[2],
                        &servo::qualify(
                            &host::read(&files[0])?,
                            &host::read::<Vec<_>>(&files[1])?,
                        )?,
                    )
                }
                "learn" | "follow" => {
                    args.reference()?;
                    let port = args.required("port")?;
                    let latest = args.path("latest")?;
                    if operation == "learn" {
                        let output = args.path("output")?;
                        args.done()?;
                        let mut client = Client::open(&port, geometry, None)?;
                        client.establish()?;
                        host::write(
                            output,
                            &servo::collect(&client, &latest, &[2, 4, 8, 16, 32, 64])?,
                        )
                    } else {
                        let model: servo::Model = host::read(args.path("model")?)?;
                        let target: trajectory::Target = host::read(args.path("target")?)?;
                        let seconds = args.number("seconds", 60.)?;
                        args.done()?;
                        let mut client = Client::open(&port, geometry.clone(), None)?;
                        client.establish()?;
                        servo::follow(
                            &geometry,
                            &client,
                            &latest,
                            &model,
                            target.values_mm,
                            [1, 1],
                            seconds,
                        )
                    }
                }
                _ => bail!("unknown response operation: {operation}"),
            }
        }
        "trajectory" => {
            ensure!(!args.positional.is_empty(), "trajectory operation required");
            let operation = args.positional.remove(0);
            let geometry = Geometry::read(&geometry_path)?;
            match operation.as_str() {
                "fit" => {
                    let files = args.positionals(4)?;
                    args.done()?;
                    host::write(
                        &files[3],
                        &trajectory::fit(
                            &geometry,
                            &host::read(&files[0])?,
                            &host::read(&files[1])?,
                            &host::read(&files[2])?,
                            3,
                        )?,
                    )
                }
                "qualify" => {
                    let files = args.positionals(3)?;
                    let output = args.path("output")?;
                    args.done()?;
                    host::write(
                        output,
                        &trajectory::qualify(
                            &geometry,
                            &host::read(&files[0])?,
                            &[host::read(&files[1])?, host::read(&files[2])?],
                        )?,
                    )
                }
                "capture" | "replay" => {
                    args.reference()?;
                    let port = args.required("port")?;
                    let log = args.path("log")?;
                    let seconds = args.number("seconds", 110.)?;
                    let selected = args
                        .option("profile")
                        .map(host::read::<trajectory::Profile>)
                        .transpose()?;
                    if operation == "capture" {
                        let latest = args.path("latest")?;
                        let output = args.path("output")?;
                        let speed = args.number("speed", f64::NAN)?;
                        let direction = args.required("direction")?;
                        ensure!(
                            ["cw", "ccw"].contains(&direction.as_str()),
                            "direction must be cw or ccw"
                        );
                        let index = args.required("index")?;
                        args.done()?;
                        let period = trajectory::period_for_speed(speed)?;
                        let profile = selected
                            .unwrap_or_else(|| trajectory::Profile::centered(&geometry, period));
                        ensure!(
                            profile.period_us == period,
                            "profile does not match the rotator speed"
                        );
                        trajectory::check(&geometry, &profile)?;
                        let mut client = Client::open(&port, geometry.clone(), Some(&log))?;
                        client.establish()?;
                        host::write(
                            output,
                            &trajectory::capture(
                                &geometry, &client, &latest, &profile, seconds, speed, &direction,
                                &index,
                            )?,
                        )
                    } else {
                        let profile = selected.context("--profile required")?;
                        args.done()?;
                        trajectory::check(&geometry, &profile)?;
                        let mut client = Client::open(&port, geometry.clone(), Some(&log))?;
                        client.establish()?;
                        trajectory::replay(&geometry, &client, &profile, seconds)
                    }
                }
                _ => bail!("unknown trajectory operation: {operation}"),
            }
        }
        _ => bail!("unknown command: {command}\n{HELP}"),
    }
}
extern "C" fn interrupted(_: libc::c_int) {
    host::interrupt();
}
fn main() {
    unsafe {
        libc::signal(libc::SIGINT, interrupted as *const () as libc::sighandler_t);
        libc::signal(
            libc::SIGTERM,
            interrupted as *const () as libc::sighandler_t,
        );
    }
    if let Err(error) = run() {
        eprintln!("{error:#}");
        std::process::exit(1);
    }
}
