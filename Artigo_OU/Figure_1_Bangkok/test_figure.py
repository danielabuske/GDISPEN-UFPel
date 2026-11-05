"""Mathematical and export tests: python -m unittest -v."""
import csv
import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from statistics import NormalDist
import numpy as np
from generate_figure_1_bangkok import (
    Parameters, reach_km, generate_figure, CENTRAL_PROBABILITY,
    SPATIAL_STANDARD_DEVIATIONS, TWO_SD_PROBABILITY, reach_label, reach_suffix,
)


# Accept legacy headers while comparing the archived numerical reference values.
LEGACY_CSV_COLUMNS = {
    "tempo_semanas": "time_weeks",
    "alcance_km": "reach_km",
    "ponto_no_grafico": "plotted",
}

class TestFigure1(unittest.TestCase):
    def test_full_precision_beta(self):
        self.assertAlmostEqual(Parameters().beta_per_week, 1.2938747370452313, places=13)

    def test_historical_96_percent_anchor_at_54_weeks(self):
        p = Parameters(central_probability=.96)
        self.assertAlmostEqual(float(reach_km(54, p)), 20.0311679616657, places=9)

    def test_points_from_original_pdf(self):
        # Vector marker centers from page 13; extraction tolerance: 2 cm.
        times = [1, 3, 53, 55]
        reference = [.4519980272106222, .5413919724425984,
                      18.662055785243382, 21.500752318605482]
        p = Parameters(central_probability=.96)
        np.testing.assert_allclose(reach_km(times, p), reference, rtol=0, atol=2e-5)

    def test_central_probability_of_rescaled_normal(self):
        p = Parameters()
        self.assertEqual(CENTRAL_PROBABILITY, .96)
        self.assertEqual(p.normal_quantile, NormalDist().inv_cdf(.98))
        self.assertAlmostEqual(p.normal_quantile, 2.053748910631822, places=14)
        for t in [1, 10, 54, 55]:
            sigma = p.reference_length_km * math.sqrt(
                p.gamma_per_week / p.beta_per_week * math.expm1(2*p.beta_per_week*t)
            ) * math.exp(-p.alpha*(t/p.generation_time_weeks-1))
            prob = math.erf(float(reach_km(t, p))/(math.sqrt(2)*sigma))
            self.assertAlmostEqual(float(reach_km(t, p))/sigma, p.normal_quantile, places=13)
            self.assertAlmostEqual(prob, CENTRAL_PROBABILITY, places=13)

    def test_two_sd_only_rescales_96_percent_reach(self):
        times = [1, 3, 10, 54, 55]
        previous = reach_km(times, Parameters(central_probability=.96))
        p2sd = Parameters(central_probability=TWO_SD_PROBABILITY)
        self.assertEqual(SPATIAL_STANDARD_DEVIATIONS, 2.0)
        self.assertEqual(TWO_SD_PROBABILITY, math.erf(2/math.sqrt(2)))
        self.assertEqual(p2sd.normal_quantile, 2.0)
        factor = 2/NormalDist().inv_cdf(.98)
        np.testing.assert_allclose(reach_km(times, p2sd), previous*factor, rtol=2e-15)
        self.assertAlmostEqual(float(reach_km(54, p2sd)), 19.506929847138, places=10)
        self.assertAlmostEqual(float(reach_km(54)), 20.0311679616657, places=9)
        self.assertEqual(Parameters().alpha, 3.180)

    def test_labels_and_suffixes_distinguish_percentiles(self):
        self.assertEqual(reach_suffix(CENTRAL_PROBABILITY), "p96")
        self.assertEqual(reach_label(CENTRAL_PROBABILITY), "96% reach distance (km)")
        self.assertEqual(reach_suffix(TWO_SD_PROBABILITY), "2sd")
        self.assertIn("2", reach_label(TWO_SD_PROBABILITY))
        self.assertEqual(reach_suffix(.99), "p99")
        self.assertIn("99%", reach_label(.99))
        self.assertEqual(reach_suffix(.96), "p96")

    def test_origin(self):
        self.assertEqual(float(reach_km(0)), 0)

    def test_linear_scaling(self):
        p = Parameters(reference_length_km=2*Parameters().reference_length_km)
        np.testing.assert_allclose(reach_km([1, 54], p), 2*reach_km([1, 54]))

    def test_invalid_inputs(self):
        for t in [-1, float("nan"), float("inf")]:
            with self.assertRaises(ValueError):
                reach_km(t)
        for kwargs in [dict(central_probability=1), dict(reference_length_km=0),
                       dict(reference_generation_time_days=10), dict(alpha=-1)]:
            with self.assertRaises(ValueError):
                Parameters(**kwargs)

    def test_error_messages_are_in_english(self):
        with self.assertRaisesRegex(ValueError, "central probability"):
            Parameters(central_probability=1)
        with self.assertRaisesRegex(ValueError, "Times must be finite and nonnegative"):
            reach_km(-1)

    def test_pdf_csv_json_export_without_legends(self):
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot  # Initialize before instrumenting Figure.text.
        with tempfile.TemporaryDirectory(prefix="figure1_ou_test_") as tmp:
            with patch("matplotlib.figure.Figure.legend", side_effect=AssertionError("No external legend")), \
                 patch("matplotlib.figure.Figure.text", side_effect=AssertionError("No external annotation")), \
                 patch("matplotlib.pyplot.close", side_effect=matplotlib.pyplot.close) as close_plot:
                files = generate_figure(Path(tmp))
            figure = close_plot.call_args.args[0]
            self.assertEqual(figure.axes[0].get_ylabel(), "Modulated spatial reach (km)")
            self.assertEqual(figure.axes[0].get_xlabel(), "Elapsed time (weeks)")
            self.assertEqual(figure.axes[0].xaxis.label.get_fontsize(), 18)
            self.assertEqual(figure.axes[0].yaxis.label.get_fontsize(), 18)
            for tick in figure.axes[0].get_xticklabels() + figure.axes[0].get_yticklabels():
                self.assertEqual(tick.get_fontsize(), 10)
            self.assertEqual({p.suffix for p in files}, {".pdf", ".csv", ".json"})
            self.assertTrue(next(p for p in files if p.suffix == ".pdf").read_bytes().startswith(b"%PDF-"))
            self.assertFalse(list(Path(tmp).glob("*.jpg")))
            self.assertTrue(all(p.stat().st_size > 0 for p in files))
            self.assertTrue(all(p.stem == "figure_1_bangkok_p96" for p in files))
            data = json.loads((Path(tmp)/"figure_1_bangkok_p96.json").read_text(encoding="utf-8"))
            self.assertEqual(data["colors"]["points"], "#0000FF")
            self.assertEqual(len(data["plot_weeks"]), 28)
            self.assertEqual(data["reach_multiplier_sd"], NormalDist().inv_cdf(.98))
            self.assertEqual(data["parameters"]["central_probability"], CENTRAL_PROBABILITY)
            with (Path(tmp)/"figure_1_bangkok_p96.csv").open(encoding="utf-8", newline="") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 29)
            self.assertEqual(set(rows[0]), {"time_weeks", "reach_km", "plotted"})
            self.assertEqual(next(r for r in rows if r["time_weeks"] == "54")
                             ["plotted"], "0")



