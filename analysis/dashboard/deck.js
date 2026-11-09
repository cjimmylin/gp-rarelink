// Collaborator overview deck for GP-RareLink. Reads analysis/dashboard/deck_data.json (written by
// export_deck_data.py) so every number traces to the committed result files. Writes reports/deck/gp_rarelink_overview.pptx.
//   cd analysis/dashboard/node && npm install   (once)
//   node analysis/dashboard/deck.js
const path = require("path");
const fs = require("fs");
const pptxgen = require(path.join(__dirname, "node", "node_modules", "pptxgenjs"));

const ROOT = path.resolve(__dirname, "..", "..");
const D = JSON.parse(fs.readFileSync(path.join(__dirname, "deck_data.json"), "utf8"));
const S = D.stats;
const OUT = path.join(ROOT, "reports", "deck", "gp_rarelink_overview.pptx");

// Palette (the project's validated data-visualization palette; hex without '#', as pptxgenjs requires)
const INK = "0B0B0B", INK2 = "52514E", MUTED = "898781", GRID = "E1E0D9", PAPER = "FFFFFF", TINT = "F3F3F1";
const BLUE = "2A78D6", DEEP = "184F95", NAVY = "0F2F5C", ORANGE = "EB6834", LIGHTBLUE = "CDE2FB", PEACH = "FDF1EC", AQUA = "1BAF7A";
const FONT = "Calibri";

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10 x 5.625 in
pres.theme = { headFontFace: FONT, bodyFontFace: FONT };
pres.title = "GP-RareLink: interim overview for collaborators";
pres.author = "GP-RareLink";

const FOOT = `GP-RareLink · interim overview for collaborators · ${D.date} · internal review`;
pres.defineSlideMaster({
  title: "DARK", background: { color: NAVY },
  objects: [{ text: { text: FOOT, options: { x: 0.5, y: 5.2, w: 7.5, h: 0.3, fontSize: 9, color: "9FB7D9", margin: 0 } } }],
  slideNumber: { x: 9.2, y: 5.2, w: 0.5, h: 0.3, fontSize: 9, color: "9FB7D9" },
});
pres.defineSlideMaster({
  title: "CONTENT", background: { color: PAPER },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.5, y: 0.3, w: 9.0, h: 0.75, fontSize: 26, bold: true, color: INK, margin: 0, valign: "middle" }, text: "" } },
    { text: { text: FOOT, options: { x: 0.5, y: 5.22, w: 7.5, h: 0.28, fontSize: 9, color: MUTED, margin: 0 } } },
  ],
  slideNumber: { x: 9.2, y: 5.22, w: 0.5, h: 0.28, fontSize: 9, color: MUTED },
});

const N = (x) => Number(x).toLocaleString("en-US");
let slideIndex = 0;
function nextNotes() { return D.slides[slideIndex++].narration; }

