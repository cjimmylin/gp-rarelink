"""Concordance harness. The only package allowed to read ``data/reference/``.

It may import ``pipeline.common`` and read tagged extraction outputs under
``data/extracted/``. It must never be imported by ``pipeline.extract``.
"""
