import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { conductorRecords } from './conductors.js';

const v = p => new THREE.Vector3(...p);

// Deliberately a bench diagram, not installed routing geometry. Connector pitch
// and relative wire section are physical; cable reach is compressed for reading.
export function buildHarness(scene, data) {
  const root = new THREE.Group();
  scene.add(root);
  root.scale.z = -1;
  const records = conductorRecords(data);
  const mats = {
    wire: new THREE.MeshStandardMaterial({ color: 0x171c24, roughness: .62 }),
    stripe: new THREE.MeshStandardMaterial({ color: 0xf5f3ec, roughness: .72 }),
    plastic: new THREE.MeshStandardMaterial({ color: 0xf5f1e6, roughness: .48 }),
    metal: new THREE.MeshStandardMaterial({ color: 0xc7d1db, roughness: .28, metalness: .78 }),
    copper: new THREE.MeshStandardMaterial({ color: 0xbb7543, metalness: .72, roughness: .4 }),
    braid: new THREE.MeshStandardMaterial({ color: 0x252e3a, roughness: .48, metalness: .12 }),
    band: new THREE.MeshStandardMaterial({ color: 0x161d29, roughness: .82 }),
    orange: new THREE.MeshStandardMaterial({ color: 0xf07726, roughness: .4 }),
    wago: new THREE.MeshPhysicalMaterial({ color: 0xc7cace, transparent: true, opacity: .72, roughness: .3, metalness: .05, depthWrite: false }),
    dark: new THREE.MeshStandardMaterial({ color: 0x263345, roughness: .5 }),
    trace: new THREE.MeshBasicMaterial({ color: 0xed812c, transparent: true, opacity: .12, depthWrite: false }),
  };
  const pickables = [], wirePickables = [], conductors = [], moving = [], dressing = [];
  let tracking = true;
  const groups = new Map(), ferrules = new Map(), spades = new Map();
  const makeGroup = (key, parent = root) => {
    const group = new THREE.Group();
    group.userData.key = key;
    parent.add(group);
    if (tracking) {
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push(group);
    }
    return group;
  };
  function mesh(geometry, material, parent, position = [0, 0, 0]) {
    const item = new THREE.Mesh(geometry, material);
    item.position.copy(v(position));
    item.castShadow = true;
    item.receiveShadow = true;
    parent.add(item);
    if (tracking) pickables.push(item);
    return item;
  }
  function box(size, material, parent, position, radius = .2) {
    return mesh(new RoundedBoxGeometry(...size, 2, Math.min(radius, Math.min(...size) / 3)), material, parent, position);
  }
  function tube(points, radius, material, parent, segments = 64) {
    const curve = new THREE.CatmullRomCurve3(points.map(v), false, 'centripetal');
    return mesh(new THREE.TubeGeometry(curve, segments, radius, 8, false), material, parent);
  }
  function ring(parent, radius, thickness, position, zScale = 1) {
    const item = mesh(new THREE.TorusGeometry(radius, thickness, 6, 48), mats.band, parent, position);
    item.rotation.y = Math.PI / 2;
    item.scale.x = zScale;
    return item;
  }
  function wire(key, points, striped = false, parent = root) {
    const group = makeGroup(key, parent);
    const material = mats.wire.clone();
    const body = tube(points, .85, material, group);
    body.userData.conductorBody = true;
    let stripeMaterial = null;
    if (striped) {
      stripeMaterial = mats.stripe.clone();
      const stripe = tube(points.map(([x, y, z]) => [x, y + .79, z]), .15, stripeMaterial, group);
      stripe.userData.conductorBody = true;
    }
    const trace = tube(points, 1.02, mats.trace, group);
    trace.userData.conductorBody = true;
    trace.visible = false;
    trace.castShadow = false;
    const hit = tube(points, 1.45, new THREE.MeshBasicMaterial({ transparent: true, opacity: 0, depthWrite: false, colorWrite: false }), group);
    hit.userData.hitOnly = true;
    if (tracking) {
      if (records.some(record => record.id === key)) wirePickables.push(hit);
      conductors.push({ key, group, material, stripeMaterial, trace });
    }
    return group;
  }
  const assembled = makeGroup('ribbons');
  const raw = makeGroup('ribbons');
  raw.visible = false;
  // These separate pieces let the first step show the two actual 3P blanks,
  // including the A3 stock that is discarded before populating the housing.
  for (const [r, zBase] of [[0, -13], [1, 9]]) {
    for (let c = 0; c < 3; c++) {
      wire(r === 0 ? ['COM', 'FAN', 'ribbons'][c] : ['OUT3', 'OUT2', 'OUT1'][c],
        [[-73, 3, zBase + c * 1.7], [0, 3, zBase + c * 1.7], [93, 3, zBase + c * 1.7]], c === 0, raw);
      if (c < 2) box([163, .3, .32], mats.wire, raw, [10, 3, zBase + c * 1.7 + .85], .05);
    }
  }
  const routes = {
    COM: [[-99.55, 17.65, -6.25], [-94, 18.2, -6.25], [-78, 7, -5.8], [-61, 3, -2.55], [21, 3, -2.55], [39, 3, -17.5], [51, 3.6, -21.2]],
    FAN: [[-99.55, 17.65, -3.75], [-94, 18.2, -3.75], [-76, 7, -3.5], [-61, 3, -.85], [23, 3, -.85], [54, 3, -34], [89, 3, -50], [116, 3, -50]],
    OUT3: [[-99.55, 17.65, 1.25], [-94, 18.2, 1.25], [-76, 7, 2.5], [-64, 3, 18], [-49, 3, 40], [-28, 3, 50], [-14, 3, 50]],
    OUT2: [[-99.55, 17.65, 3.75], [-94, 18.2, 3.75], [-76, 7, 4], [-60, 3, .85], [23, 3, .85], [56, 3, 24], [116, 3, 28]],
    OUT1: [[-99.55, 17.65, 6.25], [-94, 18.2, 6.25], [-75, 7, 6], [-60, 3, 2.55], [23, 3, 2.55], [64, 3, 7], [116, 3, 5]],
  };
  for (const [key, points] of Object.entries(routes)) wire(key, points, ['COM', 'OUT3'].includes(key), assembled);
  const positiveRoutes = [
    [[51, 3.6, -17.6], [42, 3, -17.6], [41, 3, -6], [76, 3, .5], [116, 3, .5]],
    [[51, 3.6, -14], [37, 3, -14], [38, 3, 14], [75, 3, 23.5], [116, 3, 23.5]],
    [[51, 3.6, -10.4], [32, 3, -12], [50, 3, -28], [90, 3, -45.5], [116, 3, -45.5]],
    [[51, 3.6, -6.8], [30, 3, -3], [22, 3, 26], [1, 3, 44], [-14, 3, 45.5]],
  ];
  positiveRoutes.forEach((points, i) => wire(['VI+', 'VJ+', 'FAN+', 'VK+'][i], points, false, assembled));

  const connector = makeGroup('connector');
  // XH is a vertical top-entry pair. The 2 mm inspection gap exposes the
  // native PCB header and plug socket without implying horizontal mating.
  connector.rotation.z = Math.PI / 2;
  connector.position.set(-95.95, 106.35, 0);
  const shell = makeGroup('connector', connector);
  // Six real cavities, with separate walls instead of a solid white cuboid.
  box([7.5, .65, 17.3], mats.plastic, shell, [-92.5, 6.15, 0]);
  box([7.5, .65, 17.3], mats.plastic, shell, [-92.5, 1.1, 0]);
  for (let i = 0; i <= 6; i++) box([7.5, 4.5, i === 0 || i === 6 ? .65 : .5], mats.plastic, shell, [-92.5, 3.6, -7.5 + i * 2.5], .12);
  box([.7, .8, 18.1], mats.plastic, shell, [-89, 6.6, 0]);
  for (const z of [-7.4, 7.4]) box([4, .7, 1.1], mats.plastic, shell, [-93, 6.8, z]);
  const markerShape = new THREE.Shape();
  markerShape.moveTo(-.55, -.6); markerShape.lineTo(.55, -.6); markerShape.lineTo(0, .65); markerShape.closePath();
  const marker = mesh(new THREE.ShapeGeometry(markerShape), mats.dark, shell, [-92.7, 6.49, -6.25]);
  marker.rotation.x = -Math.PI / 2;
  moving.push({ group: shell, offset: [14, 0, 0] });
  const contactGroup = makeGroup('connector', connector);
  function xhContact(z, key, parent = contactGroup) {
    const g = makeGroup(key, parent);
    // Socket box, sprung leaf, conductor crimp and insulation crimp.
    box([3.3, .25, 1.65], mats.metal, g, [-93, 2.9, z], .04);
    for (const dz of [-.78, .78]) box([3.3, 1.6, .2], mats.metal, g, [-93, 3.65, z + dz], .04);
    box([2.4, .2, 1.5], mats.metal, g, [-93.3, 4.4, z], .04);
    const leaf = box([2.7, .16, .7], mats.metal, g, [-92.7, 3.6, z], .04);
    leaf.rotation.z = -.12;
    tube([[-91.4, 3.4, z], [-90.5, 3.4, z], [-89.3, 3.5, z]], .35, mats.copper, g, 8);
    for (const x of [-90.5, -88.9]) {
      box([.85, .2, 1.5], mats.metal, g, [x, 3, z], .05);
      for (const dz of [-.65, .65]) box([.85, .9, .2], mats.metal, g, [x, 3.5, z + dz], .05);
    }
    return g;
  }
  for (const pin of data.pins.filter(pin => pin.cutMm)) xhContact((pin.pin - 3.5) * 2.5, pin.net);

  const dress = makeGroup('dress');
  const braid = makeGroup('dress', dress);
  // Interlaced helical strands make the mesh readable from any orbit angle.
  for (const direction of [-1, 1]) for (let i = 0; i < 12; i++) {
    const points = [];
    for (let j = 0; j <= 144; j++) {
      const t = j / 144;
      const angle = direction * t * Math.PI * 2 * 6 + i * Math.PI / 6;
      const weave = 1 + .035 * Math.cos(t * Math.PI * 2 * 144 + i * Math.PI);
      points.push([-57 + t * 82, 3 + Math.cos(angle) * 2.05 * weave, Math.sin(angle) * 3.8 * weave]);
    }
    tube(points, .18, mats.braid, braid, 144);
  }
  dressing.push(braid);
  moving.push({ group: braid, offset: [0, 24, 0] });
  for (const [i, x] of [-57, 25].entries()) {
    const collar = makeGroup('dress', dress);
    // Short open-ended heat-shrink tube: no end disk blocking the conductors.
    const item = mesh(new THREE.CylinderGeometry(3.8, 3.8, 5.5, 40, 1, true), mats.band, collar, [x, 3, 0]);
    item.rotation.z = Math.PI / 2;
    item.scale.x = .64;
    const tie = makeGroup('dress', dress);
    ring(tie, 2.5, .4, [x + (i ? -1 : 1), 3, 0], 1.6);
    box([2.4, 1.7, 2], mats.band, tie, [x + (i ? -1 : 1), 6, 1.8]);
    box([1, .4, .9], mats.band, tie, [x + (i ? -1 : 1), 6.7, 2.9], .1);
    dressing.push(collar, tie);
    moving.push({ group: collar, offset: [i ? 6 : -6, 13, 0] }, { group: tie, offset: [i ? 10 : -10, 7, 12] });
  }

  const farEnds = makeGroup('terminals');
  const wago = makeGroup('wago', farEnds);
  box([14, 7.5, 19.8], mats.wago, wago, [58, 4.6, -14], .8);
  for (let i = 0; i < 5; i++) {
    const z = -21.2 + i * 3.6;
    box([6.5, .6, 1.8], mats.metal, wago, [57, 3.6, z], .1);
    box([8, 1.5, 2.5], mats.orange, wago, [59, 8.9, z], .45);
    box([.35, .6, 1.5], mats.dark, wago, [63.2, 9.4, z], .05);
    // Ferrule tube and a flared insulating collar at each wire entry.
    const ferruleKey = ['COM', 'VI+', 'VJ+', 'FAN+', 'VK+'][i];
    const ferrule = makeGroup(ferruleKey, farEnds);
    ferrules.set(ferruleKey, ferrule);
    tube([[49.8, 3.6, z], [54, 3.6, z]], .62, mats.metal, ferrule, 8);
    tube([[48.4, 3.6, z], [50.5, 3.6, z]], 1.05, mats.plastic, ferrule, 8);
  }
  moving.push({ group: wago, offset: [0, 14, 0] });
  const deviceTerminals = [];
  function spade(x, z, key, provisional = false) {
    const group = makeGroup(key, farEnds);
    const boot = provisional ? mats.dark : mats.band;
    tube([[x - 1, 3, z], [x + 3.7, 3, z]], 1.35, boot, group, 8);
    box([5.2, .35, 2.9], mats.metal, group, [x + 6, 2.65, z], .15);
    for (const dz of [-1.25, 1.25]) {
      box([4.6, 1.3, .35], mats.metal, group, [x + 6, 3.2, z + dz], .13);
      box([4.3, .3, .7], mats.metal, group, [x + 6, 3.9, z + dz * .75], .1);
    }
    deviceTerminals.push(group); spades.set(key, group);
    moving.push({ group, offset: [13, provisional ? 5 : 0, 0] });
  }
  spade(116, 5, 'OUT1'); spade(116, .5, 'VI+');
  spade(116, 28, 'OUT2'); spade(116, 23.5, 'VJ+');
  spade(116, -50, 'FAN', true); spade(116, -45.5, 'FAN+', true);
  spade(-14, 50, 'OUT3'); spade(-14, 45.5, 'VK+');

  function tagFor(object) {
    for (let item = object; item; item = item.parent) if (item.userData.key) return item.userData.key;
    return null;
  }
  const anchors = [
    { key: 'pcb', title: 'PCB · J2', point: [-99, 8, 0], slot: [.12, .15] },
    { key: 'connector', title: 'JST plug', point: [-99.55, 15, 0], slot: [.15, .38] },
    { key: 'dress', title: 'Mesh & collars', point: [-15, 6, 0], slot: [.43, .21] },
    { key: 'wago', title: '+12 V Wago', point: [58, 10, -14], slot: [.67, .76] },
    { key: 'FAN', title: 'Fan −', point: [121, 4, -50], slot: [.89, .83] },
    { key: 'OUT1', title: 'V-I −', point: [121, 4, 5], slot: [.89, .53] },
    { key: 'OUT2', title: 'V-J −', point: [121, 4, 28], slot: [.89, .30] },
    { key: 'OUT3', title: 'V-K −', point: [-9, 4, 50], slot: [.53, .13] },
  ];
  for (const item of moving) item.base = item.group.position.clone();
  function update({ selection = null, step = null, reveal = false, explode = 0, opened = null }) {
    const cutting = step === 'cut';
    root.visible = !opened;
    raw.visible = cutting;
    connector.visible = !cutting;
    assembled.visible = !cutting;
    farEnds.visible = !['cut', 'jst', 'dress'].includes(step);
    dress.visible = !['cut', 'jst'].includes(step);
    for (const c of conductors) {
      const selected = selection === c.key, dimmed = !!selection && !selected;
      c.trace.visible = selected;
      c.material.color.set(selected ? 0xf28c28 : 0x171c24);
      c.material.emissive.set(selected ? 0xc45b0b : 0x000000);
      c.material.emissiveIntensity = selected ? .5 : 0;
      c.material.transparent = dimmed;
      c.material.opacity = dimmed ? .18 : 1;
      c.material.depthWrite = !dimmed;
      if (c.stripeMaterial) {
        c.stripeMaterial.transparent = dimmed;
        c.stripeMaterial.opacity = dimmed ? .18 : 1;
        c.stripeMaterial.depthWrite = !dimmed;
      }
    }
    for (const item of moving) {
      item.group.position.copy(item.base).addScaledVector(v(item.offset), explode);
    }
    if (step === 'jst') shell.position.add(v([10, 0, 0]));
    if (step === 'dress') braid.position.y += 12;
    for (const group of dressing) group.traverse(item => {
      if (!item.isMesh) return;
      // Shared materials are cloned once, so collars don't fade unrelated boots.
      if (!item.userData.dressMaterial) { item.material = item.material.clone(); item.userData.dressMaterial = true; }
      const dimmed = !!selection && selection !== 'dress';
      item.material.transparent = reveal || dimmed;
      item.material.opacity = reveal ? .10 : dimmed ? .14 : 1;
      item.material.depthWrite = !reveal && !dimmed;
      item.castShadow = !reveal && !dimmed;
    });
    root.traverse(item => {
      if (!item.isMesh || item.userData.hitOnly || item.userData.conductorBody || !item.material.emissive) return;
      if (!item.userData.selectMaterial) { item.material = item.material.clone(); item.userData.selectMaterial = true; }
      item.material.emissive.set(tagFor(item) === selection ? 0x9d4810 : 0x000000);
      item.material.emissiveIntensity = .8;
    });
    return { cutting };
  }
  let openRoot = null;
  function clonePart(part, parent) {
    const clone = part.clone(true);
    clone.position.set(0, 0, 0);
    clone.traverse(item => {
      if (!item.isMesh) return;
      item.geometry = item.geometry.clone();
      item.material = item.material.clone();
    });
    parent.add(clone);
    return clone;
  }
  function ghost(part) {
    part.traverse(item => {
      if (!item.isMesh) return;
      item.material.transparent = true;
      item.material.opacity = .18;
      item.material.depthWrite = false;
      item.castShadow = false;
    });
    return part;
  }
  function close() {
    if (!openRoot) return;
    scene.remove(openRoot);
    const sharedMaterials = Object.values(mats);
    openRoot.traverse(item => {
      if (!item.isMesh) return;
      item.geometry.dispose();
      if (!sharedMaterials.includes(item.material)) item.material.dispose();
    });
    openRoot = null;
  }
  function open(id) {
    const record = records.find(row => row.id === id);
    if (!record) return null;
    close();
    openRoot = new THREE.Group(); openRoot.scale.z = -1; scene.add(openRoot);
    const context = new THREE.Group(); openRoot.add(context);
    const z = record.pin ? (record.pin - 3.5) * 2.5 : 0;
    let source;
    // Temporary inspection objects never join the assembled pickable arrays.
    tracking = false;
    try {
      if (record.left === 'jst') {
        const plug = new THREE.Group(); openRoot.add(plug);
        plug.rotation.copy(connector.rotation); plug.position.copy(connector.position);
        ghost(clonePart(shell, plug));
        xhContact(z, id, plug);
        source = [-99.55, 17.65, z];
      } else {
        const portZ = -21.2 + record.port * 3.6;
        const block = ghost(clonePart(wago, context));
        block.rotation.y = Math.PI; block.position.set(-40, 0, portZ);
        const ferrule = clonePart(ferrules.get(id), openRoot);
        ferrule.rotation.y = Math.PI; ferrule.position.set(-40, 0, portZ);
        source = [-88.8, 3.6, 0];
      }
      const points = record.left === 'jst'
        ? [source, [-94, 18.2, z], [-78, 7, z / 2], [-58, 3.6, 0], [30, 3.6, 0], [100, record.right === 'ferrule' ? 3.6 : 3, 0]]
        : [source, [-72, 3.6, 0], [30, 3.6, 0], [100, 3, 0]];
      wire(id, points, record.stripe, openRoot);
      if (record.right === 'ferrule') {
        const block = ghost(clonePart(wago, context)); block.position.set(51, 0, 21.2);
        const ferrule = clonePart(ferrules.get('COM'), openRoot); ferrule.position.set(51, 0, 21.2);
      } else {
        const terminal = clonePart(spades.get(id), openRoot);
        const original = routes[id]?.at(-1) || positiveRoutes[['VI+', 'VJ+', 'FAN+', 'VK+'].indexOf(id)].at(-1);
        terminal.position.set(100 - original[0], 0, -original[2]);
      }
      if (record.sharedDress) ghost(clonePart(dress, context));
    } finally {
      tracking = true;
    }
    context.userData.context = true;
    return {
      from: new THREE.Vector3(record.left === 'jst' ? -99.55 : -92, record.left === 'jst' ? 15.85 : 3.6, -z),
      to: new THREE.Vector3(record.right === 'ferrule' ? 103 : 106, record.right === 'ferrule' ? 3.6 : 3.2, 0),
      sourceIsPcb: record.left === 'jst',
    };
  }
  function endpointsFor(id) {
    const record = records.find(row => row.id === id);
    if (!record) return null;
    const from = record.left === 'jst'
      ? v([-99.55, 15.85, (record.pin - 3.5) * 2.5])
      : v([52, 3.6, -21.2 + record.port * 3.6]);
    let to;
    if (record.right === 'ferrule') {
      to = v([52, 3.6, -21.2]);
    } else {
      const original = routes[id]?.at(-1) || positiveRoutes[['VI+', 'VJ+', 'FAN+', 'VK+'].indexOf(id)].at(-1);
      to = v([original[0] + 6, 3.2, original[2]]).add(spades.get(id).position);
    }
    return { from: root.localToWorld(from), to: root.localToWorld(to), sourceIsPcb: record.left === 'jst' };
  }
  function pointFor(anchor) {
    const point = v(anchor.point);
    if (anchor.key === 'connector') point.add(shell.position.clone().applyEuler(connector.rotation));
    else if (anchor.key === 'wago') point.add(wago.position);
    else if (spades.has(anchor.key)) point.add(spades.get(anchor.key).position);
    else if (anchor.key === 'dress') point.add(braid.position);
    return root.localToWorld(point);
  }
  function boundsFor(key) {
    const bounds = new THREE.Box3();
    for (const group of groups.get(key) || []) if (group.parent && root.getObjectById(group.id)) bounds.expandByObject(group);
    return bounds;
  }
  return { root, connector, pickables, wirePickables, anchors, update, tagFor, open, close, endpointsFor, pointFor, boundsFor };

}
