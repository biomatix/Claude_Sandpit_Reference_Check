# Analyst playbook (dartRverse) — sibling reference for the popgen-report skill

This file holds the analyst playbook (originally Appendix A of `popgen-prompt-proforma.md`) and the analyst flags table (originally Appendix B). The Analyst role at Step 2 of `SKILL.md` reads this file at the start of execution.

The analyst (coordinator, playing the role inline) runs these steps in the order specified by the Planner. Send each code block to the RStudio HTTP API (endpoint per project CLAUDE.md; default `http://127.0.0.1:8787/`); check `success` before continuing.

---

## A.1 Environment setup

```r
if (!requireNamespace("dartRverse", quietly = TRUE))
  install.packages("dartRverse")
library(dartRverse)

pkgs <- c("ggplot2", "patchwork", "leaflet", "hierfstat", "mmod",
          "pegas", "vegan", "adegenet", "LEA", "related", "poppr",
          "knitr")
invisible(lapply(pkgs, function(p) {
  if (!requireNamespace(p, quietly = TRUE)) install.packages(p)
  library(p, character.only = TRUE)
}))
gl.set.verbosity(3)
```

### A.1.1 Output directory and caption-snippet helpers

Every artefact this skill produces — figures, tables, snippets, the manuscript
draft, the rendered PDF, intermediate files, and audit logs — is written into
an `outputs/` subdirectory of the project working directory. The directory is
created here and referenced via `output_dir` thereafter. The image src in the
caption snippets stays as a bare filename (no `outputs/` prefix), because the
manuscript also lives in `outputs/` and pandoc resolves relative paths against
the input file's directory.

```r
output_dir <- "outputs"
dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

# Figure: writes outputs/<file> (PNG by default) and a sibling
# outputs/<file>.md with a pandoc-crossref image line that the assembler
# injects verbatim into the manuscript. The image src is the bare
# filename so it resolves alongside the manuscript inside outputs/.
#
# **Default to PNG.** Word (the deliverable medium) cannot reliably
# render embedded PDF images, so the harness prefers raster figures.
# PDF is still accepted for back-compatibility — the file extension you
# pass to `save_fig()` selects the device.
save_fig <- function(label, file, caption, expr,
                     width = 8, height = 6, res = 300,
                     img_width = "100%") {
  out_path <- file.path(output_dir, file)
  out_md   <- file.path(output_dir, sub("\\.[^.]+$", ".md", file))
  ext      <- tolower(tools::file_ext(file))
  switch(ext,
    "png"  = png(out_path,  width = width, height = height,
                 units = "in", res = res),
    "jpg"  = ,
    "jpeg" = jpeg(out_path, width = width, height = height,
                  units = "in", res = res, quality = 95),
    "tiff" = tiff(out_path, width = width, height = height,
                  units = "in", res = res),
    "pdf"  = pdf(out_path,  width = width, height = height),
    stop("Unsupported figure extension: ", ext, ". ",
         "Use .png (preferred), .jpg/.jpeg, .tiff, or .pdf.")
  )
  expr
  dev.off()
  writeLines(
    sprintf("![%s](%s){#fig:%s width=%s}\n",
            caption, file, label, img_width),
    out_md
  )
  message("Saved: ", out_path, " + ", out_md)
}

# Table: writes outputs/<file>.csv and a sibling outputs/<file>.md
# containing a pandoc-style table with a pandoc-crossref label.
save_tbl <- function(label, df, caption, file, digits = 3) {
  out_csv <- file.path(output_dir, file)
  out_md  <- file.path(output_dir, sub("\\.csv$", ".md", file))
  write.csv(df, out_csv, row.names = FALSE)
  md <- knitr::kable(df, format = "pipe", digits = digits,
                     caption = sprintf("%s {#tbl:%s}", caption, label))
  writeLines(md, out_md)
  message("Saved: ", out_csv, " + ", out_md)
}
```

All downstream sections of this playbook (and any bespoke analysis the
Planner specifies) must save figures via `save_fig()` and tables via
`save_tbl()` — never bare `pdf()/dev.off()` or bare `write.csv()`. Labels
must be unique and stable across re-runs (e.g. `pca`, `fst_heatmap`,
`diversity`, `ne_estimates`); they are the keys the manuscript uses to
cross-reference (`@fig:pca`, `@tbl:diversity`). Any other file the playbook
writes (HTML widgets, NeEstimator output, sNMF intermediates) must also be
routed through `file.path(output_dir, …)`.

