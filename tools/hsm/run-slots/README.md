# Heavy runs

`hsm-run-slots` and `hardware/scripts/_run_slots.py` share four host-wide flock
slots. New logical runs use the live count in `/tmp/hsm-<uid>/heavy/count`
(default 4, range 1–4). A concurrent start waits until the newest start among
still-active runs is 30 seconds old. A completed run adds no delay; a start
with no active run is immediate. Timing reserves all four slots. New roots wait
at macOS pressure level 4 or used swap above 10 GiB. Admitted descendants keep
running and share their parent's lease.

```sh
python3 tools/run.py --count 4
python3 tools/run.py --count 1
python3 tools/run.py --timing -- <command>
python3 tools/run.py --cad -- python3 hardware/path/to/native.py
python3 tools/run.py -- bazel build //:target
```

`tools/hsm/run-slots.defaults.json` supplies the host policy. Cargo uses two jobs;
Bazel uses one heavy action per inherited lease. Native CadQuery/OCP work also
takes the shared CAD lease. Lock order is heavy admission, CAD when needed,
compiler when needed, then local target and memory locks. Bazel reserves CAD
before compiler so its actions can inherit both. A child cannot acquire CAD
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
- `HSM_RUN_BROKER`: `{path}` for a parent broker used by persistent Bazel actions

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
`{ok:true,_lease:...}` with the rights. Only the stable broker path enters Bazel's
action environment. `hsm` ping/status and endpoint advertise `run_slots:1`.

Engine workers wait for admission before taking Cargo or renderer locks, leaving
query dispatch available to an admitted parent's RPC. Leases belong to each
request and its children, not the resident renderer or daemon. Detached service
startup strips lease environment and closes inherited lease descriptors.
