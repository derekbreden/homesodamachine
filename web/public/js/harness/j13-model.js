import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

const v = point => new THREE.Vector3(...point);
const PIN_X = -99.55;
const PLUG_BOTTOM = 10.1;
const WIRE_Y = 19.5;
const POGO_BACK = 101;
const POGO_Y = 4;
const lane = pin => (pin - 2.5) * 2.5;
const tailLane = pin => (pin - 2.5) * 2.54;

// Bench reach is compressed for inspection. The native PCB, connector pitches,
// pogo body and individual tail positions retain their physical proportions.
export function buildHarness(scene, data) {
  const root = new THREE.Group();
  root.scale.z = -1;
  scene.add(root);
  const pickables = [], wirePickables = [], wireVisuals = [], moving = [];
  const groups = new Map();
  const materials = {
    wire: new THREE.MeshStandardMaterial({ color: 0x171c24, roughness: .62 }),
    stripe: new THREE.MeshStandardMaterial({ color: 0xf5f3ec, roughness: .72 }),
    plastic: new THREE.MeshStandardMaterial({ color: 0xf5f1e6, roughness: .48 }),
    metal: new THREE.MeshStandardMaterial({ color: 0xc7d1db, roughness: .28, metalness: .78 }),
    copper: new THREE.MeshStandardMaterial({ color: 0xbb7543, metalness: .72, roughness: .4 }),
    gold: new THREE.MeshStandardMaterial({ color: 0xe2bc61, metalness: .8, roughness: .26 }),
    solder: new THREE.MeshStandardMaterial({ color: 0xd6d9df, metalness: .86, roughness: .34 }),
    body: new THREE.MeshStandardMaterial({ color: 0x20242b, roughness: .6 }),
    mark: new THREE.MeshStandardMaterial({ color: 0xf5f1e6, roughness: .7 }),
    sleeve: new THREE.MeshStandardMaterial({ color: 0x151c29, roughness: .72 }),
    trace: new THREE.MeshBasicMaterial({ color: 0xed812c, transparent: true, opacity: .12, depthWrite: false }),
    hit: new THREE.MeshBasicMaterial({ transparent: true, opacity: 0, depthWrite: false, colorWrite: false }),
  };
  function group(key, parent = root, register = true) {
    const result = new THREE.Group();
    result.userData.key = key;
    parent.add(result);
    if (register) {
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push(result);
    }
    return result;
  }
  function mesh(geometry, material, parent, position = [0, 0, 0], register = true) {
    const result = new THREE.Mesh(geometry, material);
    result.position.copy(v(position));
    result.castShadow = true;
    result.receiveShadow = true;
    parent.add(result);
    if (register) pickables.push(result);
    return result;
  }
  function box(size, material, parent, position, radius = .2, register = true) {
    return mesh(new RoundedBoxGeometry(...size, 2, Math.min(radius, Math.min(...size) / 3)), material, parent, position, register);
  }
  function tube(points, radius, material, parent, segments = 56, register = true) {
    const curve = new THREE.CatmullRomCurve3(points.map(v), false, 'centripetal');
    return mesh(new THREE.TubeGeometry(curve, segments, radius, 10, false), material, parent, [0, 0, 0], register);
  }
  function cylinderX(radius, length, material, parent, position, register = true) {
    const item = mesh(new THREE.CylinderGeometry(radius, radius, length, 24), material, parent, position, register);
    item.rotation.z = Math.PI / 2;
    return item;
  }
  function wire(record, points, parent, register = true) {
    const body = group(record.id, parent, register);
    const material = materials.wire.clone();
    tube(points, .8, material, body, 72, register);
    let stripeMaterial = null;
    if (record.stripe) {
      stripeMaterial = materials.stripe.clone();
      tube(points.map(([x, y, z]) => [x, y + .745, z]), .14, stripeMaterial, body, 72, register);
    }
    const trace = tube(points, .99, materials.trace, body, 72, false);
    trace.visible = false;
    trace.castShadow = false;
    const hit = tube(points, 1.2, materials.hit, body, 72, false);
    hit.userData.hitOnly = true;
    if (register) {
      pickables.push(hit);
      wirePickables.push(hit);
      wireVisuals.push({ id: record.id, group: body, material, stripeMaterial, trace });
    }
    return body;
  }
  function makeShell(parent, register = true) {
    const shell = group('connector', parent, register);
    // Wire-entry above: the XHP plug's socket axis is vertical, matching the
    // actual top-entry B4B-XH header in the native PCB crop. The 2 mm
    // inspection gap leaves both the real header and plug socket visible.
    box([5.7, 7.2, .65], materials.plastic, shell, [PIN_X, PLUG_BOTTOM + 3.6, -5.0], .12, register);
    box([5.7, 7.2, .65], materials.plastic, shell, [PIN_X, PLUG_BOTTOM + 3.6, 5.0], .12, register);
    box([.65, 7.2, 9.7], materials.plastic, shell, [PIN_X - 2.55, PLUG_BOTTOM + 3.6, 0], .12, register);
    box([.65, 7.2, 9.7], materials.plastic, shell, [PIN_X + 2.55, PLUG_BOTTOM + 3.6, 0], .12, register);
    for (let i = 1; i < 4; i++) box([4.4, 6.7, .45], materials.plastic, shell, [PIN_X, PLUG_BOTTOM + 3.55, -5 + i * 2.5], .08, register);
    box([.6, .85, 10.3], materials.plastic, shell, [PIN_X + 3.0, PLUG_BOTTOM + 6.6, 0], .12, register);
    for (const z of [-4.4, 4.4]) box([1.1, 2.0, .9], materials.plastic, shell, [PIN_X + 3.0, PLUG_BOTTOM + 4.0, z], .12, register);
    const shape = new THREE.Shape();
    shape.moveTo(-.5, -.55); shape.lineTo(.5, -.55); shape.lineTo(0, .6); shape.closePath();
    const mark = mesh(new THREE.ShapeGeometry(shape), materials.body, shell, [PIN_X + 2.89, PLUG_BOTTOM + 5.3, -3.75], register);
    mark.rotation.y = Math.PI / 2;
    return shell;
  }
  function xhContact(pin, parent, register = true) {
    const z = lane(pin);
    const item = group(data.pins[pin - 1].net, parent, register);
    // Socket below, open-barrel conductor and insulation crimps above.
    box([1.65, 3.3, .25], materials.metal, item, [PIN_X, PLUG_BOTTOM + 2.1, z - .72], .04, register);
    box([1.65, 3.3, .25], materials.metal, item, [PIN_X, PLUG_BOTTOM + 2.1, z + .72], .04, register);
    for (const dx of [-.73, .73]) box([.2, 3.3, 1.6], materials.metal, item, [PIN_X + dx, PLUG_BOTTOM + 2.1, z], .04, register);
    const leaf = box([.7, 2.4, .16], materials.metal, item, [PIN_X, PLUG_BOTTOM + 2.2, z], .04, register);
    leaf.rotation.x = -.12;
    tube([[PIN_X, PLUG_BOTTOM + 3.6, z], [PIN_X, PLUG_BOTTOM + 4.9, z], [PIN_X, PLUG_BOTTOM + 6.1, z]], .34, materials.copper, item, 8, register);
    for (const y of [PLUG_BOTTOM + 4.65, PLUG_BOTTOM + 6.15]) {
      box([1.5, .85, .2], materials.metal, item, [PIN_X, y, z - .62], .04, register);
      for (const dx of [-.6, .6]) box([.2, .85, 1.3], materials.metal, item, [PIN_X + dx, y, z], .04, register);
    }
    tube([[PIN_X, PLUG_BOTTOM + 6.0, z], [PIN_X, WIRE_Y, z]], .8, materials.wire, item, 8, register);
    if (pin === 1) tube([[PIN_X + .745, PLUG_BOTTOM + 6, z], [PIN_X + .745, WIRE_Y, z]], .14, materials.stripe, item, 8, register);
    return item;
  }
  const connector = group('connector');
  const shell = makeShell(connector);
  for (const record of data.conductors) xhContact(record.pin, connector);
  moving.push({ group: shell, offset: [0, 14, 0] });

  const ribbons = group('ribbons');
  for (const record of data.conductors) {
    const pinZ = lane(record.pin), trunkZ = (record.pin - 2.5) * 1.7, farZ = tailLane(record.pin);
    wire(record, [[PIN_X, WIRE_Y, pinZ], [-95, 19.9, pinZ], [-82, 8.5, trunkZ], [-66, 4, trunkZ], [62, 4, trunkZ], [84, 4, farZ], [98.9, 4, farZ]], ribbons);
  }
  for (let i = 0; i < 3; i++) box([124, .3, .3], materials.wire, ribbons, [-2, 4, (i - 1) * 1.7], .05);

  const raw = group('ribbons');
  raw.visible = false;
  for (const record of data.conductors) {
    const z = (record.pin - 2.5) * 1.7;
    wire(record, [[-74, 4, z], [0, 4, z], [88, 4, z]], raw);
  }
  for (let i = 0; i < 3; i++) box([162, .3, .3], materials.wire, raw, [7, 4, (i - 1) * 1.7], .05);

  function stadiumX(length, width, depth, material, parent, x, register = true, holes = false) {
    const radius = width / 2, halfStraight = length / 2 - radius;
    const shape = new THREE.Shape();
    shape.moveTo(-halfStraight, -radius);
    shape.lineTo(halfStraight, -radius);
    shape.absarc(halfStraight, 0, radius, -Math.PI / 2, Math.PI / 2, false);
    shape.lineTo(-halfStraight, radius);
    shape.absarc(-halfStraight, 0, radius, Math.PI / 2, Math.PI * 1.5, false);
    if (holes) for (const center of [-10.22, 10.22]) {
      const hole = new THREE.Path();
      hole.absarc(center, 0, .75, 0, Math.PI * 2, true);
      shape.holes.push(hole);
    }
    const geometry = new THREE.ExtrudeGeometry(shape, { depth, bevelEnabled: false, curveSegments: 20 });
    const item = mesh(geometry, material, parent, [x, POGO_Y, 0], register);
    // Shape long axis becomes Z, its normal becomes X.
    item.rotation.y = Math.PI / 2;
    return item;
  }
  function makePogoBody(parent, register = true) {
    const body = group('pogo', parent, register);
    stadiumX(17.54, 4, 4, materials.body, body, POGO_BACK, register);
    stadiumX(23.4, 4, 1, materials.body, body, POGO_BACK + 1, register, true);
    for (const z of [-6.77, 6.77]) cylinderX(1.45, .08, materials.metal, body, [POGO_BACK + 4.02, POGO_Y, z], register);
    // The real part's -X end is marked when the attracting pair is aligned.
    box([.1, .65, 1.1], materials.mark, body, [POGO_BACK + 4.05, POGO_Y + 1.35, 8.0], .06, register);
    return body;
  }
  function makePogoContact(record, parent, register = true) {
    const g = group(record.id, parent, register), z = tailLane(record.pin);
    cylinderX(.35, 1.5, materials.gold, g, [POGO_BACK - .75, POGO_Y, z], register);
    cylinderX(.45, .55, materials.gold, g, [POGO_BACK + 4.275, POGO_Y, z], register);
    const tip = mesh(new THREE.SphereGeometry(.45, 16, 10), materials.gold, g, [POGO_BACK + 4.55, POGO_Y, z], register);
    tip.scale.x = 1;
    return g;
  }
  function makeJoint(record, parent, register = true) {
    const z = tailLane(record.pin), joint = group(record.id, parent, register);
    tube([[97.6, POGO_Y, z], [99, POGO_Y, z], [100.5, POGO_Y, z]], .38, materials.copper, joint, 12, register);
    const fillet = mesh(new THREE.SphereGeometry(.63, 16, 10), materials.solder, joint, [99.8, POGO_Y, z], register);
    fillet.scale.set(1.45, .72, .72);
    return joint;
  }
  function makeSleeve(record, parent, register = true) {
    const item = group(record.id, parent, register);
    const sleeve = mesh(new THREE.CylinderGeometry(.98, .98, 5.6, 32, 1, true), materials.sleeve.clone(), item, [98, POGO_Y, tailLane(record.pin)], register);
    sleeve.rotation.z = Math.PI / 2;
    return item;
  }
  const farEnds = group('terminals');
  const pogo = group('pogo', farEnds);
  const pogoBody = makePogoBody(pogo);
  const joints = group('pogo', farEnds);
  const sleeves = group('dress', farEnds);
  for (const record of data.conductors) {
    makePogoContact(record, pogo);
    makeJoint(record, joints);
    const sleeve = makeSleeve(record, sleeves);
    moving.push({ group: sleeve, offset: [-12, 7, (record.pin - 2.5) * 4] });
  }
  moving.push({ group: pogoBody, offset: [14, 6, 0] });
  for (const item of moving) item.base = item.group.position.clone();

  const anchors = [
    { key: 'pcb', title: 'PCB · J13 PUMPS', point: [-99.55, 5, 0], slot: [.11, .12] },
    { key: 'connector', title: 'JST plug · four contacts', point: [PIN_X, 16, 0], slot: [.17, .42] },
    { key: 'ribbons', title: '350 mm · 4P ribbon', point: [-14, 4, 0], slot: [.47, .13] },
    { key: 'dress', title: 'Four individual shrink sleeves', point: [98, 5, 0], slot: [.73, .12] },
    { key: 'pogo', title: 'Fixed male pogo · solder tails', point: [105, 5, 0], slot: [.87, .57] },
  ];
  function tagFor(object) {
    for (let item = object; item; item = item.parent) if (item.userData.key) return item.userData.key;
    return null;
  }
  function update({ selection = null, step = null, reveal = false, explode = 0, opened = null }) {
    const cutting = step === 'cut';
    root.visible = !opened;
    raw.visible = cutting;
    ribbons.visible = !cutting;
    connector.visible = !cutting;
    farEnds.visible = !['cut', 'jst'].includes(step);
    for (const row of wireVisuals) {
      const selected = selection === row.id, dimmed = !!selection && !selected;
      row.trace.visible = selected;
      row.material.color.set(selected ? 0xf28c28 : 0x171c24);
      row.material.emissive.set(selected ? 0xc45b0b : 0x000000);
      row.material.emissiveIntensity = selected ? .5 : 0;
      row.material.transparent = dimmed;
      row.material.opacity = dimmed ? .18 : 1;
      row.material.depthWrite = !dimmed;
      if (row.stripeMaterial) {
        row.stripeMaterial.transparent = dimmed;
        row.stripeMaterial.opacity = dimmed ? .18 : 1;
        row.stripeMaterial.depthWrite = !dimmed;
      }
    }
    for (const item of moving) item.group.position.copy(item.base).addScaledVector(v(item.offset), explode);
    if (step === 'jst') shell.position.add(v([0, 10, 0]));
    sleeves.traverse(item => {
      if (!item.isMesh) return;
      const dimmed = !!selection && selection !== 'dress';
      item.material.transparent = reveal || dimmed;
      item.material.opacity = reveal ? .1 : dimmed ? tagFor(item) === selection ? .2 : .12 : 1;
      item.material.depthWrite = !reveal && !dimmed;
      item.castShadow = !reveal && !dimmed;
    });
    root.traverse(item => {
      if (!item.isMesh || item.userData.hitOnly || item.geometry.type === 'TubeGeometry' || !item.material.emissive) return;
      if (!item.userData.selectionMaterial) { item.material = item.material.clone(); item.userData.selectionMaterial = true; }
      const key = tagFor(item);
      const selected = key === selection || selection === 'pogo' && item.parent.parent === pogo || selection === 'dress' && item.parent.parent === sleeves;
      item.material.emissive.set(selected ? 0x9d4810 : 0x000000);
      item.material.emissiveIntensity = .8;
    });
    return { cutting };
  }

  let openRoot = null;
  function ghost(object, parent) {
    const copy = object.clone(true);
    copy.position.set(0, 0, 0);
    copy.traverse(item => {
      if (!item.isMesh) return;
      item.geometry = item.geometry.clone();
      item.material = item.material.clone();
      item.material.transparent = true;
      item.material.opacity = .17;
      item.material.depthWrite = false;
      item.castShadow = false;
    });
    parent.add(copy);
    return copy;
  }
  function close() {
    if (!openRoot) return;
    scene.remove(openRoot);
    openRoot.traverse(item => {
      if (!item.isMesh) return;
      item.geometry.dispose();
      if (!Object.values(materials).includes(item.material)) item.material.dispose();
    });
    openRoot = null;
  }
  function open(id) {
    const record = data.conductors.find(row => row.id === id);
    if (!record) return null;
    close();
    openRoot = new THREE.Group();
    openRoot.scale.z = -1;
    scene.add(openRoot);
    ghost(shell, openRoot);
    xhContact(record.pin, openRoot, false);
    ghost(pogoBody, openRoot);
    makePogoContact(record, openRoot, false);
    makeJoint(record, openRoot, false);
    const sleeve = makeSleeve(record, openRoot, false);
    sleeve.traverse(item => {
      if (!item.isMesh) return;
      item.material.transparent = true; item.material.opacity = .2; item.material.depthWrite = false; item.castShadow = false;
    });
    const pinZ = lane(record.pin), farZ = tailLane(record.pin);
    wire(record, [[PIN_X, WIRE_Y, pinZ], [-94, 20, pinZ], [-80, 8.5, pinZ], [-62, 4, 0], [60, 4, 0], [84, 4, farZ], [98.9, 4, farZ]], openRoot, false);
    return {
      from: new THREE.Vector3(PIN_X, PLUG_BOTTOM + 4.65, -pinZ),
      to: new THREE.Vector3(99.8, POGO_Y, -farZ),
      sourceIsPcb: true,
    };
  }
  function endpointsFor(id) {
    const record = data.conductors.find(row => row.id === id);
    if (!record) return null;
    return {
      from: root.localToWorld(v([PIN_X, PLUG_BOTTOM + 4.65, lane(record.pin)])),
      to: root.localToWorld(v([99.8, POGO_Y, tailLane(record.pin)])),
      sourceIsPcb: true,
    };
  }
  function pointFor(anchor) {
    const point = v(anchor.point);
    if (anchor.key === 'connector') point.add(shell.position);
    else if (anchor.key === 'pogo') point.add(pogoBody.position);
    return root.localToWorld(point);
  }
  function boundsFor(key) {
    const bounds = new THREE.Box3();
    for (const item of groups.get(key) || []) if (item.parent && root.getObjectById(item.id)) bounds.expandByObject(item);
    return bounds;
  }
  return { root, connector, pickables, wirePickables, anchors, update, tagFor, open, close, endpointsFor, pointFor, boundsFor };
}
