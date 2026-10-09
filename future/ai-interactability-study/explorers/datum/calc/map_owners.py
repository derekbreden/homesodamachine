"""Who owns the wobble: rig, seat, work, judge bias. Numbers for exchange/datum--on--trials-w2.md (trials-04) and scene datum-14.

Radial seam offset at the station, per table angle theta (mm). All amplitudes ILLUSTRATIVE except the scale of the accepted
runout (0.25 mm TIR radial [repo weld-rotation-rig.md]).
  R  rig-owned   : rotator's own error motion at the station, keyed to the rotator angle (harmonics 1, 2)
  S  seat-owned  : tube axis vs turntable axis: 1st harmonic only; redrawn whenever the tube is re-seated
  W  work-owned  : tube-locked seam shape: harmonics 1..3 (plate offset in bore, ovality, tack pull); rotates with the tube
  B  judge bias  : tube-locked error of the camera judge (glare, tint, tack marks): harmonics 1 and 3; rotates with the tube
Judge reading  J = R+S+W+B + noise ; truth T = R+S+W ; touch (unlike sensor) = T + touch noise at K azimuths.
"""
import numpy as np
rng = np.random.default_rng(7)
NB = 60                                   # angle bins (6 deg) for the learned map
th = np.arange(NB) * 2 * np.pi / NB

def harm(amps, phases, a):                # sum of amp_k cos(k a - phase_k), k = 1..len
    return sum(A * np.cos((k + 1) * a - p) for k, (A, p) in enumerate(zip(amps, phases)))

def draw(amps):                           # random phases
    return dict(amps=amps, ph=rng.uniform(0, 2 * np.pi, len(amps)))

def comp(c, a, rot=0.0):                  # tube-locked pieces rotate by psi
    return harm(c['amps'], c['ph'], a - rot)

def rms(x): x = x - x.mean(); return float(np.sqrt(np.mean(x ** 2)))

def state():
    return dict(R=draw([0.06, 0.03]), S=draw([0.20]), W=draw([0.06, 0.05, 0.02]), B=draw([0.03, 0.0, 0.02]), psi=0.0)

def T(s, a): return comp(s['R'], a) + comp(s['S'], a) + comp(s['W'], a, s['psi'])
def B(s, a): return comp(s['B'], a, s['psi'])

def learn_judge(s, N, noise):             # mean of N revolutions per bin, DC removed
    m = np.mean([T(s, th) + B(s, th) + rng.normal(0, noise, NB) for _ in range(N)], axis=0)
    return m - m.mean()

def fit_low(a, y, H=3):                   # least-squares harmonics 1..H (+DC) on scattered angles
    A = np.column_stack([np.ones_like(a)] + [f(k * a) for k in range(1, H + 1) for f in (np.cos, np.sin)])
    c, *_ = np.linalg.lstsq(A, y, rcond=None)
    return lambda x: np.column_stack([np.ones_like(x)] + [f(k * x) for k in range(1, H + 1) for f in (np.cos, np.sin)]) @ c

def touch_azimuths(K): return np.arange(K) * 2 * np.pi / K + 0.3

