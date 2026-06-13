"""
02_extract_cliques.py
---------------------
For the primary-solution datasets (BANC, FAFB, MCNS), build the reciprocal
subgraph, enumerate maximal cliques, and report the maximum size and the pool of
neurons that appear in any maximum-size clique. The pools are what give the
freedom to pick a cell-type-aligned clique in the next step.

Writes outputs/clique_pools.json for inspection. This step is informational; the
actual selection happens in 03_match_celltypes.py.

Run:  python 02_extract_cliques.py
"""
import json
import networkx as nx

import config
from graphlib_local import load_directed, reciprocal_graph


def main():
    summary = {}
    for name in config.CLIQUE_DATASETS:
        edge_set, _, _ = load_directed(config.edge_path(name))
        G = reciprocal_graph(edge_set)
        cliques = list(nx.find_cliques(G))
        mx = max(len(c) for c in cliques)
        pool = sorted({n for c in cliques if len(c) == mx for n in c})
        n_at_max = sum(1 for c in cliques if len(c) == mx)
        summary[name] = {"max_clique": mx,
                         "num_max_cliques": n_at_max,
                         "pool_size": len(pool),
                         "pool": pool}
        print(f"{name}: max reciprocal clique = {mx}, "
              f"{n_at_max} cliques of that size, pool of {len(pool)} neurons")

    with open(f"{config.OUTPUTS}/clique_pools.json", "w") as f:
        json.dump(summary, f)
    print("wrote", f"{config.OUTPUTS}/clique_pools.json")


if __name__ == "__main__":
    main()
