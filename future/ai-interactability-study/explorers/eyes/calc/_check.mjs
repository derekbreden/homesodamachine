#!/usr/bin/env node
// check-scene.mjs - open scene pages headlessly, report errors, blank canvases and dead controls.
//
//   node tools/check-scene.mjs <sceneIdOrDir>... [--all] [--shot] [--exercise] [--page] [--size=1280x800]
//
//   --shot      save thumbs/<id>.png (960x600, stage only, default view). With --exercise also saves
//               thumbs/<id>--<controlId>-max.png (full page at --size, control at its max/last value).
//   --exercise  drive every control from window.__controls (min/max/mid/initial, toggle both ways, every
//               select/radio option, every button) and report which ones changed the frame. A control
//               declared with noVisual:true (or visual:false) or disabled (app.ui.enable(id,false)) when the
//               checker reaches it is exercised for errors but never reported as "no visible effect".
//   --page      also save thumbs/<id>--page.png: the whole page at --size (use --size=390x844 for phones).
//   --all       every scenes/*/index.html, one after another.
//
// Each invocation launches its OWN headless Chrome and closes it in `finally`; it never touches other
// Chrome processes, so several agents can run it at once. Works from file:// (no server).
// Exit code 1 only for hard errors: exceptions, page never ready, blank canvas, failed loads.
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = '/Users/derekbredensteiner/Developer/homesodamachine/future/ai-interactability-study/tools';
const STUDY = path.resolve(HERE, '..');
const SCENES = path.join(STUDY, 'scenes');
const THUMBS = path.join(STUDY, 'thumbs');
const PUPPETEER_BASE = '/Users/derekbredensteiner/Developer/homesodamachine/tools/render/';

// ---------------------------------------------------------------- args
const args = process.argv.slice(2);
const flags = new Set(args.filter(a => a.startsWith('--') && !a.includes('=')));
const kv = Object.fromEntries(args.filter(a => a.startsWith('--') && a.includes('=')).map(a => a.slice(2).split('=')));
const positional = args.filter(a => !a.startsWith('--'));
if (flags.has('--help') || (!positional.length && !flags.has('--all'))) {
  console.log(fs.readFileSync(fileURLToPath(import.meta.url), 'utf8').split('\n').slice(1, 17).map(l => l.replace(/^\/\/ ?/, '')).join('\n'));
  process.exit(flags.has('--help') ? 0 : 2);
}
const [VW, VH] = (kv.size || '1280x800').split('x').map(Number);
const SHOT = flags.has('--shot'), EXERCISE = flags.has('--exercise'), PAGE = flags.has('--page');

function resolveScenes() {
  const out = [];
  if (flags.has('--all')) {
    for (const d of fs.readdirSync(SCENES).sort()) if (fs.existsSync(path.join(SCENES, d, 'index.html'))) out.push({ id: d, file: path.join(SCENES, d, 'index.html') });
  }
  for (const a of positional) {
    let file = null, id = null;
    const cands = [a, path.join(a, 'index.html'), path.join(SCENES, a, 'index.html'), path.resolve(STUDY, a, 'index.html')];
    for (const c of cands) { if (fs.existsSync(c) && fs.statSync(c).isFile() && c.endsWith('.html')) { file = path.resolve(c); break; } }
    if (file) id = path.basename(path.dirname(file));
    out.push({ id: id || a, file });
  }
  const seen = new Set();
  return out.filter(s => (seen.has(s.id) ? false : seen.add(s.id)));
}

async function loadPuppeteer() {
  const require = createRequire(PUPPETEER_BASE);
  try { const mod = await import(pathToFileURL(require.resolve('puppeteer')).href); return mod.default || mod; }
  catch (e) { console.error('Cannot load puppeteer from ' + PUPPETEER_BASE + ': ' + e.message); process.exit(2); }
}

