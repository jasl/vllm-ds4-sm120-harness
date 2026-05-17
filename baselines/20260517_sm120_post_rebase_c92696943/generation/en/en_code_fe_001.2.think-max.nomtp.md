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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 145.740587
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 305, "total_tokens": 14658, "completion_tokens": 14353, "prompt_tokens_details": null}`
- Prompt tokens: 305
- Completion tokens: 14353
- Total tokens: 14658

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

## Reasoning Content

````text
Thinking. 1.  **Analyze the Request:**
    *   **Format:** Single file frontend app named `index.html`.
    *   **Constraints:** No external libraries, CDNs, images, or build tools. Total code under 1000 lines.
    *   **Core Task:** Accessible “meeting notes board” for a small team.
    *   **Functional Requirements:**
        1.  CRUD (Add, Edit, Delete) notes with title, owner, meeting date, tags, body.
        2.  Notes display as cards.
        3.  Filtering by owner, tag, and free-text search.
        4.  Category: “Action Required,” “Decision,” “Reference.”
        5.  Persist data in `localStorage`.
        6.  Stats strip: total notes, action-required count, unique owners, most common tag.
        7.  Responsive layout: 2-column grid (wide), single column (narrow).
        8.  Accessibility: labels for inputs, keyboard-operable controls, visible focus states.
    *   **Output:** Only the complete `index.html` content.

    1.  **Break Down the Code Structure (HTML + CSS + JS in one file):**
        *   **HTML**: Structure of the page. Header, stats strip, filter bar, form (add/edit), notes grid.
        *   **CSS**: Styling, responsive grid, focus states, basic accessibility.
        *   **JavaScript**: Logic for CRUD, filtering, localStorage persistence, stats calculation.

    2.  **Drafting the HTML (Component/Container IDs):**
        *   `<header>`: Title, Stats Strip.
        *   `<main>`:
            *   `<section id="filters">`:
                *   Search input (`type="search" id="search-input"`)
                *   Owner filter (`<select id="owner-filter">`)
                *   Tag filter (`<select id="tag-filter">`)
                *   Category filter (`<select id="category-filter">`) -> wait, need to decide if category is part of the note. A note "can be marked as" one of these. Yes.
            *   `<button id="add-note-btn">` (opens modal/form)
            *   `<section id="notes-grid">` (dynamic card container)
        *   **Modal / Form**:
            *   `<dialog>` or `<div>` overlay. `<dialog>` is better for accessibility (native focus management, `Escape` key).
            *   `<form id="note-form">`
                *   Title input (`type="text"`)
                *   Owner input (`type="text"`)
                *   Meeting Date input (`type="date"`)
                *   Tags input (`type="text"`) or maybe a textarea for multiple tags. Let's use a text input where user can type comma-separated tags, or maybe a dedicated tag area? Comma-separated is simpler and widely used.
                *   Category radio buttons or `<select>`. Select is less keyboard steps.
                *   Body textarea
                *   Submit / Cancel buttons.

    3.  **Drafting the JavaScript Logic:**
        *   `let notes = [];`
        *   `let editingId = null;`
        *   `loadNotes()`: Parse `localStorage.getItem('meetingNotes')`.
        *   `saveNotes()`: `localStorage.setItem('meetingNotes', JSON.stringify(notes))`.
        *   `renderNotes()`: Clear grid, filter `notes`, populate cards.
        *   `updateStats()`: Calculate and update stat strip.
        *   `renderFilters()`: Populate owner/tag filter dropdowns from current notes.
        *   `addNote(data)`: `notes.push(data)` -> save -> render.
        *   `editNote(id, data)`: Find index, update -> save -> render.
        *   `deleteNote(id)`: Filter out -> save -> render.
        *   **Filtering Logic:**
            *   `filteredNotes = notes.filter(...)`
            *   Check `search` (title/body/owner/tags).
            *   Check `ownerFilter`.
            *   Check `tagFilter`.
            *   Check `categoryFilter`.
        *   **Stats Logic:**
            *   Total notes (`notes.length`).
            *   Action required count (`notes.filter(n => n.category === 'action-required').length`).
            *   Unique owners (`new Set(notes.map(n => n.owner.trim().toLowerCase())).size`). Or case-sensitive? Better to be case-insensitive but display original.
            *   Most common tag: iterate all tags, count occurrences, find max.

    4.  **Drafting the CSS:**
        *   Reset / base styles.
        *   `.stats-strip` flex layout.
        *   `.filters-bar` flex layout.
        *   `.notes-grid` => CSS Grid.
            *   `grid-template-columns: repeat(2, 1fr)` on wide.
            *   `@media (max-width: 768px)` => `grid-template-columns: 1fr`.
        *   `.note-card` styling (border, shadow, spacing).
        *   Form styling.
        *   Button styling.
        *   **Accessibility:**
            *   `:focus-visible` outlines.
            *   `aria-labels` on buttons.
            *   `<label for="...">` for all form controls.
            *   `<dialog>` element.

    5.  **Refining the Requirements:**
        *   *Filter by owner, tag, and free-text search.* (Done via filters/search bar).
        *   *Category:* Action Required, Decision, Reference.
        *   *Edit and Delete notes.* (Buttons on cards).
        *   *localStorage.* (Key: `meetingNotesData`).
        *   *Stats strip.* (Total, Action Required, Unique Owners, Most Common Tag).
        *   *Responsive layout.* (2-col on wide, 1-col on narrow).
        *   *Accessibility.* (Labels, keyboard controls, focus states).
        *   *Code under 1000 lines.* Need to be concise but complete.

    6.  **Step-by-Step Implementation Details:**

        **HTML Structure:**
        ```html
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Meeting Notes Board</title>
            <style>
                /* ... CSS ... */
            </style>
        </head>
        <body>
            <header>
                <h1>Meeting Notes Board</h1>
                <div class="stats-strip" id="stats-strip">...</div>
            </header>
            <main>
                <section class="controls">
                    <div class="filters" id="filters">
                        <input type="search" id="search-input" placeholder="Search notes...">
                        <select id="owner-filter"><option value="">All Owners</option></select>
                        <select id="tag-filter"><option value="">All Tags</option></select>
                        <select id="category-filter"><option value="">All Categories</option>
                            <option value="action-required">Action Required</option>
                            <option value="decision">Decision</option>
                            <option value="reference">Reference</option>
                        </select>
                    </div>
                    <button id="add-note-btn">+ Add Note</button>
                </section>

                <section class="notes-grid" id="notes-grid" role="list" aria-label="Meeting notes list">
                    <!-- Cards rendered by JS -->
                </section>
            </main>

            <!-- Add/Edit Note Modal -->
            <dialog id="note-modal">
                <form id="note-form" method="dialog">
                    <h2 id="modal-title">Add Note</h2>
                    <label for="note-title">Title</label>
                    <input type="text" id="note-title" required>

                    <label for="note-owner">Owner</label>
                    <input type="text" id="note-owner" required>

                    <label for="note-date">Meeting Date</label>
                    <input type="date" id="note-date">

                    <label for="note-tags">Tags (comma-separated)</label>
                    <input type="text" id="note-tags" placeholder="e.g., sprint, design">

                    <label for="note-category">Category</label>
                    <select id="note-category">
                        <option value="action-required">Action Required</option>
                        <option value="decision">Decision</option>
                        <option value="reference">Reference</option>
                    </select>

                    <label for="note-body">Body</label>
                    <textarea id="note-body" rows="4"></textarea>

                    <div class="form-actions">
                        <button type="submit" id="save-note-btn">Save</button>
                        <button type="button" id="cancel-btn">Cancel</button>
                    </div>
                </form>
            </dialog>

            <script>
                /* ... JavaScript ... */
            </script>
        </body>
        </html>
        ```

        **CSS Details (keeping under 1000 lines total, CSS will be compact):**
        *   `:root` variables for colors if desired (or just static).
        *   `* { box-sizing: border-box; }`
        *   `body { font-family: system-ui, sans-serif; margin: 0; padding: 20px; }`
        *   `.controls { display: flex; gap: 10px; align-items: end; }`
        *   `.filters { display: flex; flex-wrap: wrap; gap: 10px; flex: 1; }`
        *   `.stats-strip { display: flex; gap: 20px; padding: 10px 0; }`
        *   `.stat-item { background: #f0f0f0; padding: 5px 15px; border-radius: 5px; }`
        *   `.notes-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-top: 20px; }`
        *   `@media (max-width: 700px) { .notes-grid { grid-template-columns: 1fr; } }`
        *   `.note-card { ... }`
        *   `dialog { ... }`

        **JavaScript Details:**
        *   Wait, the tags should be stored as an array of strings. Input is a comma-separated string.
        *   `addNote(data)` / `editNote(id, data)`:
            ```javascript
            function getFormData() {
                const title = document.getElementById('note-title').value.trim();
                const owner = document.getElementById('note-owner').value.trim();
                const date = document.getElementById('note-date').value;
                const tags = document.getElementById('note-tags').value.split(',').map(t => t.trim()).filter(t => t);
                const category = document.getElementById('note-category').value;
                const body = document.getElementById('note-body').value.trim();
                return { title, owner, date, tags, category, body };
            }
            ```
        *   `renderNotes(notesToRender)`:
            ```javascript
            function renderNotes() {
                let filteredNotes = getFilteredNotes();
                const grid = document.getElementById('notes-grid');
                grid.innerHTML = '';
                if (filteredNotes.length === 0) {
                    grid.innerHTML = '<p>No notes found.</p>';
                    return;
                }
                filteredNotes.forEach(note => {
                    const card = document.createElement('article');
                    card.className = 'note-card';
                    card.setAttribute('role', 'listitem');
                    card.innerHTML = `
                        <h3>${escapeHtml(note.title)}</h3>
                        <p class="note-meta">
                            <span>Owner: ${escapeHtml(note.owner)}</span>
                            <span>Date: ${note.date || 'N/A'}</span>
                            <span class="note-category ${note.category}">${note.category.replace('-', ' ')}</span>
                        </p>
                        <p>${escapeHtml(note.body)}</p>
                        <p class="note-tags">${note.tags.map(t => `<span class="tag">${escapeHtml(t)}</span>`).join(' ')}</p>
                        <div class="card-actions">
                            <button class="edit-btn" data-id="${note.id}" aria-label="Edit note: ${escapeHtml(note.title)}">Edit</button>
                            <button class="delete-btn" data-id="${note.id}" aria-label="Delete note: ${escapeHtml(note.title)}">Delete</button>
                        </div>
                    `;
                    grid.appendChild(card);
                });
                // Attach event listeners (or use event delegation on the grid)
                document.querySelectorAll('.edit-btn').forEach(btn => {
                    btn.addEventListener('click', (e) => openEditModal(e.target.dataset.id));
                });
                document.querySelectorAll('.delete-btn').forEach(btn => {
                    btn.addEventListener('click', (e) => deleteNote(e.target.dataset.id));
                });
            }
            ```
            *Event Delegation is better.*
            ```javascript
            grid.addEventListener('click', (e) => {
                const target = e.target;
                if (target.classList.contains('edit-btn')) {
                    openEditModal(target.dataset.id);
                }
                if (target.classList.contains('delete-btn')) {
                    deleteNote(target.dataset.id);
                }
            });
            ```
            *   `escapeHtml` function to prevent XSS.
            *   `filteredNotes = notes.filter(...)`. Filter logic.
            *   **Stats Calculation:**
                ```javascript
                function updateStats() {
                    const total = notes.length;
                    const actionRequired = notes.filter(n => n.category === 'action-required').length;
                    const uniqueOwners = new Set(notes.map(n => n.owner.toLowerCase())).size;
                    const tagCounts = {};
                    notes.forEach(n => {
                        n.tags.forEach(t => {
                            const lowerTag = t.toLowerCase();
                            tagCounts[lowerTag] = (tagCounts[lowerTag] || 0) + 1;
                        });
                    });
                    let mostCommonTag = 'N/A';
                    let maxCount = 0;
                    for (const [tag, count] of Object.entries(tagCounts)) {
                        if (count > maxCount) {
                            maxCount = count;
                            mostCommonTag = tag;
                        }
                    }
                    document.getElementById('stat-total').textContent = total;
                    document.getElementById('stat-actions').textContent = actionRequired;
                    document.getElementById('stat-owners').textContent = uniqueOwners;
                    document.getElementById('stat-tag').textContent = mostCommonTag + (maxCount > 0 ? ` (${maxCount})` : '');
                }
                ```

        **Filtering Logic:**
        *   Search: check title, body, owner, tags.
        *   Owner filter: exact match against dropdown value.
        *   Tag filter: exact match against dropdown value.
        *   Category filter: exact match against dropdown value.

        **Modal/Dialog Logic:**
        *   Use native `<dialog>` element.
        *   `openAddModal()`: Reset form, set `editingId = null`, show modal.
        *   `openEditModal(id)`: Find note, populate form, set `editingId = id`, show modal.
        *   `cancelModal()`: Close dialog.
        *   `submitForm()` (on form submit):
            *   `form.elements` or `getElementById`.
            *   Validate required fields (title, owner).
            *   If `editingId` is null, add note. Else, update note.
            *   Close dialog.
            *   render / update stats.

        **Data Model:**
        ```javascript
        {
            id: Date.now() + Math.random(), // unique ID
            title: "string",
            owner: "string",
            date: "2024-05-20", // string from input
            tags: ["tag1", "tag2"],
            category: "action-required", // "decision", "reference"
            body: "string"
        }
        ```

        **Let's write the code strictly under 1000 lines.**
        It's easy to accidentally exceed the line limit with HTML, CSS, and JS combined. Let's keep the CSS very concise (no fancy animations, just structured layout), HTML semantic but tight, JS efficient.

        **Detailed Accessibility & UX Check:**
        *   Labels: `for` attributes on `<label>`.
        *   Focus states: `:focus-visible { outline: 2px solid blue; }`
        *   Keyboard: `<dialog>` handles escape. Buttons are tabbable. Forms submit on Enter.
        *   *Important:* The form inside `<dialog>` should use `method="dialog"` or we handle the `submit` event ourselves and call `event.preventDefault()` and `close()`.

        **Potential Pitfalls / Edge Cases:**
        *   Empty states (no notes, no filtered results).
        *   Duplicate tags in stats? The filter logic for most common tag should be case-insensitive but we should display the most common cased version, or just lowercased. Let's do lowercased for simplicity and consistency.
        *   Escaping HTML in displayed text.
        *   The search also searches tags.
        *   Deleting a note that is being edited? Just close the modal.

        **Striving for good code organization inside a single script block.**

        **Line count management:**
        *   HTML: ~80 lines (structure, modal, stats strip).
        *   CSS: ~100 lines (layout, cards, responsive, focus).
        *   JS: ~200 lines (CRUD, filters, render, stats).
        Total: ~380 lines. Well under 1000.

        Let's flesh out the implementation text by text.

        **Refining Stats Display:**
        ```html
        <div class="stats-strip" id="stats-strip" aria-label="Note statistics">
            <div class="stat-item">Total Notes: <strong id="stat-total">0</strong></div>
            <div class="stat-item">Action Required: <strong id="stat-actions">0</strong></div>
            <div class="stat-item">Unique Owners: <strong id="stat-owners">0</strong></div>
            <div class="stat-item">Top Tag: <strong id="stat-tag">N/A</strong></div>
        </div>
        ```

        **Refining Form:**
        ```html
        <dialog id="note-modal">
            <form id="note-form" method="dialog">
                <h2 id="modal-title">Add Note</h2>
                <p><label for="note-title">Title</label><input type="text" id="note-title" required></p>
                <p><label for="note-owner">Owner</label><input type="text" id="note-owner" required></p>
                <p><label for="note-date">Meeting Date</label><input type="date" id="note-date"></p>
                <p><label for="note-tags">Tags (comma-separated)</label><input type="text" id="note-tags" placeholder="e.g., sprint, design"></p>
                <p><label for="note-category">Category</label>
                    <select id="note-category">
                        <option value="action-required">Action Required</option>
                        <option value="decision">Decision</option>
                        <option value="reference">Reference</option>
                    </select>
                </p>
                <p><label for="note-body">Body</label><textarea id="note-body" rows="4"></textarea></p>
                <div class="form-actions">
                    <button type="submit" id="save-note-btn">Save</button>
                    <button type="button" id="cancel-btn">Cancel</button>
                </div>
            </form>
        </dialog>
        ```
        Let's use `method="dialog"` on the form. Wait, if `method="dialog"` is used, the form's submit event doesn't trigger a POST, it just closes the modal and returns the submit button value to the `dialog.returnValue`. It's better to prevent the default form submit and handle it manually.
        ```javascript
        noteForm.addEventListener('submit', (event) => {
            event.preventDefault();
            handleFormSubmit();
        });
        ```
        This gives us full control. The `method="dialog"` can be removed. If `type="submit"` is used without `method="dialog"`, the browser might try to submit a form. `event.preventDefault()` avoids this.

        **Refining Delete:**
        ```javascript
        function deleteNote(id) {
            if (confirm('Are you sure you want to delete this note?')) {
                notes = notes.filter(n => n.id != id);
                saveNotes();
                render();
            }
        }
        ```

        **Refining Render (Filter Dropdowns):**
        Need to dynamically update the filter dropdown options.
        ```javascript
        function updateFilterOptions() {
            const owners = [...new Set(notes.map(n => n.owner))];
            const tags = [...new Set(notes.flatMap(n => n.tags))];
            // Populate owner-filter
            const ownerSelect = document.getElementById('owner-filter');
            const currentOwnerVal = ownerSelect.value;
            ownerSelect.innerHTML = '<option value="">All Owners</option>';
            owners.forEach(o => {
                ownerSelect.innerHTML += `<option value="${escapeHtml(o)}">${escapeHtml(o)}</option>`;
            });
            ownerSelect.value = currentOwnerVal; // preserve selection if possible

            const tagSelect = document.getElementById('tag-filter');
            const currentTagVal = tagSelect.value;
            tagSelect.innerHTML = '<option value="">All Tags</option>';
            tags.forEach(t => {
                tagSelect.innerHTML += `<option value="${escapeHtml(t)}">${escapeHtml(t)}</option>`;
            });
            tagSelect.value = currentTagVal;
        }
        ```

        **Refining Stats Most Common Tag:**
        The "most common tag" needs to handle case insensitivity for counting, but we can display the most commonly occurring exact string. Let's just display the first one found, or the lowercase one with a representative casing. For simplicity, finding the mode and displaying lower case is fine. If there's a tie, the first encountered alphabetically or by index. Let's just do the first one with the highest count.

        ```javascript
        function getMostCommonTag() {
            if (notes.length === 0) return { tag: 'N/A', count: 0 };
            const counts = {};
            notes.forEach(n => {
                n.tags.forEach(t => {
                    const lower = t.toLowerCase();
                    counts[lower] = (counts[lower] || 0) + 1;
                });
            });
            let maxCount = 0;
            let mostCommon = 'N/A';
            for (const [tag, count] of Object.entries(counts)) {
                if (count > maxCount) {
                    maxCount = count;
                    mostCommon = tag;
                }
            }
            return { tag: mostCommon, count: maxCount };
        }
        ```

        **Refining `saveNotes` and data handling:**
        Use `localStorage`.

        **Event Listeners Setup:**
        *   `document.getElementById('add-note-btn').addEventListener('click', openAddModal);`
        *   `document.getElementById('cancel-btn').addEventListener('click', closeModal);`
        *   `document.getElementById('note-form').addEventListener('submit', handleFormSubmit);`
        *   Filter listeners:
            ```javascript
            ['search-input', 'owner-filter', 'tag-filter', 'category-filter'].forEach(id => {
                document.getElementById(id).addEventListener('input', render);
            });
            ```
            (Using `input` event for search, `change` for selects).

        **CSS optimization:**
        Let's do a quick CSS scrub.
        ```css
        * { box-sizing: border-box; }
        body { font-family: system-ui, -apple-system, sans-serif; margin: 0; padding: 20px; background: #f8f9fa; color: #212529; }
        header { margin-bottom: 20px; }
        h1 { font-size: 1.8rem; margin: 0 0 10px; }
        .stats-strip { display: flex; gap: 15px; flex-wrap: wrap; }
        .stat-item { background: #fff; padding: 8px 16px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); font-size: 0.9rem; }
        .controls { display: flex; gap: 15px; align-items: end; flex-wrap: wrap; justify-content: space-between; margin-bottom: 20px; }
        .filters { display: flex; gap: 10px; flex-wrap: wrap; flex: 1; }
        .filters input, .filters select { padding: 8px 12px; border: 1px solid #ced4da; border-radius: 6px; font-size: 0.9rem; }
        .filters input#search-input { min-width: 200px; flex: 1; }
        #add-note-btn { padding: 8px 16px; background: #0d6efd; color: #fff; border: none; border-radius: 6px; font-size: 0.9rem; cursor: pointer; white-space: nowrap; }
        .notes-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
        @media (max-width: 768px) { .notes-grid { grid-template-columns: 1fr; } }
        .note-card { background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); border-left: 5px solid transparent; }
        .note-card.note-category-action-required { border-left-color: #dc3545; }
        .note-card.note-category-decision { border-left-color: #ffc107; }
        .note-card.note-category-reference { border-left-color: #0d6efd; }
        .note-card h3 { margin: 0 0 10px; font-size: 1.2rem; }
        .note-card .note-meta { font-size: 0.85rem; color: #6c757d; display: flex; gap: 15px; flex-wrap: wrap; margin-bottom: 10px; }
        .note-card .note-category { font-weight: 600; text-transform: capitalize; }
        .note-card p { margin: 0 0 10px; }
        .note-card .note-tags { display: flex; gap: 5px; flex-wrap: wrap; }
        .note-card .tag { background: #e9ecef; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; }
        .card-actions { display: flex; gap: 10px; justify-content: flex-end; }
        .card-actions button { padding: 5px 12px; border: 1px solid #ced4da; border-radius: 4px; background: #fff; cursor: pointer; font-size: 0.85rem; }
        dialog { border: none; border-radius: 12px; padding: 30px; max-width: 500px; width: 90%; box-shadow: 0 5px 20px rgba(0,0,0,0.3); }
        dialog::backdrop { background: rgba(0,0,0,0.4); }
        dialog form p { margin: 0 0 15px; }
        dialog label { display: block; margin-bottom: 5px; font-weight: 600; font-size: 0.9rem; }
        dialog input:not([type="radio"]):not([type="checkbox"]), dialog select, dialog textarea { width: 100%; padding: 8px 12px; border: 1px solid #ced4da; border-radius: 6px; font-size: 0.9rem; }
        .form-actions { display: flex; gap: 10px; justify-content: flex-end; margin-top: 20px; }
        .form-actions button { padding: 10px 20px; border-radius: 6px; font-size: 0.9rem; cursor: pointer; }
        #save-note-btn { background: #0d6efd; color: #fff; border: none; }
        #cancel-btn { background: #fff; border: 1px solid #ced4da; }
        /* Focus states */
        :focus-visible { outline: 2px solid #0d6efd; outline-offset: 2px; }
        button:hover { opacity: 0.9; }
        ```

        **JS Code:**
        Needs `escapeHtml` function:
        ```javascript
        function escapeHtml(str) {
            const div = document.createElement('div');
            div.appendChild(document.createTextNode(str));
            return div.innerHTML;
        }
        ```

        **Putting it all together:**

        Make sure the code is fully functional.

        Let's review the exact requirements:
        *   **Functional requirements:**
            1. Users can add a note with title, owner, meeting date, tags, and body. (YES)
            2. Notes appear as cards and can be filtered by owner, tag, and free-text search. (YES)
            3. A note can be marked as “Action Required,” “Decision,” or “Reference.” (YES)
            4. Users can edit and delete notes. (YES)
            5. Persist all data in `localStorage`. (YES)
            6. Provide a compact statistics strip: total notes, action-required count, unique owners, and most common tag. (YES)
            7. Responsive layout: two-column card grid on wide screens, single column on narrow screens. (YES)
            8. Basic accessibility: labels for inputs, keyboard-operable controls, visible focus states. (YES, using `<dialog>`, labels, `:focus-visible`)

        *   **Constraints:**
            *   Single file (YES, `index.html`)
            *   No external libraries (YES)
            *   No CDNs (YES)
            *   No images (YES)
            *   No build tools (YES)
            *   Under 1000 lines (YES, ~300 lines)
            *   Output *only* the complete `index.html` (YES, no markdown or explanation).

        *   **Check for subtle issues in logic:**
            *   What if `edit` is clicked, modal opens. User cancels. Form should reset.
            *   What about empty required fields? HTML `required` attribute handles browser validation. JS can also check.
            *   Deleting a note? `render()` rebuilds everything.
            *   `localStorage`: handle empty/null gracefully.
            *   Most common tag: tagging. A note without tags should just not contribute.
            *   Unique owners: case-insensitive.
            *   Card category border: The class is set on the card. Wait, in the render, I set a class on the card:
            `card.className = 'note-card';`
            `if (note.category) card.classList.add('note-category-' + note.category);`
            Yes.

            *   Edit form: Must repopulate the form exactly.
                ```javascript
                function openEditModal(id) {
                    const note = notes.find(n => n.id == id);
                    if (!note) return;
                    editingId = id;
                    document.getElementById('modal-title').textContent = 'Edit Note';
                    document.getElementById('note-title').value = note.title;
                    document.getElementById('note-owner').value = note.owner;
                    document.getElementById('note-date').value = note.date || '';
                    document.getElementById('note-tags').value = note.tags.join(', ');
                    document.getElementById('note-category').value = note.category;
                    document.getElementById('note-body').value = note.body || '';
                    document.getElementById('note-modal').showModal();
                }
                ```
            *   Add modal: Reset form.
                ```javascript
                function openAddModal() {
                    editingId = null;
                    document.getElementById('modal-title').textContent = 'Add Note';
                    document.getElementById('note-form').reset();
                    document.getElementById('note-category').value = 'action-required'; // default
                    document.getElementById('note-modal').showModal();
                }
                ```

            *   Form submission handler:
                ```javascript
                function handleFormSubmit(event) {
                    event.preventDefault();
                    const title = document.getElementById('note-title').value.trim();
                    const owner = document.getElementById('note-owner').value.trim();
                    if (!title || !owner) {
                        // basic validation, though HTML required handles it
                        return;
                    }
                    const date = document.getElementById('note-date').value;
                    const tags = document.getElementById('note-tags').value.split(',').map(t => t.trim()).filter(t => t);
                    const category = document.getElementById('note-category').value;
                    const body = document.getElementById('note-body').value.trim();

                    const noteData = { title, owner, date, tags, category, body };

                    if (editingId) {
                        const index = notes.findIndex(n => n.id == editingId);
                        if (index !== -1) {
                            notes[index] = { ...notes[index], ...noteData };
                        }
                    } else {
                        noteData.id = Date.now() + Math.random();
                        notes.push(noteData);
                    }
                    saveNotes();
                    render();
                    document.getElementById('note-modal').close();
                }
                ```
                Wait, `Date.now() + Math.random()` might not be perfectly unique if concurrent calls, but for a simple local app it's fine. Or we can use a counter or `crypto.randomUUID()`? `crypto.randomUUID()` is available in modern browsers. Let's use `Date.now() + '_' + Math.random().toString(36).substr(2, 9)` which is very safe.

            *   Filter event listeners:
                Use `change` for `<select>` elements and `input` for the search field.
                ```html
                <input type="search" id="search-input" ...>
                ```
                ```javascript
                document.getElementById('search-input').addEventListener('input', render);
                document.getElementById('owner-filter').addEventListener('change', render);
                document.getElementById('tag-filter').addEventListener('change', render);
                document.getElementById('category-filter').addEventListener('change', render);
                ```

            *   Filter function:
                ```javascript
                function getFilteredNotes() {
                    const searchTerm = document.getElementById('search-input').value.toLowerCase().trim();
                    const ownerFilter = document.getElementById('owner-filter').value;
                    const tagFilter = document.getElementById('tag-filter').value;
                    const categoryFilter = document.getElementById('category-filter').value;

                    return notes.filter(note => {
                        // search filter
                        if (searchTerm) {
                            const searchableText = (note.title + ' ' + note.owner + ' ' + note.body + ' ' + note.tags.join(' ')).toLowerCase();
                            if (!searchableText.includes(searchTerm)) {
                                return false;
                            }
                        }
                        // owner filter
                        if (ownerFilter && note.owner !== ownerFilter) {
                            return false;
                        }
                        // tag filter
                        if (tagFilter && !note.tags.includes(tagFilter)) {
                            return false;
                        }
                        // category filter
                        if (categoryFilter && note.category !== categoryFilter) {
                            return false;
                        }
                        return true;
                    });
                }
                ```

            *   Render Function calling `updateFilterOptions` and `updateStats`:
                ```javascript
                function render() {
                    updateFilterOptions();
                    const filteredNotes = getFilteredNotes();
                    const grid = document.getElementById('notes-grid');
                    grid.innerHTML = '';
                    if (filteredNotes.length === 0) {
                        grid.innerHTML = '<p>No notes found.</p>';
                    } else {
                        filteredNotes.forEach(note => {
                            const card = document.createElement('article');
                            card.className = 'note-card';
                            if (note.category) card.classList.add('note-category-' + note.category);
                            card.setAttribute('data-id', note.id);
                            card.setAttribute('role', 'listitem');
                            const safeTitle = escapeHtml(note.title);
                            card.innerHTML = `
                                <h3>${safeTitle}</h3>
                                <p class="note-meta">
                                    <span>Owner: ${escapeHtml(note.owner)}</span>
                                    <span>Date: ${escapeHtml(note.date || 'N/A')}</span>
                                    <span class="note-category">${escapeHtml(note.category.replace('-', ' '))}</span>
                                </p>
                                <p>${escapeHtml(note.body || '')}</p>
                                <p class="note-tags">${note.tags.map(t => `<span class="tag">${escapeHtml(t)}</span>`).join(' ')}</p>
                                <div class="card-actions">
                                    <button class="edit-btn" data-id="${note.id}" aria-label="Edit note: ${safeTitle}">Edit</button>
                                    <button class="delete-btn" data-id="${note.id}" aria-label="Delete note: ${safeTitle}">Delete</button>
                                </div>
                            `;
                            grid.appendChild(card);
                        });
                    }
                    updateStats();
                }
                ```

            *   Event delegation for edit/delete buttons on grid:
                ```javascript
                document.getElementById('notes-grid').addEventListener('click', (e) => {
                    const btn = e.target.closest('button');
                    if (!btn) return;
                    const id = btn.dataset.id;
                    if (btn.classList.contains('edit-btn')) {
                        openEditModal(id);
                    } else if (btn.classList.contains('delete-btn')) {
                        deleteNote(id);
                    }
                });
                ```
                This is much more robust than attaching to each button.

            *   `deleteNote` function:
                ```javascript
                function deleteNote(id) {
                    if (confirm('Are you sure you want to delete this note?')) {
                        notes = notes.filter(n => n.id != id);
                        saveNotes();
                        render();
                        // If modal is open editing this note, close it
                        // Actually, just close the modal to avoid stale state
                        if (editingId == id) {
                            document.getElementById('note-modal').close();
                        }
                    }
                }
                ```

            *   Save/Load functions:
                ```javascript
                const STORAGE_KEY = 'meetingNotesBoardData';

                function loadNotes() {
                    const stored = localStorage.getItem(STORAGE_KEY);
                    if (stored) {
                        try {
                            notes = JSON.parse(stored);
                        } catch (e) {
                            notes = [];
                        }
                    } else {
                        notes = [];
                    }
                }

                function saveNotes() {
                    localStorage.setItem(STORAGE_KEY, JSON.stringify(notes));
                }
                ```

            *   Initialization:
                ```javascript
                loadNotes();
                render();
                document.getElementById('add-note-btn').addEventListener('click', openAddModal);
                document.getElementById('note-form').addEventListener('submit', handleFormSubmit);
                document.getElementById('cancel-btn').addEventListener('click', () => document.getElementById('note-modal').close());
                document.getElementById('search-input').addEventListener('input', render);
                document.getElementById('owner-filter').addEventListener('change', render);
                document.getElementById('tag-filter').addEventListener('change', render);
                document.getElementById('category-filter').addEventListener('change', render);
                ```

            *   Close modal with Escape (handled by `<dialog>` natively).

        *   **Review against "compact statistics strip":**
            *   Total notes: `notes.length`
            *   Action-required count: `notes.filter(n => n.category === 'action-required').length`
            *   Unique owners: `new Set(notes.map(n => n.owner.toLowerCase())).size`
            *   Most common tag: `getMostCommonTag()`

        *   **Check line limit:**
            *   All the above is easily under 300 lines.
            *   Let's make sure the output is clean.

        *   **Final assembly of HTML, CSS, JS.**
        *   **CSS Adjustments:**
            *   Let's add `dialog form` styles.
            *   Add `aria-live="polite"` to the stats strip or the grid for screen reader updates when notes change. Let's add `role="region"` and `aria-live="polite"` to the grid.
            *   The `<dialog>` element handles focus nicely.
            *   The search input needs a label for accessibility. "Search notes". I'll add a visually hidden label or use `aria-label`.
            *   `<input type="search" id="search-input" aria-label="Search notes" placeholder="Search...">`

        *   **Data Validation:**
            *   `required` attribute on title and owner inputs in the form.

        *   **Closing the Modal:**
            *   `close()` method on the `<dialog>` element.
            *   Cancel button calls `document.getElementById('note-modal').close();`
            *   Form submission calls `close()`.

        *   **Edge case: Most common tag when no tags exist:**
            *   The function returns `{ tag: 'N/A', count: 0 }`. The stats display shows `N/A`.

        *   **Accessibility audit:**
            *   `<header>` wrapping stats and title.
            *   `<main>` wrapping controls and grid.
            *   `<section>` for grid with `role="list"` and `aria-label`.
            *   Cards have `role="listitem"`.
            *   Form controls have `<label>` or `aria-label`.
            *   Buttons have `aria-label` where necessary (edit/delete).
            *   Focus visible is styled.
            *   Keyboard navigation works natively for `<dialog>`, `<button>`, `<a>`, `<input>`, `<select>`, `<textarea>`.

        *   **Let's write the exact output.**

        *   Wait, do I need to display the most common tag or the top tag? "most common tag". Yes.

        *   **Refinement of CSS responsive:**
            The requirement says "two-column card grid on wide screens, single column on narrow screens." Standard breakpoint `768px` is good.

        *   **Code structure test:**
            Everything is in `<html>` -> `<head>` -> `<style>` -> `<body>` -> `<script>`.

        *   **Local Storage Key:** `meetingNotesBoardData`.

        *   **Checking the category border colors:**
            Action Required: Red (ds-danger)
            Decision: Yellow/Amber (ds-warning)
            Reference: Blue (ds-primary)

        *   **Sanity check on the JS logic:**
            `handleFormSubmit`:
            Sets `noteData.id` only for new notes.
            Updates existing note.
            Saves, renders, closes.

            `render`:
            Updates filter options (preserving current selection).
            Gets filtered notes.
            Builds HTML for grid.
            Updates stats.

            `updateFilterOptions`:
            Gets distinct owners and tags from `notes` (the full, unfiltered list).
            Rebuilds the dropdowns.

            `getFilteredNotes`:
            Filters the full `notes` array based on the current state of the filter inputs.

            `updateStats`:
            Calculates from `notes` (full list).

            Total notes: `notes.length`.
            Action Required: `notes.filter(n => n.category === 'action-required').length`.
            Unique Owners: `new Set(notes.map(n => n.owner.toLowerCase())).size`.
            Most Common Tag: needs a function.

            Let's trace the Tag counting function:
            ```javascript
            function getMostCommonTag() {
                const allTags = notes.flatMap(n => n.tags);
                if (allTags.length === 0) return 'N/A';
                const tagCounts = {};
                allTags.forEach(t => {
                    const lower = t.toLowerCase();
                    tagCounts[lower] = (tagCounts[lower] || 0) + 1;
                });
                let maxCount = 0;
                let mostCommon = 'N/A';
                for (const [tag, count] of Object.entries(tagCounts)) {
                    if (count > maxCount) {
                        maxCount = count;
                        mostCommon = tag;
                    }
                }
                return mostCommon;
            }
            ```
            This returns the tag name. Let's display it as `getMostCommonTag()`.

        *   **Everything looks solid.**

        Ready to write the output.
````

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
        *,
        *::before,
        *::after {
            box-sizing: border-box;
        }
        body {
            font-family: system-ui, -apple-system, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f8f9fa;
            color: #212529;
        }

        /* header & stats */
        header {
            margin-bottom: 20px;
        }
        h1 {
            font-size: 1.8rem;
            margin: 0 0 10px;
        }
        .stats-strip {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }
        .stat-item {
            background: #fff;
            padding: 8px 16px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
            font-size: 0.9rem;
        }
        .stat-item strong {
            font-weight: 700;
        }

        /* controls & filters */
        .controls {
            display: flex;
            gap: 15px;
            align-items: end;
            flex-wrap: wrap;
            justify-content: space-between;
            margin-bottom: 20px;
        }
        .filters {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            flex: 1;
        }
        .filters input,
        .filters select {
            padding: 8px 12px;
            border: 1px solid #ced4da;
            border-radius: 6px;
            font-size: 0.9rem;
            background: #fff;
        }
        .filters input#search-input {
            min-width: 180px;
            flex: 1;
        }
        #add-note-btn {
            padding: 8px 18px;
            background: #0d6efd;
            color: #fff;
            border: none;
            border-radius: 6px;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            white-space: nowrap;
        }

        /* notes grid */
        .notes-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
        }
        @media (max-width: 768px) {
            .notes-grid {
                grid-template-columns: 1fr;
            }
        }

        /* note card */
        .note-card {
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.08);
            border-left: 5px solid transparent;
            display: flex;
            flex-direction: column;
        }
        .note-card.note-category-action-required {
            border-left-color: #dc3545;
        }
        .note-card.note-category-decision {
            border-left-color: #ffc107;
        }
        .note-card.note-category-reference {
            border-left-color: #0d6efd;
        }
        .note-card h3 {
            margin: 0 0 8px;
            font-size: 1.15rem;
        }
        .note-card .note-meta {
            font-size: 0.85rem;
            color: #6c757d;
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-bottom: 10px;
        }
        .note-card .note-category {
            font-weight: 600;
            text-transform: capitalize;
        }
        .note-card>p {
            margin: 0 0 10px;
            white-space: pre-wrap;
            word-break: break-word;
        }
        .note-card .note-tags {
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
            margin-top: auto;
            padding-top: 10px;
        }
        .note-card .tag {
            background: #e9ecef;
            padding: 2px 10px;
            border-radius: 4px;
            font-size: 0.8rem;
        }
        .card-actions {
            display: flex;
            gap: 8px;
            justify-content: flex-end;
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid #eee;
        }
        .card-actions button {
            padding: 5px 14px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            background: #fff;
            cursor: pointer;
            font-size: 0.85rem;
        }
        .card-actions button:hover {
            background: #f1f3f5;
        }

        /* dialog / modal */
        dialog {
            border: none;
            border-radius: 12px;
            padding: 30px;
            max-width: 540px;
            width: 90%;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.25);
        }
        dialog::backdrop {
            background: rgba(0, 0, 0, 0.4);
        }
        dialog form p {
            margin: 0 0 16px;
        }
        dialog label {
            display: block;
            margin-bottom: 4px;
            font-weight: 600;
            font-size: 0.9rem;
        }
        dialog input:not([type="radio"]):not([type="checkbox"]),
        dialog select,
        dialog textarea {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #ced4da;
            border-radius: 6px;
            font-size: 0.95rem;
            font-family: inherit;
        }
        dialog textarea {
            resize: vertical;
            min-height: 60px;
        }
        .form-actions {
            display: flex;
            gap: 10px;
            justify-content: flex-end;
            margin-top: 24px;
        }
        .form-actions button {
            padding: 10px 24px;
            border-radius: 6px;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
        }
        #save-note-btn {
            background: #0d6efd;
            color: #fff;
            border: none;
        }
        #cancel-btn {
            background: #fff;
            border: 1px solid #ced4da;
        }

        /* accessibility */
        :focus-visible {
            outline: 2px solid #0d6efd;
            outline-offset: 2px;
        }
        .visually-hidden:not(:focus):not(:active) {
            position: absolute;
            width: 1px;
            height: 1px;
            margin: -1px;
            padding: 0;
            overflow: hidden;
            clip: rect(0, 0, 0, 0);
            white-space: nowrap;
            border: 0;
        }
    </style>
