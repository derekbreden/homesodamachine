import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

import { start } from "../../server.js";

const require = createRequire(import.meta.url);
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const assembly = "manifold-layout/enclosure-assembly.step";
const part = "printed-parts/cold-core/foam-cap/foam-cap-lid-top.step";
let browser;
let server;
let baseUrl;

before(async () => {
  const puppeteer = require(require.resolve("puppeteer", {
    paths: [path.join(root, "tools/render/node_modules")],
  }));
  browser = await puppeteer.launch({ headless: true });
  ({ server } = await start({ dev: false, port: 0 }));
  baseUrl = `http://127.0.0.1:${server.address().port}`;
});

after(async () => {
  await browser?.close().catch(() => {});
  if (server) {
    server.closeAllConnections?.();
    await new Promise((resolve) => server.close(resolve));
  }
});

async function openAssembly(page) {
  await page.goto(`${baseUrl}/3d#step:${encodeURIComponent(assembly)}`, {
    waitUntil: "domcontentloaded",
  });
  await page.waitForFunction((file) =>
    window.__hsm?.mountedStepFile === file && window.__hsm.currentGroup,
  { timeout: 30_000 }, assembly);
  await page.waitForSelector(".tube-toggle");
}

async function waitForResult(page, expected = {}) {
  await page.waitForFunction(({ runId, scenario, omitHoldId, coilPlane }) => {
    const panel = document.querySelector(".tube-panel");
    const overlay = window.__hsm?.scene?.getObjectByName("tube-overlay");
    const data = overlay?.userData;
    return panel?.dataset.state === "ready" && data &&
      (!runId || data.runId === runId) &&
      (!scenario || data.scenario === scenario) &&
      (omitHoldId === undefined || (data.omitHoldId || "") === omitHoldId) &&
      (!coilPlane || data.coilPlane === coilPlane);
  }, { timeout: 60_000 }, expected);
}

async function groupState(page) {
  return page.evaluate(() => {
    const h = window.__hsm;
    const group = h.currentGroup;
    let sum = 0;
    let count = 0;
    const meshes = [];
    group.traverse((obj) => {
      if (!obj.isMesh || obj.userData.side !== "front") return;
      const positions = obj.geometry.attributes.position.array;
      for (let i = 0; i < positions.length; i++) {
        sum += positions[i] * (1 + i % 13);
      }
      count += positions.length;
      meshes.push([obj.uuid, obj.geometry.uuid, obj.name, obj.matrix.toArray()]);
    });
    return { uuid: group.uuid, sum, count, meshes };
  });
}

