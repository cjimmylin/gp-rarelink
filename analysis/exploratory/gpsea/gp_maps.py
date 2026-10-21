"""Exploratory genotype-phenotype maps with GPSEA (pre-registration §7.6; D-41). EXPLORATORY.

Runs in its own uv project (this folder), kept apart from the frozen pipeline environment,
because GPSEA 0.10 needs pandas < 3 while pipeline-v1.0 is locked to pandas 3.0.6.

Input: the gatekeeper-filtered pv1 phenopackets (data/extracted/<d>/pv1-<d>/phenopackets/).
HPO: the pinned release 2026-09-01 as hp.json (fetched 2026-10-21 from purl.obolibrary.org into
the reference root outside the repo; sha256 recorded in the output).

Variant effects: GPSEA normally asks Ensembl VEP, which this environment cannot reach. Instead
a local annotator reads each phenopacket's own VariantValidator output (its vcfRecord and the
hgvs.c / hgvs.p expressions on the gene's MANE transcript) and derives the sequence-ontology
effect from the HGVS: frameshift, stop gained, start lost, in-frame deletion or insertion,
synonymous, splice donor / acceptor (intronic +1/+2, -1/-2), other intronic, UTR, or missense.
No external call is made.

Analyses (one per disease; GPSEA's HPO-term analysis: Fisher exact test, IfHpoFilter, Benjamini-
Hochberg at 0.05; a feature that is not reported is not counted as excluded):
  dominant (ha20, axd, danon): monoallelic classifier, truncating vs missense; axd: hotspot
      residues R79, R88, R239 vs other missense instead; danon also by sex (the §7.6 question).
  recessive (ssadh, tangier, lad1): biallelic classifier, truncating vs other alleles.
"truncating" = frameshift, stop gained, start lost, splice donor or acceptor, transcript ablation.

  cd analysis/exploratory/gpsea && uv run python gp_maps.py --repo ../../.. \
      --hpo /home/user/gp-rarelink-reference/ontology/hp_2026-09-01.json
writes analysis/exploratory/gpsea/results/<disease>_<analysis>.csv and summary.json/.md.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import typing
from datetime import UTC, datetime
from pathlib import Path

import hpotk
from gpsea.analysis.clf import biallelic_classifier, monoallelic_classifier, prepare_classifiers_for_terms_of_interest, sex_classifier
from gpsea.analysis.pcats import configure_hpo_term_analysis
from gpsea.analysis.predicate import anyof, variant_effect, variant_key
from gpsea.model import TranscriptAnnotation, VariantCoordinates, VariantEffect
from gpsea.model.genome import GRCh38
from gpsea.preprocessing import (CohortCreator, FunctionalAnnotator, ImpreciseSvFunctionalAnnotator,
                                 PhenopacketPatientCreator, VariantCoordinateFinder, load_phenopacket_folder)
from gpsea.preprocessing._config import _setup_hpo_validator

DISEASES = {
    "ha20": "dominant", "axd": "dominant", "danon": "dominant",
    "ssadh": "recessive", "tangier": "recessive", "lad1": "recessive",
}
TRUNCATING = (VariantEffect.FRAMESHIFT_VARIANT, VariantEffect.STOP_GAINED, VariantEffect.START_LOST,
              VariantEffect.SPLICE_DONOR_VARIANT, VariantEffect.SPLICE_ACCEPTOR_VARIANT, VariantEffect.TRANSCRIPT_ABLATION)
AXD_HOTSPOTS = ("Arg79", "Arg88", "Arg239")


def effect_from_hgvs(c: str, p: str) -> VariantEffect:
    c = c.split(":")[-1]
    p = p.split(":")[-1]
    if re.search(r"fs", p):
        return VariantEffect.FRAMESHIFT_VARIANT
    if re.search(r"Met1\?|Met1[A-Z]", p):
        return VariantEffect.START_LOST
    if re.search(r"Ter\)?$|\*\)?$", p) and "ext" not in p:
        return VariantEffect.STOP_GAINED
    if "delins" in p:
        return VariantEffect.PROTEIN_ALTERING_VARIANT
    if re.search(r"del\)?$", p):
        return VariantEffect.INFRAME_DELETION
    if re.search(r"(ins|dup)", p):
        return VariantEffect.INFRAME_INSERTION
    if "=" in p:
        return VariantEffect.SYNONYMOUS_VARIANT
    m = re.match(r"c\.(-?\d+)([+-])(\d+)", c)
    if m:
        off = int(m.group(3))
        if off <= 2:
            return VariantEffect.SPLICE_DONOR_VARIANT if m.group(2) == "+" else VariantEffect.SPLICE_ACCEPTOR_VARIANT
        return VariantEffect.SPLICE_REGION_VARIANT if off <= 8 else VariantEffect.INTRON_VARIANT
    if c.startswith("c.-"):
        return VariantEffect.FIVE_PRIME_UTR_VARIANT
    if c.startswith("c.*"):
        return VariantEffect.THREE_PRIME_UTR_VARIANT
    if re.match(r"p\.\(?[A-Z][a-z]{2}\d+[A-Z][a-z]{2}\)?$", p):
        return VariantEffect.MISSENSE_VARIANT
    return VariantEffect.CODING_SEQUENCE_VARIANT


class LocalAnnotator(FunctionalAnnotator):
    """Annotates from the phenopackets' own VariantValidator output; no remote call."""

    def __init__(self, table: dict[tuple[str, int, str, str], tuple[str, str, str, str]]):
        self._t = table
        self.misses: list[str] = []

    def annotate(self, variant_coordinates: VariantCoordinates) -> typing.Sequence[TranscriptAnnotation]:
        vc = variant_coordinates
        key = (vc.chrom.replace("chr", ""), vc.start + 1, vc.ref, vc.alt)
        hit = self._t.get(key)
        if hit is None:
            self.misses.append(vc.variant_key)
            return ()
        gene, tx, c, p = hit
        return (TranscriptAnnotation(gene_symbol=gene, tx_id=tx, hgvs_cdna=c, is_preferred=True,
                                     variant_effects=(effect_from_hgvs(c, p),), affected_exons=None,
                                     protein_id=p.split(":")[0] if ":" in p else None, hgvsp=p or None,
                                     protein_effect_coordinates=None),)


