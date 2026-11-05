#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figure 2: recalculated model and external references from Guzzetta.

Run: python generate_figure_2_poa.py (default: 96% central interval before modulation).
Export a vector PDF, CSV, and JSON; the plot includes axis labels only.
No copying of old boxplots, parameter refitting, or direct validation metrics
between OU-derived reach and maximum observed cluster diameter.
"""
from __future__ import annotations

# Script names, data paths, and generated filenames use English.

# APPEARANCE: axis-label font size in points (tick labels are unchanged).
AXIS_LABEL_FONT_SIZE = 18

# Local dependencies: this folder can be copied and run independently.
from ou_model import (
    Parameters, CENTRAL_PROBABILITY, central_quantile, reach_suffix,
)
from poa_model import (
    MEAN_BETA_PER_WEEK, SD_BETA_PER_WEEK, TRUNCATION_CDF,
    WHISKER_PERCENTILES, SAMPLES_PER_WEEK, RANDOM_SEED, WEEKS,
    BOX_COLOR, MEDIAN_COLOR, REFERENCE_COLOR,
    lognormal_parameters, beta_quantile, reach_for_beta, calculate_boxplots,
)
import argparse
import csv
import json
import math
from pathlib import Path
import numpy as np

def read_references(path):
    """Read observed-cluster references, accepting legacy or English CSV labels."""
    # Translate only at the input boundary; keep the supplied data file unchanged.
    column_names = {
        "serie": "series",
        "tempo_semanas": "time_weeks",
        "distancia_km": "distance_km",
    }
    series_names = {
        "media_diametro": "mean_diameter",
        "ic95_superior": "upper_ci95",
        "ic95_inferior": "lower_ci95",
    }
    groups = {s: [] for s in ("mean_diameter", "upper_ci95", "lower_ci95")}
    with Path(path).open(encoding="utf-8", newline="") as f:
        for source_row in csv.DictReader(f):
            row = {column_names.get(key, key): value for key, value in source_row.items()}
            series = series_names.get(row["series"], row["series"])
            if series not in groups:
                raise ValueError("Unknown series in the reference CSV.")
            point = (float(row["time_weeks"]), float(row["distance_km"]))
            if not all(math.isfinite(x) and x >= 0 for x in point):
                raise ValueError("Invalid reference point.")
            groups[series].append(point)
    for series, points in groups.items():
        if not points or any(b[0] <= a[0] for a, b in zip(points, points[1:])):
            raise ValueError(f"Empty or unordered series: {series}")
    if len(groups["mean_diameter"]) != 20:
        raise ValueError("Expected 20 red reference points.")
    return {s: np.asarray(v) for s, v in groups.items()}


def generate_figure(probability, destination, references=None, n=SAMPLES_PER_WEEK, seed=RANDOM_SEED):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    root = Path(__file__).resolve().parent
    references = Path(references) if references else root/"figure_2_data"/"red_references.csv"
    refs = read_references(references)
    stats = calculate_boxplots(probability, n, seed)
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    stem = destination / ("figure_2_poa_" + reach_suffix(probability))
    with plt.rc_context({"font.family": "DejaVu Sans", "font.size": 10}):
        fig, ax = plt.subplots(figsize=(10, 7))
        ax.bxp(stats, positions=WEEKS, widths=.5, patch_artist=True, showfliers=False,
               boxprops={"facecolor": BOX_COLOR, "edgecolor": "black"},
               medianprops={"color": MEDIAN_COLOR},
               whiskerprops={"color": "black"}, capprops={"color": "black"})
        for series in ("lower_ci95", "upper_ci95"):
            xy = refs[series]
            ax.plot(xy[:, 0], xy[:, 1], color=REFERENCE_COLOR, linewidth=1.2)
        xy = refs["mean_diameter"]
        ax.scatter(xy[:, 0], xy[:, 1], s=36, color=REFERENCE_COLOR, zorder=4)
        ax.set_xlabel("Cluster duration (weeks)", fontsize=AXIS_LABEL_FONT_SIZE)
        ax.set_ylabel("Modulated spatial reach (km)", fontsize=AXIS_LABEL_FONT_SIZE)
        ax.set_xlim(0, 20.5)
        ax.set_xticks(WEEKS)
        ax.set_ylim(bottom=0)
        ax.set_axisbelow(True)
        ax.grid(True, linestyle="--", color="#B0B0B0", alpha=.5)
        fig.tight_layout()
        pdf = stem.with_suffix(".pdf")
        fig.savefig(pdf, facecolor="white")
        plt.close(fig)

    csv_path = stem.with_suffix(".csv")
    cols = ["week", "whislo", "q1", "med", "q3", "whishi"]
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(stats)
    mu, sigma = lognormal_parameters()
    p = Parameters()
    metadata = {
        "status": "Current version: boxplots are recalculated, not copied from the old manuscript.",
        "central_probability": probability, "samples_per_week": n, "seed": seed,
        "reach_multiplier_sd": central_quantile(probability),
        "beta_mean": MEAN_BETA_PER_WEEK, "beta_sd": SD_BETA_PER_WEEK,
        "mu_log": mu, "sigma_log": sigma,
        "truncation_cdf": TRUNCATION_CDF,
        "calculated_beta_bounds": beta_quantile(TRUNCATION_CDF).tolist(),
        "whisker_percentiles": WHISKER_PERCENTILES,
        "spatial_parameters": {"L_km": p.reference_length_km, "alpha": p.alpha,
                               "gamma_per_week": p.gamma_per_week, "Tg_weeks": p.generation_time_weeks},
        "reference_data": references.name,
        "notes": [
            "The default selects a central 96% OU interval before modulation, not an ensemble percentile.",
            "The axis names model reach; red references remain diameters of reconstructed observed clusters.",
            "The historical Bangkok calibration of alpha retains the 96% convention; no recalibration.",
            "Sample size and seed were specified for this implementation; the originals are unknown.",
            "Independent weekly draws represent marginal distributions, not trajectories.",
            "Boxes show P25-P75, medians P50, and whiskers P5-P95 of modeled heterogeneity.",
            "Whiskers are not 95% confidence intervals or the P25/P75 percentiles stated in the old caption.",
            "No factor of 0.8 was applied to imitate the published boxplots.",
            "References were extracted from the OU manuscript; Guzzetta's primary data were not recovered.",
            "No RMSE, MAE, or R2 is calculated: modulated 1D reach and maximum cluster diameter are not equivalent.",
        ],
    }
    json_path = stem.with_suffix(".json")
    json_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    return [pdf, csv_path, json_path]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--central-probability", type=float, default=CENTRAL_PROBABILITY,
                        help="Alternative central probability before modulation; default: 0.96.")
    parser.add_argument("--output-dir", type=Path,
                        default=Path(__file__).resolve().parent/"results")
    args = parser.parse_args()
    for path in generate_figure(args.central_probability, args.output_dir):
        print(path.resolve())


if __name__ == "__main__":
    main()
