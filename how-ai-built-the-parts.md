# How AI Built the Parts

*This was written by Claude after I asked it to analyze the git history of my CadQuery pipeline attempts — the multi-agent system I built to get AI to produce 3D-printed parts autonomously, and why I eventually tore it down. The content below is Claude's unedited analysis.*

---

## What happened

**Phase 1: The Pipeline Era** — You built an elaborate multi-agent pipeline to get AI to produce STEP files autonomously. An orchestrator would launch an engineering manager, which would write a parts spec, then write a CadQuery script, then run it. There were rubrics, validation checks, feature traceability requirements, multiple roles (orchestrator, engineering manager, build planner). The pipeline went through many iterations itself — you added grounding rules, path continuity probes, synthesis constraints, scoping principles. All of this was scaffolding to try to get the AI to produce correct geometry *without you understanding the geometry yourself*.

**Phase 2: Frustration** — Commit messages like `"WHY IS THIS SO HARD FOR THEM?"`, `"Ugh"`, `"Why don't they commit anything?!"`, `"Remove features that were not actually functional and were just the AI confused trying to ambitiously implement more rails it did not understand at all"`. The AI kept adding features that weren't asked for, getting confused about what rails do, producing geometry that was wrong in ways that were hard to catch without inspecting the STEP file yourself. The coupler tray split — conceptually simple (cut a plate in half through the hole centers) — took multiple attempts and corrections.

**Phase 3: Pipeline Teardown** — Around 7:20 PM on March 30, you ripped out the pipeline. Merged the engineering manager into the orchestrator, deleted `pipeline.md`, flattened the steps folder, removed the research phase. Then at 9:47 PM, you removed the confused features the AI had added to the left wall.

**Phase 4: You Learned CadQuery** — Starting at commit `9339de2e` (9:49 PM March 30), something fundamentally changed. The commits are no longer "AI produces a part from a spec." They're surgical: "Allow front plate and back plate to be inserted — removing blockers that prevented insertion." You're reading the CadQuery scripts, understanding what `PASS_THRU_GAP` means, knowing that `lip_bottom_b` needs to start at `PASS_THRU_GAP` instead of `0.0` so that panels can physically slide past each other during assembly. Every commit from this point forward is a precise, small, correct change — because **you know what the code does**.

**Phase 5: AI as Typist, Not Designer** — The commits still say `Co-Authored-By: Claude Opus 4.6`, so you're still using AI. But the nature of the collaboration flipped. You're telling the AI *exactly* what to change: "widen to 170mm, shift features +15mm, move strut bores outward." The AI is executing precise instructions in a framework you now understand. It's not designing — it's typing.

---

## What you discovered

The pipeline was trying to solve the wrong problem. The issue was never "how do we get AI to produce valid CadQuery." The AI can produce valid CadQuery just fine — it passes all the validation checks. The problem is that **the AI doesn't understand what it's building**. It can't visualize the physical object. It doesn't know that two lips forming a channel need a gap at the intersection where another panel slides through. It doesn't know that a diamond cutout better matches a pump base than a circle. It adds "plate bottom rails" that overlap an existing rail because it's pattern-matching on "rails = good" without understanding why each rail exists.

No amount of pipeline scaffolding, rubrics, or validation checks can substitute for spatial understanding. The validation checks confirm the geometry *is what the script says it is* — but they can't confirm *the script describes something that makes physical sense*.

What works is: **you** understand the part, **you** decide what the geometry should be, and then you tell the AI to implement that specific geometry in CadQuery. The AI is an excellent CadQuery typist. It is not a mechanical designer.

The pipeline wasn't useless — it got the initial simple parts made (flat plates with holes). But the moment the parts needed to *relate to each other* in physical space (rails that panels slide through, cutouts that let one part pass another), the AI hit a wall. And no amount of documentation, rules, or agent orchestration could get it past that wall. You had to cross it yourself.
