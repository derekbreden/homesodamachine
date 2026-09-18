import { test } from "node:test";
import assert from "node:assert/strict";
import { FAUCET_STYLES, FAUCET_FINISHES, faucetStyleFor, hasFaucetFinish, isFaucetFinishBody } from "../contracts/faucet-options.js";
import { sourceFileFor } from "../contracts/component-sources.js";

const [sculpted, industrial] = FAUCET_STYLES;
const files = [...new Set(FAUCET_STYLES.flatMap((s) => [s.assembly, ...Object.values(s.parts)]))];

test("faucet styles name distinct assemblies and share the printable neck tip", () => {
  assert.deepEqual(FAUCET_STYLES.map((s) => s.label), ["Sculpted", "Industrial"]);
  assert.notEqual(sculpted.assembly, industrial.assembly);
  assert.equal(sculpted.parts.shell_tip, industrial.parts.shell_tip);
  assert.equal(faucetStyleFor(industrial.assembly), industrial);
  assert.equal(faucetStyleFor("manifold-layout/enclosure-assembly.step"), null);
  assert.deepEqual(FAUCET_FINISHES.map((f) => f.label), ["Black", "White"]);
});

test("part drilldown uses the owning faucet style, including the seated cover", () => {
  for (const style of FAUCET_STYLES) {
    for (const [name, part] of Object.entries(style.parts)) {
      assert.equal(sourceFileFor(name, files, style.assembly), part);
      assert.equal(sourceFileFor(`faucet/${name}`, files, style.assembly), part);
    }
  }
  assert.equal(sourceFileFor("shell_base", [], industrial.assembly), null);
  assert.equal(sourceFileFor("display-cover", files, "manifold-layout/enclosure-assembly.step"), null);
});

test("finish includes only PET-GF faucet parts and never the machine's display cover", () => {
  for (const style of FAUCET_STYLES) {
    for (const name of ["shell_base", "shell_tip", "faucet-display-cover-seated", "above_counter_plate"]) {
      assert.ok(isFaucetFinishBody(style.assembly, name));
      assert.ok(hasFaucetFinish(style.parts[name]));
    }
    for (const name of ["westbrass", "lever", "above_counter_gasket", "faucet_display", "faucet_display_screen", "flavor_a", "display-cover"]) {
      assert.equal(isFaucetFinishBody(style.assembly, name), false, name);
    }
    assert.equal(hasFaucetFinish(style.parts.above_counter_gasket), false);
  }
  assert.equal(isFaucetFinishBody("manifold-layout/enclosure-assembly.step", "shell_base"), false);
});
