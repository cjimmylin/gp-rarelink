"""Check the D-47 hand-fetched copies against the download report and the batch-1 candidate list.

Usage: python3 -I verify_d47_hand.py <unpacked dir> <status_2026-11-14.csv> <repo root> <out csv>
"""
import csv, hashlib, html, pathlib, re, subprocess, sys

src, status_csv, repo, out = (pathlib.Path(a) for a in sys.argv[1:5])
report = list(csv.DictReader(open(src / "download_report.csv", encoding="utf-8-sig")))
status = {r["pmid"]: r for r in csv.DictReader(open(status_csv, encoding="utf-8-sig"))}

# PMIDs already in the registered corpus with full text (any disease).
registered = {}
for m in sorted(repo.glob("data/literature/*/manifest.csv")):
    for r in csv.DictReader(open(m, encoding="utf-8-sig")):
        registered[r["pmid"]] = (m.parent.name, r.get("access_status", ""), r.get("fulltext_format", ""))

def words(s):
    return {w for w in re.findall(r"[a-z0-9]+", s.lower()) if len(w) >= 4}

def text_of(p):
    if p.suffix.lower() == ".pdf":
        return subprocess.run(["pdftotext", "-l", "3", str(p), "-"], capture_output=True, text=True).stdout
    raw = p.read_bytes().decode("utf-8", "replace")
    # MHTML is quoted-printable; undo soft breaks and =XX escapes well enough for word matching.
    raw = re.sub(r"=\r?\n", "", raw)
    raw = re.sub(r"=([0-9A-F]{2})", lambda m: chr(int(m.group(1), 16)), raw)
    return html.unescape(re.sub(r"<[^>]+>", " ", raw))

files = {p.name: p for p in src.iterdir() if p.suffix.lower() in (".pdf", ".mhtml")}
rows, problems = [], []
for r in report:
    if not r["local_file"]:
        continue
    name = r["local_file"]
    p = files.pop(name, None)
    row = {k: r[k] for k in ("disease", "pmid", "status", "local_file", "pdf_pages", "source_link")}
    if p is None:
        problems.append(f"missing file {name}"); row["check"] = "missing"; rows.append(row); continue
    data = p.read_bytes()
    row["bytes"] = len(data)
    row["sha256"] = hashlib.sha256(data).hexdigest()
    if p.suffix.lower() == ".pdf":
        row["magic_ok"] = data[:5] == b"%PDF-"
        info = subprocess.run(["pdfinfo", str(p)], capture_output=True, text=True).stdout
        m = re.search(r"^Pages:\s+(\d+)", info, re.M)
        row["pages"] = m.group(1) if m else ""
        if row["pages"] != r["pdf_pages"]:
            problems.append(f"{name}: pdfinfo pages {row['pages']} vs report {r['pdf_pages']}")
    else:
        row["magic_ok"] = b"MIME-Version" in data[:2000]
        row["pages"] = ""
    if not row["magic_ok"]:
        problems.append(f"{name}: not a valid {p.suffix} file")
    if not name.startswith(f"{r['disease']}_{r['pmid']}_"):
        problems.append(f"{name}: name does not match disease/pmid {r['disease']}/{r['pmid']}")
    st = status.get(r["pmid"])
    row["in_212_candidates"] = st is not None
    row["batch1_result"] = st["result"] if st else ""
    if st and st["result"] in ("pdf", "html_fulltext", "saved"):
        problems.append(f"{name}: already saved in batch 1 ({st['result']})")
    reg = registered.get(r["pmid"])
    row["registered_corpus"] = "|".join(reg) if reg else "not listed"
    if reg and reg[1] not in ("paywalled", "not_accessible", ""):
        problems.append(f"{name}: registered manifest says access_status={reg[1]}")
    txt = words(text_of(p))
    tw = words(r["title"])
    row["title_word_match"] = f"{len(tw & txt)}/{len(tw)}"
    row["title_share"] = round(len(tw & txt) / len(tw), 2) if tw else ""
    rows.append(row)

for extra in files:
    problems.append(f"file not in report: {extra}")

keys = list(dict.fromkeys(k for r in rows for k in r))
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)
print(f"{len(rows)} files checked; {len(problems)} problems")
for x in problems:
    print(" -", x)
import collections
print("batch-1 result for these PMIDs:", collections.Counter(r["batch1_result"] for r in rows))
print("registered status:", collections.Counter(r["registered_corpus"].split("|")[1] if "|" in r["registered_corpus"] else r["registered_corpus"] for r in rows))
low = sorted((r["title_share"], r["local_file"], r["title_word_match"]) for r in rows if r.get("title_share") != "" and r["title_share"] < 0.8)
print("title-word share < 0.8:", low)