</head>
<body>

    <header>
        <h1>Meeting Notes Board</h1>
        <div class="stats-strip" id="stats-strip" aria-label="Note statistics">
            <span class="stat-item">Total Notes: <strong id="stat-total">0</strong></span>
            <span class="stat-item">Action Required: <strong id="stat-actions">0</strong></span>
            <span class="stat-item">Unique Owners: <strong id="stat-owners">0</strong></span>
            <span class="stat-item">Top Tag: <strong id="stat-tag">N/A</strong></span>
        </div>
    </header>

    <main>
        <section class="controls" aria-label="Controls and filters">
            <div class="filters">
                <input type="search" id="search-input" aria-label="Search notes" placeholder="Search by text…">
                <select id="owner-filter" aria-label="Filter by owner">
                    <option value="">All Owners</option>
                </select>
                <select id="tag-filter" aria-label="Filter by tag">
                    <option value="">All Tags</option>
                </select>
                <select id="category-filter" aria-label="Filter by category">
                    <option value="">All Categories</option>
                    <option value="action-required">Action Required</option>
                    <option value="decision">Decision</option>
                    <option value="reference">Reference</option>
                </select>
            </div>
            <button id="add-note-btn">+ Add Note</button>
        </section>

        <section class="notes-grid" id="notes-grid" role="list" aria-label="Meeting notes" aria-live="polite">
            <!-- notes rendered by JS -->
        </section>
    </main>

    <dialog id="note-modal">
        <form id="note-form" method="dialog">
            <h2 id="modal-title">Add Note</h2>
            <p>
                <label for="note-title">Title *</label>
                <input type="text" id="note-title" required autocomplete="off">
            </p>
            <p>
                <label for="note-owner">Owner *</label>
                <input type="text" id="note-owner" required autocomplete="off">
            </p>
            <p>
                <label for="note-date">Meeting Date</label>
                <input type="date" id="note-date">
            </p>
            <p>
                <label for="note-tags">Tags (comma-separated)</label>
                <input type="text" id="note-tags" placeholder="e.g. sprint, design" autocomplete="off">
            </p>
            <p>
                <label for="note-category">Category</label>
                <select id="note-category">
                    <option value="action-required">Action Required</option>
                    <option value="decision">Decision</option>
                    <option value="reference">Reference</option>
                </select>
            </p>
            <p>
                <label for="note-body">Body</label>
                <textarea id="note-body" rows="4"></textarea>
            </p>
            <div class="form-actions">
                <button type="submit" id="save-note-btn">Save</button>
                <button type="button" id="cancel-btn">Cancel</button>
            </div>
        </form>
    </dialog>

    <script>
        const STORAGE_KEY = 'meetingNotesBoardData';
        let notes = [];
        let editingId = null;

        // ----- helpers -----
        function escapeHtml(str) {
            if (!str) return '';
            const div = document.createElement('div');
            div.appendChild(document.createTextNode(str));
            return div.innerHTML;
        }

        // ----- storage -----
        function loadNotes() {
            const stored = localStorage.getItem(STORAGE_KEY);
            if (stored) {
                try {
                    notes = JSON.parse(stored);
                } catch {
                    notes = [];
                }
            } else {
                notes = [];
            }
        }

        function saveNotes() {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(notes));
        }

        // ----- filtering & stats -----
        function getFilteredNotes() {
            const searchTerm = document.getElementById('search-input').value.toLowerCase().trim();
            const ownerFilter = document.getElementById('owner-filter').value;
            const tagFilter = document.getElementById('tag-filter').value;
            const categoryFilter = document.getElementById('category-filter').value;

            return notes.filter(note => {
                if (searchTerm) {
                    const haystack = (
                        note.title + ' ' +
                        note.owner + ' ' +
                        (note.body || '') + ' ' +
                        (note.tags || []).join(' ')
                    ).toLowerCase();
                    if (!haystack.includes(searchTerm)) return false;
                }
                if (ownerFilter && note.owner !== ownerFilter) return false;
                if (tagFilter && !(note.tags || []).includes(tagFilter)) return false;
                if (categoryFilter && note.category !== categoryFilter) return false;
                return true;
            });
        }

        function getMostCommonTag() {
            const allTags = notes.flatMap(n => n.tags || []);
            if (allTags.length === 0) return { name: 'N/A', count: 0 };
            const counts = {};
            allTags.forEach(t => {
                const lower = t.toLowerCase();
                counts[lower] = (counts[lower] || 0) + 1;
            });
            let maxCount = 0;
            let mostCommon = 'N/A';
            for (const [tag, count] of Object.entries(counts)) {
                if (count > maxCount) {
                    maxCount = count;
                    mostCommon = tag;
                }
            }
            return { name: mostCommon, count: maxCount };
        }

        function updateStats() {
            const total = notes.length;
            const actionRequired = notes.filter(n => n.category === 'action-required').length;
            const uniqueOwners = new Set(notes.map(n => n.owner.toLowerCase())).size;
            const topTag = getMostCommonTag();

            document.getElementById('stat-total').textContent = total;
            document.getElementById('stat-actions').textContent = actionRequired;
            document.getElementById('stat-owners').textContent = uniqueOwners;
            document.getElementById('stat-tag').textContent = topTag.name + (topTag.count > 0 ? ' (' + topTag.count + ')' : '');
        }

        function updateFilterOptions() {
            const owners = [...new Set(notes.map(n => n.owner))];
            const tags = [...new Set(notes.flatMap(n => n.tags || []))];

            const ownerSelect = document.getElementById('owner-filter');
            const currentOwner = ownerSelect.value;
            ownerSelect.innerHTML = '<option value="">All Owners</option>';
            owners.forEach(o => {
                ownerSelect.innerHTML += '<option value="' + escapeHtml(o) + '">' + escapeHtml(o) + '</option>';
            });
            if ([...ownerSelect.options].some(o => o.value === currentOwner)) {
                ownerSelect.value = currentOwner;
            }

            const tagSelect = document.getElementById('tag-filter');
            const currentTag = tagSelect.value;
            tagSelect.innerHTML = '<option value="">All Tags</option>';
            tags.forEach(t => {
                tagSelect.innerHTML += '<option value="' + escapeHtml(t) + '">' + escapeHtml(t) + '</option>';
            });
            if ([...tagSelect.options].some(o => o.value === currentTag)) {
                tagSelect.value = currentTag;
            }
        }

        // ----- render -----
        function render() {
            updateFilterOptions();
            const filteredNotes = getFilteredNotes();
            const grid = document.getElementById('notes-grid');
            grid.innerHTML = '';

            if (filteredNotes.length === 0) {
                grid.innerHTML = '<p style="grid-column:1/-1;text-align:center;color:#6c757d;">No notes found.</p>';
            } else {
                filteredNotes.forEach(note => {
                    const card = document.createElement('article');
                    card.className = 'note-card';
                    if (note.category) {
                        card.classList.add('note-category-' + note.category);
                    }
                    card.setAttribute('role', 'listitem');
                    card.dataset.id = note.id;

                    const safeTitle = escapeHtml(note.title);
                    const safeOwner = escapeHtml(note.owner);
                    const safeDate = escapeHtml(note.date || 'N/A');
                    const safeCategory = escapeHtml((note.category || '').replace('-', ' '));
                    const safeBody = escapeHtml(note.body || '');
                    const tagsHtml = (note.tags || [])
                        .map(t => '<span class="tag">' + escapeHtml(t) + '</span>')
                        .join(' ');

                    card.innerHTML = `
                            <h3>${safeTitle}</h3>
                            <p class="note-meta">
                                <span>Owner: ${safeOwner}</span>
                                <span>Date: ${safeDate}</span>
                                <span class="note-category">${safeCategory}</span>
                            </p>
                            <p>${safeBody}</p>
                            <p class="note-tags">${tagsHtml}</p>
                            <div class="card-actions">
                                <button class="edit-btn" data-id="${note.id}" aria-label="Edit note: ${safeTitle}">Edit</button>
                                <button class="delete-btn" data-id="${note.id}" aria-label="Delete note: ${safeTitle}">Delete</button>
                            </div>
                        `;
                    grid.appendChild(card);
                });
            }
            updateStats();
        }

        // ----- modal -----
        function openAddModal() {
            editingId = null;
            document.getElementById('modal-title').textContent = 'Add Note';
            document.getElementById('note-form').reset();
            document.getElementById('note-category').value = 'action-required';
            document.getElementById('note-modal').showModal();
        }

        function openEditModal(id) {
            const note = notes.find(n => n.id == id);
            if (!note) return;
            editingId = id;
            document.getElementById('modal-title').textContent = 'Edit Note';
            document.getElementById('note-title').value = note.title || '';
            document.getElementById('note-owner').value = note.owner || '';
            document.getElementById('note-date').value = note.date || '';
            document.getElementById('note-tags').value = (note.tags || []).join(', ');
            document.getElementById('note-category').value = note.category || 'action-required';
            document.getElementById('note-body').value = note.body || '';
            document.getElementById('note-modal').showModal();
        }

        function closeModal() {
            document.getElementById('note-modal').close();
        }

        function handleFormSubmit(event) {
            event.preventDefault();
            const title = document.getElementById('note-title').value.trim();
            const owner = document.getElementById('note-owner').value.trim();
            if (!title || !owner) return; // required validation

            const date = document.getElementById('note-date').value;
            const tags = document.getElementById('note-tags').value
                .split(',')
                .map(t => t.trim())
                .filter(t => t);
            const category = document.getElementById('note-category').value;
            const body = document.getElementById('note-body').value.trim();

            const noteData = { title, owner, date, tags, category, body };

            if (editingId) {
                const index = notes.findIndex(n => n.id == editingId);
                if (index !== -1) {
                    notes[index] = { ...notes[index], ...noteData };
                }
            } else {
                noteData.id = Date.now() + '_' + Math.random().toString(36).substr(2, 9);
                notes.push(noteData);
            }

            saveNotes();
            render();
            closeModal();
        }

        function deleteNote(id) {
            if (confirm('Delete this note permanently?')) {
                notes = notes.filter(n => n.id != id);
                saveNotes();
                if (editingId == id) closeModal();
                render();
            }
        }

        // ----- event wiring -----
        document.getElementById('add-note-btn').addEventListener('click', openAddModal);
        document.getElementById('note-form').addEventListener('submit', handleFormSubmit);
        document.getElementById('cancel-btn').addEventListener('click', closeModal);

        document.getElementById('search-input').addEventListener('input', render);
        document.getElementById('owner-filter').addEventListener('change', render);
        document.getElementById('tag-filter').addEventListener('change', render);
        document.getElementById('category-filter').addEventListener('change', render);

        document.getElementById('notes-grid').addEventListener('click', function(e) {
            const btn = e.target.closest('button');
            if (!btn) return;
            const id = btn.dataset.id;
            if (btn.classList.contains('edit-btn')) {
                openEditModal(id);
            } else if (btn.classList.contains('delete-btn')) {
                deleteNote(id);
            }
        });

        // ----- init -----
        loadNotes();
        render();
    </script>
</body>
</html>
```
````
