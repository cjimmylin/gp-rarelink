"""LangChain callback that feeds every Claude call's token usage into a RunManifest."""

from __future__ import annotations

from typing import Any

from langchain_core.callbacks.base import BaseCallbackHandler

from pipeline.common.cost import PriceTable
from pipeline.common.run_manifest import RunManifest


class UsageRecorder(BaseCallbackHandler):
    def __init__(self, manifest: RunManifest, table: PriceTable | None = None) -> None:
        self.manifest = manifest
        self.table = table or PriceTable.load()
        self.calls = 0
        self.unpriced = 0

    def on_llm_end(self, response, **kwargs: Any) -> None:
        for gen_list in getattr(response, "generations", []) or []:
            for gen in gen_list:
                msg = getattr(gen, "message", None)
                usage = getattr(msg, "usage_metadata", None) if msg is not None else None
                if not usage:
                    continue
                details = usage.get("input_token_details") or {}
                payload = {
                    "input_tokens": int(usage.get("input_tokens", 0) or 0),
                    "output_tokens": int(usage.get("output_tokens", 0) or 0),
                    "cache_read_input_tokens": int(details.get("cache_read", 0) or 0),
                    "cache_creation_input_tokens": int(details.get("cache_creation", 0) or 0),
                }
                # langchain-anthropic reports input_tokens as the total including cached tokens
                payload["input_tokens"] = max(0, payload["input_tokens"] - payload["cache_read_input_tokens"] - payload["cache_creation_input_tokens"])
                meta = getattr(msg, "response_metadata", {}) or {}
                served = meta.get("model_name") or meta.get("model")
                if served and served != self.manifest.model and not served.startswith(self.manifest.model):
                    self.manifest.record_fallback(document_id=str(kwargs.get("run_id", "")), original_model=self.manifest.model, served_model=served)
                try:
                    self.manifest.add_usage(payload, table=self.table)
                except Exception as exc:  # unverified price: count but never zero it silently
                    self.unpriced += 1
                    self.manifest.record_error(None, f"unpriced usage: {exc}")
                self.calls += 1
