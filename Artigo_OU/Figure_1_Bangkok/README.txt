FIGURE 1 - BANGKOK

MAIN SCRIPT TO OPEN IN GEANY
  generate_figure_1_bangkok.py

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
  python generate_figure_1_bangkok.py
No arguments or internet connection are required after environment setup.

OUTPUTS
  results/figure_1_bangkok_p96.pdf
  results/figure_1_bangkok_p96.csv
  results/figure_1_bangkok_p96.json
The results folder is created next to the script, even when the working
directory is elsewhere. Repeating a run with the same arguments overwrites
these outputs. To preserve a run, use a different destination:
  python generate_figure_1_bangkok.py --output-dir results_new_run

"Modulated spatial reach (km)" is the Y-axis label. The envelope starts from
the central 96% interval of the 1D OU density before modulation, which does not
preserve that coverage under the original OU density. It is not a 2D radial quantile.
Alpha = 3.180 and all other adopted parameters are unchanged.
Neither folder organization nor English localization recalibrated parameters.
Adjust AXIS_LABEL_FONT_SIZE in the main script to change the axis-label font size.

The main script contains the equations and configuration without local modules.
It uses fixed beta, derived from Tg = 18.2 days and the adopted latent periods.
Orange marks are visual elements, not uncertainty bars.
The plotted time grid is 1, 3, ..., 55 weeks; the 54-week reference is in the CSV.
CSV columns: time_weeks, reach_km, plotted.
The plotted indicator is 1 for a point shown in the figure and 0 otherwise.

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
