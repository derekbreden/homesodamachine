// Physical conductors are separate selectable pieces, even on the shared COM net.
export function conductorRecords(data) {
  if (data.conductors) return data.conductors;
  const targets = { COM: 'Wago +12 V · feed', FAN: 'Condenser fan −', OUT3: 'V-K −', OUT2: 'V-J −', OUT1: 'V-I −' };
  const rows = data.pins.filter(pin => pin.cutMm).map(pin => ({
    id: pin.net, pin: pin.pin, net: pin.net, title: `${pin.net} → ${targets[pin.net]}`,
    from: `PCB J2 · ${pin.net}`, to: targets[pin.net], ribbon: `${pin.ribbon}${pin.conductor}`,
    stripe: pin.stripe, cutMm: pin.cutMm, left: 'jst', right: pin.net === 'COM' ? 'ferrule' : 'disconnect',
    sharedDress: pin.net !== 'OUT3',
    fromPart: `${data.contact} contact · ${data.housing} cavity ${pin.pin}`,
    toPart: pin.termination,
    note: pin.net === 'FAN' ? 'Fan connection and final trim await the donor lead.' : pin.net === 'COM' ? 'This is the single +12 V feed. Four separate wires leave the Wago.' : 'This return goes directly to its PCB label; it bypasses the positive Wago.',
  }));
  for (const [index, target] of ['V-I +', 'V-J +', 'Fan +', 'V-K +'].entries()) rows.push({
    id: ['VI+', 'VJ+', 'FAN+', 'VK+'][index], net: 'COM', title: `Wago → ${target}`,
    from: `Wago +12 V · branch ${index + 1}`, to: target, port: index + 1,
    stripe: false, cutMm: data.positiveBranches.stockCutMm, left: 'ferrule', right: 'disconnect',
    sharedDress: false, fromPart: 'Bootlace ferrule · one conductor in this Wago port',
    toPart: index === 2 ? 'Fan connection provisional' : 'Female disconnect · match the valve tab',
    note: 'Separate bulk-wire positive branch. Cut from the 450 mm blank and trim at its device.',
  });
  return rows;
}