## A.2 Load the filtered genlight object

```r
load("filtered_genlight.Rdata")   # adjust filename as needed

cat(sprintf("Individuals: %d\nLoci: %d\nPopulations: %d\n",
            nInd(gl1), nLoc(gl1), nPop(gl1)))
popNames(gl1)
table(pop(gl1))
head(gl1@other$latlon)
```

If population names are missing, request a population-assignment vector or metadata CSV and attach with `pop(gl1) <- ...`.

## A.3 Sample distribution map

**MUST use `gl.map.interactive()` from `dartR.spatial`.** Do not substitute
ggplot+`maps`, ggmap, ggspatial, or `gl.map()`. The interactive leaflet is
the deliverable artefact (hover-identifies individuals); the PDF embeds a
static screenshot of the same widget so the print version and the live
version cannot diverge.

```r
# Set pop() to whatever the map should colour by (typically species).
gl_for_map <- gl1
pop(gl_for_map) <- factor(gl1@other$ind.metrics$species)

# Drop individuals lacking coordinates before plotting (gl.map.interactive
# silently skips them, but explicit subsetting prevents accidental misreads
# of the legend counts).
keep <- !is.na(gl_for_map@other$latlon$lat) &
        !is.na(gl_for_map@other$latlon$lon)
gl_geo <- gl_for_map[keep, ]

m <- gl.map.interactive(
  gl_geo,
  ind.circles    = TRUE,
  ind.circle.cex = 7,
  pop.labels     = FALSE,
  provider       = "OpenStreetMap"
)
htmlwidgets::saveWidget(m, file.path(output_dir, "sample_map.html"),
                        selfcontained = TRUE)

# PDF-embeddable still. webshot2 uses headless Chrome via chromote.
webshot2::webshot(file.path(output_dir, "sample_map.html"),
                  file = file.path(output_dir, "01_map.png"),
                  vwidth = 1400, vheight = 1000, delay = 4)
```

Reference the PNG (not the HTML) in the markdown figure include and point
the caption at the live HTML for the reader who wants hover-identification.
Do not commit a static-only map; the HTML is a first-class deliverable.

## A.4 Basic diversity statistics

```r
div <- gl.report.diversity(gl1, table = TRUE)
save_tbl("diversity", div,
         "Per-population diversity statistics: expected and observed heterozygosity, F\\textsubscript{IS}, and allelic richness.",
         "population_diversity.csv")

ar <- gl.report.allelerich(gl1)
save_tbl("allelic_richness", ar,
         "Rarefied allelic richness by population.",
         "allelic_richness.csv")

pa <- gl.report.pa(gl1)
bs <- gl.report.diversity(gl1)
```

Cross-check with hierfstat if desired:

```r
hf  <- gl2hierfstat(gl1)
ar2 <- allelic.richness(hf)
print(colMeans(ar2$Ar, na.rm = TRUE))
```

## A.5 PCA / PCoA

**MUST use `gl.pcoa()` for the ordination and `gl.pcoa.plot()` for the
plot.** Do not substitute `stats::prcomp`, `stats::cmdscale`,
`ade4::dudi.pco`, `vegan::rda`, `adegenet::glPca`, or hand-rolled SNP
ordinations. `gl.pcoa()` handles the SNP-matrix conventions (missing-data
imputation, locus filtering, the `genlight`-aware variance partition)
that every downstream Biomatix figure depends on; substituting another
implementation introduces silent definitional drift.

```r
pc <- gl.pcoa(gl1, nfactors = 10)
gl.pcoa.plot(pc, gl1, ellipse = TRUE, p.level = 0.95,
             legend = "topright", xaxis = 1, yaxis = 2, label = "pop")

barplot(pc$eig / sum(pc$eig) * 100,
        names.arg = paste0("PC", seq_along(pc$eig)),
        ylab = "Variance explained (%)",
        xlab = "Principal component",
        main = "PCA scree plot")

pco <- gl.pcoa(gl1, nfactors = 10, correction = "cailliez")
gl.pcoa.plot(pco, gl1, ellipse = TRUE, label = "pop")
```

## A.6 FST