class TestStandalonePackage(unittest.TestCase):
    def test_cli_from_copied_package_and_different_working_directory(self):
        """Run only this package's files, without the project's PYTHONPATH."""
        import os
        import shutil
        import subprocess
        import sys

        root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(prefix="ou_standalone_package_") as tmp:
            package = Path(tmp) / "package with spaces"
            working_dir = Path(tmp) / "other_working_directory"
            working_dir.mkdir()
            for name in ["generate_figure_1_bangkok.py"]:
                destination = package / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(root / name, destination)
            environment = os.environ.copy()
            environment.pop("PYTHONPATH", None)
            environment["MPLBACKEND"] = "Agg"
            run = subprocess.run(
                [sys.executable, "-E", "-B", "-X", "utf8",
                 str(package / "generate_figure_1_bangkok.py")],
                cwd=working_dir, env=environment, capture_output=True,
                text=True, encoding="utf-8", timeout=90,
            )
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            help_run = subprocess.run(
                [sys.executable, "-E", "-B", "-X", "utf8",
                 str(package / "generate_figure_1_bangkok.py"), "--help"],
                cwd=working_dir, env=environment, capture_output=True,
                text=True, encoding="utf-8", timeout=90,
            )
            self.assertEqual(help_run.returncode, 0, help_run.stderr)
            self.assertIn("Figure 1", help_run.stdout)
            self.assertNotIn("Figura ", help_run.stdout)
            output = package / "results"
            self.assertEqual(
                {p.name for p in output.iterdir()},
                {"figure_1_bangkok_p96.pdf", "figure_1_bangkok_p96.csv", "figure_1_bangkok_p96.json"},
            )
            self.assertFalse(list(working_dir.iterdir()))
            self.assertTrue((output / "figure_1_bangkok_p96.pdf").read_bytes().startswith(b"%PDF-"))
            with (root / "validation" / "numerical_reference_p96.csv").open(
                encoding="utf-8", newline=""
            ) as f:
                expected = [
                    {LEGACY_CSV_COLUMNS.get(key, key): value for key, value in row.items()}
                    for row in csv.DictReader(f)
                ]
            with (output / "figure_1_bangkok_p96.csv").open(
                encoding="utf-8", newline=""
            ) as f:
                actual = list(csv.DictReader(f))
            self.assertEqual(len(actual), len(expected))
            for current, previous in zip(actual, expected):
                self.assertEqual(set(current), set(previous))
                for key in current:
                    self.assertAlmostEqual(float(current[key]), float(previous[key]), places=11)

if __name__ == "__main__":
    unittest.main()
