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

The material viewer also shows **Fitted clearances** on either material in a documented
fit. The [clearance records](fitted-clearances.json) locate paired surfaces and preserve
coupon measurements with their archived evidence. The viewer reads production dimensions
from the part records and calculates the comparison from the
[shared allowances](../printed-parts/enclosure/clearance-audit.md).

Archive completed and retired trials in Git with their physical evidence, then remove
their working-tree copies. When current instructions rely on a past observation,
link to the archived file at its Git SHA.
