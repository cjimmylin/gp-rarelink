"""Ground-truth isolation: pipeline/extract must never reach data/reference.

Static checks:
1. No module under pipeline/extract imports pipeline.harness (AST).
2. No code under pipeline/extract (comments and docstrings stripped) mentions
   the reference directory, the harness, ClinVar or OMIM. The runtime guard
   module is the single allowed exception for the directory name.
3. Nothing outside pipeline/harness and tests mentions the reference
   directory in code (so a helper in pipeline/common cannot become a side
   channel).

Runtime check:
4. pipeline.extract.guard.assert_isolated refuses to run when the reference
   env var is set or a populated reference directory is readable.
"""

from __future__ import annotations

import ast
import io
import tokenize
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
EXTRACT = REPO / "pipeline" / "extract"
HARNESS = REPO / "pipeline" / "harness"
COMMON = REPO / "pipeline" / "common"
GUARD = EXTRACT / "guard.py"

FORBIDDEN_IN_EXTRACT = ("data/reference", "pipeline.harness", "harness", "clinvar", "omim")
FORBIDDEN_OUTSIDE_HARNESS = ("data/reference",)


def _py_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.py") if ".venv" not in p.parts)


def _docstring_positions(tree: ast.AST) -> set[tuple[int, int]]:
    """(lineno, col) of every docstring constant so they can be dropped."""
    positions: set[tuple[int, int]] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
                positions.add((body[0].value.lineno, body[0].value.col_offset))
    return positions


def code_only(path: Path) -> str:
    """Source with comments and docstrings removed, lower-cased."""
    src = path.read_text()
    tree = ast.parse(src)
    doc_pos = _docstring_positions(tree)
    out: list[str] = []
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type == tokenize.COMMENT:
            continue
        if tok.type == tokenize.STRING and tok.start in doc_pos:
            continue
        out.append(tok.string)
    return " ".join(out).lower()


def test_extract_never_imports_harness():
    offenders = []
    for path in _py_files(EXTRACT):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            for name in names:
                if name == "pipeline.harness" or name.startswith("pipeline.harness.") or name.split(".")[0] == "harness":
                    offenders.append(f"{path.relative_to(REPO)}: imports {name}")
    assert not offenders, "\n".join(offenders)


def test_extract_code_has_no_ground_truth_tokens():
    offenders = []
    for path in _py_files(EXTRACT):
        text = code_only(path)
        for token in FORBIDDEN_IN_EXTRACT:
            if path == GUARD and token == "data/reference":
                continue  # the guard names the directory in order to refuse it
            if token in text:
                offenders.append(f"{path.relative_to(REPO)}: contains {token!r}")
    assert not offenders, "\n".join(offenders)


def test_reference_dir_named_only_in_harness_and_guard():
    offenders = []
    for path in _py_files(REPO / "pipeline"):
        if HARNESS in path.parents or path == GUARD:
            continue
        text = code_only(path)
        for token in FORBIDDEN_OUTSIDE_HARNESS:
            if token in text:
                offenders.append(f"{path.relative_to(REPO)}: contains {token!r}")
    assert not offenders, "\n".join(offenders)


def test_guard_rejects_env_var(tmp_path, monkeypatch):
    from pipeline.extract.guard import IsolationError, assert_isolated

    with pytest.raises(IsolationError):
        assert_isolated(cwd=tmp_path, repo_root=tmp_path, env={"GP_RARELINK_REFERENCE_DIR": "/somewhere"})


def test_guard_rejects_readable_reference_dir(tmp_path):
    from pipeline.extract.guard import IsolationError, assert_isolated

    ref = tmp_path / "data" / "reference"
    ref.mkdir(parents=True)
    (ref / "snapshot.txt").write_text("x")
    with pytest.raises(IsolationError):
        assert_isolated(cwd=tmp_path, repo_root=tmp_path, env={})


def test_guard_passes_when_isolated(tmp_path):
    from pipeline.extract.guard import assert_isolated

    assert_isolated(cwd=tmp_path, repo_root=tmp_path, env={})


def test_repo_checkout_is_isolated_right_now():
    """The repo as checked out must be a valid place to run extraction."""
    from pipeline.extract.guard import assert_isolated

    assert_isolated(cwd=REPO, repo_root=REPO, env={})
