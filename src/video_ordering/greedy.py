import numpy as np

def greedy_order(files, sims, start_idx, end_idx):
    n = len(files)
    used = set([start_idx])
    order=[start_idx]
    current=start_idx

    while len(used) < n:
        best_j=None
        best_sim=-99.0
        for j in range(n):
            if j in used: continue
            if j == end_idx: continue
            sim=sims[current][j]
            if sim > best_sim:
                best_sim=sim
                best_j=j
        if best_j is None: break
        order.append(best_j)
        used.add(best_j)
        current=best_j

    if end_idx not in order:
        order.append(end_idx)

    return order
