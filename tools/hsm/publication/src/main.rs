//! hsm-publish advances completed geometry without rebuilding its producers.
use clap::Parser;
fn main() {
    if let Err(error) = run() {
        eprintln!("hsm-publish: {error:#}");
        std::process::exit(1);
    }
}
fn run() -> anyhow::Result<()> {
    hsm_run_slots::clear_inherited_for_service()?;
    let args = hsm_publication::publish::Options::parse();
    let root = args.root.canonicalize()?;
    unsafe {
        std::env::set_var("HSM_WORKSPACE", &root);
    }
    if args.selftest {
        std::process::exit(hsm_publication::checks::run(&root)?);
    }
    let context = hsm_publication::ContextData::load(&root)?;
    let transport = hsm_publication::transport::Live { context: &context };
    std::process::exit(hsm_publication::publish::run(
        &context, &transport, args.check,
    )?)
}
