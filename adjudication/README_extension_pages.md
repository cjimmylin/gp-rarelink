# Review pages for the extension to the reserve diseases (built on demand)

These pages are not committed. The rating and triage pages embed passages of the papers, and the repository is public (D-46). They were published as private Artifacts on 2026-11-15, after Jimmy lifted the no-publishing rule for them ("Ok to publish"; links in `DECISIONS.md`, D-53 entry). The extension is decision D-52 and its later calls D-53; the extension session recorded them as D-47 and D-48, and files it wrote keep those numbers. To build them, run these commands from the repository root, with the corpus present under `data/literature/<disease>/fulltext_md/`. Each page gets its own store key, so extension ratings never mix with the registered six's.

O1X unsupported-value audit (250 claims, seed 47250). There are two raters; a third page for disagreements comes later:

```bash
uv run python adjudication/o1_audit/make_rating_page.py --rater A --sample-dir adjudication/o1x_audit --store-prefix o1x-audit --out <scratch>/o1x_rater_A.html
```

```bash
uv run python adjudication/o1_audit/make_rating_page.py --rater B --sample-dir adjudication/o1x_audit --store-prefix o1x-audit --out <scratch>/o1x_rater_B.html
```

O2 discordance triage (all 48 misses, seed 72650):

```bash
python3 -I adjudication/o2_triage/make_triage_page.py --sample-dir adjudication/o2_triage_ext --store-key o2x-triage-v1 --out <scratch>/o2x_triage.html
```

The triage page finds passages by MANE numbers. Most Blau papers use legacy NM_022162 numbers, 27 residues higher, so most Blau items show no passage. The extracted proteins shown on each item make the offset visible.

O3 gap adjudication (45 candidates, 2 withdrawn). Make one page per adjudicator:

```bash
python3 -I adjudication/o3_gaps/make_adjudication_page.py --adjudicator A --root adjudication/o3_gaps_ext --store-prefix o3x-adjudication --exclude-withdrawn --out <scratch>/o3x_adjudicator_A.html
```

Collect the ratings afterwards in the same way as for the registered six: `adjudication/o1_audit/collect_o1.py` for the audit, and an `ArtifactData list` export of each store.
