// Generic slide renderer for GP-RareLink decks built from a JSON spec (used for the deep-dive deck).
// Reads the spec file given as argv[2] (default analysis/dashboard/deep_dive_data.json), writes the
// .pptx given in the spec's `output`. Slide types: title, section, bullets, figure, table, stats, cards, closing.
//   node analysis/dashboard/deck_long.js [spec.json]
const path = require("path");
const fs = require("fs");
const pptxgen = require(path.join(__dirname, "node", "node_modules", "pptxgenjs"));

const ROOT = path.resolve(__dirname, "..", "..");
const specPath = process.argv[2] ? path.resolve(process.argv[2]) : path.join(__dirname, "deep_dive_data.json");
const D = JSON.parse(fs.readFileSync(specPath, "utf8"));
const OUT = path.join(ROOT, D.output);

const INK = "0B0B0B", INK2 = "52514E", MUTED = "898781", GRID = "E1E0D9", PAPER = "FFFFFF", TINT = "F3F3F1";
const BLUE = "2A78D6", DEEP = "184F95", NAVY = "0F2F5C", ORANGE = "EB6834", AQUA = "1BAF7A";
const FONT = "Calibri";

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.theme = { headFontFace: FONT, bodyFontFace: FONT };
pres.title = D.title;
pres.author = "GP-RareLink";
const FOOT = `${D.footer} · ${D.date}`;
pres.defineSlideMaster({
  title: "DARK", background: { color: NAVY },
  objects: [{ text: { text: FOOT, options: { x: 0.5, y: 5.2, w: 7.5, h: 0.3, fontSize: 9, color: "9FB7D9", margin: 0 } } }],
  slideNumber: { x: 9.2, y: 5.2, w: 0.5, h: 0.3, fontSize: 9, color: "9FB7D9" },
});
pres.defineSlideMaster({
  title: "CONTENT", background: { color: PAPER },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.5, y: 0.3, w: 9.0, h: 0.75, fontSize: 24, bold: true, color: INK, margin: 0, valign: "middle", align: "left" }, text: "" } },
    { text: { text: FOOT, options: { x: 0.5, y: 5.22, w: 7.5, h: 0.28, fontSize: 9, color: MUTED, margin: 0 } } },
  ],
  slideNumber: { x: 9.2, y: 5.22, w: 0.5, h: 0.28, fontSize: 9, color: MUTED },
});

function bulletRuns(items, size) {
  return items.map((b, i) => ({ text: b, options: { bullet: true, breakLine: i < items.length - 1, paraSpaceAfter: 6, fontSize: size } }));
}
function card(s, x, y, w, h, head, body, num, accent) {
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, fill: { color: TINT }, line: { color: TINT }, rectRadius: 0.08 });
  if (num !== undefined) {
    s.addShape(pres.ShapeType.ellipse, { x: x + 0.2, y: y + 0.18, w: 0.4, h: 0.4, fill: { color: accent || BLUE }, line: { color: accent || BLUE } });
    s.addText(String(num), { x: x + 0.2, y: y + 0.18, w: 0.4, h: 0.4, fontSize: 12, bold: true, color: PAPER, align: "center", valign: "middle", margin: 0, isTextBox: true });
    s.addText(head, { x: x + 0.7, y: y + 0.15, w: w - 0.9, h: 0.46, fontSize: 13.5, bold: true, color: INK, valign: "middle", margin: 0, isTextBox: true });
  } else {
    s.addText(head, { x: x + 0.2, y: y + 0.15, w: w - 0.4, h: 0.4, fontSize: 13.5, bold: true, color: INK, valign: "middle", margin: 0, isTextBox: true });
  }
  s.addText(body, { x: x + 0.2, y: y + 0.68, w: w - 0.4, h: h - 0.8, fontSize: 11, color: INK2, valign: "top", margin: 0, isTextBox: true, paraSpaceAfter: 4 });
}
function stat(s, x, y, w, h, big, label, color) {
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, fill: { color: TINT }, line: { color: TINT }, rectRadius: 0.08 });
  s.addText(big, { x: x + 0.15, y: y + 0.1, w: w - 0.3, h: h * 0.5, fontSize: 26, bold: true, color: color || BLUE, valign: "middle", margin: 0, isTextBox: true });
  s.addText(label, { x: x + 0.15, y: y + h * 0.56, w: w - 0.3, h: h * 0.4, fontSize: 10, color: INK2, valign: "top", margin: 0, isTextBox: true });
}
function imgBox(fig, x, y, w, h) {
  // fit the image into the box keeping its aspect ratio (spec gives the pixel size)
  const ar = fig.w / fig.h, boxAr = w / h;
  let iw = w, ih = h;
  if (ar > boxAr) ih = w / ar; else iw = h * ar;
  return { path: fig.path, x: x + (w - iw) / 2, y: y, w: iw, h: ih };
}

