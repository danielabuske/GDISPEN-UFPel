"""Tests for Figure 2; no original PDF or internet access is required."""
import csv
import hashlib
import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from statistics import NormalDist

import numpy as np
from ou_model import Parameters, reach_km, TWO_SD_PROBABILITY
from generate_figure_2_poa import (
    CENTRAL_PROBABILITY,
    MEAN_BETA_PER_WEEK, SD_BETA_PER_WEEK, TRUNCATION_CDF,
    lognormal_parameters, beta_quantile, reach_for_beta,
    calculate_boxplots, read_references, generate_figure,
)

ROOT = Path(__file__).resolve().parent


# Accept legacy headers while comparing the archived numerical reference values.
LEGACY_CSV_COLUMNS = {
    "semana": "week",
}

class TestFigure2(unittest.TestCase):
    def test_current_default_is_96_percent(self):
        self.assertEqual(CENTRAL_PROBABILITY, .96)
        self.assertEqual(CENTRAL_PROBABILITY, Parameters().central_probability)

    def test_dependencies_are_local_copies(self):
        import ou_model
        import poa_model
        self.assertEqual(Path(ou_model.__file__).resolve().parent, ROOT)
        self.assertEqual(Path(poa_model.__file__).resolve().parent, ROOT)
        self.assertEqual(Parameters, poa_model.Parameters)

    def test_lognormal_mean_and_sd(self):
        mu, sigma = lognormal_parameters()
        mean = math.exp(mu+sigma*sigma/2)
        sd = math.sqrt(math.expm1(sigma*sigma)*math.exp(2*mu+sigma*sigma))
        self.assertAlmostEqual(mean, MEAN_BETA_PER_WEEK, places=13)
        self.assertAlmostEqual(sd, SD_BETA_PER_WEEK, places=13)

    def test_truncation_bounds(self):
        np.testing.assert_allclose(beta_quantile(TRUNCATION_CDF), [1.255346, 1.377088], atol=1e-6)
        self.assertGreater(beta_quantile(.4), 1.241)

    def test_formula_matches_figure1(self):
        t = np.array([0, 1, 10, 20, 54])
        for probability in (CENTRAL_PROBABILITY, TWO_SD_PROBABILITY, .99):
            p = Parameters(central_probability=probability)
            np.testing.assert_allclose(
                reach_for_beta(t, p.beta_per_week, probability), reach_km(t, p)
            )

    def test_reproducibility_and_order(self):
        a = calculate_boxplots(n=1000, seed=123)
        b = calculate_boxplots(n=1000, seed=123)
        self.assertEqual(a, b)
        self.assertEqual(len(a), 20)
        for row in a:
            values = [row[k] for k in ["whislo", "q1", "med", "q3", "whishi"]]
            self.assertEqual(values, sorted(values))
            self.assertGreater(values[0], 0)

    def test_96_percent_only_rescales_99_percent_and_two_sd_boxplots(self):
        old_stats = calculate_boxplots(.99)
        current_stats = calculate_boxplots()
        factor = NormalDist().inv_cdf(.98)/NormalDist().inv_cdf(.995)
        for old, current in zip(old_stats, current_stats):
            self.assertEqual(old["week"], current["week"])
            for key in ("whislo", "q1", "med", "q3", "whishi"):
                self.assertAlmostEqual(current[key], old[key]*factor, places=12)
        self.assertAlmostEqual(current_stats[-1]["med"], 2.568088263971, places=10)
        legacy_2sd = calculate_boxplots(TWO_SD_PROBABILITY)
        for legacy, current in zip(legacy_2sd, current_stats):
            for key in ("whislo", "q1", "med", "q3", "whishi"):
                self.assertAlmostEqual(
                    current[key], legacy[key]*NormalDist().inv_cdf(.98)/2, places=12
                )

    def test_separate_reference_series(self):
        refs = read_references(ROOT/"figure_2_data"/"red_references.csv")
        self.assertEqual(len(refs["mean_diameter"]), 20)
        self.assertGreater(len(refs["upper_ci95"]), 2)
        self.assertGreater(len(refs["lower_ci95"]), 2)
        self.assertFalse(np.allclose(refs["mean_diameter"][:, 0], np.arange(1, 21)))

    def test_english_reference_csv_matches_legacy_data(self):
        expected = read_references(ROOT/"figure_2_data"/"red_references.csv")
        with tempfile.TemporaryDirectory(prefix="figure2_english_csv_") as tmp:
            path = Path(tmp) / "references.csv"
            with path.open("w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["series", "time_weeks", "distance_km"])
                for series, points in expected.items():
                    writer.writerows((series, time, distance) for time, distance in points)
            actual = read_references(path)
            self.assertEqual(set(actual), set(expected))
            for series in expected:
                np.testing.assert_array_equal(actual[series], expected[series])
            with path.open("a", encoding="utf-8", newline="") as f:
                csv.writer(f).writerow(["unknown", 1, 1])
            with self.assertRaisesRegex(ValueError, "Unknown series"):
                read_references(path)

    def test_error_messages_are_in_english(self):
        with self.assertRaisesRegex(ValueError, "mean and standard deviation"):
            lognormal_parameters(mean=0)
        with self.assertRaisesRegex(ValueError, "at least 100 samples per week"):
            calculate_boxplots(n=0)

    def test_invalid_inputs(self):
        for p in [0, 1, float("nan")]:
            with self.assertRaises(ValueError):
                reach_for_beta(1, 1.3, p)
        with self.assertRaises(ValueError):
            calculate_boxplots(.99, n=0)

    def test_temporary_export(self):
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot  # Initialize before instrumenting Figure.text.
        with tempfile.TemporaryDirectory(prefix="figure2_ou_test_") as tmp:
            with patch("matplotlib.figure.Figure.legend", side_effect=AssertionError("No external legend")), \
                 patch("matplotlib.figure.Figure.text", side_effect=AssertionError("No external annotation")), \
                 patch("matplotlib.pyplot.close", side_effect=matplotlib.pyplot.close) as close_plot:
                files = generate_figure(CENTRAL_PROBABILITY, Path(tmp), n=1000, seed=123)
            figure = close_plot.call_args.args[0]
            self.assertEqual(figure.axes[0].get_ylabel(), "Modulated spatial reach (km)")
            self.assertEqual(figure.axes[0].get_xlabel(), "Cluster duration (weeks)")
            self.assertEqual(figure.axes[0].xaxis.label.get_fontsize(), 18)
            self.assertEqual(figure.axes[0].yaxis.label.get_fontsize(), 18)
            for tick in figure.axes[0].get_xticklabels() + figure.axes[0].get_yticklabels():
                self.assertEqual(tick.get_fontsize(), 10)
            self.assertEqual({p.suffix for p in files}, {".pdf", ".csv", ".json"})
            self.assertTrue(next(p for p in files if p.suffix == ".pdf").read_bytes().startswith(b"%PDF-"))
            self.assertFalse(list(Path(tmp).glob("*.jpg")))
            self.assertTrue(all(p.stat().st_size > 0 for p in files))
            data = json.loads(next(p for p in files if p.suffix == ".json").read_text(encoding="utf-8"))
            self.assertTrue(all(p.stem == "figure_2_poa_p96" for p in files))
            self.assertEqual(data["central_probability"], CENTRAL_PROBABILITY)
            self.assertEqual(data["reach_multiplier_sd"], NormalDist().inv_cdf(.98))
            self.assertEqual(data["seed"], 123)
            with next(p for p in files if p.suffix == ".csv").open(encoding="utf-8", newline="") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 20)
            self.assertEqual(set(rows[0]), {"week", "whislo", "q1", "med", "q3", "whishi"})



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
            for name in ["generate_figure_2_poa.py","ou_model.py","poa_model.py","figure_2_data/red_references.csv","figure_2_data/provenance.json"]:
                destination = package / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(root / name, destination)
            environment = os.environ.copy()
            environment.pop("PYTHONPATH", None)
            environment["MPLBACKEND"] = "Agg"
            run = subprocess.run(
                [sys.executable, "-E", "-B", "-X", "utf8",
                 str(package / "generate_figure_2_poa.py")],
                cwd=working_dir, env=environment, capture_output=True,
                text=True, encoding="utf-8", timeout=90,
            )
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            help_run = subprocess.run(
                [sys.executable, "-E", "-B", "-X", "utf8",
                 str(package / "generate_figure_2_poa.py"), "--help"],
                cwd=working_dir, env=environment, capture_output=True,
                text=True, encoding="utf-8", timeout=90,
            )
            self.assertEqual(help_run.returncode, 0, help_run.stderr)
            self.assertIn("Figure 2", help_run.stdout)
            self.assertNotIn("Figura ", help_run.stdout)
            output = package / "results"
            self.assertEqual(
                {p.name for p in output.iterdir()},
                {"figure_2_poa_p96.pdf", "figure_2_poa_p96.csv", "figure_2_poa_p96.json"},
            )
            self.assertFalse(list(working_dir.iterdir()))
            self.assertTrue((output / "figure_2_poa_p96.pdf").read_bytes().startswith(b"%PDF-"))
            with (root / "validation" / "numerical_reference_p96.csv").open(
                encoding="utf-8", newline=""
            ) as f:
                expected = [
                    {LEGACY_CSV_COLUMNS.get(key, key): value for key, value in row.items()}
                    for row in csv.DictReader(f)
                ]
            with (output / "figure_2_poa_p96.csv").open(
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
