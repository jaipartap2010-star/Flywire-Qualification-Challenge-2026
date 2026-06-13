"""
01_eda.py
---------
Exploratory analysis used to decide which structure to look for. Produces the
figure outputs/connectome_eda.png with four panels:

  A. How directed 2-paths close: feedforward (u->w) vs cyclic (w->u) vs reciprocal.
     Across all five datasets feedforward closure dominates, which is the evidence
     against chasing large directed rings.
  B. Reciprocal clique-size distribution: shows the size-38 plateau in BANC/FAFB/MCNS.
  C. Out-degree distributions (heavy-tailed -> hubs exist -> star/hourglass inflate).
  D. Largest reciprocal clique per dataset.

Run:  python 01_eda.py
"""
import random
from collections import Counter
from itertools import combinations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

import config
from graphlib_local import load_directed, reciprocal_graph

random.seed(1)
ORDER = ["BANC", "FAFB", "MCNS", "MANC", "MAOL"]
COL = {"BANC": "#2c7fb8", "FAFB": "#41ab5d", "MCNS": "#d95f0e",
       "MANC": "#8856a7", "MAOL": "#e7298a"}


def two_path_closure(edge_set, out_adj, n_samples=200000):
    """Sample directed 2-paths u->v->w and record how the u,w pair closes."""
    src = [a for (a, _) in edge_set]
    tgt = {}
    for a, b in edge_set:
        tgt.setdefault(a, []).append(b)
    edges = list(edge_set)
    counts = Counter()
    got = 0
    for _ in range(n_samples):
        u, v = edges[random.randrange(len(edges))]
        nb = tgt.get(v)
        if not nb:
            continue
        w = nb[random.randrange(len(nb))]
        if w == u:
            continue
        got += 1
        uw = (u, w) in edge_set
        wu = (w, u) in edge_set
        if uw and wu:
            counts["reciprocal"] += 1
        elif uw:
            counts["transitive"] += 1
        elif wu:
            counts["cyclic"] += 1
        else:
            counts["open"] += 1
    return {k: counts[k] / got for k in ("transitive", "cyclic", "reciprocal", "open")}


def main():
    stats = {}
    for name in ORDER:
        edge_set, out_adj, in_adj = load_directed(config.edge_path(name))
        reciprocity = sum(1 for (a, b) in edge_set if (b, a) in edge_set) / len(edge_set)
        closure = two_path_closure(edge_set, out_adj)
        G = reciprocal_graph(edge_set)
        clique_sizes = Counter(len(c) for c in nx.find_cliques(G))
        outdeg = sorted((len(v) for v in out_adj.values()), reverse=True)
        stats[name] = dict(reciprocity=reciprocity, closure=closure,
                           clique_sizes=clique_sizes, outdeg=outdeg,
                           maxclique=max(clique_sizes))
        print(f"{name}: reciprocity={reciprocity:.3f} "
              f"transitive={closure['transitive']:.3f} cyclic={closure['cyclic']:.3f} "
              f"max_reciprocal_clique={max(clique_sizes)}")

    fig, ax = plt.subplots(2, 2, figsize=(13, 9))
    fig.suptitle("Empirical structure of the five connectomes", fontsize=13)

    # Panel A
    import numpy as np
    a = ax[0, 0]; x = np.arange(len(ORDER)); w = 0.25
    a.bar(x - w, [stats[n]["closure"]["transitive"] for n in ORDER], w,
          label="transitive u->w (feedforward)", color="#2166ac")
    a.bar(x, [stats[n]["closure"]["cyclic"] for n in ORDER], w,
          label="cyclic w->u (ring)", color="#b2182b")
    a.bar(x + w, [stats[n]["closure"]["reciprocal"] for n in ORDER], w,
          label="reciprocal (clique)", color="#5aae61")
    a.set_xticks(x); a.set_xticklabels(ORDER); a.set_ylabel("fraction of 2-paths")
    a.set_title("A. Feedforward vs cyclic 2-path closure"); a.legend(fontsize=8)

    # Panel B
    b = ax[0, 1]
    for n in ORDER:
        s = stats[n]["clique_sizes"]; xs = sorted(s); ys = [s[k] for k in xs]
        b.semilogy(xs, ys, marker="o", ms=3, color=COL[n],
                   label=f"{n} (max {stats[n]['maxclique']})")
    b.axvline(38, ls="--", color="gray", lw=1)
    b.set_xlabel("reciprocal clique size"); b.set_ylabel("# maximal cliques (log)")
    b.set_title("B. Reciprocal clique-size distribution"); b.legend(fontsize=8)

    # Panel C
    c = ax[1, 0]
    for n in ORDER:
        d = np.array(stats[n]["outdeg"]); ccdf = np.arange(1, len(d) + 1) / len(d)
        c.loglog(d, ccdf, color=COL[n], label=n, lw=1.3)
    c.set_xlabel("out-degree"); c.set_ylabel("P(X >= x)")
    c.set_title("C. Out-degree distributions"); c.legend(fontsize=8)

    # Panel D
    d = ax[1, 1]
    mc = [stats[n]["maxclique"] for n in ORDER]
    bars = d.bar(ORDER, mc, color=[COL[n] for n in ORDER])
    d.axhline(38, ls="--", color="gray")
    for bar, v in zip(bars, mc):
        d.text(bar.get_x() + bar.get_width() / 2, v + 0.5, str(v), ha="center")
    d.set_ylabel("largest bidirectional clique")
    d.set_title("D. Largest reciprocal clique per dataset")

    plt.tight_layout(rect=[0, 0, 1, 0.97])
    out = f"{config.OUTPUTS}/connectome_eda.png"
    plt.savefig(out, dpi=140, bbox_inches="tight")
    print("wrote", out)


if __name__ == "__main__":
    main()
