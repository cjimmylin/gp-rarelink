# The six-disease run against OMIM as a human-curated holdout

*Generated 2026-10-28 by `analysis/omim_holdout/report.py` at commit `a5e07fc` from `results_2026-10-28.json`, `av_recall_2026-10-28.csv`, `omim_cited_papers_2026-10-28.csv`, `gap_candidates_omim_check_2026-10-28.csv`, `omim_av_clinvar.csv` and the hand-judged `patient_level_judgements.csv`. OMIM source: the twelve entry pages Dr. Lin printed from omim.org on 2026-10-28 (D-42), parsed by `pipeline/harness/omim_entries.py`; ClinVar placement of OMIM's allelic variants from ClinVar E-utilities queried 2026-10-28T15:23:07Z. Internal report: it quotes OMIM identifiers and short variant labels, and paraphrases OMIM statements in §5; it is not for release in this form (pre-registration §11).*

Wilson 95% intervals throughout. The run assessed is `pv1-<disease>` (frozen pipeline v1.0, 2026-10-20). Nothing here changes a pre-registered metric or threshold; §10 says which figures are pre-registered and which are exploratory.

## 1. Summary

- **What OMIM gives us.** Six phenotype entries and six gene entries, last edited between 2022-05-26 and 2026-04-13. The gene entries list 82 allelic variants, of which 75 are titled for the six pilot diseases (the rest: 7 for other phenotypes or reclassified, 1 moved). OMIM calls these 'selected examples'; they are a curated sample of the literature, not a catalogue, so recall against them is the meaningful direction and 'precision against OMIM' is not.
- **Variant recall (B).** The run recovered **57.3% (43/75; 46.1–67.9)** of the 75 disease-titled allelic variants at the genomic or protein level, 58.7% (44/75; 47.4–69.1) counting one notation-level match. Recall is high where the open-access corpus carries the variant literature (LAD-I 85.7% (12/14; 60.1–96.0), HA20 88.9% (8/9; 56.5–98.0)) and collapses where OMIM's evidence is pre-2005 and paywalled (Tangier 10.5% (2/19; 2.9–31.4)).
- **Literature recall (A).** Of the 84 papers OMIM cites as sources for those allelic variants, the run extracted 5. Across all 288 OMIM-cited papers (phenotype and gene entries pooled), 96 were in our screened corpus but had no open full text (D-32), 160 were never returned by the searches (mostly gene-biology and pre-1990 papers, §3), and 9 were extracted. The pipeline's literature coverage, not its reading, is the binding constraint against OMIM.
- **Where the source paper was extracted, the variant was usually there.** Restricted to allelic variants whose OMIM source paper is in the run, 14 variants: 8 were recovered from that very paper at the genomic or protein level, and the misses have two named causes: a table scrambled by PDF conversion (Akaboshi 2003, three SSADH variants) and variants the paper states only in prose ('a glycine to an arginine at amino acid 169'; 'G-to-T at the first base of intron 9'), which the run keeps verbatim but cannot key (§4.3, §5).
- **Patient level (§5).** For the 9 papers both OMIM and the run cover, our records agree with OMIM's curated statements on individuals, sex, zygosity, inheritance and outcomes in 12 of 23 comparisons and partially in 7; the 4 misses are the Akaboshi table. Where they disagree, it is usually the run having less (a supplement not in the text) rather than something wrong.
- **Gap candidates (D).** None of the 215 O3 candidates is a confirmed OMIM allelic variant; one (G-danon-001) collides with OMIM 309060.0001 by notation and is a **transcript-isoform error in our normalization**, not a gap (§7). Recommendation: withdraw it and re-check the LAMP2 exon-9 variants whose transcript was assumed.
- **OMIM is not error-free either (§6).** One OMIM allelic variant's own ClinVar record is a synonymous change at another position (610045.0007), one is placed deep in an intron (610045.0002), 9 use legacy protein numbering that differs from the current transcript, and the complex LAD-I allele 600065.0006 has a component ClinVar calls benign. A holdout curated by people needs the same provenance checks as our output.
- **OMIM is also stale relative to the corpus (§8).** 51 of the 350 extracted papers post-date the last edit of either OMIM entry for their disease, and the run holds 466 distinct genome-placed variants against OMIM's 75 selected examples. Of the ClinVar P/LP variants the run found, 39 of 193 are OMIM allelic variants.

## 2. What the frozen OMIM pages contain

| Disease | Phenotype / gene MIM | Last edit (phenotype / gene) | References (phenotype / gene) | Allelic variants listed | Titled for the disease | Other titles | With a ClinVar RCV printed |
|---|---|---|---|---|---|---|---|
| A20 haploinsufficiency | 616744 / 191163 (TNFAIP3) | 2023-03-30 / 2023-03-20 | 5 / 29 | 9 | 9 | — | 9 |
| Alexander disease | 203450 / 137780 (GFAP) | 2023-06-09 / 2026-04-13 | 26 / 31 | 13 | 13 | — | 13 |
| LAD-I | 116920 / 600065 (ITGB2) | 2025-06-23 / 2024-01-02 | 59 / 70 | 15 | 14 | MOVED TO 600065.0006: 1 | 14 |
| SSADH deficiency | 271980 / 610045 (ALDH5A1) | 2025-08-26 / 2023-02-09 | 22 / 10 | 7 | 7 | — | 7 |
| Danon disease | 300257 / 309060 (LAMP2) | 2025-07-15 / 2022-05-26 | 26 / 24 | 13 | 13 | — | 13 |
| Tangier disease | 205400 / 600046 (ABCA1) | 2022-11-16 / 2023-06-07 | 40 / 57 | 25 | 19 | HIGH DENSITY LIPOPROTEIN DEFICIENCY: 4; RECLASSIFIED - ABCA1 POLYMORPHISM: 2 | 19 |

Each allelic variant carries OMIM's legacy label (e.g. `ARG593CYS`, `IVS6DS, G-C, +5`), dbSNP and ClinVar accessions, and a narrative citing the source papers by author and year, which the parser resolves to PMIDs through the entry's own reference list. The phenotype entries carry no allelic-variant table and no clinical synopsis (that is a separate page); their Clinical Features sections summarize individual papers, which §5 uses. Parsing checks passed for all twelve pages (allelic-variant counts equal the heading counts; references number 1..n; each phenotype entry names its gene entry). Files, checksums and print times are in `analysis/poc/reference_snapshot/2026-10-28/omim_MANIFEST.json`; the content stays outside the repository (licence, pre-registration §11).

## 3. Literature recall: where OMIM's cited papers stand in our funnel (A)

Every PMID cited by a phenotype entry, a gene entry or an allelic-variant narrative was looked up in the disease's corpus manifest and in the run. 'Not found by search' means no search or seed returned it; 'in corpus, no open full text' means it passed title/abstract screening but no PMC, Europe PMC or Unpaywall copy existed (D-32, open access only).

**Pooled over the six diseases, by where OMIM cites the paper:**

| Cited in | Total | extracted | in corpus, no open full text | excluded at full-text screening | in corpus with text, not extracted | not in corpus (screened unclear/other) | excluded at title/abstract | held out (bias arm) | not found by search |
|---|---|---|---|---|---|---|---|---|---|
| allelic-variant narrative | 84 | 5 | 38 | 0 | 0 | 3 | 0 | 0 | 38 |
| phenotype entry (clinical text, not an allelic variant) | 93 | 4 | 53 | 0 | 0 | 0 | 3 | 2 | 31 |
| gene entry only | 111 | 0 | 5 | 0 | 0 | 3 | 12 | 0 | 91 |

**Allelic-variant source papers, per disease** (the papers from which OMIM took its variants):

| Disease | Total | extracted | in corpus, no open full text | excluded at full-text screening | in corpus with text, not extracted | not in corpus (screened unclear/other) | excluded at title/abstract | held out (bias arm) | not found by search |
|---|---|---|---|---|---|---|---|---|---|
| A20 haploinsufficiency | 4 | 1 | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| Alexander disease | 9 | 0 | 9 | 0 | 0 | 0 | 0 | 0 | 0 |
| LAD-I | 44 | 1 | 9 | 0 | 0 | 3 | 0 | 0 | 31 |
| SSADH deficiency | 4 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| Danon disease | 12 | 1 | 6 | 0 | 0 | 0 | 0 | 0 | 5 |
| Tangier disease | 11 | 0 | 9 | 0 | 0 | 0 | 0 | 0 | 2 |

