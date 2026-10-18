"""Run manifests: every model-calling script writes runs/<run_id>/manifest.json.

The manifest is what makes a number re-runnable (INSTRUCTIONS.md §3): commit
hash, dirty-tree flag, model and effort, hashes of schema/prompts/input
manifest, token usage, cost, fallbacks and errors. See POC_DESIGN.md §3.11.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pipeline.common.cost import USAGE_KEYS, PriceTable

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNS_DIR = REPO_ROOT / "runs"


def sha256_file(path: Path | str) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def git_commit(repo: Path = REPO_ROOT) -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()


def git_dirty(repo: Path = REPO_ROOT) -> bool:
    out = subprocess.check_output(["git", "status", "--porcelain"], cwd=repo, text=True)
    return bool(out.strip())


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class RunManifest:
    run_id: str
    stage: int
    model: str
    effort: str | None = None
    provider: str = "anthropic"
    started: str = field(default_factory=_now)
    finished: str | None = None
    git_commit: str = field(default_factory=git_commit)
    dirty_tree: bool = field(default_factory=git_dirty)
    sliders_version: str | None = None
    schema_sha256: str | None = None
    prompt_sha256: dict[str, str] = field(default_factory=dict)
    input_manifest_sha256: str | None = None
    n_documents: int = 0
    corpus_tokens: int = 0
    n_requests: int = 0
    usage: dict[str, int] = field(default_factory=lambda: {k: 0 for k in USAGE_KEYS})
    cost_usd: float = 0.0
    price_table: str | None = None
    cache_hit_rate: float | None = None
    fallbacks: list[dict[str, Any]] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)
    notes: dict[str, Any] = field(default_factory=dict)

    # ---- bookkeeping -----------------------------------------------------
    def __post_init__(self) -> None:
        if self.price_table is None:
            table = PriceTable.load()
            rel = table.path.relative_to(REPO_ROOT)
            self.price_table = f"{rel}@{self.git_commit[:12]} (read_on {table.read_on}, verified_on {table.verified_on})"

    def add_usage(self, usage: dict[str, int], table: PriceTable | None = None) -> float:
        table = table or PriceTable.load()
        cost = table.cost_usd(self.model, usage)
        for key in USAGE_KEYS:
            self.usage[key] += int(usage.get(key, 0) or 0)
        self.n_requests += 1
        self.cost_usd = round(self.cost_usd + cost, 6)
        read = self.usage["cache_read_input_tokens"]
        total = read + self.usage["input_tokens"] + self.usage["cache_creation_input_tokens"]
        self.cache_hit_rate = None if total == 0 else round(read / total, 4)
        return cost

    def record_fallback(self, document_id: str, original_model: str, served_model: str, reason: str | None = None) -> None:
        self.fallbacks.append({"document_id": document_id, "original_model": original_model, "served_model": served_model, "reason": reason, "at": _now()})

    def record_error(self, document_id: str | None, error: str) -> None:
        self.errors.append({"document_id": document_id, "error": error, "at": _now()})

    def finish(self) -> None:
        self.finished = _now()

    # ---- persistence -----------------------------------------------------
    @property
    def path(self) -> Path:
        return RUNS_DIR / self.run_id / "manifest.json"

    def write(self, path: Path | None = None) -> Path:
        path = path or self.path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), indent=2, sort_keys=True) + "\n")
        return path

    @classmethod
    def read(cls, path: Path | str) -> "RunManifest":
        data = json.loads(Path(path).read_text())
        return cls(**data)
