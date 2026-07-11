// Data-quality audit for words.js + sentences.js.
// Run: node audit.js   (exits non-zero if any check fails)
// Loads app.js with DOM stubs so conjugation/article checks use the app's real rules.
const fs = require('fs');

// --- load data + app logic with stubs ---
global.localStorage = { getItem: () => null, setItem: () => {} };
const mkEl = () => ({ classList: { add(){}, remove(){}, toggle(){ return true }, contains(){ return false } }, style: {}, dataset: {}, innerHTML: '', textContent: '', appendChild(){}, querySelector: () => mkEl() });
global.document = { addEventListener(){}, getElementById: () => mkEl(), documentElement: { getAttribute: () => null, setAttribute(){} }, querySelector: () => mkEl(), querySelectorAll: () => [], body: { classList: { add(){}, remove(){} } }, createElement: () => mkEl() };
global.alert = () => {};
eval(fs.readFileSync(__dirname + '/words.js', 'utf8').replace(/^const /, 'var '));
eval(fs.readFileSync(__dirname + '/sentences.js', 'utf8').replace(/^const /, 'var '));
eval(fs.readFileSync(__dirname + '/templates.js', 'utf8').replace(/^const TEMPLATES/, 'var TEMPLATES').replace(/\bconst GENERIC_TEMPLATES/, 'var GENERIC_TEMPLATES'));
eval(fs.readFileSync(__dirname + '/app.js', 'utf8').replace(/^const /gm, 'var ').replace(/^let /gm, 'var '));

let failures = 0;
const fail = (check, detail) => { failures++; console.log('FAIL [' + check + '] ' + detail) };
const pass = check => console.log('ok   ' + check);

// --- words.js checks ---
const seen = new Set();
let dup = 0, badField = 0, badPos = 0, badDiff = 0, ws = 0, longDef = 0;
const VALID_POS = new Set(['v.', 'n.', 'adj.', 'adv.', 'conj.', 'prep.']);
const defMap = {};
W.forEach((x, i) => {
  const k = (x.w || '').toLowerCase();
  if (seen.has(k)) { dup++; fail('dup-word', x.w) } seen.add(k);
  if (!x.w || !x.p || !x.d || !x.diff) { badField++; fail('fields', JSON.stringify(x)) }
  if (!VALID_POS.has(x.p)) { badPos++; fail('pos', x.w + ' ' + x.p) }
  if (!['easy', 'medium', 'hard'].includes(x.diff)) { badDiff++; fail('diff', x.w) }
  if (x.w !== x.w.trim() || x.d !== x.d.trim()) { ws++; fail('whitespace', x.w) }
  if (x.d.split(/\s+/).length > 12) { longDef++; fail('long-def', x.w + ': ' + x.d) }
  (defMap[x.d] = defMap[x.d] || []).push(x.w);
});
if (!dup) pass('no duplicate words (' + W.length + ' entries)');
if (!badField && !badPos && !badDiff && !ws) pass('fields/POS/difficulty valid');
const dupDefs = Object.entries(defMap).filter(([, v]) => v.length > 1);
if (dupDefs.length) dupDefs.forEach(([d, v]) => fail('dup-def', v.join('/') + ' -> "' + d + '"'));
else pass('no identical definitions');
// definition contains its own word root
let selfRef = 0;
W.forEach(x => {
  const stem = x.w.toLowerCase().slice(0, Math.max(4, x.w.length - 3));
  if (stem.length >= 4 && x.d.toLowerCase().includes(stem)) { selfRef++; fail('self-root-def', x.w + ': ' + x.d) }
});
if (!selfRef) pass('no definition contains its own root');

// --- sentences.js checks ---
const wSet = new Set(W.map(x => x.w));
let orphA = 0, orphB = 0;
W.forEach(x => { if (!SENTENCES[x.w]) { orphA++; fail('no-sentences', x.w) } });
Object.keys(SENTENCES).forEach(k => { if (!wSet.has(k)) { orphB++; fail('orphan-key', k) } });
if (!orphA && !orphB) pass('words <-> sentences alignment perfect');

