import { stopAnimate, updateDepthRange, fitGroundShadow } from "/js/viewer/scene.js";
import { poseFor, boxOfParts } from "/js/tour/frame.js";
import * as spotlight from "/js/tour/spotlight.js";
import { createFilmScenes } from "/video/film-scenes.js";

const clamp = (x) => Math.max(0, Math.min(1, x));
const ease = (x) => { const p = clamp(x); return p * p * (3 - 2 * p); };
const between = (t, a, b) => ease((t - a) / (b - a));
const mix = (a, b, p) => a + (b - a) * p;

export async function prepare(timeline, palette) {
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
  ctx.imageSmoothingEnabled = true;
  ctx.imageSmoothingQuality = "high";
  const logo = new Image();
  logo.src = "/brand/wordmark-reverse.svg";
  await logo.decode();
  await Promise.all([400, 500, 600].map((weight) => document.fonts.load(`${weight} 80px Montserrat`)));
  const view = { x: 560, y: 110, w: 1360, h: 840 };
  renderer.setPixelRatio(2);
  renderer.setClearColor(palette.cobalt, 0);
  renderer.toneMappingExposure = 1.32;
  scene.fog = null;
  camera.fov = 33;
  const fill = new THREE.DirectionalLight(0xffffff, 0.65);
  fill.position.set(500, -800, 600);
  fill.target.position.copy(bounds.getCenter(new THREE.Vector3()));
  scene.add(fill, fill.target);
  const original = tour.TOUR.steps[2].reveal;
  const panelNames = new Set([
    "enclosure-front-top", "enclosure-front-bottom", "enclosure-back-top", "enclosure-back-bottom",
    "display", "display-cover", "display-gasket", "pump-jack", "nameplate", "nameplate-ink",
    "funnel", "funnel-drain-clamp", "funnel-drain-stub", "funnel-drain-union",
  ]);
  const panelMaterials = new Map();
  const panelBodies = tour.group.children.filter((body) => panelNames.has(body.name)
    || body.name.startsWith("bulkhead-ring-"));
  const systems = [
    { number: 1, title: "Refrigeration", detail: "Moves heat out", at: 20.8, until: 23.4,
      parts: ["compressor", "condenser+fan"] },
    { number: 2, title: "Pumps + valves", detail: "Meters the selected flavor", at: 23.4, until: 25.9,
      parts: ["pump-a-head", "pump-a-motor", "pump-b-head", "pump-b-motor", "valve-v-e", "valve-v-i"] },
    { number: 3, title: "Insulated cold core", detail: "Chills water and both flavors", at: 25.9, until: 37.3,
      parts: ["cold-core/foam-shell"] },
  ];

  function text(value, x, y, size = 24, color = palette.white, weight = 400) {
    ctx.fillStyle = color;
    ctx.font = `${weight} ${size}px Montserrat, sans-serif`;
    ctx.fillText(value, x, y);
  }

  function title(lines, overline, detail, start, end, t) {
    const enter = between(t, start, start + 0.7);
    const alpha = enter * (1 - between(t, end - 0.4, end));
    if (!alpha) return;
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.translate(0, 16 * (1 - enter));
    text(overline, 100, 317, 18, palette.ice, 500);
    lines.forEach((line, i) => text(line, 94, 444 + i * 112, 94, palette.white, 600));
    text(detail, 100, 628, 24, palette.ice);
    ctx.fillStyle = palette.orange;
    ctx.beginPath(); ctx.roundRect(100, 670, 60, 4, 2); ctx.fill();
    ctx.restore();
  }

  function number(value, x, y, radius, active) {
    ctx.fillStyle = active ? palette.orange : palette.ice;
    ctx.beginPath(); ctx.arc(x, y, radius, 0, Math.PI * 2); ctx.fill();
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    text(String(value).padStart(2, "0"), x, y + 1, radius * 0.82, palette.navy, 600);
    ctx.textAlign = "left";
    ctx.textBaseline = "alphabetic";
  }

  function systemLabels(t) {
    const overall = 1 - between(t, 37.3, 38.0);
    const pins = [];
    for (const system of systems) {
      const enter = between(t, system.at, system.at + 0.5);
      const alpha = enter * overall;
      if (!alpha) continue;
      const active = t < system.until;
      const row = 480 + (system.number - 1) * 112;
      ctx.save();
      ctx.globalAlpha = alpha;
      ctx.fillStyle = active ? `${palette.ice}26` : `${palette.ice}0a`;
      ctx.beginPath(); ctx.roundRect(90, row, 455, 96, 12); ctx.fill();
      number(system.number, 125, row + 34, 19, active);
      text(system.title, 160, row + 41, 27, palette.white, 500);
      text(system.detail, 160, row + 70, 18, palette.ice);
      ctx.restore();
      const point = boxOfParts(tour.group, system.parts).getCenter(new THREE.Vector3()).project(camera);
      pins.push({ ...system, active, alpha,
        x: view.x + (point.x + 1) / 2 * view.w,
        y: view.y + (1 - point.y) / 2 * view.h });
    }
    for (const pin of pins) {
      ctx.save();
      ctx.globalAlpha = pin.alpha * (pin.active ? 1 : 0.8);
      ctx.strokeStyle = `${palette.white}b3`;
      ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.arc(pin.x, pin.y, 24, 0, Math.PI * 2); ctx.stroke();
      number(pin.number, pin.x, pin.y, 19, pin.active);
      ctx.restore();
    }
  }

  function draw(t) {
    if (film && t >= timeline.openingDuration) return film.draw(t);
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
    const pad = mix(mix(0.94, 1.65, ease(opening)), 0.96, park);
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
    spotlight.paint({ active: [], mix: 0, out: [], trail: [], paths: [], crest: [], quiet: 0 });

    ctx.fillStyle = palette.cobalt;
    ctx.fillRect(0, 0, 1920, 1080);
    const glow = ctx.createRadialGradient(1290, 430, 100, 1290, 430, 850);
    glow.addColorStop(0, `${palette.ice}14`);
    glow.addColorStop(1, `${palette.ice}00`);
    ctx.fillStyle = glow;
    ctx.fillRect(0, 0, 1920, 1080);
    const pictureAlpha = between(t, 0.2, 1.7) * (timeline.full ? 1 : 1 - between(t, 39.0, 41.3));
    ctx.save();
    ctx.globalAlpha = pictureAlpha * (1 - 0.6 * ease(opening));
    ctx.filter = "blur(22px)";
    ctx.fillStyle = `${palette.navy}66`;
    ctx.beginPath(); ctx.ellipse(1250, 924, 270, 20, 0, 0, Math.PI * 2); ctx.fill();
    ctx.restore();
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
    ctx.globalAlpha = pictureAlpha;
    ctx.drawImage(renderer.domElement, view.x, view.y, view.w, view.h);
    for (const [body, material] of restored) body.material = material;
    ctx.globalAlpha = 1;

    ctx.drawImage(logo, 87, 58, 270, 80.5);
    ctx.textAlign = "right";
    text("Inside the soda machine", 1820, 106, 23, palette.ice, 400);
    ctx.textAlign = "left";
    title(["Soda,", "on tap."], "AT HOME", "Cold. Carbonated. Ready.", 0.5, 13.5, t);
    title(["Let’s look", "inside."], "OPEN THE MACHINE", "Four enclosure quadrants.", 13.5, 21.0, t);

    const systemTitle = between(t, 21.0, 21.6) * (1 - between(t, 37.3, 38));
    ctx.save(); ctx.globalAlpha = systemTitle;
    text("BUILT AROUND THE COLD", 100, 277, 18, palette.ice, 500);
    text("One compact", 96, 354, 52, palette.white, 600);
    text("system.", 96, 419, 52, palette.white, 600);
    ctx.restore();
    systemLabels(t);

    const closing = between(t, 37.5, 38.3);
    ctx.save(); ctx.globalAlpha = closing;
    text("01 / WATER", 100, 326, 18, palette.ice, 500);
    text("Follow", 95, 447, 88, palette.white, 600);
    text("the water.", 95, 553, 88, palette.white, 600);
    ctx.fillStyle = palette.orange;
    ctx.beginPath(); ctx.roundRect(100, 608, 60, 4, 2); ctx.fill();
    ctx.restore();

    ctx.strokeStyle = `${palette.ice}40`;
    ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(100, 969); ctx.lineTo(1820, 969); ctx.stroke();
    const caption = timeline.captions.find((c) => t >= c.start && t < c.end);
    if (caption) {
      ctx.textAlign = "center";
      text(caption.text, 960, 1017, 28, palette.white, 500);
      ctx.textAlign = "left";
    }
    const fade = timeline.full ? 0 : between(t, 40.8, timeline.duration);
    if (fade > 0) {
      ctx.globalAlpha = fade;
      ctx.fillStyle = palette.cobalt;
      ctx.fillRect(0, 0, 1920, 1080);
      ctx.globalAlpha = 1;
    }
    return canvas.toDataURL("image/jpeg", 0.97);
  }
  const film = timeline.full ? createFilmScenes({ tour, timeline, palette, view, canvas, ctx, logo,
    bounds, panelBodies, text, number }) : null;
  return { draw };
}
