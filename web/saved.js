const API_BASE = 'http://localhost:8000';

function formatDate(dateStr) {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function renderSkeletons() {
  return `
    <div class="loading-grid">
      ${[1,2,3].map(() => `
      <div class="skeleton-card">
        <div class="skeleton skeleton-line short"></div>
        <div class="skeleton skeleton-block"></div>
        <div class="skeleton skeleton-tags"></div>
        <div class="skeleton skeleton-btn"></div>
      </div>`).join('')}
    </div>`;
}

function renderEmpty() {
  return `
    <div class="reels-grid">
      <div class="empty-state">
        <div class="empty-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="2" y="3" width="20" height="14" rx="2"/>
            <path d="M8 21h8M12 17v4"/>
          </svg>
        </div>
        <h2>No reels saved yet</h2>
        <p>Head back to ReelMind and categorize your first reel.</p>
        <a href="index.html" class="empty-cta">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="width:14px;height:14px">
            <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          Categorize a Reel
        </a>
      </div>
    </div>`;
}

function renderError(msg) {
  return `
    <div class="reels-grid">
      <div class="error-state">
        <p>⚠️ ${msg}</p>
        <button class="retry-btn" onclick="loadReels()">Try again</button>
      </div>
    </div>`;
}

function renderCard(reel, index) {
  const categories = Array.isArray(reel.categories) ? reel.categories : [];
  const tags = Array.isArray(reel.tags) ? reel.tags : [];

  return `
    <div class="reel-card" style="animation-delay: ${index * 0.07}s">
      <div class="card-header">
        <div class="platform-badge">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="2" y="2" width="20" height="20" rx="5"/>
            <circle cx="12" cy="12" r="4"/>
            <circle cx="17.5" cy="6.5" r="1" fill="currentColor"/>
          </svg>
          Instagram
        </div>
        <span class="card-date">${formatDate(reel.created_at)}</span>
      </div>

      ${reel.summary ? `<p class="card-summary">${reel.summary}</p>` : ''}

      ${categories.length ? `
      <div class="card-tags-section">
        <span class="section-label">Categories</span>
        <div class="tags-row">
          ${categories.map(c => `<span class="tag tag-category">${c}</span>`).join('')}
        </div>
      </div>` : ''}

      ${tags.length ? `
      <div class="card-tags-section">
        <span class="section-label">Tags</span>
        <div class="tags-row">
          ${tags.map(t => `<span class="tag tag-keyword">#${t}</span>`).join('')}
        </div>
      </div>` : ''}

      <div class="card-footer">
        <a href="${reel.url}" target="_blank" rel="noopener noreferrer" class="view-btn">
          VIEW ON INSTAGRAM
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
            <polyline points="15 3 21 3 21 9"/>
            <line x1="10" y1="14" x2="21" y2="3"/>
          </svg>
        </a>
      </div>
    </div>`;
}

async function loadReels() {
  const container = document.getElementById('gridContainer');
  const countEl = document.getElementById('reelCount');

  container.innerHTML = renderSkeletons();
  countEl.textContent = 'Loading...';

  try {
    const res = await fetch(`${API_BASE}/reels`);
    if (!res.ok) throw new Error(`Server returned ${res.status}`);

    const reels = await res.json();

    if (!reels || reels.length === 0) {
      container.innerHTML = renderEmpty();
      countEl.textContent = '0 reels saved';
      return;
    }

    countEl.textContent = `${reels.length} reel${reels.length !== 1 ? 's' : ''} saved`;
    container.innerHTML = `<div class="reels-grid">${reels.map((r, i) => renderCard(r, i)).join('')}</div>`;

  } catch (err) {
    container.innerHTML = renderError('Could not load your reels. Is the server running?');
    countEl.textContent = '';
    console.error(err);
  }
}

loadReels();