// ---------------------------------------------------------------- in-page helpers (serialised into the page)
const PAGE_FNS = {
  frames: n => new Promise(res => { let k = 0; const step = () => (++k >= n ? res() : requestAnimationFrame(step)); requestAnimationFrame(step); }),
  // Full-resolution copy of the stage canvas is kept IN the page under `key` (only numbers travel back),
  // plus a hash of the overlay DOM (labels, insets, io panel, corner inset) so DOM-only changes count too.
  sample: key => {
    window.__snaps = window.__snaps || {};
    const stage = document.querySelector('#wk-stage') || document.body;
    const cv = stage.querySelector('canvas');
    let content = 0, data = null;
    if (cv && cv.width > 0) {
      const t = document.createElement('canvas'); t.width = cv.width; t.height = cv.height;
      const x = t.getContext('2d', { willReadFrequently: true }); x.drawImage(cv, 0, 0);
      data = x.getImageData(0, 0, t.width, t.height).data;
      const bg = [data[0], data[1], data[2]]; let n = 0;
      for (let i = 0; i < data.length; i += 4 * 37) { n++; if (Math.abs(data[i] - bg[0]) + Math.abs(data[i + 1] - bg[1]) + Math.abs(data[i + 2] - bg[2]) > 24) content++; }
      content = content / n;
    }
    const io = document.querySelector('.wk-io');
    // custom panels (app.ui.panel) count as visible output too: their markup and any canvas they draw on
    const csig = c => { try { const t = document.createElement('canvas'); t.width = 24; t.height = 16; const x = t.getContext('2d'); x.drawImage(c, 0, 0, 24, 16); const d = x.getImageData(0, 0, 24, 16).data; let q = 7; for (let i = 0; i < d.length; i++) q = ((q << 5) - q + d[i]) | 0; return q; } catch (e) { return 0; } };
    const panels = Array.from(document.querySelectorAll('.wk-panel')).map(p => p.innerHTML + Array.from(p.querySelectorAll('canvas')).map(csig).join(',')).join('|');
    const s = stage.innerHTML + (io ? io.innerHTML : '') + panels;
    let hsh = 5381; for (let i = 0; i < s.length; i++) hsh = ((hsh << 5) + hsh + s.charCodeAt(i)) | 0;
    const kids = Array.from(stage.querySelectorAll('*')).filter(e => { const r = e.getBoundingClientRect(); return r.width > 4 && r.height > 4; }).length;
    window.__snaps[key] = { data: data, dom: hsh };
    return { content: content, hasCanvas: !!cv, dom: hsh, visibleEls: kids };
  },
  diff: (ka, kb) => {
    const a = window.__snaps[ka], b = window.__snaps[kb];
    if (!a || !b) return { pixels: 0, dom: false };
    let pixels = 0;
    if (a.data && b.data && a.data.length === b.data.length) {
      for (let i = 0; i < a.data.length; i += 4) if (Math.abs(a.data[i] - b.data[i]) + Math.abs(a.data[i + 1] - b.data[i + 1]) + Math.abs(a.data[i + 2] - b.data[i + 2]) > 30) pixels++;
    }
    return { pixels: pixels, dom: a.dom !== b.dom };
  },
};
const frames = (page, n = 2) => page.evaluate(PAGE_FNS.frames, n);
let snapN = 0;
const sample = async (page, key) => { const k = key || 's' + (snapN++ % 6); const r = await page.evaluate(PAGE_FNS.sample, k); r.key = k; return r; };
const lumaDiff = (page, a, b) => page.evaluate(PAGE_FNS.diff, a.key, b.key);
const changed = d => d.pixels >= 12 || d.dom;
const sleep = ms => new Promise(r => setTimeout(r, ms));

