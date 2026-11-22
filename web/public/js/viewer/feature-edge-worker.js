// Extract crease and boundary edges off the UI thread, welding the CAD faces at coincident vertices.
function featureEdges(positions, indices) {
  const vertexCount = positions.length / 3;
  const triangleCount = Math.floor((indices?.length ?? vertexCount) / 3);
  const vertexIds = new Uint32Array(vertexCount);
  const welded = new Map();
  for (let i = 0; i < vertexCount; i++) {
    const j = i * 3;
    const key = `${Math.round(positions[j] * 1e4)},${Math.round(positions[j + 1] * 1e4)},${Math.round(positions[j + 2] * 1e4)}`;
    let id = welded.get(key);
    if (id === undefined) { id = welded.size; welded.set(key, id); }
    vertexIds[i] = id;
  }
  const stride = welded.size;
  welded.clear();
  const normals = new Float32Array(triangleCount * 3);
  const unmatched = new Map();
  let output = new Float32Array(1536), length = 0;
  function append(a, b) {
    if (length + 6 > output.length) {
      const next = new Float32Array(output.length * 2);
      next.set(output); output = next;
    }
    for (let axis = 0; axis < 3; axis++) {
      output[length + axis] = positions[a * 3 + axis];
      output[length + 3 + axis] = positions[b * 3 + axis];
    }
    length += 6;
  }
  const vertex = i => indices ? indices[i] : i;
  const threshold = Math.cos(Math.PI / 6);
  for (let tri = 0; tri < triangleCount; tri++) {
    const off = tri * 3;
    const a = vertex(off), b = vertex(off + 1), c = vertex(off + 2);
    if (vertexIds[a] === vertexIds[b] || vertexIds[b] === vertexIds[c] || vertexIds[a] === vertexIds[c]) continue;
    const ux = positions[3*b]-positions[3*a], uy = positions[3*b+1]-positions[3*a+1], uz = positions[3*b+2]-positions[3*a+2];
    const vx = positions[3*c]-positions[3*a], vy = positions[3*c+1]-positions[3*a+1], vz = positions[3*c+2]-positions[3*a+2];
    const nx = uy*vz-uz*vy, ny = uz*vx-ux*vz, nz = ux*vy-uy*vx;
    const norm = Math.sqrt(nx*nx + ny*ny + nz*nz) || 1;
    normals[off] = nx/norm; normals[off+1] = ny/norm; normals[off+2] = nz/norm;
    for (let k = 0; k < 3; k++) {
      const start = vertex(off+k), end = vertex(off+(k+1)%3);
      const one = vertexIds[start], two = vertexIds[end];
      const reverse = two * stride + one, other = unmatched.get(reverse);
      if (other !== undefined) {
        const f = other - other%3;
        if (normals[off]*normals[f]+normals[off+1]*normals[f+1]+normals[off+2]*normals[f+2] <= threshold) append(start,end);
        unmatched.delete(reverse);
      } else if (!unmatched.has(one * stride + two)) unmatched.set(one * stride + two, off+k);
    }
  }
  for (const edge of unmatched.values()) {
    const tri = edge - edge%3;
    append(vertex(edge), vertex(tri+(edge%3+1)%3));
  }
  return output.slice(0,length);
}
self.onmessage = ({data}) => {
  const edges = featureEdges(data.positions, data.indices);
  self.postMessage(edges, [edges.buffer]);
};
