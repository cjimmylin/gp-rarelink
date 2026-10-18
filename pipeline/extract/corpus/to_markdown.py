"""Stage 1, step 3: convert fetched full text to Markdown for SLIDERS.

  .nxml  -> jats_to_markdown (tables kept)
  .pdf   -> Docling (same converter SLIDERS uses); requires `uv pip install docling`

Writes data/literature/<disease>/fulltext_md/<pmid>.md and <pmid>.meta.json with
the source format, table/figure counts, and a token count. The token count is
exact (Anthropic count_tokens) when ANTHROPIC_API_KEY is set, else an estimate
flagged as such; never silently mix the two.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path

from pipeline.extract.corpus.jats_to_markdown import jats_to_markdown
from pipeline.extract.guard import assert_isolated

COUNT_MODEL = "claude-opus-5-5"


def count_tokens(text: str) -> tuple[int, str]:
    if os.getenv("ANTHROPIC_API_KEY"):
        from anthropic import Anthropic

        client = Anthropic()
        n = client.messages.count_tokens(model=COUNT_MODEL, messages=[{"role": "user", "content": text}])
        return int(n.input_tokens), f"anthropic.count_tokens:{COUNT_MODEL}"
    return len(text) // 4, "estimate:chars/4 (no API key)"


def convert_pdf(path: Path) -> str:
    from docling.document_converter import DocumentConverter  # optional dependency

    return DocumentConverter().convert(str(path)).document.export_to_markdown()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--pmid", nargs="*", default=None, help="subset of PMIDs")
    ap.add_argument("--no-count", action="store_true", help="skip token counting")
    args = ap.parse_args(argv)
    assert_isolated()

    base = Path("data/literature") / args.disease
    src = base / "fulltext"
    dst = base / "fulltext_md"
    dst.mkdir(parents=True, exist_ok=True)
    manifest_rows = {r["pmid"]: r for r in csv.DictReader((base / "manifest.csv").open(newline=""))}
    done = 0
    for f in sorted(src.glob("*")):
        if f.suffix not in (".nxml", ".pdf"):
            continue
        pmid = f.stem
        if args.pmid and pmid not in args.pmid:
            continue
        meta = {"pmid": pmid, "source_file": f.name, "source_format": f.suffix[1:]}
        if f.suffix == ".nxml":
            art = jats_to_markdown(f.read_bytes())
            if not art.pmid:
                art.pmid = pmid
            row = manifest_rows.get(pmid, {})
            art.title = art.title or row.get("title", "")
            md = art.to_markdown()
            meta.update(n_tables=art.n_tables, n_figures=art.n_figures, pmcid=art.pmcid, doi=art.doi)
        else:
            md = f"PMID: {pmid}\nTitle: {manifest_rows.get(pmid, {}).get('title', '')}\n\n" + convert_pdf(f)
        if not args.no_count:
            n, method = count_tokens(md)
            meta.update(tokens=n, token_count_method=method)
        (dst / f"{pmid}.md").write_text(md)
        (dst / f"{pmid}.meta.json").write_text(json.dumps(meta, indent=2) + "\n")
        done += 1
        print(f"{pmid}: {meta.get('tokens', '?')} tokens, {meta.get('n_tables', '?')} tables")
    print(f"converted {done} documents into {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
