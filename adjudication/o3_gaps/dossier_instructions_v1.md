# Evidence dossiers for gap-variant candidates (v1, 2026-10-21)

You are preparing evidence sheets for an expert panel (three PhD scientists) who will classify each variant under the ACMG/AMP framework. You collect the evidence and quote it; **you do not classify**. Your batch file lists the candidates, the papers, and the rows already extracted from those papers.

## Hard rules

1. **Sources: only the files named in your batch file.** These are the paper texts (`paper_text`) and the extraction outputs (`extraction`). Read nothing else in the repository. In particular, never open anything under `/home/user/gp-rarelink-reference/`, `data/reference/`, `analysis/`, or any `adjudication/` file other than your batch file and your own output folder. Do not use web search or web fetch. Do not look up ClinVar, OMIM, gnomAD, LOVD, HGMD or any other database, and do not use your own memory of them.
2. **Every statement of fact carries a verbatim quote** from a paper text, with its PMID. Copy each quote exactly, character for character: no paraphrase, no ellipsis inside a quote, no fixing of typos. Keep each quote short, one sentence or one table row. A script checks every quote against the paper text after you finish.
3. **"Not reported" is a valid, expected answer.** If the papers say nothing on an item, write `"not reported"` and no quotes. Never infer evidence the paper does not state. For example, don't assume de novo because no parent is mentioned.
4. **No classification.** Do not write "pathogenic", "likely pathogenic", "VUS" or any ACMG criterion code as your own conclusion. Quote the authors' classification only if they state one, under `authors_classification`.
5. **Person-specific.** Evidence about one person must be about this variant in that person. A cohort-level sentence ("all patients had fever") is not evidence for one person; mark it `"cohort-level"` in `scope`.

## How to read efficiently

Papers can be long. Do not read whole papers unless one is short (under about 40 KB).
- Search each paper text (Grep) for the variant: its cDNA position (e.g. `559C`), its protein change in one- and three-letter forms (e.g. `Q187`, `Gln187`), and the person labels listed in your batch.
- Then read the passages around the hits: the case description, pedigree or family section, methods for genetic testing, and functional results that mention the variant.
- The extraction file for a paper (`extraction`) already lists the people, variants and phenotypes with spans. Use it to find where to look, but quote from the paper text, not from the extraction.

## What to fill, per candidate

Write one JSON file per candidate to `adjudication/o3_gaps/dossiers/<candidate_id>.json`:

```json
{
  "candidate_id": "G-ha20-008",
  "instructions_version": "dossier_v1",
  "status": "pending adjudication",
  "variant": {"hgvs_c": "...", "hgvs_p_predicted": "...", "vcf_grch38": "...",
              "as_written_in_papers": [{"pmid": "...", "quote": "..."}]},
  "items": {
    "cases": {"statement": "...", "people": [
        {"pmid": "...", "label": "...", "identity": "...", "sex": "...", "zygosity_or_genotype": "...",
         "other_allele": "...", "key_phenotypes": "...", "quotes": ["...", "..."]}]},
    "phenotype_specificity": {"statement": "...", "scope": "person|cohort-level", "quotes": [{"pmid": "...", "quote": "..."}]},
    "segregation": {"statement": "...", "quotes": [...]},
    "de_novo": {"statement": "...", "quotes": [...]},
    "in_trans": {"statement": "...", "quotes": [...]},
    "functional": {"statement": "...", "quotes": [...]},
    "variant_type_and_mechanism": {"statement": "...", "quotes": [...]},
    "computational_predictions": {"statement": "...", "quotes": [...]},
    "population_data_in_papers": {"statement": "...", "quotes": [...]},
    "authors_classification": {"statement": "...", "quotes": [...]}
  },
  "concerns": ["..."],
  "papers_read": ["..."],
  "notes_for_panel": "..."
}
```

Each item is either `{"statement": "not reported", "quotes": []}` or a short statement with its quotes. A quote is `{"pmid": "<PMID>", "quote": "<verbatim>"}`. Under `cases.people`, `quotes` is a list of `{"pmid", "quote"}` objects too.

What each item means:
- **cases:** every person in your papers who carries the variant: sex, zygosity (heterozygous, homozygous, compound heterozygous, hemizygous), the other allele for recessive diseases, and up to five key phenotypes with quotes. Use the `identity` from the batch file. Two rows with the same identity are the same person, merged by the pipeline. If you see signs that two different identities may be the same person (same family, same age and features, a later report citing the earlier one), say so in `concerns`.
- **phenotype_specificity:** whether the person's features are typical of the disease as the papers describe it, and whether other causes were excluded (e.g. other genes tested, panel or exome negative for other genes). Quote the paper.
- **segregation:** affected relatives who carry the variant, and unaffected relatives who do or do not carry it. Give counts as the paper states them.
- **de_novo:** whether both parents were tested and lacked the variant, and whether parentage was confirmed. If only one parent was tested, say so.
- **in_trans** (recessive diseases only; otherwise "not applicable"): the other allele and whether phase was shown (parents tested, or the variants were shown to be on different alleles).
- **functional:** assays that tested this variant. Say whether the material was patient cells or a construct. Give the assay, the result as the paper states it, and the controls if given.
- **variant_type_and_mechanism:** the consequence, from the HGVS in the batch file (no quote needed for that part). Then any statement in the papers on the disease mechanism (e.g. loss of function, haploinsufficiency, gain of function), quoted.
- **computational_predictions:** in-silico scores or predictions **as reported in the papers** (SIFT, PolyPhen, CADD, splice predictors), quoted. Do not run or recall predictors yourself.
- **population_data_in_papers:** only what the papers state, e.g. "absent from 200 control chromosomes" or "not found in gnomAD". Quote it. Otherwise "not reported". The panel assesses population frequency separately.
- **authors_classification:** the authors' own classification or ACMG criteria, quoted, if stated.
- **concerns:** anything the panel should know:
  - the paper's protein differs from the protein predicted from the cDNA (the batch file's `protein_check`);
  - legacy numbering, or a transcript other than the one in the batch file;
  - the variant appears only in a review or a table without a case description;
  - another candidate variant in the same person (another gene, or a second variant);
  - somatic or mosaic findings;
  - the paper contradicting itself.
- **papers_read:** the PMIDs you actually searched or read for this candidate.

## Finishing

1. Write all dossier files for your batch.
2. Run the checker on your own files and fix every problem it reports (usually a quote that is not verbatim):
   `python3 -I adjudication/o3_gaps/check_dossiers.py --batch <your batch file> --only-mine`
3. Reply with one short paragraph:
   - how many dossiers you wrote;
   - the checker result;
   - which tools you used (Read, Grep, Bash, Write). State plainly that you used no web or database lookups.
