# Generation Transcript

- Case: `en_code_fe_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 23.477478
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 226, "total_tokens": 6765, "completion_tokens": 6539, "prompt_tokens_details": null}`
- Prompt tokens: 226
- Completion tokens: 6539
- Total tokens: 6765

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
    <title>Meeting notes board · accessible team tool</title>
    <style>
        /* --- reset & base --- */
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
            background: #f5f7fb;
            color: #1e293b;
            line-height: 1.4;
            padding: 1.25rem;
        }
        h1, h2, h3 { font-weight: 600; line-height: 1.2; }
        h1 { font-size: 1.7rem; margin-bottom: 0.5rem; display: flex; gap: 0.5rem; flex-wrap: wrap; align-items: center; }
        h2 { font-size: 1.3rem; }
        a, button, input, select, textarea, [tabindex]:not([tabindex="-1"]) {
            &:focus-visible { outline: 3px solid #2563eb; outline-offset: 2px; border-radius: 3px; }
        }
        /* --- layout --- */
        .app-wrapper {
            max-width: 1280px; margin: 0 auto;
        }
        .stats-strip {
            background: white; padding: 0.75rem 1.25rem; border-radius: 16px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.04); margin-bottom: 1.5rem;
            display: flex; flex-wrap: wrap; gap: 1.8rem 2.5rem; align-items: center;
            font-size: 0.95rem;
        }
        .stats-item {
            display: flex; gap: 0.3rem 0.7rem; flex-wrap: wrap;
        }
        .stats-label { color: #475569; font-weight: 450; letter-spacing: 0.01em; }
        .stats-value { font-weight: 600; color: #0f172a; }
        .stat-highlight { background: #eef2ff; padding: 0 0.25rem; border-radius: 6px; }
        /* --- filters --- */
        .filters-panel {
            background: white; border-radius: 20px; padding: 1rem 1.2rem; margin-bottom: 1.8rem;
            box-shadow: 0 2px 6px rgba(0,0,0,0.03);
            display: flex; flex-wrap: wrap; gap: 0.9rem 1.2rem; align-items: flex-end;
        }
        .filter-group {
            display: flex; flex-direction: column; gap: 0.2rem 0.5rem; min-width: 130px;
        }
        .filter-group label {
            font-size: 0.75rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.03em; color: #475569;
        }
        .filter-group input, .filter-group select {
            padding: 0.45rem 0.6rem; border: 1px solid #cbd5e1; border-radius: 30px; font-size: 0.9rem;
            background: white; min-width: 140px;
        }
        .filter-group input { min-width: 160px; }
        .clear-filters {
            background: transparent; border: 1px dashed #94a3b8; border-radius: 30px;
            padding: 0.4rem 1rem; font-weight: 500; font-size: 0.8rem; cursor: pointer;
            transition: 0.1s;
        }
        .clear-filters:hover { background: #f1f5f9; border-color: #64748b; }
        .btn-add-note {
            background: #0f172a; color: white; border: none; border-radius: 40px;
            padding: 0.45rem 1.2rem; font-weight: 500; font-size: 0.9rem; cursor: pointer;
            margin-left: auto; white-space: nowrap; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .btn-add-note:hover { background: #1e293b; }
        /* --- card grid --- */
        .notes-grid {
            display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1.2rem; margin-top: 0.5rem;
        }
        /* --- note card --- */
        .note-card {
            background: white; border-radius: 24px; padding: 1.2rem 1.2rem 1rem;
            box-shadow: 0 6px 14px rgba(0,0,0,0.03), 0 2px 4px rgba(0,0,0,0.03);
            transition: box-shadow 0.1s; border: 1px solid #e9edf3;
            display: flex; flex-direction: column;
        }
        .note-card:hover { box-shadow: 0 10px 20px rgba(0,0,0,0.04); }
        .note-category {
            display: inline-block; background: #e9edf3; border-radius: 40px;
            padding: 0.2rem 0.8rem; font-size: 0.7rem; font-weight: 600; letter-spacing: 0.02em;
            align-self: flex-start; margin-bottom: 0.6rem; color: #1e293b;
        }
        .category-action { background: #fee2e2; color: #991b1b; }
        .category-decision { background: #dbeafe; color: #1e3a8a; }
        .category-reference { background: #e0f2fe; color: #0c4a6e; }
        .note-title {
            font-size: 1.2rem; font-weight: 600; margin-bottom: 0.25rem; word-break: break-word;
        }
        .note-meta {
            font-size: 0.8rem; color: #475569; margin-bottom: 0.5rem; display: flex; flex-wrap: wrap; gap: 0.25rem 1rem;
        }
        .note-meta strong { font-weight: 500; color: #1e293b; }
        .note-tags {
            display: flex; flex-wrap: wrap; gap: 0.3rem; margin: 0.6rem 0 0.7rem;
        }
        .tag-badge {
            background: #f1f5f9; border-radius: 40px; padding: 0.15rem 0.65rem; font-size: 0.7rem;
            color: #334155; border: 1px solid #e2e8f0;
        }
        .note-body {
            background: #fafbfc; padding: 0.7rem 0.8rem; border-radius: 16px; font-size: 0.85rem;
            margin: 0.3rem 0 0.8rem; white-space: pre-wrap; word-break: break-word;
            border: 1px solid #e9edf3; flex: 1;
        }
        .note-actions {
            display: flex; gap: 0.5rem; justify-content: flex-end; margin-top: 0.4rem;
        }
        .note-actions button {
            background: transparent; border: 1px solid #d1d9e6; border-radius: 30px;
            padding: 0.25rem 0.9rem; font-size: 0.8rem; cursor: pointer; font-weight: 450;
        }
        .btn-edit { color: #0f172a; }
        .btn-edit:hover { background: #f1f5f9; }
        .btn-delete { color: #b91c1c; border-color: #fecaca; }
        .btn-delete:hover { background: #fee2e2; }
        /* --- modal / form (inline) --- */
        .modal-overlay {
            position: fixed; inset: 0; background: rgba(0,0,0,0.35); display: flex;
            align-items: center; justify-content: center; z-index: 100;
            backdrop-filter: blur(2px);
        }
        .modal-panel {
            background: white; max-width: 550px; width: 90%; border-radius: 32px;
            padding: 1.8rem 1.5rem 1.5rem; box-shadow: 0 30px 40px rgba(0,0,0,0.2);
            max-height: 90vh; overflow-y: auto;
        }
        .modal-panel h2 { margin-bottom: 1.2rem; font-size: 1.4rem; }
        .form-row {
            display: flex; flex-direction: column; margin-bottom: 0.9rem;
        }
        .form-row label { font-weight: 500; font-size: 0.8rem; margin-bottom: 0.2rem; color: #1e293b; }
        .form-row input, .form-row select, .form-row textarea {
            padding: 0.5rem 0.7rem; border: 1px solid #cbd5e1; border-radius: 20px; font-size: 0.9rem;
            background: white;
        }
        .form-row textarea { min-height: 80px; resize: vertical; }
        .form-row-inline {
            display: flex; gap: 0.8rem; flex-wrap: wrap;
        }
        .form-row-inline .form-row { flex: 1; min-width: 120px; }
        .modal-buttons {
            display: flex; gap: 0.7rem; justify-content: flex-end; margin-top: 1.2rem;
        }
        .btn-primary {
            background: #0f172a; color: white; border: none; border-radius: 40px; padding: 0.45rem 1.5rem;
            font-weight: 500; cursor: pointer;
        }
        .btn-primary:hover { background: #1e293b; }
        .btn-secondary {
            background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 40px; padding: 0.45rem 1.2rem;
            cursor: pointer; font-weight: 450;
        }
        .btn-secondary:hover { background: #e2e8f0; }
        .hidden { display: none !important; }
        .empty-message {
            grid-column: 1 / -1; padding: 3rem 1rem; text-align: center; color: #64748b;
            background: white; border-radius: 40px; font-size: 1.1rem;
        }
        @media (max-width: 600px) {
            .notes-grid { grid-template-columns: 1fr; }
            .stats-strip { gap: 0.8rem 1.2rem; }
            .filters-panel { flex-direction: column; align-items: stretch; }
            .btn-add-note { margin-left: 0; width: 100%; }
        }
        /* small utilities */
        .mt-1 { margin-top: 0.5rem; }
        .mb-1 { margin-bottom: 0.5rem; }
        .flex { display: flex; align-items: center; }
        .gap-1 { gap: 0.5rem; }
    </style>
</head>
<body>
<div class="app-wrapper" role="application" aria-label="Meeting notes board">
    <header style="margin-bottom: 0.15rem;">
        <h1>📋 Meeting notes <span style="font-weight:400; font-size:1.1rem; color:#475569;">· team board</span></h1>
    </header>

    <!-- statistics strip -->
    <section class="stats-strip" aria-label="Statistics summary">
        <div class="stats-item"><span class="stats-label">Total notes</span><span class="stats-value" id="statTotal">0</span></div>
        <div class="stats-item"><span class="stats-label">⚡ Action required</span><span class="stats-value" id="statAction">0</span></div>
        <div class="stats-item"><span class="stats-label">👥 Unique owners</span><span class="stats-value" id="statOwners">0</span></div>
        <div class="stats-item"><span class="stats-label">🏷️ Most common tag</span><span class="stats-value" id="statTag">–</span></div>
    </section>

    <!-- filters + add -->
    <section class="filters-panel" aria-label="Filter notes">
        <div class="filter-group">
            <label for="filterOwner">Owner</label>
            <select id="filterOwner"><option value="">All owners</option></select>
        </div>
        <div class="filter-group">
            <label for="filterTag">Tag</label>
            <select id="filterTag"><option value="">All tags</option></select>
        </div>
        <div class="filter-group">
            <label for="filterSearch">Free text</label>
            <input id="filterSearch" type="search" placeholder="search title, body…" aria-label="Search notes by text">
        </div>
        <button class="clear-filters" id="clearFiltersBtn" type="button">⟳ clear filters</button>
        <button class="btn-add-note" id="addNoteBtn" type="button" aria-label="Add new meeting note">+ New note</button>
    </section>

    <!-- notes grid -->
    <div id="notesContainer" class="notes-grid" role="region" aria-label="Meeting notes cards">
        <!-- dynamic cards injected here -->
        <div class="empty-message">📌 No notes match filters. Add one!</div>
    </div>
</div>

<!-- modal (hidden by default) -->
<div id="noteModal" class="modal-overlay hidden" role="dialog" aria-modal="true" aria-labelledby="modalTitle">
    <div class="modal-panel">
        <h2 id="modalTitle">New meeting note</h2>
        <form id="noteForm" novalidate>
            <div class="form-row">
                <label for="noteTitle">Title *</label>
                <input id="noteTitle" type="text" required aria-required="true" placeholder="e.g. Sprint review">
            </div>
            <div class="form-row-inline">
                <div class="form-row">
                    <label for="noteOwner">Owner *</label>
                    <input id="noteOwner" type="text" required aria-required="true" placeholder="Alex">
                </div>
                <div class="form-row">
                    <label for="noteDate">Meeting date *</label>
                    <input id="noteDate" type="date" required aria-required="true">
                </div>
                <div class="form-row">
                    <label for="noteCategory">Category</label>
                    <select id="noteCategory">
                        <option value="action">Action required</option>
                        <option value="decision">Decision</option>
                        <option value="reference">Reference</option>
                    </select>
                </div>
            </div>
            <div class="form-row">
                <label for="noteTags">Tags (comma separated)</label>
                <input id="noteTags" type="text" placeholder="frontend, UX, sprint" aria-describedby="tagHelp">
                <span id="tagHelp" style="font-size:0.7rem; color:#64748b;">e.g. design, backend, retro</span>
            </div>
            <div class="form-row">
                <label for="noteBody">Note content</label>
                <textarea id="noteBody" rows="4" placeholder="Key points …"></textarea>
            </div>
            <div class="modal-buttons">
                <button type="button" id="cancelModalBtn" class="btn-secondary">Cancel</button>
                <button type="submit" id="saveNoteBtn" class="btn-primary">Save note</button>
            </div>
            <input id="editId" type="hidden" value="">
        </form>
    </div>
</div>

<script>
    (function() {
        // ----- Model & persistence -----
        let notes = [];
        const STORAGE_KEY = 'meeting_notes_board';

        function loadNotes() {
            try {
                const stored = localStorage.getItem(STORAGE_KEY);
                if (stored) {
                    const parsed = JSON.parse(stored);
                    if (Array.isArray(parsed)) notes = parsed;
                    else notes = [];
                } else {
                    // seed demo notes
                    notes = [
                        { id: 'n1', title: 'Sprint retro', owner: 'Emma', date: '2025-04-01', category: 'reference', tags: ['retro', 'sprint'], body: 'Action items: reduce cycle time, improve testing.' },
                        { id: 'n2', title: 'Design review', owner: 'Liam', date: '2025-03-28', category: 'decision', tags: ['design', 'UX'], body: 'Approved new component library.' },
                        { id: 'n3', title: 'Bug triage', owner: 'Emma', date: '2025-04-05', category: 'action', tags: ['bug', 'urgent'], body: 'Fix login crash on Safari.' },
                    ];
                    save();
                }
            } catch (e) { notes = []; }
            // ensure each note has tags array
            notes = notes.map(n => ({ ...n, tags: Array.isArray(n.tags) ? n.tags : [] }));
        }

        function save() {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(notes));
        }

        // ----- helpers -----
        function generateId() { return Date.now().toString(36) + Math.random().toString(36).slice(2,5); }

        // ----- stats & filters extracts -----
        function computeStats() {
            const total = notes.length;
            const actionCount = notes.filter(n => n.category === 'action').length;
            const uniqueOwners = new Set(notes.map(n => n.owner.trim().toLowerCase())).size;
            // most common tag
            const tagFreq = {};
            notes.forEach(n => (n.tags || []).forEach(t => { const key = t.trim().toLowerCase(); if(key) tagFreq[key] = (tagFreq[key]||0)+1; }));
            let mostCommon = '–';
            let maxCount = 0;
            for (const [tag, count] of Object.entries(tagFreq)) {
                if (count > maxCount) { maxCount = count; mostCommon = tag; }
            }
            if (mostCommon !== '–') mostCommon = mostCommon.charAt(0).toUpperCase() + mostCommon.slice(1);
            return { total, actionCount, uniqueOwners, mostCommon };
        }

        function getUniqueOwners() { return [...new Set(notes.map(n => n.owner.trim()))].filter(Boolean).sort(); }
        function getUniqueTags() {
            const set = new Set();
            notes.forEach(n => (n.tags || []).forEach(t => { const s = t.trim(); if(s) set.add(s); }));
            return [...set].sort();
        }

        // ----- render stats & filters & grid -----
        const container = document.getElementById('notesContainer');
        const statTotal = document.getElementById('statTotal');
        const statAction = document.getElementById('statAction');
        const statOwners = document.getElementById('statOwners');
        const statTag = document.getElementById('statTag');

        const filterOwner = document.getElementById('filterOwner');
        const filterTag = document.getElementById('filterTag');
        const filterSearch = document.getElementById('filterSearch');
        const clearFiltersBtn = document.getElementById('clearFiltersBtn');

        function renderAll() {
            // stats
            const stats = computeStats();
            statTotal.textContent = stats.total;
            statAction.textContent = stats.actionCount;
            statOwners.textContent = stats.uniqueOwners;
            statTag.textContent = stats.mostCommon;

            // populate selector options (preserve selected)
            const currentOwner = filterOwner.value;
            const currentTag = filterTag.value;
            // owners
            const owners = getUniqueOwners();
            filterOwner.innerHTML = '<option value="">All owners</option>' + owners.map(o => `<option value="${o}">${o}</option>`).join('');
            filterOwner.value = currentOwner && owners.includes(currentOwner) ? currentOwner : '';
            // tags
            const tags = getUniqueTags();
            filterTag.innerHTML = '<option value="">All tags</option>' + tags.map(t => `<option value="${t}">${t}</option>`).join('');
            filterTag.value = currentTag && tags.includes(currentTag) ? currentTag : '';

            // filter notes & render grid
            const filtered = filterNotes();
            renderCards(filtered);
        }

        function filterNotes() {
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
                    const inTitle = n.title.toLowerCase().includes(search);
                    const inBody = (n.body || '').toLowerCase().includes(search);
                    const inOwner = n.owner.toLowerCase().includes(search);
                    const inTags = (n.tags || []).some(t => t.toLowerCase().includes(search));
                    if (!(inTitle || inBody || inOwner || inTags)) return false;
                }
                return true;
            });
        }

        function renderCards(filteredNotes) {
            if (!filteredNotes.length) {
                container.innerHTML = `<div class="empty-message">📌 No notes match filters. Add one!</div>`;
                return;
            }
            const cards = filteredNotes.map(n => {
                const categoryClass = n.category === 'action' ? 'category-action' : n.category === 'decision' ? 'category-decision' : 'category-reference';
                const categoryLabel = n.category === 'action' ? '⚡ Action required' : n.category === 'decision' ? '✅ Decision' : '📎 Reference';
                const tagsHtml = (n.tags || []).filter(Boolean).map(t => `<span class="tag-badge">${escapeHtml(t)}</span>`).join('');
                const bodyExcerpt = escapeHtml(n.body || '');
                return `
                    <div class="note-card" role="article" data-note-id="${escapeHtml(n.id)}">
                        <span class="note-category ${categoryClass}">${categoryLabel}</span>
                        <div class="note-title">${escapeHtml(n.title)}</div>
                        <div class="note-meta">
                            <span><strong>Owner:</strong> ${escapeHtml(n.owner)}</span>
                            <span><strong>Date:</strong> ${escapeHtml(n.date)}</span>
                        </div>
                        ${tagsHtml ? `<div class="note-tags">${tagsHtml}</div>` : ''}
                        <div class="note-body">${bodyExcerpt}</div>
                        <div class="note-actions">
                            <button class="btn-edit" data-edit-id="${escapeHtml(n.id)}" type="button" aria-label="Edit note: ${escapeHtml(n.title)}">✎ Edit</button>
                            <button class="btn-delete" data-delete-id="${escapeHtml(n.id)}" type="button" aria-label="Delete note: ${escapeHtml(n.title)}">🗑 Delete</button>
                        </div>
                    </div>
                `;
            }).join('');
            container.innerHTML = cards;

            // attach event listeners to edit/delete buttons
            container.querySelectorAll('.btn-edit').forEach(btn => btn.addEventListener('click', (e) => {
                const id = btn.dataset.editId;
                const note = notes.find(n => n.id === id);
                if (note) openModal(note);
            }));
            container.querySelectorAll('.btn-delete').forEach(btn => btn.addEventListener('click', (e) => {
                const id = btn.dataset.deleteId;
                if (confirm('Delete this note permanently?')) {
                    notes = notes.filter(n => n.id !== id);
                    save();
                    renderAll();
                }
            }));
        }

        function escapeHtml(str) {
            if (!str) return '';
            return str.replace(/[&<>"']/g, function(m) {
                if (m === '&') return '&amp;'; if (m === '<') return '&lt;'; if (m === '>') return '&gt;';
                if (m === '"') return '&quot;'; if (m === "'") return '&#039;';
                return m;
            });
        }

        // ----- modal logic -----
        const modal = document.getElementById('noteModal');
        const modalTitle = document.getElementById('modalTitle');
        const form = document.getElementById('noteForm');
        const noteTitle = document.getElementById('noteTitle');
        const noteOwner = document.getElementById('noteOwner');
        const noteDate = document.getElementById('noteDate');
        const noteCategory = document.getElementById('noteCategory');
        const noteTags = document.getElementById('noteTags');
        const noteBody = document.getElementById('noteBody');
        const editIdInput = document.getElementById('editId');
        const cancelModalBtn = document.getElementById('cancelModalBtn');
        const addNoteBtn = document.getElementById('addNoteBtn');

        function openModal(note = null) {
            modal.classList.remove('hidden');
            if (note) {
                modalTitle.textContent = 'Edit note';
                noteTitle.value = note.title || '';
                noteOwner.value = note.owner || '';
                noteDate.value = note.date || '';
                noteCategory.value = note.category || 'action';
                noteTags.value = (note.tags || []).join(', ');
                noteBody.value = note.body || '';
                editIdInput.value = note.id;
            } else {
                modalTitle.textContent = 'New meeting note';
                form.reset();
                editIdInput.value = '';
                const today = new Date().toISOString().slice(0,10);
                noteDate.value = today;
                noteCategory.value = 'action';
            }
            // focus first input
            setTimeout(() => noteTitle.focus(), 50);
        }

        function closeModal() {
            modal.classList.add('hidden');
            form.reset();
            editIdInput.value = '';
        }

        // cancel
        cancelModalBtn.addEventListener('click', closeModal);
        // overlay click to close (only if click on overlay)
        modal.addEventListener('click', (e) => { if (e.target === modal) closeModal(); });
        // escape
        document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !modal.classList.contains('hidden')) closeModal(); });

        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const title = noteTitle.value.trim();
            const owner = noteOwner.value.trim();
            const date = noteDate.value;
            if (!title || !owner || !date) {
                alert('Title, owner and date are required.');
                return;
            }
            const category = noteCategory.value || 'action';
            const tagsRaw = noteTags.value.trim();
            const tags = tagsRaw ? tagsRaw.split(',').map(t => t.trim()).filter(Boolean) : [];
            const body = noteBody.value.trim();
            const editId = editIdInput.value;

            if (editId) {
                // edit existing
                const idx = notes.findIndex(n => n.id === editId);
                if (idx !== -1) {
                    notes[idx] = { ...notes[idx], title, owner, date, category, tags, body };
                } else { alert('Note not found, please refresh.'); closeModal(); return; }
            } else {
                // new note
                const newNote = {
                    id: generateId(),
                    title,
                    owner,
                    date,
                    category,
                    tags,
                    body
                };
                notes.push(newNote);
            }
            save();
            closeModal();
            renderAll();
        });

        // add button
        addNoteBtn.addEventListener('click', () => openModal(null));

        // filter listeners
        filterOwner.addEventListener('change', renderAll);
        filterTag.addEventListener('change', renderAll);
        filterSearch.addEventListener('input', renderAll);
        clearFiltersBtn.addEventListener('click', () => {
            filterOwner.value = '';
            filterTag.value = '';
            filterSearch.value = '';
            renderAll();
        });

        // init
        loadNotes();
        renderAll();
    })();
</script>
</body>
</html>
```
````
