# GP-RareLink background bibliography

*Compiled 2026-10-16. Machine-readable version: `manifest.csv` (same entries, same keys). Every identifier listed was confirmed on a fetched page or search result on that date; blank identifiers were not confirmed and the reason is in the note. Core entries (★) are the ones to read first.*


## 1. Methods: SLIDERS, LLM extraction and curation

### SLIDERS and Lam lab

- ★ **Joshi H, Shethia P, Dao J, Lam MS (2026).** SLIDERS: Systematic Reviews via Automated Evidence Synthesis and Reconciliation. *arXiv preprint (v1 24 Apr 2026; v2 9 Jul 2026)*.  
  arXiv:2604.22294 · access: open (arXiv) · [full text](https://arxiv.org/pdf/2604.22294) · key `joshi2026_sliders`  
  The project's extraction method: question-specific evidence tables with verbatim excerpts as provenance, plus a code-writing reconciliation agent that merges and de-conflicts extractions. *Note: No DOI shown on arXiv. Title, authors and dates re-checked 2026-10-16.*
- **Semnani SJ, Yao VZ, Zhang HC, Lam MS (2023).** WikiChat: Stopping the Hallucination of Large Language Model Chatbots by Few-Shot Grounding on Wikipedia. *Findings of EMNLP 2023*.  
  doi:10.18653/v1/2023.findings-emnlp.157 · arXiv:2305.14292 · access: open (arXiv) · [full text](https://arxiv.org/pdf/2305.14292) · key `semnani2023_wikichat`  
  Lam lab's grounding-plus-claim-verification design; precedent for the gatekeeper pass.
- **Shao Y, Jiang Y, Kanell TA, Xu P, Khattab O, Lam MS (2024).** Assisting in Writing Wikipedia-like Articles From Scratch with Large Language Models. *Proc NAACL 2024 (Long Papers):6252-6278*.  
  doi:10.18653/v1/2024.naacl-long.347 · arXiv:2402.14207 · access: open (arXiv) · [full text](https://arxiv.org/pdf/2402.14207) · key `shao2024_storm`  
  STORM, the Lam lab's retrieval-grounded long-form synthesis system and the engine behind the RGI-OVAL OpenRare collaboration.

### Phenotype/HPO extraction

- ★ **Caufield JH, Hegde H, Emonet V, Harris NL, Joachimiak MP, Matentzoglu N, Kim H, Moxon S, Reese JT, Haendel MA, Robinson PN, Mungall CJ (2024).** Structured prompt interrogation and recursive extraction of semantics (SPIRES): a method for populating knowledge bases using zero-shot learning. *Bioinformatics 40(3):btae104*.  
  PMID 38383067 · doi:10.1093/bioinformatics/btae104 · arXiv:2304.02711 · access: unknown (likely open) · [full text](https://arxiv.org/pdf/2304.02711) · key `caufield2024_spires`  
  OntoGPT/SPIRES: schema-driven LLM extraction grounded to HPO and Mondo; closest Monarch-stack prior art for filling phenopacket fields. *Note: arXiv ID seen in search results only; PMCID not confirmed.*
- ★ **Garcia BT, Westerfield L, Yelemali P, Gogate N, Rivera-Munoz EA, Du H, Dawood M, Jolly A, Lupski JR, Posey JE (2025).** Improving automated deep phenotyping through large language models using retrieval-augmented generation. *Genome Med 17(1):91*.  
  PMID 40826123 · PMC12359922 · doi:10.1186/s13073-025-01521-w · access: open (PMC) · [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC12359922/) · key `garcia2025_raghpo`  
  RAG-HPO benchmarked on 112 published case reports (our input type); best F1 0.78 with Llama-3.1-70B. Ready open-weight HPO baseline. *Note: Preprint: medRxiv 10.1101/2024.12.01.24318253 (PMC11643181).*
- ★ **Larsen M, Campbell IM, Orlando LA, Robinson P, Walton NA (2026).** Extraction of Human Phenotype Ontology (HPO) Concepts from Clinical Notes Utilizing LLMs with Model Context Protocol (MCP). *medRxiv preprint*.  
  PMID 42245026 · PMC13232345 · doi:10.64898/2026.05.23.26353963 · access: open (preprint) · [full text](https://www.medrxiv.org/content/10.64898/2026.05.23.26353963v1.full.pdf) · key `larsen2026_hpo_mcp`  
  Source of the grant's 97.6% Sonnet 4.5 HPO precision (Table 1, tool-augmented, 4 synthetic clinical notes; recall 65.3%). HPO lookup via MCP is reusable for HPO grounding. *Note: PMID/PMCID seen in search-result titles only (PubMed page blocked).*
- **Luo L, Yan S, Lai P-T, Veltri D, Oler A, Xirasagar S, Ghosh R, Similuk M, Robinson PN, Lu Z (2021).** PhenoTagger: a hybrid method for phenotype concept recognition using human phenotype ontology. *Bioinformatics 37(13):1884-1890*.  
  PMID 33471061 · doi:10.1093/bioinformatics/btab019 · arXiv:2009.08478 · access: open (arXiv) · [full text](https://arxiv.org/pdf/2009.08478) · key `luo2021_phenotagger`  
  Standard pre-LLM HPO tagger baseline. *Note: PMCID not confirmed.*
- **Groza T, Caufield H, Gration D, Baynam G, Haendel MA, Robinson PN, Mungall CJ, Reese JT (2024).** An evaluation of GPT models for phenotype concept recognition. *BMC Med Inform Decis Mak 24(1)*.  
  PMID 38297371 · PMC10829255 · doi:10.1186/s12911-024-02439-w · arXiv:2309.17169 · access: open (publisher) · [full text](https://arxiv.org/pdf/2309.17169) · key `groza2024_gpt_hpo`  
  Monarch-group evaluation: GPT-4 HPO recognition was non-deterministic and needed in-context HPO labels. Supports repeat runs and ontology grounding. *Note: PMCID from search-result title.*
- **Yang J, Liu C, Deng W, Wu D, Weng C, Zhou Y, Wang K (2024).** Enhancing phenotype recognition in clinical notes using large language models: PhenoBCBERT and PhenoGPT. *Patterns 5(1):100887*.  
  PMID 38264716 · PMC10801236 · doi:10.1016/j.patter.2023.100887 · arXiv:2308.06294 · access: open (arXiv) · [full text](https://arxiv.org/pdf/2308.06294) · key `yang2024_phenogpt`  
  Fine-tuned LLM HPO recognizer; possible comparator. *Note: PMCID from search-result title.*
- **Shyr C, Hu Y, Tinker RJ, Cassini TA, Byram KW, Hamid R, Fabbri DV, Wright A, Peterson JF, Bastarache L, Xu H (2026).** An AI framework for end-to-end rare disease phenotyping from clinical notes using large language models. *arXiv preprint*.  
  arXiv:2602.20324 · access: open (arXiv) · [full text](https://arxiv.org/pdf/2602.20324) · key `shyr2026_rarephenix`  
  RARE-PHENIX: chained extraction, HPO standardization and prioritization; recent pipeline comparator (clinical notes, not literature).

### LLMs on phenopackets

- ★ **Reese JT, Chimirri L, Bridges Y, Danis D, Caufield JH, et al.; Mungall CJ, Robinson PN (2026).** Systematic benchmarking demonstrates large language models have not reached the diagnostic accuracy of traditional rare-disease decision support tools. *Eur J Hum Genet 34(4):498-504*.  
  PMC11302616 · doi:10.1038/s41431-026-02054-5 · access: open (repository copy) · [full text](https://escholarship.org/content/qt64v8j4b5/qt64v8j4b5.pdf) · key `reese2026_llm_vs_exomiser`  
  LLMs run on ~5,200 phenopacket-derived cases from the literature (o1-preview top-1 23.6% vs Exomiser 35.5%). Shows phenopackets as evaluation currency and a memorization risk. *Note: PMID/PMCID shown are for the medRxiv preprint (PMID 39108510; PMC11302616; DOI 10.1101/2024.07.22.24310816). Journal PMID not confirmed.*
- **Nguyen M-H, Yang C-T, Cassini TA, et al.; Shyr C (2026).** Diagnostic Accuracy of Large Language Models for Rare Diseases: A Systematic Review and Meta-Analysis. *medRxiv preprint*.  
  doi:10.64898/2026.03.26.26349194 · access: open (preprint) · [full text](https://www.medrxiv.org/content/10.64898/2026.03.26.26349194v1.full.pdf) · key `nguyen2026_llm_rd_metaanalysis`  
  All 19 system-dataset pairs rated high risk of bias, mainly from data leakage: direct support for the memorization probe.

### Variant extraction and curation

- ★ **Birgmeier J, Deisseroth CA, Hayward LE, Galhardo LMT, Tierno AP, Jagadeesh KA, Stenson PD, Cooper DN, Bernstein JA, Haeussler M, Bejerano G (2020).** AVADA: toward automated pathogenic variant evidence retrieval directly from the full-text literature. *Genet Med 22(2):362-370*.  
  PMID 31467448 · doi:10.1038/s41436-019-0643-6 · access: open (preprint) · [full text](https://www.biorxiv.org/content/10.1101/461269v1.full.pdf) · key `birgmeier2020_avada`  
  Full-text variant retrieval recovered 59% of HGMD disease-causing variants; reports >60,000 likely disease-causing HGMD variants absent from ClinVar. Best prior estimate of the gap. *Note: Preprint bioRxiv 10.1101/461269. PMCID likely PMC7301356 (unconfirmed).*
- ★ **Wei C-H, Allot A, Riehle K, Milosavljevic A, Lu Z (2022).** tmVar 3.0: an improved variant concept recognition and normalization tool. *Bioinformatics 38(18):4449-4451*.  
  PMID 35904569 · doi:10.1093/bioinformatics/btac537 · arXiv:2204.03637 · access: open (publisher) · [full text](https://arxiv.org/pdf/2204.03637) · key `wei2022_tmvar3`  
  Standard variant recognizer/normalizer; baseline for HGVS extraction recall. *Note: PMCID not confirmed.*
- ★ **Wang P, Wang K (2025).** PubMind: Literature-Based Genetic Variant Extraction and Functional Annotation Using LLMs. *bioRxiv preprint*.  
  doi:10.1101/2025.10.13.682183 · access: open (preprint) · [full text](https://www.biorxiv.org/content/10.1101/2025.10.13.682183.full.pdf) · key `wang2025_pubmind`  
  LLM (Llama-3.3-70B) variant extraction at PubMed/PMC scale; ~10% of mapped variants overlap ClinVar. Closest analogue to our concordance question. *Note: A Nat Commun version (s41467-026-76834-4) appeared in search results but could not be loaded; unconfirmed.*
- ★ **Murugan M, Yuan B, Stephen J, et al.; Venner E (2026).** Performance Characteristics of Reasoning LLMs for Evidence Extraction from Clinical Genomics Literature. *medRxiv preprint*.  
  doi:10.64898/2026.02.18.26346543 · access: open (preprint) · [full text](https://www.medrxiv.org/content/10.64898/2026.02.18.26346543v1.full.pdf) · key `murugan2026_reasoning_llm_ps4`  
  Unfavourable for Claude: on counting probands (PS4), Claude Sonnet 4 had the lowest exact-count concordance (73.0% vs 91.1% best) and lowest stability. Closely related to our proband dedup and counting.
- **Allot A, Wei C-H, Phan L, Hefferon T, Landrum M, Rehm HL, Lu Z (2023).** Tracking genetic variants in the biomedical literature using LitVar 2.0. *Nat Genet 55(6):901-903*.  
  doi:10.1038/s41588-023-01414-x · access: paywalled · key `allot2023_litvar2`  
  Variant-to-paper index (~15M variants) useful for corpus building. It links to ClinVar, so keep it out of the extraction step. *Note: PMID not confirmed; PMC11096795 appeared in search results without a title (unconfirmed).*
- **Li S, Wang Y, Liu C-M, Huang Y, Lam T-W, Luo R (2025).** AutoPM3: enhancing variant interpretation via LLM-driven PM3 evidence extraction from scientific literature. *Bioinformatics 41(7):btaf382*.  
  PMID 40586923 · PMC12263107 · doi:10.1093/bioinformatics/btaf382 · access: open (PMC) · [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC12263107/) · key `li2025_autopm3`  
  Text2SQL over tables plus RAG over text for ACMG PM3 evidence; flags supplementary tables as a hard case for variant extraction. *Note: PMCID from search-result title.*
- **Saadat A, Fellay J (2026).** Large Language Models for Variant-Centric Functional Evidence Mining. *arXiv preprint*.  
  arXiv:2604.00075 · access: open (arXiv) · [full text](https://arxiv.org/pdf/2604.00075) · key `saadat2026_functional_evidence`  
  ClinGen-derived benchmark for LLM functional-evidence mining with a curator-assist pipeline; no Claude tested.
- **Ma W, Fong G, Lai J, et al.; Chung BHY (2026).** AI-CURA, an automated LLM workflow for high-accuracy genetic variant classification. *Sci Transl Med (2026; issue 855)*.  
  doi:10.1126/scitranslmed.adz4172 · access: paywalled · key `ma2026_aicura`  
  Peer-reviewed precedent for LLM literature-evidence variant classification, including reanalysis of ClinVar conflicting variants. *Note: Seen only via a secondary index; confirm volume/pages on science.org before citing.*

### Systematic-review extraction

- ★ **Gartlehner G, Kahwati L, Hilscher R, Thomas I, Kugley S, Crotty K, Viswanathan M, Nussbaumer-Streit B, Booth G, Erskine N, Konet A, Chew R (2024).** Data extraction for evidence synthesis using a large language model: a proof-of-concept study. *Res Synth Methods 15(4):576-589*.  
  doi:10.1002/jrsm.1710 · access: open (preprint) · [full text](https://www.medrxiv.org/content/10.1101/2023.10.02.23296415.full.pdf) · key `gartlehner2024_llm_extraction`  
  Claude 2 reached 96.3% accuracy on 160 data elements from 10 RCTs: earliest Claude-specific SR-extraction evidence (small sample). *Note: Preprint medRxiv 10.1101/2023.10.02.23296415. PMID not confirmed.*
- **Kataoka Y, Takayama T, Yoshimura K, et al.; Furukawa TA (2025).** Automating the data extraction process for systematic reviews using GPT-4o and o3. *Res Synth Methods 17(1):42-62 (online 17 Sep 2025)*.  
  doi:10.1017/rsm.2025.10030 · access: open (publisher) · [full text](https://www.cambridge.org/core/journals/research-synthesis-methods/article/automating-the-data-extraction-process-for-systematic-reviews-using-gpt4o-and-o3/28C54A601B80E2BE6611C8B7B15FEDAF) · key `kataoka2025_gpt4o_o3_extraction`  
  o3 ~75% accuracy; numeric fields worse than text. A warning for extracting ages, counts and variant positions. *Note: PMID not confirmed.*
- **Cao C, Arora R, Cento P, et al.; Bobrovitz N (2025).** Automation of Systematic Reviews with Large Language Models. *medRxiv preprint*.  
  doi:10.1101/2025.06.13.25329541 · access: open (preprint) · [full text](https://www.medrxiv.org/content/10.1101/2025.06.13.25329541.full.pdf) · key `cao2025_ottosr`  
  otto-SR end-to-end SR automation (93.1% extraction accuracy vs 79.7% human workflow); main comparator to SLIDERS.

### Grant-cited benchmarks

- ★ **Jackson D, Keating W, Cameron G, Hill-Smith M (2025).** AA-Omniscience: Evaluating Cross-Domain Knowledge Reliability in Large Language Models. *arXiv preprint*.  
  arXiv:2511.13029 · access: open (arXiv) · [full text](https://arxiv.org/pdf/2511.13029) · key `jackson2025_aa_omniscience`  
  Knowledge/hallucination benchmark that rewards abstention. The grant's Opus figure comes from a later Artificial Analysis page; see grant_claim_checks.md.
- ★ **Rao D, Wong E, Callison-Burch C (2026).** Detecting and Correcting Reference Hallucinations in Commercial LLMs and Deep Research Agents. *arXiv preprint*.  
  arXiv:2604.03173 · access: open (arXiv) · [full text](https://arxiv.org/pdf/2604.03173) · key `rao2026_reference_hallucination`  
  Actual source of the grant's 'DRBench 3.0%/3.2%' figures (hallucinated-URL rates for search-augmented Claude 3.5/3.7 Sonnet). See grant_claim_checks.md. *Note: Title, authors, date re-checked 2026-10-16.*
- **Du M, Xu B, Zhu C, Wang X, Mao Z (2025).** DeepResearch Bench: A Comprehensive Benchmark for Deep Research Agents. *arXiv preprint*.  
  doi:10.48550/arXiv.2506.11763 · arXiv:2506.11763 · access: open (arXiv) · [full text](https://arxiv.org/pdf/2506.11763) · key `du2025_deepresearchbench`  
  The 100-task benchmark whose agent outputs Rao et al. analysed. *Note: Not the same as ServiceNow's 'DRBench' (arXiv 2510.00172).*


## 2. Standards, ontologies and ground-truth databases

### Phenopackets and tooling

- ★ **Jacobsen JOB, Baudis M, et al.; Haendel MA, Robinson PN (2022).** The GA4GH Phenopacket schema defines a computable representation of clinical data. *Nat Biotechnol 40(6):817-820*.  
  PMID 35705716 · PMC9363006 · doi:10.1038/s41587-022-01357-4 · access: open (PMC) · [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC9363006) · key `jacobsen2022_phenopacket_schema`  
  The v2 output schema every extracted record must follow.
- ★ **Danis D, Jacobsen J, Wagner A, et al.; Haendel M, Robinson P (2023).** Phenopacket-tools: Building and validating GA4GH Phenopackets. *PLoS One 18(5):e0285433*.  
  PMID 37196000 · PMC10191354 · doi:10.1371/journal.pone.0285433 · access: open (PMC) · [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC10191354) · key `danis2023_phenopacket_tools`  
  Citable paper for phenopacket validation (there is no dedicated pyphetools/CohortValidator paper). *Note: PMCID from search-result title.*
- ★ **Danis D, Bamshad MJ, Bridges Y, et al.; Haendel MA, Robinson PN (2025).** A corpus of GA4GH phenopackets: case-level phenotyping for genomic diagnostics and discovery. *HGG Adv 6(1):100371*.  
  PMID 39394689 · PMC11564936 · doi:10.1016/j.xhgg.2024.100371 · access: open (PMC) · [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC11564936) · key `danis2025_phenopacket_store`  
  phenopacket-store resource paper (v0.1.19: 6,668 phenopackets, 959 publications), hand-curated with pyphetools. Prior art, possible human-curated reference, and a memorization risk. *Note: Preprint medRxiv 10.1101/2024.05.29.24308104 (PMC11160806). One JAX repository record (stfb2024/262) says 'withdrawn'; other sources show the paper as current. Check on the publisher page.*
- ★ **Monarch Initiative (2025).** pyphetools (software; v0.9.119 on PyPI, 3 Nov 2025) - includes CohortValidator. *Software documentation*.  
  no identifier · access: software · [full text](https://monarch-initiative.github.io/pyphetools/api/validation/) · key `pyphetools_software`  
  CohortValidator lives here; it is the validator named in the grant. *Note: No paper; cite software + version with Danis 2023/2025.*
- ★ **Rekerle L, Danis D, et al.; Haendel MA, Robinson PN (2026).** GA4GH phenopacket-driven characterization of genotype-phenotype correlations in Mendelian disorders. *Am J Hum Genet 113(1):57-70*.  
  PMID 41443197 · PMC12824607 · doi:10.1016/j.ajhg.2025.12.001 · access: open (PMC) · [full text](https://www.medrxiv.org/content/10.1101/2025.03.05.25323315.full.pdf) · key `rekerle2026_gpsea`  
  GPSEA: statistical genotype-phenotype testing on phenopacket cohorts. Ready-made engine for the per-gene genotype-phenotype maps. *Note: PMCID from search-result title; preprint PMC11908317.*
- **Ladewig M, Jacobsen J, et al.; Haendel M, Robinson P (2023).** GA4GH Phenopackets: A Practical Introduction. *Adv Genet (Hoboken) 4(1):2200016*.  
  PMID 36910590 · doi:10.1002/ggn2.202200016 · access: open (publisher) · key `ladewig2023_phenopackets_primer`  
  Practical guide for designing the extraction schema around phenopacket fields. *Note: PMCID likely PMC10000265 (unconfirmed).*

### Ontologies

- ★ **Gargano MA, Matentzoglu N, Coleman B, et al.; Robinson PN (2024).** The Human Phenotype Ontology in 2024: phenotypes around the world. *Nucleic Acids Res 52(D1):D1333-D1346*.  
  PMID 37953324 · PMC10767975 · doi:10.1093/nar/gkad1005 · access: open (PMC) · [full text](https://discovery.ucl.ac.uk/id/eprint/10189754/1/The%20Human%20Phenotype%20Ontology%20in%202024%20phenotypes%20around%20the%20world.pdf) · key `gargano2024_hpo`  
  Current HPO citation; the vocabulary for three-state phenotype coding. *Note: PMCID from search result. No newer HPO NAR paper found.*
- ★ **Vasilevsky NA, Toro S, Matentzoglu N, et al.; Mungall CJ, Haendel MA (2025).** Mondo: integrating disease terminology across communities. *Genetics 232(4):iyaf215*.  
  PMID 41052288 · PMC13050200 · doi:10.1093/genetics/iyaf215 · access: open (PMC) · [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC13050200) · key `vasilevsky2025_mondo`  
  First peer-reviewed Mondo paper; Mondo IDs are our primary disease identifiers.
- **Rath A, Olry A, Dhombres F, et al. (2012).** Representation of rare diseases in health information systems: the Orphanet approach to serve a wide range of end users. *Hum Mutat*.  
  doi:10.1002/humu.22078 · access: unknown · key `rath2012_orphanet`  
  Older peer-reviewed Orphanet citation, if a published reference is required. *Note: PMID, volume and pages not confirmed.*
- **Lucano C, Lagorce D, Olry A, et al.; Rath A (2026).** The Orphanet Nomenclature and Classification of rare diseases: a standard terminology for improved patient recognition and data interoperability. *medRxiv preprint (v2 12 Mar 2026)*.  
  doi:10.1101/2025.08.10.25333394 · access: open (preprint) · key `lucano2026_orphanet`  
  Most recent Orphanet description; for ORPHA cross-references. *Note: Not peer reviewed.*

### Variants and nomenclature

- ★ **den Dunnen JT, Dalgleish R, Maglott DR, Hart RK, Greenblatt MS, McGowan-Jordan J, Roux AF, Smith T, Antonarakis SE, Taschner PE (2016).** HGVS Recommendations for the Description of Sequence Variants: 2016 Update. *Hum Mutat 37(6):564-569*.  
  PMID 26931183 · doi:10.1002/humu.22981 · access: open (repository copy) · [full text](https://figshare.le.ac.uk/articles/journal_contribution/HGVS_Recommendations_for_the_Description_of_Sequence_Variants_2016_Update_/10132955/1) · key `dendunnen2016_hgvs`  
  Baseline HGVS nomenclature citation. *Note: Publisher version paywalled; accepted manuscript on Leicester figshare.*
- ★ **Freeman PJ, Hart RK, Gretton LJ, Brookes AJ, Dalgleish R (2018).** VariantValidator: Accurate validation, mapping, and formatting of sequence variation descriptions. *Hum Mutat 39(1):61-68*.  
  PMID 28967166 · PMC5765404 · doi:10.1002/humu.23348 · access: open (PMC) · [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC5765404) · key `freeman2018_variantvalidator`  
  The HGVS normalization tool in the pipeline.
- ★ **Morales J, Pujar S, Loveland JE, et al.; Frankish A, Cunningham F, Murphy TD (2022).** A joint NCBI and EMBL-EBI transcript set for clinical genomics and research. *Nature 604(7905):310-315*.  
  PMID 35388217 · PMC9007741 · doi:10.1038/s41586-022-04558-8 · access: open (PMC) · [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC9007741) · key `morales2022_mane`  
  MANE Select: the transcript set we state for every HGVS string. *Note: PMCID from search-result title.*
- ★ **Freeman PJ, Wagstaff JF, Fokkema IFAC, Cutting GR, Rehm HL, Davies AC, den Dunnen JT, Gretton LJ, Dalgleish R (2024).** Standardizing variant naming in literature with VariantValidator to increase diagnostic rates. *Nat Genet 56(11):2284-2286*.  
  PMID 39358598 · doi:10.1038/s41588-024-01938-w · access: paywalled · key `freeman2024_vv_literature`  
  Directly supports our premise: non-standard variant names in papers hide evidence from databases. *Note: Author correction PMID 39472695.*
- ★ **Hart RK, Fokkema IFAC, DiStefano M, Hastings R, Laros JFJ, Taylor R, Wagner AH, den Dunnen JT (2024).** HGVS Nomenclature 2024: improvements to community engagement, usability, and computability. *Genome Med 16:149*.  
  PMID 39702242 · PMC11660784 · doi:10.1186/s13073-024-01421-5 · access: open (PMC) · [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC11660784) · key `hart2024_hgvs2024`  
  Current HGVS version; cite alongside den Dunnen 2016. *Note: PMCID from search-result title.*
- **Lansdon LA, et al. (incl. Freeman PJ) (2026).** Universal presence of gene/variant nomenclature errors in journal manuscript submissions. *Clin Chem 72(6):652-661*.  
  doi:10.1093/clinchem/hvag010 · access: unknown · key `lansdon2026_nomenclature_errors`  
  All 52 audited Genetics in Medicine submissions had nomenclature errors; justifies keeping the original string next to the normalized one. *Note: PMID not confirmed.*

### Databases

- ★ **Amberger JS, Bocchini CA, Scott AF, Hamosh A (2019).** OMIM.org: leveraging knowledge across phenotype-gene relationships. *Nucleic Acids Res 47(D1):D1038-D1043*.  
  PMID 30445645 · PMC6323937 · doi:10.1093/nar/gky1151 · access: open (PMC) · [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC6323937) · key `amberger2019_omim`  
  Most recent OMIM NAR paper; ground truth for allelic variants. *Note: PMCID from search-result title.*
- ★ **Landrum MJ, Chitipiralla S, Kaur K, et al.; Kattman BL (2025).** ClinVar: updates to support classifications of both germline and somatic variants. *Nucleic Acids Res 53(D1):D1313-D1321*.  
  PMID 39578691 · doi:10.1093/nar/gkae1090 · access: open (publisher) · [full text](https://academic.oup.com/nar/article/53/D1/D1313/7907366) · key `landrum2025_clinvar`  
  Latest ClinVar paper; ground truth and submission target. *Note: PMCID not confirmed. No 2026 ClinVar NAR paper found.*
- ★ **NCBI ClinVar (2026).** ClinVar submission spreadsheet documentation (collection method: literature only) and submission instructions. *Official web pages (fetched 2026-10-16)*.  
  no identifier · access: official page · [full text](https://www.ncbi.nlm.nih.gov/clinvar/docs/spreadsheet/) · key `clinvar_submission_docs`  
  Defines 'literature only' as no additional submitter curation and recommends not providing a classification. Conflicts with our plan; see grant_claim_checks.md. *Note: Policy page; re-check before any submission.*
- ★ **Johns Hopkins University / OMIM (2026).** OMIM copyright, use agreement and download pages. *Official web pages*.  
  no identifier · access: official page · [full text](https://www.omim.org/help/copyright) · key `omim_terms`  
  Archived terms bar copying or redistribution without a license. Must be checked before storing an OMIM snapshot in data/reference/. *Note: omim.org blocks automated fetching; only a 2016 archived copy was readable. Read current terms by hand.*
- **Philippakis AA, Azzariti DR, Beltran S, et al.; Boycott KM, Rehm HL (2015).** The Matchmaker Exchange: a platform for rare disease gene discovery. *Hum Mutat 36(10):915-921*.  
  PMID 26295439 · PMC4610002 · doi:10.1002/humu.22858 · access: open (PMC) · [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC4610002) · key `philippakis2015_mme`  
  Matchmaker Exchange background, cited in the impact statement.
- **Hamosh A, Amberger JS, Bocchini C, Scott AF, Rasmussen SA (2021).** Online Mendelian Inheritance in Man (OMIM): Victor McKusick's magnum opus. *Am J Med Genet A 185(11):3259-3265*.  
  doi:10.1002/ajmg.a.62407 · access: open (publisher) · key `hamosh2021_omim`  
  Newer OMIM overview, optional companion to Amberger 2019. *Note: PMID not confirmed.*
- **Putman TE, Schaper K, Matentzoglu N, et al.; Munoz-Torres MC (2024).** The Monarch Initiative in 2024: an analytic platform integrating phenotypes, genes and diseases across species. *Nucleic Acids Res 52(D1):D938-D949*.  
  PMID 38000386 · PMC10767791 · doi:10.1093/nar/gkad1082 · access: open (PMC) · [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC10767791) · key `putman2024_monarch`  
  Latest Monarch paper; Monarch hosts phenopacket-store and is an outreach target. *Note: PMCID from search-result title.*

### Variant interpretation

- ★ **Richards S, Aziz N, Bale S, et al.; Rehm HL (2015).** Standards and guidelines for the interpretation of sequence variants: a joint consensus recommendation of the ACMG and AMP. *Genet Med 17(5):405-424*.  
  PMID 25741868 · PMC4544753 · doi:10.1038/gim.2015.30 · access: open (PMC) · [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC4544753) · key `richards2015_acmg`  
  Classification framework for the adjudication panel.
- ★ **Biesecker LG, Byrne AB, Harrison SM, Pesaran T, Schaffer AA, Shirts BH, Tavtigian SV, Rehm HL (2024).** ClinGen guidance for use of the PP1/BS4 co-segregation and PP4 phenotype specificity criteria for sequence variant pathogenicity classification. *Am J Hum Genet 111(1):24-38*.  
  PMID 38103548 · doi:10.1016/j.ajhg.2023.11.009 · access: open (publisher) · key `biesecker2024_clingen_pp1_pp4`  
  How segregation and phenotype-specificity evidence from case reports should be weighed at adjudication. *Note: PMCID not confirmed.*

### Literature vs ClinVar

- ★ **Yang S, Lincoln SE, Kobayashi Y, Nykamp K, Nussbaum RL, Topper S (2017).** Sources of discordance among germ-line variant classifications in ClinVar. *Genet Med 19(10):1118-1126*.  
  PMID 28569743 · doi:10.1038/gim.2017.60 · access: open (PMC) · key `yang2017_clinvar_discordance`  
  Literature-only entries were 8.8% of submissions but 31.4% of outlier classifications: key caution for our submissions. *Note: PMCID likely PMC5542009 (unconfirmed). Corrigendum PMID 29215652.*
- **Harrison SM, Dolinsky JS, Johnson AEK, Pesaran T, Azzariti DR, Bale S, Chao EC, Das S, Vincent L, Rehm HL (2017).** Clinical laboratories collaborate to resolve differences in variant interpretations submitted to ClinVar. *Genet Med*.  
  PMID 28301460 · doi:10.1038/gim.2017.14 · access: unknown · key `harrison2017_clinvar_conflicts`  
  Background on reconciling conflicting classifications. *Note: Volume/pages not confirmed.*
- **Wright CF, Eberhardt RY, Constantinou P, Hurles ME, FitzPatrick DR, Firth HV; DDD Study (2021).** Evaluating variants classified as pathogenic in ClinVar in the DDD Study. *Genet Med 23(3):571-575*.  
  PMID 33149276 · PMC7935711 · doi:10.1038/s41436-020-01021-9 · access: open (PMC) · [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC7935711) · key `wright2021_ddd_clinvar`  
  ClinVar is an imperfect ground truth; matters for interpreting discordance. *Note: PMCID from search-result title.*
- **Genomenon (2026).** Increasing diagnostic yield in ClinVar with literature-derived patient data: Fabry disease GLA variants (ESHG 2026 poster). *Grey literature (not peer reviewed)*.  
  no identifier · access: open (web page) · [full text](https://www.genomenon.com/resource/increasing-diagnostic-yield-clinvar-literature-derived-patient-data-example-fabry-disease-gla-variants) · key `genomenon2026_gla_poster`  
  Precedent: 753 literature-only GLA variants submitted; reported P/LP records rose 481 to 1,103. *Note: Not peer reviewed; do not cite as evidence.*


## 3. Pilot diseases and substitutes

### Alexander disease (GFAP)

- ★ **Prust M, et al. (2011).** GFAP mutations, age at onset, and clinical subtypes in Alexander disease. *Neurology 77(13):1287-1294*.  
  PMID 21917775 · doi:10.1212/WNL.0b013e3182309f72 · access: open (publisher, free) · [full text](https://n.neurology.org/content/neurology/77/13/1287.full.pdf) · key `prust2011_axd_onset`  
  30 new plus 185 published cases; defines Type I/II. Standard genotype-phenotype reference.
- ★ **Srivastava S, Waldman A, Naidu S (2020).** Alexander Disease (GeneReviews; posted 2002, updated 12 Nov 2020). *GeneReviews NBK1172*.  
  PMID 20301351 · access: free-html (NCBI Bookshelf) · [full text](https://www.ncbi.nlm.nih.gov/books/NBK1172/) · key `genereviews_axd`  
  Clinical reference for phenotype vocabulary and diagnostic criteria.
- ★ **Grossi A, Rosamilia F, Carestiato S, Salsano E, Ceccherini I, Bachetti T (2024).** A systematic review and meta-analysis of GFAP gene variants in Alexander disease. *Sci Rep 14:24341*.  
  PMID 39420046 · PMC11487261 · doi:10.1038/s41598-024-75383-4 · access: open (PMC) · [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC11487261) · key `grossi2024_axd_meta`  
  Source of the grant's 550 patients / 182 variants (Results section). Most complete patient-level GFAP catalogue; benchmark for extraction completeness. *Note: IDs re-checked 2026-10-16.*
- ★ **Gagliardi D, Wade C, Tucci A, Houlden H, Chataway J, Barkhof F, Lynch DS (2024).** Analysis of GFAP variants in UK Biobank suggests underdiagnosis or incomplete penetrance of adult-onset Alexander disease. *J Neurol Neurosurg Psychiatry (online 6 Dec 2024)*.  
  PMID 39643430 · doi:10.1136/jnnp-2024-335089 · access: unknown · key `gagliardi2024_axd_ukb`  
  Genotype-first comparator: 106 P/LP GFAP carriers in ~470,000 UK Biobank exomes, milder/under-recognized phenotypes. Directly relevant to the ascertainment-bias arm. *Note: Volume/pages not confirmed.*
- **Mura E, et al. (2021).** Alexander disease evolution over time: data from an Italian cohort of pediatric-onset patients. *Mol Genet Metab 134(4):353-358*.  
  PMID 34865968 · doi:10.1016/j.ymgme.2021.11.009 · access: paywalled · key `mura2021_axd_italian`  
  Longitudinal cohort (21 patients): natural-history comparator for the bias arm.
- **Messing A, Waldman AT, Bolt DM (2025).** Genotype-phenotype association for 14 GFAP variants in Alexander disease. *Neurol Genet 11(3):e200270*.  
  PMID 40520824 · PMC12166557 · doi:10.1212/NXG.0000000000200270 · access: open (publisher) · key `messing2025_axd_14variants`  
  Per-variant onset and survival across 231 cases; variant-level concordance check. *Note: PMCID via OpenAlex link only (unconfirmed).*

### LAD-I (ITGB2)

- ★ **Almarza Novoa E, Kasbekar S, Thrasher AJ, Kohn DB, Sevilla J, Nguyen T, Schwartz JD, Bueren JA (2018).** Leukocyte adhesion deficiency-I: a comprehensive review of all published cases. *J Allergy Clin Immunol Pract 6(4):1418-1420.e10*.  
  PMID 29371071 · doi:10.1016/j.jaip.2017.12.008 · access: open (repository copy) · [full text](https://discovery.ucl.ac.uk/id/eprint/10042078/1/Leukocyte%20adhesion%20deficiency.pdf) · key `almarzanovoa2018_lad1_review`  
  Source of 323 cases / 139 genotyped. Gives denominators for genotype completeness and severity-specific survival; 10 duplicate-reported cases are a ready dedup test. *Note: IDs re-checked 2026-10-16.*
- ★ **Kambli PM, et al. (2020).** Clinical and genetic spectrum of a large cohort of patients with leukocyte adhesion deficiency type 1 and 3: a multicentric study from India. *Front Immunol 11:612703*.  
  PMID 33391282 · PMC7772426 · doi:10.3389/fimmu.2020.612703 · access: open (publisher) · [full text](https://www.frontiersin.org/articles/10.3389/fimmu.2020.612703/pdf) · key `kambli2020_lad_india`  
  127 LAD-I patients, 57 ITGB2 variants (35 novel), published after the 2018 review: tests whether extraction picks up newer literature. *Note: PMCID via OpenAlex link only (unconfirmed).*
- **Qasim W, et al. (2009).** Allogeneic hematopoietic stem-cell transplantation for leukocyte adhesion deficiency. *Pediatrics 123(3):836-840*.  
  PMID 19255011 · PMC3380632 · doi:10.1542/peds.2008-1191 · access: open (PMC) · key `qasim2009_lad_hsct`  
  Outcomes for 36 transplanted children. *Note: PMCID via OpenAlex link only (unconfirmed).*
- **Booth C, et al. (2025).** Lentiviral gene therapy for severe leukocyte adhesion deficiency type 1. *N Engl J Med 392(17):1698-1709*.  
  PMID 40305711 · doi:10.1056/NEJMoa2407376 · access: paywalled · key `booth2025_lad_gene_therapy`  
  Current treatment context.

### A20 haploinsufficiency (TNFAIP3)

- ★ **Zhou Q, et al. (2016).** Loss-of-function mutations in TNFAIP3 leading to A20 haploinsufficiency cause an early-onset autoinflammatory disease. *Nat Genet 48(1):67-73*.  
  PMID 26642243 · PMC4777523 · doi:10.1038/ng.3459 · access: open (PMC) · key `zhou2016_ha20_original`  
  Original description of HA20. *Note: PMCID via OpenAlex link only (unconfirmed).*
- ★ **Elhani I, Riller Q, Boursier G, Hentgen V, Rieux-Laucat F, Georgin-Lavialle S (2024).** A20 haploinsufficiency: a systematic review of 177 cases. *J Invest Dermatol 144(6):1282-1294.e8*.  
  PMID 38128752 · doi:10.1016/j.jid.2023.12.007 · access: open (publisher, free) · [full text](http://www.jidonline.org/article/S0022202X23031949/pdf) · key `elhani2024_ha20_177`  
  Source of 177 patients (65 articles, PRISMA); per-phenotype counts are the literature baseline for the bias arm.
- ★ **Deuitch NT, Schwartz DM, Aksentijevich I (2024).** Haploinsufficiency of A20 (GeneReviews; posted 19 Dec 2024). *GeneReviews NBK610430*.  
  PMID 39715316 · access: free-html (NCBI Bookshelf) · [full text](https://www.ncbi.nlm.nih.gov/books/NBK610430/) · key `genereviews_ha20`  
  Clinical reference; reports >180 individuals from 97 families.
- **Aeschlimann FA, et al. (2018).** A20 haploinsufficiency (HA20): clinical phenotypes and disease course of patients with a newly recognised NF-kB-mediated autoinflammatory disease. *Ann Rheum Dis 77(5):728-735*.  
  PMID 29317407 · doi:10.1136/annrheumdis-2017-212403 · access: open (repository copy) · key `aeschlimann2018_ha20_cohort`  
  16 patients from 7 families followed over time. *Note: Repository copy: https://dspace.library.uu.nl/handle/1874/368983*
- **Li JC, et al. (2026).** How I treat: haploinsufficiency of A20. *J Hum Immun 2(4):e20250138*.  
  PMID 42169681 · doi:10.70962/jhi.20250138 · access: open (publisher) · [full text](https://rupress.org/jhi/article/2/4/e20250138/282066/How-I-Treat-Haploinsufficiency-of-A20) · key `li2026_ha20_howitreat`  
  Current review: ~200 reported cases, ~100 pathogenic variants. *Note: PMCID possibly PMC13177427 (unconfirmed).*
- **He T, Wang J, Carpio Tumba M, et al.; Zhou Q (2026).** Multicenter international cohort study of HA20 reveals novel genetic architecture and phenotypic evolution. *medRxiv preprint (4 Jan 2026)*.  
  doi:10.64898/2026.01.01.25342105 · access: open (preprint) · [full text](https://www.medrxiv.org/content/10.64898/2026.01.01.25342105.full.pdf) · key `he2026_ha20_multicenter`  
  185-patient Chinese/US cohort: largest cohort comparator for the bias arm. *Note: DOI taken from the URL. Not peer reviewed.*

### SSADH deficiency (ALDH5A1)

- ★ **DiBacco ML, Roullet JB, Kapur K, Brown MN, Walters DC, Gibson KM, Pearl PL (2019).** Age-related phenotype and biomarker changes in SSADH deficiency. *Ann Clin Transl Neurol 6(1):114-120*.  
  PMID 30656189 · PMC6331944 · doi:10.1002/acn3.696 · access: open (publisher) · [full text](https://onlinelibrary.wiley.com/doi/pdfdirect/10.1002/acn3.696) · key `dibacco2019_ssadh_natural_history`  
  Registry of 133 patients (49 longitudinal): main cohort comparator for the bias arm. *Note: PMCID via OpenAlex link only (unconfirmed). Related natural-history study NCT03758521 (record not read).*
- ★ **Didiasova M, Banning A, Brennenstuhl H, Jung-Klawitter S, Cinquemani C, Opladen T, Tikkanen R (2020).** Succinic semialdehyde dehydrogenase deficiency: an update. *Cells 9(2):477*.  
  PMID 32093054 · PMC7072817 · doi:10.3390/cells9020477 · access: open (PMC) · [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC7072817) · key `didiasova2020_ssadh_update`  
  Source of the ~450 published patients figure.
- ★ **Tokatly Latzer I, Pearl PL, Roullet JB (2025).** Succinic Semialdehyde Dehydrogenase Deficiency (GeneReviews; posted 2004, updated 9 Jan 2025). *GeneReviews NBK1195*.  
  PMID 20301374 · access: free-html (NCBI Bookshelf) · [full text](https://www.ncbi.nlm.nih.gov/books/NBK1195/) · key `genereviews_ssadh`  
  Clinical reference; states at least 450 individuals reported.
- **Pearl PL, et al. (2003).** Succinic semialdehyde dehydrogenase deficiency in children and adults. *Ann Neurol 54(S6):S73-S80*.  
  PMID 12891657 · doi:10.1002/ana.10629 · access: paywalled · key `pearl2003_ssadh_series`  
  Early case series.
- **Tokatly Latzer I, et al.; Pearl PL (2023).** Phenotypic correlates of structural and functional protein impairments resultant from ALDH5A1 variants. *Hum Genet 142:1755-1776*.  
  PMID 37503297 · PMC10371128 · doi:10.1007/s00439-023-02613-6 · access: open (repository copy) · [full text](https://iris.univr.it/retrieve/37c87b1b-721b-4110-9e34-3e41db365f9c/s00439-023-02613-6-1.pdf) · key `tokatlylatzer2023_ssadh_genotype`  
  58 patients, 32 variants: genotype-phenotype reference. *Note: OpenAlex also lists PMID 37962671; resolve before citing.*
- **Tokatly Latzer I, et al.; Pearl PL (2024).** Consensus guidelines for the diagnosis and management of succinic semialdehyde dehydrogenase deficiency. *Mol Genet Metab 142(1):108363*.  
  PMID 38452608 · PMC11073920 · doi:10.1016/j.ymgme.2024.108363 · access: open (PMC) · [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC11073920) · key `tokatlylatzer2024_ssadh_guidelines`  
  Current consensus reference.

### Danon disease (LAMP2)

- ★ **Boucek D, Jirikowic J, Taylor M (2011).** Natural history of Danon disease. *Genet Med 13(6):563-568*.  
  PMID 21415759 · doi:10.1097/GIM.0b013e31820ad795 · access: open (repository copy) · [full text](https://rocketpharma.com/wp-content/uploads/Danon_Natural-History_2011.pdf) · key `boucek2011_danon_natural_history`  
  82 patients from 36 families plus 63 literature cases; documents male/female severity difference.
- ★ **Brambatti M, Caspi O, Maolo A, Koshi E, Greenberg B, Taylor MRG, Adler ED (2019).** Danon disease: gender differences in presentation and outcomes. *Int J Cardiol 286:92-98*.  
  PMID 30857840 · doi:10.1016/j.ijcard.2019.01.020 · access: paywalled · key `brambatti2019_danon_gender`  
  146 patients from 83 papers; median age at composite outcome 21 (male) vs 38 (female). Target structure the extraction must reproduce.
- ★ **Taylor MRG, Adler ED (2024).** Danon Disease (GeneReviews; posted 2020, revised 23 May 2024). *GeneReviews NBK554742*.  
  PMID 32134616 · access: free-html (NCBI Bookshelf) · [full text](https://www.ncbi.nlm.nih.gov/books/NBK554742/) · key `genereviews_danon`  
  Clinical reference.
- **Sugie K, et al. (2018).** [Japanese nationwide survey of Danon disease; exact title not confirmed]. *Int J Mol Sci 19(11):3507*.  
  PMID 30413001 · PMC6274850 · doi:10.3390/ijms19113507 · access: open (publisher) · key `sugie2018_danon_japan`  
  National survey cohort; possible comparator. *Note: Exact title not confirmed; PMCID via OpenAlex link only. Confirm before citing.*
- **Cenacchi G, Papa V, Pegoraro V, Marozzo R, Fanin M, Angelini C (2020).** Danon disease: review of natural history and recent advances. *Neuropathol Appl Neurobiol 46(4):303-322*.  
  PMID 31698507 · doi:10.1111/nan.12587 · access: paywalled · key `cenacchi2020_danon_review`  
  Survey of >500 reported patients.
- **Sugie K, Nishino I (2024).** History and perspective of LAMP-2 deficiency (Danon disease). *Biomolecules 14(10):1272*.  
  PMID 39456205 · PMC11506487 · doi:10.3390/biom14101272 · access: open (publisher) · [full text](https://www.mdpi.com/2218-273X/14/10/1272) · key `sugie2024_danon_history`  
  States about 100 families worldwide (closest source for the grant's '>100 families'). *Note: PMCID via OpenAlex link only (unconfirmed).*
- **Khedro T, et al.; Hong KN (2025).** Danon disease in male patients: a prospective natural history study. *Orphanet J Rare Dis 20:530*.  
  PMID 41121270 · PMC12542076 · doi:10.1186/s13023-025-04058-8 · access: open (PMC) · [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC12542076) · key `khedro2025_danon_prospective`  
  Prospective natural history (9 males). *Note: Larger 116-patient study appears only as medRxiv 10.1101/2024.05.21.24307720 (not verified in detail).*

### Tangier disease (ABCA1)

- ★ **Burnett JR, Hooper AJ, McCormick SPA, Hegele RA (2019).** Tangier Disease (GeneReviews; posted 21 Nov 2019). *GeneReviews NBK549920*.  
  PMID 31751110 · access: free-html (NCBI Bookshelf) · [full text](https://www.ncbi.nlm.nih.gov/books/NBK549920/) · key `genereviews_tangier`  
  Clinical reference; states fewer than 100 cases published. *Note: Last-update date not confirmed.*
- ★ **Koseki M, et al. (2021).** Current diagnosis and management of Tangier disease. *J Atheroscler Thromb 28(8):802-810*.  
  PMID 33994407 · PMC8326168 · doi:10.5551/jat.RV17053 · access: open (publisher) · [full text](https://www.jstage.jst.go.jp/article/jat/28/8/28_RV17053/_pdf) · key `koseki2021_tangier_review`  
  Counts ~144 reported cases (35 Japan, 109 elsewhere); contradicts the grant's ~200. *Note: PMCID via OpenAlex link only (unconfirmed).*
- **Puntoni M, et al. (2012).** Tangier disease: epidemiology, pathophysiology, and management. *Am J Cardiovasc Drugs 12(5):303-311*.  
  PMID 22913675 · doi:10.1007/BF03261839 · access: paywalled · key `puntoni2012_tangier`  
  Review. *Note: Co-authors not confirmed; check before citing.*
- **Schaefer EJ, et al.; Asztalos BF (2016).** Diagnosis and treatment of high density lipoprotein deficiency. *Prog Cardiovasc Dis 59(2):97-106*.  
  PMID 27565770 · PMC5331615 · doi:10.1016/j.pcad.2016.08.006 · access: open (PMC) · key `schaefer2016_hdl_deficiency`  
  Cardiovascular disease rates by age. *Note: PMCID via OpenAlex link only (unconfirmed).*
- **Mercan M, et al.; Seyhan S (2018).** Peripheral neuropathy in Tangier disease: a literature review and assessment. *J Peripher Nerv Syst 23(2):88-98*.  
  PMID 29582519 · doi:10.1111/jns.12265 · access: paywalled · key `mercan2018_tangier_neuropathy`  
  Literature review of 54 neuropathy cases.
- **Lenzini L, Tresso S, Avogaro A, Vitturi N (2025).** Genotype and phenotype of subjects with Tangier disease developing cardiovascular disease. *Journal not confirmed*.  
  no identifier · access: unknown · [full text](https://research.unipd.it/handle/11577/3574774) · key `lenzini2025_tangier_cvd`  
  73 genetically confirmed patients (30 with CVD): genotype-phenotype literature review. *Note: PMID, DOI and journal not confirmed.*

### Substitutes

- **Wouters CH, Maes A, Foley KP, Bertin J, Rose CD (2014).** [Review of Blau syndrome; exact title not confirmed]. *Pediatr Rheumatol 12:33*.  
  PMID 25136265 · PMC4136643 · doi:10.1186/1546-0096-12-33 · access: open (PMC) · [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC4136643) · key `wouters2014_blau`  
  Key Blau syndrome (NOD2) review. *Note: Exact title not confirmed.*
- **Stockler-Ipsiroglu S, et al. (2014).** [Outcomes in 48 individuals with GAMT deficiency; exact title not confirmed]. *Mol Genet Metab 111(1):16-25*.  
  PMID 24268530 · doi:10.1016/j.ymgme.2013.10.018 · access: open (publisher) · key `stockleripsiroglu2014_gamt`  
  GAMT outcomes series; GeneReviews: Creatine Deficiency Disorders NBK3794 (PMID 20301745). *Note: Exact title not confirmed.*
- **Rose CD, et al. (2015).** [Blau syndrome prospective cohort, 31 patients from 18 centres; exact title not confirmed]. *Rheumatology (Oxford) 54(6):1008-1016*.  
  PMID 25416713 · doi:10.1093/rheumatology/keu437 · access: open (publisher, free) · key `rose2015_blau_cohort`  
  Blau prospective cohort comparator. *Note: Exact title not confirmed.*
- **Beyens A, et al. (2018).** Arterial tortuosity syndrome: 40 new families and literature review. *Genet Med 20(10):1236-1245*.  
  PMID 29323665 · doi:10.1038/gim.2017.253 · access: open (publisher, free) · key `beyens2018_ats`  
  Key arterial tortuosity syndrome (SLC2A10) review. *Note: GeneReviews NBK253404 (PMID 25392904).*
- **Ferguson PJ, et al. (2021).** [Majeed syndrome review, 24 patients from 10 families; exact title not confirmed]. *Biomolecules 11(3):367*.  
  PMID 33670882 · PMC7997317 · doi:10.3390/biom11030367 · access: open (publisher) · key `ferguson2021_majeed`  
  Key Majeed syndrome (LPIN2) review. *Note: Exact title not confirmed.*
- **Vitali C, et al. (2022).** A systematic review of the natural history and biomarkers of primary LCAT deficiency. *J Lipid Res 63(3):100169*.  
  PMID 35065092 · PMC8953693 · doi:10.1016/j.jlr.2022.100169 · access: open (publisher) · key `vitali2022_lcat`  
  146 FLD + 53 fish-eye disease patients; LCAT literature/natural-history baseline. *Note: PMCID from search-result URL.*
- **Hajialigol A, et al. (2022).** Systematic review of PAPA and PAPA-like syndromes. *Immunol Genet J 5(1):20-29*.  
  doi:10.18502/igj.v5i1.14066 · access: open (publisher) · [full text](https://igj.tums.ac.ir/index.php/igj/article/view/107) · key `hajialigol2022_papa`  
  93 PAPA patients (PSTPIP1); see also Wang Y et al., Front Immunol 2021;12:735851 (PMID 34745107). *Note: PMID not confirmed.*


## 4. Bias, memorization, grounding and evaluation

### Ascertainment bias

- ★ **AlMail A, Jamjoom A, Pan A, et al. (2024).** Consensus reporting guidelines to address gaps in descriptions of ultra-rare genetic conditions. *npj Genom Med 9:27*.  
  PMID 38582909 · PMC10998895 · doi:10.1038/s41525-024-00408-w · access: open (PMC) · [full text](https://www.nature.com/articles/s41525-024-00408-w) · key `almail2024_reporting_gaps`  
  Phenotype detail was superficial or absent in most first reports: case-report phenotype spectra are incomplete, so 'not reported' must stay separate from 'excluded'.
- ★ **Wright CF, Sharp LN, Jackson L, Murray A, Ware JS, MacArthur DG, Rehm HL, Patel KA, Weedon MN (2024).** Guidance for estimating penetrance of monogenic disease-causing variants in population cohorts. *Nat Genet (2024)*.  
  PMID 39075210 · doi:10.1038/s41588-024-01842-3 · access: open (repository copy) · [full text](https://ore.exeter.ac.uk/rest/bitstreams/199765/retrieve) · key `wright2024_penetrance`  
  Framework for why phenotype-first (literature) cohorts overstate severity and penetrance versus genotype-first cohorts. *Note: Volume/pages not confirmed.*
- **van der Sluijs PJ, Jansen S, Vergano SA, et al. (2019).** The ARID1B spectrum in 143 patients: from nonsyndromic intellectual disability to Coffin-Siris syndrome. *Genet Med 21:1295-1307*.  
  PMID 30349098 · PMC6752273 · doi:10.1038/s41436-018-0330-z · access: open (PMC) · [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC6752273) · key `vandersluijs2019_arid1b`  
  Worked example of ascertainment-driven spectrum differences; notes forms without an explicit 'absent' option undercount features.
- **Felker SA, Korf BR, Barsh GS (2025).** Genotype-first assessment of presentation and penetrance of NF1, ADPKD, and Marfan syndrome within the All of Us Research Program cohort. *medRxiv preprint*.  
  doi:10.1101/2025.02.26.25322940 · access: open (preprint) · [full text](https://www.medrxiv.org/content/10.1101/2025.02.26.25322940.full.pdf) · key `felker2025_allofus_genotype_first`  
  Model design for comparing literature spectra with a genotype-first cohort.
- **Connelly E, Laraway B, Mullen KR, Mungall CJ, Haendel MA, Hurwitz EG (2026).** A custom phenotypic profile for Fanconi anemia: addressing gaps in existing disease annotations. *medRxiv preprint*.  
  doi:10.64898/2026.02.10.26346018 · access: open (preprint) · [full text](https://www.medrxiv.org/content/10.64898/2026.02.10.26346018v1) · key `connelly2026_fanconi_annotations`  
  OMIM and Orphanet share few HPO terms for one disease: reference annotations are incomplete, so not every concordance gap is an extraction error.

### Memorization probes

- ★ **Shi W, Ajith A, Xia M, Huang Y, Liu D, Blevins T, Chen D, Zettlemoyer L (2024).** Detecting Pretraining Data from Large Language Models. *ICLR 2024*.  
  arXiv:2310.16789 · access: open (arXiv) · [full text](https://arxiv.org/pdf/2310.16789) · key `shi2024_mink_prob`  
  Min-K% Prob membership test. Needs token log-probabilities, so usable on the open-weight model but not on Claude: an asymmetry to design around.
- ★ **Duan M, Suri A, Mireshghallah N, Min S, Shi W, Zettlemoyer L, Tsvetkov Y, Choi Y, Evans D, Hajishirzi H (2024).** Do Membership Inference Attacks Work on Large Language Models?. *arXiv preprint*.  
  arXiv:2402.07841 · access: open (arXiv) · [full text](https://arxiv.org/pdf/2402.07841) · key `duan2024_mia_llm`  
  Caution: apparent membership signals often reflect date shift. The memorization probe must control for publication date.
- ★ **Golchin S, Surdeanu M (2024).** Time Travel in LLMs: Tracing Data Contamination in Large Language Models. *ICLR 2024*.  
  arXiv:2308.08493 · access: open (arXiv) · [full text](https://arxiv.org/pdf/2308.08493) · key `golchin2024_time_travel`  
  Black-box guided-completion probe; adaptable to Claude and the open-weight model identically.
- ★ **Roberts M, Thakur H, Herlihy C, White C, Dooley S (2024).** Data Contamination Through the Lens of Time. *ICLR 2024*.  
  arXiv:2310.10628 · access: open (arXiv) · [full text](https://arxiv.org/pdf/2310.10628) · key `roberts2024_lens_of_time`  
  Uses training cutoffs as a natural experiment: supports a pre- vs post-cutoff case-report split.
- ★ **Li A, Qian L, Du M, et al.; Lu Z, Xu H, Chen Q (2026).** Memorization in large language models in medicine: prevalence, characteristics, and implications. *Nat Commun (2026)*.  
  doi:10.1038/s41467-026-73779-6 · arXiv:2509.08604 · access: open (arXiv) · [full text](https://arxiv.org/pdf/2509.08604) · key `li2026_medical_memorization`  
  Main biomedical memorization study. *Note: DOI from the arXiv page; PMID not confirmed.*
- **Xu C, Guan S, Greene D, Kechadi M-T (2024).** Benchmark Data Contamination of Large Language Models: A Survey. *arXiv preprint*.  
  arXiv:2406.04244 · access: open (arXiv) · [full text](https://arxiv.org/pdf/2406.04244) · key `xu2024_contamination_survey`  
  Survey for justifying the choice of probe.
- **White C, Dooley S, Roberts M, Pal A, Feuer B, et al. (2025).** LiveBench: A Challenging, Contamination-Limited LLM Benchmark. *ICLR 2025*.  
  arXiv:2406.19314 · access: open (arXiv) · [full text](https://arxiv.org/pdf/2406.19314) · key `white2025_livebench`  
  Precedent for refreshed post-cutoff evaluation items.

### Grounding and verification

- ★ **Rashkin H, Nikolaev V, Lamm M, Aroyo L, Collins M, Das D, Petrov S, Tomar GS, Turc I, Reitter D (2023).** Measuring Attribution in Natural Language Generation Models. *Comput Linguist 49(4):777-840*.  
  doi:10.1162/coli_a_00486 · arXiv:2112.12870 · access: open (publisher) · [full text](https://aclanthology.org/2023.cl-4.2.pdf) · key `rashkin2023_ais`  
  AIS framework: a formal definition of 'supported by the cited span', the gatekeeper's audit criterion.
- ★ **Min S, Krishna K, Lyu X, Lewis M, Yih W, Koh PW, Iyyer M, Zettlemoyer L, Hajishirzi H (2023).** FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation. *EMNLP 2023*.  
  arXiv:2305.14251 · access: open (arXiv) · [full text](https://arxiv.org/pdf/2305.14251) · key `min2023_factscore`  
  Atomic-claim checking maps onto the 250-claim audit unit (one claim per extracted value).
- ★ **Gero Z, Singh C, Cheng H, Naumann T, Galley M, Gao J, Poon H (2023).** Self-Verification Improves Few-Shot Clinical Information Extraction. *arXiv preprint*.  
  arXiv:2306.00024 · access: open (arXiv) · [full text](https://arxiv.org/pdf/2306.00024) · key `gero2023_self_verification`  
  Closest prior design to the gatekeeper: the LLM cites evidence spans for its extractions, then verifies them.
- ★ **Huang J, Chen X, Mishra S, Zheng HS, Yu AW, Song X, Zhou D (2024).** Large Language Models Cannot Self-Correct Reasoning Yet. *ICLR 2024*.  
  arXiv:2310.01798 · access: open (arXiv) · [full text](https://arxiv.org/pdf/2310.01798) · key `huang2024_no_self_correct`  
  Counter-evidence: ungrounded self-correction can hurt. The gatekeeper should check against the verbatim span, and be calibrated against human labels.
- ★ **Wu K, Wu E, Wei K, Zhang A, Casasola A, Nguyen T, Riantawan S, Shi P, Ho D, Zou J (2025).** An automated framework for assessing how well LLMs cite relevant medical references. *Nat Commun 16:3615*.  
  PMID 40240349 · PMC12003634 · doi:10.1038/s41467-025-58551-6 · access: open (PMC) · [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC12003634) · key `wu2025_sourcecheckup`  
  Biomedical evidence that LLM citations often don't support the statements they're attached to.
- **Gao T, Yen H, Yu J, Chen D (2023).** Enabling Large Language Models to Generate Text with Citations. *EMNLP 2023*.  
  arXiv:2305.14627 · access: open (arXiv) · [full text](https://arxiv.org/pdf/2305.14627) · key `gao2023_alce`  
  Citation recall/precision metrics automatable with NLI or LLM judges.
- **Zheng L, Chiang W-L, Sheng Y, et al.; Gonzalez JE, Stoica I (2023).** Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. *NeurIPS 2023 Datasets and Benchmarks*.  
  doi:10.48550/arXiv.2306.05685 · arXiv:2306.05685 · access: open (arXiv) · [full text](https://arxiv.org/pdf/2306.05685) · key `zheng2023_llm_judge`  
  Documents self-enhancement bias: relevant when Claude audits Claude; consider cross-model or human-calibrated auditing.
- **Dhuliawala S, Komeili M, Xu J, Raileanu R, Li X, Celikyilmaz A, Weston J (2024).** Chain-of-Verification Reduces Hallucination in Large Language Models. *Findings of ACL 2024*.  
  arXiv:2309.11495 · access: open (arXiv) · [full text](https://arxiv.org/pdf/2309.11495) · key `dhuliawala2024_cove`  
  Verification-question pattern usable inside the gatekeeper.
- **Chung P, Swaminathan A, Goodell AJ, et al.; Aghaeepour N (2025).** VeriFact: Verifying Facts in LLM-Generated Clinical Text with Electronic Health Records. *arXiv preprint*.  
  arXiv:2501.16672 · access: open (arXiv) · [full text](https://arxiv.org/pdf/2501.16672) · key `chung2025_verifact`  
  Template for validating an LLM claim-checker against clinician labels.
- **Croxford E, Gao Y, First E, et al.; Patterson BW, Afshar M (2025).** Evaluating clinical AI summaries with large language models as judges. *npj Digit Med 8*.  
  doi:10.1038/s41746-025-02005-2 · access: open (publisher) · key `croxford2025_clinical_llm_judge`  
  Clinical LLM-as-judge validated against a human instrument. *Note: PMID not confirmed.*

### Audit statistics

- ★ **Hanley JA, et al. (1983).** If nothing goes wrong, is everything all right? Interpreting zero numerators. *JAMA 249(13):1743*.  
  doi:10.1001/jama.1983.03330370053031 · access: paywalled · key `hanley1983_zero_numerators`  
  Rule of three: 0 errors in 250 claims gives a 95% upper bound of ~1.2%. Sets what the 250-claim audit can and cannot certify. *Note: Co-author and PMID not confirmed.*
- ★ **Brown LD, Cai TT, DasGupta A (2001).** Interval Estimation for a Binomial Proportion. *Stat Sci 16(2)*.  
  doi:10.1214/ss/1009213286 · access: open (publisher) · [full text](https://projecteuclid.org/download/pdf_1/euclid.ss/1009213286) · key `brown2001_binomial_ci`  
  Use Wilson/Jeffreys intervals, not Wald, for the <2% unsupported-value rate. *Note: Pages not confirmed.*
- **Newman TB (1995).** If almost nothing goes wrong, is almost everything all right? Interpreting small numerators. *JAMA 274(13):1013*.  
  doi:10.1001/jama.1995.03530130019013 · access: paywalled · key `newman1995_small_numerators`  
  Extends the rule of three to small non-zero error counts.

### Open-weight vs proprietary

- ★ **Chen Q, Hu Y, Peng X, et al.; Lu Z, Xu H (2025).** Benchmarking large language models for biomedical natural language processing applications and recommendations. *Nat Commun 16:3280*.  
  PMID 40188094 · PMC11972378 · doi:10.1038/s41467-025-56989-2 · arXiv:2305.16326 · access: open (PMC) · [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC11972378) · key `chen2025_bionlp_benchmark`  
  Closed vs open models across 12 biomedical NLP benchmarks; key prior result for the head-to-head.
- ★ **Yin D, Leung MKS, Pun DWH, Chen FH, Kwon JY, Lin X, Ho JWK (2025).** Can large language models reliably extract human disease genes from full-text scientific literature?. *bioRxiv preprint*.  
  doi:10.1101/2025.07.27.667022 · access: open (preprint) · [full text](https://www.biorxiv.org/content/10.1101/2025.07.27.667022.full.pdf) · key `yin2025_llm_disease_genes`  
  Task closest to ours: GPT-4o vs Claude Opus 4 vs DeepSeek-V3 extracting gene/disease/phenotype from full text; disease and phenotype fields error-prone for all.
- **Dorfner FJ, Jurgensen L, Donle L, et al. (2024).** Comparing commercial and open-source large language models for labeling chest radiograph reports. *Radiology 313(1):e241139*.  
  doi:10.1148/radiol.241139 · arXiv:2402.12298 · access: open (arXiv) · [full text](https://arxiv.org/pdf/2402.12298) · key `dorfner2024_open_vs_commercial_radiology`  
  Gap closes under few-shot prompting with the same setup: supports the identical-scaffold rule. *Note: PMID not confirmed.*
- **Zhang G, Jin Q, Zhou Y, et al.; Lu Z, Weng C, Peng Y (2024).** Closing the gap between open source and commercial large language models for medical evidence summarization. *npj Digit Med 7*.  
  doi:10.1038/s41746-024-01239-w · access: open (publisher) · key `zhang2024_open_vs_commercial_summarization`  
  Fine-tuning narrows the gap; context if the open-weight arm is fine-tuned (it shouldn't be, under an identical scaffold). *Note: PMID not confirmed.*
- **Stachura D, Konieczna J, Nowak A (2025).** Are smaller open-weight LLMs closing the gap to proprietary models for biomedical question answering?. *arXiv preprint*.  
  arXiv:2509.18843 · access: open (arXiv) · [full text](https://arxiv.org/pdf/2509.18843) · key `stachura2025_open_weight_bioasq`  
  Recent QA comparison including Claude 3.5/3.7.

### Patient deduplication

- **Konig K, Pechmann A, Thiele S, et al. (2019).** De-duplicating patient records from three independent data sources reveals the incidence of rare neuromuscular disorders in Germany. *Orphanet J Rare Dis 14:152*.  
  doi:10.1186/s13023-019-1125-2 · access: open (publisher) · [full text](https://ojrd.biomedcentral.com/articles/10.1186/s13023-019-1125-2) · key `konig2019_registry_dedup`  
  Record-linkage deduplication across rare-disease sources (registries, not publications). *Note: PMID not confirmed.*
- **Shivakumar K, Abida H, Sun E, Ma O, Day J, Gupta L (2026).** Addressing cohort reliance in rare diseases literature: a scoping review of myositis research. *Rheumatology*.  
  PMID 41546378 · doi:10.1093/rheumatology/keag013 · access: unknown · key `shivakumar2026_cohort_reliance`  
  A few cohorts reused across many papers: supports explicit cross-paper patient deduplication. *Note: Year/volume not confirmed.*
