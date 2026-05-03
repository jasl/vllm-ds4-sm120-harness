# Generation Transcript

- Case: `en_code_fe_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 101.826233
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 226, "total_tokens": 6639, "completion_tokens": 6413, "prompt_tokens_details": null}`
- Prompt tokens: 226
- Completion tokens: 6413
- Total tokens: 6639

## Prompt

```markdown
Create a single-file frontend app named `index.html`. Do not use external libraries, CDNs, images, or build tools. Keep the total code under 1,000 lines.

Task: build an accessible “meeting notes board” for a small team.

Functional requirements:
1. Users can add a note with title, owner, meeting date, tags, and body.
2. Notes appear as cards and can be filtered by owner, tag, and free-text search.
3. A note can be marked as “Action Required,” “Decision,” or “Reference.”
4. Users can edit and delete notes.
5. Persist all data in `localStorage`.
6. Provide a compact statistics strip: total notes, action-required count, unique owners, and most common tag.
7. Responsive layout: two-column card grid on wide screens, single column on narrow screens.
8. Basic accessibility: labels for inputs, keyboard-operable controls, visible focus states.

Output only the complete `index.html` content, including HTML, CSS, and JavaScript. Do not include explanatory text.
```

## Assistant

````markdown
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>meeting notes board</title>
  <style>
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      font-family: system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      background: #f4f5f7;
      color: #1a1d23;
      padding: 1.5rem;
      line-height: 1.4;
    }

    /* focus styles for keyboard */
    :focus-visible {
      outline: 3px solid #005fcc;
      outline-offset: 2px;
      border-radius: 4px;
    }

    h1 {
      font-size: 1.8rem;
      margin-bottom: 0.75rem;
      font-weight: 600;
      letter-spacing: -0.01em;
    }

    .app-container {
      max-width: 1280px;
      margin: 0 auto;
    }

    /* stats strip */
    .stats-strip {
      display: flex;
      flex-wrap: wrap;
      gap: 1.8rem;
      background: white;
      padding: 1rem 1.5rem;
      border-radius: 16px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
      margin-bottom: 1.8rem;
      font-size: 0.95rem;
      font-weight: 500;
    }

    .stat-item {
      display: flex;
      align-items: baseline;
      gap: 0.3rem;
    }

    .stat-number {
      font-weight: 700;
      font-size: 1.3rem;
      color: #0a2540;
      min-width: 1.8rem;
    }

    .stat-label {
      color: #4a5568;
    }

    /* filters section */
    .filter-bar {
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem 1rem;
      background: white;
      padding: 1rem 1.5rem;
      border-radius: 20px;
      box-shadow: 0 1px 6px rgba(0,0,0,0.02);
      margin-bottom: 2rem;
      align-items: flex-end;
    }

    .filter-group {
      display: flex;
      flex-direction: column;
      gap: 0.2rem;
      flex: 1 0 140px;
      min-width: 130px;
    }

    .filter-group label {
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.02em;
      color: #2d3748;
    }

    .filter-group input,
    .filter-group select {
      background: #f9fafc;
      border: 1px solid #d0d5dd;
      border-radius: 30px;
      padding: 0.5rem 0.9rem;
      font-size: 0.9rem;
      color: #1a1d23;
      transition: border 0.15s;
    }

    .filter-group input:focus,
    .filter-group select:focus {
      border-color: #005fcc;
      background: white;
    }

    .add-btn-container {
      display: flex;
      align-items: flex-end;
      margin-left: auto;
    }

    .btn-primary {
      background: #0a2540;
      color: white;
      border: none;
      border-radius: 40px;
      padding: 0.6rem 1.6rem;
      font-weight: 600;
      font-size: 0.9rem;
      cursor: pointer;
      transition: background 0.15s, transform 0.1s;
      white-space: nowrap;
    }

    .btn-primary:hover,
    .btn-primary:focus-visible {
      background: #1e3a5f;
    }

    .btn-secondary {
      background: transparent;
      border: 1px solid #b0b8c5;
      border-radius: 40px;
      padding: 0.4rem 1rem;
      font-weight: 500;
      font-size: 0.8rem;
      cursor: pointer;
      transition: 0.1s;
    }

    .btn-secondary:hover {
      background: #eef0f4;
    }

    .btn-icon {
      background: none;
      border: none;
      cursor: pointer;
      font-size: 1.1rem;
      padding: 0.2rem 0.4rem;
      border-radius: 40px;
      transition: background 0.1s;
      color: #3b4a5e;
    }
    .btn-icon:hover {
      background: #e6eaf0;
    }

    /* cards grid */
    .notes-grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 1.5rem;
    }

    @media (min-width: 640px) {
      .notes-grid {
        grid-template-columns: repeat(2, 1fr);
      }
    }

    .note-card {
      background: white;
      border-radius: 24px;
      padding: 1.3rem 1.3rem 1rem;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02), 0 2px 6px rgba(0,0,0,0.03);
      transition: 0.1s;
      border: 1px solid #ebedf0;
      display: flex;
      flex-direction: column;
    }

    .note-header {
      display: flex;
      justify-content: space-between;
      flex-wrap: wrap;
      align-items: baseline;
      margin-bottom: 0.3rem;
    }

    .note-title {
      font-weight: 700;
      font-size: 1.1rem;
      margin-right: 0.5rem;
    }

    .note-badge {
      font-size: 0.7rem;
      font-weight: 600;
      padding: 0.25rem 0.75rem;
      border-radius: 40px;
      background: #eaeef5;
      color: #1e2b3a;
      letter-spacing: 0.02em;
    }

    .badge-action { background: #fde6d2; color: #9b4b1c; }
    .badge-decision { background: #d3e3fd; color: #1a4c8c; }
    .badge-reference { background: #e1e7d6; color: #3f5a2b; }

    .note-meta {
      font-size: 0.8rem;
      color: #4a5a6e;
      margin: 0.3rem 0 0.5rem;
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem 1rem;
    }

    .note-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 0.4rem 0.5rem;
      margin: 0.5rem 0 0.7rem;
    }

    .tag {
      background: #edf2f7;
      padding: 0.2rem 0.7rem;
      border-radius: 40px;
      font-size: 0.7rem;
      font-weight: 500;
      color: #1f2a3b;
    }

    .note-body {
      font-size: 0.9rem;
      color: #1d2633;
      margin: 0.4rem 0 0.8rem;
      white-space: pre-wrap;
      word-break: break-word;
      flex: 1;
    }

    .note-actions {
      display: flex;
      gap: 0.6rem;
      justify-content: flex-end;
      border-top: 1px solid #eceff3;
      padding-top: 0.7rem;
      margin-top: 0.5rem;
    }

    /* modal overlay */
    .modal-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.3);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
    }

    .modal-card {
      background: white;
      border-radius: 28px;
      padding: 2rem 2rem 1.8rem;
      width: 90%;
      max-width: 580px;
      max-height: 90vh;
      overflow-y: auto;
      box-shadow: 0 20px 40px rgba(0,0,0,0.2);
    }

    .modal-card h2 {
      font-size: 1.5rem;
      margin-bottom: 1rem;
      font-weight: 600;
    }

    .form-group {
      margin-bottom: 0.9rem;
    }

    .form-group label {
      display: block;
      font-size: 0.8rem;
      font-weight: 600;
      margin-bottom: 0.2rem;
      color: #2d3748;
    }

    .form-group input,
    .form-group select,
    .form-group textarea {
      width: 100%;
      padding: 0.6rem 0.9rem;
      border: 1px solid #cdd3dc;
      border-radius: 30px;
      font-size: 0.9rem;
      background: #fafbfc;
    }

    .form-group textarea {
      min-height: 80px;
      resize: vertical;
      border-radius: 20px;
    }

    .form-group input:focus,
    .form-group select:focus,
    .form-group textarea:focus {
      border-color: #005fcc;
      background: white;
    }

    .modal-actions {
      display: flex;
      gap: 0.8rem;
      justify-content: flex-end;
      margin-top: 1.2rem;
    }

    .empty-message {
      grid-column: 1 / -1;
      text-align: center;
      padding: 3rem 0;
      color: #5b6b7e;
      background: #f0f2f5;
      border-radius: 40px;
    }

    .hidden {
      display: none !important;
    }
  </style>
