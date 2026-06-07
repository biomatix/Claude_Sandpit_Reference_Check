#!/usr/bin/env python3
"""
normalize_literature.py — rename every PDF in a Literature/ folder to the canonical
form  <FirstAuthorSurname>_<Year>_<sanitised-lowercased-DOI>.pdf

Used by the reference-check skill, check 6, to normalise PDFs the user drops in with
arbitrary publisher/browser filenames. Dry-run by default; pass --apply to execute.

    python normalize_literature.py --lit <Literature dir> --refs <manuscript-or-reflist> [--apply]

How a file's DOI is decided (in order), and WHY each rule exists:
  1. Already canonical          -> just lowercase the DOI part (consistency).
  2. DOI in the PDF text that is one of the manuscript's CITED DOIs.
        WHY "cited only": a paper's own DOI is on page 1, but its reference list is full
        of OTHER DOIs; trusting any text DOI mis-renamed a Nextflow paper with an ACM DOI
        scraped from its bibliography. Matching only against cited DOIs avoids that.
  3. DOI recoverable from the FILENAME (incl. URL/SICI-encoded DOIs, e.g. "icb_2F37.6.504",
        "_28sici_29...") matched against the cited set.
  4. first-author SURNAME + YEAR in the filename matched to a unique cited reference
        (handles publisher names like "Global Change Biology - 2023 - Fuentes - ...").
  5. otherwise -> left untouched and listed as MANUAL (read its first page yourself).

Safety lessons baked in:
  * CASE-INSENSITIVE FILESYSTEM SAFETY (critical): a case-only rename (……GCEN -> ……gcen)
    must NOT trigger a "remove existing target" — on Windows/macOS the target path
    resolves to the SAME file, so removing it deletes the source. We compare paths with
    os.path.normcase and only remove a target that is a genuinely DIFFERENT file.
  * DEDUPE keeps the text-richest copy (a freshly downloaded text PDF beats an old scan).
  * SCANNED (image-only) PDFs are reported, never silently treated as verified.
  * Never rename on a weak guess: ambiguous surname+year (>1 cited match) -> MANUAL.
"""
import argparse, os, re, sys, glob, subprocess, unicodedata

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
_M = str.maketrans({"ø":"o","Ø":"o","ł":"l","đ":"d","ð":"d","þ":"th","ß":"ss","æ":"ae","œ":"oe"})
def deacc(s): return "".join(c for c in unicodedata.normalize("NFKD", s.translate(_M)) if not unicodedata.combining(c))
def fsafe(s): return re.sub(r"[^A-Za-z0-9._-]", "_", s)
def alnum(s): return re.sub(r"[^a-z0-9]", "", deacc(s).lower())

def surname_words(first_author_block):
    ws = first_author_block.split()
    while ws and re.fullmatch(r"[A-Z]{1,4}", ws[-1]):   # drop trailing initials
        ws.pop()
    return ws or first_author_block.split()

def canon_surname(sn): return fsafe(deacc(sn).replace(" ", ""))   # "Di Tommaso"->"DiTommaso"
def doipart(doi): return fsafe(doi.lower().replace("/", "_"))

def clean_doi(raw):
    d = raw.replace("\\", "").strip().rstrip(".,;)")
    for pat in (";SUBJMETA",";JOURNAL",";WGROUP",";CTYPE",";KWRD","/METRICS","/BIBTEX",
                "/SUPPL_FILE","/ASSET","/FULL","/EPDF","/ABSTRACT","/META","/HTML","/PDF"):
        i = d.upper().find(pat)
        if i != -1: d = d[:i]
    return d.rstrip("/. ")

# ---------- parse the manuscript / reference list ----------
def parse_refs(path):
    text = open(path, encoding="utf-8", errors="ignore").read()
    refs = []
    if "@" in text and re.search(r"@\w+\s*\{", text):   # BibTeX
        for m in re.finditer(r"@\w+\s*\{(.+?)\n\}", text, re.S):
            blk = m.group(1)
            au = re.search(r"author\s*=\s*[{\"](.+?)[}\"]", blk, re.S|re.I)
            yr = re.search(r"year\s*=\s*[{\"]?\s*(\d{4})", blk, re.I)
            doi = re.search(r"doi\s*=\s*[{\"]?\s*([^},\"\s]+)", blk, re.I)
            if au and yr:
                sur = re.split(r"\s+and\s+", au.group(1))[0].split(",")[0].strip()
                refs.append({"surname": sur, "year": yr.group(1),
                             "doi": clean_doi(doi.group(1)).lower() if doi else ""})
        return refs
    block = text.split("# References", 1)[-1]            # prose reference list
    for para in re.split(r"\n\s*\n", block):
        p = " ".join(para.split())
        if not p or p.startswith("#") or p.startswith("!["): continue
        ym = re.search(r"\((\d{4})\)", p) or re.search(r"\b(19|20)\d\d\b", p)
        if not ym: continue
        year = ym.group(0).strip("()")
        first = p[:ym.start()].split(",")[0].strip()
        sur = " ".join(surname_words(first))
        dm = re.search(r"doi:\s*(\S+)", p, re.I) or re.search(r"(10\.\d{4,9}/[^\s]+)", p)
        refs.append({"surname": sur, "year": year,
                     "doi": clean_doi(dm.group(1)).lower() if dm else ""})
    return refs

