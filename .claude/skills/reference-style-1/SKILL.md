---
name: reference-style-1
description: >
  Format, check, or convert references to the Harvard style. Use this skill whenever the user
  asks you to write, reformat, verify or critique in-text citations or a reference
  list in Harvard (author-date) style. Covers in-text citation rules and reference-list entries for
  journal articles, preprints, datasets, books, book chapters, theses, reports,
  conference proceedings, web material, standards and patents.
---

## Role

You are acting as a referencing assistant for Harvard style. Apply the rules in
this skill whenever the user asks you to format, check, convert, or critique
in-text citations or a reference list, or when the user is preparing a manuscript
for a journal.

Before editing a reference list, confirm which style is required — the target
journal's author instructions are authoritative. This skill documents the local Harvard variant.

---

## How to Respond

When asked to **reformat** an existing list of references, return the revised list
as a clean block, with one reference per paragraph, in the same order the user
provided unless they ask for sorting. Briefly note any references you could not
reformat because information was missing (e.g. no DOI, no page range).

When asked to **check** a reference list, report issues reference by reference:
name the problem (e.g. "missing DOI", "journal name abbreviated", "ellipsis used
instead of full author list"), quote the offending part and give the corrected
form.

When asked to **convert** from another style (APA, Chicago, Vancouver) to 
Harvard, produce the converted list directly. Flag any reference where the source
style omits information the target style requires.

Do not invent authors, years, DOIs, page ranges, or publisher details. If a field
is missing from the source, leave a clear `[missing: <field>]` placeholder and
list it at the end of the response.

---

## 1. General Rules

All references listed at the end of the paper must be cited in the text, and all
in-text citations must appear in the reference list.

Use full titles for all references. Do not abbreviate journal names.

Include all author names in the reference list where possible. Where this is not possible, 
include the first three author names followed by *et al.* Do not use ellipses (…) to
indicate missing authors.

If several references share the same author and year, differentiate them with
italicised letter extensions: 2023*a*, 2023*b*.

Arrange the reference list alphabetically by first author surname, then
chronologically (earliest first) within the same author.

---

## 2. In-Text Citations

Cite references by author and date:

> (Smith 2024)

For two or more references together, list in **chronological order** separated by
semicolons:

> (Bloggs 2017; Doe 2024)

For multiple references from the **same year**, cite alphabetically:

> (Doe 2024; Smith 2024)

For two co-authors, link names with "and":

> (Doe and Smith 2023)

For three or more authors, use "*et al.*" after the first author's name (italic
*et al.*):

> (Smith *et al.* 2024)

For a direct quote, include the page number:

> (Smith *et al.* 2024, p. 6)

---

## 3. Reference List — Entry Formats

Each entry type is shown with the canonical form and a worked example is provided for guidance.

### 3.1 Journal article (with page range)

**Form:** `Author(s) (Year). Title. Journal Name Volume:page–page. doi:…`

Journal name in italics. Page range with en-dash.

> Povh LF, Willers N, Fleming PA (2023). Set free: an evaluation of two break-away mechanisms for tracking collars. *Wildlife Research* 50:782–291. doi:10.1071/WR21176

### 3.2 Journal article (with article ID)

Used when the journal assigns an article ID rather than page numbers.

> Franz SC, Colavito MM, Edgeley CM (2024). From flexibility to feasibility: identifying the policy conditions that support the management of wildfire for objectives other than full suppression. *International Journal of Wildland Fire* 33:WF24031. doi:10.1071/WF24031

### 3.3 Preprint

Mark with `[Preprint]` before the server name.

> Corcoran AJ, Schirmacher MR, Black E, Hedrick TL (2021) ThruTracker: open-source software for 2-D and 3-D animal video tracking. [Preprint] bioRxiv. doi:10.1101/2021.05.12.443854

### 3.4 Dataset

Include version if available. Mark with `[Dataset]` before the repository.

> Fiddes S, Pepler A, Saunders K, Hope P (2020). Southern Australia's climate regions. (Version 1.0.0) [Dataset] Zenodo. doi:10.5281/zenodo.4265471

### 3.5 Book

Title in italics. Edition after title. Publisher and location in parentheses.

> Lezak MD (1983). *Neuropsychological assessment*, 2nd edn. (Oxford University Press: New York, NY, USA)

### 3.6 Book chapter

Chapter title unquoted. Book title in italics, preceded by page numbers and "in". Editors marked `(Eds …)`, then page range, then publisher in parentheses.

> Gill AM, Bradstock R (2003). Fire regimes and biodiversity: a set of postulates. Pp 15-25 in *Australia burning: Fire ecology, policy and management issues*. (Eds G Cary, D Lindenmayer, S Dovers) (CSIRO Publishing: Melbourne, Vic, Australia)

### 3.7 Thesis

Include degree, institution, and location. Italicise scientific names if present in the title.

