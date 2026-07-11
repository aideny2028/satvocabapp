const LS_KEY = 'sat_vocab_v4';

// Escape HTML special characters (used for any string that could come from imported data)
function esc(s) {
    return String(s).replace(/[&<>"']/g, c => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
    }[c]))
}

// Local-timezone date key (YYYY-MM-DD). Never use toISOString for day keys — it's UTC
// and shifts evening practice onto the next day for anyone west of Greenwich.
function dateKey(d) {
    return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0')
}

function getDailyGoal() {
    const g = state?.dailyGoal;
    if (g === 0) return Infinity;
    return g || 20
}

function getSessionSize() {
    const s = state?.sessionSize;
    if (s === 0) return Infinity;
    return s || null
}

function hideTimer() {
    document.getElementById('timerContent').style.display = 'none';
    document.getElementById('timerShow').style.display = '';
    state.timerHidden = true;
    save()
}

function showTimerBar() {
    document.getElementById('timerContent').style.display = '';
    document.getElementById('timerShow').style.display = 'none';
    state.timerHidden = false;
    save()
}

function setSessionSize(n) {
    state.sessionSize = n;
    save();
    updateSittingDesc()
}
let state = load();
pruneState(730); // bound state growth: drop daily-log entries older than 2 years

function defaults() {
    return {
        missCount: {},
        sessionsCompleted: 0,
        totalCorrect: 0,
        totalAnswered: 0,
        questionTypes: {
            wordToDef: true,
            defToWord: true,
            sentence: true,
            synonym: true,
            context: true,
            passage: true
        },
        dailyLog: {},
        bestStreak: 0,
        dailyGoal: 20,
        leitner: {},
        retryInSession: false,
        flagged: {},
        difficultyFilter: 'all',
        sessionHistory: [],
        timedMode: false,
        timerSeconds: 30,
        timerHidden: false,
        sessionSize: null,
        diffStats: {
            easy: {
                correct: 0,
                total: 0
            },
            medium: {
                correct: 0,
                total: 0
            },
            hard: {
                correct: 0,
                total: 0
            }
        }
    }
}
const LEITNER_INTERVALS = [0, 1, 3, 7, 14, 30];

function getLeitner(idx) {
    if (!state.leitner[idx]) state.leitner[idx] = {
        b: 0,
        due: todayKey(),
        wt: 0,
        dw: 0,
        sc: 0,
        sy: 0
    };
    return state.leitner[idx]
}

function advanceLeitner(idx) {
    const l = getLeitner(idx);
    l.b = Math.min(l.b + 1, 5);
    const d = new Date();
    d.setDate(d.getDate() + LEITNER_INTERVALS[l.b]);
    l.due = dateKey(d);
    save()
}

function resetLeitner(idx) {
    const l = getLeitner(idx);
    l.b = 1;
    const d = new Date();
    d.setDate(d.getDate() + 1);
    l.due = dateKey(d);
    save()
}

function markForReview(idx) {
    const l = getLeitner(idx);
    l.b = 0;
    l.due = todayKey();
    save();
    renderReview()
}

const TYPE_COUNTERS = {
    wordToDef: 'wt',
    defToWord: 'dw',
    sentence: 'sc',
    synonym: 'sy',
    context: 'cx',
    passage: 'pq'
};

function pickTypeForWord(idx, enabledTypes) {
    const l = getLeitner(idx);
    const typeMap = TYPE_COUNTERS;
    const scored = enabledTypes.map(t => ({
        t,
        c: l[typeMap[t]] || 0
    }));
    scored.sort((a, b) => a.c - b.c);
    const minCount = scored[0].c;
    const ties = scored.filter(x => x.c === minCount);
    return pick(ties).t
}

function countMastery() {
    let n = 0,
        learning = 0,
        unseen = 0;
    for (let i = 0; i < W.length; i++) {
        const l = state.leitner[i];
        if (!l || l.b === 0) unseen++;
        else if (l.b >= 5) n++; // box 5 = Learned, matching bucketName and the word list
        else learning++
    }
    return {
        learned: n,
        learning,
        unseen
    }
}

function load() {
    try {
        const s = localStorage.getItem(LS_KEY);
        const d = defaults();
        if (!s) {
            const old = localStorage.getItem('sat_vocab_v3');
            if (old) {
                const p = JSON.parse(old);
                return {
                    ...d,
                    ...p,
                    dailyLog: p.dailyLog || {},
                    bestStreak: p.bestStreak || 0,
                    questionTypes: {
                        ...d.questionTypes,
                        ...(p.questionTypes || {})
                    },
                    leitner: p.leitner || {}
                }
            }
            return d
        }
        const p = JSON.parse(s);
        return {
            ...d,
            ...p,
            dailyLog: p.dailyLog || {},
            bestStreak: p.bestStreak || 0,
            questionTypes: {
                ...d.questionTypes,
                ...(p.questionTypes || {})
            },
            leitner: p.leitner || {}
        }
    } catch (e) {
        return defaults()
    }
}

function pruneState(days) {
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - days);
    const ck = dateKey(cutoff);
    for (const k of Object.keys(state.dailyLog || {})) {
        if (k < ck) delete state.dailyLog[k]
    }
    if (state.sessionHistory && state.sessionHistory.length > 100) state.sessionHistory = state.sessionHistory.slice(-100)
}

function save() {
    try {
        localStorage.setItem(LS_KEY, JSON.stringify(state))
    } catch (e) {
        // Storage full — prune old history and retry once
        pruneState(400);
        try {
            localStorage.setItem(LS_KEY, JSON.stringify(state))
        } catch (e2) {
            if (!save._warned) {
                save._warned = true;
                alert('Warning: progress could not be saved — browser storage is full.')
            }
        }
    }
}

function todayKey() {
    return dateKey(new Date())
}

function getTodayLog() {
    const k = todayKey();
    if (!state.dailyLog[k]) state.dailyLog[k] = {
        answered: 0,
        correct: 0
    };
    return state.dailyLog[k]
}

function addDailyAnswer(isCorrect) {
    const log = getTodayLog();
    log.answered++;
    if (isCorrect) log.correct++;
    // bestStreak is updated here, after real practice — not inside calcStreak,
    // which render functions call and which should stay a pure getter.
    const streak = calcStreak();
    if (streak > state.bestStreak) state.bestStreak = streak;
    save()
}

function calcStreak() {
    const today = new Date();
    let streak = 0;
    const d = new Date(today);
    const tk = todayKey();
    const eg = getEffectiveGoal();
    const todayDone = (state.dailyLog[tk]?.answered || 0) >= eg;
    if (!todayDone) d.setDate(d.getDate() - 1);
    while (true) {
        const k = dateKey(d);
        const log = state.dailyLog[k];
        if (log && log.answered >= eg) {
            streak++;
            d.setDate(d.getDate() - 1)
        } else break
    }
    return streak
}
let session = {
    words: [],
    current: 0,
    score: 0,
    streak: 0,
    answered: [],
    total: 20
};

function shuffle(a) {
    for (let i = a.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [a[i], a[j]] = [a[j], a[i]]
    }
    return a
}

function pick(arr) {
    return arr[Math.floor(Math.random() * arr.length)]
}
const DIFF_CACHE = W.map(w => w.diff || 'medium');

function pickSessionWords() {
    const ss = getSessionSize();
    const goal = ss !== null ? ss : getDailyGoal();
    const today = todayKey();
    const filter = state.difficultyFilter || 'all';
    const retry = [];
    const due = [];
    const unseen = [];
    const notDue = [];
    W.forEach((w, i) => {
        if (filter !== 'all' && DIFF_CACHE[i] !== filter) return;
        const l = state.leitner[i];
        const obj = {
            ...w,
            _idx: i
        };
        const missed = state.missCount[i] || 0;
        // Words already missed today were just retried in-session; give them
        // breathing room until tomorrow's Leitner review instead of again now.
        const missedToday = (state.missDay || {})[i] === today;
        if (state.retryInSession && missed > 0 && !missedToday && l && l.b <= 1) {
            obj._retry = true;
            retry.push(obj)
        } else if (!l || l.b === 0) {
            unseen.push(obj)
        } else if (l.due <= today) {
            due.push(obj)
        } else {
            notDue.push(obj)
        }
    });
    shuffle(retry);
    shuffle(due);
    shuffle(unseen);
    shuffle(notDue);
    // Cap review words at ~1/3 of the session so a sitting is never wall-to-wall
    // retries, and shuffle the final selection so they aren't front-loaded.
    const cap = goal === Infinity ? retry.length : Math.ceil(goal / 3);
    const pool = [...retry.slice(0, cap), ...due, ...unseen, ...retry.slice(cap), ...notDue];
    const selected = goal === Infinity ? pool : pool.slice(0, goal);
    shuffle(selected);
    return selected
}

function setDiffFilter(f) {
    state.difficultyFilter = f;
    save();
    updateSittingDesc()
}

function countByDiff() {
    const counts = {
        all: 0,
        easy: 0,
        medium: 0,
        hard: 0
    };
    W.forEach((w, i) => {
        counts.all++;
        counts[DIFF_CACHE[i]]++
    });
    return counts
}

function defTokens(d) {
    return d.toLowerCase().replace(/[^a-z ]/g, '').split(/\s+/).filter(w => w.length > 3 && !['that', 'this', 'with', 'from', 'have', 'been', 'were', 'they', 'their', 'being', 'which', 'about', 'would', 'make', 'like', 'into', 'than', 'them', 'then', 'more', 'very', 'when', 'what', 'some', 'only', 'also', 'such', 'most', 'other', 'extremely', 'excessively', 'quality', 'having', 'often', 'manner', 'state', 'tending', 'related'].includes(w))
}

function setSim(ta, tb) {
    if (ta.size === 0 || tb.size === 0) return 0;
    let shared = 0;
    for (const w of ta)
        if (tb.has(w)) shared++;
    return shared / Math.max(ta.size, tb.size)
}

function defSimilarity(a, b) {
    return setSim(new Set(defTokens(a)), new Set(defTokens(b)))
}

// Token sets for all definitions, computed once — getDistractors compares the
// current word against every other word per question, so per-question
// re-tokenization of ~1,700 definitions was the app's hottest path.
const DEF_TOKEN_SETS = W.map(w => new Set(defTokens(w.d)));