</head>
<body>
<div class="app-container">
  <h1>📋 meeting notes board</h1>

  <!-- stats strip -->
  <div class="stats-strip" id="statsStrip" aria-label="Statistics">
    <div class="stat-item"><span class="stat-number" id="totalNotes">0</span><span class="stat-label">notes</span></div>
    <div class="stat-item"><span class="stat-number" id="actionCount">0</span><span class="stat-label">action required</span></div>
    <div class="stat-item"><span class="stat-number" id="uniqueOwners">0</span><span class="stat-label">unique owners</span></div>
    <div class="stat-item"><span class="stat-number" id="commonTag">—</span><span class="stat-label">most common tag</span></div>
  </div>

  <!-- filter bar -->
  <div class="filter-bar" role="search" aria-label="Filter notes">
    <div class="filter-group">
      <label for="filterOwner">Owner</label>
      <input type="text" id="filterOwner" placeholder="any owner" aria-describedby="ownerHelp">
    </div>
    <div class="filter-group">
      <label for="filterTag">Tag</label>
      <input type="text" id="filterTag" placeholder="any tag">
    </div>
    <div class="filter-group">
      <label for="filterSearch">Search (title / body)</label>
      <input type="text" id="filterSearch" placeholder="keyword">
    </div>
    <div class="add-btn-container">
      <button class="btn-primary" id="openAddModal" aria-label="Add new note">+ add note</button>
    </div>
  </div>

  <!-- notes grid -->
  <div class="notes-grid" id="notesGrid" role="region" aria-label="Notes list">
    <!-- cards inserted by JS -->
  </div>