function content(title) {
  const s = pres.addSlide({ masterName: "CONTENT" });
  s.addText(title, { placeholder: "title" });
  s.addNotes(nextNotes());
  return s;
}
function card(s, x, y, w, h, head, body, opts = {}) {
  const fill = opts.fill || TINT;
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, fill: { color: fill }, line: { color: fill }, rectRadius: 0.08 });
  if (opts.number !== undefined) {
    s.addShape(pres.ShapeType.ellipse, { x: x + 0.2, y: y + 0.2, w: 0.42, h: 0.42, fill: { color: opts.accent || BLUE }, line: { color: opts.accent || BLUE } });
    s.addText(String(opts.number), { x: x + 0.2, y: y + 0.2, w: 0.42, h: 0.42, fontSize: 13, bold: true, color: PAPER, align: "center", valign: "middle", margin: 0, isTextBox: true });
    s.addText(head, { x: x + 0.72, y: y + 0.18, w: w - 0.9, h: 0.46, fontSize: 14, bold: true, color: INK, valign: "middle", margin: 0, isTextBox: true });
  } else {
    s.addText(head, { x: x + 0.2, y: y + 0.18, w: w - 0.4, h: 0.4, fontSize: 14, bold: true, color: INK, valign: "middle", margin: 0, isTextBox: true });
  }
  s.addText(body, { x: x + 0.2, y: y + 0.7, w: w - 0.4, h: h - 0.85, fontSize: opts.bodySize || 11.5, color: INK2, valign: "top", margin: 0, isTextBox: true, paraSpaceAfter: 4 });
}
function stat(s, x, y, w, h, big, label, color = BLUE) {
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, fill: { color: TINT }, line: { color: TINT }, rectRadius: 0.08 });
  s.addText(big, { x: x + 0.15, y: y + 0.12, w: w - 0.3, h: h * 0.52, fontSize: 30, bold: true, color, valign: "middle", margin: 0, isTextBox: true });
  s.addText(label, { x: x + 0.15, y: y + h * 0.58, w: w - 0.3, h: h * 0.38, fontSize: 10.5, color: INK2, valign: "top", margin: 0, isTextBox: true });
}
function img(s, key, x, y, w, h) {
  s.addImage({ path: D.figures[key], x, y, w, h });
}

// 1. Title (dark)
{
  const s = pres.addSlide({ masterName: "DARK" });
  s.addText("GP-RareLink", { x: 0.6, y: 1.1, w: 8.8, h: 0.6, fontSize: 20, color: "9FB7D9", margin: 0, isTextBox: true });
  s.addText("Reading the rare-disease literature with a language model, and checking its work", { x: 0.6, y: 1.7, w: 8.8, h: 1.6, fontSize: 34, bold: true, color: PAPER, margin: 0, isTextBox: true, valign: "top" });
  s.addText(`Interim overview for collaborators · ${D.date}`, { x: 0.6, y: 3.5, w: 8.8, h: 0.4, fontSize: 15, color: "CDE2FB", margin: 0, isTextBox: true });
  s.addText("Rare Genomics Institute with the Stanford Open Virtual Assistant Lab · funded by Anthropic's AI for Science program", { x: 0.6, y: 3.95, w: 8.8, h: 0.6, fontSize: 12, color: "9FB7D9", margin: 0, isTextBox: true });
  s.addNotes(nextNotes());
}

// 2. The problem
{
  const s = content("A variant published once, and then lost");
  s.addText([
    { text: "When a child with a rare disease is finally diagnosed, the responsible variant is often reported in a single case report and never submitted to a public database. The laboratory testing the next child searches ClinVar and finds nothing.", options: { breakLine: true, paraSpaceAfter: 10 } },
    { text: "The knowledge exists. It is scattered across thousands of papers, in prose and tables no database can query, and hand curation has never kept up.", options: { breakLine: true, paraSpaceAfter: 10 } },
    { text: "Alexander disease is the example on the right: a 2024 review counts the published variants and patients; ClinVar holds a fraction of them.", options: {} },
  ], { x: 0.5, y: 1.25, w: 4.9, h: 3.6, fontSize: 14, color: INK2, valign: "top", margin: 0, isTextBox: true });
  stat(s, 5.8, 1.25, 3.7, 1.0, "182", "distinct causative variants published for Alexander disease (2024 review)");
  stat(s, 5.8, 2.4, 3.7, 1.0, "550", "published patients with Alexander disease");
  stat(s, 5.8, 3.55, 3.7, 1.0, String(S.axd_clinvar_plp), `pathogenic or likely-pathogenic ClinVar records for the gene (release ${S.clinvar_release})`, ORANGE);
}

