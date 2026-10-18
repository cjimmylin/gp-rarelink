"""Runtime ground-truth isolation guard for the extraction side.

Every extraction entry point calls ``assert_isolated()`` before its first
model call. It refuses to run when ground truth could be reachable:

* ``GP_RARELINK_REFERENCE_DIR`` is set in the environment (the harness uses it
  to find snapshots; the extraction process must not even know where they are);
* a readable reference directory exists under the working directory or the
  repository root (default name ``data/reference``).

The check is deliberately crude. The static test in tests/test_isolation.py
covers the code; this covers the process. Keep reference snapshots outside the
extraction container, or mounted so this process cannot read them.

This module is the one file under pipeline/extract allowed to name the
reference directory; tests/test_isolation.py exempts it explicitly.
"""

from __future__ import annotations

import os
from pathlib import Path

REFERENCE_ENV = "GP_RARELINK_REFERENCE_DIR"
REFERENCE_DIRNAME = ("data", "reference")


class IsolationError(RuntimeError):
    """Raised when the extraction process could reach ground truth."""


def _candidates(cwd: Path, repo_root: Path | None) -> list[Path]:
    roots = [cwd]
    if repo_root is not None:
        roots.append(repo_root)
    return [root.joinpath(*REFERENCE_DIRNAME) for root in roots]


def assert_isolated(cwd: Path | str | None = None, repo_root: Path | str | None = None, env: dict | None = None) -> None:
    env = os.environ if env is None else env
    if env.get(REFERENCE_ENV):
        raise IsolationError(
            f"{REFERENCE_ENV} is set; the extraction process must not know where ground truth lives. "
            "Unset it; only the concordance side may use it."
        )
    cwd = Path(cwd or Path.cwd()).resolve()
    repo_root = Path(repo_root).resolve() if repo_root else Path(__file__).resolve().parents[2]
    for candidate in _candidates(cwd, repo_root):
        if candidate.exists() and os.access(candidate, os.R_OK) and any(candidate.iterdir()):
            raise IsolationError(
                f"reference data is readable at {candidate}. Run extraction where ground truth is "
                "absent or unreadable (POC_DESIGN.md §3.2)."
            )
