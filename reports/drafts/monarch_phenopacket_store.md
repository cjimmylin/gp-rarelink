# Message to the Monarch / phenopacket-store maintainers: draft for Jimmy to send

*Drafted 2026-10-19 by Claude. Status: **draft, not sent.** Claude does not contact anyone (`CLAUDE.md`); Jimmy sends it, from his own address, through whichever channel the maintainers prefer. Fill the items marked [fill]. Figures come from the pilot report (`reports/poc_report.md`, 2026-10-19). Do not use the grant's "408 cohorts" figure, which has no published source (D-14).*

**To:** [fill: phenopacket-store maintainers or Monarch contact; GitHub issue or email]
**Subject:** Contributing literature-derived phenopackets for six rare diseases (GP-RareLink)

Dear phenopacket-store team,

I lead GP-RareLink, a six-month project at the Rare Genomics Institute with Prof. Monica Lam's lab at Stanford (OVAL), funded by Anthropic's AI for Science program. We build GA4GH Phenopackets (v2) from published case reports, with a PMID and a verbatim quote behind every value. We measure their accuracy against ClinVar and OMIM, and against a human audit.

The six diseases are Alexander disease (*GFAP*), leukocyte adhesion deficiency I (*ITGB2*), A20 haploinsufficiency (*TNFAIP3*), SSADH deficiency (*ALDH5A1*), Danon disease (*LAMP2*) and Tangier disease (*ABCA1*). As far as we can see, none of them is in phenopacket-store yet [fill: confirm against the current repository].

We have finished a pilot on A20 haploinsufficiency:
- 749 phenopackets from 85 open-access papers, all schema-valid;
- HPO terms from release 2026-09-01; HA20 bound to MONDO:0800045;
- variants normalized with VariantValidator.

Our human audit is honest about the limits. In a 50-claim audit, 6% of values were not supported by their quote. We are fixing the two error classes it found before the main run. The pilot report is public [fill: link to the repository or report].

We would like to offer the six cohorts to phenopacket-store once they have passed our audit, and to build them so that they fit your standards from the start. Could you tell us:
1. what you require for a cohort to be accepted (curation standards, required fields, validation tools, review process);
2. whether model-assisted curation is acceptable when every record carries a PMID and verbatim evidence and a human audit is reported alongside;
3. how you prefer to receive provenance for each feature and variant (we keep the PMID, section and quote);
4. how you handle the same patient reported in several papers (we deduplicate on citation evidence and record the evidence for each merge);
5. any licensing or attribution terms for contributed cohorts.

We are happy to adapt our output to your conventions, and to share the pipeline as open source.

With thanks,
Jimmy Lin, MD, PhD, MHS
Founder and CEO, Rare Genomics Institute
jimmy.lin@raregenomics.org
