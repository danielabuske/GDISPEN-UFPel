"""Local boxplot configuration and calculations; no reference data are read.

Time-specific marginal distributions, with variability in beta only.
"""
from __future__ import annotations

from ou_model import (
    Parameters, CENTRAL_PROBABILITY, central_quantile, reach_suffix, reach_label,
)

# CURRENT CONFIGURATION: recalculate, rather than copy the old manuscript boxplots.
# All other parameters of the prepared implementation are retained without refitting.
# Spatial convention shared with Figure 1: central 96% interval before modulation.
MEAN_BETA_PER_WEEK = 1.2939
SD_BETA_PER_WEEK = 0.1294
TRUNCATION_CDF = (0.40, 0.75)
WHISKER_PERCENTILES = (5.0, 95.0)  # Explicit definition for this implementation.
SAMPLES_PER_WEEK = 10000
RANDOM_SEED = 20261102  # Reproducibility seed for this implementation, not recovered from the original.
WEEKS = tuple(range(1, 21))
BOX_COLOR = "#ADD8E6"
MEDIAN_COLOR = "#FF7F0E"
REFERENCE_COLOR = "#FF0000"

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np
from scipy.special import ndtri


def lognormal_parameters(mean=MEAN_BETA_PER_WEEK, sd=SD_BETA_PER_WEEK):
    if not all(math.isfinite(v) and v > 0 for v in (mean, sd)):
        raise ValueError("The mean and standard deviation of beta must be positive and finite.")
    sigma = math.sqrt(math.log1p((sd/mean)**2))
    return math.log(mean)-sigma*sigma/2, sigma


def beta_quantile(probability):
    q = np.asarray(probability, dtype=float)
    if np.any(~np.isfinite(q)) or np.any((q <= 0) | (q >= 1)):
        raise ValueError("Quantile probabilities must be strictly between zero and one.")
    mu, sigma = lognormal_parameters()
    return np.exp(mu + sigma*ndtri(q))


def reach_for_beta(time, beta, probability=CENTRAL_PROBABILITY):
    z = central_quantile(probability)
    t, b = np.asarray(time, dtype=float), np.asarray(beta, dtype=float)
    if np.any(~np.isfinite(t)) or np.any(t < 0) or np.any(~np.isfinite(b)) or np.any(b <= 0):
        raise ValueError("Times must be nonnegative, beta must be positive, and both must be finite.")
    p = Parameters()
    with np.errstate(over="raise", invalid="raise"):
        return (z*p.reference_length_km*np.sqrt(p.gamma_per_week/b)
                * np.exp((b-p.alpha/p.generation_time_weeks)*t+p.alpha)
                * np.sqrt(-np.expm1(-2*b*t)))


def calculate_boxplots(probability=CENTRAL_PROBABILITY, n=SAMPLES_PER_WEEK, seed=RANDOM_SEED):
    if not isinstance(n, int) or n < 100:
        raise ValueError("Use at least 100 samples per week.")
    rng = np.random.default_rng(seed)
    u = rng.uniform(*TRUNCATION_CDF, size=(len(WEEKS), n))
    beta = beta_quantile(u)
    values = reach_for_beta(np.asarray(WEEKS)[:, None], beta, probability)
    levels = [WHISKER_PERCENTILES[0]/100, .25, .5, .75, WHISKER_PERCENTILES[1]/100]
    quantiles = np.quantile(values, levels, axis=1).T
    return [dict(week=t, whislo=float(q[0]), q1=float(q[1]), med=float(q[2]),
                 q3=float(q[3]), whishi=float(q[4]), fliers=[])
            for t, q in zip(WEEKS, quantiles)]
