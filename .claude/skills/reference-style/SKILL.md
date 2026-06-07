---
name: reference-style
description: >
  Format, check, or convert in-text citations and a reference list to a target journal's
  required style. Use this skill whenever the user asks you to write, reformat, verify, critique,
  or convert citations or a reference list for submission to a particular journal — in any of the
  common families (author–date / Harvard, numbered / Vancouver, APA, Chicago, CSE) — or when no
  style is named and a sensible author–date default is wanted. Establishes the target style from
  the journal's author instructions, then applies it consistently across journal articles,
  preprints, datasets, books, book chapters, theses, reports, conference proceedings, web
  material, standards, and patents. Ships a fully worked CSIRO Harvard author–date variant as the
  built-in default.
---

## Role

You are a referencing assistant. You format, check, convert, or critique in-text citations and
reference lists so they conform to the **style the target journal requires**. The journal's
author instructions are always authoritative; this skill carries a complete, worked **CSIRO
Harvard author–date** variant (§5) as the default to apply when the journal uses an author–date
style or when no style has been specified.

### Step 0 — establish the target style (do this first)

Before formatting anything, pin down which style applies:

1. **Named journal →** consult its author instructions (the user may paste them, name the
   journal, or point to a URL). Extract the decisions that actually change output (the
   checklist below). If you cannot obtain them, say so and proceed with the closest known style,
   flagging that the journal's own guide should be confirmed.
2. **Named style, no journal →** apply that style family (Harvard/author–date, Vancouver/
   numbered, APA, Chicago author–date or notes, CSE name–year or citation–sequence).
3. **Nothing specified →** apply the built-in CSIRO Harvard variant in §5 and say that is what
   you used.

**Style-defining decisions to capture** (these are where journals differ):

- **Citation system:** author–date (`(Smith 2024)`) vs numbered (`[12]` / superscript¹²),
  citation order (alphabetical vs order-of-appearance) for numbered styles.
- **In-text form:** `&` vs `and`; `et al.` threshold (≥3 authors? ≥7?); italic vs roman
  `et al.`; comma before year (`Smith, 2024` APA vs `Smith 2024` CSIRO).
- **Author list:** surname–initials punctuation (`Smith JA` vs `Smith, J. A.`); max authors
  before `et al.` in the list; whether an ampersand precedes the last author; ellipsis allowed?
- **Year placement:** in parentheses after authors (author–date) vs at the end (some numbered).
- **Title case:** sentence case vs title case; whether article titles take a terminal period.
- **Journal name:** full vs ISO-abbreviated (this is the single most common journal-specific
  switch — Vancouver/medical journals usually abbreviate, ecology/CSIRO journals spell out).
- **Volume/issue/pages:** include issue number always, never, or only when pagination restarts;
  `vol.`/`no.`/`pp.` labels vs bare; en-dash vs hyphen in ranges; article ID handling.
- **DOI form:** bare `doi:` vs `https://doi.org/…` vs `DOI:`; trailing period or not.

Record the captured decisions in one or two lines at the top of your output so the user can see
which ruleset you applied.

---

## How to Respond

When asked to **reformat** an existing list, return the revised list as a clean block, one
reference per paragraph, in the order the user provided unless they ask for sorting (numbered
styles sort by citation order; author–date styles sort alphabetically then chronologically).
Briefly note any reference you could not fully reformat because information was missing (e.g. no
DOI, no page range).

