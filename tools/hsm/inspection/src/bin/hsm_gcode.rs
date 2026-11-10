//! The G-code inspection CLI reads existing slices without building or sending a print.
fn main() {
    let args = std::env::args().skip(1).collect::<Vec<_>>();
    match hsm_inspection::gcode::cli(&args) {
        Ok(status) => std::process::exit(status),
        Err(error) => {
            eprintln!("hsm-gcode: {error:#}");
            std::process::exit(1);
        }
    }
}
