// Keep the worker entry on this origin; its implementation is the pinned BVH
// library's own worker, bundled with its Three.js dependency for module workers.
import 'https://esm.sh/three-mesh-bvh@0.9.5/src/workers/generateMeshBVH.worker.js?bundle&deps=three@0.181.1';
