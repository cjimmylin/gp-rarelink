"""Extraction side of the pipeline.

Ground-truth isolation (CLAUDE.md, INSTRUCTIONS.md §1.3, POC_DESIGN.md §3.2):
nothing in this package may read ``data/reference/``, import
``pipeline.harness`` or carry ClinVar/OMIM content. ``tests/test_isolation.py``
checks this statically; ``pipeline.extract.guard.assert_isolated`` checks it at
run time and must be called by every extraction entry point before any model
call.
"""
