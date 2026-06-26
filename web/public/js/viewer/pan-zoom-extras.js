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
//   inside the *default (fit) view* the user is currently zoomed. Both
//   boxes are screen-shaped: the outer box matches the container's
//   aspect (the wrapper IS the screen), the inner box represents the
//   sub-rectangle of the default view that the current pan/zoom is
//   showing. At fit, inner == outer. At 2× fit centered, inner is
//   the middle quarter. We don't clone the SVG content because the
//   goal is the "where" indicator, not a miniature preview. The
//   caller drives updates by calling minimap.update(transform) inside
//   pz.onTransformLive; the minimap caches the most recent transform
//   so its own ResizeObserver can re-render on container resize
//   without needing a pz reference.
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

export function makeMinimap(svgEl, container, obstacles) {
  const nat = naturalSize(svgEl);
  // Fit obstacles (container-local px rects), read live so the indicator's
  // "default view" rectangle tracks the same obstacle-aware fit PanZoom uses
  // (see PanZoom.fitScale). Absent ⇒ the original full-frame fit.
  const obs = obstacles || null;
  // If we can't measure the source, return a no-op shell — the caller
  // still gets a valid element to insert; it just won't update. (We
  // still need nat to compute the fit scale and centered fit-pan.)
  if (!nat.w || !nat.h) {
    const empty = document.createElement("div");
    empty.className = "pan-zoom-minimap";
    return { el: empty, update: () => {}, destroy: () => {} };
  }

  const wrap = document.createElement("div");
  wrap.className = "pan-zoom-minimap";

  const rect = document.createElement("div");
  rect.className = "pan-zoom-minimap-rect";
  wrap.appendChild(rect);

  // Cache the most recent transform so the ResizeObserver can redraw
  // without needing a pz reference. The caller passes the live transform
  // every time it changes; we just remember the latest.
  let lastTransform = { scale: 1, panX: 0, panY: 0 };

  function update(transform) {
    if (transform && transform.scale) lastTransform = transform;
    // Layout size (transform-invariant; the modal card animates scale on open).
    const W = container.clientWidth, H = container.clientHeight;
    if (!W || !H) return;

    // Outer box matches the container's aspect ratio (both views — fit
    // and current — live inside the same wrapper, so the box that
    // represents either of them is wrapper-shaped). Longest side
    // capped at MINIMAP_MAX. Computed here so device rotation /
    // container resize updates the outer box, not just the inner one.
    const aspect = W / H;
    let mW, mH;
    if (aspect >= 1) {
      mW = MINIMAP_MAX;
      mH = Math.round(MINIMAP_MAX / aspect);
    } else {
      mH = MINIMAP_MAX;
      mW = Math.round(MINIMAP_MAX * aspect);
    }
    wrap.style.width  = mW + "px";
    wrap.style.height = mH + "px";

    const t = lastTransform;
    if (!t.scale) return;

    // Default (fit) view parameters. Match PanZoom's obstacle-aware fit: the
    // largest centered box that clears the chrome, then centered in the wrapper.
    const fs = (window.PanZoom && window.PanZoom.fitScale)
      ? window.PanZoom.fitScale(W, H, nat.w, nat.h, obs)
      : Math.min(W / nat.w, H / nat.h);
    if (!fs) return;
    const fsPanX = (W - fs * nat.w) / 2;
    const fsPanY = (H - fs * nat.h) / 2;

    // Current viewport, expressed in *default-view* (= wrapper-at-fit)
    // coordinates. An SVG point sx maps to default-view x = sx*fs + fsPanX.
    // The current viewport spans SVG x in [-panX/scale, (W-panX)/scale],
    // so in default-view coords it spans
    //   [-panX*fs/scale + fsPanX, (W-panX)*fs/scale + fsPanX]
    // Width fs/scale * W — at fit (scale==fs) the inner box fills the
    // outer, at 2× fit it's half, etc.
    const dvX = -t.panX * fs / t.scale + fsPanX;
    const dvY = -t.panY * fs / t.scale + fsPanY;
    const dvW = W * fs / t.scale;
    const dvH = H * fs / t.scale;

    // Scale into minimap pixel coords. Aspect of the outer box matches
    // the wrapper, so a single scale factor handles both axes.
    const m = mW / W; // == mH / H within rounding

    // Clamp to outer-box bounds — pan/zoom can drift the viewport
    // outside the default-view rectangle (e.g. into the letterbox
    // margins when the SVG aspect doesn't match the wrapper), and we
    // don't want the indicator to float past the minimap edges.
    const x0 = Math.max(0, dvX * m);
    const y0 = Math.max(0, dvY * m);
    const x1 = Math.min(mW, (dvX + dvW) * m);
    const y1 = Math.min(mH, (dvY + dvH) * m);

    // -2 on width/height so the inner element's external size (content +
    // its own 1px border) lands at the outer's content edge instead of
    // 1px past it. Without this, at fit the inner's right + bottom
    // borders get clipped by the outer's overflow:hidden and only the
    // outer's border shows on those sides.
    rect.style.left   = x0 + "px";
    rect.style.top    = y0 + "px";
    rect.style.width  = Math.max(0, x1 - x0 - 2) + "px";
    rect.style.height = Math.max(0, y1 - y0 - 2) + "px";
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
