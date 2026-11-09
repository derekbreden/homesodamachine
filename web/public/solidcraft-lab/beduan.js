// The valve lab keeps one native session, applies edits incrementally and suspends it in the background.
const base = '/labs/solidcraft/beduan';
const storageKey = 'hsm-solidcraft-beduan-design';
const $ = id => document.getElementById(id);
const labels = {
  terminal_length: 'Terminal length', post_radius: 'Mounting post radius',
  post_pitch_x: 'Post spacing across', post_pitch_y: 'Post spacing front to back',
  bearing_face_z: 'Bearing face height', bearing_radius: 'Bearing radius',
  port_axis_z: 'Port axis height', port_face_y: 'Port face position', port_radius: 'Port radius',
  terminal_pitch: 'Terminal spacing', terminal_plane_z: 'Terminal height',
};
const quick = new Set(['terminal_length', 'post_radius']);
let phase = 'loading';
let frame, api, checkpoint, referenceText, referenceHash, model;
let pollTimer, pollWork, pauseRequested = false;
let camera, cameraLayout;
const observations = [];

function status(text, error = false) {
  $('status').textContent = text;
  $('status').toggleAttribute('data-error', error);
}
function state(next, label) {
  phase = next;
  $('state-label').textContent = label;
  $('state-dot').toggleAttribute('data-ready', next === 'ready');
  for (const control of document.querySelectorAll('[data-ready], .parameter input')) control.disabled = next !== 'ready';
  $('pause').disabled = !api || next !== 'ready';
  $('renderer').disabled = next === 'loading' || next === 'busy';
}
function cover(title, detail, {resume = false, fallback = false} = {}) {
  $('cover').hidden = false;
  $('cover-title').textContent = title;
  $('cover-detail').textContent = detail;
  $('resume').hidden = !resume;
  $('fallback').hidden = !fallback;
}
function changed(input) {
  input.toggleAttribute('data-changed', input.value.trim() !== input.dataset.current);
}
function fields(source) {
  const favoriteNames = new Set(source.favorites);
  const params = source.params.filter(p => favoriteNames.has(p.name));
  const order = name => quick.has(name) ? Array.from(quick).indexOf(name) : quick.size;
  params.sort((a, b) => order(a.name) - order(b.name));
  for (const param of params) {
    const label = document.createElement('label');
    label.className = 'parameter';
    const text = document.createElement('span');
    text.textContent = labels[param.name] || param.name.replaceAll('_', ' ');
    const input = document.createElement('input');
    input.name = param.name;
    input.value = param.expr;
    input.dataset.current = param.expr;
    input.disabled = true;
    input.spellcheck = false;
    input.autocomplete = 'off';
    input.addEventListener('input', () => changed(input));
    label.append(text, input);
    $(quick.has(param.name) ? 'quick-parameters' : 'more-parameters').append(label);
  }
}
function syncFields(force = false) {
  for (const param of model.params) {
    const input = $('parameters').elements.namedItem(param.name);
    if (!input) continue;
    if (force || !input.hasAttribute('data-changed')) input.value = param.expression;
    input.dataset.current = param.expression;
    changed(input);
  }
  $('undo').disabled = phase !== 'ready' || !model.undo;
}
function retain() {
  try {
    localStorage.setItem(storageKey, JSON.stringify({baseHash: referenceHash, text: checkpoint.text, camera, cameraLayout}));
  } catch {
    status('The browser could not retain local edits. Download the native design to keep them.', true);
  }
}
function currentCameraLayout() {
  return {width: $('stage').clientWidth, height: $('stage').clientHeight, panels: $('native-panels').checked};
}
async function capture({keepCamera = false} = {}) {
  checkpoint = await api.request('document.export');
  if (keepCamera) {
    const view = await api.request('ui.camera');
    camera = Object.fromEntries(['target', 'distance', 'yaw', 'pitch', 'roll'].map(key => [key, view[key]]));
    cameraLayout = currentCameraLayout();
  }
  retain();
  await api.request('document.saved', {revision: checkpoint.revision});
}
async function frames() {
  if (document.hidden) return;
  await new Promise(resolve => {
    const done = () => { document.removeEventListener('visibilitychange', onVisibility); resolve(); };
    const onVisibility = () => { if (document.hidden) done(); };
    document.addEventListener('visibilitychange', onVisibility);
    requestAnimationFrame(() => requestAnimationFrame(done));
  });
}
function note(label, ms, result = {}) {
  observations.unshift({label, ms, recomputed: result.recomputed, restored: result.restored});
  observations.splice(6);
  $('timing-empty').hidden = true;
  $('timing-list').replaceChildren(...observations.map(item => {
    const row = document.createElement('li');
    const label = document.createElement('span'); label.textContent = item.label;
    const time = document.createElement('strong'); time.textContent = item.ms < 1000 ? `${Math.round(item.ms)} ms` : `${(item.ms / 1000).toFixed(2)} s`;
    row.append(label, time);
    if (Number.isFinite(item.recomputed)) {
      const detail = document.createElement('small');
      detail.textContent = `${item.recomputed} features rebuilt${item.restored ? ` · ${item.restored} restored from cache` : ''}`;
      row.append(detail);
    }
    return row;
  }));
}
function schedulePoll() {
  clearTimeout(pollTimer);
  if (phase !== 'ready' || document.hidden) return;
  pollTimer = setTimeout(() => {
    pollWork = (async () => {
      const revision = await api.request('document.revision');
      if (revision.revision !== checkpoint?.revision) {
        model = await api.inspect();
        syncFields();
        await capture();
      }
    })().catch(error => status(error.message, true)).finally(() => {
      pollWork = null;
      schedulePoll();
    });
  }, 2500);
}
function release() {
  clearTimeout(pollTimer);
  frame?.remove();
  frame = undefined;
  api = undefined;
}
async function setPanels() {
  const show = $('native-panels').checked;
  await api.request('ui.set', {showBrowser: show, showTimeline: show});
  await api.execute('view.ribbon_tabs_only', {on: !show});
}
async function pause({background = false} = {}) {
  clearTimeout(pollTimer);
  if (phase === 'busy' || phase === 'loading') { pauseRequested = true; return; }
  if (!api) return;
  state('busy', 'Saving local design');
  try {
    if (pollWork) await pollWork;
    await capture({keepCamera: true});
    if (background && !document.hidden) {
      state('ready', 'Native model ready'); syncFields(); schedulePoll(); return;
    }
    release();
    state('paused', 'Paused');
    cover('Model paused', 'Your design is kept in this browser. Resume when you want to continue.', {resume: true});
    status('The embedded CAD runtime is unloaded. Your edits are retained locally.');
  } catch (error) {
    state('ready', 'Native model ready');
    status(`Could not pause: ${error.message}`, true);
    schedulePoll();
  }
}
async function act(label, operation, {forceFields = false, timed = true} = {}) {
  if (phase !== 'ready') return;
  clearTimeout(pollTimer);
  state('busy', label);
  status(`${label}…`);
  try {
    if (pollWork) await pollWork;
    const started = performance.now();
    const result = await operation();
    await frames();
    if (timed) note(label, performance.now() - started, result);
    model = await api.inspect();
    await capture();
    const errors = model.timeline.filter(feature => feature.error);
    status(errors.length ? 'The native model reports a feature error. Undo or adjust the dimension to continue.' : 'Native model updated. Edits are retained in this browser.', errors.length > 0);
  } catch (error) {
    status(error.message, true);
    try { model = await api.inspect(); await capture(); } catch { /* Keep the last retained design available. */ }
  } finally {
    state('ready', 'Native model ready');
    if (model) syncFields(forceFields);
    if (pauseRequested || document.hidden) {
      pauseRequested = false;
      await pause({background: document.hidden});
    } else schedulePoll();
  }
}
async function start() {
  if (frame) return;
  pauseRequested = false;
  state('loading', 'Loading native engine');
  cover('Loading the engine', 'The first visit downloads the browser runtime. Later visits can reuse it.');
  status('Loading SolidCraft…');
  const started = performance.now();
  try {
    await sourceReady;
    let kept;
    try { kept = JSON.parse(localStorage.getItem(storageKey)); } catch { /* Start from the reference source. */ }
    if (kept?.baseHash !== referenceHash) kept = null;
    frame = document.createElement('iframe');
    frame.title = 'SolidCraft native Beduan valve';
    frame.setAttribute('allow', 'fullscreen');
    const query = new URLSearchParams({embed: 'editor'});
    if ($('renderer').value === 'webgl') query.set('webgl', '');
    frame.src = `${base}/editor?${query}`;
    const ready = new Promise((resolve, reject) => {
      const timeout = setTimeout(() => finish(new Error('The browser engine did not finish loading. Try WebGL or resume to retry.')), 240000);
      const handler = event => {
        if (event.origin !== location.origin || event.source !== frame?.contentWindow) return;
        if (event.data?.type === 'solidcraft-lab-ready') finish();
        else if (event.data?.type === 'solidcraft-lab-error') finish(new Error(event.data.error));
      };
      function finish(error) {
        clearTimeout(timeout);
        window.removeEventListener('message', handler);
        error ? reject(error) : resolve();
      }
      window.addEventListener('message', handler);
    });
    $('stage').prepend(frame);
    await ready;
    api = frame.contentWindow.solidcraft;
    note('Engine startup', performance.now() - started);
    cover('Building the native valve', 'Evaluating the saved feature history and preparing the view.');
    status('Building the native valve…');
    const buildStarted = performance.now();
    const imported = await api.request('document.import', {text: kept?.text || referenceText, name: 'Beduan valve'});
    await setPanels();
    if (kept?.camera) {
      await api.request('ui.camera', kept.camera);
      if (JSON.stringify(kept.cameraLayout) !== JSON.stringify(currentCameraLayout())) await api.request('ui.view', {view: 'fit'});
    } else {
      await api.request('ui.view', {view: 'iso'});
      await api.request('ui.view', {view: 'fit'});
    }
    await frames();
    note(kept ? 'Resume design' : 'Open reference', performance.now() - buildStarted);
    model = await api.inspect();
    await capture({keepCamera: true});
    state('ready', 'Native model ready');
    syncFields(true);
    $('cover').hidden = true;
    status(imported.errors ? 'The saved design has feature errors. Undo or restore the reference.' : 'Native valve ready. Try changing the terminal length, or explore its feature history.', Boolean(imported.errors));
    if (pauseRequested || document.hidden) { pauseRequested = false; await pause({background: document.hidden}); }
    else schedulePoll();
  } catch (error) {
    release();
    state('failed', 'Could not start');
    cover('Could not open the native model', error.message, {resume: true, fallback: $('renderer').value !== 'webgl'});
    status(error.message, true);
  }
}