// ---------------------------------------------------------------- one scene
async function checkScene(browser, scene) {
  const rep = { id: scene.id, file: scene.file, ok: true, errors: [], warnings: [], notes: [], controls: [], size: [VW, VH] };
  const hard = m => { rep.errors.push(m); rep.ok = false; };
  if (!scene.file) { hard('scene not found: ' + scene.id); return rep; }
  const t0 = Date.now();
  const page = await browser.newPage();
  const log = { console: [], pageerrors: [], failed: [] };
  page.on('console', m => { const t = m.type(); if (t === 'error' || t === 'warning') log.console.push({ type: t, text: m.text() }); });
  page.on('pageerror', e => log.pageerrors.push(String((e && e.message) || e)));
  page.on('requestfailed', r => { if (!/favicon/.test(r.url())) log.failed.push(r.url() + ' ' + ((r.failure() && r.failure().errorText) || '')); });
  page.on('response', r => { if (r.status() >= 400 && !/favicon/.test(r.url())) log.failed.push(r.status() + ' ' + r.url()); });
  try {
    await page.setViewport({ width: VW, height: VH, deviceScaleFactor: 1 });
    try { await page.goto(pathToFileURL(scene.file).href, { waitUntil: 'load', timeout: 300000 }); }
    catch (e) { hard('page failed to load: ' + e.message); return rep; }
    let ready = true;
    try { await page.waitForFunction(() => window.__sceneReady === true, { timeout: 300000 }); } catch (e) { ready = false; hard('window.__sceneReady never became true (15 s)'); }
    rep.readyMs = Date.now() - t0;
    await sleep(250); await frames(page, 3);
    const info = await page.evaluate(() => ({
      title: document.title, sceneErrors: (window.__sceneErrors || []).slice(), controls: JSON.parse(JSON.stringify(window.__controls || [])),
      custom: !!(window.__app && window.__app.custom), hasApp: !!window.__app, badges: window.__badges || [],
      insets: window.__app && window.__app.inset ? window.__app.inset.list() : [], sections: Array.from(document.querySelectorAll('.wk-sec')).map(s => s.dataset.sec),
      overflowX: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
    }));
    rep.title = info.title; rep.custom = info.custom; rep.insets = info.insets; rep.sections = info.sections; rep.badges = info.badges;
    if (!info.hasApp) hard('no WK.app on the page (window.__app missing)');
    info.sceneErrors.forEach(e => hard('scene error: ' + e));
    if (info.overflowX) rep.warnings.push('page scrolls horizontally at ' + VW + 'x' + VH + ' (layout overflow)');

    // blank check
    const s0 = await sample(page);
    rep.content = +s0.content.toFixed(3);
    if (ready) {
      if (info.custom) { if (s0.visibleEls < 3) hard('custom stage has no visible content'); }
      else if (!s0.hasCanvas) hard('no WebGL canvas in the stage');
      else if (s0.content < 0.01) hard('canvas looks blank (content ' + (s0.content * 100).toFixed(2) + '% of cells differ from the background)');
    }
    // idle animation? (makes pixel diffs unreliable)
    await sleep(300); const s1 = await sample(page);
    const d01 = await lumaDiff(page, s0, s1);
    rep.animated = d01.pixels >= 12;

    if (PAGE) { const f = path.join(THUMBS, scene.id + '--page.png'); await page.screenshot({ path: f }); rep.notes.push('saved ' + path.relative(STUDY, f)); }
    if (SHOT && ready) {
      await page.setViewport({ width: 960, height: 600, deviceScaleFactor: 1 });
      await page.evaluate(() => document.querySelector('.wk-app').classList.add('wk-thumb'));
      await sleep(200); await frames(page, 4);
      const f = path.join(THUMBS, scene.id + '.png'); fs.mkdirSync(THUMBS, { recursive: true });
      await page.screenshot({ path: f });
      rep.thumb = path.relative(STUDY, f);
      await page.evaluate(() => document.querySelector('.wk-app').classList.remove('wk-thumb'));
      await page.setViewport({ width: VW, height: VH, deviceScaleFactor: 1 });
      await sleep(200); await frames(page, 3);
    }

    // exercise controls
    if (EXERCISE && ready) {
      const nErr0 = () => page.evaluate(() => (window.__sceneErrors || []).length);
      const setCtl = (id, v) => page.evaluate((i, val) => window.__setControl(i, val), id, v);
      await page.evaluate(() => window.__resetAll && window.__resetAll()); await frames(page, 2);
      const base = await sample(page, 'base');
      for (const c of info.controls) {
        const r = { id: c.id, type: c.type, kind: c.kind, noVisual: !!c.noVisual, effect: null, errors: [] };
        r.disabledAtStart = await page.evaluate(id => { const e = document.querySelector(`[data-wk-id="${id}"]`); return !!(e && e.classList.contains('is-disabled')); }, c.id);
        const e0 = log.pageerrors.length, se0 = await nErr0();
        let vals = [];
        if (c.type === 'slider') vals = [c.min, c.max, +((c.min + c.max) / 2).toFixed(4), c.value];
        else if (c.type === 'toggle') vals = [true, false, c.value];
        else if (c.type === 'select' || c.type === 'radio') vals = c.options || [];
        else vals = [null];
        const sigs = [];
        for (let i = 0; i < vals.length; i++) {
          try { await setCtl(c.id, vals[i]); } catch (e) { r.errors.push('setControl(' + JSON.stringify(vals[i]) + '): ' + e.message); continue; }
          await frames(page, 2); const sg = await sample(page, 'c' + sigs.length); sigs.push(sg);
          if (SHOT && c.type !== 'button' && ((c.type === 'slider' && i === 1) || (c.type === 'toggle' && i === 0) || ((c.type === 'select' || c.type === 'radio') && i === vals.length - 1))) {
            const f = path.join(THUMBS, scene.id + '--' + c.id + '-max.png'); await page.screenshot({ path: f }); r.shot = path.relative(STUDY, f);
          }
        }
        if (c.type === 'button') { r.effect = sigs[0] ? changed(await lumaDiff(page, base, sigs[0])) : false; }
        else { let eff = false; for (let i = 1; i < sigs.length; i++) if (changed(await lumaDiff(page, sigs[0], sigs[i]))) eff = true; r.effect = eff; }
        // restore this control, then a real-DOM click pass for buttons/toggles/options
        try { await page.evaluate(() => window.__resetAll()); } catch (e) { /* ignore */ }
        await frames(page, 2);
        try {
          const sel = `[data-wk-id="${c.id}"]`;
          if (c.type === 'button') await page.click(sel + ' button');
          else if (c.type === 'toggle') await page.click(sel + ' .wk-switch');
          else if (c.type === 'radio') for (const v of vals) await page.click(sel + ` .wk-segbtn[data-value="${String(v).replace(/"/g, '\\"')}"]`);
          else if (c.type === 'select') for (const v of vals) await page.select(sel + ' select', String(v));
        } catch (e) { r.errors.push('DOM click failed: ' + e.message.split('\n')[0]); }
        await page.mouse.move(1, 1);   // leave any hover-highlight before the next frame is sampled
        await frames(page, 2);
        try { await page.evaluate(() => window.__resetAll()); } catch (e) { /* ignore */ }
        await frames(page, 2);
        const e1 = log.pageerrors.length, se1 = await nErr0();
        if (e1 > e0) r.errors.push(...log.pageerrors.slice(e0));
        if (se1 > se0) r.errors.push(...(await page.evaluate(n => window.__sceneErrors.slice(n), se0)));
        if (r.errors.length) hard('control "' + c.id + '": ' + r.errors.join(' | '));
        else if (r.effect === false && !rep.animated && !r.disabledAtStart && !r.noVisual) rep.warnings.push('control "' + c.id + '" has no visible effect on the stage (min/max/mid/initial or options gave identical frames)');
        rep.controls.push(r);
      }
    }
    // final error sweep
    const finalErr = await page.evaluate(() => (window.__sceneErrors || []).slice());
    finalErr.filter(e => !info.sceneErrors.includes(e) && !rep.errors.some(x => x.includes(e))).forEach(e => hard('scene error: ' + e));
    log.pageerrors.forEach(e => { if (!rep.errors.some(x => x.includes(e))) hard('page error: ' + e); });
    log.console.filter(m => m.type === 'error').forEach(m => { if (!rep.errors.some(x => x.includes(m.text))) hard('console.error: ' + m.text); });
    log.console.filter(m => m.type === 'warning').forEach(m => rep.warnings.push('console.warn: ' + m.text));
    log.failed.forEach(f => hard('failed request: ' + f));
  } catch (e) {
    hard('checker exception: ' + (e && e.stack ? e.stack.split('\n').slice(0, 3).join(' | ') : e));
  } finally {
    try { await page.close(); } catch (e) { /* ignore */ }
  }
  rep.elapsedMs = Date.now() - t0;
  return rep;
}

