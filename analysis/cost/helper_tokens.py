"""Sum helper-agent token usage per disease and stage from the helper transcripts.
Weighted tokens use the usual ratios relative to base input: cache write 5m 1.25, 1h 2, cache read 0.1, output 5.
Usage: python3 helper_tokens.py <tasks_dir>"""
import json, re, sys, glob, os, collections
W = dict(input_tokens=1, c5=1.25, c1h=2.0, cache_read_input_tokens=0.1, output_tokens=5)
tot = collections.defaultdict(lambda: collections.Counter())
for f in glob.glob(os.path.join(sys.argv[1], "a*.output")):
    key = None; seen = set(); c = collections.Counter()
    for line in open(f, errors="replace"):
        try: d = json.loads(line)
        except Exception: continue
        if not isinstance(d, dict): continue
        m = d.get("message")
        if key is None and isinstance(m, dict) and m.get("role") == "user":
            txt = json.dumps(m.get("content"))
            o = re.search(r"Output file: /home/user/gp-rarelink/data/extracted/(\w+)/([\w-]+)/(per_paper|gatekeeper_v4|gatekeeper|hpo_model_bindings)/", txt)
            mp = re.search(r"map_prompt_(\w+)\.txt", txt)
            if o: key = (o.group(1), o.group(2), {"per_paper": "extract", "hpo_model_bindings": "hpo_binding"}.get(o.group(3), "gatekeeper"))
            elif mp: key = (mp.group(1), "stage4", "checklist_hpo_map")  # D-40 map drafting helpers
            elif "checklist" in txt.lower(): key = ("other", "checklist", "other")
            else: key = ("other", "other", "other")
        if isinstance(m, dict) and "usage" in m and d.get("requestId") not in seen:
            seen.add(d.get("requestId"))
            u = m["usage"]; cc = u.get("cache_creation") or {}
            c["input_tokens"] += u.get("input_tokens", 0)
            c["c5"] += cc.get("ephemeral_5m_input_tokens", u.get("cache_creation_input_tokens", 0) if not cc else 0)
            c["c1h"] += cc.get("ephemeral_1h_input_tokens", 0)
            c["cache_read_input_tokens"] += u.get("cache_read_input_tokens", 0)
            c["output_tokens"] += u.get("output_tokens", 0)
            c["calls"] += 1
    if key: tot[key].update(c); tot[key]["helpers"] += 1
for k in sorted(tot):
    c = tot[k]; w = sum(c[x] * W[x] for x in W)
    print(json.dumps({"disease": k[0], "run": k[1], "stage": k[2], "helpers": c["helpers"], "calls": c["calls"],
                      "weighted_mtok": round(w / 1e6, 2), "output_mtok": round(c["output_tokens"] / 1e6, 3)}))
