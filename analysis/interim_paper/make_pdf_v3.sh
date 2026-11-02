#!/usr/bin/env bash
# Render reports/interim_paper_v3/interim_paper_v3.md to PDF: pandoc -> HTML, then headless Chromium -> PDF.
# No LaTeX engine is installed in the cloud container; the Playwright Chromium is. Run from the repository root.
set -euo pipefail
cd "$(dirname "$0")/../.."
OUT=reports/interim_paper_v3
CSS=analysis/interim_paper/paper.css
CHROME=$(find /opt/pw-browsers -maxdepth 3 -type f -name chrome | head -1)
if [ -z "$CHROME" ]; then echo "no Chromium found under /opt/pw-browsers" >&2; exit 1; fi
pandoc "$OUT/interim_paper_v3.md" --from gfm+pipe_tables --to html5 --standalone --metadata pagetitle="GP-RareLink in brief (interim, version 3)" \
  --css "$(pwd)/$CSS" --resource-path "$OUT" -o "$OUT/interim_paper_v3.html"
sed -i "s#src=\"figures/#src=\"file://$(pwd)/$OUT/figures/#g" "$OUT/interim_paper_v3.html"
"$CHROME" --headless=new --no-sandbox --disable-gpu --run-all-compositor-stages-before-draw --virtual-time-budget=10000 \
  --no-pdf-header-footer --print-to-pdf="$OUT/interim_paper_v3.pdf" "file://$(pwd)/$OUT/interim_paper_v3.html" 2>/dev/null
rm -f "$OUT/interim_paper_v3.html"
ls -la "$OUT/interim_paper_v3.pdf"
pdfinfo "$OUT/interim_paper_v3.pdf" 2>/dev/null | grep Pages || true
