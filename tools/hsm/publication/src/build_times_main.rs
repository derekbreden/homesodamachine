//! Recorded native print-build timings reach the site's history without starting a build.
fn main() {
    if let Err(error) = hsm_run_slots::clear_inherited_for_service() {
        eprintln!("hsm-build-times: {error:#}");
        std::process::exit(1);
    }
    hsm_publication::maintenance_main("hsm-build-times", hsm_publication::build_times::run);
}
