"""Build the O2 discordance-triage page (pre-registration §7.2.6; D-11, D-35).

For each of the 50 sampled misses (sample.csv, seed 72650) the page shows the ClinVar record
the paper is cited for, what the pv1 extraction found in that paper, and passages of the paper
(found by script) that mention the variant's cDNA position or protein residue. That way the
rater can see quickly whether the paper describes the variant at all. The rater picks one of
the five registered categories and may add a note. Ratings save to the page's store
(collection `triage`, one document per row number).

Search used for the passages (no model): the cDNA position from the ClinVar name (e.g. "468"
next to "c." or a base change), and the protein residue in one- and three-letter forms (e.g.
"L157", "Leu157"). Up to four passages of about 300 characters each.

  python3 -I adjudication/o2_triage/make_triage_page.py --out <scratch>/o2_triage.html
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
AA = {"Ala": "A", "Arg": "R", "Asn": "N", "Asp": "D", "Cys": "C", "Gln": "Q", "Glu": "E", "Gly": "G", "His": "H", "Ile": "I",
      "Leu": "L", "Lys": "K", "Met": "M", "Phe": "F", "Pro": "P", "Ser": "S", "Thr": "T", "Trp": "W", "Tyr": "Y", "Val": "V", "Ter": "*"}
CATS = [["1", "Extraction error", "the paper describes this variant and the extraction missed or misread it"],
        ["2", "Normalization error", "the extraction has it, but normalization placed it on a different allele"],
        ["3", "Error in the paper", "a typo, legacy numbering or another transcript in the paper"],
        ["4", "Reference error or ambiguity", "the ClinVar record itself is wrong or ambiguous"],
        ["5", "Citation not about this variant", "the paper does not describe this variant (ClinVar cites it for something else)"]]


def passages(md: str, name: str, limit: int = 4) -> list[str]:
    pats = []
    m = re.search(r"c\.(\d+)", name)
    if m:
        pos = m.group(1)
        pats.append(re.compile(rf"(c\.\s?{pos}(?!\d)|(?<!\d){pos}\s?[ACGT]\s?[>→]|(?<!\d){pos}(del|dup|ins|_))", re.I))
    p = re.search(r"p\.\(?([A-Z][a-z]{2})(\d+)", name)
    if p:
        three, num = p.group(1), p.group(2)
        one = AA.get(three, "")
        pats.append(re.compile(rf"(?<![A-Za-z]){three}{num}(?!\d)|(?<![A-Za-z]){re.escape(one)}{num}(?!\d)"))
    out, seen = [], set()
    for rx in pats:
        for mm in rx.finditer(md):
            s = max(0, mm.start() - 140)
            key = s // 200
            if key in seen:
                continue
            seen.add(key)
            out.append(md[s:mm.end() + 160].replace("\n", " "))
            if len(out) >= limit:
                return out
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    rows = list(csv.DictReader((HERE / "sample.csv").open()))
    items = []
    for r in rows:
        md_path = ROOT / f"data/literature/{r['disease']}/fulltext_md/{r['pmid']}.md"
        md = md_path.read_text() if md_path.exists() else ""
        items.append({"n": r["n"], "disease": r["disease"], "pmid": r["pmid"], "vid": r["clinvar_variation_id"], "name": r["clinvar_name"],
                      "vcf": r["clinvar_vcf"], "alleles": r["extracted_alleles_in_pmid"], "proteins": r["extracted_proteins_in_pmid"],
                      "passages": passages(md, r["clinvar_name"]), "paper_found": bool(md)})
    style = (ROOT / "adjudication/o3_gaps/adjudication_page_template.html").read_text()
    style = style[style.index("<style>"):style.index("</style>") + 8]
    data = json.dumps({"items": items, "cats": CATS, "store_key": "o2-triage-v1"}, ensure_ascii=False).replace("</", "<\\/")
    page = TEMPLATE.replace("/*__STYLE__*/", style).replace("/*__DATA__*/null", data)
    Path(a.out).write_text(page)
    print(json.dumps({"items": len(items), "with_passages": sum(bool(i["passages"]) for i in items),
                      "papers_missing": sum(not i["paper_found"] for i in items), "bytes": len(page.encode())}))
    return 0


TEMPLATE = """<title>O2 Miss Triage</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Serif:ital,wght@0,400;0,500;1,400&display=swap">
/*__STYLE__*/
<style>
main .wrap.single { grid-template-columns: minmax(0, 1fr); max-width: 920px; }
.cats { display: grid; gap: 6px; }
.cats label { display: grid; grid-template-columns: 22px minmax(0, 1fr); gap: 8px; align-items: start; font-size: 14px; cursor: pointer; }
.cats small { color: var(--muted); display: block; }
.chips a { color: var(--accent); font-size: 13px; }
.passage { font-family: var(--font-data); font-size: 12.5px; background: var(--paper); border: 1px solid var(--rule); border-radius: 6px; padding: 8px 10px; overflow-wrap: anywhere; }
</style>
<header class="top"><div class="wrap">
  <div class="title-row"><h1>O2 miss triage</h1><span class="save-state" id="save-state">Connecting to the store…</span></div>
  <div class="tools"><span id="count">0 of 50 triaged</span><span class="spacer"></span><button class="plain" id="copy-btn" type="button">Copy all as text</button></div>
  <div class="meter" aria-hidden="true"><i id="meter"></i></div>