function defContains(a, b) {
    const la = a.toLowerCase().replace(/[^a-z ]/g, '').trim();
    const lb = b.toLowerCase().replace(/[^a-z ]/g, '').trim();
    return la.length > 3 && lb.length > 3 && (la.includes(lb) || lb.includes(la))
}
// Verbs that double their final consonant before -ed / -ing (final-syllable stress, CVC ending)
const CONJ_DBL = new Set(['abet', 'abhor', 'annul', 'defer', 'deter', 'dispel', 'extol', 'compel', 'expel', 'impel', 'propel', 'repel', 'rebel', 'excel', 'control', 'patrol',
    'occur', 'recur', 'incur', 'concur', 'demur', 'confer', 'infer', 'prefer', 'refer', 'transfer', 'aver', 'inter', 'abut', 'rebut', 'regret', 'commit', 'omit', 'emit', 'permit', 'remit', 'submit', 'transmit', 'admit', 'acquit', 'allot', 'befit', 'equip', 'enrol', 'instil', 'fulfil',
    'strip', 'rob', 'plod', 'shun', 'stir', 'spur', 'blur', 'slur', 'jot', 'trot', 'swat', 'grip', 'whet', 'throb', 'prod', 'nod', 'skim', 'brim', 'trim', 'strut', 'jut', 'chat', 'wrap', 'swap', 'trap', 'strap', 'scrap', 'stop', 'prop', 'drop', 'grab', 'stab', 'nab', 'jab', 'snub', 'stub', 'scrub', 'drub', 'dub', 'sob', 'lob', 'fib', 'sag', 'nag', 'wag', 'flag', 'brag', 'drag', 'snag', 'lag', 'gag', 'beg', 'jog', 'flog', 'slog', 'clog', 'pin', 'span', 'plan', 'scan', 'ban', 'fan', 'tan', 'con', 'don', 'pun', 'stun', 'grin', 'sin', 'thin', 'skin', 'hum', 'drum', 'sum', 'dot', 'blot', 'clot', 'knot', 'plot', 'spot', 'top', 'chop', 'crop', 'flop', 'hop', 'mop', 'shop', 'slop', 'map', 'nap', 'tap', 'zap', 'dip', 'drip', 'flip', 'nip', 'quip', 'rip', 'ship', 'sip', 'skip', 'slip', 'snip', 'tip', 'trip', 'whip', 'zip', 'bar', 'mar', 'scar', 'star', 'jar', 'tar', 'war', 'bag', 'tag', 'dig', 'rig', 'log', 'hog', 'pet', 'net', 'vet', 'wet', 'bet', 'fret', 'jet', 'gut', 'cut', 'pat', 'mat', 'bat', 'rot', 'pot', 'wed', 'shred', 'thud', 'stud', 'bud', 'skid', 'pad', 'dam', 'cram', 'ram', 'slam', 'jam']);

// Irregular simple-past forms — the naive +ed rule produces non-words for these
// ("upholded", "withdrawed", "forsaked"…), which visibly breaks quiz options.
const IRREG_PAST = {
    uphold: 'upheld', withhold: 'withheld', hold: 'held', behold: 'beheld',
    withdraw: 'withdrew', draw: 'drew', overdraw: 'overdrew',
    forsake: 'forsook', shake: 'shook', take: 'took', partake: 'partook', overtake: 'overtook', undertake: 'undertook', mistake: 'mistook',
    gainsay: 'gainsaid', say: 'said',
    shrink: 'shrank', sink: 'sank', sing: 'sang', spring: 'sprang', ring: 'rang', swim: 'swam', begin: 'began', drink: 'drank',
    forbid: 'forbade', forget: 'forgot', beget: 'begot', get: 'got',
    forgo: 'forwent', forego: 'forewent', undergo: 'underwent', go: 'went',
    rend: 'rent', cling: 'clung', fling: 'flung', sling: 'slung', slink: 'slunk', spin: 'spun', sting: 'stung', string: 'strung', swing: 'swung', wring: 'wrung', hang: 'hung',
    weep: 'wept', sweep: 'swept', sleep: 'slept', keep: 'kept', creep: 'crept', leap: 'leapt',
    seek: 'sought', beseech: 'besought', teach: 'taught', catch: 'caught', fight: 'fought', think: 'thought', bring: 'brought', buy: 'bought',
    stand: 'stood', withstand: 'withstood', understand: 'understood',
    strive: 'strove', thrive: 'throve', weave: 'wove', cleave: 'clove',
    bear: 'bore', forbear: 'forbore', forswear: 'forswore', swear: 'swore', tear: 'tore', wear: 'wore',
    steal: 'stole', speak: 'spoke', bespeak: 'bespoke', break: 'broke', choose: 'chose', freeze: 'froze',
    rise: 'rose', arise: 'arose', write: 'wrote', ride: 'rode', stride: 'strode', drive: 'drove', strike: 'struck',
    bind: 'bound', grind: 'ground', wind: 'wound', find: 'found',
    fly: 'flew', flee: 'fled', slay: 'slew', blow: 'blew', grow: 'grew', outgrow: 'outgrew', know: 'knew', throw: 'threw', overthrow: 'overthrew',
    run: 'ran', overrun: 'overran', come: 'came', become: 'became', overcome: 'overcame',
    give: 'gave', forgive: 'forgave', see: 'saw', foresee: 'foresaw', oversee: 'oversaw', eat: 'ate', fall: 'fell', befall: 'befell',
    lead: 'led', mislead: 'misled', feed: 'fed', breed: 'bred', bleed: 'bled', meet: 'met',
    lose: 'lost', leave: 'left', mean: 'meant', deal: 'dealt', dwell: 'dwelt', kneel: 'knelt',
    send: 'sent', spend: 'spent', lend: 'lent', bend: 'bent', build: 'built',
    sell: 'sold', tell: 'told', foretell: 'foretold', retell: 'retold',
    shine: 'shone', sit: 'sat', win: 'won', dig: 'dug', stick: 'stuck', shoot: 'shot',
    burst: 'burst', cast: 'cast', broadcast: 'broadcast', cost: 'cost', cut: 'cut', hit: 'hit', hurt: 'hurt', let: 'let', put: 'put', quit: 'quit', shed: 'shed', shut: 'shut', split: 'split', spread: 'spread', thrust: 'thrust', beset: 'beset', set: 'set', bet: 'bet', rid: 'rid'
};

function conjugatePast(w) {
    w = w.toLowerCase();
    if (IRREG_PAST[w]) return IRREG_PAST[w];
    if (CONJ_DBL.has(w)) return w + w.slice(-1) + 'ed';
    if (w.endsWith('e')) return w + 'd';
    if (/[^aeiou]y$/.test(w)) return w.slice(0, -1) + 'ied';
    return w + 'ed'
}

function conjugateIng(w) {
    w = w.toLowerCase();
    if (CONJ_DBL.has(w)) return w + w.slice(-1) + 'ing';
    if (w.endsWith('ie')) return w.slice(0, -2) + 'ying';
    if (w.endsWith('e') && !w.endsWith('ee')) return w.slice(0, -1) + 'ing';
    return w + 'ing'
}

function conjugateS(w) {
    w = w.toLowerCase();
    if (/[sxz]$/.test(w) || /[sc]h$/.test(w)) return w + 'es';
    if (/[^aeiou]y$/.test(w)) return w.slice(0, -1) + 'ies';
    if (/[^aeiou]o$/.test(w)) return w + 'es';
    return w + 's'
}

function conjugateN(w) {
    w = w.toLowerCase();
    if (w === 'forsake') return 'forsaken';
    return conjugatePast(w)
}

function getDistractors(correct, count, type) {
    const cIdx = correct._idx != null ? correct._idx : W.findIndex(x => x.w === correct.w);
    const cTokens = cIdx >= 0 ? DEF_TOKEN_SETS[cIdx] : new Set(defTokens(correct.d));
    const SIM = 0.4;
    const scored = [];
    for (let i = 0; i < W.length; i++) {
        const c = W[i];
        if (i === cIdx || c.w === correct.w) continue;
        // Same part of speech is required — a lone noun among verbs is a free elimination
        if (c.p !== correct.p) continue;
        const sim = setSim(cTokens, DEF_TOKEN_SETS[i]);
        if (sim >= SIM) continue; // near-synonym — could be a second right answer
        if (defContains(correct.d, c.d)) continue;
        let s = Math.random() * 2;
        if (c.diff === correct.diff) s += 4; // same difficulty tier reads as equally plausible
        if (type === 'def') {
            const lr = Math.min(c.d.length, correct.d.length) / Math.max(c.d.length, correct.d.length);
            s += lr * 5 // similar definition length — length imbalance gives the answer away
        }
        if (sim > 0.05 && sim < SIM) s += sim * 6; // related-but-wrong is the best trap
        // Confusable lookalikes (shared shape, different meaning) make classic SAT traps
        if (c.w[0] === correct.w[0] && c.w.length >= 6 && Math.abs(c.w.length - correct.w.length) <= 2 && c.w.slice(-4) === correct.w.slice(-4)) s += 8;
        scored.push({
            c,
            i,
            s
        })
    }
    scored.sort((a, b) => b.s - a.s);
    const picks = [],
        pickSets = [];
    for (const {
            c,
            i
        }
        of scored) {
        if (picks.length >= count) break;
        let clash = false;
        for (let p = 0; p < picks.length; p++) {
            if (setSim(pickSets[p], DEF_TOKEN_SETS[i]) >= SIM || defContains(picks[p].d, c.d)) {
                clash = true;
                break
            }
        }
        if (!clash) {
            picks.push(c);
            pickSets.push(DEF_TOKEN_SETS[i])
        }
    }
    // Fallbacks: same-POS first, then anything (only tiny POS classes ever get here)
    if (picks.length < count) {
        for (const x of W) {
            if (picks.length >= count) break;
            if (x.w !== correct.w && x.p === correct.p && !picks.includes(x)) picks.push(x)
        }
    }
    if (picks.length < count) {
        for (const x of W) {
            if (picks.length >= count) break;
            if (x.w !== correct.w && !picks.includes(x)) picks.push(x)
        }
    }
    return type === 'def' ? picks.map(x => x.d) : picks.map(x => x.w)
}

function getEnabledTypes() {
    const qt = state.questionTypes || {};
    const all = ['wordToDef', 'defToWord', 'sentence', 'synonym', 'context', 'passage'];
    const enabled = all.filter(k => qt[k] !== false);
    return enabled.length > 0 ? enabled : ['wordToDef']
}

// Phrasal-verb particles and other glue words: sharing only these does NOT
// make two definitions synonymous ("to cut down" vs "to lay down").
const WEAK_TOKENS = new Set(['down', 'away', 'back', 'over', 'upon', 'onto', 'without', 'toward', 'towards', 'give', 'take', 'make', 'lack', 'lacking', 'something', 'someone', 'person', 'thing', 'especially', 'usually', 'greatly', 'highly', 'strongly']);

// Strongest near-synonym in the word list (same POS, most-similar definition).
// Returns the index, or -1 when nothing clears the threshold.
function findNearSynonym(idx) {
    const me = W[idx];
    let best = -1,
        bestSim = 0.45; // must be a genuinely defensible synonym
    for (let i = 0; i < W.length; i++) {
        if (i === idx || W[i].p !== me.p) continue;
        const sim = setSim(DEF_TOKEN_SETS[idx], DEF_TOKEN_SETS[i]);
        if (sim > bestSim) {
            // at least one shared token must carry real meaning
            let strong = false;
            for (const t of DEF_TOKEN_SETS[idx]) {
                if (DEF_TOKEN_SETS[i].has(t) && !WEAK_TOKENS.has(t)) {
                    strong = true;
                    break
                }
            }
            if (!strong) continue;
            bestSim = sim;
            best = i
        }
    }
    return best
}

function startSession() {
    const words = pickSessionWords();
    if (words.length === 0) {
        alert('No words available for the current filter. Try changing the difficulty filter.');
        return
    }
    session = {
        words: words,
        current: 0,
        score: 0,
        streak: 0,
        answered: [],
        total: words.length,
        enabledTypes: getEnabledTypes()
    };
    document.getElementById('startScreen').classList.add('hidden');
    document.getElementById('quizActive').classList.remove('hidden');
    document.getElementById('summaryView').classList.add('hidden');
    document.body.classList.add('quiz-active');
    showFirstQuizHint();
    showQuestion()
}

// One-time hint — the shortcuts otherwise hide behind the "i" button
function showFirstQuizHint() {
    if (state.hintShown) return;
    // Keyboard shortcuts are meaningless on touch-only devices
    if (!(window.matchMedia && window.matchMedia('(hover: hover)').matches)) return;
    state.hintShown = true;
    save();
    const hint = document.createElement('div');
    hint.className = 'quiz-hint';
    hint.innerHTML = 'Tip: press <strong>1&ndash;4</strong> to answer, <strong>Enter</strong> to continue. Right-click crosses out an option.';
    const card = document.getElementById('qCard');
    card.parentNode.insertBefore(hint, card);
    setTimeout(() => hint.remove(), 12000)
}

