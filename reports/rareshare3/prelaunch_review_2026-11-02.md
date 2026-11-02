# RareShare 3.0 pre-launch review (dev site)

*Reviewed 2026-11-02 by Claude in a Claude Code session, at Jimmy's request. Non-destructive, logged-out only. Nothing was submitted, created, changed or brute-forced.*

**Site reviewed:** https://raresharedev30.wpenginepowered.com (WordPress 7.1.4 + BuddyPress + bbPress on WP Engine, behind Cloudflare).
**Compared against:** https://prod30.rareshare.org (the WP Engine production environment, DNS `wp.wpenginepowered.com`) and the live https://rareshare.org (the old Rails site on AWS).

**Note on the link you sent.** `https://raresharedev3.0.wpenginepowered.com` does not work: the dot in `3.0` makes it a two-level subdomain that WP Engine's wildcard certificate does not cover, and the TLS handshake fails before any page loads. The environment is `raresharedev30`. Check any place the link was shared (emails, docs, the WP Engine dashboard notes).

Supporting data for every number below is in `data/` (crawl summary, broken-link list, browser and accessibility results, content inventory, path probe) and `screenshots/`.

---

## 1. Findings ranked

| # | Severity | Finding | Where | Fix |
|---|---|---|---|---|
| 1 | **Critical** | **The homepage returns HTTP 404 ("Error 404 - Not Found") for every mobile and tablet browser, including Googlebot-smartphone.** Desktop gets 200. Reproduced 6 times with iPhone, Android, iPad and Googlebot user agents. Every other page tested is fine on mobile. prod30 does not have the bug, so it is in a change made on dev since the last deploy. | `/` on dev | Find what differs on dev for the front page (theme/front-page template, a mobile-detection plugin, or the "Homepage" page settings). Must be fixed and re-verified on production before launch, or most visitors and Google see a 404. |
| 2 | **Critical** | **Vulnerable plugin, admin takeover:** miniOrange "WordPress Social Login and Register" 7.6.7 is installed and active. CVE-2026-12761 (CVSS 9.8, disclosed 2026-07-10) lets an unauthenticated attacker take over an administrator account through the profile-completion OTP flow; it affects every version up to 7.7.0, fixed in 7.8.0. The plugin is not even configured: the login page shows "No apps configured. Please contact your administrator." | both environments | Remove the plugin now. If Google/Facebook login is wanted (the old site had both), install the current version and configure it, or use a different plugin. |
| 3 | High | **Plain HTTP is served without redirecting to HTTPS**, and the WordPress Address (siteurl) is `http://raresharedev30.wpenginepowered.com` (the REST index shows `url: http://…`, `home: https://…`). `http://…/wp-login.php` loads a working login form over HTTP and sets cookies. No HSTS. prod30 also answers plain HTTP with 200. | both | Set WordPress Address to https, turn on WP Engine "Secure All URLs" (forces the redirect), add `Strict-Transport-Security`. |
| 4 | High | **No security headers at all** on dev: no HSTS, `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, `Content-Security-Policy` or `Permissions-Policy`. prod30 has only a reCAPTCHA-related Permissions-Policy. The old site has `X-Frame-Options` and `nosniff`. | both | Add headers via WP Engine Web Rules or a headers plugin. |
| 5 | High | **Account enumeration.** `/wp-json/wp/v2/users` lists 6 accounts with login names (`admin`, `andynagai`, `carolli`, `estherwhang`, `jimkern`, `ui_redd`); prod30 lists 4. `/author/<login>/` confirms them. The BuddyPress REST API returns `user_login` for every member. An account literally named `admin` exists. wp-login.php is reachable (WP Engine's protection is on, `wpe-login=true`). | both | Restrict the users and BuddyPress members endpoints to logged-in requests, rename or retire `admin`, require 2FA for administrators, add login rate limiting. |
| 6 | High (launch) | **No redirect map from the old site's URLs.** The dev site has no redirect rules; what looks like redirects is WordPress guessing from the last path segment, which sends old URLs to unrelated pages (e.g. `/topics/why` goes to the post "Why I hate my kids' birthday", `/users/edit` goes to an Editas Medicine news item). Old community URLs (`/communities/<slug>`, 1,019 of them, the most-linked pages of the old site) 404 unless a page happens to share the slug. Details in §5. | launch | Build and test a redirect map before DNS cutover; disable or constrain `redirect_guess_404_permalink`. |
| 7 | High (launch) | **Outdated plugins with published issues:** Contact Form 7 5.8.7 (unauthenticated open redirect fixed in 5.9.5, June 2024; current is 6.1.x), WPForms Lite 1.10.0.4 (CVE-2026-48835, missing authorization, CVSS 7.5, affects ≤1.10.0.4), Akismet 5.3.1 and WP Mail SMTP 4.6.0 (both well behind). WPForms and Contact Form 7 are both installed; only CF7 forms are used. | both | Update everything; remove WPForms if unused. |
| 8 | Medium | **reCAPTCHA is misconfigured.** Three different site keys appear in page source (CF7 `6Lcc6A4s…`, `6LdwpA4s…`, and `6LdmH-UU…` from the BuddyPress reCAPTCHA plugin). On `/register/` the browser logs `Error: Invalid site key or not loaded in api.js: 6Lcc6A4s…`, so the CF7 newsletter form on that page cannot get a token. Keys are domain-bound and must be registered for the launch domain. | all pages | Use one key pair, register all domains, test the newsletter, contact and sign-up forms end to end. |
| 9 | Medium | **Sign-up page renders a giant unstyled caps-lock icon** between the password field and the form, with "Caps lock is on." always visible (WordPress core password UI markup without its admin CSS). Screenshot in `screenshots/register_capslock_bug.jpg`. | `/register/` | Hide `.wp-pwd .caps-lock`/dashicon until the JS toggles it, or load the core styles. |
| 10 | Medium | **Privacy posture for a patient community** (see §6): member directory, group member lists (411 names on the Systemic Capillary Leak Syndrome group), profile fields (city, gender, country), the site-wide activity feed and its RSS, and the REST API all expose "person X joined disease community Y" to anyone logged out. Avatars come from Gravatar (email hashes). | design decision | Decide what is public; the defaults are the most open option. |
| 11 | Medium (launch) | **SEO and indexing:** "Discourage search engines" is on (dev and prod30), so every page is `noindex, nofollow` and the sitemap is disabled; no meta descriptions anywhere; no `<h1>` on 2,132 of 2,200 pages; podcast and newsletter "detail" pages share one title and one canonical URL (`/podcast-detail/`), so none would be indexed individually; prod30 already has a stale URL in Google. | launch | Turn indexing on for production only, add an SEO plugin, fix titles/canonicals/H1s, redirect prod30 to the canonical domain after cutover. |
| 12 | Medium | **Images hot-linked from the old infrastructure** on 130+ pages: `rareshareprod.s3.amazonaws.com` (46 pages), `rareshare.org` (27), Mailchimp galleries (51, 7 already broken), `sendy.rareshare.org` over plain `http://` (mixed content, 6 pages), Google user content (7). These break when the old site, S3 bucket or Sendy server goes away. | content | Import into the media library and rewrite URLs. |
| 13 | Medium | **Test, sample and duplicate content** is live (see §4): "test-community", "Test Group", "Test Disease" groups, "This is a test" page, "Sample Page" with lorem ipsum, test forum topics inside real communities, two Privacy Policy pages (the cookie banner and the footer link to different ones), two Contact pages, newsletters and podcasts present three times. | content | Clean up before launch. |
| 14 | Medium | **Broken links:** 197 external links are dead (404/410/DNS), 6 of them to raregenomics.org pages; 22 point at old rareshare.org URLs that depend on the redirect map; 8 internal links to `/communities/<slug>` 404; 6 hrefs are malformed (e.g. `http://https://antidote.me/…`, `http://What%20My%20Family…`). | content | List in `data/broken_external_links.json`. |
| 15 | Medium | **Performance:** homepage is 1.4 MB over 43 requests with a 773 KB SVG; background PNGs of 530–940 KB; uploads up to 7.6 MB served unresized; uncached time-to-first-byte 1.2–3.9 s; member activity pages 6–8 s; 6 of 2,200 pages timed out (504) under 12 concurrent requests. | theme/media | Optimize images, check caching for BuddyPress pages. |
| 16 | Low | Theme build files are publicly readable (`package.json`, `vite.config.js`, `DEVELOPMENT.md`, `README.md`, `dist/manifest.json`, a 524 KB `screenshot.png`); `license.txt` is readable; the RSS feed and asset URLs disclose the WordPress version; Bootstrap 4.5.2 (end-of-life) is loaded from the legacy `maxcdn.bootstrapcdn.com` host without Subresource Integrity. | theme | Block non-asset files in the theme directory; self-host or drop Bootstrap. |
| 17 | Low | Accessibility (axe, WCAG 2.1 AA): 328 links without a name (logo and icon links on every page), 73 contrast failures (form placeholders and inputs), unlabeled sign-up checkboxes, unnamed country and sort selects, no H1s, 311 pages with heading-level skips. | theme | See §7. |
| 18 | Low | Email: `rareshare.org` SPF only authorizes Google (`include:_spf.google.com ~all`) and there is no DMARC record. If WP Mail SMTP sends through another provider from an @rareshare.org address, mail will fail SPF. | DNS | Add the sender to SPF, set up DKIM, publish DMARC. |
| 19 | Low | Housekeeping: footer reads "Copyright © 2026 All Rights Reserved Rareshare Genomics Institute."; "Articles" in the Resources menu links to `/?s#` (an empty search); timezone is a fixed UTC-8 offset with no named zone (no daylight saving); no site icon set in WordPress (favicon comes only from the theme); 86 posts carry migration suffixes (`-98`, `-news-link-126`), 3 pages carry UUID suffixes. | content | |

