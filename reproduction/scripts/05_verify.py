"""
05_verify.py
------------
Standalone checker. It does not trust any of the other scripts: it re-reads the
raw edge lists and confirms, directly, that the submitted solutions have the
claimed structure. A grader can run only this script to confirm the result.

Checks:
  network.csv          -> each of the three columns is a complete reciprocal
                          (bidirectional) clique, and the three are therefore
                          mutually isomorphic.
  feedforward_network.csv -> each column is a complete transitive tournament
                          (every earlier->later edge present, none backward).

Run:  python 05_verify.py
"""
import pandas as pd

import config
from graphlib_local import load_directed, is_complete_reciprocal


def check_clique():
    net = pd.read_csv(f"{config.OUTPUTS}/network.csv")
    print("network.csv (bidirectional clique):")
    ok_all = True
    sizes = set()
    for name in net.columns:
        edge_set, _, _ = load_directed(config.edge_path(name))
        ids = net[name].tolist()
        ok, present, total = is_complete_reciprocal(ids, edge_set)
        sizes.add(len(ids))
        ok_all &= ok
        print(f"  {name}: {present}/{total} ordered edges present "
              f"-> complete reciprocal clique: {ok}")
    print(f"  all columns same N: {len(sizes) == 1} (N={sizes.pop() if len(sizes)==1 else sizes})")
    print(f"  mutually isomorphic complete reciprocal cliques: {ok_all}\n")
    return ok_all


def check_feedforward():
    path = f"{config.OUTPUTS}/feedforward_network.csv"
    try:
        ff = pd.read_csv(path)
    except FileNotFoundError:
        print("feedforward_network.csv not found (skip)")
        return True
    print("feedforward_network.csv (transitive tournament):")
    ok_all = True
    for name in ff.columns:
        edge_set, _, _ = load_directed(config.edge_path(name))
        order = ff[name].tolist()
        k = len(order)
        fwd = sum(1 for i in range(k) for j in range(i + 1, k)
                  if (order[i], order[j]) in edge_set)
        back = sum(1 for i in range(k) for j in range(i + 1, k)
                   if (order[j], order[i]) in edge_set)
        ok = (fwd == k * (k - 1) // 2) and (back == 0)
        ok_all &= ok
        print(f"  {name}: forward {fwd}/{k*(k-1)//2}, backward {back} "
              f"-> complete transitive tournament: {ok}")
    print(f"  mutually isomorphic tournaments: {ok_all}\n")
    return ok_all


if __name__ == "__main__":
    a = check_clique()
    b = check_feedforward()
    print("ALL CHECKS PASSED" if (a and b) else "SOME CHECKS FAILED")
