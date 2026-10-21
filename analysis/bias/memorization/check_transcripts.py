"""Check memorization-probe helper transcripts for tool use (WS5, D-41).

A probe is valid only if its helper made no tool call except Write of its own response
file, and, for batches given by file, one Read of its own batch file. The harness's own hand-back call is ignored. Any other call
(another Read, Grep, Glob, Bash, web) invalidates that batch; it is discarded and reported.

  python3 -I analysis/bias/memorization/check_transcripts.py <tasks_dir>
writes analysis/bias/memorization/tool_check.json.
"""
import glob
import json
import os
import re
import sys

ROOT = "analysis/bias/memorization"
res = {}
for f in glob.glob(os.path.join(sys.argv[1], "a*.output")):
    batch, calls = None, []
    for line in open(f, errors="replace"):
        try:
            d = json.loads(line)
        except Exception:
            continue
        m = d.get("message") if isinstance(d, dict) else None
        if not isinstance(m, dict):
            continue
        if batch is None and m.get("role") == "user":
            hit = re.search(r"memorization/batches/(\w+)", json.dumps(m.get("content")))
            batch = hit.group(1) if hit else ""
        if m.get("role") == "assistant" and isinstance(m.get("content"), list):
            for c in m["content"]:
                if isinstance(c, dict) and c.get("type") == "tool_use":
                    calls.append({"name": c.get("name"), "path": (c.get("input") or {}).get("file_path", ""),
                                  "id": c.get("id")})
    if not batch:
        continue
    seen = {c["id"]: c for c in calls}
    calls = list(seen.values())
    ok_paths = {"Write": f"/home/user/gp-rarelink/{ROOT}/responses/{batch}.json",
                "Read": f"/home/user/gp-rarelink/{ROOT}/batches/{batch}.json"}
    calls = [c for c in calls if c["name"] != "SubagentHandback"]  # the harness's own reply call, not a lookup
    bad = [c for c in calls if c["name"] not in ok_paths or c["path"] != ok_paths[c["name"]]]
    reads = sum(c["name"] == "Read" for c in calls)
    res.setdefault(batch, []).append({"transcript": os.path.basename(f), "calls": [(c["name"], c["path"]) for c in calls],
                                      "valid": not bad and reads <= 1, "disallowed": [(c["name"], c["path"]) for c in bad]})
json.dump(res, open(f"{ROOT}/tool_check.json", "w"), indent=1)
for b, v in sorted(res.items()):
    print(b, [(x["valid"], len(x["calls"]), x["disallowed"]) for x in v])
