"""Helper-agent token use for the Majeed work of 2026-11-15, by stage, from this session's helper transcripts.

Same weights as analysis/cost/helper_tokens.py (input 1, cache write 5m 1.25, 1h 2, cache read 0.1,
output 5) and the project's helper rate of $5.996 per weighted million tokens for Opus helpers.
Sonnet helpers are priced at half that rate (the Sonnet/Opus input-price ratio in configs/prices.yaml).
Stages are recognised from each helper's first message. Estimates, not billing figures.

  python3 analysis/majeed/helper_costs.py <tasks_dir> > analysis/majeed/helper_costs.json
"""
import collections, glob, json, os, re, sys

W = dict(input_tokens=1, c5=1.25, c1h=2.0, cache_read_input_tokens=0.1, output_tokens=5)
RATE = 5.996
STAGES = [("screen_ta", r"screening/launch_v[12]|screen one batch of PubMed|Title/abstract screening"),
          ("screen_fulltext", r"screening_fulltext/(launch_v1|work/nopmid)|screening full-text"),
          ("checklist", r"checklist_from_review_v1"), ("hpo_map", r"checklist_hpo_map_v1"),
          ("extract", r"extract_v6_majeed"), ("gatekeeper", r"gatekeeper_launch_v[12]"),
          ("hpo_binding", r"hpo_binding_v1"), ("runbook_explore", r"command-level runbook")]
tot = collections.defaultdict(collections.Counter)
for f in glob.glob(os.path.join(sys.argv[1], "a*.output")):
    stage, model, seen, c = None, None, set(), collections.Counter()
    for line in open(f, errors="replace"):
        try:
            d = json.loads(line)
        except Exception:
            continue
        m = d.get("message") if isinstance(d, dict) else None
        if stage is None and isinstance(m, dict) and m.get("role") == "user":
            txt = json.dumps(m.get("content"))
            stage = next((s for s, pat in STAGES if re.search(pat, txt)), "other")
        if isinstance(m, dict) and "usage" in m and d.get("requestId") not in seen:
            seen.add(d.get("requestId"))
            model = model or m.get("model", "")
            u = m["usage"]; cc = u.get("cache_creation") or {}
            c["input_tokens"] += u.get("input_tokens", 0)
            c["c5"] += cc.get("ephemeral_5m_input_tokens", u.get("cache_creation_input_tokens", 0) if not cc else 0)
            c["c1h"] += cc.get("ephemeral_1h_input_tokens", 0)
            c["cache_read_input_tokens"] += u.get("cache_read_input_tokens", 0)
            c["output_tokens"] += u.get("output_tokens", 0)
    if stage:
        key = (stage, "sonnet" if "sonnet" in (model or "") else "opus")
        tot[key].update(c); tot[key]["helpers"] += 1
out, total = [], 0.0
for (stage, model), c in sorted(tot.items()):
    w = sum(c[x] * W[x] for x in W) / 1e6
    usd = w * RATE * (0.5 if model == "sonnet" else 1)
    total += usd
    out.append({"stage": stage, "model": model, "helpers": c["helpers"], "weighted_mtok": round(w, 2), "usd_estimate": round(usd, 2)})
print(json.dumps({"rate_usd_per_weighted_mtok_opus": RATE, "stages": out, "total_usd_estimate": round(total, 2)}, indent=1))
