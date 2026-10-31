// A solid's faces: three.js r170 MeshStandardMaterial under the viewer's studio rig
// (web/public/js/viewer/scene.js addStudioLighting), double-sided with its back faces darkened.

// The rig, on the scene's own +Z-up axes. Directions point toward the light.
const KEY_DIR: vec3<f32> = vec3<f32>(0.40160966, -0.48193159, 0.80321932);
const KEY: f32 = 1.1;
const FILL_DIR: vec3<f32> = vec3<f32>(-0.81274932, 0.54183288, 0.20318733);
const FILL: f32 = 0.3;
const AMBIENT: f32 = 0.12;
const HEMI: f32 = 0.35;
// 0x333340, decoded to linear.
const HEMI_GROUND: vec3<f32> = vec3<f32>(0.03310477, 0.03310477, 0.05126946);

struct VsIn {
  @location(0) position: vec3<f32>,
  @location(1) normal: vec3<f32>,
}

struct VsOut {
  @builtin(position) clip: vec4<f32>,
  @location(0) world: vec3<f32>,
  @location(1) normal: vec3<f32>,
  @location(2) @interpolate(flat) slot: u32,
  @location(3) depth: f32,
}

@vertex
fn vs_surface(v: VsIn, @builtin(instance_index) slot: u32) -> VsOut {
  var o: VsOut;
  o.clip = view.view_proj * vec4<f32>(v.position, 1.0);
  o.world = v.position;
  o.normal = v.normal;
  o.slot = slot;
  o.depth = -(view.view * vec4<f32>(v.position, 1.0)).z;
  return o;
}

// cube_uv_reflection_fragment: roughness to the PMREM's mip, where 8 is the sharp 256² level
// and -2 the last of the six blurred 16² levels.
fn roughness_to_mip(r: f32) -> f32 {
  if (r >= 0.8) {
    return (1.0 - r) * (-1.0 - -2.0) / (1.0 - 0.8) + -2.0;
  } else if (r >= 0.4) {
    return (0.8 - r) * (2.0 - -1.0) / (0.8 - 0.4) + -1.0;
  } else if (r >= 0.305) {
    return (0.4 - r) * (3.0 - 2.0) / (0.4 - 0.305) + 2.0;
  } else if (r >= 0.21) {
    return (0.305 - r) * (4.0 - 3.0) / (0.305 - 0.21) + 3.0;
  }
  return -2.0 * log2(1.16 * r);
}

fn env_at(dir: vec3<f32>, mip: f32) -> vec3<f32> {
  let level = 8.0 - mip;
  if (level <= 4.0) {
    return textureSampleLevel(env_main, linear_clamp, dir, level).rgb;
  }
  return textureSampleLevel(env_extra, linear_clamp, dir, i32(level) - 5, 0.0).rgb;
}

fn env_lookup(dir: vec3<f32>, roughness: f32) -> vec3<f32> {
  let mip = clamp(roughness_to_mip(roughness), -2.0, 8.0);
  let f = fract(mip);
  let i = floor(mip);
  let c0 = env_at(dir, i);
  if (f == 0.0) {
    return c0;
  }
  return mix(c0, env_at(dir, i + 1.0), f);
}

fn f_schlick(f0: vec3<f32>, f90: f32, dot_vh: f32) -> vec3<f32> {
  let fresnel = exp2((-5.55473 * dot_vh - 6.98316) * dot_vh);
  return f0 * (1.0 - fresnel) + (f90 * fresnel);
}

fn brdf_ggx(l: vec3<f32>, v: vec3<f32>, n: vec3<f32>, f0: vec3<f32>, roughness: f32) -> vec3<f32> {
  let alpha = roughness * roughness;
  let h = normalize(l + v);
  let dot_nl = clamp(dot(n, l), 0.0, 1.0);
  let dot_nv = clamp(dot(n, v), 0.0, 1.0);
  let dot_nh = clamp(dot(n, h), 0.0, 1.0);
  let dot_vh = clamp(dot(v, h), 0.0, 1.0);
  let f = f_schlick(f0, 1.0, dot_vh);
  let a2 = alpha * alpha;
  let gv = dot_nl * sqrt(a2 + (1.0 - a2) * dot_nv * dot_nv);
  let gl = dot_nv * sqrt(a2 + (1.0 - a2) * dot_nl * dot_nl);
  let vis = 0.5 / max(gv + gl, 1e-6);
  let denom = dot_nh * dot_nh * (a2 - 1.0) + 1.0;
  let d = a2 / (PI * denom * denom);
  return f * (vis * d);
}

