# Stamped setting authority checks

Run this host-only check when reviewing compare/apply, stamps, persistence, or
transport layout. It is separate from PlatformIO's native test filter and adds
no build or commit gate.

```sh
c++ -std=c++11 -Wall -Wextra -Werror \
  -Ifirmware/lib/proto_link -Ifirmware/src_appliance \
  firmware/src_appliance/settings_core.cpp \
  firmware/test/manual_stamped_settings/checks.cpp \
  -o /tmp/hsm-stamped-settings-checks
/tmp/hsm-stamped-settings-checks
```

The check exercises the production pure authority with deterministic fake epoch
and value stores: conditional writes, same-value writes, ABA, field/channel
isolation, unconditional display/console mutations, pair transactions, malformed
values, deferred persistence, power loss, restart, epoch/storage failure, and wire
encoding. All appliance mutation entry points use this authority through
`settingsWrite`, `settingsWritePair`, or `settingsAnswer`.
