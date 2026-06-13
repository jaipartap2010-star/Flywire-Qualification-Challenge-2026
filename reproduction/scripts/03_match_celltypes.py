"""
03_match_celltypes.py
---------------------
Build the final, cell-type-aligned network.csv.

Why this step exists: a bidirectional clique is symmetric, so any pairing of two
cliques is a valid isomorphism and the row-to-row correspondence is otherwise
arbitrary. Because each dataset has many size-38 cliques, we can instead *choose*
cliques whose cell-type compositions line up, and order rows so that row k is the
same cell type across datasets wherever possible.

Anchor: we fix the FAFB column to a specific 38-clique (inputs/fafb_anchor_clique.csv)
and select the BANC and MCNS cliques to match it. FAFB side is left; BANC and MCNS
are right (the circuit therefore appears in both antennal lobes).

Determinism: among candidate cliques we maximise type overlap with FAFB, prefer
including the projection neurons (BANC), and break ties by the sorted neuron-id tuple.

Inputs:  data/consolidated_cell_types.csv (FAFB), data/neurons.csv (BANC),
         inputs/mcns_celltypes_manual.csv (MCNS, gathered from Codex by hand),
         inputs/fafb_anchor_clique.csv
Outputs: outputs/network.csv, outputs/network_key.csv

Run:  python 03_match_celltypes.py
"""
from collections import Counter, defaultdict, deque
from itertools import combinations

import pandas as pd
import networkx as nx

import config
from graphlib_local import load_directed, reciprocal_graph, is_complete_reciprocal

PN_TYPES = {"DP1m_adPN", "VL2p_adPN"}


def fafb_anchor_and_types():
    anchor = pd.read_csv(config.FAFB_ANCHOR)["FAFB"].tolist()
    cons = pd.read_csv(config.FAFB_TYPES).set_index("root_id")["primary_type"].to_dict()
    ftype = {n: cons.get(n) for n in anchor}
    return anchor, ftype


def banc_clique(fafb_comp):
    edge_set, _, _ = load_directed(config.edge_path("BANC"))
    G = reciprocal_graph(edge_set)
    banc = pd.read_csv(config.BANC_TYPES)
    banc.columns = [c.strip() for c in banc.columns]
    btype = banc.set_index("Root ID")["Primary Cell Type"].to_dict()
    cliques = [sorted(c) for c in nx.find_cliques(G) if len(c) == 38]

    def overlap(c):
        cc = Counter(btype.get(n) for n in c)
        return sum(min(cc[t], fafb_comp[t]) for t in fafb_comp)

    def pn_count(c):
        return sum(1 for n in c if btype.get(n) in PN_TYPES)

    # prefer projection neurons, then type overlap, then deterministic tie-break
    best = max(cliques, key=lambda c: (pn_count(c), overlap(c), tuple(c)))
    return best, btype, edge_set


def mcns_clique(fafb_comp):
    edge_set, _, _ = load_directed(config.edge_path("MCNS"))
    labels = pd.read_csv(config.MCNS_TYPES)
    mtype = dict(zip(labels.mcns_id, labels.cell_type))
    nodes = list(mtype)
    G = nx.Graph(); G.add_nodes_from(nodes)
    for a, b in combinations(nodes, 2):
        if (a, b) in edge_set and (b, a) in edge_set:
            G.add_edge(a, b)
    cliques = [sorted(c) for c in nx.find_cliques(G)]

    def overlap(c):
        cc = Counter(mtype[n] for n in c)
        return sum(min(cc[t], fafb_comp[t]) for t in fafb_comp)

    best = max(cliques, key=lambda c: (overlap(c), tuple(c)))
    return best, mtype, edge_set


def assemble(anchor, ftype, bclq, btype, mclq, mtype):
    fafb_comp = Counter(ftype.values())

    # order FAFB rows: group by type (most common first), projection neurons last
    order_types = [t for t, _ in fafb_comp.most_common() if t not in PN_TYPES]
    order_types += [t for t in ("DP1m_adPN", "VL2p_adPN") if t in fafb_comp]
    fafb_rows = [(n, ftype[n]) for t in order_types for n in anchor if ftype[n] == t]

    bq, mq = defaultdict(deque), defaultdict(deque)
    for n in bclq:
        bq[btype.get(n)].append(n)
    for n in mclq:
        mq[mtype.get(n)].append(n)

    rows = []
    for fn, t in fafb_rows:
        bb = bq[t].popleft() if bq[t] else None
        mm = mq[t].popleft() if mq[t] else None
        rows.append([fn, bb, mm, t])

    # fill rows that had no same-type partner with leftover neurons, so each column
    # remains a full 38-neuron clique
    bleft = deque(n for q in bq.values() for n in q)
    mleft = deque(n for q in mq.values() for n in q)
    for r in rows:
        if r[1] is None and bleft:
            r[1] = bleft.popleft()
        if r[2] is None and mleft:
            r[2] = mleft.popleft()
    return rows


def main():
    anchor, ftype = fafb_anchor_and_types()
    fafb_comp = Counter(ftype.values())
    bclq, btype, banc_edges = banc_clique(fafb_comp)
    mclq, mtype, mcns_edges = mcns_clique(fafb_comp)
    rows = assemble(anchor, ftype, bclq, btype, mclq, mtype)

    fafb = [r[0] for r in rows]; banc = [r[1] for r in rows]; mcns = [r[2] for r in rows]

    # write the submission file (3 dataset columns)
    pd.DataFrame({"BANC": banc, "FAFB": fafb, "MCNS": mcns}).to_csv(
        f"{config.OUTPUTS}/network.csv", index=False)

    # write the companion key with per-row type and match flags
    key = pd.DataFrame({
        "FAFB": fafb,
        "cell_type": [r[3] for r in rows],
        "BANC": banc,
        "BANC_type_match": ["Y" if btype.get(b) == r[3] else "N" for b, r in zip(banc, rows)],
        "MCNS": mcns,
        "MCNS_type_match": ["Y" if mtype.get(m) == r[3] else "N" for m, r in zip(mcns, rows)],
    })
    key.to_csv(f"{config.OUTPUTS}/network_key.csv", index=False)

    both = sum((key.BANC_type_match == "Y") & (key.MCNS_type_match == "Y"))
    print(f"BANC type-matched: {sum(key.BANC_type_match=='Y')}/38")
    print(f"MCNS type-matched: {sum(key.MCNS_type_match=='Y')}/38")
    print(f"matched in all three: {both}/38")
    print("wrote network.csv and network_key.csv")


if __name__ == "__main__":
    main()
