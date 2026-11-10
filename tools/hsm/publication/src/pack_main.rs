//! hsm-pack reconciles or explicitly maintains the geometry artifact store.
use clap::Parser;
fn main() {
    if let Err(error) = run() {
        eprintln!("hsm-pack: {error:#}");
        std::process::exit(1);
    }
}
fn run() -> anyhow::Result<()> {
    let args = hsm_publication::pack::Options::parse();
    let root = args.root.canonicalize()?;
    unsafe {
        std::env::set_var("HSM_WORKSPACE", &root);
    }
    if args.selftest || args.mode.as_deref() == Some("selftest") {
        std::process::exit(hsm_publication::checks::run(&root)?);
    }
    let context = hsm_publication::ContextData::load(&root)?;
    let transport = hsm_publication::transport::Live { context: &context };
    std::process::exit(hsm_publication::pack::run(&context, &transport, &args)?)
}
