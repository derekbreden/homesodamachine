import * as THREE from "three";

export function mountTags(host) {
  const layer = document.createElement("div");
  layer.className = "tour-callout-layer";
  layer.style.cssText = "position:absolute;inset:0;pointer-events:none;z-index:5";
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("aria-hidden", "true");
  svg.style.cssText = "position:absolute;width:100%;height:100%;overflow:visible";
  const line = document.createElementNS(svg.namespaceURI, "path");
  line.setAttribute("fill", "none");
  line.setAttribute("stroke", "var(--tour-accent,#86dfd3)");
  line.setAttribute("stroke-width", "1.2");
  const dot = document.createElementNS(svg.namespaceURI, "circle");
  dot.setAttribute("r", "3");
  dot.setAttribute("fill", "var(--tour-accent,#86dfd3)");
  svg.append(line, dot);
  const label = document.createElement("div");
  label.className = "tour-subject-label";
  label.style.cssText = "position:absolute;padding:7px 11px;border-left:2px solid var(--tour-accent,#86dfd3);background:rgba(16,25,35,.94);color:#f4f7fb;font-size:12px;line-height:1.3;letter-spacing:.02em;max-width:180px;border-radius:0 4px 4px 0";
  layer.append(svg, label);
  host.append(layer);
  const point = new THREE.Vector3();
  return {
    update({ camera, rect, box, text, active, alpha = 1 }) {
      if (!active || !box || box.isEmpty()) { layer.style.opacity = "0"; return; }
      camera.updateMatrixWorld();
      box.getCenter(point).project(camera);
      if (point.z > 1 || point.z < -1 || Math.abs(point.x) > 1 || Math.abs(point.y) > 1) {
        layer.style.opacity = "0"; return;
      }
      const x = (point.x * .5 + .5) * rect.width;
      const y = (-point.y * .5 + .5) * rect.height;
      const right = x < rect.width * .55;
      const labelX = right ? Math.min(x + 55, rect.width - 185) : Math.max(16, x - 200);
      const labelY = THREE.MathUtils.clamp(y - 75, 65, rect.height - 50);
      label.textContent = text;
      label.style.left = `${labelX}px`;
      label.style.top = `${labelY}px`;
      const endX = right ? labelX : labelX + label.offsetWidth;
      const endY = labelY + label.offsetHeight / 2;
      line.setAttribute("d", `M${x},${y} L${endX - (right ? 15 : -15)},${endY} L${endX},${endY}`);
      dot.setAttribute("cx", x); dot.setAttribute("cy", y);
      layer.style.opacity = String(alpha);
    },
    hide() { layer.style.opacity = "0"; },
  };
}
