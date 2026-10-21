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
               "ssadh": "autosomal recessive", "tangier": "autosomal recessive", "lad1": "autosomal recessive"}
DISEASE_NAME = {"ha20": "A20 haploinsufficiency", "axd": "Alexander disease", "danon": "Danon disease",
                "ssadh": "succinic semialdehyde dehydrogenase deficiency", "tangier": "Tangier disease",
                "lad1": "leukocyte adhesion deficiency type I"}
ROOT = Path("adjudication/o3_gaps")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--max-candidates", type=int, default=20)
    ap.add_argument("--max-papers", type=int, default=8)
    args = ap.parse_args(argv)
    ev = [json.loads(l) for l in (ROOT / "evidence_rows.jsonl").open()]
    by_d = defaultdict(list)
    for e in ev:
        by_d[e["disease"]].append(e)
    batches = []
    for d in ["ha20", "ssadh", "tangier", "lad1", "axd", "danon"]:
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
               "extraction": {p: f"data/extracted/{d}/pv1-{d}/per_paper/{p}.json" for p in sorted(papers)},
               "candidates": cands}
        (out / f"{name}.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
        index.append({"batch": name, "disease": d, "candidates": len(cands), "papers": len(papers),
                      "paper_bytes": sum(Path(f"data/literature/{d}/fulltext_md/{p}.md").stat().st_size for p in papers)})
    (out / "index.json").write_text(json.dumps(index, indent=1) + "\n")
    for x in index:
        print(x)
    print(len(index), "batches;", sum(x["candidates"] for x in index), "candidates;", sum(x["papers"] for x in index), "paper reads")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