</div>

<!-- modal (hidden by default) -->
<div id="noteModal" class="modal-overlay hidden" role="dialog" aria-modal="true" aria-labelledby="modalTitle">
  <div class="modal-card">
    <h2 id="modalTitle">New note</h2>
    <form id="noteForm" autocomplete="off">
      <div class="form-group">
        <label for="inputTitle">Title *</label>
        <input type="text" id="inputTitle" required minlength="1" placeholder="e.g. Sprint review">
      </div>
      <div class="form-group">
        <label for="inputOwner">Owner *</label>
        <input type="text" id="inputOwner" required minlength="1" placeholder="e.g. Alex">
      </div>
      <div class="form-group">
        <label for="inputDate">Meeting date *</label>
        <input type="date" id="inputDate" required>
      </div>
      <div class="form-group">
        <label for="inputTags">Tags (comma separated)</label>
        <input type="text" id="inputTags" placeholder="design, frontend">
      </div>
      <div class="form-group">
        <label for="inputStatus">Status</label>
        <select id="inputStatus">
          <option value="Reference">Reference</option>
          <option value="Action Required">Action Required</option>
          <option value="Decision">Decision</option>
        </select>
      </div>
      <div class="form-group">
        <label for="inputBody">Body</label>
        <textarea id="inputBody" placeholder="Meeting notes …"></textarea>
      </div>
      <div class="modal-actions">
        <button type="button" class="btn-secondary" id="cancelModalBtn">Cancel</button>
        <button type="submit" class="btn-primary" id="saveNoteBtn">Save note</button>
      </div>
    </form>
  </div>
</div>

