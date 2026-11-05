//! `manifold-layout/above_core.py`, the production above-core placements, as the typed
//! recipes read it. Its specification is copied out of the Python process once; frame
//! arithmetic stays with the provider, which answers through `_layout_data`.

use super::*;

pub struct AboveCore {
    pub module: Val,
    spec: Val,
}

impl Module for AboveCore {
    const NAME: &'static str = "above_core";
    fn init(rt: &Runtime) -> Result<Self> {
        let module = rt.py("above_core")?;
        let spec = own(&module.m("specification", vec![])?)?;
        Ok(Self { module, spec })
    }
}

impl AboveCore {
    pub fn get(rt: &Runtime) -> Result<Rc<Self>> {
        rt.state::<Self>()
    }
    /// `specification()`.
    pub fn spec(&self) -> &Val {
        &self.spec
    }
    /// `specification()['cap_face_z_mm']`.
    pub fn cap_face_z(&self) -> Result<f64> {
        self.spec.kf("cap_face_z_mm")
    }
    /// `pose(name)`.
    pub fn pose(&self, name: &str) -> Result<Val> {
        self.spec.k("parts")?.k(name)
    }
    /// `snapshot_pose(name)`.
    pub fn snapshot_pose(&self, name: &str) -> Result<Val> {
        self.spec.k("snapshots")?.k(name)
    }
    /// `cap_lid_pose()`.
    pub fn cap_lid_pose(&self) -> Result<Val> {
        self.spec.k("cap_lid_pose")
    }
    /// `point(frame, xyz)`.
    pub fn point(&self, frame: &Val, xyz: impl ToVal) -> Result<[f64; 3]> {
        self.module.m("point", args![frame, xyz])?.v3()
    }
    /// `vector(rotation, point)`.
    pub fn vector(&self, rotation: &Val, xyz: impl ToVal) -> Result<[f64; 3]> {
        self.module.m("vector", args![rotation, xyz])?.v3()
    }
    /// `inverse_point(frame, xyz)`.
    pub fn inverse_point(&self, frame: &Val, xyz: impl ToVal) -> Result<[f64; 3]> {
        self.module.m("inverse_point", args![frame, xyz])?.v3()
    }
    /// `world_to_cap(xyz)`.
    pub fn world_to_cap(&self, xyz: impl ToVal) -> Result<[f64; 3]> {
        self.module.m("world_to_cap", args![xyz])?.v3()
    }
    /// `frame_location(frame)`: a CadQuery location.
    pub fn frame_location(&self, frame: &Val) -> Result<Val> {
        self.module.m("frame_location", args![frame])
    }
    /// `location(name)`.
    pub fn location(&self, name: &str) -> Result<Val> {
        self.module.m("location", args![name])
    }
}
