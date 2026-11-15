# D-47 batch 2: hand-fetched free copies received 2026-11-15

Jimmy uploaded these to Claude Code session `ecstatic-ride` on 2026-11-15 as three zips. According to the bundle's README, they were downloaded on 2026-11-14 in Chrome driven by Claude computer use, from the links in the D-47 hand-fetch tracker (the 183 papers the 2026-11-14 headless run did not save). No CAPTCHA was solved, and pages that needed an account, subscription or payment were skipped.

- `hand_fetch_report_2026-11-14.csv`: the bundle's own report for all 183 papers. 72 were saved (68 PDFs and 4 PMC pages saved as `.mhtml`). The other 111 were not: 36 needed access, 35 were not retrieved, 22 stopped at a security check and 18 had broken links or were unavailable.
- `hand_fetched_2026-11-14.csv`: one row per saved file, with identifiers only: sha256, page count, route (`PMC` 69, `publisher free` 2, `repository` 1), URL and fetch date. No paper text.
- `verify_hand_fetched.py`: the check that produced the manifest. Run it as `python3 -I verify_hand_fetched.py <unpacked dir> <status_2026-11-14.csv> <repo root> <out csv>`. `status_2026-11-14.csv` is on the D-47 batch-1 branch.

Result of the check on 2026-11-15:
- 72 of 72 files are present and valid. Every PDF's page count matches the report.
- Every file name matches its disease and PMID, and every title matched (each file had at least 80% of its title words in its first three pages).
- None of the 72 was saved in batch 1. All 72 are among the 183 that batch 1 did not fetch (48 stopped at a challenge page, 21 had no PDF found, 2 had no URL, 1 had an HTTP error).
- None has full text in the registered corpus: 67 are listed as `paywalled` (meaning no PMC copy at the time) and 5 as `not_found`.

By disease: AxD 31, SSADH 13, Tangier 13, LAD-I 7, Danon 5, HA20 3.

The files themselves are in the git-ignored `data/literature/free_copies/hand_fetched_2026-11-14/` and disappear with the container. The durable copies are Jimmy's originals and the D-47 Drive folder.

**Update, 2026-11-15.** Jimmy asked for the batch to be processed at once, and D-47 was amended the same day (`DECISIONS.md`): batch 2 ran as `pv1a2-<d>`, and his instruction is recorded as accepting the computer-use fetch route (the question this note first raised). The four `.mhtml` pages were printed to PDF in headless Chromium (JavaScript off, offline) before conversion; the sha256 values in the manifest are of the files as received, not of those printed PDFs. Results: `reports/addendum_d47_batch2_findings.md`.
