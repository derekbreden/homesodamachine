// A reduced index lets a dense solid move without changing its inspection geometry.
import { MeshoptSimplifier } from "/vendor/meshoptimizer/simplifier.js";

self.onmessage = async ({ data: { positions, indices } }) => {
  try {
    await MeshoptSimplifier.ready;
    const target = Math.max(64, Math.floor(indices.length / 3 * 0.055)) * 3;
    const [reduced, error] = MeshoptSimplifier.simplify(indices, positions, 3, target, 0.001, ["Permissive"]);
    const deviation = error * MeshoptSimplifier.getScale(positions, 3);
    self.postMessage({ reduced, deviation }, [reduced.buffer]);
  } catch {
    self.postMessage(null);
  }
};