class NoSv(ImpreciseSvFunctionalAnnotator):
    def annotate(self, item):  # imprecise SVs are not in these phenopackets
        return ()


class NoHgvs(VariantCoordinateFinder[str]):
    def find_coordinates(self, item: str):  # every variant here carries a vcfRecord
        return None


GPSEA_GENOTYPES = {"heterozygous", "compound heterozygous", "simple heterozygous", "homozygous",
                   "hemizygous", "hemizygous X-linked", "hemizygous Y-linked"}


def filtered_copy(folder: Path, dest: Path, mode: str, x_linked: bool) -> dict:
    """Copy the phenopackets for GPSEA, filling a missing allelic state by an ANALYSIS ASSUMPTION.

    The records themselves leave zygosity unset when the paper does not state it (three-state rule);
    GPSEA needs a genotype on every call. For this exploratory run only:
      dominant:  a call with no state is taken as heterozygous (X-linked: hemizygous in a male,
                 heterozygous in a female; left out when sex is unknown);
      recessive: a person with exactly two distinct calls, both without a state, is taken as
                 compound heterozygous; a single call without a state is left out (it could be
                 homozygous or have an unreported second allele).
    Calls in states GPSEA cannot represent (e.g. mosaic) are left out. Every choice is counted.
    """
    tally = {}

    def bump(k):
        tally[k] = tally.get(k, 0) + 1

    for f in sorted(folder.glob("*.json")):
        d = json.loads(f.read_text())
        sex = (d.get("subject") or {}).get("sex", "UNKNOWN_SEX")
        for interp in d.get("interpretations") or []:
            diag = interp.get("diagnosis") or {}
            gis = diag.get("genomicInterpretations") or []
            missing = [gi for gi in gis if not ((gi.get("variantInterpretation") or {}).get("variationDescriptor") or {}).get("allelicState")]
            keep = []
            for gi in gis:
                vd = (gi.get("variantInterpretation") or {}).get("variationDescriptor") or {}
                state = (vd.get("allelicState") or {}).get("label")
                if state in GPSEA_GENOTYPES:
                    keep.append(gi); bump(f"stated:{state}")
                    continue
                if state:
                    bump(f"left_out:{state}")
                    continue
                if mode == "dominant":
                    if x_linked and sex not in ("MALE", "FEMALE"):
                        bump("left_out:no_state_sex_unknown"); continue
                    lab, gid = (("hemizygous", "GENO:0000134") if x_linked and sex == "MALE" else ("heterozygous", "GENO:0000135"))
                    vd["allelicState"] = {"id": gid, "label": lab}
                    keep.append(gi); bump(f"assumed:{lab}")
                elif len(missing) == 2 and len({json.dumps(((m.get("variantInterpretation") or {}).get("variationDescriptor") or {}).get("vcfRecord"), sort_keys=True) for m in missing}) == 2:
                    vd["allelicState"] = {"id": "GENO:0000402", "label": "compound heterozygous"}
                    keep.append(gi); bump("assumed:compound heterozygous")
                else:
                    bump("left_out:no_state_recessive")
            if diag:
                diag["genomicInterpretations"] = keep
        (dest / f.name).write_text(json.dumps(d))
    return tally