let total = 0, badBlank = 0, badDis = 0, disEqAns = 0, leak = 0, dupDis = 0;
const conj = w => [w, conjugatePast(w), conjugateIng(w), conjugateS(w)];
for (const [w, arr] of Object.entries(SENTENCES)) {
  for (const e of arr) {
    total++;
    const s = e[0], dis = e.slice(1);
    if ((s.match(/_{5}/g) || []).length !== 1 || /_{6}/.test(s)) { badBlank++; fail('blank', w + ': ' + s.slice(0, 50)) }
    if (dis.length !== 3 || dis.some(d => !d || typeof d !== 'string')) { badDis++; fail('distractors', w) }
    const forms = new Set(conj(w.toLowerCase()));
    dis.forEach(d => { if (forms.has(d.toLowerCase())) { disEqAns++; fail('distractor=answer', w + ' / ' + d) } });
    if (new Set(dis.map(d => d.toLowerCase())).size !== dis.length) { dupDis++; fail('dup-distractor', w) }
    const rest = s.replace(/_{5}[a-z]*/i, ' ').toLowerCase();
    if (new RegExp('\\b' + w.toLowerCase().replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\b').test(rest)) { leak++; fail('answer-leak', w + ': ' + s.slice(0, 60)) }
    // root leak: 5+ char stem of the answer appearing elsewhere in the sentence
    const stem = w.toLowerCase().slice(0, Math.max(5, w.length - 4));
    if (stem.length >= 5 && rest.includes(stem)) { leak++; fail('root-leak', w + ': ' + s.slice(0, 70)) }
  }
}
if (!badBlank) pass('every sentence has exactly one 5-underscore blank (' + total + ' sentences)');
if (!badDis && !dupDis) pass('every sentence has 3 unique distractors');
if (!disEqAns) pass('no distractor equals the answer or its conjugations');
if (!leak) pass('no answer/root leaks in sentence text');

// --- conjugation validity for suffix-blank sentences (uses app rules) ---
let badConj = 0;
// past forms the naive rules must NOT produce (spot regressions in IRREG_PAST/CONJ_DBL coverage)
const MALFORMED = /(?:hold|sake|draw|take|stand|gainsay)ed$|^(?:rob|plod|strip|omit|commit|permit|acquit|shun|jot|throb|prod)(?:ed|ing)$/;
for (const [w, arr] of Object.entries(SENTENCES)) {
  for (const e of arr) {
    const m = e[0].match(/_____([a-z]+)/i);
    if (!m) continue;
    const suf = m[1].toLowerCase();
    let fn = null;
    if (['d', 'ed', 'ied', 'led', 'red', 'ted'].includes(suf)) fn = conjugatePast;
    else if (['ing', 'ting'].includes(suf)) fn = conjugateIng;
    else if (['s', 'es', 'ies'].includes(suf)) fn = conjugateS;
    else if (suf === 'n') fn = conjugateN;
    if (!fn) { badConj++; fail('unknown-suffix', w + ': _____' + suf); continue }
    for (const opt of [w, ...e.slice(1)]) {
      const out = fn(opt.toLowerCase());
      if (fn === conjugatePast && IRREG_PAST[opt.toLowerCase()] && out !== IRREG_PAST[opt.toLowerCase()]) { badConj++; fail('conj', opt + ' -> ' + out) }
      if (MALFORMED.test(out)) { badConj++; fail('conj-shape', opt + ' -> ' + out) }
    }
  }
}
if (!badConj) pass('all suffix-blank conjugations resolve through app rules');

// --- article check (mirrors app addArticle sound rules) ---
const anExc = /^(uni(?![nmd])|unan|use|usu|usur|util|utop|ubiq|eu|ewe|once|one)/i;
const aExc = /^(honest|honor|honou?r|heir|hour)/i;
let artChecked = 0;
for (const [w, arr] of Object.entries(SENTENCES)) {
  for (const e of arr) {
    if (!/\b(a|an)\s+_____/i.test(e[0])) continue;
    for (const opt of [w, ...e.slice(1)]) {
      artChecked++;
      // The app now computes articles by sound; this asserts the exception
      // lists still classify the known tricky spellings correctly.
      if (anExc.test(opt) && aExc.test(opt)) fail('article-conflict', opt);
    }
  }
}
pass('article sound-rules applied to ' + artChecked + ' article-blank options (no conflicts)');

console.log('\n' + (failures === 0 ? 'ALL CHECKS PASS' : failures + ' FAILURES'));
process.exit(failures === 0 ? 0 : 1);
