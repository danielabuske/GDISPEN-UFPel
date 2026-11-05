"""Standalone local OU core using the adopted 96% central-interval convention.

No imports from other figures, external data reads, or parameter recalibration.
"""
from __future__ import annotations

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