test("/3d tube overlay is optional and leaves canonical assembly geometry intact", { timeout: 90_000 }, async () => {
  const page = await browser.newPage();
  const errors = [];
  page.on("pageerror", (err) => errors.push(err.message));
  try {
    await openAssembly(page);
    assert.equal(await page.$eval(".tube-toggle", (el) => el.getAttribute("aria-pressed")), "false");
    assert.equal(await page.evaluate(() => !!window.__hsm.scene.getObjectByName("tube-overlay")), false);
    const original = await groupState(page);

    await page.click(".tube-toggle");
    await waitForResult(page, { runId: "fluid-18", scenario: "straight" });
    const state = await page.evaluate(() => {
      const h = window.__hsm;
      const overlay = h.scene.getObjectByName("tube-overlay");
      return {
        outside: !h.currentGroup.getObjectById(overlay.id),
        children: overlay.children.length,
        results: Object.keys(overlay.userData.results),
        diagnostic: document.querySelector(".tube-diagnostics")?.textContent,
        holds: [...document.querySelectorAll(".tube-hold-focus[data-hold-id]")]
          .map((el) => el.dataset.holdId),
      };
    });
    assert.equal(state.outside, true, "tube overlay entered canonical CAD group");
    assert.ok(state.children > 0, "no tube scenario was drawn");
    assert.ok(state.results.includes("straight"));
    assert.ok(state.diagnostic?.trim(), "scenario has no diagnostic reading");
    assert.ok(state.holds.length > 0, "fluid-18 has no physical restraint markers");
    const geometry = await page.evaluate(async (file) => {
      const data = await fetch(`/api/tube-routes/${file}`).then((response) => response.json());
      const route = data.runs.find((run) => run.id === "fluid-18");
      const overlay = window.__hsm.scene.getObjectByName("tube-overlay");
      const result = overlay.userData.results.straight;
      const distance = (a, b) => Math.hypot(...a.map((value, i) => value - b[i]));
      const endpointError = Math.max(distance(result.points[0], route.points[0]),
        distance(result.points.at(-1), route.points.at(-1)));
      const holdErrors = route.holds.map((physical) => {
        const hold = result.holds.find((resolved) => resolved.id === physical.id);
        return hold?.index == null ? Infinity : distance(result.points[hold.index], physical.point);
      });
      const markerErrors = route.holds.map((physical) => {
        const marker = overlay.getObjectByName(`tube-hold-${physical.id}`);
        return marker ? distance(marker.position.toArray(), physical.point) : Infinity;
      });
      const tangentCosine = (a, b, target) => {
        const direction = b.map((v, i) => v - a[i]);
        return direction.reduce((sum, v, i) => sum + v * target[i], 0) /
          Math.hypot(...direction) / Math.hypot(...target);
      };
      return {
        finite: result.points.every((point) => point.every(Number.isFinite)),
        endpointError, holdError: Math.max(0, ...holdErrors), markerError: Math.max(0, ...markerErrors),
        startTangentCosine: tangentCosine(result.points[0], result.points[1], route.ends[0].tangent),
        endTangentCosine: tangentCosine(result.points.at(-2), result.points.at(-1), route.ends[1].tangent.map((v) => -v)),
        expectedRuns: data.runs.filter((run) => /^lldpe(?:-|$)/i.test(run.material)).map((run) => run.id).sort(),
        displayedRuns: [...document.querySelector(".tube-run").options].map((option) => option.value).sort(),
        lengthError: result.diagnostics.lengthErrorMm,
        status: result.diagnostics.status,
        screened: result.contactScreen?.method,
      };
    }, assembly);
    assert.equal(geometry.finite, true);
    assert.ok(geometry.endpointError < 1e-6, "fitting mouths moved");
    assert.ok(Number.isFinite(geometry.holdError) && geometry.holdError < 1e-6, "retained physical holds moved or vanished");
    assert.ok(Number.isFinite(geometry.markerError) && geometry.markerError < 1e-6, "physical hold markers moved from the exported seats");
    assert.ok(geometry.startTangentCosine > 1 - 1e-8, "start fitting tangent was not retained");
    assert.ok(geometry.endTangentCosine > 1 - 1e-8, "end fitting inward tangent was not reversed");
    assert.deepEqual(geometry.displayedRuns, geometry.expectedRuns, "run menu does not match the LLDPE inventory");
    assert.notEqual(geometry.status, "infeasible", "default fluid-18 scenario is length-infeasible");
    assert.ok(Math.abs(geometry.lengthError) < 0.01, "tube lost its assembled developed length");
    assert.equal(geometry.screened, "capsule-surface");
    assert.deepEqual(await groupState(page), original);

    await page.click(".tube-toggle");
    await page.waitForFunction(() => !window.__hsm.scene.getObjectByName("tube-overlay")?.visible);
    assert.equal(await page.$eval(".tube-toggle", (el) => el.getAttribute("aria-pressed")), "false");
    assert.deepEqual(await groupState(page), original);
    assert.deepEqual(errors, []);
  } finally {
    await page.close().catch(() => {});
  }
});

test("/3d tube scenarios and restraint release follow the latest control values", { timeout: 120_000 }, async () => {
  const page = await browser.newPage();
  try {
    await openAssembly(page);
    await page.click(".tube-toggle");
    await waitForResult(page, { runId: "fluid-18", scenario: "straight" });
    const hold = await page.$eval(".tube-omit", (el) => [...el.options].find((opt) => opt.value)?.value);
    assert.ok(hold, "fluid-18 offers no physical restraint to release");

    await page.select(".tube-scenario", "coil-positive");
    await page.select(".tube-scenario", "coil-negative");
    await page.select(".tube-coil-plane", "xz");
    await page.select(".tube-coil-plane", "yz");
    await page.select(".tube-omit", hold);
    await waitForResult(page, { runId: "fluid-18", scenario: "coil-negative", omitHoldId: hold, coilPlane: "yz" });
    await page.click(".tube-reset");
    await waitForResult(page, { runId: "fluid-18", scenario: "straight", omitHoldId: "", coilPlane: "xy" });
    const otherRun = await page.$eval(".tube-run", (el) => {
      const ids = [...el.options].map((option) => option.value);
      return ids.includes("fluid-14") ? "fluid-14" : ids.find((id) => id !== "fluid-18");
    });
    assert.ok(otherRun, "assembly offers only one LLDPE route");
    await page.select(".tube-run", otherRun);
    await waitForResult(page, { runId: otherRun, scenario: "straight", omitHoldId: "" });

    await page.evaluate((file) => { location.hash = `step:${encodeURIComponent(file)}`; }, part);
    await page.waitForFunction((file) => window.__hsm.mountedStepFile === file,
      { timeout: 30_000 }, part);
    await page.waitForFunction(() => !window.__hsm.scene.getObjectByName("tube-overlay")?.visible);
    const visiblePanel = await page.$eval(".tube-panel", (el) =>
      !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length)).catch(() => false);
    assert.equal(visiblePanel, false, "assembly tube controls remain visible on a standalone lid");
  } finally {
    await page.close().catch(() => {});
  }
});

