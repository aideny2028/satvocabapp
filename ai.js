// AI tutor integration (BYOK — bring your own key).
// Providers: Google Gemini (free tier) or Anthropic Claude (direct browser access).
// The API key lives in its own localStorage keys and is deliberately NOT part of
// the exported/imported progress state.

const AI_PROVIDER_KEY = 'sat_ai_provider';
const AI_KEY_KEY = 'sat_ai_key';

function getAiConfig() {
    return {
        provider: localStorage.getItem(AI_PROVIDER_KEY) || 'gemini',
        key: localStorage.getItem(AI_KEY_KEY) || ''
    };
}

function setAiConfig(provider, key) {
    localStorage.setItem(AI_PROVIDER_KEY, provider);
    localStorage.setItem(AI_KEY_KEY, key);
}

const AI_SYSTEM_PROMPT = 'You are a friendly SAT vocabulary tutor inside a vocabulary practice app. ' +
    'Be concise (under 150 words unless asked for more). When explaining a word, cover: what it means in plain ' +
    'language, a memorable mnemonic or etymology hook, and one vivid example sentence. When explaining a wrong ' +
    'answer, contrast the two words precisely. Plain text only - no markdown headers or bullets.';

// Rolling chat history for the panel (user/assistant turns, capped)
let aiHistory = [];

async function callGemini(key, history) {
    const url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=' + encodeURIComponent(key);
    const contents = history.map(m => ({
        role: m.role === 'assistant' ? 'model' : 'user',
        parts: [{ text: m.content }]
    }));
    const res = await fetch(url, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
            system_instruction: { parts: [{ text: AI_SYSTEM_PROMPT }] },
            contents: contents,
            generationConfig: { maxOutputTokens: 1024 }
        })
    });
    if (!res.ok) {
        const body = await res.text().catch(() => '');
        throw new Error('Gemini error ' + res.status + (res.status === 400 || res.status === 403 ? ' - check your API key in Settings' : '') + (body ? ': ' + body.slice(0, 200) : ''));
    }
    const data = await res.json();
    const text = data.candidates && data.candidates[0] && data.candidates[0].content &&
        data.candidates[0].content.parts && data.candidates[0].content.parts.map(p => p.text || '').join('');
    if (!text) throw new Error('Gemini returned an empty response.');
    return text;
}

async function callClaude(key, history) {
    const res = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
            'content-type': 'application/json',
            'x-api-key': key,
            'anthropic-version': '2023-06-01',
            'anthropic-dangerous-direct-browser-access': 'true'
        },
        body: JSON.stringify({
            model: 'claude-haiku-4-5',
            max_tokens: 1024,
            system: AI_SYSTEM_PROMPT,
            messages: history.map(m => ({ role: m.role, content: m.content }))
        })
    });
    if (!res.ok) {
        const status = res.status;
        throw new Error('Claude error ' + status + (status === 401 ? ' - check your API key in Settings' : status === 429 ? ' - rate limited, try again shortly' : ''));
    }
    const data = await res.json();
    if (data.stop_reason === 'refusal') throw new Error('The model declined to answer that.');
    const text = (data.content || []).filter(b => b.type === 'text').map(b => b.text).join('');
    if (!text) throw new Error('Claude returned an empty response.');
    return text;
}

async function askAi(history) {
    const cfg = getAiConfig();
    if (!cfg.key) throw new Error('NO_KEY');
    return cfg.provider === 'claude' ? callClaude(cfg.key, history) : callGemini(cfg.key, history);
}

// ---------- Chat panel UI ----------

function aiPanelOpen() {
    return !document.getElementById('aiPanel').classList.contains('hidden');
}

function toggleAiChat(forceOpen) {
    const panel = document.getElementById('aiPanel');
    if (forceOpen === true) panel.classList.remove('hidden');
    else panel.classList.toggle('hidden');
    if (aiPanelOpen()) {
        if (!getAiConfig().key && aiHistory.length === 0) {
            appendAiMsg('assistant', 'To use the AI tutor, add a free Google Gemini API key (or an Anthropic key) in Settings → AI Tutor.', true);
        }
        const inp = document.getElementById('aiInput');
        if (inp && window.matchMedia && window.matchMedia('(hover: hover)').matches) inp.focus();
    }
}