// 3. The question and the rules
{
  const s = content("The question, and the rules behind it");
  s.addText("Can a language model, reading with strict rules, do the first pass of curation: which variant, in which person, with which clinical features, each value tied to the sentence it came from, at an accuracy we can measure rather than assume?",
    { x: 0.5, y: 1.2, w: 9.0, h: 0.9, fontSize: 14, color: INK2, italic: true, margin: 0, isTextBox: true, valign: "top" });
  card(s, 0.5, 2.25, 2.9, 2.7, "Quote everything", "A value without a verbatim quote is not allowed. A script looks up every quote in the paper. \"Not reported\" is a valid answer; a paper's silence never becomes a \"no\".", { number: 1 });
  card(s, 3.55, 2.25, 2.9, 2.7, "Hold out the answer key", "ClinVar and OMIM are never shown to the model. Code that reads papers cannot read them; a test fails if it could. They are compared afterwards, by a separate harness.", { number: 2 });
  card(s, 6.6, 2.25, 2.9, 2.7, "Decide the rules first", "Prompts, forms and the analysis plan were frozen on 2026-10-20, after a one-disease pilot. Changes since are logged as numbered deviations.", { number: 3 });
}

// 4. The pipeline
{
  const s = content("How it works: read, quote, check, compare");
  img(s, "fig1_workflow", 0.5, 1.15, 9.0, 3.9);
}

// 5. The six diseases
{
  const s = content("Six diseases, six organ systems");
  const head = ["Disease", "Gene", "Inheritance", "Papers read (open share)", "Individuals", "With a variant", "Variants placed", "Candidates", "OMIM variants recovered"];
  const rows = [head.map((h) => ({ text: h, options: { bold: true, color: PAPER, fill: { color: DEEP }, fontSize: 10.5 } }))];
  for (const d of D.diseases) {
    rows.push([
      { text: d.short + (d.development ? "*" : ""), options: { bold: true } }, { text: d.gene, options: { italic: true } }, d.inheritance,
      `${d.papers} (${d.cov_pct}%)`, N(d.individuals), N(d.with_variant), String(d.placed), String(d.candidates), `${d.omim_k} of ${d.omim_n}`,
    ]);
  }
  s.addTable(rows, { x: 0.5, y: 1.25, w: 9.0, colW: [0.95, 0.85, 1.15, 1.35, 0.95, 0.95, 0.95, 1.0, 0.85], fontSize: 11, color: INK, fontFace: FONT,
    border: { type: "solid", color: GRID, pt: 0.75 }, fill: { color: PAPER }, rowH: 0.36, valign: "middle", autoPage: false });
  s.addText(`*A20 haploinsufficiency (HA20) developed the pipeline; the other five are the confirmatory set. Only open-access papers were read. "Placed" = written unambiguously on the GRCh38 genome, which is what makes a variant comparable with ClinVar. "Candidates" = absent from ClinVar and OMIM, awaiting adjudication.`,
    { x: 0.5, y: 4.3, w: 9.0, h: 0.8, fontSize: 10, color: MUTED, margin: 0, isTextBox: true, valign: "top" });
}

// 6. Headline numbers
{
  const s = content("The numbers so far");
  const tiles = [
    [N(S.papers), "open-access papers read, six diseases"], [N(S.records), "individual records (GA4GH phenopackets), every value with a quote"],
    [N(S.quotes), "quotes checked against the paper text: all found, word for word"], [N(S.placed), "distinct variants placed on the genome"],
    [String(S.candidates), "variants in neither ClinVar nor OMIM, each with an evidence dossier"], [`${S.omim_k} of ${S.omim_n}`, `variants OMIM lists for these diseases recovered (${S.omim_pct}%)`],
  ];
  tiles.forEach(([big, label], i) => {
    const col = i % 3, row = Math.floor(i / 3);
    stat(s, 0.5 + col * 3.05, 1.25 + row * 1.85, 2.9, 1.65, big, label, i === 4 ? ORANGE : BLUE);
  });
}