fn dfg_approx(n: vec3<f32>, v: vec3<f32>, roughness: f32) -> vec2<f32> {
  let dot_nv = clamp(dot(n, v), 0.0, 1.0);
  let c0 = vec4<f32>(-1.0, -0.0275, -0.572, 0.022);
  let c1 = vec4<f32>(1.0, 0.0425, 1.04, -0.04);
  let r = roughness * c0 + c1;
  let a004 = min(r.x * r.x, exp2(-9.28 * dot_nv)) * r.x + r.y;
  return vec2<f32>(-1.04, 1.04) * a004 + r.zw;
}

fn standard(m: Material, base: vec3<f32>, n: vec3<f32>, v: vec3<f32>, geometry_roughness: f32) -> vec3<f32> {
  let metal = m.params.y;
  let diffuse = base * (1.0 - metal);
  let f0 = mix(vec3<f32>(0.04), base, metal);
  let roughness = min(max(m.params.x, 0.0525) + geometry_roughness, 1.0);

  var direct_diffuse = vec3<f32>(0.0);
  var direct_specular = vec3<f32>(0.0);
  let dirs = array<vec3<f32>, 2>(KEY_DIR, FILL_DIR);
  let powers = array<f32, 2>(KEY, FILL);
  for (var i = 0; i < 2; i++) {
    let l = dirs[i];
    let irradiance = clamp(dot(n, l), 0.0, 1.0) * powers[i];
    direct_diffuse += irradiance * diffuse / PI;
    direct_specular += irradiance * brdf_ggx(l, v, n, f0, roughness);
  }

  // Ambient and hemisphere, through Lambert.
  let w = 0.5 * n.z + 0.5;
  let flat_irradiance = vec3<f32>(AMBIENT) + mix(HEMI_GROUND, vec3<f32>(1.0), w) * HEMI;
  var indirect_diffuse = flat_irradiance * diffuse / PI;

  // The studio environment: irradiance off the roughest level, radiance off the reflection.
  let ibl_irradiance = PI * env_lookup(n, 1.0);
  let r = normalize(mix(reflect(-v, n), n, roughness * roughness));
  let radiance = env_lookup(r, roughness);
  let fab = dfg_approx(n, v, roughness);
  let fss_ess = f0 * fab.x + vec3<f32>(fab.y);
  let ess = fab.x + fab.y;
  let ems = 1.0 - ess;
  let favg = f0 + (vec3<f32>(1.0) - f0) * 0.047619;
  let fms = fss_ess * favg / (vec3<f32>(1.0) - ems * favg);
  let single = fss_ess;
  let multi = fms * ems;
  let total = single + multi;
  let cosine_weighted = ibl_irradiance / PI;
  let indirect_specular = radiance * single + multi * cosine_weighted;
  indirect_diffuse += diffuse * (1.0 - max(max(total.r, total.g), total.b)) * cosine_weighted;

  return direct_diffuse + indirect_diffuse + direct_specular + indirect_specular;
}

@fragment
fn fs_surface(in: VsOut, @builtin(front_facing) front: bool) -> @location(0) vec4<f32> {
  // Derivatives first, while every lane of the quad is still running.
  let facing = select(-1.0, 1.0, front);
  let dwx = dpdx(in.world);
  let dwy = dpdy(in.world);
  var n = in.normal;
  let len = length(n);
  let geometric = normalize(cross(dwx, dwy));
  n = select(geometric * facing, n / len * facing, len > 1e-12);
  let n_view = (view.view * vec4<f32>(n, 0.0)).xyz;
  let dxy = max(abs(dpdx(n_view)), abs(dpdy(n_view)));
  let geometry_roughness = max(max(dxy.x, dxy.y), dxy.z);

  let m = materials[in.slot];
  let flags = m.flags.x;
  if (clipped(in.world)) {
    discard;
  }
  if ((flags & FRONT_ONLY) != 0u && !front) {
    discard;
  }
  if ((flags & BACK_ONLY) != 0u && front) {
    discard;
  }

  var color: vec3<f32>;
  if ((flags & UNLIT) != 0u) {
    color = m.color.rgb;
  } else {
    let base = m.color.rgb * select(m.params.w, 1.0, front);
    var v = view.back.xyz;
    if (view.eye.w > 0.5) {
      v = normalize(view.eye.xyz - in.world);
    }
    color = standard(m, base, n, v, geometry_roughness);
  }
  var out = srgb(tone_map(color));
  if ((flags & NO_FOG) == 0u) {
    out = fogged(out, in.depth);
  }
  return vec4<f32>(out, m.color.a);
}
