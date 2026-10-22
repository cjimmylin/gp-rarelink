import json

OUT = "/home/user/gp-rarelink/data/extracted/ha20/ow-ha20/per_paper/31175876.json"
SCHEMA = "/home/user/gp-rarelink/pipeline/extract/claude_code/schema_ha20_v5.json"

data = json.load(open(OUT))
schema = json.load(open(SCHEMA))

fields = {t["name"]: [f["name"] for f in t["fields"]] for t in schema["tables"]}

problems = []
for tname, rows in data["tables"].items():
    expected = fields[tname]
    for i, row in enumerate(rows):
        got = list(row.keys())
        if got != expected:
            problems.append((tname, i, "field mismatch", got, expected))

if problems:
    for p in problems:
        print(p)
else:
    print("All rows have exactly the schema fields, in order")
