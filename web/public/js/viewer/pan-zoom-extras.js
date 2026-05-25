// Reset button + minimap helpers for the 2D PanZoom modal surfaces (mermaid
// and drawings). The 3D STEP/DXF surface has its own reset (cad-detail.js'
// makeResetViewButton, which lerps the camera) and the ViewCube gizmo for
// orientation; this module is the 2D analog so the two surfaces feel
// equivalent.
//
// makeResetButton(pz, { transformKey }) — a bottom-right "Reset view"
//   button that calls pz.fit() and clears the saved transform so a
//   subsequent open restarts from fit-to-container.
//
// makeMinimap(svgEl, container) — a top-right minimap showing where
//   inside the natural SVG bounds the user is currently zoomed. The
//   minimap itself is just the bounding rectangle (preserving the source's
//   aspect ratio) with a viewport rectangle drawn over it; we don't clone
//   the SVG content because the goal is the "where" indicator, not a
//   miniature preview. The caller drives updates by calling
//   minimap.update(transform) inside pz.onTransformLive; the minimap
//   caches the most recent transform so its own ResizeObserver can
//   re-render on container resize without needing a pz reference.
//
// Both return DOM elements + (for the minimap) a refresh handle the
// caller can hold onto for window-resize updates.

const MINIMAP_MAX = 140;

function naturalSize(svgEl) {
  const vb = svgEl.viewBox && svgEl.viewBox.baseVal;
  if (vb && vb.width && vb.height) return { w: vb.width, h: vb.height };
  const w = parseFloat(svgEl.getAttribute("width")) || 0;
  const h = parseFloat(svgEl.getAttribute("height")) || 0;
  return { w, h };
}

export function makeResetButton(pz, opts = {}) {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "reset-view pan-zoom-reset";
  btn.textContent = "Reset view";
  btn.title = "Reset to default view";
  btn.addEventListener("click", (e) => {
    e.stopPropagation();
    if (opts.transformKey) {
      try { localStorage.removeItem(opts.transformKey); } catch {}
    }
    if (pz && typeof pz.fit === "function") pz.fit();
  });
  return btn;
}

export function makeMinimap(svgEl, container) {
  const nat = naturalSize(svgEl);
  // If we can't measure the source, return a no-op shell — the caller
  // still gets a valid element to insert; it just won't update.
  if (!nat.w || !nat.h) {
    const empty = document.createElement("div");
    empty.className = "pan-zoom-minimap";
    return { el: empty, update: () => {}, destroy: () => {} };
  }

  // Size the minimap so its longest side is MINIMAP_MAX and aspect
  // matches the source. Wide drawings get a wide rectangle; tall ones
  // get a tall one. Either way the math below stays clean.
  const aspect = nat.w / nat.h;
  let mW, mH;
  if (aspect >= 1) {
    mW = MINIMAP_MAX;
    mH = Math.round(MINIMAP_MAX / aspect);
  } else {
    mH = MINIMAP_MAX;
    mW = Math.round(MINIMAP_MAX * aspect);
  }

  const wrap = document.createElement("div");
  wrap.className = "pan-zoom-minimap";
  wrap.style.width = mW + "px";
  wrap.style.height = mH + "px";

  const rect = document.createElement("div");
  rect.className = "pan-zoom-minimap-rect";
  wrap.appendChild(rect);

  // Cache the most recent transform so the ResizeObserver can redraw
  // without needing a pz reference. The caller passes the live transform
  // every time it changes; we just remember the latest.
  let lastTransform = { scale: 1, panX: 0, panY: 0 };

  function update(transform) {
    if (transform && transform.scale) lastTransform = transform;
    const cb = container.getBoundingClientRect();
    if (!cb.width || !cb.height) return;
    const t = lastTransform;
    if (!t.scale) return;

    // Map from natural SVG coords to minimap pixel coords.
    // (Aspect was preserved when sizing the minimap, so a single scale
    // factor handles both axes.)
    const m = mW / nat.w; // == mH / nat.h within rounding

    // Visible region in natural coords. The main view shows
    //   natural_x in [-panX/scale, (cb.w - panX)/scale]
    //   natural_y in [-panY/scale, (cb.h - panY)/scale]
    const visX = -t.panX / t.scale;
    const visY = -t.panY / t.scale;
    const visW = cb.width / t.scale;
    const visH = cb.height / t.scale;

    // Clamp to the natural bounds — pan/zoom can place the viewport
    // beyond the content edges and we don't want the rect to float
    // outside the minimap box.
    const x0 = Math.max(0, visX);
    const y0 = Math.max(0, visY);
    const x1 = Math.min(nat.w, visX + visW);
    const y1 = Math.min(nat.h, visY + visH);
    const w = Math.max(0, x1 - x0);
    const h = Math.max(0, y1 - y0);

    rect.style.left   = (x0 * m) + "px";
    rect.style.top    = (y0 * m) + "px";
    rect.style.width  = (w * m) + "px";
    rect.style.height = (h * m) + "px";
  }

  // Initial draw — fit() will fire onTransformLive once the container
  // settles, but draw now so the indicator isn't a blank box during the
  // open animation.
  update();

  let ro = null;
  if (typeof ResizeObserver === "function") {
    ro = new ResizeObserver(() => update());
    ro.observe(container);
  }

  function destroy() {
    if (ro) { try { ro.disconnect(); } catch {} ro = null; }
  }

  return { el: wrap, update, destroy };
}
