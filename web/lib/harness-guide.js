import fs from 'node:fs';
import path from 'node:path';
import { conductorRecords } from '../public/js/harness/conductors.js';

const esc = value => String(value).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const repo = 'https://github.com/derekbreden/homesodamachine/blob/main/';

function readHarness(hardwareDir, id) {
  const file = path.join(hardwareDir, 'assembly', 'harnesses', `${id}.json`);
  return fs.existsSync(file) ? JSON.parse(fs.readFileSync(file, 'utf8')) : null;
}
export const readJ2Harness = hardwareDir => readHarness(hardwareDir, 'j2');
export const readJ13Harness = hardwareDir => readHarness(hardwareDir, 'j13');

// The estimate, conductor inspector and build sequence describe the same piece.
// Both guides are embedded in Wiring and included in its ledger total once.
export function renderHarnessGuide(data, rate) {
  if (!data) return '';
  const id = data.id.toLowerCase(), rows = conductorRecords(data);
  const minutes = data.steps.reduce((sum, step) => sum + step.minutes, 0);
  const money = ((minutes / 60) * rate).toLocaleString('en-US', { style: 'currency', currency: 'USD' });
  return `<section class="harness-guide" id="${id}-harness" data-harness="${esc(data.id)}" aria-labelledby="${id}-title">
  <header class="harness-heading">
    <h3 id="${id}-title">${esc(data.id)} <span>${esc(data.name)}</span></h3>
    <div class="harness-time"><strong>${minutes} min</strong><span>unit ${data.estimateUnit}${rate ? ` · ${money}` : ''}</span></div>
  </header>
  <div class="harness-workbench">
    <button type="button" class="harness-launch" data-harness-launch aria-haspopup="dialog" aria-label="Open ${esc(data.id)} interactive 3D harness" hidden><span><strong>Explore ${esc(data.id)} in 3D ↗</strong><small>Tap to open · pinch to zoom</small></span></button>
    <div class="harness-visual">
      <div class="harness-toolbar" hidden>
        <div class="harness-views" role="group" aria-label="${esc(data.id)} camera">
          <button type="button" data-harness-view="overall" aria-pressed="true">Whole harness</button>
          <button type="button" data-harness-view="pcb" aria-pressed="false">PCB labels</button>
          <button type="button" data-harness-view="connector" aria-pressed="false">JST plug</button>
          <button type="button" data-harness-view="top" aria-pressed="false">Top</button>
        </div>
        <button type="button" data-harness-reset aria-label="Reset ${esc(data.id)} view">Reset view</button>
        <button type="button" data-harness-fullscreen>Expand</button>
      </div>
      <div class="harness-navigation" hidden>
        <div role="group" aria-label="${esc(data.id)} drag action">${[['rotate', 'Rotate'], ['pan', 'Pan'], ['zoom', 'Zoom']].map(([key, label]) => `<button type="button" data-harness-nav="${key}" aria-pressed="${key === 'rotate'}">${label}</button>`).join('')}</div>
        <span>Right drag or two fingers to pan</span>
      </div>
      <div class="harness-stage" tabindex="0" aria-label="${esc(data.id)} interactive harness. Click a wire to highlight it. Use Open conductor separately to inspect its ends. Drag to rotate; right drag, two fingers, or Pan mode to pan; pinch or scroll to zoom. Arrow keys rotate, Shift and arrows pan, plus and minus zoom, Home resets the view.">
        <p class="harness-loading" role="status">Loading the harness and its native PCB…</p>
        <svg class="harness-leaders" aria-hidden="true"></svg>
        <div class="harness-labels"></div>
        <div class="harness-open-banner" hidden><span data-harness-open-title></span><button type="button" data-harness-close>Back to harness</button></div>
      </div>
      <div class="harness-scene-controls" hidden>
        ${data.dress.sleeve === 'None' ? '' : '<label><input type="checkbox" data-harness-wires> See through sleeves</label>'}
        <label><input type="checkbox" data-harness-xray> X-ray</label>
        <label title="Millimeter rulers on the native PCB; cable reach is compressed."><input type="checkbox" data-harness-rulers> PCB rulers</label>
        <label><input type="checkbox" data-harness-labels checked> Part labels</label>
        <button type="button" data-harness-show-all disabled>Show all</button>
        <label class="harness-explode">Separate parts <input type="range" data-harness-explode min="0" max="100" value="0" aria-label="Separate ${esc(data.id)} parts"><output data-harness-explode-value>0%</output></label>
      </div>
      <p class="harness-caption">Drag to rotate · two fingers or right drag to pan · pinch or scroll to zoom. Use the cube for a precise view. Click a wire to highlight it, then choose <strong>Open conductor</strong> to inspect both ends.<span>Native PCB crop and printed labels · plug lifted for inspection · cable reach compressed · rulers measure the native PCB only</span></p>
    </div>
    <aside class="harness-inspector" aria-label="${esc(data.id)} assembly inspector">
      <div class="harness-find" hidden><input type="search" data-harness-find aria-label="Find ${esc(data.id)} conductor or part" placeholder="Find a wire, pin or part…"><div data-harness-find-results aria-live="polite" hidden></div></div>
      <div class="harness-tabs" role="tablist" aria-label="${esc(data.id)} guide" hidden>
        ${[['wires', 'Conductors'], ['build', 'Build'], ['parts', 'Parts']].map(([key, label]) => `<button type="button" role="tab" id="${id}-tab-${key}" aria-controls="${id}-panel-${key}" aria-selected="${key === 'wires'}" data-harness-tab="${key}">${label}</button>`).join('')}
      </div>
      <div class="harness-pane" id="${id}-panel-wires" role="tabpanel" aria-labelledby="${id}-tab-wires" data-harness-panel="wires">
        <div data-harness-wire-list>
          <p class="harness-panel-intro">Choose one physical conductor.</p>
          <div class="harness-conductors">${rows.map(row => `<button type="button" data-harness-select="${esc(row.id)}" aria-pressed="false"><i class="harness-wire-swatch${row.stripe ? ' is-striped' : ''}" aria-hidden="true"></i><span>${esc(row.title.replace(/^J13 /, ''))}</span></button>`).join('')}</div>
          <p class="harness-map-status">${esc(data.mapStatus)}</p>
        </div>
        <div class="harness-selection" hidden>
          <button type="button" class="harness-back" data-harness-clear>← All conductors</button>
          <h4 data-harness-selection-title></h4>
          <button type="button" class="harness-open" data-harness-open hidden>Open conductor ↗</button>
          <button type="button" class="harness-hide" data-harness-hide>Hide selected</button>
          <div class="harness-connection" hidden>
            <button type="button" data-harness-focus="from"><small>FROM</small><strong data-harness-from></strong><span>Show this end</span></button>
            <div class="harness-connection-arrow" aria-hidden="true">↓</div>
            <button type="button" data-harness-focus="to"><small>TO</small><strong data-harness-to></strong><span>Show this end</span></button>
          </div>
          <p data-harness-selection-detail></p>
          <dl data-harness-selection-facts></dl>
          <div data-harness-part-wires></div>
        </div>
      </div>
      <div class="harness-pane" id="${id}-panel-build" role="tabpanel" aria-labelledby="${id}-tab-build" data-harness-panel="build" hidden>
        <div class="harness-sequence-heading"><span>${minutes} minutes · one complete piece</span><button type="button" data-harness-finished aria-pressed="true">Finished view</button></div>
        <ol class="harness-steps">${data.steps.map((step, index) => `<li><button type="button" data-harness-step="${esc(step.id)}" aria-pressed="false"><span>${index + 1}</span><strong>${esc(step.title)}</strong><b>${step.minutes} min</b></button></li>`).join('')}</ol>
        <div class="harness-step-detail" hidden><p data-harness-step-index></p><h4 data-harness-step-title></h4><p data-harness-step-copy></p><div class="harness-step-nav"><button type="button" data-harness-prev>Previous</button><button type="button" data-harness-next>Next step</button></div></div>
        <p class="harness-practice-note">Practiced time at unit ${data.estimateUnit}, with the map, tools and materials ready. The estimate is theoretical and unmeasured.</p>
      </div>
      <div class="harness-pane" id="${id}-panel-parts" role="tabpanel" aria-labelledby="${id}-tab-parts" data-harness-panel="parts" hidden>
        <h4>Everything on this piece</h4><dl data-harness-materials></dl>
        <p class="harness-map-status">${esc(data.dress.qualification)}</p>
      </div>
    </aside>
  </div>
  <div class="harness-fallback"><details><summary>Text connections &amp; build instructions</summary>
    <table><thead><tr><th>From</th><th>To</th><th>Wire / cut</th><th>Ends</th></tr></thead><tbody>${rows.map(row => `<tr><td>${esc(row.from)}</td><td>${esc(row.to)}</td><td>${esc(row.ribbon || 'Bulk wire')}${row.stripe ? ' · white stripe' : ''} · ${row.cutMm} mm</td><td>${esc(row.fromPart)} → ${esc(row.toPart)}</td></tr>`).join('')}</tbody></table>
    <ol>${data.steps.map(step => `<li><strong>${esc(step.title)} · ${step.minutes} min.</strong> ${esc(step.instruction)}</li>`).join('')}</ol>
  </details></div>
  <details class="harness-basis"><summary>Estimate basis &amp; sources</summary><p>${esc(data.estimateBasis)}</p><p>This ${minutes}-minute bench job is included in Wiring and in the assembly cost total. Installation is estimated separately.</p><p>${data.sources.map(source => `<a href="${esc(source.url || repo + source.path)}">${esc(source.label)}</a>`).join(' · ')} · <a href="/harness/${id}-board.json">Native PCB crop provenance</a></p></details>
  <script type="application/json" data-harness-data>${JSON.stringify(data).replace(/</g, '\\u003c')}</script>
</section>`;
}
