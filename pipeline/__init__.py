"""GP-RareLink pipeline.

Subpackages:
- ``pipeline.common``  shared, data-free helpers (run manifests, cost).
- ``pipeline.extract`` extraction side. Must never read ``data/reference/`` or
  import ``pipeline.harness``. See POC_DESIGN.md §3.2.
- ``pipeline.harness`` concordance side. The only code allowed to read
  ``data/reference/``.
"""
