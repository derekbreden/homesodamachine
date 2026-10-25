// The two product units and their tooling open the same models their thumbnails
// draw. Description lookup reaches every material and uncataloged CAD model.
import { openDetail } from './cad-detail.js';
import { seatParts } from '/contracts/parts-tree.js';
import { materialForFile, materialIndex, bomCounts, bomCountText } from '/contracts/materials.js';
import { FAUCET_STYLES, FAUCET_FINISHES, faucetStyleFor } from '/contracts/faucet-options.js';
import { state } from './state.js';
import { makeMaterialSearch } from './material-search.js';
import { openMaterial, materialHash } from './material-nav.js';

export function syncFaucetCard(card) {
  const style = FAUCET_STYLES.find((s) => s.id === state.faucetStyle) || FAUCET_STYLES[0];
  const finish = FAUCET_FINISHES.find((f) => f.id === state.faucetFinish) || FAUCET_FINISHES[0];
  card.dataset.file = style.assembly;
  card.dataset.finish = finish.id;
  const material = materialForFile(state.materialCatalog, style.assembly);
  if (material) {
    card.dataset.material = material.id;
    card.querySelector('.assembly-model-link').href = '/3d#' + materialHash(material.id);
    card.querySelector('.name').textContent = material.description;
    card.querySelector('.assembly-note').textContent = material.id;
    syncBomLink(card);
  }
  card.querySelector('.faucet-card-options').textContent = `${style.label} · ${finish.label} · Choose style and finish`;
}

function syncBomLink(card) {
  const id = card.dataset.material, link = card.querySelector('.assembly-bom-link');
  if (!id || !link) return;
  link.href = '/3d#' + materialHash(id, { tab: 'bom' });
  link.textContent = bomCountText(bomCounts(state.materialCatalog, id, { finish: state.faucetFinish })) + ' →';
  link.title = 'Open bill of materials';
}

function renderAssembly({ description, note, file, id }) {
  const card = document.createElement('article');
  card.className = 'card card-assembly';
  card.dataset.file = file;
  card.dataset.type = 'step';
  if (id) card.dataset.material = id;
  const model = document.createElement('a'); model.className = 'assembly-model-link';
  model.href = '/3d#' + (id ? materialHash(id) : 'step:' + encodeURIComponent(file));
  const image = document.createElement('img'); image.alt = '';
  const label = document.createElement('div'); label.className = 'label card-caption';
  const name = document.createElement('span'); name.className = 'name'; name.textContent = description;
  const detail = document.createElement('span'); detail.className = 'assembly-note'; detail.textContent = note;
  label.append(name, detail); model.append(image, label); card.append(model);
  if (id) {
    const bom = document.createElement('a'); bom.className = 'assembly-bom-link';
    bom.addEventListener('click', (event) => {
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault(); event.stopPropagation();
      openMaterial(card.dataset.material, true, { tab: 'bom' });
    });
    card.append(bom); syncBomLink(card);
  }
  if (faucetStyleFor(file)) {
    card.dataset.faucet = '1';
    const options = document.createElement('span'); options.className = 'faucet-card-options';
    label.append(options); syncFaucetCard(card);
  }
  card.addEventListener('click', (event) => {
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    if (card.dataset.material) openMaterial(card.dataset.material);
    else openDetail(card.dataset.file);
  });
  return card;
}

export function buildPartsSection(gridEl, { steps, dxfs, glbs }) {
  const search = makeMaterialSearch(); gridEl.append(search);
  if (!state.materialCatalog) {
    const note = document.createElement('p'); note.className = 'material-catalog-status';
    note.textContent = 'The material catalog is unavailable. You can still search and open CAD models.'; gridEl.append(note);
    const row = document.createElement('div'); row.className = 'assembly-row';
    for (const assembly of seatParts({ steps, dxfs, glbs }).assemblies) if (assembly.model) {
      row.append(renderAssembly({ description: assembly.label, note: assembly.note, file: assembly.model.primary.file }));
    }
    gridEl.append(row); return;
  }
  const index = materialIndex(state.materialCatalog);
  const roots = state.materialCatalog.roots.map((id) => index.get(id)).filter(Boolean);
  for (const [kind, heading] of [['assembly', 'The machine'], ['tooling', 'Build tools']]) {
    const title = document.createElement('h2'); title.className = 'material-section-title'; title.textContent = heading;
    const row = document.createElement('div'); row.className = 'assembly-row' + (kind === 'tooling' ? ' assembly-row-tools' : '');
    for (const m of roots.filter((m) => m.kind === kind)) {
      const file = m.models?.[0]?.file; if (!file || !steps.includes(file)) continue;
      row.append(renderAssembly({ description: m.description, note: m.id, file, id: m.id }));
    }
    if (row.childElementCount) gridEl.append(title, row);
  }
}
