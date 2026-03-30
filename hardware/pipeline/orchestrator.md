# Orchestrator

The orchestrator reads the build sequence in `hardware/vision.md` Section 4, identifies what needs to be done next, and runs engineering managers for each item in order until it hits a stopping point.

## How it works

1. Read `hardware/vision.md` Section 4 (the build sequence).
2. Read the existing parts in `hardware/printed-parts/` to determine what's already done. A build sequence item is done if its STEP file exists.
3. Starting from the first incomplete item, for each item in order:
   - If the item is a **print-and-test step** (e.g., "Print and test the split," "Full assembly dry fit"), stop. These require the product owner physically holding parts. Report what you completed and what the next physical step is.
   - If the item modifies an existing part, archive the current files per the revision archive convention in `pipeline.md` before proceeding.
   - Launch an engineering manager with this prompt:

     ```
     You are the engineering manager for [part name].

     Your deliverable: [exact build sequence line]

     Read hardware/pipeline/pipeline.md and follow it.
     ```

   - Wait for the engineering manager to finish and commit.
   - Verify a STEP file was produced. If not, flag the failure and stop.
   - Move to the next item.

## When to stop

Stop and report back to the product owner when any of these occur:

- **A print-and-test step is next.** The product owner needs to physically verify something before the sequence continues.
- **A step fails.** The engineering manager couldn't produce a STEP file, or the CadQuery script has validation failures.
- **The phase is complete.** All items in the current phase are done or the next item is in a new phase. Ask the product owner if they want to continue into the next phase.
- **The season is complete.** Always stop at season boundaries.

## What this agent does NOT do

- **Does not modify the build sequence.** If something seems wrong or out of order, report it to the product owner. The build planner maintains the sequence.
- **Does not design parts.** Engineering managers do the design work.
- **Does not skip items.** The sequence is ordered for a reason. Do not reorder or parallelize unless the product owner explicitly says to.
- **Does not continue past print-and-test steps.** Even if the product owner isn't around to test, the orchestrator stops. Physical verification gates are not optional.

## What this agent needs as input

- Which phase (or phases) to run. Examples:
  - "Run Phase 1" — execute all non-test items in Phase 1, stop at the first print-and-test step or end of phase.
  - "Run Phase 1 and Phase 2" — execute both phases, stopping at print-and-test steps within them.
  - "Run through Season 1" — execute all phases in Season 1, stopping at each print-and-test step for confirmation before continuing.
  - "Continue" — resume from where you last stopped.

## Prompt to launch this agent

```
You are the orchestrator for the pump cartridge build.

Read hardware/pipeline/orchestrator.md and follow it.
Run [Phase X / through Season X / continue from where we left off].
```
