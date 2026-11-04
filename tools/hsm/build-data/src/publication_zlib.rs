//! The host zlib primitive used for byte-compatible deterministic gzip streams.
use anyhow::{Context, Result, bail, ensure};
use libloading::Library;
use std::{
    ffi::{CStr, c_char, c_int, c_uint, c_ulong, c_void},
    fs::File,
    io::{self, Write},
    path::Path,
};

#[repr(C)]
struct Stream {
    next_in: *mut u8,
    avail_in: c_uint,
    total_in: c_ulong,
    next_out: *mut u8,
    avail_out: c_uint,
    total_out: c_ulong,
    msg: *mut c_char,
    state: *mut c_void,
    zalloc: Option<unsafe extern "C" fn(*mut c_void, c_uint, c_uint) -> *mut c_void>,
    zfree: Option<unsafe extern "C" fn(*mut c_void, *mut c_void)>,
    opaque: *mut c_void,
    data_type: c_int,
    adler: c_ulong,
    reserved: c_ulong,
}
type Deflate = unsafe extern "C" fn(*mut Stream, c_int) -> c_int;
type End = unsafe extern "C" fn(*mut Stream) -> c_int;
struct Api {
    _library: Library,
    deflate: Deflate,
    end: End,
    version: String,
}
fn library_name() -> String {
    if let Ok(path) = std::env::var("HSM_ZLIB_LIBRARY") {
        return path;
    }
    #[cfg(target_os = "macos")]
    {
        "/usr/lib/libz.1.dylib".into()
    }
    #[cfg(not(target_os = "macos"))]
    {
        "libz.so.1".into()
    }
}
impl Api {
    unsafe fn open() -> Result<Self> {
        let name = library_name();
        let library =
            unsafe { Library::new(&name) }.with_context(|| format!("loading zlib: {name}"))?;
        let deflate = unsafe { *library.get::<Deflate>(b"deflate\0")? };
        let end = unsafe { *library.get::<End>(b"deflateEnd\0")? };
        let version =
            unsafe { *library.get::<unsafe extern "C" fn() -> *const c_char>(b"zlibVersion\0")? };
        let version = unsafe { CStr::from_ptr(version()) }
            .to_string_lossy()
            .into_owned();
        Ok(Self {
            _library: library,
            deflate,
            end,
            version,
        })
    }
}
pub fn info() -> Result<serde_json::Value> {
    let api = unsafe { Api::open()? };
    Ok(serde_json::json!({"path":library_name(),"version":api.version}))
}
pub struct Gzip {
    api: Api,
    stream: Box<Stream>,
    file: File,
    crc: crc32fast::Hasher,
    count: u32,
    closed: bool,
}
impl Gzip {
    pub fn new(path: &Path, level: u32) -> Result<Self> {
        let mut file = File::create(path)?;
        let api = unsafe { Api::open()? };
        let mut stream = Box::new(unsafe { std::mem::zeroed::<Stream>() });
        let init = unsafe {
            *api._library.get::<unsafe extern "C" fn(
                *mut Stream,
                c_int,
                c_int,
                c_int,
                c_int,
                c_int,
                *const c_char,
                c_int,
            ) -> c_int>(b"deflateInit2_\0")?
        };
        let version = std::ffi::CString::new(api.version.clone())?;
        let status = unsafe {
            init(
                &mut *stream,
                level as c_int,
                8,
                -15,
                8,
                0,
                version.as_ptr(),
                std::mem::size_of::<Stream>() as c_int,
            )
        };
        ensure!(status == 0, "zlib deflate initialization returned {status}");
        let header = file.write_all(&[
            31,
            139,
            8,
            0,
            0,
            0,
            0,
            0,
            if level == 9 {
                2
            } else if level == 1 {
                4
            } else {
                0
            },
            255,
        ]);
        if let Err(error) = header {
            unsafe {
                (api.end)(&mut *stream);
            }
            return Err(error.into());
        }
        Ok(Self {
            api,
            stream,
            file,
            crc: crc32fast::Hasher::new(),
            count: 0,
            closed: false,
        })
    }
    fn compress(&mut self, data: &[u8]) -> io::Result<()> {
        for chunk in data.chunks(c_uint::MAX as usize) {
            self.stream.next_in = chunk.as_ptr() as *mut u8;
            self.stream.avail_in = chunk.len() as c_uint;
            while self.stream.avail_in > 0 {
                let status = self.pump(0)?;
                if status != 0 {
                    return Err(io::Error::other(format!("zlib deflate returned {status}")));
                }
            }
        }
        Ok(())
    }
    fn pump(&mut self, flush: c_int) -> io::Result<c_int> {
        let mut output = [0u8; 1 << 16];
        self.stream.next_out = output.as_mut_ptr();
        self.stream.avail_out = output.len() as c_uint;
        let status = unsafe { (self.api.deflate)(&mut *self.stream, flush) };
        let count = output.len() - self.stream.avail_out as usize;
        self.file.write_all(&output[..count])?;
        Ok(status)
    }
    pub fn finish(mut self) -> Result<()> {
        self.stream.next_in = std::ptr::null_mut();
        self.stream.avail_in = 0;
        loop {
            let status = self.pump(4)?;
            if status == 1 {
                break;
            }
            if status != 0 {
                bail!("zlib finish returned {status}");
            }
        }
        let crc = std::mem::replace(&mut self.crc, crc32fast::Hasher::new()).finalize();
        self.file.write_all(&crc.to_le_bytes())?;
        self.file.write_all(&self.count.to_le_bytes())?;
        let status = unsafe { (self.api.end)(&mut *self.stream) };
        self.closed = true;
        ensure!(status == 0, "zlib deflate end returned {status}");
        Ok(())
    }
}
impl Write for Gzip {
    fn write(&mut self, data: &[u8]) -> io::Result<usize> {
        self.compress(data)?;
        self.crc.update(data);
        self.count = self.count.wrapping_add(data.len() as u32);
        Ok(data.len())
    }
    fn flush(&mut self) -> io::Result<()> {
        self.file.flush()
    }
}
impl Drop for Gzip {
    fn drop(&mut self) {
        if !self.closed {
            unsafe {
                (self.api.end)(&mut *self.stream);
            }
        }
    }
}
