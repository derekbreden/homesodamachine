// Local demonstrations only. Feature behavior lives in the linked production modules.
const search = document.querySelector('#guide-material-search');
const results = [...document.querySelectorAll('[data-guide-result]')];
const searchStatus = document.querySelector('#guide-search-status');
function filterMaterials() {
  const query = search.value.trim().toLowerCase();
  for (const result of results) result.hidden = !result.dataset.guideResult.includes(query);
  const count = results.filter(result => !result.hidden).length;
  searchStatus.textContent = query
    ? `${count} sample ${count === 1 ? 'material' : 'materials'} found.`
    : "3 sample materials. Try ‘insertion’ or ‘HSM-000005’.";
}
search.addEventListener('input', filterMaterials);
document.querySelector('[data-guide-focus]').addEventListener('click', () => search.focus());
document.querySelector('[data-guide-clear]').addEventListener('click', () => {
  search.value = '';
  filterMaterials();
  search.focus();
});

const tabs = [...document.querySelectorAll('#guide-tabs [role=tab]')];
function selectTab(tab) {
  for (const item of tabs) {
    const selected = item === tab;
    item.setAttribute('aria-selected', String(selected));
    item.tabIndex = selected ? 0 : -1;
    document.getElementById(item.getAttribute('aria-controls')).hidden = !selected;
  }
}
for (const tab of tabs) {
  tab.addEventListener('click', () => selectTab(tab));
  tab.addEventListener('keydown', event => {
    const index = tabs.indexOf(tab);
    const next = { ArrowRight: (index + 1) % tabs.length, ArrowLeft: (index + tabs.length - 1) % tabs.length, Home: 0, End: tabs.length - 1 }[event.key];
    if (next === undefined) return;
    event.preventDefault();
    selectTab(tabs[next]);
    tabs[next].focus();
  });
}
const rows = [...document.querySelectorAll('#guide-bom .bom-row')];
for (const row of rows) row.querySelector('.bom-select').addEventListener('click', () => {
  for (const item of rows) {
    item.classList.toggle('selected', item === row);
    item.querySelector('.bom-select').setAttribute('aria-pressed', String(item === row));
  }
  document.querySelector('#guide-selection-status').textContent = `${row.querySelector('.bom-description').textContent} selected in this example.`;
});

for (const button of document.querySelectorAll('[data-guide-copy]')) button.addEventListener('click', async () => {
  const code = document.getElementById(button.dataset.guideCopy);
  const status = button.nextElementSibling;
  try {
    await navigator.clipboard.writeText(code.textContent);
    status.textContent = 'Markup copied.';
  } catch {
    const selection = window.getSelection();
    const range = document.createRange();
    range.selectNodeContents(code);
    selection.removeAllRanges();
    selection.addRange(range);
    status.textContent = 'Markup selected. Use your browser’s Copy command.';
  }
});

for (const button of document.querySelectorAll('[data-guide-view]')) button.addEventListener('click', () => {
  const toolbar = button.closest('.cad-workspace-header');
  for (const mode of toolbar.querySelectorAll('[data-guide-view]')) mode.setAttribute('aria-pressed', String(mode === button));
  toolbar.querySelector('.drawing-tools').hidden = button.dataset.guideView !== 'drawing';
});

for (const output of document.querySelectorAll('[data-guide-measure]')) {
  const sample = document.getElementById(output.dataset.guideMeasure);
  const style = getComputedStyle(sample);
  output.textContent = `${style.fontSize} · ${style.fontWeight} weight`;
}
for (const output of document.querySelectorAll('[data-guide-color]')) {
  const color = getComputedStyle(output.closest('div').querySelector('.guide-swatch')).backgroundColor;
  const channels = color.match(/^rgb\((\d+), (\d+), (\d+)\)$/);
  output.textContent = channels ? '#' + channels.slice(1).map(value => Number(value).toString(16).padStart(2, '0')).join('') : color;
}
