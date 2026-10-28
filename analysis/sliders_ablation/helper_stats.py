"""Per-helper token usage and wall-clock for the direct runs and the judge (SLIDERS ablation, D-42).

Reads the Claude Code helper transcripts of this session (one JSONL file per helper in the tasks
directory; they disappear with the container, so the derived table is committed) and keeps the
helpers whose first message names a direct-run output file (data/extracted/<d>/direct-<d>/records/<pmid>.json)
or a judge verdict file (adjudication/sliders_ablation/judge/verdicts/<chunk>.csv). Token weights are
those of analysis/cost/helper_tokens.py (cache write 5m 1.25, 1h 2, cache read 0.1, output 5); the
price is the six-disease run's $5.996 per weighted million (BUDGET.md), an estimate, not an invoice.

  python3 analysis/sliders_ablation/helper_stats.py <tasks_dir> > analysis/sliders_ablation/helper_stats.json
"""

import collections
import glob
import json
import os
import re
import sys
from datetime import datetime

W = dict(input_tokens=1, c5=1.25, c1h=2.0, cache_read_input_tokens=0.1, output_tokens=5)
RATE = 5.996  # $ per weighted million tokens
DIRECT = re.compile(r"Output file: /home/user/gp-rarelink/data/extracted/(\w+)/(direct-\w+)/records/(\d+)\.json")
JUDGE = re.compile(r"adjudication/sliders_ablation/judge/verdicts/(\w+)\.csv")


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def main():
    tasks = sys.argv[1]
    rows = []
    for f in sorted(glob.glob(os.path.join(tasks, "*.output"))):
        key, seen, c, t0, t1, model = None, set(), collections.Counter(), None, None, collections.Counter()
        for line in open(f, errors="replace"):
            try:
                d = json.loads(line)
            except Exception:  # noqa: BLE001
                continue
            if not isinstance(d, dict):
                continue
            if d.get("timestamp"):
                t = ts(d["timestamp"])
                t0, t1 = (t if t0 is None else min(t0, t)), (t if t1 is None else max(t1, t))
            m = d.get("message")
            if key is None and isinstance(m, dict) and m.get("role") == "user":
                txt = json.dumps(m.get("content"))
                o, j = DIRECT.search(txt), JUDGE.search(txt)
                if o:
                    key = {"kind": "direct", "disease": o.group(1), "run": o.group(2), "pmid": o.group(3)}
                elif j:
                    key = {"kind": "judge", "chunk": j.group(1), "disease": j.group(1).split("_")[0], "pmid": j.group(1).split("_")[1]}
                else:
                    key = {"kind": "other"}
            if isinstance(m, dict) and "usage" in m and d.get("requestId") not in seen:
                seen.add(d.get("requestId"))
                u = m["usage"]
                cc = u.get("cache_creation") or {}
                c["input_tokens"] += u.get("input_tokens", 0)
                c["c5"] += cc.get("ephemeral_5m_input_tokens", u.get("cache_creation_input_tokens", 0) if not cc else 0)
                c["c1h"] += cc.get("ephemeral_1h_input_tokens", 0)
                c["cache_read_input_tokens"] += u.get("cache_read_input_tokens", 0)
                c["output_tokens"] += u.get("output_tokens", 0)
                c["calls"] += 1
                if m.get("model"):
                    model[m["model"]] += 1
        if key and key["kind"] != "other":
            w = sum(c[x] * W[x] for x in W)
            rows.append({**key, "helper_file": os.path.basename(f), "calls": c["calls"], "weighted_tokens": round(w),
                         "cost_usd_estimate": round(w / 1e6 * RATE, 4), "wall_seconds": round(t1 - t0, 1) if t0 is not None else None,
                         "models_served": dict(model), **{k: c[k] for k in ("input_tokens", "c5", "c1h", "cache_read_input_tokens", "output_tokens")}})
    json.dump(sorted(rows, key=lambda r: (r["kind"], r.get("run", ""), r.get("pmid", ""), r["helper_file"])), sys.stdout, indent=1)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
