//! The positioner's native saved-frame readers, image features and capture-helper protocol.
pub mod capture;
pub mod features;
pub mod helper_stream;
pub mod imageio;

/// The helper and observer share the platform's monotonic host clock.
pub fn monotonic_ns() -> u64 {
    #[cfg(target_os = "macos")]
    {
        #[repr(C)]
        struct Timebase {
            numer: u32,
            denom: u32,
        }
        unsafe extern "C" {
            fn mach_absolute_time() -> u64;
            fn mach_timebase_info(info: *mut Timebase) -> i32;
        }
        static BASE: std::sync::OnceLock<(u32, u32)> = std::sync::OnceLock::new();
        let &(numer, denom) = BASE.get_or_init(|| {
            let mut info = Timebase { numer: 0, denom: 0 };
            let result = unsafe { mach_timebase_info(&mut info) };
            assert!(
                result == 0 && info.denom != 0,
                "the monotonic host timebase"
            );
            (info.numer, info.denom)
        });
        let ticks = unsafe { mach_absolute_time() };
        ((ticks as u128 * numer as u128) / denom as u128) as u64
    }
    #[cfg(not(target_os = "macos"))]
    {
        let mut value = libc::timespec {
            tv_sec: 0,
            tv_nsec: 0,
        };
        let result = unsafe { libc::clock_gettime(libc::CLOCK_MONOTONIC, &mut value) };
        assert_eq!(result, 0, "the monotonic host clock");
        value.tv_sec as u64 * 1_000_000_000 + value.tv_nsec as u64
    }
}

pub fn quantile(values: &[f64], fraction: f64) -> f64 {
    let mut values = values.to_vec();
    values.sort_by(f64::total_cmp);
    if values.is_empty() {
        return f64::NAN;
    }
    let position = fraction * (values.len() - 1) as f64;
    let low = position.floor() as usize;
    let high = position.ceil() as usize;
    values[low] + (values[high] - values[low]) * (position - low as f64)
}

pub fn median(values: &[f64]) -> f64 {
    quantile(values, 0.5)
}
