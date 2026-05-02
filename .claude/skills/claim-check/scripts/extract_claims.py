#!/usr/bin/env python3
"""Extract (citation_key, carrying_sentence, line_number) triples from a markdown draft.

Recognises three citation styles in the draft body:
  1. Author-year prose: (Smith 2023), (Smith and Jones 2023), (Smith et al. 2023),
     (Smith et al., 2023), Smith (2023), Smith et al. (2023).
  2. Pandoc citeproc: [@smith2023], [@smith2023; @jones2024], @smith2023.
  3. Compound parenthetical: (Smith 2023; Jones 2024), split into one row per source.

The "carrying sentence" is the full sentence in which the citation appears. Sentences are
delimited by .!? followed by whitespace. Markdown formatting (emphasis, links) is
preserved in the carrying sentence so the calling agent can locate it in the draft.

Output: TSV on stdout with header row `citation_key\\tcarrying_sentence\\tline_number`.

Reference-list entries are skipped: any line at or after a heading whose text is one of
{References, REFERENCES, Bibliography, BIBLIOGRAPHY, Works cited} is ignored.

Usage:
  python extract_claims.py <draft.md>
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REFERENCES_HEADING = re.compile(
    r"^#{1,6}\s+(References|REFERENCES|Bibliography|BIBLIOGRAPHY|Works cited)\s*$"
)

# Author-year citations.
# Forms covered:
#   (Smith 2023)            (Smith, 2023)
#   (Smith and Jones 2023)  (Smith & Jones, 2023)
#   (Smith et al. 2023)     (Smith et al., 2023)
# We deliberately accept either a comma or no comma between author and year.
AUTHOR_YEAR_PAREN = re.compile(
    r"\("
    r"(?P<entries>"
    r"[A-Z][A-Za-z\-']+(?:\s+(?:and|&)\s+[A-Z][A-Za-z\-']+|\s+et\s+al\.?)?,?\s+\d{4}[a-z]?"
    r"(?:\s*;\s*"
    r"[A-Z][A-Za-z\-']+(?:\s+(?:and|&)\s+[A-Z][A-Za-z\-']+|\s+et\s+al\.?)?,?\s+\d{4}[a-z]?"
    r")*"
    r")"
    r"\)"
)

#   Smith (2023), Smith and Jones (2023), Smith et al. (2023)
AUTHOR_YEAR_NARRATIVE = re.compile(
    r"(?P<author>"
    r"[A-Z][A-Za-z\-']+(?:\s+(?:and|&)\s+[A-Z][A-Za-z\-']+|\s+et\s+al\.?)?"
    r")\s*\((?P<year>\d{4}[a-z]?)\)"
)

# Pandoc citeproc keys: [@smith2023], @smith2023, [@smith2023; @jones2024]
CITEPROC_BRACKET = re.compile(r"\[@([^\]]+)\]")
# Excludes `[` from the negative lookbehind so `[@key]` is not double-matched
# by both the bracket and bare patterns.
CITEPROC_BARE = re.compile(r"(?<![\w@\[])@([A-Za-z0-9][A-Za-z0-9_:.\-]*)")

# Common abbreviations whose trailing period should NOT be treated as sentence-end.
ABBREVIATIONS = frozenset({"al", "Al", "AL", "e.g", "i.e", "cf", "Fig", "fig", "Eq", "eq", "Tab", "tab", "St", "Mt", "Mr", "Mrs", "Dr", "Prof", "Jr", "Sr"})

ENTRY_SPLIT = re.compile(r"\s*;\s*")


def normalise_author_year_to_key(entry: str) -> str:
    """Convert 'Smith et al. 2023' or 'Smith, 2023' into a stable bib-style key.

    'Smith 2023'           -> 'smith2023'
    'Smith and Jones 2023' -> 'smith_jones2023'
    'Smith et al. 2023'    -> 'smith_etal2023'
    'Smith, 2023a'         -> 'smith2023a'
    """
    entry = entry.strip().rstrip(",")
    m = re.match(
        r"(?P<a1>[A-Z][A-Za-z\-']+)"
        r"(?:\s+(?:and|&)\s+(?P<a2>[A-Z][A-Za-z\-']+)|\s+et\s+al\.?)?"
        r",?\s+(?P<year>\d{4}[a-z]?)$",
        entry,
    )
    if not m:
        return entry.lower().replace(" ", "_")
    a1 = m.group("a1").lower()
    a2 = m.group("a2")
    if "et al" in entry:
        return f"{a1}_etal{m.group('year')}"
    if a2:
        return f"{a1}_{a2.lower()}{m.group('year')}"
    return f"{a1}{m.group('year')}"


def split_into_sentences(line_text: str) -> list[tuple[int, int, str]]:
    """Return [(start_idx, end_idx, sentence_text), ...] for a single line.

    A `.` is a sentence boundary unless the preceding token is a known
    abbreviation (e.g. `et al.`, `e.g.`, `Fig.`).
    """
    out: list[tuple[int, int, str]] = []
    start = 0
    i = 0
    n = len(line_text)
    while i < n:
        ch = line_text[i]
        if ch in ".!?" and (i + 1 == n or line_text[i + 1].isspace()):
            # Look back for the token preceding the period.
            j = i - 1
            while j >= 0 and (line_text[j].isalnum() or line_text[j] == "."):
                j -= 1
            preceding = line_text[j + 1 : i]
            if ch == "." and preceding in ABBREVIATIONS:
                i += 1
                continue
            end = i + 1
            sentence = line_text[start:end].strip()
            if sentence:
                out.append((start, end, sentence))
            start = end
        i += 1
    tail = line_text[start:].strip()
    if tail:
        out.append((start, len(line_text), tail))
    return out


def find_carrying_sentence(line_text: str, citation_offset: int) -> str:
    for s, e, sent in split_into_sentences(line_text):
        if s <= citation_offset < e:
            return sent
    return line_text.strip()


def extract(md_path: Path) -> list[tuple[str, str, int]]:
    rows: list[tuple[str, str, int]] = []
    in_references = False
    with md_path.open("r", encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, start=1):
            line = raw.rstrip("\n")
            if REFERENCES_HEADING.match(line):
                in_references = True
                continue
            if in_references:
                continue
            for m in AUTHOR_YEAR_PAREN.finditer(line):
                entries = ENTRY_SPLIT.split(m.group("entries"))
                sentence = find_carrying_sentence(line, m.start())
                for entry in entries:
                    key = normalise_author_year_to_key(entry)
                    rows.append((key, sentence, lineno))
            for m in AUTHOR_YEAR_NARRATIVE.finditer(line):
                key = normalise_author_year_to_key(
                    f"{m.group('author')} {m.group('year')}"
                )
                sentence = find_carrying_sentence(line, m.start())
                rows.append((key, sentence, lineno))
            for m in CITEPROC_BRACKET.finditer(line):
                keys = [k.strip().lstrip("@") for k in m.group(1).split(";")]
                sentence = find_carrying_sentence(line, m.start())
                for k in keys:
                    if k:
                        rows.append((k, sentence, lineno))
            # Bare @key — skip when preceded by an open bracket (already handled)
            # by virtue of the negative lookbehind in the pattern.
            for m in CITEPROC_BARE.finditer(line):
                k = m.group(1)
                if k:
                    sentence = find_carrying_sentence(line, m.start())
                    rows.append((k, sentence, lineno))
    return rows


def main() -> int:
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: extract_claims.py <draft.md>\n")
        return 2
    md = Path(sys.argv[1])
    if not md.exists():
        sys.stderr.write(f"Draft not found: {md}\n")
        return 2
    rows = extract(md)
    sys.stdout.write("citation_key\tcarrying_sentence\tline_number\n")
    for key, sent, lineno in rows:
        # Tabs and newlines in sentences would corrupt the TSV; substitute spaces.
        clean = sent.replace("\t", " ").replace("\n", " ")
        sys.stdout.write(f"{key}\t{clean}\t{lineno}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