</div></header>
<main><div class="wrap single">
  <div class="panel"><div class="intro">
    <p><b>Each card is a variant ClinVar cites this paper for, which our extraction did not find in that paper.</b> Decide why, using the paper (PMID link) and the passages found by script. Pick one category; add a note if useful.</p>
    <p>Every miss already counts against us in the main figure. This sorting is a secondary breakdown (pre-registration §7.2.6).</p>
  </div></div>
  <textarea id="copy-box" class="copy-box" hidden readonly aria-label="Triage as text"></textarea>
  <div id="list" style="display:grid; gap:14px"></div>
</div></main>
<script>
const DATA = /*__DATA__*/null;
const state = {}; let db = null, store = "none";
const $ = (id) => document.getElementById(id);
const el = (tag, attrs = {}, ...kids) => { const n = document.createElement(tag); for (const [k, v] of Object.entries(attrs)) { if (k === "class") n.className = v; else if (k === "text") n.textContent = v; else n.setAttribute(k, v); } for (const c of kids) if (c != null) n.append(c); return n; };
function card(it) {
  const p = el("div", { class: "panel", id: "t-" + it.n });
  p.append(el("div", { class: "chips" }, el("span", { class: "chip", text: "#" + it.n }), el("span", { class: "chip", text: it.disease }),
    el("a", { href: "https://pubmed.ncbi.nlm.nih.gov/" + it.pmid + "/", target: "_blank", rel: "noopener", text: "PMID " + it.pmid }),
    el("a", { href: "https://www.ncbi.nlm.nih.gov/clinvar/variation/" + it.vid + "/", target: "_blank", rel: "noopener", text: "ClinVar " + it.vid })));
  p.append(el("p", { class: "variant-title", text: it.name }), el("div", { class: "variant-sub", text: "GRCh38 " + (it.vcf || "(no VCF allele)") }));
  const f = el("dl", { class: "facts" });
  f.append(el("dt", { text: "We extracted from this paper (alleles)" }), el("dd", { text: it.alleles || "none" }));
  f.append(el("dt", { text: "…and proteins" }), el("dd", { text: it.proteins || "none" }));
  p.append(f);
  p.append(el("h2", { text: it.passages.length ? "Where the paper mentions this position (script search)" : "The script found no mention of this position or residue in the paper text" }));
  it.passages.forEach((s) => p.append(el("div", { class: "passage", text: "…" + s + "…" })));
  const cats = el("div", { class: "cats", role: "radiogroup", "aria-label": "Category" });
  for (const [v, l, h] of DATA.cats) {
    const id = "c-" + it.n + "-" + v;
    const r = el("input", { type: "radio", name: "cat-" + it.n, id, value: v });
    r.addEventListener("change", () => { state[it.n] = { ...(state[it.n] || {}), category: v }; save(it.n); count(); });
    cats.append(el("label", { for: id }, r, el("span", {}, v + ". " + l, el("small", { text: h }))));
  }
  const note = el("textarea", { class: "note", id: "note-" + it.n, placeholder: "Note (optional)", "aria-label": "Note" });
  let t = null; note.addEventListener("input", () => { clearTimeout(t); t = setTimeout(() => { state[it.n] = { ...(state[it.n] || {}), note: note.value }; save(it.n); }, 800); });
  p.append(el("div", { class: "subhead", text: "Category" }), cats, note);
  return p;
}
function paint(n) { const r = state[n] || {}; document.querySelectorAll('input[name="cat-' + n + '"]').forEach((x) => (x.checked = x.value === r.category)); const no = $("note-" + n); if (no && document.activeElement !== no) no.value = r.note || ""; }
function count() { const k = DATA.items.filter((i) => (state[i.n] || {}).category).length; $("count").textContent = k + " of " + DATA.items.length + " triaged"; $("meter").style.width = (100 * k / DATA.items.length) + "%"; }
const chains = {};
function save(n) {
  const r = state[n] || {}; const body = { category: r.category || "", note: r.note || "", updated_at: new Date().toISOString() };
  chains[n] = (chains[n] || Promise.resolve()).then(async () => { if (store === "db") await db.doc("triage/r" + String(n).padStart(2, "0")).set(body); else { try { localStorage.setItem(DATA.store_key, JSON.stringify(state)); } catch (e) {} } })
    .catch((e) => { $("save-state").textContent = "Not saved: " + ((e && e.message) || "store refused") + ". Copy all as text as a backup."; $("save-state").classList.add("warn"); });
}
$("copy-btn").addEventListener("click", async () => {
  const lines = ["n,disease,pmid,clinvar_variation_id,category,note"].concat(DATA.items.map((i) => [i.n, i.disease, i.pmid, i.vid, (state[i.n] || {}).category || "", JSON.stringify((state[i.n] || {}).note || "")].join(",")));
  const text = lines.join("\\n");
  try { await navigator.clipboard.writeText(text); $("copy-btn").textContent = "Copied"; } catch (e) { const b = $("copy-box"); b.value = text; b.hidden = false; b.select(); }
});
DATA.items.forEach((i) => $("list").append(card(i))); count();
(async () => {
  const api = window.claude && window.claude.use ? await window.claude.use("db") : null;
  if (!api) { store = "local"; try { Object.assign(state, JSON.parse(localStorage.getItem(DATA.store_key) || "{}")); } catch (e) {} DATA.items.forEach((i) => paint(i.n)); count();
    $("save-state").textContent = "Saved only in this browser. When done, use Copy all as text and send it to Jimmy Lin."; $("save-state").classList.add("warn"); return; }
  db = api; store = "db"; $("save-state").textContent = "Choices save to this page's store as you go.";
  db.collection("triage").onSnapshot((snap) => { for (const d of snap.docs) { const n = String(parseInt(d.id.slice(1), 10)); state[n] = { ...(state[n] || {}), ...(d.data() || {}) }; paint(n); } count(); });
})();
</script>
"""

if __name__ == "__main__":
    raise SystemExit(main())
