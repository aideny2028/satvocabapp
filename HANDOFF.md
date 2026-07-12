# SAT Vocabulary Trainer — Handoff

**URL**: https://aideny2028.github.io/satvocabapp/ · **Repo**: https://github.com/aideny2028/satvocabapp
**Stack**: vanilla HTML/CSS/JS, no build step, GitHub Pages, all state in localStorage (`sat_vocab_v4`).
**Last major overhaul**: July 2026 (full audit + rebuild — see git log for the commit series).

## Files

| File | Purpose |
|---|---|
| `index.html` | Single page; inline theme script in `<head>` (no dark flash); PWA manifest + icons linked |
| `app.js` | All app logic (readable, formatted — no longer minified) |
| `style.css` | All styles; light/dark via CSS custom properties; mobile at `@media(max-width:600px)` |
| `words.js` | `const W = [{w,p,d,diff,hu?}, ...]` — `hu:true` marks high-utility digital-SAT words |
| `sentences.js` | `const SENTENCES = {word: [[sentence,d1,d2,d3] x6]}` — one `_____` blank each |
| `contextq.js` | Original SAT-format passage questions (`CONTEXTQ`) for the "Words in Context" type |
| `ai.js` | BYOK AI tutor (Gemini `gemini-2.0-flash` / Claude `claude-haiku-4-5`); key in localStorage only, never exported |
| `templates.js` | Fallback sentence generators (rarely used; generic fallback for conj./prep.) |
| `sw.js`, `manifest.json`, `icon*` | PWA: offline app-shell cache (bump `CACHE_VERSION` in sw.js when deploying data changes) |
| `audit.js` | `node audit.js` — full machine audit of words/sentences using the app's real conjugation/article rules. Must print ALL CHECKS PASS before any data commit. |

## Key behaviors (post-overhaul)

- **Dates are local-timezone** (`dateKey()`), never `toISOString` — streaks/calendar/Leitner due dates.
- **Six question types**: wordToDef, defToWord, sentence, synonym (true near-synonym matching when one exists), context ("most nearly means" on a real sentence), passage (official digital-SAT stem, original passages from contextq.js). Per-word rotation via least-used counters in `state.leitner[i]` (`wt/dw/sc/sy/cx/pq`).
- **Distractor engine**: same-POS required, same-difficulty preferred, near-synonym guard (`setSim >= 0.4` excluded), confusable-lookalike bonus, precomputed `DEF_TOKEN_SETS`.
- **Retry system**: wrong answer re-queues the word 4–8 questions later (once, no double stats); session selection caps review words at 1/3 and excludes words already missed today.
- **Sessions persist** (`state.currentSession`) — resume offer on the start screen.
- **Conjugation**: `IRREG_PAST` map + doubling set handle suffix blanks (`_____ed` etc.); articles chosen by sound ("a uniform", "an honest").
- **Import** is deep-validated (`sanitizeImport`); state-derived strings escaped with `esc()` before innerHTML.
- **Flag button** (Bluebook parity) during quiz; flagged words appear in Review; per-option × eliminator works on touch.

## Workflow

- Serve locally: `python3 -m http.server 8735 --directory .` (service worker needs http).
- Data changes: edit via script, then `node --check` each file and `node audit.js`.
- Deploy: commit to `main`, push — GitHub Pages auto-deploys. **Bump `CACHE_VERSION` in sw.js** whenever shipped files change, or returning PWA users keep the old cache until the background refresh.
- Push: `git push origin main` (works from this machine; credentials in macOS keychain).

## Content pipeline (July 2026)

- Word expansion + full sentence-bank editorial revamp ran as agent workflows; validation scripts live in the session scratchpad (`integrate-words.js`, `apply-fixes.js`) — both regenerate/append data files and are guarded by `audit.js`.
- Every quiz sentence is machine-audited (blank shape, distractor count/quality, answer/root leaks, conjugation validity, article correctness) and the bank was editorially reviewed against the digital-SAT rubric: context clue must force the answer; distractors must be excluded, not just worse.