> Purcell BV (2010). Order in the pack: ecology of *Canis lupus* dingo in the southern Greater Blue Mountains World Heritage Area. PhD Thesis, University of Western Sydney, NSW, Australia.

### 3.8 Report, part of a report, or bulletin

Include report number, series, issuing body, and location.

> Bradshaw FJ (2015). Reference material for karri forest silviculture. Technical Report FEM067. Forest Management Series. Department of Parks and Wildlife, Perth.

For a chapter or part of a larger report, treat like a book chapter:

> IPCC (2022). Summary for Policymakers. pp. 3–48. in *Climate Change 2022: Mitigation of Climate Change. Contribution of Working Group III to the Sixth Assessment Report of the Intergovernmental Panel on Climate Change* (Eds PR Shukla, J Skea, R Slade, A Al Khourdajie, R van Diemen, D McCollum, M Pathak, S Some, P Vyas, R Fradera, M Belkacemi, A Hasija, G Lisboa, S Luz, J Malley) (Cambridge University Press, Cambridge, UK and New York, NY, USA) doi:10.1017/9781009157926.001

### 3.9 Conference proceedings

Proceedings title in quotes, preceded by page numbers and "in". Include dates and location of the conference, editors, page range, and publisher.

> Robinson RM (2005). Volume loss in thinned karri regrowth infected by *Armillaria luteobubalina* in Western Australia. Pp. 296–303 in *Proceedings of the 11th IUFRO International Conference on Root and Butt Rots of Forest Trees*, 16–22 August 2004, Poznan and Bialowieza, Poland. (Eds M Manka, P Lakony) (The August Cieszkowski Agricultural University: Poznan, Poland)

### 3.10 Web-based material (URL or DOI)

Prefer DOI if available. Otherwise provide full URL and access date.

> Stroke Foundation (2023). Clinical Guidelines for Stroke Management. Available at https://informme.org.au/Guidelines/Clinical-Guidelines-for-Stroke-Management [accessed 13 November 2023]

> Dunne S, Fletcher A, Bradbury C (2024). Life after lockdown: loneliness, exclusion, and the impact of hidden disability. doi:10.17605/OSF.IO/MYFH4

### 3.11 Standard

Include standard code, issuing body, and location. Add URL if accessed online.

> ISO (2022). Environmental management — Guidelines for environmental due diligence assessment. ISO14015:2022. International Organization for Standardization: Geneva. Available at https://www.iso.org/standard/78014.html

### 3.12 Patent

Include patent number, issuing office, and URL.

> Ghatak S (2019). Immunization testing system (U.S. Patent No. 10,788,482). U.S. Patent and Trademark Office. Available at https://rb.gy/ik0fb0

---

## 4. Formatting Conventions

The following details are what reviewers and copy editors most often flag. Apply
them strictly when producing output.

- **Author names:** Surname first, then initials without periods or spaces (e.g. `Smith JA`, not `Smith, J. A.` or `Smith J. A.`).
- **Year:** In parentheses directly after the author list, then a period and a space before the title.
- **Title:** Sentence case. No terminal period before the journal name for articles; end with a period for books, theses, and reports.
- **Journal name:** Italicised, full (never abbreviated).
- **Volume:** Issue numbers are not included for unless pagination restarts each issue.
- **Pages:** En-dash (–), not hyphen (-). No "pp." for journal articles; use "pp." for book chapters, reports, and proceedings.
- **DOI:** Lower-case `doi:` prefix, no space, no trailing period. Do not wrap in `https://doi.org/`.
- **Editors:** `(Eds AB Smith, CD Jones)` — "Eds" even for a single editor is not used; use "(Ed. AB Smith)" for one editor.
- **Scientific names:** Italicise genus and species anywhere they appear (title, journal name context, etc.).
- **Ampersand:** Never used. Always "and" between author surnames in text.
- **Ellipses:** Never used to truncate author lists.
- **Same author/year:** Append italic letters, e.g. `Smith JA (2023`*`a`*`)`, `Smith JA (2023`*`b`*`)`, ordered by appearance in the text or alphabetically by title.

---

## 5. Common Errors to Flag on Review

When reviewing a reference list, watch for and call out:

- Abbreviated journal names (`J. Anim. Ecol.` → spell out as `Journal of Animal Ecology`).
- Hyphens in page ranges (should be en-dashes).
- Missing DOIs where one is available.
- `et al.` used in the reference list when fewer than three authors are listed before it.
- Ellipses (`…`) in place of omitted authors.
- In-text citations using `&` instead of `and`.
- References cited in text but absent from the list (or vice versa).
- Same-year same-author references without `a`/`b` suffixes.
- Non-chronological ordering of multi-citation parenthetical groups.
- Issue numbers included where pagination is continuous across a volume.
- `pp.` included for journal articles, or omitted for book chapters.

---

## 6. Source

The rules and examples in this skill are modified from CSIRO Publishing's
"Harvard references: Details and examples for journal authors". Always defer to
the specific author instructions of the target journal where they differ.
