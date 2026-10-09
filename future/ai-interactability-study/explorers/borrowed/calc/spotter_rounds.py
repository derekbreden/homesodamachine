#!/usr/bin/env python3
"""How many instruction rounds does a person need when software only spots and a hand turns the knobs?

Notebook arrangement B5 (manual cross-slide + jack with digital scales; the AI reads the scales and a camera and says
which knob to turn by how much). ILLUSTRATIVE model, two axes (radial X, vertical Z):
  each round: the camera estimate of the dot error = truth + bias + noise (sigma_cam, mm);
  the AI instructs a knob move equal to minus the estimate;
  the person turns the knob to the instructed scale reading, landing within +-hand (uniform) of it, the scale reads to
  res (0.01 mm), and a direction reversal loses `backlash` mm of screw travel before the table moves.
Rounds counted until the TRUE error on both axes is below tol; the floor of the error is set by the bias.
"""
import numpy as np

def trial(rng, bias, sigma_cam, hand, backlash, res=0.01, tol=0.1, start=(1.5, -1.0), max_rounds=20):
    err = np.array(start, float); last_dir = np.zeros(2)
    for k in range(1, max_rounds + 1):
        if np.all(np.abs(err) < tol): return k - 1, err
        est = err + bias + rng.normal(0, sigma_cam, 2)
        want = -est
        want = np.round(want / res) * res
        for i in range(2):
            actual = want[i] + rng.uniform(-hand, hand)
            d = np.sign(actual)
            if d != 0 and last_dir[i] != 0 and d != last_dir[i]:
                actual -= d * backlash          # slack taken up before the table moves
            if d != 0: last_dir[i] = d
            err[i] += actual
    return max_rounds, err

if __name__ == '__main__':
    rng = np.random.default_rng(7)
    print('mean rounds to reach 0.1 mm true error (start 1.5 / -1.0 mm), 400 trials; "-" = floor above 0.1 mm (never reached)')
    print('%-8s %-9s %-10s %-9s %s' % ('hand mm', 'backlash', 'cam bias', 'cam noise', 'rounds (mean)  final |error| mm (mean)'))
    for hand in (0.01, 0.05, 0.15):
        for bl in (0.0, 0.1):
            for bias in (0.0, 0.15):
                for sc in (0.03, 0.15):
                    rs = []; fe = []
                    for _ in range(400):
                        r, e = trial(rng, np.array([bias, -bias]), sc, hand, bl)
                        rs.append(r); fe.append(np.abs(e).max())
                    reached = np.mean([r < 20 for r in rs])
                    print('%-8.2f %-9.2f %-10.2f %-9.2f %s   %.3f' % (hand, bl, bias, sc, ('%.1f (%.0f%% reached)' % (np.mean(rs), reached * 100)) if reached > 0 else '-', np.mean(fe)))
