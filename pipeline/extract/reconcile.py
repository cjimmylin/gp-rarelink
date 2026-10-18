"""Deterministic cross-paper merging of individuals (POC_DESIGN.md §3.6).

The same patient is often reported in several papers: a case report, then a
cohort, then a review table. This script decides which per-paper individual
rows describe the same person. It uses only the extraction output and the
papers' own reference lists, never ClinVar or OMIM (ground-truth isolation),
and it involves no model call, so the same inputs always give the same merges.

Variant key. Two individuals can only be merged if they share a variant in the
target gene. Variants are compared on the cDNA HGVS as stated (transcript
prefix, spaces and case removed) when both rows give one; otherwise on the
protein HGVS (three-letter amino acids folded to one letter, Ter/X folded to
*); otherwise on the original string. Different variants are never merged.

Citation link. Each paper's reference list (from its JATS XML; the papers are
literature, not reference data) is used to resolve
  - an individual's source_reference_in_review (e.g. "[12]", "Zhou et al. 2016"),
  - the paper's prior_report_citation, when cites_prior_report_of_same_patients is true,
to PMIDs. Resolution is by reference number first, then by surname plus year.

Confidence labels (policy v2, 2026-10-18):
  explicit_citation  same variant, and one row's own source_reference_in_review
                     resolves to the other row's PMID.
  strong_match       same variant and no conflict, plus either (a) the paper-level
                     prior-report citation resolves to the other PMID, or (b) same
                     sex and age at onset within 1 year, both stated.
  weak_match         same variant, sex not in conflict, nothing else. Never merged;
                     listed for the human audit.
  blocked_conflict   same variant but a conflict. A conflict is a stated sex that
                     differs (this blocks even an explicit citation), or, without an
                     explicit citation, stated onset ages more than 2 years apart.
Explicit and strong candidates are merged only if both hold:
  - one-to-one: within the other paper, each row is the other's unique best
    candidate. Candidates are ranked by confidence, then by agreement score
    (+1 each for same stated sex, same stated proband status, onset within 1
    year). A review row that cites a family and matches several relatives with
    the same variant is therefore left unmerged ("ambiguous_one_to_many");
  - no identity may hold two rows from the same paper ("skipped_same_paper").
Policy v1 (earlier the same day) merged every explicit or strong candidate; on
the first 58 run-1 papers that joined relatives into one identity.

Merged pairs are joined transitively into identities. The record of record for
an identity is a first-hand row (no source_reference_in_review), earliest
publication year first, then lowest PMID. An identity made only of rows taken
from summaries of earlier reports is flagged review_only.

Writes, under data/extracted/<disease>/<run_id>/:
  merges.csv               one row per candidate pair (merged or not)
  individuals_reconciled.csv  one row per individual with its identity id
  reconcile_summary.json   counts before and after merging, by confidence

  uv run python -m pipeline.extract.reconcile --disease ha20 --run-id poc-ha20-run-1
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from itertools import combinations
from pathlib import Path

POLICY_VERSION = "merge_policy_v2"
MISSING = {None, "", "not reported", "unknown"}
AA3 = {"ala": "A", "arg": "R", "asn": "N", "asp": "D", "cys": "C", "gln": "Q", "glu": "E", "gly": "G",
       "his": "H", "ile": "I", "leu": "L", "lys": "K", "met": "M", "phe": "F", "pro": "P", "ser": "S",
       "thr": "T", "trp": "W", "tyr": "Y", "val": "V", "ter": "*", "sec": "U"}
ISO_PART = re.compile(r"(\d+(?:\.\d+)?)([YMWD])")


def v(cell):
    return (cell or {}).get("value")


# ---- variant keys -------------------------------------------------------------
def cdna_key(s) -> str | None:
    if s in MISSING:
        return None
    s = re.sub(r"\s+", "", str(s)).lower()
    s = s.split(":")[-1]
    m = re.search(r"c\.[^,;()]+", s)
    return m.group(0) if m else None


AA = r"(?:Ala|Arg|Asn|Asp|Cys|Gln|Glu|Gly|His|Ile|Leu|Lys|Met|Phe|Pro|Ser|Thr|Trp|Tyr|Val|Ter|Sec|[ACDEFGHIKLMNPQRSTVWY])"
BARE_PROTEIN = re.compile(rf"^\(?({AA}\d+(?:{AA}|\*|X)?(?:fs(?:\*|X|Ter)?\d*)?|{AA}\d+(?:{AA}|\*|X))\)?$")


def protein_key(s) -> str | None:
    """Protein change with notation folded: 'p.(Arg271Ter)', 'p.R271*', 'R271X' and 'Arg271Ter' all give 'p.R271*'.

    Bare forms without 'p.' are accepted when the whole string looks like a protein
    change (amino acid, position, amino acid or stop or frameshift), since reviews
    often print them that way.
    """
    if s in MISSING:
        return None
    s = re.sub(r"\s+", "", str(s))
    s = s.split(":")[-1]
    m = re.search(r"p\.\(?([^,;]+?)\)?$", s) or re.search(r"p\.\(?([A-Za-z*0-9_]+(?:fs\*?\d*|fsX\d*|fsTer\d*)?)", s)
    if m:
        body = m.group(1)
    else:
        b = BARE_PROTEIN.match(s)
        if not b:
            return None
        body = b.group(1)
    body = body.replace("(", "").replace(")", "")
    body = re.sub(r"(?i)(ala|arg|asn|asp|cys|gln|glu|gly|his|ile|leu|lys|met|phe|pro|ser|thr|trp|tyr|val|ter|sec)",
                  lambda x: AA3[x.group(1).lower()], body)
    body = body.replace("X", "*")
    return "p." + body


def orig_key(s) -> str | None:
    return None if s in MISSING else re.sub(r"\s+", "", str(s)).lower()


def same_variant(a: dict, b: dict) -> str | None:
    """Return the matching key if two variant rows describe the same variant, else None."""
    if a["cdna"] and b["cdna"]:
        return a["cdna"] if a["cdna"] == b["cdna"] else None
    if a["protein"] and b["protein"]:
        return a["protein"] if a["protein"] == b["protein"] else None
    if a["orig"] and b["orig"] and a["orig"] == b["orig"]:
        return a["orig"]
    return None


# ---- references ---------------------------------------------------------------
def reference_list(xml_path: Path) -> list[tuple[str, str, str]]:
    """(label, citation text, pmid) for each reference in the paper's JATS XML.

    Read from the XML rather than the Markdown because some publishers nest the
    reference list inside a section, which the Markdown flattens into one
    paragraph. A reference without a <label> gets its position in the list.
    PMIDs come from <pub-id pub-id-type="pmid"> or <ext-link ext-link-type="pmid">.
    """
    if not xml_path.exists():
        return []
    root = ET.fromstring(xml_path.read_bytes())
    for el in root.iter():
        if isinstance(el.tag, str) and "}" in el.tag:
            el.tag = el.tag.split("}", 1)[1]
    refs = []
    for n, ref in enumerate(root.iter("ref"), 1):
        label_el = ref.find("label")
        label = "".join(label_el.itertext()).strip() if label_el is not None else str(n)
        pmid = ""
        for pid in ref.iter("pub-id"):
            if pid.get("pub-id-type") == "pmid" and (pid.text or "").strip().isdigit():
                pmid = pid.text.strip()
        if not pmid:
            for link in ref.iter("ext-link"):
                if link.get("ext-link-type") == "pmid":
                    href = next((val for key, val in link.attrib.items() if key.endswith("href")), "")
                    if href.strip().isdigit():
                        pmid = href.strip()
        cit = next((c for c in ref if c.tag in ("element-citation", "mixed-citation", "citation", "nlm-citation")), ref)
        text = re.sub(r"\s+", " ", " ".join(cit.itertext())).strip()
        refs.append((label, text, pmid))
    return refs


def resolve(citation, refs: list[tuple[str, str, str]]) -> list[str]:
    """PMIDs that a verbatim citation string points to, using the paper's own reference list."""
    if citation in MISSING or not refs:
        return []
    s = str(citation)
    direct = re.findall(r"PMID:?\s*(\d{6,9})", s)
    if direct:
        return sorted(set(direct))
    by_label = {}
    for label, _, pmid in refs:
        digits = re.sub(r"\D", "", label)
        if digits:
            by_label.setdefault(digits, pmid)
    nums: list[str] = []
    for a, b in re.findall(r"(?<!\d)(\d{1,3})\s*[–—-]\s*(\d{1,3})(?!\d)", s):
        if int(a) < int(b) <= int(a) + 20:
            nums += [str(n) for n in range(int(a), int(b) + 1)]
    nums += [n for n in re.findall(r"(?<!\d)(\d{1,3})(?!\d)", s)]
    out = {by_label[n] for n in nums if by_label.get(n)}
    if out:
        return sorted(out)
    years = re.findall(r"(?<!\d)(19\d\d|20\d\d)(?!\d)", s)
    surname = re.match(r"\s*([A-Z][A-Za-z'\-]+)", s)
    if surname and years:
        hits = {pmid for _, text, pmid in refs
                if pmid and text.lower().startswith(surname.group(1).lower()) and years[0] in text}
        if len(hits) == 1:
            return sorted(hits)
    return []