// 7. Finding 1: receipts
{
  const s = content("Finding 1: receipts hold, decisive check pending");
  img(s, "fig2_checks", 0.5, 1.2, 5.9, 2.61);
  s.addText([
    { text: `Second model read: ${S.unsup_pct5}% of values unsupported on the five confirmatory diseases (${S.unsup_pct6}% with HA20).`, options: { bullet: true, breakLine: true, paraSpaceAfter: 8 } },
    { text: `Human raters in the pilot, before the fixes were frozen: ${S.human1}% and ${S.human2}%.`, options: { bullet: true, breakLine: true, paraSpaceAfter: 8 } },
    { text: `The pre-registered test is a blinded audit of ${S.n_o1} claims by two panel members. It is built; no claim has been rated.`, options: { bullet: true, breakLine: true, paraSpaceAfter: 8 } },
    { text: "Until then, the machine's rate is a filter's reading, not an accuracy.", options: { bullet: true, bold: true } },
  ], { x: 6.45, y: 1.2, w: 3.05, h: 3.8, fontSize: 12.5, color: INK2, valign: "top", margin: 0, isTextBox: true });
  s.addText("Blue: the gatekeeper's verdicts per disease run. Orange: two human audits of the pilot's output. Dashed line: the 2% target.", { x: 0.5, y: 3.9, w: 5.9, h: 0.6, fontSize: 10, color: MUTED, margin: 0, isTextBox: true, valign: "top" });
}

// 8. Finding 2: coverage
{
  const s = content("Finding 2: we find what we can read");
  img(s, "fig3_coverage", 0.5, 1.15, 9.0, 3.19);
  s.addText(`Left: the share of each disease's papers with open full text (light) beside the share of OMIM's listed variants we recovered (dark). Right: of the ${S.omim_src_all} papers OMIM cites for those variants, we could read ${S.omim_src_extracted}; ${S.omim_src_paywalled} are behind paywalls and ${S.omim_src_notfound} were never returned by our searches, mostly pre-1990 papers under earlier names for the disease. Where the source paper was read, the variant was in our records ${S.omim_restricted_k} times out of ${S.omim_restricted_n}.`,
    { x: 0.5, y: 4.4, w: 9.0, h: 0.75, fontSize: 10.5, color: INK2, margin: 0, isTextBox: true, valign: "top" });
}

// 9. Finding 3: the gap
{
  const s = content("Finding 3: a real gap in the databases");
  img(s, "fig4_gaps", 0.5, 1.2, 5.9, 2.42);
  s.addText([
    { text: `${N(S.placed)} variants placed on the genome; ${N(S.in_clinvar)} are in ClinVar, ${N(S.plp)} of them pathogenic or likely pathogenic.`, options: { bullet: true, breakLine: true, paraSpaceAfter: 8 } },
    { text: `${S.absent} are absent from ClinVar. After dropping unsupported ones, checking OMIM and withdrawing one normalization error of our own: ${S.candidates} candidates.`, options: { bullet: true, breakLine: true, paraSpaceAfter: 8 } },
    { text: `${S.reclass} more sit in ClinVar as uncertain or conflicting while papers call them pathogenic; ${S.reclass_strong} with strong evidence.`, options: { bullet: true, breakLine: true, paraSpaceAfter: 8 } },
    { text: "Every candidate has a dossier: papers, quotes, individuals, the authors' classification, and flags for the panel. Nothing is submitted without adjudication.", options: { bullet: true } },
  ], { x: 6.65, y: 1.2, w: 2.85, h: 3.9, fontSize: 11.5, color: INK2, valign: "top", margin: 0, isTextBox: true });
  s.addText("Each bar: one disease's genome-placed variants. Orange: candidates awaiting the panel.", { x: 0.5, y: 3.7, w: 5.9, h: 0.5, fontSize: 10, color: MUTED, margin: 0, isTextBox: true, valign: "top" });
}

