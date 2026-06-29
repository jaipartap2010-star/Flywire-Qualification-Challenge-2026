# Largest shared neuronal circuit across FlyWire connectomes — technical approach

This repository contains my solution to the qualification challenge: finding the
largest neuronal circuit that recurs, as an identical directed wiring pattern, across
at least three of the five connectome datasets in Codex (BANC, FAFB, MANC, MAOL, MCNS).
This file explains how I chose what to look for, how I found it, how the matching was
done, and how to reproduce everything. The one-page biological summary is in
`science.md`.

## The problem

The task is to find a set of N neurons in each of three datasets whose directed,
induced subgraphs are mutually isomorphic, with N as large as possible, and weakly connected. Edge weights were not given for this problem.

The constraint that drives the whole approach and solution is that the datasets share no neuron
identifiers, forcing that the isomorphic structures can only be found by comparing connectivity across datasets.

## Choosing what structure to look for

The problem is NP-hard as it is a Maximum Common Induced Subgraph Problem, and these graphs have 23,000 to 166,000 nodes, so brute-force in search of the best solution is not possible. I also could not just
maximise N blindly, because that results in degenerate solutions with no clear biological meaning. Hence I sorted candidate structures by whether their size is limited by the graph or only by how long you search:

- A set of neurons with no connections (independent set) is identical everywhere because
  there is nothing to compare. It is now disallowed by the weak-connectivity requirement,
  but it shows the failure mode.
- A star (one hub, many unconnected targets), an hourglass, and a complete bipartite
  motif all have the same problem: one side only needs to be an independent set, so the
  structure grows with graph sparsity rather than stopping at a real ceiling. I tested
  the bipartite case directly and it collapsed to a two-hub star (two sources onto a few
  hundred mutually unconnected targets).
- An induced directed chain has the same issue. Searching for one returned paths of 86 to
  146 nodes, limited by search effort, not by structure.
- Directed rings (the continuous-attractor idea) are a real circuit type, but the data
  argues against finding large clean ones here (see the next section).

I refer to the first group as unbounded: their reported size is an illusion of a focus on only maximizing N. A **bidirectional clique** is the opposite. Every added neuron must connect to all
the others in both directions, so growth stops at a hard ceiling set by the data. It is
also, for the purposes of this challenge, the cleanest possible structure: a complete
reciprocal graph contains every possible edge, so its induced subgraph is identical in
any dataset that contains one and the isomorphism is automatic due to the reciprocation.

**Note on unbounded structures:** they are not invalid. A star or chain can be made
meaningful by adding constraints (a minimum hub degree, a fixed branching pattern, and so
on). But justifying any particular threshold is itself a neuroscience question, and an
arbitrary cutoff would make the reported N a choice *I* made rather than a property of the
data. I therefore restricted the submission to structures whose maximum is fixed by the
graph, and noted the others as deliberately set aside rather than overlooked.

### Why direction matters, and the second structure

The bidirectional clique has one weakness as a result: because every edge is reciprocal,
it carries no directional information. To address that I also searched for the directional counterpart of a clique,
a transitive tournament: a set of neurons that can be ordered so every earlier one
connects to every later one, one way, with no edges backward. This uses direction fully
and, unlike the clique, fixes a unique role for each neuron (a single source, a single
sink, and a unique position for each in between). It is reported as a secondary result
because it is smaller.

## Exploratory analysis behind the choice

Before committing, I measured structural properties of all five graphs
(`images/connectome_eda.png`):

- Reciprocity (fraction of edges whose reverse also exists): 14 to 17 percent in BANC,
  FAFB, MCNS; 28 to 30 percent in MANC and MAOL.
- Feedforward versus cyclic tendency: sampling directed two-paths, the path closes into a
  feedforward triangle 2.3 to 4.4 times more often than into a cycle, in every dataset.
  Cycles are the rarest closure, which is why I did not pursue large directed rings.
- Reciprocal clique sizes: the large cliques are not isolated. BANC contains 336 distinct
  cliques of size 38, MCNS has hundreds up to size 41. The size-38 result sits on a broad
  plateau, not a single peak.
- Degree distributions are heavy-tailed, which is why hub and star structures are easy to
  find but not meaningful as maxima.

So the structure was finalized from measurements.

## The bidirectional clique result

The three datasets with the largest reciprocal cliques are BANC and FAFB (38 each) and
MCNS (41). The common maximum is therefore 38. Each set of 38 neurons forms a complete
reciprocal graph: all 38 by 37 = 1,406 ordered edges are present, verified directly
against the raw edge lists for every dataset.