function appendAiMsg(role, text, ephemeral) {
    const log = document.getElementById('aiLog');
    const div = document.createElement('div');
    div.className = 'ai-msg ' + (role === 'user' ? 'ai-user' : 'ai-bot');
    div.textContent = text; // textContent - model output is never injected as HTML
    log.appendChild(div);
    log.scrollTop = log.scrollHeight;
    if (!ephemeral) {
        aiHistory.push({ role: role, content: text });
        if (aiHistory.length > 12) aiHistory = aiHistory.slice(-12);
    }
    return div;
}

async function sendAiMessage(prefill) {
    const inp = document.getElementById('aiInput');
    const text = (prefill != null ? prefill : inp.value).trim();
    if (!text) return;
    if (prefill == null) inp.value = '';
    toggleAiChat(true);
    appendAiMsg('user', text);
    const pending = appendAiMsg('assistant', '…', true);
    try {
        const reply = await askAi(aiHistory);
        pending.remove();
        appendAiMsg('assistant', reply);
    } catch (err) {
        pending.remove();
        if (err.message === 'NO_KEY') {
            appendAiMsg('assistant', 'No API key set. Add a free Gemini key (aistudio.google.com) or an Anthropic key in Settings → AI Tutor.', true);
        } else {
            appendAiMsg('assistant', 'Something went wrong: ' + err.message, true);
        }
    }
}

// ---------- Hook points used by app.js ----------

function aiExplainWord(word, def) {
    sendAiMessage('Explain the SAT word "' + word + '" (meaning: ' + def + '). Give me a plain-language explanation, a mnemonic or etymology hook, and one vivid example sentence.');
}

function aiExplainWrong(word, def, chosenText) {
    sendAiMessage('In a vocab quiz I confused "' + word + '" (' + def + ') with this answer: "' + chosenText + '". Explain the difference precisely and give me a trick to keep them apart.');
}

// Settings section HTML (rendered inside renderSettings)
function aiSettingsHtml() {
    const cfg = getAiConfig();
    return '<div class="setting-group"><h3>AI Tutor</h3>' +
        '<p>Optional: add your own API key to enable the AI tutor (explanations, mnemonics, "why was I wrong?"). ' +
        'Gemini has a free tier at aistudio.google.com. The key is stored only in this browser and is never included in progress exports.</p>' +
        '<div class="ai-settings-row"><label for="aiProviderSel">Provider</label>' +
        '<select id="aiProviderSel"><option value="gemini"' + (cfg.provider === 'gemini' ? ' selected' : '') + '>Google Gemini (free tier)</option>' +
        '<option value="claude"' + (cfg.provider === 'claude' ? ' selected' : '') + '>Anthropic Claude</option></select></div>' +
        '<div class="ai-settings-row"><label for="aiKeyInput">API key</label>' +
        '<input type="password" id="aiKeyInput" placeholder="Paste your API key" value="' + esc(cfg.key) + '" autocomplete="off"></div>' +
        '<div class="review-actions" style="justify-content:flex-start;margin-top:12px"><button onclick="saveAiSettings()">Save AI settings</button></div></div>';
}

function saveAiSettings() {
    setAiConfig(document.getElementById('aiProviderSel').value, document.getElementById('aiKeyInput').value.trim());
    alert('AI settings saved.');
}

// ---------- Bootstrap the widget ----------

(function initAiWidget() {
    const wrap = document.createElement('div');
    wrap.innerHTML =
        '<button class="ai-fab" id="aiFab" onclick="toggleAiChat()" aria-label="AI tutor" title="AI tutor">Ai</button>' +
        '<div class="ai-panel hidden" id="aiPanel" role="dialog" aria-label="AI tutor chat">' +
        '<div class="ai-panel-head"><span>AI Tutor</span><button class="ai-close" onclick="toggleAiChat()" aria-label="Close chat">&times;</button></div>' +
        '<div class="ai-log" id="aiLog"></div>' +
        '<div class="ai-input-row"><input type="text" id="aiInput" placeholder="Ask about any word…" aria-label="Message the AI tutor">' +
        '<button onclick="sendAiMessage()" aria-label="Send">&#10148;</button></div>' +
        '</div>';
    while (wrap.firstChild) document.body.appendChild(wrap.firstChild);
    document.getElementById('aiInput').addEventListener('keydown', e => {
        if (e.key === 'Enter') sendAiMessage();
        e.stopPropagation(); // typing must not trigger quiz keyboard shortcuts
    });
})();
