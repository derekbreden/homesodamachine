// Rasterize the actual surfaces of each hidden component into its small restore button.
let side, light, pixels, depth;

function project(positions, m) {
  const screen = new Float32Array(positions.length);
  for (let i = 0; i < positions.length; i += 3) {
    const x = positions[i], y = positions[i + 1], z = positions[i + 2];
    const w = m[3]*x + m[7]*y + m[11]*z + m[15];
    screen[i] = (1 + (m[0]*x + m[4]*y + m[8]*z + m[12]) / w) * side / 2;
    screen[i + 1] = (1 - (m[1]*x + m[5]*y + m[9]*z + m[13]) / w) * side / 2;
    screen[i + 2] = (m[2]*x + m[6]*y + m[10]*z + m[14]) / w;
  }
  return screen;
}

function lighting(p, a, b, c, normal, backFace) {
  const ux = p[b] - p[a], uy = p[b+1] - p[a+1], uz = p[b+2] - p[a+2];
  const vx = p[c] - p[a], vy = p[c+1] - p[a+1], vz = p[c+2] - p[a+2];
  const nx = uy*vz - uz*vy, ny = uz*vx - ux*vz, nz = ux*vy - uy*vx;
  const x = normal[0]*nx + normal[3]*ny + normal[6]*nz;
  const y = normal[1]*nx + normal[4]*ny + normal[7]*nz;
  const z = normal[2]*nx + normal[5]*ny + normal[8]*nz;
  const length = Math.sqrt(x*x + y*y + z*z) || 1;
  const toward = (x*light[0] + y*light[1] + z*light[2]) / length;
  return Math.max(0, backFace ? -toward : toward);
}

function draw({ positions, indices, transform, normal, mirrored, color, metalness }) {
  const screen = project(positions, transform);
  const red = color >> 16, green = color >> 8 & 255, blue = color & 255;
  const count = indices?.length ?? positions.length / 3;
  for (let i = 0; i < count; i += 3) {
    const a = 3*(indices ? indices[i] : i);
    const b = 3*(indices ? indices[i+1] : i+1);
    const c = 3*(indices ? indices[i+2] : i+2);
    const ax = screen[a], ay = screen[a+1], bx = screen[b], by = screen[b+1], cx = screen[c], cy = screen[c+1];
    const xmin = Math.max(0, Math.ceil(Math.min(ax, bx, cx) - 0.5));
    const xmax = Math.min(side - 1, Math.floor(Math.max(ax, bx, cx) - 0.5));
    const ymin = Math.max(0, Math.ceil(Math.min(ay, by, cy) - 0.5));
    const ymax = Math.min(side - 1, Math.floor(Math.max(ay, by, cy) - 0.5));
    if (xmin > xmax || ymin > ymax) continue;
    const area = (bx-ax)*(cy-ay) - (by-ay)*(cx-ax);
    if (!area) continue;
    const diffuse = lighting(positions, a, b, c, normal, (area > 0) !== mirrored);
    const shade = 0.54 + 0.72 * diffuse;
    const specular = (70 + 45*metalness) * diffuse**2;
    const r = red*shade + specular, g = green*shade + specular, bl = blue*shade + specular;
    for (let y = ymin; y <= ymax; y++) {
      for (let x = xmin; x <= xmax; x++) {
        const px = x + 0.5 - ax, py = y + 0.5 - ay;
        const u = (px*(cy-ay) - py*(cx-ax)) / area;
        const v = ((bx-ax)*py - (by-ay)*px) / area;
        if (u < 0 || v < 0 || u + v > 1) continue;
        const z = screen[a+2] + u*(screen[b+2]-screen[a+2]) + v*(screen[c+2]-screen[a+2]);
        const at = y*side + x;
        if (z >= depth[at]) continue;
        depth[at] = z;
        pixels[at*4] = r; pixels[at*4+1] = g; pixels[at*4+2] = bl;
      }
    }
  }
}

self.onmessage = ({ data }) => {
  if (data.begin) {
    side = data.begin;
    light = data.light;
    depth = new Float32Array(side*side).fill(Infinity);
    pixels = new Uint8ClampedArray(side*side*4);
    for (let i = 0; i < pixels.length; i += 4) {
      pixels[i] = 230; pixels[i+1] = 236; pixels[i+2] = 245; pixels[i+3] = 255;
    }
  } else if (data.finish) {
    self.postMessage(pixels, [pixels.buffer]);
    depth = pixels = null;
    return;
  } else {
    draw(data);
  }
  self.postMessage(null);
};
