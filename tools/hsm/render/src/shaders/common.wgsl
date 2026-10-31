// Shared by every draw: the frame, the materials, and the viewer's output transform
// (three.js r170: ACES filmic at exposure 0.6, sRGB encoding, then the fog mixed in sRGB).

struct View {
  view_proj: mat4x4<f32>,
  view: mat4x4<f32>,
  proj: mat4x4<f32>,
  // xyz the camera; w is 1 for a perspective camera, 0 for an orthographic one.
  eye: vec4<f32>,
  // Unit vector from the scene toward the camera.
  back: vec4<f32>,
  // width, height, near, far
  screen: vec4<f32>,
  // near, far, on
  fog: vec4<f32>,
  fog_color: vec4<f32>,
  // The contact shadow's centre (z is its height) and half extents.
  shadow_center: vec4<f32>,
  shadow_half: vec4<f32>,
  // Keep where dot(xyz, p) + w >= 0.
  clip: array<vec4<f32>, 8>,
  // x: clip planes in use, y: segments in the scene, z: meshes in the scene, w: the clip planes
  // the ground shadow is cut by too (the bands, ahead of a section's plane)
  counts: vec4<u32>,
}

struct Material {
  // Linear RGB and opacity.
  color: vec4<f32>,
  // roughness, metalness, line width in pixels, back-face darkening
  params: vec4<f32>,
  // x: flag bits below
  flags: vec4<u32>,
}

const UNLIT: u32 = 1u;
const FRONT_ONLY: u32 = 2u;
const BACK_ONLY: u32 = 4u;
const NO_FOG: u32 = 8u;

struct Segment {
  a: vec3<f32>,
  mesh: u32,
  b: vec3<f32>,
  pad: u32,
}

@group(0) @binding(0) var<uniform> view: View;
@group(0) @binding(1) var<storage, read> materials: array<Material>;
@group(0) @binding(2) var env_main: texture_cube<f32>;
@group(0) @binding(3) var env_extra: texture_cube_array<f32>;
@group(0) @binding(4) var linear_clamp: sampler;
@group(0) @binding(5) var<storage, read> segments: array<Segment>;
@group(0) @binding(6) var<storage, read> edge_slot: array<u32>;
@group(0) @binding(7) var shadow_map: texture_2d<f32>;

const PI: f32 = 3.141592653589793;

// Cut away by one of the first `planes` clip planes.
fn clipped_by(p: vec3<f32>, planes: u32) -> bool {
  for (var i = 0u; i < planes; i++) {
    let c = view.clip[i];
    if (dot(c.xyz, p) + c.w < 0.0) {
      return true;
    }
  }
  return false;
}

fn clipped(p: vec3<f32>) -> bool {
  return clipped_by(p, view.counts.x);
}

fn rrt_and_odt_fit(v: vec3<f32>) -> vec3<f32> {
  let a = v * (v + 0.0245786) - 0.000090537;
  let b = v * (0.983729 * v + 0.4329510) + 0.238081;
  return a / b;
}

// ACESFilmicToneMapping at toneMappingExposure 0.6, which the curve divides back out to 1.
fn tone_map(c: vec3<f32>) -> vec3<f32> {
  let aces_in = mat3x3<f32>(
    vec3<f32>(0.59719, 0.07600, 0.02840),
    vec3<f32>(0.35458, 0.90834, 0.13383),
    vec3<f32>(0.04823, 0.01566, 0.83777),
  );
  let aces_out = mat3x3<f32>(
    vec3<f32>(1.60475, -0.10208, -0.00327),
    vec3<f32>(-0.53108, 1.10813, -0.07276),
    vec3<f32>(-0.07367, -0.00605, 1.07602),
  );
  var color = aces_in * c;
  color = rrt_and_odt_fit(color);
  color = aces_out * color;
  return clamp(color, vec3<f32>(0.0), vec3<f32>(1.0));
}

fn srgb(c: vec3<f32>) -> vec3<f32> {
  let lo = c * 12.92;
  let hi = pow(c, vec3<f32>(0.41666)) * 1.055 - vec3<f32>(0.055);
  return select(hi, lo, c <= vec3<f32>(0.0031308));
}

// three's Fog: smoothstep between near and far on view depth, mixed after encoding.
fn fogged(color: vec3<f32>, depth: f32) -> vec3<f32> {
  if (view.fog.z < 0.5) {
    return color;
  }
  let f = smoothstep(view.fog.x, view.fog.y, depth);
  return mix(color, view.fog_color.rgb, f);
}
