"""Group the Stage 5 gatekeeper flags by reason (for the Stage 4-5 report).

Reads data/extracted/<disease>/<run_id>/gatekeeper_summary.json (written by
pipeline.extract.claude_code.gatekeeper_merge) and sorts every claim the
gatekeeper did not judge supported into one reason group. The grouping is a
keyword rule on the helper's free-text reason, applied in the order below;
the first rule that matches wins. It is approximate by construction: the
groups are for describing the flags, not for scoring, and every flag with its
reason stays listed in the summary file.

  age_or_timing     any flag on an *_iso8601 field (an age or onset recorded
                    differently from the span: a range as one value, age at
                    presentation as age at diagnosis); assigned by field first
  inverted_label    a normal finding or a negated phrase recorded as the
                    feature with status 'excluded' ("normal CRP" excluded);
                    the meaning is usually right, the label reads backwards
  wrong_person      the span is about another person
  contradicted      the paper's table or text says the opposite
  hedged            the span hedges ("suggesting", "usually", "suspected")
  silence           an absence or fact inferred from silence or from a list
                    that leaves the person out
  more_specific     the value is more specific than the span ("fever" ->
                    "recurrent fever", "cytopenia" -> "autoimmune cytopenia",
                    oral/genital ulcers split, a diagnosis read as a feature)
  detail_not_in_span  the value adds a true detail that sits outside the quote
  other

Writes analysis/poc/gatekeeper_flags_<run_id>.json and prints a table.

  uv run python analysis/poc/gatekeeper_flags.py --disease ha20 --run-id poc-ha20-run-2
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

RULES = [
    ("inverted_label", r"double negative|literally|invert|reads backwards|opposite of what|wrong way round|label (?:itself )?(?:contains|names|says)|names the normal|normal finding|finding was normal|fits only if read|read as (?:the )?abnormality|negated|negation in (?:the )?(?:label|context|feature)"),
    ("wrong_person", r"wrong person|refers to (?:the )?(?:mother|father|relatives|other)|not (?:this|the) (?:patient|proband|individual)|another (?:patient|person)|different (?:patient|group)"),
    ("contradicted", r"contradict|conflict|records? \w+ '?yes'?|marks? \w+ ['\"]?[–-]"),
    ("hedged", r"hedg|suggest|usually|suspected|probabl|possible"),
    ("silence", r"silence|never (?:tested|states|says)|not tested|absent from (?:the )?list|missing from|left out of|not named|without names|impl(?:y|ies|ied)"),
    ("detail_not_in_span", r"not in (?:the )?(?:cited |quoted )?spans?|outside|next sentence|adjacent|elsewhere|\badds?\b|not contain|omit|isn't in|is not in|aren't in|are not in|not stated in"),
    ("more_specific", r"recurrent|autoimmune|more specific|split|oral/genital|orogenital|initial diagnosis|inference|infer|extra step|mapped|counted as|reading .* as"),
]
AGE_FIELD = re.compile(r"_iso8601$")


def group(reason: str, field: str = "") -> str:
    r = reason.lower()
    if AGE_FIELD.search(field):
        return "age_or_timing"
    for name, pat in RULES:
        if re.search(pat, r):
            return name
    return "other"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--run-id", required=True)
    args = ap.parse_args(argv)
    s = json.loads((Path("data/extracted") / args.disease / args.run_id / "gatekeeper_summary.json").read_text())
    by_group, by_verdict, by_field = Counter(), defaultdict(Counter), defaultdict(Counter)
    examples = defaultdict(list)
    for f in s["flagged"]:
        g = group(f.get("reason") or "", f.get("field", ""))
        by_group[g] += 1
        by_verdict[f["verdict"]][g] += 1
        by_field[f"{f['table']}.{f['field']}"][g] += 1
        if len(examples[g]) < 5:
            examples[g].append({k: f[k] for k in ("claim_id", "pmid", "field", "verdict", "reason")})
    out = {"run_id": args.run_id, "flags": len(s["flagged"]), "rules": ["age_or_timing (by field)"] + [n for n, _ in RULES] + ["other"],
           "by_group": dict(by_group.most_common()), "by_verdict": {k: dict(v) for k, v in by_verdict.items()},
           "by_field": {k: dict(v) for k, v in sorted(by_field.items(), key=lambda kv: -sum(kv[1].values()))},
           "examples": examples}
    dest = Path("analysis/poc") / f"gatekeeper_flags_{args.run_id}.json"
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    for g, n in by_group.most_common():
        print(f"{g:20s} {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
