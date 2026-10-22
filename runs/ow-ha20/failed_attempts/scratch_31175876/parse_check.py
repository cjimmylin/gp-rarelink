import json
d = json.load(open("/tmp/openweight_scratch/ow-ha20/31175876/part1.json"))
print("part1 parses OK")
print({k: len(v) for k, v in d["tables"].items()})
