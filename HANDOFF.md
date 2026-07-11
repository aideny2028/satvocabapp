# SAT Vocabulary Trainer — Complete Handoff Document

**Project**: SAT Vocabulary Quiz App
**URL**: https://aideny2028.github.io/satvocabapp/
**Repo**: https://github.com/aideny2028/satvocabapp
**Hosting**: GitHub Pages (static site, no backend)
**Owner**: Aiden (misteryeoh@gmail.com)
**Date**: July 11, 2026

---

## TABLE OF CONTENTS

1. [Project Overview](#1-project-overview)
2. [File Architecture](#2-file-architecture)
3. [Data Formats](#3-data-formats)
4. [App.js Complete Logic Map](#4-appjs-complete-logic-map)
5. [CSS Architecture](#5-css-architecture)
6. [Current State & Statistics](#6-current-state--statistics)
7. [Known Bugs (Code Audit)](#7-known-bugs-code-audit)
8. [Data Quality Audit Results](#8-data-quality-audit-results)
9. [User Feedback (Unresolved)](#9-user-feedback-unresolved)
10. [UI/UX Research Findings](#10-uiux-research-findings)
11. [AI Chatbot Integration Plan](#11-ai-chatbot-integration-plan)
12. [SAT Research Findings](#12-sat-research-findings)
13. [Pending Tasks & Priorities](#13-pending-tasks--priorities)
14. [Git History & Push Instructions](#14-git-history--push-instructions)
15. [Development Workflow](#15-development-workflow)

---

## 1. PROJECT OVERVIEW

A single-page static web app for SAT vocabulary study. Pure vanilla HTML/CSS/JS — no frameworks, no build step, no backend. Deployed to GitHub Pages via `git push origin main`.

**Core Features:**
- Quiz mode with 4 question types: Define the Term, Identify the Word, Sentence Completion, Closest in Meaning
- 1,715 vocabulary words with 10,143 fill-in-the-blank sentences
- Leitner spaced repetition system (6 boxes: New, Box 1-4, Learned)
- Word list with search, sort (A-Z, Z-A, most/least missed), filter by difficulty
- Review tab for missed words with "Practice These" button
- Record tab with accuracy chart (SVG), session history, mastery bar, difficulty breakdown
- Calendar view with streak tracking, daily goal progress
- Settings: daily goal, question types toggle, timed mode, retry toggle, export/import
- Dark mode (CSS custom properties with `[data-theme="dark"]`)
- Keyboard shortcuts (1-4 select option, Enter confirm, Esc exit, right-click cross-out)
- Difficulty filter (Easy/Medium/Hard) for practice sessions
- Customizable session size (10/20/30/50/Unlimited/Custom)
- Optional countdown timer (15s/20s/30s/45s/60s)

**Tech Stack:**
- HTML5 (single index.html)
- Vanilla CSS (1,302 lines, custom properties for theming)
- Vanilla JavaScript (88 lines of dense/minified code in app.js)
- Data in separate JS files: words.js (1,718 lines), sentences.js (61,592 lines), templates.js (236 lines)
- All state in localStorage under key `sat_vocab_v4`

---

## 2. FILE ARCHITECTURE

```
satvocabapp/
├── index.html      (80 lines)   — Single page, all views as divs, script tags at bottom
├── style.css       (1,302 lines) — All styles, light/dark themes, responsive, animations
├── app.js          (88 lines)    — All application logic (heavily minified)
├── words.js        (1,718 lines) — Word database: const W = [{w,p,d,diff}, ...]
├── sentences.js    (61,592 lines)— Sentence database: const SENTENCES = {"word": [[sentence, w1, w2, w3], ...], ...}
├── templates.js    (236 lines)   — Fallback sentence generators for words without pre-written sentences
├── HANDOFF.md      (this file)
└── .git/
```

### index.html Structure

```html
<body>
  <div class="container">
    <header> <!-- Title + theme toggle --> </header>
    <div class="nav"> <!-- 6 tab buttons: Practice, Words, Review, Record, Calendar, Settings --> </div>
    <div id="quizView">
      <div id="dailyBanner"> <!-- Today's progress bar + streak --> </div>
      <div id="startScreen"> <!-- Start button + Customize panel --> </div>
      <div id="quizActive" class="hidden"> <!-- Timer, question card, options, feedback --> </div>
      <div id="summaryView" class="hidden"> <!-- Post-session results --> </div>
    </div>
    <div id="calendarView" class="hidden"> <!-- Streak display + monthly calendar --> </div>
    <div id="reviewView" class="hidden"> <!-- Missed words list --> </div>
    <div id="statsView" class="hidden"> <!-- Record/stats dashboard --> </div>
    <div id="settingsView" class="hidden"> <!-- Settings page --> </div>
    <div id="wordsView" class="hidden"> <!-- Full word list with search/filter --> </div>
  </div>
  <script src="words.js"></script>
  <script src="templates.js"></script>
  <script src="sentences.js"></script>
  <script src="app.js"></script>
</body>
```

### View Navigation

Views are toggled via `showView(v)` which hides all views and shows the requested one. Nav buttons get `.active` class. Each view has a render function called on show:
- `quiz` → `updateWordPoolInfo()`, `updateDailyBanner()`, `updateSittingDesc()`
- `words` → `renderWordList()`
- `review` → `renderReview()`
- `stats` → `renderStats()`
- `calendar` → `renderCalendar()`
- `settings` → `renderSettings()`

---

## 3. DATA FORMATS

### words.js

```javascript
const W = [
  {w:"abase", p:"v.", d:"to humiliate, degrade", diff:"hard"},
  {w:"abate", p:"v.", d:"to reduce, lessen", diff:"medium"},
  // ... 1,715 total entries
];
```

Fields:
- `w` (string): The word itself, lowercase
- `p` (string): Part of speech — one of: `"v."`, `"n."`, `"adj."`, `"adv."`, `"conj."`, `"prep."`
- `d` (string): Short definition, 2-8 words ideally (some go to 11)
- `diff` (string): Difficulty — `"easy"` | `"medium"` | `"hard"`

**Difficulty distribution**: Easy: 311 (18.1%), Medium: 868 (50.6%), Hard: 536 (31.3%)

### sentences.js

```javascript
const SENTENCES = {
  "abandon": [
    ["The settlers had to _____ their homes when the floodwaters rose above the levees.", "evacuate", "renovate", "construct"],
    ["She decided to _____ her cautious approach and embrace the opportunity with open arms.", "reject", "maintain", "strengthen"],
    // ... 5-6 sentences per word
  ],
  // ... 1,715 word entries
};
```

Each sentence entry: `[sentence_with_blank, wrong_answer_1, wrong_answer_2, wrong_answer_3]`
- The blank is `_____` (five underscores)
- The correct answer is the key (the word itself)
- 3 wrong answers that are plausible but incorrect

**Stats**: 1,715 words with sentences, 10,143 total sentences, 5-6 sentences per word (147 words have 5, 1,568 have 6)

### templates.js

Fallback sentence generators used when `SENTENCES[word]` doesn't exist (currently all words have pre-written sentences, so these are rarely used). Contains template functions for each POS:

```javascript
const TEMPLATES = {
  'adj.': [60 template functions],
  'n.':   [60 template functions],
  'v.':   [60 template functions],
  'adv.': [46 template functions]
};
function makeSentence(wordObj) {
  let pool = TEMPLATES[wordObj.p] || TEMPLATES['adj.'];
  return pick(pool)(wordObj.d);
}
```

**BUG**: No template for `"conj."` — words like "albeit" fall back to `'adj.'` templates, producing nonsensical sentences.

### localStorage State (`sat_vocab_v4`)

```javascript
{
  missCount: {idx: count, ...},           // Index → miss count
  sessionsCompleted: 0,                    // Total sessions finished
  totalCorrect: 0,                         // Lifetime correct answers
  totalAnswered: 0,                        // Lifetime total answers
  currentSession: null,                    // UNUSED — was for session persistence
  questionTypes: {                         // Which question types are enabled
    wordToDef: true,
    defToWord: true,
    sentence: true,
    synonym: true
  },
  dailyLog: {                              // Per-day tracking
    "2026-07-11": {answered: 15, correct: 12}
  },
  bestStreak: 0,                           // All-time best streak
  dailyGoal: 20,                           // Words per day for streak (0 = Infinity/any)
  leitner: {                               // Per-word Leitner data (keyed by W array index)
    "42": {
      b: 3,                                // Box number (0=New, 1-4=Learning, 5=Learned)
      due: "2026-07-18",                   // Next review date (ISO string)
      wt: 5,                               // Times seen as "wordToDef" question
      dw: 3,                               // Times seen as "defToWord" question
      sc: 4,                               // Times seen as "sentence" question
      sy: 2                                // Times seen as "synonym" question
    }
  },
  retryInSession: false,                   // Setting: retry missed words in session
  difficultyFilter: 'all',                 // Current difficulty filter
  sessionHistory: [                        // Last 100 sessions
    {date: "2026-07-11", time: "2:30 PM", score: 18, total: 20, pct: 90}
  ],
  timedMode: false,                        // Timer enabled?
  timerSeconds: 30,                        // Timer duration
  timerHidden: false,                      // Timer bar hidden?
  sessionSize: null,                       // Custom session size (null = use dailyGoal)
  diffStats: {                             // Accuracy by difficulty
    easy: {correct: 0, total: 0},
    medium: {correct: 0, total: 0},
    hard: {correct: 0, total: 0}
  }
}
```

---

## 4. APP.JS COMPLETE LOGIC MAP

The file is 88 lines of heavily minified JavaScript. Here is every function, what it does, and where it lives:

### State Management (Lines 1-21)
- `LS_KEY = 'sat_vocab_v4'` — localStorage key
- `getDailyGoal()` — Returns daily goal (0 → Infinity)
- `getSessionSize()` — Returns session size (0 → Infinity, null → use daily goal)
- `hideTimer()` / `showTimerBar()` — Toggle timer visibility
- `setSessionSize(n)` — Set custom session size
- `defaults()` — Returns default state object (Line 8)
- `LEITNER_INTERVALS = [0, 1, 3, 7, 14, 30]` — Days between reviews per box
- `getLeitner(idx)` — Get/initialize Leitner data for word index
- `advanceLeitner(idx)` — Move word to next box, set due date
- `resetLeitner(idx)` — Reset word to Box 1, due tomorrow (**BUG**: goes to Box 1 not Box 0)
- `markForReview(idx)` — Reset word to Box 0, due today (used by Review tab reset button)
- `pickTypeForWord(idx, enabledTypes)` — Picks least-used question type for this word
- `countMastery()` — Returns {learned, learning, unseen} counts
- `load()` — Load state from localStorage with v3 migration and defaults merging
- `save()` — Save state (**BUG**: no try/catch for QuotaExceededError)
- `todayKey()` — Returns today as "YYYY-MM-DD"
- `getTodayLog()` — Get/initialize today's daily log
- `addDailyAnswer(isCorrect)` — Increment today's answered/correct counts
- `calcStreak()` — Calculate current streak (**BUG**: side effect — writes bestStreak and calls save())

### Session Management (Lines 22-28)
- `session` object — Holds current quiz state: `{words, current, score, streak, answered, retryQueue, retryCounter, total, enabledTypes}`
- `shuffle(a)` — Fisher-Yates shuffle in place
- `randInt(min, max)` — **DEAD CODE**, never called
- `pick(arr)` — Random element from array
- `DIFF_CACHE` — Pre-computed difficulty array for all words
- `pickSessionWords()` — **CRITICAL FUNCTION** — Selects words for a session:
  1. Filters by difficulty if set
  2. Categorizes each word: retry (missed + low box), due, unseen, not-due
  3. Shuffles each category
  4. Concatenates: retry → due → unseen → not-due
  5. Slices to session size
- `setDiffFilter(f)` — Set difficulty filter, save, update UI
- `countByDiff()` — Count words per difficulty level

### Text Processing (Lines 30-33)
- `defTokens(d)` — Tokenize a definition, removing stop words (for distractor selection)
- `defSimilarity(a, b)` — Jaccard-like similarity between two definitions
- `defContains(a, b)` — Check if one definition contains the other
- Conjugation functions: `conjugatePast`, `conjugateIng`, `conjugateS`, `conjugateN` — Handle verb forms in sentence completion

### Distractor Selection (Line 34)
- `getDistractors(correct, count, type)` — **PERFORMANCE-CRITICAL** — Selects 3 wrong answers:
  1. Filters out the correct word
  2. Scores all remaining 1,714 words by: same POS (+10), definition similarity (+6 for moderate overlap), definition length ratio (+5)
  3. Rejects words with similarity ≥ 0.4 or that contain each other
  4. Sorts by score descending, picks top 3 ensuring no mutual clashes
  5. Falls back to random words if not enough quality distractors
  - Returns definitions (for wordToDef/synonym) or words (for defToWord/sentence)

### Question Types (Lines 35-38)
- `getEnabledTypes()` — Returns array of enabled question type strings
- `startSession()` — Initialize session, hide start screen, show quiz, call showQuestion
- `exitSession()` — Stop timer, save, return to start screen
- `showQuestion()` — **LARGEST FUNCTION (~80 dense lines)** — Renders a question:
  - Gets the current word from `session.words[session.current]`
  - Picks question type via `pickTypeForWord()`
  - For each type, constructs: question text, answer options, correct index
  - **Sentence completion** has complex conjugation logic:
    - Detects suffix after blank (e.g., `_____ed` → conjugate past tense)
    - Detects article before blank (a/an _____ → prepend correct article)
    - Applies conjugation to all options including correct word
  - Creates option DOM elements with click and right-click handlers
  - Stores metadata in `card.dataset.*` for checkAnswer to read
  - Starts timer if timed mode is on

### Answer Handling (Lines 39-44)
- `selectOption(idx)` — Highlight selected option, show Check button
- `toggleInfo()` — Show/hide keyboard shortcuts panel (**BUG**: event listener leak)
- `toggleCrossOut(idx)` — Toggle strikethrough on an option
- `findWordDef(w)` — **DEAD CODE**, never called (**BUG**: startsWith can match wrong words)
- `checkAnswer()` — **CRITICAL FUNCTION**:
  - Handles both normal answers and timer timeout (timedOut = chosen < 0)
  - Shows correct answer (green), marks wrong answer (red) if applicable
  - Updates session score, streak, Leitner box, miss count, difficulty stats, daily log
  - Pushes to `session.retryQueue` on wrong answer (**BUG**: queue is never consumed)
  - Updates daily banner live
  - Records answer in `session.answered` for summary
  - Tracks per-question-type counts per word in Leitner data
- `nextQuestion()` — Increment current, show next question or summary

### Summary (Line 45)
- `showSummary()` — Renders post-session results:
  - Increments `sessionsCompleted`
  - Pushes to `sessionHistory` (max 100)
  - Calculates grade message based on percentage
  - Deduplicates missed words display
  - Shows: score, percentage, missed words list, buttons for New Sitting / Missed Log / View Record

### Review (Lines 46-49)
- `bucketName(b)` — Maps box number to display name
- `renderReview()` — Renders missed words list sorted by miss frequency
  - Each word shows: term, POS, difficulty tag, Leitner box, definition, miss count, Reset button
  - "Practice These" button at top calls `practiceMissed()`
  - "Clear List" button at bottom
- `practiceMissed()` — Creates a session from all missed words:
  - Gets all word indices from `missCount`
  - Shuffles, limits to daily goal count
  - Creates session with `_retry: true` flag
  - Starts quiz
- `clearMissed()` — Clears missCount after confirmation

### Statistics (Lines 50-56)
- `chartScale` — Current chart time range ('all', '1y', '6m', '1m', '1w', '1d')
- `setChartScale(s)` — Change time range, re-render
- `buildProgressChart()` — Builds SVG accuracy chart from dailyLog data
  - Handles: no data, single data point, multi-point with scaling
  - SVG viewBox 560x180, uses CSS variables for colors
  - Shows dots for ≤60 data points, hides for more
  - X-axis date labels, Y-axis percentage labels with guide lines
- `chartScaleButtons()` — Renders time scale button bar
- `renderDiffStats()` — Renders accuracy bars by difficulty level
- `renderSessionHistory()` — Renders last 20 sessions as rows
- `renderStats()` — Full Record tab render:
  - Overall stats grid (answered, correct, accuracy%, sittings)
  - Mastery bar (learned/learning/unseen)
  - Accuracy by difficulty
  - Daily accuracy chart with scale buttons
  - Session history
  - Reset button

### Daily Banner & Calendar (Lines 57-62)
- `updateDailyBanner()` — Shows today's progress bar, word count, streak
  - Hidden when no practice today
  - Shows "Daily goal reached" or "Today's progress" with fill bar
- `calYear`, `calMonth` — Current calendar view state
- `renderCalendar()` — Full calendar render:
  - Streak display (current + best)
  - Monthly grid with day cells
  - Each day shows: fill bar for progress, checkmark if goal met, count if partial
  - Navigation arrows for month switching
  - Legend with completed/total days
- `setDailyGoal(n)` — Update daily goal setting
- `getEffectiveGoal()` — Returns 1 if goal is Infinity, otherwise the goal number

### Settings (Lines 63-70)
- `renderSettings()` — Full settings page:
  - Daily goal selector (5/10/15/20/25/30/40/50/Any)
  - Question types checkboxes
  - Practice mode toggle (retry missed words)
  - Backup section (export/import)
  - Reset all progress
- `exportProgress()` — Downloads state as JSON (**BUG**: URL.revokeObjectURL race condition)
- `importProgress()` — File picker, JSON parse, shallow validation, merge into state (**BUG**: weak validation)
- `saveSettingsTypes()` — Save question type checkboxes
- `updateSittingDesc()` — Renders Practice tab start screen with customize options:
  - Start Practicing button
  - Collapsible "Customize" panel with:
    - Difficulty filter chips (All/Easy/Medium/Hard with counts)
    - Session size buttons (10/20/30/50/∞/Custom)
    - Timer buttons (Off/15s/20s/30s/45s/60s)
- `promptCustomSize()` — Prompt for custom session word count
- `optionsOpen` — State for customize panel
- `toggleOptions()` — Toggle customize panel visibility

### Word List (Lines 71-76)
- `wlDiffFilter`, `wlSort` — Current word list filter/sort state
- `setWlDiff(f)` / `setWlSort(s)` — Change filter/sort, re-render
- `renderWordList()` — Full word list render (**PERFORMANCE ISSUE**: renders ALL 1,715 words at once):
  - Search input with live filtering
  - Filter buttons (All/Easy/Medium/Hard)
  - Sort buttons (A-Z/Z-A/Most missed/Least missed)
  - Each word item shows: word, POS, definition, difficulty tag, mastery level, miss count
  - Expandable detail view with: example sentences (first 2), stats (seen/missed/box/due date)
- `toggleWordExpand(el)` — Toggle expanded state on word item
- `filterWordList()` — Live search filter by word name or definition text

### Timer (Lines 77-80)
- `timerInterval`, `timerRemaining` — Timer state
- `startTimer()` — Start countdown if timed mode enabled
  - Shows timer bar at top of screen
  - Respects hidden state
  - Turns red at ≤5 seconds
  - Calls `timeUp()` on expiry
  - **BUG**: Uses `setInterval(1000)` which drifts when tab is backgrounded
- `stopTimer()` — Clear interval, hide timer
- `timeUp()` — Force-submit with no selection (triggers checkAnswer with selectedIdx = -1)

### Navigation & Theme (Lines 81-87)
- `showView(v)` — Tab navigation handler
- `updateWordPoolInfo()` — **DEAD CODE** — empty function, called from multiple places
- Keyboard handler — Global keydown on document:
  - Only active when `quizActive` is visible
  - Escape → exit session
  - 1-4 or A-D → select option
  - Enter/Space → check answer or continue
- `toggleTheme()` — Switch light/dark mode
- IIFE at line 85 — Initialize theme from localStorage on page load
- Lines 86-87 — Initialize daily banner and start screen on load

---

## 5. CSS ARCHITECTURE

### Theming
- Light mode: `:root` variables — white bg, black ink, black accents
- Dark mode: `[data-theme="dark"]` variables — near-black bg, off-white ink
- All colors use CSS custom properties (var(--xxx))
- Theme toggle uses `document.documentElement.setAttribute('data-theme', ...)`
- Preference stored in localStorage as `sat_theme`
- **NOT detecting `prefers-color-scheme`** — first-time visitors always get light mode

### Key Measurements
- Body font-size: 19px (bumped from 17px for readability)
- Container max-width: 960px
- All text sizes use rem (relative to body font-size)
- Padding/margins use px
- Line-height: 1.5

### Animation System
- `--ease: cubic-bezier(.4, 0, .2, 1)` — Standard ease
- `--ease-bounce: cubic-bezier(.34, 1.56, .64, 1)` — Bounce for score reveals
- 8 `@keyframes` defined: scoreReveal, barComplete, plus various transitions
- Micro-interactions: stat card hover lifts, option hover slide, search focus glow, calendar day hover
- Custom thin scrollbar for word list
- **NO `prefers-reduced-motion` media query** — should be added

### Responsive Design
- Mobile breakpoints at various widths
- `.quiz-active` body class hides nav bar during quiz for full-screen focus
- Question card is flex column layout
- Options are full-width clickable rows

### Notable CSS Selectors
- `.option` — Quiz answer choice row
- `.option.selected` — User-selected answer (before checking)
- `.option.correct.show-correct` — Correct answer reveal (green)
- `.option.wrong` — Wrong answer reveal (red)
- `.option.crossed-out` — User right-clicked to eliminate
- `.wl-item` — Word list entry
- `.wl-item.expanded` — Expanded word detail
- `.diff-tag.easy/medium/hard` — Difficulty color badges
- `.diff-chip` — Difficulty filter buttons
- `.size-btn` — Session size / timer buttons
- `.daily-banner` — Today's progress bar at top of Practice
- `.streak-display` — Streak number on Calendar
- `.mastery-track` / `.mf-learned` / `.mf-learning` — Mastery progress bar
- `.progress-chart` — SVG accuracy chart
- `.sh-row` — Session history row
- `.cal-grid` / `.cal-day` — Calendar grid

---

## 6. CURRENT STATE & STATISTICS

### Database
- **1,715 words** in words.js
- **10,143 sentences** in sentences.js (5-6 per word)
- **0 orphan words** (every word has sentences, every sentence key has a word)
- **0 duplicate words**
- **8 pairs of duplicate definitions** (synonyms sharing exact definition text)
- **55 definitions** exceed 8 words (longest: 11 words)
- **37 sentences** contain em dashes (cosmetic, renders fine)
- **147 words** have only 5 sentences (rest have 6)

### Git State
- Latest commit: `2966642` "Add 147 new SAT vocabulary words with 735 sentences"
- Branch: `main`
- 1 untracked file: `audit.js` (can be deleted)
- **There may be uncommitted changes from previous sessions** — always check with `git status`
- Push command: `cd ~/satvocabapp && rm -f .git/index.lock .git/HEAD.lock && git push origin main`

---

## 7. KNOWN BUGS (CODE AUDIT)

### CRITICAL

**1. `save()` has no error handling for localStorage quota (Line 17)**
```javascript
function save(){localStorage.setItem(LS_KEY,JSON.stringify(state))}
```
If localStorage is full (~5-10MB), `setItem` throws `QuotaExceededError`, crashing mid-answer. State grows unboundedly over time.
**Fix**: Wrap in try/catch, warn user, or prune old dailyLog entries.

**2. `correctIdx` can be -1 with duplicate definitions (Line 38)**
For `wordToDef` and `synonym` types:
```javascript
options = [wordObj.d, ...distractors];
shuffle(options);
correctIdx = options.indexOf(wordObj.d);
```
8 word pairs share exact definitions. If a distractor has the same definition string, `indexOf` finds the first occurrence, which may be the distractor. User could select the correct definition but at the wrong index.
**Fix**: Track correct index through shuffle instead of using `indexOf` post-shuffle:
```javascript
const correctIdx = 0; // correct is always first
options = [wordObj.d, ...distractors];
// Track where index 0 ends up after shuffle
let trackedIdx = 0;
for (let i = options.length - 1; i > 0; i--) {
  const j = Math.floor(Math.random() * (i + 1));
  [options[i], options[j]] = [options[j], options[i]];
  if (trackedIdx === i) trackedIdx = j;
  else if (trackedIdx === j) trackedIdx = i;
}
correctIdx = trackedIdx;
```

**3. Import function does not validate data deeply (Line 65)**
Only checks top-level type and two fields. Does not validate: missCount values (could be NaN), totalCorrect/totalAnswered (could be negative), dailyLog entries, leitner entries (invalid dates, non-numeric boxes), diffStats structure. A crafted JSON file could inject unexpected state.
**Fix**: Add comprehensive validation for each field type and range.

**4. XSS via innerHTML with word data (Lines 38, 43, 45, 47, 74)**
Word data is interpolated into `innerHTML` without escaping:
```javascript
qTextEl.innerHTML = `<span class="q-word">${wordObj.w}</span>...`;
fb.innerHTML = `Correct — <em>${wordObj.w}</em>: ${wordObj.d}`;
```
Currently safe because W array is static, but the import function could inject HTML via crafted data.
**Fix**: Escape HTML entities or use textContent where possible.

### WARNING

**5. `retryQueue` is populated but never consumed (Lines 22, 43)**
Wrong answers push to `session.retryQueue`, but `nextQuestion()` just increments `session.current`. Words are never re-presented within a session. The "Retry missed words in session" setting only affects word SELECTION for the next session, not within-session retry. `session.retryCounter` is also dead.
**Fix**: Either implement actual within-session retry (re-insert missed words later in the queue) or remove the dead code and clarify the setting description.

**6. `getDistractors()` is O(n) with ~3,400 string operations per question (Line 34)**
Runs `defSimilarity` (tokenize + set intersection) against all 1,714 other words for every question. Causes noticeable lag on slower devices.
**Fix**: Pre-compute a similarity matrix, or use a faster heuristic (same POS + random).

**7. `renderWordList()` builds entire DOM for 1,715 words at once (Line 74)**
Generates ~200KB of HTML in one string, then sets via innerHTML. No virtualization.
**Fix**: Implement virtual scrolling or lazy loading (render only visible items).

**8. `toggleInfo()` event listener leak (Line 40)**
Multiple document click listeners accumulate if user rapidly toggles the info panel.
**Fix**: Store the listener reference, remove it in the toggle-off branch.

**9. Mastery bar percentages can overflow 100% (Line 56)**
Due to rounding, `learnedPct + learningPct` can exceed 100, causing the learning bar to overflow.
**Fix**: Clamp `learningPct` to `Math.min(learningPct, 100 - learnedPct)`.

**10. `calcStreak()` has side effects (Line 21)**
A getter that writes `state.bestStreak` and calls `save()`. Called from rendering functions.
**Fix**: Separate the bestStreak update into a separate function called only after practice.

**11. Timer drift in backgrounded tabs (Line 78)**
`setInterval(1000)` is throttled when tab is backgrounded. Timer can drift 5+ seconds.
**Fix**: Use `Date.now()` delta instead of decrementing a counter.

**12. `resetLeitner()` goes to Box 1, not Box 0 (Line 12)**
When user gets a word wrong, it goes to Box 1 (due tomorrow) not Box 0 (New). Words never return to "Unseen" count even when repeatedly missed.
**Fix**: Consider whether this is desired behavior or should reset to Box 0.

**13. Export `URL.revokeObjectURL` race condition (Line 64)**
Called synchronously after `a.click()`, but download may not have started yet.
**Fix**: Use `setTimeout(() => URL.revokeObjectURL(url), 1000)`.

**14. `practiceMissed()` ignores session size setting (Line 48)**
Uses `getDailyGoal()` instead of `getSessionSize()` to limit session.
**Fix**: Use `getSessionSize() ?? getDailyGoal()`.

**15. No system dark mode detection (Line 85)**
First-time visitors always get light mode regardless of OS preference.
**Fix**: Check `window.matchMedia('(prefers-color-scheme: dark)')` if no saved preference.

### INFO (Dead Code)
- `updateWordPoolInfo()` — Empty function (Line 82)
- `currentSession` in defaults — Never read or written (Line 8)
- `session.retryCounter` — Never read or written (Line 22)
- `randInt()` — Never called (Line 24)
- `findWordDef()` — Never called (Line 42)
- No session persistence across page reloads
- No `conj.` template in templates.js (only "albeit" affected)
- Calendar legend denominator is confusing when no practice this month

---

## 8. DATA QUALITY AUDIT RESULTS

### Passed (All Clear)
- No duplicate words
- All entries have required fields (w, p, d, diff)
- All difficulty values are valid (easy/medium/hard)
- All POS values are valid
- Every sentence has exactly one _____ blank
- Every sentence has exactly 3 wrong answers
- Perfect word↔sentence alignment (no orphans)
- No wrong answers duplicate each other or match the correct word
- No empty definitions
- No encoding issues, broken quotes, or special character problems

### Issues to Consider

**8 duplicate definition pairs** (synonyms with identical definitions):
| Definition | Word 1 | Word 2 |
|---|---|---|
| "sickeningly sweet" | cloying | saccharine |
| "soothing" | emollient | pacific |
| "to free from guilt or blame" | exculpate | exonerate |
| "dull, boring" | insipid | tedious |
| "highest point" | pinnacle | zenith |
| "an omen" | portent | presage |
| "loud, boisterous" | raucous | vociferous |
| "occurring at irregular intervals" | intermittent | sporadic |

**Fix**: Add distinguishing nuances (e.g., "pinnacle" → "highest point or achievement", "zenith" → "highest point in the sky or peak").

**55 definitions over 8 words** — Most are 9-11 words. Not critical but could be trimmed for consistency.

**147 words with only 5 sentences** — The 147 most recently added words have 5 sentences each while the original 1,568 have 6. Consider adding a 6th sentence to each for consistency.

---

## 9. USER FEEDBACK (UNRESOLVED)

### From the user directly:

**A. "You review the word right after you get it wrong, make it more spaced out"**
The app currently shows the correct answer immediately after a wrong answer (which is correct behavior), but the NEXT time that word appears is the very next session if "Retry missed words in session" is on. The Leitner system sets missed words to Box 1 with a 1-day interval, so they should reappear the next day. The user may be experiencing:
- The `retryInSession` setting prioritizing missed words at the start of the next session
- The word appearing again quickly because it's marked as "due" the next day
- **Fix needed**: Review the `pickSessionWords()` priority order. Consider NOT putting freshly-missed words at the front of the next session. Add more spacing between retries.

**B. "You can't review words you got wrong"**
The Review tab DOES show missed words, but the user may be experiencing:
- The Review tab list being hard to find or use
- The "Practice These" button not being prominent enough
- Missed words not being clearly actionable
- **Fix needed**: Make the Review tab more prominent. Consider adding a direct "Practice Missed Words" button on the post-session summary. Ensure the Review tab's "Practice These" button works correctly.

**C. Previous feedback (all addressed in earlier sessions)**:
- Scaling inconsistency between Words and Review tabs → Fixed
- Text too small → Fixed (body font-size 17px → 19px)

---

## 10. UI/UX RESEARCH FINDINGS

### Comprehensive research was conducted. Key findings:

#### What Top Apps Do Well
- **Anki**: Best algorithm (89% retention at day 14) but worst UI
- **Quizlet**: Multiple study modes keep sessions fresh; Match mode gamifies review
- **Brainscape**: Simpler confidence rating (1-5) achieves 82% retention with better UX
- **Magoosh**: Ultra-clean dashboard, 4 main sections, video lessons 4-12 min
- **Kaplan**: "20-Minute Workout" sessions, "Question of the Day"

#### Evidence-Based Gamification
- **Streaks**: 3.6x engagement improvement (Duolingo data). Weekly target (5/7 days) better than rigid daily
- **Spaced repetition + gamification**: 3x retention vs either alone
- **Growth-mindset encouragement**: +7.2% day-14 return rate
- **XP scaled to difficulty**: Prevents easy-word grinding
- **Badges**: Mostly fluff unless tied to genuine mastery milestones
- **Leaderboards**: Decrease motivation for lower performers

#### Visual Design
- Font size 18px+ improves comprehension (Carnegie Mellon eye-tracking)
- Line height 1.4-1.6x font size
- 60-30-10 color rule: 60% neutral, 30% surface, 10% accent
- Dark mode: #121212 bg not pure black, #E0E0E0 text not pure white
- One card = one word at a time (reduce cognitive load)
- Max 4 answer choices (Hick's Law)

#### Mobile
- 75% of touchscreen interactions are thumb-driven
- Primary actions in bottom 40% of screen
- 44x44px minimum touch targets
- Swipe gestures for flashcard review

#### Session Design
- 15-20 minutes optimal (hippocampal working memory window)
- Microlearning 3-7 minutes: 17% more efficient
- Break suggestions after 20 cards
- "One more?" prompt at session end

### Prioritized Improvements (by impact):

**Tier 1 — High Impact:**
1. Confidence-based spaced repetition with visible mastery levels per word
2. Streak system with weekly target (5 of 7 days) + streak freeze
3. Immediate visual feedback improvements (better animations for correct/incorrect)
4. Post-session summary with encouragement + "Review 5 more?" prompt
5. Thumb-zone-optimized mobile layout

**Tier 2 — High Impact, Lower Effort:**
6. Typography refinements (already at 19px, but could use Inter/system sans-serif)
7. Simplified home screen with "due for review" counter
8. Dark mode refinement (currently #0a0a0a, could be #121212)
9. Multiple quiz modes (add matching mode)
10. Progressive disclosure in quizzes

**Tier 3 — Medium Impact:**
11. Session length controls (Quick 5 mode)
12. XP system scaled to difficulty
13. Consistent micro-animation system + prefers-reduced-motion
14. Accessibility pass (contrast ratios, keyboard nav, ARIA)
15. Color-coded word mastery in word list

---

## 11. AI CHATBOT INTEGRATION PLAN

### Recommended Approach: Google Gemini Free Tier with BYOK

**Why Gemini**: Free tier (250 requests/day, 10 RPM), works from browser via raw fetch(), adequate quality for vocabulary explanations.

**Architecture**: Create new `ai.js` file, add to index.html after app.js.

### Features to Implement:
1. **Floating chat widget** — Fixed-position FAB button (bottom-right), opens chat panel
2. **"AI Explain" button** — On each word in word list, sends word to AI for etymology + mnemonic + examples
3. **"Ask AI: Why?" button** — After wrong answers, explains why correct answer is better
4. **"Mnemonic" button** — Generates personalized memory aid for any word
5. **Settings integration** — API key input (stored in localStorage), provider selector (Gemini/Claude)

### Files to Create/Modify:
- **CREATE `ai.js`** — All AI logic (~100 lines):
  - `getAiConfig()`, `callGemini(prompt)`, `callClaude(prompt)`, `askAi(prompt)`
  - `toggleAiChat()`, `sendAiMessage()`, `appendChatMessage()`
  - `explainWord(word, def)`, `explainWrongAnswer(chosen, correct, correctDef)`, `generateMnemonic(word, def)`
- **MODIFY `index.html`** — Add chat widget HTML + `<script src="ai.js"></script>`
- **MODIFY `style.css`** — Add `.ai-fab`, `.ai-chat-widget`, `.ai-msg`, `.ai-explain-btn` styles
- **MODIFY `app.js`** — Add "Ask AI: Why?" button in `checkAnswer()`, add AI buttons in `renderWordList()`, add AI settings in `renderSettings()`

### API Details:

**Gemini (free, recommended for personal use):**
```javascript
const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${key}`;
// POST with: system_instruction, contents, generationConfig
```

**Claude (better quality, costs ~$6/month at heavy use):**
```javascript
const url = 'https://api.anthropic.com/v1/messages';
// Requires header: 'anthropic-dangerous-direct-browser-access': 'true'
// Model: 'claude-haiku-4-20250414'
```

### Security
- BYOK (Bring Your Own Key) pattern — user pastes API key in Settings
- Key stored in localStorage (acceptable for personal use)
- No third-party scripts = low XSS risk
- Gemini keys can be restricted to specific referrer domains

---

## 12. SAT RESEARCH FINDINGS

### Current SAT Format (2024+)
The SAT transitioned to a fully digital format in 2024. The Reading and Writing section is 64 minutes, 54 questions in 2 modules.

### How Vocabulary is Tested Now
The old-style "sentence completion" format (pick the word that fills the blank) was **removed in 2016**. The current SAT tests vocabulary through:

1. **Words in Context** — A short passage (25-150 words) with a question like "As used in the text, 'volatile' most nearly means..." with 4 definition choices. Tests understanding of words with multiple meanings in specific contexts.

2. **Text Completion** — A passage with a blank, asking which word best completes the text. Similar to the app's current sentence completion but with a full passage providing context.

3. **Vocabulary used in Craft and Structure questions** — Understanding how word choice affects meaning, tone, and purpose.

### Implications for the App
The app's current fill-in-the-blank format is CLOSE to the actual SAT "Text Completion" style but could be improved:
- **Add a "Words in Context" question type** — Show a passage with a word underlined, ask what it means in that context. This is the #1 most common vocabulary question on the current SAT.
- Current sentence completion is still valid practice but should use longer, more passage-like contexts.
- The app should distinguish between "learning mode" (flashcard-style) and "test prep mode" (SAT-style questions).

### High-Frequency SAT Word Categories
Research shows these categories appear most frequently:
- **Tone/Attitude words**: ambivalent, complacent, cynical, diffident, indifferent, sardonic, zealous
- **Argument/Reasoning words**: assert, corroborate, refute, substantiate, undermine, advocate
- **Change/Transition words**: fluctuate, innovate, transform, volatile, static, stagnant
- **Relationship words**: analogous, complementary, contradictory, disparate, parallel
- **Evidence words**: empirical, anecdotal, hypothetical, speculative, conclusive

### Study Strategy Research
- **Spaced repetition**: 85% retention after 1 year vs 22% with traditional methods
- **Context-based learning**: More effective than pure definition memorization for the current SAT format
- **Active recall** (testing yourself) is 50% more effective than passive review
- **Interleaving** (mixing different types of practice) beats blocked practice
- **Elaborative interrogation** ("why does this word mean this?") improves retention

---

## 13. PENDING TASKS & PRIORITIES

### Critical Bug Fixes (Do First)
1. Add try/catch to `save()` for QuotaExceededError
2. Fix `correctIdx` indexOf collision with duplicate definitions
3. Fix retryQueue dead code — either implement within-session retry or remove
4. Add system dark mode detection (`prefers-color-scheme`)
5. Fix mastery bar percentage overflow
6. Fix export URL.revokeObjectURL race condition

### User Feedback Fixes
7. Fix "review word right after wrong" — adjust `pickSessionWords()` to not front-load recently-missed words. Add spacing between retries.
8. Fix "can't review words you got wrong" — improve Review tab discoverability, add "Practice Missed" button to post-session summary

### Feature Additions
9. Implement AI chatbot integration (ai.js, chat widget, explain/mnemonic buttons)
10. Add "Words in Context" question type (passage-based, matching actual SAT format)
11. Add more vocabulary words (identify high-frequency SAT words not yet in database)
12. Add `prefers-reduced-motion` media query
13. Add 6th sentence to the 147 words that only have 5
14. Differentiate the 8 duplicate definition pairs
15. Add "due for review" counter on Practice home screen
16. Implement virtual scrolling for word list (performance)

### UI Improvements (from research)
17. Add post-session encouragement messages (growth-mindset framing)
18. Add "Quick 5" session mode (5 words, ~3 minutes)
19. Add "Review 5 more?" prompt at session end
20. Add word mastery color indicators in word list (colored dots for New/Learning/Reviewing/Mastered)
21. Add celebration animation on session complete / word mastered
22. Mobile: move action buttons to bottom 40% of screen
23. Add skeleton loading states
24. Add personal best tracking
25. Add streak freeze mechanism (5 of 7 days target)

---

## 14. GIT HISTORY & PUSH INSTRUCTIONS

### Recent Commits (newest first)
```
2966642 Add 147 new SAT vocabulary words with 735 sentences
134d4f5 UI polish: micro-interactions and refinements
bb96b58 Scale up all text sizes + unify Words/Review consistency
0a93c8a UI cleanup: reduce visual weight across all views
5c2f601 Style options box
27c3bd9 Add collapsible Customize toggle, Words tab filter/sort, fix calendar goal bug
9d47ba0 Unify button styles
64bc47f Fix button alignment
88e9b2d Complete sentence rewrite with SAT context clues, timer UI, session options
1065fc9 SAT sentence rewrite, timer UI, session size options
60240a4 Fix score display, word list layout, empty pool crash, mobile tap targets
105919d Fix timer bug, sentence data, chart label, dead code cleanup
e5f74db Add difficulty filter, progress chart, session history, export/import, word details
e2160c8 Fix feedback bar lingering
4a31bfa Major update: 498 new words (1568 total), UI fixes, practice missed
```

### Push from Local Machine
```bash
cd ~/satvocabapp && rm -f .git/index.lock .git/HEAD.lock && git add -A && git commit -m "message" && git push origin main
```

The sandbox environment (Cowork/Claude Code) cannot push directly because `.git/index.lock` persists due to permissions. Always provide push commands for the user to run locally.

### Deployment
GitHub Pages auto-deploys from the `main` branch. After push, changes are live at https://aideny2028.github.io/satvocabapp/ within 1-2 minutes.

---

## 15. DEVELOPMENT WORKFLOW

### File Access
- **File tools** (Read/Write/Edit): Use paths like `/Users/aiden/satvocabapp/app.js`
- **Bash/shell**: Use paths like `/sessions/dreamy-fervent-lovelace/mnt/satvocabapp/app.js` (or whatever the session mount is)
- The sandbox mount path changes per session — check the system prompt for the current mapping

### Testing
- **Live preview**: Use Chrome MCP to navigate to `https://aideny2028.github.io/satvocabapp/` and screenshot
- **CSS injection for previewing changes**: Use `mcp__claude-in-chrome__javascript_tool` to inject CSS rules with `!important` for live preview before committing
- **JavaScript validation**: Run `node -e 'var W=...; eval(code); ...'` in bash to validate JS syntax (must replace `const` with `var` for eval compatibility)
- **Data validation**: Run Node.js scripts to cross-check words.js ↔ sentences.js alignment

### Key Gotchas
1. **app.js is heavily minified** — All functions are on single lines. Use a beautifier before editing, then re-minify or just edit carefully.
2. **words.js and sentences.js are HUGE** — Don't try to read them fully. Use scripts to validate and make targeted edits.
3. **Git lock files** — The sandbox can't delete `.git/index.lock`. Always include `rm -f .git/index.lock .git/HEAD.lock` in push commands.
4. **CSS file is 1,302 lines** — All changes in this session were CSS-only. Use Edit tool with targeted old_string/new_string.
5. **`const` declarations** — words.js uses `const W=[...]`, sentences.js uses `const SENTENCES = {...}`. These can't be `eval()`'d directly in Node.js; replace with `var` for validation scripts.
6. **innerHTML everywhere** — The entire app uses string-based HTML generation. Be careful with special characters in word definitions.

### Architecture Decisions Made
- **No framework** — Deliberate choice for simplicity, zero build step, instant GitHub Pages deployment
- **Single file per concern** — HTML, CSS, JS, data are all separate files
- **CSS custom properties** — All theming via variables, no CSS-in-JS
- **Leitner over SM-2** — Simpler algorithm, easier to understand and debug
- **Serif font** — Iowan Old Style / Palatino for a classic, book-like aesthetic
- **Monochrome design** — Black-and-white aesthetic inspired by OnePrep, with color only for semantic meaning (good/bad/gold)
- **No backend** — Everything in localStorage, no auth, no server, no API (until AI chatbot)

---

*End of handoff document. This covers every aspect of the project as of July 11, 2026.*
