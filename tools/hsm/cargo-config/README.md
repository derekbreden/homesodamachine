# Cargo configuration

`hsm-cargo-config` writes the compiler settings and external package versions
shared by native producer programs.

```sh
tools/run -- hsm-cargo-config
```

The producer reads the workspace manifest and lock file. It omits workspace
membership and packages without a source registry or repository, sorts JSON keys,
and retains an unchanged output's timestamp. Its own compiler declaration names
the manifest and lock file directly; the generated configuration is an input to
the other native programs.

An output directory stages `tools/hsm/cargo-config.json` beneath that directory.
`--root ROOT` selects its input checkout and `--output FILE` selects an explicit
destination instead.

`hsm-ci-image-digest` hashes the repository inputs used by the CI image. It is a
standalone command in this crate, using the digest source and crate manifest,
Docker configuration, and the render and web package manifests and
locks. `--inputs` lists these paths; `--root ROOT` selects their checkout.
