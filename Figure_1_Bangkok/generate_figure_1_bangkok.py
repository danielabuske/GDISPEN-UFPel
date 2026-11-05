#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figure 1: analytical OU model with a default 96% central-interval convention.

Run directly to export a vector PDF, CSV, and JSON to the existing output folder.
The plot includes axis labels only, without legends or external annotations.
No REBASE11 dependency or parameter refitting is required.
"""
from __future__ import annotations

# Script names, data paths, and generated filenames use English.

# APPEARANCE: axis-label font size in points (tick labels are unchanged).
AXIS_LABEL_FONT_SIZE = 18

import math

# CONFIGURATION: time in weeks and distance in kilometers.
CENTRAL_PROBABILITY = 0.96
# The default matches the reference used to calibrate alpha in Bangkok.
# The constants below retain the historical two-standard-deviation option.
SPATIAL_STANDARD_DEVIATIONS = 2.0
TWO_SD_PROBABILITY = math.erf(SPATIAL_STANDARD_DEVIATIONS / math.sqrt(2.0))
REFERENCE_LENGTH_KM = 8.94e-3
ALPHA = 3.180
REFERENCE_GENERATION_TIME_DAYS = 18.2
VECTOR_LATENT_PERIOD_DAYS = 6.1
HUMAN_LATENT_PERIOD_DAYS = 4.6
HUMAN_REMOVAL_TIME_DAYS = 5.5
PLOT_WEEKS = tuple(range(1, 56, 2))  # Original: 1, 3, ..., 55.
REFERENCE_WEEK = 54.0
POINT_COLOR = "#0000FF"
MARKER_LINE_COLOR = "#FF7F0E"
GRID_COLOR = "#B0B0B0"

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import NormalDist

import numpy as np


def central_quantile(probability: float) -> float:
    """Spatial multiplier, not the standard deviation of beta or of the ensemble."""
    if not math.isfinite(probability) or not 0 < probability < 1:
        raise ValueError("The central probability must be strictly between zero and one.")
    if probability == TWO_SD_PROBABILITY:
        return SPATIAL_STANDARD_DEVIATIONS
    return NormalDist().inv_cdf((1.0 + probability) / 2.0)


def reach_label(probability: float) -> str:
    if probability == TWO_SD_PROBABILITY:
        return f"{SPATIAL_STANDARD_DEVIATIONS:g}σ reach distance (km)"
    return f"{100*probability:g}% reach distance (km)"


def reach_suffix(probability: float) -> str:
    # Use "sd" for the standard-deviation convention in English filenames.
    if probability == TWO_SD_PROBABILITY:
        return f"{SPATIAL_STANDARD_DEVIATIONS:g}sd".replace(".", "_")
    return "p" + f"{100*probability:g}".replace(".", "_")


@dataclass(frozen=True)
class Parameters:
    central_probability: float = CENTRAL_PROBABILITY
    reference_length_km: float = REFERENCE_LENGTH_KM
    alpha: float = ALPHA
    reference_generation_time_days: float = REFERENCE_GENERATION_TIME_DAYS
    vector_latent_period_days: float = VECTOR_LATENT_PERIOD_DAYS
    human_latent_period_days: float = HUMAN_LATENT_PERIOD_DAYS
    human_removal_time_days: float = HUMAN_REMOVAL_TIME_DAYS

    def __post_init__(self) -> None:
        if not all(math.isfinite(v) for v in asdict(self).values()):
            raise ValueError("All parameters must be finite.")
        if not 0 < self.central_probability < 1:
            raise ValueError("The central probability must be strictly between 0 and 1.")
        if min(self.reference_length_km, self.human_removal_time_days) <= 0:
            raise ValueError("L and the removal timescale must be positive.")
        if min(self.alpha, self.vector_latent_period_days, self.human_latent_period_days) < 0:
            raise ValueError("Alpha and the latent periods must be nonnegative.")
        if self.reference_generation_time_days <= self.vector_latent_period_days + self.human_latent_period_days:
            raise ValueError("Tg must exceed the sum of the latent periods.")

    @property
    def beta_per_week(self) -> float:
        # Use full precision, not the rounded value in Table 1.
        days = self.reference_generation_time_days - (self.vector_latent_period_days + self.human_latent_period_days)
        return 7.0 * 2.0 * math.log(2.0) / days

    @property
    def gamma_per_week(self) -> float:
        return 7.0 / self.human_removal_time_days

    @property
    def generation_time_weeks(self) -> float:
        return self.reference_generation_time_days / 7.0

    @property
    def normal_quantile(self) -> float:
        return central_quantile(self.central_probability)


def reach_km(time_weeks, parameters: Parameters | None = None) -> np.ndarray:
    """Modulated 1D spatial reach derived from a central OU interval.

    sigma_OU(t)^2 = L^2 * gamma/beta * (exp(2*beta*t) - 1).
    r(t) = z * sigma_OU(t) * exp[-alpha * (t/Tg - 1)].
    Phenomenological modulation applies to the envelope, not to the OU process.
    The central probability refers to the OU interval before modulation;
    the modulated reach need not retain that probability under the OU density.
    This is neither a 2D radial CDF nor a summary of cumulative cases.
    """
    p = parameters or Parameters()
    t = np.asarray(time_weeks, dtype=float)
    if np.any(~np.isfinite(t)) or np.any(t < 0):
        raise ValueError("Times must be finite and nonnegative.")
    beta = p.beta_per_week
    # Avoid computing exp(2*beta*t) separately; the result is exactly zero at t=0.
    exponent = (beta - p.alpha / p.generation_time_weeks) * t + p.alpha
    with np.errstate(over="raise", invalid="raise"):
        return (p.normal_quantile * p.reference_length_km
                * math.sqrt(p.gamma_per_week / beta)
                * np.exp(exponent) * np.sqrt(-np.expm1(-2.0 * beta * t)))


def generate_figure(output_dir: Path, parameters: Parameters | None = None) -> list[Path]:
    """Generate the plot and record the values and parameters used."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    p = parameters or Parameters()
    times = np.asarray(PLOT_WEEKS, dtype=float)
    reaches = reach_km(times, p)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = output_dir / ("figure_1_bangkok_" + reach_suffix(p.central_probability))
    with plt.rc_context({"font.family": "DejaVu Sans", "font.size": 10}):
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(times, reaches, linestyle="none", marker="o", markersize=6,
                markerfacecolor=POINT_COLOR, markeredgecolor=POINT_COLOR, zorder=3)
        # Visual elements from the original figure, NOT error bars or intervals.
        ax.hlines(reaches, times - 0.25, times + 0.25,
                  colors=MARKER_LINE_COLOR, linewidth=1, zorder=4)
        ax.set_xlabel("Elapsed time (weeks)", fontsize=AXIS_LABEL_FONT_SIZE)
        ax.set_ylabel("Modulated spatial reach (km)", fontsize=AXIS_LABEL_FONT_SIZE)
        ax.set_xticks(times)
        ax.set_xlim(0.5, 55.5)
        ax.set_axisbelow(True)
        ax.grid(True, linestyle="--", color=GRID_COLOR, alpha=0.5)
        fig.tight_layout()
        pdf = stem.with_suffix(".pdf")
        fig.savefig(pdf, facecolor="white")
        files = [pdf]
        plt.close(fig)

    csv_path = stem.with_suffix(".csv")
    with csv_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["time_weeks", "reach_km", "plotted"])
        for t in sorted(set(PLOT_WEEKS) | {REFERENCE_WEEK}):
            writer.writerow([f"{t:g}", f"{float(reach_km(t, p)):.12f}",
                             int(t in PLOT_WEEKS)])
    files.append(csv_path)
    metadata = {
        "source": "Metodo_OU_Area_de_Risco__versao_3_ (71).pdf",
        "source_pages": [6, 12, 13, 23],
        "method": "Analytical model with a spatial-reach convention; no refitting of dynamic parameters.",
        "definition": "Before modulation: P(|X(t)-x0| <= r_OU) = p for the symmetric 1D OU density.",
        "formula": "z*L*sqrt(gamma/beta)*exp((beta-alpha/Tg)*t+alpha)*sqrt(1-exp(-2*beta*t))",
        "parameters": asdict(p),
        "beta_per_week": p.beta_per_week,
        "gamma_per_week": p.gamma_per_week,
        "reference_generation_time_weeks": p.generation_time_weeks,
        "normal_quantile": p.normal_quantile,
        "reach_multiplier_sd": p.normal_quantile,
        "historical_calibration_reference": {"central_probability": 0.96, "adopted_alpha": ALPHA},
        "plot_weeks": list(PLOT_WEEKS),
        "text_reference_week": REFERENCE_WEEK,
        "reference_reach_km": float(reach_km(REFERENCE_WEEK, p)),
        "colors": {"points": POINT_COLOR, "marker_lines": MARKER_LINE_COLOR, "grid": GRID_COLOR},
        "notes": [
            "The default selects a central 96% interval of the 1D normal density before modulation.",
            "Changing the reach convention does not recalibrate alpha or change beta, L, gamma, or Tg.",
            "Agreement with the historical Bangkok points explicitly uses p=0.96.",
            "The original time grid ends at 55 weeks; the text refers to 54 weeks.",
            "Tg is the baseline value of 18.2 days, not the value after attenuation.",
            "Orange marks preserve the original appearance; they do not represent uncertainty.",
            "Do not interpret 1D reach as a two-dimensional radial quantile.",
        ],
    }
    json_path = stem.with_suffix(".json")
    json_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    files.append(json_path)
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path,
                        default=Path(__file__).resolve().parent / "results")
    parser.add_argument("--pdf", action="store_true",
                        help="Compatibility option: vector PDF is already the default format.")
    args = parser.parse_args()
    p = Parameters()
    for file in generate_figure(args.output_dir, p):
        print(file.resolve())
    print(f"beta = {p.beta_per_week:.12f} / week")
    print(f"Modulated reach using the {100*p.central_probability:g}% central interval at 54 weeks: "
          f"{float(reach_km(54, p)):.6f} km")
    print("Original plot time grid retained: 1, 3, ..., 55 weeks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
