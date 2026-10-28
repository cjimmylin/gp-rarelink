"""Build GA4GH Phenopackets (schema v2) from one run (POC_DESIGN.md §3.7, Stage 4 step 4).

One phenopacket per merged identity (individuals_reconciled.csv, written by
pipeline.extract.reconcile under the current merge policy). Inputs, all under
data/extracted/<disease>/<run_id>/:
  per_paper/*.json         the extraction (values and verbatim spans)
  individuals_reconciled.csv  identity of every row
  hpo_bindings.csv         HPO term per phenotypic_features row (bind_ontologies)
  disease_bindings.csv     Mondo term per individual row
  variants_normalized.csv  VariantValidator results per distinct description
and configs/ha20_checklist_hpo.json for the checklist.

Content of each phenopacket:
  subject       identity id; sex if all member rows that state it agree;
                time at last encounter from the record-of-record row.
  phenotypicFeatures  every bound phenotypic_features row of every member
                row, de-duplicated by (HPO term, excluded), each with evidence
                (PMID and verbatim span). A term both observed and excluded
                across rows, or an excluded term that is an ancestor of an
                observed term (observing 'Lymphadenopathy' entails its
                ancestors), is dropped as excluded and listed in conflicts;
                the evidence tables keep both rows.
                Checklist rows add the mapped terms: excluded items add their
                excluded terms unless the term is observed; observed items add
                their observed term when the map gives one and no feature row
                already carries it.
  diseases      the bound Mondo disease, when the paper states one.
  interpretations  one per identity with target-gene variant rows. Variant
                expressions come from VariantValidator (MANE Select c. and p.,
                GRCh38 g., VCF record) when normalized; the original string is
                kept as the variation descriptor's description. The genomic
                interpretation is CAUSATIVE when an HA20 diagnosis is stated or
                the authors call the variant pathogenic or likely pathogenic;
                otherwise UNKNOWN_STATUS. The diagnosis disease is the stated
                HA20 term, else the gene-based group term.
  metaData      resources with the pinned ontology versions, the PMIDs.

Gatekeeper (POC_DESIGN.md §3.9): with --gatekeeper not_supported (the
default), every claim the Stage 5 gatekeeper did not judge supported
(partially_supported, unsupported, span_not_found; gatekeeper.csv from
pipeline.extract.claude_code.gatekeeper_merge) is left out: a phenotypic
feature or checklist row whose status or feature text is not supported; a
variant row whose original string or gene is not supported; and, singly, a
sex, age, onset, zygosity, pathogenicity statement or disease label that is
not supported. The evidence tables keep every row with its verdict.
--gatekeeper unsupported drops only unsupported and span_not_found (a
sensitivity build); --gatekeeper none ignores the verdicts.

Evidence code: ECO:0007539 'author statement supported from referenced clinical
study used in automatic assertion' (the values were extracted by a model; ECO
from the pinned snapshot). "Not reported" cannot be expressed in a phenopacket
except by omission; the evidence tables stay the primary three-state record.

Writes phenopackets/<identity>.json and phenopacket_build.json (counts and
conflicts) under the run directory.

  uv run python -m pipeline.extract.to_phenopackets --disease ha20 --run-id poc-ha20-run-2
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from google.protobuf.json_format import MessageToJson
from phenopackets import (
    Disease,
    Evidence,
    ExternalReference,
    GeneDescriptor,
    GenomicInterpretation,
    Interpretation,
    MetaData,
    OntologyClass,
    Phenopacket,
    PhenotypicFeature,
    Resource,
    Sex,
    TimeElement,
    VariantInterpretation,
    VariationDescriptor,
    VcfRecord,
)
from phenopackets import Expression as HgvsExpression

from pipeline.extract import ontologies
from pipeline.extract.normalize_variants import cdna_of, clean, transcript_of
from pipeline.extract.reconcile import is_gene, protein_key

MISSING = {None, "", "not reported", "unknown"}
ECO_ID = "ECO:0007539"
GENO = {"heterozygous": "GENO:0000135", "homozygous": "GENO:0000136", "hemizygous": "GENO:0000134", "mosaic": "GENO:0000964"}
HGNC = {"TNFAIP3": ("HGNC:11896", "TNFAIP3")}  # other genes come from configs/stage4/<disease>.json (D-40)
PATHOGENIC = re.compile(r"\b(likely\s+)?pathogenic\b", re.IGNORECASE)
NOT_PATHOGENIC = re.compile(r"\b(uncertain|VUS|benign|non-?pathogenic)\b", re.IGNORECASE)


def v(cell):
    return cell.get("value") if isinstance(cell, dict) else None  # a cell not in {value, span} shape reads as missing


def span_text(cell) -> str:
    s = (cell or {}).get("span")
    if isinstance(s, list):
        return " … ".join(str(x) for x in s)
    return str(s or "")


def evidence(pmid: str, span: str, eco: ontologies.Term) -> Evidence:
    return Evidence(evidence_code=OntologyClass(id=eco.id, label=eco.name),
                    reference=ExternalReference(id=f"PMID:{pmid}", description=span[:1000]))


def sex_of(values: list[str]) -> int:
    stated = {s.lower() for s in values if s not in MISSING}
    if stated == {"male"}:
        return Sex.MALE
    if stated == {"female"}:
        return Sex.FEMALE
    return Sex.UNKNOWN_SEX


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--gene", default="TNFAIP3")
    ap.add_argument("--group-mondo", default="MONDO:0100222")
    ap.add_argument("--checklist-map", default="configs/ha20_checklist_hpo.json")
    ap.add_argument("--created", default=date.today().isoformat())
    ap.add_argument("--gatekeeper", choices=("not_supported", "unsupported", "none"), default="not_supported")
    ap.add_argument("--out-name", default="phenopackets", help="output directory and summary name under the run directory")
    ap.add_argument("--gatekeeper-file", default="gatekeeper.csv", help="merged gatekeeper verdicts under the run directory (gatekeeper_v4.csv for pv1 runs)")
    ap.add_argument("--no-config", action="store_true", help="ignore configs/stage4/<disease>.json")
    args = ap.parse_args(argv)
    cfg_path = Path("configs/stage4") / f"{args.disease}.json"
    if cfg_path.exists() and not args.no_config:
        cfg = json.loads(cfg_path.read_text())
        args.gene, args.group_mondo, args.checklist_map = cfg["gene"], cfg["group_mondo"], cfg["checklist_map"]
        HGNC[cfg["gene"]] = (cfg["hgnc_id"], cfg["gene"])
    run_dir = Path("data/extracted") / args.disease / args.run_id
    drop = {"not_supported": {"partially_supported", "unsupported", "span_not_found"},
            "unsupported": {"unsupported", "span_not_found"}, "none": set()}[args.gatekeeper]
    bad: set[tuple[str, str, int, str]] = set()
    if drop:
        gk_path = run_dir / args.gatekeeper_file
        if not gk_path.exists():
            raise SystemExit(f"{gk_path} not found; run gatekeeper_merge or pass --gatekeeper none")
        for g in csv.DictReader(gk_path.open()):
            if g["verdict"] in ("not_judged_yet",):
                raise SystemExit("gatekeeper.csv has claims not judged yet; finish Stage 5 or pass --gatekeeper none")
            if g["verdict"] in drop:
                bad.add((g["pmid"], g["table"], int(g["row"]), g["field"]))

    def ok(pm: str, table: str, i, field: str) -> bool:
        return i is None or (pm, table, int(i), field) not in bad
    snap = ontologies.latest_dir()
    hp, mondo, eco_o, geno_o = (ontologies.load(n, snap) for n in ("hp", "mondo", "eco", "geno"))
    eco = eco_o.terms[ECO_ID]
    for g in GENO.values():
        assert g in geno_o.terms and not geno_o.terms[g].obsolete, g
    cmap = json.loads(Path(args.checklist_map).read_text())["items"]
    papers = {p.stem: json.loads(p.read_text()) for p in sorted((run_dir / "per_paper").glob("*.json"))}
    recon = list(csv.DictReader((run_dir / "individuals_reconciled.csv").open()))
    hpo = {(r["pmid"], int(r["row"])): r for r in csv.DictReader((run_dir / "hpo_bindings.csv").open())}
    dis = {(r["pmid"], r["individual_label_in_paper"]): r for r in csv.DictReader((run_dir / "disease_bindings.csv").open())}
    norm = {}
    norm_path = run_dir / "variants_normalized.csv"
    if norm_path.exists():
        norm = {r["variant_key"]: r for r in csv.DictReader(norm_path.open())}
    members = defaultdict(list)
    record = {}
    for r in recon:
        members[r["identity"]].append((r["pmid"], r["individual_label_in_paper"]))
        if r["record_of_record"] == "True":
            record[r["identity"]] = (r["pmid"], r["individual_label_in_paper"])

    def rows_for(table: str, pmid: str, label: str):
        for i, r in enumerate((papers[pmid].get("tables") or {}).get(table) or []):
            if str(v(r.get("individual_label_in_paper"))) == str(label):
                yield i, r

    out_dir = run_dir / args.out_name
    out_dir.mkdir(exist_ok=True)
    for old in out_dir.glob("*.json"):
        old.unlink()
    c, conflicts = Counter(), []
    for ident, mem in sorted(members.items()):
        pp = Phenopacket(id=f"{args.disease}-{args.run_id}-{ident}")
        pp.subject.id = ident
        inds = [(pm, *next(iter(rows_for("individuals", pm, lab)), (None, {}))) for pm, lab in mem]
        sexes = []
        for pm, i, r in inds:
            if ok(pm, "individuals", i, "sex"):
                sexes.append(str(v(r.get("sex"))))
            else:
                c["gk_dropped_sex"] += 1
        pp.subject.sex = sex_of(sexes)
        rec_pmid, rec_label = record.get(ident, mem[0])
        rec_i, rec_ind = next(iter(rows_for("individuals", rec_pmid, rec_label)), (None, {}))
        age = v(rec_ind.get("age_at_last_evaluation_iso8601"))
        if age not in MISSING and not ok(rec_pmid, "individuals", rec_i, "age_at_last_evaluation_iso8601"):
            c["gk_dropped_age"] += 1
            age = None
        if age not in MISSING and re.fullmatch(r"P(\d+(\.\d+)?[YMWD])+", str(age)):
            pp.subject.time_at_last_encounter.CopyFrom(TimeElement(age={"iso8601duration": str(age)}))
        # phenotypic features
        feats: dict[tuple[str, bool], PhenotypicFeature] = {}
        observed_terms = set()
        for pm, lab in mem:
            for i, r in rows_for("phenotypic_features", pm, lab):
                b = hpo.get((pm, i))
                if not b or not b["hpo_id"]:
                    c["feature_rows_unbound_skipped"] += 1
                    continue
                if not (ok(pm, "phenotypic_features", i, "status") and ok(pm, "phenotypic_features", i, "feature_text_as_stated")):
                    c["gk_dropped_feature_rows"] += 1
                    continue
                excl = v(r.get("status")) == "excluded"
                key = (b["hpo_id"], excl)
                if key not in feats:
                    f = PhenotypicFeature(type=OntologyClass(id=b["hpo_id"], label=hp.terms[b["hpo_id"]].name), excluded=excl)
                    onset = v(r.get("onset_iso8601"))
                    if onset not in MISSING and not ok(pm, "phenotypic_features", i, "onset_iso8601"):
                        c["gk_dropped_onset"] += 1
                        onset = None
                    if onset not in MISSING and re.fullmatch(r"P(\d+(\.\d+)?[YMWD])+", str(onset)):
                        f.onset.CopyFrom(TimeElement(age={"iso8601duration": str(onset)}))
                    feats[key] = f
                feats[key].evidence.append(evidence(pm, span_text(r.get("feature_text_as_stated")) or span_text(r.get("status")), eco))
                if not excl:
                    observed_terms.add(b["hpo_id"])
        for pm, lab in mem:
            for i, r in rows_for("phenotype_checklist", pm, lab):
                item, status = cmap.get(str(v(r.get("checklist_feature")))), v(r.get("status"))
                if not item or status not in ("observed", "excluded"):
                    continue
                if not ok(pm, "phenotype_checklist", i, "status"):
                    c["gk_dropped_checklist_rows"] += 1
                    continue
                if status == "observed" and item["observed"] and item["observed"] not in observed_terms:
                    key = (item["observed"], False)
                    if key not in feats:
                        feats[key] = PhenotypicFeature(type=OntologyClass(id=item["observed"], label=hp.terms[item["observed"]].name))
                        c["features_from_checklist_observed"] += 1
                    feats[key].evidence.append(evidence(pm, span_text(r.get("status")), eco))
                    observed_terms.add(item["observed"])
                elif status == "excluded":
                    for tid in item["excluded"]:
                        if tid in observed_terms:
                            continue
                        key = (tid, True)
                        if key not in feats:
                            feats[key] = PhenotypicFeature(type=OntologyClass(id=tid, label=hp.terms[tid].name), excluded=True)
                            c["features_from_checklist_excluded"] += 1
                        feats[key].evidence.append(evidence(pm, span_text(r.get("status")), eco))
        observed_closure = set(observed_terms)
        for tid in observed_terms:
            observed_closure |= hp.ancestors(tid)
        for (tid, excl) in list(feats):
            if excl and tid in observed_closure:
                kind = "same_term" if tid in observed_terms else "excluded_ancestor_of_observed"
                conflicts.append({"identity": ident, "hpo_id": tid, "label": hp.terms[tid].name, "kind": kind,
                                  "kept": "observed", "dropped": "excluded"})
                del feats[(tid, excl)]
        for f in sorted(feats.values(), key=lambda f: (f.excluded, f.type.id)):
            pp.phenotypic_features.append(f)
        c["features_observed"] += sum(1 for f in feats.values() if not f.excluded)
        c["features_excluded"] += sum(1 for f in feats.values() if f.excluded)
        # disease
        dis_ok = {}
        for (pm, i, _), (_, lab) in zip(inds, mem):
            if (pm, lab) in dis:
                if ok(pm, "individuals", i, "disease_label_as_stated"):
                    dis_ok[(pm, lab)] = dis[(pm, lab)]
                elif dis[(pm, lab)]["mondo_id"]:
                    c["gk_dropped_disease_label"] += 1
        d_terms = {d["mondo_id"] for d in dis_ok.values() if d["mondo_id"]}
        for mid in sorted(d_terms):
            pp.diseases.append(Disease(term=OntologyClass(id=mid, label=mondo.terms[mid].name)))
        ha20_stated = any(d.get("method") in ("ha20_label_rule", "label_rule") for d in dis_ok.values())
        # variants
        gis = []
        seen = set()
        for pm, lab in mem:
            for i, r in rows_for("variants", pm, lab):
                if not is_gene(v(r.get("gene_symbol_as_stated")), args.gene) or v(r.get("variant_original_string")) in MISSING:
                    continue
                if not (ok(pm, "variants", i, "variant_original_string") and ok(pm, "variants", i, "gene_symbol_as_stated")):
                    c["gk_dropped_variant_rows"] += 1
                    continue
                orig = str(v(r.get("variant_original_string")))
                (cdna, _legacy), tx = cdna_of(r), transcript_of(r)
                prot = protein_key(v(r.get("protein_hgvs_as_stated"))) or protein_key(orig)
                vkey = f"{tx or ''}|{cdna or ''}|{prot or ''}|{'' if (cdna or prot) else clean(orig).lower()}"
                n = norm.get(vkey, {})
                ident_key = n.get("vcf_grch38") or vkey
                if ident_key in seen:
                    continue
                seen.add(ident_key)
                vd = VariationDescriptor(id=f"{ident}-var{len(gis) + 1}", label=orig[:200], description=orig,
                                         gene_context=GeneDescriptor(value_id=HGNC[args.gene][0], symbol=HGNC[args.gene][1]))
                if n.get("mane_hgvs_transcript") or n.get("hgvs_transcript"):
                    vd.expressions.append(HgvsExpression(syntax="hgvs.c", value=n.get("mane_hgvs_transcript") or n["hgvs_transcript"]))
                if n.get("mane_hgvs_protein") or n.get("hgvs_protein"):
                    vd.expressions.append(HgvsExpression(syntax="hgvs.p", value=n.get("mane_hgvs_protein") or n["hgvs_protein"]))
                # D-43: when the paper's transcript is not the MANE Select (an alternative isoform), keep its validated
                # description too, so an exon-9b frameshift is not shown only as an intronic change on the MANE transcript
                if n.get("hgvs_transcript") and n.get("mane_hgvs_transcript") \
                        and n["hgvs_transcript"].split(":")[0].split(".")[0] != n["mane_hgvs_transcript"].split(":")[0].split(".")[0] \
                        and n["hgvs_transcript"].split(":", 1)[-1] != n["mane_hgvs_transcript"].split(":", 1)[-1]:
                    vd.expressions.append(HgvsExpression(syntax="hgvs.c", value=n["hgvs_transcript"]))
                    if n.get("hgvs_protein") and n["hgvs_protein"] != n.get("mane_hgvs_protein"):
                        vd.expressions.append(HgvsExpression(syntax="hgvs.p", value=n["hgvs_protein"]))
                if n.get("hgvs_genomic_grch38"):
                    vd.expressions.append(HgvsExpression(syntax="hgvs.g", value=n["hgvs_genomic_grch38"]))
                if n.get("vcf_grch38") and n["vcf_grch38"].count(":") == 3:
                    chrom, pos, ref, alt = n["vcf_grch38"].split(":")
                    vd.vcf_record.CopyFrom(VcfRecord(genome_assembly="GRCh38", chrom=chrom, pos=int(pos), ref=ref, alt=alt))
                zyg = str(v(r.get("zygosity")))
                if zyg in GENO and not ok(pm, "variants", i, "zygosity"):
                    c["gk_dropped_zygosity"] += 1
                    zyg = ""
                if zyg in GENO:
                    vd.allelic_state.CopyFrom(OntologyClass(id=GENO[zyg], label=geno_o.terms[GENO[zyg]].name))
                patho = str(v(r.get("pathogenicity_as_stated_by_authors")) or "")
                if patho and not ok(pm, "variants", i, "pathogenicity_as_stated_by_authors"):
                    c["gk_dropped_pathogenicity"] += 1
                    patho = ""
                causative = ha20_stated or (bool(PATHOGENIC.search(patho)) and not NOT_PATHOGENIC.search(patho))
                gi = GenomicInterpretation(subject_or_biosample_id=ident,
                                           interpretation_status=GenomicInterpretation.CAUSATIVE if causative else GenomicInterpretation.UNKNOWN_STATUS,
                                           variant_interpretation=VariantInterpretation(variation_descriptor=vd))
                gis.append(gi)
                c["variants_with_normalized_expression" if n.get("hgvs_genomic_grch38") else "variants_original_string_only"] += 1
        if gis:
            dx = next(iter(sorted(d_terms)), None) if ha20_stated else None
            dx = dx or args.group_mondo
            interp = Interpretation(id=f"{ident}-interpretation",
                                    progress_status=Interpretation.SOLVED if any(g.interpretation_status == GenomicInterpretation.CAUSATIVE for g in gis) else Interpretation.UNKNOWN_PROGRESS)
            interp.diagnosis.disease.CopyFrom(OntologyClass(id=dx, label=mondo.terms[dx].name))
            for g in gis:
                interp.diagnosis.genomic_interpretations.append(g)
            pp.interpretations.append(interp)
        # metadata
        md = MetaData(created_by="GP-RareLink pilot (Claude Code route, D-20)" if args.run_id.startswith("poc-") else "GP-RareLink pipeline-v1.0 (Claude Code route, D-20; Stage 4 settings D-40)",
                      phenopacket_schema_version="2.0")
        md.created.FromJsonString(f"{args.created}T00:00:00Z")
        for prefix, onto, name, url, iri in (("HP", hp, "Human Phenotype Ontology", "http://purl.obolibrary.org/obo/hp.owl", "http://purl.obolibrary.org/obo/HP_"),
                                             ("MONDO", mondo, "Mondo Disease Ontology", "http://purl.obolibrary.org/obo/mondo.obo", "http://purl.obolibrary.org/obo/MONDO_"),
                                             ("ECO", eco_o, "Evidence and Conclusion Ontology", "http://purl.obolibrary.org/obo/eco.owl", "http://purl.obolibrary.org/obo/ECO_"),
                                             ("GENO", geno_o, "Genotype Ontology", "http://purl.obolibrary.org/obo/geno.owl", "http://purl.obolibrary.org/obo/GENO_")):
            md.resources.append(Resource(id=prefix.lower(), name=name, url=url, version=onto.version, namespace_prefix=prefix, iri_prefix=iri))
        md.resources.append(Resource(id="hgnc", name="HUGO Gene Nomenclature Committee", url="https://www.genenames.org",
                                     version="not pinned", namespace_prefix="HGNC", iri_prefix="https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/"))
        for pm in sorted({pm for pm, _ in mem}):
            md.external_references.append(ExternalReference(id=f"PMID:{pm}"))
        pp.meta_data.CopyFrom(md)
        (out_dir / f"{ident}.json").write_text(MessageToJson(pp) + "\n")
        c["phenopackets"] += 1
        c["with_interpretation"] += bool(gis)
    summary = {"run_id": args.run_id, "created": args.created, "gatekeeper": args.gatekeeper,
               "gatekeeper_claims_dropped_available": len(bad), "counts": dict(sorted(c.items())),
               "observed_excluded_conflicts": len(conflicts), "conflicts": conflicts}
    name = "phenopacket_build.json" if args.out_name == "phenopackets" else f"{args.out_name}_build.json"
    (run_dir / name).write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: summary[k] for k in summary if k != "conflicts"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
