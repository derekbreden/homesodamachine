// The studio environment, baked as three.js r170's PMREMGenerator.fromScene(room, 0.03) bakes it:
// the room scene.js builds, seen from its centre, then each level a two-pass Gaussian of the one
// before, latitudinal about a pole and then longitudinal toward it (PMREMGenerator._halfBlur).
// Every level is a true cube here, so a texel's direction is the cube map's own.

struct Params {
  // The output face's edge in texels, the kernel's sample count, 1 for the latitudinal pass.
  size: u32,
  samples: u32,
  latitudinal: u32,
  pad: u32,
  pole: vec4<f32>,
  // x: radians between samples
  step: vec4<f32>,
  weights: array<vec4<f32>, 5>,
}

@group(0) @binding(0) var src_env: texture_cube<f32>;
@group(0) @binding(1) var bilinear: sampler;
@group(0) @binding(2) var dst_env: texture_storage_2d_array<rgba16float, write>;
@group(0) @binding(3) var<uniform> params: Params;

// scene.js ROOM_PANELS: lit boxes, each its own power, in a surround of SURROUND, on +Z-up axes.
const PANEL_SIZE = array<vec3<f32>, 5>(
  vec3<f32>(9.0, 7.0, 0.2), vec3<f32>(0.2, 8.0, 6.0), vec3<f32>(7.0, 0.2, 5.0),
  vec3<f32>(4.0, 0.2, 3.0), vec3<f32>(10.0, 10.0, 0.2),
);
const PANEL_AT = array<vec3<f32>, 5>(
  vec3<f32>(2.0, -3.0, 7.0), vec3<f32>(-7.0, 1.0, 0.0), vec3<f32>(1.0, -7.0, -1.0),
  vec3<f32>(-2.0, 6.0, 4.0), vec3<f32>(0.0, 0.0, -7.0),
);
const PANEL_POWER = array<f32, 5>(7.0, 3.0, 2.0, 4.0, 0.84);
const SURROUND: f32 = 0.14;

fn texel_direction(id: vec3<u32>, size: u32) -> vec3<f32> {
  let u = 2.0 * (f32(id.x) + 0.5) / f32(size) - 1.0;
  let v = 2.0 * (f32(id.y) + 0.5) / f32(size) - 1.0;
  switch id.z {
    case 0u: { return vec3<f32>(1.0, -v, -u); }
    case 1u: { return vec3<f32>(-1.0, -v, u); }
    case 2u: { return vec3<f32>(u, 1.0, v); }
    case 3u: { return vec3<f32>(u, -1.0, -v); }
    case 4u: { return vec3<f32>(u, -v, 1.0); }
    default: { return vec3<f32>(-u, -v, -1.0); }
  }
}

// What the room's centre sees along d: the nearest panel's power, or the surround.
fn room_radiance(d: vec3<f32>) -> f32 {
  var sizes = PANEL_SIZE;
  var ats = PANEL_AT;
  var powers = PANEL_POWER;
  var nearest = 1e30;
  var power = SURROUND;
  for (var i = 0u; i < 5u; i++) {
    let h = sizes[i] * 0.5;
    let lo = (ats[i] - h) / d;
    let hi = (ats[i] + h) / d;
    let t0 = min(lo, hi);
    let t1 = max(lo, hi);
    let enter = max(max(t0.x, t0.y), t0.z);
    let leave = min(min(t1.x, t1.y), t1.z);
    if (enter <= leave && enter > 0.0 && enter < nearest) {
      nearest = enter;
      power = powers[i];
    }
  }
  return power;
}

@compute @workgroup_size(8, 8, 1)
fn room(@builtin(global_invocation_id) id: vec3<u32>) {
  if (id.x >= params.size || id.y >= params.size) {
    return;
  }
  let p = room_radiance(texel_direction(id, params.size));
  textureStore(dst_env, vec2<i32>(id.xy), i32(id.z), vec4<f32>(p, p, p, 1.0));
}

// Rodrigues' rotation of v about a unit axis.
fn rotated(v: vec3<f32>, axis: vec3<f32>, theta: f32) -> vec3<f32> {
  let c = cos(theta);
  return v * c + cross(axis, v) * sin(theta) + axis * dot(axis, v) * (1.0 - c);
}

@compute @workgroup_size(8, 8, 1)
fn blur(@builtin(global_invocation_id) id: vec3<u32>) {
  if (id.x >= params.size || id.y >= params.size) {
    return;
  }
  let d = texel_direction(id, params.size);
  var axis = select(cross(params.pole.xyz, d), params.pole.xyz, params.latitudinal == 1u);
  if (all(axis == vec3<f32>(0.0))) {
    axis = vec3<f32>(d.z, 0.0, -d.x);
  }
  axis = normalize(axis);
  var sum = params.weights[0].x * textureSampleLevel(src_env, bilinear, d, 0.0).rgb;
  for (var i = 1u; i < params.samples; i++) {
    let w = params.weights[i / 4u][i % 4u];
    let theta = params.step.x * f32(i);
    sum += w * textureSampleLevel(src_env, bilinear, rotated(d, axis, -theta), 0.0).rgb;
    sum += w * textureSampleLevel(src_env, bilinear, rotated(d, axis, theta), 0.0).rgb;
  }
  textureStore(dst_env, vec2<i32>(id.xy), i32(id.z), vec4<f32>(sum, 1.0));
}
