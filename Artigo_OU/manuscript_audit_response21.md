# Manuscript Audit: Resposta_ao_Revisor (21).pdf

Date: 2026-11-04.
Document: An Analytical Model of Infectiousness for Spatial Epidemic Risk Assessment.
Scope: reading all 24 pages, including appendices and references; inspecting figures; independently checking the main calculations; targeted consultation of primary sources and the public Dryad record. The PDF contains the manuscript, not a response letter to reviewers.

Archive note: this is an English translation of the dated audit, not a fresh audit of a later manuscript. Findings and statements about material availability refer to the version and materials available at that audit. Subsequent code-language and metadata corrections are recorded separately in organization_manifest.json.

## Assessment

The revision should prioritize spatial interpretation, calibration traceability, and references. The central temporal calculations agree with the equations presented. The OU solution and mean-incidence factorization are consistent under the stated assumptions.

The findings below distinguish verifiable errors, acknowledged limitations, and points still requiring documentation. A phenomenological assumption is not, by itself, a mathematical error.

## Priority Findings

### 1. The 96% label does not describe envelope coverage after modulation

**High priority. Location: pp. 12-15 and Appendix A.2, p. 22, Eq. (30).**

Appendix A.2 already correctly states that multiplying the half-width by exp[-alpha(t/Tg-1)] does not preserve probability under the original OU density. In the audited PDF, the axes of Figures 2 and 3 still say "96% reach distance (km)". This permits a probabilistic interpretation that the appendix itself rules out.

If r_OU = z_0.98 * sigma_OU and r_mod = r_OU * f(t), then:

    P_OU(|X-x0| <= r_mod) = erf[z_0.98 * f(t) / sqrt(2)]
    f(t) = exp[-alpha * (t/Tg - 1)]

Using the manuscript's baseline parameters:

| Time | Baseline modulated reach | Mass under the original OU density |
| --- | ---: | ---: |
| 2.6 weeks | 0.5261 km | 96.00% |
| 4.5 weeks | 0.6022 km | 15.93% |
| 7 weeks | 0.7188 km | 0.754% |
| 10 weeks | 0.8889 km | 0.0192% |

These values belong to the fixed baseline configuration, not the median of the random-beta scenario. The median of approximately 0.65 km in Figure 3 remains correct for that scenario.

**Sufficient correction without changing the formulation:** use "Modulated spatial reach (km)" and explain that the envelope was constructed from the central 96% interval BEFORE modulation. Do not present the final envelope as containing 96% of the OU mean incidence.

**Action taken in the original audit session:** the Figure 1 label was checked and the Figure 2 and 3 labels were corrected. All three figure PDFs were regenerated. Figure 3 was updated following the supplementary request. The manuscript PDF was not changed.

### 2. Figure 2 overlays different geometric and temporal quantities

**High priority. Location: pp. 12-16, particularly Figure 2 on p. 14.**

The model envelope's half-width at a given instant is compared with the diameter of clusters reconstructed from observed cases by Guzzetta. In the latter case, diameter involves the maximum separation between cluster cases and cluster duration, not a quantile of an instantaneous spatial distribution. The primary source is Figure 4c of [Guzzetta et al. (2018)](https://doi.org/10.1038/s41467-018-05230-4).

The text already acknowledges this difference, which should be retained. However, the visual overlay still encourages an interpretation of fitting. Doubling the reach would only harmonize half-width and width; it would not make the result equivalent to the maximum diameter of a set of accumulated observed cases.

**Suggested correction:** explicitly retain the comparison as one of spatial scales; identify each quantity in the caption and consider separate panels. Do not calculate predictive error between the series as though they measured the same observable.

The P5-P95 boxplot whiskers cover 90% of the simulated parameter scenario. The red band represents a 95% confidence interval in the external source. The manuscript correctly distinguishes these quantities; they should not share an undifferentiated "uncertainty" label.

