import numpy as np
import math

def dp_best_order(files, sims, start_idx, end_idx, max_n=18):
    n=len(files)
    if n > max_n:
        return None

    size=1<<n
    dp=[[-math.inf]*n for _ in range(size)]
    parent=[[None]*n for _ in range(size)]

    start_mask=1<<start_idx
    dp[start_mask][start_idx]=0.0

    for mask in range(size):
        for i in range(n):
            if dp[mask][i] == -math.inf: continue
            if not (mask & (1<<i)): continue
            for j in range(n):
                if mask & (1<<j): continue
                new_mask=mask|(1<<j)
                score=dp[mask][i]+sims[i][j]
                if score > dp[new_mask][j]:
                    dp[new_mask][j]=score
                    parent[new_mask][j]=i

    full_mask=(1<<n)-1
    best_last=end_idx
    if dp[full_mask][best_last] == -math.inf:
        return None

    order=[]
    mask=full_mask
    cur=best_last
    while cur is not None:
        order.append(cur)
        prev=parent[mask][cur]
        mask ^=1<<cur
        cur=prev

    order.reverse()
    if order[0] != start_idx: return None
    return order
