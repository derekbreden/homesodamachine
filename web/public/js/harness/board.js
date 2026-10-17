import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

// This is a cropped copy of the site's native PCBA, with its original Gerber
// pixels and component geometry. Board XY becomes bench XZ; no mirrored text.
export async function loadBoard(scene, data = { id: 'J2' }) {
  const id = data.id.toUpperCase();
  if (!['J2', 'J13'].includes(id)) throw new Error(`No native PCB crop for ${id}`);
  const path = `/harness/${id.toLowerCase()}-board`;
  const [gltf, provenance] = await Promise.all([
    new GLTFLoader().loadAsync(`${path}.glb`),
    fetch(`${path}.json`).then(response => {
      if (!response.ok) throw new Error(`Could not load ${id} PCB source record`);
      return response.json();
    }),
  ]);
  const root = new THREE.Group();
  const board = gltf.scene;
  const pose = provenance.benchPose;
  board.scale.setScalar(pose.scale);
  board.rotation.set(...pose.rotationXYZ);
  board.position.fromArray(pose.positionMm);
  root.add(board); scene.add(root);
  root.name = `${id} native PCB crop`;
  root.userData.key = 'pcb';
  root.userData.provenance = provenance;
  const pickables = [];
  root.traverse(item => {
    if (!item.isMesh) return;
    item.castShadow = true; item.receiveShadow = true;
    item.userData.key = 'pcb'; pickables.push(item);
    // The CAD export supplies surface colors but omits reflectance. glTF's
    // metallic default turns white polymer black without an environment map.
    // Keep every native color and face texture; use the bench's matte response.
    const materials = Array.isArray(item.material) ? item.material : [item.material];
    for (const material of materials) {
      if (!material.name.startsWith('mat_')) continue;
      material.metalness = material.name === provenance.pinMaterialName ? .25 : 0;
      material.roughness = .68;
    }
  });
  root.updateMatrixWorld(true);
  const bounds = new THREE.Box3().setFromObject(root);
  const highlight = new THREE.Box3Helper(bounds.clone().expandByScalar(.7), 0xe5822d);
  highlight.layers.enable(1);
  highlight.visible = false; scene.add(highlight);
  const pinPoint = (pin, station = 'tip') => {
    const source = provenance.pins.find(item => item.pin === Number(pin));
    if (!source) return null;
    const z = station === 'pad' ? provenance.padSurfaceZMm : provenance.pinTipZMm;
    // Physical source XY and metal-tip Z travel through the exact same matrix as
    // the original header. The board remains independent of the ribbon mirror.
    return board.localToWorld(new THREE.Vector3(source.boardMm[0] / 1000, source.boardMm[1] / 1000, z / 1000));
  };
  const anchor = bounds.getCenter(new THREE.Vector3());
  anchor.y = bounds.max.y + .4;
  return {
    root, pickables, bounds, anchor, pinPoint,
    select(key) { highlight.visible = key === 'pcb' && root.visible; },
  };
}
