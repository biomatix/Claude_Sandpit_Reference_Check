#!/usr/bin/env python3
"""Resolve a DOI to the best-available cited content for claim verification.

Priority order:
  1. Local PDF at <local-dir>/<citation-key>.pdf — caller-supplied override.
  2. Open-access PDF or HTML via Unpaywall (https://api.unpaywall.org).
  3. Preprint mirror: bioRxiv (via DOI prefix), Europe PMC (via DOI), arXiv.
  4. CrossRef abstract (https://api.crossref.org/works/<doi>).
  5. PubMed abstract (E-utilities, biomedical only).

Extracted plain text is cached at <cache-dir>/<citation-key>.txt so repeat runs
skip re-fetch and re-extraction.

Output: a single JSON object on stdout, e.g.
  {"kind": "open_access_pdf",
   "text_path": "outputs/.claim_check_cache/smith2023.txt",
   "source_url": "https://example.org/smith2023.pdf"}

Possible kinds: local_pdf, open_access_pdf, open_access_html, preprint,
                abstract_only, not_found.

Usage:
  python resolve_full_text.py --doi <DOI> --citation-key <KEY> \
    [--local-dir <DIR>] [--cache-dir <DIR>] [--email <EMAIL>]

Environment:
  CLAIM_CHECK_EMAIL  used as the Unpaywall and NCBI contact email (recommended;
                     CrossRef etiquette and Unpaywall require it).

This script depends only on the standard library plus optional `pypdf` for PDF
text extraction. If pypdf is unavailable, PDFs are returned as `not_found`.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import urllib.parse
import urllib.request
from pathlib import Path

DEFAULT_CACHE = "outputs/.claim_check_cache"
USER_AGENT = "claim-check/1.0 (mailto:{email})"
TIMEOUT = 30


def fetch(url: str, email: str, accept: str = "*/*") -> tuple[bytes, str]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT.format(email=email),
            "Accept": accept,
        },
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.read(), r.headers.get("Content-Type", "")


def extract_pdf_text(pdf_bytes: bytes) -> str | None:
    try:
        import pypdf
    except ImportError:
        return None
    import io

    try:
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        return "\n".join((p.extract_text() or "") for p in reader.pages)
    except Exception:
        return None


def strip_html(html: str) -> str:
    # Drop <script> and <style> blocks.
    html = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    html = re.sub(r"<style[\s\S]*?</style>", " ", html, flags=re.I)
    # Replace block tags with newlines so paragraph structure survives.
    html = re.sub(r"<(?:p|br|div|li|h\d|tr)\b[^>]*>", "\n", html, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&lt;", "<", text)
    text = re.sub(r"&gt;", ">", text)
    text = re.sub(r"\s+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def write_cache(cache_dir: Path, key: str, text: str) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    out = cache_dir / f"{key}.txt"
    out.write_text(text, encoding="utf-8")
    return out


def try_local_pdf(local_dir: Path, key: str, cache_dir: Path) -> dict | None:
    candidate = local_dir / f"{key}.pdf"
    if not candidate.exists():
        return None
    text = extract_pdf_text(candidate.read_bytes())
    if not text or len(text.strip()) < 200:
        return {
            "kind": "local_pdf_extraction_failed",
            "text_path": None,
            "source_url": str(candidate),
        }
    text_path = write_cache(cache_dir, key, text)
    return {
        "kind": "local_pdf",
        "text_path": str(text_path),
        "source_url": str(candidate),
    }


def try_unpaywall(doi: str, key: str, cache_dir: Path, email: str) -> dict | None:
    try:
        url = f"https://api.unpaywall.org/v2/{urllib.parse.quote(doi)}?email={urllib.parse.quote(email)}"
        body, _ = fetch(url, email, accept="application/json")
        data = json.loads(body.decode("utf-8"))
    except Exception:
        return None
    best = data.get("best_oa_location") or {}
    pdf_url = best.get("url_for_pdf")
    landing = best.get("url_for_landing_page") or best.get("url")
    if pdf_url:
        try:
            pdf_bytes, _ = fetch(pdf_url, email, accept="application/pdf")
            text = extract_pdf_text(pdf_bytes)
            if text and len(text.strip()) >= 200:
                text_path = write_cache(cache_dir, key, text)
                return {
                    "kind": "open_access_pdf",
                    "text_path": str(text_path),
                    "source_url": pdf_url,
                }
        except Exception:
            pass
    if landing:
        try:
            html_bytes, ctype = fetch(landing, email, accept="text/html")
            if "html" in ctype.lower():
                text = strip_html(html_bytes.decode("utf-8", errors="replace"))
                if text and len(text.strip()) >= 200:
                    text_path = write_cache(cache_dir, key, text)
                    return {
                        "kind": "open_access_html",
                        "text_path": str(text_path),
                        "source_url": landing,
                    }
        except Exception:
            pass
    return None


def try_europepmc(doi: str, key: str, cache_dir: Path, email: str) -> dict | None:
    try:
        q = urllib.parse.quote(f'DOI:"{doi}"')
        url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={q}&format=json"
        body, _ = fetch(url, email, accept="application/json")
        data = json.loads(body.decode("utf-8"))
        hits = data.get("resultList", {}).get("result", [])
        if not hits:
            return None
        hit = hits[0]
        pmcid = hit.get("pmcid")
        if not pmcid:
            return None
        full = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
        body, ctype = fetch(full, email, accept="application/xml")
        text = strip_html(body.decode("utf-8", errors="replace"))
        if text and len(text.strip()) >= 200:
            text_path = write_cache(cache_dir, key, text)
            return {
                "kind": "preprint",
                "text_path": str(text_path),
                "source_url": full,
            }
    except Exception:
        return None
    return None


def try_crossref_abstract(doi: str, key: str, cache_dir: Path, email: str) -> dict | None:
    try:
        url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}"
        body, _ = fetch(url, email, accept="application/json")
        data = json.loads(body.decode("utf-8"))
    except Exception:
        return None
    abstract = data.get("message", {}).get("abstract")
    if not abstract:
        return None
    text = strip_html(abstract)
    if not text or len(text.strip()) < 50:
        return None
    text_path = write_cache(cache_dir, key, text)
    return {
        "kind": "abstract_only",
        "text_path": str(text_path),
        "source_url": url,
    }


def try_pubmed_abstract(doi: str, key: str, cache_dir: Path, email: str) -> dict | None:
    try:
        # Map DOI to PMID via E-utilities esearch.
        q = urllib.parse.quote(f"{doi}[doi]")
        s = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={q}&retmode=json&email={urllib.parse.quote(email)}"
        body, _ = fetch(s, email, accept="application/json")
        ids = json.loads(body.decode("utf-8")).get("esearchresult", {}).get("idlist", [])
        if not ids:
            return None
        pmid = ids[0]
        f_url = (
            f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            f"?db=pubmed&id={pmid}&rettype=abstract&retmode=text&email={urllib.parse.quote(email)}"
        )
        body, _ = fetch(f_url, email, accept="text/plain")
        text = body.decode("utf-8", errors="replace").strip()
        if not text or len(text) < 50:
            return None
        text_path = write_cache(cache_dir, key, text)
        return {
            "kind": "abstract_only",
            "text_path": str(text_path),
            "source_url": f_url,
        }
    except Exception:
        return None


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--doi", required=True)
    p.add_argument("--citation-key", required=True)
    p.add_argument("--local-dir", default=None)
    p.add_argument("--cache-dir", default=DEFAULT_CACHE)
    p.add_argument(
        "--email",
        default=os.environ.get("CLAIM_CHECK_EMAIL", "anonymous@example.com"),
    )
    args = p.parse_args()

    doi = args.doi.strip().lstrip("https://doi.org/").lstrip("doi.org/")
    key = args.citation_key.strip()
    cache_dir = Path(args.cache_dir)

    cached = cache_dir / f"{key}.txt"
    if cached.exists() and cached.stat().st_size > 0:
        sys.stdout.write(
            json.dumps(
                {
                    "kind": "cached",
                    "text_path": str(cached),
                    "source_url": "(cache)",
                }
            )
            + "\n"
        )
        return 0

    if args.local_dir:
        result = try_local_pdf(Path(args.local_dir), key, cache_dir)
        if result:
            sys.stdout.write(json.dumps(result) + "\n")
            return 0

    for fn in (try_unpaywall, try_europepmc, try_crossref_abstract, try_pubmed_abstract):
        result = fn(doi, key, cache_dir, args.email)
        if result:
            sys.stdout.write(json.dumps(result) + "\n")
            return 0

    sys.stdout.write(
        json.dumps({"kind": "not_found", "text_path": None, "source_url": None}) + "\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