# ---- ages ---------------------------------------------------------------------
def years(iso) -> float | None:
    if iso in MISSING or not str(iso).startswith("P"):
        return None
    total = 0.0
    for num, unit in ISO_PART.findall(str(iso)):
        total += float(num) * {"Y": 1, "M": 1 / 12, "W": 1 / 52, "D": 1 / 365}[unit]
    return total


# ---- main ---------------------------------------------------------------------
def load(run_dir: Path, xml_dir: Path, gene: str) -> tuple[list[dict], dict[str, dict]]:
    people, papers = [], {}
    for path in sorted((run_dir / "per_paper").glob("*.json")):
        doc = json.loads(path.read_text())
        pmid = str(doc.get("pmid") or path.stem)
        t = doc.get("tables") or {}
        pub = (t.get("publications") or [{}])[0]
        refs = reference_list(xml_dir / f"{pmid}.nxml")
        prior = resolve(v(pub.get("prior_report_citation")), refs) if v(pub.get("cites_prior_report_of_same_patients")) is True else []
        year = v(pub.get("year"))
        papers[pmid] = {"year": int(year) if str(year or "").isdigit() else 9999, "study_type": v(pub.get("study_type")),
                        "prior_pmids": prior, "n_refs": len(refs)}
        variants = defaultdict(list)
        for r in t.get("variants") or []:
            if str(v(r.get("gene_symbol_as_stated")) or "").upper() != gene:
                continue
            variants[v(r.get("individual_label_in_paper"))].append({
                "cdna": cdna_key(v(r.get("cdna_hgvs_as_stated"))) or cdna_key(v(r.get("variant_original_string"))),
                "protein": protein_key(v(r.get("protein_hgvs_as_stated"))) or protein_key(v(r.get("variant_original_string"))),
                "orig": orig_key(v(r.get("variant_original_string"))),
            })
        for r in t.get("individuals") or []:
            label = v(r.get("individual_label_in_paper"))
            src = v(r.get("source_reference_in_review"))
            people.append({
                "pmid": pmid, "label": label, "sex": v(r.get("sex")), "proband": v(r.get("is_proband")),
                "onset": years(v(r.get("age_at_onset_iso8601"))),
                "family": v(r.get("family_label_in_paper")),
                "source_reference": src if src not in MISSING else "",
                "source_pmids": resolve(src, refs),
                "variants": variants.get(label, []),
            })
    return people, papers


