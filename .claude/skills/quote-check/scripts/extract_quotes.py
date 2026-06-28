#!/usr/bin/env python3
"""Extract direct quotations and their citations from a markdown draft.

Encodes the sandpit's house rules for quotation marks so the quote-check workflow can
verify each quotation against its source:

  * Double quotes (`"` / `“…”`) delimit a direct quotation.
  * Single quotes (`'` / `‘…’`) in a draft are ambiguous: house style reserves them for
    emphasis or a quote-within-a-quote, but a draft under audit may still wrap a real
    quotation in them. They are disambiguated by two signals (the caller then flags any
    single-quoted quotation as a single→double conversion):
      - a single-quoted span IMMEDIATELY followed by a citation is a quotation (any length);
      - otherwise, a span of more than a few words (> SINGLE_EMPHASIS_MAX) is a candidate
        quotation (emitted, possibly with no citation — itself a finding); a shorter span
        with no adjacent citation is emphasis and is skipped.
    Apostrophes (contractions/possessives) are not quote marks; the scanner skips a
    `'` that has a letter on both sides.
  * A quotation longer than 30 words is set as indented italics with NO quote marks.
    Such long quotes are therefore detected from markdown italics (`*…*` / `_…_`) and
    block quotes (`>`), not from quote marks.
  * A quotation is followed by a SINGLE source, with the page number after a colon —
    `(Brown, 1996:72)`. This script records the citation, the page locus, the page
    separator actually used (`:` correct, `p` for p./pp., empty if none), and whether
    the citation names a single source, so the caller can flag format departures.

Output: TSV on stdout with header
  `quote\tcitation_key\tcited_pages\tpage_sep\tsingle_source\tkind\twords\tline_number`
`kind` is `inline` (double-quoted), `single` (single-quoted — flag as single→double),
`italic`, or `block`. An empty `citation_key` means no citation was found adjacent to the
quote — itself a finding.

Reference-list lines (at/after a References heading) are skipped.

Usage:
  python extract_quotes.py <draft.md>
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

MIN_WORDS = 4  # a double-quoted span shorter than this, with no citation, is a scare quote
LONG_WORDS = 30  # > this ⇒ house style requires indented italics without quote marks
WINDOW = 160  # how far from a quote to look for its citation
SINGLE_EMPHASIS_MAX = 4  # single-quoted spans of ≤ this many words, with no adjacent citation, are emphasis
IMMEDIATE = 8  # a citation within this many chars of a closing quote counts as "immediately following"

# A single quote may open a quotation only after one of these boundary characters
# (start, whitespace, an opening bracket, or a dash) — never mid-word (an apostrophe).
OPEN_BOUNDARY = set(" \t\r\n([{—–-“\"")

REFERENCES_HEADING = re.compile(
    r"^#{1,6}\s+(References|REFERENCES|Bibliography|BIBLIOGRAPHY|Works cited)\s*$"
)

# Inline direct quotation: straight or typographic double quotes (single quotes excluded).
QUOTE_INLINE = re.compile(r"[\"“]([^\"”“]{1,2000}?)[\"”]")
# Long quote set as italics: a *…* or _…_ span of substantial length.
ITALIC_SPAN = re.compile(r"(?<!\*)\*([^*\n]{40,2000})\*(?!\*)|(?<!_)_([^_\n]{40,2000})_(?!_)")

# One author-year citation entry, optionally with a page locus after ':' or 'p.'/'pp.'.
ENTRY = re.compile(
    r"(?P<author>[A-Z][A-Za-z\-']+(?:\s+(?:and|&)\s+[A-Z][A-Za-z\-']+|\s+et\s+al\.?)?)"
    r",?\s+(?P<year>\d{4}[a-z]?)"
    r"(?:(?P<sep>\s*:\s*|,?\s*pp?\.?\s*)(?P<pages>\d+(?:\s*[-–—]\s*\d+)?))?"
)
CITEPROC = re.compile(
    r"\[@(?P<key>[A-Za-z0-9][A-Za-z0-9_:.\-]*)"
    r"(?:(?P<sep>\s*:\s*|,?\s*pp?\.?\s*)(?P<pages>\d+(?:\s*[-–—]\s*\d+)?))?[^\]]*\]"
)


def author_year_key(author: str, year: str) -> str:
    a = re.split(r"\s+(?:and|&)\s+|\s+et\s+al\.?", author.strip())
    first = a[0].lower()
    if "et al" in author:
        return f"{first}_etal{year}"
    if len(a) > 1 and a[1]:
        return f"{first}_{a[1].lower()}{year}"
    return f"{first}{year}"


def sep_kind(sep: str | None) -> str:
    if not sep:
        return ""
    return ":" if ":" in sep else "p"


def parse_paren_citation(window: str):
    """Find the nearest (...) citation group in window; return dict or None."""
    m = re.search(r"\(([^()]*\b\d{4}[a-z]?\b[^()]*)\)", window)
    if not m:
        return None
    inner = m.group(1)
    parts = re.split(r"\s*;\s*", inner)
    entries = [e for p in parts if (e := ENTRY.search(p))]
    if not entries:
        return None
    # The quote's source is the entry bearing the page locus, else the first.
    chosen = next((e for e in entries if e.group("pages")), entries[0])
    return {
        "pos": m.start(),
        "key": author_year_key(chosen.group("author"), chosen.group("year")),
        "pages": re.sub(r"\s*[-–—]\s*", "-", (chosen.group("pages") or "")),
        "sep": sep_kind(chosen.group("sep")),
        "single": len(parts) == 1,
    }


def parse_citeproc(window: str):
    m = CITEPROC.search(window)
    if not m:
        return None
    # multiple keys ⇒ multi-source
    single = ";" not in window[m.start():m.end()]
    return {
        "pos": m.start(),
        "key": m.group("key"),
        "pages": re.sub(r"\s*[-–—]\s*", "-", (m.group("pages") or "")),
        "sep": sep_kind(m.group("sep")),
        "single": single,
    }


def parse_narrative(window: str):
    """Narrative form just before a quote: 'Brown (1996:72)'."""
    best = None
    for m in ENTRY.finditer(window):
        # require an author-then-(year…) shape near the match
        if "(" in window[max(0, m.start() - 1):m.start() + 60]:
            best = m  # keep last (closest to the quote, which is at window end)
    if not best:
        return None
    return {
        "pos": best.start(),
        "key": author_year_key(best.group("author"), best.group("year")),
        "pages": re.sub(r"\s*[-–—]\s*", "-", (best.group("pages") or "")),
        "sep": sep_kind(best.group("sep")),
        "single": True,
    }


def immediate_citation(full: str, q_end: int):
    """A parenthetical/citeproc citation within IMMEDIATE chars of the closing quote, else None."""
    after = full[q_end:q_end + 48]
    cands = [c for c in (parse_paren_citation(after), parse_citeproc(after))
             if c and c["pos"] <= IMMEDIATE]
    return min(cands, key=lambda c: c["pos"]) if cands else None


def find_single_quoted(body: str):
    """Yield (start, end, inner) for single-quoted spans, skipping apostrophes.

    A `'`/`‘` opens a span only after a boundary character (never mid-word). The matching
    close is the next `'`/`’` that is NOT a contraction apostrophe (a `'` with a letter on
    both sides), within a sane span length."""
    spans, i, n = [], 0, len(body)
    while i < n:
        if body[i] in "'‘":
            prev = body[i - 1] if i > 0 else "\n"
            if prev in OPEN_BOUNDARY:
                j, end = i + 1, None
                while j < n and (j - i) < 1500:
                    if body[j] in "'’":
                        pj = body[j - 1] if j > 0 else " "
                        nj = body[j + 1] if j + 1 < n else "\n"
                        if not (pj.isalpha() and nj.isalpha()):  # not a contraction
                            end = j
                            break
                    j += 1
                if end is not None and end > i + 1:
                    spans.append((i, end + 1, body[i + 1:end]))
                    i = end + 1
                    continue
        i += 1
    return spans


def citation_for(full: str, q_start: int, q_end: int):
    after = full[q_end:min(len(full), q_end + WINDOW)]
    cands = [c for c in (parse_paren_citation(after), parse_citeproc(after)) if c]
    if cands:
        return min(cands, key=lambda c: c["pos"])
    # Narrative lead-in ("Brown (1996:72) wrote, …"): look behind, but only within the
    # quote's own sentence, so a trailing citation from the previous sentence is not stolen.
    before = full[max(0, q_start - WINDOW):q_start]
    bound = list(re.finditer(r"[.!?]\s|\n", before))
    if bound:
        before = before[bound[-1].end():]
    nar = parse_narrative(before)
    if nar and (len(before) - nar["pos"]) <= 60:
        return nar
    return None


def line_of(full: str, offset: int) -> int:
    return full.count("\n", 0, offset) + 1


def references_cutoff(full: str) -> int:
    pos = 0
    for line in full.splitlines(keepends=True):
        if REFERENCES_HEADING.match(line.rstrip("\n")):
            return pos
        pos += len(line)
    return len(full)


def word_count(s: str) -> int:
    return len(re.findall(r"\w+", s))


def emit(rows, quote, kind, cit, lineno):
    quote = re.sub(r"\s+", " ", quote).strip()
    if not quote:
        return
    words = word_count(quote)
    if cit is None and kind == "inline" and words < MIN_WORDS:
        return  # short double-quoted term with no citation — emphasis, not a quotation
    key = cit["key"] if cit else ""
    pages = cit["pages"] if cit else ""
    sep = cit["sep"] if cit else ""
    single = "yes" if (cit and cit["single"]) else ("no" if cit else "")
    rows.append((quote, key, pages, sep, single, kind, words, lineno))


def extract(md_path: Path):
    full = md_path.read_text(encoding="utf-8")
    body = full[:references_cutoff(full)]
    rows: list = []
    claimed: list[tuple[int, int]] = []  # spans already taken as italic/block long quotes

    # Long quotes set as block quotes (runs of '>' lines).
    pos = 0
    block, b_start = [], 0
    for line in body.splitlines(keepends=True):
        if line.lstrip().startswith(">"):
            if not block:
                b_start = pos
            block.append(re.sub(r"^\s*>\s?", "", line).rstrip("\n"))
        elif block:
            text = " ".join(block)
            span_end = b_start + (pos - b_start)
            emit(rows, text, "block", citation_for(body, b_start, span_end), line_of(body, b_start))
            claimed.append((b_start, span_end))
            block = []
        pos += len(line)
    if block:
        text = " ".join(block)
        emit(rows, text, "block", citation_for(body, b_start, len(body)), line_of(body, b_start))
        claimed.append((b_start, len(body)))

    # Long quotes set as italics.
    for m in ITALIC_SPAN.finditer(body):
        quote = m.group(1) or m.group(2)
        if word_count(quote) < LONG_WORDS:
            continue  # short italics are emphasis, not a long quotation
        emit(rows, quote, "italic", citation_for(body, m.start(), m.end()), line_of(body, m.start()))
        claimed.append((m.start(), m.end()))

    # Inline double-quoted quotations (skip any inside an already-claimed italic/block span).
    for m in QUOTE_INLINE.finditer(body):
        if any(s <= m.start() < e for s, e in claimed):
            continue
        emit(rows, m.group(1), "inline", citation_for(body, m.start(), m.end()), line_of(body, m.start()))
        claimed.append((m.start(), m.end()))  # so a quote-within-quote single span is not double-counted

    # Inline single-quoted spans: keep only those that are quotations, not emphasis.
    for s, e, inner in find_single_quoted(body):
        if any(cs <= s < ce for cs, ce in claimed):
            continue  # nested inside a double quote / italic / block — part of that quotation
        imm = immediate_citation(body, e)
        if imm is not None:
            emit(rows, inner, "single", imm, line_of(body, s))  # citation ⇒ a quotation
        elif word_count(inner) > SINGLE_EMPHASIS_MAX:
            emit(rows, inner, "single", citation_for(body, s, e), line_of(body, s))  # long ⇒ candidate
        # else: short, no adjacent citation ⇒ emphasis — skip

    rows.sort(key=lambda r: r[-1])
    return rows


def main() -> int:
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: extract_quotes.py <draft.md>\n")
        return 2
    md = Path(sys.argv[1])
    if not md.exists():
        sys.stderr.write(f"Draft not found: {md}\n")
        return 2
    rows = extract(md)
    sys.stdout.write("quote\tcitation_key\tcited_pages\tpage_sep\tsingle_source\tkind\twords\tline_number\n")
    for quote, key, pages, sep, single, kind, words, lineno in rows:
        sys.stdout.write(
            f"{quote.replace(chr(9), ' ')}\t{key}\t{pages}\t{sep}\t{single}\t{kind}\t{words}\t{lineno}\n"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
