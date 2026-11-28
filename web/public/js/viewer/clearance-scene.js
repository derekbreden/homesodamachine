// One orbitable close-up places both surface sets in their common frame and attaches the readout to them.
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { faceColors } from "./clearance-surfaces.js";

const v3 = () => new THREE.Vector3();
const radians = THREE.MathUtils.degToRad;

export function clearanceScene(diagram, plot) {
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.localClippingEnabled = true;
  const scene = new THREE.Scene();
  const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.01, 2000);
  camera.up.set(0, 0, 1);
  const fill = new THREE.HemisphereLight(0xffffff, 0xb1bdd4, 1.75);
  const key = new THREE.DirectionalLight(0xffffff, 1.65);
  scene.add(fill, key, key.target);
  const canvas = renderer.domElement;
  canvas.setAttribute("aria-label", "Fitted surfaces in 3D");
  plot.prepend(canvas);
  const controls = new OrbitControls(camera, canvas);
  controls.enablePan = false;
  controls.minZoom = 0.35; controls.maxZoom = 12;
  const leaders = document.createElement("canvas");
  leaders.className = "fit-leaders";
  leaders.setAttribute("aria-hidden", "true");
  diagram.append(leaders);
  const ctx = leaders.getContext("2d");
  let pair = null, labelRows = [], activeSide = "host", apart = true, focus = null;
  let frame = 0, baseHeight = 1, baseWidth = 1;
  const direction = v3(), pull = v3(), offset = v3();
  const bounds = new THREE.Box3();

  // Numbered faces fit on a phone. Wider views also carry the face name beside its leader.
  let hitLabels = [];
  function drawLabels() {
    const area = diagram.getBoundingClientRect(), view = plot.getBoundingClientRect();
    const ratio = renderer.getPixelRatio();
    const w = Math.round(area.width * ratio), h = Math.round(area.height * ratio);
    if (leaders.width !== w || leaders.height !== h) { leaders.width = w; leaders.height = h; }
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0); ctx.clearRect(0, 0, area.width, area.height);
    hitLabels = [];
    if (!pair) return;
    const left = view.x - area.x, top = view.y - area.y;
    const compact = diagram.offsetWidth < 720;
    const color = "#" + faceColors[activeSide].toString(16);
    const clamp = (v, min, max) => Math.max(min, Math.min(max, v));
    ctx.font = "600 12px system-ui";
    for (const [i, row] of labelRows.entries()) {
      const anchors = row.marks.map(mark => {
        const p = mark.point.clone().add(pair[activeSide].group.position).project(camera);
        return { x: left + (p.x + 1) * view.width / 2, y: top + (1 - p.y) * view.height / 2 };
      }).filter(p => p.x >= left && p.x <= left + view.width && p.y >= top && p.y <= top + view.height);
      if (!anchors.length) continue;
      const cx = anchors.reduce((sum, a) => sum + a.x, 0) / anchors.length;
      const cy = anchors.reduce((sum, a) => sum + a.y, 0) / anchors.length;
      const letter = String.fromCharCode(65 + i);
      const text = compact && focus !== i ? letter : letter + "  " + row.label;
      const value = focus === i && row.values ? row.values.join(" / ") + " mm" : null;
      const width = Math.max(ctx.measureText(text).width, value ? ctx.measureText(value).width : 0) + 14;
      const height = value ? 38 : 22;
      const sign = cx < left + view.width * 0.50 ? -1 : 1;
      const x = clamp(cx + sign * ((compact ? 18 : 39) + width / 2), left + width / 2 + 3, left + view.width - width / 2 - 3);
      let y;
      for (const delta of [-16, 15, -45, 44, -76, 75, -106, 105]) {
        y = clamp(cy + delta, top + height / 2 + 3, top + view.height - height / 2 - 4);
        if (!hitLabels.some(other => Math.abs(x - other.x) < (width + other.width) / 2 + 4 &&
          Math.abs(y - other.y) < (height + other.height) / 2 + 3)) break;
      }
      hitLabels.push({ i, x, y, width, height, text, value });
      ctx.globalAlpha = focus === null || focus === i ? 1 : 0.40;
      ctx.lineWidth = 1.5; ctx.strokeStyle = color;
      for (const a of anchors) {
        ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(a.x, a.y); ctx.stroke();
        ctx.fillStyle = color; ctx.beginPath(); ctx.arc(a.x, a.y, 3.3, 0, Math.PI * 2); ctx.fill();
      }
    }
    ctx.textAlign = "center"; ctx.textBaseline = "middle";
    for (const { i, x, y, width, height, text, value } of hitLabels) {
      ctx.globalAlpha = focus === null || focus === i ? 1 : 0.55;
      ctx.fillStyle = "#132540"; ctx.strokeStyle = color; ctx.lineWidth = 1.2;
      ctx.beginPath(); ctx.roundRect(x - width / 2, y - height / 2, width, height, text.length === 1 ? 11 : 5);
      ctx.fill(); ctx.stroke();
      ctx.fillStyle = "#fff"; ctx.fillText(text, x, value ? y - 8 : y);
      if (value) { ctx.fillStyle = "#e0eaf5"; ctx.fillText(value, x, y + 8); }
    }
    ctx.globalAlpha = 1;
  }
  let pressed = null;
  canvas.addEventListener("pointerdown", event => { pressed = [event.clientX, event.clientY]; });
  canvas.addEventListener("pointerup", event => {
    if (!pressed || Math.hypot(event.clientX - pressed[0], event.clientY - pressed[1]) > 5) return;
    const area = diagram.getBoundingClientRect();
    const hit = hitLabels.find(box => Math.abs(event.clientX - area.x - box.x) <= box.width / 2 + 3 &&
      Math.abs(event.clientY - area.y - box.y) <= box.height / 2 + 3);
    if (hit) labelRows[hit.i]?.element.querySelector("button")?.click();
  });
  function draw() {
    frame = 0;
    key.position.copy(camera.position).addScaledVector(camera.up, camera.position.distanceTo(controls.target) * 0.7);
    key.target.position.copy(controls.target);
    renderer.render(scene, camera);
    drawLabels();
  }
  function invalidate() { if (!frame) frame = requestAnimationFrame(draw); }
  function resize() {
    const { width, height } = plot.getBoundingClientRect();
    if (!width || !height) return;
    renderer.setSize(width, height, false);
    const aspect = width / height;
    const half = Math.max(baseHeight, baseWidth / aspect) * 0.65;
    camera.left = -half * aspect; camera.right = half * aspect;
    camera.top = half; camera.bottom = -half;
    camera.updateProjectionMatrix();
    invalidate();
  }
  const observer = new ResizeObserver(resize);
  observer.observe(plot); observer.observe(diagram);
  controls.addEventListener("change", invalidate);

  function frameParts(resetDirection = false) {
    if (!pair) return;
    pair.host.move(offset.set(0, 0, 0));
    const joint = pair.host.bounds.clone().union(pair.mate.bounds);
    const span = joint.getSize(v3()).length();
    pair.mate.move(offset.copy(pull).multiplyScalar(apart ? span * 0.79 : 0));
    bounds.copy(pair.host.bounds).union(pair.mate.bounds.clone().translate(offset));
    const size = bounds.getSize(v3()), target = bounds.getCenter(v3());
    const look = resetDirection ? direction : camera.position.clone().sub(controls.target).normalize();
    camera.position.copy(target).addScaledVector(look, size.length() * 3);
    camera.far = size.length() * 8;
    camera.lookAt(target); camera.updateMatrixWorld(); controls.target.copy(target);
    const right = v3().setFromMatrixColumn(camera.matrix, 0), up = v3().setFromMatrixColumn(camera.matrix, 1);
    const projectedWidth = vec => Math.abs(vec.x) * size.x + Math.abs(vec.y) * size.y + Math.abs(vec.z) * size.z;
    baseHeight = Math.max(1, projectedWidth(up)); baseWidth = Math.max(1, projectedWidth(right));
    camera.zoom = 1; controls.update(); resize();
  }
  function clear() {
    for (const side of Object.values(pair || {})) {
      scene.remove(side.group);
      side.group.traverse(obj => { obj.geometry?.dispose(); obj.material?.dispose(); });
    }
    pair = null; labelRows = []; focus = null; invalidate();
  }
  function setPair(host, mate, fit, site, separated) {
    clear(); pair = { host, mate }; apart = separated;
    scene.add(host.group, mate.group);
    const [az, el] = fit.pull ? [29, 29] : site.view;
    direction.set(Math.cos(radians(el)) * Math.cos(radians(az)), Math.cos(radians(el)) * Math.sin(radians(az)), Math.sin(radians(el)));
    if (fit.pull) pull.fromArray(fit.pull);
    else pull.crossVectors(camera.up, direction).normalize();
    frameParts(true);
  }
  function setLabels(side, rows) {
    activeSide = side; labelRows = rows; focus = null;
    for (const [name, surfaces] of Object.entries(pair || {})) for (const mark of surfaces.marks) {
      if (mark.material) mark.material.opacity = name === side ? 0.80 : 0.23;
    }
    invalidate();
  }
  function select(index) {
    focus = index;
    for (const [i, row] of labelRows.entries()) for (const mark of row.marks) {
      if (mark.material) mark.material.opacity = index === null || index === i ? 0.86 : 0.16;
    }
    invalidate();
  }
  return { setPair, setLabels, select, clear, reset: () => frameParts(true),
    separate(next) { apart = next; frameParts(); },
    dispose() {
      observer.disconnect(); controls.dispose(); clear(); cancelAnimationFrame(frame);
      renderer.dispose(); renderer.forceContextLoss(); canvas.remove(); leaders.remove();
    } };
}