<script>
  (function() {
    // ----- data layer -----
    let notes = [];
    let editingId = null; // null = new note

    const LS_KEY = 'meetingNotesBoard';

    function loadNotes() {
      try {
        const stored = localStorage.getItem(LS_KEY);
        if (stored) {
          notes = JSON.parse(stored);
        } else {
          // seed sample data
          notes = [
            { id: 'n1', title: 'Design sync', owner: 'Emma', date: '2025-03-10', tags: ['design', 'UX'], status: 'Decision', body: 'Approved new palette.' },
            { id: 'n2', title: 'Frontend planning', owner: 'Liam', date: '2025-03-12', tags: ['frontend', 'sprint'], status: 'Action Required', body: 'Update component library.' },
            { id: 'n3', title: 'Retro', owner: 'Emma', date: '2025-03-08', tags: ['retro', 'team'], status: 'Reference', body: 'Action items distributed.' },
            { id: 'n4', title: 'QA review', owner: 'Noa', date: '2025-03-11', tags: ['QA', 'testing'], status: 'Action Required', body: 'Check regression suite.' },
          ];
          notes.forEach(n => { if (!n.tags) n.tags = []; if (!n.body) n.body = ''; });
        }
      } catch(e) { notes = []; }
    }

    function saveNotes() {
      localStorage.setItem(LS_KEY, JSON.stringify(notes));
    }

    // ----- stats update -----
    function updateStats() {
      const total = notes.length;
      const actionCount = notes.filter(n => n.status === 'Action Required').length;
      const owners = new Set(notes.map(n => n.owner.trim().toLowerCase()));
      const uniqueOwners = owners.size;

      // most common tag (excluding empty)
      const tagCount = {};
      notes.forEach(n => {
        (n.tags || []).forEach(t => {
          const key = t.trim().toLowerCase();
          if (key) tagCount[key] = (tagCount[key] || 0) + 1;
        });
      });
      let commonTag = '—';
      let maxCount = 0;
      for (const [tag, cnt] of Object.entries(tagCount)) {
        if (cnt > maxCount) { maxCount = cnt; commonTag = tag; }
      }
      if (commonTag !== '—') {
        // restore original casing from first occurrence
        for (const n of notes) {
          const found = (n.tags || []).find(t => t.trim().toLowerCase() === commonTag);
          if (found) { commonTag = found.trim(); break; }
        }
      }

      document.getElementById('totalNotes').textContent = total;
      document.getElementById('actionCount').textContent = actionCount;
      document.getElementById('uniqueOwners').textContent = uniqueOwners;
      document.getElementById('commonTag').textContent = commonTag;
    }

    // ----- render cards (with filters) -----
    function renderNotes() {
      const ownerFilter = document.getElementById('filterOwner').value.trim().toLowerCase();
      const tagFilter = document.getElementById('filterTag').value.trim().toLowerCase();
      const searchFilter = document.getElementById('filterSearch').value.trim().toLowerCase();

      const filtered = notes.filter(n => {
        if (ownerFilter && !n.owner.toLowerCase().includes(ownerFilter)) return false;
        if (tagFilter) {
          const noteTags = (n.tags || []).map(t => t.toLowerCase());
          if (!noteTags.some(t => t.includes(tagFilter))) return false;
        }
        if (searchFilter) {
          const haystack = (n.title + ' ' + (n.body || '')).toLowerCase();
          if (!haystack.includes(searchFilter)) return false;
        }
        return true;
      });

      const grid = document.getElementById('notesGrid');
      if (filtered.length === 0) {
        grid.innerHTML = `<div class="empty-message">✨ no notes match your filters</div>`;
        updateStats();
        return;
      }

      let html = '';
      filtered.forEach(n => {
        const statusClass = n.status === 'Action Required' ? 'badge-action' : (n.status === 'Decision' ? 'badge-decision' : 'badge-reference');
        const tagsHtml = (n.tags || []).filter(t => t.trim()).map(t => `<span class="tag">${escapeHtml(t.trim())}</span>`).join('');
        const bodyPreview = n.body ? escapeHtml(n.body.substring(0, 120)) : '';
        html += `
          <div class="note-card" data-id="${n.id}">
            <div class="note-header">
              <span class="note-title">${escapeHtml(n.title)}</span>
              <span class="note-badge ${statusClass}">${escapeHtml(n.status)}</span>
            </div>
            <div class="note-meta">
              <span>👤 ${escapeHtml(n.owner)}</span>
              <span>📅 ${escapeHtml(n.date)}</span>
            </div>
            <div class="note-tags">${tagsHtml}</div>
            <div class="note-body">${bodyPreview}</div>
            <div class="note-actions">
              <button class="btn-icon edit-btn" data-id="${n.id}" aria-label="Edit note">✎</button>
              <button class="btn-icon delete-btn" data-id="${n.id}" aria-label="Delete note">🗑</button>
            </div>
          </div>
        `;
      });
      grid.innerHTML = html;

      // attach event listeners to edit/delete
      grid.querySelectorAll('.edit-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
          const id = btn.dataset.id;
          openEditModal(id);
        });
      });
      grid.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
          const id = btn.dataset.id;
          deleteNoteById(id);
        });
      });

      updateStats();
    }

    // helper
    function escapeHtml(str) {
      const div = document.createElement('div');
      div.textContent = str;
      return div.innerHTML;
    }

    // ----- CRUD operations -----
    function deleteNoteById(id) {
      if (!confirm('Delete this note?')) return;
      notes = notes.filter(n => n.id !== id);
      saveNotes();
      renderNotes();
    }

    function openAddModal() {
      editingId = null;
      document.getElementById('modalTitle').textContent = 'New note';
      document.getElementById('noteForm').reset();
      document.getElementById('inputDate').value = new Date().toISOString().slice(0,10);
      document.getElementById('inputStatus').value = 'Reference';
      document.getElementById('noteModal').classList.remove('hidden');
      document.getElementById('inputTitle').focus();
    }

    function openEditModal(id) {
      const note = notes.find(n => n.id === id);
      if (!note) return;
      editingId = id;
      document.getElementById('modalTitle').textContent = 'Edit note';
      document.getElementById('inputTitle').value = note.title || '';
      document.getElementById('inputOwner').value = note.owner || '';
      document.getElementById('inputDate').value = note.date || '';
      document.getElementById('inputTags').value = (note.tags || []).join(', ');
      document.getElementById('inputStatus').value = note.status || 'Reference';
      document.getElementById('inputBody').value = note.body || '';
      document.getElementById('noteModal').classList.remove('hidden');
      document.getElementById('inputTitle').focus();
    }

    function closeModal() {
      document.getElementById('noteModal').classList.add('hidden');
      editingId = null;
    }

    function handleFormSubmit(e) {
      e.preventDefault();
      const title = document.getElementById('inputTitle').value.trim();
      const owner = document.getElementById('inputOwner').value.trim();
      const date = document.getElementById('inputDate').value;
      const tagsRaw = document.getElementById('inputTags').value;
      const status = document.getElementById('inputStatus').value;
      const body = document.getElementById('inputBody').value.trim();

      if (!title || !owner || !date) {
        alert('Title, owner and date are required.');
        return;
      }

      const tags = tagsRaw.split(',').map(t => t.trim()).filter(t => t.length > 0);

      if (editingId) {
        // edit existing
        const idx = notes.findIndex(n => n.id === editingId);
        if (idx !== -1) {
          notes[idx] = { ...notes[idx], title, owner, date, tags, status, body };
        }
      } else {
        // new note
        const newId = 'note_' + Date.now() + '_' + Math.random().toString(36).slice(2,6);
        notes.push({ id: newId, title, owner, date, tags, status, body });
      }

      saveNotes();
      closeModal();
      renderNotes();
    }

    // ----- filter listeners -----
    function setupFilterListeners() {
      const ids = ['filterOwner', 'filterTag', 'filterSearch'];
      ids.forEach(id => {
        document.getElementById(id).addEventListener('input', renderNotes);
      });
    }

    // ----- modal listeners -----
    function setupModalListeners() {
      document.getElementById('openAddModal').addEventListener('click', openAddModal);
      document.getElementById('cancelModalBtn').addEventListener('click', closeModal);
      document.getElementById('noteModal').addEventListener('click', (e) => {
        if (e.target === document.getElementById('noteModal')) closeModal();
      });
      document.getElementById('noteForm').addEventListener('submit', handleFormSubmit);

      // close on escape
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !document.getElementById('noteModal').classList.contains('hidden')) {
          closeModal();
        }
      });
    }

    // ----- bootstrap -----
    loadNotes();
    renderNotes();
    setupFilterListeners();
    setupModalListeners();

    // ensure stats on load
    updateStats();

    // keyboard activation for delete/edit already via click; also keep accessibility
    // global listeners for dynamically created buttons? use event delegation
    document.getElementById('notesGrid').addEventListener('click', (e) => {
      const target = e.target.closest('.delete-btn');
      if (target) {
        const id = target.dataset.id;
        deleteNoteById(id);
      }
    });
    // edit handled by direct listener, but delegating also works. avoid double: but we already set per-btn, plus delegation is fine
    // to avoid double fire, we remove inline listeners and use delegation. But we already set per-btn, let's keep only delegation.
    // rewire: we will rewrite render to NOT attach per-btn, rely on delegation.
    // quick fix: remove inline edit listener and use delegation.
    // override render function? simpler: replace set.
    // we override renderNotes function to use delegation only.
    const originalRender = renderNotes;
    renderNotes = function() {
      const ownerFilter = document.getElementById('filterOwner').value.trim().toLowerCase();
      const tagFilter = document.getElementById('filterTag').value.trim().toLowerCase();
      const searchFilter = document.getElementById('filterSearch').value.trim().toLowerCase();

      const filtered = notes.filter(n => {
        if (ownerFilter && !n.owner.toLowerCase().includes(ownerFilter)) return false;
        if (tagFilter) {
          const noteTags = (n.tags || []).map(t => t.toLowerCase());
          if (!noteTags.some(t => t.includes(tagFilter))) return false;
        }
        if (searchFilter) {
          const haystack = (n.title + ' ' + (n.body || '')).toLowerCase();
          if (!haystack.includes(searchFilter)) return false;
        }
        return true;
      });

      const grid = document.getElementById('notesGrid');
      if (filtered.length === 0) {
        grid.innerHTML = `<div class="empty-message">✨ no notes match your filters</div>`;
        updateStats();
        return;
      }

      let html = '';
      filtered.forEach(n => {
        const statusClass = n.status === 'Action Required' ? 'badge-action' : (n.status === 'Decision' ? 'badge-decision' : 'badge-reference');
        const tagsHtml = (n.tags || []).filter(t => t.trim()).map(t => `<span class="tag">${escapeHtml(t.trim())}</span>`).join('');
        const bodyPreview = n.body ? escapeHtml(n.body.substring(0, 120)) : '';
        html += `
          <div class="note-card" data-id="${n.id}">
            <div class="note-header">
              <span class="note-title">${escapeHtml(n.title)}</span>
              <span class="note-badge ${statusClass}">${escapeHtml(n.status)}</span>
            </div>
            <div class="note-meta">
              <span>👤 ${escapeHtml(n.owner)}</span>
              <span>📅 ${escapeHtml(n.date)}</span>
            </div>
            <div class="note-tags">${tagsHtml}</div>
            <div class="note-body">${bodyPreview}</div>
            <div class="note-actions">
              <button class="btn-icon edit-btn" data-id="${n.id}" aria-label="Edit note" type="button">✎</button>
              <button class="btn-icon delete-btn" data-id="${n.id}" aria-label="Delete note" type="button">🗑</button>
            </div>
          </div>
        `;
      });
      grid.innerHTML = html;
      updateStats();
    };

    // attach delegation for edit & delete
    document.getElementById('notesGrid').addEventListener('click', function(e) {
      const editBtn = e.target.closest('.edit-btn');
      if (editBtn) {
        const id = editBtn.dataset.id;
        openEditModal(id);
        return;
      }
      const delBtn = e.target.closest('.delete-btn');
      if (delBtn) {
        const id = delBtn.dataset.id;
        deleteNoteById(id);
      }
    });

    // re-render after override
    renderNotes();
  })();
</script>
</body>
</html>
```
````
