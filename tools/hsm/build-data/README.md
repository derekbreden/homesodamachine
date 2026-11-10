# Build data

`hsm-build-data` supplies native payload, source, inventory, publication and
output-carry APIs to the build planner and publisher. Its publication module owns
catalogue selection, provenance, archives and local publication state; see
[PUBLICATION.md](PUBLICATION.md).

`hsm-build-plan` calls the native selection and carry APIs directly.
`hsm-publish` calls the native artifact and publication APIs directly.

`build-data` serves retained CAD compatibility callers as newline-delimited JSON
with `--serve`. Source parsing and tokenization use explicit callbacks. Those
callbacks can issue nested requests on the same service.

Compiler source declarations come from Cargo dep-info. Native producer tracing
combines that closure with the program's runtime-read receipt.
