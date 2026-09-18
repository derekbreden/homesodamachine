const root = document.querySelector(".unit-page");

if (root) {
  const included = root.querySelector("#included");
  const openIncluded = () => {
    if (included && location.hash === "#included") included.open = true;
  };
  root.querySelector('a[href="#included"]')?.addEventListener("click", () => {
    included.open = true;
  });
  window.addEventListener("hashchange", openIncluded);
  openIncluded();

  const checks = [...root.querySelectorAll('.unit-checks input[type="checkbox"]')];
  if (checks.length) {
    const key = `hsm-unit-${root.dataset.unit}-preparation`;
    try {
      const saved = JSON.parse(localStorage.getItem(key));
      for (const check of checks) check.checked = saved?.[check.name] === true;
    } catch { /* The checklist also works when browser storage is unavailable. */ }
    for (const check of checks) check.addEventListener("change", () => {
      try {
        localStorage.setItem(key, JSON.stringify(Object.fromEntries(checks.map(input => [input.name, input.checked]))));
      } catch { /* Browser storage is optional. */ }
    });
  }
}
