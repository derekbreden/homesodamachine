const A = require('./20-balanced-arm.js');
function show(l, o) { const r = A.analyse(o); console.log(l.padEnd(44), 'net', r.cur.net.toFixed(2), 'N*m', '|', r.state, '| eq angle', r.thEq.toFixed(1), '| window', r.win.map(w=>w[0].toFixed(0)+'..'+w[1].toFixed(0)).join(' ') || 'none', '| micro', r.micro.mm.toFixed(1), 'mm | tip err x,z', r.tipErr.x.toFixed(1), r.tipErr.z.toFixed(1), '| motor bal/unbal', r.motorBalanced.toFixed(2), r.motorUnbalanced.toFixed(2)); }
show('default 1.5 kg on a 2.0 kg spring', {});
show('matched: 1.5 kg on 1.5 kg spring', { md: 1.5 });
show('ballast 0.5 kg (payload 2.0)', { ballast: 0.5 });
show('matched, umbilical change 2 N', { md: 1.5, dF: 2 });
show('matched, 2 N, cable clipped on arm', { md: 1.5, dF: 2, cableOnArm: true });
show('matched, 2 N, brake', { md: 1.5, dF: 2, brake: true });
show('matched, eps 0.4', { md: 1.5, eps: 0.4, th: 35 });
show('matched, friction 0.1', { md: 1.5, taf: 0.1, th: 35 });
