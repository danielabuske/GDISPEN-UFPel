#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figure 3: current Porto Alegre model from 1 to 4.5 weeks, without red references.

Run directly to generate Figure 3 only (vector PDF, CSV, and JSON).
The plot includes axis labels only, without legends or external annotations.
Uses local copies of the model functions; no dependency on the Figure 2 folder.
"""
from __future__ import annotations

# Script names, data paths, and generated filenames use English.

# APPEARANCE: axis-label font size in points (tick labels are unchanged).
AXIS_LABEL_FONT_SIZE = 18

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import poa_model as poa

# FIGURE 3 CONFIGURATION: 96% central interval and current Porto Alegre parameters.
WEEKS = (1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5)
CENTRAL_PROBABILITY = poa.CENTRAL_PROBABILITY
SAMPLES_PER_WEEK = poa.SAMPLES_PER_WEEK
RANDOM_SEED = poa.RANDOM_SEED


def calculate_short_boxplots(probability=CENTRAL_PROBABILITY,
                           n=SAMPLES_PER_WEEK, seed=RANDOM_SEED):
    if not isinstance(n, int) or n < 100:
        raise ValueError("Use at least 100 samples per week.")
    rng = np.random.default_rng(seed)
    # Reconstruct the exact random stream of Figure 2 without reading its outputs.
    u_base = rng.uniform(*poa.TRUNCATION_CDF, size=(len(poa.WEEKS), n))
    beta_base = poa.beta_quantile(u_base)
    index = {float(t): i for i, t in enumerate(poa.WEEKS)}
    beta_rows = []
    for t in WEEKS:
        if t in index:
            beta_rows.append(beta_base[index[t]])
        else:
            # Draw new samples only for half-weeks, after consuming the original stream.
            beta_rows.append(poa.beta_quantile(rng.uniform(*poa.TRUNCATION_CDF, size=n)))
    values = poa.reach_for_beta(
        np.asarray(WEEKS)[:, None], np.asarray(beta_rows), probability
    )
    levels = [poa.WHISKER_PERCENTILES[0]/100, .25, .5, .75, poa.WHISKER_PERCENTILES[1]/100]
    quantiles = np.quantile(values, levels, axis=1).T
    return [dict(week=t, whislo=float(q[0]), q1=float(q[1]), med=float(q[2]),
                 q3=float(q[3]), whishi=float(q[4]), fliers=[])
            for t, q in zip(WEEKS, quantiles)]


def generate_figure(destination, probability=CENTRAL_PROBABILITY,
          n=SAMPLES_PER_WEEK, seed=RANDOM_SEED):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    stats = calculate_short_boxplots(probability, n, seed)
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    stem = destination / ("figure_3_poa_4_5_weeks_" + poa.reach_suffix(probability))
    with plt.rc_context({"font.family": "DejaVu Sans", "font.size": 10}):
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bxp(stats, positions=WEEKS, widths=.24, patch_artist=True, showfliers=False,
               boxprops={"facecolor": poa.BOX_COLOR, "edgecolor": "black"},
               medianprops={"color": poa.MEDIAN_COLOR},
               whiskerprops={"color": "black"}, capprops={"color": "black"})
        ax.set_xlabel("Cluster duration (weeks)", fontsize=AXIS_LABEL_FONT_SIZE)
        ax.set_ylabel("Modulated spatial reach (km)", fontsize=AXIS_LABEL_FONT_SIZE)
        ax.set_xticks(WEEKS, [f"{t:.1f}" for t in WEEKS])
        ax.set_xlim(min(WEEKS)-.3, max(WEEKS)+.3)
        # Use automatic vertical limits to avoid clipping current results to the old axis.
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

    root = Path(__file__).resolve().parent
    p = poa.Parameters()
    mu, sigma = poa.lognormal_parameters()
    metadata = {
        "figure": 3,
        "status": "Short time window of the current Porto Alegre model; no data from the old plot.",
        "weeks": WEEKS,
        "central_probability": probability,
        "reach_multiplier_sd": poa.central_quantile(probability),
        "samples_per_week": n,
        "seed": seed,
        "beta_mean": poa.MEAN_BETA_PER_WEEK,
        "beta_sd": poa.SD_BETA_PER_WEEK,
        "mu_log": mu, "sigma_log": sigma,
        "truncation_cdf": poa.TRUNCATION_CDF,
        "calculated_beta_bounds": poa.beta_quantile(poa.TRUNCATION_CDF).tolist(),
        "whisker_percentiles": poa.WHISKER_PERCENTILES,
        "spatial_parameters": {
            "L_km": p.reference_length_km, "alpha": p.alpha,
            "gamma_per_week": p.gamma_per_week, "Tg_weeks": p.generation_time_weeks,
        },
        "colors": {"boxes": poa.BOX_COLOR, "medians": poa.MEDIAN_COLOR, "whiskers": "#000000"},
        "local_dependencies_sha256": {
            name: hashlib.sha256((root/name).read_bytes()).hexdigest()
            for name in ("ou_model.py", "poa_model.py")
        },
        "notes": [
            "The default selects a central 96% OU interval before modulation, not an ensemble percentile.",
            "Integer weeks reuse the same draws as Figure 2 without reading output CSV files.",
            "Half-weeks use new draws after consuming the original Figure 2 stream.",
            "Draws represent time-specific marginal distributions, not individual trajectories.",
            "No PDFs, Guzzetta references, or published boxplots are read.",
            "Modulated 1D reach at each time, not a monthly expansion speed.",
            "Intervals represent heterogeneity in beta, not confidence intervals.",
            "Tg retains its baseline reference of 18.2 days and alpha remains 3.180; no refitting.",
        ],
    }
    json_path = stem.with_suffix(".json")
    json_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    return [pdf, csv_path, json_path]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path,
                        default=Path(__file__).resolve().parent/"results")
    parser.add_argument("--central-probability", type=float, default=CENTRAL_PROBABILITY,
                        help="Alternative central probability before modulation; default: 0.96.")
    args = parser.parse_args()
    for path in generate_figure(args.output_dir, args.central_probability):
        print(path.resolve())


if __name__ == "__main__":
    main()
