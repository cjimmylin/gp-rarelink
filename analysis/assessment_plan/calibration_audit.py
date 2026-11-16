"""Draw the candidate claims for the audit calibration set (D-55) and prepare the reference-labelling sheet.

Rule (DECISIONS.md, D-55, written before this ran): 60 claims of the six registered runs that
are not in the registered audit sample, 36 the gatekeeper judged unsupported and 24 it judged
supported, spread over the six diseases as evenly as the pools allow, from papers whose text
can be restored exactly (JATS full text, no appended supplementary text). Refinements made here
for variety, also before any draw: at most one claim per paper, and at most two claims of the
same field per disease in each pool.

The candidates, the seed and the key (which pool each claim came from) are written to a
git-ignored private folder: the repository is public and holds the gatekeeper's verdicts, so
publishing the list would give the calibration answers away. Only sha256 values are committed
(adjudication/calibration/commitment_<date>.json). After calibration ends the private files are
committed and anyone can check them against those values.

  uv run python analysis/assessment_plan/calibration_audit.py --date 2026-11-15

The rating page is then built from the private sample with adjudication/o1_audit/make_rating_page.py.
Harness side: reads gatekeeper verdicts only to choose claims; nothing here feeds extraction.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import secrets
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "adjudication" / "poc_audit"))
from make_rating_page import context_for  # noqa: E402  (the page's own passage finder)
from pipeline.extract.corpus.eutils import Client  # noqa: E402
from pipeline.extract.corpus.jats_to_markdown import jats_to_markdown  # noqa: E402

DISEASES = ["ha20", "ssadh", "tangier", "lad1", "axd", "danon"]
EMPTY = {"", "null", '""', '"not reported"', '"unknown"', "[]", '"Not reported"'}
QUOTA = {"unsupported": 6, "supported": 4}        # per disease: 36 + 24 = 60
MAX_PER_FIELD = 2
PRIV = Path("adjudication/calibration/private")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


class Text:
    """Restores a paper's Markdown into the git-ignored fulltext_md folder, once, and says whether it worked."""

    def __init__(self):
        self.client, self.log = Client(), {}

    def ensure(self, d: str, pmid: str, man: dict) -> str | None:
        key = (d, pmid)
        if key in self.log:
            return self.log[key]["path"]
        md = Path(f"data/literature/{d}/fulltext_md/{pmid}.md")
        row = man[pmid]
        status = "already present" if md.exists() else None
        if not md.exists():
            first = self.client.europepmc_fulltext_xml if row["access_status"] == "europepmc_xml" else self.client.efetch_pmc_xml
            other = self.client.efetch_pmc_xml if row["access_status"] == "europepmc_xml" else self.client.europepmc_fulltext_xml
            xml = None
            for f in (first, other):
                try:
                    xml = f(row["pmcid"]) if row.get("pmcid") else None
                except Exception:
                    xml = None
                if xml:
                    break
            if xml:
                md.parent.mkdir(parents=True, exist_ok=True)
                art = jats_to_markdown(xml)            # the same steps as pipeline.extract.corpus.to_markdown takes for JATS
                if not art.pmid:
                    art.pmid = pmid
                art.title = art.title or row.get("title", "")
                md.write_text(art.to_markdown())
                status = "fetched, sha256 as in the manifest" if hashlib.sha256(xml).hexdigest() == row["sha256"] else "fetched, sha256 differs from the manifest"
            else:
                status = "not fetched"
        self.log[key] = {"path": str(md) if md.exists() else None, "status": status}
        return self.log[key]["path"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    ap.add_argument("--draw", type=int, default=1, help="1 for the first draw; 2, 3, ... for a further draw by the same rule when the reference labels give fewer than 20 unsupported claims")
    ap.add_argument("--n-unsupported", type=int, default=36, help="candidates from the claims the gatekeeper removed (first draw: 36)")
    ap.add_argument("--n-supported", type=int, default=24, help="candidates from the claims the gatekeeper kept (first draw: 24)")
    a = ap.parse_args()
    out = PRIV / ("audit_candidates" if a.draw == 1 else f"audit_candidates_draw{a.draw}")
    if (out / "key.json").exists():
        raise SystemExit(f"{out}/key.json exists; the candidates are drawn once")
    earlier = [json.loads(k.read_text()) for k in sorted(PRIV.glob("audit_candidates*/key.json"))]
    earlier_claims = {(i["disease"], i["claim_id"]) for e in earlier for i in e["items"]}
    earlier_papers = {(r["disease"], r["pmid"]) for f in sorted(PRIV.glob("audit_candidates*/sample.csv")) for r in csv.DictReader(f.open(newline=""))}
    first_n = 1 + sum(len(e["items"]) for e in earlier)
    out.mkdir(parents=True, exist_ok=True)
    seed = secrets.token_hex(16)
    rng = random.Random(seed)
    key = json.loads(Path("adjudication/o1_audit/sample_key.json").read_text())
    in_sample = defaultdict(set)
    for it in key["items"]:
        in_sample[it["disease"]].add(it["claim_id"])
    text = Text()
    chosen, pools, inputs = [], {}, {}
    data = {}
    for d in DISEASES:
        run = Path(f"data/extracted/{d}/pv1-{d}")
        man = {r["pmid"]: r for r in csv.DictReader(open(f"data/literature/{d}/manifest.csv", newline=""))}
        conv = Path(f"data/literature/{d}/supplementary/conversion.csv")
        supp = {r["pmid"] for r in csv.DictReader(conv.open())} if conv.exists() else set()
        gk = list(csv.DictReader((run / "gatekeeper_v4.csv").open(newline="")))
        claims = list(csv.DictReader((run / "claims.csv").open(newline="")))
        inputs[str(run / "gatekeeper_v4.csv")] = sha(run / "gatekeeper_v4.csv")
        ok_paper = {p for p in {r["pmid"] for r in gk} if man.get(p, {}).get("fulltext_format") == "nxml" and p not in supp}
        elig = [r for r in gk if r["class"] == "model" and r["value"].strip() not in EMPTY and r["claim_id"] not in in_sample[d] and r["pmid"] in ok_paper
                and (d, r["claim_id"]) not in earlier_claims and (d, r["pmid"]) not in earlier_papers]
        data[d] = {"run": run, "man": man, "claims": claims,
                   "unsupported": [r for r in elig if r["verdict"] == "unsupported"], "supported": [r for r in elig if r["verdict"] == "supported"]}
        pools[d] = {k: len(data[d][k]) for k in ("unsupported", "supported")}
        for k in ("unsupported", "supported"):
            rng.shuffle(data[d][k])

    used_paper = defaultdict(set)
    rejected = Counter()

    def take(d: str, pool: str, n: int) -> int:
        got, fields = 0, Counter(c["field"] for c in chosen if c["disease"] == d and c["pool"] == pool)
        lst = data[d][pool]
        while lst and got < n:
            g = lst.pop()
            if g["pmid"] in used_paper[d] or fields[g["field"]] >= MAX_PER_FIELD:
                continue
            sp = data[d]["claims"][int(g["claim_id"][1:]) - 1]
            assert (sp["pmid"], sp["table"], sp["row"], sp["field"]) == (g["pmid"], g["table"], g["row"], g["field"]), g["claim_id"]
            parts = [q for q in sp["span"].split(" || ") if q.strip()]
            path = text.ensure(d, g["pmid"], data[d]["man"])
            if not path or not parts or not all(context_for(Path(path).read_text(), q)[1] for q in parts):
                rejected["no text or passage not located"] += 1
                used_paper[d].add(g["pmid"])          # do not retry a paper whose text could not be restored
                continue
            rec = ((json.loads((data[d]["run"] / "per_paper" / f"{g['pmid']}.json").read_text()).get("tables") or {}).get(g["table"]) or [])[int(g["row"])]
            context = ""
            if g["table"] == "phenotypic_features":
                context = (rec.get("feature_text_as_stated") or {}).get("value", "")
            elif g["table"] == "phenotype_checklist":
                context = (rec.get("checklist_feature") or {}).get("value", "")
            elif g["table"] == "variants":
                context = (rec.get("variant_original_string") or {}).get("value", "")
            chosen.append({"disease": d, "pool": pool, "claim_id": g["claim_id"], "pmid": g["pmid"], "table": g["table"], "field": g["field"], "value": g["value"],
                           "span": sp["span"], "individual": (rec.get("individual_label_in_paper") or {}).get("value", ""), "context": context})
            used_paper[d].add(g["pmid"])
            fields[g["field"]] += 1
            got += 1
        return got

    short = Counter()
    total = {"unsupported": a.n_unsupported, "supported": a.n_supported}
    for pool in ("unsupported", "supported"):
        order = DISEASES[:]
        if a.draw > 1:
            rng.shuffle(order)                         # which diseases get the remainder is part of the seeded draw
        quota = {d: total[pool] // len(DISEASES) + (1 if i < total[pool] % len(DISEASES) else 0) for i, d in enumerate(order)}
        assert a.draw > 1 or quota == {d: QUOTA[pool] for d in DISEASES}
        for d in DISEASES:
            short[pool] += quota[d] - take(d, pool, quota[d])
        while short[pool] > 0:                         # fill a shortfall from the disease with the most claims left
            d = max(DISEASES, key=lambda x: len(data[x][pool]))
            if not data[d][pool] or not take(d, pool, 1):
                if not any(data[x][pool] for x in DISEASES):
                    break
                continue
            short[pool] -= 1
    rng.shuffle(chosen)
    rows = [{"n": n, "item_id": f"CAL-{n:03d}", "disease": c["disease"], "pmid": c["pmid"], "pubmed": f"https://pubmed.ncbi.nlm.nih.gov/{c['pmid']}/",
             "paper_text": f"data/literature/{c['disease']}/fulltext_md/{c['pmid']}.md", "individual": c["individual"], "context": c["context"],
             "table": c["table"], "field": c["field"], "value": c["value"], "span": c["span"]} for n, c in enumerate(chosen, first_n)]
    with (out / "sample.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    (out / "seed.txt").write_text(seed + "\n")
    (out / "key.json").write_text(json.dumps({
        "date": a.date, "draw": a.draw, "rule": "DECISIONS.md D-55; analysis/assessment_plan/calibration_audit.py", "seed_file": "seed.txt",
        "items": [{"item_id": r["item_id"], "disease": c["disease"], "claim_id": c["claim_id"], "pool": c["pool"]} for r, c in zip(rows, chosen)],
        "text_restore": {f"{d}:{p}": v["status"] for (d, p), v in sorted(text.log.items())}, "inputs_sha256": inputs}, indent=1) + "\n")
    by = Counter((c["pool"], c["disease"]) for c in chosen)
    commit = {"date": a.date, "decision": "D-55", "draw": a.draw, "what": "audit calibration candidates for Jimmy's reference labels; private until calibration ends",
              "candidates": len(chosen), "by_pool": dict(Counter(c["pool"] for c in chosen)),
              "by_pool_and_disease": {f"{p}:{d}": n for (p, d), n in sorted(by.items())},
              "eligible_pool_sizes": pools, "candidates_passed_over": dict(rejected),
              "papers_restored": dict(Counter(v["status"] for v in text.log.values())),
              "sha256": {"sample.csv": sha(out / "sample.csv"), "key.json": sha(out / "key.json"), "seed.txt": sha(out / "seed.txt")},
              "note": f"The three files are in {out}/ (git-ignored) and in the private package handed to Jimmy. "
                      "They are committed when calibration has ended; these values let anyone check that they were not changed."}
    name = f"commitment_{a.date}.json" if a.draw == 1 else f"commitment_draw{a.draw}_{a.date}.json"
    Path(f"adjudication/calibration/{name}").write_text(json.dumps(commit, indent=1) + "\n")
    print(json.dumps({k: commit[k] for k in ("candidates", "by_pool", "by_pool_and_disease", "candidates_passed_over", "papers_restored")}, indent=1))
    print("fields:", dict(Counter(c["field"] for c in chosen).most_common(12)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