function exitSession() {
    stopTimer();
    save();
    document.body.classList.remove('quiz-active');
    document.getElementById('quizActive').classList.add('hidden');
    document.getElementById('startScreen').classList.remove('hidden');
    updateWordPoolInfo();
    updateDailyBanner();
    updateSittingDesc()
}

function showQuestion() {
    const total = session.total;
    const qNum = session.current + 1;
    document.getElementById('qNum').textContent = `No. ${qNum} of ${total}`;
    document.getElementById('scoreDisp').textContent = `Correct: ${session.score}`;
    document.getElementById('streakDisp').textContent = `Streak: ${session.streak}`;
    document.getElementById('progFill').style.width = ((session.current) / total * 100) + '%';
    document.getElementById('feedback').textContent = '';
    document.getElementById('feedback').className = 'feedback';
    document.getElementById('feedback').style.display = 'none';
    document.getElementById('nextBtn').style.display = 'none';
    let wordObj, isRetry = false;
    wordObj = session.words[session.current];
    if (wordObj._retry) isRetry = true;
    let types = session.enabledTypes || ['wordToDef', 'defToWord'];
    const wIdx = wordObj._idx != null ? wordObj._idx : W.findIndex(x => x.w === wordObj.w);
    // Filter to the types this word can actually support
    types = types.filter(t => {
        if (t === 'passage') return typeof CONTEXTQ !== 'undefined' && CONTEXTQ[wordObj.w];
        if (t === 'context') return typeof SENTENCES !== 'undefined' && SENTENCES[wordObj.w];
        return true
    });
    if (types.length === 0) types = ['wordToDef'];
    const qType = wIdx >= 0 ? pickTypeForWord(wIdx, types) : pick(types);
    const card = document.getElementById('qCard');
    const qTypeEl = document.getElementById('qType');
    const qTextEl = document.getElementById('qText');
    const optDiv = document.getElementById('optionsDiv');
    const letters = ['A', 'B', 'C', 'D'];
    let options, correctIdx;
    if (qType === 'wordToDef') {
        qTypeEl.textContent = 'Define the term';
        qTextEl.innerHTML = `<span class="q-word">${wordObj.w}</span>${isRetry?'<span class="retry-badge">Review</span>':''}<div class="q-pos">${wordObj.p}</div>Select the correct definition.`;
        const distractors = getDistractors(wordObj, 3, 'def');
        const optPairs = [{
            t: wordObj.d,
            c: true
        }, ...distractors.map(t => ({
            t,
            c: false
        }))];
        shuffle(optPairs);
        options = optPairs.map(o => o.t);
        correctIdx = optPairs.findIndex(o => o.c)
    } else if (qType === 'defToWord') {
        qTypeEl.textContent = 'Identify the word';
        qTextEl.innerHTML = `Select the word that means:${isRetry?'<span class="retry-badge">Review</span>':''}<div style="margin-top:10px;font-style:italic;color:var(--ink);opacity:.7">"${wordObj.d}"</div>`;
        const distractors = getDistractors(wordObj, 3, 'word');
        const optPairs = [{
            t: wordObj.w,
            c: true
        }, ...distractors.map(t => ({
            t,
            c: false
        }))];
        shuffle(optPairs);
        options = optPairs.map(o => o.t);
        correctIdx = optPairs.findIndex(o => o.c)
    } else if (qType === 'sentence') {
        qTypeEl.textContent = 'Sentence completion';
        const sArr = typeof SENTENCES !== 'undefined' && SENTENCES[wordObj.w];
        let sentence, distractors;
        if (sArr) {
            const entry = sArr[Math.floor(Math.random() * sArr.length)];
            if (Array.isArray(entry)) {
                sentence = entry[0];
                distractors = entry.slice(1);
                if (distractors.length < 3) distractors = getDistractors(wordObj, 3, 'word')
            } else {
                sentence = entry;
                distractors = getDistractors(wordObj, 3, 'word')
            }
        } else {
            sentence = makeSentence(wordObj);
            distractors = getDistractors(wordObj, 3, 'word')
        }
        const rawOpts = [wordObj.w, ...distractors];
        let displaySentence = sentence;
        // Only strip a suffix after the blank when we know how to conjugate it;
        // unknown suffixes stay in the sentence untouched.
        const KNOWN_SUFFIXES = ['d', 'ed', 'ied', 'led', 'red', 'ted', 'ing', 'ting', 's', 'es', 'ies', 'n'];
        const sufMatch = sentence.match(/_____([a-z]+)/i);
        let conjForm = null;
        if (sufMatch && KNOWN_SUFFIXES.includes(sufMatch[1].toLowerCase())) {
            conjForm = sufMatch[1].toLowerCase();
            displaySentence = displaySentence.replace(/_____[a-z]+/i, '_____')
        }
        const artMatch = displaySentence.match(/\b(a|an)\s+_____/i);
        let hasArt = false,
            artCap = false;
        if (artMatch) {
            artCap = /^[A-Z]/.test(artMatch[1]);
            displaySentence = displaySentence.replace(/\b(a|an)\s+_____/i, '_____');
            hasArt = true
        }

        function conjW(w) {
            if (!conjForm) return w;
            if ('d ed ied led red ted'.split(' ').includes(conjForm)) return conjugatePast(w);
            if ('ing ting'.split(' ').includes(conjForm)) return conjugateIng(w);
            if ('s es ies'.split(' ').includes(conjForm)) return conjugateS(w);
            if (conjForm === 'n') return conjugateN(w);
            return w
        }

        function addArticle(w) {
            if (!hasArt) return w;
            // Sound, not spelling: "a uniform/eulogy/utopian" but "an honest/heir/hour"
            let art;
            if (/^(honest|honor|honou?r|heir|hour)/i.test(w)) art = 'an';
            else if (/^(uni(?![nmd])|unan|use|usu|usur|util|utop|ubiq|eu|ewe|once|one)/i.test(w)) art = 'a';
            else art = /^[aeiou]/i.test(w) ? 'an' : 'a';
            if (artCap) art = art.charAt(0).toUpperCase() + art.slice(1);
            return art + ' ' + w
        }
        // Track the correct option through the shuffle instead of matching strings
        // afterwards — string matching breaks when a distractor renders identically.
        const optPairs = rawOpts.map((w, i) => ({
            t: addArticle(conjW(w)),
            c: i === 0
        }));
        shuffle(optPairs);
        options = optPairs.map(o => o.t);
        correctIdx = optPairs.findIndex(o => o.c);
        qTextEl.innerHTML = `${isRetry?'<span class="retry-badge">Review</span>':''}<div class="q-sentence">${displaySentence.replace('_____','<span class="blank">_____</span>')}</div><div style="margin-top:8px;opacity:.55;font-size:.85rem">Select the word that best fills the blank.</div>`
    } else if (qType === 'synonym') {
        qTypeEl.textContent = 'Closest in meaning';
        // Real synonym matching when the list contains a near-synonym; otherwise
        // fall back to the definition format (previously this type was just a
        // relabeled copy of Define-the-term).
        const synIdx = wIdx >= 0 ? findNearSynonym(wIdx) : -1;
        if (synIdx >= 0) {
            qTextEl.innerHTML = `${isRetry?'<span class="retry-badge">Review</span>':''}Which word is closest in meaning to <span class="q-word" style="font-size:1.2em">${wordObj.w}</span>?`;
            const synWord = W[synIdx].w;
            let distractors = getDistractors(wordObj, 4, 'word').filter(d => d !== synWord).slice(0, 3);
            const optPairs = [{
                t: synWord,
                c: true
            }, ...distractors.map(t => ({
                t,
                c: false
            }))];
            shuffle(optPairs);
            options = optPairs.map(o => o.t);
            correctIdx = optPairs.findIndex(o => o.c)
        } else {
            qTextEl.innerHTML = `<span class="q-word">${wordObj.w}</span>${isRetry?'<span class="retry-badge">Review</span>':''}<div class="q-pos">${wordObj.p}</div>Which description is closest in meaning?`;
            const distractors = getDistractors(wordObj, 3, 'def');
            const optPairs = [{
                t: wordObj.d,
                c: true
            }, ...distractors.map(t => ({
                t,
                c: false
            }))];
            shuffle(optPairs);
            options = optPairs.map(o => o.t);
            correctIdx = optPairs.findIndex(o => o.c)
        }
    } else if (qType === 'context') {
        // Digital-SAT "meaning in context" style: the word appears in a real
        // sentence, and the student picks what it most nearly means there.
        qTypeEl.textContent = 'Meaning in context';
        const sArr = SENTENCES[wordObj.w];
        const entry = sArr[Math.floor(Math.random() * sArr.length)];
        const text = Array.isArray(entry) ? entry[0] : entry;
        qTextEl.innerHTML = `${isRetry?'<span class="retry-badge">Review</span>':''}<div class="q-sentence">${fillBlank(text, wordObj.w)}</div><div class="q-stem">As used in this sentence, <em>${wordObj.w}</em> most nearly means:</div>`;
        const distractors = getDistractors(wordObj, 3, 'def');
        const optPairs = [{
            t: wordObj.d,
            c: true
        }, ...distractors.map(t => ({
            t,
            c: false
        }))];
        shuffle(optPairs);
        options = optPairs.map(o => o.t);
        correctIdx = optPairs.findIndex(o => o.c)
    } else if (qType === 'passage') {
        // Digital-SAT text-completion style: short original passage, blank,
        // four same-POS single-word choices.
        qTypeEl.textContent = 'SAT · Words in Context';
        const entries = CONTEXTQ[wordObj.w];
        const entry = entries[Math.floor(Math.random() * entries.length)];
        qTextEl.innerHTML = `${isRetry?'<span class="retry-badge">Review</span>':''}<div class="q-sentence q-passage">${entry.p.replace('_____','<span class="blank">_____</span>')}</div><div class="q-stem">Which choice completes the text with the most logical and precise word?</div>`;
        const optPairs = [{
            t: wordObj.w,
            c: true
        }, ...entry.d.map(t => ({
            t,
            c: false
        }))];
        shuffle(optPairs);
        options = optPairs.map(o => o.t);
        correctIdx = optPairs.findIndex(o => o.c)
    }
    optDiv.innerHTML = '';
    options.forEach((opt, i) => {
        const div = document.createElement('div');
        div.className = 'option';
        div.innerHTML = `<span class="letter">${letters[i]}</span><span>${opt}</span>`;
        div.dataset.idx = i;
        // Real interactive semantics: focusable, announced as a button, and
        // activatable with Enter/Space when focused via Tab.
        div.setAttribute('role', 'button');
        div.setAttribute('aria-pressed', 'false');
        div.tabIndex = 0;
        div.onclick = () => selectOption(i);
        div.onkeydown = (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                e.stopPropagation(); // keep the global handler from instantly submitting
                selectOption(i)
            }
        };
        div.oncontextmenu = (e) => {
            e.preventDefault();
            toggleCrossOut(i)
        };
        // Bluebook-style answer eliminator — right-click doesn't exist on touch
        const x = document.createElement('button');
        x.className = 'opt-x';
        x.setAttribute('aria-label', 'Cross out option ' + letters[i]);
        x.title = 'Cross out';
        x.textContent = '×';
        x.onclick = (e) => {
            e.stopPropagation();
            toggleCrossOut(i)
        };
        div.appendChild(x);
        optDiv.appendChild(div)
    });
    updateFlagBtn(wIdx);
    card.dataset.correctIdx = correctIdx;
    card.dataset.wordJson = JSON.stringify(wordObj);
    card.dataset.isRetry = isRetry;
    card.dataset.qType = qType;
    card.dataset.answered = 'false';
    card.dataset.selectedIdx = '-1';
    document.getElementById('checkBtn').style.display = 'none';
    startTimer()
}

