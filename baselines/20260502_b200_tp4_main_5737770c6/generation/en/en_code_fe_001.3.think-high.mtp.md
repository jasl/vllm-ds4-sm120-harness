# Generation Transcript

- Case: `en_code_fe_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 23.241028
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 226, "total_tokens": 6783, "completion_tokens": 6557, "prompt_tokens_details": null}`
- Prompt tokens: 226
- Completion tokens: 6557
- Total tokens: 6783

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
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.5">
    <title>Meeting notes board</title>
    <style>
        /* reset & base */
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
            background: #f4f6fb;
            color: #1e293b;
            line-height: 1.5;
            padding: 1.5rem 1rem;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        /* main container */
        .app {
            max-width: 1300px;
            margin: 0 auto;
            width: 100%;
        }

        h1 {
            font-weight: 600;
            font-size: 2rem;
            letter-spacing: -0.01em;
            margin-bottom: 0.6rem;
            color: #0f172a;
        }

        /* ----- stats strip ----- */
        .stats-strip {
            display: flex;
            flex-wrap: wrap;
            gap: 1.2rem 2rem;
            background: white;
            padding: 0.9rem 1.8rem;
            border-radius: 60px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.04);
            margin-bottom: 1.8rem;
            font-size: 0.95rem;
            font-weight: 500;
            border: 1px solid #e9eef3;
        }
        .stat-item {
            display: flex;
            align-items: baseline;
            gap: 0.4rem;
        }
        .stat-value {
            font-weight: 700;
            font-size: 1.25rem;
            color: #1e4f8a;
            min-width: 1.8rem;
        }

        /* ----- filters bar ----- */
        .filters {
            display: flex;
            flex-wrap: wrap;
            gap: 0.8rem 1.2rem;
            background: white;
            padding: 1.2rem 1.5rem;
            border-radius: 28px;
            margin-bottom: 2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.02);
            border: 1px solid #eef2f7;
            align-items: center;
        }
        .filter-group {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0.4rem 0.7rem;
        }
        .filter-group label {
            font-size: 0.85rem;
            font-weight: 500;
            color: #2c3e50;
        }
        .filter-group input,
        .filter-group select {
            font-size: 0.9rem;
            padding: 0.4rem 0.8rem;
            border-radius: 30px;
            border: 1px solid #d0d9e8;
            background: white;
            min-width: 130px;
            transition: 0.15s;
        }
        .filter-group input:focus,
        .filter-group select:focus {
            outline: 2px solid #3b7fc9;
            outline-offset: 2px;
            border-color: transparent;
        }
        .filter-group input {
            min-width: 170px;
        }
        .btn-reset {
            background: #eef2f7;
            border: none;
            padding: 0.4rem 1.2rem;
            border-radius: 30px;
            font-weight: 500;
            font-size: 0.85rem;
            cursor: pointer;
            transition: 0.1s;
        }
        .btn-reset:hover {
            background: #dce3ed;
        }
        .btn-reset:focus-visible {
            outline: 2px solid #1e4f8a;
        }

        /* ----- note grid ----- */
        .note-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1.5rem;
            margin-bottom: 2.5rem;
        }

        /* card */
        .note-card {
            background: white;
            border-radius: 28px;
            padding: 1.4rem 1.5rem 1.2rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.02);
            border: 1px solid #e3eaf2;
            transition: 0.1s;
            position: relative;
        }
        .note-card:hover {
            border-color: #cbd8e9;
        }
        .note-card .card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 0.45rem;
            gap: 0.5rem;
        }
        .note-card h3 {
            font-weight: 600;
            font-size: 1.2rem;
            word-break: break-word;
            margin-right: 0.5rem;
        }
        .note-card .meta {
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem 1rem;
            font-size: 0.8rem;
            color: #3b4b5e;
            margin: 0.3rem 0 0.5rem;
        }
        .note-card .meta span {
            background: #f0f4fe;
            padding: 0.15rem 0.7rem;
            border-radius: 40px;
            font-weight: 500;
        }
        .note-card .tags {
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem 0.5rem;
            margin: 0.6rem 0 0.8rem;
        }
        .tag-badge {
            background: #dfe9f8;
            font-size: 0.75rem;
            padding: 0.2rem 0.9rem;
            border-radius: 40px;
            font-weight: 500;
            color: #1e3b5c;
        }
        .note-card .body-preview {
            font-size: 0.9rem;
            color: #1f2a3a;
            margin: 0.6rem 0 0.9rem;
            word-break: break-word;
            background: #fafcff;
            padding: 0.5rem 0.7rem;
            border-radius: 16px;
            border-left: 3px solid #b7ceea;
        }
        .note-type-badge {
            display: inline-block;
            font-size: 0.7rem;
            font-weight: 600;
            padding: 0.2rem 1rem;
            border-radius: 30px;
            background: #eef2f6;
            letter-spacing: 0.02em;
            margin-bottom: 0.4rem;
        }
        .type-action { background: #fde6d2; color: #9d4b1a; }
        .type-decision { background: #d2e8fd; color: #1a5b8d; }
        .type-reference { background: #e3e9f2; color: #2d3c54; }

        .card-actions {
            display: flex;
            gap: 0.5rem;
            justify-content: flex-end;
            margin-top: 0.4rem;
            flex-wrap: wrap;
        }
        .card-actions button {
            background: transparent;
            border: 1px solid #dae1ed;
            padding: 0.25rem 1rem;
            border-radius: 30px;
            font-size: 0.8rem;
            font-weight: 500;
            cursor: pointer;
            transition: 0.1s;
        }
        .card-actions button:hover {
            background: #eef3fc;
        }
        .card-actions button:focus-visible {
            outline: 2px solid #1e4f8a;
            outline-offset: 2px;
        }
        .btn-delete {
            color: #a03d2f;
            border-color: #f0cdc8;
        }
        .btn-delete:hover {
            background: #fbeae7;
        }

        /* empty state */
        .empty-notes {
            grid-column: 1 / -1;
            text-align: center;
            padding: 3rem 1rem;
            color: #5b6f86;
            background: white;
            border-radius: 48px;
            border: 1px dashed #cbd8e9;
        }

        /* ----- add / edit form ----- */
        .form-panel {
            background: white;
            border-radius: 32px;
            padding: 1.8rem 2rem;
            border: 1px solid #e3eaf2;
            margin-top: 1.2rem;
            margin-bottom: 1rem;
        }
        .form-panel h2 {
            font-weight: 600;
            font-size: 1.5rem;
            margin-bottom: 1.2rem;
        }
        .form-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem 1.8rem;
        }
        .form-group {
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }
        .form-group label {
            font-weight: 500;
            font-size: 0.85rem;
        }
        .form-group input,
        .form-group select,
        .form-group textarea {
            font-size: 0.95rem;
            padding: 0.5rem 0.9rem;
            border-radius: 20px;
            border: 1px solid #d0d9e8;
            background: white;
            transition: 0.1s;
            font-family: inherit;
        }
        .form-group textarea {
            min-height: 80px;
            resize: vertical;
        }
        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
            outline: 2px solid #2f6eb3;
            outline-offset: 2px;
            border-color: transparent;
        }
        .full-width {
            grid-column: 1 / -1;
        }
        .form-actions {
            display: flex;
            gap: 1rem;
            margin-top: 1.2rem;
            flex-wrap: wrap;
        }
        .form-actions button {
            background: #1e4f8a;
            border: none;
            padding: 0.5rem 2rem;
            border-radius: 40px;
            font-weight: 600;
            color: white;
            font-size: 0.95rem;
            cursor: pointer;
            transition: 0.1s;
        }
        .form-actions button:hover {
            background: #143a66;
        }
        .form-actions button:focus-visible {
            outline: 3px solid #a2c4f0;
            outline-offset: 2px;
        }
        .btn-cancel {
            background: transparent !important;
            color: #1e293b !important;
            border: 1px solid #bccbdf !important;
        }
        .btn-cancel:hover {
            background: #eff4fd !important;
        }

        /* responsive */
        @media (max-width: 680px) {
            .note-grid {
                grid-template-columns: 1fr;
                gap: 1rem;
            }
            .form-grid {
                grid-template-columns: 1fr;
            }
            .filters {
                flex-direction: column;
                align-items: stretch;
            }
            .filter-group {
                flex-wrap: wrap;
            }
            .stats-strip {
                border-radius: 40px;
                padding: 0.8rem 1.2rem;
                gap: 0.8rem 1.2rem;
            }
        }

        /* visible focus for all interactive */
        button:focus-visible,
        input:focus-visible,
        select:focus-visible,
        textarea:focus-visible {
            outline: 2px solid #1e4f8a;
            outline-offset: 2px;
        }
        /* remove default outline for mouse */
        button:focus:not(:focus-visible),
        input:focus:not(:focus-visible),
        select:focus:not(:focus-visible) {
            outline: none;
        }
    </style>
</head>
<body>
<div class="app">
    <h1>📋 Meeting notes board</h1>

    <!-- stats strip -->
    <div class="stats-strip" role="region" aria-label="Statistics">
        <div class="stat-item"><span class="stat-value" id="statTotal">0</span> total notes</div>
        <div class="stat-item"><span class="stat-value" id="statAction">0</span> action required</div>
        <div class="stat-item"><span class="stat-value" id="statOwners">0</span> unique owners</div>
        <div class="stat-item"><span class="stat-value" id="statTopTag">—</span> most common tag</div>
    </div>

    <!-- filters -->
    <div class="filters" role="group" aria-label="Filter controls">
        <div class="filter-group">
            <label for="filterOwner">👤 Owner</label>
            <select id="filterOwner" aria-label="Filter by owner">
                <option value="">All owners</option>
            </select>
        </div>
        <div class="filter-group">
            <label for="filterTag">🏷️ Tag</label>
            <select id="filterTag" aria-label="Filter by tag">
                <option value="">All tags</option>
            </select>
        </div>
        <div class="filter-group">
            <label for="filterSearch">🔍 Search</label>
            <input type="text" id="filterSearch" placeholder="title, body, owner..." aria-label="Free text search">
        </div>
        <button class="btn-reset" id="resetFilters" aria-label="Reset all filters">Reset</button>
    </div>

    <!-- note grid -->
    <div id="noteGrid" class="note-grid" role="list" aria-label="Meeting notes"></div>

    <!-- add form -->
    <div class="form-panel" id="formPanel">
        <h2 id="formTitle">➕ Add new note</h2>
        <form id="noteForm" novalidate>
            <div class="form-grid">
                <div class="form-group">
                    <label for="noteTitle">Title *</label>
                    <input type="text" id="noteTitle" required aria-required="true" placeholder="e.g. Sprint review">
                </div>
                <div class="form-group">
                    <label for="noteOwner">Owner *</label>
                    <input type="text" id="noteOwner" required aria-required="true" placeholder="e.g. Ana">
                </div>
                <div class="form-group">
                    <label for="noteDate">Meeting date</label>
                    <input type="date" id="noteDate">
                </div>
                <div class="form-group">
                    <label for="noteTags">Tags (comma separated)</label>
                    <input type="text" id="noteTags" placeholder="e.g. design, frontend">
                </div>
                <div class="form-group full-width">
                    <label for="noteBody">Notes</label>
                    <textarea id="noteBody" placeholder="Details ..." rows="3"></textarea>
                </div>
                <div class="form-group">
                    <label for="noteType">Type</label>
                    <select id="noteType">
                        <option value="Action Required">⚠️ Action Required</option>
                        <option value="Decision">✅ Decision</option>
                        <option value="Reference">📎 Reference</option>
                    </select>
                </div>
            </div>
            <div class="form-actions">
                <button type="submit" id="submitBtn">💾 Save note</button>
                <button type="button" id="cancelEditBtn" class="btn-cancel" style="display:none;">Cancel</button>
            </div>
            <input type="hidden" id="editId" value="">
        </form>
    </div>
</div>

<script>
    (function() {
        // ----- data layer -----
        const STORAGE_KEY = 'meeting_notes_board';
        let notes = [];
        let editingId = null;   // string (id)

        // DOM refs
        const grid = document.getElementById('noteGrid');
        const form = document.getElementById('noteForm');
        const formTitle = document.getElementById('formTitle');
        const submitBtn = document.getElementById('submitBtn');
        const editIdInput = document.getElementById('editId');
        const cancelEditBtn = document.getElementById('cancelEditBtn');

        const filterOwner = document.getElementById('filterOwner');
        const filterTag = document.getElementById('filterTag');
        const filterSearch = document.getElementById('filterSearch');
        const resetBtn = document.getElementById('resetFilters');

        const statTotal = document.getElementById('statTotal');
        const statAction = document.getElementById('statAction');
        const statOwners = document.getElementById('statOwners');
        const statTopTag = document.getElementById('statTopTag');

        // initialize
        function loadFromStorage() {
            const stored = localStorage.getItem(STORAGE_KEY);
            if (stored) {
                try {
                    notes = JSON.parse(stored);
                    // ensure tags array
                    notes = notes.map(n => ({ ...n, tags: Array.isArray(n.tags) ? n.tags : [] }));
                } catch(e) { notes = []; }
            } else {
                // seed demo data
                notes = [
                    { id: '1', title: 'Sprint planning', owner: 'Ana', date: '2025-03-10', tags: ['planning','frontend'], body: 'Set goals for sprint 12.', type: 'Decision' },
                    { id: '2', title: 'Design review', owner: 'Ben', date: '2025-03-12', tags: ['design','UX'], body: 'New dashboard mockup approved with changes.', type: 'Action Required' },
                    { id: '3', title: 'Retrospective', owner: 'Ana', date: '2025-03-14', tags: ['retro','team'], body: 'Action items: improve CI pipeline.', type: 'Reference' },
                    { id: '4', title: 'API discussion', owner: 'Chloe', date: '2025-03-15', tags: ['backend','API'], body: 'Decided to use REST for new service.', type: 'Decision' },
                ];
                saveToStorage();
            }
            renderAll();
        }

        function saveToStorage() {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(notes));
        }

        // generate simple id
        function genId() { return Date.now().toString(36) + Math.random().toString(36).slice(2,6); }

        // ----- CRUD -----
        function addNote(note) {
            note.id = genId();
            notes.push(note);
            saveToStorage();
            renderAll();
        }

        function updateNote(id, updated) {
            const idx = notes.findIndex(n => n.id === id);
            if (idx !== -1) {
                notes[idx] = { ...notes[idx], ...updated, id };
                saveToStorage();
                renderAll();
            }
        }

        function deleteNote(id) {
            notes = notes.filter(n => n.id !== id);
            saveToStorage();
            renderAll();
        }

        // ----- render helpers -----
        function getAllOwners() {
            const set = new Set(notes.map(n => n.owner.trim().toLowerCase()));
            return [...new Set(notes.map(n => n.owner))].filter(o => o.trim() !== '');
        }

        function getAllTags() {
            const tagSet = new Set();
            notes.forEach(n => (n.tags || []).forEach(t => tagSet.add(t.trim())));
            return [...tagSet].filter(t => t !== '');
        }

        function getFilteredNotes() {
            const ownerFilter = filterOwner.value.trim().toLowerCase();
            const tagFilter = filterTag.value.trim().toLowerCase();
            const search = filterSearch.value.trim().toLowerCase();

            return notes.filter(n => {
                if (ownerFilter && n.owner.trim().toLowerCase() !== ownerFilter) return false;
                if (tagFilter) {
                    const noteTags = (n.tags || []).map(t => t.trim().toLowerCase());
                    if (!noteTags.includes(tagFilter)) return false;
                }
                if (search) {
                    const haystack = (n.title + ' ' + n.owner + ' ' + n.body + ' ' + (n.tags || []).join(' ')).toLowerCase();
                    if (!haystack.includes(search)) return false;
                }
                return true;
            });
        }

        function renderStats() {
            const total = notes.length;
            const actionCount = notes.filter(n => n.type === 'Action Required').length;
            const uniqueOwners = new Set(notes.map(n => n.owner.trim().toLowerCase())).size;
            // most common tag
            const tagFreq = {};
            notes.forEach(n => (n.tags || []).forEach(t => {
                const key = t.trim();
                if (key) tagFreq[key] = (tagFreq[key] || 0) + 1;
            }));
            let topTag = '—';
            let maxCount = 0;
            for (const [tag, count] of Object.entries(tagFreq)) {
                if (count > maxCount) { maxCount = count; topTag = tag; }
            }
            statTotal.textContent = total;
            statAction.textContent = actionCount;
            statOwners.textContent = uniqueOwners;
            statTopTag.textContent = topTag;
        }

        function renderCards() {
            const filtered = getFilteredNotes();
            const owners = getAllOwners();
            const tags = getAllTags();

            // update filter dropdowns (preserve selection)
            const prevOwner = filterOwner.value;
            const prevTag = filterTag.value;
            filterOwner.innerHTML = '<option value="">All owners</option>' + owners.map(o => `<option value="${o}">${o}</option>`).join('');
            filterTag.innerHTML = '<option value="">All tags</option>' + tags.map(t => `<option value="${t}">${t}</option>`).join('');
            filterOwner.value = prevOwner;
            filterTag.value = prevTag;

            if (filtered.length === 0) {
                grid.innerHTML = `<div class="empty-notes" role="listitem">📭 No notes match your filters.</div>`;
                return;
            }

            let html = '';
            filtered.forEach(n => {
                const tagsHtml = (n.tags || []).filter(t => t.trim() !== '').map(t => `<span class="tag-badge">${escapeHtml(t.trim())}</span>`).join('');
                const typeClass = n.type === 'Action Required' ? 'type-action' : (n.type === 'Decision' ? 'type-decision' : 'type-reference');
                const dateStr = n.date || '—';
                html += `
                    <div class="note-card" role="listitem" data-id="${n.id}">
                        <div class="card-header">
                            <h3>${escapeHtml(n.title)}</h3>
                            <span class="note-type-badge ${typeClass}">${escapeHtml(n.type)}</span>
                        </div>
                        <div class="meta">
                            <span>👤 ${escapeHtml(n.owner)}</span>
                            <span>📅 ${escapeHtml(dateStr)}</span>
                        </div>
                        ${tagsHtml ? `<div class="tags">${tagsHtml}</div>` : ''}
                        <div class="body-preview">${escapeHtml(n.body || '')}</div>
                        <div class="card-actions">
                            <button class="btn-edit" data-id="${n.id}" aria-label="Edit note: ${escapeHtml(n.title)}">✏️ Edit</button>
                            <button class="btn-delete" data-id="${n.id}" aria-label="Delete note: ${escapeHtml(n.title)}">🗑️ Delete</button>
                        </div>
                    </div>
                `;
            });
            grid.innerHTML = html;

            // attach event listeners to cards
            grid.querySelectorAll('.btn-edit').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const id = e.currentTarget.dataset.id;
                    populateFormForEdit(id);
                });
            });
            grid.querySelectorAll('.btn-delete').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const id = e.currentTarget.dataset.id;
                    if (confirm('Delete this note?')) deleteNote(id);
                });
            });
        }

        function escapeHtml(str) {
            if (!str) return '';
            return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
        }

        function renderAll() {
            renderStats();
            renderCards();
            // clear edit if note removed
            if (editingId && !notes.find(n => n.id === editingId)) {
                resetForm();
            }
        }

        // ----- form logic -----
        function resetForm() {
            form.reset();
            editIdInput.value = '';
            editingId = null;
            formTitle.textContent = '➕ Add new note';
            submitBtn.textContent = '💾 Save note';
            cancelEditBtn.style.display = 'none';
            document.getElementById('noteDate').value = new Date().toISOString().slice(0,10);
        }

        function populateFormForEdit(id) {
            const note = notes.find(n => n.id === id);
            if (!note) return;
            editingId = id;
            editIdInput.value = id;
            document.getElementById('noteTitle').value = note.title || '';
            document.getElementById('noteOwner').value = note.owner || '';
            document.getElementById('noteDate').value = note.date || '';
            document.getElementById('noteTags').value = (note.tags || []).join(', ');
            document.getElementById('noteBody').value = note.body || '';
            document.getElementById('noteType').value = note.type || 'Reference';
            formTitle.textContent = '✏️ Edit note';
            submitBtn.textContent = '💾 Update note';
            cancelEditBtn.style.display = 'inline-block';
            window.scrollTo({ top: document.getElementById('formPanel').offsetTop - 20, behavior: 'smooth' });
        }

        function handleFormSubmit(e) {
            e.preventDefault();
            const title = document.getElementById('noteTitle').value.trim();
            const owner = document.getElementById('noteOwner').value.trim();
            if (!title || !owner) {
                alert('Title and Owner are required.');
                return;
            }
            const date = document.getElementById('noteDate').value;
            const tagsRaw = document.getElementById('noteTags').value;
            const tags = tagsRaw.split(',').map(t => t.trim()).filter(t => t !== '');
            const body = document.getElementById('noteBody').value.trim();
            const type = document.getElementById('noteType').value;

            const noteData = { title, owner, date, tags, body, type };

            const id = editIdInput.value;
            if (id && notes.find(n => n.id === id)) {
                updateNote(id, noteData);
            } else {
                addNote(noteData);
            }
            resetForm();
        }

        // cancel edit
        function cancelEdit() {
            if (editingId) {
                resetForm();
            }
        }

        // ----- filter handlers -----
        function applyFilters() {
            renderCards();
            renderStats(); // stats stays for all notes (but we show global stats as required)
        }

        function resetFilters() {
            filterOwner.value = '';
            filterTag.value = '';
            filterSearch.value = '';
            applyFilters();
        }

        // ----- init -----
        function init() {
            loadFromStorage();

            // event listeners
            form.addEventListener('submit', handleFormSubmit);
            cancelEditBtn.addEventListener('click', cancelEdit);
            resetBtn.addEventListener('click', resetFilters);
            filterOwner.addEventListener('change', applyFilters);
            filterTag.addEventListener('change', applyFilters);
            filterSearch.addEventListener('input', applyFilters);

            // set default date
            if (!document.getElementById('noteDate').value) {
                document.getElementById('noteDate').value = new Date().toISOString().slice(0,10);
            }

            // keyboard support: delete via keyboard on cards (delegated)
            grid.addEventListener('keydown', (e) => {
                if (e.key === 'Delete' || e.key === 'Backspace') {
                    const card = e.target.closest('.note-card');
                    if (card) {
                        const id = card.dataset.id;
                        if (id && confirm('Delete this note?')) deleteNote(id);
                    }
                }
            });
            // make cards focusable for keyboard
            // (but we already have buttons inside, it's fine)
        }

        init();
    })();
</script>
</body>
</html>
```
````
