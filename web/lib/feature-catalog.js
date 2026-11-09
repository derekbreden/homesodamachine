// Feature catalogs read construction identities from existing immutable mesh headers on demand.
import fs from "node:fs";
import path from "node:path";
import { createGunzip } from "node:zlib";
import { objectFeatures } from "../contracts/features.js";

const held = new Map();
const MAX_HEADER = 8 * 1024 * 1024;

export function readMeshHeader(file) {
  const fd = fs.openSync(file, "r");
  try {
    const prefix = Buffer.alloc(4);
    if (fs.readSync(fd, prefix, 0, 4, 0) !== 4) throw new Error("Truncated mesh header");
    const length = prefix.readUInt32LE();
    if (length > MAX_HEADER) throw new Error("Mesh header too large");
    const text = Buffer.alloc(length);
    if (fs.readSync(fd, text, 0, length, 4) !== length) throw new Error("Truncated mesh header");
    return JSON.parse(text.toString("utf8"));
  } finally { fs.closeSync(fd); }
}

async function streamedHeader(stream) {
  const unzip = createGunzip();
  stream.on("error", error => unzip.destroy(error));
  stream.pipe(unzip);
  let bytes = Buffer.alloc(0), length = null;
  try {
    for await (const chunk of unzip) {
      bytes = Buffer.concat([bytes, chunk]);
      if (length === null && bytes.length >= 4) {
        length = bytes.readUInt32LE();
        if (length > MAX_HEADER) throw new Error("Mesh header too large");
      }
      if (length !== null && bytes.length >= length + 4) return JSON.parse(bytes.subarray(4, length + 4).toString("utf8"));
    }
    throw new Error("Truncated mesh header");
  } finally { stream.destroy(); unzip.destroy(); }
}

function compact(header) { return { meshes: header.meshes.map(row => ({ features: row.features || [] })) }; }
const assetFile = (hardwareDir, hash) => path.join(hardwareDir, "..", ".cache/meshes/scene-assets", `${hash}.mesh`);

export function localFeatureCatalog(hardwareDir, file) {
  const header = readMeshHeader(path.join(hardwareDir, file + ".mesh"));
  const features = [];
  for (const node of header.meshes || []) {
    if (!node.feature_count || !/^[a-f0-9]{64}$/.test(node.asset)) continue;
    try { features.push(...objectFeatures(node, readMeshHeader(assetFile(hardwareDir, node.asset)))); }
    catch (error) { if (error.code !== "ENOENT") throw error; }
  }
  return { file, revision: header.src, instances: [...new Set((header.meshes || []).map(node => node.name))], features: features.map(feature => ({ ...feature, file })) };
}

export async function featureCatalog(hardwareDir, file, store) {
  const header = readMeshHeader(path.join(hardwareDir, file + ".mesh"));
  const nodes = (header.meshes || []).filter(node => node.feature_count && /^[a-f0-9]{64}$/.test(node.asset));
  const features = [];
  for (const node of nodes) {
    const key = `${hardwareDir}:${node.asset}`;
    if (!held.has(key)) {
      const promise = (async () => {
        try { return compact(readMeshHeader(assetFile(hardwareDir, node.asset))); }
        catch (error) {
          if (error.code !== "ENOENT" || !store) throw error;
          return compact(await streamedHeader(await store.readStream(`s-${node.asset}.gz`)));
        }
      })().catch(error => { held.delete(key); throw error; });
      held.set(key, promise);
      while (held.size > 128) held.delete(held.keys().next().value);
    }
    features.push(...objectFeatures(node, await held.get(key)));
  }
  return { file, revision: header.src, instances: [...new Set((header.meshes || []).map(node => node.name))], features: features.map(feature => ({ ...feature, file })) };
}