function selectOption(idx) {
    const card = document.getElementById('qCard');
    if (card.dataset.answered === 'true') return;
    const opts = document.querySelectorAll('.option');
    opts.forEach(o => {
        o.classList.remove('selected');
        o.setAttribute('aria-pressed', 'false')
    });
    opts[idx].classList.remove('crossed-out');
    opts[idx].classList.add('selected');
    opts[idx].setAttribute('aria-pressed', 'true');
    card.dataset.selectedIdx = idx;
    document.getElementById('checkBtn').style.display = 'block'
}

// Bluebook-style flag: mark the current word mid-quiz to revisit later.
// Flagged words surface in the Review tab alongside missed words.
function updateFlagBtn(wIdx) {
    const btn = document.getElementById('flagBtn');
    if (!btn) return;
    const flagged = wIdx >= 0 && state.flagged && state.flagged[wIdx];
    btn.classList.toggle('active', !!flagged)
}

function toggleFlagCurrent() {
    const card = document.getElementById('qCard');
    if (!card.dataset.wordJson) return;
    const wordObj = JSON.parse(card.dataset.wordJson);
    const wIdx = wordObj._idx != null ? wordObj._idx : W.findIndex(x => x.w === wordObj.w);
    if (wIdx < 0) return;
    if (!state.flagged) state.flagged = {};
    if (state.flagged[wIdx]) delete state.flagged[wIdx];
    else state.flagged[wIdx] = true;
    save();
    updateFlagBtn(wIdx)
}

function toggleInfo() {
    const p = document.getElementById('infoPanel');
    if (!p.classList.contains('hidden')) {
        p.classList.add('hidden');
        return
    }
    p.classList.remove('hidden');
    setTimeout(() => {
        function close(e) {
            if (!p.contains(e.target) && !e.target.classList.contains('info-btn')) {
                p.classList.add('hidden')
            }
            document.removeEventListener('click', close)
        }
        document.addEventListener('click', close)
    }, 0)
}

function toggleCrossOut(idx) {
    const card = document.getElementById('qCard');
    if (card.dataset.answered === 'true') return;
    const opt = document.querySelectorAll('.option')[idx];
    if (opt.classList.contains('selected')) {
        opt.classList.remove('selected');
        card.dataset.selectedIdx = '-1';
        document.getElementById('checkBtn').style.display = 'none'
    }
    opt.classList.toggle('crossed-out')
}

// Fill a sentence's blank with the (conjugated) word, underlined — used to
// reinforce the word in context at the feedback moment.
function fillBlank(text, word) {
    return text.replace(/_____([a-z]*)/i, (mm, suf) => {
        suf = suf.toLowerCase();
        let w = word;
        if (['d', 'ed', 'ied', 'led', 'red', 'ted'].includes(suf)) w = conjugatePast(word);
        else if (['ing', 'ting'].includes(suf)) w = conjugateIng(word);
        else if (['s', 'es', 'ies'].includes(suf)) w = conjugateS(word);
        else if (suf === 'n') w = conjugateN(word);
        else if (suf) return '<u>' + word + '</u>' + suf;
        return '<u>' + w + '</u>'
    })
}

function exampleSentenceHtml(word) {
    const sArr = typeof SENTENCES !== 'undefined' && SENTENCES[word];
    if (!sArr || !sArr.length) return '';
    const entry = sArr[Math.floor(Math.random() * sArr.length)];
    const text = Array.isArray(entry) ? entry[0] : entry;
    return `<div class="fb-example">${fillBlank(text, word)}</div>`
}

function checkAnswer() {
    const card = document.getElementById('qCard');
    const chosen = parseInt(card.dataset.selectedIdx);
    if (card.dataset.answered === 'true') return;
    stopTimer();
    const timedOut = chosen < 0;
    if (timedOut && !state.timedMode) return;
    card.dataset.answered = 'true';
    const correct = parseInt(card.dataset.correctIdx);
    const wordObj = JSON.parse(card.dataset.wordJson);
    const isRetry = card.dataset.isRetry === 'true';
    const opts = document.querySelectorAll('.option');
    opts.forEach(o => {
        o.classList.add('disabled');
        o.classList.remove('selected')
    });
    opts[correct].classList.add('correct', 'show-correct');
    document.getElementById('checkBtn').style.display = 'none';
    const fb = document.getElementById('feedback');
    fb.style.display = '';
    const wIdx = wordObj._idx != null ? wordObj._idx : W.findIndex(x => x.w === wordObj.w);
    const qType = card.dataset.qType || 'wordToDef';
    if (wIdx >= 0) {
        const l = getLeitner(wIdx);
        const key = TYPE_COUNTERS[qType] || 'wt';
        l[key] = (l[key] || 0) + 1
    }
    if (chosen === correct) {
        session.score++;
        session.streak++;
        state.totalCorrect++;
        // A correct answer on an in-session retry doesn't advance the box —
        // the word was just missed and still belongs in tomorrow's review.
        if (wIdx >= 0 && !wordObj._requeued) advanceLeitner(wIdx);
        fb.innerHTML = `Correct — <em>${wordObj.w}</em>: ${wordObj.d}` + exampleSentenceHtml(wordObj.w);
        fb.className = 'feedback correct-fb';
        const sd = document.getElementById('scoreDisp');
        const sk = document.getElementById('streakDisp');
        sd.textContent = `Correct: ${session.score}`;
        sk.textContent = `Streak: ${session.streak}`;
        sd.classList.remove('score-pop');
        sk.classList.remove('score-pop');
        void sd.offsetWidth;
        sd.classList.add('score-pop');
        if (session.streak > 1) sk.classList.add('score-pop')
    } else {
        if (chosen >= 0) opts[chosen].classList.add('wrong');
        session.streak = 0;
        document.getElementById('streakDisp').textContent = 'Streak: 0';
        if (wIdx >= 0 && !wordObj._requeued) {
            state.missCount[wIdx] = (state.missCount[wIdx] || 0) + 1;
            if (!state.missDay) state.missDay = {};
            state.missDay[wIdx] = todayKey();
            resetLeitner(wIdx)
        }
        // Within-session retry: re-queue the missed word once, 4–8 questions
        // later, so it gets a second attempt this sitting with some spacing.
        if (state.retryInSession && !wordObj._requeued) {
            const again = {
                ...wordObj,
                _retry: true,
                _requeued: true
            };
            const pos = Math.min(session.words.length, session.current + 4 + Math.floor(Math.random() * 5));
            session.words.splice(pos, 0, again);
            session.total = session.words.length
        }
        // "Ask AI why" — explains the confusion between the chosen and correct answers
        let whyBtn = '';
        if (typeof aiExplainWrong === 'function' && chosen >= 0) {
            const chosenText = opts[chosen] ? opts[chosen].children[1].textContent : '';
            whyBtn = ` <button class="ai-why-btn" onclick='aiExplainWrong(${JSON.stringify(wordObj.w)},${JSON.stringify(wordObj.d)},${JSON.stringify(chosenText).replace(/'/g, "&#39;")})'>Ask AI why</button>`
        }
        fb.innerHTML = (timedOut ? `Time's up — the answer is <em>${wordObj.w}</em>: ${wordObj.d}` : `Incorrect — the answer is <em>${wordObj.w}</em>: ${wordObj.d}`) + whyBtn + exampleSentenceHtml(wordObj.w);
        fb.className = 'feedback wrong-fb'
    }
    state.totalAnswered++;
    if (!state.diffStats) state.diffStats = {
        easy: {
            correct: 0,
            total: 0
        },
        medium: {
            correct: 0,
            total: 0
        },
        hard: {
            correct: 0,
            total: 0
        }
    };
    const wd = DIFF_CACHE[wIdx] || 'medium';
    if (state.diffStats[wd]) {
        state.diffStats[wd].total++;
        if (chosen === correct) state.diffStats[wd].correct++
    }
    addDailyAnswer(chosen === correct);
    session.answered.push({
        word: wordObj.w,
        def: wordObj.d,
        idx: wIdx,
        correct: chosen === correct
    });
    save();
    updateDailyBanner();
    document.getElementById('nextBtn').style.display = 'block'
}

function nextQuestion() {
    session.current++;
    if (session.current >= session.total) {
        showSummary()
    } else {
        showQuestion()
    }
}

function showSummary() {
    state.sessionsCompleted++;
    if (!state.sessionHistory) state.sessionHistory = [];
    state.sessionHistory.push({
        date: todayKey(),
        time: new Date().toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
        }),
        score: session.score,
        total: session.total,
        pct: Math.round(session.score / session.total * 100)
    });
    if (state.sessionHistory.length > 100) state.sessionHistory = state.sessionHistory.slice(-100);
    save();
    document.body.classList.remove('quiz-active');
    document.getElementById('quizActive').classList.add('hidden');
    const sv = document.getElementById('summaryView');
    sv.classList.remove('hidden');
    const missed = session.answered.filter(a => !a.correct);
    const total = session.total;
    const pct = Math.round(session.score / total * 100);
    let grade = '';
    if (pct >= 95) grade = 'Exemplary performance.';
    else if (pct >= 80) grade = 'A commendable showing.';
    else if (pct >= 60) grade = 'Satisfactory — room to improve.';
    else grade = 'Further study is advised.';
    let missedHtml = '';
    if (missed.length > 0) {
        const missedMap = {};
        missed.forEach(m => {
            if (missedMap[m.word]) {
                missedMap[m.word].count++
            } else {
                missedMap[m.word] = {
                    word: m.word,
                    def: m.def,
                    count: 1
                }
            }
        });
        const deduped = Object.values(missedMap);
        missedHtml = `<div class="missed-list"><h3>Entries requiring review</h3>${deduped.map(m=>`<div class="missed-item"><span class="mw">${m.word}</span>${m.count>1?` <span style="font-family:monospace;font-size:.75rem;opacity:.6">${m.count}&times;</span>`:''} — <span class="md">${m.def}</span></div>`).join('')}</div>`
    }
    const missedCount = new Set(missed.map(m => m.word)).size;
    const retryBtn = missedCount > 0 ? `<button class="teal" onclick="retrySessionMissed()">Retry Missed (${missedCount})</button>` : '';
    // Streak / goal payoff line at the emotional peak of finishing a sitting
    const streakNow = calcStreak();
    const goalDone = getTodayLog().answered >= getEffectiveGoal();
    const payoff = goalDone && streakNow > 0 ? `<p class="summary-payoff">Daily goal reached — ${streakNow}-day streak</p>` : '';
    sv.innerHTML = `<div class="summary"><h2>${grade}</h2><div class="score-big">${session.score} <span class="of">/ ${total}</span></div><p style="text-align:center;opacity:.65;font-size:.85rem">${pct}% accuracy this sitting</p>${payoff}${missedHtml}<div class="summary-btns">${retryBtn}<button onclick="startSession()">New Sitting</button><button class="secondary" onclick="showView('review')">Missed Log</button><button class="secondary" onclick="showView('stats')">View Record</button></div></div>`
}

function bucketName(b) {
    return ['New', 'Box 1', 'Box 2', 'Box 3', 'Box 4', 'Learned'][b] || 'New'
}

