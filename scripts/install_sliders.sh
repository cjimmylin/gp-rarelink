#!/usr/bin/env bash
# Install SLIDERS (stanford-oval/sliders) at a pinned commit with the
# GP-RareLink Anthropic-provider patch applied, into the project's uv venv.
#
# Usage: scripts/install_sliders.sh            (from the repo root)
#
# What it does:
#   1. clones the upstream repo at SLIDERS_COMMIT into .vendor/sliders (git-ignored)
#   2. applies pipeline/extract/sliders_adapter/0001-anthropic-provider.patch
#   3. installs the package without dependencies; the dependencies are the
#      `extract` group in pyproject.toml (everything SLIDERS needs except
#      docling, which is only used to convert PDFs and pulls in ~GBs of model
#      weights; we convert JATS XML to Markdown ourselves).
set -euo pipefail

SLIDERS_REPO="${SLIDERS_REPO:-https://github.com/stanford-oval/sliders}"
SLIDERS_COMMIT="${SLIDERS_COMMIT:-b66094d89b8068458c86a649668bed5fd0d6201c}"   # 2026-04-14 "initial commit"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENDOR="$ROOT/.vendor/sliders"
PATCH="$ROOT/pipeline/extract/sliders_adapter/0001-anthropic-provider.patch"

if [ ! -d "$VENDOR/.git" ]; then
  git clone -q "$SLIDERS_REPO" "$VENDOR"
fi
git -C "$VENDOR" fetch -q origin
git -C "$VENDOR" checkout -q --force "$SLIDERS_COMMIT"
git -C "$VENDOR" reset -q --hard "$SLIDERS_COMMIT"
git -C "$VENDOR" clean -qfd
git -C "$VENDOR" apply --check "$PATCH"
git -C "$VENDOR" apply "$PATCH"
echo "SLIDERS $SLIDERS_COMMIT + $(basename "$PATCH") checked out in $VENDOR"

cd "$ROOT"
uv sync --inexact --group extract --group dev   # --inexact keeps the optional pdf group (Docling) if installed
uv pip install --no-deps "$VENDOR"
uv run python -c "import sliders, sliders.llm.anthropic_client as a; print('sliders import OK; anthropic provider module:', a.__name__)"