Things that are already right: WP Engine blocks `xmlrpc.php`, `readme.html`, `?author=N`, `wp-config.php`, `.env`, `.git`, `.htaccess`, `debug.log` and directory listings; search input is escaped (no reflected XSS); the dev site has `robots.txt` Disallow-all and noindex and is not in Google; a cookie notice is present; no third-party trackers or ad scripts load (only Google reCAPTCHA, Google Fonts, Libsyn and YouTube embeds); `viewport` and `lang` are set; no PHP warnings leak into pages; no unrendered shortcodes; every HTML page has a title; 397 of 405 image files resolve.

---

## 2. Security

### 2.1 Software versions (read from the plugins' own `readme.txt` files and asset URLs, 2026-11-02)

| Component | Installed | Status | Known issue in the installed version |
|---|---|---|---|
| WordPress core | 7.1.4 | current (security release of 2026-10-28) | none |
| BuddyPress | 14.5.4 | newer than the last security release I could find (14.5.2, 2026-07-29) | none found |
| bbPress | 2.6.21 | not checked against advisories | – |
| miniOrange Social Login and Register (`miniorange-login-openid`) | 7.6.7 | **vulnerable, unused** | CVE-2026-12761: unauthenticated authentication bypass to administrator account takeover via the profile-completion OTP flow, CVSS 9.8, affects ≤ 7.7.0, fixed in 7.8.0 |
| Contact Form 7 | 5.8.7 | outdated (6.1.x current) | unauthenticated open redirect, fixed in 5.9.5 (2024-06); further security changes in 6.0.6 (2025-04) |
| WPForms Lite | 1.10.0.4 | outdated, apparently unused | CVE-2026-48835 missing authorization (CVSS 7.5, ≤ 1.10.0.4); CVE-2026-7792 and CVE-2026-4986 concern payment flows |
| WP Mail SMTP | 4.6.0 (2025-08-26) | outdated (4.8.0 available) | none found |
| Akismet | 5.3.1 | outdated | none found |
| Cookie Notice / Compliance by Hu-manity | 3.1.4 | current | none found |
| reCAPTCHA for BuddyPress (`buddypress-recaptcha`) | 2.0.1 | not checked | – |
| Bootstrap CSS (maxcdn.bootstrapcdn.com) | 4.5.2 | end-of-life branch, legacy CDN, no SRI | – |
| jQuery / jQuery Migrate | 3.7.1 / 3.4.1 | current | – |

