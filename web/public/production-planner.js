// The planning workspace lets Derek adjust purchase packs and see cumulative coverage against the shared stock record.
import { freshScenario, optionKey, coverageFor, fillPurchasePlan, projectProduction, materialBalance } from '/contracts/production-plan.js';
import { lotCost } from '/contracts/purchase-lots.js';

const host = document.querySelector('.production-planner');
if (host) {
  const data = JSON.parse(document.getElementById('production-planner-data').textContent);
  const key = 'hsm-production-scenario-v1';
  const money = cents => '$' + (cents / 100).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const number = n => n == null ? '?' : n.toLocaleString('en-US', { maximumFractionDigits: 3 });
  const escape = text => String(text ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
  const labels = { stock: 'On hand', estimate: 'On hand · estimate', incoming: 'Await receipt', planned: 'With purchase', short: 'Short', unknown: 'Confirm', unused: '—' };
  const select = selector => host.querySelector(selector);
  let scenario = freshScenario(), openRow = null, visible = 12, projection, saved = false;
  try {
    const held = JSON.parse(localStorage.getItem(key));
    if (held && data.finishes[held.finish] && [10, 20].includes(held.horizon) && Number.isSafeInteger(held.focus) && held.focus >= 1 && held.focus <= held.horizon) {
      scenario = { ...scenario, ...held, buyFor: Math.max(1, Math.min(data.horizon, held.buyFor || held.focus)) };
      for (const orders of Object.values(scenario.orders)) for (const [pack, count] of Object.entries(orders)) if (!Number.isSafeInteger(count) || count < 0 || count > 10000) delete orders[pack];
    }
  } catch { /* A blocked or invalid browser store starts a fresh scenario. */ }
  select('#planner-finish').value = scenario.finish;

  const required = (row, n = scenario.focus) => row.needs[n] || 0;
  const stateOf = (row, n = scenario.focus) => coverageFor(row, n, row.purchase);
  const badge = (status, extra = '') => `<span class="planner-badge" data-tone="${status}">${escape(extra || labels[status])}</span>`;
  function bar(unit) {
    return `<span class="planner-coverage-bar" aria-hidden="true">${Object.entries(unit.counts).map(([status, count]) => count ? `<i data-tone="${status}" style="flex-grow:${count}"></i>` : '').join('')}</span>`;
  }
  function unitDescription(unit) {
    const c = unit.counts;
    return `${c.stock + c.estimate} on hand${c.incoming ? ` · ${c.incoming} await receipt` : ''}${c.planned ? ` · ${c.planned} with purchases` : ''}${c.short ? ` · ${c.short} short` : ''}${unit.countUnknown ? ` · ${unit.countUnknown} stock counts` : ''}${unit.usageUnknown ? ` · ${unit.usageUnknown} usage checks` : ''}${unit.definitions ? ` · ${unit.definitions} inputs to define` : ''}`;
  }
  function save() {
    try { localStorage.setItem(key, JSON.stringify(scenario)); saved = true; } catch { saved = false; }
  }
  function renderMilestones() {
    select('.planner-milestones').innerHTML = [1, 2, 5, 10, ...(scenario.horizon === 20 ? [20] : [])].map(n => {
      const unit = projection.units[n - 1];
      return `<button type="button" class="planner-milestone" data-focus="${n}" aria-pressed="${scenario.focus === n}"><span>${n <= 2 ? `Unit ${n}` : `Through unit ${n}`}</span><strong>${unit.counts.short ? `${unit.counts.short} short` : unit.counts.unknown ? 'Confirm stock' : unit.counts.planned ? 'Purchases cover' : unit.counts.incoming ? 'On order' : 'Stock covers'}</strong>${bar(unit)}<small>${unit.counts.unknown} to confirm · ${unit.counts.incoming} await receipt</small><span class="planner-forecast-money">${money(unit.extraPartsCents)}<small>quoted parts still to buy</small>${unit.baselinePartsCents !== unit.extraPartsCents ? `<small class="planner-baseline">Without this plan: ${money(unit.baselinePartsCents)}</small>` : ''}</span></button>`;
    }).join('');
    select('.planner-outlook').innerHTML = `<div class="planner-section-head"><h3>Follow the stock through production</h3><label>Look ahead<select id="planner-horizon"><option value="10"${scenario.horizon === 10 ? ' selected' : ''}>10 units</option><option value="20"${scenario.horizon === 20 ? ' selected' : ''}>20 units</option></select></label></div><div class="planner-unit-strip">${projection.units.slice(0, scenario.horizon).map(unit => `<button type="button" data-focus="${unit.quantity}" aria-pressed="${scenario.focus === unit.quantity}" aria-label="Through unit ${unit.quantity}: ${escape(unitDescription(unit))}"><b>${unit.quantity}</b>${bar(unit)}<span>${unit.counts.short + unit.counts.unknown ? `${unit.counts.short + unit.counts.unknown} gaps` : unit.counts.planned ? 'Planned' : unit.counts.incoming ? 'Ordered' : 'Stock'}</span></button>`).join('')}</div>`;
  }
  function details(row, index) {
    const balance = materialBalance(row, scenario.focus, row.purchase);
    const { required: need, previousConsumed: before, added: extra, onHandBefore: afterPrevious } = balance;
    const remainder = balance.projectedAfter == null ? 'Usage unresolved' : (balance.atLeast ? 'At least ' : '') + number(balance.projectedAfter) + ' ' + escape(row.unit);
    const packs = (row.quote?.options || []).map((option, i) => {
      const count = scenario.orders[row.id]?.[optionKey(option)] || 0;
      return `<label class="planner-pack"><span><strong>${escape(option.label)}</strong><small>${number(option.quantity)} ${escape(row.unit)} / pack · ${money(lotCost(option, count || 1) / (count || 1))} / pack${option.available === false ? ' · unavailable' : ''}${option.tiers?.length ? ' · quantity pricing' : ''}</small></span><span class="planner-stepper"><button type="button" data-adjust="-1" data-input="pack-${index}-${i}" aria-label="Remove a ${escape(option.label)}"${!count || option.available === false ? ' disabled' : ''}>−</button><input id="pack-${index}-${i}" data-kind="pack" data-row="${escape(row.id)}" data-key="${escape(optionKey(option))}" aria-label="Packs of ${escape(option.label)}" type="number" min="0" max="10000" step="1" value="${count}"${option.available === false ? ' disabled' : ''}><button type="button" data-adjust="1" data-input="pack-${index}-${i}" aria-label="Add a ${escape(option.label)}"${option.available === false ? ' disabled' : ''}>+</button></span></label>`;
    }).join('');
    const custom = scenario.custom[row.id];
    const customFields = custom ? `<div class="planner-custom-fields"><label>Pack quantity (${escape(row.unit)})<input id="custom-${index}-quantity" type="number" min="0.001" step="any" value="${custom.quantity}" data-kind="custom" data-field="quantity" data-row="${escape(row.id)}"></label><label>Price / pack ($)<input id="custom-${index}-price" type="number" min="0.01" step="0.01" placeholder="Unquoted" value="${custom.priceCents == null ? '' : custom.priceCents / 100}" data-kind="custom" data-field="priceCents" data-row="${escape(row.id)}"></label><label>Packs<input id="custom-${index}-count" type="number" min="0" max="10000" step="1" value="${custom.count}" data-kind="custom" data-field="count" data-row="${escape(row.id)}"></label></div>` : '';
    const uses = row.uses.slice(0, 6).map(id => `<a href="/3d#material:${encodeURIComponent(id)}?panel=materials">${escape(data.materials[id] || id)}</a>`).join(' · ');
    return `<tr class="planner-detail"><td colspan="${scenario.horizon + 3}"><div class="planner-detail-grid"><div><h4>After the earlier units</h4><dl class="planner-quantities"><div><dt>Used through unit ${scenario.focus - 1}</dt><dd>${number(before)} ${escape(row.unit)}</dd></div><div><dt>On hand left for unit ${scenario.focus}</dt><dd>${row.available == null ? 'Count needed' : number(afterPrevious) + ' ' + escape(row.unit)}</dd></div><div><dt>This unit adds</dt><dd>${row.quantityKnown ? number(extra) + ' ' + escape(row.unit) : 'Usage unresolved'}</dd></div><div><dt>Total through unit ${scenario.focus}</dt><dd>${row.quantityKnown ? number(need) + ' ' + escape(row.unit) : row.material ? number(need) + ' parts · input undefined' : 'Usage unresolved'}</dd></div>${balance.reusable ? `<div><dt>Reusable during the run</dt><dd>${number(balance.reusable)} ${escape(row.unit)}</dd></div>` : ''}<div><dt>Already ordered</dt><dd>${number(row.incoming)} ${escape(row.unit)}</dd></div><div><dt>In this purchase plan</dt><dd>${number(row.purchase.quantity)} ${escape(row.unit)}</dd></div><div><dt>Left after unit ${scenario.focus}, with plan</dt><dd>${remainder}</dd></div></dl><p class="planner-evidence">${escape(row.note)}${row.reserved ? ` Reserved: ${number(row.reserved)} ${escape(row.unit)}.` : ''}</p><p class="planner-used-by">Used by ${uses}</p>${row.material ? `<a href="/build?material=${row.material}">Review this manufacturing input ↗</a>` : ''}</div><div><h4>Try purchase packs</h4>${packs || `<p>${row.material ? 'The manufacturing input needs defining before stock coverage can be calculated.' : 'No supplier pack is recorded. Add a custom pack to try a quantity and price.'}</p>`}${!row.material ? `<button class="planner-text-button" type="button" data-custom="${escape(row.id)}">${custom ? 'Remove custom pack' : 'Add a custom pack'}</button>${customFields}` : ''}${row.quote ? `<p class="planner-evidence">${escape(row.quote.note)}</p>` : ''}${row.href && /^https:\/\//.test(row.href) ? `<a href="${escape(row.href)}" target="_blank" rel="noopener noreferrer">Supplier / recorded source ↗</a>` : ''}</div></div></td></tr>`;
  }
  function renderRows() {
    const query = select('#planner-search').value.trim().toLowerCase(), filter = select('#planner-filter').value, supplier = select('#planner-supplier').value;
    const matching = projection.rows.map((row, index) => ({ row, index })).filter(({ row }) => {
      const status = stateOf(row);
      if (!required(row) && !row.active?.[scenario.focus]) return false;
      if (query && ![row.name, row.id, row.category, ...row.uses, ...row.uses.map(id => data.materials[id])].join(' ').toLowerCase().includes(query)) return false;
      if (supplier !== 'all' && (supplier === 'none' ? Boolean(row.supplier) : row.supplier !== supplier)) return false;
      return row.id === openRow || filter === 'all' || filter === 'planned' && row.purchase.quantity > 0 || filter === 'attention' && ['short', 'unknown', 'incoming'].includes(status) || filter === 'short' && status === 'short' || filter === 'unknown' && status === 'unknown';
    }).sort((a, b) => {
      const rank = row => ({ short: 0, unknown: 1, incoming: 2 }[coverageFor(row, scenario.focus)] ?? 3);
      return rank(a.row) - rank(b.row) || a.row.name.localeCompare(b.row.name);
    });
    select('.planner-table thead').innerHTML = `<tr><th scope="col">Material / purchase packs</th><th scope="col">Available now</th>${Array.from({ length: scenario.horizon }, (_, i) => `<th scope="col" class="planner-unit-head${scenario.focus === i + 1 ? ' is-focus' : ''}"><button type="button" data-focus="${i + 1}" aria-label="Focus unit ${i + 1}">${i + 1}</button></th>`).join('')}<th scope="col">Through ${scenario.focus}</th></tr>`;
    select('.planner-table tbody').innerHTML = matching.slice(0, visible).map(({ row, index }) => {
      const status = stateOf(row), total = required(row);
      const cells = Array.from({ length: scenario.horizon }, (_, i) => {
        const state = stateOf(row, i + 1);
        return `<td class="planner-unit-cell${scenario.focus === i + 1 ? ' is-focus' : ''}"><span class="planner-cell" data-tone="${state}" title="Through unit ${i + 1}: need ${number(required(row, i + 1))} ${escape(row.unit)} · ${labels[state]}"><span class="planner-sr-only">${labels[state]}</span></span></td>`;
      }).join('');
      return `<tr class="planner-material-row" data-resource="${escape(row.id)}"><th scope="row"><button class="planner-material-toggle" id="row-${index}" data-open="${escape(row.id)}" type="button" aria-expanded="${openRow === row.id}"><span><strong>${escape(row.name)}</strong><small>${escape(row.category)}${row.estimated ? ' · estimated usage / stock' : ''}</small></span><span aria-hidden="true">${openRow === row.id ? '−' : '+'}</span></button>${row.purchase.quantity ? `<small class="planner-row-purchase">+ ${number(row.purchase.quantity)} ${escape(row.unit)} planned · ${money(row.purchase.costCents)}${row.purchase.unpriced ? ' + unpriced' : ''}</small>` : ''}</th><td><b>${row.available == null ? '?' : number(row.available)}</b><small>${escape(row.unit)}${row.incoming ? `<br>+ ${number(row.incoming)} ordered` : ''}</small></td>${cells}<td>${badge(status, status === 'unknown' && row.material ? 'Define input' : '')}<small>${row.quantityKnown ? number(total) + ' ' + escape(row.unit) + ' needed' : 'Usage unresolved'}</small></td></tr>${openRow === row.id ? details(row, index) : ''}`;
    }).join('') || `<tr><td colspan="${scenario.horizon + 3}" class="planner-empty">No materials match this view. Try all materials or another search.</td></tr>`;
    select('#planner-row-count').textContent = `${Math.min(visible, matching.length)} of ${matching.length} material lines`;
    select('#planner-more').hidden = visible >= matching.length;
  }
  function renderBasket() {
    const budget = projection.budget, unit = projection.units[scenario.focus - 1];
    select('.planner-basket').innerHTML = `<div class="planner-basket-head"><p class="planner-eyebrow">Your purchase scenario</p><h3 id="planner-basket-title">What if we buy…</h3><p>Choose packs in a material row, or start with a suggested batch.</p></div><div class="planner-buy-target"><label>Cover through unit<select id="planner-buy-for">${[1, 2, 5, 10, 20].map(n => `<option value="${n}"${scenario.buyFor === n ? ' selected' : ''}>${n}</option>`).join('')}</select></label><button type="button" id="planner-fill">Suggest packs</button></div><p class="planner-caption">Uses available quotes and credits on-order stock. Replaces planned supplier packs. Keeps custom packs.</p><div class="planner-basket-total"><span>Planned purchase cash${budget.unpriced ? ' · partial' : ' · estimate'}</span><strong>${money(budget.totalCents)}</strong><small>${projection.buying.length} purchase lines${budget.unpriced ? ` · ${budget.unpriced} unpriced` : ''}</small></div><dl class="planner-budget"><div><dt>Quoted packs</dt><dd>${money(budget.partsCents)}</dd></div><div><dt>Delivery reserve</dt><dd>${money(budget.freightCents)}</dd></div><div><dt>Tax reserve</dt><dd>${money(budget.taxCents)}</dd></div></dl>${budget.unavailable ? `<p class="planner-warning">${budget.unavailable} proposed lines need an available source.</p>` : ''}<div class="planner-basket-items">${projection.buying.map(row => `<button type="button" data-open="${escape(row.id)}"><span>${escape(row.name)}<small>${row.purchase.packs.map(pack => `${number(pack.count)} × ${escape(pack.option.label)}`).join(' + ')}</small></span><strong>${money(row.purchase.costCents)}${row.purchase.unpriced ? ' + ?' : ''}</strong></button>`).join('') || '<p class="planner-empty">No proposed purchases yet.<br>The outlook starts from recorded stock and existing orders.</p>'}</div><div class="planner-after-buy"><span>Still to source through unit ${scenario.focus}</span><strong>${money(unit.extraPartsCents)}</strong><small>quoted parts beyond this basket${unit.unquoted ? ` · ${unit.unquoted} lines need quantities or quotes` : ''}${unit.unavailable ? ` · ${unit.unavailable} source availability issues` : ''}</small></div><div class="planner-basket-actions"><button type="button" id="planner-reset"${projection.buying.length ? '' : ' disabled'}>Clear purchases</button><button type="button" id="planner-export">Export plan</button></div><details class="planner-pricing-note"><summary>What these estimates include</summary><p>Purchase packs, recorded delivery allowances and a tax reserve. Existing stock creates no new purchase expense. Full build labor and other production costs are in the cost sections below.</p><p>Delivery uses the next recorded batch allowance for the purchase target. Custom packs use merchandise pricing; shipping still needs a quote. Delivered-price offers are not taxed again. Unquoted lines are excluded from dollar totals. Supplier observations are dated, not live availability.</p><p>${escape(data.stockNote)}</p></details><p class="planner-local-note">${saved ? 'Scenario saved in this browser.' : 'Scenario stays in this tab.'} Purchases here are planning assumptions.</p>`;
  }
  function render() {
    const active = document.activeElement, activeId = active?.id, activeValue = active?.value;
    projection = projectProduction(data, scenario);
    renderMilestones();
    const unit = projection.units[scenario.focus - 1];
    select('#planner-focus-title').textContent = scenario.focus === 1 ? 'What the first unit needs' : scenario.focus === 2 ? 'What the second unit needs' : `What we need through unit ${scenario.focus}`;
    select('#planner-focus-note').textContent = unitDescription(unit) + '. Expand a material to adjust packs and inspect its stock evidence.';
    const completed = data.finishes[scenario.finish].completed[scenario.focus] || [];
    if (completed.length) select('#planner-focus-note').textContent += ` Completed stock credits: ${completed.map(m => number(m.quantity) + ' × ' + m.name).join('; ')}.`;
    select('#planner-build-link').href = `/build?material=${data.root}&quantity=${scenario.focus}&finish=${scenario.finish}`;
    renderRows(); renderBasket();
    if (activeId && document.getElementById(activeId) && active !== document.getElementById(activeId)) {
      const replacement = document.getElementById(activeId); replacement.focus({ preventScroll: true });
      if (active?.tagName === 'INPUT') replacement.value = activeValue;
    }
    host.dataset.enhanced = 'true';
  }
  function changed(message = '') { save(); render(); if (message) select('.planner-status').textContent = message; }
  host.addEventListener('click', event => {
    const button = event.target.closest('button'); if (!button) return;
    if (button.dataset.focus) { scenario.focus = Number(button.dataset.focus); visible = 12; changed(); }
    else if (button.dataset.open) {
      openRow = openRow === button.dataset.open ? null : button.dataset.open;
      if (button.closest('.planner-basket')) { select('#planner-search').value = ''; select('#planner-supplier').value = 'all'; visible = projection.rows.length; }
      render();
      if (button.closest('.planner-basket') && openRow) { const index = data.finishes[scenario.finish].rows.findIndex(row => row.id === openRow); document.getElementById('row-' + index)?.scrollIntoView({ block: 'nearest' }); }
    }
    else if (button.dataset.custom) {
      const id = button.dataset.custom;
      if (scenario.custom[id]) delete scenario.custom[id]; else scenario.custom[id] = { quantity: 1, count: 0, priceCents: null };
      changed();
    } else if (button.dataset.adjust) {
      const input = document.getElementById(button.dataset.input); input.value = Math.max(0, Number(input.value) + Number(button.dataset.adjust)); input.dispatchEvent(new Event('input', { bubbles: true }));
    } else if (button.id === 'planner-fill') {
      scenario = fillPurchasePlan(data, scenario, scenario.buyFor); scenario.focus = scenario.buyFor; scenario.horizon = Math.max(scenario.horizon, scenario.focus); visible = 12; changed(`Suggested available packs through unit ${scenario.buyFor}. Review quantities and supplier evidence.`);
    } else if (button.id === 'planner-reset') {
      scenario.orders = {}; scenario.custom = {}; changed('Proposed purchases cleared. Recorded stock is unchanged.');
    } else if (button.id === 'planner-more') { visible += 20; renderRows(); }
    else if (button.id === 'planner-export') {
      const csv = [['Material', 'Unit', 'Available', 'Incoming', 'Need through ' + scenario.focus, 'Proposed quantity', 'Quoted pack cost USD', 'Unpriced packs', 'Coverage', 'Packs'], ...projection.rows.filter(row => required(row) > 0 || row.active?.[scenario.focus] || row.purchase.quantity).map(row => [row.name, row.unit, row.available ?? 'Unknown', row.incoming, required(row), row.purchase.quantity, row.purchase.costCents / 100, row.purchase.unpriced ? 'Yes' : 'No', labels[stateOf(row)], row.purchase.packs.map(p => p.count + ' × ' + p.option.label).join(' + ')])].map(row => row.map(value => '"' + String(value).replace(/"/g, '""') + '"').join(',')).join('\r\n');
      const link = document.createElement('a'), url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
      link.href = url; link.download = `production-plan-${scenario.finish}-through-${scenario.focus}.csv`; link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
    }
  });
  host.addEventListener('change', event => {
    const input = event.target;
    if (input.id === 'planner-finish') { scenario.finish = input.value; openRow = null; changed(); }
    else if (input.id === 'planner-horizon') { scenario.horizon = Number(input.value); scenario.focus = Math.min(scenario.focus, scenario.horizon); changed(); }
    else if (input.id === 'planner-buy-for') { scenario.buyFor = Number(input.value); changed(); }
    else if (['planner-filter', 'planner-supplier'].includes(input.id)) { visible = 12; renderRows(); }
  });
  host.addEventListener('input', event => {
    const input = event.target;
    if (input.id === 'planner-search') { visible = 12; renderRows(); return; }
    if (input.dataset.kind) {
      if (input.value !== '' && !input.checkValidity()) return;
      const id = input.dataset.row, value = Number(input.value);
      if (input.dataset.kind === 'pack') { (scenario.orders[id] ||= {})[input.dataset.key] = Math.max(0, Math.floor(value)); }
      else {
        const field = input.dataset.field;
        scenario.custom[id][field] = field === 'priceCents' ? input.value === '' ? null : Math.round(value * 100) : value;
      }
      changed();
    }
  });
  save(); render();
}
