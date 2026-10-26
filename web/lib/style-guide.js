import { renderHead, renderNav, renderPageHeader, renderFooter } from './shell.js';
import { COST_CSS } from './cost.js';
import { SIGNUP_BUTTON_CSS } from './landing.js';
import { readMaterialCatalog } from './material-catalog.js';

const escape = value => String(value).replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
const repo = 'https://github.com/derekbreden/homesodamachine/blob/main/';
const source = (path, label) => `<a href="${repo}${path}">${escape(label)}</a>`;

// The displayed example and its copyable markup are the same string.
function example({ id, title, usage, markup, sources }) {
  return `<article class="guide-example" id="${id}">
  <h3>${title}</h3>
  <p class="guide-usage">${usage}</p>
  <div class="guide-preview">${markup}</div>
  <p class="guide-sources">Production source: ${sources.map(([path, label]) => source(path, label)).join(' ')}</p>
  <details class="guide-code"><summary>Markup for ${title.toLowerCase()}</summary>
    <pre><code id="${id}-code">${escape(markup)}</code></pre>
    <div class="material-actions"><button type="button" data-guide-copy="${id}-code">Copy markup</button><span role="status"></span></div>
  </details>
</article>`;
}

function renderGuide(hardwareDir) {
  const { materials } = readMaterialCatalog(hardwareDir);
  const find = id => materials.find(material => material.id === id);
  const root = find('HSM-000006');
  const samples = [root, find('HSM-000005'), find('HSM-000161')];
  const rows = ['HSM-000151', 'HSM-000152', 'HSM-000155'].map(id => ({ material: find(id), item: root.bom.items.find(item => item.material === id) }));
  const materialLink = material => `/3d#material:${material.id}`;
  const documentLink = document => document.path.endsWith('.pdf') ? `/read/${document.path}` : repo + 'hardware/' + document.path;

  const roles = [
    { name: 'Page heading', sample: '<h2 class="cost-title" id="guide-type-heading">Parts by category</h2>', id: 'guide-type-heading', use: 'Introduce a page or major section. Cost uses a smaller heading inside its expandable panels.', path: 'web/lib/cost.js', selector: '.cost-title' },
    { name: 'Body copy', sample: '<p id="guide-type-body">Two flavors, chilled carbonated water, on tap.</p>', id: 'guide-type-body', use: 'Sentences that carry the page’s main explanation. Inherit the shared body font and line height.', path: 'web/lib/shell.js', selector: 'body' },
    { name: 'Primary name', sample: `<span class="bom-description" id="guide-type-name">${escape(rows[0].material.description)}</span>`, id: 'guide-type-name', use: 'The thing a reader is finding or choosing. BOM descriptions and cost category labels share this size and primary text color.', path: 'web/public/css/materials.css', selector: '.bom-description' },
    { name: 'Key number', sample: '<span class="bom-quantity" id="guide-type-number">2 ea</span>', id: 'guide-type-number', use: 'Quantities and amounts stay in the primary text color, with tabular digits for comparison.', path: 'web/public/css/materials.css', selector: '.bom-quantity' },
    { name: 'Identifier', sample: `<span class="bom-number" id="guide-type-id">${rows[0].material.id}</span>`, id: 'guide-type-id', use: 'Supporting identity. The BOM uses monospace; cost percentages use the same size in the body font.', path: 'web/public/css/materials.css', selector: '.bom-number' },
    { name: 'Explanatory note', sample: '<p class="cost-note" id="guide-type-note">Quantities are per assembly.</p>', id: 'guide-type-note', use: 'Scope and interpretation. Keep this supporting information below the names and key numbers in emphasis.', path: 'web/lib/cost.js', selector: '.cost-note' },
  ];
  const typeMarkup = roles.map(role => `<div class="guide-role">
  <div class="guide-role-label">${role.name}</div>
  <div class="guide-role-sample">${role.sample}<span class="guide-measure" data-guide-measure="${role.id}"></span></div>
  <div class="guide-role-note">${role.use}<br>${source(role.path, role.selector)}</div>
</div>`).join('\n');
  const colors = [
    ['--bg', 'Page and recessed surfaces'], ['--surface', 'Cards and fields'], ['--surface-2', 'Raised and hover surfaces'], ['--border', 'Edges and dividers'],
    ['--text', 'Primary information'], ['--text-2', 'Secondary information'], ['--text-3', 'Explanatory notes'], ['--accent', 'Links and selection'],
    ['--action', 'Primary action'], ['--on-action', 'Text on the primary action'], ['--ok', 'Success feedback'], ['--err', 'Error feedback'],
  ];
  const paletteMarkup = `<dl class="guide-palette">\n${colors.map(([token, use]) => `  <div><dt><span class="guide-swatch" style="--swatch: var(${token})" aria-hidden="true"></span>${token}</dt><dd>${use}<span class="guide-measure" data-guide-color="${token}"></span></dd></div>`).join('\n')}\n</dl>`;
  const buttonsMarkup = `<div class="guide-buttons">
  <button type="button" class="signup-btn" data-guide-focus>Focus the search</button>
  <div class="material-actions"><button type="button" data-guide-clear>Clear search</button></div>
  <a class="material-link" href="${documentLink(root.documents[0])}">Assembly guide</a>
</div>`;
  const endcapDrawing = find('HSM-000009').documents.find(document => document.kind === 'engineering-drawing');
  const drawingMarkup = `<a class="material-document material-drawing-feature" href="${documentLink(endcapDrawing)}">
  <span class="material-document-kind">Engineering drawing</span>
  <strong>${escape(endcapDrawing.title)}</strong>
  <span>Open in Drawing →</span>
</a>`;
  const workspaceMarkup = `<header class="cad-workspace-header" id="guide-workspace-toolbar">
  <div class="cad-context"><div class="cad-title">Carbonator endcap · 316 stainless, 2 ports</div></div>
  <div class="cad-view-tools">
    <div class="cad-view-slot"><div class="material-view-switch" role="group" aria-label="Example material view">
      <button type="button" aria-pressed="false" data-guide-view="3d">3D</button>
      <button type="button" aria-pressed="true" data-guide-view="drawing">Drawing</button>
    </div></div>
    <div class="cad-document-slot"><div class="drawing-tools" role="group" aria-label="Example drawing controls">
      <div class="drawing-zoom"><button type="button" aria-label="Zoom out">−</button><button type="button" aria-label="Fit drawing to page">Fit</button><button type="button" aria-label="Zoom in">+</button></div>
      <details class="workspace-menu"><summary aria-label="Drawing actions">⋯</summary><div class="workspace-menu-body"><div class="drawing-menu-zoom"><span>Zoom</span><button type="button" aria-label="Zoom out">−</button><button type="button" aria-label="Zoom in">+</button></div><a href="${documentLink(endcapDrawing)}">Open full drawing</a><a href="/docs/${endcapDrawing.path}?download=1" download>Download PDF</a></div></details>
    </div></div>
  </div>
  <div class="cad-header-actions"><button type="button" class="materials-toggle" aria-expanded="true">Materials</button><button type="button" class="cv-close" aria-label="Close">×</button></div>
</header>`;
  const searchMarkup = `<div class="material-search">
  <label>Find a material<input id="guide-material-search" type="search" placeholder="Description, part number or alias…" aria-describedby="guide-search-status" autocomplete="off"></label>
  <p class="material-search-status" id="guide-search-status" role="status">3 sample materials. Try ‘insertion’ or ‘HSM-000005’.</p>
  <div class="material-search-results">
${samples.map(material => `    <a href="${materialLink(material)}" data-guide-result="${escape([material.description, material.id, ...(material.aliases || [])].join(' ').toLowerCase())}"><strong>${escape(material.description)}</strong><span>${material.id} · ${material.kind}</span></a>`).join('\n')}
  </div>
</div>`;
  const bomMarkup = `<div class="material-tabs" id="guide-tabs" role="tablist" aria-label="Example material relationships">
  <button type="button" id="guide-tab-bom" role="tab" aria-selected="true" aria-controls="guide-bom">BOM</button>
  <button type="button" id="guide-tab-docs" role="tab" aria-selected="false" aria-controls="guide-docs" tabindex="-1">Documents</button>
</div>
<div id="guide-bom" role="tabpanel" aria-labelledby="guide-tab-bom">
  <p class="material-scope">Three rows from the ${escape(root.description.toLowerCase())} parts list. Quantities per assembly.</p>
  <div class="bom-tree">
${rows.map(({ material, item }, i) => `    <div class="bom-row${i === 0 ? ' selected' : ''}" style="--depth: 0">
      <button type="button" class="bom-disclosure" disabled aria-label="No child materials">·</button>
      <button type="button" class="bom-select" aria-pressed="${i === 0}" aria-label="${escape(material.description)}, ${item.quantity} ${item.unit} in this assembly"><span class="bom-description">${escape(material.description)}</span><span class="bom-number">${material.id}</span></button>
      <span class="bom-quantity">${item.quantity} ${item.unit}</span>
    </div>`).join('\n')}
  </div>
  <p class="material-selection-note" id="guide-selection-status" role="status">${escape(rows[0].material.description)} selected in this example.</p>
</div>
<div id="guide-docs" role="tabpanel" aria-labelledby="guide-tab-docs" hidden>
${root.documents.map(document => `  <a class="material-document" href="${documentLink(document)}"><strong>${escape(document.title)}</strong><span>${escape(root.description)}</span></a>`).join('\n')}
</div>`;
  const panelMarkup = `<details class="cost-panel" open>
  <summary>
    <span><span class="cost-panel-heading">Parts by category</span><span class="cost-panel-caption">Illustrative amounts for this style example.</span></span>
    <span class="cost-panel-metrics"><span class="cost-panel-value"><strong>$100.00</strong><small>example total</small></span></span>
    <span class="cost-panel-marker" aria-hidden="true"></span>
  </summary>
  <div class="cost-panel-content">
    <h3 class="cost-title">Example category</h3>
    <div class="cost-bar">
      <div class="cost-bl">FDM printed parts</div>
      <div class="cost-bt" aria-hidden="true"><div class="cost-bf" style="width: 25%"></div></div>
      <div class="cost-bv">$25.00</div><div class="cost-bp">25.0%</div>
    </div>
    <p class="cost-note">The name and amount carry the row. The percentage and note support it.</p>
  </div>
</details>`;

  return `<main class="cost-wrap guide site-content">
  <header>
    <p>A small reference for building pages on Home Soda Machine. These examples load the same styles as the pages they come from.</p>
    <p>Choose text by its role and importance. The cost page is the reference for compact names, numbers and supporting text. Body copy inherits the shared shell.</p>
    <nav class="guide-contents" aria-label="Style guide sections"><a href="#text-color">Text and color</a><a href="#controls">Links and controls</a><a href="#data">Data and disclosure</a></nav>
  </header>
  <section class="guide-section" id="text-color" aria-labelledby="text-color-title">
    <h2 class="cost-title" id="text-color-title">Text and color</h2>
    ${example({ id: 'text-roles', title: 'Reading hierarchy', usage: 'Match the role before matching the size. The readouts show the font currently rendered by the production CSS. Give compact text room to wrap and keep essential information prominent.', markup: typeMarkup, sources: [['web/lib/shell.js', 'Shared body and palette'], ['web/lib/cost.js', 'Cost text roles'], ['web/public/css/materials.css', 'Material text roles']] })}
    ${example({ id: 'color-roles', title: 'Color roles', usage: 'Use the shared variables for their named purpose. Size, weight and placement also carry emphasis; a color change alone should not be the only sign of selection or feedback.', markup: paletteMarkup, sources: [['web/lib/shell.js', ':root variables'], ['brand/README.md', 'Brand palette']] })}
  </section>
  <section class="guide-section" id="controls" aria-labelledby="controls-title">
    <h2 class="cost-title" id="controls-title">Links and controls</h2>
    ${example({ id: 'buttons', title: 'Actions, links and keyboard focus', usage: 'Use a link for navigation and a button for an action. The orange button gives a primary action emphasis; the compact material button supports it. Try Tab to see their production focus indicators. These buttons focus and clear the search below.', markup: buttonsMarkup, sources: [['web/lib/landing.js', '.signup-btn'], ['web/public/css/materials.css', '.material-actions and .material-link']] })}
    ${example({ id: 'workspace', title: 'Model and drawing workspace', usage: 'Group part navigation, view mode, drawing tools and workspace actions in one toolbar. On phones the view tools occupy a second row. Zoom steps move into the drawing menu at narrow widths. This layout example switches modes; the production viewer connects zoom to the sheet. Standalone readers use the same grouping for the title, page navigation and page-fit controls.', markup: workspaceMarkup, sources: [['web/public/css/materials.css', '.cad-workspace-header'], ['web/public/js/viewer/material-drawing.js', 'Drawing mode and controls'], ['web/lib/document-reader.js', 'Standalone reader'], ['web/public/css/workspace.css', 'Shared action menus']] })}
    ${example({ id: 'engineering-drawing', title: 'Featured engineering drawing', usage: 'Pin a part’s own engineering drawing first in Documents. Drawing is also a persistent workspace mode. The document row opens it in the viewer; this example opens the full reader.', markup: drawingMarkup, sources: [['web/public/css/materials.css', '.material-drawing-feature'], ['web/public/js/viewer/material-panel.js', 'Material documents']] })}
    ${example({ id: 'search', title: 'Material search', usage: 'Give the field a visible label and supporting status. Results put the description first and the identity second. This working sample filters three catalog records; its result links open the real materials.', markup: searchMarkup, sources: [['web/public/css/materials.css', '.material-search'], ['web/public/js/viewer/material-search.js', 'Production search behavior']] })}
  </section>
  <section class="guide-section" id="data" aria-labelledby="data-title">
    <h2 class="cost-title" id="data-title">Data and disclosure</h2>
    ${example({ id: 'selection', title: 'Material rows and selected states', usage: 'A selected tab has a filled background and underline. A selected row also keeps its pressed state in the markup. Click a row, switch tabs, or use the arrow keys on the tab list. Selection changes only this example.', markup: bomMarkup, sources: [['web/public/css/materials.css', 'BOM rows, tabs and documents'], ['web/public/js/viewer/material-panel.js', 'Production relationships'], ['hardware/ledger/materials.json', 'Catalog content']] })}
    ${example({ id: 'disclosure', title: 'Expandable panel and cost row', usage: 'Keep a useful heading and headline value visible when a panel is collapsed. Native details and summary provide disclosure without JavaScript. The cost row wraps its name above the values on phones.', markup: panelMarkup, sources: [['web/lib/cost.js', '.cost-panel and .cost-bar']] })}
  </section>
  <section class="guide-section" aria-labelledby="using-guide-title">
    <h2 class="cost-title" id="using-guide-title">Using this reference</h2>
    <p>Each example offers its markup and a link to the styles that render it. Reuse the production classes and connect controls to the feature’s behavior. The local demonstrations live in ${source('web/public/style-guide.js', 'style-guide.js')}; their sample hooks belong to this page.</p>
    <p>Page introductions, content surfaces, spacing and typography come from ${source('web/public/css/site.css', 'the shared site styles')}. Owner pages use the same typeface with ${source('web/public/css/unit.css', 'a layout for setup and reference')}. CAD measurements use specialized numeric displays.</p>
    <p>Add a pattern here when new work needs a reusable reference. Apply corrections to existing pages where a concrete readability or hierarchy problem has been identified.</p>
  </section>
</main>
<script src="/style-guide.js" defer></script>`;
}

export function mountStyleGuideRoutes(app, { hardwareDir } = {}) {
  app.get('/style-guide', (_req, res) => {
    res.set('Content-Type', 'text/html; charset=utf-8');
    res.set('Cache-Control', 'no-cache');
    res.send(renderHead({
      title: 'Website style guide — Home Soda Machine',
      pageClass: 'site-interior',
      pageStyles: COST_CSS + '\n' + SIGNUP_BUTTON_CSS,
      pageHead: '<link rel="stylesheet" href="/css/workspace.css"><link rel="stylesheet" href="/css/materials.css"><link rel="stylesheet" href="/css/style-guide.css">',
    }) + renderNav() + renderPageHeader({ eyebrow: 'Style guide', title: 'One visual language.', description: 'The typography, surfaces, and working components shared across Home Soda Machine.' }) + renderGuide(hardwareDir) + renderFooter({ siteFooter: true }));
  });
}
