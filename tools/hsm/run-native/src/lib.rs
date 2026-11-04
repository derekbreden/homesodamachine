//! ABI1 entry points for the in-process host runtime.
use std::ffi::c_char;

#[unsafe(no_mangle)]
pub unsafe extern "C" fn hsm_run_request(
    input: *const c_char,
    callback: hsm_run_slots::runtime::Host,
) -> *mut c_char {
    unsafe { hsm_run_slots::runtime::ffi_request(input, callback) }
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn hsm_run_free(value: *mut c_char) {
    unsafe { hsm_run_slots::runtime::ffi_free(value) }
}
