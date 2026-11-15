"""Split the O3 gap candidates into helper batches for the WS3 evidence dossiers (D-41).

Input: adjudication/o3_gaps/evidence_rows.jsonl (from pipeline/harness/gap_candidates.py).
That file holds the extracted rows and verbatim spans only; no ClinVar or OMIM content.
This script reads nothing else from the harness side.

Candidates that share a paper go to the same batch where possible, so each paper is read
by one helper. Batches stay within one disease and hold at most --max-candidates
candidates and --max-papers papers (a candidate with more papers than that gets a batch
of its own).

  python3 -I adjudication/o3_gaps/make_dossier_batches.py
writes adjudication/o3_gaps/batches/batch_NN.json and batches/index.json.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

INHERITANCE = {"ha20": "autosomal dominant", "axd": "autosomal dominant (mostly de novo)", "danon": "X-linked dominant",
               "ssadh": "autosomal recessive", "tangier": "autosomal recessive", "lad1": "autosomal recessive",
               # D-47 extension
               "gamt": "autosomal recessive", "papa": "autosomal dominant", "ats": "autosomal recessive",
               "blau": "autosomal dominant", "lcat": "autosomal recessive",
               # exploratory twelfth disease (D-54)
               "majeed": "autosomal recessive"}
DISEASE_NAME = {"ha20": "A20 haploinsufficiency", "axd": "Alexander disease", "danon": "Danon disease",
                "ssadh": "succinic semialdehyde dehydrogenase deficiency", "tangier": "Tangier disease",
                "lad1": "leukocyte adhesion deficiency type I",
                "gamt": "guanidinoacetate methyltransferase deficiency",
                "papa": "PAPA syndrome (pyogenic sterile arthritis, pyoderma gangrenosum and acne)",
                "ats": "arterial tortuosity syndrome", "blau": "Blau syndrome",
                "lcat": "familial LCAT deficiency (including fish-eye disease)",
                "majeed": "Majeed syndrome"}
ROOT = Path("adjudication/o3_gaps")


def main(argv: list[str] | None = None) -> int:
    global ROOT
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--max-candidates", type=int, default=20)
    ap.add_argument("--max-papers", type=int, default=8)
    ap.add_argument("--root", default=str(ROOT), help="candidate folder (default adjudication/o3_gaps; the D-47 extension uses adjudication/o3_gaps_ext)")
    ap.add_argument("--run-prefix", default="pv1", help="extraction files are data/extracted/<d>/<prefix>-<d>/per_paper (pv1s for the exploratory Majeed run)")
    ap.add_argument("--skip-missing-text", action="store_true",
                    help="leave out candidates with a paper whose text is not in data/literature/<d>/fulltext_md and list them in index.json")
    args = ap.parse_args(argv)
    ROOT = Path(args.root)
    ev = [json.loads(l) for l in (ROOT / "evidence_rows.jsonl").open()]
    by_d = defaultdict(list)
    skipped = []
    for e in ev:
        no_text = [p for p in e["pmids"] if not Path(f"data/literature/{e['disease']}/fulltext_md/{p}.md").exists()]
        if args.skip_missing_text and no_text:
            skipped.append({"candidate_id": e["candidate_id"], "papers_without_text": no_text})
            continue
        by_d[e["disease"]].append(e)
    batches = []
    for d in ["ha20", "ssadh", "tangier", "lad1", "axd", "danon", "gamt", "papa", "ats", "blau", "lcat", "majeed"]:
        # greedy: order candidates by their most-shared paper, then fill batches
        share = defaultdict(int)
        for e in by_d[d]:
            for p in e["pmids"]:
                share[p] += 1
        todo = sorted(by_d[d], key=lambda e: (-max(share[p] for p in e["pmids"]), sorted(e["pmids"], key=lambda p: -share[p])[0], e["candidate_id"]))
        cur, papers = [], set()
        for e in todo:
            new = papers | set(e["pmids"])
            if cur and (len(cur) >= args.max_candidates or len(new) > args.max_papers):
                batches.append((d, cur, papers))
                cur, new = [], set(e["pmids"])
            cur.append(e)
            papers = new
        if cur:
            batches.append((d, cur, papers))
    out = ROOT / "batches"
    out.mkdir(parents=True, exist_ok=True)
    index = []
    for i, (d, cands, papers) in enumerate(batches, 1):
        name = f"batch_{i:02d}"
        doc = {"batch": name, "disease": d, "disease_name": DISEASE_NAME[d], "inheritance": INHERITANCE[d],
               "gene": cands[0]["gene"], "papers": sorted(papers),
               "paper_text": {p: f"data/literature/{d}/fulltext_md/{p}.md" for p in sorted(papers)},
               "extraction": {p: f"data/extracted/{d}/{args.run_prefix}-{d}/per_paper/{p}.json" for p in sorted(papers)},
               "candidates": cands}
        (out / f"{name}.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
        index.append({"batch": name, "disease": d, "candidates": len(cands), "papers": len(papers),
                      "paper_bytes": sum(Path(f"data/literature/{d}/fulltext_md/{p}.md").stat().st_size for p in papers)})
    if skipped:
        index.append({"skipped_no_paper_text": skipped})
    (out / "index.json").write_text(json.dumps(index, indent=1) + "\n")
    for x in index:
        print(x)
    done = [x for x in index if "batch" in x]
    print(len(done), "batches;", sum(x["candidates"] for x in done), "candidates;", sum(x["papers"] for x in done), "paper reads")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
