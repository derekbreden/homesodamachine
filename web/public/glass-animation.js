// GlassAnimation — vanilla JS / Canvas2D port of GlassAnimationView.swift
// and GlassAnimation.kt. All coordinates live in a 1024×1024 logical space
// and are scaled at render time. Cycle: 1.6s, 4 bubbles, sine-driven wave.
//
// Exposes a single global: mountGlassAnimation(canvas, options) -> { stop }.

(function () {
  'use strict';

  // 1024-space constants (verbatim from iOS/Android sources).
  var CYCLE_MS = 1600;
  var LIQUID_TOP_BASE = 347;
  var WAVE_AMPLITUDE = 9;
  var BUBBLE_BOTTOM = 740;

  // Liquid gradient stops — pink → magenta → violet. Theme.swift L24-26.
  var LIQUID_STOP_0 = 'rgb(233, 69, 96)';    // (0.914, 0.271, 0.376)
  var LIQUID_STOP_1 = 'rgb(194, 51, 115)';   // (0.761, 0.200, 0.451)
  var LIQUID_STOP_2 = 'rgb(123, 47, 247)';   // (0.482, 0.184, 0.969)

  // 4 bubbles. cx/r match the original SVG; phases keep them spread.
  // GlassAnimationView.swift L50-55 / GlassAnimation.kt L63-68.
  var BUBBLES = [
    { cx: 440, r: 42, phase: 0.00, strokeOpacity: 0.20, strokeWidth: 2.5 },
    { cx: 580, r: 35, phase: 0.20, strokeOpacity: 0.20, strokeWidth: 2.5 },
    { cx: 500, r: 30, phase: 0.42, strokeOpacity: 0.18, strokeWidth: 2.0 },
    { cx: 620, r: 26, phase: 0.62, strokeOpacity: 0.18, strokeWidth: 2.0 },
  ];

  // Bubble physics. Mirrors the Swift/Kotlin three-region cycle:
  //   bt < 0.75 — rise from BUBBLE_BOTTOM to bubbleTop, ease-out (1 - (1-x)^1.5),
  //               grow 1.0→1.15, lateral wobble ±8 at 3π over the rise.
  //   bt < 0.85 — pop at surface: r 1.15→0.65, opacity 0.8→0, x locked.
  //   else      — invisible (respawn delay).
  function bubbleState(b, t) {
    var bt = (t + b.phase) % 1;
    if (bt < 0) bt += 1;
    var bubbleTop = LIQUID_TOP_BASE + b.r + WAVE_AMPLITUDE;

    if (bt < 0.75) {
      var riseT = bt / 0.75;
      var easeT = 1 - Math.pow(1 - riseT, 1.5);
      var cy = BUBBLE_BOTTOM - easeT * (BUBBLE_BOTTOM - bubbleTop);
      var cx = b.cx + 8 * Math.sin(riseT * Math.PI * 3 + b.phase * 10);
      var r = b.r * (1.0 + 0.15 * riseT);
      return { cx: cx, cy: cy, r: r, opacity: 0.8 };
    }
    if (bt < 0.85) {
      var popT = (bt - 0.75) / 0.10;
      return {
        cx: b.cx,
        cy: bubbleTop,
        r: b.r * (1.15 - 0.5 * popT),
        opacity: 0.8 * (1 - popT),
      };
    }
    return null;
  }

  // Quad bezier from (x0,y0) via control (cx,cy) to (x,y).
  function quad(ctx, cx, cy, x, y) {
    ctx.quadraticCurveTo(cx, cy, x, y);
  }

  // Glass body. Matches AppIcon.svg / GlassAnimationView.swift L60-68.
  function buildGlassPath(ctx, s) {
    ctx.beginPath();
    ctx.moveTo(310 * s, 247 * s);
    ctx.lineTo(340 * s, 747 * s);
    quad(ctx, 345 * s, 777 * s, 380 * s, 777 * s);
    ctx.lineTo(644 * s, 777 * s);
    quad(ctx, 679 * s, 777 * s, 684 * s, 747 * s);
    ctx.lineTo(714 * s, 247 * s);
    ctx.closePath();
  }

  // Liquid body with wavy top edge — sine-shifted bezier control points.
  // GlassAnimationView.swift L78-94.
  function buildLiquidPath(ctx, s, waveShift) {
    ctx.beginPath();
    ctx.moveTo(300 * s, (347 + waveShift) * s);
    quad(ctx, 400 * s, (327 + waveShift) * s, 512 * s, (352 - waveShift) * s);
    quad(ctx, 624 * s, (377 - waveShift) * s, 724 * s, (342 + waveShift) * s);
    ctx.lineTo(724 * s, 800 * s);
    ctx.lineTo(300 * s, 800 * s);
    ctx.closePath();
  }

  // Meniscus highlight — closed band that follows the wavy edge and the
  // same wave shape ~20 units lower. GlassAnimationView.swift L110-130.
  function buildWavePath(ctx, s, waveShift) {
    ctx.beginPath();
    ctx.moveTo(300 * s, (347 + waveShift) * s);
    quad(ctx, 400 * s, (327 + waveShift) * s, 512 * s, (352 - waveShift) * s);
    quad(ctx, 624 * s, (377 - waveShift) * s, 724 * s, (342 + waveShift) * s);
    ctx.lineTo(724 * s, (367 + waveShift) * s);
    quad(ctx, 624 * s, (397 - waveShift) * s, 512 * s, (372 - waveShift) * s);
    quad(ctx, 400 * s, (347 + waveShift) * s, 300 * s, (367 + waveShift) * s);
    ctx.closePath();
  }

  function drawFrame(ctx, w, h, t) {
    var s = Math.min(w, h) / 1024;
    ctx.clearRect(0, 0, w, h);

    // 1. Glass body fill (white @ 0.06).
    buildGlassPath(ctx, s);
    ctx.fillStyle = 'rgba(255, 255, 255, 0.06)';
    ctx.fill();

    // 2. Clipped layer: liquid + meniscus + bubbles.
    ctx.save();
    buildGlassPath(ctx, s);
    ctx.clip();

    var waveShift = Math.sin(t * 2 * Math.PI) * WAVE_AMPLITUDE;

    // 2a. Liquid fill with the 3-stop gradient.
    buildLiquidPath(ctx, s, waveShift);
    var grad = ctx.createLinearGradient(300 * s, 327 * s, 724 * s, 800 * s);
    grad.addColorStop(0, LIQUID_STOP_0);
    grad.addColorStop(0.5, LIQUID_STOP_1);
    grad.addColorStop(1, LIQUID_STOP_2);
    ctx.fillStyle = grad;
    ctx.fill();

    // 2b. Surface highlight wave (white @ 0.12).
    buildWavePath(ctx, s, waveShift);
    ctx.fillStyle = 'rgba(255, 255, 255, 0.12)';
    ctx.fill();

    // 2c. Bubbles.
    for (var i = 0; i < BUBBLES.length; i++) {
      var b = BUBBLES[i];
      var st = bubbleState(b, t);
      if (!st) continue;
      // iOS guard: skip anything outside the glass interior y-range.
      if (st.cy <= 250 || st.cy >= 780) continue;

      var cx = st.cx * s;
      var cy = st.cy * s;
      var r = st.r * s;

      // iOS uses a layer with opacity = st.opacity multiplying both fill and
      // stroke alphas. Canvas2D's globalAlpha is the natural analog.
      ctx.save();
      ctx.globalAlpha = st.opacity;

      var rg = ctx.createRadialGradient(cx, cy, 0, cx, cy, r);
      rg.addColorStop(0, 'rgba(255, 255, 255, 0.5)');
      rg.addColorStop(1, 'rgba(255, 255, 255, 0.1)');
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, 2 * Math.PI);
      ctx.fillStyle = rg;
      ctx.fill();

      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, 2 * Math.PI);
      ctx.strokeStyle = 'rgba(255, 255, 255, ' + b.strokeOpacity + ')';
      ctx.lineWidth = b.strokeWidth * s;
      ctx.stroke();

      ctx.restore();
    }

    ctx.restore();

    // 3. Glass body stroke (white @ 0.25, width 4).
    buildGlassPath(ctx, s);
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.25)';
    ctx.lineWidth = 4 * s;
    ctx.lineCap = 'butt';
    ctx.lineJoin = 'miter';
    ctx.stroke();

    // 4. Glass rim highlight (white @ 0.35, width 5, round caps).
    ctx.beginPath();
    ctx.moveTo(310 * s, 247 * s);
    ctx.lineTo(714 * s, 247 * s);
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.35)';
    ctx.lineWidth = 5 * s;
    ctx.lineCap = 'round';
    ctx.stroke();

    // 5. Glass left-edge highlight (white @ 0.10, width 8, round caps).
    ctx.beginPath();
    ctx.moveTo(314 * s, 257 * s);
    ctx.lineTo(342 * s, 737 * s);
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.10)';
    ctx.lineWidth = 8 * s;
    ctx.lineCap = 'round';
    ctx.stroke();
    ctx.lineCap = 'butt';

    // 6. Glass surface gradient overlay (white 0.15 @ 0 → 0 @ 0.4).
    buildGlassPath(ctx, s);
    var surf = ctx.createLinearGradient(310 * s, 0, 714 * s, 0);
    surf.addColorStop(0, 'rgba(255, 255, 255, 0.15)');
    surf.addColorStop(0.4, 'rgba(255, 255, 255, 0)');
    ctx.fillStyle = surf;
    ctx.fill();
  }

  function mountGlassAnimation(canvas, options) {
    if (!(canvas instanceof HTMLCanvasElement)) {
      throw new Error('mountGlassAnimation: canvas must be an HTMLCanvasElement');
    }
    options = options || {};

    var ctx = canvas.getContext('2d');
    var rafId = 0;
    var running = false;
    var visible = true;
    var startMs = performance.now();
    var pausedAccum = 0;     // total ms paused
    var pauseStart = 0;      // timestamp when current pause started

    function syncSize() {
      var dpr = window.devicePixelRatio || 1;
      var rect = canvas.getBoundingClientRect();
      var cssW = rect.width || canvas.clientWidth || canvas.width;
      var cssH = rect.height || canvas.clientHeight || canvas.height;
      var pxW = Math.max(1, Math.round(cssW * dpr));
      var pxH = Math.max(1, Math.round(cssH * dpr));
      if (canvas.width !== pxW) canvas.width = pxW;
      if (canvas.height !== pxH) canvas.height = pxH;
    }

    function frame(now) {
      if (!running) return;
      syncSize();
      var elapsed = now - startMs - pausedAccum;
      var t = ((elapsed % CYCLE_MS) + CYCLE_MS) % CYCLE_MS / CYCLE_MS;
      drawFrame(ctx, canvas.width, canvas.height, t);
      rafId = requestAnimationFrame(frame);
    }

    function start() {
      if (running) return;
      if (pauseStart) {
        pausedAccum += performance.now() - pauseStart;
        pauseStart = 0;
      }
      running = true;
      rafId = requestAnimationFrame(frame);
    }

    function pause() {
      if (!running) return;
      running = false;
      if (rafId) cancelAnimationFrame(rafId);
      rafId = 0;
      pauseStart = performance.now();
    }

    function evaluate() {
      var shouldRun = visible && !document.hidden;
      if (shouldRun && !running) start();
      else if (!shouldRun && running) pause();
    }

    var io = null;
    if (typeof IntersectionObserver === 'function') {
      io = new IntersectionObserver(function (entries) {
        for (var i = 0; i < entries.length; i++) {
          if (entries[i].target === canvas) visible = entries[i].isIntersecting;
        }
        evaluate();
      });
      io.observe(canvas);
    }

    function onVis() { evaluate(); }
    document.addEventListener('visibilitychange', onVis);

    start();

    return {
      stop: function () {
        running = false;
        if (rafId) cancelAnimationFrame(rafId);
        rafId = 0;
        if (io) io.disconnect();
        document.removeEventListener('visibilitychange', onVis);
      },
    };
  }

  // Single global export (no module system in this site).
  if (typeof window !== 'undefined') {
    window.mountGlassAnimation = mountGlassAnimation;
  } else if (typeof globalThis !== 'undefined') {
    globalThis.mountGlassAnimation = mountGlassAnimation;
  }
})();
