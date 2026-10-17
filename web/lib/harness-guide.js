import fs from 'node:fs';
import path from 'node:path';

const esc = value => String(value).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const repo = 'https://github.com/derekbreden/homesodamachine/blob/main/';

export function readJ2Harness(hardwareDir) {
  const file = path.join(hardwareDir, 'assembly', 'harnesses', 'j2.json');
  return fs.existsSync(file) ? JSON.parse(fs.readFileSync(file, 'utf8')) : null;
}

// One bench object owns its wire map, sequence and estimate. The browser reads
// this same record from the JSON block, including when WebGL is unavailable.
export function renderHarnessGuide(data, rate) {
  if (!data) return '';
  const minutes = data.steps.reduce((total, step) => total + step.minutes, 0);
  const money = mins => ((mins / 60) * rate).toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
  return `<section class="harness-guide" id="j2-harness" aria-labelledby="j2-title">
  <header class="harness-heading">
    <div><p class="harness-eyebrow">Assembly · one finished harness</p><h3 id="j2-title">J2 <span>Manifold B</span></h3><p>Two ribbons. Five populated contacts. One complete bench job.</p></div>
    <div class="harness-time"><strong>${minutes} min</strong><span>working estimate${rate ? ` · ${money(minutes)}` : ''}</span><small>First reference build: ~${data.referenceBuild.minutes} min, including lookups</small></div>
  </header>
  <p class="harness-scope">${esc(data.scope)}. ${esc(data.mapStatus)} The Lillium build parks FAN and OUT3; its active loads are V-I and V-J.</p>
  <p class="harness-scope">This J2 estimate is shown separately from the unit total. The ledger&rsquo;s shared 45-minute allowance for all twelve harnesses still needs to be mapped to complete bench jobs.</p>
  <div class="harness-workbench">
    <div class="harness-visual">
      <div class="harness-toolbar" hidden>
        <div class="harness-views" role="group" aria-label="Harness camera"><button type="button" data-harness-view="overall" aria-pressed="true">3D</button><button type="button" data-harness-view="top" aria-pressed="false">Top</button><button type="button" data-harness-view="connector" aria-pressed="false">JST close-up</button></div>
        <button type="button" data-harness-reset>Reset view</button>
        <button type="button" data-harness-fullscreen>Expand</button>
      </div>
      <div class="harness-stage" tabindex="0" aria-label="Interactive J2 harness. Drag to orbit, scroll to zoom, or use arrow keys to orbit and plus or minus to zoom. Select a wire in the pin map to trace it."><p class="harness-loading" role="status">Loading the 3D harness… The complete wire map and build sequence are below.</p><div class="harness-labels"></div></div>
      <div class="harness-scene-controls" hidden>
        <label><input type="checkbox" data-harness-wires> Reveal wires through mesh</label>
        <label><input type="checkbox" data-harness-labels checked> Labels</label>
        <label class="harness-explode">Explode <input type="range" min="0" max="100" value="0" data-harness-explode aria-label="Separate housing, mesh, collars and terminals"><output data-harness-explode-value>0%</output></label>
      </div>
      <p class="harness-caption">Drag to orbit · Scroll / pinch to zoom · Select a wire to trace it<br>Bench layout is schematic; printed cut lengths come from the run schedule.</p>
    </div>
    <aside class="harness-inspector" aria-label="Selected harness component">
      <p class="harness-eyebrow">On the bench</p><h4 data-harness-selection-title>The finished harness</h4>
      <p data-harness-selection-detail>JST-XH at the board, two 3P ribbons with white index stripes, a dressed four-wire trunk, a short V-K branch and a five-port positive fan-out.</p>
      <dl data-harness-selection-facts><div><dt>Board end</dt><dd>1 × XHP-6 + 5 contacts</dd></div><div><dt>Wire stock</dt><dd>22 AWG · 3P + 3P</dd></div><div><dt>Far end</dt><dd>5 ferrules + 6 valve disconnects + 2 provisional fan ends</dd></div></dl>
      <button type="button" data-harness-clear hidden>Show the whole harness</button>
      <div class="harness-cavity-note"><strong>Cavity 3 stays empty.</strong><span>COM is +12 V. The Wago carries positives only; every switched return goes straight to its J2 pin.</span></div>
    </aside>
  </div>
  <div class="harness-sequence-heading"><h4>Build this piece, start to finish</h4><button type="button" data-harness-finished aria-pressed="true" hidden>Finished view</button></div>
  <ol class="harness-steps">${data.steps.map((step, i) => `<li><button type="button" data-harness-step="${step.id}" aria-pressed="false"><span class="harness-step-number">${i + 1}</span><span>${esc(step.title)}</span><b>${step.minutes} min</b></button><p>${esc(step.instruction)}</p></li>`).join('')}</ol>
  <div class="harness-step-detail" hidden aria-live="polite"><div><span data-harness-step-index></span><h4 data-harness-step-title></h4></div><p data-harness-step-copy></p><div class="harness-step-nav"><button type="button" data-harness-prev>Previous</button><button type="button" data-harness-next>Next step</button></div></div>
  <details class="harness-map" open><summary>Wire map <span>Count from the white-striped edge of each ribbon</span></summary>
    <div class="harness-pin-face"><div><strong>Housing orientation</strong><p data-harness-face-label>Wire-entry view · orient the circuit 1 mark to the left</p></div><button type="button" data-harness-face hidden>Show mating face</button></div>
    <div class="harness-pin-strip" aria-label="J2 cavities, wire-entry view">${data.pins.map(pin => `<button type="button" data-harness-pin="${pin.pin}" aria-pressed="false" class="${pin.pin === 3 ? 'is-empty' : ''}" aria-label="Cavity ${pin.pin}, ${pin.net}, ${pin.pin === 3 ? 'empty' : `${pin.ribbon}${pin.conductor}${pin.stripe ? ', white stripe' : ''}, ${pin.destination}`}"><b>${pin.pin}</b><span>${pin.net}</span><small>${pin.pin === 3 ? 'empty' : `${pin.ribbon}${pin.conductor}${pin.stripe ? ' ▰' : ''}`}</small>${pin.pin === 1 ? '<i aria-hidden="true">1 ◂</i>' : ''}</button>`).join('')}</div>
    <p class="harness-map-note">The circuit 1 mark identifies COM. The mating face mirrors this order. ▰ = white stripe on the black insulation. ${esc(data.mapStatus)}</p>
    <div class="harness-map-table"><table><thead><tr><th>Cavity / net</th><th>Ribbon lead</th><th>Bench cut</th><th>Other end</th></tr></thead><tbody>${data.pins.map(pin => `<tr data-harness-row="${pin.pin}"><th scope="row"><button type="button" data-harness-select="${pin.pin}">${pin.pin} · ${pin.net}</button></th><td>${pin.ribbon}${pin.conductor}${pin.stripe ? ' · white stripe' : ''}${pin.pin === 3 ? ' · discard' : ''}</td><td>${pin.cutMm ? `${pin.cutMm} mm` : '—'}</td><td>${esc(pin.destination)}<small>${esc(pin.termination)}</small></td></tr>`).join('')}</tbody></table></div>
    <p class="harness-map-note"><strong>Positive branches:</strong> 4 × 450 mm blanks of 22 AWG black bulk wire, each ferruled into its own Wago port. Trim to the V-I, V-J, fan and V-K landings. These four branches are additional to the five wires leaving J2.</p>
  </details>
  <details class="harness-materials"><summary>Everything that goes on this harness</summary><ul>
    <li><strong>Board end:</strong> 1 XHP-6 housing; 5 SXH-001T-P0.6 contacts. No contact in cavity 3.</li>
    <li><strong>Cable:</strong> 2 × 650 mm 3P ribbon blanks, 22 AWG black silicone; 4 × 450 mm bulk-wire positive branch blanks. Short leads trimmed per the map.</li>
    <li><strong>Slip on before large terminals:</strong> nominal 1/2 in black PET mesh and 2 heat-shrink end collars. Stage 2 black zip ties; close and flush-cut after dressing.</li>
    <li><strong>Far ends:</strong> 5 bootlace ferrules, 1 Wago 221-415, 6 female valve disconnects. The two fan ends have provisional disconnects in the schedule. Valve tab widths (4.8 / 6.3 mm) and the donor fan interface are not recorded.</li>
    <li><strong>Tools:</strong> stripper, SN-2549 JST crimper, ferrule crimper, insulated-terminal crimper, heat gun, flush cutters and multimeter.</li>
  </ul><p>${esc(data.dress.qualification)}</p></details>
  <details class="harness-basis"><summary>Time estimate, scope &amp; sources</summary><p>${esc(data.estimateBasis)}</p><p>${esc(data.referenceBuild.basis)} The ${minutes}-minute guide estimate${rate ? ` (${money(minutes)} at the ledger’s $${rate}/h)` : ''} is a reference for this piece. The cost rollup still carries its shared 45-minute allowance for all twelve harnesses; it needs a harness-by-harness estimate before this reference is included in the total.</p><p>${esc(data.positiveBranches.basis)}</p><p>${data.sources.map(source => `<a href="${esc(source.url || repo + source.path)}">${esc(source.label)}</a>`).join(' · ')}</p></details>
  <script type="application/json" id="j2-harness-data">${JSON.stringify(data).replace(/</g, '\\u003c')}</script>
</section>`;
}
