# Print results and physical fit

When Derek shares a print result, save his photos and observations with the print
they document. Give him the record's file path or its archived Git link.

When Derek tries a made part in hand and says anything affirmative about it, add
a row to [`fitted.json`](fitted.json) with the material number, date, his exact
words, what he tried and where the fuller record is. “Good enough” qualifies.
Include any flaw he names. A comment on a model or photo alone does not qualify.
If a later in-hand trial of that part fails, remove its rows. Git keeps the history.

The site uses this record alone to mark each printed part as fitted or not fitted yet.
The list behind the machine's mark names its printed parts still awaiting a fit.
The [website contract](../../web/contracts/README.md) describes where those marks appear.

Archive completed and retired trials in Git with their physical evidence, then remove
their working-tree copies. When current instructions rely on a past observation,
link to the archived file at its Git SHA.

## Evidence for a fit claim

- **Did the print fit in hand?** When Derek says it fits well enough, record what
  he tried and his exact words in [the fitted record](fitted.json).
- **What clearance does the model show?** Measure the named parts or features in
  the current export with [`hsm gap`](../../tools/hsm/README.md#geometry) when asked.
- **Why was a dimension chosen?** Record the reason and its evidence in the commit
  that sets it. Follow the setting’s line back with [`git why`](../../tools/hsm/git-tools/README.md#following-a-line-past-a-rewrite).