const sourceReady = (async () => {
  const response = await fetch(`${base}/model.json`);
  if (!response.ok) throw new Error('The reference design could not be loaded.');
  referenceText = await response.text();
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(referenceText));
  referenceHash = Array.from(new Uint8Array(digest), byte => byte.toString(16).padStart(2, '0')).join('');
  fields(JSON.parse(referenceText));
})();

$('parameters').addEventListener('submit', event => {
  event.preventDefault();
  const changes = Object.fromEntries(Array.from(document.querySelectorAll('.parameter input[data-changed]')).map(input => [input.name, input.value.trim()]));
  if (!Object.keys(changes).length) { status('Change a dimension first.'); return; }
  act('Apply dimensions', () => api.execute('parameters.change', {changes}), {forceFields: true});
});
$('undo').addEventListener('click', () => act('Undo', () => api.execute('edit.undo'), {forceFields: true}));
$('reset').addEventListener('click', () => act('Restore reference', async () => {
  const view = await api.request('ui.camera');
  const result = await api.request('document.import', {text: referenceText, name: 'Beduan valve'});
  await api.request('ui.camera', Object.fromEntries(['target', 'distance', 'yaw', 'pitch', 'roll'].map(key => [key, view[key]])));
  return result;
}, {forceFields: true}));
$('fit').addEventListener('click', () => act('Fit valve', () => api.request('ui.view', {view: 'fit'}), {timed: false}));
$('download').addEventListener('click', () => act('Download design', async () => {
  const design = await api.request('document.export');
  const url = URL.createObjectURL(new Blob([design.text], {type: 'application/json'}));
  const link = document.createElement('a');
  link.href = url; link.download = 'beduan-valve.json'; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}, {timed: false}));
$('pause').addEventListener('click', () => pause());
$('resume').addEventListener('click', start);
$('fallback').addEventListener('click', () => { $('renderer').value = 'webgl'; start(); });
$('renderer').addEventListener('change', async () => { if (api) await pause(); await start(); });
$('native-panels').addEventListener('change', () => act('Update editing panels', async () => {
  await setPanels();
  await api.request('ui.view', {view: 'fit'});
}, {timed: false}));
document.addEventListener('visibilitychange', () => { if (document.hidden) pause({background: true}); });
fetch('/solidcraft-lab/runtime.json').then(response => response.json()).then(runtime => {
  $('runtime-version').textContent = `SolidCraft ${runtime.version}`;
}).catch(() => {});
if (new URLSearchParams(location.search).get('renderer') === 'webgl' || !navigator.gpu) $('renderer').value = 'webgl';
$('native-panels').checked = !matchMedia('(max-width: 700px)').matches;
if (document.hidden) {
  state('paused', 'Paused');
  cover('Open the native valve', 'Load the model when you are ready to work with it.', {resume: true});
} else start();
