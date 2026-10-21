import json
src = open("/tmp/openweight_scratch/ow-ha20/29682366/build.py", encoding="utf-8").read()
ns = {}
exec(compile(src, "build.py", "exec"), ns)
paper = open("/home/user/gp-rarelink/data/literature/ha20/fulltext_md/29682366.md", encoding="utf-8").read()
d = json.load(open("/home/user/gp-rarelink/data/extracted/ha20/ow-ha20/per_paper/29682366.json", encoding="utf-8"))
print("REPORTS:", d["reports_individuals_with_tnfaip3_variant"])
bad = 0
def walk(o, path=""):
    global bad
    if isinstance(o, dict):
        if set(o.keys()) == {"value", "span"}:
            sp = o["span"]
            if sp is not None:
                for s in (sp if isinstance(sp, list) else [sp]):
                    if s not in paper:
                        bad += 1
                        print("MISSING:", path, repr(s[:100]))
            return
        for k, v in o.items():
            walk(v, path + "/" + k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, path + f"[{i}]")
walk(d)
print("missing spans:", bad)
print({k: len(v) for k, v in d["tables"].items()})
schema = json.load(open("/home/user/gp-rarelink/pipeline/extract/claude_code/schema_ha20_v5.json", encoding="utf-8"))
for t in schema["tables"]:
    names = [f["name"] for f in t["fields"]]
    for i, row in enumerate(d["tables"][t["name"]]):
        if list(row.keys()) != names:
            print("FIELD MISMATCH", t["name"], i, set(names) ^ set(row.keys()))
print("field check done")
