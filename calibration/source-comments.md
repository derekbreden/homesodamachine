# Source comments

Omit comments that narrate the next few lines. If a comment gives an operation a
better name, use that name in the code. When a type or calculation can enforce a
constraint, express it there. Keep each piece of machinery’s one-line purpose
where it is defined.

Before adding a tag, name the tool that reads it and what the tag enables. The
enclosure gives the status LED lead channel a feature name so the viewer can
highlight the cut. In G-code, `; FEATURE:` tells slice review which moves belong
to a wall. Preserve these annotations when editing the code that produces them.
[Enclosure feature](../hardware/printed-parts/enclosure/enclosure/quadrants/display.rs) · [Slice review](../tools/hsm/print-prep/src/review.rs)

## Clearance and fit

- **Did the print fit in hand?** When Derek says a print he tried fits well enough,
  record what he tried and his exact words. Follow the [physical fit instructions](../hardware/ledger/fitted.md)
  for the [fitted record](../hardware/ledger/fitted.json).
- **What clearance does the model show?** Measure the named parts or features
  in the current export with [`hsm gap`](../tools/hsm/README.md) when the question comes up.
- **Why was this dimension chosen?** Put the reason and its evidence in the
  commit that sets it. Read that commit from the setting’s line with
  [`git why`](../tools/hsm/git-tools/README.md#following-a-line-past-a-rewrite).
