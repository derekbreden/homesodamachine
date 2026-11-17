// Production planning tests cover cumulative stock use, purchase lots, uncertain inputs and cash boundaries.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { coverageFor, freshScenario, optionKey, projectProduction, fillPurchasePlan, materialBalance } from '../contracts/production-plan.js';
import { productionData, readProductionPlanner, renderProductionPlanner } from '../lib/production-planner.js';
import { readMaterialCatalog } from '../lib/material-catalog.js';
import { readMaterialStock } from '../lib/material-stock.js';
import { planMaterial } from '../contracts/material-stock.js';
import { fileURLToPath } from 'node:url';

const offer = (quantity = 10, priceCents = 1000) => ({ quantity, priceCents, label: quantity + '-piece pack', available: true });
function data(rows) {
  return { horizon: 10, taxRate: 0.1, suppliers: [{ id: 'maker', name: 'Maker', shippingCents: { 5: 100, 10: 200, 20: 300 } }],
    finishes: { white: { rows, completed: [] }, black: { rows, completed: [] } } };
}
const row = (changes = {}) => ({ id: 'screws', name: 'Screws', unit: 'ea', available: 7, incoming: 0, quantityKnown: true, estimated: false,
  needs: Array.from({ length: 11 }, (_, i) => i * 4), quote: { supplier: 'maker', priceBasis: 'merchandise', options: [offer()] }, ...changes });
const order = (scenario, resource, option, count) => { scenario.orders[resource] = { [optionKey(option)]: count }; };

test('unit two shares the opening stock with unit one and pack changes carry into later units', () => {
  const value = data([row()]), scenario = freshScenario();
  const first = projectProduction(value, scenario);
  assert.equal(first.units[0].counts.stock, 1);
  assert.equal(first.units[1].counts.short, 1);
  assert.equal(first.units[1].extraPartsCents, 1000);
  order(scenario, 'screws', value.finishes.white.rows[0].quote.options[0], 1);
  const after = projectProduction(value, scenario);
  assert.equal(after.units[3].counts.planned, 1);
  assert.equal(after.units[4].counts.short, 1);
  assert.equal(after.units[1].extraPartsCents, 0);
  assert.equal(after.budget.totalCents, 1210);
  assert.equal(first.units[1].counts.short, 1, 'earlier projection is not mutated');
});

test('orders reduce duplicate purchases while awaiting receipt stays separate from on-hand coverage', () => {
  const value = data([row({ available: 0, incoming: 4 })]);
  const scenario = fillPurchasePlan(value, freshScenario(), 1);
  assert.deepEqual(scenario.orders, {});
  const result = projectProduction(value, scenario);
  assert.equal(result.units[0].counts.incoming, 1);
  assert.equal(result.units[0].ready, false);
  assert.equal(result.units[0].extraPartsCents, 0);
  assert.equal(result.units[1].extraPartsCents, 1000);
});

test('unknown usage remains an active unresolved input even when no numerical usage is available', () => {
  const value = data([row({ quantityKnown: false, needs: Array(11).fill(0), active: Array(11).fill(true) })]);
  const scenario = freshScenario(); order(scenario, 'screws', offer(), 100);
  const result = projectProduction(value, scenario);
  assert.equal(result.units[0].counts.unknown, 1);
  assert.equal(result.units[0].covered, false);
  assert.equal(result.units[0].unquoted, 1);
});

test('an unknown stock balance gets no credit and a proposed custom pack stays visibly unpriced', () => {
  const value = data([row({ available: null, quote: null })]), scenario = freshScenario();
  assert.equal(projectProduction(value, scenario).units[0].counts.unknown, 1);
  scenario.custom.screws = { quantity: 8, count: 1, priceCents: null };
  const result = projectProduction(value, scenario);
  assert.equal(result.units[1].counts.planned, 1);
  assert.equal(result.budget.unpriced, 1);
  assert.equal(result.budget.partsCents, 0);
  assert.equal(result.units[1].ready, false);
});

test('unavailable offers are not suggested or credited as usable proposed stock', () => {
  const option = { ...offer(), available: false }, value = data([row({ available: 0, quote: { options: [option], supplier: 'maker' } })]);
  const scenario = fillPurchasePlan(value, freshScenario(), 2);
  assert.deepEqual(scenario.orders, {});
  order(scenario, 'screws', option, 1);
  const result = projectProduction(value, scenario);
  assert.equal(result.units[0].counts.short, 1);
  assert.equal(result.budget.unavailable, 1);
});

test('manual pack counts apply tier prices and custom merchandise does not tax delivered packs again', () => {
  const option = { ...offer(), tiers: [{ minimum: 2, priceCents: 800 }] };
  const value = data([row({ quote: { priceBasis: 'delivered', supplier: 'maker', options: [option] } })]);
  const scenario = freshScenario(); order(scenario, 'screws', option, 2);
  scenario.custom.screws = { quantity: 1, count: 1, priceCents: 100 };
  const result = projectProduction(value, scenario);
  assert.equal(result.budget.partsCents, 1700);
  assert.equal(result.budget.taxCents, 20, 'tax applies to the custom pack and freight');
  assert.equal(result.budget.totalCents, 1820);
  const customOnly = projectProduction(value, { ...scenario, orders: {} });
  assert.equal(customOnly.budget.freightCents, 0);
});

