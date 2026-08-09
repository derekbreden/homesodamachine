# Integrated ground-fault protection (GFCI)

*Pie-in-the-sky, not roadmap. Captured 2026-06-22.*

An in-appliance Class A GFCI, so the machine carries its own ground-fault protection on its AC side and that protection travels with the unit to whatever receptacle it plugs into. A plumbed Class I appliance — water, four bonded exposed-metal surfaces, a 120 VAC cord — is exactly the case this protection exists for.

## The desire

A self-test Class A GFCI: 6 mA personnel trip, with the automatic periodic self-test the 2015 UL 943 revision calls for, mounted on the AC side between the rear C14 inlet and the AC distribution block. The line cord stays a generic NEMA 5-15P → C13 and the protection lives in the appliance, so a swapped cord cannot defeat it. The off-the-shelf candidate scoped for the role is the Legrand Radiant 1597BKCCD12 (self-test every 3 seconds, SafeLock end-of-life lockout), already acquired and in stock. The standing posture — the obligation, the standard, the bond path through the C14 cord — is in [`/business/regulatory.md`](/business/regulatory.md) under "UL 943".

## Where the build stands

The current Kitchen build does not integrate the module: the C14 inlet lands onto the three mains splices in the +X wall's own Wago wells with no device in series (`enclosure._east_wells`). This doc holds the integrated GFCI as a live want for a later pass.
