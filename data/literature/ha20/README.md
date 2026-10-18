# HA20 corpus (Stage 1 of POC_DESIGN.md)

Status 2026-10-18: scripts written and unit-tested; **not yet run**. The cloud
container that wrote them cannot reach NCBI, Europe PMC or Unpaywall (network
policy), so Stage 1 has to be executed on a networked machine (the Mac mini
was used for `background/fetch_papers.sh`).

## Runbook (networked machine, from the repo root)

```bash
uv sync --group extract
cp .env.example .env            # fill ANTHROPIC_API_KEY, NCBI_API_KEY (optional), UNPAYWALL_EMAIL

# 1. manifest: seeds + PubMed query. Record the exact query string you use.
uv run python -m pipeline.extract.corpus.build_manifest --disease ha20 \
  --seeds data/literature/ha20/seeds/*.csv \
  --query '("A20 haploinsufficiency"[tiab] OR HA20[tiab] OR "TNFAIP3"[tiab] OR TNFAIP3[Gene Name]) AND (humans[mh]) AND ("case reports"[pt] OR "case report"[tiab] OR patient*[tiab] OR cohort[tiab] OR family[tiab] OR families[tiab])' \
  --mindate 2015/01/01

# 1b. study-type classification (claude-haiku-5-5; logs cost to runs/<run_id>/manifest.json)
uv run python -m pipeline.extract.corpus.classify_study_type --disease ha20 --run-id poc-ha20-classify-1
#     then fill study_type_spotcheck.csv (20 rows) by hand -> copy labels into
#     manifest.csv column study_type_human_check and re-run 1b.

# 2. full text (PMC OA -> Europe PMC -> Unpaywall); records licence per file
uv run python -m pipeline.extract.corpus.fetch_fulltext --disease ha20

# 3. Markdown + token counts (exact counts need ANTHROPIC_API_KEY)
uv run python -m pipeline.extract.corpus.to_markdown --disease ha20

# 4. corpus statistics for the gate (Q1: >= 70 % of in-corpus rows with full text)
uv run python -m pipeline.extract.corpus.corpus_stats --disease ha20
```

Commit `manifest.csv`, `corpus_stats.json`, `study_type_spotcheck.csv` and the
run manifests. Never commit `fulltext/` or `fulltext_md/`.

## Seeds

| File | Source | Rows |
|---|---|---|
| `seeds/background_bibliography.csv` | HA20 entries of `background/manifest.csv` (IDs verified 2026-10-16) | 6 |

Still to add (need the papers in hand): the reference lists of El Hani 2024
(`elhani2024_ha20_177`) and GeneReviews HA20, as `seeds/elhani2024_refs.csv`
and `seeds/genereviews_refs.csv`, and the *TNFAIP3* PMIDs from ClinVar's
`var_citations.txt` written by the harness side (`seed_source=clinvar_citations`).

## Paywalled papers

List them here after step 2 with DOI and journal, for the library request
(POC_DESIGN.md Stage 1 step 4). Do not scrape.
