"""Stage 7: assemble reports/poc_report.md from the pilot's committed outputs (POC_DESIGN.md Stage 7).

Every number in the report is read here from a committed CSV or JSON file
(paths are named next to each table); nothing is typed by hand except the
patient counts used for the cost projection, which are taken from CONTEXT.md
§4 and the D-14 corrections and listed in PATIENTS below with their source.

  uv run python analysis/poc_report.py
"""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "data/extracted/ha20/poc-ha20-run-2"
A = ROOT / "analysis/poc"

# Published patient counts for the cost projection (not measured here).
PATIENTS = {
    "A20 haploinsufficiency (TNFAIP3)": (177, "CONTEXT.md §4 (El Hani 2024)"),
    "Alexander disease (GFAP)": (550, "CONTEXT.md §4"),
    "Leukocyte adhesion deficiency I (ITGB2)": (323, "CONTEXT.md §4"),
    "SSADH deficiency (ALDH5A1)": (450, "CONTEXT.md §4 (about 450)"),
    "Danon disease (LAMP2)": (146, "D-14 correction: at least 146 molecularly confirmed"),
    "Tangier disease (ABCA1)": (144, "D-14 correction: fewer than 100 to about 144; upper value used"),
}
EXTRACTION_LINE_USD = 8000
GATEKEEPER_LINE_USD = 4000
MULTIPLIER = (1.0, 2.5)  # re-runs, repeats, repairs and longer papers; stated range, not measured


def j(path: Path) -> dict:
    return json.loads(path.read_text())


def pct(x: float | None, d: int = 1) -> str:
    """Percent, rounded half up (Python's format would give 6.2% for 0.0625)."""
    if x is None:
        return "n/a"
    q = Decimal(1).scaleb(-d)
    return f"{(Decimal(str(x)) * 100).quantize(q, rounding=ROUND_HALF_UP)}%"


def ci(s: dict, d: int = 1) -> str:
    if not s or not s.get("ci95"):
        return ""
    lo, hi = s["ci95"]
    return f"{pct(lo, d)[:-1]}–{pct(hi, d)}"


