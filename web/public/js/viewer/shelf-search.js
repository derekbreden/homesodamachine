// Bind shelf search and start its catalog while the CAD viewer modules load.
import { state } from "./state.js";
import { makeMaterialSearch } from "./material-search.js";

export async function loadMaterialCatalog() {
  const response = await fetch("/api/materials").catch(() => null);
  state.materialCatalog = response?.ok ? await response.json() : null;
  state.materialCatalogTag = response?.ok ? response.headers.get("ETag") : null;
}

let catalogPending = true;
let openWhenReady = null;
let ready = false;
export function enableShelfSearchNavigation() {
  ready = true;
  openWhenReady?.();
  openWhenReady = null;
}

function mountShelfSearch() {
  const search = makeMaterialSearch({
    catalogPending: () => catalogPending,
    navigate(open) {
      if (ready) open();
      else openWhenReady = open;
    },
  });
  document.getElementById("grid").prepend(search);
  return loadMaterialCatalog().finally(() => {
    catalogPending = false;
    search.refresh();
  });
}

export const initialCatalog = location.pathname.replace(/\/$/, "") === "/3d" ? mountShelfSearch() : undefined;
