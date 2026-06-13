"""
04_feedforward.py
-----------------
Secondary result: the largest feedforward circuit common to three datasets,
defined as a transitive tournament (a set of neurons orderable so every earlier
one connects to every later one, one-way, with no edge backward). This is the
directional counterpart of the clique: it uses edge direction fully and fixes a
unique role for each neuron.

The search is a randomised greedy construction, so the reported size is a lower
bound and can vary slightly between runs (typically 8-10). The best run we obtained
was N=9, which is the version in the submitted feedforward_network.csv; re-running
may return 8 or 10. The primary clique result (03) is fully deterministic by
contrast.

Outputs: outputs/feedforward_network.csv (FAFB, MANC, MAOL; rows in source->sink order)

Run:  python 04_feedforward.py
"""
import random
import pandas as pd

import config
from graphlib_local import load_directed

random.seed(0)
TIME_BUDGET_SECONDS = 40     # per dataset; raise to find larger tournaments


def largest_tournament(out_adj, in_adj, nodes, budget):
    """Greedy: repeatedly append a node that receives from all current members and
    sends to none of them, which keeps the set a transitive tournament."""
    import time
    best = []
    t0 = time.time()
    deg_sorted = sorted(nodes, key=lambda n: -len(out_adj.get(n, ())))[:500]
    while time.time() - t0 < budget:
        s = random.choice(deg_sorted) if random.random() < 0.5 else random.choice(nodes)
        L, Lset = [s], {s}
        cand = {u for u in out_adj.get(s, set()) if s not in out_adj.get(u, set())}
        while cand:
            w = max(cand, key=lambda u: len(out_adj.get(u, set()) & cand))
            L.append(w); Lset.add(w)
            cand &= out_adj.get(w, set())
            cand = {u for u in cand if not (out_adj.get(u, set()) & Lset)} - Lset
        if len(L) > len(best):
            best = L[:]
    return best   # in source -> sink order


def verify_tournament(order, edge_set):
    k = len(order)
    fwd = sum(1 for i in range(k) for j in range(i + 1, k)
              if (order[i], order[j]) in edge_set and (order[j], order[i]) not in edge_set)
    return fwd, k * (k - 1) // 2


def main():
    # Find a tournament per dataset, verifying inline, and keep only the small
    # ordered list (never hold more than one full graph in memory at a time).
    found = {}
    for name in config.FEEDFORWARD_DATASETS:
        edge_set, out_adj, in_adj = load_directed(config.edge_path(name))
        nodes = list(set(out_adj) | set(in_adj))
        best = largest_tournament(out_adj, in_adj, nodes, TIME_BUDGET_SECONDS)
        fwd, total = verify_tournament(best, edge_set)
        assert fwd == total, f"{name} tournament not complete ({fwd}/{total})"
        found[name] = best
        del edge_set, out_adj, in_adj           # free the graph before the next dataset
        print(f"{name}: largest transitive tournament found = {len(best)} (verified)")

    n = min(len(b) for b in found.values())      # common size
    print(f"common size N = {n}")

    cols = {name: found[name][:n] for name in config.FEEDFORWARD_DATASETS}
    pd.DataFrame(cols).to_csv(f"{config.OUTPUTS}/feedforward_network.csv", index=False)
    print("wrote feedforward_network.csv (rows in source->sink order)")


if __name__ == "__main__":
    main()
