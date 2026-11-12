// /foam draws the fill model's prediction of a pour: the printed piece as glass, and the foam as
// the surface where the model's arrival time equals the time on the slider.
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

const root = document.getElementById("foam");
const stage = root.querySelector(".foam-stage");
const loading = root.querySelector(".foam-loading");
const tabs = root.querySelector(".foam-tabs");
const says = root.querySelector("#foam-says");
const play = root.querySelector("#foam-play");
const slider = root.querySelector("#foam-time");
const timeValue = root.querySelector("#foam-time-value");
const byAge = root.querySelector("#foam-age");
const showPrint = root.querySelector("#foam-print");
const legend = root.querySelector("#foam-legend");
const status = root.querySelector("#foam-status");
const placesBody = root.querySelector("#foam-places");
const chart = root.querySelector("#foam-chart");
const chartTitle = root.querySelector("#foam-chart-title");
const pourList = root.querySelector("#foam-pour");
const modelFacts = root.querySelector("#foam-model");

// The page's own colours, read from the shell's tokens.
const swatch = document.createElement("span");
swatch.hidden = true;
root.appendChild(swatch);
function token(name) {
  swatch.style.color = `var(${name})`;
  return new THREE.Color(getComputedStyle(swatch).color);
}

async function gunzip(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`${url} did not load (${response.status})`);
  return new Response(response.body.pipeThrough(new DecompressionStream("gzip"))).arrayBuffer();
}

async function json(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`${url} did not load (${response.status})`);
  return response.json();
}

const vertexShader = /* glsl */ `
  varying vec3 vWorld;
  void main() {
    vec4 world = modelMatrix * vec4(position, 1.0);
    vWorld = world.xyz;
    gl_Position = projectionMatrix * viewMatrix * world;
  }
`;

// March each view ray through the arrival-time field and stop where foam has arrived by `uNow`.
const fragmentShader = /* glsl */ `
  precision highp float;
  precision highp sampler3D;
  uniform sampler3D uField;
  uniform vec3 uLo;
  uniform vec3 uHi;
  uniform float uNow;
  uniform float uCell;
  uniform float uByAge;
  uniform vec3 uFoam;
  uniform mat4 uViewProjection;
  varying vec3 vWorld;

  float arrival(vec3 p) {
    return texture(uField, (p - uLo) / (uHi - uLo)).r;
  }

  vec3 ramp(float u) {
    vec3 a = vec3(0.24, 0.42, 1.0);
    vec3 b = vec3(0.35, 0.79, 0.64);
    vec3 c = vec3(1.0, 0.82, 0.29);
    vec3 d = vec3(1.0, 0.35, 0.21);
    u = clamp(u, 0.0, 1.0) * 3.0;
    return u < 1.0 ? mix(a, b, u) : u < 2.0 ? mix(b, c, u - 1.0) : mix(c, d, u - 2.0);
  }

  void main() {
    vec3 origin = cameraPosition;
    vec3 ray = normalize(vWorld - cameraPosition);
    vec3 inverse = 1.0 / ray;
    vec3 a = (uLo - origin) * inverse;
    vec3 b = (uHi - origin) * inverse;
    vec3 nearest = min(a, b);
    vec3 farthest = max(a, b);
    float enter = max(max(nearest.x, nearest.y), max(nearest.z, 0.0));
    float leave = min(min(farthest.x, farthest.y), farthest.z);
    if (enter >= leave) discard;

    float stride = uCell * 0.5;
    float jitter = fract(sin(dot(gl_FragCoord.xy, vec2(12.9898, 78.233))) * 43758.5453);
    float t = enter + stride * jitter;
    bool found = false;
    for (int i = 0; i < 1400; i++) {
      if (t > leave) break;
      if (arrival(origin + ray * t) <= uNow) { found = true; break; }
      t += stride;
    }
    if (!found) discard;
    float outside = max(t - stride, enter);
    float inside = t;
    for (int i = 0; i < 6; i++) {
      float middle = 0.5 * (outside + inside);
      if (arrival(origin + ray * middle) <= uNow) inside = middle; else outside = middle;
    }
    vec3 p = origin + ray * inside;

    vec2 e = vec2(uCell * 1.5, 0.0);
    vec3 slope = vec3(
      arrival(p + e.xyy) - arrival(p - e.xyy),
      arrival(p + e.yxy) - arrival(p - e.yxy),
      arrival(p + e.yyx) - arrival(p - e.yyx));
    vec3 normal = length(slope) > 1e-5 ? normalize(slope) : -ray;
    if (dot(normal, ray) > 0.0) normal = -normal;

    vec3 base = uFoam;
    if (uByAge > 0.5) {
      float when = arrival(p - normal * uCell * 1.5);
      base = ramp(when / max(uNow, 1e-3));
    }
    vec3 key = normalize(vec3(0.35, -0.55, 0.75));
    float lit = 0.42 + 0.5 * max(dot(normal, key), 0.0) + 0.16 * max(dot(normal, normalize(vec3(-0.6, 0.4, 0.3))), 0.0);
    float rim = pow(1.0 - max(dot(normal, -ray), 0.0), 3.0);
    gl_FragColor = vec4(base * lit + rim * 0.08, 1.0);

    vec4 clip = uViewProjection * vec4(p, 1.0);
    gl_FragDepth = clamp(clip.z / clip.w * 0.5 + 0.5, 0.0, 1.0);
  }
`;