Also present: WP Engine's cache and sign-on plugins, "Search Exclude" (quadlayers), a custom theme `rare-share` (Vite build, version 4.0.0 in `package.json`).

### 2.2 Transport

- `http://raresharedev30.wpenginepowered.com/` answers 200 with the full page and `http://` links in it; no redirect to HTTPS. `http://…/wp-login.php` serves the login form and sets `wordpress_test_cookie`. Same on `http://prod30.rareshare.org/`.
- The REST index reports `url: http://raresharedev30.wpenginepowered.com` (WordPress Address) and `home: https://…` (Site Address). Set both to https.
- No `Strict-Transport-Security`.
- The TLS cipher/protocol configuration could not be tested from this environment (traffic goes through a TLS-terminating proxy). Run the Qualys SSL Labs test on the launch domain.

### 2.3 Disclosure and enumeration

| Check | Result |
|---|---|
| `/wp-json/wp/v2/users?per_page=100` | 200, 6 accounts with `slug` (login name) and author URLs; prod30: 4 |
| `/wp-json/buddypress/v1/members` | 200, 16 "active" members with `user_login`, name, profile fields (Full name, City, Gender, Country) |
| `/wp-json/buddypress/v1/xprofile/fields`, `/xprofile/<field>/data/<user>` | 200 logged out |
| `/wp-json/buddypress/v1/groups`, `/activity` | 200, 1,022 groups, 42 activity items |
| `/author/admin/`, `/author/<login>/` | 200 (confirms logins) |
| `/wp-content/themes/rare-share/{package.json,vite.config.js,DEVELOPMENT.md,README.md,dist/manifest.json,screenshot.png}` | 200 |
| `/license.txt` | 200 |
| `/feed/` generator tag, `?ver=7.1.4` on assets | WordPress version visible (it is current, so low impact) |
| Login page cookie `mo_openid_signup_url` | set by the unused miniOrange plugin, without `Secure`, containing an `http://` URL |