test("/3d tube controls remain reachable on a narrow viewport", { timeout: 90_000 }, async () => {
  const page = await browser.newPage();
  try {
    await page.setViewport({ width: 390, height: 844, deviceScaleFactor: 1 });
    await openAssembly(page);
    await page.click(".tube-toggle");
    await waitForResult(page, { runId: "fluid-18", scenario: "straight" });
    const boxes = await page.evaluate(() => [".tube-run", ".tube-scenario", ".tube-omit", ".tube-reset"]
      .map((selector) => {
        const el = document.querySelector(selector);
        const b = el.getBoundingClientRect();
        return { selector, left: b.left, right: b.right, width: b.width, height: b.height };
      }));
    for (const box of boxes) {
      assert.ok(box.width > 0 && box.height > 0, `${box.selector} has no layout`);
      assert.ok(box.left >= 0 && box.right <= 390, `${box.selector} extends beyond viewport`);
    }
    await page.select(".tube-scenario", "coil-positive");
    await waitForResult(page, { scenario: "coil-positive" });
    await page.click(".tube-focus-run");
    await page.waitForFunction(() => {
      const h = window.__hsm;
      const overlay = h.scene.getObjectByName("tube-overlay");
      const data = overlay?.userData;
      const points = data?.results?.[data.scenario]?.points;
      h.camera.updateMatrixWorld();
      return document.querySelector(".tube-panel")?.classList.contains("collapsed") &&
        points?.every((point) => {
          const p = new h.THREE.Vector3(...point).project(h.camera);
          return Math.abs(p.x) < 0.99 && Math.abs(p.y) < 0.99 && Math.abs(p.z) < 1;
        });
    }, { timeout: 5_000 });
  } finally {
    await page.close().catch(() => {});
  }
});

test("/3d unchanged carb-2 tube does not acquire new contacts from resampling", { timeout: 90_000 }, async () => {
  const page = await browser.newPage();
  try {
    await openAssembly(page);
    await page.click(".tube-toggle");
    await waitForResult(page, { runId: "fluid-18", scenario: "straight" });
    await page.select(".tube-run", "carb-2");
    await waitForResult(page, { runId: "carb-2", scenario: "straight" });
    const result = await page.evaluate(() => {
      const data = window.__hsm.scene.getObjectByName("tube-overlay").userData;
      const result = data.results.straight;
      return {
        shift: result.diagnostics.maxDisplacementMm,
        converged: result.diagnostics.converged,
        contacts: result.contactScreen.totalContacts,
        text: document.querySelector(".tube-contact-status").textContent,
      };
    });
    assert.equal(result.converged, true);
    assert.ok(result.shift < 1e-4, "the straight, taut carb-2 tube changed shape");
    assert.ok(result.contacts > 0, "carb-2 no longer exercises nominal surface contact");
    assert.doesNotMatch(result.text, /possible new surface contact|new location/,
      "different segment spacing invented a new collision on an unchanged tube");
    assert.match(result.text, /CAD route's sampled contact segments/);
  } finally {
    await page.close().catch(() => {});
  }
});

test("/3d refuses unavailable and stale tube route data without drawing a scenario", { timeout: 90_000 }, async () => {
  for (const fixture of [
    { status: 404, body: "No tube route data" },
    { status: 200, body: JSON.stringify({
      version: 1, status: "stale", staleReasons: ["Assembly payload changed"], runs: [],
    }) },
    { status: 200, body: JSON.stringify({
      version: 1, status: "current", source: { payload_sha256: "0".repeat(64) }, runs: [],
    }) },
  ]) {
    const page = await browser.newPage();
    try {
      await page.setRequestInterception(true);
      page.on("request", (request) => {
        if (request.url().includes("/api/tube-routes/")) {
          request.respond({ ...fixture, contentType: "application/json" });
        } else request.continue();
      });
      await openAssembly(page);
      await page.click(".tube-toggle");
      await page.waitForFunction(() => document.querySelector(".tube-panel")?.dataset.state === "error",
        { timeout: 10_000 });
      assert.equal(await page.evaluate(() => !!window.__hsm.scene.getObjectByName("tube-overlay")?.visible), false);
      const status = await page.$eval(".tube-status", (el) => el.textContent);
      assert.ok(status.trim(), "unavailable overlay has no explanation");
      if (fixture.status === 200) assert.match(status, /stale|changed|match|current|different|payload/i);
    } finally {
      await page.close().catch(() => {});
    }
  }
});
