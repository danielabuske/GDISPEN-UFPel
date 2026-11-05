FIGURE 2 - PORTO ALEGRE THROUGH WEEK 20

MAIN SCRIPT TO OPEN IN GEANY
  generate_figure_2_poa.py

This folder can be copied to another location on its own. Keep its local files;
the other figures, REBASE11, and manuscript PDFs are not required.

SETUP
Verified Python version: 3.12.
If needed, run in a terminal opened in this folder:
  python -m pip install -r requirements.txt
Libraries are not bundled. Configure Geany to use the same Python interpreter
in which the dependencies were installed.

RUN
In Geany, open the main script listed above and choose Execute.
Alternatively, run in a terminal opened in this folder:
  python generate_figure_2_poa.py
No arguments or internet connection are required after environment setup.

OUTPUTS
  results/figure_2_poa_p96.pdf
  results/figure_2_poa_p96.csv
  results/figure_2_poa_p96.json
The results folder is created next to the script, even when the working
directory is elsewhere. Repeating a run with the same arguments overwrites
these outputs. To preserve a run, use a different destination:
  python generate_figure_2_poa.py --output-dir results_new_run

"Modulated spatial reach (km)" is the Y-axis label. The envelope starts from
the central 96% interval of the 1D OU density before modulation, which does not
preserve that coverage under the original OU density. It is not a 2D radial quantile.
Alpha = 3.180 and all other adopted parameters are unchanged.
Neither folder organization nor English localization recalibrated parameters.
Adjust AXIS_LABEL_FONT_SIZE in the main script to change the axis-label font size.

LOCAL FILES
- ou_model.py: equation and reference spatial/temporal parameters.
- poa_model.py: beta distribution, sampling, colors, and statistics.
- figure_2_data/red_references.csv: red reference points and curves.
- figure_2_data/provenance.json: reference provenance and limitations.

BOXPLOT CONFIGURATION
The mean and SD of beta are 1.2939 and 0.1294 per week in the lognormal distribution
BEFORE truncation. Truncation is between quantiles 0.40 and 0.75.
Each time point uses 10,000 draws; seed = 20261102.
Median P50, boxes P25-P75, whiskers P5-P95. These are time-specific marginal
distributions, not longitudinal trajectories, 95% confidence intervals, or a
representation of all model uncertainty.
Red references were digitized from the OU manuscript; they are not primary data.
They describe diameters of reconstructed clusters of observed cases and are not
equivalent to the model's modulated 1D reach.
The input CSV uses series, order, time_weeks, and distance_km.
Series labels are mean_diameter, lower_ci95, and upper_ci95.
Legacy Portuguese labels remain supported by the reader.
The output CSV uses week, whislo, q1, med, q3, and whishi.
These statistics are the time point, P5, P25, P50, P75, and P95, respectively.

TESTS
  python -B -m unittest -v test_figure
The portability test copies only the necessary files into a temporary folder
and executes from another working directory, without the project's PYTHONPATH.
validation/numerical_reference_p96.csv records previous numerical values to detect
unintended changes. It is not epidemiological validation data and is not read
by the generator. Only its column labels were translated; numbers are unchanged.

Each figure has its own configuration. When changing article parameters, check
consistency across the three folders; they are not synchronized automatically.
Filenames, local imports, and output paths use English.
