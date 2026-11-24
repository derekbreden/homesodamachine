# Home Soda Machine

The [README](README.md) maps the machine, the product plans and the market.
Read the `AGENTS.md` files along the directory path to your work. Follow the
guide for the task wherever it comes up, including in chat.

- [Parts, sourcing, drawings and print trials](hardware/AGENTS.md)
- [Builds, scratch files and chat visuals](tools/AGENTS.md)
- [Writing or editing code and documentation](calibration/editing.md)

Keep instructions at the narrowest scope that needs them. Link to the procedure
or evidence that holds the details.

## What Counts

What Derek sees on the website and what he prints are the measure of the work.
The machine is the same when the site shows the same things and the same solids
print within the kernel's rule. Keep fabrication order files generatable on demand.
An output, check, report or costly site detail that serves none of these can go.

## Speed

Minimize the time from Derek's request to the first relevant source-authored change
visible on the site. Publish completed parts while other parts and focused review
continue. Tell Derek what he can see, what geometry is checked and what is ready to print.

## What Runs Every Time

Add work to every edit, commit or build only when Derek asks for that specific thing.
Run a check when someone asks the question it answers. In your own loop, check
what the change touched once. The cost of a recurring check is enough reason to remove it.

## Shared checkout

Use `/Users/derekbredensteiner/Developer/homesodamachine` on `main` for all work
on this Mac. Keep it current with `origin/main`. Coordinate overlapping edits with
the other session and integrate both changes. Stage new files, commit only your
session's paths with `git commit -- <paths>`, and push directly to `main` without
asking for confirmation. Follow the [commit message and setting provenance rules](tools/hsm/git-tools/README.md#commit-messages).
Use [`tools/run`](tools/hsm/run-slots/README.md) for Cargo, slicing and rendering.

## Working with Derek

Look in the repo before asking Derek for information. Use only this Mac when
you need his Chrome.
