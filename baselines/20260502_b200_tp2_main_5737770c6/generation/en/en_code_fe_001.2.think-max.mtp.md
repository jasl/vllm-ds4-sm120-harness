# Generation Transcript

- Case: `en_code_fe_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 22.611364
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 226, "total_tokens": 6525, "completion_tokens": 6299, "prompt_tokens_details": null}`
- Prompt tokens: 226
- Completion tokens: 6299
- Total tokens: 6525

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
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
            background: #f8fafc;
            color: #0b1b2b;
            padding: 1.5rem;
            min-height: 100vh;
        }
        #app {
            max-width: 1400px;
            margin: 0 auto;
        }
        h1 {
            font-size: 1.8rem;
            font-weight: 600;
            letter-spacing: -0.01em;
            margin-top: 0.2rem;
            margin-bottom: 1.5rem;
            color: #0b2b3b;
        }
        .stats-strip {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem 2rem;
            background: white;
            padding: 0.9rem 1.6rem;
            border-radius: 24px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
            margin-bottom: 1.8rem;
            align-items: center;
            font-size: 0.95rem;
            border: 1px solid #e2e8f0;
        }
        .stat-item {
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }
        .stat-label {
            color: #475569;
            font-weight: 450;
        }
        .stat-value {
            font-weight: 600;
            background: #eef2f6;
            padding: 0.1rem 0.7rem;
            border-radius: 30px;
            color: #0b2b3b;
        }
        .filters {
            display: flex;
            flex-wrap: wrap;
            gap: 0.8rem 1.2rem;
            background: white;
            padding: 1.2rem 1.6rem;
            border-radius: 28px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.02);
            margin-bottom: 2rem;
            border: 1px solid #e2edf2;
            align-items: center;
        }
        .filter-group {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0.4rem 0.8rem;
        }
        .filter-group label {
            font-size: 0.85rem;
            font-weight: 500;
            color: #1e3a5a;
        }
        .filter-group input, .filter-group select {
            padding: 0.45rem 0.9rem;
            border-radius: 40px;
            border: 1px solid #cbd5e1;
            background: white;
            font-size: 0.9rem;
            min-width: 130px;
            transition: 0.15s;
        }
        .filter-group input:focus, .filter-group select:focus {
            outline: 2px solid #1d6f9c;
            outline-offset: 2px;
            border-color: transparent;
        }
        .btn-add-note {
            background: #1d4a6b;
            color: white;
            border: none;
            padding: 0.5rem 1.5rem;
            border-radius: 40px;
            font-weight: 500;
            font-size: 0.95rem;
            cursor: pointer;
            margin-left: auto;
            transition: background 0.1s;
        }
        .btn-add-note:hover, .btn-add-note:focus-visible {
            background: #133b52;
            outline: 2px solid #7ab6d9;
        }
        .btn-add-note:focus-visible {
            outline-offset: 2px;
        }
        .note-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.2rem;
        }
        @media (max-width: 680px) {
            .note-grid {
                grid-template-columns: 1fr;
            }
        }
        .note-card {
            background: white;
            border-radius: 28px;
            padding: 1.3rem 1.4rem;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.02);
            border: 1px solid #e2eaf0;
            transition: 0.1s;
            display: flex;
            flex-direction: column;
            gap: 0.6rem;
            word-wrap: break-word;
        }
        .note-card-header {
            display: flex;
            flex-wrap: wrap;
            align-items: baseline;
            justify-content: space-between;
            gap: 0.5rem 1rem;
        }
        .note-title {
            font-weight: 600;
            font-size: 1.2rem;
            color: #0b2b3b;
        }
        .note-type-badge {
            font-size: 0.7rem;
            font-weight: 600;
            letter-spacing: 0.02em;
            padding: 0.25rem 0.9rem;
            border-radius: 40px;
            background: #e6edf4;
            color: #1a4b67;
            border: 1px solid #b8cbd9;
        }
        .note-type-badge[data-type="Action Required"] {
            background: #fce9e6;
            color: #a13e2a;
            border-color: #ddbcb3;
        }
        .note-type-badge[data-type="Decision"] {
            background: #e2f0ea;
            color: #1c6e52;
            border-color: #b3d1c2;
        }
        .note-type-badge[data-type="Reference"] {
            background: #e8eef6;
            color: #345c7a;
            border-color: #bccbd9;
        }
        .note-meta {
            display: flex;
            flex-wrap: wrap;
            column-gap: 1.4rem;
            row-gap: 0.2rem;
            font-size: 0.85rem;
            color: #334e66;
        }
        .note-meta span {
            background: #f0f4f9;
            padding: 0.1rem 0.7rem;
            border-radius: 30px;
        }
        .tag-list {
            display: flex;
            flex-wrap: wrap;
            gap: 0.3rem 0.5rem;
            margin: 0.2rem 0;
        }
        .tag {
            background: #dee8f0;
            padding: 0.15rem 0.8rem;
            border-radius: 30px;
            font-size: 0.75rem;
            font-weight: 500;
            color: #1c4560;
        }
        .note-body {
            font-size: 0.9rem;
            color: #1d3243;
            line-height: 1.4;
            padding: 0.5rem 0 0.1rem;
            border-top: 1px dashed #dce5ed;
            margin-top: 0.2rem;
            white-space: pre-wrap;
        }
        .note-actions {
            display: flex;
            gap: 0.5rem;
            margin-top: 0.4rem;
            justify-content: flex-end;
        }
        .note-actions button {
            background: none;
            border: 1px solid #cbdae5;
            padding: 0.2rem 0.8rem;
            border-radius: 40px;
            font-size: 0.75rem;
            font-weight: 500;
            cursor: pointer;
            transition: 0.08s;
            color: #1a3b52;
        }
        .note-actions button:hover, .note-actions button:focus-visible {
            background: #e5edf5;
            border-color: #8da7be;
            outline: 2px solid #1d6f9c;
            outline-offset: 2px;
        }
        .note-actions .delete-btn {
            border-color: #dbb8b0;
            color: #a13e2a;
        }
        .note-actions .delete-btn:hover {
            background: #f7e2dc;
        }
        /* modal overlay */
        .modal-overlay {
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(2px);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            padding: 1rem;
        }
        .modal-panel {
            background: white;
            max-width: 560px;
            width: 100%;
            border-radius: 36px;
            padding: 1.8rem 2rem;
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
            display: flex;
            flex-direction: column;
            gap: 1rem;
            max-height: 95vh;
            overflow-y: auto;
        }
        .modal-panel h2 {
            font-size: 1.4rem;
            font-weight: 500;
            margin-bottom: 0.2rem;
        }
        .modal-panel label {
            font-size: 0.85rem;
            font-weight: 500;
            color: #1f405b;
            display: flex;
            flex-direction: column;
            gap: 0.2rem;
        }
        .modal-panel input, .modal-panel select, .modal-panel textarea {
            padding: 0.5rem 0.8rem;
            border-radius: 30px;
            border: 1px solid #c2d3e2;
            font-size: 0.95rem;
            background: #fcfdff;
            transition: 0.1s;
        }
        .modal-panel textarea {
            min-height: 80px;
            resize: vertical;
        }
        .modal-panel input:focus, .modal-panel select:focus, .modal-panel textarea:focus {
            outline: 2px solid #1d6f9c;
            outline-offset: 1px;
            border-color: transparent;
        }
        .modal-actions {
            display: flex;
            gap: 1rem;
            justify-content: flex-end;
            margin-top: 0.5rem;
        }
        .modal-actions button {
            padding: 0.4rem 1.8rem;
            border-radius: 40px;
            border: 1px solid #bccfde;
            font-weight: 500;
            background: white;
            cursor: pointer;
        }
        .modal-actions .primary-btn {
            background: #1d4a6b;
            color: white;
            border: none;
        }
        .modal-actions .primary-btn:hover, .modal-actions .primary-btn:focus-visible {
            background: #133b52;
            outline: 2px solid #7ab6d9;
        }
        .modal-actions button:focus-visible {
            outline: 2px solid #1d6f9c;
            outline-offset: 2px;
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
        @media (max-width: 480px) {
            .filters {
                flex-direction: column;
                align-items: stretch;
            }
            .btn-add-note {
                margin-left: 0;
                width: fit-content;
            }
            .stats-strip {
                gap: 0.7rem 1rem;
            }
        }
        [hidden] {
            display: none !important;
        }
    </style>
</head>
<body>
<div id="app">
    <h1>📋 Meeting Notes Board</h1>
    <!-- compact statistics strip -->
    <div class="stats-strip" role="status" aria-live="polite">
        <span class="stat-item"><span class="stat-label">📌 Total</span> <span class="stat-value" id="statTotal">0</span></span>
        <span class="stat-item"><span class="stat-label">⚡ Action Required</span> <span class="stat-value" id="statAction">0</span></span>
        <span class="stat-item"><span class="stat-label">👥 Owners</span> <span class="stat-value" id="statOwners">0</span></span>
        <span class="stat-item"><span class="stat-label">🏷️ Common tag</span> <span class="stat-value" id="statTopTag">—</span></span>
    </div>

    <!-- filters -->
    <div class="filters" role="search" aria-label="Filter notes">
        <div class="filter-group">
            <label for="filterOwner">Owner</label>
            <select id="filterOwner" aria-label="Filter by owner">
                <option value="">All</option>
            </select>
        </div>
        <div class="filter-group">
            <label for="filterTag">Tag</label>
            <select id="filterTag" aria-label="Filter by tag">
                <option value="">All</option>
            </select>
        </div>
        <div class="filter-group">
            <label for="filterSearch">🔍 Search</label>
            <input type="text" id="filterSearch" placeholder="title or body ..." aria-label="Search notes by text">
        </div>
        <button class="btn-add-note" id="addNoteBtn" aria-label="Add new note">+ New Note</button>
    </div>

    <!-- card grid -->
    <div class="note-grid" id="noteGrid" role="list" aria-label="Meeting notes"></div>
</div>

<script>
    (function() {
        // ----- STATE -----
        let notes = [];
        let currentEditId = null;  // null => add mode

        const STORAGE_KEY = 'meeting_notes_board';

        // DOM refs
        const grid = document.getElementById('noteGrid');
        const statTotal = document.getElementById('statTotal');
        const statAction = document.getElementById('statAction');
        const statOwners = document.getElementById('statOwners');
        const statTopTag = document.getElementById('statTopTag');
        const filterOwner = document.getElementById('filterOwner');
        const filterTag = document.getElementById('filterTag');
        const filterSearch = document.getElementById('filterSearch');
        const addNoteBtn = document.getElementById('addNoteBtn');

        // ----- helpers -----
        function loadFromStorage() {
            try {
                const raw = localStorage.getItem(STORAGE_KEY);
                if (raw) notes = JSON.parse(raw);
                else notes = [];
            } catch(e) { notes = []; }
        }
        function saveToStorage() {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(notes));
        }

        // generate unique id
        function genId() {
            return Date.now() + '-' + Math.random().toString(36).slice(2, 8);
        }

        // ----- render stats -----
        function updateStats() {
            const filtered = getFilteredNotes();
            const total = notes.length;
            const actionCount = notes.filter(n => n.type === 'Action Required').length;
            const ownersSet = new Set(notes.map(n => n.owner).filter(Boolean));
            const ownersCount = ownersSet.size;

            // most common tag across all notes (not filtered)
            const tagFreq = {};
            notes.forEach(n => {
                (n.tags || []).forEach(t => {
                    tagFreq[t] = (tagFreq[t] || 0) + 1;
                });
            });
            let topTag = '—';
            let maxFreq = 0;
            for (const [tag, freq] of Object.entries(tagFreq)) {
                if (freq > maxFreq) {
                    maxFreq = freq;
                    topTag = tag;
                }
            }
            if (maxFreq === 0) topTag = '—';

            statTotal.textContent = total;
            statAction.textContent = actionCount;
            statOwners.textContent = ownersCount;
            statTopTag.textContent = topTag;
        }

        // ----- filter logic -----
        function getFilteredNotes() {
            const ownerVal = filterOwner.value.trim();
            const tagVal = filterTag.value.trim();
            const searchVal = filterSearch.value.trim().toLowerCase();

            return notes.filter(n => {
                if (ownerVal && n.owner !== ownerVal) return false;
                if (tagVal && !(n.tags || []).includes(tagVal)) return false;
                if (searchVal) {
                    const title = (n.title || '').toLowerCase();
                    const body = (n.body || '').toLowerCase();
                    if (!title.includes(searchVal) && !body.includes(searchVal)) return false;
                }
                return true;
            });
        }

        // populate filter dropdowns
        function populateFilterOptions() {
            const owners = [...new Set(notes.map(n=> n.owner).filter(Boolean))];
            const tags = [...new Set(notes.flatMap(n => n.tags || []).filter(Boolean))];

            const currentOwner = filterOwner.value;
            const currentTag = filterTag.value;

            filterOwner.innerHTML = '<option value="">All</option>';
            owners.forEach(o => {
                const opt = document.createElement('option');
                opt.value = o;
                opt.textContent = o;
                if (o === currentOwner) opt.selected = true;
                filterOwner.appendChild(opt);
            });

            filterTag.innerHTML = '<option value="">All</option>';
            tags.forEach(t => {
                const opt = document.createElement('option');
                opt.value = t;
                opt.textContent = t;
                if (t === currentTag) opt.selected = true;
                filterTag.appendChild(opt);
            });
        }

        // ----- render cards -----
        function renderCards() {
            const filtered = getFilteredNotes();
            grid.innerHTML = '';
            if (filtered.length === 0) {
                const emptyMsg = document.createElement('div');
                emptyMsg.style.gridColumn = '1 / -1';
                emptyMsg.style.padding = '2rem';
                emptyMsg.style.textAlign = 'center';
                emptyMsg.style.color = '#4b6b7a';
                emptyMsg.textContent = '📭 No notes match your filters.';
                grid.appendChild(emptyMsg);
            } else {
                filtered.forEach(note => {
                    const card = document.createElement('div');
                    card.className = 'note-card';
                    card.setAttribute('role', 'listitem');
                    card.dataset.noteId = note.id;

                    const headerDiv = document.createElement('div');
                    headerDiv.className = 'note-card-header';

                    const titleSpan = document.createElement('span');
                    titleSpan.className = 'note-title';
                    titleSpan.textContent = note.title || '(untitled)';

                    const typeBadge = document.createElement('span');
                    typeBadge.className = 'note-type-badge';
                    const typeLabel = note.type || 'Reference';
                    typeBadge.textContent = typeLabel;
                    typeBadge.setAttribute('data-type', typeLabel);

                    headerDiv.appendChild(titleSpan);
                    headerDiv.appendChild(typeBadge);

                    const metaDiv = document.createElement('div');
                    metaDiv.className = 'note-meta';
                    if (note.owner) {
                        const ownerSpan = document.createElement('span');
                        ownerSpan.textContent = '👤 ' + note.owner;
                        metaDiv.appendChild(ownerSpan);
                    }
                    if (note.meetingDate) {
                        const dateSpan = document.createElement('span');
                        dateSpan.textContent = '📅 ' + note.meetingDate;
                        metaDiv.appendChild(dateSpan);
                    }
                    if (note.tags && note.tags.length > 0) {
                        const tagContainer = document.createElement('div');
                        tagContainer.className = 'tag-list';
                        note.tags.forEach(t => {
                            const tagEl = document.createElement('span');
                            tagEl.className = 'tag';
                            tagEl.textContent = t;
                            tagContainer.appendChild(tagEl);
                        });
                        metaDiv.appendChild(tagContainer);
                    }

                    const bodyDiv = document.createElement('div');
                    bodyDiv.className = 'note-body';
                    bodyDiv.textContent = note.body || '';

                    const actionsDiv = document.createElement('div');
                    actionsDiv.className = 'note-actions';
                    const editBtn = document.createElement('button');
                    editBtn.textContent = '✎ Edit';
                    editBtn.setAttribute('aria-label', `Edit note: ${note.title}`);
                    editBtn.addEventListener('click', () => openEditModal(note.id));
                    const deleteBtn = document.createElement('button');
                    deleteBtn.textContent = '🗑 Delete';
                    deleteBtn.className = 'delete-btn';
                    deleteBtn.setAttribute('aria-label', `Delete note: ${note.title}`);
                    deleteBtn.addEventListener('click', () => deleteNote(note.id));
                    actionsDiv.appendChild(editBtn);
                    actionsDiv.appendChild(deleteBtn);

                    card.appendChild(headerDiv);
                    card.appendChild(metaDiv);
                    card.appendChild(bodyDiv);
                    card.appendChild(actionsDiv);
                    grid.appendChild(card);
                });
            }
            updateStats();
        }

        // ----- delete note -----
        function deleteNote(id) {
            if (!confirm('Delete this note?')) return;
            notes = notes.filter(n => n.id !== id);
            saveToStorage();
            populateFilterOptions();
            renderCards();
        }

        // ----- modal logic (add/edit) -----
        function openEditModal(noteId) {
            const note = notes.find(n => n.id === noteId);
            if (!note) return;
            currentEditId = noteId;
            showModal(note);
        }

        function openAddModal() {
            currentEditId = null;
            showModal({
                title: '',
                owner: '',
                meetingDate: '',
                tags: '',
                body: '',
                type: 'Reference'
            });
        }

        function showModal(prefill) {
            // remove existing overlay
            const existing = document.querySelector('.modal-overlay');
            if (existing) existing.remove();

            const overlay = document.createElement('div');
            overlay.className = 'modal-overlay';
            overlay.setAttribute('role', 'dialog');
            overlay.setAttribute('aria-modal', 'true');
            overlay.setAttribute('aria-label', currentEditId ? 'Edit note' : 'Add note');

            const panel = document.createElement('div');
            panel.className = 'modal-panel';

            const heading = document.createElement('h2');
            heading.textContent = currentEditId ? '✏️ Edit note' : '📝 New note';

            // title
            const titleLabel = document.createElement('label');
            titleLabel.textContent = 'Title';
            const titleInput = document.createElement('input');
            titleInput.type = 'text';
            titleInput.value = prefill.title || '';
            titleInput.id = 'modalTitle';
            titleLabel.appendChild(titleInput);
            titleLabel.htmlFor = 'modalTitle';

            // owner
            const ownerLabel = document.createElement('label');
            ownerLabel.textContent = 'Owner';
            const ownerInput = document.createElement('input');
            ownerInput.type = 'text';
            ownerInput.value = prefill.owner || '';
            ownerInput.id = 'modalOwner';
            ownerLabel.appendChild(ownerInput);
            ownerLabel.htmlFor = 'modalOwner';

            // meeting date
            const dateLabel = document.createElement('label');
            dateLabel.textContent = 'Meeting date';
            const dateInput = document.createElement('input');
            dateInput.type = 'date';
            dateInput.value = prefill.meetingDate || '';
            dateInput.id = 'modalDate';
            dateLabel.appendChild(dateInput);
            dateLabel.htmlFor = 'modalDate';

            // tags (comma separated)
            const tagsLabel = document.createElement('label');
            tagsLabel.textContent = 'Tags (comma separated)';
            const tagsInput = document.createElement('input');
            tagsInput.type = 'text';
            tagsInput.value = Array.isArray(prefill.tags) ? prefill.tags.join(', ') : (prefill.tags || '');
            tagsInput.id = 'modalTags';
            tagsLabel.appendChild(tagsInput);
            tagsLabel.htmlFor = 'modalTags';

            // type
            const typeLabel = document.createElement('label');
            typeLabel.textContent = 'Type';
            const typeSelect = document.createElement('select');
            typeSelect.id = 'modalType';
            ['Action Required', 'Decision', 'Reference'].forEach(t => {
                const opt = document.createElement('option');
                opt.value = t;
                opt.textContent = t;
                if (prefill.type === t) opt.selected = true;
                typeSelect.appendChild(opt);
            });
            typeLabel.appendChild(typeSelect);
            typeLabel.htmlFor = 'modalType';

            // body
            const bodyLabel = document.createElement('label');
            bodyLabel.textContent = 'Body';
            const bodyTextarea = document.createElement('textarea');
            bodyTextarea.value = prefill.body || '';
            bodyTextarea.id = 'modalBody';
            bodyLabel.appendChild(bodyTextarea);
            bodyLabel.htmlFor = 'modalBody';

            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'modal-actions';

            const cancelBtn = document.createElement('button');
            cancelBtn.textContent = 'Cancel';
            cancelBtn.addEventListener('click', () => overlay.remove());
            cancelBtn.setAttribute('aria-label', 'Cancel and close');

            const saveBtn = document.createElement('button');
            saveBtn.textContent = 'Save note';
            saveBtn.className = 'primary-btn';
            saveBtn.addEventListener('click', () => {
                // validation: title required
                const title = titleInput.value.trim();
                if (!title) {
                    alert('Please enter a title.');
                    titleInput.focus();
                    return;
                }
                const owner = ownerInput.value.trim();
                const meetingDate = dateInput.value.trim();
                const tagsRaw = tagsInput.value.trim();
                const tags = tagsRaw ? tagsRaw.split(',').map(s => s.trim()).filter(Boolean) : [];
                const type = typeSelect.value;
                const body = bodyTextarea.value.trim();

                if (currentEditId) {
                    const note = notes.find(n => n.id === currentEditId);
                    if (note) {
                        note.title = title;
                        note.owner = owner;
                        note.meetingDate = meetingDate;
                        note.tags = tags;
                        note.type = type;
                        note.body = body;
                    }
                } else {
                    notes.push({
                        id: genId(),
                        title,
                        owner,
                        meetingDate,
                        tags,
                        type,
                        body
                    });
                }
                saveToStorage();
                populateFilterOptions();
                renderCards();
                overlay.remove();
            });

            actionsDiv.appendChild(cancelBtn);
            actionsDiv.appendChild(saveBtn);

            panel.appendChild(heading);
            panel.appendChild(titleLabel);
            panel.appendChild(ownerLabel);
            panel.appendChild(dateLabel);
            panel.appendChild(tagsLabel);
            panel.appendChild(typeLabel);
            panel.appendChild(bodyLabel);
            panel.appendChild(actionsDiv);
            overlay.appendChild(panel);
            document.body.appendChild(overlay);

            // focus title
            titleInput.focus();

            // close on Escape
            overlay.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') overlay.remove();
            });
            // click backdrop to close
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) overlay.remove();
            });
        }

        // ----- event listeners for filters -----
        function onFilterChange() {
            renderCards();
        }

        filterOwner.addEventListener('change', onFilterChange);
        filterTag.addEventListener('change', onFilterChange);
        filterSearch.addEventListener('input', onFilterChange);

        addNoteBtn.addEventListener('click', openAddModal);

        // ----- initialize -----
        loadFromStorage();
        populateFilterOptions();
        renderCards();

        // expose for debugging
        window.__notes = notes;
    })();
</script>
</body>
</html>
```
````
