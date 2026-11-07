//! The turns about X that lay the shell's two prints on the bed, in radians, as JSON: what the
//! faucet's print project turns each piece by, from the faucet's numbers.
//!
//!     faucet-shell-print-rotations
use hsm_faucet_numbers::shell::{PRINT_BASE_BUILD_ROT, PRINT_TIP_BUILD_ROT};

fn main() {
    println!("{{\"faucet-shell-base\": {PRINT_BASE_BUILD_ROT:?}, \"faucet-shell-tip\": {PRINT_TIP_BUILD_ROT:?}}}");
}