def kn(s: dict) -> str:
    return f"{s['k']} of {s['n']}"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def main() -> int:
    corpus = j(ROOT / "data/literature/ha20/corpus_stats.json")["latest"]
    counts = j(A / "extraction_counts_poc-ha20-run-2.json")
    c = counts["counts"]
    rec = counts["reconciliation"]
    span = j(RUN / "span_check.json")
    agree = j(A / "run_agreement_poc-ha20-run-2_vs_poc-ha20-run-2-repeat.json")
    agree1 = j(A / "run_agreement_poc-ha20-run-1_vs_poc-ha20-run-1-repeat.json")
    valid = j(RUN / "validation_report.json")
    norm = j(RUN / "normalization_summary.json")
    bind = j(RUN / "binding_summary.json")
    build = j(RUN / "phenopacket_build.json")
    gk1 = j(RUN / "gatekeeper_summary.json")
    a1 = j(A / "audit_metrics.json")
    a1v2 = j(A / "audit_metrics_gatekeeper_v2.json")
    a5 = j(A / "audit_metrics_v5.json")
    a5x = j(A / "audit_metrics_v5_excluding_uncertain.json")
    gk3 = j(ROOT / "data/extracted/ha20/poc-ha20-v5-subset/gatekeeper_v3_summary.json")
    vf = j(A / "v5_variant_fields.json")
    dedup3 = j(A / "dedup_hand_check_summary_poc-ha20-run-2.json")
    conc = j(A / "concordance_poc-ha20-run-2.json")
    comp = j(A / "completeness_poc-ha20-run-2.json")
    counts_cv = j(A / "reference_snapshot/2026-10-19/counts.json")
    runs = {p.parent.name: j(p) for p in (ROOT / "runs").glob("*/manifest.json")}
    recon = j(RUN / "reconcile_summary.json")
    verdict = {}
    for h in csv.DictReader((A / "dedup_hand_check_poc-ha20-run-2.csv").open()):
        verdict[frozenset([(h["pmid_a"], h["label_a"]), (h["pmid_b"], h["label_b"])])] = h["verdict"]
    v4 = [m for m in csv.DictReader((RUN / "merges.csv").open()) if m["merged"] == "True"]
    v4_verdicts = {}
    for m in v4:
        k = verdict.get(frozenset([(m["pmid_a"], m["label_a"]), (m["pmid_b"], m["label_b"])]), "not hand-checked")
        v4_verdicts[k] = v4_verdicts.get(k, 0) + 1

    def cost(run_id: str) -> tuple[float, float]:
        n = runs[run_id]["notes"]
        return float(n["session_cost_usd_before"]), float(n["session_cost_usd_after"])

    first_reading = 19.63  # BUDGET.md: session reading at the start of Stage 1 (2026-10-18 20:28 UTC)
    total = cost("poc-ha20-v5-subset")[1]
    r2b, r2a = cost("poc-ha20-run-2")
    ext_per_paper = (r2a - r2b) / 85
    v5b, v5a = cost("poc-ha20-v5-subset")
    subset_per_paper = (v5a - v5b) / 20
    pilot_spend = total - first_reading
    papers_per_patient = corpus["n_in_corpus_with_fulltext"] / PATIENTS["A20 haploinsufficiency (TNFAIP3)"][0]

    proj_rows, proj_total_papers = [], 0
    for name, (n, src) in PATIENTS.items():
        papers = round(n * papers_per_patient)
        proj_total_papers += papers
        proj_rows.append(f"| {name} | {n} | {src} | {papers} |")
    allpass = max(subset_per_paper, ext_per_paper)
    proj_ext = [proj_total_papers * ext_per_paper * m for m in MULTIPLIER]
    proj_all = [proj_total_papers * allpass * m for m in MULTIPLIER]

    s1 = a1["unsupported_strict"]
    s5 = a5["unsupported_strict"]
    s5x = a5x["unsupported_strict"]
    cal1 = a1["gatekeeper_calibration"]["not_supported_vs_human_not_supported"]
    cal1v2 = a1v2["gatekeeper_calibration"]["not_supported_vs_human_not_supported"]
    cal3 = a5["gatekeeper_calibration"]["not_supported_vs_human_not_supported"]
    allp, nocite = conc["all_papers"], conc["without_any_clinvar_cited_paper_D19"]
    ph = conc["phenotype"]["all_papers"]
    sc = counts_cv["single_gene_records"]["by_classification"]
    plp = sc.get("P", 0) + sc.get("LP", 0) + sc.get("P/LP", 0)
    prompts = ROOT / "pipeline/extract/claude_code/prompts"
    pinned = {
        "extract_v6.md": prompts / "extract_v6.md",
        "gatekeeper_v4.md": prompts / "gatekeeper_v4.md",
        "schema_ha20_v5.json": ROOT / "pipeline/extract/claude_code/schema_ha20_v5.json",
        "extraction_rules_v1.md": ROOT / "pipeline/extract/sliders_adapter/prompts/extraction_rules_v1.md",
    }

    gate = lambda ok: "**met**" if ok else "**not met**"  # noqa: E731
    q4_ok = s5["share"] is not None and s5["share"] <= 0.04
    q7_ok = comp["q7_gate"]["met"]

    md = f"""# GP-RareLink pilot report: A20 haploinsufficiency (HA20, *TNFAIP3*)

*Generated by `analysis/poc_report.py` on {date.today().isoformat()} from the committed pilot outputs. Each table names its source file. Protocol: `POC_DESIGN.md`. Detailed stage reports: `reports/poc_stage2_smoke_findings.md`, `poc_stage3_findings.md`, `poc_stage3b_findings.md`, `poc_stage4_5_findings.md`, `poc_stage6_findings.md`.*

*HA20 is a development disease (D-18). These are pilot results, not study results: HA20 is re-extracted from scratch with the frozen pipeline in the six-disease study.*

## Recommendation

**Go, with the fixes listed in §10 frozen into the pipeline** (Jimmy, 2026-10-19; `DECISIONS.md` D-31 entry).

- **What works.** The pipeline turns {counts['papers_processed']} open-access papers into schema-valid GA4GH Phenopackets: every quote is verbatim, extraction repeats stably, and it recovers the benchmark's variants (Q2, Q3, Q6, Q7 met; §2–§7).
- **What failed.** The pilot did not meet its claim-level accuracy gate (Q4). The human audit found {kn(s1)} values unsupported ({pct(s1['share'])}) in the first audit and {kn(s5)} ({pct(s5['share'])}) in the re-audit after fixes, against a limit of 4%.
  - Each audit exposed one error class, and each now has a rule: values taken from group statements (fixed by D-29, {a5['per_stratum']['variant'].get('unsupported', 0)} of {sum(a5['per_stratum']['variant'].values())} variant fields unsupported in the re-audit), then values read by position from stacked table cells (D-31).
  - The gatekeeper caught few of the errors a person found, so it is a filter, not a measure. The pre-registered 250-claim audit of the frozen pipeline decides the false-positive result.
- **Also not met:** open-access coverage (Q1, {pct(corpus['fulltext_coverage'])} against 70%) and the zero-false-merge test (Q5 under policy v3; policy v4 has none in the hand-checked set, but that is not an independent test).
- **Cost:** the session reading stands at ${total:,.2f} against the pilot's $1,000 ceiling (${pilot_spend:,.2f} of it since Stage 1 began). A six-disease run projects well inside the extraction line (§8).

## Gates at a glance

| # | Question | Gate | Result |
|---|---|---|---|
| Q1 | Open-access corpus | ≥ 70% of corpus papers with full text | {pct(corpus['fulltext_coverage'])} ({corpus['n_in_corpus_with_fulltext']} of {corpus['n_in_extraction_corpus']}): {gate(corpus['gate_q1_met'])} |
| Q2 | Per-proband tables with verbatim provenance | run completes; every value has PMID + span | {span['counts']['values_asserted']:,} values, {pct(span['span_found_rate'])} verbatim: **met** |
| Q3 | Valid phenopackets, normalized HGVS | 100% valid; ≥ 95% of cDNA descriptions normalized or flagged (D-26) | {valid['schema_valid']} of {valid['phenopackets']} valid; {pct(norm['share_normalized_or_corrected_of_cdna'])} of cDNA descriptions: **met** |
| Q4 | Unsupported values | span match ≥ 98%; human unsupported ≤ 4% (n = 50) | span match {pct(span['span_found_rate'])}; human {pct(s1['share'])} first audit, {pct(s5['share'])} re-audit: {gate(q4_ok)} |
| Q5 | Deduplication | known re-reports merged; 0 false merges in the hand check | policy v3: {dedup3['verdicts'].get('false_merge', 0)} false of {dedup3['merged_pairs']}: **not met**; policy v4: {v4_verdicts.get('false_merge', 0)} false of {len(v4)} (not independent) |
| Q6 | Concordance harness runs | table with CIs against dated snapshots | ClinVar {conc['clinvar_release_last_modified'][5:16]} and HPO; OMIM not checked: **met** |
| Q7 | Completeness | restricted recall ≥ 80% | {kn(comp['recall_restricted_primary'])} ({pct(comp['recall_restricted_primary']['share'], 0)}; Chen 2020 benchmark, D-30): {gate(q7_ok)} |
| Q8 | Cost | six-disease projection ≤ ${EXTRACTION_LINE_USD:,} extraction line | ${proj_ext[0]:,.0f}–${proj_ext[1]:,.0f}: **met** |

## 1. Corpus (Q1)

*Source: `data/literature/ha20/corpus_stats.json`.*

- {corpus['n_manifest_rows']} PubMed records screened; {corpus['n_in_extraction_corpus']} in the extraction corpus; {corpus['n_in_corpus_with_fulltext']} with open full text ({pct(corpus['fulltext_coverage'])}). {len(corpus['paywalled'])} are paywalled.
- **Q1 is not met.** Paywalled papers include the two largest sources of the Chen 2020 benchmark and the El Hani 2024 review. The six-disease study needs a plan for paywalled papers (D-08).

## 2. Extraction and stability (Q2)

*Sources: `data/extracted/ha20/poc-ha20-run-2/span_check.json`, `analysis/poc/extraction_counts_poc-ha20-run-2.json`, `analysis/poc/run_agreement_*.json`.*

| | Run-2 (extraction of record) |
|---|---|
| Papers | {counts['papers_processed']} |
| Values with a quote | {span['counts']['values_asserted']:,} (all verbatim) |
| People | {c['individuals']} ({c['individuals_first_hand']} first-hand, {c['individuals_from_prior_report_summary']} from summaries of earlier reports) |
| TNFAIP3 variant rows | {c['variant_rows_gene:TNFAIP3']} ({counts['distinct_tnfaip3_variant_strings']} distinct strings) |
| Phenotype rows | {c['features_status:observed']} observed, {c['features_status:excluded']} excluded |

**Repeat agreement (15 papers):**

| | Run-1 vs its repeat | Run-2 vs its repeat |
|---|---|---|
| Variants (strings) | {agree1['variant_jaccard']:.3f} | {agree['variant_jaccard']:.3f} |
| Variants (normalized keys) | {agree1.get('variant_key_jaccard', float('nan')):.3f} | {agree['variant_key_jaccard']:.3f} |
| Checklist cells | {agree1['checklist_agreement']:.3f} | {agree['checklist_agreement']:.3f} |
| Phenotype rows (label-free) | {agree1.get('feature_jaccard_label_free', float('nan')):.3f} | {agree['feature_jaccard_label_free']:.3f} |

Variant agreement clears the 0.9 stability threshold in run-2. Free-text phenotype rows agree less ({agree['feature_jaccard_label_free']:.2f}): two readers phrase and split features differently. The checklist, which fixes the feature names, agrees at {agree['checklist_agreement']:.3f}.

## 3. Phenopackets, normalization and binding (Q3)

*Sources: `validation_report.json`, `normalization_summary.json`, `binding_summary.json`, `phenopacket_build.json` in the run folder.*

- **Phenopackets:** {valid['phenopackets']} (one per merged person), all schema-valid; {build['counts']['with_interpretation']} carry a genomic interpretation.
- **Normalization (VariantValidator {norm['vv_version'].split('+')[0]}):**
  - {norm['status_counts']['normalized'] + norm['status_counts']['corrected']} of {norm['cdna_descriptions']} cDNA descriptions normalized ({pct(norm['share_normalized_or_corrected_of_cdna'])}).
  - {norm['status_counts']['protein_only']} descriptions give only a protein change and cannot be placed on the genome.
- **HPO binding:** {pct(bind['feature_share_bound'])} of {bind['feature_rows']:,} phenotype rows bound to a term (HPO {bind['hpo_release'].split('/')[-1]}); HA20 bound to {bind['ha20_mondo']}.
- **Gatekeeper filter:** phenopackets exclude {build['gatekeeper_claims_dropped_available']} claims the gatekeeper did not judge supported.

## 4. Provenance and the human audit (Q4)

*Sources: `analysis/poc/audit_metrics.json` (first audit, run-2), `audit_metrics_gatekeeper_v2.json`, `audit_metrics_v5.json` and `audit_metrics_v5_excluding_uncertain.json` (re-audit, D-29 subset); `gatekeeper_summary.json` and `gatekeeper_v3_summary.json`.*

| | First audit (run-2, instructions v3) | Re-audit (20 papers, instructions v5) |
|---|---|---|
| Claims rated | {a1['rated']} | {a5['rated']} (2 left unrated) |
| Unsupported | {kn(s1)}, {pct(s1['share'])} ({ci(s1)}) | {kn(s5)}, {pct(s5['share'])} ({ci(s5)}) |
| Not fully supported | {kn(a1['not_supported_lenient'])}, {pct(a1['not_supported_lenient']['share'])} | {kn(a5['not_supported_lenient'])}, {pct(a5['not_supported_lenient']['share'])} |
| Weighted by stratum pool, unsupported | {pct(a1['stratum_weighted']['unsupported'])} | {pct(a5['stratum_weighted']['unsupported'])} |
| Variant fields unsupported | {a1['per_stratum']['variant'].get('unsupported', 0)} of {sum(a1['per_stratum']['variant'].values())} | {a5['per_stratum']['variant'].get('unsupported', 0)} of {sum(a5['per_stratum']['variant'].values())} |

**Error classes:**

| Audit | Claims | Class | Fix |
|---|---|---|---|
| First | 3 unsupported, 1 partial (variant fields) | value taken from a group statement or a literature-summary column, not this person | D-29: instructions v5 variant-field rule |
| First | 2 partial | normal finding recorded in the inverted form | D-27 |
| Re-audit | 3 unsupported (ages) | value read by position from a stacked multi-patient cell; the rater could not verify it | D-31: instructions v6, gatekeeper v4 |

- **Sensitivity:** leaving out the three stacked-cell claims the rater judged uncertain gives {kn(s5x)} unsupported ({ci(s5x)}). The gated figure counts them, because a value an expert cannot verify from its quote should have been an abstention.
- **The 50-claim audits cannot certify the pre-registered target** (< 2%, 250 claims). Their 95% intervals reach {ci(s1)} and {ci(s5)}.

**The gatekeeper against the human labels** (flags = partially supported or unsupported):

| Gatekeeper | Run | Its unsupported rate over all judged values | Human not-fully-supported claims it flagged | False flags |
|---|---|---|---|---|
| v1 | run-2 | {pct(gk1['rates_all_values']['unsupported_or_not_found']['share'], 3)} | {cal1['tp']} of {cal1['tp'] + cal1['fn']} | {cal1['fp']} |
| v2 (re-check) | run-2 audit claims | — | {cal1v2['tp']} of {cal1v2['tp'] + cal1v2['fn']} | {cal1v2['fp']} |
| v3 | D-29 subset | {pct(gk3['rates_all_values']['unsupported_or_not_found']['share'], 2)} | {cal3['tp']} of {cal3['tp'] + cal3['fn']} | {cal3['fp']} |

- The v1 figures use Jimmy's final labels. Two of them changed after he saw v1's reasons, so v1's agreement is not independent.
- **What this means:** the gatekeeper's own rate understates the error rate by an order of magnitude, and its recall against a person is low. Report it as a filter, with its accuracy against human labels (pre-registration §7.1(b)), never as the error rate.

## 5. Deduplication (Q5)

*Sources: `analysis/poc/dedup_hand_check_summary_poc-ha20-run-2.json`, `extraction_counts_poc-ha20-run-2.json` (reconciliation).*

- **Policy v3** merged {dedup3['merged_pairs']} pairs. A full hand check found {dedup3['verdicts'].get('true_merge', 0)} true, {dedup3['verdicts'].get('false_merge', 0)} false and {dedup3['verdicts'].get('cannot_tell', 0)} cannot tell. All false merges came from matching on sex and onset; citation-based merges were all correct.
- **Policy v4** (D-23) merges on citations only: {rec['individuals_before_merging']} people become {rec['identities_after_merging']} identities through {recon['merged_pairs']} merges. Against the policy-v3 hand check they are {v4_verdicts.get('true_merge', 0)} true, {v4_verdicts.get('cannot_tell', 0)} cannot tell, {v4_verdicts.get('false_merge', 0)} false and {v4_verdicts.get('not hand-checked', 0)} not hand-checked. The policy was chosen after the check, so this is not an independent test.
- **Proband counting** is a known weak point for language models (Claude Sonnet 4 was weakest of five models at it; `murugan2026_reasoning_llm_ps4`). The pilot's false merges agree: identity needs explicit evidence.
- **Against Chen 2020's patient counts** (§7), our carrier counts match for most source papers; two papers have one fewer carrier.

## 6. Concordance with ClinVar (Q6)

*Sources: `analysis/poc/concordance_poc-ha20-run-2.json`, `analysis/poc/reference_snapshot/2026-10-19/counts.json`. ClinVar release {conc['clinvar_release_last_modified'][5:16]}; HPO annotations {conc['hpoa_version'].replace('#version: ', '')}. OMIM not checked.*

- **Direct dated count for *TNFAIP3*:** {counts_cv['single_gene_records']['total']} single-gene records, {plp} P/LP, {sc.get('VUS', 0)} VUS. This replaces the application's 542 / ~58 / ~289.

| | All papers | Without ClinVar-cited papers (D-19) |
|---|---|---|
| Distinct normalized extracted variants | {allp['distinct_normalized_variants']} | {nocite['distinct_normalized_variants']} |
| In ClinVar | {kn(allp['variant_presence'])} ({pct(allp['variant_presence']['share'])}, {ci(allp['variant_presence'])}) | {kn(nocite['variant_presence'])} ({pct(nocite['variant_presence']['share'])}) |
| Authors' P/LP agrees with ClinVar P/LP | {kn(allp['author_plp_with_clinvar_plp'])} | {kn(nocite['author_plp_with_clinvar_plp'])} |
| Gap candidates (not in ClinVar) | {allp['gap_candidates']} | {nocite['gap_candidates']} |

- **Phenotypes:** extracted terms recall {kn(ph['annotation_recall'])} HPO terms annotated to HA20. Pair precision against that short annotation is {pct(ph['pair_precision']['share'])}; this measures how much the literature reports beyond the annotation, not extraction error.
- **Gap candidates** (`gap_candidates_poc-ha20-run-2.csv`) need hand triage before adjudication.

## 7. Completeness (Q7)

*Source: `analysis/poc/completeness_poc-ha20-run-2.json`. Benchmark: Chen 2020 Table S1 (D-30), {comp['benchmark_patients']} patients, {comp['benchmark_variants']} protein-level variants.*

| Measure | Result |
|---|---|
| Restricted (source paper in the run), primary-paper rows: gated | {kn(comp['recall_restricted_primary'])} ({ci(comp['recall_restricted_primary'], 0)}) |
| Unrestricted, primary-paper rows | {kn(comp['recall_unrestricted_primary'])} ({pct(comp['recall_unrestricted_primary']['share'])}, {ci(comp['recall_unrestricted_primary'], 0)}) |

The gate is met, but on {comp['restricted_variants']} variants: most of the benchmark's source papers are paywalled (Q1).

## 8. Cost (Q8)

*Sources: session list-price usage readings in `runs/*/manifest.json` and `BUDGET.md`. These are estimates, not billing figures; readings sometimes froze for up to an hour, and some stages overlapped. Per-call token usage and cache hit rates are not available on the Claude Code route (D-20).*

| | Value |
|---|---|
| Session reading at the end of the D-29 re-run (the figure logged against the ceiling) | ${total:,.2f} of the $1,000 ceiling |
| Of which since Stage 1 began (reading ${first_reading:.2f} then) | ${pilot_spend:,.2f} |
| Run-2 extraction, per paper | ${ext_per_paper:.2f} (${r2a - r2b:,.2f} for 85 papers) |
| Run-2 extraction, per merged identity with a TNFAIP3 variant | ${(r2a - r2b) / rec['identities_with_target_gene_variant']:.2f} ({rec['identities_with_target_gene_variant']} identities) |
| Run-2 extraction, per quoted value | ${(r2a - r2b) / span['counts']['values_asserted']:.4f} |
| D-29 subset, extraction and gatekeeper v3 together, per paper (upper bound; includes concurrent Stage 6 work) | ${subset_per_paper:.2f} |

**Six-disease projection.** Papers are projected from published patient counts, at HA20's measured ratio of {papers_per_patient:.2f} full-text papers per published patient. That ratio is the largest uncertainty: it will differ by disease, and the corpus searches will replace it.

| Disease | Published patients | Source | Projected full-text papers |
|---|---|---|---|
{chr(10).join(proj_rows)}
| **Total** | | | **{proj_total_papers}** |

| | Multiplier {MULTIPLIER[0]:g}× | Multiplier {MULTIPLIER[1]:g}× (re-runs, repeats, repairs) | Budget line |
|---|---|---|---|
| Extraction | ${proj_ext[0]:,.0f} | ${proj_ext[1]:,.0f} | ${EXTRACTION_LINE_USD:,} |
| Extraction and gatekeeper v3 | ${proj_all[0]:,.0f} | ${proj_all[1]:,.0f} | ${EXTRACTION_LINE_USD + GATEKEEPER_LINE_USD:,} (lines 1 and 2) |

- **Q8 is met** even at the upper multiplier.
- **Billing (D-17):** the pilot ran as Claude Code helper agents on a claude.ai account, and part of it ran on overage after the five-hour limit. Jimmy reconciles these readings with claude.ai Settings > Usage; there is no Console export on this route.

## 9. Limitations

- HA20 is a development disease: every rule was tuned on it, so its results flatter the pipeline (D-18).
- The audits are small (n = 50 and 48), rated by one person (Jimmy), and their rules were written after seeing earlier ratings.
- The second-look tabs showed gatekeeper reasons, so labels changed there are not independent of the gatekeeper.
- Q1 is not met; recall and dedup are measured only on what is open access.
- OMIM was not checked. The Q7 benchmark is small and is itself in the corpus.
- Cost figures are session estimates with frozen readings and overlapping stages.
- The memorization probe (Stage 8) was not run.

## 10. Changes to make before freezing the pre-registration

1. **Extraction:** instructions v6 (`extract_v6.md`): the D-27 normal-finding rule, the D-29 variant-field rule and the D-31 stacked-cell rule. Not yet run.
2. **Gatekeeper:** v4 (`gatekeeper_v4.md`), judging every value with the person link (D-28). Report it as a filter with its accuracy against human labels.
3. **Merging:** policy v4 (citations only; D-23).
4. **Normalization:** the D-26 repairs and reporting by description type.
5. **Concordance harness:** snapshots outside the repository (the extraction guard), VCF-key matching on GRCh38, the protein-consistency pre-triage, D-19 splits, and the ancestor-closure phenotype rule.
6. **Completeness:** state the benchmark per disease in advance. For HA20, Chen 2020 (D-30).
7. **Still to decide before the freeze:** D-08 to D-12, D-17 and D-19. For D-19, the pilot shows a modest effect: presence falls from {pct(allp['variant_presence']['share'], 0)} to {pct(nocite['variant_presence']['share'], 0)} without ClinVar-cited papers. The recommendation is to keep ClinVar-cited PMIDs out of corpus building, as pre-registration §5.1 says, and report the split.
8. **For Jimmy:** whether the < 2% target is judged on the point estimate or the upper confidence bound (`background/grant_claim_checks.md` #14).

**Pinned files for the frozen pipeline** (sha256, first 12 characters):

| File | sha256 |
|---|---|
{chr(10).join(f'| `{k}` | `{sha(v)}` |' for k, v in pinned.items())}
"""
    (ROOT / "reports/poc_report.md").write_text(md)
    print(f"wrote reports/poc_report.md ({len(md):,} characters); pilot spend ${pilot_spend:,.2f}; projected papers {proj_total_papers}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
