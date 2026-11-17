// Find material records, construction features and the print plates on the current page.
const form = document.getElementById("site-search");
if (form) mountSearch(form);

function mountSearch(form) {
  const input = document.getElementById("site-search-input");
  const status = document.getElementById("site-search-status");
  const results = document.getElementById("site-search-results");
  let catalog, features, timer, pending, revision = 0;

  function read(url) {
    return fetch(url).then(response => {
      if (!response.ok) throw new Error(`Search request returned ${response.status}`);
      return response.json();
    });
  }

  function message(text) {
    const p = document.createElement("p");
    p.textContent = text;
    results.replaceChildren(p);
    status.textContent = text;
  }

  function hide() {
    ++revision;
    clearTimeout(timer);
    timer = pending = null;
    results.hidden = true;
    status.textContent = "";
  }

  function link({ title, meta, href }) {
    const a = document.createElement("a");
    const name = document.createElement("strong");
    const details = document.createElement("span");
    a.href = href;
    name.textContent = title;
    a.append(name);
    if (meta) { details.textContent = meta; a.append(details); }
    return a;
  }

  function result(hit) {
    const record = link(hit);
    record.dataset.searchResult = "";
    if (!hit.locations?.length) return record;
    const entry = document.createElement("div");
    entry.className = "nav-search-entry";
    const locations = document.createElement("details");
    const summary = document.createElement("summary");
    summary.textContent = hit.locations.length === 1 ? "Installed location" : "Installed locations";
    locations.append(summary, ...hit.locations.map(link));
    entry.append(record, locations);
    return entry;
  }

  async function update() {
    clearTimeout(timer);
    timer = null;
    const query = input.value.trim();
    if (!query) return hide();
    const request = ++revision;
    results.hidden = false;
    message("Looking up parts…");
    catalog ??= read("/api/materials").catch(error => { catalog = null; throw error; });
    features ??= read("/api/features").catch(() => { features = null; return {}; });
    try {
      const [
        data, { file, features: available = [], instances = [] }, { searchCatalog, searchWords, materialForFile },
        { matchFeatures, instanceLabel }, { featureUrl }, { materialHash }, { instancesInScene },
      ] = await Promise.all([
        catalog, features, import("/contracts/materials.js"), import("/contracts/features.js"),
        import("/contracts/step-locations.js"), import("/contracts/material-tabs.js"),
        import("/contracts/material-instances.js"),
      ]);
      if (request !== revision) return;

      const materialUrl = (id, tab) => "/parts#" + materialHash(id, { panel: "materials", tab });
      const owner = file && instances.length ? materialForFile(data, file) : null;
      const locationsOf = id => owner ? instancesInScene(data, owner.id, id, instances).map(instance => ({
        title: instance.label,
        href: "/parts#" + materialHash(owner.id, { instance: instance.name }),
      })) : [];
      const partHits = searchCatalog(data, query).slice(0, 16).map(({ material, line, match, unmatched }) =>
        material ? { title: material.description, href: materialUrl(material.id),
          locations: locationsOf(material.id),
          meta: `${material.id} · ${material.kind}${match === "suggestion" ? " · Possible match" : ""}${unmatched?.length ? " · Unmatched: " + unmatched.join(", ") : ""}` }
          : { title: line.label, href: materialUrl(line.holders[0].id, "cost"), meta: "Stock and supplies" },
      );
      const featureHits = matchFeatures(query, available).slice(0, 6).map(feature => ({
        title: feature.label,
        meta: "Feature of " + instanceLabel(feature.body),
        href: featureUrl(feature.key, feature.file || file),
      }));
      const words = searchWords(query);
      const wantsPlate = words.includes("print") || words.includes("plate");
      const terms = words.filter(word => word !== "print" && word !== "plate");
      const plateHits = [...document.querySelectorAll("a[data-plate-search]")].filter(a =>
        (terms.length || wantsPlate) && terms.every(term =>
          searchWords(a.dataset.plateSearch + (wantsPlate ? " " + a.dataset.plateParts : "")).some(word => word.startsWith(term)),
        ),
      ).map(a => ({ title: a.dataset.plateSearch, meta: "Print plate", href: a.href }));
      const hits = [...plateHits, ...partHits, ...featureHits];
      if (!hits.length) return message("No matches. Try a part name or number.");
      results.replaceChildren(...hits.map(result));
      status.textContent = `${hits.length} result${hits.length === 1 ? "" : "s"}`;
    } catch {
      if (request === revision) message("Part search is unavailable. Try again.");
    }
  }

  input.addEventListener("input", () => {
    ++revision;
    clearTimeout(timer);
    pending = null;
    if (!input.value.trim()) hide();
    else timer = setTimeout(refresh, 100);
  });
  const refresh = () => (pending = update());
  input.addEventListener("focus", () => { if (input.value.trim() && results.hidden) refresh(); });
  form.addEventListener("submit", async event => {
    event.preventDefault();
    if (!input.value.trim()) { input.focus(); return; }
    await (results.hidden || timer ? refresh() : pending);
    const links = results.querySelectorAll("[data-search-result]");
    if (links.length === 1) links[0].click();
    else if (links.length) links[0].focus();
    else input.focus();
  });
  form.addEventListener("keydown", event => {
    if (event.key === "Escape") {
      if (results.hidden && !input.value) return;
      event.preventDefault();
      event.stopPropagation();
      input.value = "";
      input.focus();
      hide();
      return;
    }
    if (!["ArrowDown", "ArrowUp"].includes(event.key) || results.hidden) return;
    const links = [...results.querySelectorAll("a, summary")].filter(node => node.getClientRects().length);
    if (!links.length) return;
    event.preventDefault();
    const current = links.indexOf(document.activeElement);
    const next = current + (event.key === "ArrowDown" ? 1 : -1);
    (links[next] || (current === -1 ? links.at(-1) : input)).focus();
  });
  form.addEventListener("focusout", event => {
    if (!form.contains(event.relatedTarget)) hide();
  });
  document.addEventListener("pointerdown", event => { if (!form.contains(event.target)) hide(); });
  if (input.value.trim()) input.focus({ preventScroll: true });
}
