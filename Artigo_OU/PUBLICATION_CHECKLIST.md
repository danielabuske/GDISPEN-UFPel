# Publication checklist (complete before making this repository public)

1. **Confirm sharing permissions and authorship.** Obtain approval from all relevant code/data rights holders and the journal's editorial procedure, as applicable.
2. **Choose a software license.** No license has been assigned automatically. Consider MIT or BSD-3-Clause for software only if the authors agree; document the appropriate treatment of any third-party data and figures separately.
3. **Add an accurate citation.** Create `CITATION.cff` with the confirmed author list, article title and identifiers, or insert the final article DOI after assignment. Do not use placeholder authors or an invented DOI.
4. **Review the data provenance.** `Figure_2_POA/figure_2_data/provenance.json` explains that the red series was digitised from an earlier OU plot, not obtained from raw surveillance records. Keep the source and limitations visible.
5. **Validate final figure parity.** Compare the checked-in vector PDFs and CSVs with the exact versions used in the manuscript, including the time grids and axis labels.
6. **Test the pinned environment.** The package documents Python 3.12; recreate its per-folder requirements and run `python -B -m unittest -v test_figure` for each figure.
7. **Review archived content.** `manuscript_audit_response21.md` and `organization_manifest.json` are historical provenance. Keep them only if the authors wish to make them public. Removing or relocating them requires corresponding edits to the README; do not rewrite past hash claims.
8. **Create a stable release.** After final checks, tag a version (e.g. `v1.0.0`) and, if appropriate, archive that release with a repository that issues a DOI. A GitHub URL by itself is not a permanent archival DOI.
9. **Check journal requirements.** Distinguish the separately uploaded mathematical electronic supplementary material from this software-and-figures repository; provide the proper software availability statement and citation as requested by the journal.

The content and numerical source code in the three figure folders have intentionally been kept unchanged in this packaging operation.
