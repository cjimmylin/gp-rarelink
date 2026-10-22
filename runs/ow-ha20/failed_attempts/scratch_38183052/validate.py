import json, re, sys

PAPER = "/home/user/gp-rarelink/data/literature/ha20/fulltext_md/38183052.md"
OUT = "/home/user/gp-rarelink/data/extracted/ha20/ow-ha20/per_paper/38183052.json"
text = open(PAPER).read()
d = json.load(open(OUT))

missing = []


def check(v, path):
    if isinstance(v, dict):
        s = v.get("span")
        if s is None:
            return
        if isinstance(s, list):
            for x in s:
                if x not in text:
                    missing.append((path, x))
        else:
            if s not in text:
                missing.append((path, s))
    elif isinstance(v, list):
        for i, x in enumerate(v):
            check(x, path + "[%d]" % i)


for tname, rows in d["tables"].items():
    for i, row in enumerate(rows):
        for fname, cell in row.items():
            check(cell, "%s[%d].%s" % (tname, i, fname))

print("missing spans:", len(missing))
for p, s in missing[:40]:
    print(" ", p, "->", repr(s))

# schema field completeness
schema = json.load(open("/home/user/gp-rarelink/pipeline/extract/claude_code/schema_ha20_v5.json"))
for t in schema["tables"]:
    rows = d["tables"][t["name"]]
    fields = [f["name"] for f in t["fields"]]
    for i, row in enumerate(rows):
        if list(row.keys()) != fields:
            print("FIELD MISMATCH", t["name"], i, set(fields) ^ set(row.keys()))
        for f in t["fields"]:
            if f["required"] and row[f["name"]]["value"] in (None, "not reported"):
                print("EMPTY REQUIRED", t["name"], i, f["name"])
print("counts:", {k: len(v) for k, v in d["tables"].items()})
