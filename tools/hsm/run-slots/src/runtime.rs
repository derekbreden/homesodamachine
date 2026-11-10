//! In-process ABI for Python adapters and the native heavy-command runner.
use super::*;
use std::{
    collections::BTreeMap,
    ffi::{CStr, CString, c_char},
    os::fd::IntoRawFd,
};
pub mod cad;
pub mod install;
pub mod runner;
pub mod slots;
static DIRECTORY: Mutex<Option<PathBuf>> = Mutex::new(None);
pub(crate) fn directory_override() -> Option<PathBuf> {
    DIRECTORY.lock().unwrap().clone()
}
pub type Host = Option<extern "C" fn(*const c_char) -> *const c_char>;
pub fn host(callback: Host, value: Value) -> Result<Value> {
    if let Some(callback) = callback {
        let input = CString::new(serde_json::to_vec(&value)?)?;
        let returned = callback(input.as_ptr());
        ensure!(!returned.is_null(), "host primitive returned no result");
        let value: Value = serde_json::from_slice(unsafe { CStr::from_ptr(returned) }.to_bytes())?;
        if let Some(error) = value.get("error") {
            bail!("host primitive: {}", error.as_str().unwrap_or("failed"));
        }
        return value.get("value").cloned().context("host primitive result");
    }
    match value["call"].as_str() {
        Some("stdout") => {
            print!("{}", value["text"].as_str().unwrap_or(""));
            std::io::stdout().flush()?;
            Ok(Value::Null)
        }
        Some("stderr") => {
            eprint!("{}", value["text"].as_str().unwrap_or(""));
            std::io::stderr().flush()?;
            Ok(Value::Null)
        }
        _ => bail!("no host primitive for {value}"),
    }
}
pub fn text(value: &Value) -> Result<&str> {
    value.as_str().context("runtime string")
}
pub fn dispatch(input: Value, callback: Host) -> Result<Value> {
    if let Some(value) = input.get("directory") {
        *DIRECTORY.lock().unwrap() = value.as_str().map(PathBuf::from);
    }
    if let Some(value) = input.get("environment") {
        slots::refresh_environment(value);
    }
    let op = text(&input["op"])?;
    let data = &input["data"];
    match op {
        "runtime_info" => install::info(Path::new(text(&input["root"])?)),
        op if op.starts_with("cad_") => {
            cad::request(op, data, Path::new(text(&input["root"])?), callback)
        }
        op if op.starts_with("socket_") => socket(op, data, callback),
        _ => slots::request(op, data, callback),
    }
}
fn socket(op: &str, d: &Value, callback: Host) -> Result<Value> {
    if op == "socket_send" {
        let mut bytes = serde_json::to_vec(&d["value"])?;
        bytes.push(b'\n');
        ensure!(
            bytes.len() <= 16384
                && d["fds"].as_array().context("descriptors")?.len() <= capacity() + 2,
            "oversized lease frame"
        );
        let sent = host(
            callback,
            json!({"call":"sendmsg","bytes":bytes,"fds":d["fds"]}),
        )?
        .as_u64()
        .context("socket send count")? as usize;
        ensure!(sent > 0, "socket accepted no lease bytes");
        if sent < bytes.len() {
            host(callback, json!({"call":"sendall","bytes":bytes[sent..]}))?;
        }
        return Ok(Value::Null);
    }
    ensure!(op == "socket_receive", "unknown socket operation {op}");
    let timeout = host(callback, json!({"call":"gettimeout"}))?;
    let began = std::time::Instant::now();
    let seconds = timeout.as_f64().unwrap_or(1.);
    let mut bytes = Vec::new();
    let mut fds: Vec<OwnedFd> = Vec::new();
    let result = (|| -> Result<Value> {
        loop {
            let remaining = seconds - began.elapsed().as_secs_f64();
            ensure!(remaining > 0., "lease frame timed out");
            host(callback, json!({"call":"settimeout","value":remaining}))?;
            let reply = host(
                callback,
                json!({"call":"recvmsg","bytes":4096,"space":rustix::cmsg_space!(ScmRights(512))}),
            )?;
            for row in reply["ancillary"]
                .as_array()
                .context("received ancillary data")?
            {
                if row[0].as_i64() == Some(libc::SOL_SOCKET as i64)
                    && row[1].as_i64() == Some(libc::SCM_RIGHTS as i64)
                {
                    let bytes: Vec<u8> = serde_json::from_value(row[2].clone())?;
                    for raw in bytes.chunks_exact(4) {
                        let fd = i32::from_ne_bytes(raw.try_into().unwrap());
                        ensure!(fd >= 0, "invalid descriptor");
                        let owned = unsafe { OwnedFd::from_raw_fd(fd) };
                        cloexec(fd)?;
                        fds.push(owned);
                    }
                }
            }
            ensure!(
                reply["flags"].as_i64().unwrap_or(0) & libc::MSG_CTRUNC as i64 == 0
                    && fds.len() <= capacity() + 2,
                "truncated or excess lease descriptors"
            );
            let chunk: Vec<u8> = serde_json::from_value(reply["bytes"].clone())?;
            let closed = chunk.is_empty();
            bytes.extend(chunk);
            ensure!(
                bytes.len() <= d["limit"].as_u64().unwrap_or(16384) as usize,
                "oversized lease frame"
            );
            if bytes.contains(&b'\n') {
                let value: Value = serde_json::from_slice(&bytes)?;
                ensure!(value.is_object(), "a lease frame must be an object");
                return Ok(json!([
                    value,
                    fds.iter().map(AsRawFd::as_raw_fd).collect::<Vec<_>>()
                ]));
            }
            ensure!(!closed, "socket closed before a complete lease frame");
        }
    })();
    let restored = host(callback, json!({"call":"settimeout","value":timeout}));
    let value = result?;
    restored?;
    for fd in fds {
        let _ = fd.into_raw_fd();
    }
    Ok(value)
}
pub unsafe extern "C" fn ffi_request(input: *const c_char, callback: Host) -> *mut c_char {
    let result = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| -> Result<Value> {
        ensure!(!input.is_null(), "missing runtime request");
        dispatch(
            serde_json::from_slice(unsafe { CStr::from_ptr(input) }.to_bytes())?,
            callback,
        )
    }));
    let reply = match result {
        Ok(Ok(value)) => json!({"value":value}),
        Ok(Err(error)) => {
            json!({"error":format!("{error:#}"),"errno":error.downcast_ref::<std::io::Error>().and_then(std::io::Error::raw_os_error)})
        }
        Err(_) => json!({"error":"native runtime failed"}),
    };
    CString::new(serde_json::to_vec(&reply).unwrap())
        .unwrap()
        .into_raw()
}
pub unsafe extern "C" fn ffi_free(value: *mut c_char) {
    if !value.is_null() {
        drop(unsafe { CString::from_raw(value) });
    }
}