**Pre-registered share (§7.2.5):** corpus PMIDs cited by OMIM for the gene (phenotype and gene entries pooled):

| Disease | Corpus PMIDs | Cited by OMIM | Extracted PMIDs | Extracted and cited by OMIM |
|---|---|---|---|---|
| A20 haploinsufficiency | 160 | 3.1% (5/160; 1.3–7.1) | 85 | 1.2% (1/85; 0.2–6.4) |
| Alexander disease | 363 | 5.8% (21/363; 3.8–8.7) | 69 | 1.4% (1/69; 0.3–7.8) |
| LAD-I | 274 | 4.7% (13/274; 2.8–7.9) | 42 | 2.4% (1/42; 0.4–12.3) |
| SSADH deficiency | 171 | 10.5% (18/171; 6.8–16.0) | 40 | 10.0% (4/40; 4.0–23.1) |
| Danon disease | 244 | 6.1% (15/244; 3.8–9.9) | 83 | 2.4% (2/83; 0.7–8.4) |
| Tangier disease | 284 | 11.6% (33/284; 8.4–15.9) | 31 | 0.0% (0/31; 0.0–11.0) |

**The 69 'not found by search' papers cited by phenotype entries or allelic-variant narratives** (titles fetched from PubMed on 2026-10-28; `not_found_titles.json` under the reference root) by decade: 1950s 1, 1960s 3, 1970s 9, 1980s 37, 1990s 17, 2000s 1, 2020s 1. 
Reading the titles: most are pre-1990 descriptions of the disorder under earlier names (LAD-I as 'Mo1 deficiency', 'LFA-1 immunodeficiency', 'defective neutrophil adhesion'; Danon disease as 'lysosomal glycogen storage disease with normal acid maltase'; Tangier disease as 'familial alpha-lipoprotein deficiency'), gene-biology, mapping and animal-model papers, and a few that OMIM cites for the allelic variant .0015 of ITGB2 as historical background. The searches in `configs/diseases.yaml` use current disease and gene names; the pre-gene-era names were not in them. That is a corpus-building limit worth fixing for diseases described before their gene (LAD-I 1979–1990, Danon 1981–2000, Tangier 1961–1999), and it matters less for HA20 (2016) and AxD.

Examples among the allelic-variant sources our search never returned:

| Disease | PMID | Year | Title (PubMed) |
|---|---|---|---|
| LAD-I | 1270326 | 1976 | An inherited defect in granulocyte function: impaired chemotaxis, phagocytosis and intracellular killing of mi |
| LAD-I | 1346613 | 1992 | Genetic cause of leukocyte adhesion molecule deficiency. Abnormal splicing and a missense mutation in a conser |
| LAD-I | 1347532 | 1992 | Identification of two molecular defects in a child with leukocyte adherence deficiency. |
| LAD-I | 1384046 | 1992 | Identification and prevalence of a genetic defect that causes leukocyte adhesion deficiency in Holstein cattle |
| LAD-I | 1605311 | 1992 | Bovine leukocyte adhesion deficiency. Beta 2 integrin deficiency in young Holstein cattle. |
| LAD-I | 1680882 | 1991 | An in vivo animal model of gene therapy for leukocyte adhesion deficiency. |
| LAD-I | 185306 | 1976 | Defective initiation of the metabolic stimulation in phagocytizing granulocytes: a new congenital defect. |
| LAD-I | 219339 | 1979 | Defective initiation of oxidative metabolism in polymorphonuclear leukocytes. |
| LAD-I | 2877234 | 1986 | Bone-marrow transplantation for immunodeficiencies and osteopetrosis: European survey, 1968-1985. |
| LAD-I | 2880869 | 1987 | Leukocytes from four patients with complete or partial Leu-CAM deficiency contain the common beta-subunit prec |
| LAD-I | 3028646 | 1987 | Cloning of the beta subunit of the leukocyte adhesion proteins: homology to an extracellular matrix receptor d |
| LAD-I | 3278007 | 1988 | A monoclonal antibody to the adherence-promoting leukocyte glycoprotein, CD18, reduces organ injury and improv |

## 4. Allelic-variant recall (B)

**Matching.** Each OMIM allelic variant was placed in ClinVar through ClinVar's own OMIM cross-reference or the RCV accessions OMIM prints (dbSNP ids were not used alone: one rs number covers every allele at a position). ClinVar's title then gives current HGVS on the preferred transcript, and for SNVs a GRCh38 allele. The run's variants were matched by, in order: the ClinVar VariationID already assigned by the O2 harness (tier 1 or 2 as recorded there); the GRCh38 allele from VariantValidator; the cDNA description on the same transcript; the protein change (OMIM's label, ClinVar's title or a protein stated in the narrative); and, reported separately, a notation-tolerant token (position plus bases, which also absorbs OCR artefacts such as `c.612G4A`). 'tier 1' below means a genomic-level or cDNA match, 'tier 2' protein-level only, 'token' notation-level only.

| Disease | OMIM allelic variants | Tier 1 | Tier 2 | Token only | Not recovered | Recall anywhere in the run (tiers 1+2) | … from non-review papers | Source paper in run | Recovered from that source paper |
|---|---|---|---|---|---|---|---|---|---|
| A20 haploinsufficiency | 9 | 8 | 0 | 0 | 1 | 88.9% (8/9; 56.5–98.0) | 88.9% (8/9; 56.5–98.0) | 6 | 100.0% (6/6; 61.0–100.0) |
| Alexander disease | 13 | 8 | 1 | 0 | 4 | 69.2% (9/13; 42.4–87.3) | 69.2% (9/13; 42.4–87.3) | 0 | — |
| LAD-I | 14 | 12 | 0 | 0 | 2 | 85.7% (12/14; 60.1–96.0) | 71.4% (10/14; 45.4–88.3) | 2 | 50.0% (1/2; 9.5–90.5) |
| SSADH deficiency | 7 | 3 | 1 | 0 | 3 | 57.1% (4/7; 25.0–84.2) | 57.1% (4/7; 25.0–84.2) | 5 | 0.0% (0/5; 0.0–43.4) |
| Danon disease | 13 | 7 | 1 | 1 | 4 | 61.5% (8/13; 35.5–82.3) | 53.8% (7/13; 29.1–76.8) | 1 | 100.0% (1/1; 20.7–100.0) |
| Tangier disease | 19 | 0 | 2 | 0 | 17 | 10.5% (2/19; 2.9–31.4) | 10.5% (2/19; 2.9–31.4) | 0 | — |
| **All six** | 75 | 38 | 5 | 1 | 31 | 57.3% (43/75; 46.1–67.9) |  | 14 |  |

**§7.2.2 in the OMIM form** (reference pairs: a PMID in the run × an allelic variant OMIM cites to it; the ClinVar form of this figure is in `reports/six_disease_run_findings.md` §11):

| Disease | Pairs | Recall tier 1 | Recall tiers 1+2 | With token matches |
|---|---|---|---|---|
| A20 haploinsufficiency | 6 | 100.0% (6/6; 61.0–100.0) | 100.0% (6/6; 61.0–100.0) | 100.0% (6/6; 61.0–100.0) |
| Alexander disease | 0 | — | — | — |
| LAD-I | 2 | 50.0% (1/2; 9.5–90.5) | 50.0% (1/2; 9.5–90.5) | 50.0% (1/2; 9.5–90.5) |
| SSADH deficiency | 6 | 0.0% (0/6; 0.0–39.0) | 0.0% (0/6; 0.0–39.0) | 0.0% (0/6; 0.0–39.0) |
| Danon disease | 1 | 100.0% (1/1; 20.7–100.0) | 100.0% (1/1; 20.7–100.0) | 100.0% (1/1; 20.7–100.0) |
| Tangier disease | 0 | — | — | — |

