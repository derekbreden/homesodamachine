# Heavy runs

`hsm-run-slots` owns the four host-wide flock slots. `tools/run` executes the native
`hsm-run` command wrapper. Native commands and optional oracle commands inherit
the same verified descriptors. New logical runs use the live count in `/tmp/hsm-<uid>/heavy/count`
(default 4, range 1–4). A concurrent start waits until the newest start among
still-active runs is 30 seconds old. A completed run adds no delay; a start
with no active run is immediate. Timing reserves all four slots. New roots wait
at macOS pressure level 4 or used swap above 10 GiB. Admitted descendants keep
running and share their parent's lease.

```sh
tools/run --count 4
tools/run --count 1
tools/run --timing -- <command>
tools/run --cad -- <native-import-command>
tools/run -- hsm-print-build enclosure-back-top
```

`tools/hsm/run-slots.defaults.json` supplies the host policy. Cargo uses two jobs.
Native CadQuery/OCP work also takes the shared CAD lease. Lock order is heavy
admission, CAD when needed, compiler when needed, then local target and memory
locks. A child cannot acquire CAD
while holding compiler alone. Rust part runs retain the engine's memory budget.
Kept part answers and the six ordinary mesh queries book no new heavy slot.

Descriptors carry ownership. `slot.N.lock`, `cad.lock` and `compiler.lock` hold
JSON with `v:1`, `kind`, `token` and diagnostic `pid`. Slot records also name
`slot`, `key` and `started_unix_ms`. `admission.lock` protects scans and
`admission.json` (`v:1,last_start_unix_ms`) records the last root start for diagnostics. Busy slot
records with one token count as one logical root. Decreasing the live count
waits for existing roots to drain without terminating them.

The inherited environment is:

- `HSM_RUN_LEASE`: `{v:1,fds:[{fd,slot,token},...]}`
- `HSM_CAD_LEASE` and `HSM_COMPILER_LEASE`: `{v:1,fd,token}`
- `HSM_RUN_BROKER`: `{path}` for a parent broker used by launchers that close inherited descriptors

Each descriptor must name the expected lock inode, contend with an independently
opened FD, successfully lock through its existing open-file description, and
match the record token and kind. Environment text and `HSM_NO_BUILD_LOCK=1`
alone grant no admission. Release closes descriptors; it never explicitly
unlocks an open-file description a surviving child may still hold.
If a launcher closes inherited numeric FDs, the helper tries the live broker and
validates its returned rights. A failed local lease without a valid broker is an
error. Service startup closes only individually validated original lease FDs;
an unrelated file occupying a stale FD number stays open.

Engine JSON requests and broker replies carry optional `_lease` metadata:

```text
{v:1,slots:[{slot,token},...],cad:{token}|null,compiler:{token}|null,profile:string|null}
```

One SCM_RIGHTS message carries descriptors in exactly that order: slots, then
CAD, then compiler, at most six. `profile` is diagnostic. The receiver validates
the complete count and every FD. Broker clients read the private adjacent `.json`
owner token and request `{v:1,token}`; successful replies contain
`{ok:true,_lease:...}` with the rights. Each command owns its broker for the
lifetime of its inherited work. `hsm` ping/status and endpoint advertise `run_slots:1`.

Engine workers wait for admission before taking Cargo or renderer locks, leaving
query dispatch available to an admitted parent's RPC. Leases belong to each
request and its children, not the resident renderer or daemon. Detached service
startup strips lease environment and closes inherited lease descriptors.

The installer keeps the runner and source receipt in versioned
`~/.local/lib/hsm/runtime/` directories. `runtime.json` names the current runner.
`tools/run` uses the checkout runner or the installed launcher. A runner whose
embedded host-policy sources differ from the checkout rebuilds the runner and
installs its immutable artifact under shared admission and the compiler lease,
then continues with the requested command. Existing jobs keep their original
executable and verified leases.

`hsm-run --install-tools WORKSPACE BINARY...` installs built command artifacts under
`~/.local/lib/hsm/tools/` and exposes their names in `~/.local/bin`. Each launcher
names an immutable executable, so installation leaves running jobs on their
original artifacts. `--prefix DIRECTORY` selects another installation directory.

The shared `hsm-run-slots` crate supplies the Rust lease library and native command
runner. Ordinary producer builds retain Cargo's hashed Rust-library outputs.
