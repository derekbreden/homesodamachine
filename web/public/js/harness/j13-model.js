import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

const v = point => new THREE.Vector3(...point);
const PIN_X = -99.55;
const PLUG_BOTTOM = 10.1;
const WIRE_Y = 19.5;
const TRUNK_X = -66;
const TRUNK_Y = 4;
const RAW_X = -74;
const END_X = 98;
const RIBBON_PITCH = 1.7;
const PAIR_SPACING = 16;
const FASTON_SPACING = 4.5;
const centered = (index, count, spacing) => (index - (count - 1) / 2) * spacing;

// Bench reach is compressed along the trunk. The native PCB, the XH pitch and
// the record's peeled and parted lengths at the pump end keep their physical
// proportions. Each Faston is drawn as J2's disconnect; the record matches its
// size to the motor tab.
export function buildHarness(scene, data) {
  const root = new THREE.Group();
  root.scale.z = -1;
  scene.add(root);
  const pickables = [], wirePickables = [], wireVisuals = [], moving = [];
  const groups = new Map(), fastons = new Map(), layout = new Map();
  const records = [...data.conductors].sort((a, b) => a.pin - b.pin);
  const lane = pin => centered(pin - 1, records.length, data.pitchMm);
  const ribbon = data.ribbons[0];
  const { peelMm, partMm } = ribbon;
  if (!(peelMm > partMm && partMm > 0)) throw new Error(`${data.id} ribbon record gives no peel and part lengths`);
  const PEEL_X = END_X - peelMm, PART_X = END_X - partMm;
  const PEEL_RUN = (peelMm - partMm) / 3, PART_RUN = partMm / 2;
  // One pair per pump, in ribbon order, named by the conductors' destinations.
  const pumps = [];
  for (const record of records) {
    const name = record.to.match(/^Pump \S+/)?.[0];
    if (!name) throw new Error(`${data.id} ${record.id} names no pump`);
    let pump = pumps.find(item => item.name === name);
    if (!pump) pumps.push(pump = { name, key: name.toLowerCase().replace(/\s+/g, '-'), conductors: [] });
    pump.conductors.push(record);
  }
  const trunkLane = record => centered(records.indexOf(record), records.length, RIBBON_PITCH);
  pumps.forEach((pump, index) => {
    pump.center = centered(index, pumps.length, PAIR_SPACING);
    pump.trunk = pump.conductors.reduce((sum, record) => sum + trunkLane(record), 0) / pump.conductors.length;
    pump.conductors.forEach((record, slot) => layout.set(record.id, {
      pump,
      trunk: trunkLane(record),
      offset: trunkLane(record) - pump.trunk,
      end: pump.center + centered(slot, pump.conductors.length, FASTON_SPACING),
    }));
  });
  const materials = {
    wire: new THREE.MeshStandardMaterial({ color: 0x171c24, roughness: .62 }),
    stripe: new THREE.MeshStandardMaterial({ color: 0xf5f3ec, roughness: .72 }),
    plastic: new THREE.MeshStandardMaterial({ color: 0xf5f1e6, roughness: .48 }),
    metal: new THREE.MeshStandardMaterial({ color: 0xc7d1db, roughness: .28, metalness: .78 }),
    copper: new THREE.MeshStandardMaterial({ color: 0xbb7543, metalness: .72, roughness: .4 }),
    body: new THREE.MeshStandardMaterial({ color: 0x20242b, roughness: .6 }),
    band: new THREE.MeshStandardMaterial({ color: 0x161d29, roughness: .82 }),
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
    tube(points, .8, material, body, 160, register).userData.conductorBody = true;
    let stripeMaterial = null;
    if (record.stripe) {
      stripeMaterial = materials.stripe.clone();
      tube(points.map(([x, y, z]) => [x, y + .745, z]), .14, stripeMaterial, body, 160, register).userData.conductorBody = true;
    }
    const trace = tube(points, .99, materials.trace, body, 160, false);
    trace.visible = false;
    trace.castShadow = false;
    const hit = tube(points, 1.2, materials.hit, body, 160, false);
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
  for (const record of records) xhContact(record.pin, connector);
  moving.push({ group: shell, offset: [0, 14, 0] });

  // A smooth sideways move from z0 at x0 to z1 at x1, held `offset` off that
  // path along its normal. The straight lead on either side keeps the curve
  // from bowing the neighbouring straights.
  function shift(x0, x1, z0, z1, offset = 0, steps = 8) {
    const step = (x1 - x0) / steps;
    return Array.from({ length: steps + 3 }, (_, i) => {
      const t = Math.min(1, Math.max(0, (i - 1) / steps));
      const slope = (z1 - z0) * 6 * t * (1 - t) / (x1 - x0), normal = Math.hypot(1, slope);
      return [x0 + (i - 1) * step - offset * slope / normal, TRUNK_Y, z0 + (z1 - z0) * t * t * (3 - 2 * t) + offset / normal];
    });
  }
  // From the peel point each pair leaves the ribbon at its own pitch; over the
  // parted length its two conductors separate to their own Fastons.
  function pumpEnd(record) {
    const { pump, offset, end } = layout.get(record.id);
    return [...shift(PEEL_X, PEEL_X + PEEL_RUN, pump.trunk, pump.center, offset), ...shift(PART_X, PART_X + PART_RUN, pump.center + offset, end), [END_X, TRUNK_Y, end]];
  }
  // The web joins neighbours along the trunk, and a pair's conductors until they part.
  function webs(parent, start) {
    for (let i = 1; i < records.length; i++) {
      const a = layout.get(records[i - 1].id), b = layout.get(records[i].id), z = (a.trunk + b.trunk) / 2;
      if (a.pump !== b.pump) { box([PEEL_X - start, .3, .3], materials.wire, parent, [(start + PEEL_X) / 2, TRUNK_Y, z], .05); continue; }
      const { pump } = a, offset = z - pump.trunk;
      tube([[start, TRUNK_Y, z], ...shift(PEEL_X, PEEL_X + PEEL_RUN, pump.trunk, pump.center, offset), [PART_X, TRUNK_Y, pump.center + offset]], .15, materials.wire, parent, 96);
    }
  }
  const ribbons = group('ribbons');
  for (const record of records) {
    const z = lane(record.pin), { trunk } = layout.get(record.id);
    wire(record, [[PIN_X, WIRE_Y, z], [-95, 19.9, z], [-82, 8.5, trunk], [TRUNK_X, TRUNK_Y, trunk], [TRUNK_X + 8, TRUNK_Y, trunk], ...pumpEnd(record)], ribbons);
  }
  webs(ribbons, TRUNK_X + 2);

  const raw = group('ribbons');
  raw.visible = false;
  for (const record of records) wire(record, [[RAW_X, TRUNK_Y, layout.get(record.id).trunk], ...pumpEnd(record)], raw);
  webs(raw, RAW_X);

  function faston(record, parent, register = true, z = layout.get(record.id).end) {
    const item = group(record.id, parent, register);
    // Insulated boot over the crimp barrel; the open receptacle faces the tab.
    cylinderX(1.35, 4.7, materials.band, item, [END_X + 1.35, TRUNK_Y, z], register);
    box([5.2, .35, 2.9], materials.metal, item, [END_X + 6, TRUNK_Y - .35, z], .15, register);
    for (const dz of [-1.25, 1.25]) {
      box([4.6, 1.3, .35], materials.metal, item, [END_X + 6, TRUNK_Y + .2, z + dz], .13, register);
      box([4.3, .3, .7], materials.metal, item, [END_X + 6, TRUNK_Y + .9, z + dz * .75], .1, register);
    }
    return item;
  }
  const farEnds = group('terminals');
  for (const pump of pumps) {
    const pair = group(pump.key, farEnds);
    for (const record of pump.conductors) {
      const item = faston(record, pair);
      fastons.set(record.id, item);
      moving.push({ group: item, offset: [13, 0, 0] });
    }
  }
  for (const item of moving) item.base = item.group.position.clone();

  const anchors = [
    { key: 'pcb', title: `PCB · ${data.id} ${data.name.toUpperCase()}`, point: [PIN_X, 5, 0], slot: [.11, .12] },
    { key: 'connector', title: `JST plug · ${records.length} contacts`, point: [PIN_X, 16, 0], slot: [.17, .42] },
    { key: 'ribbons', title: `${ribbon.cutMm} mm · ${ribbon.poles}P ribbon`, point: [-14, TRUNK_Y, 0], slot: [.47, .13] },
    ...pumps.map((pump, index) => ({
      key: pump.key, title: `${pump.name} · ${pump.conductors.length} Fastons`, name: pump.name, conductors: pump.conductors,
      point: [END_X + 6, TRUNK_Y + 1, pump.center], slot: [.84, index ? .38 : .8],
    })),
  ];
  function tagFor(object) {
    for (let item = object; item; item = item.parent) if (item.userData.key) return item.userData.key;
    return null;
  }
  function within(object, key) {
    for (let item = object; item; item = item.parent) if (item.userData.key === key) return true;
    return false;
  }
  function update({ selection = null, step = null, explode = 0, opened = null }) {
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
    const pumpSelected = pumps.some(pump => pump.key === selection);
    root.traverse(item => {
      if (!item.isMesh || item.userData.hitOnly || item.userData.conductorBody || !item.material.emissive) return;
      if (!item.userData.selectionMaterial) { item.material = item.material.clone(); item.userData.selectionMaterial = true; }
      const selected = tagFor(item) === selection || pumpSelected && within(item, selection);
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
    const record = records.find(row => row.id === id);
    if (!record) return null;
    close();
    openRoot = new THREE.Group();
    openRoot.scale.z = -1;
    scene.add(openRoot);
    ghost(shell, openRoot);
    xhContact(record.pin, openRoot, false);
    faston(record, openRoot, false, 0);
    const pinZ = lane(record.pin);
    wire(record, [[PIN_X, WIRE_Y, pinZ], [-94, 20, pinZ], [-80, 8.5, pinZ], [-62, TRUNK_Y, 0], [60, TRUNK_Y, 0], [END_X, TRUNK_Y, 0]], openRoot, false);
    return {
      from: new THREE.Vector3(PIN_X, PLUG_BOTTOM + 4.65, -pinZ),
      to: new THREE.Vector3(END_X + 6, TRUNK_Y + .2, 0),
      sourceIsPcb: true,
    };
  }
  function endpointsFor(id) {
    const record = records.find(row => row.id === id);
    if (!record) return null;
    return {
      from: root.localToWorld(v([PIN_X, PLUG_BOTTOM + 4.65, lane(record.pin)])),
      to: root.localToWorld(v([END_X + 6, TRUNK_Y + .2, layout.get(id).end]).add(fastons.get(id).position)),
      sourceIsPcb: true,
    };
  }
  function pointFor(anchor) {
    const point = v(anchor.point);
    if (anchor.key === 'connector') point.add(shell.position);
    else if (anchor.conductors) point.add(fastons.get(anchor.conductors[0].id).position);
    return root.localToWorld(point);
  }
  function boundsFor(key) {
    const bounds = new THREE.Box3();
    for (const item of groups.get(key) || []) if (item.parent && root.getObjectById(item.id)) bounds.expandByObject(item);
    return bounds;
  }
  return { root, connector, pickables, wirePickables, anchors, update, tagFor, open, close, endpointsFor, pointFor, boundsFor };
}