### 3. The Bangkok anchor requires clearer provenance and time conversion

**High priority. Location: p. 12, Section 5.2, and Figure 1, p. 13.**

The manuscript adopts approximately 20 km at 54 weeks to calibrate alpha, but does not identify the curve, points, or procedure that produced that target.

Figure 3 of [Salje et al. (2021)](https://pmc.ncbi.nlm.nih.gov/articles/PMC7985522/) presents distance distributions after 20 generations. With the adopted Tg of 18.2 days, 20 generations correspond to 364 days, or 52 weeks. Choosing 54 weeks requires its own justification. I did not find a direct statement in the source text identifying "20 km at 54 weeks" as a 96% quantile.

The 96% mentioned in Salje's abstract refers to the time infected individuals spend in their home community. It does not, by itself, justify a spatial 96th percentile.

**Suggested correction:** document the panel/curve, reading method, spatial meaning, and conversion from generations to weeks. If the target is an adopted illustrative benchmark, retain that qualification throughout the manuscript. The current distinction between calibration and independent validation is appropriate.

### 4. Modulation determines much of the reported spatial behavior

**High priority for interpretation, not an algebraic error. Location: pp. 5, 12, and 22.**

Combining Eqs. (4), (7), and (30) gives:

    r_mod(t) = z * L * sqrt(gamma/beta)
               * exp[(beta-alpha/Tg)*t + alpha]
               * sqrt[1-exp(-2*beta*t)]

At longer times, growth depends on beta-alpha/Tg. With the baseline values, this difference is approximately 0.07080 per week, whereas beta is approximately 1.29387 per week.

Modulation is therefore a substantial correction. For example, at 4.5 weeks the original OU half-width is approximately 6.151 km, while the modulated envelope is 0.602 km. This should be explicit when attributing the spatial curve to the transport model.

**Suggested correction:** present the combined expression and attribute the results to the model plus phenomenological modulation. The statistical-correction precedents cited in the Discussion do not validate this particular functional form.

### 5. There are verifiable problems in the references

**High priority before submission. Location: pp. 17-21.**

| Entry | Finding | Action |
| --- | --- | --- |
| [62], Zhang et al. | DOI 10.1073/pnas.2003159117 belongs to a paper about mice, not the cited title. The paper with the stated title appeared in Science, DOI 10.1126/science.abb8001. | Correct the journal, volume, pages, and DOI. Also reassess its relevance in the spatial-kernel paragraph. |
| [5], Boender and Hagenaars | I could not confirm the stated title and identifier s41598-023-35013-z. I found a 2023 paper on kernels by the same authors, with a different title and DOI. | Check the intended source before replacing the entry. |
| Entry after [19] | Hamel and Rossi appears without its own number, within the [19] block. | Correct the bibliography structure. |
| [44] | The address starts with "https://doi.10.1016/...", a malformed URL. | Correct it to the doi.org/10.1016/... format. |
| [52] | The title adds "was quantified", which is absent from the original title. | Restore the correct bibliographic title. |
| [18] | The entry says "Forthcoming 2025", but the consulted record is already published. | Cite the version actually used. |

Verification of [62]: [correct paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC7199529/) and [paper matching the incorrect DOI](https://pmc.ncbi.nlm.nih.gov/articles/PMC7355008/).
Possible intended source for [5], without assuming equivalence: [Common features in spatial livestock disease transmission parameters](https://pmc.ncbi.nlm.nih.gov/articles/PMC9981765/).
Original title for [52]: [PLOS publication](https://journals.plos.org/plosntds/article?id=10.1371/journal.pntd.0000920).

This was a targeted bibliographic check; it does not individually certify all 65 references.

### 6. Publicly available materials need to match this revision

**High priority for reproducibility. Location: pp. 4-9, 15-16, and reference [18].**

The consulted public [Dryad record](https://datadryad.org/dataset/doi:10.5061/dryad.hmgqnk9rr) shows an update in January 2025. Its README describes four figure generators and R_0.py, whereas the current manuscript has three figures. The record's abstract still highlights 38.5% presymptomatic transmission, a result absent from the audited revision.

This demonstrates a mismatch in the public documentation, but does not establish the ZIP file's complete contents: the access attempt returned a verification page, so the package could not be inspected.

The proofs called Supplementary Material 1 and 2 are not included in the 24 pages received. Ensure that they accompany the submission and are identified in the corresponding public version.

**Suggested correction:** align the record, README, scripts, tables, and supplements with the submitted version, identifying its date/version. The local Artigo_OU documentation is more recent, and its tests for all three figures passed.

## Medium-Priority Methodological Points

### 7. The origin of L and the conditional calibration of alpha need clarification

**Location: pp. 5, 11-12, and 22.**

L = 8.94 x 10^-3 km appears as an adopted value, without a source or quantitative justification in the PDF. A single spatial target identifies alpha only after L and the other parameters have been fixed; it does not identify L and alpha simultaneously.

**Suggested correction:** explain how L was chosen and include it, alpha, and the reference percentile in the parameter table. State that alpha's calibration is conditional on these choices. No additional formulation is required.

### 8. The truncated beta distribution shifts the scenario's center

**Location: p. 13 and Figures 2-3.**

The text correctly states that the mean of 1.2939 and SD of 0.1294 per week precede truncation. However, truncating between P40 and P75 removes asymmetric intervals and changes the center of the distribution actually sampled.

Recalculation of the conditional distribution:

| Statistic | Value per week |
| --- | ---: |
| Lower bound | 1.255346 |
| Upper bound | 1.377088 |
| Mean after truncation | 1.313341 |
| Median after truncation | 1.311998 |
| Fixed baseline beta | 1.293875 |

At 20 weeks, baseline reach is 1.804 km and the scenario's theoretical median is 2.575 km. The code's sample value, approximately 2.568 km, is compatible with that theoretical median.

**Suggested correction:** report the conditional moments or emphasize that the scenario is not centered on the baseline case; justify the P40-P75 choice. Box widths do not estimate observed heterogeneity in Porto Alegre. The manuscript already avoids that last claim.

### 9. Absolute reproduction values depend on the amplitude convention

**Location: pp. 6-11, particularly Eqs. (12), (24), and (25).**

The calculations are consistent with kappa_h = sqrt(8/pi) and kappa_v = sqrt(8m/pi), but these amplitudes are adopted. Absolute Rcycle values are therefore conditional model results, not estimates inferred from the cities' data.

The approximately 40% reduction contrasts two scenarios with fixed parameters. It does not demonstrate the observed effectiveness of an intervention. Latent periods represented as delays without additional losses and use of the source-evaluated curve as an infectivity profile are also explicit assumptions.

**Suggested correction:** briefly justify the amplitude convention and retain the existing conditional language. I found no error in the Rcycle versus R0,NGM distinction; the square-root relation between these conventions is correct for the matrix presented.

### 10. The initial singularity warrants explanation alongside the temporal profile

**Location: pp. 6-8 and limitations on p. 16.**

The density in Eq. (18) diverges as w^(-1/2) when w approaches zero. The singularity is integrable in one dimension and therefore does not invalidate the calculated moments. However, it is a strong assumption about the temporal shape of infection production immediately after infectiousness begins.

**Suggested correction:** explain this property when introducing the profile. The qualification about regularization in two dimensions, already included in the Discussion, is relevant. The profile need not be changed to acknowledge the limitation.

### 11. The original contribution should be identified more precisely

**Location: pp. 2, 14-16.**

The identity j(x,t) = i(t)P(x,t) follows from composition of the same spatial semigroup across generations and the position independence of the temporal kernel. It is consistent with the stated assumptions, but this identity alone does not establish mathematical novelty in branching-process theory.

**Suggested correction:** identify the specific combination, interpretation, and application as the contribution, distinguishing known results from developments of this work. Do not treat the descriptive comparison as proof of operational validity.

## Independent Numerical Check

The values below were recalculated directly from the manuscript's equations, without using the old Dryad scripts.

| Quantity | Recalculation | Assessment |
| --- | ---: | --- |
| beta per day | 0.1848392481 | Matches |
| beta per week | 1.2938747370 | Matches |
| Baseline Ehv | 1.0082737053 | Matches |
| Evh | 1.8240357635 | Matches |
| Attenuated Ehv | 0.6053048993 | Matches |
| Baseline Rcycle | 1.8391272979 | Matches |
| Attenuated Rcycle | 1.1040977842 | Matches |
| Relative reduction | 39.9662% | Matches approximately 40% |
| Baseline generation-time mean | 18.2 days | Calibration target |
| Baseline generation-time SD | 6.938731 days | Matches |
| Attenuated generation-time mean | 15.935500 days | Matches |
| Attenuated generation-time SD | 5.316952 days | Matches |
| Baseline reach at 54 weeks | 20.031168 km | Matches the approximate 20 km target with rounded alpha |
| Theoretical median at 4.5 weeks, truncated beta | 0.648816 km | Matches approximately 0.65 km |
| Theoretical P5-P95 at 4.5 weeks | 0.526096-0.823194 km | Matches approximately 0.53-0.82 km |

The Gaussian OU solution, the 2Dt variance limit, normalization of Eq. (18), its moments, and the Gamma factor in Eq. (16) are consistent with the one-dimensional formulation.

The incidence factorization in Eq. (6) is valid under a common operator, fixed center, and position-independent reproduction. I identified no sign error in the repulsive drift or in the correspondence in Appendix B.

## Editorial and Local-Material Consistency

- Figure 1 uses "Figura", whereas Figures 2 and 3 use "Figure". Standardize the English manuscript.
- B_infinity is defined as the value at the source, not a limit as time approaches infinity. A notation such as B_src would reduce ambiguity if convenient for the revision.
- The Introduction announces "operational value", but the application is illustrative and still requires validation. Align that phrase with the abstract and conclusion.
- The Discussion repeats several Results values and qualifications. It could be shortened while retaining the essential distinctions about observables, calibration, and coverage.
- Local provenance of the red references is documented in Figure_2_POA/figure_2_data/provenance.json. It identifies a figure from an earlier version of the OU manuscript as the direct source. This is not equivalent to newly digitizing and checking Guzzetta's original figure.
- At the time of the audit, generator docstrings, console messages, and JSON metadata still included statements assigning 96% mass to the modulated reach. Changing the axes did not automatically correct those statements. They needed alignment with Appendix A.2 in a revision of supporting text.
- The organization manifest recorded historical hashes and was not treated as an updated manifest of that audit revision.

## Changes and Checks Performed

Following the subsequent request about the axes:

1. Confirmed "Modulated spatial reach (km)" in Figure 1.
2. Replaced the Figure 2 and 3 labels with the same text.
3. Updated the existing label tests and corresponding LEIA_ME files.
4. Regenerated PDF, CSV, and JSON outputs for all three figures.
5. Ran the 22 tests for Figures 1 and 2 and, following the supplementary request, the seven Figure 3 tests. All passed, including numerical-reproduction checks.
6. Checked the text of all three generated PDFs and visually inspected Figure 2.

The manuscript PDF was not rewritten and mathematical parameters were not modified. Labels in all three generators and individual figure PDFs were updated.

## Audit Limitations

Supplementary Materials 1 and 2, the reviewer's letter, and the original individual-level data were not included in the PDF. The public Dryad ZIP was not accessible for inspection. The audit therefore confirms consistency of the presented calculations and the three tested local packages, but does not certify every public resource, every reference, or independent empirical validation.

