# How to run

Python 3 with `pandas`, `numpy`, `networkx`, `matplotlib`:

    pip install pandas numpy networkx matplotlib

## Data

Put the challenge data in a folder named `data/` next to `scripts/`, or set the
`DATA_DIR` environment variable to wherever the files live. Expected files:

    data/banc_626_edge_list.csv
    data/fafb_783_edge_list.csv
    data/manc_1_2_1_edge_list.csv
    data/maol_1_1_edge_list.csv
    data/mcns_0_9_edge_list.csv
    data/consolidated_cell_types.csv     (FAFB cell types)
    data/neurons.csv                     (BANC cell types + side)

The MCNS cell-type labels are not downloadable; the ones I gathered by hand from
Codex are shipped in `inputs/mcns_celltypes_manual.csv`. The specific FAFB clique
the matching is anchored to is in `inputs/fafb_anchor_clique.csv`.

## Order

    python scripts/01_eda.py            # structural analysis -> outputs/connectome_eda.png
    python scripts/02_extract_cliques.py # reciprocal clique pools (informational)
    python scripts/03_match_celltypes.py # builds outputs/network.csv + network_key.csv
    python scripts/04_feedforward.py     # builds outputs/feedforward_network.csv
    python scripts/05_verify.py          # re-checks the solutions against the raw edges

`05_verify.py` is the one to run to confirm the result independently: it re-reads
the raw edge lists and checks that each column of `network.csv` is a complete
reciprocal clique and that the three are mutually isomorphic.

## Notes

- `03_match_celltypes.py` is deterministic and reproduces the submitted
  `network.csv` exactly (BANC 27/38, MCNS 35/38, all-three 26/38 cell-type matches).
- `04_feedforward.py` is a randomised heuristic; size may vary slightly between runs.
- `01` and `02` enumerate maximal cliques on the larger graphs and take a few minutes.
