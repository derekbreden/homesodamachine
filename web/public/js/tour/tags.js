import * as THREE from "three";

const namespace = "http://www.w3.org/2000/svg";
const clamp = THREE.MathUtils.clamp;
const accent = "var(--tour-accent,#ff9152)";
const colorOf = (color) => typeof color === "number"
  ? `#${color.toString(16).padStart(6, "0")}` : color || accent;

export function mountTags(host) {
  const layer = document.createElement("div");
  layer.className = "tour-callout-layer";
  layer.setAttribute("aria-hidden", "true");
  layer.style.cssText = "position:absolute;inset:0;pointer-events:none;z-index:5;opacity:0";
  const svg = document.createElementNS(namespace, "svg");
  svg.style.cssText = "position:absolute;width:100%;height:100%;overflow:hidden";
  layer.append(svg);
  host.append(layer);

  const labels = new Map();
  const point = new THREE.Vector3();
  const corner = new THREE.Vector3();

  function labelFor(id, text, compact) {
    let item = labels.get(id);
    if (!item) {
      const group = document.createElementNS(namespace, "g");
      const line = document.createElementNS(namespace, "path");
      line.setAttribute("fill", "none");
      line.setAttribute("stroke-width", "1");
      const dot = document.createElementNS(namespace, "circle");
      const label = document.createElement("div");
      label.className = "tour-subject-label";
      label.dataset.subjectId = id;
      group.append(line, dot);
      svg.append(group);
      layer.append(label);
      item = { label, group, line, dot, text: null, compact: null, width: 0, height: 0 };
      labels.set(id, item);
    }
    if (item.text !== text || item.compact !== compact) {
      item.label.textContent = text;
      item.label.style.fontSize = compact ? "11px" : "12px";
      item.text = text;
      item.compact = compact;
      item.width = item.label.offsetWidth;
      item.height = item.label.offsetHeight;
    }
    item.label.style.visibility = "visible";
    item.group.style.visibility = "visible";
    return item;
  }

  function hideLabels() {
    for (const item of labels.values()) {
      item.label.style.visibility = "hidden";
      item.group.style.visibility = "hidden";
    }
  }

  function project(box, camera, rect) {
    if (!box || box.isEmpty()) return null;
    box.getCenter(point).project(camera);
    if (!Number.isFinite(point.x + point.y + point.z) || point.z > 1 || point.z < -1) return null;
    const x = (point.x * .5 + .5) * rect.width;
    const y = (-point.y * .5 + .5) * rect.height;
    let left = Infinity, right = -Infinity, top = Infinity, bottom = -Infinity;
    for (let i = 0; i < 8; i++) {
      corner.set(i & 1 ? box.max.x : box.min.x,
        i & 2 ? box.max.y : box.min.y, i & 4 ? box.max.z : box.min.z).project(camera);
      const px = (corner.x * .5 + .5) * rect.width;
      const py = (-corner.y * .5 + .5) * rect.height;
      left = Math.min(left, px); right = Math.max(right, px);
      top = Math.min(top, py); bottom = Math.max(bottom, py);
    }
    return { x, y, left, right, top, bottom };
  }

  function place(item, projection, x, y, side, active, color, rect) {
    item.label.style.transform = `translate(${x.toFixed(1)}px,${y.toFixed(1)}px)`;
    item.label.dataset.active = String(!!active);
    item.label.style.borderBottomColor = active ? color : "var(--border)";
    item.line.setAttribute("stroke", color);
    item.line.setAttribute("opacity", active ? ".8" : ".28");
    item.dot.setAttribute("fill", color);
    item.dot.setAttribute("opacity", active ? "1" : ".5");
    item.dot.setAttribute("r", active ? "2.5" : "1.7");
    const endX = side === "left" ? x + item.width : x;
    const endY = y + item.height / 2;
    const dx = endX - projection.x, dy = endY - projection.y;
    const halfWidth = Math.max(1, (projection.right - projection.left) / 2);
    const halfHeight = Math.max(1, (projection.bottom - projection.top) / 2);
    const edge = Math.min(1, .8 / Math.max(Math.abs(dx) / halfWidth, Math.abs(dy) / halfHeight));
    const startX = clamp(projection.x + dx * edge, 5, rect.width - 5);
    const startY = clamp(projection.y + dy * edge, 5, rect.height - 5);
    const elbowX = endX + (side === "left" ? 12 : -12);
    item.line.setAttribute("d", `M${startX.toFixed(1)},${startY.toFixed(1)} L${elbowX.toFixed(1)},${endY.toFixed(1)} L${endX.toFixed(1)},${endY.toFixed(1)}`);
    item.dot.setAttribute("cx", startX.toFixed(1));
    item.dot.setAttribute("cy", startY.toFixed(1));
  }

  function multiple(subjects, camera, rect) {
    const compact = rect.width < 600;
    const margin = compact ? 12 : 25;
    const top = Math.min(compact ? 68 : 82, rect.height * .22);
    const bottom = Math.max(top, rect.height - 18);
    const pins = subjects.map((subject) => {
      const projection = project(subject.box, camera, rect);
      if (!projection) return null;
      const item = labelFor(subject.id, subject.text, compact);
      return { subject, projection, item };
    }).filter(Boolean).sort((a, b) => a.projection.x - b.projection.x
      || a.subject.id.localeCompare(b.subject.id));
    const split = Math.ceil(pins.length / 2);
    for (const [side, column] of [["left", pins.slice(0, split)], ["right", pins.slice(split)]]) {
      column.sort((a, b) => a.projection.y - b.projection.y
        || a.subject.id.localeCompare(b.subject.id));
      const gap = 12;
      let cursor = top;
      for (const pin of column) {
        pin.y = Math.max(cursor, clamp(pin.projection.y - pin.item.height / 2, top, bottom - pin.item.height));
        cursor = pin.y + pin.item.height + gap;
      }
      cursor = bottom;
      for (let i = column.length - 1; i >= 0; i--) {
        const pin = column[i];
        pin.y = Math.min(pin.y, cursor - pin.item.height);
        cursor = pin.y - gap;
      }
      for (const { subject, projection, item, y } of column) {
        const x = side === "left" ? margin : rect.width - margin - item.width;
        place(item, projection, x, y, side, subject.active, colorOf(subject.color), rect);
      }
    }
    return pins.length > 0;
  }

  return {
    update({ camera, rect, box, text, active, subjects, alpha = 1 }) {
      hideLabels();
      if (alpha <= 0 || rect.width <= 0 || rect.height <= 0) { layer.style.opacity = "0"; return; }
      camera.updateMatrixWorld();
      if (subjects?.length) {
        layer.style.opacity = multiple(subjects, camera, rect) ? String(alpha) : "0";
        return;
      }
      const projection = active && project(box, camera, rect);
      if (!projection || projection.x < 0 || projection.x > rect.width
        || projection.y < 0 || projection.y > rect.height) { layer.style.opacity = "0"; return; }
      const item = labelFor("single", text || "", rect.width < 600);
      const side = projection.x < rect.width * .55 ? "right" : "left";
      const x = clamp(side === "right" ? projection.x + 55 : projection.x - item.width - 55,
        16, rect.width - item.width - 16);
      const y = clamp(projection.y - 75, Math.min(65, rect.height * .22), rect.height - item.height - 18);
      place(item, projection, x, y, side, true, accent, rect);
      layer.style.opacity = String(alpha);
    },
    hide() { layer.style.opacity = "0"; },
  };
}