Blocked as expected (403 or 404): `xmlrpc.php` (GET and POST), `readme.html`, `?author=1`, `wp-config.php` and backups, `.env`, `.git/HEAD`, `.htaccess`, `wp-content/debug.log`, `phpinfo.php`, backup folders, `wp-content/uploads/` listing, `wp-includes/` listing, `/wp-json/wp/v2/settings` and `/plugins` (401). `wp-admin/install.php` and `wp-admin/maint/repair.php` answer with their harmless "already installed / repair disabled" pages.

### 2.4 Dev environment exposure

The dev site is publicly reachable without a password, and it holds real migrated data: thousands of forum posts under real member names, 1,022 disease communities with member lists, and profile pages. It is noindexed and not in Google, but anyone with the URL can read it. WP Engine can password-protect an environment in one click; do that until launch, and keep prod30 protected (or at least noindexed) until DNS cutover.

---

## 3. Functional bugs

### 3.1 Homepage 404 on mobile (critical)

| Request to `/` on dev | Status | WP Engine cache group |
|---|---|---|
| Desktop Chrome UA | 200 | normal |
| iPhone Safari UA (3 tries) | 404 | iphone |
| Android Chrome UA | 404 | iphone |
| iPad Safari UA | 404 | ipad |
| Googlebot smartphone UA | 404 | iphone |
| `/?p=12`, `/home/`, `/index.php` with iPhone UA | 301 to `/`, then 404 | |
| prod30 `/` with iPhone and Googlebot smartphone UA | 200 | |

The 404 is generated by WordPress (body class `error404`, title "Page not found – Rare Share", `cache-control: no-store`), not by the CDN. Other dev pages (`/about-us/`, `/groups/`, `/members/`, posts) are 200 on mobile. Screenshot: `screenshots/home_mobile_404.jpg`. Since the dev build is what will be promoted, this has to be found and fixed first; after deploying, re-test with a phone and with Google Search Console's URL inspection.

### 3.2 Sign-up page

- A large unstyled caps-lock SVG and the text "Caps lock is on." are always shown between the password field and the rest of the form (`screenshots/register_capslock_bug.jpg`). A second stray icon appears above the footer.
- The password field loads a 393 KB strength-meter script (`zxcvbn`); fine, but it is the largest asset on the page.
- Country select and the two consent checkboxes have no accessible names (axe `select-name`, `label`).
- Profile fields City/Gender/Country have visibility selectors; check the default visibility that BuddyPress applies for new sign-ups (see §6).

