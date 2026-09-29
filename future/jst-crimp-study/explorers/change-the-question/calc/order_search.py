import itertools
def evaluate(seq):  # seq: list of cavity (or None) in ribbon position order
    m = {i+1: c for i, c in enumerate(seq)}
    A = sorted([(c, p) for p, c in m.items() if c is not None and c % 2 == 1])
    B = sorted([(c, p) for p, c in m.items() if c is not None and c % 2 == 0])
    cr = lambda row: sum(1 for i in range(len(row)) for j in range(i+1, len(row)) if row[i][1] > row[j][1])
    mis = sum(1 for c, p in A if p % 2 == 0) + sum(1 for c, p in B if p % 2 == 1)
    return mis, cr(A) + cr(B)
def orders_4p_J4():
    pairs = [("3V3", "IO26"), ("V5", "IO25")]
    out = set()
    for pp in itertools.permutations(pairs):
        for f0 in (0, 1):
            for f1 in (0, 1):
                a = pp[0][::-1] if f0 else pp[0]; b = pp[1][::-1] if f1 else pp[1]
                out.add(tuple(a + b))
    return out
cav4 = {"3V3": 1, "GND": 2, "V5": 3, "IO25": 4, "IO26": 5, "IO27": 6, "IO23": 7}
best = []
for o4 in orders_4p_J4():
    for o3 in itertools.permutations(["GND", "IO27", "IO23"]):
        if abs(o3.index("IO27") - o3.index("IO23")) != 1: continue
        for first in ("4P", "3P"):
            seq = list(o4) + list(o3) if first == "4P" else list(o3) + list(o4)
            best.append((evaluate([cav4[n] for n in seq]), first, seq))
best.sort()
print("J4 least-crossing orderings (off-parity conductors, crossings):")
for b in best[:6]: print(" ", b)
cav7 = {"RB1":1,"RB2":2,"RB3":3,"RB4":4,"CLO":5,"CHI":6,"GND":7}
best7 = []
for o5 in itertools.permutations(["RB1","RB2","RB3","RB4","GND"]):
    for o3 in itertools.permutations(["CLO","CHI","X"]):
        for first in ("5P","3P"):
            seq = list(o5)+list(o3) if first=="5P" else list(o3)+list(o5)
            best7.append((evaluate([cav7.get(n) for n in seq]), first, seq))
best7.sort()
print("J7 least-crossing orderings (unconstrained reed order):")
for b in best7[:6]: print(" ", b)
# J7 with reed order kept monotone along the 5P (peel order up the column) and GND at either edge
cons = [b for b in best7 if [n for n in b[2] if n.startswith("RB")] in (["RB1","RB2","RB3","RB4"],["RB4","RB3","RB2","RB1"])]
print("J7 least-crossing with reeds in column order:")
for b in cons[:6]: print(" ", b)
