# Isoform check for the extension genes (D-47 addendum §3, before Stage 4)

*2026-11-15. Data: `transcript_check_2026-11-14.json` (VariantValidator transcript list) and
`isoform_check_2026-11-15.json` (RefSeq GenBank exon structures, E-utilities, parsed with
`pipeline/extract/isoform_regions.parse_exons`; script in the session scratchpad, logic as in
`isoform_regions.py`).*

The addendum asks for every new gene to be checked for alternatively spliced coding exons before
Stage 4, with the check recorded. D-43's rule (`isoform_sensitive` in `configs/stage4/<d>.json`)
marks a description with no stated transcript as `isoform_ambiguous` when its position lies past
the point where the MANE and alternative exon structures diverge, unless the paper's own words
name the isoform.

| Gene | MANE Select | Alternative coding transcripts | Exon structure identical through | Decision |
|---|---|---|---|---|
| LCAT | NM_000229.2 | none | — | no block needed |
| SLC2A10 | NM_030777.4 | none | — | no block needed |
| GAMT | NM_000156.6 | NM_138924.3 (isoform b, retained intron at the 3′ end) | c.459 | no block (see below) |
| PSTPIP1 | NM_003978.5 | NM_001321135.2, NM_001411086.1 (3′ differences from c.742 and c.986); NM_001321136.2, NM_001321137.1 (different first exon, so different c. numbering throughout) | c.0 for two alternatives | no block (see below) |
| NOD2 | NM_001370466.1 | NM_001293557.2 (same protein); NM_022162.3 (legacy numbering, 27 residues longer at the N-terminus) | c.0 for NM_022162.3 | handled at Blau Stage 4 (registered rule vs revised rule, to be reported side by side) |

**Why no `isoform_sensitive` block for GAMT and PSTPIP1 (Claude's call, flagged for Jimmy):**

- In both corpora, every description that names a transcript names it explicitly. GAMT: 109
  descriptions on NM_000156, 4 on NM_138924 (isoform b) and 3 on Ensembl IDs. Normalization
  honours a stated transcript, so the isoform-b descriptions are projected correctly. PAPA: 13
  descriptions, all on NM_003978. No extracted string or span uses an isoform word.
- For PSTPIP1, two alternatives start from a different first exon, so their c. numbering differs
  everywhere. A D-43 block would therefore mark *every* PSTPIP1 description without a transcript
  as `isoform_ambiguous`, including the canonical E250K, A230T and E250Q. That would wrongly
  remove placeable variants, which is not the intent of D-43. That rule targets genes where the
  literature does use alternative terminal exons (LAMP2B, GFAP-epsilon) without saying so.
- VariantValidator still checks the reference base. A description written on an alternative
  transcript but read on MANE usually fails with a reference mismatch and does not produce a
  wrong genomic key silently.

If Jimmy prefers the literal reading of the addendum, the block can be added with
`isoform_regions.py` and the two runs re-normalized (a few minutes, about 160 cached
VariantValidator calls).