const fmt = (value, digits = 0) => Number(value).toLocaleString("en-US", { maximumFractionDigits: digits, minimumFractionDigits: digits });

function reading(place, value) {
  if (place.read === "fill") return `${fmt(value)}% full`;
  if (place.read === "reach") return `${fmt(value)} mm down from its top, of ${fmt(place.full)}`;
  return `${fmt(value)} mm up from its floor, of ${fmt(place.full)}`;
}

try {
  const index = await json("/foam/index.json");
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  if (!renderer.capabilities.isWebGL2) throw new Error("This view needs WebGL 2");
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.setClearColor(0, 0);
  stage.appendChild(renderer.domElement);
  const scene = new THREE.Scene();
  scene.add(new THREE.HemisphereLight(0xffffff, 0x687182, 2.2));
  const sun = new THREE.DirectionalLight(0xffffff, 1.6);
  sun.position.set(250, -350, 650);
  scene.add(sun);
  const camera = new THREE.PerspectiveCamera(32, 1, 1, 6000);
  camera.up.set(0, 0, 1);
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = false;
  const viewProjection = new THREE.Matrix4();

  let frame = 0;
  function render() {
    frame = 0;
    camera.updateMatrixWorld();
    viewProjection.multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse);
    renderer.render(scene, camera);
  }
  const draw = () => { if (!frame) frame = requestAnimationFrame(render); };
  controls.addEventListener("change", draw);
  function resize() {
    const { width, height } = stage.getBoundingClientRect();
    if (!width || !height) return;
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    draw();
  }
  new ResizeObserver(resize).observe(stage);

  const pieces = new Map();
  let current = null;
  let chosen = null;
  let playing = false;
  let last = 0;

  async function load(entry) {
    const data = await json(`/foam/${entry.file}`);
    const [field, mesh] = await Promise.all([gunzip(`/foam/${data.field}`), gunzip(`/foam/${data.mesh}`)]);
    const [nx, ny, nz] = data.grid.n;
    const gl = renderer.getContext();
    if (Math.max(nx, ny, nz) > gl.getParameter(gl.MAX_3D_TEXTURE_SIZE)) throw new Error("this device cannot hold the prediction's field");
    const texture = new THREE.Data3DTexture(new Uint8Array(field), nx, ny, nz);
    texture.format = THREE.RedFormat;
    texture.type = THREE.UnsignedByteType;
    texture.minFilter = texture.magFilter = THREE.LinearFilter;
    texture.unpackAlignment = 1;
    texture.needsUpdate = true;

    const lo = new THREE.Vector3(...data.grid.origin);
    const size = new THREE.Vector3(nx, ny, nz).multiplyScalar(data.cell_mm);
    const hi = lo.clone().add(size);
    const group = new THREE.Group();

    const foam = new THREE.Mesh(
      new THREE.BoxGeometry(size.x, size.y, size.z),
      new THREE.ShaderMaterial({
        vertexShader, fragmentShader, side: THREE.BackSide,
        uniforms: {
          uField: { value: texture }, uLo: { value: lo }, uHi: { value: hi }, uNow: { value: 1 },
          uCell: { value: data.cell_mm }, uByAge: { value: 0 }, uFoam: { value: new THREE.Color(0xe2c078) },
          uViewProjection: { value: viewProjection },
        },
      }),
    );
    foam.position.copy(lo).addScaledVector(size, 0.5);
    foam.renderOrder = 0;
    group.add(foam);

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute("position", new THREE.BufferAttribute(new Float32Array(mesh), 3));
    geometry.computeVertexNormals();
    const glass = new THREE.Mesh(geometry, new THREE.MeshStandardMaterial({
      color: token("--text"), transparent: true, opacity: 0.13, depthWrite: false, side: THREE.DoubleSide, roughness: 0.35,
    }));
    glass.renderOrder = 1;
    const edges = new THREE.LineSegments(
      new THREE.EdgesGeometry(geometry, 30),
      new THREE.LineBasicMaterial({ color: token("--text-2"), transparent: true, opacity: 0.55 }),
    );
    edges.renderOrder = 2;
    const print = new THREE.Group();
    print.add(glass, edges);
    group.add(print);

    const marker = new THREE.Box3Helper(new THREE.Box3(), token("--action"));
    marker.renderOrder = 3;
    marker.material.depthTest = false;
    marker.visible = false;
    group.add(marker);

    geometry.computeBoundingBox();
    return { data, group, foam, print, marker, bounds: geometry.boundingBox.clone() };
  }

  function frameCamera(piece) {
    const centre = piece.bounds.getCenter(new THREE.Vector3());
    const radius = piece.bounds.getSize(new THREE.Vector3()).length() / 2;
    // Fit the narrower of the view's two angles, so a tall phone screen frames it too.
    const up = THREE.MathUtils.degToRad(camera.fov / 2);
    const across = Math.atan(Math.tan(up) * camera.aspect);
    const distance = radius / Math.sin(Math.min(up, across)) * 1.02;
    controls.target.copy(centre);
    camera.position.copy(centre).add(new THREE.Vector3(-0.72, -0.9, 0.5).normalize().multiplyScalar(distance));
    camera.near = distance / 100;
    camera.far = distance * 10;
    camera.updateProjectionMatrix();
    controls.update();
  }

  function at(series, times, t) {
    const span = times[times.length - 1] - times[0];
    const where = Math.min(Math.max((t - times[0]) / span, 0), 1) * (series.length - 1);
    const low = Math.floor(where);
    const high = Math.min(low + 1, series.length - 1);
    return series[low] + (series[high] - series[low]) * (where - low);
  }

  function setTime(t) {
    const { data, foam } = current;
    const clock = data.clock;
    t = Math.min(Math.max(t, clock.start_s), clock.end_s);
    slider.value = t;
    timeValue.textContent = `${fmt(t)} s`;
    // Bytes count steps from the first pour; never-reached cells hold the top value.
    foam.material.uniforms.uNow.value = Math.min((t - clock.start_s) / clock.step_s + 0.5, 254.5) / 255;
    const volume = at(data.foam_ml_series, data.times_s, t);
    status.textContent = `${fmt(volume)} mL of foam from ${fmt(data.poured_ml, 1)} mL of liquid`;
    drawChart(t);
    draw();
  }

  function drawChart(t) {
    const { data } = current;
    const place = chosen ?? data.places[0];
    const [w, h, left, bottom, top, right] = [640, 200, 46, 26, 12, 12];
    const times = data.times_s;
    const most = place.read === "fill" ? 100 : place.full;
    const x = (time) => left + (time - times[0]) / (times[times.length - 1] - times[0]) * (w - left - right);
    const y = (value) => h - bottom - Math.min(value / most, 1) * (h - bottom - top);
    const points = place.series.map((value, i) => `${x(times[i]).toFixed(1)},${y(value).toFixed(1)}`).join(" ");
    const now = at(place.series, times, t);
    chart.innerHTML = `
      <line class="axis" x1="${left}" y1="${h - bottom}" x2="${w - right}" y2="${h - bottom}"/>
      <line class="axis" x1="${left}" y1="${top}" x2="${left}" y2="${h - bottom}"/>
      <text x="${left - 6}" y="${top + 4}" text-anchor="end">${fmt(most)}</text>
      <text x="${left - 6}" y="${h - bottom}" text-anchor="end">0</text>
      <text x="${left}" y="${h - 6}">${fmt(times[0])} s</text>
      <text x="${w - right}" y="${h - 6}" text-anchor="end">${fmt(times[times.length - 1])} s</text>
      <polyline class="curve" points="${points}"/>
      <line class="now" x1="${x(t)}" y1="${top}" x2="${x(t)}" y2="${h - bottom}"/>
      <circle class="dot" cx="${x(t)}" cy="${y(now)}" r="4"/>`;
    chartTitle.textContent = `${place.name}: ${reading(place, now)} at ${fmt(t)} s`;
  }

  function choose(place) {
    chosen = place;
    for (const row of placesBody.children) row.setAttribute("aria-selected", String(row.dataset.id === place.id));
    const [lo, hi] = place.region;
    current.marker.box.set(new THREE.Vector3(...lo), new THREE.Vector3(...hi));
    current.marker.visible = true;
    drawChart(Number(slider.value));
    draw();
  }

  function fillPanels(piece) {
    const { data } = piece;
    says.textContent = data.says;
    placesBody.replaceChildren(...data.places.map((place) => {
      const row = document.createElement("tr");
      row.dataset.id = place.id;
      row.tabIndex = 0;
      row.setAttribute("aria-selected", "false");
      const cells = [place.name, place.stands_for, reading(place, place.value), "Not poured yet"];
      row.append(...cells.map((text, i) => {
        const cell = document.createElement(i === 0 ? "th" : "td");
        if (i === 0) cell.scope = "row";
        cell.textContent = text;
        return cell;
      }));
      if (place.read !== "fill" && place.air_ml > 0) {
        const small = document.createElement("small");
        small.textContent = `${fmt(place.filled_percent)}% full, ${fmt(place.air_ml, 1)} mL of air`;
        row.children[2].append(small);
      }
      row.addEventListener("click", () => choose(place));
      row.addEventListener("keydown", (event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); choose(place); } });
      return row;
    }));
    pourList.replaceChildren(
      ...data.pours.map((pour, i) => {
        const item = document.createElement("li");
        const where = data.pours.length > 1 ? `Pour ${i + 1}` : "One pour";
        item.textContent = `${where}: ${fmt(pour.grams)} g of mixed liquid, starting ${fmt(pour.start_s)} s after mixing begins and taking ${fmt(pour.seconds)} s.`;
        return item;
      }),
      Object.assign(document.createElement("li"), {
        textContent: `That is ${fmt(data.poured_ml, 1)} mL of liquid. The model turns it into ${fmt(data.foam_ml)} mL of foam, of which ${fmt(data.out_of_the_piece_ml)} mL ends above the piece.`,
      }),
    );
  }

  function fillModel(foam) {
    const rows = [
      ["Free rise, far from walls", `${fmt(foam.expansion)} times the liquid`],
      ["Starts to rise", `${fmt(foam.cream_s)} s after mixing begins`],
      ["Stops rising", `${fmt(foam.rise_end_s)} s after mixing begins`],
      ["Liquid density", `${fmt(foam.liquid_density_kg_m3 / 1000, 2)} g/mL`],
      ["Liquid viscosity", `${fmt(foam.viscosity_pa_s, 1)} Pa·s`],
      ["Thickening by gas", `${fmt(foam.gas_thickening)} per volume of gas`],
      ["Thickening by cure", `power ${fmt(foam.cure_exponent)} of the time left`],
      ["Expansion lost on a wall", `${fmt(foam.skin_loss * 100)}%, fading over ${fmt(foam.skin_depth_mm, 1)} mm`],
      ["Flow through a gap", `as its width to the power ${fmt(foam.gap_exponent + 1)}`],
    ];
    modelFacts.replaceChildren(...rows.map(([name, value]) => {
      const row = document.createElement("div");
      row.append(Object.assign(document.createElement("dt"), { textContent: name }), Object.assign(document.createElement("dd"), { textContent: value }));
      return row;
    }));
  }

  async function show(entry) {
    for (const tab of tabs.children) tab.setAttribute("aria-selected", String(tab.dataset.id === entry.id));
    setPlaying(false);
    loading.hidden = false;
    loading.textContent = "Loading the prediction…";
    if (!pieces.has(entry.id)) pieces.set(entry.id, await load(entry));
    if (current) scene.remove(current.group);
    current = pieces.get(entry.id);
    chosen = null;
    scene.add(current.group);
    current.marker.visible = false;
    current.print.visible = showPrint.checked;
    current.foam.material.uniforms.uByAge.value = byAge.checked ? 1 : 0;
    const clock = current.data.clock;
    slider.min = clock.start_s;
    slider.max = clock.end_s;
    slider.disabled = play.disabled = false;
    root.querySelector("#foam-legend-from").textContent = `${fmt(clock.start_s)} s`;
    root.querySelector("#foam-legend-to").textContent = "now";
    fillPanels(current);
    resize();
    frameCamera(current);
    setTime(clock.end_s);
    loading.hidden = true;
    history.replaceState(null, "", `#${entry.id}`);
  }

  function setPlaying(on) {
    playing = on;
    play.textContent = on ? "Pause" : "Play";
    if (on) {
      const clock = current.data.clock;
      if (Number(slider.value) >= clock.end_s - 0.5) setTime(clock.start_s);
      last = performance.now();
      requestAnimationFrame(tick);
    }
  }

  // A pour plays in about a quarter of a minute.
  function tick(now) {
    if (!playing) return;
    const clock = current.data.clock;
    const rate = (clock.end_s - clock.start_s) / 15;
    const t = Number(slider.value) + (now - last) / 1000 * rate;
    last = now;
    setTime(t);
    if (t >= clock.end_s) setPlaying(false); else requestAnimationFrame(tick);
  }

  tabs.replaceChildren(...index.pours.map((entry) => {
    const tab = document.createElement("button");
    tab.type = "button";
    tab.role = "tab";
    tab.dataset.id = entry.id;
    tab.textContent = entry.name;
    tab.addEventListener("click", () => show(entry).catch(fail));
    return tab;
  }));
  play.addEventListener("click", () => setPlaying(!playing));
  slider.addEventListener("input", () => { setPlaying(false); setTime(Number(slider.value)); });
  byAge.addEventListener("change", () => {
    current.foam.material.uniforms.uByAge.value = byAge.checked ? 1 : 0;
    legend.hidden = !byAge.checked;
    draw();
  });
  showPrint.addEventListener("change", () => { current.print.visible = showPrint.checked; draw(); });
  fillModel(index.foam);
  addEventListener("hashchange", () => {
    const entry = index.pours.find((pour) => `#${pour.id}` === location.hash);
    if (entry && entry.id !== current?.data.id) show(entry).catch(fail);
  });
  const wanted = index.pours.find((entry) => `#${entry.id}` === location.hash) ?? index.pours.find((entry) => entry.id === "comb") ?? index.pours[0];
  await show(wanted);
} catch (error) {
  fail(error);
}

function fail(error) {
  loading.hidden = false;
  loading.textContent = `The prediction could not be shown: ${error.message}`;
}
