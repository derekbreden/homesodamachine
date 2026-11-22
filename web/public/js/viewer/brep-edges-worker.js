// Recover exact B-rep boundary chains for one solid without occupying the viewer thread.
const QUANT = 1e4;

function tableSize(entries) {
  return 2 ** Math.ceil(Math.log2(Math.max(1, entries * 1.5)));
}

function sameCoordinate(a, b) {
  return a === b || (Number.isNaN(a) && Number.isNaN(b));
}

// Keep the topology pass in compact tables. Weld each vertex once and retain
// the first exact position at each quantized coordinate.
function boundarySegments(pos, idx, triFace) {
  const vertexIds = new Uint32Array(pos.length / 3);
  const welded = new Uint32Array(tableSize(vertexIds.length));
  const weldMask = welded.length - 1;
  const vertexId = (index) => {
    if (vertexIds[index]) return vertexIds[index];
    if (index >= vertexIds.length) return vertexIds.length + 1;
    const i = index * 3;
    const x = Math.round(pos[i] * QUANT);
    const y = Math.round(pos[i + 1] * QUANT);
    const z = Math.round(pos[i + 2] * QUANT);
    let slot = (Math.imul(x, 73856093) ^ Math.imul(y, 19349663) ^ Math.imul(z, 83492791)) & weldMask;
    while (welded[slot]) {
      const j = (welded[slot] - 1) * 3;
      if (sameCoordinate(x, Math.round(pos[j] * QUANT)) &&
          sameCoordinate(y, Math.round(pos[j + 1] * QUANT)) &&
          sameCoordinate(z, Math.round(pos[j + 2] * QUANT))) {
        vertexIds[index] = welded[slot];
        return vertexIds[index];
      }
      slot = (slot + 1) & weldMask;
    }
    welded[slot] = index + 1;
    vertexIds[index] = index + 1;
    return vertexIds[index];
  };

  // Each record holds the first directed segment and the lowest two distinct
  // face IDs. The slots find a record while the array keeps triangle order.
  const slots = new Uint32Array(tableSize(idx.length));
  const mask = slots.length - 1;
  const segments = new Int32Array(idx.length * 4);
  const noSecondFace = 0x7fffffff;
  let length = 0;
  const add = (p, q, face) => {
    if (p === q) return;
    let slot = (Math.imul(Math.min(p, q), 73856093) ^ Math.imul(Math.max(p, q), 19349663)) & mask;
    while (slots[slot]) {
      const i = (slots[slot] - 1) * 4;
      const a = segments[i], b = segments[i + 1];
      if ((p === a && q === b) || (p === b && q === a)) {
        const first = segments[i + 2];
        if (face < first) {
          segments[i + 3] = first;
          segments[i + 2] = face;
        } else if (face > first && face < segments[i + 3]) {
          segments[i + 3] = face;
        }
        return;
      }
      slot = (slot + 1) & mask;
    }
    slots[slot] = length / 4 + 1;
    segments[length++] = p;
    segments[length++] = q;
    segments[length++] = face;
    segments[length++] = noSecondFace;
  };
  for (let t = 0; t < triFace.length; t++) {
    const i = t * 3;
    const a = vertexId(idx[i]), b = vertexId(idx[i + 1]), c = vertexId(idx[i + 2]);
    const face = triFace[t];
    add(a, b, face);
    add(b, c, face);
    add(c, a, face);
  }

  const byPair = new Map();
  for (let i = 0; i < length; i += 4) {
    const second = segments[i + 3];
    if (second === noSecondFace) continue;
    const key = segments[i + 2] + "," + second;
    let list = byPair.get(key);
    if (!list) { list = []; byPair.set(key, list); }
    list.push({ a: segments[i], b: segments[i + 1] });
  }
  return byPair;
}

// Chain boundary segments (all sharing one face-pair) into polylines. Walks
// through degree-2 nodes and stops at a node of any other degree — a real BREP
// vertex (junction or open end). Loops (a closed rim with no vertex) come back
// to their start.
function chainSegments(segs) {
  const adj = new Map();
  const link = (n, to, i) => {
    let a = adj.get(n);
    if (!a) { a = []; adj.set(n, a); }
    a.push({ to, i });
  };
  segs.forEach((s, i) => { link(s.a, s.b, i); link(s.b, s.a, i); });

  const used = new Array(segs.length).fill(false);
  const out = [];
  // open chains first (start at degree-1 ends), then whatever's left (loops)
  const starts = [...adj.keys()].filter((n) => adj.get(n).length === 1).concat([...adj.keys()]);

  for (const start of starts) {
    let edge = adj.get(start).find((e) => !used[e.i]);
    if (!edge) continue;
    let cur = start;
    const path = [cur];
    while (edge) {
      used[edge.i] = true;
      cur = edge.to;
      path.push(cur);
      const inc = adj.get(cur);
      if (inc.length !== 2) break; // BREP vertex
      edge = inc.find((e) => !used[e.i]);
    }
    if (path.length >= 2) out.push(path);
  }
  return out;
}

self.onmessage = ({ data: { positions, indices, ranges } }) => {
  const triFace = new Int32Array(Math.floor(indices.length / 3)).fill(-1);
  for (let f = 0; f < ranges.length; f += 2) triFace.fill(f / 2, ranges[f], ranges[f + 1] + 1);
  const chains = [];
  let vertices = 0;
  for (const [key, segments] of boundarySegments(positions, indices, triFace)) {
    const pair = key.split(",").map(Number);
    for (const path of chainSegments(segments)) {
      chains.push({ path, pair });
      vertices += path.length;
    }
  }
  const points = new Float32Array(vertices * 3);
  const lines = new Uint32Array((vertices - chains.length) * 2);
  const starts = new Uint32Array(chains.length + 1);
  const pairs = new Int32Array(chains.length * 2);
  const boxes = new Float32Array(chains.length * 6);
  let vertex = 0, line = 0;
  for (let e = 0; e < chains.length; e++) {
    const { path, pair } = chains[e];
    starts[e] = vertex;
    pairs.set(pair, e * 2);
    let x0 = Infinity, y0 = Infinity, z0 = Infinity;
    let x1 = -Infinity, y1 = -Infinity, z1 = -Infinity;
    for (const id of path) {
      const v = (id - 1) * 3, out = vertex * 3;
      const x = positions[v], y = positions[v + 1], z = positions[v + 2];
      points[out] = x; points[out + 1] = y; points[out + 2] = z;
      x0 = Math.min(x0,x); y0 = Math.min(y0,y); z0 = Math.min(z0,z);
      x1 = Math.max(x1,x); y1 = Math.max(y1,y); z1 = Math.max(z1,z);
      if (vertex > starts[e]) { lines[line++] = vertex - 1; lines[line++] = vertex; }
      vertex++;
    }
    boxes.set([x0, y0, z0, x1, y1, z1], e * 6);
  }
  starts[chains.length] = vertex;
  self.postMessage({ points, lines, starts, pairs, boxes }, [points.buffer, lines.buffer, starts.buffer, pairs.buffer, boxes.buffer]);
};