# ---------- DOI discovery ----------
DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\"'<>)\]]+")
def content_cited_doi(path, cset):
    txt = subprocess.run(["pdftotext","-l","3",path,"-"],capture_output=True,text=True,errors="ignore").stdout
    for m in DOI_RE.finditer(txt):
        d = clean_doi(m.group(0)).lower()
        if d in cset: return d
    return None

_HEX = {"28":"(","29":")","2f":"/","3a":":","3c":"<","3e":">","3b":";","2c":",","5b":"[","5d":"]"}
def decode_name(name):
    s = name.lower()
    for h,ch in _HEX.items():
        s = s.replace("_"+h, ch).replace("%"+h, ch)
    return s
def filename_cited_doi(name, cset):
    decn = alnum(decode_name(name))
    best=None; blen=0
    for d in cset:
        suf = d.split("/",1)[1] if "/" in d else d
        sn = alnum(suf)
        if len(sn) >= 5 and sn in decn and len(sn) > blen:
            best, blen = d, len(sn)
    return best
def author_year_doi(name, refs):
    toks = set(re.split(r"[^a-z0-9]+", deacc(name).lower()))
    hits=[]
    for r in refs:
        if not r["doi"]: continue
        # year ±1 — filenames often carry the online year, the reference the print year
        yrs = {r["year"]}
        if r["year"].isdigit(): yrs |= {str(int(r["year"])-1), str(int(r["year"])+1)}
        if not (toks & yrs): continue
        # surname match on distinctive sub-tokens (split hyphen/space) or the joined form
        sub = {alnum(w) for w in re.split(r"[ -]+", r["surname"]) if len(alnum(w)) >= 4}
        sub.add(alnum(r["surname"]))
        if sub & toks:
            hits.append(r["doi"])
    return hits[0] if len(set(hits)) == 1 else None

def words(p):
    try: return len(subprocess.run(["pdftotext","-l","2",p,"-"],capture_output=True,text=True,errors="ignore").stdout.split())
    except Exception: return 0

# ---------- main ----------
ap = argparse.ArgumentParser()
ap.add_argument("--lit", required=True); ap.add_argument("--refs", required=True)
ap.add_argument("--apply", action="store_true")
A = ap.parse_args()
refs = parse_refs(A.refs)
cset = {r["doi"]:(r["surname"],r["year"]) for r in refs if r["doi"]}
print(f"parsed {len(refs)} references ({len(cset)} with DOIs)\n")

CANON = re.compile(r"^([A-Za-z][A-Za-z'-]+)_((?:18|19|20)\d\d)_(.+)\.pdf$")
plan = {}; manual = []
for path in sorted(glob.glob(os.path.join(A.lit, "*.pdf"))):
    name = os.path.basename(path)
    m = CANON.match(name)
    if m and ("10." in m.group(3) or m.group(3).lower()=="nodoi"):
        target = f"{m.group(1)}_{m.group(2)}_{m.group(3).lower()}.pdf"; via="canonical"
    else:
        doi = content_cited_doi(path, cset) or filename_cited_doi(name, cset) or author_year_doi(name, refs)
        if not doi:
            manual.append(name); continue
        sur, yr = cset.get(doi, (None,None))
        if not sur:
            manual.append(name); continue
        target = f"{canon_surname(sur)}_{yr}_{doipart(doi)}.pdf"; via="resolved"
    plan.setdefault(target.lower(), []).append((path, name, words(path), target, via))

renames=[]; dups=[]; ok=0
for srcs in plan.values():
    srcs.sort(key=lambda x:-x[2])              # richest text first
    keep = srcs[0]
    if keep[1] != keep[3]: renames.append(keep)
    else: ok += 1
    dups.extend(srcs[1:])

def act(s): return "DRY" if not A.apply else "DONE"
print(f"== RENAME / NORMALISE ({len(renames)}) ==")
for path,name,w,target,via in sorted(renames,key=lambda x:x[3]):
    print(f"  [{act(0)}] {name}\n        -> {target}   [{via}, {w}w{' SCANNED' if w<20 else ''}]")
    if A.apply:
        dst = os.path.join(A.lit, target)
        same = os.path.normcase(os.path.abspath(path))==os.path.normcase(os.path.abspath(dst))
        try:
            if os.path.exists(dst) and not same: os.remove(dst)   # only a DIFFERENT file
            os.replace(path, dst)
        except Exception as e: print(f"        ERROR: {e}")
print(f"\n== DEDUPE — same DOI, remove non-richest ({len(dups)}) ==")
for path,name,w,target,via in dups:
    print(f"  [{act(0)}] remove {name} ({w}w; keep {target})")
    if A.apply:
        try: os.remove(path)
        except FileNotFoundError: pass
print(f"\n== already canonical: {ok}")
print(f"\n== MANUAL — no cited DOI found, read first page ({len(manual)}) ==")
for n in manual: print(f"  {n}")
print(f"\n{'APPLIED' if A.apply else 'DRY RUN — rerun with --apply to execute'}.")
