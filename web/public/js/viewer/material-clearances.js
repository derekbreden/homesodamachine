// The material's fitted interfaces, their default CAD sizes, and the two sets of faces in the viewer.
import { fpt } from "./pick-format.js";
import { PARTS_PATH } from "/contracts/viewer-links.js";

const mm = value => value.toFixed(2);

function faceLink(el, label, file, site) {
  const picks = site.faces.map(([name, x, y, z]) => `face: ${fpt({ x, y, z })} "${name}"`);
  const [az, elevation] = site.view;
  picks.push(`view: az=${az} el=${elevation}`);
  const link = el("a", "material-link", label);
  link.href = `${PARTS_PATH}#step:${encodeURIComponent(site.file || file)}?find=${encodeURIComponent(picks.join("\n"))}`;
  return link;
}

function surfaces(el, label, file, sites) {
  const group = el("div", "clearance-surfaces");
  const target = site => faceLink(el, label, file, site);
  let link = target(sites[0]);
  group.append(link);
  if (sites.length > 1) {
    const select = el("select");
    select.setAttribute("aria-label", "Pocket location");
    for (const site of sites) select.append(el("option", "", site.label));
    select.addEventListener("change", () => {
      const next = target(sites[select.selectedIndex]);
      link.replaceWith(next);
      link = next;
    });
    group.append(select);
  }
  return group;
}

function dimensionTable(el, fit, allowance) {
  const table = el("table", "clearance-table");
  const headers = table.createTHead().insertRow();
  for (const title of ["Dimension (mm)", "Chosen CAD", "Default CAD"]) {
    const th = el("th", "", title);
    th.scope = "col"; headers.append(th);
  }
  const body = table.createTBody();
  for (const dim of fit.dimensions) {
    const row = body.insertRow();
    const th = el("th", "", dim.label); th.scope = "row";
    const external = dim.external ? -1 : 1;
    const ordinary = allowance[dim.motion || fit.motion];
    const total = ordinary * (dim.faces ?? 2) + allowance.supported * (dim.supported || 0);
    let standard = total;
    if (dim.nominal != null) {
      standard = dim.nominal + external * total;
      th.append(el("small", "", `${dim.reference} · ${mm(dim.nominal)}`));
    }
    row.append(th);
    for (const value of [dim.chosen, standard]) {
      const cell = row.insertCell();
      cell.append(el("strong", "", mm(value)));
      if (dim.nominal != null) {
        const clearance = external * (value - dim.nominal);
        cell.append(el("small", "", `${mm(Math.abs(clearance))} ${clearance < 0 ? "interference" : "clearance"}`));
      }
    }
  }
  return table;
}

export function renderClearances(content, records, selected, index, catalog, el, materialLink) {
  const { allowance, guidance } = catalog;
  for (const [i, fit] of records.entries()) {
    const host = index.get(fit.host), mate = index.get(fit.mate);
    const other = selected === host.id ? mate : host;
    const card = el("details", "clearance-fit"); card.open = i === 0;
    const heading = el("summary");
    heading.append(el("strong", "", fit.title), el("span", "", other.description));
    card.append(heading, materialLink(other, other.id + " · " + other.description, { tab: "clearances" }));
    card.append(dimensionTable(el, fit, allowance));
    const rule = fit.motion === "sliding" ? "Sliding fit" : "Static fit";
    const support = fit.support ? ` Add ${mm(allowance.supported)} mm at ${fit.support}.` : "";
    card.append(el("p", "clearance-rule", `${rule} · ${mm(allowance[fit.motion])} mm per mating face.${support}`));
    const views = el("div", "clearance-views");
    views.append(el("h4", "", "Surfaces in 3D"),
      surfaces(el, fit.hostSurface, host.models?.[0]?.file, fit.hostSites),
      surfaces(el, fit.mateSurface, mate.models?.[0]?.file, fit.mateSites));
    card.append(views);
    if (fit.note) card.append(el("p", "clearance-note", fit.note));
    const sources = el("div", "clearance-sources");
    for (const source of [...fit.sources, { label: "Clearance guidance", href: guidance }]) {
      const link = el("a", "material-link", source.label);
      link.href = source.href;
      sources.append(link);
    }
    card.append(sources);
    content.append(card);
  }
}
