# RareShare 3.0 pre-launch review, part 2: TLS, forms, email, logged-in behaviour, load, admin

*2026-11-02, follow-up to `prelaunch_review_2026-11-02.md` at Jimmy's request. Same site (https://raresharedev30.wpenginepowered.com), same rules: nothing on the site was changed except the test artefacts listed in §9, which are labelled for deletion.*

## 1. TLS configuration (Qualys SSL Labs, assessment not published, 2026-11-02)

The container's outbound proxy terminates TLS, so ciphers could not be negotiated directly; the Qualys SSL Labs scanner was used instead, against both WP Engine hosts. Raw results: `data/ssllabs_*.json`.

| | raresharedev30.wpenginepowered.com | prod30.rareshare.org |
|---|---|---|
| Grade | **A** (both IPs: 141.193.213.10, .11) | **A** (same two IPs) |
| Protocols | TLS 1.2, TLS 1.3 only | same |
| Certificate | Let's Encrypt, wildcard `*.wpenginepowered.com`, RSA 2048, SHA-256, no issues, valid to 2027-01 | Let's Encrypt, `prod30.rareshare.org` only, RSA 2048, valid to 2026-12 (auto-renewed by WP Engine) |
| Forward secrecy | robust (every simulated client) | same |
| Known weaknesses tested | none: no RC4, Heartbleed, POODLE, FREAK, Logjam, DROWN or ROBOT; secure renegotiation; no compression; 0-RTT off | same |
| Cipher suites | TLS 1.3: 3 modern suites. TLS 1.2: 20 suites, of which 14 are marked *weak* by SSL Labs (CBC-mode suites and static-RSA key exchange such as `TLS_RSA_WITH_AES_128_GCM_SHA256`); they only matter for very old clients | same |
| HSTS | absent (this is what keeps the grade at A rather than A+) | absent |
| OCSP stapling | off | off |
| Clients that cannot connect | Android 2.3–4.3, IE 6–10, Java 6 (expected, all end-of-life) | same |

Verdict: the transport layer is sound; the only actionable items are the ones already in part 1 (HSTS, forcing HTTPS). The cipher list is Cloudflare/WP Engine's default and cannot be changed from WordPress; if the static-RSA suites bother the security reviewer, ask WP Engine. The wildcard certificate is also why the mistyped `raresharedev3.0.…` hostname fails: a wildcard covers one label only.

Mozilla HTTP Observatory (headers, cookies, CSP): **grade F, score 5/100, 6 of 12 tests passed**, on both hosts. Raw results: `data/obs_*.json`. This repeats part 1 §2.2.

## 2. Form submissions

Submissions were made from a real headless Chromium with a throwaway inbox (`rs30testphktu9@fldubai.com`, mail.tm) as the sender/recipient.

### 2.1 Contact form (`/contact-us/`, Contact Form 7 form 16)

- Fields: First name*, Last name*, Subject*, Company/Organization, Email*, Message*. The first attempt that left first/last name empty was correctly rejected client-side ("One or more fields have an error").
- With every field filled, the server answered the submission with `status: "spam"`, and the visitor saw **"There was an error trying to send your message. Please try again later."** No email was sent (the response says `posted_data_hash: ""`).
- Cause candidates, in order of likelihood: reCAPTCHA v3 scoring the headless browser below the threshold; Akismet 5.3.1 (installed) flagging it; the reCAPTCHA key conflict from part 1 §3.4. The site does not tell the visitor which, and the wording blames a transient error rather than a spam decision, so a real person who is wrongly flagged (VPN, privacy browser, corporate network) will retry and fail again.
- Action: submit the form once from a normal browser and confirm the email arrives in the configured mailbox (the recipient address is only visible in the admin side); check the CF7 reCAPTCHA threshold (Contact > Integration) and whether Akismet is wired to this form; consider a plain mailto fallback in the error text.

### 2.2 Newsletter sign-up (Contact Form 7 form 34, "Subscribe")