// 10. Finding 4: open-weight model (native chart)
{
  const s = content("Finding 4: same variants, lost receipts, lower cost");
  const cats = ["A20 haploinsufficiency (HA20)", "SSADH deficiency"];
  s.addChart(pres.ChartType.bar, [
    { name: "Claude Opus", labels: cats, values: [S.ow.ha20.claude_unsup_f, S.ow.ssadh.claude_unsup_f] },
    { name: "DeepSeek-V4.1-Flash", labels: cats, values: [S.ow.ha20.open_unsup_f, S.ow.ssadh.open_unsup_f] },
  ], {
    x: 0.5, y: 1.2, w: 5.3, h: 3.6, barDir: "col", barGrouping: "clustered", chartColors: [BLUE, ORANGE],
    showTitle: true, title: "Values judged unsupported by the second read (%)", titleFontSize: 11, titleColor: INK2, titleFontFace: "+mn-lt",
    showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 10, dataLabelColor: INK2, dataLabelFontFace: "+mn-lt", dataLabelFormatCode: "0.0",
    catAxisLabelColor: INK2, catAxisLabelFontSize: 10, catAxisLabelFontFace: "+mn-lt", valAxisLabelColor: MUTED, valAxisLabelFontSize: 9, valAxisLabelFontFace: "+mn-lt",
    valGridLine: { color: GRID, size: 0.5 }, catGridLine: { style: "none" }, valAxisMaxVal: 10, valAxisMinVal: 0,
    showLegend: true, legendPos: "b", legendFontSize: 10, legendColor: INK2, legendFontFace: "+mn-lt",
  });
  s.addText([
    { text: `Same papers, prompts, forms and scoring. The open model found the same variants ${S.ow.ha20.jaccard}% to ${S.ow.ssadh.jaccard}% of the time (shared over union).`, options: { bullet: true, breakLine: true, paraSpaceAfter: 8 } },
    { text: `About 1/${S.cost_ratio} of the cost per paper ($${S.ow.ha20.open_cost} vs $${S.ow.ha20.claude_cost} median) and ${S.time_ratio} times the wall-clock.`, options: { bullet: true, breakLine: true, paraSpaceAfter: 8 } },
    { text: `${S.ow.ssadh.no_quote_pct}% to ${S.ow.ha20.no_quote_pct}% of its values came with no quote at all, which the rules forbid.`, options: { bullet: true, breakLine: true, paraSpaceAfter: 8 } },
    { text: "The judge is itself Claude, so the comparison is not neutral until the planned blinded human audit of both outputs.", options: { bullet: true } },
  ], { x: 6.05, y: 1.2, w: 3.45, h: 3.8, fontSize: 12, color: INK2, valign: "top", margin: 0, isTextBox: true });
}

// 11. Two more checks
{
  const s = content("Two more checks: repeats and memorization");
  card(s, 0.5, 1.25, 4.4, 3.7, "Run-to-run stability", `A tenth of the papers (${S.repeat_papers}) were run a second time.\n\nSame checklist answers ${S.chk_lo}% to ${S.chk_hi}% of the time.\n\nSame variants ${S.var_lo}% to ${S.var_hi}% of the time.\n\nWhere the runs differed, it was mostly over how many individuals a cohort paper describes.`, { number: "A", bodySize: 13 });
  card(s, 5.1, 1.25, 4.4, 3.7, "Memorization probe", `${S.mem_papers} papers were probed, stratified around the model's training cutoff: asked about each paper without its text, and asked to continue a passage.\n\nIn the ${S.mem_after} papers published after the cutoff, neither Claude nor the open model produced a specific recall or a correct variant.\n\nThe probe is small and will grow, but it gives no sign of memorization.`, { number: "B", bodySize: 13, accent: AQUA });
}