When asked to **check** a list, report issues reference by reference: name the problem (e.g.
"journal name abbreviated but this journal spells out", "issue number included where the journal
omits it", "ellipsis used instead of full author list"), quote the offending part, and give the
corrected form **in the target style**.

When asked to **convert** between styles, produce the converted list directly. Flag any
reference where the source style omits information the target style requires (e.g. converting a
numbered list with abbreviated journals into an author–date style that spells them out — you may
need to expand abbreviations and should flag any you cannot resolve confidently).

**Never invent** authors, years, DOIs, page ranges, or publisher details. If a field is missing
from the source, leave a clear `[missing: <field>]` placeholder and list it at the end. Filling
a field is the job of `citation-check` (which resolves it against the published record), not this
skill — flag, don't guess.

---

## Applying a target style that is not the built-in default

The entry templates in §5 are written for the CSIRO Harvard author–date default. To apply a
different journal style, take §5 as the structural template (which fields each entry type needs)
and re-skin it with the Step 0 decisions. The common transformations:

- **To a numbered style (Vancouver/CSE citation–sequence):** replace in-text `(Author Year)`
  with the citation number; move the year to the journal-style position; abbreviate journal
  names if the journal requires it; renumber the list in order of first appearance.
- **To APA:** `Surname, F. M.` author form, `&` before the last author, year in parentheses,
  sentence-case article titles, title-case journal names, issue number in parentheses after the
  volume, `https://doi.org/…` DOI form.
- **To another author–date variant:** usually only the punctuation of the author list, the
  `and`/`&` choice, the `et al.` threshold, and the issue-number/DOI conventions change — the
  rest of §5 carries over.

If the journal's instructions are silent on a detail, fall back to the §5 default for that
detail and note it.

---

## General rules (apply in every style)

- All references in the list must be cited in the text, and all in-text citations must appear in
  the list. (The two-way cross-check itself is owned by `reference-check`, not this skill — but
  flag any mismatch you happen to see.)
- Be **internally consistent**: one journal-name convention, one DOI form, one title-case rule,
  one page-range dash — applied uniformly across the whole list.
- If several references share author and year, differentiate with letter suffixes (`2023a`,
  `2023b`); style decides whether the letter is italic.
- Do not abbreviate journal names unless the target style requires it; if it does, use the
  official ISO 4 / NLM abbreviation, not an ad-hoc shortening.

---

## §5 — Built-in default: CSIRO Harvard author–date

Apply this variant when the target journal uses an author–date style, or when no style is
specified. It is adapted from CSIRO Publishing's "Harvard references: Details and examples for
journal authors"; defer to the target journal's instructions where they differ.

### 5.1 In-text citations

- Author and date: `(Smith 2024)`.
- Two or more references together, in **chronological** order, semicolon-separated:
  `(Bloggs 2017; Doe 2024)`; same year → alphabetical: `(Doe 2024; Smith 2024)`.
- Two co-authors linked with "and": `(Doe and Smith 2023)`.
- Three or more authors: first author + italic `*et al.*`: `(Smith *et al.* 2024)`.
- Direct quote takes a page number: `(Smith *et al.* 2024, p. 6)`.

### 5.2 Reference-list entry formats

Each type is shown with a worked example.

**5.2.1 Journal article (page range)** — `Author(s) (Year). Title. *Journal Name* Volume:page–page. doi:…`
> Povh LF, Willers N, Fleming PA (2023). Set free: an evaluation of two break-away mechanisms for tracking collars. *Wildlife Research* 50:782–291. doi:10.1071/WR21176

**5.2.2 Journal article (article ID)** — used when the journal assigns an article ID rather than pages.
> Franz SC, Colavito MM, Edgeley CM (2024). From flexibility to feasibility: identifying the policy conditions that support the management of wildfire for objectives other than full suppression. *International Journal of Wildland Fire* 33:WF24031. doi:10.1071/WF24031

**5.2.3 Preprint** — mark `[Preprint]` before the server.
> Corcoran AJ, Schirmacher MR, Black E, Hedrick TL (2021) ThruTracker: open-source software for 2-D and 3-D animal video tracking. [Preprint] bioRxiv. doi:10.1101/2021.05.12.443854

**5.2.4 Dataset** — include version if available; mark `[Dataset]`.
> Fiddes S, Pepler A, Saunders K, Hope P (2020). Southern Australia's climate regions. (Version 1.0.0) [Dataset] Zenodo. doi:10.5281/zenodo.4265471

**5.2.5 Book** — title italic; edition after title; publisher and location in parentheses.
> Lezak MD (1983). *Neuropsychological assessment*, 2nd edn. (Oxford University Press: New York, NY, USA)

**5.2.6 Book chapter** — chapter title unquoted; book title italic, preceded by page numbers and "in"; editors `(Eds …)`, then publisher.
> Gill AM, Bradstock R (2003). Fire regimes and biodiversity: a set of postulates. Pp 15-25 in *Australia burning: Fire ecology, policy and management issues*. (Eds G Cary, D Lindenmayer, S Dovers) (CSIRO Publishing: Melbourne, Vic, Australia)

**5.2.7 Thesis** — degree, institution, location; italicise scientific names in the title.
> Purcell BV (2010). Order in the pack: ecology of *Canis lupus* dingo in the southern Greater Blue Mountains World Heritage Area. PhD Thesis, University of Western Sydney, NSW, Australia.

**5.2.8 Report / part of a report / bulletin** — report number, series, issuing body, location.
> Bradshaw FJ (2015). Reference material for karri forest silviculture. Technical Report FEM067. Forest Management Series. Department of Parks and Wildlife, Perth.

For a chapter or part of a larger report, treat like a book chapter:
> IPCC (2022). Summary for Policymakers. pp. 3–48. in *Climate Change 2022: Mitigation of Climate Change. Contribution of Working Group III to the Sixth Assessment Report of the Intergovernmental Panel on Climate Change* (Eds PR Shukla, J Skea, R Slade, A Al Khourdajie, R van Diemen, D McCollum, M Pathak, S Some, P Vyas, R Fradera, M Belkacemi, A Hasija, G Lisboa, S Luz, J Malley) (Cambridge University Press, Cambridge, UK and New York, NY, USA) doi:10.1017/9781009157926.001

**5.2.9 Conference proceedings** — proceedings title in quotes, preceded by page numbers and "in"; dates and location; editors; publisher.
> Robinson RM (2005). Volume loss in thinned karri regrowth infected by *Armillaria luteobubalina* in Western Australia. Pp. 296–303 in *Proceedings of the 11th IUFRO International Conference on Root and Butt Rots of Forest Trees*, 16–22 August 2004, Poznan and Bialowieza, Poland. (Eds M Manka, P Lakony) (The August Cieszkowski Agricultural University: Poznan, Poland)

**5.2.10 Web-based material** — prefer DOI; otherwise full URL and access date.
> Stroke Foundation (2023). Clinical Guidelines for Stroke Management. Available at https://informme.org.au/Guidelines/Clinical-Guidelines-for-Stroke-Management [accessed 13 November 2023]
> Dunne S, Fletcher A, Bradbury C (2024). Life after lockdown: loneliness, exclusion, and the impact of hidden disability. doi:10.17605/OSF.IO/MYFH4

**5.2.11 Standard** — standard code, issuing body, location; URL if online.
> ISO (2022). Environmental management — Guidelines for environmental due diligence assessment. ISO14015:2022. International Organization for Standardization: Geneva. Available at https://www.iso.org/standard/78014.html

**5.2.12 Patent** — patent number, issuing office, URL.
> Ghatak S (2019). Immunization testing system (U.S. Patent No. 10,788,482). U.S. Patent and Trademark Office. Available at https://rb.gy/ik0fb0

### 5.3 Formatting conventions (the details reviewers flag)

- **Author names:** surname then initials, no periods or spaces (`Smith JA`).
- **Year:** in parentheses after the author list, then a period and a space before the title.
- **Title:** sentence case; no terminal period before the journal for articles; terminal period
  for books, theses, reports.
- **Journal name:** italic, full (never abbreviated).
- **Volume/issue:** issue number omitted unless pagination restarts each issue.
- **Pages:** en-dash (–), not hyphen; no `pp.` for journal articles; `pp.` for book chapters,
  reports, proceedings.
- **DOI:** lower-case `doi:` prefix, no space, no trailing period; not wrapped in
  `https://doi.org/`.
- **Editors:** `(Eds AB Smith, CD Jones)`; one editor → `(Ed. AB Smith)`.
- **Scientific names:** italicise genus and species wherever they appear.
- **Ampersand:** never; always "and".
- **Ellipses:** never used to truncate author lists.
- **Same author/year:** italic letter suffixes (`Smith JA (2023a)`), ordered by text appearance
  or alphabetically by title.

### 5.4 Common errors to flag on review

Abbreviated journal names where the style spells out; hyphens in page ranges; missing DOIs where
one exists; `et al.` in the list below the style's author threshold; ellipses for omitted
authors; in-text `&` where the style uses "and"; references in text but not the list (or vice
versa); same-year same-author without `a`/`b`; non-chronological multi-citation groups; issue
numbers where pagination is continuous; `pp.` misuse.

---

## Source

The default variant in §5 is modified from CSIRO Publishing's "Harvard references: Details and
examples for journal authors". For any submission, the target journal's author instructions take
precedence — capture them in Step 0 and apply them over this default where they differ.
