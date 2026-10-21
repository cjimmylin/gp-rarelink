"""Per-paper cost and wall-clock of the Claude extraction helpers (D-10 comparison, §7.5).

Reads the Claude Code helper transcripts (one JSONL file per helper, `a*.output` in the session's
tasks directory; they disappear with the container, so the derived table is committed) and keeps
the extraction helpers of the given runs. For each helper: the paper (from the output path in its
first message), API calls, token counts, weighted tokens (same weights as
analysis/cost/helper_tokens.py) and wall-clock seconds from its first to its last timestamp.
A paper extracted by more than one helper (a repair) gets one row per helper.

  python3 analysis/openweight/claude_helper_stats.py <tasks_dir> pv1-ha20 pv1-ssadh \
      > analysis/openweight/claude_helper_stats.json
"""
import collections
import glob
import json
import os
import re
import sys
from datetime import datetime

W = dict(input_tokens=1, c5=1.25, c1h=2.0, cache_read_input_tokens=0.1, output_tokens=5)


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def main():
    tasks, runs = sys.argv[1], set(sys.argv[2:])
    rows = []
    for f in sorted(glob.glob(os.path.join(tasks, "a*.output"))):
        key, seen, c, t0, t1 = None, set(), collections.Counter(), None, None
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
                o = re.search(r"Output file: /home/user/gp-rarelink/data/extracted/(\w+)/([\w-]+)/per_paper/(\d+)\.json",
                              json.dumps(m.get("content")))
                key = (o.group(1), o.group(2), o.group(3)) if o else ("", "", "")
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
        if key and key[1] in runs:
            rows.append({"disease": key[0], "run": key[1], "pmid": key[2], "helper_file": os.path.basename(f),
                         "calls": c["calls"], "weighted_tokens": round(sum(c[x] * W[x] for x in W)),
                         "wall_seconds": round(t1 - t0, 1) if t0 is not None else None,
                         **{k: c[k] for k in ("input_tokens", "c5", "c1h", "cache_read_input_tokens", "output_tokens")}})
    json.dump(sorted(rows, key=lambda r: (r["run"], r["pmid"], r["helper_file"])), sys.stdout, indent=1)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
