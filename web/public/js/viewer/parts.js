// The /3d grid: the machine's two units, one thumbnail each.
//
// A card draws the model it opens (grid.js's paintStepThumb), so what is on the
// card and what is behind it are one read of one file.
//
// contracts/parts-tree.js states the tree — imported here over the URL the server
// serves it at and by path on the Node side, one file either way. Each root is one
// card, and the card opens that assembly in the detail modal. EVERYTHING ELSE IS
// REACHED BY OPENING IT: arm Select → Component, click a solid, take the file the
// panel offers. That includes the cold core, which is one component of the
// enclosure and an assembly in its own right — so the page has no third card for
// it and no shelf under the two.
//
// A CARD IS A PART, NOT A FILE. `seatParts` folds the `.step` and the `.dxf` of
// one cut part into a single part; `data-file` and `data-type` are what grid.js's
// lazy window and live.js's repaint select on.
//
// THIS RUNS AHEAD OF EVERY CAD RENDER IN THE REPOSITORY. `main.js` calls
// `applyInitialRoute` after `buildGrid`, and the render family in tools/render/
// opens `/3d?file=…` and waits on `__hsm.mountedStepFile` — so a throw here is
// not a broken page, it is a scene that never mounts. contracts/parts-tree.js
// names them.

import { openDetail } from "./cad-detail.js";
import { seatParts } from "/contracts/parts-tree.js";

function esc(s) {
  return String(s ?? "")
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// An assembly: its render, the name the machine's docs call it by, and what it
// holds. The click opens the assembly, which is where its own parts are reached.
function renderAssembly(assembly) {
  const card = document.createElement("div");
  card.className = "card card-assembly";
  card.dataset.file = assembly.model.primary.file;
  card.dataset.type = assembly.model.primary.type;
  card.innerHTML = `<img alt="">` +
    `<div class="label"><span class="name-row">` +
    `<span class="name">${esc(assembly.label)}</span></span>` +
    `<span class="assembly-note">${esc(assembly.note)}</span></div>`;
  card.addEventListener("click", () => openDetail(assembly.model.primary.file));
  return card;
}

export function buildPartsSection(gridEl, { steps, dxfs, glbs }) {
  const tree = seatParts({ steps, dxfs, glbs });

  // The directories holding files no assembly, install-kit, purchased, or
  // tooling root claimed.
  // Nothing below the two cards is drawn, so this warning is the visible half of
  // that gate.
  if (tree.unseated.length) {
    const warn = document.createElement("div");
    warn.className = "grid-warn";
    warn.innerHTML = `<b>Unclassified CAD:</b><ul>` +
      tree.unseated.map((d) => `<li><code>${esc(d)}</code> has no appliance, install-kit, ` +
        `purchased, or workshop classification — classify it in ` +
        `<code>contracts/parts-tree.js</code></li>`)
        .join("") + `</ul>`;
    gridEl.appendChild(warn);
  }

  const row = document.createElement("div");
  row.className = "assembly-row";
  for (const assembly of tree.assemblies) {
    if (assembly.model) row.appendChild(renderAssembly(assembly));
  }
  gridEl.appendChild(row);
}
