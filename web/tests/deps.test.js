// Native metadata fixtures hold exact producer selection and output refresh identities.
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { nativeBuildPlan, buildTargetsForSources, buildOrder, viewerOutput } from "../dev-server/deps.js";

function fixture(t, graph) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "hsm-native-deps-"));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  fs.mkdirSync(path.join(root, "tools/hsm/build-plan"), { recursive: true });
  for (const source of Object.keys(graph)) {
    fs.mkdirSync(path.dirname(path.join(root, source)), { recursive: true });
    fs.writeFileSync(path.join(root, source), "fn main() {}\n");
  }
  fs.writeFileSync(path.join(root, "tools/hsm/build-plan/graph.json"), JSON.stringify(graph));
  return root;
}
const row = (source, reads, writes, extra = {}) => ({ reads, writes, rewritten: [], program: { crate: "fixture", name: "fixture", sources: [source] }, ...extra });

test("exact native output paths select downstream consumers without basename collisions", t => {
  const root = fixture(t, {
    "hardware/left/build.rs": row("hardware/left/build.rs", [], ["hardware/left/part.step"]),
    "hardware/right/build.rs": row("hardware/right/build.rs", [], ["hardware/right/part.step"]),
    "hardware/assembly.rs": row("hardware/assembly.rs", ["hardware/left/part.step"], ["hardware/assembly.step.mesh"]),
  });
  const plan = nativeBuildPlan(root);
  assert.deepEqual(buildTargetsForSources(["hardware/left/build.rs"], root, plan), ["//:assembly", "//:left-build"]);
  assert.deepEqual(buildTargetsForSources(["//:right-build"], root, plan), ["//:right-build"]);
  assert.deepEqual(buildOrder(plan).map(producer => producer.target), ["left-build", "assembly", "right-build"]);
});

test("compiler sources and runtime data select their declared readers", t => {
  const source = "hardware/part.rs";
  const root = fixture(t, { [source]: row(source, ["hardware/size.json"], ["hardware/part.step"], {
    program: { crate: "fixture", name: "fixture", sources: [source, "tools/hsm/interface/src/lib.rs"] },
  }) });
  for (const request of ["hardware/size.json", "tools/hsm/interface/src/lib.rs", path.join(root, source)])
    assert.deepEqual(buildTargetsForSources([request], root), ["//:part"]);
  assert.throws(() => buildTargetsForSources(["unrelated.rs"], root), /No declared native producer/);
  assert.throws(() => buildTargetsForSources(["../../outside.rs"], root), /outside the checkout/);
});

test("co-writers share the same declared target", t => {
  const program = { crate: "fixture", name: "fixture", sources: ["hardware/a.rs", "hardware/b.rs"] };
  const root = fixture(t, {
    "hardware/a.rs": row("hardware/a.rs", [], ["hardware/shared.json"], { program }),
    "hardware/b.rs": row("hardware/b.rs", [], ["hardware/shared.json", "hardware/part.step"], { program }),
  });
  const plan = nativeBuildPlan(root);
  assert.equal(plan.producers.size, 1);
  assert.deepEqual(plan.producers.get("a").sources, ["hardware/a.rs", "hardware/b.rs"]);
  assert.deepEqual(buildTargetsForSources(["hardware/b.rs"], root, plan), ["//:a"]);
});

test("rewritten authored documents do not become generated upstream solids", t => {
  const root = fixture(t, {
    "hardware/notes.rs": row("hardware/notes.rs", ["hardware/notes.md"], ["hardware/notes.md"], { rewritten: ["hardware/notes.md"] }),
    "hardware/part.rs": row("hardware/part.rs", ["hardware/notes.md", "hardware/part.step.mesh"], ["hardware/part.step"]),
  });
  const plan = nativeBuildPlan(root);
  assert.equal(plan.byOutput.has("hardware/notes.md"), false);
  assert.equal(plan.producers.get("part").dependencies.size, 0);
  assert.deepEqual(buildTargetsForSources(["hardware/notes.md"], root, plan), ["//:notes", "//:part"]);
});

test("metadata is reread for a new producer and rejects an undeclared runtime", t => {
  const source = "hardware/part.rs";
  const root = fixture(t, { [source]: row(source, [], ["hardware/part.step"]) });
  assert.equal(nativeBuildPlan(root).producers.size, 1);
  const source2 = "hardware/new.rs";
  fs.writeFileSync(path.join(root, source2), "fn main() {}\n");
  fs.writeFileSync(path.join(root, "tools/hsm/build-plan/graph.json"), JSON.stringify({
    [source]: row(source, [], ["hardware/part.step"]), [source2]: row(source2, [], ["hardware/new.step"]),
  }));
  assert.equal(nativeBuildPlan(root).producers.size, 2);
  fs.writeFileSync(path.join(root, "tools/hsm/build-plan/graph.json"), JSON.stringify({ [source]: { reads: [], writes: ["part.step"] } }));
  assert.throws(() => nativeBuildPlan(root), /no declared native program/);
});

test("cycles are named instead of yielding a partial build order", t => {
  const root = fixture(t, {
    "hardware/a.rs": row("hardware/a.rs", ["hardware/b.step"], ["hardware/a.step"]),
    "hardware/b.rs": row("hardware/b.rs", ["hardware/a.step"], ["hardware/b.step"]),
  });
  assert.throws(() => buildOrder(nativeBuildPlan(root)), /Native producer cycle: a -> b -> a/);
});

test("source saves have no output notification while each native payload identifies its model", () => {
  const root = "/checkout/hardware";
  for (const file of ["part.rs", "part.py", "part.tsx", "size.json"]) assert.equal(viewerOutput(path.join(root, file), root), null);
  assert.equal(viewerOutput(path.join(root, "part.step.mesh"), root), "part.step");
  assert.equal(viewerOutput(path.join(root, "assembly/scenes/glb/install.glb.mesh"), root), "assembly/scenes/glb/install.glb");
  assert.equal(viewerOutput(path.join(root, "pcb/pcba/out/pcba.glb.mesh"), root), null);
  assert.equal(viewerOutput(path.join(root, "machine.scene.npz"), root), "machine.step");
  assert.equal(viewerOutput(path.join(root, "pcb/pcba/out/pcba.glb"), root), "pcb/pcba/out/pcba.glb");
  assert.equal(viewerOutput(path.join(root, "manual/manual.pdf.json"), root), "manual/manual.pdf");
  assert.equal(viewerOutput("/outside/part.step", root), null);
});