Identifying the circuit: I cross-referenced the 38 FAFB neuron IDs against the Schlegel
et al. annotation table. Thirty-six are antennal-lobe local neurons (lLN1 and lLN2
families) and two are antennal-lobe projection neurons (DP1m_adPN and VL2p_adPN). The
antennal lobe is the first olfactory relay; its local neurons are broadly interconnected
and provide lateral inhibition, which is the direct reason a large reciprocal clique
exists there. The BANC and MCNS members were checked against their own cell-type tables
(BANC) and in Codex (MCNS) and are antennal-lobe local neurons as well.

## Making the correspondence meaningful

A bidirectional clique is symmetric: any one-to-one pairing of two cliques is a valid
isomorphism. So the row-to-row correspondence in a clique solution is not determined by
the structure, and an arbitrary pairing carries no information. I did not want to submit
that.

The way out came from the plateau noted above. Because each dataset contains many
distinct size-38 cliques (a pool of 52 candidate neurons in BANC, 88 in FAFB, 149 in
MCNS), there is freedom to choose which clique to report. 

This was a key issue as there's no meaning to the isomorphism, so I used that freedom to pick
cliques whose cell-type compositions line up, and then ordered the rows so that row k is
the same cell type across datasets where possible. The structural result (N=38, three
identical reciprocal cliques) is unchanged; the matching is layered on top using an
external attribute (cell type) that the structure itself cannot supply.

I did the FAFB and BANC matching computationally from the two annotation tables, and
matched MCNS by looking its candidates up in Codex by hand. Results:

- 26 of 38 rows are the same cell type across all three datasets.
- 35 of 38 match between FAFB and MCNS.
- 27 of 38 match between FAFB and BANC.

The remaining rows are real compositional differences between the datasets, not errors;
`network_key.csv` marks every row with its cell type and whether BANC and MCNS matched.

Two specific findings came out of this. First, the two projection neurons behave
differently across datasets: FAFB has both DP1m and VL2p, DP1m recurs in the MCNS clique,
VL2p recurs in the BANC clique, but neither of the other two datasets contains both
alongside FAFB. In MCNS specifically, DP1m and VL2p do not appear in any common
bidirectional clique, because they are not reciprocally connected to each other there.
Second, on side: I kept FAFB on the left antennal lobe (matching the 3D figure) and BANC
and MCNS on the right. The same circuit therefore appears in both the left and right
lobe across the three datasets, which is consistent with the antennal lobe being
bilaterally paired. Matching across, rather than within, sides was a deliberate choice;
the region clarification from the organisers confirmed that cross-dataset region or side
correspondence is not required.

## Secondary result: feedforward circuit

The largest transitive tournament common to three datasets is N=9 (FAFB, MANC, MAOL),
verified as 36 one-way edges with none backward. In FAFB this cascade is fed by an
ascending neuron from the ventral nerve cord and runs through a series of AVLP (anterior
ventrolateral protocerebrum) neurons. It is included as a directional companion to the
clique because it exercises the directionality constraint the clique does not, and its
correspondence is fixed by position rather than arbitrary. Files: `feedforward network materials/feedforward_network.csvv`,
`feedforward network materials/feedforward_FAFB.graphml`, `feedforward network materials/FAFB_2D_feedforward.jpg`, and `feedforward network materials/FAFB_3D_feedforward.jpg`. The interpretation of small directed
motifs as computational units follows the approach in Seung (2024), which predicts
function from connectivity alone.

## Other approaches I tried and dropped

Early on I compiled lists of candidate macro-structures (block models, spectral
signatures, assortativity profiles). These describe whether two networks are similar in a
statistical sense but do not produce a node-for-node isomorphic subgraph, so they cannot
be a solution file for this task. I kept them only as context for why I chose an exact
structural object instead.

## Verification

Every reported set is checked independently of the procedure that found it: the
verification step re-reads the raw edge lists and confirms that the neuron set forms a
complete reciprocal clique (for the clique) or a complete one-way tournament (for the
feedforward). All three clique columns pass at 703 of 703 reciprocal pairs.

## Assumptions

1. Edge weights ignored; all analysis on unweighted directed graphs.
2. Self-loops removed.
3. A circuit is a directed induced subgraph; weak connectivity required; I additionally
   restricted to bounded structures.
4. No cross-dataset neuron identity assumed; correspondence is structural, then aligned by
   cell type where the annotations allow.
