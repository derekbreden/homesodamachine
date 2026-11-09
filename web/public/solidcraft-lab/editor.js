// The editor loads the pinned upstream engine and reports readiness to its lab host.
const base = '/labs/solidcraft/beduan/runtime/';
try {
  const response = await fetch('/solidcraft-lab/runtime.json');
  if (!response.ok) throw new Error('The runtime manifest is unavailable.');
  const runtime = await response.json();
  const { default: init, ...bindings } = await import(base + runtime.module);
  const wasm = await init({ module_or_path: base + runtime.wasm });
  window.wasmBindings = bindings;
  window.solidcraftWasm = wasm;
  const deadline = performance.now() + 180000;
  while (!window.solidcraft) {
    if (performance.now() > deadline) throw new Error('The native editor did not become ready.');
    await new Promise(resolve => setTimeout(resolve, 50));
  }
  parent.postMessage({ type: 'solidcraft-lab-ready' }, location.origin);
} catch (error) {
  parent.postMessage({ type: 'solidcraft-lab-error', error: error.message }, location.origin);
}