function renderReview() {
    const rv = document.getElementById('reviewView');
    // Missed words plus flagged-but-never-missed words (flag = ⚑ badge)
    const keys = new Set([...Object.keys(state.missCount), ...Object.keys(state.flagged || {})]);
    const missEntries = [...keys].map(idx => {
        const i = Number(idx);
        const l = state.leitner[i];
        return {
            idx: i,
            w: W[i]?.w || '?',
            p: W[i]?.p || '',
            d: W[i]?.d || '',
            count: state.missCount[i] || 0,
            flagged: !!(state.flagged && state.flagged[i]),
            diff: DIFF_CACHE[i] || 'medium',
            bucket: l ? l.b : 0
        }
    }).sort((a, b) => b.count - a.count);
    let listHtml = '';
    if (missEntries.length === 0) {
        listHtml = '<div class="review-empty">No missed words yet. Complete a session to see words you got wrong here.</div>'
    } else {
        listHtml = missEntries.map(w => `<div class="review-word"><span class="rw-term">${w.w}<span class="rw-pos">${w.p}</span> <span class="diff-tag ${w.diff}">${w.diff}</span> <span class="bucket-label">${bucketName(w.bucket)}</span>${w.flagged?' <span class="rw-flag" title="Flagged during practice">&#9873;</span>':''}</span><span class="rw-def">${w.d}</span><span style="display:flex;align-items:center;gap:8px;flex-shrink:0"><span class="rw-count">${w.count>0?w.count+'&times;':''}</span><button class="mark-review-btn" onclick="markForReview(${w.idx})">Reset</button></span></div>`).join('')
    }
    rv.innerHTML = `<div class="review"><h2>Missed Words</h2><p class="review-sub">Words you've gotten wrong, sorted by frequency. Reset sends a word back to the start of the review cycle.</p>${missEntries.length>0?`<div class="review-actions" style="margin-bottom:20px;margin-top:0;padding-top:0;border-top:none"><button class="teal" onclick="practiceMissed()">Practice These</button></div>`:''}${listHtml}${missEntries.length>0?`<div class="review-actions"><button class="danger" onclick="clearMissed()">Clear List</button></div>`:''}</div>`
}

// Start a review session from a list of word indices
function practiceList(idxs) {
    const missIdxs = idxs.filter(i => W[i]);
    if (missIdxs.length === 0) return;
    shuffle(missIdxs);
    const cap = getSessionSize() ?? getDailyGoal();
    const goal = Math.min(missIdxs.length, cap);
    const words = missIdxs.slice(0, goal).map(i => ({
        ...W[i],
        _idx: i,
        _retry: true
    }));
    session = {
        words,
        current: 0,
        score: 0,
        streak: 0,
        answered: [],
        total: goal,
        enabledTypes: getEnabledTypes()
    };
    showView('quiz');
    document.getElementById('startScreen').classList.add('hidden');
    document.getElementById('quizActive').classList.remove('hidden');
    document.getElementById('summaryView').classList.add('hidden');
    document.body.classList.add('quiz-active');
    showQuestion()
}

function practiceMissed() {
    const keys = new Set([...Object.keys(state.missCount), ...Object.keys(state.flagged || {})]);
    practiceList([...keys].map(Number))
}

// Retry only the words missed in the sitting that just ended
function retrySessionMissed() {
    const idxs = [...new Set(session.answered.filter(a => !a.correct && a.idx >= 0).map(a => a.idx))];
    practiceList(idxs)
}

function clearMissed() {
    if (!confirm('Clear the missed words list?')) return;
    state.missCount = {};
    state.flagged = {};
    save();
    renderReview()
}
let chartScale = '1m';

function setChartScale(s) {
    chartScale = s;
    renderStats()
}

function buildProgressChart() {
    const logs = state.dailyLog || {};
    const allDays = Object.keys(logs).sort();
    if (allDays.length === 0) return '<div class="chart-empty">Complete a few sessions to see your progress chart.</div>';
    const now = new Date();
    let cutoff = null;
    if (chartScale === '1d') {
        cutoff = new Date(now);
        cutoff.setDate(cutoff.getDate() - 1)
    } else if (chartScale === '1w') {
        cutoff = new Date(now);
        cutoff.setDate(cutoff.getDate() - 7)
    } else if (chartScale === '1m') {
        cutoff = new Date(now);
        cutoff.setDate(cutoff.getDate() - 30)
    } else if (chartScale === '6m') {
        cutoff = new Date(now);
        cutoff.setDate(cutoff.getDate() - 180)
    } else if (chartScale === '1y') {
        cutoff = new Date(now);
        cutoff.setDate(cutoff.getDate() - 365)
    }
    const cutoffStr = cutoff ? dateKey(cutoff) : null;
    const days = cutoffStr ? allDays.filter(d => d >= cutoffStr) : allDays;
    if (days.length === 0) return '<div class="chart-empty">No data for this time range.</div>';
    if (days.length === 1) {
        const l = logs[days[0]];
        const pct = l.answered > 0 ? Math.round(l.correct / l.answered * 100) : 0;
        return `<div class="chart-single"><span class="chart-single-date">${days[0].slice(5)}</span><span class="chart-single-pct">${pct}%</span></div>`
    }
    const points = days.map(d => {
        const l = logs[d];
        return {
            date: d,
            pct: l.answered > 0 ? Math.round(l.correct / l.answered * 100) : 0
        }
    });
    const w = 560,
        h = 180,
        pad = 40,
        padR = 20,
        padT = 20,
        padB = 30;
    const xStep = (w - pad - padR) / (points.length - 1);
    const yMin = 0,
        yMax = 100;

    function x(i) {
        return pad + i * xStep
    }

    function y(v) {
        return padT + (1 - (v - yMin) / (yMax - yMin)) * (h - padT - padB)
    }
    let pathD = points.map((p, i) => `${i===0?'M':'L'}${x(i).toFixed(1)},${y(p.pct).toFixed(1)}`).join(' ');
    let areaD = pathD + ` L${x(points.length-1).toFixed(1)},${y(0).toFixed(1)} L${x(0).toFixed(1)},${y(0).toFixed(1)} Z`;
    let dots = points.length <= 60 ? points.map((p, i) => `<circle cx="${x(i).toFixed(1)}" cy="${y(p.pct).toFixed(1)}" r="4" fill="var(--ink)" stroke="var(--bg)" stroke-width="2"/>`).join('') : '';
    const labelEvery = points.length <= 7 ? 1 : points.length <= 14 ? 2 : points.length <= 30 ? 5 : points.length <= 90 ? 14 : 30;
    let labels = points.map((p, i) => {
        const d = p.date.slice(5);
        return i % labelEvery === 0 || i === points.length - 1 ? `<text x="${x(i).toFixed(1)}" y="${h-4}" text-anchor="middle" font-size="10" fill="var(--ink-secondary)">${d}</text>` : ''
    }).join('');
    let yLabels = [0, 25, 50, 75, 100].map(v => `<text x="${pad-8}" y="${(y(v)+4).toFixed(1)}" text-anchor="end" font-size="10" fill="var(--ink-secondary)">${v}%</text><line x1="${pad}" y1="${y(v).toFixed(1)}" x2="${w-padR}" y2="${y(v).toFixed(1)}" stroke="var(--line)" stroke-dasharray="3,3"/>`).join('');
    return `<svg viewBox="0 0 ${w} ${h}" class="progress-chart">${yLabels}<path d="${areaD}" fill="var(--accent-soft)" opacity="0.3"/><path d="${pathD}" fill="none" stroke="var(--ink)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>${dots}${labels}</svg>`
}

function chartScaleButtons() {
    const scales = [
        ['all', 'All'],
        ['1y', '1Y'],
        ['6m', '6M'],
        ['1m', '1M'],
        ['1w', '1W'],
        ['1d', '1D']
    ];
    return `<div class="chart-scale-bar">${scales.map(([k,label])=>`<button class="chart-scale-btn${chartScale===k?' active':''}" onclick="setChartScale('${k}')">${label}</button>`).join('')}</div>`
}

function renderDiffStats() {
    const ds = state.diffStats || {
        easy: {
            correct: 0,
            total: 0
        },
        medium: {
            correct: 0,
            total: 0
        },
        hard: {
            correct: 0,
            total: 0
        }
    };
    return ['easy', 'medium', 'hard'].map(d => {
        const s = ds[d] || {
            correct: 0,
            total: 0
        };
        const pct = s.total > 0 ? Math.round(s.correct / s.total * 100) : 0;
        return `<div class="diff-stat-row"><span class="diff-stat-label"><span class="diff-tag ${d}">${d}</span></span><div class="diff-stat-bar-track"><div class="diff-stat-bar-fill" style="width:${pct}%"></div></div><span class="diff-stat-pct">${pct}%</span><span class="diff-stat-count">${s.correct}/${s.total}</span></div>`
    }).join('')
}

function renderSessionHistory() {
    const hist = (state.sessionHistory || []).slice().reverse().slice(0, 20);
    if (hist.length === 0) return '<div class="chart-empty">No sessions recorded yet.</div>';
    return `<div class="session-history-list">${hist.map(h=>`<div class="sh-row"><span class="sh-date">${esc(String(h.date).slice(5))}</span><span class="sh-time">${esc(h.time||'')}</span><span class="sh-score">${h.score}/${h.total}</span><div class="sh-bar-track"><div class="sh-bar-fill${h.pct>=80?' good':h.pct>=60?' ok':' low'}" style="width:${h.pct}%"></div></div><span class="sh-pct">${h.pct}%</span></div>`).join('')}</div>`
}

// Plain-language takeaway under the accuracy chart — a bare line can read as
// failure on days with harder material.
function chartCaption() {
    const logs = state.dailyLog || {};
    const days = Object.keys(logs).sort();
    if (days.length < 2) return '';
    let best = null;
    for (const d of days) {
        const l = logs[d];
        if (l.answered >= 5) {
            const p = Math.round(l.correct / l.answered * 100);
            if (!best || p > best.p) best = {
                d,
                p
            }
        }
    }
    return best ? `<p class="chart-caption">Best day: ${best.p}% on ${best.d.slice(5)}</p>` : ''
}

function renderStats() {
    const sv = document.getElementById('statsView');
    const accuracy = state.totalAnswered > 0 ? Math.round(state.totalCorrect / state.totalAnswered * 100) : 0;
    const m = countMastery();
    const learnedPct = Math.round(m.learned / W.length * 100);
    // Clamp so rounding can't push learned% + learning% past 100 (bar overflow)
    const learningPct = Math.min(Math.round(m.learning / W.length * 100), 100 - learnedPct);
    // First-run: explain what will appear here instead of a wall of zeros
    const intro = state.totalAnswered === 0 ? `<p class="dash-empty">Your record will appear here after your first sitting.</p>` : '';
    // Hero stats first (mastery + accuracy — what actually motivates), raw counters second
    sv.innerHTML = `<div class="dash"><h2>Cumulative Record</h2>${intro}<div class="dash-grid dash-hero"><div class="dash-stat"><div class="num">${m.learned}<span class="of-total"> / ${W.length}</span></div><div class="label">Words Learned</div></div><div class="dash-stat"><div class="num">${accuracy}%</div><div class="label">Accuracy</div></div></div><div class="dash-grid dash-secondary"><div class="dash-stat"><div class="num">${state.totalAnswered}</div><div class="label">Answered</div></div><div class="dash-stat"><div class="num">${state.totalCorrect}</div><div class="label">Correct</div></div><div class="dash-stat"><div class="num">${state.sessionsCompleted}</div><div class="label">Sittings</div></div></div><div class="mastery-bar"><h3>Word Mastery</h3><div class="mastery-track"><div class="mastery-fill"><div class="mf-learned" style="width:${learnedPct}%"></div><div class="mf-learning" style="width:${learningPct}%"></div></div></div><div class="mastery-legend"><span><span class="ml-dot" style="background:var(--good)"></span> Learned ${m.learned}</span><span><span class="ml-dot" style="background:var(--gold)"></span> Learning ${m.learning}</span><span><span class="ml-dot" style="background:var(--paper-tint);border-color:var(--line)"></span> Unseen ${m.unseen}</span></div></div><div class="dash-section"><h3>Accuracy by Difficulty</h3>${renderDiffStats()}</div><div class="dash-section"><h3>Daily Accuracy</h3>${chartScaleButtons()}${buildProgressChart()}${chartCaption()}</div><div class="dash-section"><h3>Session History</h3>${renderSessionHistory()}</div><div class="reset-btn"><button onclick="if(confirm('Erase all progress? This cannot be undone.')){state=defaults();save();renderStats();updateWordPoolInfo()}">Reset Record</button></div></div>`
}

