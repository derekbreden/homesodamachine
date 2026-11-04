//! The retained GEOS planar union/simplification/miter-buffer primitive.
//!
//! The explicit HSM_GEOS_LIBRARY path overrides the installed library. The
//! default is the GEOS shipped with this checkout's pinned CAD runtime.
use crate::shell_dimensions::Dimensions;
use anyhow::{Context, Result, bail};
use libloading::Library;
use std::ffi::{CStr, CString, c_char, c_int, c_uint, c_void};
use std::path::{Path, PathBuf};
type Ptr = *mut c_void;

pub fn library_path() -> Result<PathBuf> {
    if let Some(path) = std::env::var_os("HSM_GEOS_LIBRARY") {
        return Ok(PathBuf::from(path));
    }
    let root = std::env::var_os("HSM_WORKSPACE")
        .map(PathBuf::from)
        .unwrap_or(std::env::current_dir()?);
    let runtime = root.join("tools/cad-venv/lib");
    if let Ok(dirs) = std::fs::read_dir(runtime) {
        for dir in dirs.flatten() {
            let site = dir.path().join("site-packages");
            for directory in [
                site.join("shapely/.dylibs"),
                site.join("shapely.libs"),
                site.join("shapely/.libs"),
            ] {
                if let Ok(files) = std::fs::read_dir(directory) {
                    for file in files.flatten() {
                        let name = file.file_name().to_string_lossy().into_owned();
                        if name.starts_with("libgeos_c")
                            && (name.ends_with(".dylib") || name.contains(".so"))
                        {
                            return Ok(file.path());
                        }
                    }
                }
            }
        }
    }
    bail!(
        "Set HSM_GEOS_LIBRARY to the GEOS C library, or install the checkout's pinned CAD runtime"
    )
}
struct Api {
    library: Library,
    context: Ptr,
}
impl Api {
    fn new() -> Result<Self> {
        let path = library_path()?;
        unsafe {
            let library =
                Library::new(&path).with_context(|| format!("loading {}", path.display()))?;
            let init: unsafe extern "C" fn() -> Ptr = *library.get(b"GEOS_init_r\0")?;
            let context = init();
            if context.is_null() {
                bail!("GEOS context allocation failed");
            }
            Ok(Self { library, context })
        }
    }
    unsafe fn symbol<T: Copy>(&self, name: &[u8]) -> Result<T> {
        Ok(*unsafe { self.library.get::<T>(name) }?)
    }
    fn geom(&self, ptr: Ptr) -> Result<Geom<'_>> {
        if ptr.is_null() {
            bail!("GEOS planar operation failed");
        }
        Ok(Geom { api: self, ptr })
    }
    fn polygon(&self, points: &[[f64; 2]]) -> Result<Geom<'_>> {
        let mut pts = points.to_vec();
        if pts.first() != pts.last() {
            pts.push(pts[0]);
        }
        let wkt = format!(
            "POLYGON (({}))",
            pts.iter()
                .map(|p| format!("{} {}", p[0], p[1]))
                .collect::<Vec<_>>()
                .join(",")
        );
        let text = CString::new(wkt)?;
        unsafe {
            let create: unsafe extern "C" fn(Ptr) -> Ptr =
                self.symbol(b"GEOSWKTReader_create_r\0")?;
            let read: unsafe extern "C" fn(Ptr, Ptr, *const c_char) -> Ptr =
                self.symbol(b"GEOSWKTReader_read_r\0")?;
            let destroy: unsafe extern "C" fn(Ptr, Ptr) =
                self.symbol(b"GEOSWKTReader_destroy_r\0")?;
            let reader = create(self.context);
            let ptr = read(self.context, reader, text.as_ptr());
            destroy(self.context, reader);
            self.geom(ptr)
        }
    }
    fn union_all<'a>(&'a self, regions: Vec<Geom<'a>>) -> Result<Geom<'a>> {
        unsafe {
            let collection: unsafe extern "C" fn(Ptr, c_int, *mut Ptr, c_uint) -> Ptr =
                self.symbol(b"GEOSGeom_createCollection_r\0")?;
            let union: unsafe extern "C" fn(Ptr, Ptr) -> Ptr =
                self.symbol(b"GEOSUnaryUnion_r\0")?;
            let mut pointers: Vec<_> = regions.iter().map(|g| g.ptr).collect();
            let ptr = collection(
                self.context,
                7,
                pointers.as_mut_ptr(),
                pointers.len() as c_uint,
            );
            if ptr.is_null() {
                bail!("GEOS geometry collection failed");
            }
            for region in regions {
                std::mem::forget(region);
            }
            let geometry = self.geom(ptr)?;
            self.geom(union(self.context, geometry.ptr))
        }
    }
    fn version(&self) -> Result<String> {
        unsafe {
            let f: unsafe extern "C" fn() -> *const c_char = self.symbol(b"GEOSversion\0")?;
            Ok(CStr::from_ptr(f()).to_string_lossy().into_owned())
        }
    }
}
impl Drop for Api {
    fn drop(&mut self) {
        unsafe {
            if let Ok(f) = self
                .library
                .get::<unsafe extern "C" fn(Ptr)>(b"GEOS_finish_r\0")
            {
                f(self.context);
            }
        }
    }
}
struct Geom<'a> {
    api: &'a Api,
    ptr: Ptr,
}
impl Geom<'_> {
    fn buffer(&self, d: f64) -> Result<Geom<'_>> {
        unsafe {
            let f: unsafe extern "C" fn(Ptr, Ptr, f64, c_int, c_int, c_int, f64) -> Ptr =
                self.api.symbol(b"GEOSBufferWithStyle_r\0")?;
            self.api
                .geom(f(self.api.context, self.ptr, d, 16, 1, 2, 5.0))
        }
    }
    fn simplify(&self, t: f64) -> Result<Geom<'_>> {
        unsafe {
            let f: unsafe extern "C" fn(Ptr, Ptr, f64) -> Ptr =
                self.api.symbol(b"GEOSTopologyPreserveSimplify_r\0")?;
            self.api.geom(f(self.api.context, self.ptr, t))
        }
    }
    fn union(&self, other: &Geom) -> Result<Geom<'_>> {
        unsafe {
            let f: unsafe extern "C" fn(Ptr, Ptr, Ptr) -> Ptr =
                self.api.symbol(b"GEOSUnion_r\0")?;
            self.api.geom(f(self.api.context, self.ptr, other.ptr))
        }
    }
    fn exterior(&self) -> Result<Vec<[f64; 2]>> {
        unsafe {
            let ring: unsafe extern "C" fn(Ptr, Ptr) -> Ptr =
                self.api.symbol(b"GEOSGetExteriorRing_r\0")?;
            let seq: unsafe extern "C" fn(Ptr, Ptr) -> Ptr =
                self.api.symbol(b"GEOSGeom_getCoordSeq_r\0")?;
            let size: unsafe extern "C" fn(Ptr, Ptr, *mut c_uint) -> c_int =
                self.api.symbol(b"GEOSCoordSeq_getSize_r\0")?;
            let x: unsafe extern "C" fn(Ptr, Ptr, c_uint, *mut f64) -> c_int =
                self.api.symbol(b"GEOSCoordSeq_getX_r\0")?;
            let y: unsafe extern "C" fn(Ptr, Ptr, c_uint, *mut f64) -> c_int =
                self.api.symbol(b"GEOSCoordSeq_getY_r\0")?;
            let ring = ring(self.api.context, self.ptr);
            if ring.is_null() {
                bail!("lever sweep must have one polygon exterior");
            }
            let seq = seq(self.api.context, ring);
            let mut count = 0;
            if size(self.api.context, seq, &mut count) == 0 {
                bail!("GEOS exterior has no coordinate sequence");
            }
            let mut out = vec![];
            for i in 0..count - 1 {
                let (mut px, mut py) = (0.0, 0.0);
                if x(self.api.context, seq, i, &mut px) == 0
                    || y(self.api.context, seq, i, &mut py) == 0
                {
                    bail!("GEOS exterior coordinate failed");
                }
                out.push([px, py]);
            }
            Ok(out)
        }
    }
}
impl Drop for Geom<'_> {
    fn drop(&mut self) {
        unsafe {
            if let Ok(f) = self
                .api
                .symbol::<unsafe extern "C" fn(Ptr, Ptr)>(b"GEOSGeom_destroy_r\0")
            {
                f(self.api.context, self.ptr);
            }
        }
    }
}
pub fn lever_outline(d: &Dimensions) -> Result<Vec<[f64; 2]>> {
    let api = Api::new()?;
    let profile = [
        [-42.0, d.zone2_z_top + 10.0],
        [-42.0, d.lever_rest_top_z],
        [d.lever_rest_back_y, d.lever_rest_top_z],
        [d.lever_rest_back_y, d.zone2_z_top + 1.0],
        [-6.0, d.zone2_z_top + 1.0],
        [-6.0, d.zone2_z_top + 4.5],
    ];
    let (py, pz) = (1.5, d.zone2_z_top + 7.0);
    let poses: Vec<Vec<_>> = (0..=18)
        .map(|angle| {
            let a = angle as f64 * (std::f64::consts::PI / 180.0);
            let (c, s) = (a.cos(), a.sin());
            profile
                .iter()
                .map(|[y, z]| {
                    [
                        py + c * (y - py) - s * (z - pz),
                        pz + s * (y - py) + c * (z - pz),
                    ]
                })
                .collect()
        })
        .collect();
    let rect = |a: f64, b: f64, c: f64, e: f64| api.polygon(&[[c, b], [c, e], [a, e], [a, b]]);
    let mut regions = vec![];
    for pose in &poses {
        regions.push(api.polygon(pose)?);
    }
    regions.push(rect(
        d.lever_insertion_front_y,
        d.zone2_z_top + 1.0,
        -5.9,
        d.lever_rest_top_z,
    )?);
    for w in poses.windows(2) {
        for i in 0..profile.len() {
            let j = (i + 1) % profile.len();
            let polygon = api.polygon(&[w[0][i], w[0][j], w[1][j], w[1][i]])?;
            let buffered = polygon.buffer(0.0)?;
            regions.push(api.geom(buffered.ptr)?);
            std::mem::forget(buffered);
        }
    }
    let united = api.union_all(regions)?;
    let simplified = united.simplify(0.001)?;
    let grown = simplified.buffer(d.lever_fit_clearance + d.lever_sweep_allowance)?;
    let plateau = rect(
        -d.westbrass_bore_rect_long_y / 2.0,
        d.zone2_z_top - 0.01,
        d.fill_y_min,
        d.lever_rest_top_z,
    )?;
    grown.union(&plateau)?.exterior()
}
pub fn info() -> Result<serde_json::Value> {
    let api = Api::new()?;
    Ok(serde_json::json!({"path":library_path()?.display().to_string(),"version":api.version()?}))
}
