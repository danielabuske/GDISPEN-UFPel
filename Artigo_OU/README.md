# OU Spatial Epidemic Risk — Reproducible Figures

Code, supporting data and reproducible figures accompanying the manuscript **“An Analytical Model of Infectiousness for Spatial Epidemic Risk Assessment”** (*Royal Society Open Science*, manuscript under editorial consideration).

This repository contains **three independently runnable figure packages**. The code reproduces the numerical results and plots supplied with the manuscript; it does **not** establish independent epidemiological validation.

> **Article citation and DOI:** to be added after publication. Until then, cite the manuscript according to its current publication status. See [`PUBLICATION_CHECKLIST.md`](PUBLICATION_CHECKLIST.md).

## Figures and files

| Figure | Folder | Main script | Output PDF |
|---|---|---|---|
| Figure 1 — Bangkok-calibrated reach, weeks 1–55 | [`Figure_1_Bangkok/`](Figure_1_Bangkok/) | `generate_figure_1_bangkok.py` | [`figure_1_bangkok_p96.pdf`](Figure_1_Bangkok/results/figure_1_bangkok_p96.pdf) |
| Figure 2 — Porto Alegre descriptive comparison, weeks 1–20 | [`Figure_2_POA/`](Figure_2_POA/) | `generate_figure_2_poa.py` | [`figure_2_poa_p96.pdf`](Figure_2_POA/results/figure_2_poa_p96.pdf) |
| Figure 3 — Short-term reach, weeks 1–4.5 | [`Figure_3_POA_4_5_weeks/`](Figure_3_POA_4_5_weeks/) | `generate_figure_3_poa_4_5_weeks.py` | [`figure_3_poa_4_5_weeks_p96.pdf`](Figure_3_POA_4_5_weeks/results/figure_3_poa_4_5_weeks_p96.pdf) |

Each figure folder includes a local `README.txt`, exact package requirements, tests, a `validation/` numerical reference, and `results/` containing the accompanying vector PDF, CSV and JSON files. Figure 2 also includes `figure_2_data/` with the digitised comparison series and a provenance statement.

## Quick start

The supplied package was verified by its creators with **Python 3.12** and the exact dependencies listed in the individual folders. The figure directories are self-contained; do **not** install a guessed global dependency list in place of their own requirements.

```bash
# Choose any figure directory, for example:
cd Figure_1_Bangkok

# Optional: create and activate a virtual environment before installing.
python -m pip install -r requirements.txt
python generate_figure_1_bangkok.py
python -B -m unittest -v test_figure
```

For the other figures, use the analogous commands with their respective main scripts:

```bash
cd Figure_2_POA
python -m pip install -r requirements.txt
python generate_figure_2_poa.py
python -B -m unittest -v test_figure
```

```bash
cd Figure_3_POA_4_5_weeks
python -m pip install -r requirements.txt
python generate_figure_3_poa_4_5_weeks.py
python -B -m unittest -v test_figure
```

Start each block from the repository root (or open a terminal in the appropriate figure folder). The scripts can also be run from Geany if Geany uses the same Python environment.

Each generator writes a vector PDF and CSV/JSON data to its own `results/` folder, even when launched from a different working directory. Existing outputs are overwritten by default. To keep a separate run:

```bash
python generate_figure_1_bangkok.py --output-dir results_new_run
```

## Numerical and plotting conventions

- Reference central probability interval: **96% of the unmodified one-dimensional OU spatial density**, evaluated at a fixed time.
- The plotted reach is then scaled phenomenologically. **The adjusted envelope need not retain 96% probability coverage** under the original OU density.
- Spatial modulation coefficient: **α = 3.180**.
- Reference mean generation time: **18.2 days**.
- Vertical-axis label: **Modulated spatial reach (km)**.
- Figures 2 and 3 use **10,000 independent parameter draws at each time point** with random seed `20261102`.
- Their boxes are the 25th–75th percentiles, the center marks the median, and whiskers show the 5th–95th percentiles. These are model-output distributions under assumed variation of β, **not confidence intervals estimated from surveillance data**.
- Each figure keeps its own parameter definitions. If you change a parameter, update the other figures separately when a consistent comparison is intended.

### Figure-specific interpretation

**Figure 1:** The adjusted spatial envelope is calibrated to an *adopted* reference of approximately **20 km at 54 weeks**. This is calibration, not independent validation. The displayed time grid includes odd weeks from 1 to 55; the benchmark at week 54 is retained in the output CSV.

**Figure 2:** The red reference series, held in [`Figure_2_POA/figure_2_data/red_references.csv`](Figure_2_POA/figure_2_data/red_references.csv), is digitised from a prior graphical representation in the OU manuscript. Its provenance and limitations are documented in [`provenance.json`](Figure_2_POA/figure_2_data/provenance.json). The red references describe **diameters of reconstructed clusters of observed cases**; the model produces a **modulated one-dimensional reach**. These quantities are different, so their juxtaposition is descriptive rather than a test of predictive accuracy. The boxplot whiskers are not the red series' reported 95% confidence bounds.

**Figure 3:** Shows the same spatial-reach model over weeks 1–4.5 without the red empirical references. It does **not** estimate monthly cluster expansion speed.

## Reproducibility and provenance

The standalone code is designed not to require a network connection, the legacy `REBASE11` workflow, or archived manuscript PDFs during figure generation. The numerical reference files in `validation/` are read by tests, **not** as observational validation datasets.

An automated test run on this GitHub-preparation copy passed **33/33 tests** (Figure 1: 12; Figure 2: 13; Figure 3: 8) under Python 3.13.5 with the available local libraries. This is an additional compatibility check, **not** a replacement for the originally documented Python 3.12 environment and exact pinned package versions, and **not** epidemiological validation.

The supplied [`organization_manifest.json`](organization_manifest.json) records the previous packaging and file-hash provenance. Its original historical paths and source checksums have been left untouched; they refer to the original organization, not to this newly documented repository. The historical [`manuscript_audit_response21.md`](manuscript_audit_response21.md) is preserved for provenance and **should not be interpreted as an assessment of the final manuscript**.

## Citation, permissions and publication

The final article citation, author list and article DOI are not supplied in this code package. They should be added after confirmation by the authors. The package does **not** yet specify a software license; until the rights holders choose and add one, users should not assume unrestricted redistribution or reuse permissions. See [`PUBLICATION_CHECKLIST.md`](PUBLICATION_CHECKLIST.md).

For methodological details and limitations, consult the associated manuscript. In particular, computational reproduction of a plot must not be presented as independent validation of the epidemiological model.
