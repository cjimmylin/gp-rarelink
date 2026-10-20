"""Look up terms in the pinned HPO release (a tool for building checklist-to-HPO maps, D-40).

  uv run python -m pipeline.extract.hpo_lookup search "left ventricular hypertrophy"
      current terms whose name or synonym contains every word (case-folded), shortest names first
  uv run python -m pipeline.extract.hpo_lookup show HP:0001712
      name, EXACT synonyms, parents, children, obsolete flag
  uv run python -m pipeline.extract.hpo_lookup is-ancestor HP:0001626 HP:0001712
      whether the first term is an ancestor of the second

Reads only the pinned snapshot under data/ontologies (pipeline/extract/ontologies.py).
"""

from __future__ import annotations

import re
import sys

from pipeline.extract import ontologies

FOLD = re.compile(r"[^a-z0-9]+")


def fold(s: str) -> str:
    return FOLD.sub(" ", s.lower()).strip()


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print(__doc__)
        return 1
    hp = ontologies.load("hp", ontologies.latest_dir())
    cmd, rest = argv[0], argv[1:]
    if cmd == "search":
        words = fold(" ".join(rest)).split()
        hits = []
        for t in hp.terms.values():
            if t.obsolete:
                continue
            texts = [t.name] + [s for _, s in t.synonyms]
            for txt in texts:
                f = fold(txt).split()
                if all(w in f for w in words):
                    hits.append((len(t.name), t.id, t.name, txt if txt != t.name else ""))
                    break
        for _, tid, name, via in sorted(hits)[:25]:
            print(f"{tid}\t{name}" + (f"\t(synonym: {via})" if via else ""))
        print(f"[{len(hits)} hits; HPO {hp.version}]")
    elif cmd == "show":
        for tid in rest:
            t = hp.terms.get(tid)
            if not t:
                print(f"{tid}: not in HPO {hp.version}")
                continue
            kids = sorted(k.id for k in hp.terms.values() if tid in k.parents and not k.obsolete)
            print(f"{t.id}\t{t.name}\tobsolete={t.obsolete}")
            print("  EXACT:", "; ".join(s for sc, s in t.synonyms if sc == "EXACT") or "-")
            print("  parents:", "; ".join(f"{p} {hp.terms[p].name}" for p in t.parents if p in hp.terms))
            print("  children:", "; ".join(f"{k} {hp.terms[k].name}" for k in kids[:30]) or "-")
    elif cmd == "is-ancestor":
        a, b = rest[:2]
        print(a in hp.ancestors(b))
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
