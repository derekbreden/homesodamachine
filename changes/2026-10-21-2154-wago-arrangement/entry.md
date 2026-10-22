---
title: Nine Wagos, sized for their actual junctions
lede: Reservoir A uses one continuous common instead of a connector. The two west-side junctions use three-port blocks, and the power row follows its connections.
date: 2026-10-21T21:54:01-05:00
commit: 66afca468f088b1b049a6c00557e99e611ccbb09
model: manifold-layout/enclosure-assembly.step
---
The reservoir-A Wago and its wall well are removed. One continuous J6 common follows the four signal conductors to the reed column, with insulated local taps. That connection is 293 mm, replacing two wires totaling 485 mm.

The reservoir-B/carbonator common and the temperature/flow common each use three ports, so both use 221-413 blocks. The machine has seven 221-413, one 221-415 and one 221-420. The manifold commons stay with the removable front-top shell beside their valve branches.

The power row runs front to rear as +12 V, DC GND, PE, L and N in the existing five wells. Its 14 connections total 1718 mm instead of 1958 mm and contain 64 modeled bends instead of 82. Their approaches leave neighboring connector entries open. No mounting parts are added.

All 102 native wires are valid single solids. Full-scene mesh witnesses have zero native overlap outside the intended local electrical endpoints. These readings cover the proposed installed geometry; physical harness dressing and closing motions remain separate.

Derek: “please also do what you can to make simple choices to give us simple arrangements for the WAGO connectors.”
