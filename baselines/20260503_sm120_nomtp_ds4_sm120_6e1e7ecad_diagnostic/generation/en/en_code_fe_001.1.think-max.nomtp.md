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
- Elapsed seconds: 104.788679
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 226, "total_tokens": 6822, "completion_tokens": 6596, "prompt_tokens_details": null}`
- Prompt tokens: 226
- Completion tokens: 6596
- Total tokens: 6822

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
    <title>Meeting Notes Board</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
            background: #f4f6fb;
            padding: 1.2rem;
            min-height: 100vh;
            color: #1e293b;
        }
        .app {
            max-width: 1280px;
            margin: 0 auto;
        }

        /* HEADER + STATS */
        .app-header {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.2rem;
        }
        .app-header h1 {
            font-weight: 600;
            font-size: 1.8rem;
            letter-spacing: -0.02em;
        }
        .stats-strip {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem 1.6rem;
            background: white;
            padding: 0.65rem 1.2rem;
            border-radius: 40px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.04);
            font-size: 0.9rem;
        }
        .stats-strip span {
            display: inline-flex;
            align-items: baseline;
            gap: 0.3rem;
        }
        .stat-value {
            font-weight: 700;
            color: #0f172a;
        }
        .stat-label {
            color: #475569;
        }

        /* FILTERS ROW */
        .filters {
            display: flex;
            flex-wrap: wrap;
            gap: 0.8rem 1.2rem;
            background: white;
            padding: 1rem 1.2rem;
            border-radius: 24px;
            margin-bottom: 1.8rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            align-items: flex-end;
        }
        .filter-group {
            display: flex;
            flex-direction: column;
            min-width: 130px;
            flex: 1 0 auto;
        }
        .filter-group label {
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.02em;
            color: #475569;
            margin-bottom: 0.2rem;
        }
        .filter-group input,
        .filter-group select {
            background: #f8fafc;
            border: 1px solid #d1d5db;
            border-radius: 30px;
            padding: 0.45rem 0.9rem;
            font-size: 0.9rem;
            font-family: inherit;
            outline: none;
            transition: 0.15s;
        }
        .filter-group input:focus,
        .filter-group select:focus {
            border-color: #2563eb;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.25);
        }
        .filter-group input::placeholder {
            color: #94a3b8;
        }

        /* ADD NOTE TRIGGER */
        .add-area {
            display: flex;
            justify-content: flex-end;
            margin-bottom: 1.5rem;
        }
        .add-btn {
            background: #2563eb;
            color: white;
            border: none;
            border-radius: 40px;
            padding: 0.6rem 1.6rem;
            font-weight: 600;
            font-size: 0.95rem;
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            cursor: pointer;
            box-shadow: 0 2px 6px rgba(37, 99, 235, 0.2);
            transition: background 0.15s;
        }
        .add-btn:hover {
            background: #1d4ed8;
        }
        .add-btn:focus-visible {
            outline: 2px solid #1e293b;
            outline-offset: 2px;
        }

        /* NOTE GRID */
        .notes-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1.2rem;
        }

        /* CARD */
        .note-card {
            background: white;
            border-radius: 24px;
            padding: 1.2rem 1.4rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            transition: 0.1s ease;
            border-left: 6px solid #e2e8f0;
            word-break: break-word;
        }
        .note-card[data-type="action"] {
            border-left-color: #ef4444;
        }
        .note-card[data-type="decision"] {
            border-left-color: #f59e0b;
        }
        .note-card[data-type="reference"] {
            border-left-color: #3b82f6;
        }
        .note-card[data-type=""] {
            border-left-color: #cbd5e1;
        }

        .card-header {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: flex-start;
            gap: 0.3rem 0.6rem;
            margin-bottom: 0.4rem;
        }
        .card-title {
            font-weight: 700;
            font-size: 1.2rem;
            line-height: 1.3;
        }
        .card-type-badge {
            font-size: 0.6rem;
            font-weight: 700;
            text-transform: uppercase;
            background: #e2e8f0;
            padding: 0.2rem 0.7rem;
            border-radius: 30px;
            letter-spacing: 0.02em;
            white-space: nowrap;
        }
        .note-card[data-type="action"] .card-type-badge {
            background: #fee2e2;
            color: #b91c1c;
        }
        .note-card[data-type="decision"] .card-type-badge {
            background: #fef3c7;
            color: #92400e;
        }
        .note-card[data-type="reference"] .card-type-badge {
            background: #dbeafe;
            color: #1e40af;
        }

        .card-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 0.8rem 1rem;
            font-size: 0.8rem;
            color: #475569;
            margin: 0.5rem 0 0.2rem;
        }
        .card-meta span {
            display: inline-flex;
            align-items: center;
            gap: 0.2rem;
        }
        .tag-list {
            display: flex;
            flex-wrap: wrap;
            gap: 0.3rem 0.5rem;
            margin: 0.5rem 0 0.2rem;
        }
        .tag {
            background: #eef2ff;
            color: #4338ca;
            border-radius: 40px;
            padding: 0.1rem 0.7rem;
            font-size: 0.7rem;
            font-weight: 500;
        }
        .card-body {
            margin: 0.6rem 0 0.8rem;
            font-size: 0.9rem;
            line-height: 1.5;
            color: #1e293b;
            white-space: pre-wrap;
        }
        .card-actions {
            display: flex;
            flex-wrap: wrap;
            gap: 0.6rem;
            margin-top: 0.6rem;
            border-top: 1px solid #f1f5f9;
            padding-top: 0.7rem;
        }
        .card-actions button {
            background: transparent;
            border: 1px solid #d1d5db;
            border-radius: 40px;
            padding: 0.25rem 0.9rem;
            font-size: 0.75rem;
            font-weight: 500;
            cursor: pointer;
            transition: 0.1s;
            color: #1e293b;
        }
        .card-actions button:hover {
            background: #f1f5f9;
        }
        .card-actions button:focus-visible {
            outline: 2px solid #2563eb;
            outline-offset: 2px;
        }
        .delete-btn {
            color: #b91c1c !important;
            border-color: #fecaca !important;
        }
        .delete-btn:hover {
            background: #fee2e2 !important;
        }

        /* MODAL (Add/Edit) */
        .modal-overlay {
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.3);
            backdrop-filter: blur(2px);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            padding: 1rem;
        }
        .modal {
            background: white;
            border-radius: 32px;
            max-width: 550px;
            width: 100%;
            padding: 1.8rem 1.5rem 1.5rem;
            box-shadow: 0 20px 40px rgba(0,0,0,0.12);
            max-height: 90vh;
            overflow-y: auto;
        }
        .modal h2 {
            font-size: 1.5rem;
            margin-bottom: 1.2rem;
        }
        .modal-field {
            display: flex;
            flex-direction: column;
            margin-bottom: 0.9rem;
        }
        .modal-field label {
            font-weight: 600;
            font-size: 0.8rem;
            margin-bottom: 0.2rem;
            color: #334155;
        }
        .modal-field input,
        .modal-field textarea,
        .modal-field select {
            background: #f8fafc;
            border: 1px solid #d1d5db;
            border-radius: 30px;
            padding: 0.5rem 0.9rem;
            font-family: inherit;
            font-size: 0.9rem;
            outline: none;
        }
        .modal-field textarea {
            border-radius: 20px;
            resize: vertical;
            min-height: 80px;
        }
        .modal-field input:focus,
        .modal-field textarea:focus,
        .modal-field select:focus {
            border-color: #2563eb;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2);
        }
        .modal-actions {
            display: flex;
            flex-wrap: wrap;
            justify-content: flex-end;
            gap: 0.7rem;
            margin-top: 1.3rem;
        }
        .modal-actions button {
            padding: 0.5rem 1.4rem;
            border-radius: 40px;
            font-weight: 600;
            border: 1px solid transparent;
            cursor: pointer;
            transition: 0.1s;
        }
        .modal-actions .btn-secondary {
            background: #f1f5f9;
            color: #1e293b;
            border-color: #d1d5db;
        }
        .modal-actions .btn-primary {
            background: #2563eb;
            color: white;
            border-color: #2563eb;
        }
        .modal-actions button:focus-visible {
            outline: 2px solid #1e293b;
            outline-offset: 2px;
        }

        .visually-hidden:not(:focus):not(:active) {
            position: absolute;
            width: 1px;
            height: 1px;
            margin: -1px;
            padding: 0;
            overflow: hidden;
            clip: rect(0,0,0,0);
            border: 0;
        }

        /* RESPONSIVE */
        @media (max-width: 640px) {
            body { padding: 0.8rem; }
            .app-header { flex-direction: column; align-items: stretch; gap: 0.6rem; }
            .stats-strip { border-radius: 30px; justify-content: space-around; }
            .filters { flex-direction: column; align-items: stretch; }
            .filter-group { min-width: unset; }
            .notes-grid {
                grid-template-columns: 1fr;
            }
            .modal { padding: 1.5rem 1.2rem; }
        }
        @media (max-width: 480px) {
            .stats-strip { font-size: 0.75rem; gap: 0.4rem 0.8rem; flex-wrap: wrap; }
        }
    </style>
</head>
<body>
<div class="app" role="application" aria-label="Meeting notes board">
    <!-- HEADER + STATS -->
    <header class="app-header">
        <h1>📋 Meeting Notes</h1>
        <div class="stats-strip" id="statsStrip" role="group" aria-label="Statistics">
            <span><span class="stat-value" id="totalNotes">0</span> <span class="stat-label">total</span></span>
            <span><span class="stat-value" id="actionCount">0</span> <span class="stat-label">⚠️ actions</span></span>
            <span><span class="stat-value" id="uniqueOwners">0</span> <span class="stat-label">owners</span></span>
            <span><span class="stat-value" id="mostCommonTag">-</span> <span class="stat-label">top tag</span></span>
        </div>
    </header>

    <!-- FILTERS -->
    <section class="filters" aria-label="Filter notes">
        <div class="filter-group">
            <label for="filterOwner">Owner</label>
            <select id="filterOwner">
                <option value="">All owners</option>
            </select>
        </div>
        <div class="filter-group">
            <label for="filterTag">Tag</label>
            <select id="filterTag">
                <option value="">All tags</option>
            </select>
        </div>
        <div class="filter-group">
            <label for="filterSearch">Search (title/body)</label>
            <input type="search" id="filterSearch" placeholder="free text..." autocomplete="off">
        </div>
    </section>

    <!-- ADD BUTTON -->
    <div class="add-area">
        <button class="add-btn" id="addNoteBtn" aria-label="Add new meeting note">+ Add Note</button>
    </div>

    <!-- NOTES GRID -->
    <div class="notes-grid" id="notesGrid" role="list" aria-label="Meeting notes cards"></div>
</div>

<!-- MODAL (hidden by default) -->
<div id="modalContainer" class="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="modalTitle" style="display:none;">
    <div class="modal">
        <h2 id="modalTitle">New Note</h2>
        <form id="noteForm" novalidate>
            <div class="modal-field">
                <label for="noteTitle">Title *</label>
                <input type="text" id="noteTitle" required maxlength="120" placeholder="e.g. Sprint review">
            </div>
            <div class="modal-field">
                <label for="noteOwner">Owner</label>
                <input type="text" id="noteOwner" placeholder="e.g. Alex">
            </div>
            <div class="modal-field">
                <label for="noteDate">Meeting date</label>
                <input type="date" id="noteDate">
            </div>
            <div class="modal-field">
                <label for="noteTags">Tags (comma separated)</label>
                <input type="text" id="noteTags" placeholder="e.g. design, frontend">
            </div>
            <div class="modal-field">
                <label for="noteType">Type</label>
                <select id="noteType">
                    <option value="">— Select —</option>
                    <option value="action">Action Required</option>
                    <option value="decision">Decision</option>
                    <option value="reference">Reference</option>
                </select>
            </div>
            <div class="modal-field">
                <label for="noteBody">Body</label>
                <textarea id="noteBody" rows="3" placeholder="Details..."></textarea>
            </div>
            <div class="modal-actions">
                <button type="button" class="btn-secondary" id="cancelModal">Cancel</button>
                <button type="submit" class="btn-primary" id="saveNoteBtn">Save</button>
            </div>
            <input type="hidden" id="editId" value="">
        </form>
    </div>
</div>

<script>
    (function() {
        // --- state ---
        let notes = [];
        let filteredNotes = [];

        // DOM refs
        const grid = document.getElementById('notesGrid');
        const statsStrip = document.getElementById('statsStrip');
        const totalEl = document.getElementById('totalNotes');
        const actionEl = document.getElementById('actionCount');
        const ownersEl = document.getElementById('uniqueOwners');
        const topTagEl = document.getElementById('mostCommonTag');

        const filterOwner = document.getElementById('filterOwner');
        const filterTag = document.getElementById('filterTag');
        const filterSearch = document.getElementById('filterSearch');

        const modal = document.getElementById('modalContainer');
        const modalTitle = document.getElementById('modalTitle');
        const form = document.getElementById('noteForm');
        const editIdInput = document.getElementById('editId');
        const titleInput = document.getElementById('noteTitle');
        const ownerInput = document.getElementById('noteOwner');
        const dateInput = document.getElementById('noteDate');
        const tagsInput = document.getElementById('noteTags');
        const typeSelect = document.getElementById('noteType');
        const bodyInput = document.getElementById('noteBody');
        const cancelBtn = document.getElementById('cancelModal');
        const addNoteBtn = document.getElementById('addNoteBtn');

        // --- helpers ---
        function saveToStorage() {
            localStorage.setItem('meetingNotes', JSON.stringify(notes));
        }

        function loadFromStorage() {
            try {
                const data = localStorage.getItem('meetingNotes');
                if (data) notes = JSON.parse(data);
                else notes = [];
            } catch { notes = []; }
        }

        function generateId() {
            return Date.now().toString(36) + Math.random().toString(36).slice(2,6);
        }

        // --- statistics ---
        function computeStats() {
            const total = notes.length;
            const actionCount = notes.filter(n => n.type === 'action').length;
            const owners = new Set(notes.map(n => n.owner?.trim().toLowerCase()).filter(o => o));
            const uniqueOwners = owners.size;

            // most common tag
            const tagFreq = {};
            notes.forEach(n => {
                (n.tags || []).forEach(t => {
                    const key = t.trim().toLowerCase();
                    if (key) tagFreq[key] = (tagFreq[key] || 0) + 1;
                });
            });
            let mostCommon = '-';
            let maxCount = 0;
            for (const [tag, cnt] of Object.entries(tagFreq)) {
                if (cnt > maxCount) { maxCount = cnt; mostCommon = tag; }
            }
            if (mostCommon !== '-') {
                // capitalize first letter
                mostCommon = mostCommon.charAt(0).toUpperCase() + mostCommon.slice(1);
            }

            totalEl.textContent = total;
            actionEl.textContent = actionCount;
            ownersEl.textContent = uniqueOwners;
            topTagEl.textContent = mostCommon;
        }

        // --- render grid & filter dropdowns ---
        function populateFilterOptions() {
            const ownerSet = new Set();
            const tagSet = new Set();
            notes.forEach(n => {
                if (n.owner?.trim()) ownerSet.add(n.owner.trim());
                (n.tags || []).forEach(t => { if (t.trim()) tagSet.add(t.trim()); });
            });

            // preserve current selection if possible
            const curOwner = filterOwner.value;
            const curTag = filterTag.value;

            filterOwner.innerHTML = '<option value="">All owners</option>';
            [...ownerSet].sort().forEach(o => {
                filterOwner.innerHTML += `<option value="${o.replace(/"/g, '&quot;')}">${o}</option>`;
            });
            filterTag.innerHTML = '<option value="">All tags</option>';
            [...tagSet].sort().forEach(t => {
                filterTag.innerHTML += `<option value="${t.replace(/"/g, '&quot;')}">${t}</option>`;
            });

            if ([...ownerSet].includes(curOwner)) filterOwner.value = curOwner;
            else filterOwner.value = '';
            if ([...tagSet].includes(curTag)) filterTag.value = curTag;
            else filterTag.value = '';
        }

        function filterNotes() {
            const ownerVal = filterOwner.value.trim().toLowerCase();
            const tagVal = filterTag.value.trim().toLowerCase();
            const searchVal = filterSearch.value.trim().toLowerCase();

            filteredNotes = notes.filter(n => {
                if (ownerVal && (n.owner || '').trim().toLowerCase() !== ownerVal) return false;
                if (tagVal) {
                    const noteTags = (n.tags || []).map(t => t.trim().toLowerCase());
                    if (!noteTags.includes(tagVal)) return false;
                }
                if (searchVal) {
                    const title = (n.title || '').toLowerCase();
                    const body = (n.body || '').toLowerCase();
                    if (!title.includes(searchVal) && !body.includes(searchVal)) return false;
                }
                return true;
            });
        }

        function renderCards() {
            filterNotes();
            if (filteredNotes.length === 0) {
                grid.innerHTML = `<div style="grid-column:1/-1; text-align:center; padding:2rem; color:#64748b;">No notes match filters</div>`;
                return;
            }
            let html = '';
            filteredNotes.forEach(n => {
                const typeClass = n.type || '';
                const cardType = n.type || '';
                let typeLabel = '';
                if (n.type === 'action') typeLabel = 'Action';
                else if (n.type === 'decision') typeLabel = 'Decision';
                else if (n.type === 'reference') typeLabel = 'Reference';

                const tags = (n.tags || []).filter(t => t.trim()).map(t => `<span class="tag">${t.trim()}</span>`).join('');

                html += `
                    <div class="note-card" data-type="${typeClass}" role="listitem">
                        <div class="card-header">
                            <span class="card-title">${escapeHtml(n.title || 'Untitled')}</span>
                            ${typeLabel ? `<span class="card-type-badge">${typeLabel}</span>` : ''}
                        </div>
                        <div class="card-meta">
                            ${n.owner ? `<span>👤 ${escapeHtml(n.owner)}</span>` : ''}
                            ${n.date ? `<span>📅 ${escapeHtml(n.date)}</span>` : ''}
                        </div>
                        ${tags ? `<div class="tag-list">${tags}</div>` : ''}
                        <div class="card-body">${escapeHtml(n.body || '')}</div>
                        <div class="card-actions">
                            <button data-id="${n.id}" class="edit-btn">✎ Edit</button>
                            <button data-id="${n.id}" class="delete-btn">🗑 Delete</button>
                        </div>
                    </div>
                `;
            });
            grid.innerHTML = html;

            // Attach event listeners to edit/delete buttons
            grid.querySelectorAll('.edit-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const id = btn.dataset.id;
                    openEditModal(id);
                });
            });
            grid.querySelectorAll('.delete-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const id = btn.dataset.id;
                    deleteNote(id);
                });
            });
        }

        function escapeHtml(text) {
            if (!text) return '';
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        function refreshUI() {
            populateFilterOptions();
            computeStats();
            renderCards();
        }

        // --- CRUD ---
        function addNote(noteData) {
            const note = {
                id: generateId(),
                title: noteData.title.trim() || 'Untitled',
                owner: noteData.owner.trim() || '',
                date: noteData.date || '',
                tags: noteData.tags.split(',').map(s => s.trim()).filter(s => s),
                type: noteData.type || '',
                body: noteData.body.trim() || '',
            };
            notes.push(note);
            saveToStorage();
            refreshUI();
        }

        function updateNote(id, noteData) {
            const idx = notes.findIndex(n => n.id === id);
            if (idx === -1) return;
            notes[idx] = {
                ...notes[idx],
                title: noteData.title.trim() || 'Untitled',
                owner: noteData.owner.trim() || '',
                date: noteData.date || '',
                tags: noteData.tags.split(',').map(s => s.trim()).filter(s => s),
                type: noteData.type || '',
                body: noteData.body.trim() || '',
            };
            saveToStorage();
            refreshUI();
        }

        function deleteNote(id) {
            if (!confirm('Delete this note permanently?')) return;
            notes = notes.filter(n => n.id !== id);
            saveToStorage();
            refreshUI();
        }

        // --- modal ---
        function openNewModal() {
            modalTitle.textContent = 'New Note';
            form.reset();
            editIdInput.value = '';
            document.getElementById('noteDate').value = new Date().toISOString().slice(0,10);
            modal.style.display = 'flex';
            titleInput.focus();
        }

        function openEditModal(id) {
            const note = notes.find(n => n.id === id);
            if (!note) return;
            modalTitle.textContent = 'Edit Note';
            editIdInput.value = id;
            titleInput.value = note.title || '';
            ownerInput.value = note.owner || '';
            dateInput.value = note.date || '';
            tagsInput.value = (note.tags || []).join(', ');
            typeSelect.value = note.type || '';
            bodyInput.value = note.body || '';
            modal.style.display = 'flex';
            titleInput.focus();
        }

        function closeModal() {
            modal.style.display = 'none';
            form.reset();
            editIdInput.value = '';
        }

        // --- modal save ---
        function handleFormSubmit(e) {
            e.preventDefault();
            const title = titleInput.value.trim();
            if (!title) {
                alert('Title is required.');
                titleInput.focus();
                return;
            }
            const formData = {
                title,
                owner: ownerInput.value.trim(),
                date: dateInput.value,
                tags: tagsInput.value,
                type: typeSelect.value,
                body: bodyInput.value,
            };
            const editId = editIdInput.value;
            if (editId) {
                updateNote(editId, formData);
            } else {
                addNote(formData);
            }
            closeModal();
        }

        // --- initial load & events ---
        loadFromStorage();

        // attach events
        filterOwner.addEventListener('change', renderCards);
        filterTag.addEventListener('change', renderCards);
        filterSearch.addEventListener('input', renderCards);

        addNoteBtn.addEventListener('click', openNewModal);
        cancelBtn.addEventListener('click', closeModal);
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeModal();
        });
        form.addEventListener('submit', handleFormSubmit);

        // close on Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal.style.display === 'flex') closeModal();
        });

        // initial render
        refreshUI();

        // if no notes, add demo samples
        if (notes.length === 0) {
            const demo = [
                { title: 'Q2 planning', owner: 'Alice', date: '2025-04-10', tags: 'planning, design', type: 'decision', body: 'Decided to move to new design system.' },
                { title: 'Bug triage', owner: 'Bob', date: '2025-04-08', tags: 'bug, urgent', type: 'action', body: 'Fix login issue (P1).' },
                { title: 'Retro notes', owner: 'Carol', date: '2025-04-01', tags: 'retro', type: 'reference', body: 'Action items from retro.' },
            ];
            demo.forEach(d => addNote(d));
        }
    })();
</script>
</body>
</html>
```
````
