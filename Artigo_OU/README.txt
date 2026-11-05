OU ARTICLE - STANDALONE FIGURES

This package contains three independently runnable figures for the article.
No REBASE11 execution is required. The original organization preserved earlier
versions under Figuras_Artigo_OU/Figura_1_Bangkok in the source project; those
historical files are not required by this standalone package.

STRUCTURE
  Figure_1_Bangkok/           Figure 1, evolution through week 55
  Figure_2_POA/               Figure 2, boxplots from weeks 1 to 20
  Figure_3_POA_4_5_weeks/    Figure 3, boxplots from weeks 1 to 4.5

Each subfolder is independent and can be copied to another location on its own.
It does not import modules from neighboring folders or require old PDFs or
network access during generation. Python libraries are not bundled; their
names and versions are listed in each subfolder's requirements.txt.

HOW TO RUN
1. Use Python 3.12 (the verified version).
2. If dependencies are missing, open a terminal in the selected subfolder:
     python -m pip install -r requirements.txt
   This is only needed to prepare the environment; reinstalling is unnecessary
   if the selected Python interpreter already has the listed versions.
3. In Geany, open the subfolder's generate_figure_...py script and choose Execute.
   Configure Geany to use the Python interpreter containing the dependencies.
4. PDF, CSV, and JSON files are written to the figure's results folder,
   regardless of Geany's working directory.
5. To check the installation and calculations, run in the selected subfolder:
     python -B -m unittest -v test_figure

ADOPTED CONFIGURATION
- Figures 1, 2, and 3 use the Y-axis label "Modulated spatial reach (km)".
- The envelope starts from the central 96% interval of the 1D OU density.
- Modulation does not preserve that coverage under the original OU density.
- Alpha = 3.180, baseline Tg = 18.2 days; all other parameters are retained.
- Figures 2 and 3 use 10,000 samples per time point and seed 20261102.
- Boxes show P25-P75, medians P50, and whiskers P5-P95 of assumed beta variability.
- The mathematical code and colors are retained; output is vector PDF,
  without legends below the plots.
- Both axis labels use 18 pt; tick labels remain 10 pt.
  Adjust AXIS_LABEL_FONT_SIZE near the start of each main figure script.
- No recalibration or change in statistical interpretation was introduced.

INTERPRETATION
Figure 2 retains red references digitized from the previous OU manuscript.
They are diameters of reconstructed clusters of observed cases, not the same
quantity as the model's modulated 1D reach.
The spatial 96% convention is neither the boxplot interval nor parameter confidence.
Figure 3 does not use these references and does not represent monthly speed.

Each folder contains its own parameters and required functions.
Changing one figure does NOT automatically update the others. Keep configurations
consistent when comparing the article's figures.

LANGUAGE AND COMPATIBILITY
Python code, instructions, report text, and CSV column/series labels are in English.
Files and figure subfolders use English names. The package root remains Artigo_OU.
Source-document titles and archived historical path identifiers are retained for
provenance; they do not identify current executable files.
The Figure 2 reader also accepts the legacy Portuguese CSV labels.
The requirements.txt comments are in English; dependency versions are unchanged.
The audit report is a dated historical assessment, not a new review of the
latest manuscript. Its translation does not update its scientific findings.

REPRODUCIBILITY
Tests check calculations, output format and appearance, numerical reproduction,
and execution from an isolated copy with a different working directory.
These are code-consistency tests, not epidemiological validation.
Reference CSV files in validation are used only by tests.
organization_manifest.json records historical provenance and the current file
hashes and English-localization checks.
Generated __pycache__ folders are not required for execution or distribution.