// 12. What it means
{
  const s = content("What it means");
  card(s, 0.5, 1.25, 2.9, 3.75, "Accuracy", `Records with complete provenance, stable across repeats, and a second read that removed ${N(S.dropped)} claims before records were built. What is missing is a human-rated error rate for the frozen pipeline. The ${S.n_o1}-claim audit provides it and costs no model time.`, { number: 1, bodySize: 12 });
  card(s, 3.55, 1.25, 2.9, 3.75, "Coverage", `Reading is not the bottleneck; access is. With ${S.cov_lo}% to ${S.cov_hi}% of each corpus open, completeness and the candidate list are lower bounds. A decision on institutional or text-mining access would change these results more than any change to the model.`, { number: 2, bodySize: 12 });
  card(s, 6.6, 1.25, 2.9, 3.75, "The answer key", "Databases curated by people deserve the same scrutiny. OMIM lists selected examples, not a catalogue; two of its entries link to ClinVar records that contradict their text. The OMIM check caught one of our own normalization errors, now fixed in the pipeline.", { number: 3, bodySize: 12, accent: ORANGE });
}

// 13. What we need from you
{
  const s = content("What we need from you");
  const head = ["Role", "What you would do", "Effort", "What it unlocks"];
  const rows = [head.map((h) => ({ text: h, options: { bold: true, color: PAPER, fill: { color: DEEP }, fontSize: 11 } }))];
  rows.push([{ text: "Audit rater", options: { bold: true } }, `Rate ${S.n_o1} extracted values against their quoted evidence on a blinded web page; two raters and a tie-breaker`, "10 to 15 hours per rater", "The primary outcome: the first true accuracy figure"]);
  rows.push([{ text: "Adjudicator", options: { bold: true } }, `Review the ${S.candidates} candidate variants from their dossiers and decide whether the evidence supports a submission`, "10 to 15 minutes per candidate", "ClinVar literature-only submissions and OMIM candidates"]);
  rows.push([{ text: "Cohort reader", options: { bold: true } }, "Fill a comparator sheet of clinical-feature frequencies from a natural-history cohort paper, without looking at our records", "1 to 2 hours per sheet", "The ascertainment-bias arm"]);
  rows.push([{ text: "Methods or domain reviewer", options: { bold: true } }, "Read the short paper or the full report and tell us what is wrong, missing or unclear, from your field's point of view", "1 to 3 hours", "A better study before anything is submitted"]);
  s.addTable(rows, { x: 0.5, y: 1.25, w: 9.0, colW: [1.6, 3.6, 1.6, 2.2], fontSize: 11, color: INK, fontFace: FONT, border: { type: "solid", color: GRID, pt: 0.75 }, fill: { color: PAPER }, rowH: 0.62, valign: "middle", autoPage: false });
  s.addText("Tell us who you are and how you would like to contribute through the form linked on the dashboard. Everything is published literature; there is no patient data.", { x: 0.5, y: 4.55, w: 9.0, h: 0.55, fontSize: 11.5, color: INK2, margin: 0, isTextBox: true, valign: "top" });
}

// 14. Closing (dark)
{
  const s = pres.addSlide({ masterName: "DARK" });
  s.addText("Thank you", { x: 0.6, y: 1.0, w: 8.8, h: 0.8, fontSize: 34, bold: true, color: PAPER, margin: 0, isTextBox: true });
  s.addText([
    { text: "The dashboard holds the short paper, the full report and supplement, this deck, the overview video, the candidate list and the form.", options: { breakLine: true, paraSpaceAfter: 10 } },
    { text: D.pages_url, options: { breakLine: true, paraSpaceAfter: 10, color: "CDE2FB", bold: true } },
    { text: `Every number in this deck comes from the project repository at commit ${D.commit}, and the report says plainly which questions are still open: the human audit, the access decision, and the adjudication of the candidates.`, options: {} },
  ], { x: 0.6, y: 2.0, w: 8.8, h: 2.6, fontSize: 15, color: "CDE2FB", margin: 0, isTextBox: true, valign: "top" });
  s.addNotes(nextNotes());
}

if (slideIndex !== D.slides.length) throw new Error(`narration count ${D.slides.length} does not match slides ${slideIndex}`);
fs.mkdirSync(path.dirname(OUT), { recursive: true });
pres.writeFile({ fileName: OUT }).then(() => console.log("wrote " + OUT + " (" + slideIndex + " slides)"));