5. Clique and tournament searches are heuristics, so the reported N are lower bounds on
   the true maxima.

## Reproducing the results

Requirements: Python 3 with `pandas`, `numpy`, `networkx`, `matplotlib`
(`pip install pandas numpy networkx matplotlib`).

All code is in the `reproduction/` folder (`scripts/`, `inputs/`, `RUN.md`). Place the
challenge data in a `data/` folder next to `scripts/`, or set the `DATA_DIR`
environment variable to point at it. Expected files: the five edge lists, plus
`consolidated_cell_types.csv` (FAFB) and `neurons.csv` (BANC). The MCNS cell-type
labels were gathered by hand from Codex and are shipped in
`inputs/mcns_celltypes_manual.csv`; the fixed FAFB clique everything is matched to is
in `inputs/fafb_anchor_clique.csv`.

Run in order:

    python scripts/01_eda.py             # structural analysis -> connectome_eda.png
    python scripts/02_extract_cliques.py # reciprocal clique pools (informational)
    python scripts/03_match_celltypes.py # builds network.csv + network_key.csv
    python scripts/04_feedforward.py     # builds feedforward_network.csv
    python scripts/05_verify.py          # re-checks the solutions against raw edges

`03_match_celltypes.py` is deterministic and reproduces the submitted `network.csv`
exactly (BANC 27/38, MCNS 35/38, all three 26/38 cell-type matches).
`05_verify.py` is the script to run to confirm the result independently: it re-reads
the raw edge lists and checks that each column of `network.csv` is a complete
reciprocal clique and that the three are mutually isomorphic. `04_feedforward.py` is a
randomised heuristic, so its size may vary slightly between runs (8 to 10); the
submitted file is the best run (N=9). Steps 01 and 02 enumerate maximal cliques on the
larger graphs and take a few minutes.

## Files


- `network.csv` — primary solution: BANC, FAFB, MCNS; 38 rows; each column a verified
  bidirectional clique.
- `network_key.csv` — per-row cell type and BANC/MCNS type-match flags.
- `feedforward_network.csv` — secondary directional result (FAFB, MANC, MAOL; 9 rows).
- `feedforward_FAFB.graphml`, `feedforward_FAFB.png` — feedforward circuit graph.
- `connectome_eda.png` — exploratory analysis figure.
- `science.md` — one-page biological summary.
- `reproduction/` — runnable scripts, inputs, and run guide (see `reproduction/RUN.md`).

## Limitations

- The clique correspondence is not unique; cell-type matching makes it meaningful for 26
  of 38 rows but the rest remain structural only.
- Two of the three clique datasets (BANC, FAFB) are brain tissue, so cross-dataset
  conservation is partly within-tissue; the only sex contrast is MCNS (male) versus FAFB
  (female).
- Cell-type labels, especially predicted neurotransmitters, are annotations and
  predictions, not measurements.
- Searches are heuristic; true maxima may be slightly larger.

## Data sources and citations

Per the FlyWire citation guidance, the FlyWire resource is cited with Dorkenwald et al.
and Schlegel et al. Specific data products used here:

- Connectome reconstruction and connectivity: Dorkenwald et al., 2024.
  https://doi.org/10.1038/s41586-024-07558-y
- Hierarchical annotations and cell typing (FAFB): Schlegel et al., 2024.
  https://doi.org/10.1038/s41586-024-07686-5
- FAFB electron-microscopy volume: Zheng et al., 2018.
  https://doi.org/10.1016/j.cell.2018.06.019
- Predicted neurotransmitters (used for figure colouring): Eckstein, Bates et al., 2024.
  https://doi.org/10.1016/j.cell.2024.03.016
- Codex (data explorer used for lookups and 3D meshes):
  http://dx.doi.org/10.13140/RG.2.2.35928.67844
- Distributed control circuits across a brain-and-cord connectome: Bates et al.2026.
  https://www.nature.com/articles/s41586-026-10735-w 

Additional datasets (MANC, MAOL, MCNS) were used as data provided directly by the FlyWire team; primary dataset citations were not located and should be added if available.

Published FlyWire data is released under CC BY-NC 4.0.

Acknowledgement (per FlyWire credits guidance): "We thank the Princeton FlyWire team and
members of the Murthy and Seung labs, as well as members of the Allen Institute for Brain
Science, for development and maintenance of FlyWire (supported by BRAIN Initiative grants
MH117815 and NS126935 to Murthy and Seung). We also acknowledge members of the Princeton
FlyWire team and the FlyWire consortium for neuron proofreading and annotation."