def compare(a: dict, b: dict, papers: dict[str, dict]) -> dict | None:
    key = next((k for va in a["variants"] for vb in b["variants"] if (k := same_variant(va, vb))), None)
    if key is None:
        return None
    conflicts = []
    if a["sex"] not in MISSING and b["sex"] not in MISSING and a["sex"] != b["sex"]:
        conflicts.append(f"sex {a['sex']} vs {b['sex']}")
    if a["onset"] is not None and b["onset"] is not None and abs(a["onset"] - b["onset"]) > 2:
        conflicts.append(f"onset {a['onset']:.1f}y vs {b['onset']:.1f}y")
    evidence = [f"same {gene_key_kind(key)} {key}"]
    cited = b["pmid"] in a["source_pmids"] or a["pmid"] in b["source_pmids"]
    sex_conflict = any(c.startswith("sex") for c in conflicts)
    if cited:
        side = a if b["pmid"] in a["source_pmids"] else b
        evidence.append(f"source_reference_in_review of {side['pmid']}:{side['label']} = {side['source_reference']!r} resolves to the other PMID")
    if (cited and sex_conflict) or (not cited and conflicts):
        return {"variant_key": key, "confidence": "blocked_conflict", "candidate": False, "score": 0,
                "evidence": "; ".join(evidence), "conflicts": "; ".join(conflicts)}
    if cited:
        conf = "explicit_citation"
    elif b["pmid"] in papers[a["pmid"]]["prior_pmids"] or a["pmid"] in papers[b["pmid"]]["prior_pmids"]:
        evidence.append("paper-level prior_report_citation resolves to the other PMID")
        conf = "strong_match"
    elif (a["sex"] not in MISSING and a["sex"] == b["sex"] and a["onset"] is not None and b["onset"] is not None
          and abs(a["onset"] - b["onset"]) <= 1):
        evidence.append(f"same sex ({a['sex']}); onset {a['onset']:.1f}y vs {b['onset']:.1f}y")
        conf = "strong_match"
    else:
        evidence.append("no corroborating detail")
        conf = "weak_match"
    if a["family"] not in MISSING and a["family"] == b["family"]:
        evidence.append(f"same family label {a['family']!r}")
    score = ((a["sex"] not in MISSING and a["sex"] == b["sex"])
             + (a["proband"] is not None and a["proband"] == b["proband"])
             + (a["onset"] is not None and b["onset"] is not None and abs(a["onset"] - b["onset"]) <= 1))
    return {"variant_key": key, "confidence": conf, "candidate": conf in ("explicit_citation", "strong_match"),
            "score": int(score), "evidence": "; ".join(evidence), "conflicts": "; ".join(conflicts)}


