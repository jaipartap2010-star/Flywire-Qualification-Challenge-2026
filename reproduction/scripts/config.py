"""
config.py
---------
Shared paths and constants for the pipeline.

By default this expects the five edge-list CSVs and the two cell-type tables in a
folder called `data/` sitting next to this scripts/ directory. Override with the
DATA_DIR environment variable if your files live elsewhere, e.g.

    DATA_DIR=/path/to/data python 02_extract_cliques.py

Edge-list files are two columns (source id, target id), no header assumptions made
beyond the first two columns being source and target.
"""
import os

# ----------------------------------------------------------------------
# Folder layout
# ----------------------------------------------------------------------
HERE      = os.path.dirname(os.path.abspath(__file__))
ROOT      = os.path.dirname(HERE)                       # the solution/ folder
DATA_DIR  = os.environ.get("DATA_DIR", os.path.join(ROOT, "data"))
INPUTS    = os.path.join(ROOT, "inputs")                # files we ship (manual labels, anchor)
OUTPUTS   = os.path.join(ROOT, "outputs")              # everything the pipeline writes
os.makedirs(OUTPUTS, exist_ok=True)

# ----------------------------------------------------------------------
# Edge lists (the five connectomes)
# ----------------------------------------------------------------------
EDGE_FILES = {
    "BANC": "banc_626_edge_list.csv",
    "FAFB": "fafb_783_edge_list.csv",
    "MANC": "manc_1_2_1_edge_list.csv",
    "MAOL": "maol_1_1_edge_list.csv",
    "MCNS": "mcns_0_9_edge_list.csv",
}

def edge_path(name):
    return os.path.join(DATA_DIR, EDGE_FILES[name])

# ----------------------------------------------------------------------
# Cell-type tables
#   FAFB: consolidated_cell_types.csv  (root_id, primary_type, additional_type(s))
#   BANC: neurons.csv                  (Root ID, ..., Soma side, Primary Cell Type, ...)
#   MCNS: shipped in inputs/ because these labels were gathered by hand from Codex
# ----------------------------------------------------------------------
FAFB_TYPES = os.path.join(DATA_DIR, "consolidated_cell_types.csv")
BANC_TYPES = os.path.join(DATA_DIR, "neurons.csv")
MCNS_TYPES = os.path.join(INPUTS,  "mcns_celltypes_manual.csv")

# The specific FAFB 38-clique we anchored the whole matching to (see README).
FAFB_ANCHOR = os.path.join(INPUTS, "fafb_anchor_clique.csv")

# Datasets used for each result
CLIQUE_DATASETS      = ["BANC", "FAFB", "MCNS"]   # primary bidirectional-clique solution
FEEDFORWARD_DATASETS = ["FAFB", "MANC", "MAOL"]   # secondary transitive-tournament result
