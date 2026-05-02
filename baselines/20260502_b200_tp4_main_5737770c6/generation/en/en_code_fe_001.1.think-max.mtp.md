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
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 24.248455
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 226, "total_tokens": 7214, "completion_tokens": 6988, "prompt_tokens_details": null}`
- Prompt tokens: 226
- Completion tokens: 6988
- Total tokens: 7214

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
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.5, user-scalable=yes">
    <title>Meeting Notes Board – team</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
            background: #f4f6fa;
            color: #1e2a41;
            padding: 1.5rem 1rem 2rem;
            line-height: 1.5;
        }
        h1, h2, h3 {
            font-weight: 500;
            letter-spacing: -0.01em;
        }
        h1 {
            font-size: 1.8rem;
            margin-bottom: 0.75rem;
        }
        .wrapper {
            max-width: 1320px;
            margin: 0 auto;
        }

        /* stats strip */
        .stats-strip {
            background: white;
            border-radius: 20px;
            padding: 1.1rem 1.6rem;
            display: flex;
            flex-wrap: wrap;
            gap: 1.2rem 2.5rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.04);
            margin-bottom: 2rem;
            align-items: center;
            font-size: 0.95rem;
        }
        .stat-item {
            display: flex;
            align-items: baseline;
            gap: 0.35rem;
        }
        .stat-badge {
            background: #eef2f7;
            padding: 0.2rem 0.7rem;
            border-radius: 40px;
            font-weight: 500;
            color: #1e2a41;
            font-size: 0.9rem;
        }
        .stat-label {
            color: #3d4e6b;
        }
        .stat-value {
            font-weight: 600;
            font-size: 1.1rem;
            color: #0b1a33;
        }

        /* filter bar */
        .filter-bar {
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem 1rem;
            background: white;
            padding: 1rem 1.5rem;
            border-radius: 28px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.02);
            margin-bottom: 2rem;
            align-items: center;
        }
        .filter-group {
            display: flex;
            align-items: center;
            gap: 0.4rem 0.8rem;
            flex-wrap: wrap;
        }
        .filter-group label {
            font-size: 0.85rem;
            font-weight: 500;
            color: #2c3e5a;
        }
        .filter-input {
            border: 1px solid #d8e0ec;
            border-radius: 40px;
            padding: 0.4rem 1rem;
            font-size: 0.9rem;
            background: white;
            min-width: 120px;
            transition: 0.2s;
        }
        .filter-input:focus {
            outline: 2px solid #005fcc;
            outline-offset: 2px;
            border-color: transparent;
        }
        .filter-select {
            border: 1px solid #d8e0ec;
            border-radius: 40px;
            padding: 0.4rem 1.8rem 0.4rem 1rem;
            font-size: 0.9rem;
            background: white;
            min-width: 110px;
            appearance: none;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%233d4e6b' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: right 0.5rem center;
            background-size: 1rem;
        }
        .filter-select:focus {
            outline: 2px solid #005fcc;
            outline-offset: 2px;
            border-color: transparent;
        }
        .clear-btn {
            background: transparent;
            border: 1px solid #bcc9db;
            border-radius: 40px;
            padding: 0.3rem 1.2rem;
            font-size: 0.85rem;
            cursor: pointer;
            margin-left: auto;
            transition: 0.15s;
            color: #1e2a41;
        }
        .clear-btn:hover {
            background: #e8edf5;
        }
        .clear-btn:focus-visible {
            outline: 2px solid #005fcc;
            outline-offset: 2px;
        }

        /* add note & edit panel */
        .panel {
            background: white;
            border-radius: 24px;
            padding: 1.5rem 1.8rem;
            box-shadow: 0 6px 18px rgba(0,0,0,0.03);
            margin-bottom: 2.5rem;
        }
        .panel h2 {
            font-size: 1.3rem;
            margin-bottom: 1rem;
        }
        .note-form {
            display: flex;
            flex-wrap: wrap;
            gap: 0.8rem 1.2rem;
        }
        .form-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.6rem 1rem;
            width: 100%;
        }
        .form-group {
            display: flex;
            flex-direction: column;
            flex: 1 0 150px;
            min-width: 140px;
        }
        .form-group label {
            font-size: 0.75rem;
            font-weight: 500;
            color: #3d4e6b;
            margin-bottom: 0.2rem;
        }
        .form-group input, .form-group select, .form-group textarea {
            border: 1px solid #d8e0ec;
            border-radius: 18px;
            padding: 0.5rem 1rem;
            font-size: 0.9rem;
            background: white;
            font-family: inherit;
        }
        .form-group textarea {
            min-height: 70px;
            resize: vertical;
        }
        .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
            outline: 2px solid #005fcc;
            outline-offset: 2px;
            border-color: transparent;
        }
        .btn-primary {
            background: #1e2a41;
            color: white;
            border: none;
            border-radius: 40px;
            padding: 0.5rem 1.8rem;
            font-weight: 500;
            font-size: 0.95rem;
            cursor: pointer;
            transition: 0.15s;
            align-self: flex-end;
            margin-top: 0.3rem;
        }
        .btn-primary:hover {
            background: #2b3b59;
        }
        .btn-primary:focus-visible {
            outline: 2px solid #005fcc;
            outline-offset: 3px;
        }
        .btn-secondary {
            background: #eef2f7;
            border: 1px solid #cbd4e2;
            border-radius: 40px;
            padding: 0.4rem 1.5rem;
            cursor: pointer;
            font-weight: 500;
            transition: 0.15s;
        }
        .btn-secondary:hover {
            background: #e2e8f0;
        }
        .btn-secondary:focus-visible {
            outline: 2px solid #005fcc;
            outline-offset: 2px;
        }
        .btn-danger {
            background: transparent;
            border: 1px solid #d0a0a0;
            color: #b13a3a;
            border-radius: 40px;
            padding: 0.4rem 1.2rem;
            cursor: pointer;
            font-weight: 500;
        }
        .btn-danger:hover {
            background: #fbe9e9;
            border-color: #b13a3a;
        }
        .btn-danger:focus-visible {
            outline: 2px solid #b13a3a;
            outline-offset: 2px;
        }

        /* cards grid */
        .cards-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1.2rem;
        }
        @media (max-width: 640px) {
            .cards-grid {
                grid-template-columns: 1fr;
            }
        }

        .note-card {
            background: white;
            border-radius: 24px;
            padding: 1.2rem 1.5rem 1.5rem;
            box-shadow: 0 8px 20px rgba(0,0,0,0.02);
            border-left: 5px solid #b8c7dd;
            transition: 0.1s;
        }
        .note-card[data-category="action"] {
            border-left-color: #d1453b;
        }
        .note-card[data-category="decision"] {
            border-left-color: #2d7b9b;
        }
        .note-card[data-category="reference"] {
            border-left-color: #6f8c6f;
        }
        .note-card-header {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            flex-wrap: wrap;
            gap: 0.3rem 0.8rem;
            margin-bottom: 0.3rem;
        }
        .note-title {
            font-weight: 600;
            font-size: 1.1rem;
            word-break: break-word;
        }
        .note-category-badge {
            font-size: 0.7rem;
            font-weight: 500;
            padding: 0.15rem 0.8rem;
            border-radius: 30px;
            background: #eef2f7;
            color: #1e2a41;
            white-space: nowrap;
        }
        .note-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem 1.2rem;
            font-size: 0.8rem;
            color: #3d4e6b;
            margin: 0.5rem 0 0.6rem;
        }
        .note-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 0.3rem 0.5rem;
            margin: 0.6rem 0 0.8rem;
        }
        .tag {
            background: #e2e9f2;
            border-radius: 40px;
            padding: 0.1rem 0.8rem;
            font-size: 0.75rem;
            font-weight: 500;
            color: #1f334c;
        }
        .note-body {
            font-size: 0.9rem;
            color: #1e2a41;
            white-space: pre-wrap;
            word-break: break-word;
            margin-bottom: 1rem;
            background: #fafcff;
            padding: 0.5rem 0.7rem;
            border-radius: 12px;
        }
        .card-actions {
            display: flex;
            gap: 0.6rem;
            flex-wrap: wrap;
            margin-top: 0.5rem;
        }
        .empty-notes {
            grid-column: 1 / -1;
            text-align: center;
            padding: 3rem 1rem;
            color: #4a5e7a;
            font-size: 1rem;
        }
        .hidden {
            display: none !important;
        }
        .flex-spacer {
            flex: 1;
        }
        .tag-gray {
            background: #dce3ec;
        }
        .sr-only {
            position: absolute;
            width: 1px;
            height: 1px;
            padding: 0;
            margin: -1px;
            overflow: hidden;
            clip: rect(0,0,0,0);
            border: 0;
        }
        button {
            font-family: inherit;
        }
    </style>
</head>
<body>
<div class="wrapper">
    <h1>📋 Meeting notes board</h1>

    <!-- stats strip -->
    <section class="stats-strip" aria-label="Statistics overview">
        <div class="stat-item"><span class="stat-label">📌 total</span> <span id="statTotal" class="stat-value">0</span></div>
        <div class="stat-item"><span class="stat-label">⚡ action</span> <span id="statAction" class="stat-value">0</span></div>
        <div class="stat-item"><span class="stat-label">👥 owners</span> <span id="statOwners" class="stat-value">0</span></div>
        <div class="stat-item"><span class="stat-label">🏷️ top tag</span> <span id="statTag" class="stat-badge">—</span></div>
    </section>

    <!-- filter bar -->
    <div class="filter-bar" role="search" aria-label="Filter notes">
        <div class="filter-group">
            <label for="filterOwner">Owner</label>
            <select id="filterOwner" class="filter-select">
                <option value="">all</option>
            </select>
        </div>
        <div class="filter-group">
            <label for="filterTag">Tag</label>
            <select id="filterTag" class="filter-select">
                <option value="">all</option>
            </select>
        </div>
        <div class="filter-group">
            <label for="filterSearch">Search</label>
            <input type="text" id="filterSearch" class="filter-input" placeholder="title, body…" aria-label="Free text search">
        </div>
        <button id="clearFiltersBtn" class="clear-btn" aria-label="Clear all filters">clear</button>
    </div>

    <!-- add note panel -->
    <section class="panel" aria-label="Add new note">
        <h2>➕ Add note</h2>
        <form id="addForm" class="note-form" novalidate>
            <div class="form-row">
                <div class="form-group">
                    <label for="addTitle">Title *</label>
                    <input type="text" id="addTitle" required placeholder="e.g. Sprint review">
                </div>
                <div class="form-group">
                    <label for="addOwner">Owner</label>
                    <input type="text" id="addOwner" placeholder="Alice">
                </div>
                <div class="form-group">
                    <label for="addDate">Meeting date</label>
                    <input type="date" id="addDate">
                </div>
                <div class="form-group">
                    <label for="addCategory">Category</label>
                    <select id="addCategory">
                        <option value="action">Action Required</option>
                        <option value="decision">Decision</option>
                        <option value="reference">Reference</option>
                    </select>
                </div>
            </div>
            <div class="form-row">
                <div class="form-group" style="flex:2; min-width:180px;">
                    <label for="addTags">Tags (comma separated)</label>
                    <input type="text" id="addTags" placeholder="design, frontend">
                </div>
                <div class="form-group" style="flex:3; min-width:200px;">
                    <label for="addBody">Body</label>
                    <textarea id="addBody" placeholder="Key points…"></textarea>
                </div>
            </div>
            <button type="submit" class="btn-primary" id="saveNoteBtn">Save note</button>
        </form>
    </section>

    <!-- edit panel (hidden) -->
    <section class="panel hidden" id="editPanel" aria-label="Edit note">
        <h2>✏️ Edit note</h2>
        <form id="editForm" class="note-form" novalidate>
            <input type="hidden" id="editId" value="">
            <div class="form-row">
                <div class="form-group">
                    <label for="editTitle">Title *</label>
                    <input type="text" id="editTitle" required>
                </div>
                <div class="form-group">
                    <label for="editOwner">Owner</label>
                    <input type="text" id="editOwner">
                </div>
                <div class="form-group">
                    <label for="editDate">Meeting date</label>
                    <input type="date" id="editDate">
                </div>
                <div class="form-group">
                    <label for="editCategory">Category</label>
                    <select id="editCategory">
                        <option value="action">Action Required</option>
                        <option value="decision">Decision</option>
                        <option value="reference">Reference</option>
                    </select>
                </div>
            </div>
            <div class="form-row">
                <div class="form-group" style="flex:2; min-width:180px;">
                    <label for="editTags">Tags (comma separated)</label>
                    <input type="text" id="editTags" placeholder="design, frontend">
                </div>
                <div class="form-group" style="flex:3; min-width:200px;">
                    <label for="editBody">Body</label>
                    <textarea id="editBody" rows="2"></textarea>
                </div>
            </div>
            <div style="display: flex; gap: 0.8rem; flex-wrap: wrap;">
                <button type="submit" class="btn-primary">Update note</button>
                <button type="button" id="cancelEditBtn" class="btn-secondary">Cancel</button>
            </div>
        </form>
    </section>

    <!-- notes grid -->
    <div id="notesContainer" class="cards-grid" role="region" aria-label="Notes list">
        <div class="empty-notes">No notes yet. Add one above.</div>
    </div>
</div>
<script>
    (function() {
        const STORAGE_KEY = 'meeting_notes_board';

        // ---- data ----
        let notes = [];

        // load from localStorage
        function loadNotes() {
            try {
                const stored = localStorage.getItem(STORAGE_KEY);
                if (stored) {
                    notes = JSON.parse(stored);
                    if (!Array.isArray(notes)) notes = [];
                } else {
                    notes = [];
                }
            } catch(e) { notes = []; }
        }
        function saveNotes() {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(notes));
        }

        // ---- generate id ----
        function nextId() {
            return Date.now() + '_' + Math.random().toString(36).slice(2,7);
        }

        // ---- dom refs ----
        const container = document.getElementById('notesContainer');
        const addForm = document.getElementById('addForm');
        const editPanel = document.getElementById('editPanel');
        const editForm = document.getElementById('editForm');
        const editId = document.getElementById('editId');
        const cancelEditBtn = document.getElementById('cancelEditBtn');

        const filterOwner = document.getElementById('filterOwner');
        const filterTag = document.getElementById('filterTag');
        const filterSearch = document.getElementById('filterSearch');
        const clearFiltersBtn = document.getElementById('clearFiltersBtn');

        const statTotal = document.getElementById('statTotal');
        const statAction = document.getElementById('statAction');
        const statOwners = document.getElementById('statOwners');
        const statTag = document.getElementById('statTag');

        // ---- helper: get unique tags from notes ----
        function getAllUniqueTags() {
            const tagSet = new Set();
            notes.forEach(n => {
                (n.tags || []).forEach(t => tagSet.add(t.trim().toLowerCase()));
            });
            return [...tagSet].sort();
        }

        // ---- helper: get unique owners ----
        function getAllUniqueOwners() {
            const ownerSet = new Set(notes.map(n => (n.owner || '').trim()).filter(o => o !== ''));
            return [...ownerSet].sort();
        }

        // ---- update filter dropdowns ----
        function populateFilterDropdowns() {
            // owners
            const owners = getAllUniqueOwners();
            const currentOwner = filterOwner.value;
            filterOwner.innerHTML = '<option value="">all</option>';
            owners.forEach(ow => {
                const opt = document.createElement('option');
                opt.value = ow;
                opt.textContent = ow;
                filterOwner.appendChild(opt);
            });
            if (owners.includes(currentOwner)) filterOwner.value = currentOwner;
            else filterOwner.value = '';

            // tags
            const tags = getAllUniqueTags();
            const currentTag = filterTag.value;
            filterTag.innerHTML = '<option value="">all</option>';
            tags.forEach(t => {
                const opt = document.createElement('option');
                opt.value = t;
                opt.textContent = t;
                filterTag.appendChild(opt);
            });
            if (tags.includes(currentTag)) filterTag.value = currentTag;
            else filterTag.value = '';
        }

        // ---- compute stats ----
        function updateStats() {
            const total = notes.length;
            const actionCount = notes.filter(n => n.category === 'action').length;
            const uniqueOwners = new Set(notes.map(n => (n.owner || '').trim()).filter(o => o)).size;

            // most common tag
            const tagFreq = {};
            notes.forEach(n => {
                (n.tags || []).forEach(t => {
                    const key = t.trim().toLowerCase();
                    if (key) tagFreq[key] = (tagFreq[key] || 0) + 1;
                });
            });
            let topTag = '—';
            let maxCount = 0;
            for (const [tag, count] of Object.entries(tagFreq)) {
                if (count > maxCount) {
                    maxCount = count;
                    topTag = tag;
                }
            }
            statTotal.textContent = total;
            statAction.textContent = actionCount;
            statOwners.textContent = uniqueOwners;
            statTag.textContent = topTag;
        }

        // ---- render cards ----
        function renderNotes() {
            const ownerFilter = filterOwner.value.trim().toLowerCase();
            const tagFilter = filterTag.value.trim().toLowerCase();
            const searchFilter = filterSearch.value.trim().toLowerCase();

            let filtered = notes.filter(n => {
                if (ownerFilter && (n.owner || '').trim().toLowerCase() !== ownerFilter) return false;
                if (tagFilter) {
                    const noteTags = (n.tags || []).map(t => t.trim().toLowerCase());
                    if (!noteTags.includes(tagFilter)) return false;
                }
                if (searchFilter) {
                    const title = (n.title || '').toLowerCase();
                    const body = (n.body || '').toLowerCase();
                    const owner = (n.owner || '').toLowerCase();
                    const tagsStr = (n.tags || []).join(' ').toLowerCase();
                    if (!title.includes(searchFilter) && !body.includes(searchFilter) && !owner.includes(searchFilter) && !tagsStr.includes(searchFilter)) {
                        return false;
                    }
                }
                return true;
            });

            if (filtered.length === 0) {
                container.innerHTML = `<div class="empty-notes">No matching notes.</div>`;
                return;
            }

            let html = '';
            filtered.forEach(note => {
                const category = note.category || 'reference';
                const catLabel = category === 'action' ? 'Action Required' : category === 'decision' ? 'Decision' : 'Reference';
                const dateStr = note.meetingDate || '';
                const tags = note.tags || [];
                const tagHtml = tags.map(t => `<span class="tag">${escapeHtml(t)}</span>`).join(' ');
                const owner = escapeHtml(note.owner || '—');
                const title = escapeHtml(note.title || 'Untitled');
                const body = escapeHtml(note.body || '');

                html += `
                    <div class="note-card" data-id="${note.id}" data-category="${category}">
                        <div class="note-card-header">
                            <span class="note-title">${title}</span>
                            <span class="note-category-badge">${catLabel}</span>
                        </div>
                        <div class="note-meta">
                            <span>👤 ${owner}</span>
                            ${dateStr ? `<span>📅 ${escapeHtml(dateStr)}</span>` : ''}
                        </div>
                        ${tagHtml ? `<div class="note-tags">${tagHtml}</div>` : ''}
                        ${body ? `<div class="note-body">${body}</div>` : ''}
                        <div class="card-actions">
                            <button class="btn-secondary edit-btn" data-id="${note.id}" aria-label="Edit note">✎ Edit</button>
                            <button class="btn-danger delete-btn" data-id="${note.id}" aria-label="Delete note">🗑 Delete</button>
                        </div>
                    </div>
                `;
            });
            container.innerHTML = html;

            // attach event listeners for edit/delete
            container.querySelectorAll('.edit-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const id = btn.getAttribute('data-id');
                    openEditPanel(id);
                });
            });
            container.querySelectorAll('.delete-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const id = btn.getAttribute('data-id');
                    deleteNoteById(id);
                });
            });
        }

        function escapeHtml(str) {
            if (!str) return '';
            return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
        }

        // ---- CRUD ----
        function addNote(title, owner, meetingDate, category, tagsArr, body) {
            const newNote = {
                id: nextId(),
                title: title.trim(),
                owner: owner.trim(),
                meetingDate: meetingDate,
                category: category,
                tags: tagsArr.map(t => t.trim()).filter(t => t !== ''),
                body: body.trim(),
            };
            notes.unshift(newNote);
            saveNotes();
            refreshUI();
        }

        function deleteNoteById(id) {
            if (!confirm('Delete this note?')) return;
            notes = notes.filter(n => n.id !== id);
            saveNotes();
            // if edit panel is open for this note, close it
            if (editPanel.classList.contains('hidden') === false && editId.value === id) {
                closeEditPanel();
            }
            refreshUI();
        }

        function updateNote(id, title, owner, meetingDate, category, tagsArr, body) {
            const note = notes.find(n => n.id === id);
            if (!note) return;
            note.title = title.trim();
            note.owner = owner.trim();
            note.meetingDate = meetingDate;
            note.category = category;
            note.tags = tagsArr.map(t => t.trim()).filter(t => t !== '');
            note.body = body.trim();
            saveNotes();
            closeEditPanel();
            refreshUI();
        }

        // ---- edit panel ----
        function openEditPanel(id) {
            const note = notes.find(n => n.id === id);
            if (!note) return;
            editId.value = note.id;
            document.getElementById('editTitle').value = note.title || '';
            document.getElementById('editOwner').value = note.owner || '';
            document.getElementById('editDate').value = note.meetingDate || '';
            document.getElementById('editCategory').value = note.category || 'reference';
            document.getElementById('editTags').value = (note.tags || []).join(', ');
            document.getElementById('editBody').value = note.body || '';
            editPanel.classList.remove('hidden');
            document.getElementById('editTitle').focus();
            window.scrollTo({ top: editPanel.offsetTop - 20, behavior: 'smooth' });
        }

        function closeEditPanel() {
            editPanel.classList.add('hidden');
            editForm.reset();
            editId.value = '';
        }

        // ---- refresh all ----
        function refreshUI() {
            populateFilterDropdowns();
            renderNotes();
            updateStats();
        }

        // ---- event listeners ----
        // add form
        addForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const title = document.getElementById('addTitle').value.trim();
            if (!title) {
                alert('Title is required.');
                return;
            }
            const owner = document.getElementById('addOwner').value;
            const date = document.getElementById('addDate').value;
            const category = document.getElementById('addCategory').value;
            const tagsRaw = document.getElementById('addTags').value;
            const tagsArr = tagsRaw.split(',').map(s => s.trim()).filter(s => s);
            const body = document.getElementById('addBody').value;
            addNote(title, owner, date, category, tagsArr, body);
            addForm.reset();
            document.getElementById('addTitle').focus();
        });

        // edit form
        editForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const id = editId.value;
            if (!id) return;
            const title = document.getElementById('editTitle').value.trim();
            if (!title) {
                alert('Title is required.');
                return;
            }
            const owner = document.getElementById('editOwner').value;
            const date = document.getElementById('editDate').value;
            const category = document.getElementById('editCategory').value;
            const tagsRaw = document.getElementById('editTags').value;
            const tagsArr = tagsRaw.split(',').map(s => s.trim()).filter(s => s);
            const body = document.getElementById('editBody').value;
            updateNote(id, title, owner, date, category, tagsArr, body);
        });

        cancelEditBtn.addEventListener('click', closeEditPanel);

        // filter changes
        filterOwner.addEventListener('change', renderNotes);
        filterTag.addEventListener('change', renderNotes);
        filterSearch.addEventListener('input', renderNotes);
        clearFiltersBtn.addEventListener('click', function() {
            filterOwner.value = '';
            filterTag.value = '';
            filterSearch.value = '';
            renderNotes();
        });

        // ---- init ----
        loadNotes();
        refreshUI();

        // if notes empty, add a demo note? optional: but keep clean.
        // ensure statistics strip updates with actual data.

        // keyboard: global ESC to close edit panel
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && !editPanel.classList.contains('hidden')) {
                closeEditPanel();
                e.preventDefault();
            }
        });

        // ensure focus visible
    })();
</script>
</body>
</html>
```
````