def gene_key_kind(key: str) -> str:
    return "cDNA" if key.startswith("c.") else ("protein" if key.startswith("p.") else "original string")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--gene", default="TNFAIP3")
    args = ap.parse_args(argv)
    run_dir = Path("data/extracted") / args.disease / args.run_id
    xml_dir = Path("data/literature") / args.disease / "fulltext"
    people, papers = load(run_dir, xml_dir, args.gene.upper())
    corpus = set(papers)

    pairs = []
    for i, j in combinations(range(len(people)), 2):
        a, b = people[i], people[j]
        if a["pmid"] == b["pmid"]:
            continue
        res = compare(a, b, papers)
        if res:
            pairs.append((i, j, res))

    # one-to-one: keep a candidate pair only if each row is the other's unique best in that paper
    conf_rank = {"explicit_citation": 2, "strong_match": 1}
    options: dict[tuple[int, str], list[tuple[tuple[int, int], int]]] = defaultdict(list)
    for i, j, res in pairs:
        if res["candidate"]:
            key = (conf_rank[res["confidence"]], res["score"])
            options[(i, people[j]["pmid"])].append((key, j))
            options[(j, people[i]["pmid"])].append((key, i))

    def unique_best(row: int, paper: str) -> int | None:
        opts = sorted(options[(row, paper)], reverse=True)
        if len(opts) == 1 or (opts and opts[0][0] > opts[1][0]):
            return opts[0][1]
        return None

    for i, j, res in pairs:
        if not res["candidate"]:
            res["decision"] = "not_merged_" + res["confidence"]
        elif unique_best(i, people[j]["pmid"]) == j and unique_best(j, people[i]["pmid"]) == i:
            res["decision"] = "pending"
        else:
            res["decision"] = "ambiguous_one_to_many"

    parent = list(range(len(people)))
    papers_in = {i: {people[i]["pmid"]} for i in range(len(people))}

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    order = sorted((k for k in range(len(pairs)) if pairs[k][2]["decision"] == "pending"),
                   key=lambda k: (-conf_rank[pairs[k][2]["confidence"]], -pairs[k][2]["score"],
                                  people[pairs[k][0]]["pmid"], str(people[pairs[k][0]]["label"]),
                                  people[pairs[k][1]]["pmid"], str(people[pairs[k][1]]["label"])))
    for k in order:
        i, j, res = pairs[k]
        ri, rj = find(i), find(j)
        if ri == rj:
            res["decision"] = "merged"
        elif papers_in[ri] & papers_in[rj]:
            res["decision"] = "skipped_same_paper"
        else:
            parent[ri] = rj
            papers_in[rj] |= papers_in.pop(ri)
            res["decision"] = "merged"
    for _, _, res in pairs:
        res["merged"] = res["decision"] == "merged"
    clusters = defaultdict(list)
    for i in range(len(people)):
        clusters[find(i)].append(i)

    def rank(i: int):
        p = people[i]
        return (bool(p["source_reference"]), papers[p["pmid"]]["year"], p["pmid"], str(p["label"]))

    ordered = sorted(clusters.values(), key=lambda m: min(rank(i) for i in m))
    identity, record, review_only = {}, set(), set()
    for n, members in enumerate(ordered, 1):
        ident = f"{args.disease.upper()}-ID{n:04d}"
        best = min(members, key=rank)
        record.add(best)
        for i in members:
            identity[i] = ident
        if all(people[i]["source_reference"] for i in members):
            review_only.update(members)

    with (run_dir / "merges.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["pmid_a", "label_a", "pmid_b", "label_b", "variant_key", "confidence", "agreement_score",
                    "decision", "merged", "evidence", "conflicts", "identity", "policy"])
        for i, j, res in pairs:
            a, b = people[i], people[j]
            w.writerow([a["pmid"], a["label"], b["pmid"], b["label"], res["variant_key"], res["confidence"],
                        res["score"], res["decision"], res["merged"], res["evidence"], res["conflicts"], identity[i] if res["merged"] else "", POLICY_VERSION])
    with (run_dir / "individuals_reconciled.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["pmid", "individual_label_in_paper", "identity", "record_of_record", "review_only",
                    "has_target_gene_variant", "source_reference_in_review", "source_pmids_resolved",
                    "source_pmids_in_corpus"])
        for i, p in enumerate(people):
            w.writerow([p["pmid"], p["label"], identity[i], i in record, i in review_only, bool(p["variants"]),
                        p["source_reference"], " ".join(p["source_pmids"]),
                        " ".join(x for x in p["source_pmids"] if x in corpus)])

    from collections import Counter
    conf = Counter(res["confidence"] for _, _, res in pairs)
    secondary = [p for p in people if p["source_reference"]]
    summary = {
        "run_id": args.run_id,
        "policy": POLICY_VERSION,
        "individuals_before_merging": len(people),
        "identities_after_merging": len(ordered),
        "identities_with_target_gene_variant": len({identity[i] for i, p in enumerate(people) if p["variants"]}),
        "identities_review_only": len({identity[i] for i in review_only}),
        "candidate_pairs_by_confidence": dict(sorted(conf.items())),
        "candidate_pairs_by_decision": dict(sorted(Counter(res["decision"] for _, _, res in pairs).items())),
        "merged_pairs": sum(1 for *_, r in pairs if r["merged"]),
        "rows_from_prior_report_summaries": len(secondary),
        "of_which_source_resolved_to_pmid": sum(1 for p in secondary if p["source_pmids"]),
        "of_which_source_pmid_in_corpus": sum(1 for p in secondary if set(p["source_pmids"]) & corpus),
        "papers_without_parsed_reference_list": sorted(k for k, x in papers.items() if x["n_refs"] == 0),
    }
    (run_dir / "reconcile_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