test('completed subassemblies and reservations flow from the same physical plan into each cumulative target', () => {
  const catalog = { cost_root: 'machine', materials: [{ id: 'machine', kind: 'assembly', bom: { items: [{ material: 'assembly', quantity: 1 }] } }, { id: 'assembly', kind: 'assembly', bom: { items: [{ material: 'part', quantity: 2 }] } }, { id: 'part', kind: 'manufactured' }],
    stock: { asOf: '2026-11-08', opening: { note: 'Counted' }, materials: { assembly: { material: 'assembly', onHand: 2, reserved: 1 } }, resources: { screws: { id: 'screws', name: 'Screws', unit: 'ea', onHand: 20, reserved: 5 } }, inputs: { part: [{ resource: 'screws', quantity: 1 }] } } };
  const before = structuredClone(catalog);
  const result = productionData(catalog, { checkedAt: '2026-11-08', taxRate: 0, suppliers: [], items: [] }, 10);
  const material = result.finishes.white.rows[0];
  assert.equal(material.needs[1], 0);
  assert.equal(material.needs[2], 2);
  assert.equal(material.available, 15);
  assert.equal(result.finishes.white.completed[1][0].quantity, 1);
  assert.deepEqual(catalog, before);
});

test('the published workspace carries every real stock input, unknown usage and missing manufacturing definition', () => {
  const hardware = fileURLToPath(new URL('../../hardware', import.meta.url));
  const value = readProductionPlanner(hardware);
  const catalog = readMaterialCatalog(hardware); catalog.stock = readMaterialStock(hardware, catalog);
  for (const finish of ['white', 'black']) for (const units of [1, 2, 5, 10, 20]) {
    const plan = planMaterial(catalog, catalog.cost_root, units, { finish });
    const rows = new Map(value.finishes[finish].rows.map(row => [row.id, row]));
    for (const resource of plan.resources) {
      assert.equal(rows.get(resource.resource).needs[units], resource.needed);
      assert.equal(rows.get(resource.resource).quantityKnown, resource.quantityKnown);
      assert.equal(rows.get(resource.resource).active[units], true);
    }
    for (const gap of plan.gaps) assert.ok(rows.get('material:' + gap.material).needs[units] > 0);
  }
  const html = renderProductionPlanner(value);
  assert.doesNotMatch(html, /NaN|Infinity/);
  assert.match(html, /production-planner-data/);
  assert.match(html, /Stock &amp; assembly records/);
  for (const [finish, { rows }] of Object.entries(value.finishes)) {
    assert.ok(rows.some(row => row.id === 'siraya85a-clear' && row.uses.includes('HSM-0088') && row.needs[1] > 0));
    assert.ok(rows.some(row => row.id === 'tpu85a-black' && row.uses.includes('HSM-0090') && row.needs[1] > 0));
    assert.ok(rows.some(row => row.id === 'tpu90a-' + finish && row.uses.includes('HSM-0093') && row.needs[1] > 0));
    for (const color of ['white', 'black', 'clear']) {
      assert.ok(rows.some(row => row.id === 'petg-' + color && row.uses.includes('HSM-0579') && row.needs[1] > 0));
    }
    const rod = rows.find(row => row.id === 'B0FYCJJXCS-rod');
    assert.ok(rod.quantityKnown && rod.unit === 'mm' && rod.uses.includes('HSM-0011') && rod.uses.includes('HSM-0459'));
    const foamSeal = rows.find(row => row.id === 'prv-shroud-foam-seal');
    assert.ok(foamSeal.active[1] && !foamSeal.quantityKnown);
    assert.equal(foamSeal.incoming, 83);
    assert.equal(foamSeal.quote, null);
    assert.ok(!rows.some(row => row.name.includes('GE Silicone II')));
    const maskingTape = rows.find(row => row.id === 'B00004Z4CP');
    assert.equal(maskingTape.needs[1], 3);
    assert.equal(maskingTape.incoming, 180);
    assert.equal(coverageFor(maskingTape, 1), 'incoming');
    assert.ok(!rows.some(row => /HSM-0324|HSM-0334|HSM-0335|HSM-0364/.test(row.id)));
    const screw = rows.find(row => row.id === 'svling-B0GHNNYVDH');
    assert.ok(screw.available >= screw.needs[1] && screw.estimated);
    assert.ok(screw.quote.options.every(option => option.available === false));
  }
});

test('reusable equipment remains after each build while consumable stock is depleted', () => {
  const reusable = row({ available: 1, needs: [0, ...Array(10).fill(1)], reusableNeeds: [0, ...Array(10).fill(1)] });
  const result = materialBalance(reusable, 5);
  assert.equal(result.previousConsumed, 0);
  assert.equal(result.onHandBefore, 1);
  assert.equal(result.projectedAfter, 1);
  assert.equal(materialBalance(row(), 1).projectedAfter, 3);
  assert.equal(materialBalance(row(), 2).onHandBefore, 3);
});
