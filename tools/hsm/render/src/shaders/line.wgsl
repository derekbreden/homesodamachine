// Feature edges: three.js r170's LineMaterial (examples/jsm/lines), lines a fixed number of
// pixels wide with round caps, their soft edge turned into coverage (alphaToCoverage), unlit and
// tone-mapped. A segment is one instance of LineSegmentsGeometry's quad.

// The quad: its body runs y 0..1 along the segment, and a cap stands past each end.
const LINE_POS = array<vec2<f32>, 8>(
  vec2<f32>(-1.0, 2.0), vec2<f32>(1.0, 2.0), vec2<f32>(-1.0, 1.0), vec2<f32>(1.0, 1.0),
  vec2<f32>(-1.0, 0.0), vec2<f32>(1.0, 0.0), vec2<f32>(-1.0, -1.0), vec2<f32>(1.0, -1.0),
);
const LINE_UV = array<vec2<f32>, 8>(
  vec2<f32>(-1.0, 2.0), vec2<f32>(1.0, 2.0), vec2<f32>(-1.0, 1.0), vec2<f32>(1.0, 1.0),
  vec2<f32>(-1.0, -1.0), vec2<f32>(1.0, -1.0), vec2<f32>(-1.0, -2.0), vec2<f32>(1.0, -2.0),
);
const LINE_INDEX = array<u32, 18>(0u, 2u, 1u, 2u, 3u, 1u, 2u, 4u, 3u, 4u, 5u, 3u, 4u, 6u, 5u, 6u, 7u, 5u);

struct LineOut {
  @builtin(position) clip: vec4<f32>,
  @location(0) uv: vec2<f32>,
  @location(1) world: vec3<f32>,
  @location(2) @interpolate(flat) slot: u32,
  @location(3) depth: f32,
}

// An end behind the camera is pulled back to between the camera and the near plane, where
// three's conservative estimate of the near plane puts it.
fn trim_segment(start: vec4<f32>, end: vec4<f32>) -> vec4<f32> {
  let n = view.screen.z;
  let f = view.screen.w;
  let near_estimate = -(n * f) / (f + n);
  let alpha = (near_estimate - start.z) / (end.z - start.z);
  return vec4<f32>(mix(start.xyz, end.xyz, alpha), end.w);
}

// Each mesh's segments are drawn as one instance range. An instance past the last segment of the
// scene draws that segment again with its mesh's material from the next bank of `edge_slot`,
// which is how one edge carries both its own colour and the selection's.
@vertex
fn vs_line(@builtin(vertex_index) vi: u32, @builtin(instance_index) instance: u32) -> LineOut {
  var index = LINE_INDEX;
  var positions = LINE_POS;
  var uvs = LINE_UV;
  let corner = index[vi];
  let position = positions[corner];
  let total = view.counts.y;
  let bank = instance / total;
  let seg = segments[instance - bank * total];
  let slot = edge_slot[bank * view.counts.z + seg.mesh];
  let m = materials[slot];

  var start = view.view * vec4<f32>(seg.a, 1.0);
  var end = view.view * vec4<f32>(seg.b, 1.0);
  if (view.eye.w > 0.5) {
    if (start.z < 0.0 && end.z >= 0.0) {
      end = trim_segment(start, end);
    } else if (end.z < 0.0 && start.z >= 0.0) {
      start = trim_segment(end, start);
    }
  }
  let clip_start = view.proj * start;
  let clip_end = view.proj * end;
  let ndc_start = clip_start.xyz / clip_start.w;
  let ndc_end = clip_end.xyz / clip_end.w;

  // The offset is worked in a square space and handed back to the frame's aspect.
  let aspect = view.screen.x / view.screen.y;
  var dir = ndc_end.xy - ndc_start.xy;
  dir.x *= aspect;
  let len = length(dir);
  dir = select(vec2<f32>(1.0, 0.0), dir / len, len > 1e-12);
  var offset = vec2<f32>(dir.y, -dir.x);
  dir.x /= aspect;
  offset.x /= aspect;
  if (position.x < 0.0) {
    offset = -offset;
  }
  if (position.y < 0.0) {
    offset -= dir;
  } else if (position.y > 1.0) {
    offset += dir;
  }
  offset *= m.params.z;
  offset /= view.screen.y;
  let at_start = position.y < 0.5;
  var clip = select(clip_end, clip_start, at_start);
  offset *= clip.w;
  clip = vec4<f32>(clip.xy + offset, clip.zw);

  var o: LineOut;
  o.clip = clip;
  o.uv = uvs[corner];
  o.world = select(seg.b, seg.a, at_start);
  o.slot = slot;
  o.depth = -select(end.z, start.z, at_start);
  return o;
}

@fragment
fn fs_line(in: LineOut) -> @location(0) vec4<f32> {
  // The cap's edge, softened over one pixel by its derivative, taken while every lane still runs.
  let a = in.uv.x;
  let b = select(in.uv.y + 1.0, in.uv.y - 1.0, in.uv.y > 0.0);
  let len2 = a * a + b * b;
  let dlen = fwidth(len2);

  let m = materials[in.slot];
  let flags = m.flags.x;
  if (clipped(in.world)) {
    discard;
  }
  var alpha = m.color.a;
  if (abs(in.uv.y) > 1.0) {
    alpha *= 1.0 - smoothstep(1.0 - dlen, 1.0 + dlen, len2);
  }
  var color = srgb(tone_map(m.color.rgb));
  if ((flags & NO_FOG) == 0u) {
    color = fogged(color, in.depth);
  }
  return vec4<f32>(color, alpha);
}
