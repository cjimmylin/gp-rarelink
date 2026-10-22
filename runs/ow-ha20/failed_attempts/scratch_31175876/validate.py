import json, sys

OUT = "/home/user/gp-rarelink/data/extracted/ha20/ow-ha20/per_paper/31175876.json"
PAPER = "/home/user/gp-rarelink/data/literature/ha20/fulltext_md/31175876.md"

with open(OUT) as fh:
    data = json.load(fh)

paper = open(PAPER).read()

missing = []
def walk(node, path):
    if isinstance(node, dict):
        if set(node.keys()) == {"value", "span"}:
            sp = node["span"]
            if sp is None:
                return
            spans = sp if isinstance(sp, list) else [sp]
            for s in spans:
                if s not in paper:
                    missing.append((path, s))
            return
        for k, v in node.items():
            walk(v, path + "/" + k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, path + "[%d]" % i)

walk(data, "")

if missing:
    print("SPANS NOT FOUND:", len(missing))
    for p, s in missing:
        print("  ", p, "->", repr(s[:160]))
else:
    print("All spans verbatim OK")

# field completeness
import collections
for tname, rows in data["tables"].items():
    print(tname, "rows:", len(rows))
