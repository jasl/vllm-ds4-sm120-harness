# Generation Transcript

- Case: `en_code_fe_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 53.076393
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 226, "total_tokens": 6705, "completion_tokens": 6479, "prompt_tokens_details": null}`
- Prompt tokens: 226
- Completion tokens: 6479
- Total tokens: 6705

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
  <title>Meeting Notes Board</title>
  <style>
    /* reset & base */
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    body {
      font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
      background: #f4f6f9;
      min-height: 100vh;
      padding: 1.5rem;
      color: #1e293b;
    }
    :focus-visible {
      outline: 2px solid #2563eb;
      outline-offset: 2px;
      border-radius: 4px;
    }
    button, input, select, textarea {
      font: inherit;
      color: inherit;
    }
    h1, h2, h3 {
      font-weight: 600;
      letter-spacing: -0.01em;
    }
    .app {
      max-width: 1280px;
      margin: 0 auto;
    }

    /* header */
    .app-header {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 1.75rem;
    }
    .app-header h1 {
      font-size: 1.9rem;
      background: linear-gradient(145deg, #1e3a5f, #2d5a8e);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
    .add-btn {
      background: #1e3a5f;
      color: white;
      border: none;
      padding: 0.6rem 1.4rem;
      border-radius: 40px;
      font-weight: 500;
      font-size: 1rem;
      cursor: pointer;
      transition: background 0.15s;
      box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }
    .add-btn:hover { background: #2a4b77; }
    .add-btn:active { background: #16324d; }

    /* stats strip */
    .stats-strip {
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem 2rem;
      background: white;
      padding: 1rem 1.4rem;
      border-radius: 20px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.03);
      margin-bottom: 2rem;
      font-size: 0.95rem;
      border: 1px solid #e9edf2;
    }
    .stat-item {
      display: flex;
      gap: 0.3rem 0.6rem;
      align-items: baseline;
      flex-wrap: wrap;
    }
    .stat-label {
      color: #64748b;
      font-weight: 450;
    }
    .stat-value {
      font-weight: 650;
      background: #f1f5f9;
      padding: 0.1rem 0.7rem;
      border-radius: 30px;
      color: #0b1e33;
    }

    /* filters */
    .filter-area {
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem 1rem;
      margin-bottom: 1.8rem;
      align-items: center;
      background: white;
      padding: 0.9rem 1.2rem;
      border-radius: 20px;
      border: 1px solid #e9edf2;
    }
    .filter-group {
      display: flex;
      align-items: center;
      gap: 0.3rem 0.6rem;
      flex-wrap: wrap;
    }
    .filter-group label {
      font-size: 0.85rem;
      font-weight: 500;
      color: #334155;
    }
    .filter-group input, .filter-group select {
      background: #f8fafc;
      border: 1px solid #d1d9e6;
      border-radius: 30px;
      padding: 0.3rem 1rem;
      font-size: 0.9rem;
      min-width: 110px;
    }
    .filter-group input:focus, .filter-group select:focus {
      border-color: #2563eb;
      background: white;
    }
    .clear-filters {
      background: transparent;
      border: 1px solid #d1d9e6;
      border-radius: 30px;
      padding: 0.3rem 1.2rem;
      font-size: 0.85rem;
      cursor: pointer;
      margin-left: auto;
      transition: 0.1s;
    }
    .clear-filters:hover {
      background: #eef2f7;
    }

    /* card grid */
    .note-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 1.5rem;
      margin-bottom: 2rem;
    }
    @media (max-width: 700px) {
      .note-grid {
        grid-template-columns: 1fr;
      }
    }

    /* card */
    .note-card {
      background: white;
      border-radius: 24px;
      padding: 1.3rem 1.4rem;
      box-shadow: 0 4px 12px rgba(0,0,0,0.02);
      border: 1px solid #e9edf2;
      transition: 0.1s ease;
      display: flex;
      flex-direction: column;
    }
    .note-card:hover {
      border-color: #cbd5e1;
    }
    .card-header {
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: baseline;
      margin-bottom: 0.25rem;
    }
    .card-title {
      font-weight: 650;
      font-size: 1.2rem;
      word-break: break-word;
      margin-right: 0.5rem;
    }
    .card-badge {
      font-size: 0.7rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.03em;
      padding: 0.2rem 0.8rem;
      border-radius: 30px;
      background: #eef2f6;
      color: #1e293b;
      white-space: nowrap;
      border: 1px solid #dce2ea;
    }
    .badge-action { background: #fee2e2; border-color: #fecaca; color: #991b1b; }
    .badge-decision { background: #dbeafe; border-color: #b9d6fd; color: #1e3a7a; }
    .badge-reference { background: #e8f0e7; border-color: #c7d9c5; color: #2b4f2b; }

    .card-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 0.3rem 1rem;
      font-size: 0.8rem;
      color: #475569;
      margin: 0.5rem 0 0.6rem;
    }
    .card-meta span {
      background: #f1f5f9;
      padding: 0.1rem 0.7rem;
      border-radius: 30px;
    }
    .card-body {
      margin: 0.5rem 0 0.8rem;
      line-height: 1.5;
      word-break: break-word;
      color: #1e293b;
      flex: 1;
    }
    .card-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 0.4rem 0.6rem;
      margin-bottom: 0.75rem;
    }
    .tag {
      background: #eef2f6;
      padding: 0.1rem 0.7rem;
      border-radius: 30px;
      font-size: 0.75rem;
      font-weight: 500;
      color: #1e293b;
    }
    .card-actions {
      display: flex;
      gap: 0.6rem;
      justify-content: flex-end;
      border-top: 1px solid #ecf1f5;
      padding-top: 0.75rem;
      margin-top: 0.2rem;
    }
    .card-actions button {
      background: transparent;
      border: 1px solid #dce2ea;
      padding: 0.2rem 1rem;
      border-radius: 30px;
      font-size: 0.8rem;
      cursor: pointer;
      transition: 0.1s;
    }
    .card-actions button:hover {
      background: #f1f5f9;
      border-color: #b9c3d1;
    }
    .card-actions .delete-btn {
      color: #b91c1c;
      border-color: #fecaca;
    }
    .card-actions .delete-btn:hover {
      background: #fee2e2;
    }

    /* modal overlay */
    .modal-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.35);
      backdrop-filter: blur(2px);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 200;
      padding: 1rem;
    }
    .modal-content {
      background: white;
      max-width: 580px;
      width: 100%;
      border-radius: 32px;
      padding: 1.8rem 1.8rem 2rem;
      box-shadow: 0 20px 40px rgba(0,0,0,0.2);
      max-height: 90vh;
      overflow-y: auto;
    }
    .modal-content h2 {
      font-size: 1.5rem;
      margin-bottom: 1.2rem;
    }
    .form-field {
      margin-bottom: 0.9rem;
    }
    .form-field label {
      display: block;
      font-size: 0.8rem;
      font-weight: 500;
      margin-bottom: 0.2rem;
      color: #334155;
    }
    .form-field input, .form-field select, .form-field textarea {
      width: 100%;
      padding: 0.5rem 0.9rem;
      border: 1px solid #d1d9e6;
      border-radius: 20px;
      background: #fafcff;
    }
    .form-field textarea {
      resize: vertical;
      min-height: 70px;
    }
    .form-field input:focus, .form-field select:focus, .form-field textarea:focus {
      border-color: #2563eb;
      background: white;
    }
    .modal-actions {
      display: flex;
      gap: 0.8rem;
      justify-content: flex-end;
      margin-top: 1.5rem;
    }
    .modal-actions button {
      padding: 0.4rem 1.4rem;
      border-radius: 40px;
      border: 1px solid #d1d9e6;
      background: white;
      cursor: pointer;
      font-weight: 500;
    }
    .modal-actions .primary-btn {
      background: #1e3a5f;
      color: white;
      border: none;
    }
    .modal-actions .primary-btn:hover { background: #2a4b77; }

    .hidden { display: none; }
    .no-notes {
      grid-column: 1 / -1;
      text-align: center;
      padding: 3rem 1rem;
      color: #64748b;
    }
  </style>
</head>
<body>
<div class="app">
  <!-- header -->
  <header class="app-header">
    <h1>📋 Meeting Notes Board</h1>
    <button class="add-btn" id="addNoteBtn" aria-label="Add new meeting note">+ New note</button>
  </header>

  <!-- stats strip -->
  <section class="stats-strip" aria-label="Statistics summary">
    <div class="stat-item"><span class="stat-label">Total notes</span><span class="stat-value" id="totalNotes">0</span></div>
    <div class="stat-item"><span class="stat-label">Action required</span><span class="stat-value" id="actionCount">0</span></div>
    <div class="stat-item"><span class="stat-label">Unique owners</span><span class="stat-value" id="uniqueOwners">0</span></div>
    <div class="stat-item"><span class="stat-label">Most common tag</span><span class="stat-value" id="mostCommonTag">—</span></div>
  </section>

  <!-- filters -->
  <section class="filter-area" aria-label="Filter notes">
    <div class="filter-group">
      <label for="filterOwner">Owner</label>
      <select id="filterOwner" aria-label="Filter by owner"><option value="">All</option></select>
    </div>
    <div class="filter-group">
      <label for="filterTag">Tag</label>
      <select id="filterTag" aria-label="Filter by tag"><option value="">All</option></select>
    </div>
    <div class="filter-group">
      <label for="filterSearch">Search</label>
      <input type="text" id="filterSearch" placeholder="free text..." aria-label="Free text search">
    </div>
    <button class="clear-filters" id="clearFiltersBtn" aria-label="Clear all filters">Clear</button>
  </section>

  <!-- note grid -->
  <div class="note-grid" id="noteGrid" role="list" aria-label="Notes list">
    <!-- cards rendered dynamically -->
  </div>
</div>

<!-- modal (hidden by default) -->
<div id="modalOverlay" class="modal-overlay hidden" role="dialog" aria-modal="true" aria-labelledby="modalTitle">
  <div class="modal-content">
    <h2 id="modalTitle">New note</h2>
    <form id="noteForm" novalidate>
      <div class="form-field">
        <label for="noteTitle">Title *</label>
        <input type="text" id="noteTitle" required>
      </div>
      <div class="form-field">
        <label for="noteOwner">Owner *</label>
        <input type="text" id="noteOwner" required>
      </div>
      <div class="form-field">
        <label for="noteDate">Meeting date *</label>
        <input type="date" id="noteDate" required>
      </div>
      <div class="form-field">
        <label for="noteTags">Tags (comma separated)</label>
        <input type="text" id="noteTags" placeholder="e.g. design, frontend">
      </div>
      <div class="form-field">
        <label for="noteCategory">Category</label>
        <select id="noteCategory">
          <option value="Reference">Reference</option>
          <option value="Decision">Decision</option>
          <option value="Action Required">Action Required</option>
        </select>
      </div>
      <div class="form-field">
        <label for="noteBody">Body</label>
        <textarea id="noteBody" rows="3"></textarea>
      </div>
      <input type="hidden" id="noteId" value="">
      <div class="modal-actions">
        <button type="button" id="cancelModalBtn">Cancel</button>
        <button type="submit" class="primary-btn" id="saveNoteBtn">Save</button>
      </div>
    </form>
  </div>
</div>

<script>
  (function() {
    // --- state ---
    let notes = [];
    let editingId = null; // null = new note
    let filters = { owner: '', tag: '', search: '' };

    // --- DOM references ---
    const grid = document.getElementById('noteGrid');
    const totalEl = document.getElementById('totalNotes');
    const actionEl = document.getElementById('actionCount');
    const uniqueOwnersEl = document.getElementById('uniqueOwners');
    const mostCommonTagEl = document.getElementById('mostCommonTag');

    const filterOwner = document.getElementById('filterOwner');
    const filterTag = document.getElementById('filterTag');
    const filterSearch = document.getElementById('filterSearch');
    const clearFiltersBtn = document.getElementById('clearFiltersBtn');
    const addNoteBtn = document.getElementById('addNoteBtn');

    const modalOverlay = document.getElementById('modalOverlay');
    const modalTitle = document.getElementById('modalTitle');
    const noteForm = document.getElementById('noteForm');
    const noteIdHidden = document.getElementById('noteId');
    const noteTitle = document.getElementById('noteTitle');
    const noteOwner = document.getElementById('noteOwner');
    const noteDate = document.getElementById('noteDate');
    const noteTags = document.getElementById('noteTags');
    const noteCategory = document.getElementById('noteCategory');
    const noteBody = document.getElementById('noteBody');
    const cancelModalBtn = document.getElementById('cancelModalBtn');
    const saveNoteBtn = document.getElementById('saveNoteBtn');

    // --- helpers ---
    function generateId() { return Date.now().toString(36) + '_' + Math.random().toString(36).slice(2,7); }

    function formatDate(dateStr) {
      if (!dateStr) return '';
      const d = new Date(dateStr + 'T00:00:00');
      return d.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
    }

    // --- localStorage ---
    function loadNotes() {
      try {
        const stored = localStorage.getItem('meetingNotesBoard');
        if (stored) notes = JSON.parse(stored);
        else notes = [];
      } catch { notes = []; }
    }
    function saveNotes() {
      localStorage.setItem('meetingNotesBoard', JSON.stringify(notes));
    }

    // --- stats ---
    function computeStats() {
      const total = notes.length;
      const actionRequired = notes.filter(n => n.category === 'Action Required').length;
      const owners = new Set(notes.map(n => n.owner.trim().toLowerCase()));
      const uniqueOwners = owners.size;

      // most common tag
      const tagCount = {};
      notes.forEach(n => {
        (n.tags || []).forEach(t => {
          const low = t.trim().toLowerCase();
          if (low) tagCount[low] = (tagCount[low] || 0) + 1;
        });
      });
      let mostCommon = '—';
      let maxCount = 0;
      for (const [tag, count] of Object.entries(tagCount)) {
        if (count > maxCount) { maxCount = count; mostCommon = tag; }
      }
      if (mostCommon !== '—') {
        // restore original capitalisation (pick first occurrence)
        for (const n of notes) {
          for (const t of (n.tags || [])) {
            if (t.trim().toLowerCase() === mostCommon) { mostCommon = t.trim(); break; }
          }
          if (mostCommon !== '—') break;
        }
      }
      totalEl.textContent = total;
      actionEl.textContent = actionRequired;
      uniqueOwnersEl.textContent = uniqueOwners;
      mostCommonTagEl.textContent = mostCommon;
    }

    // --- filter & render ---
    function getFilteredNotes() {
      return notes.filter(n => {
        const ownerMatch = !filters.owner || n.owner.toLowerCase() === filters.owner.toLowerCase();
        const tagMatch = !filters.tag || (n.tags || []).some(t => t.trim().toLowerCase() === filters.tag.toLowerCase());
        let searchMatch = true;
        if (filters.search) {
          const q = filters.search.toLowerCase();
          searchMatch = n.title.toLowerCase().includes(q) || n.owner.toLowerCase().includes(q) ||
                        (n.body || '').toLowerCase().includes(q) || (n.tags || []).some(t => t.toLowerCase().includes(q));
        }
        return ownerMatch && tagMatch && searchMatch;
      });
    }

    function render() {
      const filtered = getFilteredNotes();
      if (filtered.length === 0) {
        grid.innerHTML = `<div class="no-notes" role="status">No notes match your filters.</div>`;
      } else {
        let html = '';
        filtered.forEach(n => {
          const badgeClass = n.category === 'Action Required' ? 'badge-action' : n.category === 'Decision' ? 'badge-decision' : 'badge-reference';
          const tagsHtml = (n.tags || []).filter(t => t.trim()).map(t => `<span class="tag">${escapeHtml(t.trim())}</span>`).join('');
          const bodyExcerpt = n.body ? (n.body.length > 120 ? escapeHtml(n.body.slice(0,120)) + '…' : escapeHtml(n.body)) : '';
          html += `
            <div class="note-card" role="listitem" data-id="${n.id}">
              <div class="card-header">
                <span class="card-title">${escapeHtml(n.title)}</span>
                <span class="card-badge ${badgeClass}">${n.category}</span>
              </div>
              <div class="card-meta">
                <span>👤 ${escapeHtml(n.owner)}</span>
                <span>📅 ${formatDate(n.meetingDate)}</span>
              </div>
              ${bodyExcerpt ? `<div class="card-body">${bodyExcerpt}</div>` : ''}
              <div class="card-tags">${tagsHtml}</div>
              <div class="card-actions">
                <button class="edit-btn" data-id="${n.id}" aria-label="Edit note: ${escapeHtml(n.title)}">Edit</button>
                <button class="delete-btn" data-id="${n.id}" aria-label="Delete note: ${escapeHtml(n.title)}">Delete</button>
              </div>
            </div>`;
        });
        grid.innerHTML = html;
      }
      computeStats();
      updateFilterDropdowns();
    }

    function escapeHtml(text) {
      if (!text) return '';
      const div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML;
    }

    // --- filter dropdowns (owners & tags) from notes ---
    function updateFilterDropdowns() {
      const owners = new Set(notes.map(n => n.owner.trim()));
      const tags = new Set();
      notes.forEach(n => (n.tags || []).forEach(t => { if (t.trim()) tags.add(t.trim()); }));

      // owner select
      const currentOwner = filterOwner.value;
      filterOwner.innerHTML = '<option value="">All</option>';
      [...owners].sort().forEach(o => {
        filterOwner.innerHTML += `<option value="${escapeHtml(o)}">${escapeHtml(o)}</option>`;
      });
      if ([...owners].some(o => o === currentOwner)) filterOwner.value = currentOwner;
      else filterOwner.value = '';

      // tag select
      const currentTag = filterTag.value;
      filterTag.innerHTML = '<option value="">All</option>';
      [...tags].sort().forEach(t => {
        filterTag.innerHTML += `<option value="${escapeHtml(t)}">${escapeHtml(t)}</option>`;
      });
      if ([...tags].some(t => t === currentTag)) filterTag.value = currentTag;
      else filterTag.value = '';
    }

    // --- modal ---
    function openModal(note = null) {
      editingId = note ? note.id : null;
      modalTitle.textContent = note ? 'Edit note' : 'New note';
      noteIdHidden.value = note ? note.id : '';
      noteTitle.value = note ? note.title : '';
      noteOwner.value = note ? note.owner : '';
      noteDate.value = note ? note.meetingDate : '';
      noteTags.value = note && note.tags ? note.tags.join(', ') : '';
      noteCategory.value = note ? note.category : 'Reference';
      noteBody.value = note ? (note.body || '') : '';
      modalOverlay.classList.remove('hidden');
      noteTitle.focus();
    }

    function closeModal() {
      modalOverlay.classList.add('hidden');
      editingId = null;
    }

    function getFormData() {
      return {
        title: noteTitle.value.trim(),
        owner: noteOwner.value.trim(),
        meetingDate: noteDate.value,
        tags: noteTags.value.split(',').map(s => s.trim()).filter(s => s),
        category: noteCategory.value,
        body: noteBody.value.trim(),
      };
    }

    function handleSave(e) {
      e.preventDefault();
      const data = getFormData();
      if (!data.title || !data.owner || !data.meetingDate) {
        alert('Title, Owner, and Meeting date are required.');
        return;
      }
      if (editingId) {
        // edit existing
        const idx = notes.findIndex(n => n.id === editingId);
        if (idx !== -1) {
          notes[idx] = { ...notes[idx], ...data };
        }
      } else {
        // new note
        const newNote = {
          id: generateId(),
          ...data,
        };
        notes.push(newNote);
      }
      saveNotes();
      closeModal();
      render();
    }

    function deleteNote(id) {
      if (!confirm('Delete this note permanently?')) return;
      notes = notes.filter(n => n.id !== id);
      saveNotes();
      render();
    }

    // --- event listeners ---
    function setupEventListeners() {
      // add note button
      addNoteBtn.addEventListener('click', () => openModal(null));

      // cancel modal
      cancelModalBtn.addEventListener('click', closeModal);
      modalOverlay.addEventListener('click', (e) => { if (e.target === modalOverlay) closeModal(); });

      // form submit
      noteForm.addEventListener('submit', handleSave);

      // grid events (edit / delete)
      grid.addEventListener('click', (e) => {
        const editBtn = e.target.closest('.edit-btn');
        const deleteBtn = e.target.closest('.delete-btn');
        if (editBtn) {
          const id = editBtn.dataset.id;
          const note = notes.find(n => n.id === id);
          if (note) openModal(note);
        }
        if (deleteBtn) {
          const id = deleteBtn.dataset.id;
          deleteNote(id);
        }
      });

      // filter changes
      filterOwner.addEventListener('change', () => {
        filters.owner = filterOwner.value;
        render();
      });
      filterTag.addEventListener('change', () => {
        filters.tag = filterTag.value;
        render();
      });
      filterSearch.addEventListener('input', () => {
        filters.search = filterSearch.value;
        render();
      });
      clearFiltersBtn.addEventListener('click', () => {
        filterOwner.value = '';
        filterTag.value = '';
        filterSearch.value = '';
        filters = { owner: '', tag: '', search: '' };
        render();
      });

      // close modal with escape
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !modalOverlay.classList.contains('hidden')) {
          closeModal();
        }
      });
    }

    // --- initial ---
    function init() {
      loadNotes();
      // if no notes, add sample data for demonstration (but keep under 1000 lines)
      if (notes.length === 0) {
        const today = new Date();
        const ymd = d => d.toISOString().slice(0,10);
        const sample = [
          { id: generateId(), title: 'Sprint review', owner: 'Alice', meetingDate: ymd(new Date(today.getTime() - 86400000)), tags: ['sprint', 'frontend'], category: 'Decision', body: 'Approved new dashboard layout.' },
          { id: generateId(), title: 'Design sync', owner: 'Bob', meetingDate: ymd(today), tags: ['design', 'ui'], category: 'Action Required', body: 'Finalize color palette by Friday.' },
          { id: generateId(), title: 'Backend planning', owner: 'Carol', meetingDate: ymd(new Date(today.getTime() + 86400000 * 2)), tags: ['backend', 'api'], category: 'Reference', body: 'Notes on microservices migration.' },
          { id: generateId(), title: 'QA handoff', owner: 'Alice', meetingDate: ymd(new Date(today.getTime() - 86400000 * 3)), tags: ['testing'], category: 'Action Required', body: 'Write test plans for v2.1' },
        ];
        notes = sample;
        saveNotes();
      }
      render();
      setupEventListeners();
    }

    init();
  })();
</script>
</body>
</html>
```
````