def trial(event, N=3, noise=0.03, K=8, tnoise=0.02, reps=200):
    out = dict(stale=[], relearn=[], owner=[], owner_touch=[])
    for _ in range(reps):
        s = state()
        judge_map = learn_judge(s, N, noise)              # characterised before the event
        # touch characterisation of B (once per tube): judge map minus touch, low harmonics
        a = touch_azimuths(K); tq = T(s, a) + rng.normal(0, tnoise, K)
        jj = np.interp(a, np.append(th, 2 * np.pi), np.append(judge_map, judge_map[0]))
        Bfit = fit_low(a, (jj - (tq - tq.mean())))        # judge minus touch = B (+DC); DC dropped below
        # -- event
        s2 = dict(R=s['R'], S=s['S'], W=s['W'], B=s['B'], psi=s['psi'])
        if event == 'reseat': s2['S'] = draw([0.20])
        elif event == 'rotate': s2['S'] = draw([0.20]); s2['psi'] = rng.uniform(1.2, 2.2)
        elif event == 'newtube': s2['S'] = draw([0.20]); s2['W'] = draw([0.06, 0.05, 0.02]); s2['B'] = draw([0.03, 0.0, 0.02]); s2['psi'] = rng.uniform(0, 6)
        elif event == 'reclamp': s2['R'] = draw([0.06, 0.03])
        elif event == 'tack': s2['W'] = draw([0.06, 0.05, 0.05]); s2['B'] = draw([0.03, 0.0, 0.03])
        elif event == 'lift': s2['S'] = dict(amps=[0.20], ph=s['S']['ph'] + rng.normal(0, 0.05, 1))
        truth = T(s2, th)
        out['stale'].append(rms(truth - judge_map))
        m2 = learn_judge(s2, N, noise)                       # full relearn through the judge: B is imprinted
        out['relearn'].append(rms(truth - m2))
        # ownership-aware: keep the pieces the event leaves alone (from the earlier characterisation), rebuild the seat piece from K touches
        # kept = stored judge map minus its seat piece (seat piece known to the AI from its own fit) ; here: rebuild by touches at the same K azimuths
        a2 = touch_azimuths(K); t2 = T(s2, a2) + rng.normal(0, tnoise, K)
        kept = lambda x: comp(s['R'], x) + comp(s['W'], x, s['psi'])              # what the event leaves alone (perfectly known: upper bound)
        if event in ('reseat', 'lift'):
            seat = fit_low(a2, t2 - kept(a2), H=1)
            est = kept(th) + seat(th)
        elif event == 'rotate':
            # the work piece has rotated: its phase comes from a work index (ports give it mod 180 deg; assume resolved): re-key by measured psi
            kept2 = lambda x: comp(s['R'], x) + comp(s['W'], x, s2['psi'])
            seat = fit_low(a2, t2 - kept2(a2), H=1); est = kept2(th) + seat(th)
        elif event == 'reclamp':
            rig = fit_low(a2, t2 - (comp(s['S'], a2) + comp(s['W'], a2, s['psi'])), H=2); est = comp(s['S'], th) + comp(s['W'], th, s['psi']) + rig(th)
        else:                                                    # new tube or tack: no piece survives, K touches then a full fit up to 3 harmonics
            est = fit_low(a2, t2, H=3)(th)
        out['owner'].append(rms(truth - est))
    return {k: (np.mean(v) if v else 0) for k, v in out.items()}

print("radial rms residual after replay (mm), mean of 200 draws; N=3 judge revolutions, judge noise 0.03, K=8 touches at 0.02")
print(f"{'event':<9}{'stale map':>11}{'relearn N=3':>13}{'owner+K touches':>17}")
for ev in ('lift', 'reseat', 'rotate', 'reclamp', 'tack', 'newtube'):
    r = trial(ev)
    print(f"{ev:<9}{r['stale']:>11.3f}{r['relearn']:>13.3f}{r['owner']:>17.3f}")
s = state(); print("\nreference amplitudes: R", s['R']['amps'], "S", s['S']['amps'], "W", s['W']['amps'], "B", s['B']['amps'])
print("Bias imprint (judge-only relearn floor) = rms of B alone:", round(float(np.mean([rms(comp(state()['B'], th)) for _ in range(200)])), 3))
print("\nTouch count K vs residual for the 'newtube' policy (fit 3 harmonics), tnoise 0.02: ", end="")
for K in (4, 6, 8, 12):
    r = trial('newtube', K=K, reps=100); print(f"K={K}: {r['owner']:.3f}  ", end="")
print()
print("\nHow the estimate of harmonic k splits between rotate-in-nest laps: (e^{-ik dpsi} - 1) magnitude for dpsi = 100 deg")
for k in (1, 2, 3, 4):
    print(f"  k={k}: |e^(-ik*100deg) - 1| = {abs(np.exp(-1j*k*np.radians(100)) - 1):.2f}   at 120 deg: {abs(np.exp(-1j*k*np.radians(120)) - 1):.2f}")

# ---- invariants: how small a change in a harmonic can the judge see between two laps of the same tube?
print("\nPer-harmonic amplitude noise of a learned map: sigma_h = noise * sqrt(2 / (NB * N)), NB = %d bins" % NB)
for noise in (0.03, 0.06):
    for N in (1, 3, 5):
        print(f"  judge noise {noise:.2f}, N={N}: {noise*np.sqrt(2/(NB*N))*1000:.1f} micrometres per harmonic (1 sigma); a 3-sigma change is {3*noise*np.sqrt(2/(NB*N))*1000:.0f} micrometres")
# ---- time cost, illustrative: 8 mm/s bead speed = 49 s/rev; a touch pair at a stopped azimuth
rev = 388.61 / 8.0
print(f"\nOne revolution at 8 mm/s: {rev:.0f} s. N=3 revolutions: {3*rev:.0f} s.")
print("K=8 touches: table moves 45 deg (about 6 s at 7.4 deg/s), wall touch about 10 s (fast then slow), so about", 8 * 16, "s. Not faster; different (no judge bias).")