function updateDailyBanner() {
    const banner = document.getElementById('dailyBanner');
    const log = getTodayLog();
    const done = log.answered;
    const streak = calcStreak();
    // Keep the banner visible at 0 progress for returning users — that's
    // exactly when the streak nudge matters. Hide only for brand-new users.
    if (done === 0 && streak === 0 && state.totalAnswered === 0) {
        banner.classList.add('hidden');
        return
    }
    banner.classList.remove('hidden');
    const eg = getEffectiveGoal();
    const pct = Math.min(100, Math.round(done / eg * 100));
    const complete = done >= eg;
    const goalText = eg === Infinity || eg === 1 ? '' : '<span class="of">/ ' + eg + '</span>';
    const countText = complete ? (eg === Infinity || eg === 1 ? done : eg) + ' ' + goalText : done + ' ' + goalText;
    const label = complete ? 'Daily goal reached' : done === 0 ? (streak > 0 ? 'Keep the streak alive' : 'Today\'s goal') : 'Today\'s progress';
    banner.innerHTML = `<div class="db-left"><div class="db-label">${label}</div><div class="db-count">${countText}</div></div><div class="db-bar"><div class="db-bar-track"><div class="db-bar-fill ${complete?'complete':''}" style="width:${pct}%"></div><div class="db-bar-text">${complete?'COMPLETE':done===0?'':pct+'%'}</div></div></div><div class="db-streak"><div class="db-streak-num">${streak}</div><div class="db-streak-label">${streak===1?'Day':'Days'} streak</div></div>`
}
let calYear, calMonth;
(function() {
    const now = new Date();
    calYear = now.getFullYear();
    calMonth = now.getMonth()
})();

function renderCalendar() {
    const cv = document.getElementById('calendarView');
    const now = new Date();
    const todayStr = todayKey();
    const streak = calcStreak();
    const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
    const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const firstDay = new Date(calYear, calMonth, 1).getDay();
    const daysInMonth = new Date(calYear, calMonth + 1, 0).getDate();
    let dayCells = '';
    DAYS.forEach(d => {
        dayCells += `<div class="cal-hdr">${d}</div>`
    });
    for (let i = 0; i < firstDay; i++) dayCells += `<div class="cal-day empty"></div>`;
    for (let d = 1; d <= daysInMonth; d++) {
        const dateStr = `${calYear}-${String(calMonth+1).padStart(2,'0')}-${String(d).padStart(2,'0')}`;
        const log = state.dailyLog[dateStr];
        const isToday = dateStr === todayStr;
        const isFuture = new Date(calYear, calMonth, d) > now;
        const answered = log?.answered || 0;
        const eg = getEffectiveGoal();
        const pct = Math.min(100, Math.round(answered / eg * 100));
        const isDone = answered >= eg;
        let inner = `<div class="cd-num">${d}</div>`;
        if (!isFuture && answered > 0) {
            inner += `<div class="cd-fill"><div class="cd-fill-inner ${isDone?'full':''}" style="width:${pct}%"></div></div>`;
            if (isDone) inner += `<div class="cd-check">&#10003;</div>`;
            else inner += `<div class="cd-count">${answered}</div>`
        } else if (!isFuture) {
            inner += `<div class="cd-fill"><div class="cd-fill-inner" style="width:0"></div></div>`
        }
        // Tap a day for its detail — hover tooltips don't exist on touch
        const clickable = !isFuture && answered > 0;
        dayCells += `<div class="cal-day${isToday?' today':''}${isFuture?' future':''}${clickable?' has-log':''}"${clickable?` onclick="showDayDetail('${dateStr}')"`:''}>${inner}</div>`
    }
    let completedDays = 0,
        totalDaysWorked = 0;
    for (let d = 1; d <= daysInMonth; d++) {
        const dateStr = `${calYear}-${String(calMonth+1).padStart(2,'0')}-${String(d).padStart(2,'0')}`;
        const log = state.dailyLog[dateStr];
        if (log && log.answered > 0) totalDaysWorked++;
        if (log && log.answered >= getEffectiveGoal()) completedDays++
    }
    const calGoal = getEffectiveGoal();
    const calEmpty = Object.keys(state.dailyLog).length === 0 ? `<p class="dash-empty">Practice on any day and it will be logged here.</p>` : '';
    cv.innerHTML = `<div class="streak-display"><div class="streak-num">${streak}</div><div class="streak-label">${streak===1?'Day':'Days'} streak</div><div class="streak-best">Best: ${state.bestStreak} day${state.bestStreak!==1?'s':''}</div></div><div class="cal"><h2>Daily Practice Log</h2><p class="cal-sub">${getDailyGoal()===Infinity?'Any practice':getEffectiveGoal()+' words'} per day to maintain your streak</p>${calEmpty}<div class="cal-nav"><button onclick="calMonth--;if(calMonth<0){calMonth=11;calYear--}renderCalendar()" aria-label="Previous month">&larr;</button><span class="cal-month">${MONTHS[calMonth]} ${calYear}</span><button onclick="calMonth++;if(calMonth>11){calMonth=0;calYear++}renderCalendar()" aria-label="Next month">&rarr;</button></div><div class="cal-grid">${dayCells}</div><div class="cal-day-detail" id="calDayDetail"></div><div class="cal-legend"><span><span class="leg-box leg-teal"></span> In progress</span><span><span class="leg-box leg-gold"></span> Completed (${getDailyGoal()===Infinity?'1':getEffectiveGoal()}+)</span><span>${completedDays} goal day${completedDays!==1?'s':''} &middot; ${totalDaysWorked} practice day${totalDaysWorked!==1?'s':''} this month</span></div></div>`
}

function showDayDetail(dateStr) {
    const el = document.getElementById('calDayDetail');
    if (!el) return;
    const log = state.dailyLog[dateStr];
    if (!log) return;
    const pct = log.answered > 0 ? Math.round(log.correct / log.answered * 100) : 0;
    const met = log.answered >= getEffectiveGoal();
    el.innerHTML = `<strong>${dateStr.slice(5)}</strong> — ${log.answered} answered, ${log.correct} correct (${pct}%)${met?' · goal met &#10003;':''}`
}

function setDailyGoal(n) {
    state.dailyGoal = n;
    save();
    renderSettings();
    updateSittingDesc()
}

function getEffectiveGoal() {
    const dg = getDailyGoal();
    return dg === Infinity ? 1 : dg
}

function renderSettings() {
    const sv = document.getElementById('settingsView');
    const goal = getDailyGoal();
    const dgDisplay = goal === Infinity ? 'Any' : goal;
    const options = [5, 10, 15, 20, 25, 30, 40, 50];
    sv.innerHTML = `<div class="settings-page"><h2>Settings</h2><p class="settings-sub">Configure your daily practice.</p><div class="setting-group"><h3>Daily goal (for streak)</h3><p>Minimum words per day to maintain your streak. Session size and timer can be set from the Practice tab.</p><div class="goal-options">${options.map(n=>`<div class="goal-btn${goal===n?' active':''}" onclick="setDailyGoal(${n})">${n}<div class="goal-label">words</div></div>`).join('')}<div class="goal-btn${goal===Infinity?' active':''}" onclick="setDailyGoal(0)">&infin;<div class="goal-label">any</div></div></div></div><div class="setting-group"><h3>Question types</h3><p>Toggle which question formats appear during practice.</p><div class="settings"><div class="chk-row"><input type="checkbox" id="sChkWordDef" ${state.questionTypes.wordToDef!==false?'checked':''}><label for="sChkWordDef">Define the term<span class="chk-desc">Given a word, select the correct definition</span></label></div><div class="chk-row"><input type="checkbox" id="sChkDefWord" ${state.questionTypes.defToWord!==false?'checked':''}><label for="sChkDefWord">Identify the word<span class="chk-desc">Given a definition, select the matching word</span></label></div><div class="chk-row"><input type="checkbox" id="sChkSentence" ${state.questionTypes.sentence!==false?'checked':''}><label for="sChkSentence">Sentence completion<span class="chk-desc">Fill in the blank with the word that fits the context</span></label></div><div class="chk-row"><input type="checkbox" id="sChkSynonym" ${state.questionTypes.synonym!==false?'checked':''}><label for="sChkSynonym">Closest in meaning<span class="chk-desc">Select the word most similar in meaning to the given term</span></label></div><div class="chk-row"><input type="checkbox" id="sChkContext" ${state.questionTypes.context!==false?'checked':''}><label for="sChkContext">Meaning in context<span class="chk-desc">SAT style: what a word most nearly means in a given sentence</span></label></div><div class="chk-row"><input type="checkbox" id="sChkPassage" ${state.questionTypes.passage!==false?'checked':''}><label for="sChkPassage">SAT passage completion<span class="chk-desc">Official digital-SAT format: complete a short passage with the most logical and precise word</span></label></div></div><div class="review-actions" style="margin-top:16px"><button onclick="saveSettingsTypes()">Save question types</button></div></div><div class="setting-group"><h3>Practice mode</h3><p>Adjust how your practice sessions work.</p><div class="settings"><div class="chk-row"><input type="checkbox" id="sChkRetry" ${state.retryInSession?'checked':''} onchange="state.retryInSession=this.checked;save()"><label for="sChkRetry">Retry missed words in session<span class="chk-desc">Words you get wrong will reappear later in the same sitting for another attempt</span></label></div></div></div>${typeof aiSettingsHtml==='function'?aiSettingsHtml():''}<div class="setting-group"><h3>Backup</h3><p>Export your progress to a file, or import a previous backup.</p><div class="review-actions" style="justify-content:flex-start;gap:12px"><button onclick="exportProgress()">Export Progress</button><button onclick="importProgress()">Import Progress</button></div></div><div class="setting-group"><h3>Reset</h3><p>Clear all progress data and start fresh.</p><div class="review-actions" style="justify-content:flex-start"><button class="danger" onclick="if(confirm('Erase all progress? This cannot be undone.')){state=defaults();save();renderSettings();updateWordPoolInfo();updateDailyBanner();updateSittingDesc()}">Reset all progress</button></div></div></div>`
}