for (const sl of D.slides) {
  if (sl.type === "title") {
    const s = pres.addSlide({ masterName: "DARK" });
    s.addText(sl.kicker || "GP-RareLink", { x: 0.6, y: 1.0, w: 8.8, h: 0.5, fontSize: 18, color: "9FB7D9", margin: 0, isTextBox: true });
    s.addText(sl.title, { x: 0.6, y: 1.55, w: 8.8, h: 1.7, fontSize: 32, bold: true, color: PAPER, margin: 0, isTextBox: true, valign: "top" });
    s.addText(sl.subtitle || "", { x: 0.6, y: 3.4, w: 8.8, h: 0.5, fontSize: 15, color: "CDE2FB", margin: 0, isTextBox: true });
    s.addText(sl.note || "", { x: 0.6, y: 3.95, w: 8.8, h: 0.8, fontSize: 12, color: "9FB7D9", margin: 0, isTextBox: true, valign: "top" });
    s.addNotes(sl.narration);
  } else if (sl.type === "section") {
    const s = pres.addSlide({ masterName: "DARK" });
    s.addText(sl.kicker || "", { x: 0.6, y: 1.6, w: 8.8, h: 0.5, fontSize: 16, color: "9FB7D9", margin: 0, isTextBox: true });
    s.addText(sl.title, { x: 0.6, y: 2.1, w: 8.8, h: 1.0, fontSize: 34, bold: true, color: PAPER, margin: 0, isTextBox: true });
    s.addText(sl.subtitle || "", { x: 0.6, y: 3.2, w: 8.8, h: 1.2, fontSize: 15, color: "CDE2FB", margin: 0, isTextBox: true, valign: "top" });
    s.addNotes(sl.narration);
  } else if (sl.type === "closing") {
    const s = pres.addSlide({ masterName: "DARK" });
    s.addText(sl.title, { x: 0.6, y: 1.0, w: 8.8, h: 0.8, fontSize: 32, bold: true, color: PAPER, margin: 0, isTextBox: true });
    s.addText(sl.lines.map((l, i) => ({ text: l, options: { breakLine: i < sl.lines.length - 1, paraSpaceAfter: 10 } })), { x: 0.6, y: 2.0, w: 8.8, h: 2.8, fontSize: 14, color: "CDE2FB", margin: 0, isTextBox: true, valign: "top" });
    s.addNotes(sl.narration);
  } else {
    const s = pres.addSlide({ masterName: "CONTENT" });
    s.addText(sl.title, { placeholder: "title" });
    s.addNotes(sl.narration);
    if (sl.type === "bullets") {
      const size = sl.fontSize || 12.5;
      if (sl.figure) {
        const fig = D.figures[sl.figure];
        const fw = sl.figureWidth || 5.6;
        s.addImage(imgBox(fig, 0.5, 1.2, fw, 3.3));
        if (sl.caption) s.addText(sl.caption, { x: 0.5, y: 4.55, w: fw, h: 0.6, fontSize: 9.5, color: MUTED, margin: 0, isTextBox: true, valign: "top" });
        s.addText(bulletRuns(sl.bullets, size), { x: 0.5 + fw + 0.3, y: 1.2, w: 9.5 - fw - 0.3, h: 3.9, color: INK2, valign: "top", margin: 0, isTextBox: true });
      } else {
        s.addText(bulletRuns(sl.bullets, size), { x: 0.5, y: 1.2, w: 9.0, h: 3.9, color: INK2, valign: "top", margin: 0, isTextBox: true });
      }
    } else if (sl.type === "figure") {
      const fig = D.figures[sl.figure];
      s.addImage(imgBox(fig, 0.5, 1.15, 9.0, sl.caption ? 3.35 : 3.95));
      if (sl.caption) s.addText(sl.caption, { x: 0.5, y: 4.55, w: 9.0, h: 0.6, fontSize: 10, color: INK2, margin: 0, isTextBox: true, valign: "top" });
    } else if (sl.type === "table") {
      const rows = [sl.head.map((h) => ({ text: h, options: { bold: true, color: PAPER, fill: { color: DEEP }, fontSize: sl.fontSize || 10.5 } }))];
      for (const r of sl.rows) rows.push(r.map((c, j) => (j === 0 ? { text: String(c), options: { bold: true } } : String(c))));
      const opts = { x: 0.5, y: 1.2, w: 9.0, fontSize: sl.fontSize || 10.5, color: INK, fontFace: FONT, border: { type: "solid", color: GRID, pt: 0.75 }, fill: { color: PAPER }, valign: "middle", autoPage: false };
      if (sl.colW) opts.colW = sl.colW;
      if (sl.rowH) opts.rowH = sl.rowH;
      s.addTable(rows, opts);
      if (sl.note) s.addText(sl.note, { x: 0.5, y: sl.noteY || 4.5, w: 9.0, h: 0.65, fontSize: 9.5, color: MUTED, margin: 0, isTextBox: true, valign: "top" });
    } else if (sl.type === "stats") {
      const n = sl.tiles.length, cols = n <= 3 ? n : 3, rows = Math.ceil(n / cols);
      const w = (9.0 - 0.15 * (cols - 1)) / cols, h = rows === 1 ? 2.4 : 1.75;
      sl.tiles.forEach(([big, label, accent], i) => {
        const c = i % cols, r = Math.floor(i / cols);
        stat(s, 0.5 + c * (w + 0.15), 1.25 + r * (h + 0.2), w, h, big, label, accent ? ORANGE : BLUE);
      });
      if (sl.note) s.addText(sl.note, { x: 0.5, y: 4.75, w: 9.0, h: 0.4, fontSize: 10, color: MUTED, margin: 0, isTextBox: true });
    } else if (sl.type === "cards") {
      let y = 1.2, h = 3.8;
      if (sl.intro) { s.addText(sl.intro, { x: 0.5, y: 1.15, w: 9.0, h: 0.7, fontSize: 12.5, color: INK2, italic: true, margin: 0, isTextBox: true, valign: "top" }); y = 1.95; h = 3.1; }
      const n = sl.cards.length, w = (9.0 - 0.15 * (n - 1)) / n;
      sl.cards.forEach(([head, body], i) => card(s, 0.5 + i * (w + 0.15), y, w, h, head, body, sl.numbered ? i + 1 : undefined, i === n - 1 && sl.lastAccent ? ORANGE : (sl.aqua ? AQUA : BLUE)));
    } else {
      throw new Error(`unknown slide type ${sl.type}`);
    }
  }
}
fs.mkdirSync(path.dirname(OUT), { recursive: true });
pres.writeFile({ fileName: OUT }).then(() => console.log(`wrote ${OUT} (${D.slides.length} slides)`));
