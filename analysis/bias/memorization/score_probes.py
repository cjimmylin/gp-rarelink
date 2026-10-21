"""Score the WS5 memorization probes against the full-text extraction (pre-registration §7.4.3; D-41).

Never scored against ClinVar or OMIM. Inputs: responses/<disease>_<probe>.json from the
helpers, targets/<disease>_completion.json, sample.csv, the pv1 per-paper extraction and
HPO bindings, and tool_check.json (a batch whose helper used a disallowed tool is dropped).

(a) closed_book, per paper:
    variants  model strings parsed for c. and p. descriptions; a hit is a shared protein key
              (one-letter, as concordance.protein_short) or cDNA with a target-gene row of
              the paper. Reported: papers with any variant hit; variant precision.
    phenotypes model terms looked up by exact HPO label or exact synonym (pinned hp.obo); a hit
              is a term equal to, or an ancestor of, a term observed in the paper's bound rows.
    recall    the model's own label: specific / guess / none.
(b) completion, per paper: word-level ROUGE-L F1 between the first 50 words of the
    continuation and the true next 50 words; longest common run of words; and the share of the
    true text's 5-grams that the continuation reproduces.
Summaries by stratum (after the Jun 2026 cutoff / recent / older), with an ordinary least
squares fit of each score on an "after" indicator and publication year (the confound named
in §7.4.3). Papers after the cutoff are few, so the comparison has little power; say so.

  uv run python analysis/bias/memorization/score_probes.py
writes analysis/bias/memorization/scores.csv and scores_summary.json/.md.
"""
from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

from pipeline.extract.normalize_variants import MISSING, is_gene, v
from pipeline.harness.concordance import ancestors_or_self, load_obo_parents, protein_short

ROOT = Path("analysis/bias/memorization")
HPO = Path("data/ontologies/2026-10-19/hp.obo")
CDNA = re.compile(r"c\.\s*[-*]?\d[\w+\-*_>]*", re.I)
PROT = re.compile(r"p\.\s*\(?[A-Za-z]{1,3}\d+[A-Za-z*]*(?:fs\*?\d*|\*)?\)?")
WORD = re.compile(r"[a-z0-9]+")
# A completion item whose opening is publisher boilerplate, not the paper's text, says nothing about
# memorizing the paper; it is excluded and listed. Found after the first scoring run (2026-10-21):
# tangier-33346003's selected paragraph was Elsevier's "Journal Pre-proof" notice.
BOILERPLATE = re.compile(r"This is a PDF file of an article that has undergone enhancements", re.I)


def hpo_lookup(path: Path) -> dict[str, str]:
    out, cur = {}, None
    for line in path.open():
        line = line.strip()
        if line == "[Term]":
            cur = None
        elif line.startswith("id: HP:"):
            cur = line[4:]
        elif cur and line.startswith("name: "):
            out.setdefault(line[6:].lower(), cur)
        elif cur and line.startswith("synonym: \"") and " EXACT" in line:
            out.setdefault(line.split('"')[1].lower(), cur)
    return out


def words(s: str) -> list[str]:
    return WORD.findall(s.lower())


def lcs(a: list[str], b: list[str]) -> int:
    prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0]
        for j, y in enumerate(b):
            cur.append(prev[j] + 1 if x == y else max(prev[j + 1], cur[j]))
        prev = cur
    return prev[-1]


def longest_run(a: list[str], b: list[str]) -> int:
    best, prev = 0, [0] * (len(b) + 1)
    for x in a:
        cur = [0]
        for j, y in enumerate(b):
            cur.append(prev[j] + 1 if x == y else 0)
        best = max(best, max(cur))
        prev = cur
    return best


def ngram_share(cont: list[str], true: list[str], n: int = 5) -> float | None:
    t = {tuple(true[i:i + n]) for i in range(len(true) - n + 1)}
    c = {tuple(cont[i:i + n]) for i in range(len(cont) - n + 1)}
    return len(t & c) / len(t) if t else None


def ols(y: list[float], cols: list[list[float]]) -> list[float] | None:
    """Least squares with an intercept, by normal equations (small k)."""
    X = [[1.0] + [c[i] for c in cols] for i in range(len(y))]
    k = len(X[0])
    A = [[sum(r[i] * r[j] for r in X) for j in range(k)] for i in range(k)]
    b = [sum(r[i] * yy for r, yy in zip(X, y)) for i in range(k)]
    for i in range(k):  # Gauss-Jordan
        piv = max(range(i, k), key=lambda r: abs(A[r][i]))
        if abs(A[piv][i]) < 1e-12:
            return None
        A[i], A[piv], b[i], b[piv] = A[piv], A[i], b[piv], b[i]
        for r in range(k):
            if r != i:
                f = A[r][i] / A[i][i]
                A[r] = [x - f * z for x, z in zip(A[r], A[i])]
                b[r] -= f * b[i]
    return [b[i] / A[i][i] for i in range(k)]


