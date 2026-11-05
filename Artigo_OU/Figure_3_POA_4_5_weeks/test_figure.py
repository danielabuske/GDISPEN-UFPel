"""Check Figure 3 and its consistency with the integer weeks of Figure 2."""
import csv
import json
import math
from statistics import NormalDist
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import poa_model as poa
import generate_figure_3_poa_4_5_weeks as fig3


# Accept legacy headers while comparing the archived numerical reference values.
LEGACY_CSV_COLUMNS = {
    "semana": "week",
}

class TestFigure3(unittest.TestCase):
    def test_time_grid_and_configuration(self):
        self.assertEqual(fig3.WEEKS, (1., 1.5, 2., 2.5, 3., 3.5, 4., 4.5))
        self.assertEqual(fig3.CENTRAL_PROBABILITY, .96)
        self.assertEqual(fig3.CENTRAL_PROBABILITY, poa.CENTRAL_PROBABILITY)
        self.assertEqual(fig3.RANDOM_SEED, poa.RANDOM_SEED)

    def test_integer_weeks_exactly_match_figure2(self):
        full = {float(row["week"]): row for row in poa.calculate_boxplots()}
        short = fig3.calculate_short_boxplots()
        for row in short:
            if row["week"].is_integer():
                self.assertEqual(row, full[row["week"]])

    def test_reproducibility(self):
        a = fig3.calculate_short_boxplots(n=1000, seed=123)
        b = fig3.calculate_short_boxplots(n=1000, seed=123)
        self.assertEqual(a, b)

    def test_quantile_order_and_endpoint(self):
        rows = fig3.calculate_short_boxplots()
        self.assertEqual(len(rows), 8)
        for row in rows:
            q = [row[k] for k in ("whislo", "q1", "med", "q3", "whishi")]
            self.assertEqual(q, sorted(q))
            self.assertGreater(q[0], 0)
        self.assertEqual(rows[-1]["week"], 4.5)
        self.assertAlmostEqual(rows[-1]["med"], .649063329270, places=10)
        # The explicit legacy mode remains available without recalibration.
        old_stats = fig3.calculate_short_boxplots(probability=.99)
        self.assertAlmostEqual(old_stats[-1]["med"], .8140607329, places=8)
        legacy_2sd = fig3.calculate_short_boxplots(probability=math.erf(2/math.sqrt(2)))
        self.assertAlmostEqual(legacy_2sd[-1]["med"], .632076614536, places=10)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            fig3.calculate_short_boxplots(n=0)
        with self.assertRaises(ValueError):
            fig3.calculate_short_boxplots(probability=1, n=100)

    def test_error_messages_are_in_english(self):
        with self.assertRaisesRegex(ValueError, "at least 100 samples per week"):
            fig3.calculate_short_boxplots(n=0)
        with self.assertRaisesRegex(ValueError, "central probability"):
            fig3.calculate_short_boxplots(probability=1, n=100)

    def test_export_without_external_references(self):
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot  # Initialize before instrumenting Figure.text.
        with tempfile.TemporaryDirectory(prefix="figure3_ou_test_") as tmp:
            self.assertFalse(hasattr(poa, "read_references"))
            with patch("matplotlib.figure.Figure.legend", side_effect=AssertionError("No external legend")), \
                 patch("matplotlib.figure.Figure.text", side_effect=AssertionError("No external annotation")), \
                 patch("matplotlib.pyplot.close", side_effect=matplotlib.pyplot.close) as close_plot:
                paths = fig3.generate_figure(tmp, n=1000, seed=123)
            figure = close_plot.call_args.args[0]
            self.assertEqual(figure.axes[0].get_ylabel(), "Modulated spatial reach (km)")
            self.assertEqual(figure.axes[0].get_xlabel(), "Cluster duration (weeks)")
            self.assertEqual(figure.axes[0].xaxis.label.get_fontsize(), 18)
            self.assertEqual(figure.axes[0].yaxis.label.get_fontsize(), 18)
            for tick in figure.axes[0].get_xticklabels() + figure.axes[0].get_yticklabels():
                self.assertEqual(tick.get_fontsize(), 10)
            self.assertEqual({p.suffix for p in paths}, {".pdf", ".csv", ".json"})
            self.assertTrue(next(p for p in paths if p.suffix == ".pdf").read_bytes().startswith(b"%PDF-"))
            self.assertFalse(list(Path(tmp).glob("*.jpg")))
            self.assertTrue(all(p.stat().st_size > 0 for p in paths))
            data = json.loads(next(p for p in paths if p.suffix == ".json").read_text(encoding="utf-8"))
            self.assertEqual(data["weeks"][-1], 4.5)
            self.assertEqual(data["spatial_parameters"]["alpha"], 3.180)
            self.assertEqual(data["central_probability"], fig3.CENTRAL_PROBABILITY)
            self.assertEqual(data["reach_multiplier_sd"], NormalDist().inv_cdf(.98))
            self.assertTrue(all(p.stem == "figure_3_poa_4_5_weeks_p96" for p in paths))
            with next(p for p in paths if p.suffix == ".csv").open(encoding="utf-8", newline="") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 8)
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
            for name in ["generate_figure_3_poa_4_5_weeks.py","ou_model.py","poa_model.py"]:
                destination = package / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(root / name, destination)
            environment = os.environ.copy()
            environment.pop("PYTHONPATH", None)
            environment["MPLBACKEND"] = "Agg"
            run = subprocess.run(
                [sys.executable, "-E", "-B", "-X", "utf8",
                 str(package / "generate_figure_3_poa_4_5_weeks.py")],
                cwd=working_dir, env=environment, capture_output=True,
                text=True, encoding="utf-8", timeout=90,
            )
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            help_run = subprocess.run(
                [sys.executable, "-E", "-B", "-X", "utf8",
                 str(package / "generate_figure_3_poa_4_5_weeks.py"), "--help"],
                cwd=working_dir, env=environment, capture_output=True,
                text=True, encoding="utf-8", timeout=90,
            )
            self.assertEqual(help_run.returncode, 0, help_run.stderr)
            self.assertIn("Figure 3", help_run.stdout)
            self.assertNotIn("Figura ", help_run.stdout)
            output = package / "results"
            self.assertEqual(
                {p.name for p in output.iterdir()},
                {"figure_3_poa_4_5_weeks_p96.pdf", "figure_3_poa_4_5_weeks_p96.csv", "figure_3_poa_4_5_weeks_p96.json"},
            )
            self.assertFalse(list(working_dir.iterdir()))
            self.assertTrue((output / "figure_3_poa_4_5_weeks_p96.pdf").read_bytes().startswith(b"%PDF-"))
            with (root / "validation" / "numerical_reference_p96.csv").open(
                encoding="utf-8", newline=""
            ) as f:
                expected = [
                    {LEGACY_CSV_COLUMNS.get(key, key): value for key, value in row.items()}
                    for row in csv.DictReader(f)
                ]
            with (output / "figure_3_poa_4_5_weeks_p96.csv").open(
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
