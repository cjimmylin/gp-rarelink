// Try each free URL from candidates_<date>.json in headless Chromium (Playwright,
// default settings: no user-agent spoofing, no stealth plugins).
//
// For each paper, stops at the first PDF obtained. For an HTML landing page it
// follows the page's own citation_pdf_url meta tag; if there is none and the page
// itself carries a long article text, it saves the page HTML instead.
// A challenge page (CAPTCHA, Cloudflare "Just a moment", "verify you are human")
// is recorded as such and never interacted with.
//
// Output (git-ignored): data/literature/free_copies/<disease>/<pmid>.pdf|.html
// and data/literature/free_copies/results_<date>.jsonl (one line per paper,
// appended, so a re-run skips papers already done).
//
//   node analysis/corpus/free_copies/fetch_browser.js 2026-11-14

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '../../..');
const DATE = process.argv[2];
const BASE = path.join(ROOT, 'data/literature/free_copies');
const RESULTS = path.join(BASE, `results_${DATE}.jsonl`);
const CHALLENGE = /just a moment|recaptcha|captcha|attention required|verify you are human|are you a robot|security check|bot verification|checking your browser|unusual traffic|access denied/i;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function isPdf(buf) { return buf && buf.length > 4 && buf.slice(0, 5).toString() === '%PDF-'; }

async function tryPdfRequest(ctx, url) {
  try {
    const r = await ctx.request.get(url, { timeout: 60000, maxRedirects: 10 });
    const body = await r.body();
    if (isPdf(body)) return { ok: true, body, status: r.status(), final: r.url() };
    return { ok: false, status: r.status(), ctype: r.headers()['content-type'] || '', final: r.url() };
  } catch (e) { return { ok: false, error: e.message.split('\n')[0] }; }
}

async function tryUrl(ctx, url) {
  const page = await ctx.newPage();
  const rec = { url };
  try {
    let resp;
    const dl = page.waitForEvent('download', { timeout: 60000 }).catch(() => null);
    try {
      resp = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
    } catch (e) {
      if (/Download is starting/.test(e.message)) {
        const d = await dl;
        if (d) {
          const p = await d.path();
          const body = p ? fs.readFileSync(p) : null;
          if (isPdf(body)) return { ...rec, outcome: 'pdf', body, how: 'download' };
        }
        return { ...rec, outcome: 'download_not_pdf' };
      }
      return { ...rec, outcome: 'error', error: e.message.split('\n')[0] };
    }
    await page.waitForTimeout(2500);
    rec.status = resp ? resp.status() : null;
    rec.final = page.url();
    const ctype = (resp && resp.headers()['content-type']) || '';
    if (/pdf/i.test(ctype)) {
      const body = await resp.body().catch(() => null);
      if (isPdf(body)) return { ...rec, outcome: 'pdf', body, how: 'inline' };
      const r = await tryPdfRequest(ctx, page.url());
      if (r.ok) return { ...rec, outcome: 'pdf', body: r.body, how: 'request' };
    }
    const title = await page.title().catch(() => '');
    const text = await page.evaluate(() => (document.body ? document.body.innerText : '')).catch(() => '');
    rec.title = title.slice(0, 150);
    if (CHALLENGE.test(title) || (CHALLENGE.test(text.slice(0, 1500)) && text.length < 3000)) {
      return { ...rec, outcome: 'challenge' };
    }
    if (rec.status && rec.status >= 400) return { ...rec, outcome: `http_${rec.status}` };
    const pdfMeta = await page.evaluate(() => {
      const m = document.querySelector('meta[name="citation_pdf_url"]');
      return m ? m.content : null;
    }).catch(() => null);
    if (pdfMeta) {
      rec.pdf_meta = pdfMeta;
      const r = await tryPdfRequest(ctx, pdfMeta);
      if (r.ok) return { ...rec, outcome: 'pdf', body: r.body, how: 'citation_pdf_url' };
      rec.pdf_meta_result = r;
      // Some hosts serve the PDF only to a page navigation.
      const p2 = await ctx.newPage();
      try {
        const dl2 = p2.waitForEvent('download', { timeout: 45000 }).catch(() => null);
        let r2;
        try { r2 = await p2.goto(pdfMeta, { waitUntil: 'domcontentloaded', timeout: 45000 }); } catch (e) {
          if (/Download is starting/.test(e.message)) {
            const d = await dl2; const p = d && await d.path(); const body = p ? fs.readFileSync(p) : null;
            if (isPdf(body)) return { ...rec, outcome: 'pdf', body, how: 'citation_pdf_url_download' };
          }
        }
        if (r2) {
          const body = await r2.body().catch(() => null);
          if (isPdf(body)) return { ...rec, outcome: 'pdf', body, how: 'citation_pdf_url_nav' };
          const t2 = await p2.title().catch(() => '');
          if (CHALLENGE.test(t2)) rec.pdf_meta_result = { challenge: t2.slice(0, 100) };
        }
      } finally { await p2.close().catch(() => {}); }
    }
    rec.text_len = text.length;
    // An article page with its full text on it: long, with a references section.
    if (text.length > 20000 && /\bReferences\b|\bREFERENCES\b|\bBibliography\b/.test(text) && /\b(Methods|Case report|CASE REPORT|Discussion|DISCUSSION|Introduction|INTRODUCTION)\b/.test(text)) {
      return { ...rec, outcome: 'html_fulltext', html: await page.content() };
    }
    return { ...rec, outcome: pdfMeta ? 'pdf_link_failed' : 'landing_only' };
  } catch (e) {
    return { ...rec, outcome: 'error', error: e.message.split('\n')[0] };
  } finally {
    await page.close().catch(() => {});
  }
}

(async () => {
  const cands = JSON.parse(fs.readFileSync(path.join(BASE, `candidates_${DATE}.json`)));
  const done = new Set();
  if (fs.existsSync(RESULTS)) for (const l of fs.readFileSync(RESULTS, 'utf8').split('\n')) if (l) done.add(JSON.parse(l).pmid);
  const browser = await chromium.launch();
  let n = 0;
  for (const c of cands) {
    if (done.has(c.pmid)) continue;
    if (process.env.LIMIT && n >= Number(process.env.LIMIT)) break;
    n += 1;
    const ctx = await browser.newContext({ acceptDownloads: true });
    const attempts = [];
    let saved = null;
    for (const t of c.try) {
      const r = await tryUrl(ctx, t.url);
      const { body, html, ...meta } = r;
      attempts.push({ ...meta, site: t.site, style: t.style });
      if (r.outcome === 'pdf' || r.outcome === 'html_fulltext') {
        const dir = path.join(BASE, c.disease);
        fs.mkdirSync(dir, { recursive: true });
        const f = path.join(dir, `${c.pmid}.${r.outcome === 'pdf' ? 'pdf' : 'html'}`);
        fs.writeFileSync(f, r.outcome === 'pdf' ? body : html);
        saved = { file: path.relative(ROOT, f), kind: r.outcome, bytes: fs.statSync(f).size, from: t.url };
        break;
      }
      await sleep(2000);
    }
    await ctx.close();
    const line = { disease: c.disease, pmid: c.pmid, doi: c.doi, pmcid: c.pmcid, priority: c.priority,
      saved, attempts, challenge_urls: c.challenge_urls, at: new Date().toISOString() };
    fs.appendFileSync(RESULTS, JSON.stringify(line) + '\n');
    console.log(`${n} ${c.disease} ${c.pmid} -> ${saved ? saved.kind : (attempts.map((a) => a.outcome).join(',') || 'no_url')}`);
  }
  await browser.close();
})();