### 3.3 Login page

"No apps configured. Please contact your administrator." is shown under the form (the unused miniOrange plugin). Screenshot: `screenshots/login_no_apps_configured.jpg`.

### 3.4 reCAPTCHA

Page source contains three site keys. `api.js` is loaded with the CF7 key on most pages; on `/register/` the BuddyPress reCAPTCHA plugin loads its own, and the browser console shows `Error: Invalid site key or not loaded in api.js: 6Lcc6A4s…` (twice), i.e. the CF7 subscribe form in the footer cannot obtain a token there. `www.google.com/recaptcha/api2/pat` answered 401 for both keys, which is usually benign but worth a look in the reCAPTCHA admin console. Before launch: one key pair, all domains registered (`rareshare.org`, `www`, prod30, dev), then submit each form once and confirm the email arrives.

### 3.5 Navigation

"Articles" under Resources links to `/?s#`, which opens an empty search titled "Resources". The three menu parents are `#` links (fine on desktop with hover; the mobile menu toggle was not exercised in this review).

### 3.6 Capacity and timeouts

With 12 concurrent requests the crawl got six Cloudflare 504 "Gateway time-out" responses on ordinary posts and one on a member profile; all were 200 on retry. Member activity pages took 6–8 s uncached. Time-to-first-byte on uncached pages was 1.2–3.9 s (privacy policy 3.9 s). Worth a load test and a look at object caching before launch day traffic.

---

## 4. Migration and content

### 4.1 What is on the new site

