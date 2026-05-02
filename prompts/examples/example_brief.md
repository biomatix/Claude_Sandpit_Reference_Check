<!--
Example contract brief, kept for reference. Real briefs are pasted into
jobs/<slug>/brief.md after running /new-job, then parsed with /intake.
This file lives outside jobs/ on purpose: it is documentation, not a job.
-->

# Example brief — Bellinger River turtles (Myuchelys)

## Study

Genus *Myuchelys* — four species: *M. bellii*, *M. georgesi*, *M. purvisi*, *M. latisternum*. A gravid female *Myuchelys* (sample ID **LSWt111**) was captured in the Bellinger River, transported to the University of New England, and laid a clutch of 24 eggs. The embryos were sacrificed before the half-way point of incubation to provide tissue for genotyping; no live progeny exist.

## Data

- File: `raw.RData` in the working directory (raw DArTseq SNPs, ~153k loci, ~280 individuals; load via `gl.load`).
- LSWt111 is in population `Bella_mum`; her 24 offspring are in population `Bella_egg`.
- Reference panels for *M. bellii*, *M. purvisi* and *Emydura macquarii* are in the same file. There is **no *M. latisternum* reference**.
- The data are raw — apply standard filtering (secondaries, reproducibility, callrate, monomorphs) at the start of the Analyst step.

## Questions

**Q1. Does the genetics support the assignment of LSWt111 as the mother of the 24 *Bella_egg* offspring?**

**Q2. Is there evidence of multiple paternity within the clutch?**
- Context: chelid turtles store sperm and multiple paternity is widespread in the family — multiple paternity is the null expectation, not the exception.

**Q3. To which species do LSWt111 and her clutch belong?**
- Context: reference samples are available for *M. bellii*, *M. purvisi* and *Emydura macquarii*; no *M. latisternum* reference. The Bellinger collection locality is consistent with *M. georgesi*.

**Q4. Is there genetic evidence that LSWt111 is a *Myuchelys × Emydura macquarii* hybrid? If so, does her clutch carry the *Emydura* component?**
- Context: *Myuchelys georgesi × Emydura macquarii* hybridisation has been documented in the Bellinger.

**Q5. What management actions are supported by the genetic results for (a) LSWt111 herself and (b) the clutch tissue?**
- FACT: The 24 embryos were sacrificed for tissue. No live progeny exist. The hatchlings cannot be released or added to a captive insurance colony — the only conservation deposit derivable from this clutch is its cryobanked tissue/DNA plus the indirect paternal genotype reconstructable from the joint mother–offspring data.
- Context: A captive insurance colony for *M. georgesi* is held at Taronga. LSWt111 herself is alive; the release-versus-retention decision for her is in scope.

**Q6. The "windfall" question. A nidovirus epizootic in 2014–2015 killed almost every adult *M. georgesi* in the Bellinger. LSWt111 and about six other adults survived and are now being radio-tracked. Conditional on LSWt111 being confirmed *M. georgesi* (Q3), advise on what can be done with this surviving cohort to identify the genetic background that may afford immunity to the virus.**
- FACT: This is a request for a concrete action plan with named methods and inputs, not a single-paragraph hedge. Do not demote to "future work".

## Standard outputs to include alongside the question-driven analyses

- A geographic map of the source localities of all sampled animals.
- A PCA showing the relationships among all individuals and the placement of LSWt111 and her clutch.