The denominators are small because so few OMIM source papers are open access (§3): this figure is reported because it is registered, not because it discriminates.

### 4.1 Every allelic variant

| OMIM AV | OMIM label | ClinVar HGVS (current) | Recovery | Routes | Papers in run reporting it | From OMIM's source paper | Source paper status (most common) |
|---|---|---|---|---|---|---|---|
| 191163.0001 | LEU227TER | p.Leu227Ter | tier1 | cdna; ClinVar id tier1; ClinVar id tier2; protein; substitution token | 5 | yes | extracted |
| 191163.0002 | 1-BP DEL, 671T | p.Phe224fs | tier1 | cdna; ClinVar id tier1; indel token; protein | 7 | yes | extracted |
| 191163.0003 | ARG271TER | p.Arg271Ter | tier1 | cdna; ClinVar id tier1; ClinVar id tier2; protein; substitution token | 10 | yes | extracted |
| 191163.0004 | 1-BP DEL, 1809G | p.Thr604fs | tier1 | cdna; ClinVar id tier1; indel token; protein | 6 | yes | extracted |
| 191163.0005 | TYR306TER | p.Tyr306Ter | tier1 | cdna; ClinVar id tier1; ClinVar id tier2; protein; substitution token | 5 | yes | extracted |
| 191163.0006 | 1-BP DEL, 799G | p.Pro268fs | tier1 | cdna; ClinVar id tier1; indel token; protein | 4 | yes | extracted |
| 191163.0007 | 1-BP DEL, 1345A | p.Asn449fs | tier1 | cdna; ClinVar id tier1; indel token; protein | 3 | not in run | in corpus, no open full text |
| 191163.0008 | MET476ILE | p.Met476Ile | tier1 | cdna; ClinVar id tier1; ClinVar id tier2; protein; substitution token | 4 | not in run | in corpus, no open full text |
| 191163.0009 | 1-BP DEL, NT912 | p.Glu305fs | not recovered |  | 0 | not in run | in corpus, no open full text |
| 137780.0001 | ARG239CYS | p.Arg239Cys | tier1 | cdna; ClinVar id tier1; ClinVar id tier2; protein; substitution token | 4 | not in run | in corpus, no open full text |
| 137780.0002 | ARG239HIS | p.Arg239His | tier1 | cdna; ClinVar id tier1; ClinVar id tier2; protein; substitution token | 3 | not in run | in corpus, no open full text |
| 137780.0003 | ARG416TRP | p.Arg416Trp | tier1 | cdna; ClinVar id tier1; ClinVar id tier2; protein; substitution token | 4 | not in run | in corpus, no open full text |
| 137780.0004 | ARG79HIS | GFAP):c.[236G>A;667G>C] | tier1 | cdna; ClinVar id tier1; ClinVar id tier2; protein; substitution token | 10 | not in run | in corpus, no open full text |
| 137780.0005 | ARG79CYS | p.Arg79Cys | tier1 | cdna; ClinVar id tier1; ClinVar id tier2; protein; substitution token | 5 | not in run | in corpus, no open full text |
| 137780.0006 | ARG88CYS | p.Arg88Cys | tier1 | cdna; ClinVar id tier1; ClinVar id tier2; protein; substitution token | 5 | not in run | in corpus, no open full text |
| 137780.0007 | ARG88SER | p.Arg88Ser | not recovered |  | 0 | not in run | in corpus, no open full text |
| 137780.0008 | LEU76PHE | p.Leu76Phe | not recovered |  | 0 | not in run | in corpus, no open full text |
| 137780.0009 | ASN77TYR | p.Asn77Tyr | not recovered |  | 0 | not in run | in corpus, no open full text |
| 137780.0010 | GLU362ASP | p.Glu362Asp | not recovered |  | 0 | not in run | in corpus, no open full text |
| 137780.0011 | ARG276LEU | p.Arg276Leu | tier1 | cdna; ClinVar id tier1; ClinVar id tier2; protein; substitution token | 4 | not in run | in corpus, no open full text |
| 137780.0012 | LEU352PRO | p.Leu352Pro | tier1 | cdna; ClinVar id tier1; protein; substitution token | 1 | not in run | in corpus, no open full text |
| 137780.0013 | ASP78GLU | p.Asp78Glu | tier2 protein | ClinVar id tier2; protein | 1 | not in run | in corpus, no open full text |
| 600065.0001 | ARG593CYS | p.Arg593Cys | tier1 | cdna; ClinVar id tier1; ClinVar id tier2; protein; substitution token | 4 | not in run | in corpus, no open full text |
| 600065.0002 | LYS196THR | p.Lys196Thr | not recovered |  | 0 | not in run | in corpus, no open full text |
| 600065.0003 | LEU149PRO | p.Leu149Pro | tier1 | cdna; ClinVar id tier1; ClinVar id tier2; protein; substitution token | 2 | yes | extracted |
| 600065.0004 | GLY169ARG | p.Gly169Arg | tier1 | cdna; ClinVar id tier1; ClinVar id tier2; protein; substitution token | 3 | extracted, not found there | extracted |
| 600065.0005 | INITIATION MUTATION | p.Met1Lys | tier1 | cdna; ClinVar id tier1; protein; substitution token | 1 | not in run | — |
| 600065.0006 | ARG586TRP AND 12-BP INS | p.Arg586Trp | tier1 | cdna; ClinVar id tier1; substitution token | 2 | not in run | not found by search |
| 600065.0008 | ASN351SER | p.Asn351Ser | tier1 | cdna; ClinVar id tier1; ClinVar id tier2; protein; substitution token | 2 | not in run | not found by search |
| 600065.0009 | PRO178LEU | p.Pro178Leu | tier1 | cdna; ClinVar id tier1; protein; substitution token | 5 | not in run | not found by search |
| 600065.0010 | ASP128ASN | p.Asp128Asn | tier1 | cdna; ClinVar id tier1; protein; substitution token | 2 | not in run | in corpus, no open full text |
| 600065.0011 | IVSDS, G-A, +1 | ITGB2):c.897+1G>A | tier1 | cdna; ClinVar id tier1; substitution token | 2 | not in run | in corpus, no open full text |
| 600065.0012 | GLY284SER | p.Gly284Ser | tier1 | cdna; ClinVar id tier1; ClinVar id tier2; protein; substitution token | 6 | not in run | not found by search |
| 600065.0013 | SER138PRO | p.Ser138Pro | tier1 | cdna; ClinVar id tier1; protein; substitution token | 1 | not in run | in corpus, no open full text |
| 600065.0014 | GLY273ARG | p.Gly273Arg | tier1 | cdna; ClinVar id tier1; protein; substitution token | 6 | not in run | in corpus, no open full text |
| 600065.0015 | IVS4AS, 169-BP DEL, -37 | ITGB2):c.329-36_452del | not recovered |  | 0 | not in run | not found by search |
| 610045.0001 | IVS9DS, G-T, +1 | ALDH5A1):c.1343+1G>T | not recovered |  | 0 | extracted, not found there | extracted |
| 610045.0002 | IVS5DS, G-A, +1 | ALDH5A1):c.727-3298G>A | not recovered |  | 0 | extracted, not found there | extracted |
| 610045.0003 | TRP204TER | p.Trp204Ter | tier1 | cdna; ClinVar id tier1; ClinVar id tier2; protein; substitution token | 7 | extracted, not found there | extracted |
| 610045.0004 | ARG412TER | p.Arg412Ter | tier1 | cdna; ClinVar id tier1; protein; substitution token | 5 | extracted, not found there | extracted |
| 610045.0005 | GLY409ASP | p.Gly409Asp | tier1 | cdna; ClinVar id tier1; ClinVar id tier2; protein; substitution token | 13 | extracted, not found there | extracted |
| 610045.0006 | EX7DEL | ALDH5A1):c.1014+723_1173+796del | not recovered |  | 0 | not in run | in corpus, no open full text |
| 610045.0007 | GLY441ARG | p.Glu107= | tier2 protein | protein | 5 | not in run | in corpus, no open full text |
| 309060.0001 | 2-BP DEL, 1097AA | LAMP2):c.1093+2440_1093+2441del | fuzzy token | indel token | 1 | not in run | in corpus, no open full text |
| 309060.0002 | LEU113TER | p.Leu147Ter | tier1 | cdna; ClinVar id tier1; protein; substitution token | 1 | not in run | in corpus, no open full text |
| 309060.0003 | IVS6DS, G-C, +5 | LAMP2):c.864+5G>C | tier1 | cdna; ClinVar id tier1; substitution token | 1 | not in run | in corpus, no open full text |
| 309060.0004 | 1-BP INS, 974A | p.Leu325fs | tier1 | cdna; ClinVar id tier1; ClinVar id tier2; indel token; protein | 11 | not in run | in corpus, no open full text |
| 309060.0005 | IVS5DS, G-A, +1 | LAMP2):c.741+1G>A | tier1 | cdna; ClinVar id tier1; substitution token | 1 | not in run | not found by search |
| 309060.0006 | 1-BP DEL, 14G | p.Arg5fs | not recovered |  | 0 | not in run | in corpus, no open full text |
| 309060.0007 | 1-BP INS, 883T | p.Tyr295fs | tier1 | cdna; ClinVar id tier1; indel token; protein | 1 | not in run | in corpus, no open full text |
| 309060.0008 | 7-BP DEL | p.Gly13fs | not recovered |  | 0 | not in run | in corpus, no open full text |
| 309060.0009 | GLN174TER | p.Gln174Ter | not recovered |  | 0 | not in run | in corpus, no open full text |
| 309060.0010 | VAL310ILE | p.Val310Ile | tier1 | cdna; ClinVar id tier1; ClinVar id tier2; protein; substitution token | 7 | not in run | in corpus, no open full text |
| 309060.0011 | TRP321ARG | p.Trp321Arg | tier2 protein | ClinVar id tier2; protein | 1 | not in run | in corpus, no open full text |
| 309060.0012 | 1-BP DEL, 1219A | p.Lys361fs | not recovered |  | 0 | not in run | in corpus, no open full text |
| 309060.0013 | IVS6DS, A-G, +4 | LAMP2):c.864+4A>G | tier1 | cdna; substitution token | 1 | yes | extracted |
| 600046.0001 | CYS1417ARG | p.Cys1477Arg | tier2 protein | ClinVar id tier2; protein | 1 | not in run | in corpus, no open full text |
| 600046.0002 | G-C, EXON 24 | ABCA1):c.3738+1G>C | not recovered |  | 0 | not in run | in corpus, no open full text |
| 600046.0003 | GLN537ARG | p.Gln597Arg | not recovered |  | 0 | not in run | in corpus, no open full text |
| 600046.0005 | 1-BP DEL, 1764G | p.Thr609fs | not recovered |  | 0 | not in run | in corpus, no open full text |
| 600046.0006 | ASN875SER | p.Asn935Ser | not recovered |  | 0 | not in run | in corpus, no open full text |
| 600046.0007 | ALA877VAL | p.Ala937Val | not recovered |  | 0 | not in run | in corpus, no open full text |
| 600046.0008 | TRP530SER | p.Trp590Ser | not recovered |  | 0 | not in run | in corpus, no open full text |
| 600046.0009 | 1-BP DEL, 1764G | p.Thr609fs | not recovered |  | 0 | not in run | in corpus, no open full text |
| 600046.0010 | 110-BP INS/14-BP DEL | p.Glu529_Trp533delinsGlyArgGlyGlyArgSerC | not recovered |  | 0 | not in run | in corpus, no open full text |
| 600046.0011 | 2-BP DEL, 3283TC | p.Ser1115fs | not recovered |  | 0 | not in run | in corpus, no open full text |
| 600046.0012 | 1-BP DEL, 2665C | p.Arg909fs | not recovered |  | 0 | not in run | in corpus, no open full text |
| 600046.0013 | SER1446LEU | p.Ser1506Leu | not recovered |  | 0 | not in run | in corpus, no open full text |
| 600046.0014 | ASN935SER | p.Asn935Ser | not recovered |  | 0 | not in run | in corpus, no open full text |
| 600046.0015 | ASN935HIS | p.Asn935His | tier2 protein | ClinVar id tier2; protein | 1 | not in run | in corpus, no open full text |
| 600046.0016 | 1.2-KB DEL AND 19.9-KB DEL | NG_007981.1:g.[101177_102434delins36;107 | not recovered |  | 0 | not in run | not found by search |
| 600046.0017 | ARG1680TRP | p.Arg1680Trp | not recovered |  | 0 | not in run | in corpus, no open full text |
| 600046.0020 | ASP1229ASN | p.Asp1289Asn | not recovered |  | 0 | not in run | in corpus, no open full text |
| 600046.0021 | ARG2021TRP | p.Arg2081Trp | not recovered |  | 0 | not in run | in corpus, no open full text |
| 600046.0023 | TYR573TER | p.Tyr573Ter | not recovered |  | 0 | not in run | in corpus, no open full text |

### 4.2 Misses, by cause

| Disease | OMIM AV | Label | Category | OMIM source papers and their status |
|---|---|---|---|---|
| A20 haploinsufficiency | 191163.0009 | TNFAIP3, 1-BP DEL, NT912 | no source paper in the run; variant not reported elsewhere in the extracted corpus | 32666380: in corpus, no open full text |
| Alexander disease | 137780.0007 | GFAP, ARG88SER | no source paper in the run; variant not reported elsewhere in the extracted corpus | 11567214: in corpus, no open full text |
| Alexander disease | 137780.0008 | GFAP, LEU76PHE | no source paper in the run; variant not reported elsewhere in the extracted corpus | 11567214: in corpus, no open full text |
| Alexander disease | 137780.0009 | GFAP, ASN77TYR | no source paper in the run; variant not reported elsewhere in the extracted corpus | 11567214: in corpus, no open full text |
| Alexander disease | 137780.0010 | GFAP, GLU362ASP | no source paper in the run; variant not reported elsewhere in the extracted corpus | 12034796: in corpus, no open full text |
| LAD-I | 600065.0002 | ITGB2, LYS196THR | no source paper in the run; variant not reported elsewhere in the extracted corpus | 1968911: in corpus, no open full text |
| LAD-I | 600065.0015 | ITGB2, IVS4AS, 169-BP DEL, -37 | no source paper in the run; variant not reported elsewhere in the extracted corpus | 10712675: in corpus, no open full text; 1270326: not found by search; 1384046: not found by search; 1605311: not found b |
| SSADH deficiency | 610045.0001 | ALDH5A1, IVS9DS, G-T, +1 | source paper extracted; variant missed there | 14635103: extracted; 9683595: extracted |
| SSADH deficiency | 610045.0002 | ALDH5A1, IVS5DS, G-A, +1 | source paper extracted; variant missed there | 9683595: extracted |
| SSADH deficiency | 610045.0006 | ALDH5A1, EX7DEL | no source paper in the run; variant not reported elsewhere in the extracted corpus | 16542398: in corpus, no open full text |
| Danon disease | 309060.0006 | LAMP2, 1-BP DEL, 14G | no source paper in the run; variant not reported elsewhere in the extracted corpus | 10972294: in corpus, no open full text; 3087571: not found by search |
| Danon disease | 309060.0008 | LAMP2, 7-BP DEL | no source paper in the run; variant not reported elsewhere in the extracted corpus | 15253947: in corpus, no open full text |
| Danon disease | 309060.0009 | LAMP2, GLN174TER | no source paper in the run; variant not reported elsewhere in the extracted corpus | 15253947: in corpus, no open full text |
| Danon disease | 309060.0012 | LAMP2, 1-BP DEL, 1219A | no source paper in the run; variant not reported elsewhere in the extracted corpus | 17899313: in corpus, no open full text; 8504498: not found by search |
| Tangier disease | 600046.0002 | ABCA1, G-C, EXON 24 | no source paper in the run; variant not reported elsewhere in the extracted corpus | 10431236: in corpus, no open full text |
| Tangier disease | 600046.0003 | ABCA1, GLN537ARG | no source paper in the run; variant not reported elsewhere in the extracted corpus | 10431236: in corpus, no open full text |
| Tangier disease | 600046.0005 | ABCA1, 1-BP DEL, 1764G | no source paper in the run; variant not reported elsewhere in the extracted corpus | 10431237: in corpus, no open full text |
| Tangier disease | 600046.0006 | ABCA1, ASN875SER | no source paper in the run; variant not reported elsewhere in the extracted corpus | 10431237: in corpus, no open full text |
| Tangier disease | 600046.0007 | ABCA1, ALA877VAL | no source paper in the run; variant not reported elsewhere in the extracted corpus | 10431237: in corpus, no open full text |
| Tangier disease | 600046.0008 | ABCA1, TRP530SER | no source paper in the run; variant not reported elsewhere in the extracted corpus | 10431237: in corpus, no open full text |
| Tangier disease | 600046.0009 | ABCA1, 1-BP DEL, 1764G | no source paper in the run; variant not reported elsewhere in the extracted corpus | 10431238: in corpus, no open full text |
| Tangier disease | 600046.0010 | ABCA1, 110-BP INS/14-BP DEL | no source paper in the run; variant not reported elsewhere in the extracted corpus | 10431238: in corpus, no open full text |
| Tangier disease | 600046.0011 | ABCA1, 2-BP DEL, 3283TC | no source paper in the run; variant not reported elsewhere in the extracted corpus | 10535983: in corpus, no open full text |
| Tangier disease | 600046.0012 | ABCA1, 1-BP DEL, 2665C | no source paper in the run; variant not reported elsewhere in the extracted corpus | 11476961: in corpus, no open full text |
| Tangier disease | 600046.0013 | ABCA1, SER1446LEU | no source paper in the run; variant not reported elsewhere in the extracted corpus | 11476961: in corpus, no open full text |
| Tangier disease | 600046.0014 | ABCA1, ASN935SER | no source paper in the run; variant not reported elsewhere in the extracted corpus | 12111381: in corpus, no open full text |
| Tangier disease | 600046.0016 | ABCA1, 1.2-KB DEL AND 19.9-KB DEL | no source paper in the run; variant not reported elsewhere in the extracted corpus | 12111381: in corpus, no open full text; 3005356: not found by search; 8209894: not found by search |
| Tangier disease | 600046.0017 | ABCA1, ARG1680TRP | no source paper in the run; variant not reported elsewhere in the extracted corpus | 12111371: in corpus, no open full text |
| Tangier disease | 600046.0020 | ABCA1, ASP1229ASN | no source paper in the run; variant not reported elsewhere in the extracted corpus | 11476965: in corpus, no open full text |
| Tangier disease | 600046.0021 | ABCA1, ARG2021TRP | no source paper in the run; variant not reported elsewhere in the extracted corpus | 11476965: in corpus, no open full text |
| Tangier disease | 600046.0023 | ABCA1, TYR573TER | no source paper in the run; variant not reported elsewhere in the extracted corpus | 12702168: in corpus, no open full text |

31 allelic variants were not recovered: 29 because no paper OMIM cites for them is in the run and no other extracted paper reports them, 2 because the source paper was extracted and the variant was missed there. Tangier accounts for 17 of the misses: its allelic variants come from the 1999–2003 gene-discovery papers (Brooks-Wilson, Bodzioch, Rust, Remaley, Lapicka-Bodzioch, Guo, Huang), all in our corpus and all paywalled, and the open-access Tangier papers that were extracted are recent case reports with other variants.

### 4.3 What the misses inside extracted papers say about the pipeline

- **Table conversion, not reading.** The three SSADH variants OMIM selected from Akaboshi 2003 (W204X, R412X, G409D) were not attributed to any family because the paper's Table 2 was scrambled in PDF-to-Markdown conversion; the helper recorded this and extracted only what the text supports (the same failure was logged in `reports/six_disease_run_findings.md` §5). All three were recovered from five other papers each, so the corpus is redundant for common variants but the per-paper record is incomplete.
- **Prose variants have no key.** Wardlaw 1990 states patient 2's variant only as 'a glycine to an arginine at amino acid 169' and Chambliss 1998 gives 'G-to-T transversion at the first base of intron 9'. The run kept these verbatim with the right individuals and zygosity, but they carry no protein or cDNA field, so they never reach VariantValidator and count as unmatched in every harness. A rule to derive `p.Gly169Arg` from such prose (and nothing more) would have keyed the first; the intronic prose needs exon coordinates and should stay unkeyed but be flagged for review.
- **Isoform ambiguity.** GFAP-epsilon R430H (Melchionda 2013) failed normalization on the assumed MANE transcript with a reference mismatch, which is the safe failure; the LAMP2 exon-9b deletion in Sugie 2018 did not fail and was placed on the wrong isoform (§7). Where a paper names an exon (`E9b`) or an isoform, the transcript assumption should be overridden or the variant held back.
- **Legacy OMIM numbering.** OMIM's labels for ABCA1 use a protein numbering 60 residues short of the current transcript (CYS1417ARG is p.Cys1477Arg) and LAMP2's LEU113TER is p.Leu147Ter; matching on OMIM's label alone would have missed them. ClinVar's title resolves this, which is why the ClinVar placement step matters.

Token-only matches (reported, not counted as recovered):

| Disease | OMIM AV | Label | Routes | Papers |
|---|---|---|---|---|
| Danon disease | 309060.0001 | LAMP2, 2-BP DEL, 1097AA | indel_token | 30413001 |

## 5. Patient-level agreement on the papers both OMIM and the run cover

OMIM's curators summarize individual papers in the Clinical Features and allelic-variant texts. For the 9 extracted papers OMIM cites, each OMIM statement was compared by hand with our per-paper records (individuals, sex, zygosity, inheritance, variant, features, outcomes). Judged by Claude in this session on 2026-10-28 from the records in `data/extracted/<disease>/pv1-<disease>/per_paper/<pmid>.json`; the OMIM side is paraphrased to identifiers and facts. 'agree' means every fact OMIM states is in our record with the same value; 'partial' means the variant and individuals agree but something OMIM states is missing from ours.

| Scope | Disease | OMIM AV | Paper | OMIM states | Our record | Agreement | Note |
|---|---|---|---|---|---|---|---|
| allelic variant | A20 haploinsufficiency | 191163.0001 | Zhou 2016 (26642243) | 3 affected members of a European Canadian family; heterozygous c.680T>A (L227X) | 3 individuals (Family 1: mother and two daughters), female, 'Caucasian ancestry (European Canadian)', heterozygous c.680T>A p.Leu227* | **agree** |  |
| allelic variant | A20 haploinsufficiency | 191163.0002 | Zhou 2016 (26642243) | 3 affected members of a European American family; heterozygous c.671delT (Phe224SerfsTer4) | P4, P5, P6 (Family 2), female, 'Italian ancestry (European American)', heterozygous c.671delT p.Phe224Serfs*4; P6 inherited maternal | **agree** |  |
| allelic variant | A20 haploinsufficiency | 191163.0003 | Zhou 2016 (26642243) | Turkish father and son; heterozygous c.811C>T (R271X) | one individual (Family 3; sex not reported; Turkish), heterozygous c.811C>T p.Arg271* | **partial** | variant and origin agree; one of two individuals recorded and sex not captured: the paper's per-patient supplement and pedigrees were not in the extraction text (method note) |
| allelic variant | A20 haploinsufficiency | 191163.0004 | Zhou 2016 (26642243) | a woman; de novo heterozygous c.1809delG (Thr604ArgfsTer93) | one individual (Family 4; sex not reported; European-American), heterozygous c.1809delG p.Thr604Argfs*93, inheritance not reported | **partial** | variant agrees; sex and de novo status not captured (same cause) |
| allelic variant | A20 haploinsufficiency | 191163.0005 | Zhou 2016 (26642243) | Dutch mother and daughter; heterozygous c.918C>G (Y306X) | one individual (Family 5; sex not reported; Dutch), heterozygous c.918C>G p.Tyr306* | **partial** | variant and origin agree; one of two individuals recorded and sex not captured (same cause) |
| allelic variant | A20 haploinsufficiency | 191163.0006 | Zhou 2016 (26642243) | Turkish mother and her 2 daughters; heterozygous c.799delG (Pro268LeufsTer19) | 3 individuals (Family 6: mother with adult-onset Behcet's and two daughters), female, Turkish, heterozygous c.799delG p.Pro268Leufs*19; daughters inherited maternal | **agree** | ClinVar writes the same deletion 3'-shifted as c.801del; the run's VariantValidator normalization placed it on the same allele (tier 1) |
| allelic variant | LAD-I | 600065.0003 | Wardlaw 1990 (1694220) | patient 14, moderately severe LAD; Leu149Pro (T-to-C) | 'patient 14', LAD, Caucasian, Leu149Pro missense; zygosity recorded as heterozygous | **agree** | OMIM gives no zygosity; the paper is an OCR text in which the beta symbol is garbled (method note) |
| allelic variant | LAD-I | 600065.0004 | Wardlaw 1990 (1694220) | patient 2, severe LAD; Gly169Arg (G-to-A) | 'patient 2', LAD; variant recorded as the paper's prose 'a glycine to an arginine at amino acid 169' with no protein field | **partial** | patient agrees; the variant was captured as text only, so it has no key and did not normalize from this paper; the same variant was recovered from three other papers |
| allelic variant | SSADH deficiency | 610045.0001 | Chambliss 1998 (9683595) | consanguineous family: 2 sibs and their cousin, homozygous G-to-T at the first base of intron 9; sibs with hypotonia, developmental and speech delay, hyporeflexia, behavioral problems including mild autism; cousin aged 23 at examination; unaffected parents and sibs heterozygous | OD, PD (sibs; consanguinity yes) and ZZ (23 years at examination), homozygous 'G>T transversion at the first base of intron 9' (prose; OCR renders the arrow as 'r'); parents and sibs heterozygous; observed: developmental delays, speech delays, hyporeflexia, behavioral problems, hypotonia (OD, PD), ataxia | **partial** | individuals, zygosity, relatives and most phenotypes agree; the variant is prose only (the paper gives no c. notation) so it has no genomic key; autism is 'not reported' in our checklist rows although OMIM states mild autism (to verify against the paper); our labels split the sibs and the cousin into two family groups after the paper's table headers |
| allelic variant | SSADH deficiency | 610045.0002 | Chambliss 1998 (9683595) | a patient, homozygous G-to-A at the first base of intron 5; both parents heterozygous; moderately affected: developmental and speech delay, hyporeflexia, behavioral problems including mild autism | AC, male, consanguinity yes, homozygous 'G>A transition at the first base of intron 5'; both parents heterozygous; observed: developmental delays, speech delays, hyporeflexia, behavioral problems, hypotonia | **partial** | variant prose only (no genomic key); autism 'not reported' in our rows (to verify); ClinVar's record for this OMIM number is placed at c.727-3298G>A, which is not the first base of intron 5 (OMIM-ClinVar inconsistency to check) |
| allelic variant | SSADH deficiency | 610045.0003 | Akaboshi 2003 (14635103) | 8 unrelated families of European ancestry; 612G>A (W204X), homozygous or compound heterozygous; founder effect | not captured from this paper: Table 2 (genotypes of 54 families) was scrambled by the PDF conversion and no cell could be attributed to a family (method note); recovered from five other papers | **missed in source paper** | conversion failure, not a reading error |
| allelic variant | SSADH deficiency | 610045.0004 | Akaboshi 2003 (14635103) | 7 unrelated families; 1234C>T (R412X), homozygous or compound heterozygous | not captured from this paper (same cause); recovered from five other papers | **missed in source paper** | conversion failure |
| allelic variant | SSADH deficiency | 610045.0005 | Akaboshi 2003 (14635103) | 6 unrelated families; 1226G>A (G409D), homozygous or compound heterozygous | not captured from this paper (same cause); recovered from five other papers | **missed in source paper** | conversion failure |
| allelic variant | Danon disease | 309060.0013 | Roos 2018 (28822614) | 4 males and 3 females of one family, hemizygous or heterozygous IVS6DS A-G +4 (c.864+4A>G); exon 6 skipping; reduced LAMP2 in fibroblasts | Cases A-G: 4 males hemizygous, 3 females heterozygous, c.864+4A>G splice, 'causal mutation'; maternal inheritance where stated | **agree** |  |
| paper | A20 haploinsufficiency | — | Zhou 2016 (26642243) | 14 patients (12 female, 2 male) from 6 families; onset 2-16 years (one at 29); oral and genital ulcers; polyarthritis, rash, uveitis (3), gastrointestinal inflammation or ulceration (4), periodic fever (2), hemolytic anemia (1), thrombocytopenia (1); autoantibodies; response to TNF inhibitors or colchicine | 12 variant carriers across the 6 families (plus 5 relatives or unassigned rows); sex recorded for 9 carriers (all female), onset for 2; observed features only for P4, P5 and P6 | **partial** | 12 of 14 patients captured (one of the Turkish father-son pair and one of the Dutch mother-daughter pair missing); sex, onset and features largely not captured because Supplementary Table 1 and the pedigrees were not in the extraction text |
| paper | Alexander disease | — | Melchionda 2013 (23634874) | brother and sister half-sib pair with adult-onset Alexander disease; GFAP-epsilon c.1289G>A (R430H) in exon 7A after excluding GFAP-alpha; the brother also carried HDAC6 c.2566C>T (P856S) | Pt1 female (onset 55 years) and Pt2 male (onset 46 years), both heterozygous GFAP c.1289G>A p.R430H; Pt2 hemizygous HDAC6 c.2566C>T p.P856S (maternal); mother I-2 heterozygous for HDAC6 | **agree** | our record adds the onset ages and the mother's carrier status; the paper names no transcript, so normalization assumed NM_002055.5 (GFAP-alpha) and failed with a reference mismatch (no genomic key from this paper); two other papers that name the isoform transcript normalized to 17:44910143:C:T |
| paper | LAD-I | — | Wardlaw 1990 (1694220) | 2 patients with CD18 mutations | 4 individuals: patients 14 and 2 with the variants; patients 1 and 15 studied without a mutation found | **agree** |  |
| paper | SSADH deficiency | — | Akaboshi 2003 (14635103) | 48 additional unrelated patients; 27 novel mutations; 25 point mutations, 4 small insertions, 5 small deletions; 7 splice, 7 nonsense, 12 missense; no hotspot | 12 individuals and 14 variant rows (6 distinct described variants); Table 2 scrambled by conversion | **missed (major under-capture)** | 12 of 48 patients; none of the three OMIM-selected variants attributed to a family |
| paper | SSADH deficiency | — | Chambliss 1998 (9683595) | 4 patients from 2 unrelated families homozygous for 2 splice-site mutations; unaffected parents and sibs heterozygous | OD, PD, ZZ and AC homozygous for the two splice variants; 9 heterozygous relatives; plus SM and IA (enzyme-deficient subjects) and 2 individuals cited from earlier papers | **agree** | see the allelic-variant rows for the prose-only variants and the autism item |
| paper | SSADH deficiency | — | Gibson 1997 (9093300) | 23 new patients; most frequent: developmental delay (motor, mental, language), hypotonia, seizures, hyporeflexia, ataxia, behavioral problems, EEG abnormalities; less common: abnormal eye movements, psychosis in older patients; about 30% normal early development | 23 patients plus 3 relatives; checklist 'observed' over the 26 rows: motor deficits 19, speech or language 18, hypotonia 17, intellectual disability 16, seizures 10, ataxia 8, EEG abnormality 6, attention problems 5, psychotic symptoms 2 | **agree** | cohort-level ranking of features matches OMIM's summary; OMIM's other 'Gibson et al. (1997)' paragraph (the Lifu Island sibs) may cite a different 1997 paper, so it was not compared |
| paper | SSADH deficiency | — | Leuzzi 2007 (17438226) | 2 Italian sibs with paroxysmal exercise-induced dystonia at 16 and 12 years; classic prior phenotype; vigabatrin improved the dystonia in both, and gait clumsiness and seizures in one | Case 1 (male, 18 years, Italian; paroxysmal exercise-induced dystonia, generalized epilepsy, autism, hypotonia, severe intellectual disability) and Case 2 (male, 13 years; multifocal seizures, psychomotor delay, OCD, gait abnormality, dystonic posture of upper limbs); treatment summaries record vigabatrin's effect on each; compound c.278G>T p.C93F and c.526G>A p.G176R | **agree** | zygosity field 'not reported' although two variants per sib imply compound heterozygosity |
| paper | Danon disease | — | Maron 2009 (19318653) | 7 young patients (6 boys, 1 girl) with LAMP2 mutations from Arad 2005; over 8.6 years: LV systolic dysfunction and cavity enlargement; deaths from heart failure (4), sudden death (1), aborted arrest (1), transplant (1); septal thickness 60 and 65 mm in two; preexcitation in 6; 7 female obligate carriers asymptomatic | 7 patients (6 male, 1 female) with vital status and cause of death per patient (5 deceased at 12-24 years, 2 alive), LV hypertrophy and systolic dysfunction in all, WPW in 6; variants as printed (Y109, IVS6+1_4delGTGA, K289fs, IVS1+1G>T, IVS1-2A>G, V310I and one OCR-garbled string); 3 relatives recorded | **agree** | V310I is OMIM 309060.0010 and was matched at tier 1; the mother of patient 4 is recorded with 'dilated CM' where OMIM summarizes carriers as asymptomatic (the paper's own statement should decide) |
| paper | Danon disease | — | Roos 2018 (28822614) | patient A: exercise-induced myalgia, learning and behavioral difficulties, elevated ALT and CK, LV hypertrophy at 16, ICD, died at 21 after ventricular arrhythmias; patient B: mild learning difficulties, LV hypertrophy at 16, ventricular tachycardia, amiodarone-induced thyrotoxicosis, died at 23; females with later-onset disease | Case A: deceased at 21 (cardiac failure and ventricular tachyarrhythmia), exercise-induced myalgia, learning and behavioural difficulties, elevated ALT, elevated CK, LV hypertrophy; Case B: deceased at 23 (asystolic arrest after amiodarone-induced thyrotoxicosis), ventricular tachycardia; Cases D, F, G onset in the fifth decade | **agree** |  |

**Tally:** agree 12, partial 7, missed in source paper 3, missed (major under-capture) 1 of 23 comparisons. 
Three patterns: (1) where the paper's text carries the facts, our record matches OMIM and often says more (onset ages, a carrier mother, per-patient outcomes in Maron 2009); (2) where the facts sit in a supplement or pedigree figure that was not in the extraction text (Zhou 2016), the run has the variants but not the sex, onset or de novo status; (3) one phenotype statement OMIM makes (mild autism in Chambliss 1998) is 'not reported' in our checklist rows, which is either a paper-text nuance or an extraction miss and should be checked against the paper. No comparison found our record asserting a fact that contradicts OMIM.

## 6. OMIM's allelic variants in ClinVar, and OMIM's coverage of what the run found (C)

| Disease | OMIM AVs | Placed in ClinVar | ClinVar germline classification of the OMIM AVs | Distinct placed variants in run | Run variants in ClinVar | … P/LP | Run P/LP variants that are OMIM AVs |
|---|---|---|---|---|---|---|---|
| A20 haploinsufficiency | 9 | 9 | Pathogenic: 8; Uncertain significance: 1 | 103 | 43 | 26 | 26.9% (7/26; 13.7–46.1) |
| Alexander disease | 13 | 13 | Pathogenic: 13 | 67 | 85 | 36 | 25.0% (9/36; 13.8–41.1) |
| LAD-I | 14 | 14 | Pathogenic: 9; Pathogenic/Likely pathogenic: 4; Benign/Likely benign; Pathogenic: 1 | 129 | 45 | 36 | 33.3% (12/36; 20.2–49.7) |
| SSADH deficiency | 7 | 7 | Pathogenic: 5; Pathogenic/Likely pathogenic: 1; Likely pathogenic: 1 | 78 | 72 | 55 | 5.5% (3/55; 1.9–14.9) |
| Danon disease | 13 | 13 | Pathogenic: 9; Uncertain significance: 2; Pathogenic/Likely pathogenic: 1; Likely pathogenic: 1 | 73 | 40 | 33 | 18.2% (6/33; 8.6–34.4) |
| Tangier disease | 19 | 19 | Pathogenic: 14; Likely pathogenic: 3; Conflicting classifications of pathogenicity: 1; Benign/Likely benign: 1 | 16 | 16 | 7 | 28.6% (2/7; 8.2–64.1) |

OMIM's allelic variants are almost all in ClinVar (the one exception is the moved entry 600065.0007), and ClinVar classifies most of them pathogenic. The run's ClinVar-matched P/LP variants, by contrast, are mostly **not** OMIM allelic variants: OMIM's list is a sample of the pathogenic spectrum, so 'absent from OMIM' alone says little about a variant and the pre-registered gap definition rightly requires absence from both databases.

**OMIM against ClinVar on the same variants.** Comparing OMIM's protein label with the protein change in the ClinVar record that OMIM itself points to:

| Disease | OMIM AV | OMIM label | ClinVar record OMIM cites | Kind |
|---|---|---|---|---|
| SSADH deficiency | 610045.0007 | ALDH5A1, GLY441ARG | NM_001080.3(ALDH5A1):c.321G>A (p.Glu107=) | different change |
| Danon disease | 309060.0002 | LAMP2, LEU113TER | NM_002294.3(LAMP2):c.440T>A (p.Leu147Ter) | numbering offset (same residues) |
| Tangier disease | 600046.0001 | ABCA1, CYS1417ARG | NM_005502.4(ABCA1):c.4429T>C (p.Cys1477Arg) | numbering offset (same residues) |
| Tangier disease | 600046.0003 | ABCA1, GLN537ARG | NM_005502.4(ABCA1):c.1790A>G (p.Gln597Arg) | numbering offset (same residues) |
| Tangier disease | 600046.0006 | ABCA1, ASN875SER | NM_005502.4(ABCA1):c.2804A>G (p.Asn935Ser) | numbering offset (same residues) |
| Tangier disease | 600046.0007 | ABCA1, ALA877VAL | NM_005502.4(ABCA1):c.2810C>T (p.Ala937Val) | numbering offset (same residues) |
| Tangier disease | 600046.0008 | ABCA1, TRP530SER | NM_005502.4(ABCA1):c.1769G>C (p.Trp590Ser) | numbering offset (same residues) |
| Tangier disease | 600046.0013 | ABCA1, SER1446LEU | NM_005502.4(ABCA1):c.4517C>T (p.Ser1506Leu) | numbering offset (same residues) |
| Tangier disease | 600046.0020 | ABCA1, ASP1229ASN | NM_005502.4(ABCA1):c.3865G>A (p.Asp1289Asn) | numbering offset (same residues) |
| Tangier disease | 600046.0021 | ABCA1, ARG2021TRP | NM_005502.4(ABCA1):c.6241C>T (p.Arg2081Trp) | numbering offset (same residues) |

Two inconsistencies are more than numbering: OMIM 610045.0007 (GLY441ARG; DiBacco 2020) is linked to ClinVar record 992960, `c.321G>A (p.Glu107=)`, a synonymous change at another codon, while the run's four papers give `c.1321G>A p.Gly441Arg` (placed at 6:24528144:G:A), which is what the OMIM narrative's own text (`c.321G-A ... gly441-to-arg`) must have meant; and OMIM 610045.0002 (first base of intron 5) is linked to a record at `c.727-3298G>A`. ClinVar 600065.0006's components split into a benign/likely-benign missense (`c.1756C>T`) and a pathogenic splice change (`c.742-14C>A`), and the run found only the pathogenic component. These are small in number but they are the kind of error a provenance-first pipeline is built to avoid, and they argue for treating OMIM as a strong but fallible holdout.

## 7. Gap candidates checked against OMIM (D)

Pre-registration §7.3 defines a gap variant as absent from ClinVar **and** not listed among OMIM's allelic variants; the OMIM half waited on D-12. With the frozen pages, every one of the 215 O3 candidates was compared with the allelic variants of its gene by GRCh38 allele, cDNA, protein and notation tokens.

| Disease | Candidates | Present in OMIM (allele, cDNA or protein) | Notation or isoform collision to check |
|---|---|---|---|
| A20 haploinsufficiency | 64 | 0 | 0 |
| Alexander disease | 17 | 0 | 0 |
| LAD-I | 82 | 0 | 0 |
| SSADH deficiency | 10 | 0 | 0 |
| Danon disease | 35 | 0 | 1 |
| Tangier disease | 7 | 0 | 0 |

`gap_candidates_omim_check_2026-10-28.csv` carries the verdict per candidate (it replaces the `omim_checked = no (D-12)` column of `adjudication/o3_gaps/candidates.csv`; the adjudication page is not changed by this report).

**G-danon-001** (`NM_002294.3:c.1097_1098del`, `NP_002285.1:p.(Gln366ArgfsTer6)`, from Sugie 2018, PMID 30413001) matches OMIM 309060.0001 (`LAMP2, 2-BP DEL, 1097AA`, Nishino 2000) on the deletion token only. The paper's table gives the exon as `E9b` (the span the run stored reads `| 1 | E9b | c.1097_1098 delAA |`). LAMP2 has alternative terminal exons 9a and 9b; c.1097_1098 on the LAMP2B transcript (exon 9b) lies in intron 9 of the MANE transcript NM_002294.3 (LAMP2A), which is exactly where ClinVar places OMIM's variant (`c.1093+2440_1093+2441del`, record 1410728, uncertain significance, alias `Q366fs`). The run's normalization assumed NM_002294.3 because the paper named no transcript (`transcript_assumed = yes`), VariantValidator accepted the description after trimming redundant bases, and the result is a different genomic allele in exon 9a, X:120431457:CTT:C, that no database holds because it is not what the paper reported. **This candidate is a normalization artefact and should be withdrawn** pending re-normalization on NM_013995 (LAMP2B).

The same risk applies to every LAMP2 description at c.1094 or beyond whose transcript was assumed: 2 in the Danon run (`NM_002294.3:c.1150G>C` from PMID 25228319; `NM_002294.3:c.1097_1098del` from PMID 30413001). Across the six runs, 448 normalized descriptions carry `transcript_assumed = yes`; for genes without alternative coding exons the assumption is harmless, for GFAP (alpha/epsilon) and LAMP2 (9a/9b) it is not. A per-gene list of isoform-sensitive regions in the Stage 4 settings (D-40 already made those per disease) would catch this before adjudication.

## 8. Context: inheritance, zygosity and staleness (E)

| Disease | OMIM inheritance | Zygosity of extracted variant rows (top values) | Last OMIM edit | Extracted papers after it | Corpus papers after it |
|---|---|---|---|---|---|
| A20 haploinsufficiency | Autosomal dominant | heterozygous: 307; not reported: 288; mosaic: 7 | 2023-03-30 | 30 of 85 | 46 of 160 |
| Alexander disease | Autosomal dominant | not reported: 212; heterozygous: 115; mosaic: 4; homozygous: 2 | 2026-04-13 | 0 of 69 | 0 of 363 |
| LAD-I | Autosomal recessive | not reported: 283; homozygous: 49; heterozygous: 39; compound heterozygous: 28 | 2025-06-23 | 2 of 42 | 7 of 274 |
| SSADH deficiency | Autosomal recessive | compound heterozygous: 194; not reported: 161; homozygous: 84; heterozygous: 27 | 2025-08-26 | 2 of 40 | 2 of 171 |
| Danon disease | X-linked dominant | not reported: 184; heterozygous: 52; hemizygous: 45; mosaic: 4 | 2025-07-15 | 9 of 83 | 21 of 244 |
| Tangier disease | Autosomal recessive | heterozygous: 27; homozygous: 24; compound heterozygous: 17; not reported: 11 | 2023-06-07 | 8 of 31 | 17 of 284 |

Zygosity patterns follow OMIM's inheritance where stated (heterozygous for the dominant HA20 and AxD; homozygous and compound heterozygous for the recessive LAD-I, SSADH and Tangier; hemizygous males and heterozygous females for X-linked Danon), with 'not reported' large in cohort tables that print genotypes per family rather than per person. The staleness columns are the other side of §3: OMIM's entries draw on the founding literature, much of it closed; the open-access corpus is weighted to the last ten years. The two sources overlap less than one might expect, which is why the recall figures in §4 measure corpus coverage as much as extraction.

## 9. Where the work succeeds, and what to improve

**Succeeds**

- When an OMIM source paper is in the run, the curated variant is almost always in our record with the right individuals and zygosity (§4, §5); the per-patient detail is richer than OMIM's summary (outcomes, ages, carrier relatives).
- Recurrent variants are recovered from several independent papers each (§4.1, 'papers in run reporting it'), so the record does not hinge on one paper.
- No contradiction with OMIM was found at the patient level, and no O3 candidate is a known OMIM variant (§5, §7): the pipeline's abstention and provenance rules hold against an external curated source.
- The frozen pipeline's own flags (`transcript_assumed`, conversion notes in `method_note`, verbatim prose variants) were enough to diagnose every miss inside an extracted paper after the fact.

**Improve**

- **Corpus coverage is the binding constraint.** For diseases described before their gene, add the historical disease names to the searches (LAD-I: Mo1 or LFA-1 deficiency, defective neutrophil adhesion; Danon: lysosomal glycogen storage with normal acid maltase; Tangier: familial alpha-lipoprotein deficiency, analphalipoproteinemia is already there) and record which seed found each paper. This is a pre-registration §5.1 change for any re-search and needs a deviation entry.
- **Open access only (D-32) costs the founding literature.** 96 OMIM-cited papers are in our corpus with no open copy. The options are institutional access for a defined list, or reporting that the pipeline's view of these diseases starts where open access starts; the write-up must say which.
- **Table conversion failures should be visible in the harness**, not only in method notes: a per-paper 'tables usable' flag would let O2/O3 denominators exclude or mark such papers.
- **Key prose protein changes.** A narrow rule ('<residue> to <residue> at amino acid N' → p.XnY) would have keyed Wardlaw's variant without inventing anything; intronic prose should be flagged, not keyed.
- **Isoform-aware normalization** for GFAP and LAMP2 (and any gene with alternative coding exons): never assume MANE for positions inside an alternative exon; use the paper's exon label when it gives one.
- **Phenotype three-state check on a curated statement:** the autism item in Chambliss 1998 is a cheap test of whether 'not reported' was right.
- **Treat OMIM as fallible:** two allelic variants point to ClinVar records that do not match their own description; any OMIM-based concordance figure should exclude or footnote them.

## 10. What is pre-registered here and what is exploratory

- **Pre-registered and now computed:** §7.2.5 (share of corpus PMIDs cited by OMIM; §3), §7.2.2 reference pairs in the OMIM form (§4), §7.3's OMIM criterion for gap candidates (§7). None of these changes O2's ClinVar figures or any threshold.
- **Exploratory, reported as such:** unrestricted recall of OMIM allelic variants anywhere in the run (the completeness shape of §7.2.7, which D-35 registered for HA20 and AxD catalogues only), the literature funnel, the patient-level comparison, the ClinVar-standing and staleness tables.
- **Source and route:** OMIM pages frozen by Dr. Lin on 2026-10-28 (D-42); no API; content outside git. The ClinVar placement used live E-utilities on 2026-10-28, whereas O2 used the 2026-10-12 release; the VariationIDs agree for every variant both saw.
- **Re-run:** `uv run python -m pipeline.harness.omim_entries --root <root> --date 2026-10-28 --manifest-out analysis/poc/reference_snapshot`; `uv run python analysis/omim_holdout/clinvar_lookup.py`; `uv run python analysis/omim_holdout/assess.py`; `uv run python analysis/omim_holdout/report.py`. The PDFs must be copied back to `<root>/2026-10-28/omim/entry_<MIM>.pdf` in a new container.
- **Cost:** no model calls; session tokens only.