- The markup is on every page inside `#popup-subscribe` (a Magnific Popup container with `mfp-hide`, `display: none`).
- **Nothing on the site opens it.** No link, button or menu item references the popup, so visitors cannot subscribe anywhere. The form could not be submitted in testing for the same reason.
- Action: either add the trigger (the theme's footer probably used to have a "Subscribe" button) or remove the dead markup and its reCAPTCHA load from every page. Also decide where subscriptions go: a CF7 form only emails the admin; it does not add anyone to Mailchimp/Sendy, which the old newsletters were sent from.

### 2.3 Sign-up form defaults (`/register/`)

- The password field is pre-filled with a WordPress-generated strong password (`#pass1`, shown as plain text); the confirm field is hidden. Fine, but the visible "Caps lock is on." widget from part 1 sits right under it.
- **Profile field visibility defaults to "Public"** for City, Gender and Country (radio groups `field_2/3/7_visibility`, options public / adminsonly / loggedin). Combined with part 1 §6 this means a new member's city and gender are world-readable unless they click "Change" during sign-up. Consider defaulting to "Only Me" or "All Members" (BuddyPress: Users > Profile Fields > field > Visibility, and untick "Allow members to override" if the default should be enforced).

### 2.4 Sign-up submission

- The sign-up form carries a **reCAPTCHA v2 "I'm not a robot" checkbox** (site key `6LdmH-UU…`, from the reCAPTCHA for BuddyPress plugin). This is a good control, and it is also why the automated registration stopped here: the checkbox cannot be, and was not, bypassed. Screenshot: `screenshots/register_after_submit.jpg`.
- Two more bugs are visible on that screenshot:
  - **Duplicate privacy checkbox outside the form.** The page contains two inputs with `id="signup-privacy-policy-accept"`: one inside `#signup-form` and one after `</form>`, rendered as a stray checkbox floating above the footer (the "second stray icon" from part 1 §3.2). A third consent box (`privacy_policy`) is also inside the form. Ticking the stray one does nothing; duplicate ids also break the label association for screen readers.
  - **Gender is pre-selected as "Male".** The select does have a blank "----" option, but "Male" carries `selected` because it is set as the field's default option (Users > Profile Fields > Gender). Every member who skips the field is recorded as Male. Clear the default.
- Because the CAPTCHA was not completed, no account and no pending sign-up were created; nothing needs deleting.

## 3. Email delivery

Not verified. The only logged-out actions that send email are the contact form (rejected as spam, §2.1), the newsletter form (unreachable, §2.2), sign-up (blocked by the CAPTCHA, §2.4) and password reset (which I did not trigger, because it would email a real member). What is known:

- The site runs WP Mail SMTP 4.6.0, so mail is probably routed through an SMTP/API provider rather than PHP `mail()`; which provider, and whether it is configured on the dev environment at all, is only visible in the admin side (WP Mail SMTP > Settings, and its Email Log if enabled).
- `rareshare.org` publishes SPF for Google only and no DMARC (part 1 §5.4). If the provider is not Google Workspace, mail from `@rareshare.org` will fail SPF at Gmail/Outlook unless the provider is added and DKIM is set up.
- WP Engine's own outbound mail is rate-limited and intended for transactional mail only; bulk newsletters should stay on Mailchimp/Sendy.

Five-minute manual test (needs a normal browser and one inbox you control, ideally Gmail or Outlook):
1. Sign up with that address; note how long the activation email takes and whether it lands in spam. Open the message's "Show original" to read `Authentication-Results` (SPF/DKIM/DMARC pass/fail) and the sending host.
2. Click the activation link, log in, then use "Forgot password" and time that email too.
3. Submit the contact form; confirm it arrives at the configured recipient and that replying goes to the visitor's address.
4. Change the account email under Settings; confirm the verification email.
5. Join a group and post a reply to a topic that another test account subscribed to; confirm the notification email, and that its unsubscribe link works.

## 4. Logged-in behaviour

Not tested: no account could be created automatically (§2.4) and no test credentials were available. The test script is ready (`data/functional_v3.js`, run with `SKIP_FORMS=1 SKIP_REGISTER=1` and a `creds.json` holding a test member's username and password). With a plain *member* account (not an admin) it checks, in about five minutes:

- login cookie flags (`Secure`, `HttpOnly`, `SameSite`), the landing page after login, and that logged-in pages are not cached by WP Engine (`x-cache`, `cache-control`) nor served to logged-out visitors afterwards;
- authorization: that `/manage-users/`, `/manage-communities/`, `/manage-guides/`, `/manage-news-links/`, `/manage-newsletters/`, `/manage-podcasts/`, `/start-a-community/` and `/wp-admin/users.php`, `edit.php`, `plugins.php`, `options-general.php` are refused for a member (part 1 only showed they redirect for logged-out visitors);
- profile edit, the visibility controls a member actually gets, and HTML escaping of a profile field (`<b>` in City must render as text);
- joining `test-community`, posting an activity update, creating a forum topic and a reply there (and nowhere else);
- notifications, settings, delete-account and messages pages; the REST API as a member (`users/me?context=edit`, `settings`, `users?context=edit`);
- the mobile homepage while logged in; logout; and a password reset for the test account only, timing the email.

To run it I need either a test member account created by you (username + password, on the dev site, which you delete afterwards), or your go-ahead to complete one sign-up by hand in a normal browser and hand me the credentials. Everything the script creates is labelled "automated pre-launch test" and confined to the test community.

## 5. The admin side

Not tested: it needs an administrator session, and there is no safe way to obtain one from outside. Two options: a temporary administrator account on the dev environment that you delete after the review (an Editor account covers most of the content checks but none of the settings), or you walk the checklist yourself. Either way, these are the things to look at, in order:

**Settings**
- General: WordPress Address and Site Address both `https://…`; timezone set to a named zone (currently fixed UTC-8); site icon set; "Anyone can register" and the default role (Subscriber).
- Reading: "Discourage search engines" off on production only; front page = "Homepage" (compare dev vs prod to find the mobile 404 of part 1 §3.1).
- Permalinks: `/%postname%/`; note any custom rules.
- Discussion: comments on posts (the default WordPress comment is still live); avatars (switch off Gravatar for a patient community, part 1 §6).
- Privacy: which page is set as the Privacy Policy page (there are two).
- BuddyPress > Settings: components enabled (Messages seem off), account deletion, profile sync, "@" mentions; BuddyPress > Profile Fields: default visibility and "allow members to override" for City, Gender, Country; group creation permission ("Start a Community" page); activity stream visibility and the activity RSS.
- bbPress > Settings: who can create topics/replies, anonymous posting (must be off), throttle time, editing window, forum/topic/reply slugs, "Forum Root" (the `/forums2/` page suggests an earlier attempt).
- WP Mail SMTP: mailer, from-address, test email; Email Log.
- Contact Form 7 > Integration: reCAPTCHA keys (one pair for the whole site); each form's recipient; Akismet integration. The "Subscribe" form 34: where it sends.
- reCAPTCHA for BuddyPress: which forms it protects, v2 vs v3, keys.
- miniOrange Social Login: delete (part 1 finding 2), unless Google login will be configured on the current version.
- Cookie Notice: the "Learn more" link target (points at `/privacy-policy/`, the older of the two).
- WP Engine (User Portal, not wp-admin): Secure All URLs; password-protect the dev environment; Web Rules for security headers and the redirect map; cache exclusions for BuddyPress pages; CDN; backups schedule and a restore test; environment PHP version.

**Users**
- Users list: how many accounts came over from the old site, how many are administrators; rename or demote `admin`; delete the team's test accounts after launch; enable two-factor auth for administrators (no 2FA plugin is installed); application passwords in use.
- Look at one migrated member (e.g. `aporzeca`): role, email present, display name, whether a password reset will work for them at launch (they will all need one if password hashes did not migrate).
- Eight profiles display as "Anonymous User": decide whether to delete or hide them.

**Content**
- Pages: delete or unpublish `this-is-a-test`, `sample-page`, `scripts`, the duplicate privacy/contact pages, UUID-suffixed duplicates; check what `forums2`, `news`, `guide-detail`, `newsletter-detail`, `podcast-detail` are for.
- Groups: delete `test-community`, `test-group`, `test-disease` (and their forums); check the 65 groups with empty descriptions.
- Forums: delete the test topics listed in part 1 §4.2; spot-check that migrated topics kept their authors and dates.
- Media: 36 items only; plan the import of the hot-linked images (part 1 §4.4).
- Menus: fix the "Articles" item (`/?s#`).

**Site Health (Tools > Site Health)**
- Status page: PHP version, HTTPS status, object cache, scheduled events, REST availability, "debug mode" off, file editor disabled (`DISALLOW_FILE_EDIT`), automatic updates; Info > Server for the PHP memory limit and upload limit (uploads of 7.6 MB got through).
- Plugins: update everything; delete deactivated plugins; keep a changelog of what was removed.

## 6. Load beyond modest concurrency

A ramped test from one client (this container's egress), four steps of 45 s each, request mix 20% homepage, 15% groups directory, 10% a group page, 5% members directory, 30% a random post, 10% a random search, 10% news links; roughly half the requests were WP Engine cache hits, the rest went to PHP. The script (`data/loadtest.py`-style, results in `data/loadtest_results.json`) aborts automatically if recent requests start failing. No login, no POSTs. Total duration under four minutes.

| Concurrent clients | Requests | Throughput | 200 | 504 | p50 | p95 | p99 | max |
|---|---|---|---|---|---|---|---|---|
| 5 | 389 | 8.6 req/s | 389 | 0 | 0.16 s | 1.5 s | 2.2 s | 2.8 s |
| 10 | 353 | 7.4 req/s | 353 | 0 | 1.7 s | 3.3 s | 3.7 s | 4.1 s |
| 20 | 422 | 8.5 req/s | 422 | 0 | 0.15 s | 6.4 s | 7.3 s | 7.9 s |
| 30 | 1,775 | 34 req/s (inflated by fast failures) | 1,248 | **527 (30%)** | 0.10 s | 6.3 s | 7.9 s | 9.5 s |

Reading it:
- Throughput of successful requests is flat at about 8 per second from 5 clients upward: that is the point where the PHP workers behind this environment are saturated. Above it, requests queue (p95 climbs from 1.5 s to 6.4 s) and at 30 clients Cloudflare starts returning **504 Gateway time-out** for 3 in 10 requests within the first minute. No request was challenged or rate-limited by Cloudflare; nothing came back 403 or 429.
- Cache hits (about half of the mix) stayed fast throughout (p50 ≈ 0.1–0.2 s). The pain is entirely in uncached pages, which is what every logged-in member sees for every page.
- In practical terms: on this environment, 10 simultaneous logged-in members get 2–4 s pages, 20 get 6–8 s, and 30 get errors. Rare Disease Day or a newsletter send could produce that in minutes.

Caveats: this was one client, one IP, one region, for 45 s per step, against the *dev* environment. WP Engine environments of one install share the plan's resources, so production should behave much the same, but a dev environment can have extra plugins or debugging enabled. I could not find a published WP Engine rule on customer load testing; before a fuller test (several regions, longer steps, a logged-in mix) tell WP Engine support what you plan, since their edge protection may otherwise treat it as an attack and since they can watch the backend while it runs.

What to do with it: ask WP Engine which plan tier the site is on and what the PHP worker count is; enable their object cache (Redis) if not already on; make sure BuddyPress directory pages, group pages and forums are cached for logged-out visitors (every crawled page was a cache MISS in part 1); shrink the uncached work per page (the member activity pages took 6–8 s on their own); then re-test at 20–50 clients on production before launch.

## 7. Artefacts and clean-up

- Contact form: one test submission attempt (sender `rs30testphktu9@fldubai.com`, subject "RareShare 3.0 pre-launch test (automated, please ignore)"); it was rejected as spam, so nothing should have been emailed or stored. If a spam-logging plugin exists, the entry can be deleted.
- Sign-up: one attempt for username `rs30test_phktu9`, stopped at the CAPTCHA. No activation email was sent. If Users > Manage Signups on the dev site nevertheless lists it, delete it.
- Nothing else was created, joined, posted or changed. The throwaway inbox was emptied of nothing because nothing arrived.

## 8. Still open after this part

| Area | Status | What unblocks it |
|---|---|---|
| TLS | done, grade A | HSTS and forced HTTPS (part 1) |
| Form submissions | contact form rejected as spam, newsletter form unreachable, sign-up stops at CAPTCHA | one manual submission of each from a normal browser; fix §2.2 |
| Email delivery | not verified | the five-step manual test in §3, or WP Mail SMTP's log from the admin side |
| Logged-in behaviour | not tested; script ready | a test member account on dev, or permission to complete one sign-up by hand |
| Admin side | not tested; checklist in §5 | a temporary administrator (or editor) account on dev, or you run the checklist |
| Load | tested to 30 clients from one location; backend saturates at ~8 uncached req/s | coordinated test on production with WP Engine |