```r
fst <- gl.fst.pop(gl1, nboots = 1000)
gl.plot.heatmap(fst$Fsts, main = "Pairwise FST (Weir & Cockerham)")
print(round(fst$Fsts, 3))
print(fst$Pvalues)

if (requireNamespace("mmod", quietly = TRUE)) {
  library(mmod)
  gen <- gl2genind(gl1)
  gst <- diff_stats(gen)
  cat("Global Hedrick G'ST:", mean(gst$per.locus$Gst_prime, na.rm = TRUE), "\n")
}
```

## A.7 Isolation by distance

```r
ibd <- gl.ibd(gl1, Dgeo_trans = "log", Dgen_trans = "Fst", permutations = 999)
```

## A.8 Population structure / admixture

```r
gl.tree.nj(gl1, type = "fan", labelsize = 0.8)

gl2geno(gl1, outfile = "gl_for_lea", outpath = output_dir)
npop <- nPop(gl1)
project <- snmf(file.path(output_dir, "gl_for_lea.geno"),
                K = 1:(npop + 2), entropy = TRUE,
                repetitions = 10, project = "new")
plot(project, col = "blue", pch = 19, cex = 1.2)

K_best <- npop
best   <- which.min(cross.entropy(project, K = K_best))
qmat   <- Q(project, K = K_best, run = best)
rownames(qmat) <- indNames(gl1)
gl.plot.structure(qmat, K = K_best, pop.labels = pop(gl1))

save_tbl("admixture_q",
         data.frame(id = indNames(gl1), pop = pop(gl1), qmat),
         sprintf("Per-individual admixture proportions (Q matrix) at K = %d.",
                 K_best),
         "admixture_Qmatrix.csv")
```

## A.9 Effective population size (Ne)

```r
ne <- gl.LDNe(gl1,
              outfile     = file.path(output_dir, "Ne_estimates.txt"),
              neest.path  = getOption("neest.path"),
              critical    = c(0, 0.05),
              singleton.rm = TRUE,
              mating      = "random")
```

If NeEstimator is not installed, instruct the user to download v2 from <http://www.molecularfisherieslaboratory.com.au/neestimator-software/> and set `options(neest.path = "C:/path/to/NeEstimator/")`.

## A.10 Relatedness

```r
rel <- gl.grm(gl1)
heatmap(rel, symm = TRUE, main = "Genomic relatedness matrix")
```

## A.11 AMOVA

```r
amova_res <- gl.amova(gl1, nperm = 999)
```

## A.12 Save publication-ready figures

Each call writes both the figure (PNG by default — see §A.1.1) and a
caption snippet that the Coordinator injects inline at first reference.

```r
save_fig("pca", "01_PCA.png",
         "Principal-coordinates analysis of individuals, coloured by population. Ellipses enclose 95\\% of the within-population scores.",
         gl.pcoa.plot(pc, gl1, ellipse = TRUE, label = "pop"))

save_fig("fst_heatmap", "02_FST_heatmap.png",
         "Pairwise F\\textsubscript{ST} (Weir \\& Cockerham) among populations.",
         gl.plot.heatmap(fst$Fsts))

save_fig("ibd", "03_IBD.png",
         "Isolation by distance: pairwise genetic distance against log-transformed geographic distance, with Mantel test result.",
         print(ibd))

save_fig("nj_tree", "04_NJ_tree.png",
         "Neighbour-joining tree of individuals based on Euclidean genetic distance.",
         gl.tree.nj(gl1, type = "fan"))
```

---

## Analyst flags

Raise these proactively to the Coordinator:

| Observation | Action |
|---|---|
| n < 10 in any population | Warn; allelic richness and Ne estimates unreliable |
| Negative FIS values | Check for relatives; run relatedness screen |
| Convergence at K = 1 in sNMF | Populations may not be genetically differentiated |
| IBD not significant but FST significant | Consider landscape barriers analysis |
| Loci retained < 1000 | Relax MAF or callrate thresholds slightly |
| silicoDArT: He > 0.5 | Unexpected for presence/absence — check ploidy |

**Bespoke analyses outside the playbook.** When the Planner specifies an analysis not in the playbook (parentage exclusion, KING-robust kinship within a clutch, sNMF cross-entropy stability across many reps, *f*-statistic admixture tests, etc.), implement it directly in R against the active session and include the result in the Analyst's results document. The standard playbook is a starting set, not an exhaustive list — the user's prompt-coverage table determines what must be answered. Bespoke figures and tables must still be saved through `save_fig()` / `save_tbl()` (§A.1.1) so the Coordinator has caption snippets to inject at first reference.
