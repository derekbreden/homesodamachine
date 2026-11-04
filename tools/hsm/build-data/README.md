# Build data

`build-data` serves mesh payload, projection, source dependency, artifact identity,
cache, inventory and print-surface planning operations. Its publication module
owns catalogue selection, provenance, archives and local publication state; see
[PUBLICATION.md](PUBLICATION.md).

`bookkeeping-data` serves build selection, failure reports, source/output carry,
derived-file removal and artifact pointer operations. The Python entrypoints in
`tools/bazel/` and `tools/cad-artifacts/` preserve their command and object APIs.

The services accept one JSON request per line with `--serve`. Source parsing and
tokenization use explicit standard-library callbacks; Rust owns traversal,
selection and transformation. Callbacks can issue nested requests on the same
service without losing native object identity.

Compiled dependencies come from Cargo dep-info. Compatibility entrypoints also
register the raw inputs and outputs handled by the services. The generated BUILD
declares this closure for its source-stripping and graph-support actions.

Fixed-input comparisons and combined-build results are in the
[conversion records](../conversion-results/).
