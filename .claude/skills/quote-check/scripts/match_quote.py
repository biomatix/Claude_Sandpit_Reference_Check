#!/usr/bin/env python3
"""Decide whether a quotation appears verbatim in a source, and on which page.

Implements the sandpit's quotation rules:

  * Verbatim, punctuation retained — comparison is CHARACTER-level (after light
    normalisation: NFKC, typographic quotes -> straight, dash variants -> hyphen,
    whitespace runs -> one space). A changed comma or word is therefore a departure.
  * Ellipsis (`…` / `...`) marks an elision — at the start, the end, or within a quote.
    The quote is split on ellipsis into segments; each segment must occur, in order,
    on the same page, with arbitrary text in the gaps.
  * `[bracketed]` editorial material and `[sic]` cannot be verbatim-matched (they are
    the author's, not the source's). The bracket span — and a single word immediately
    before `[sic]` — are blanked out of the verbatim test, and `had_editorial` is set so
    the caller asks for a human eye on those spots.

Page locus: with `--pdf`, text is extracted per page (pdftotext, form-feed separated);
the match reports the 1-based PDF page index and any printed page numbers detected in the
running head/foot of that page, for the caller to compare against the cited page. With
`--text`, `page_aware` is false and the page cannot be verified.

Output: one JSON object on stdout.

Usage:
  python match_quote.py --quote "<text>" --pdf  <path> [--cited-pages 72]
  python match_quote.py --quote "<text>" --text <path> [--cited-pages 72]
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

ELLIPSIS = re.compile(r"\s*(?:…|\.\s*\.\s*\.)\s*")
BRACKETS = re.compile(r"\[[^\]]*\]")
WORD = re.compile(r"\w+(?:[-'’]\w+)*")
RATIO_REPORT = 0.60  # below this similarity, report "not found" rather than "altered"

_TRANS = {0x201C: 34, 0x201D: 34, 0x201E: 34, 0x201F: 34,
          0x2018: 39, 0x2019: 39, 0x201A: 39, 0x201B: 39,
          0x2013: 45, 0x2014: 45, 0x2212: 45, 0x2012: 45, 0x2010: 45}


def normalise(s: str) -> str:
    s = unicodedata.normalize("NFKC", s).translate(_TRANS)
    return re.sub(r"\s+", " ", s).strip()


def prep_quote(quote: str):
    """Return (segments, had_editorial). Editorial material — a `[sic]`-flagged word and
    any other `[bracketed]` insertion — cannot be matched against the source, so it is
    turned into an elision point (handled like an ellipsis gap). The quote is then split
    on every ellipsis into segments that ARE verifiable verbatim, in order."""
    had_editorial = bool(BRACKETS.search(quote))
    # A [sic]-flagged word and the marker together become a gap.
    q = re.sub(r"\S+\s*\[\s*sic\s*\]", " … ", quote, flags=re.IGNORECASE)
    q = BRACKETS.sub(" … ", q)  # any remaining [editorial] insertion becomes a gap
    segs = [normalise(s) for s in ELLIPSIS.split(q)]
    segs = [s for s in segs if s]
    return segs, had_editorial


def ordered_substrings(hay: str, segs: list[str], ci: bool):
    """True if every segment occurs in hay, in order. Returns (ok, first_idx)."""
    h = hay.lower() if ci else hay
    pos, first = 0, None
    for seg in segs:
        s = seg.lower() if ci else seg
        idx = h.find(s, pos)
        if idx < 0:
            return (False, None)
        if first is None:
            first = idx
        pos = idx + len(s)
    return (True, first)


def first_letter_only(hay: str, segs: list[str]):
    """When a case-insensitive match holds, is the ONLY case difference the quote's first letter?"""
    # Reconstruct the matched source substrings and compare char-by-char.
    h = hay.lower()
    pos = 0
    diffs = 0
    first_letter_adjusted = False
    for si, seg in enumerate(segs):
        idx = h.find(seg.lower(), pos)
        src = hay[idx:idx + len(seg)]
        for ci_, (a, b) in enumerate(zip(src, seg)):
            if a != b:
                if si == 0 and ci_ == 0 and a.lower() == b.lower():
                    first_letter_adjusted = True
                else:
                    diffs += 1
        pos = idx + len(seg)
    return diffs == 0, first_letter_adjusted


def token_diff(src_tokens, qt_tokens):
    out = []
    s = difflib.SequenceMatcher(autojunk=False, a=src_tokens, b=qt_tokens)
    for tag, i1, i2, j1, j2 in s.get_opcodes():
        if tag == "replace":
            out.append(f"source “{' '.join(src_tokens[i1:i2])}” → quote “{' '.join(qt_tokens[j1:j2])}”")
        elif tag == "delete":
            out.append(f"quote drops “{' '.join(src_tokens[i1:i2])}”")
        elif tag == "insert":
            out.append(f"quote adds “{' '.join(qt_tokens[j1:j2])}”")
    return out


def best_window(page_tokens, qt_tokens):
    if not qt_tokens or not page_tokens:
        return (0.0, -1)
    w = len(qt_tokens)
    sm = difflib.SequenceMatcher(autojunk=False)
    sm.set_seq2(qt_tokens)
    best = (0.0, -1)
    for i in range(0, max(1, len(page_tokens) - w + 1)):
        sm.set_seq1(page_tokens[i:i + w])
        r = sm.ratio()
        if r > best[0]:
            best = (r, i)
    return best


