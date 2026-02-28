// ─── CONFIG ──────────────────────────────────────────────────────────────────
const API_BASE     = 'http://localhost:8000';
const API_ENDPOINT = `${API_BASE}/categorize`;
// POST /categorize  →  { "url": "<reel_url>" }
// Expected response: { summary, categories: [], tags: [] }
// ─────────────────────────────────────────────────────────────────────────────

const input         = document.getElementById('reelUrl');
const submitBtn     = document.getElementById('submitBtn');
const pasteBtn      = document.getElementById('pasteBtn');
const statusEl      = document.getElementById('status');
const resultBox     = document.getElementById('resultBox');
const resultContent = document.getElementById('resultContent');

const REEL_PATTERN = /instagram\.com\/(reel|reels|p)\/[A-Za-z0-9_-]+/;

// ─── Helpers ─────────────────────────────────────────────────────────────────

function validate(url) {
  if (!url) return null;
  try { new URL(url); } catch { return false; }
  return REEL_PATTERN.test(url);
}

function setStatus(msg, type = '') {
  statusEl.textContent = msg;
  statusEl.className   = `status ${type}`;
}

function setLoading(isLoading) {
  submitBtn.disabled = isLoading;
  submitBtn.classList.toggle('loading', isLoading);
  submitBtn.querySelector('.btn-text').textContent = isLoading ? 'ANALYZING…' : 'CATEGORIZE REEL';
}

// ─── API ─────────────────────────────────────────────────────────────────────

async function categorizeReel(url) {
  const res = await fetch(API_ENDPOINT, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify({ url }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }

  return res.json();
}

// ─── Render ──────────────────────────────────────────────────────────────────

function renderResult(data) {
  if (!data.summary && !data.categories && !data.tags) {
    resultContent.innerHTML = `<pre style="font-size:0.8rem;opacity:0.7;white-space:pre-wrap">${JSON.stringify(data, null, 2)}</pre>`;
    return;
  }

  let html = '';

  if (data.summary) {
    html += `<p class="result-summary">${data.summary}</p>`;
  }

  if (data.categories?.length) {
    html += `<div class="result-section-label">Categories</div>`;
    html += data.categories.map(c => `<span class="tag tag-category">${c}</span>`).join('');
  }

  if (data.tags?.length) {
    html += `<div class="result-section-label">Tags</div>`;
    html += data.tags.map(t => `<span class="tag tag-keyword">#${t}</span>`).join('');
  }

  resultContent.innerHTML = html;
}

// ─── Event Listeners ─────────────────────────────────────────────────────────

input.addEventListener('input', () => {
  const val = input.value.trim();
  const v   = validate(val);

  if (!val) {
    input.className    = 'url-input';
    submitBtn.disabled = true;
    setStatus('');
  } else if (v === false) {
    input.className    = 'url-input invalid';
    submitBtn.disabled = true;
    setStatus('Not a valid URL', 'error');
  } else {
    input.className    = 'url-input valid';
    submitBtn.disabled = false;
    setStatus('Looks good!', 'success');
  }
});

input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !submitBtn.disabled) submitBtn.click();
});

pasteBtn.addEventListener('click', async () => {
  try {
    input.value = await navigator.clipboard.readText();
    input.dispatchEvent(new Event('input'));
  } catch {
    setStatus('Clipboard access denied', 'error');
  }
});

submitBtn.addEventListener('click', async () => {
  const url = input.value.trim();
  if (!url) return;

  setLoading(true);
  setStatus('Analyzing with AI…', 'loading');
  resultBox.classList.remove('visible');

  try {
    const data = await categorizeReel(url);
    setStatus('Categorized!', 'success');
    renderResult(data);
    resultBox.classList.add('visible');
  } catch (err) {
    setStatus(`Error: ${err.message}`, 'error');
  } finally {
    setLoading(false);
  }
});