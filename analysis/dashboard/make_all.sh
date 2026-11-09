#!/usr/bin/env bash
# Rebuild the collaborator deck, the captioned video and the GitHub Pages dashboard from the committed results.
# Run from the repository root. Needs: uv project synced, node (pptxgenjs installed once with
# `cd analysis/dashboard/node && npm install`), LibreOffice (soffice), pdftoppm, ffmpeg, pandoc.
# The pptx skill's helper scripts (validate.py, soffice.py) are optional; set PPTX_SKILL_DIR to use them.
set -euo pipefail
cd "$(dirname "$0")/../.."

uv run python -m analysis.interim_paper.build_v3          # short paper (text + figures the deck reuses)
bash analysis/interim_paper/make_pdf_v3.sh
uv run python -m analysis.dashboard.export_deck_data      # numbers + narration -> deck_data.json
node analysis/dashboard/deck.js                           # -> reports/deck/gp_rarelink_overview.pptx
zip -dq reports/deck/gp_rarelink_overview.pptx '*/' 2>/dev/null || true
if [ -n "${PPTX_SKILL_DIR:-}" ]; then
  python3 "$PPTX_SKILL_DIR/scripts/office/validate.py" reports/deck/gp_rarelink_overview.pptx
  (cd reports/deck && python3 "$PPTX_SKILL_DIR/scripts/office/soffice.py" --headless --convert-to pdf gp_rarelink_overview.pptx)
else
  (cd reports/deck && soffice --headless --convert-to pdf gp_rarelink_overview.pptx)
fi
uv run python -m analysis.dashboard.build_video           # -> reports/video/*.mp4, .srt, narration_script.md
uv run python -m analysis.dashboard.build_site            # -> site/
echo "done: commit reports/deck reports/video site; on main the Pages workflow deploys site/"