// ---------------------------------------------------------------- main
const scenes = resolveScenes();
if (!scenes.length) { console.error('no scenes to check'); process.exit(2); }
fs.mkdirSync(THUMBS, { recursive: true });
const puppeteer = await loadPuppeteer();
let browser = null;
const killOwn = () => { try { if (browser && browser.process()) browser.process().kill('SIGKILL'); } catch (e) { /* ignore */ } };
process.on('SIGINT', () => { killOwn(); process.exit(130); });
process.on('SIGTERM', () => { killOwn(); process.exit(143); });
let failed = 0;
try {
  browser = await puppeteer.launch({
    headless: true, pipe: true,
    args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--allow-file-access-from-files', '--no-sandbox'],
  });
  for (const s of scenes) {
    const rep = await checkScene(browser, s);
    if (!rep.ok) failed++;
    const tag = rep.ok ? (rep.warnings.length ? 'OK (warnings)' : 'OK') : 'FAIL';
    const ctl = rep.controls.length ? '  controls ' + rep.controls.length + ' (' + rep.controls.filter(c => c.effect).length + ' change the frame' + (rep.controls.some(c => c.effect === false && !c.disabledAtStart && !c.noVisual) ? ', ' + rep.controls.filter(c => c.effect === false && !c.disabledAtStart && !c.noVisual).length + ' no visible effect' : '') + ')' : '';
    console.log(`${rep.id}  ${tag}  ${rep.title ? '"' + rep.title.replace(/ - weld study$/, '') + '"  ' : ''}ready ${rep.readyMs != null ? (rep.readyMs / 1000).toFixed(1) + 's' : 'never'}  content ${rep.content != null ? Math.round(rep.content * 100) + '%' : '-'}${rep.animated ? '  animated' : ''}${ctl}${rep.insets && rep.insets.length ? '  insets ' + rep.insets.length : ''}`);
    rep.errors.forEach(e => console.log('   ERROR  ' + e));
    rep.warnings.forEach(w => console.log('   warn   ' + w));
    if (rep.thumb) console.log('   thumb  ' + rep.thumb);
    rep.controls.filter(c => c.shot).forEach(c => console.log('   shot   ' + c.shot));
    if (rep.badges && rep.badges.length) rep.notes.push('badges: ' + rep.badges.map(b => b.level + ':' + b.text).join(' ; '));
    rep.notes.forEach(n => console.log('   note   ' + n));
    fs.writeFileSync(path.join(THUMBS, rep.id + '.check.json'), JSON.stringify(rep, null, 2));
  }
} finally {
  try { if (browser) await browser.close(); } catch (e) { killOwn(); }
}
console.log(failed ? `${failed} of ${scenes.length} scene(s) FAILED` : `${scenes.length} scene(s) passed`);
process.exit(failed ? 1 : 0);
