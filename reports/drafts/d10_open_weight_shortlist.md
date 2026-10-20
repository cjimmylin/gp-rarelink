# D-10 shortlist: the open-weight model for the comparison (O5)

*Drafted 2026-10-20 by Claude for Jimmy's pick (D-10, decision log 2026-10-20). Model facts were read on 2026-10-20 from each model's Hugging Face card and `config.json` (licence tag, parameter count from the safetensors index, `max_position_embeddings`). Prices come from OpenRouter's public model list, read 2026-10-20 02:59 UTC. Prices change often and differ by host: check the host's own rate card before any run. Rankings in blog roundups disagree, so none are used here.*

## What the comparison needs

1. **Open weights under an open licence**, so the result is reproducible and the weights can be pinned (MIT or Apache 2.0 preferred).
2. **Long context.** Converted papers run to 62,000 tokens (Danon corpus maximum, `fulltext_md` metadata). The agentic route also re-reads context, so 128K is the floor.
3. **Tool use.** Under D-17, Claude runs as Claude Code helper agents that read files and write CSVs with tools. The open-weight model needs an agent harness that gives it the same instructions, files and tools.
4. **Cost and hosting** within what we can fund. The grant's $2,000 line covers Claude credits only, so open-weight compute is unbudgeted (pre-registration §7.5).

## Candidates

| Model | Licence | Size | Context | OpenRouter price, $/M tokens in / out | Notes |
|---|---|---|---|---|---|
| **DeepSeek-V4.1-Flash** (2026-09-10) | MIT | 763B MoE (384 experts) | 1,048,576 | 0.05 / 0.15 (batch). The non-batch row reads 0.035 / 0.011, which looks like a cache rate, so check it | Cheapest of the strong models. A newer checkpoint (-1017) exists; pin one |
| **GLM-5.2** (2026-06-16) | MIT | 753B MoE (256 experts) | 1,048,576 | 0.62 / 2.42 | Strong. Its successor GLM-5.3 is *not* MIT (licence "other"); only GLM-5.3-Flash is MIT |
| **GLM-5.3-Flash** (2026-08-25) | MIT | 321B MoE | 1,048,576 | 0.15 / 0.50 (batch 0.05 / 0.18) | Smaller and cheaper |
| **Qwen3.8-27B** (2026-08-05) | Apache 2.0 | 28B dense | 262,144 | 0.24 / 2.20 | Runs on one large GPU. Qwen's flagship (3.8-2.4T) is not Apache |
| **gpt-oss-120b** (2025-08-04) | Apache 2.0 | 117B MoE | 131,072 | 0.15 / 0.60 (batch 0.03 / 0.14) | Oldest and smallest context; fits one 80 GB GPU, so it is the easiest to self-host and pin |
| Kimi K3 (2026-06-13) | "other" (custom) | 2.78T MoE | 1,048,576 | listed inconsistently | **Not recommended:** custom licence, and the price rows look inconsistent |

**Rough compute cost** for HA20 plus one other disease (about 170 papers), at 300K–1M input and 30K–60K output tokens per paper (a guess at agentic re-reading, not a measurement):
- DeepSeek-V4.1-Flash batch: $3–10;
- GLM-5.3-Flash: $10–31;
- gpt-oss-120b: $11–32;
- Qwen3.8-27B: $23–63;
- GLM-5.2: $44–130.

The gatekeeper pass would add about as much again.

## Recommendation

**DeepSeek-V4.1-Flash, pinned to the 2026-09-10 checkpoint, run through a hosted API, with gpt-oss-120b as a self-hosted reproducibility check if time allows.**
- **Why:** it meets all four needs, under the most permissive licence, at the lowest cost. Compute is small enough to come from contingency (about $50 with a margin for re-runs) without touching the $2,000 Claude line.
- **The real cost is the harness, not the tokens.** Claude runs inside Claude Code; the open-weight model cannot. An identical scaffold therefore needs one of two things:
  - **(a)** an open-source agent harness that calls an OpenAI-compatible endpoint, given the same instruction files, the same Markdown inputs and the same file tools. The write-up states the remaining differences (system prompt, tool wording).
  - **(b)** both models run through the pipeline's own non-agentic SLIDERS adapter (`pipeline/extract/sliders_adapter/`), with Claude called by API for this arm only. That is the cleanest comparison, but it needs API billing for Claude (D-17 put the main route on Claude Code).

  I recommend (a). It keeps Claude's arm identical to the main study, and (b) would compare a route we don't otherwise use.
- **Hosting:** a hosted endpoint serves the published weights, but quantization and serving settings vary by host. The run records the host, model ID, checkpoint and date, and the pre-registration says so.

## For Jimmy to decide

1. **The model:** DeepSeek-V4.1-Flash (recommended), GLM-5.2, or another from the table.
2. **The second disease** beside HA20: I suggest SSADH deficiency (37 eligible open papers, mid-sized).
3. **The compute budget:** about $50 from contingency, logged in `BUDGET.md` with the host's invoice.
4. **Harness (a) or (b).**

Nothing here has been run, and no account has been opened with any host.
