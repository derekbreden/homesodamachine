"""Can a camera + small motorised correction make Derek's soft suspension hold a dot?

1-DOF model of the tip node along X (radial) - the direction carry-and-locate holds with bungees.
    m x'' + c x' + k (x - u) = F(t)
x: dot position; u: bungee anchor position, moved by a stepper-driven slide; k: bungee pair.
The camera samples x at FPS with LATENCY and the slide follows a PID command (rate-limited).
All numbers are assumptions: gun + shell + loop hardware 1.5 kg on the tip node's share,
bungee pair 0.1 N/mm (carry-and-locate's estimate), damping ratio 0.03 open-loop.

Disturbances (carry-and-locate's load table, assumed magnitudes):
  wire push   2 N, ramped on over 0.3 s at bead start, then steady
  trigger     5 N step (only if pressed by hand; zero if the presser is inside the shell)
  cable creep 0.5 N over 60 s
Reported: peak and settled dot error. Also the same float with a damper added (zeta 0.5).
"""
import math

M = 1.5          # kg
K = 100.0        # N/m  (0.1 N/mm)
FPS, LATENCY = 30.0, 0.06
DT = 0.0005
V_MAX = 0.05     # m/s slide speed limit (50 mm/s, printer-class)


def run(force, zeta, gains, t_end=6.0):
    c = 2 * zeta * math.sqrt(K * M)
    kp, ki, kd = gains
    x = v = u = 0.0
    integ = 0.0
    last_meas = 0.0
    buf = []
    next_sample = 0.0
    u_cmd = 0.0
    peak = 0.0
    t = 0.0
    hist = []
    while t < t_end:
        if t >= next_sample:
            buf.append((t + LATENCY, x))
            next_sample += 1.0 / FPS
        while buf and buf[0][0] <= t:
            _, meas = buf.pop(0)
            err = -meas
            integ += err / FPS
            deriv = (meas - last_meas) * FPS
            last_meas = meas
            u_cmd = kp * err + ki * integ - kd * deriv
        du = max(-V_MAX * DT, min(V_MAX * DT, u_cmd - u))
        u += du
        a = (force(t) - c * v - K * (x - u)) / M
        v += a * DT
        x += v * DT
        peak = max(peak, abs(x))
        hist.append(x)
        t += DT
    settled = max(abs(h) for h in hist[-int(0.5 / DT):])
    return peak * 1000, settled * 1000


FORCES = {
    "wire push 2 N ramp 0.3 s": lambda t: 2.0 * min(1.0, t / 0.3),
    "trigger 5 N step": lambda t: 5.0,
    "cable creep 0.5 N / 60 s (first 6 s)": lambda t: 0.5 * t / 60.0,
}

print("open loop (anchor fixed): steady offset = F/k")
for name, f in FORCES.items():
    pk, st = run(f, 0.03, (0.0, 0.0, 0.0))
    print(f"  {name:36s}: peak {pk:7.2f} mm, end {st:7.2f} mm")


def stable(res):
    return all(st < max(0.3, 0.2 * pk) for pk, st in res)


for zeta in (0.03, 0.5):
    print(f"\nclosed loop through the bungee, camera {FPS:.0f} fps, {LATENCY*1000:.0f} ms latency, damping ratio {zeta}")
    candidates = []
    for kp in (0.1, 0.3, 0.6, 1.0, 2.0, 3.0):
        for ki in (0.0, 0.3, 1.0, 3.0):
            for kd in (0.0, 0.05, 0.1, 0.2, 0.4):
                res = [run(f, zeta, (kp, ki, kd)) for f in FORCES.values()]
                if stable(res):
                    candidates.append((max(pk for pk, _ in res[:2]), kp, ki, kd, res))
    if not candidates:
        print("  no stable gain set in the grid")
        continue
    candidates.sort(key=lambda c: c[0])
    w, kp, ki, kd, res = candidates[0]
    print(f"  best gains found kp={kp} ki={ki} kd={kd}")
    for (name, f), (pk, st) in zip(FORCES.items(), res):
        print(f"  {name:36s}: peak {pk:7.2f} mm, last 0.5 s within {st:6.3f} mm")