| Content | Old site | New site (dev) |
|---|---|---|
| Disease communities | 1,019 links on `/communities` | 1,022 groups (all public), 65 with empty descriptions, 27 with numeric/UUID slug suffixes |
| Group members | e.g. SCLS: members listed | SCLS group: 411 members; group memberships migrated |
| Discussions | `/topics/<id>` | bbPress forum per group; SCLS forum has 567 topics; authors shown by real name, dates present |
| Articles / news links | `/articles/<slug>` | 1,237 posts (1,180 "External News Links", 28 podcasts, 16 newsletters, 3 guides), dates 2012-06 to 2026-09 |
| Pages | | 163 published |
| Members directory | | shows only 16 "active" accounts (the team's test accounts); migrated members exist (e.g. `/members/aporzeca/`, `/members/rnuara/` are 200) but do not appear because they have no BuddyPress last-activity record. Eight migrated profiles are titled "Anonymous User". |
| Media library | | 36 items; everything else is hot-linked (§4.4) |
| Ebooks, patient stories, video interviews | sections exist in the old nav (`/ebooks`, `/patient_stories`, `/video_interviews`) but render without items when fetched logged out | not found on the new site; confirm there is nothing to migrate |

A decision is needed on the members directory: either back-fill last-activity so migrated members appear, or hide the directory until people log in.

### 4.2 Test and sample content to remove

- Pages: `/this-is-a-test/`, `/sample-page/` (lorem ipsum, Flickr image over http), `/scripts/` (empty page), `/forums2/`, `/news/` (check they are needed).
- Groups: `/groups/test-community/` (14 members, description with placeholder links such as `https://another%20url`), `/groups/test-group/`, `/groups/test-disease/`.
- Forum topics: `…/systemic-capillary-leak-syndrome/forum/topic/testing-test/`, `…/13q-deletion-syndrome/forum/topic/testing-2/`, `…/adactylia-unilateral-dominant/forum/topic/this-is-a-test/`, a topic containing "xxx" in `12q-chromosome-deletion`.
- Comment: the default "A WordPress Commenter" comment on `/primary-sclerosing-cholangitis-clinical-trial/`.
- Activity feed items generated by the test accounts ("andynagai joined the group test-community").

### 4.3 Duplicates

- Two Privacy Policy pages: `/privacy-policy/` (1,502 words, 2024-02) and `/privacy-policy-2/` (3,133 words, 2026-08). The footer links to `-2`, the cookie banner's "Learn more" links to `/privacy-policy/`. Keep one, redirect the other.
- Two Contact pages (`/contact-us/`, `/contact-us-2/`).
- Newsletters exist three ways: `/april-2018-newsletter/`, `/april-2018-newsletter-103/`, and `/newsletter-detail/?newsletter_id=103`. Same for podcasts (`/podcast-detail/?podcast_id=N`). All `?…_id=` views share the title "Podcast Detail – Rare Share" / "Newsletter Detail – Rare Share" and canonicalize to the bare detail page.
- 17 post titles appear more than once (e.g. "Rare Disease Day 2023" ×3); 86 posts/pages carry numeric migration suffixes; 3 pages carry UUID suffixes; pairs like `/role-of-physical-therapist…/` and `/role-of-physical-therapists…/`, `/guide/` and `/rareshare-guide-on-genetic-inheritance/`, `/systemic-capillary-leak-syndrome/` and `/what-is-systemic-capillary-leak-syndrome/`.

### 4.4 Hot-linked images and mixed content

| Host | Pages | Note |
|---|---|---|
| rareshareprod.s3.amazonaws.com | 46 | old site's S3 bucket |
| rareshare.org | 27 | old site; also one `blob:` URL that can never load |
| cdn-images.mailchimp.com / gallery.mailchimp.com / mcusercontent.com | 54 | 7 already return 403 |
| sendy.rareshare.org | 6 | plain `http://`, mixed content |
| lh3.googleusercontent.com | 7 | Google-hosted |

### 4.5 Broken links

- Internal: 8 links to `/communities/<slug>` inside migrated posts (404; the matching groups exist at `/groups/<slug>/`), plus `/the-diagnostic-odyssey/UDN` and a link with a non-breaking space before `https:` on `/serving-the-undiagnosed/`.
- External: 2,103 unique URLs checked. 1,462 OK; **197 dead** (404/410/DNS); 232 returned 403 and 91 returned 429 (sites that block automated requests, unverified); 52 connection errors; 12 hosts could not be reached from this environment. Dead links include 6 to raregenomics.org (`/patient-application`, `/rgtf/`, `/rarewear/home`, `/press-releases/beheard-challenge-awards-21`, two blog posts) and 22 to old rareshare.org URLs (`/notifications/<slug>`, `/podcasts/<slug>`, `/ebooks/<slug>`), which only work after the redirect map exists. Full list with referring pages: `data/broken_external_links.json`.
- 6 malformed hrefs (`http://https://antidote.me/…` on the LELANTOS II page, `http://What%20My%20Family…`, and four placeholder URLs in the test community).

---

## 5. Launch readiness: URLs, redirects, indexing

### 5.1 Old URLs on the new site today

| Old URL pattern | On dev today | Suggested target |
|---|---|---|
| `/communities` | 404 | `/groups/` |
| `/communities/<slug>` | 404, or a guessed page when a page shares the slug | `/groups/<slug>/` (slugs match for all 11 sampled) |
| `/topics/<id>` | 404, or a guessed unrelated post | the migrated bbPress topic (needs an id map from the migration) |
| `/articles` | 404 | `/news-links/` or the posts archive |
| `/articles/<slug>` | 301 to `/<slug>/` by guessing only | explicit rule |
| `/users/sign_in`, `/users/sign_up` | 404 | `/log-in/`, `/register/` |
| `/users/auth/google_oauth2`, `/users/auth/facebook` | 404 | social login, if kept |
| `/users/<id-or-slug>` | 404 / guessed | `/members/<slug>/` (needs a map) |
| `/pages/faq` (+ `#terms_of_Service`, `#privacy_Policy`, `#cookies_Policy`) | 301 to `/about-us/faq/` by guessing | explicit; anchors to Terms/Privacy pages |
| `/contact_us`, `/news_links`, `/home/leader_list` | 404 | `/contact-us/`, `/news-links/`, `/volunteer-community-leader-list/` |
| `/podcasts`, `/newsletters`, `/guides` | 301 by guessing | explicit |
| `/notifications/<slug>` (old announcements, linked from newsletters) | 404 | the migrated page (22 such links found) |
| `/ebooks`, `/ebooks/<slug>`, `/patient_stories`, `/video_interviews` | 404 | decide |

### 5.2 WordPress 404 guessing

With `redirect_guess_404_permalink` active and a `/%postname%/` structure, any unknown URL whose last segment prefixes a post or page slug gets a 301. Evidence: `/zzz/why-rare-diseases` → `/why-rare-diseases/`; `/communities/systemic` → the SCLS page; `/topics/why` → `/why-i-hate-my-kids-birthday/`; `/users/edit` → `/editas-medicine-gets-fda-rare-pediatric-disease-designation-for-edit-301/`. This will quietly mis-route old bookmarks and search results. Add real rules and turn the guessing off (or restrict it to exact matches).

### 5.3 Indexing and SEO checklist

- "Discourage search engines" is on for dev and prod30 (`<meta name='robots' content='noindex, nofollow'>` on all 2,200 pages, `wp-sitemap.xml` 404, `/sitemap.xml` redirects to it). Turn it off on production only, at cutover.
- prod30.rareshare.org is indexed by Google (`?p=15`). After cutover redirect prod30 and `www` to the canonical domain.
- No meta descriptions, no Open Graph tags (no SEO plugin). Page titles on the BuddyPress directories, register page and homepage are just "Rare Share".
- No `<h1>` on 2,132 pages (the homepage headline is an `<h3>`, post titles are `<h2>`).
- Podcast/newsletter detail URLs collapse to one canonical (§4.3).
- reCAPTCHA keys and any OAuth redirect URIs must include the launch domain.
- Run a search-and-replace for the dev hostname at deploy time (it is in 2,199 pages' HTML; WP Engine's copy does this, verify).
- Timezone: set a named zone; site icon: set in Customizer.

### 5.4 Email

`rareshare.org` TXT: `v=spf1 include:_spf.google.com ~all`; MX: Google; `_dmarc.rareshare.org`: none. If WP Mail SMTP sends via anything other than Google Workspace, add it to SPF and set DKIM; publish a DMARC record (start with `p=none`). Then test sign-up, password-reset, contact and subscribe emails from production.

---

## 6. Privacy posture (decisions for Jimmy)

What a logged-out visitor, crawler or RSS reader can see today:

- Members directory (`/members/`) with names and "Active 2 weeks ago"; member profile pages with Full name, City, Gender, Country when set to public; profile sub-pages (activity, groups, forums).
- Every group's member list (`/groups/<slug>/members/`, e.g. 411 names for SCLS). Membership of a disease community reveals a health condition of the member or a family member.
- The site-wide activity stream (`/activity/`) and its RSS (`/activity/feed/`): "X joined the group Y", "X became a registered member".
- Forum posts with real names (these were public on the old site too).
- All of the above in machine-readable form via the REST API, including `user_login`.
- Avatars from Gravatar carry a hash of the member's email, which third parties use to link identities across sites.

Options, from least to most restrictive: leave as is (matches the old site); make directories, group member lists and the activity stream visible to logged-in members only and restrict the BuddyPress REST endpoints accordingly; additionally hide profile fields by default and switch to local avatars (no Gravatar). Whatever is chosen, the Privacy Policy should describe it, and the sign-up defaults for field visibility should match.

---

## 7. Accessibility (axe-core 4.10, WCAG 2.0/2.1 A and AA, 23 pages desktop + 4 mobile)

| Rule | Impact | Nodes | Examples |
|---|---|---|---|
| link-name | serious | 328 | header and footer logo links, search icon link, social icon links (every page) |
| color-contrast | serious | 73 | input placeholders (`First name`, `#signup_email`), muted text |
| label | critical | 4 | sign-up checkboxes "I accept the Privacy Policy", "I am at least 18 years of age" |
| select-name | critical | 3 | country select (`#field_7`), directory sort selects |
| link-in-text-block | serious | 1 | activity stream links |

Also: no H1 anywhere; heading-level skips on 311 pages; 11 images without an `alt` attribute (most images carry empty `alt`, which is fine for decoration); on mobile, the activity page has 102 tap targets smaller than 24 px and the groups directory has 55 text elements under 12 px; no horizontal overflow on any page tested; `lang="en-US"` and the viewport meta are set. Per-page detail: `data/browser_audit_playwright_axe.json`.

---

## 8. Performance (headless Chromium, cold cache, desktop)

| Page | TTFB | Load | Requests | Transfer | Largest assets |
|---|---|---|---|---|---|
| `/` | 0.6 s | 4.3 s | 43 | 1,419 KB | `homepage-ornament.svg` 773 KB, reCAPTCHA 348 KB |
| `/register/` | 0.2 s | 3.6 s | 64 | 865 KB | `zxcvbn.min.js` 393 KB, reCAPTCHA 351 KB |
| `/groups/` | 0.2 s | 3.0 s | 54 | 1,192 KB | `hero-green-background.png` 607 KB, `news-background.png` 581 KB |
| `/privacy-policy-2/` | 3.9 s | 6.4 s | 40 | | |
| `/members/carolli/` | 2.1 s | 4.8 s | 55 | | |

Crawl of 2,200 URLs: median 1.4 s per page; 120 pages over 3 s; largest uploads served at full size: 7.6 MB (`CSC_Staff_Photo.jpg`), 5.2 MB, 2.8 MB. Nearly every crawled page was a cache MISS (`x-cache: MISS` on 2,159 of 2,200).

---

## 9. Not tested in this part

See `prelaunch_review_part2_2026-11-02.md` (same folder, same day) for TLS configuration (SSL Labs grade A), form submissions, email delivery, logged-in behaviour, the admin side and a ramped load test. Still untested after part 2: logged-in behaviour and the admin side (both need an account), email delivery end to end, the mobile menu interaction, the old site's logged-in sections (ebooks, patient stories, video interviews), plugin code (no file access).

---

## 10. Files in this folder

- `data/crawl_summary.txt`: status, SEO, content and performance summary of the 2,200-URL crawl, 405 image files and 2,103 external links.
- `data/broken_external_links.json`: the 197 dead external links with the pages they are on.
- `data/browser_audit_playwright_axe.json`: per-page console errors, failed requests, timings, axe violations (desktop and mobile).
- `data/wordpress_path_probe.txt`: status of 70 well-known WordPress paths and REST endpoints.
- `data/content_inventory.json`: counts and lists of pages, groups sample, public member profiles, media.
- `screenshots/`: homepage desktop and mobile (404), sign-up page bug, login page message, groups directory with test groups.
- Part 2 (`prelaunch_review_part2_2026-11-02.md`) adds `data/ssllabs_*.json`, `data/obs_*.json`, `data/loadtest_results.json`, `data/loadtest.py`, `data/functional_test_results.json`, `data/functional_v3.js` and `screenshots/register_after_submit.jpg`.

## Sources for the version and vulnerability statements

- WordPress 7.1.4: https://wordpress.org/support/wordpress-version/version-7-1-4/ and https://docs.pantheon.io/release-notes/2026/10/wordpress-7-1-4
- miniOrange CVE-2026-12761: https://www.wordfence.com/threat-intel/vulnerabilities/wordpress-plugins/miniorange-login-openid/miniorange-social-login-and-register-discord-google-twitter-linkedin-770-unauthenticated-authentication-bypass-to-administrator-account-takeover-via-profile-completion-otp-flow , https://www.incibe.es/en/incibe-cert/early-warning/vulnerabilities/cve-2026-12761 , https://dbugs.ptsecurity.com/vulnerability/PT-2026-57277
- Contact Form 7 history: https://patchstack.com/database/wordpress/plugin/contact-form-7/vulnerabilities , https://github.com/rocklobster-in/contact-form-7/releases , https://contactform7.com/2025/04/10/contact-form-7-606/
- WPForms Lite: https://notcve.org/vendors/wpforms/ , https://www.wordfence.com/threat-intel/vulnerabilities/wordpress-plugins/wpforms-lite/wpforms-lite-1501-202-unauthenticated-arbitrary-shortcode-execution
- WP Mail SMTP: https://patchstack.com/database/wordpress/plugin/wp-mail-smtp/vulnerabilities
- BuddyPress releases: https://codex.buddypress.org/version-14-5-2/ , https://patchstack.com/database/wordpress/plugin/buddypress/vulnerabilities
- Cookie Notice: https://patchstack.com/database/Wordpress/Plugin/cookie-notice/vulnerabilities
