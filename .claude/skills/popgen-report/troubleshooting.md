# Troubleshooting common dartRverse issues — sibling reference for the popgen-report skill

Originally Appendix D of `popgen-prompt-proforma.md`. Read on demand when an analyst step fails.

---

- **`gl.read.dart` fails** — check the DArT report CSV uses the expected two-row header. Use `dart.report = TRUE` to inspect.
- **Population names lost after filtering** — reattach with `pop(gl1) <- pop(gl_original)[indNames(gl1)]`.
- **`gl2hierfstat` error with missing data** — impute first: `gl1 <- gl.impute(gl1, method = "frequency")`.
- **sNMF project already exists** — use `project = "continue"` or delete the `.snmfProject` directory.
- **Negative eigenvalues in PCoA** — use `correction = "cailliez"` or `correction = "lingoes"` in `gl.pcoa()`.
- **`load()` fails with "bad restore file magic number"** — the `.Rdata` file may actually be a serialised dartR genlight saved via `gl.save()`. Use `gl.load("filename.RData")` instead.
- **PDF render fails with "Unable to open output PDF"** — the file is locked, usually by a viewer. Render to a fresh filename (`manuscript_final_v2.pdf`) instead of overwriting.
- **`xelatex` warning "Missing character: There is no ≥ (U+2265)"** — cosmetic; the symbol is dropped but compilation continues. To fix, use a font with broader Unicode coverage or replace ≥/≤/× with their LaTeX equivalents (`\geq`, `\leq`, `\times`).
- **sNMF cross-entropy near-tie between adjacent K values** — re-run with ≥ 20 replicates per K and report the per-K spread (boxplot of `cross.entropy(proj, K = k)`); a difference smaller than the rep-to-rep SD is not a defensible K choice.
- **GRM coefficients negative or implausible in a small relative-dominated subset** — VanRaden GRM centres on sample-derived allele frequencies and breaks down when one family dominates the sample. Switch to KING-robust kinship (Manichaikul et al. 2010), which is robust to that misanchoring.
