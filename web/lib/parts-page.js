// Lay out the machine and its tooling by how each item is obtained.
import fs from "node:fs/promises";
import path from "node:path";
import { ASSEMBLIES } from "../contracts/parts-tree.js";
import { materialHash } from "../contracts/material-tabs.js";
import { renderHead, renderNav, renderFooter } from "./shell.js";
import { readPartsCatalog } from "./parts-catalog.js";
import { renderPartsViewer } from "./viewer-pages.js";

const groups = [
  { key: "print", name: "Print plates", noun: "plate" },
  { key: "order", name: "Made to order", noun: "part" },
  { key: "shelf", name: "Off the shelf", noun: "part" },
];

const escape = value => String(value ?? "").replace(/[&<>"']/g, char =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]);
const internal = href => typeof href === "string" && /^\/(?![\/\\])/.test(href) ? escape(href) : "";
const countOf = (n, noun) => `${n} ${noun}${n === 1 ? "" : "s"}`;

function partsUrl(scope, group) {
  const query = new URLSearchParams();
  if (scope === "tools") query.set("scope", "tools");
  if (group) query.set("group", group);
  return "/parts" + (query.size ? `?${query}` : "");
}

async function readPlates(hardwareDir) {
  try { return JSON.parse(await fs.readFile(path.join(hardwareDir, "printed-parts", "plates.json"), "utf8")); }
  catch (error) {
    if (error.code === "ENOENT") return [];
    throw error;
  }
}

async function readCatalog(hardwareDir, pointersPath) {
  try { return await readPartsCatalog(hardwareDir, { pointersPath }); }
  catch (error) {
    if (error.code === "ENOENT") return {};
    throw error;
  }
}

function plateCard(plate) {
  return {
    id: plate.id, name: plate.label, image: plate.thumbnail,
    href: plate.href || (plate.material && "/parts#" + materialHash(plate.material, { view: "print" })),
    note: plate.detail || plate.filament,
    related: plate.relatedPrints,
    parts: plate.parts,
  };
}

function printLinks(label, prints) {
  if (!prints?.length) return "";
  return `<details class="parts-related">
    <summary>${label}</summary>
    <ul>${prints.map(print => {
      const title = escape(print.label);
      const href = internal(print.href || (print.material && "/parts#" + materialHash(print.material)));
      return `<li>${href ? `<a href="${href}">${title}</a>` : title}</li>`;
    }).join("")}</ul>
  </details>`;
}

function tile(card, { plate, large }) {
  const name = escape(card.name);
  const image = internal(card.image);
  const href = internal(card.href);
  const graphic = image
    ? `<span class="parts-tile-image"><img src="${image}" alt="" decoding="async"${plate ? "" : ' loading="lazy"'}></span>`
    : `<span class="parts-tile-image parts-tile-text-frame"><span class="parts-tile-text">${name}</span></span>`;
  const meta = card.provider || (large && typeof card.note === "string" ? card.note : "");
  const caption = image ? `<span class="parts-tile-name">${name}</span>` : "";
  const content = graphic + caption + (meta ? `<span class="parts-tile-meta">${escape(meta)}</span>` : "");
  return `<li>${href
    ? `<a class="parts-tile" href="${href}" title="${name}"${plate ? ` data-plate-search="${name}" data-plate-parts="${escape((card.parts || []).map(part => part.label).join(" "))}"` : ""}>${content}</a>`
    : `<div class="parts-tile">${content}</div>`}
    ${large && card.parts?.length > 1 ? printLinks("Parts on this plate", card.parts) : ""}
    ${large ? printLinks("Separate print jobs", card.related) : ""}</li>`;
}

function groupSection(group, cards, scope, focused) {
  const { key, name, noun } = group;
  const tiles = key === "shelf" ? cards : cards.filter(card => internal(card.image));
  const withoutImages = key === "shelf" ? [] : cards.filter(card => !internal(card.image));
  const tileCount = countOf(cards.length, noun);
  const expand = !focused && tiles.length > 0;
  return `<section id="parts-${key}" class="parts-group parts-group-${key}" aria-labelledby="parts-${key}-title">
    <header class="parts-group-heading">
      <h2 id="parts-${key}-title">${name}</h2>
      <span class="parts-count">${tileCount}</span>
      ${expand ? `<a class="parts-enlarge" href="${partsUrl(scope, key)}" aria-label="Enlarge ${name.toLowerCase()} thumbnails">Enlarge <span aria-hidden="true">↗</span></a>` : ""}
    </header>
    <div class="parts-group-items">
      ${tiles.length ? `<ul class="parts-tiles" role="list">${tiles.map(card => tile(card, { plate: key === "print", large: focused })).join("")}</ul>` : ""}
      ${withoutImages.length ? `<details class="parts-no-models"${!tiles.length || focused ? " open" : ""}>
        <summary>${countOf(withoutImages.length, noun)} without ${key === "print" ? "a preview" : "a 3D model"}</summary>
        <ul>${withoutImages.map(card => {
          const href = internal(card.href);
          const title = escape(card.name);
          return `<li>${href ? `<a href="${href}">${title}</a>` : title}</li>`;
        }).join("")}</ul>
      </details>` : ""}
      ${cards.length ? "" : `<p class="parts-empty">No ${noun}s in this group.</p>`}
    </div>
  </section>`;
}

export function mountPartsPage(app, { hardwareDir, pointersPath }) {
  app.get("/parts", async (req, res) => {
    const scope = req.query.scope === "tools" ? "tools" : "machine";
    const focus = groups.find(group => group.key === req.query.group);
    const searchQuery = typeof req.query.q === "string" ? req.query.q.slice(0, 160) : "";
    const [plates, catalog] = await Promise.all([readPlates(hardwareDir), readCatalog(hardwareDir, pointersPath)]);
    const data = {
      print: plates.filter(plate => plate.scope === scope).map(plateCard),
      order: catalog[scope]?.madeToOrder ?? [],
      shelf: catalog[scope]?.offTheShelf ?? [],
    };
    const current = focus ? [focus] : groups;
    const modelLink = (model, name) => {
      const image = internal(catalog.machine?.assemblyImages?.[model]);
      const thumb = image ? `<span class="parts-tile-image"><img src="${image}" alt="" decoding="async"></span>` : "";
      return `<a href="/parts#step:${encodeURIComponent(model)}">${thumb}<span>${name} <span aria-hidden="true">↗</span></span></a>`;
    };
    const toolModels = catalog.tools?.assemblies ?? [];
    res.set("Cache-Control", "no-cache").type("html").send(
      renderHead({
        title: `${focus?.name ?? "Parts"} · Home Soda Machine`,
        pageClass: "site-interior site-parts",
        pageHead: '<link rel="stylesheet" href="/css/parts.css">',
      }) +
      renderNav({ active: "parts", searchQuery }) +
      `<main id="parts-catalog" class="parts-catalog site-light${focus ? " parts-focused" : ""}">
        <header class="parts-heading">
          <h1>Parts</h1>
          <nav class="parts-scope" aria-label="Parts to show">
            ${["machine", "tools"].map(value => `<a href="${partsUrl(value, focus?.key)}"${value === scope ? ' aria-current="page"' : ""}>${value === "machine" ? "Machine" : "Tools"}</a>`).join("")}
          </nav>
          ${scope === "machine" ? `<nav class="parts-assembly-links" aria-label="Assembled models">
            ${modelLink(ASSEMBLIES[0].model, "Machine in 3D")}${modelLink(ASSEMBLIES[1].model, "Faucet in 3D")}
          </nav>` : toolModels.length ? `<details class="parts-tool-models">
            <summary>Tools in 3D</summary>
            <ul>${toolModels.map(model => `<li><a href="${internal(model.href)}">${escape(model.name)}</a></li>`).join("")}</ul>
          </details>` : ""}
        </header>
        ${focus ? `<a class="parts-overview" href="${partsUrl(scope)}"><span aria-hidden="true">←</span> All groups</a>` : ""}
        <div class="parts-map">${current.map(group => groupSection(group, data[group.key], scope, Boolean(focus))).join("")}</div>
      </main>` +
      renderPartsViewer() + renderFooter({ siteFooter: true }),
    );
  });
}
