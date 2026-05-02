#!/usr/bin/env python3
"""Score and surface the top candidate supporting passages from a source text.

Given a claim sentence and the path to extracted source text (produced by
resolve_full_text.py), return the top-N passages most likely to support or
contradict the claim, ranked by content-word overlap with the claim.

This script does NOT decide whether the source supports the claim — that judgement
requires reading the candidates and is left to the calling LLM. The script's job
is purely to surface the right windows of the source so the LLM doesn't have to
read the whole paper.

Output: JSON on stdout:
  {
    "candidates": [
      {"score": 0.42, "page_hint": null, "passage": "...", "source_offset": 1234},
      ...
    ],
    "best_score": 0.42,
    "below_threshold": false,
    "threshold": 0.10
  }

Usage:
  python find_passage.py --claim "<sentence>" --text <path> [--top 3] [--window 3]

  --window N  number of consecutive sentences per candidate passage (default 3)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

STOP_WORDS = frozenset(
    """
a about above after again against all am an and any are as at be because been before being
below between both but by can could did do does doing down during each few for from further
had has have having he her here hers herself him himself his how however i if in into is it
its itself just may me might more most must my myself no nor not now of off on once only or
other our ours ourselves out over own s same shall she should so some such t than that the
their theirs them themselves then there these they this those through to too under until up
upon us very was we were what when where which while who whom why will with within without
would you your yours yourself yourselves
""".split()
)

WORD_RE = re.compile(r"[A-Za-z][A-Za-z\-']{2,}")
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z\d])")
DEFAULT_THRESHOLD = 0.10


def content_words(text: str) -> list[str]:
    return [
        w.lower() for w in WORD_RE.findall(text) if w.lower() not in STOP_WORDS and len(w) > 2
    ]


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    return [s.strip() for s in SENTENCE_RE.split(text) if s.strip()]


def score(claim_words: set[str], passage_words: list[str]) -> float:
    if not claim_words:
        return 0.0
    if not passage_words:
        return 0.0
    pw = set(passage_words)
    overlap = len(claim_words & pw)
    return overlap / len(claim_words)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--claim", required=True)
    p.add_argument("--text", required=True)
    p.add_argument("--top", type=int, default=3)
    p.add_argument("--window", type=int, default=3)
    p.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    args = p.parse_args()

    text_path = Path(args.text)
    if not text_path.exists() or text_path.stat().st_size == 0:
        sys.stdout.write(
            json.dumps({"candidates": [], "best_score": 0.0, "below_threshold": True, "threshold": args.threshold})
            + "\n"
        )
        return 0

    claim_words = set(content_words(args.claim))
    if not claim_words:
        sys.stderr.write("claim has no content words after stop-word removal\n")
        return 2

    sentences = split_sentences(text_path.read_text(encoding="utf-8"))
    if not sentences:
        sys.stdout.write(
            json.dumps({"candidates": [], "best_score": 0.0, "below_threshold": True, "threshold": args.threshold})
            + "\n"
        )
        return 0

    scored: list[tuple[float, int, str]] = []
    n = len(sentences)
    w = max(1, args.window)
    for i in range(n - w + 1):
        passage = " ".join(sentences[i : i + w])
        s = score(claim_words, content_words(passage))
        if s > 0:
            scored.append((s, i, passage))

    scored.sort(key=lambda r: (-r[0], r[1]))
    best = scored[: args.top]
    best_score = best[0][0] if best else 0.0
    out = {
        "candidates": [
            {"score": round(s, 3), "page_hint": None, "passage": passage, "source_offset": offset}
            for s, offset, passage in best
        ],
        "best_score": round(best_score, 3),
        "below_threshold": best_score < args.threshold,
        "threshold": args.threshold,
    }
    sys.stdout.write(json.dumps(out) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
