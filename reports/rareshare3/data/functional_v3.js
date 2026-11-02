const { chromium } = require('playwright');
const fs = require('fs');
const B = 'https://raresharedev30.wpenginepowered.com';
const cfg = JSON.parse(fs.readFileSync('inbox.json', 'utf8')); if (fs.existsSync('creds.json')) Object.assign(cfg, JSON.parse(fs.readFileSync('creds.json', 'utf8')));
const out = { steps: [], created: [] };
const log = (k, v) => { out.steps.push({ step: k, ...v }); console.log(k, JSON.stringify(v).slice(0, 400)); };
const MAILTM = 'https://api.mail.tm';
async function mail(path, opts = {}) { const r = await fetch(MAILTM + path, { ...opts, headers: { Authorization: 'Bearer ' + cfg.token, Accept: 'application/json', ...(opts.headers || {}) } }); return r; }
async function waitForMail(pred, ms = 180000) { const t0 = Date.now(); while (Date.now() - t0 < ms) { const r = await mail('/messages'); const d = await r.json(); const m = (d['hydra:member'] || []).find(pred); if (m) return m; await new Promise(r => setTimeout(r, 10000)); } return null; }
(async () => {
  const browser = await chromium.launch({ proxy: { server: process.env.HTTPS_PROXY } });
  const ctx = await browser.newContext({ viewport: { width: 1366, height: 900 }, userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36' });
  const page = await ctx.newPage();
  const net = [];
  page.on('response', r => { const u = r.url(); if (/contact-form-7|wp-login|signup|register|wp-admin\/admin-ajax|bbpress|activity|groups\/|wp-json\/buddypress/.test(u) && r.request().method() === 'POST') net.push({ url: u.slice(0, 140), status: r.status(), setCookie: (r.headers()['set-cookie'] || '').slice(0, 300) }); });
  const shot = async n => { try { await page.screenshot({ path: `shots_v3_${n}.jpg`, type: 'jpeg', quality: 50, fullPage: true }); } catch (e) {} };
  if (!process.env.SKIP_FORMS) {
  // A1 contact form
  try {
    await page.goto(B + '/contact-us/', { waitUntil: 'networkidle', timeout: 90000 });
    const f = page.locator('form.wpcf7-form').filter({ has: page.locator('input[name="your-subject"]') });
    await f.locator('input[name="your-email"]').fill(cfg.address);
    await f.locator('input[name="your-subject"]').fill('RareShare 3.0 pre-launch test (automated, please ignore)');
    await f.locator('textarea[name="your-message"]').fill('Automated pre-launch form test run by Claude at Dr. Jimmy Lin\'s request, 2026-11-02. No action needed.');
    const comp = f.locator('input[name="your-company"]'); if (await comp.count()) log('contact_form_honeypot_or_company_field', { present: true, visible: await comp.isVisible() });
    await f.locator('input[type="submit"]').click();
    await page.waitForTimeout(6000);
    const resp = await f.locator('.wpcf7-response-output').innerText().catch(() => '');
    log('contact_form_submit', { response_text: resp.trim(), status_class: await f.getAttribute('data-status'), network: net.filter(n => n.url.includes('contact-form-7')) });
    await shot('contact');
  } catch (e) { log('contact_form_submit', { error: String(e).slice(0, 300) }); }
  // A2 newsletter subscribe (footer form 34) on home
  try {
    net.length = 0;
    await page.goto(B + '/', { waitUntil: 'networkidle', timeout: 90000 });
    const f = page.locator('form.wpcf7-form').filter({ has: page.locator('input[value="Subscribe"]') }).first();
    await f.locator('input[name="your-email"]').fill(cfg.address);
    await f.locator('input[type="submit"]').click();
    await page.waitForTimeout(6000);
    const resp = await f.locator('.wpcf7-response-output').innerText().catch(() => '');
    log('newsletter_subscribe_submit', { response_text: resp.trim(), status_class: await f.getAttribute('data-status'), network: net.filter(n => n.url.includes('contact-form-7')) });
  } catch (e) { log('newsletter_subscribe_submit', { error: String(e).slice(0, 300) }); }
  }
  if (!process.env.SKIP_REGISTER) {
  // A3 registration
  try {
    net.length = 0;
    await page.goto(B + '/register/', { waitUntil: 'networkidle', timeout: 90000 });
    const vis = await page.$$eval('select[name$="_visibility"], input[name$="_visibility"]', els => els.map(e => ({ name: e.name, value: e.value, type: e.tagName, options: e.tagName === 'SELECT' ? [...e.options].map(o => o.value) : null })));
    log('register_default_field_visibility', { fields: vis });
    await page.fill('#signup_username', cfg.site_user);
    await page.fill('#signup_email', cfg.address);
    await page.fill('#pass1', cfg.site_pw); await page.waitForTimeout(800);
    const conf = page.locator('#pass2'); if (await conf.count() && await conf.isVisible()) if (await conf.count()) await conf.fill(cfg.site_pw);
    await page.fill('#field_1', 'RS30 Prelaunch Test (delete me)');
    await page.fill('#field_2', 'Testville');
    const country = page.locator('#field_7'); if (await country.count()) { try { await country.selectOption('US'); } catch (e) { await country.selectOption({ index: 1 }); } }
    for (const sel of ['#signup-privacy-policy-accept', '#signup-age-confirmation', 'input[name="signup_age_confirmation"]', 'input[name="signup-privacy-policy-accept"]']) { const c = page.locator(sel); if (await c.count() && !(await c.first().isChecked())) await c.first().check().catch(() => {}); }
    await shot('register_filled');
    await page.click('#signup_submit, input[name="signup_submit"]');
    await page.waitForLoadState('networkidle', { timeout: 90000 });
    const body = (await page.locator('main, #content, body').first().innerText()).replace(/\s+/g, ' ');
    const errs = await page.$$eval('.error, .bp-messages, .bp-feedback', e => e.map(x => x.innerText.trim()).filter(Boolean));
    log('register_submit', { url: page.url(), messages: errs.slice(0, 5), body_excerpt: body.slice(0, 500), network: net.filter(n => /register|signup/.test(n.url)) });
    out.created.push({ type: 'signup', username: cfg.site_user, email: cfg.address });
    await shot('register_result');
  } catch (e) { log('register_submit', { error: String(e).slice(0, 300) }); }
  // B activation mail
  let actLink = null;
  try {
    const m = await waitForMail(x => /activat|confirm|rare ?share/i.test(x.subject + ' ' + (x.from && x.from.address)));
    if (m) {
      const full = await (await mail('/messages/' + m.id)).json();
      const src = await (await mail('/messages/' + m.id + '/download')).text();
      fs.writeFileSync('activation_email.eml', src);
      const hdr = {}; for (const h of ['Received', 'Return-Path', 'DKIM-Signature', 'Authentication-Results', 'X-Mailer', 'Message-ID', 'From', 'Reply-To', 'List-Unsubscribe']) { const mm = src.match(new RegExp('^' + h + ':[^\\n]*(\\n[ \\t][^\\n]*)*', 'mi')); if (mm) hdr[h] = mm[0].replace(/\s+/g, ' ').slice(0, 300); }
      const links = (full.html || []).join(' ').match(/https?:\/\/[^"'\s<>]+/g) || []; actLink = links.find(l => /activat|key=/.test(l)) || (full.text || '').match(/https?:\/\/[^\s]+activat[^\s]*/)?.[0];
      log('activation_email', { received_after_s: Math.round((Date.now() - new Date(m.createdAt).getTime()) / 1000), from: m.from, subject: m.subject, headers: hdr, activation_link: actLink });
    } else log('activation_email', { received: false, note: 'no email within 3 minutes' });
    const all = await (await mail('/messages')).json(); log('inbox_snapshot', { count: all['hydra:totalItems'], subjects: (all['hydra:member'] || []).map(x => x.subject) });
  } catch (e) { log('activation_email', { error: String(e).slice(0, 300) }); }
  if (actLink) { try { await page.goto(actLink, { waitUntil: 'networkidle', timeout: 90000 }); const t = (await page.locator('main, body').first().innerText()).replace(/\s+/g, ' ').slice(0, 300); log('activate', { url: page.url(), text: t }); await shot('activated'); out.created.push({ type: 'activated_account', username: cfg.site_user }); } catch (e) { log('activate', { error: String(e).slice(0, 300) }); } }
  }
  // C login
  let loggedIn = false;
  try {
    net.length = 0;
    await page.goto(B + '/log-in/', { waitUntil: 'networkidle', timeout: 90000 });
    await page.fill('input[name="log"]', cfg.site_user); await page.fill('input[name="pwd"]', cfg.site_pw);
    await Promise.all([page.waitForNavigation({ waitUntil: 'networkidle', timeout: 90000 }).catch(() => {}), page.click('input[name="wp-submit"], button[type="submit"].bbp-login-form, form.bbp-login-form input[type="submit"]')]);
    const cookies = await ctx.cookies(B);
    const auth = cookies.filter(c => /wordpress_logged_in|wordpress_sec|wordpress_[0-9a-f]{32}$|bp-|wp-settings/.test(c.name)).map(c => ({ name: c.name.slice(0, 40), secure: c.secure, httpOnly: c.httpOnly, sameSite: c.sameSite, expires: c.expires }));
    const txt = (await page.locator('body').innerText()).replace(/\s+/g, ' ');
    loggedIn = /log ?out|my profile|logout/i.test(txt) || cookies.some(c => c.name.startsWith('wordpress_logged_in'));
    log('login', { landed: page.url(), logged_in: loggedIn, auth_cookies: auth, login_post: net.filter(n => n.url.includes('wp-login')), error_text: (txt.match(/(error|incorrect|invalid|unknown)[^.]{0,120}/i) || [])[0] });
    await shot('after_login');
  } catch (e) { log('login', { error: String(e).slice(0, 300) }); }
  if (loggedIn) {
    const visit = async (p, label) => { try { const r = await page.goto(B + p, { waitUntil: 'networkidle', timeout: 90000 }); const t = (await page.locator('main, body').first().innerText()).replace(/\s+/g, ' '); const h = r.headers(); log(label || p, { status: r.status(), final: page.url(), xcache: h['x-cache'], cache_control: h['cache-control'], text: t.slice(0, 220) }); return t; } catch (e) { log(label || p, { error: String(e).slice(0, 200) }); return ''; } };
    // authorization checks for a plain member
    for (const p of ['/manage-users/', '/manage-communities/', '/manage-guides/', '/manage-news-links/', '/manage-newsletters/', '/manage-podcasts/', '/start-a-community/', '/my-communities/', '/wp-admin/', '/wp-admin/users.php', '/wp-admin/edit.php', '/wp-admin/options-general.php', '/wp-admin/plugins.php']) await visit(p, 'authz ' + p);
    // own profile, edit, visibility
    await visit('/members/me/', 'profile_me');
    try {
      await page.goto(B + `/members/${cfg.site_user.toLowerCase()}/profile/edit/`, { waitUntil: 'networkidle', timeout: 90000 });
      const vis = await page.$$eval('select[name$="_visibility"], input[name$="_visibility"]:checked, .field-visibility-settings, .current-visibility-level', els => els.map(e => (e.value || e.innerText || '').trim().slice(0, 40)));
      log('profile_edit_visibility', { url: page.url(), visibility_controls: vis.slice(0, 12) });
      const city = page.locator('#field_2'); if (await city.count()) { await city.fill('<b>rs30-xss-check</b>'); await page.click('#profile-group-edit-submit, input[name="profile-group-edit-submit"]'); await page.waitForLoadState('networkidle'); const html = await page.content(); const shown = await page.locator('body').innerText(); log('profile_field_html_escaping', { raw_tag_in_html: /<b>rs30-xss-check<\/b>/.test(html), escaped_in_html: /&lt;b&gt;rs30-xss-check/.test(html), visible_text: (shown.match(/.{0,30}rs30-xss-check.{0,30}/) || [])[0] }); await page.goto(B + `/members/${cfg.site_user.toLowerCase()}/profile/edit/`, { waitUntil: 'networkidle' }); await page.fill('#field_2', 'Testville'); await page.click('#profile-group-edit-submit, input[name="profile-group-edit-submit"]').catch(() => {}); }
    } catch (e) { log('profile_edit', { error: String(e).slice(0, 300) }); }
    // logged-out view of the test profile (what others see)
    try { const c2 = await browser.newContext(); const p2 = await c2.newPage(); await p2.goto(B + `/members/${cfg.site_user.toLowerCase()}/`, { waitUntil: 'networkidle', timeout: 90000 }); const t = (await p2.locator('main, body').first().innerText()).replace(/\s+/g, ' '); log('profile_public_view', { shows_city: /Testville/.test(t), shows_country: /United States|US\b/.test(t), shows_fullname: /RS30 Prelaunch Test/.test(t), excerpt: t.slice(0, 300) }); const r = await p2.goto(B + '/groups/', { waitUntil: 'networkidle' }); const t2 = await p2.locator('body').innerText(); log('cache_leak_check_logged_out_groups', { status: r.status(), xcache: r.headers()['x-cache'], shows_logged_in_ui: /log ?out|my profile/i.test(t2), shows_test_user: t2.includes(cfg.site_user) }); await c2.close(); } catch (e) { log('profile_public_view', { error: String(e).slice(0, 300) }); }
    // join test community, post activity, forum topic + reply
    try {
      await page.goto(B + '/groups/test-community/', { waitUntil: 'networkidle', timeout: 90000 });
      const join = page.locator('a.group-button.join-group, .group-button a:has-text("Join"), a:has-text("Join Group")').first();
      if (await join.count()) { await join.click(); await page.waitForTimeout(4000); }
      const t = (await page.locator('body').innerText()).replace(/\s+/g, ' ');
      log('join_test_community', { joined: /leave group|member of|you are a member/i.test(t) || !(await join.count()), excerpt: (t.match(/.{0,60}(Join Group|Leave Group).{0,60}/i) || [])[0] });
      const ta = page.locator('#whats-new, textarea[name="whats-new"], #whats-new-textarea, .whats-new-textarea [contenteditable]').first();
      if (await ta.count()) { await ta.click(); await ta.fill('Automated pre-launch test post (RareShare 3.0 review, 2026-11-02). Please delete.'); await page.click('#aw-whats-new-submit, button[name="aw-whats-new-submit"]'); await page.waitForTimeout(5000); const t2 = await page.locator('body').innerText(); log('post_activity_update', { visible: t2.includes('Automated pre-launch test post'), network: net.filter(n => /activity|admin-ajax|buddypress/.test(n.url)).slice(-3) }); out.created.push({ type: 'activity_update', group: 'test-community' }); } else log('post_activity_update', { form_found: false });
      await shot('test_community');
      await page.goto(B + '/groups/test-community/forum/', { waitUntil: 'networkidle', timeout: 90000 });
      const title = page.locator('#bbp_topic_title'); if (await title.count()) { await title.fill('RS30 pre-launch test topic (automated, please delete)'); const c = page.locator('#bbp_topic_content, textarea[name="bbp_topic_content"]').first(); await c.fill('Automated test topic created during the 2026-11-02 pre-launch review. Please delete.'); await page.click('#bbp_topic_submit'); await page.waitForLoadState('networkidle'); const t3 = await page.locator('body').innerText(); log('create_forum_topic', { url: page.url(), visible: t3.includes('RS30 pre-launch test topic') }); out.created.push({ type: 'forum_topic', group: 'test-community', url: page.url() });
        const rc = page.locator('#bbp_reply_content, textarea[name="bbp_reply_content"]').first(); if (await rc.count()) { await rc.fill('Automated test reply, please delete.'); await page.click('#bbp_reply_submit'); await page.waitForLoadState('networkidle'); const t4 = await page.locator('body').innerText(); log('create_forum_reply', { visible: t4.includes('Automated test reply') }); out.created.push({ type: 'forum_reply', url: page.url() }); } else log('create_forum_reply', { form_found: false }); } else log('create_forum_topic', { form_found: false, note: 'no new-topic form on test-community forum for a member' });
      await shot('forum_topic');
    } catch (e) { log('community_actions', { error: String(e).slice(0, 300) }); }
    // notifications, settings, messages, delete-account availability
    for (const p of [`/members/${cfg.site_user.toLowerCase()}/notifications/`, `/members/${cfg.site_user.toLowerCase()}/settings/`, `/members/${cfg.site_user.toLowerCase()}/settings/profile/`, `/members/${cfg.site_user.toLowerCase()}/settings/delete-account/`, `/members/${cfg.site_user.toLowerCase()}/messages/`, `/members/${cfg.site_user.toLowerCase()}/friends/`, '/activity/']) await visit(p, 'member ' + p.replace(`/members/${cfg.site_user.toLowerCase()}`, '/members/<me>'));
    // REST as logged-in user
    try { const r = await page.evaluate(async () => { const n = (window.wpApiSettings && wpApiSettings.nonce) || (window.BP_Nouveau && BP_Nouveau.nonces && BP_Nouveau.nonces.rest) || null; const res = {}; for (const u of ['/wp-json/wp/v2/users/me?context=edit', '/wp-json/buddypress/v1/members/me', '/wp-json/wp/v2/users?context=edit&per_page=3', '/wp-json/wp/v2/settings']) { const x = await fetch(u, { headers: n ? { 'X-WP-Nonce': n } : {} }); res[u] = { status: x.status, body: (await x.text()).slice(0, 200) }; } return { nonce_found: !!n, res }; }); log('rest_logged_in', r); } catch (e) { log('rest_logged_in', { error: String(e).slice(0, 200) }); }
    // mobile homepage while logged in
    try { const mc = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1' }); await mc.addCookies(await ctx.cookies()); const mp = await mc.newPage(); const r = await mp.goto(B + '/', { waitUntil: 'networkidle', timeout: 90000 }); log('mobile_home_logged_in', { status: r.status(), title: await mp.title() }); await mc.close(); } catch (e) { log('mobile_home_logged_in', { error: String(e).slice(0, 200) }); }
    // logout
    try { await page.goto(B + '/wp-login.php?action=logout', { waitUntil: 'networkidle' }); const a = page.locator('a:has-text("log out")'); if (await a.count()) await a.first().click(); await page.waitForTimeout(3000); const c = (await ctx.cookies(B)).filter(x => x.name.startsWith('wordpress_logged_in')); const r = await page.goto(B + '/members/me/', { waitUntil: 'networkidle' }); log('logout', { logged_in_cookie_left: c.length, members_me_after_logout: page.url(), status: r.status() }); } catch (e) { log('logout', { error: String(e).slice(0, 200) }); }
    // lost password for the test account only
    try { await page.goto(B + '/lost-password/', { waitUntil: 'networkidle', timeout: 90000 }); const inp = page.locator('input[name="user_login"], input[type="text"], input[type="email"]').first(); await inp.fill(cfg.site_user); await page.click('input[type="submit"], button[type="submit"]'); await page.waitForLoadState('networkidle'); const t = (await page.locator('main, body').first().innerText()).replace(/\s+/g, ' '); const m = await waitForMail(x => /password|reset/i.test(x.subject), 150000); log('lost_password', { page_text: (t.match(/.{0,120}(email|check|sent|reset|error).{0,120}/i) || [])[0], email_received: !!m, subject: m && m.subject, from: m && m.from }); } catch (e) { log('lost_password', { error: String(e).slice(0, 200) }); }
  }
  const all = await (await mail('/messages')).json().catch(() => ({})); log('final_inbox', { count: all['hydra:totalItems'], subjects: (all['hydra:member'] || []).map(x => ({ subject: x.subject, from: x.from && x.from.address, at: x.createdAt })) });
  fs.writeFileSync('functional_v3_results.json', JSON.stringify(out, null, 1));
  await browser.close(); console.log('FUNCTIONAL DONE');
})().catch(e => { console.error('FATAL', e); fs.writeFileSync('functional_v3_results.json', JSON.stringify(out, null, 1)); process.exit(1); });