def table_from_phenopackets(folder: Path) -> tuple[dict, str]:
    t, tx_seen = {}, set()
    for f in sorted(folder.glob("*.json")):
        d = json.loads(f.read_text())
        for interp in d.get("interpretations") or []:
            for gi in (interp.get("diagnosis") or {}).get("genomicInterpretations") or []:
                vd = (gi.get("variantInterpretation") or {}).get("variationDescriptor") or {}
                vcf = vd.get("vcfRecord")
                if not vcf:
                    continue
                ex = {e["syntax"]: e["value"] for e in vd.get("expressions") or []}
                c = ex.get("hgvs.c", "")
                tx = c.split(":")[0] if ":" in c else ""
                tx_seen.add(tx)
                t[(str(vcf["chrom"]).replace("chr", ""), int(vcf["pos"]), vcf["ref"], vcf["alt"])] = (
                    (vd.get("geneContext") or {}).get("symbol", ""), tx, c, ex.get("hgvs.p", ""))
    tx_seen.discard("")
    return t, sorted(tx_seen)[0] if tx_seen else ""


def rows_of(result, hpo, name: str) -> list[dict]:
    out = []
    pv = result.pvals
    cpv = result.corrected_pvals or [None] * len(pv)
    for i, (term, counts, n) in enumerate(zip(result.phenotypes, result.all_counts, result.n_usable)):
        if pv[i] is None or pv[i] != pv[i]:
            continue
        cols = {}
        for col in counts.columns:
            yes = int(counts.loc[[r for r in counts.index if str(r).lower() in ("yes", "true")], col].sum()) if len(counts.index) else 0
            tot = int(counts[col].sum())
            cols[str(col)] = f"{yes}/{tot}"
        out.append({"analysis": name, "hpo_id": term.value, "hpo_label": hpo.get_term_name(term) or "", "n_usable": int(n),
                    **{f"group_{k}": v for k, v in cols.items()}, "p": pv[i], "p_bh": cpv[i]})
    return sorted(out, key=lambda r: r["p"])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--hpo", required=True)
    a = ap.parse_args()
    repo = Path(a.repo).resolve()
    hpo = hpotk.load_minimal_ontology(a.hpo)
    out_dir = Path("results")
    out_dir.mkdir(exist_ok=True)
    summary = {"date": datetime.now(UTC).date().isoformat(), "hpo_file": a.hpo,
               "hpo_sha256": hashlib.sha256(Path(a.hpo).read_bytes()).hexdigest(), "hpo_version": hpo.version,
               "label": "EXPLORATORY (pre-registration §7.6)", "diseases": {}}
    analysis = configure_hpo_term_analysis(hpo)
    for d, mode in DISEASES.items():
        folder = repo / f"data/extracted/{d}/pv1-{d}/phenopackets"
        table, tx = table_from_phenopackets(folder)
        ann = LocalAnnotator(table)
        pc = PhenopacketPatientCreator(hpo=hpo, validator=_setup_hpo_validator(hpo, None), build=GRCh38,
                                       functional_annotator=ann, imprecise_sv_functional_annotator=NoSv(),
                                       hgvs_coordinate_finder=NoHgvs())
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            dropped = filtered_copy(folder, Path(tmp), mode, d == "danon")
            cohort, val = load_phenopacket_folder(tmp, CohortCreator(pc), validation_policy="permissive")
        pheno = prepare_classifiers_for_terms_of_interest(cohort, hpo)
        trunc = anyof([variant_effect(e, tx) for e in TRUNCATING])
        analyses = []
        if mode == "dominant" and d != "axd":
            analyses.append(("truncating_vs_missense", monoallelic_classifier(
                a_predicate=trunc, b_predicate=variant_effect(VariantEffect.MISSENSE_VARIANT, tx),
                a_label="truncating", b_label="missense")))
        if d == "axd":
            hot = [k for k, v in table.items() if any(h in v[3] for h in AXD_HOTSPOTS)]
            keys = [f"{c}_{pos}_{pos + len(ref) - 1}_{ref}_{alt}" for (c, pos, ref, alt) in hot]
            hot_pred = anyof([variant_key(k) for k in keys])
            other = variant_effect(VariantEffect.MISSENSE_VARIANT, tx) & ~hot_pred  # disjoint from the hotspot group
            analyses.append(("hotspot_R79_R88_R239_vs_other", monoallelic_classifier(
                a_predicate=hot_pred, b_predicate=other, a_label="hotspot", b_label="other missense")))
        if d == "danon":
            analyses.append(("sex", sex_classifier()))
        if mode == "recessive":
            analyses.append(("biallelic_truncating", biallelic_classifier(
                a_predicate=trunc, a_label="truncating", b_label="other", partitions=(0, 1, 2))))
        dres = {"patients": len(cohort), "transcript": tx, "annotator_misses": len(ann.misses),
                "validation_ok": val.is_ok(), "allelic_state_tally": dropped, "analyses": {}}
        for name, clf in analyses:
            try:
                res = analysis.compare_genotype_vs_phenotypes(cohort=cohort.all_patients, gt_clf=clf, pheno_clfs=pheno)
            except Exception as e:  # report and continue: exploratory
                dres["analyses"][name] = {"error": f"{type(e).__name__}: {e}"}
                continue
            rows = rows_of(res, hpo, name)
            import csv
            if rows:
                keys = sorted({k for r in rows for k in r}, key=lambda k: (k != "analysis", k != "hpo_id", k != "hpo_label", k))
                with (out_dir / f"{d}_{name}.csv").open("w", newline="") as fh:
                    w = csv.DictWriter(fh, fieldnames=keys)
                    w.writeheader(); w.writerows(rows)
            sig = [r for r in rows if r["p_bh"] is not None and r["p_bh"] < 0.05]
            dres["analyses"][name] = {"terms_tested": res.total_tests, "significant_bh_0.05": len(sig),
                                      "top": [{k: r[k] for k in r if k != "analysis"} for r in rows[:5]]}
        summary["diseases"][d] = dres
        print(d, json.dumps({k: v for k, v in dres.items() if k != "analyses"}),
              {n: (x.get("terms_tested"), x.get("significant_bh_0.05"), x.get("error")) for n, x in dres["analyses"].items()})
    Path("results/summary.json").write_text(json.dumps(summary, indent=1, default=str) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
