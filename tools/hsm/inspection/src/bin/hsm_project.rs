//! `hsm-project compare` tells what differs between two print projects by value, when someone
//! asks; it builds, slices and sends nothing.
use clap::{Parser, Subcommand};
use hsm_inspection::project_compare;

#[derive(Parser)]
#[command(name = "hsm-project", about = "Compare two Bambu print projects by value, member by member")]
struct Command {
    #[command(subcommand)]
    mode: Mode,
}

#[derive(Subcommand)]
enum Mode {
    /// What differs, by value, between two projects, two sliced archives or two preparers' output folders.
    Compare(project_compare::Options),
}

fn main() {
    let Mode::Compare(options) = Command::parse().mode;
    match project_compare::run(options) {
        Ok(status) => std::process::exit(status),
        Err(error) => {
            eprintln!("hsm-project: {error:#}");
            std::process::exit(2);
        }
    }
}
