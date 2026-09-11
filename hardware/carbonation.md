# Carbonation

How much CO2 is dissolved in the soda, and where it is read.

The number that matters is the one at the glass, a few seconds after the pour, because that is
when the drink is drunk. Everything upstream — CO2 setpoint, water temperature, contact time in
the vessel — is a means to it, and every joint between the carbonator and the tip is a place it
is lost. A reading taken at the carbonator is not that number.

## Units

Carbonation is in **volumes**: litres of CO2 at STP dissolved per litre of water. One volume is
1.96 g/L. Canned soda is 3.5–4.2 volumes.

## The equilibrium ceiling

A sealed vessel of water under pure CO2 approaches a ceiling set by temperature and absolute
pressure. Volumes per atmosphere absolute:

| Water temperature | Volumes per atm |
|---|---|
| 0 °C | 1.71 |
| 2 °C | 1.59 |
| 4 °C | 1.48 |
| 6 °C | 1.39 |
| 10 °C | 1.18 |
| 20 °C | 0.86 |

Gauge pressure in PSI becomes atmospheres absolute as `psi / 14.7 + 1`. At the
[carbonator wall setpoint](/hardware/assembly/acceptance-and-burn-in.md) of 2 °C, a 90 PSI
headspace has a ceiling of 11.4 volumes and a 70 PSI headspace 9.2 volumes.

The ceiling is not the contents. Approach depends on contact area and time: the sparge stone
bubbling through the column ([`pressure-vessel.md`](/hardware/assembly/pressure-vessel.md) step 4)
is a fast contactor and is connected to the regulator whenever the machine is on
([`fluid-topology-carbonator.mmd`](/hardware/topology/fluid-topology-carbonator.mmd) carries no
CO2 solenoid), so the vessel climbs toward its ceiling continuously between pours. A vessel that
carbonates through headspace contact alone climbs far more slowly and sits well below it.

## The instrument

Shake-to-equilibrium headspace pressure. A sample is sealed in a rigid vessel with a gauge,
shaken until the gauge stops rising, and read against the table above at the sample's own
measured temperature.

Rig: a pressure-rated PET bottle, a carbonation cap that seals its neck and carries a gauge
reading to at least 120 PSI, and a probe thermometer. All three are commodity homebrew parts.

1. Fill the bottle to a marked line. **The fill fraction is part of the calibration** — hold it
   identical across every sample being compared.
2. Cap immediately. Vent once to purge the air above the liquid, then re-seal.
3. Shake until the gauge is steady over ten seconds.
4. Read gauge pressure and liquid temperature together.
5. Volumes = `(psi / 14.7 + 1) × (volumes per atm at that temperature)`.

**This is a comparator, not an absolute.** CO2 leaving solution into the headspace during the
shake makes the reading low, by an amount set by the headspace fraction. Held constant, the
error is common to every sample and differences between samples are real. Changed, they are not.

## Where it is read

Two readings, and the interesting quantity is the difference:

- **At the vessel** — drawn straight off the dispense path with the faucet wide open into the
  sample bottle, filled fast and capped immediately. This is what the carbonator made.
- **At the glass** — poured as a customer pours, left the few seconds a customer leaves it, then
  decanted into the sample bottle. This is what the customer drinks.

The gap between them is what the delivery path costs: the run from the cold core's
`carb-water-out` conduit to the tip, the pressure break at the faucet, the fall into the glass,
and the ice. It is the only measurement that prices a change to that path.

Pour temperature is read at the same time as every glass-side sample. Solubility moves about 8 %
between 2 °C and 4 °C, which is inside the wall setpoint's own band, so a carbonation reading
without its temperature cannot be compared to another.
