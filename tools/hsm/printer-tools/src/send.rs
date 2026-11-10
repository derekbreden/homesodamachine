//! Submit through the selected native application input mode and trust the printer's new job report.
use crate::{
    archive::{self, Details},
    config,
    mqtt::Watch,
    state,
    ui::{self, Input, Ui},
    Args,
};
use anyhow::{bail, Context, Result};
use serde_json::{json, Value};
use std::{
    fs::{self, File, OpenOptions},
    os::fd::AsRawFd,
    path::{Path, PathBuf},
    time::{Duration, Instant},
};

pub struct Transaction {
    _file: File,
}
impl Transaction {
    pub fn open(cache: &Path) -> Result<Self> {
        fs::create_dir_all(cache)?;
        let file = OpenOptions::new()
            .write(true)
            .create(true)
            .truncate(false)
            .open(cache.join("bambu-print.lock"))?;
        if unsafe { libc::flock(file.as_raw_fd(), libc::LOCK_EX | libc::LOCK_NB) } != 0 {
            bail!("Another printer send transaction is active")
        };
        Ok(Self { _file: file })
    }
}
pub struct Options {
    pub path: PathBuf,
    pub printer: String,
    pub dry_run: bool,
    pub attempts: usize,
    pub timeout: Duration,
    pub busy_wait: Duration,
    pub timelapse: String,
}
pub fn arguments(args: &mut Args, background: bool) -> Result<Options> {
    let dry_run = args.flag("--dry-run");
    let attempts = args.number("--attempts", 3_usize)?;
    let timeout = args.number(
        "--accept-timeout",
        if background { 120_f64 } else { 90_f64 },
    )?;
    let busy_wait = args.number("--busy-wait", 900_f64)?;
    let timelapse = args.option("--timelapse").unwrap_or_else(|| "On".into());
    let path = crate::expand(&args.positional("archive")?).canonicalize()?;
    let printer = args.positional("printer")?;
    args.finish()?;
    ui::shown(&printer)?;
    if !(1..=3).contains(&attempts)
        || !timeout.is_finite()
        || timeout <= 0.
        || !busy_wait.is_finite()
        || busy_wait < 0.
        || !matches!(timelapse.as_str(), "On" | "Off")
    {
        bail!("Invalid attempts, timeout, busy-wait or timelapse option")
    }
    if !path.is_file()
        || !path
            .file_name()
            .unwrap_or_default()
            .to_string_lossy()
            .ends_with(".gcode.3mf")
    {
        bail!("Supply an existing .gcode.3mf archive")
    }
    Ok(Options {
        path,
        printer,
        dry_run,
        attempts,
        timeout: Duration::from_secs_f64(timeout),
        busy_wait: Duration::from_secs_f64(busy_wait),
        timelapse,
    })
}
pub fn run(root: &Path, args: &mut Args, background: bool) -> Result<()> {
    let options = arguments(args, background)?;
    let details = archive::details(&options.path)?;
    let cache = root.join(".cache/printer-control");
    let _lock = Transaction::open(&cache)?;
    let imported = cache
        .join("imports")
        .join(&details.sha256)
        .join(&details.name);
    fs::create_dir_all(imported.parent().unwrap())?;
    fs::copy(&options.path, &imported)?;
    let printers = config::configured(&crate::home()?)?;
    let printer = printers
        .get(&options.printer)
        .context("Printer is not configured")?;
    let mut watch = Watch::open(printer)?;
    let before = watch.activity.initial.clone();
    if state::busy(&before) && !options.dry_run {
        bail!(
            "{} is {} on {}",
            options.printer,
            before["gcode_state"],
            before["subtask_name"]
        )
    }
    archive::verify_spools(&details, &before)?;
    println!(
        "{}: {}, job {}",
        options.printer,
        before["gcode_state"],
        state::text(&before["job_id"])
    );
    let result = if background {
        crate::ax::send(root, &cache, &options, &details, &imported, &mut watch)?
    } else {
        foreground(root, &cache, &options, &details, &imported, &mut watch)?
    };
    if let Some(result) = result {
        let receipt = json!({"printer":options.printer,"observed_at":crate::now(),"archive":details,"printer_task_id":state::text(&result["job_id"]),"gcode_state":result["gcode_state"],"subtask_name":result["subtask_name"],"print_error":result["print_error"],"hms":result["hms"],"layer_num":result["layer_num"],"total_layer_num":result["total_layer_num"],"mc_remaining_time":result["mc_remaining_time"]});
        let path = cache.join(format!(
            "{}-{}-launch.json",
            options.printer,
            state::text(&result["job_id"])
        ));
        fs::write(
            &path,
            format!("{}\n", serde_json::to_string_pretty(&receipt)?),
        )?;
        println!(
            "{}\nLaunch record: {}",
            serde_json::to_string_pretty(&receipt)?,
            path.display()
        );
    }
    Ok(())
}
fn foreground(
    root: &Path,
    cache: &Path,
    options: &Options,
    details: &Details,
    imported: &Path,
    watch: &mut Watch,
) -> Result<Option<Value>> {
    let desired = ui::wanted(&options.timelapse);
    let mut input = Ui::open(root, cache)?;
    let result = (|| -> Result<Option<Value>> {
        for attempt in 0..options.attempts {
            fs::copy(&options.path, imported)?;
            let nodes = ui::prepare(&mut input, imported, &options.printer, details, &desired)?;
            let button = ui::matching(&nodes, "confirm", Some("AXButton"))[0];
            if options.dry_run {
                println!(
                    "Dry run: Send is {}; cancelling without sending",
                    if button.enabled {
                        "enabled"
                    } else {
                        "disabled"
                    }
                );
                return Ok(None);
            }
            if !button.enabled {
                bail!("Send is disabled; nothing was sent")
            }
            let current = watch.fresh()?.clone();
            if state::accepted(&watch.activity.initial, &current, &details.name) {
                return Ok(Some(current));
            }
            if !state::may_retry(
                &watch.activity.initial,
                &current,
                watch.activity.activity,
                "",
            ) {
                bail!("The printer changed or is heating; nothing more was sent")
            }
            archive::verify_spools(details, &current)?;
            if crate::digest(&options.path)? != details.sha256 {
                bail!("The archive changed after import")
            }
            ui::verify(&input.nodes()?, &options.printer, details, &desired)?;
            println!(
                "Sending attempt {}: one foreground mouse click",
                attempt + 1
            );
            if let Err(error) = input.click("confirm", "AXButton", 0, false) {
                println!(
                    "Send input returned {error}; checking the printer before any further action"
                )
            }
            if let Some(result) = observe(&mut input, watch, details, options.timeout)? {
                return Ok(Some(result));
            }
            println!("No printer activity and no transfer in the app; opening a fresh dialog");
        }
        bail!("The printer received no job after the bounded send attempts")
    })();
    if let Err(error) = ui::close_dialog(&mut input) {
        eprintln!("Dialog cleanup: {error}")
    }
    result
}
pub fn observe(
    input: &mut impl Input,
    watch: &mut Watch,
    details: &Details,
    timeout: Duration,
) -> Result<Option<Value>> {
    let deadline = Instant::now() + timeout;
    while Instant::now() < deadline {
        let reading = watch.drain(Duration::from_millis(500))?.clone();
        if let Some(reply) = &watch.activity.reply {
            if !matches!(
                reply["result"]
                    .as_str()
                    .map(str::to_ascii_lowercase)
                    .as_deref(),
                Some("success" | "ok")
            ) {
                bail!("Printer refused the job: {reply}")
            }
        }
        if state::accepted(&watch.activity.initial, &reading, &details.name) {
            watch.drain(Duration::from_secs(3))?;
            let reading = watch.fresh()?.clone();
            if state::accepted(&watch.activity.initial, &reading, &details.name) {
                return Ok(Some(reading));
            }
        }
        if state::text(&reading["print_error"])
            != state::text(&watch.activity.initial["print_error"])
            && state::truth(&reading["print_error"])
        {
            bail!("Printer error {}; no repeat send", reading["print_error"])
        }
        let error = ui::visible_error(&input.nodes()?);
        if !error.is_empty() {
            watch.activity.events.push(json!({"ui_error":error}));
            bail!("Bambu Connect: {error}; no repeat send")
        }
    }
    let reading = watch.fresh()?.clone();
    let text = ui::page_text(&input.nodes()?);
    if state::may_retry(
        &watch.activity.initial,
        &reading,
        watch.activity.activity,
        &text,
    ) {
        return Ok(None);
    }
    bail!("The send has an uncertain or rejected result; no repeat send. Printer: {}, job {}; page: {text}",reading["gcode_state"],state::text(&reading["job_id"]))
}
