"""
graphlib_local.py
-----------------
Small shared helpers for loading an edge list into the structures the other
scripts need. Kept separate so every step loads graphs the same way.
"""
import pandas as pd
import networkx as nx


def load_directed(path):
    """Return (edge_set, out_adj, in_adj) for a two-column edge list.

    edge_set : set of (source, target) tuples, self-loops removed
    out_adj  : dict source -> set of targets
    in_adj   : dict target -> set of sources
    """
    df = pd.read_csv(path)
    df = df.iloc[:, :2]
    df.columns = ["s", "t"]
    df = df[df.s != df.t]
    s = df.s.tolist()
    t = df.t.tolist()
    edge_set = set(zip(s, t))
    out_adj, in_adj = {}, {}
    for a, b in zip(s, t):
        out_adj.setdefault(a, set()).add(b)
        in_adj.setdefault(b, set()).add(a)
    return edge_set, out_adj, in_adj


def reciprocal_graph(edge_set):
    """Undirected graph with an edge u-v iff both u->v and v->u exist.

    A clique in this graph is exactly a bidirectional clique in the original
    directed graph, which is what the primary result is built on.
    """
    G = nx.Graph()
    for (a, b) in edge_set:
        if a < b and (b, a) in edge_set:
            G.add_edge(a, b)
    return G


def is_complete_reciprocal(ids, edge_set):
    """True iff every ordered pair among `ids` is present (a complete reciprocal clique)."""
    ids = list(ids)
    k = len(ids)
    present = sum(
        1
        for i in range(k)
        for j in range(k)
        if i != j and (ids[i], ids[j]) in edge_set
    )
    return present == k * (k - 1), present, k * (k - 1)
