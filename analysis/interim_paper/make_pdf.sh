#!/usr/bin/env bash
# Render reports/interim_paper/{interim_paper,supplement}.md to one PDF: pandoc -> HTML, then headless Chromium -> PDF.
# No LaTeX engine is installed in the cloud container; the Playwright Chromium is. Run from the repository root.
set -euo pipefail
cd "$(dirname "$0")/../.."
OUT=reports/interim_paper
CSS=analysis/interim_paper/paper.css
CHROME=$(find /opt/pw-browsers -maxdepth 3 -type f -name chrome | head -1)
if [ -z "$CHROME" ]; then echo "no Chromium found under /opt/pw-browsers" >&2; exit 1; fi
TMP=$(mktemp -d)
{ cat "$OUT/interim_paper.md"; printf '\n\n<div class="page-break"></div>\n\n'; cat "$OUT/supplement.md"; } > "$TMP/combined.md"
pandoc "$TMP/combined.md" --from gfm+pipe_tables --to html5 --standalone --metadata title="GP-RareLink interim report" \
  --css "$(pwd)/$CSS" --resource-path "$OUT" -o "$OUT/interim_paper.html"
# make image paths absolute for Chromium
sed -i "s#src=\"figures/#src=\"file://$(pwd)/$OUT/figures/#g" "$OUT/interim_paper.html"
"$CHROME" --headless=new --no-sandbox --disable-gpu --run-all-compositor-stages-before-draw --virtual-time-budget=10000 \
  --no-pdf-header-footer --print-to-pdf="$OUT/interim_paper.pdf" "file://$(pwd)/$OUT/interim_paper.html" 2>/dev/null
rm -f "$OUT/interim_paper.html"
rm -rf "$TMP"
ls -la "$OUT/interim_paper.pdf"