function exportProgress() {
    const data = JSON.stringify(state, null, 2);
    const blob = new Blob([data], {
        type: 'application/json'
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `sat-vocab-backup-${todayKey()}.json`;
    a.click();
    // Revoke async — a synchronous revoke can race the download in Safari
    setTimeout(() => URL.revokeObjectURL(url), 1000)
}

// Deep-validate an imported backup: every field is type/range-checked and
// invalid entries are dropped, so a malformed or crafted file can't corrupt
// state or inject markup into innerHTML render paths.
function sanitizeImport(imp) {
    const d = defaults();
    const isDate = s => typeof s === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(s);
    const nonNegInt = (v, max) => (typeof v === 'number' && isFinite(v) && v >= 0 && v <= (max || 1e9)) ? Math.floor(v) : null;
    const out = d;
    if (imp.missCount && typeof imp.missCount === 'object' && !Array.isArray(imp.missCount)) {
        for (const [k, v] of Object.entries(imp.missCount)) {
            const idx = nonNegInt(Number(k), 99999);
            const n = nonNegInt(v, 99999);
            if (idx !== null && n !== null && n > 0) out.missCount[idx] = n
        }
    }
    out.sessionsCompleted = nonNegInt(imp.sessionsCompleted) ?? 0;
    out.totalCorrect = nonNegInt(imp.totalCorrect) ?? 0;
    out.totalAnswered = nonNegInt(imp.totalAnswered) ?? 0;
    if (out.totalCorrect > out.totalAnswered) out.totalCorrect = out.totalAnswered;
    if (imp.questionTypes && typeof imp.questionTypes === 'object') {
        for (const k of Object.keys(out.questionTypes)) {
            if (typeof imp.questionTypes[k] === 'boolean') out.questionTypes[k] = imp.questionTypes[k]
        }
    }
    if (imp.dailyLog && typeof imp.dailyLog === 'object' && !Array.isArray(imp.dailyLog)) {
        for (const [k, v] of Object.entries(imp.dailyLog)) {
            if (!isDate(k) || !v || typeof v !== 'object') continue;
            const a = nonNegInt(v.answered, 99999),
                c = nonNegInt(v.correct, 99999);
            if (a !== null && c !== null) out.dailyLog[k] = {
                answered: a,
                correct: Math.min(c, a)
            }
        }
    }
    out.bestStreak = nonNegInt(imp.bestStreak, 99999) ?? 0;
    const goal = nonNegInt(imp.dailyGoal, 1000);
    if (goal !== null) out.dailyGoal = goal;
    if (imp.leitner && typeof imp.leitner === 'object' && !Array.isArray(imp.leitner)) {
        for (const [k, v] of Object.entries(imp.leitner)) {
            const idx = nonNegInt(Number(k), 99999);
            if (idx === null || !v || typeof v !== 'object') continue;
            const b = nonNegInt(v.b, 5);
            if (b === null || !isDate(v.due)) continue;
            out.leitner[idx] = {
                b: b,
                due: v.due,
                wt: nonNegInt(v.wt, 99999) ?? 0,
                dw: nonNegInt(v.dw, 99999) ?? 0,
                sc: nonNegInt(v.sc, 99999) ?? 0,
                sy: nonNegInt(v.sy, 99999) ?? 0
            }
        }
    }
    if (typeof imp.retryInSession === 'boolean') out.retryInSession = imp.retryInSession;
    if (imp.flagged && typeof imp.flagged === 'object' && !Array.isArray(imp.flagged)) {
        for (const k of Object.keys(imp.flagged)) {
            const idx = nonNegInt(Number(k), 99999);
            if (idx !== null && imp.flagged[k]) out.flagged[idx] = true
        }
    }
    if (['all', 'easy', 'medium', 'hard'].includes(imp.difficultyFilter)) out.difficultyFilter = imp.difficultyFilter;
    if (Array.isArray(imp.sessionHistory)) {
        out.sessionHistory = imp.sessionHistory.filter(h => h && typeof h === 'object' && isDate(h.date)).map(h => ({
            date: h.date,
            time: typeof h.time === 'string' ? h.time.slice(0, 20) : '',
            score: nonNegInt(h.score, 99999) ?? 0,
            total: nonNegInt(h.total, 99999) ?? 0,
            pct: nonNegInt(h.pct, 100) ?? 0
        })).slice(-100)
    }
    if (typeof imp.timedMode === 'boolean') out.timedMode = imp.timedMode;
    const ts = nonNegInt(imp.timerSeconds, 600);
    if (ts !== null && ts >= 5) out.timerSeconds = ts;
    if (typeof imp.timerHidden === 'boolean') out.timerHidden = imp.timerHidden;
    const ss = imp.sessionSize === null ? null : nonNegInt(imp.sessionSize, 10000);
    out.sessionSize = ss;
    if (imp.diffStats && typeof imp.diffStats === 'object') {
        for (const k of ['easy', 'medium', 'hard']) {
            const s = imp.diffStats[k];
            if (s && typeof s === 'object') {
                const t = nonNegInt(s.total) ?? 0,
                    c = nonNegInt(s.correct) ?? 0;
                out.diffStats[k] = {
                    correct: Math.min(c, t),
                    total: t
                }
            }
        }
    }
    return out
}

function importProgress() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = e => {
        const file = e.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = ev => {
            try {
                const imported = JSON.parse(ev.target.result);
                if (typeof imported !== 'object' || imported === null || Array.isArray(imported)) throw new Error('bad');
                state = sanitizeImport(imported);
                save();
                renderSettings();
                updateDailyBanner();
                updateSittingDesc();
                alert('Progress imported successfully!')
            } catch (err) {
                alert('Invalid backup file.')
            }
        };
        reader.readAsText(file)
    };
    input.click()
}

function saveSettingsTypes() {
    state.questionTypes = {
        wordToDef: document.getElementById('sChkWordDef').checked,
        defToWord: document.getElementById('sChkDefWord').checked,
        sentence: document.getElementById('sChkSentence').checked,
        synonym: document.getElementById('sChkSynonym').checked,
        context: document.getElementById('sChkContext').checked,
        passage: document.getElementById('sChkPassage').checked
    };
    save();
    renderSettings()
}

// Words due for review today vs never-seen words (drives the home dashboard)
function countDueNew() {
    const today = todayKey();
    let due = 0,
        fresh = 0;
    W.forEach((w, i) => {
        const l = state.leitner[i];
        if (!l || l.b === 0) fresh++;
        else if (l.b < 5 && l.due <= today) due++
    });
    return {
        due,
        fresh
    }
}

function updateSittingDesc() {
    const el = document.getElementById('startScreen');
    if (!el) return;
    let html = '';
    const dc = countByDiff();
    const f = state.difficultyFilter || 'all';
    // Status-forward home: what's due, the streak, and mastery — before the CTA
    const dn = countDueNew();
    const m = countMastery();
    const streak = calcStreak();
    const learnedPct = m.learned / W.length * 100;
    const learningPct = m.learning / W.length * 100;
    html += `<div class="home-dashboard"><div class="home-stats">` +
        `<div class="home-stat"><div class="home-stat-num">${dn.due}</div><div class="home-stat-label">Due today</div></div>` +
        `<div class="home-stat"><div class="home-stat-num">${streak}</div><div class="home-stat-label">Day streak</div></div>` +
        `<div class="home-stat"><div class="home-stat-num">${m.learned}</div><div class="home-stat-label">Learned</div></div>` +
        `</div><div class="home-mastery"><div class="home-mastery-track" style="display:flex">` +
        `<div style="width:${learnedPct}%;background:var(--learned-color)"></div>` +
        `<div style="width:${Math.min(learningPct,100-learnedPct)}%;background:var(--learning-color)"></div>` +
        `</div><div class="home-mastery-legend"><span><span class="ml-dot" style="background:var(--learned-color)"></span> ${m.learned} learned</span><span><span class="ml-dot" style="background:var(--learning-color)"></span> ${m.learning} learning</span><span><span class="ml-dot" style="background:var(--unseen-color)"></span> ${m.unseen} unseen</span></div></div></div>`;
    const cta = dn.due > 0 ? `Start — ${dn.due} due for review` : `Start Practicing`;
    html += `<button onclick="startSession()">${cta}</button>`;
    html += `<button id="optionsToggle" class="options-toggle${optionsOpen?' open':''}" onclick="toggleOptions()">Customize <span class="toggle-arrow">${optionsOpen?'▴':'▾'}</span></button>`;
    html += `<div id="optionsBox" class="options-box${optionsOpen?' open':''}">`;
    html += `<div class="diff-filter"><span class="diff-filter-label">Focus</span><button class="diff-chip${f==='all'?' active':''}" onclick="setDiffFilter('all')">All <span class="chip-count">${dc.all}</span></button><button class="diff-chip easy${f==='easy'?' active':''}" onclick="setDiffFilter('easy')">Easy <span class="chip-count">${dc.easy}</span></button><button class="diff-chip medium${f==='medium'?' active':''}" onclick="setDiffFilter('medium')">Medium <span class="chip-count">${dc.medium}</span></button><button class="diff-chip hard${f==='hard'?' active':''}" onclick="setDiffFilter('hard')">Hard <span class="chip-count">${dc.hard}</span></button></div>`;
    const ss = getSessionSize();
    const effectiveSize = ss !== null ? ss : getDailyGoal();
    const sizeOptions = [10, 20, 30, 50];
    const isCustom = ss !== null && !sizeOptions.includes(ss) && ss !== Infinity;
    html += `<div class="session-size-row"><span class="diff-filter-label">Session</span>${sizeOptions.map(n=>`<button class="size-btn${effectiveSize===n?' active':''}" onclick="setSessionSize(${n})">${n}</button>`).join('')}<button class="size-btn${effectiveSize===Infinity?' active':''}" onclick="setSessionSize(0)">&infin;</button><button class="size-btn custom-size-btn${isCustom?' active':''}" onclick="promptCustomSize()">Custom</button></div>`;
    const timerOn = state.timedMode;
    const ts = state.timerSeconds || 30;
    html += `<div class="session-timer-row"><span class="diff-filter-label">Timer</span><button class="size-btn${!timerOn?' active':''}" onclick="state.timedMode=false;save();updateSittingDesc()">Off</button>${[15,20,30,45,60].map(n=>`<button class="size-btn${timerOn&&ts===n?' active':''}" onclick="state.timedMode=true;state.timerSeconds=${n};save();updateSittingDesc()">${n}s</button>`).join('')}</div>`;
    html += `</div>`;
    el.innerHTML = html
}

function promptCustomSize() {
    const val = prompt('Enter number of words per session:');
    if (val === null) return;
    const n = parseInt(val);
    if (!isNaN(n) && n > 0 && n <= W.length) {
        setSessionSize(n)
    } else {
        alert('Please enter a number between 1 and ' + W.length)
    }
}
let optionsOpen = false;

function toggleOptions() {
    optionsOpen = !optionsOpen;
    document.getElementById('optionsBox').classList.toggle('open', optionsOpen);
    document.getElementById('optionsToggle').classList.toggle('open', optionsOpen);
    document.querySelector('.toggle-arrow').textContent = optionsOpen ? '▴' : '▾'
}
let wlDiffFilter = 'all',
    wlSort = 'az';

function setWlDiff(f) {
    wlDiffFilter = f;
    renderWordList()
}

function setWlSort(s) {
    wlSort = s;
    renderWordList()
}

function renderWordList() {
    var container = document.getElementById('wordsView');
    var indices = [];
    for (var i = 0; i < W.length; i++) {
        if (wlDiffFilter === 'weak') {
            // Weak = missed at least once, or still in the early boxes after being seen
            var lw = state.leitner[i];
            var isWeak = (state.missCount[i] || 0) > 0 || (lw && lw.b > 0 && lw.b <= 2);
            if (!isWeak) continue
        } else if (wlDiffFilter !== 'all' && DIFF_CACHE[i] !== wlDiffFilter) continue;
        indices.push(i)
    }
    if (wlSort === 'za') {
        indices.sort(function(a, b) {
            return W[b].w.localeCompare(W[a].w)
        })
    } else if (wlSort === 'most') {
        indices.sort(function(a, b) {
            return (state.missCount[b] || 0) - (state.missCount[a] || 0)
        })
    } else if (wlSort === 'least') {
        indices.sort(function(a, b) {
            return (state.missCount[a] || 0) - (state.missCount[b] || 0)
        })
    } else {
        indices.sort(function(a, b) {
            return W[a].w.localeCompare(W[b].w)
        })
    }
    var html = '<div class="wl-wrap">';
    html += '<div class="wl-search-row"><input type="text" class="wl-search" id="wlSearch" placeholder="Search words..." oninput="filterWordList()"><span class="wl-count" id="wlCount">' + indices.length + ' words</span></div>';
    html += '<div class="wl-controls"><div class="wl-filter-row"><span class="diff-filter-label">Filter</span><button class="size-btn' + (wlDiffFilter === 'all' ? ' active' : '') + '" onclick="setWlDiff(\'all\')">All</button><button class="size-btn' + (wlDiffFilter === 'easy' ? ' active' : '') + '" onclick="setWlDiff(\'easy\')">Easy</button><button class="size-btn' + (wlDiffFilter === 'medium' ? ' active' : '') + '" onclick="setWlDiff(\'medium\')">Medium</button><button class="size-btn' + (wlDiffFilter === 'hard' ? ' active' : '') + '" onclick="setWlDiff(\'hard\')">Hard</button><button class="size-btn' + (wlDiffFilter === 'weak' ? ' active' : '') + '" onclick="setWlDiff(\'weak\')">Weak</button></div><div class="wl-filter-row"><span class="diff-filter-label">Sort</span><button class="size-btn' + (wlSort === 'az' ? ' active' : '') + '" onclick="setWlSort(\'az\')">A–Z</button><button class="size-btn' + (wlSort === 'za' ? ' active' : '') + '" onclick="setWlSort(\'za\')">Z–A</button><button class="size-btn' + (wlSort === 'most' ? ' active' : '') + '" onclick="setWlSort(\'most\')">Most missed</button><button class="size-btn' + (wlSort === 'least' ? ' active' : '') + '" onclick="setWlSort(\'least\')">Least missed</button></div></div>';
    html += '<div class="wl-list" id="wlList">';
    var alphaSort = wlSort === 'az' || wlSort === 'za';
    var lastLetter = '';
    indices.forEach(function(i) {
        var word = W[i];
        var diff = DIFF_CACHE[i];
        var l = state.leitner[i];
        var bucket = l ? l.b : 0;
        var bName = bucketName(bucket);
        var missed = state.missCount[i] || 0;
        var mastery = bucket === 5 ? 'learned' : bucket > 0 ? 'learning' : 'unseen';
        // Sticky letter dividers give the 1,700-word alphabetical scroll landmarks
        if (alphaSort) {
            var letter = word.w.charAt(0).toUpperCase();
            if (letter !== lastLetter) {
                lastLetter = letter;
                html += '<div class="wl-letter">' + letter + '</div>'
            }
        }
        html += '<div class="wl-item" data-word="' + word.w.toLowerCase() + '" data-diff="' + diff + '" data-missed="' + missed + '" data-idx="' + i + '" onclick="toggleWordExpand(this)">';
        html += '<div class="wl-main">';
        html += '<span class="wl-dot ' + mastery + '" title="' + bName + '"></span>';
        html += '<span class="wl-word">' + word.w + '</span>';
        html += '<span class="wl-pos">' + word.p + '</span>';
        html += '<span class="wl-def">' + word.d + '</span>';
        html += '</div>';
        html += '<div class="wl-tags">';
        html += '<span class="diff-tag ' + diff + '">' + diff + '</span>';
        html += '<span class="wl-mastery ' + mastery + '">' + bName + '</span>';
        if (missed > 0) html += '<span class="wl-missed">' + missed + '&times; missed</span>';
        html += '</div>';
        // Expanded detail is filled lazily on first expand — building example
        // sentences for all 1,700+ rows up front dominated render time.
        html += '<div class="wl-expand"></div>';
        html += '</div>'
    });
    html += '</div></div>';
    container.innerHTML = html
}

function buildWordExpand(i) {
    var word = W[i];
    var l = state.leitner[i];
    var missed = state.missCount[i] || 0;
    var bName = bucketName(l ? l.b : 0);
    var totalSeen = (l ? (l.wt || 0) + (l.dw || 0) + (l.sc || 0) + (l.sy || 0) : 0);
    var sentences = typeof SENTENCES !== 'undefined' && SENTENCES[word.w];
    var sentHtml = '';
    if (sentences && sentences.length > 0) {
        sentHtml = sentences.slice(0, 2).map(function(s) {
            var text = Array.isArray(s) ? s[0] : s;
            return '<div class="wl-ex-sentence">' + text.replace('_____', '<u>' + word.w + '</u>') + '</div>'
        }).join('')
    } else {
        sentHtml = '<div class="wl-ex-sentence"><em>No examples available.</em></div>'
    }
    // AI tutor hook (only when ai.js is loaded)
    var aiBtn = typeof aiExplainWord === 'function' ?
        '<button class="ai-explain-btn" onclick="event.stopPropagation();aiExplainWord(' + JSON.stringify(word.w).replace(/"/g, '&quot;') + ',' + JSON.stringify(word.d).replace(/"/g, '&quot;') + ')">AI Explain</button>' : '';
    return '<div class="wl-ex-section"><div class="wl-ex-label">EXAMPLE USAGE</div>' + sentHtml + '</div>' +
        '<div class="wl-ex-stats"><span>Seen: ' + totalSeen + '</span><span>Missed: ' + missed + '</span><span>Box: ' + bName + '</span>' + (l && l.due ? '<span>Due: ' + esc(String(l.due).slice(5)) + '</span>' : '') + aiBtn + '</div>'
}

function toggleWordExpand(el) {
    var expanded = el.classList.toggle('expanded');
    if (expanded) {
        var ex = el.querySelector('.wl-expand');
        if (ex && !ex.dataset.loaded) {
            ex.dataset.loaded = '1';
            ex.innerHTML = buildWordExpand(Number(el.dataset.idx))
        }
    }
}

function filterWordList() {
    var q = document.getElementById('wlSearch').value.toLowerCase();
    var items = document.querySelectorAll('.wl-item');
    var count = 0;
    items.forEach(function(item) {
        var match = item.dataset.word.includes(q) || item.querySelector('.wl-def').textContent.toLowerCase().includes(q);
        item.style.display = match ? '' : 'none';
        if (match) count++
    });
    // Letter dividers are meaningless over filtered results — hide while searching
    document.querySelectorAll('.wl-letter').forEach(function(el) {
        el.style.display = q ? 'none' : ''
    });
    document.getElementById('wlCount').textContent = count + ' words'
}
let timerInterval = null;
let timerDeadline = 0;

function startTimer() {
    if (!state.timedMode) {
        document.getElementById('timerTop').style.display = 'none';
        return
    }
    clearInterval(timerInterval);
    const totalMs = (state.timerSeconds || 30) * 1000;
    // Wall-clock deadline instead of a decrementing counter — setInterval is
    // throttled in background tabs and the old countdown drifted badly.
    timerDeadline = Date.now() + totalMs;
    const bar = document.getElementById('timerBar');
    const text = document.getElementById('timerText');
    const top = document.getElementById('timerTop');
    if (!bar || !top) return;
    top.style.display = 'block';
    if (state.timerHidden) {
        document.getElementById('timerContent').style.display = 'none';
        document.getElementById('timerShow').style.display = ''
    } else {
        document.getElementById('timerContent').style.display = '';
        document.getElementById('timerShow').style.display = 'none'
    }
    bar.style.width = '100%';
    bar.classList.remove('timer-low');
    text.classList.remove('timer-low-text');
    text.textContent = (state.timerSeconds || 30) + 's';
    timerInterval = setInterval(() => {
        const msLeft = timerDeadline - Date.now();
        if (msLeft <= 0) {
            clearInterval(timerInterval);
            timerInterval = null;
            text.textContent = '0s';
            bar.style.width = '0%';
            timeUp();
            return
        }
        const secLeft = Math.ceil(msLeft / 1000);
        bar.style.width = (msLeft / totalMs * 100) + '%';
        text.textContent = secLeft + 's';
        if (secLeft <= 5) {
            bar.classList.add('timer-low');
            text.classList.add('timer-low-text')
        }
    }, 250)
}

function stopTimer() {
    clearInterval(timerInterval);
    timerInterval = null;
    const top = document.getElementById('timerTop');
    if (top) top.style.display = 'none'
}

function timeUp() {
    const card = document.getElementById('qCard');
    if (card.dataset.answered === 'true') return;
    card.dataset.selectedIdx = '-1';
    checkAnswer()
}

function showView(v) {
    document.getElementById('quizView').classList.toggle('hidden', v !== 'quiz');
    document.getElementById('calendarView').classList.toggle('hidden', v !== 'calendar');
    document.getElementById('reviewView').classList.toggle('hidden', v !== 'review');
    document.getElementById('statsView').classList.toggle('hidden', v !== 'stats');
    document.getElementById('settingsView').classList.toggle('hidden', v !== 'settings');
    document.getElementById('wordsView').classList.toggle('hidden', v !== 'words');
    const navMap = {
        navQuiz: 'quiz',
        navCal: 'calendar',
        navReview: 'review',
        navStats: 'stats',
        navSettings: 'settings',
        navWords: 'words'
    };
    for (const [id, view] of Object.entries(navMap)) {
        const btn = document.getElementById(id);
        btn.classList.toggle('active', v === view);
        if (v === view) btn.setAttribute('aria-current', 'page');
        else btn.removeAttribute('aria-current')
    }
    if (v === 'stats') renderStats();
    if (v === 'review') renderReview();
    if (v === 'calendar') renderCalendar();
    if (v === 'settings') renderSettings();
    if (v === 'words') renderWordList();
    if (v === 'quiz') {
        updateWordPoolInfo();
        updateDailyBanner();
        updateSittingDesc()
    }
}

function updateWordPoolInfo() {}
document.addEventListener('keydown', e => {
    if (document.getElementById('quizActive').classList.contains('hidden')) return;
    if (e.repeat) return; // a held Enter must not check-then-skip through feedback
    const card = document.getElementById('qCard');
    const key = e.key.toLowerCase();
    if (key === 'escape') {
        exitSession();
        return
    }
    if (card.dataset.answered === 'false') {
        let idx = -1;
        if (key === '1' || key === 'a') idx = 0;
        if (key === '2' || key === 'b') idx = 1;
        if (key === '3' || key === 'c') idx = 2;
        if (key === '4' || key === 'd') idx = 3;
        if (idx >= 0) {
            selectOption(idx)
        } else if (key === 'enter' || key === ' ') {
            e.preventDefault();
            if (parseInt(card.dataset.selectedIdx) >= 0) checkAnswer()
        }
    } else if (key === 'enter' || key === ' ') {
        e.preventDefault();
        nextQuestion()
    }
});

function toggleTheme() {
    const html = document.documentElement;
    const isDark = html.getAttribute('data-theme') === 'dark';
    html.setAttribute('data-theme', isDark ? 'light' : 'dark');
    localStorage.setItem('sat_theme', isDark ? 'light' : 'dark');
    document.getElementById('themeToggle').innerHTML = isDark ? '&#9790;' : '&#9728;'
}
// Theme is applied by the inline <head> script before first paint (no flash);
// here we only sync the toggle-button glyph.
(function() {
    if (document.documentElement.getAttribute('data-theme') === 'dark') {
        document.getElementById('themeToggle').innerHTML = '&#9728;'
    }
})();
updateDailyBanner();
updateSittingDesc();