def printed_page_hints(raw_page: str) -> list[int]:
    lines = [ln.strip() for ln in raw_page.splitlines() if ln.strip()]
    hints, seen = [], set()
    for ln in lines[:3] + lines[-3:]:
        if len(ln) <= 12 or re.search(r"(?i)\bpage\b", ln):
            for m in re.finditer(r"\b(\d{1,4})\b", ln):
                v = int(m.group(1))
                if v not in seen:
                    seen.add(v)
                    hints.append(v)
    return hints


def pdf_pages(pdf: Path) -> list[str]:
    try:
        res = subprocess.run(
            ["pdftotext", "-layout", "-enc", "UTF-8", str(pdf), "-"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120,
        )
    except FileNotFoundError:
        sys.stderr.write("pdftotext not found on PATH — install poppler-utils\n")
        return []
    if res.returncode != 0:
        sys.stderr.write(f"pdftotext failed: {res.stderr.strip()}\n")
        return []
    return res.stdout.split("\f")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--quote", required=True)
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--pdf")
    src.add_argument("--text")
    p.add_argument("--cited-pages", default="")
    args = p.parse_args()

    segs, had_editorial = prep_quote(args.quote)
    out = {
        "source": "pdf" if args.pdf else "text",
        "page_aware": bool(args.pdf),
        "cited_pages": args.cited_pages or None,
        "had_editorial": had_editorial,
        "found": False,
        "verbatim": False,
        "method": "none",
        "first_letter_case_adjusted": False,
        "match_pdf_page": None,
        "printed_page_hints": [],
        "alterations": [],
        "best_ratio": 0.0,
        "note": "",
    }

    if not segs:
        out["note"] = "quote has no comparable text after removing editorial brackets"
        print(json.dumps(out, ensure_ascii=False))
        return 0

    if args.pdf:
        raw_pages = pdf_pages(Path(args.pdf))
        if not raw_pages or not any(rp.strip() for rp in raw_pages):
            out["note"] = "no extractable text in PDF (missing, image-only scan, or pdftotext absent)"
            print(json.dumps(out, ensure_ascii=False))
            return 0
    else:
        tp = Path(args.text)
        if not tp.exists() or tp.stat().st_size == 0:
            out["note"] = "source text file missing or empty"
            print(json.dumps(out, ensure_ascii=False))
            return 0
        raw_pages = [tp.read_text(encoding="utf-8", errors="replace")]

    norm_pages = [normalise(rp) for rp in raw_pages]

    # Pass 1 — character-exact, case-sensitive, ordered segments.
    for i, np in enumerate(norm_pages):
        ok, _ = ordered_substrings(np, segs, ci=False)
        if ok:
            out.update(found=True, verbatim=True, match_pdf_page=i + 1,
                       method="ellipsis-segments" if len(segs) > 1 else "exact",
                       printed_page_hints=printed_page_hints(raw_pages[i]))
            out["note"] = ("verbatim match"
                           + ("; editorial [sic]/[…] present — confirm the bracketed text by hand"
                              if had_editorial else ""))
            print(json.dumps(out, ensure_ascii=False))
            return 0

    # Pass 2 — case-insensitive: separate an allowed first-letter change from a real case alteration.
    for i, np in enumerate(norm_pages):
        ok, _ = ordered_substrings(np, segs, ci=True)
        if ok:
            clean, fl_adj = first_letter_only(np, segs)
            if clean:
                out.update(found=True, verbatim=True, match_pdf_page=i + 1, method="exact",
                           first_letter_case_adjusted=fl_adj,
                           printed_page_hints=printed_page_hints(raw_pages[i]))
                out["note"] = ("verbatim (first-letter case adjusted to fit the sentence)"
                               if fl_adj else "verbatim match")
                print(json.dumps(out, ensure_ascii=False))
                return 0
            out.update(found=True, verbatim=False, match_pdf_page=i + 1, method="case",
                       best_ratio=1.0, printed_page_hints=printed_page_hints(raw_pages[i]),
                       alterations=["letter case differs from the source beyond the first letter"])
            out["note"] = "found, but case differs from the source — not verbatim"
            print(json.dumps(out, ensure_ascii=False))
            return 0

    # Pass 3 — fuzzy: closest window, report the word-level departure.
    qt_tokens = WORD.findall(" ".join(segs))
    best = (0.0, -1, -1)  # ratio, page_idx, start
    for i, rp in enumerate(raw_pages):
        pt = WORD.findall(normalise(rp))
        r, start = best_window(pt, qt_tokens)
        if r > best[0]:
            best = (r, i, start)
    ratio, page_idx, start = best
    out["best_ratio"] = round(ratio, 3)
    if ratio >= RATIO_REPORT and page_idx >= 0:
        pt = WORD.findall(normalise(raw_pages[page_idx]))
        diffs = token_diff(pt[start:start + len(qt_tokens)], qt_tokens)
        if not diffs:
            # Every word matches yet the verbatim test failed ⇒ punctuation or spacing differs.
            diffs = ["punctuation or spacing differs from the source (every word matches)"]
        out.update(found=True, verbatim=False, match_pdf_page=page_idx + 1, method="fuzzy",
                   alterations=diffs, printed_page_hints=printed_page_hints(raw_pages[page_idx]))
        out["note"] = "close match — quote departs from the source (see alterations)"
    else:
        out["note"] = "quotation not found in source text"
    print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