def main() -> int:
    sample = {(r["disease"], r["pmid"]): r for r in csv.DictReader((ROOT / "sample.csv").open())}
    valid = {b: all(x["valid"] for x in v) for b, v in json.loads((ROOT / "tool_check.json").read_text()).items()}
    look, parents, cache = hpo_lookup(HPO), load_obo_parents(HPO), {}
    rows, dropped, excluded = [], [], []
    for (d, pmid), s in sorted(sample.items()):
        gene = json.loads(Path(f"configs/stage4/{d}.json").read_text())["gene"]
        rows.append({"disease": d, "pmid": pmid, "stratum": s["stratum"], "year": int(s["year"])})
    by_key = {(r["disease"], r["pmid"]): r for r in rows}
    for d in sorted({r["disease"] for r in rows}):
        gene = json.loads(Path(f"configs/stage4/{d}.json").read_text())["gene"]
        run = Path(f"data/extracted/{d}/pv1-{d}")
        norm = {r["variant_key"]: r for r in csv.DictReader((run / "variants_normalized.csv").open())}
        obs = defaultdict(set)
        for r in csv.DictReader((run / "hpo_bindings.csv").open()):
            if r["status"] == "observed" and r["hpo_id"]:
                obs[r["pmid"]].add(r["hpo_id"])
        cb = ROOT / "responses" / f"{d}_closed_book.json"
        if cb.exists() and valid.get(f"{d}_closed_book", False):
            for a in json.loads(cb.read_text())["answers"]:
                pmid = a["id"].split("-", 1)[1]
                r = by_key.get((d, pmid))
                if r is None:
                    continue
                true_p, true_c = set(), set()
                t = (json.loads((run / "per_paper" / f"{pmid}.json").read_text()).get("tables") or {}).get("variants") or []
                for x in t:
                    if not is_gene(v(x.get("gene_symbol_as_stated")), gene):
                        continue
                    for f in ("protein_hgvs_as_stated", "variant_original_string"):
                        for m in PROT.findall(str(v(x.get(f)) or "")):
                            true_p.add(protein_short(m))
                    for f in ("cdna_hgvs_as_stated", "variant_original_string"):
                        for m in CDNA.findall(str(v(x.get(f)) or "")):
                            true_c.add(re.sub(r"\s", "", m).lower())
                for n in norm.values():
                    if pmid in (n.get("pmids") or "").split():
                        if n.get("hgvs_protein"):
                            true_p.add(protein_short(n["hgvs_protein"]))
                        if n.get("mane_hgvs_transcript"):
                            true_c.add(n["mane_hgvs_transcript"].split(":")[-1].lower())
                mv = a.get("variants") or []
                hits = 0
                for s_ in mv:
                    ps = {protein_short(m) for m in PROT.findall(s_)}
                    cs = {re.sub(r"\s", "", m).lower() for m in CDNA.findall(s_)}
                    hits += bool((ps & true_p) or (cs & true_c))
                ph = a.get("phenotypes") or []
                mapped = [look.get(p.lower().strip()) for p in ph]
                obs_anc = set()
                for o in obs.get(pmid, ()):
                    obs_anc.add(o)
                ph_hits = sum(1 for m in mapped if m and any(m in ancestors_or_self(o, parents, cache) for o in obs.get(pmid, ())))
                r.update({"cb_recall": a.get("recall"), "cb_variants_given": len(mv), "cb_variant_hits": hits,
                          "cb_true_variants": len(true_p | true_c) > 0, "cb_phen_given": len(ph),
                          "cb_phen_mapped": sum(1 for m in mapped if m), "cb_phen_hits": ph_hits})
        elif cb.exists():
            dropped.append(f"{d}_closed_book")
        cp = ROOT / "responses" / f"{d}_completion.json"
        if cp.exists() and valid.get(f"{d}_completion", False):
            tg = json.loads((ROOT / "targets" / f"{d}_completion.json").read_text())
            openings = {it["id"]: it["opening"] for it in json.loads((ROOT / "batches" / f"{d}_completion.json").read_text())["items"]}
            for a in json.loads(cp.read_text())["answers"]:
                pmid = a["id"].split("-", 1)[1]
                r = by_key.get((d, pmid))
                if r is None or a["id"] not in tg:
                    continue
                if BOILERPLATE.search(openings.get(a["id"], "")):
                    excluded.append(a["id"])
                    continue
                c, t = words(a.get("continuation") or "")[:50], words(tg[a["id"]])
                l = lcs(c, t)
                f1 = 2 * l / (len(c) + len(t)) if c and t else 0.0
                r.update({"cp_recall": a.get("recall"), "cp_rougeL_f1": round(f1, 4), "cp_longest_run": longest_run(c, t),
                          "cp_5gram_share": round(ngram_share(c, t) or 0.0, 4)})
        elif cp.exists():
            dropped.append(f"{d}_completion")
    keys = sorted({k for r in rows for k in r})
    with (ROOT / "scores.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader(); w.writerows(rows)

    def summ(sel: list[dict]) -> dict:
        cb = [r for r in sel if "cb_recall" in r]
        cp = [r for r in sel if "cp_rougeL_f1" in r]
        mean = lambda xs: round(sum(xs) / len(xs), 4) if xs else None
        return {"papers": len(sel), "closed_book_scored": len(cb),
                "cb_specific": sum(r["cb_recall"] == "specific" for r in cb), "cb_guess": sum(r["cb_recall"] == "guess" for r in cb),
                "cb_none": sum(r["cb_recall"] == "none" for r in cb),
                "cb_papers_with_variant_hit": sum(r["cb_variant_hits"] > 0 for r in cb),
                "cb_variants_given": sum(r["cb_variants_given"] for r in cb), "cb_variant_hits": sum(r["cb_variant_hits"] for r in cb),
                "cb_phen_given": sum(r["cb_phen_given"] for r in cb), "cb_phen_mapped": sum(r["cb_phen_mapped"] for r in cb),
                "cb_phen_hits": sum(r["cb_phen_hits"] for r in cb),
                "completion_scored": len(cp), "cp_specific": sum(r["cp_recall"] == "specific" for r in cp),
                "cp_mean_rougeL_f1": mean([r["cp_rougeL_f1"] for r in cp]), "cp_max_longest_run": max([r["cp_longest_run"] for r in cp], default=None),
                "cp_mean_5gram_share": mean([r["cp_5gram_share"] for r in cp]),
                "cp_papers_run_ge_8": sum(r["cp_longest_run"] >= 8 for r in cp)}
    out = {"date": datetime.now(UTC).date().isoformat(), "dropped_batches": dropped, "excluded_boilerplate_items": excluded, "by_disease_stratum": {}, "by_stratum": {}, "fits": {}}
    for d in sorted({r["disease"] for r in rows}):
        for s in ("after", "recent", "older"):
            sel = [r for r in rows if r["disease"] == d and r["stratum"] == s]
            if sel:
                out["by_disease_stratum"][f"{d}|{s}"] = summ(sel)
    for s in ("after", "recent", "older"):
        out["by_stratum"][s] = summ([r for r in rows if r["stratum"] == s])
    for score in ("cp_rougeL_f1", "cp_5gram_share"):
        sel = [r for r in rows if score in r]
        if len(sel) > 5 and any(r["stratum"] == "after" for r in sel):
            beta = ols([r[score] for r in sel], [[1.0 if r["stratum"] == "after" else 0.0 for r in sel], [float(r["year"]) for r in sel]])
            out["fits"][score] = {"n": len(sel), "intercept_after_year": [round(b, 5) for b in beta] if beta else None,
                                  "note": "score ~ after-cutoff + publication year; descriptive, few after-cutoff papers"}
    (ROOT / "scores_summary.json").write_text(json.dumps(out, indent=1) + "\n")
    L = [f"# Memorization probe scores, Claude side ({out['date']})", "",
         "*Generated by `analysis/bias/memorization/score_probes.py`. Scored against the pv1 full-text extraction, never against ClinVar or OMIM. Exploratory per §7.4.3; papers after the Jun 2026 cutoff are few.*", "",
         "| Stratum | Papers | Closed-book: specific / guess / none | Papers with a variant hit | Variants given (hits) | Phenotype terms given, mapped to HPO, hits | Completion: mean ROUGE-L F1 | Mean 5-gram share | Longest run (max) | Runs of 8+ words |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for s, x in out["by_stratum"].items():
        L.append(f"| {s} | {x['papers']} | {x['cb_specific']} / {x['cb_guess']} / {x['cb_none']} | {x['cb_papers_with_variant_hit']} | {x['cb_variants_given']} ({x['cb_variant_hits']}) | "
                 f"{x['cb_phen_given']}, {x['cb_phen_mapped']}, {x['cb_phen_hits']} | {x['cp_mean_rougeL_f1']} | {x['cp_mean_5gram_share']} | {x['cp_max_longest_run']} | {x['cp_papers_run_ge_8']} |")
    if dropped:
        L += ["", f"Dropped for disallowed tool use: {', '.join(dropped)}."]
    if excluded:
        L += ["", f"Completion items excluded because the opening was publisher boilerplate, not paper text: {', '.join(excluded)}."]
    (ROOT / "scores_summary.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
