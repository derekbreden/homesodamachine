import { stopAnimate, updateDepthRange, fitGroundShadow } from "/js/viewer/scene.js";
import { poseFor, boxOfParts } from "/js/tour/frame.js";
import * as spotlight from "/js/tour/spotlight.js";

const clamp = (x) => Math.max(0, Math.min(1, x));
const ease = (x) => { const p = clamp(x); return p * p * (3 - 2 * p); };
const between = (t, a, b) => ease((t - a) / (b - a));
const mix = (a, b, p) => a + (b - a) * p;

export async function prepare(timeline) {
  const tour = window.__tour;
  const { THREE, renderer, scene, camera } = tour;
  stopAnimate();
  window.requestAnimationFrame = () => 0;
  tour.seekTime(0);
  const bounds = boxOfParts(tour.group, [
    "enclosure-front-top", "enclosure-front-bottom", "enclosure-back-top", "enclosure-back-bottom",
  ]);
  const canvas = document.createElement("canvas");
  canvas.width = timeline.width;
  canvas.height = timeline.height;
  const ctx = canvas.getContext("2d", { alpha: false });
  const logo = new Image();
  logo.src = "/brand/wordmark-reverse.svg";
  await logo.decode();
  await document.fonts.load('600 80px Montserrat');
  await document.fonts.load('400 30px Montserrat');
  const view = { x: 510, y: 106, w: 1410, h: 860 };
  renderer.setPixelRatio(1);
  renderer.setClearColor(0x081421, 0);
  renderer.toneMappingExposure = 1.38;
  spotlight.setBackground(0x081421);
  scene.fog = null;
  camera.fov = 33;
  const original = tour.TOUR.steps[2].reveal;
  const panelNames = new Set([
    "enclosure-front-top", "enclosure-front-bottom", "enclosure-back-top", "enclosure-back-bottom",
    "display", "display-cover", "display-gasket", "pump-jack", "nameplate", "nameplate-ink",
    "funnel", "funnel-drain-clamp", "funnel-drain-stub", "funnel-drain-union",
  ]);
  const panelMaterials = new Map();
  const panelBodies = tour.group.children.filter((body) => panelNames.has(body.name)
    || body.name.startsWith("bulkhead-ring-"));
  const systemParts = {
    refrigeration: ["compressor", "condenser+fan"],
    flavor: ["pump-a-head", "pump-a-motor", "pump-b-head", "pump-b-motor", "valve-v-e", "valve-v-i"],
    core: ["cold-core/foam-shell"],
  };

  function text(value, x, y, size = 24, color = "#dce6ff", weight = 400) {
    ctx.fillStyle = color;
    ctx.font = `${weight} ${size}px Montserrat, sans-serif`;
    ctx.fillText(value, x, y);
  }

  function title(lines, overline, detail, start, end, t) {
    const alpha = between(t, start, start + 0.7) * (1 - between(t, end - 0.4, end));
    if (!alpha) return;
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.translate(0, 18 * (1 - between(t, start, start + 0.8)));
    text(overline, 100, 327, 17, "#ff9152", 600);
    lines.forEach((line, i) => text(line, 94, 447 + i * 103, 88, "#f2f5ff", 500));
    text(detail, 100, 615, 22, "#9eafc4");
    ctx.fillStyle = "#ff9152";
    ctx.fillRect(100, 660, 52, 3);
    ctx.restore();
  }

  function leader(names, label, x, y, alpha, color) {
    if (alpha <= 0) return;
    const point = boxOfParts(tour.group, names).getCenter(new THREE.Vector3()).project(camera);
    const px = view.x + (point.x + 1) / 2 * view.w;
    const py = view.y + (1 - point.y) / 2 * view.h;
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.strokeStyle = color;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(x, y + 15);
    ctx.lineTo(x + 210, y + 15);
    ctx.lineTo(px - 18, py);
    ctx.lineTo(px, py);
    ctx.stroke();
    ctx.fillStyle = color;
    ctx.beginPath(); ctx.arc(px, py, 4, 0, Math.PI * 2); ctx.fill();
    text(label, x, y, 24, "#e7efff", 500);
    ctx.restore();
  }

  function draw(t) {
    const release = clamp((t - 13.7) / 2.4);
    const opening = clamp((t - 16.1) / 4.1);
    const park = between(t, 20.3, 22.0);
    tour.TOUR.steps[2].reveal = { ...original, park };
    const tourTime = t < 13.7 ? mix(0, 5999, clamp(t / 13.7))
      : t < 16.1 ? mix(6000, 10499, release)
        : mix(10500, 16499, opening);
    tour.seekTime(tourTime);
    renderer.setSize(view.w, view.h, false);
    camera.aspect = view.w / view.h;
    const pad = mix(mix(0.95, 1.65, ease(opening)), 0.96, park);
    const orbit = 0.055 * Math.sin(t / 15);
    const pose = poseFor(bounds, [0.9 + orbit, -1, 0.48], pad, camera);
    camera.position.copy(pose.position);
    camera.up.copy(pose.up);
    camera.lookAt(pose.target);
    camera.updateMatrixWorld();
    updateDepthRange();
    scene.fog = null;
    camera.updateProjectionMatrix();
    fitGroundShadow(null);

    const fridge = between(t, 20.8, 21.2) * (1 - between(t, 23.3, 23.7));
    const flavor = between(t, 23.4, 23.8) * (1 - between(t, 25.8, 26.2));
    const core = between(t, 25.9, 26.4) * (1 - between(t, 36.3, 37.1));
    const active = core > 0.1 ? systemParts.core : flavor > 0.1 ? systemParts.flavor
      : fridge > 0.1 ? systemParts.refrigeration : [];
    spotlight.paint({ active, hue: core ? "soda" : flavor ? "flavor" : "refrigerant",
      mix: Math.max(core, flavor, fridge) * 0.45, out: [], trail: [], paths: [], crest: [],
      pulse: t, quiet: 0, haloWidth: 0.55 });
    spotlight.fitScrim(camera);

    const background = ctx.createLinearGradient(0, 0, 1920, 1080);
    background.addColorStop(0, "#08172b");
    background.addColorStop(1, "#040b15");
    ctx.fillStyle = background;
    ctx.fillRect(0, 0, 1920, 1080);
    const glow = ctx.createRadialGradient(1300, 460, 10, 1300, 460, 800);
    glow.addColorStop(0, "#16355060");
    glow.addColorStop(1, "#08172b00");
    ctx.fillStyle = glow;
    ctx.fillRect(0, 0, 1920, 1080);
    const restored = [];
    for (const body of panelBodies) {
      if (!body.material || !park) continue;
      const materials = Array.isArray(body.material) ? body.material : [body.material];
      const faded = materials.map((material) => {
        let copy = panelMaterials.get(material);
        if (!copy) { copy = material.clone(); panelMaterials.set(material, copy); }
        copy.transparent = true;
        copy.opacity = material.opacity * (1 - park);
        copy.depthWrite = false;
        return copy;
      });
      restored.push([body, body.material]);
      body.material = Array.isArray(body.material) ? faded : faded[0];
    }
    const screws = tour.group.getObjectByName("tour-fasteners");
    if (screws) screws.visible = park < 0.5;
    renderer.render(scene, camera);
    ctx.globalAlpha = between(t, 0.2, 1.7) * (1 - between(t, 39.0, 41.3));
    ctx.drawImage(renderer.domElement, view.x, view.y, view.w, view.h);
    for (const [body, material] of restored) body.material = material;
    ctx.globalAlpha = 1;

    ctx.drawImage(logo, 87, 61, 285, 85);
    ctx.textAlign = "right";
    text("INSIDE THE SODA MACHINE", 1820, 109, 16, "#899fb9", 500);
    ctx.textAlign = "left";
    title(["Soda,", "on tap."], "AT HOME", "Cold. Carbonated. Ready.", 0.5, 13.5, t);
    title(["Let’s look", "inside."], "OPEN THE MACHINE", "Four enclosure quadrants.", 13.5, 21.0, t);

    const systemTitle = between(t, 21.0, 21.6) * (1 - between(t, 37.3, 38));
    ctx.save(); ctx.globalAlpha = systemTitle;
    text("BUILT AROUND THE COLD", 100, 278, 17, "#ff9152", 600);
    text("One compact", 96, 353, 46, "#f2f5ff", 500);
    text("system.", 96, 410, 46, "#f2f5ff", 500);
    ctx.restore();
    leader(systemParts.flavor, "Pumps + valves", 100, 495,
      between(t, 23.4, 23.8) * systemTitle, "#e0b479");
    leader(systemParts.core, "Insulated cold core", 100, 585,
      between(t, 25.9, 26.4) * systemTitle, "#7be1dd");
    leader(systemParts.refrigeration, "Refrigeration", 100, 675,
      between(t, 20.8, 21.2) * systemTitle, "#9cbda8");

    const closing = between(t, 37.5, 38.3);
    ctx.save(); ctx.globalAlpha = closing;
    text("01 / WATER", 100, 338, 17, "#ff9152", 600);
    text("Follow", 95, 449, 80, "#f2f5ff", 500);
    text("the water.", 95, 546, 80, "#f2f5ff", 500);
    ctx.restore();

    const caption = timeline.captions.find((c) => t >= c.start && t < c.end);
    if (caption) {
      ctx.font = "400 28px Montserrat, sans-serif";
      const width = ctx.measureText(caption.text).width;
      ctx.fillStyle = "#02070cc9";
      ctx.beginPath(); ctx.roundRect(960 - width / 2 - 24, 962, width + 48, 61, 8); ctx.fill();
      ctx.textAlign = "center";
      text(caption.text, 960, 1002, 28, "#e7edf7");
      ctx.textAlign = "left";
    }
    const fade = 1 - between(t, 40.8, timeline.duration);
    if (fade < 1) {
      ctx.fillStyle = `rgba(4,11,21,${1 - fade})`;
      ctx.fillRect(0, 0, 1920, 1080);
    }
    return canvas.toDataURL("image/jpeg", 0.95);
  }
  return { draw };
}
