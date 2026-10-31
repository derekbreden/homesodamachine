// The contact shadow (scene.js fitGroundShadow): one quad a hair under the model's floor carrying
// the falloff shadow.rs draws, black over whatever stands behind it, never fogged, seen from
// above only, and cut by the clip bands as everything in the scene is.

struct ShadowOut {
  @builtin(position) clip: vec4<f32>,
  @location(0) uv: vec2<f32>,
  @location(1) world: vec3<f32>,
}

@vertex
fn vs_shadow(@builtin(vertex_index) vi: u32) -> ShadowOut {
  var corners = array<vec2<f32>, 6>(
    vec2<f32>(-1.0, -1.0), vec2<f32>(1.0, -1.0), vec2<f32>(1.0, 1.0),
    vec2<f32>(-1.0, -1.0), vec2<f32>(1.0, 1.0), vec2<f32>(-1.0, 1.0),
  );
  let c = corners[vi];
  let p = view.shadow_center.xyz + vec3<f32>(c * view.shadow_half.xy, 0.0);
  var o: ShadowOut;
  o.clip = view.view_proj * vec4<f32>(p, 1.0);
  // The canvas's first row is the quad's +Y edge.
  o.uv = vec2<f32>(0.5 + 0.5 * c.x, 0.5 - 0.5 * c.y);
  o.world = p;
  return o;
}

@fragment
fn fs_shadow(in: ShadowOut, @builtin(front_facing) front: bool) -> @location(0) vec4<f32> {
  let a = textureSample(shadow_map, linear_clamp, in.uv).r;
  if (!front || clipped_by(in.world, view.counts.w)) {
    discard;
  }
  return vec4<f32>(0.0, 0.0, 0.0, a);
}
