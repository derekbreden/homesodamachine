//! Pick text and published links point at existing exported surfaces.
use anyhow::{Context, Result};
use clap::{Parser, Subcommand};
use hsm_inspection::{
    pick_format::{self, Compose},
    pick_read,
};
use std::{
    fs,
    io::{self, Read},
    path::PathBuf,
};
#[derive(Parser)]
#[command(
    name = "hsm-pick",
    about = "Compose browser picks and read their existing fine, print and viewer exports"
)]
struct Args {
    #[arg(long, global = true)]
    root: Option<PathBuf>,
    #[command(subcommand)]
    command: Action,
}
#[derive(Subcommand)]
enum Action {
    Demo,
    Compose {
        input: Option<PathBuf>,
        #[arg(long)]
        link: bool,
        #[arg(long,default_value=pick_format::SITE)]
        site: String,
    },
    Link {
        model: PathBuf,
        input: Option<PathBuf>,
        #[arg(long,default_value=pick_format::SITE)]
        site: String,
    },
    Read {
        input: Option<PathBuf>,
        #[arg(long, default_value_t = 1.)]
        radius: f64,
        #[arg(long, default_value_t = 6)]
        rows: usize,
        #[arg(long, value_delimiter = ',', default_value = "authored,printed,drawn")]
        surfaces: Vec<String>,
        #[arg(long)]
        json: bool,
    },
}
fn text(input: Option<PathBuf>) -> Result<String> {
    match input {
        Some(path) if path.as_os_str() != "-" => Ok(fs::read_to_string(path)?),
        _ => {
            let mut text = String::new();
            io::stdin().read_to_string(&mut text)?;
            Ok(text)
        }
    }
}
fn run() -> Result<()> {
    let args = Args::parse();
    let root = args
        .root
        .unwrap_or_else(hsm_print_prep::root)
        .canonicalize()?;
    match args.command {
        Action::Demo => println!(
            "{}",
            pick_format::compose(&root, &pick_format::demo())?.join("\n")
        ),
        Action::Compose { input, link, site } => {
            let request: Compose = serde_json::from_str(&text(input)?)?;
            let lines = pick_format::compose(&root, &request)?.join("\n");
            if link {
                println!(
                    "{}",
                    pick_format::link(
                        &root,
                        request
                            .model
                            .as_ref()
                            .context("compose --link needs model")?,
                        &lines,
                        &site
                    )
                );
            } else {
                println!("{lines}");
            }
        }
        Action::Link { model, input, site } => {
            println!("{}", pick_format::link(&root, &model, &text(input)?, &site))
        }
        Action::Read {
            input,
            radius,
            rows,
            surfaces,
            json,
        } => {
            let options = pick_read::Options {
                radius,
                rows,
                surfaces,
            };
            let report = pick_read::read(&root, &text(input)?, &options)?;
            if json {
                println!("{}", serde_json::to_string_pretty(&report)?);
            } else {
                pick_read::print(&report, &options);
            }
        }
    }
    Ok(())
}
fn main() {
    if let Err(error) = run() {
        eprintln!("hsm-pick: {error:#}");
        std::process::exit(1);
    }
}
