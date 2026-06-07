#!/usr/bin/env python3
"""
build_ris.py — emit references as an RIS file (imports into EndNote / Zotero / Mendeley).

The reference-check workflow uses this for its two bibliographic deliverables:
  * the MISSING-PDF upload request  -> feed to EndNote "Find Full Text"
  * the corrected REFERENCE LIST    -> import the clean bibliography

    python build_ris.py --refs <manuscript .md/.bib/reflist> --out references.ris --all
    python build_ris.py --refs <manuscript> --lit <Literature dir> --out pdfs_needed.ris --missing

Modes:
  --all      every reference parsed from --refs.
  --missing  only references that have NO readable PDF in --lit (needs --lit). Skips entries
             with no DOI (Find Full Text can't use them) and notes them on stderr.

RIS is bibliographic only — issue/analysis reporting stays in the markdown audit.
"""
import argparse, re, os, glob, subprocess, unicodedata, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def fsafe(s): return re.sub(r"[^A-Za-z0-9._-]", "_", s)
def doipart(doi): return fsafe(doi.lower().replace("/", "_"))
def words(p):
    try: return len(subprocess.run(["pdftotext","-l","2",p,"-"],capture_output=True,text=True,errors="ignore").stdout.split())
    except Exception: return 0

def ris_authors(block):
    out=[]
    for a in block.split(","):
        a=a.strip()
        if not a: continue
        ws=a.split()
        if len(ws)>=2 and re.fullmatch(r"[A-Z]{1,4}", ws[-1]):
            out.append(f"{' '.join(ws[:-1])}, {ws[-1]}")
        else:
            out.append(a)
    return out

def parse_refs(path):
    text=open(path, encoding="utf-8", errors="ignore").read()
    recs=[]
    block=text.split("# References",1)[-1] if "# References" in text else text
    block=re.split(r"#+\s*Uncited", block, flags=re.I)[0]   # skip any separated 'uncited/orphan' section
    for para in re.split(r"\n\s*\n", block):
        p=" ".join(para.split()).replace("**","").replace("[ADDED]","").strip()
        if not p or p.startswith("#") or p.startswith("!["): continue
        ym=re.search(r"\((\d{4}[a-z]?)\)", p)
        if not ym: continue
        year=re.sub(r"[a-z]$","",ym.group(1))
        authblock=p[:ym.start()].strip()
        rest=p[ym.end():].strip()
        dm=re.search(r"doi:\s*(\S+)", rest, re.I)
        doi=dm.group(1).replace("\\","").rstrip(". ").lower() if dm else ""
        body=(rest[:dm.start()] if dm else rest).strip().rstrip(". ")
        vol=sp=ep=jo=title=""
        # pull a trailing  Volume[(issue)][:pages]  off the end (handles "Journal. 12:3-4" and "Journal 12:3-4")
        mvp=re.search(r"[.\s](\d{1,4})(?:\([^)]*\))?:\s*([A-Za-z]?\d+)(?:[–-]([A-Za-z]?\d+))?\.?\s*$", body)
        if mvp:
            vol,sp,ep=mvp.group(1),mvp.group(2),(mvp.group(3) or "")
            body=body[:mvp.start()].rstrip(" .")
        else:
            mv=re.search(r"[.\s](\d{1,4})(?:\([^)]*\))?\.?\s*$", body)   # volume only, no pages
            if mv: vol=mv.group(1); body=body[:mv.start()].rstrip(" .")
        segs=[s.strip().rstrip(".") for s in body.split(". ") if s.strip()]
        if len(segs)>=2: jo=segs[-1]; title=". ".join(segs[:-1])
        else: jo=""; title=segs[0] if segs else ""
        title=re.sub(r"[*_]","",title).rstrip(". ")
        recs.append({"au":ris_authors(authblock),"py":year,"ti":title,"jo":re.sub(r"[*_]","",jo),
                     "vl":vol,"sp":sp,"ep":ep,"do":doi})
    return recs

ap=argparse.ArgumentParser()
ap.add_argument("--refs", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--lit"); g=ap.add_mutually_exclusive_group()
g.add_argument("--all", action="store_true"); g.add_argument("--missing", action="store_true")
A=ap.parse_args()
recs=parse_refs(A.refs)

if A.missing:
    if not A.lit: sys.exit("--missing requires --lit")
    pdfs=glob.glob(os.path.join(A.lit,"*.pdf"))
    def readable(doi):
        want=doipart(doi)
        for f in pdfs:
            if want and want in fsafe(os.path.basename(f)).lower(): return words(f)>=20
        return False
    keep=[]; nodoi=0
    for r in recs:
        if not r["do"]: nodoi+=1; continue
        if not readable(r["do"]): keep.append(r)
    recs=keep
    sys.stderr.write(f"missing (no readable PDF): {len(recs)}; skipped {nodoi} with no DOI\n")

with open(A.out,"w",encoding="utf-8") as f:
    for r in recs:
        f.write("TY  - JOUR\n")
        for a in r["au"]: f.write(f"AU  - {a}\n")
        if r["py"]: f.write(f"PY  - {r['py']}\n")
        if r["ti"]: f.write(f"TI  - {r['ti']}\n")
        if r["jo"]: f.write(f"JO  - {r['jo']}\n")
        if r["vl"]: f.write(f"VL  - {r['vl']}\n")
        if r["sp"]: f.write(f"SP  - {r['sp']}\n")
        if r["ep"]: f.write(f"EP  - {r['ep']}\n")
        if r["do"]: f.write(f"DO  - {r['do']}\n")
        f.write("ER  - \n\n")
print(f"wrote {A.out}: {len(recs)} records ({'missing-PDF' if A.missing else 'all'} mode)")
